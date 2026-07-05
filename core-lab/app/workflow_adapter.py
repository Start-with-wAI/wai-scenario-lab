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

class WorkflowAdapterError(Exception):
    """Raised when workflow adapter payload validation fails."""
    pass


def build_agent_1_input(workflow_payload: dict) -> dict:
    """Validates the normalized payload and prepares the input structure expected by Agent 1.

    Args:
        workflow_payload: Normalized payload from Sprint 2.

    Returns:
        Structured input dictionary for Agent 1.

    Raises:
        WorkflowAdapterError: If required payload fields are missing.
    """
    required_keys = ["scenario_id", "episode_number", "scenario_title", "answers", "scenario_context"]
    for k in required_keys:
        if k not in workflow_payload:
            raise WorkflowAdapterError(f"Missing required payload key: '{k}'")

    answers = workflow_payload["answers"]
    if not isinstance(answers, dict):
        raise WorkflowAdapterError("Key 'answers' must be a dictionary.")

    from app.config_loader import load_scenario_config
    try:
        config = load_scenario_config()
    except Exception as e:
        raise WorkflowAdapterError(f"Failed to load scenario configuration: {e}")

    scenario_id = workflow_payload.get("scenario_id")
    scenario_config = config.get("scenarios", {}).get(scenario_id)
    if not scenario_config:
        raise WorkflowAdapterError(f"Scenario '{scenario_id}' not found in config.")

    # Derive required question IDs dynamically from config
    questions = scenario_config.get("questions", [])
    required_answers = [q.get("id") for q in questions if q.get("required")]
    for a in required_answers:
        if a not in answers or answers[a] == "":
            raise WorkflowAdapterError(f"Missing required answer key: '{a}'")

    context = workflow_payload["scenario_context"]
    if not isinstance(context, dict):
        raise WorkflowAdapterError("Key 'scenario_context' must be a dictionary.")

    return {
        "scenario_id": scenario_id,
        "selected_scenario": {
            "episode_number": workflow_payload.get("episode_number"),
            "title": workflow_payload.get("scenario_title"),
            "context": context.get("context"),
            "measurement_preview": context.get("measurement_preview")
        },
        "user_answers": answers,
        "adapter_status": "READY_FOR_AGENT_1"
    }


def build_graph_transition_trace(workflow_payload: dict) -> list[dict]:
    """Generates the deterministic dry-run graph transition trace without executing agents.

    Args:
        workflow_payload: Normalized workflow payload.

    Returns:
        A list of step dictionaries representing the intended execution path.
    """
    # Enforce basic validation by building input first (which throws WorkflowAdapterError if invalid)
    build_agent_1_input(workflow_payload)

    return [
        {
            "step": 1,
            "node": "START",
            "status": "READY",
            "execution": "not_run"
        },
        {
            "step": 2,
            "node": "scenario_guide_agent",
            "status": "INPUT_PREPARED",
            "execution": "not_run"
        },
        {
            "step": 3,
            "node": "workflow_analyst_agent",
            "status": "WAITING_FOR_AGENT_1_OUTPUT",
            "execution": "not_run"
        },
        {
            "step": 4,
            "node": "value_evidence_agent",
            "status": "WAITING_FOR_AGENT_2_OUTPUT",
            "execution": "not_run"
        },
        {
            "step": 5,
            "node": "safety_quality_agent",
            "status": "WAITING_FOR_AGENT_3_OUTPUT",
            "execution": "not_run"
        },
        {
            "step": 6,
            "node": "evaluate_safety_gate",
            "status": "WAITING_FOR_AGENT_4_RELEASE_STATUS",
            "execution": "not_run"
        },
        {
            "step": 7,
            "node": "terminal_route_pending",
            "status": "PENDING_SPRINT_4",
            "execution": "not_run"
        }
    ]


def prepare_workflow_adapter_response(workflow_payload: dict) -> dict:
    """Prepares the complete response structure for the workflow adapter checkpoint.

    Args:
        workflow_payload: Validated and normalized workflow payload.

    Returns:
        Structured checkpoint response.

    Raises:
        WorkflowAdapterError: If validation fails.
    """
    agent_1_in = build_agent_1_input(workflow_payload)
    trace = build_graph_transition_trace(workflow_payload)

    return {
        "checkpoint": "Sprint 3",
        "message": "Sprint 3 checkpoint: normalized input prepared for workflow adapter. Agent workflow has not run yet.",
        "scenario_id": workflow_payload.get("scenario_id"),
        "episode_number": workflow_payload.get("episode_number"),
        "scenario_title": workflow_payload.get("scenario_title"),
        "adapter_status": "READY_FOR_AGENT_1",
        "agent_1_input": agent_1_in,
        "graph_transition_trace": trace,
        "not_run": [
            "Gemini model calls",
            "ADK Runner execution",
            "Agent 1 execution",
            "Agent 2 execution",
            "Agent 3 execution",
            "Agent 4 execution",
            "Safety gate routing",
            "Scenario Brief rendering"
        ]
    }


# Backward compatibility aliases for tests
prepare_episode_01_workflow_adapter_response = prepare_workflow_adapter_response


