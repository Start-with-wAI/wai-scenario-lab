# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from app.services.safety import evaluate_safety_text


class SafetyRouterError(Exception):
    """Raised when safety routing checks or mappings fail."""
    pass


def combine_answers_for_safety_scan(workflow_payload: dict) -> str:
    """Combines answer fields into a single text block for safety scan dynamically.

    Args:
        workflow_payload: Normalized workflow payload.

    Returns:
        Combined answers string.

    Raises:
        SafetyRouterError: If answers structure is invalid.
    """
    if "answers" not in workflow_payload:
        raise SafetyRouterError("Missing answers block in workflow payload.")
    
    answers = workflow_payload["answers"]
    if not isinstance(answers, dict):
        raise SafetyRouterError("Answers block must be a dictionary.")

    from app.config_loader import load_scenario_config
    try:
        config = load_scenario_config()
    except Exception as e:
        raise SafetyRouterError(f"Failed to load scenario config: {e}")

    scenario_id = workflow_payload.get("scenario_id")
    scenario_config = config.get("scenarios", {}).get(scenario_id)
    if scenario_config:
        # Check required questions for this scenario are present in answers
        for q in scenario_config.get("questions", []):
            if q.get("required", False) and q.get("id") not in answers:
                raise SafetyRouterError(f"Missing required answer key for safety scan: '{q.get('id')}'")
    else:
        # Fallback to hardcoded cool_down_tax required keys if scenario is not found in config (for testing)
        required_keys = ["interaction_type", "frequency", "minutes_lost", "work_disrupted"]
        for key in required_keys:
            if key not in answers:
                raise SafetyRouterError(f"Missing required answer key for safety scan: '{key}'")

    parts = []
    for k, v in answers.items():
        parts.append(f"{k}: {v}")

    return "\n".join(parts)



def run_deterministic_safety_precheck(workflow_payload: dict) -> dict:
    """Executes the deterministic safety precheck on the payload answers.

    Args:
        workflow_payload: Normalized workflow payload.

    Returns:
        Deterministic safety precheck result dictionary.
    """
    try:
        combined_text = combine_answers_for_safety_scan(workflow_payload)
    except SafetyRouterError as e:
        raise SafetyRouterError(f"Safety scan failed: {e}")

    safety_res = evaluate_safety_text(combined_text)

    return {
        "safety_checkpoint": "deterministic_precheck",
        "release_status": safety_res.get("release_status", "APPROVED"),
        "sensitive_data_detected": safety_res.get("sensitive_data_detected", False),
        "redaction_categories": safety_res.get("redaction_categories", []),
        "high_risk_domain_flag": safety_res.get("high_risk_domain_flag", False),
        "flagged_domains": safety_res.get("flagged_domains", []),
        "prohibited_automation_flag": safety_res.get("prohibited_automation_flag", False),
        "unsupported_claims": safety_res.get("unsupported_claims", False),
        "source": "app.services.safety.evaluate_safety_text",
        "note": "Deterministic precheck only. Agent 4 has not run yet."
    }


def map_release_status_to_terminal_route(release_status: str) -> dict:
    """Maps the safety release status to a terminal route preview.

    Args:
        release_status: Safety check release status.

    Returns:
        Dictionary detailing the mapped terminal route.
    """
    status_map = {
        "APPROVED": "RENDER_BRIEF",
        "APPROVED_WITH_LIMITATION": "RENDER_LIMITATION_BANNER",
        "BLOCKED": "TERMINATE_BLOCKED",
        "REVISE": "HUMAN_TRIAGE"
    }

    terminal_route = status_map.get(release_status, "HUMAN_TRIAGE")

    return {
        "release_status": release_status,
        "terminal_route": terminal_route,
        "route_status": "ROUTE_PREVIEW_READY",
        "execution": "not_run"
    }


def build_safety_routing_trace(release_status: str) -> list[dict]:
    """Constructs the trace steps representing deterministic safety routing path.

    Args:
        release_status: Mapped release status.

    Returns:
        List of trace step dictionaries.
    """
    route_info = map_release_status_to_terminal_route(release_status)
    terminal_route = route_info["terminal_route"]

    return [
        {
            "step": 1,
            "node": "safety_precheck",
            "status": "COMPLETED",
            "execution": "deterministic_only"
        },
        {
            "step": 2,
            "node": "evaluate_safety_gate",
            "status": "ROUTE_PREVIEW_READY",
            "execution": "not_run"
        },
        {
            "step": 3,
            "node": "terminal_route_preview",
            "status": terminal_route,
            "execution": "not_run"
        }
    ]


def prepare_sprint_4_safety_routing_response(workflow_payload: dict, adapter_response: dict) -> dict:
    """Assembles the complete Sprint 4 response combining adapter payload and safety precheck.

    Args:
        workflow_payload: Normalized payload.
        adapter_response: Sprint 3 adapter output.

    Returns:
        Complete Sprint 4 response dictionary.
    """
    precheck = run_deterministic_safety_precheck(workflow_payload)
    route_preview = map_release_status_to_terminal_route(precheck["release_status"])
    safety_trace = build_safety_routing_trace(precheck["release_status"])

    return {
        "checkpoint": "Sprint 4",
        "message": "Sprint 4 checkpoint: deterministic safety routing preview completed. Agent workflow has not run yet.",
        "scenario_id": workflow_payload.get("scenario_id"),
        "episode_number": workflow_payload.get("episode_number"),
        "scenario_title": workflow_payload.get("scenario_title"),
        "adapter_status": adapter_response.get("adapter_status", "READY_FOR_AGENT_1"),
        "agent_1_input": adapter_response.get("agent_1_input", {}),
        "safety_precheck": precheck,
        "terminal_route_preview": route_preview,
        "safety_routing_trace": safety_trace,
        "not_run": [
            "Gemini model calls",
            "ADK Runner execution",
            "Agent 1 execution",
            "Agent 2 execution",
            "Agent 3 execution",
            "Agent 4 execution",
            "Terminal node execution",
            "Scenario Brief rendering"
        ]
    }
