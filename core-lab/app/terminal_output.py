# Copyright 2026 Google LLC
# Modifications copyright 2026 Start with wAI.
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

"""Terminal Output Assembly Service.

Collects workflow data, safety prechecks, and config definitions to compile
a Scenario Brief preview strictly utilizing Jason's assemble_brief() service.
"""

from typing import Any
from app.services.brief_assembler import assemble_brief


class TerminalOutputError(Exception):
    """Raised when terminal output assembly fails or encounters validation errors."""
    pass


def build_deterministic_sanitized_input(workflow_payload: dict) -> dict:
    """Builds a ScenarioInputState-compatible dictionary from the workflow payload.

    Args:
        workflow_payload: The normalized workflow payload.

    Returns:
        ScenarioInputState-compatible dict.
    """
    answers = workflow_payload.get("answers", {})
    stated_problem = answers.get("interaction_type")
    
    if not stated_problem:
        raise TerminalOutputError("Stated problem (interaction_type) is missing or empty.")

    return {
        "scenario_id": workflow_payload.get("scenario_id", "cool_down_tax"),
        "stated_problem": stated_problem,
        "frequency": answers.get("frequency", "weekly"),
        "estimated_time_loss": answers.get("minutes_lost"),
        "current_process": answers.get("work_disrupted"),
        "primary_constraint": "Recovery time after stressful business interaction",
        "available_tools": [],
        "missing_information": []
    }


def build_deterministic_analysis_state(workflow_payload: dict) -> dict:
    """Creates a cautious, deterministic AnalysisState preview.

    Args:
        workflow_payload: The normalized workflow payload.

    Returns:
        AnalysisState-compatible dict.
    """
    answers = workflow_payload.get("answers", {})
    freq = answers.get("frequency", "weekly")
    time_loss = answers.get("minutes_lost", 0)

    return {
        "friction_summary": "The friction may be occurring during recovery and response preparation after the reported interaction.",
        "workflow_stage": "Follow-up response preparation",
        "known_facts": [
            f"The user reported the interaction happens {freq}.",
            f"The user reported {time_loss} minutes of productive time lost afterward."
        ],
        "assumptions": [
            "The reported time loss reflects a typical incident."
        ],
        "constraints": [
            "The next step should remain small, reversible, and manually reviewed."
        ],
        "unknowns": [
            "Whether a reusable neutral response template already exists."
        ],
        "proposed_next_action": "Track the recovery time for the next three similar interactions before changing the process.",
        "action_rationale": "A short observation period can create a baseline without automating customer communication."
    }


def build_deterministic_calculation_state(workflow_payload: dict, scenario_config: dict) -> dict:
    """Builds a CalculationState-compatible baseline measurement.

    Args:
        workflow_payload: The normalized workflow payload.
        scenario_config: Specific scenario config dict.

    Returns:
        CalculationState-compatible dict.
    """
    answers = workflow_payload.get("answers", {})
    minutes_lost = answers.get("minutes_lost", 0)
    try:
        baseline_val = float(minutes_lost)
    except (ValueError, TypeError):
        baseline_val = 0.0

    return {
        "recommended_measure": scenario_config.get("measurement_preview", "Recovery time per incident"),
        "measure_unit": "minutes",
        "baseline_value": baseline_val,
        "baseline_display": f"{int(baseline_val)} minutes",
        "calculation_method": "Use the reported minutes lost as a starting observation baseline, then compare it with the next three similar incidents.",
        "assumptions": [
            "The reported value is self-reported and should be treated as a starting observation."
        ],
        "evidence_strength": "partial",
        "measurement_period": "Track the next three similar incidents.",
        "insufficient_data_flag": False
    }


def build_safety_review_from_route_preview(sprint_4_response: dict) -> dict:
    """Converts the Sprint 4 safety precheck into a SafetyReviewState dictionary.

    Args:
        sprint_4_response: Output from safety router.

    Returns:
        SafetyReviewState-compatible dict.
    """
    precheck = sprint_4_response.get("safety_precheck", {})
    release_status = precheck.get("release_status", "REVISE")
    redaction_cats = precheck.get("redaction_categories", [])

    if release_status in ("APPROVED", "APPROVED_WITH_LIMITATION"):
        return {
            "privacy_status": "No sensitive data detected in deterministic precheck.",
            "sensitive_data_detected": False,
            "unsupported_claims": False,
            "scope_violation": False,
            "high_risk_domain_flag": False,
            "human_review_present": True,
            "required_disclosures_present": True,
            "quality_score": 8,
            "release_status": release_status,
            "revision_instructions": "",
            "redaction_categories": []
        }
    elif release_status == "REVISE":
        return {
            "privacy_status": "Sensitive data detected during deterministic safety precheck.",
            "sensitive_data_detected": True,
            "unsupported_claims": False,
            "scope_violation": False,
            "high_risk_domain_flag": False,
            "human_review_present": True,
            "required_disclosures_present": True,
            "quality_score": 5,
            "release_status": "REVISE",
            "revision_instructions": "Remove or revise sensitive information before rendering a Scenario Brief.",
            "redaction_categories": redaction_cats
        }
    else:  # BLOCKED
        return {
            "privacy_status": "Outside safe scope of the demo.",
            "sensitive_data_detected": False,
            "unsupported_claims": False,
            "scope_violation": True,
            "high_risk_domain_flag": True,
            "human_review_present": True,
            "required_disclosures_present": True,
            "quality_score": 1,
            "release_status": "BLOCKED",
            "revision_instructions": "",
            "redaction_categories": []
        }


def prepare_sprint_5_terminal_output_response(
    config: dict,
    workflow_payload: dict,
    adapter_response: dict,
    sprint_4_response: dict
) -> dict:
    """Merges all adapter outputs, runs safety mapping, and assembles the brief preview.

    Args:
        config: Loaded config dictionary.
        workflow_payload: Normalized input payload.
        adapter_response: Output from Sprint 3 adapter.
        sprint_4_response: Output from Sprint 4 safety router.

    Returns:
        Sprint 5 response dictionary.
    """
    scenario_id = workflow_payload.get("scenario_id", "cool_down_tax")
    scenarios = config.get("scenarios", {})
    scenario_config = scenarios.get(scenario_id, {})
    required_disclosures = config.get("required_disclosures", {})

    if not scenario_config:
        raise TerminalOutputError(f"Scenario configuration for '{scenario_id}' not found.")

    sanitized_input = build_deterministic_sanitized_input(workflow_payload)
    analysis_state = build_deterministic_analysis_state(workflow_payload)
    calculation_state = build_deterministic_calculation_state(workflow_payload, scenario_config)
    safety_review = build_safety_review_from_route_preview(sprint_4_response)

    brief_preview = assemble_brief(
        scenario_config=scenario_config,
        sanitized_input=sanitized_input,
        analysis_state=analysis_state,
        calculation_state=calculation_state,
        safety_review=safety_review,
        required_disclosures=required_disclosures
    )

    release_status = safety_review["release_status"]
    terminal_route = sprint_4_response.get("terminal_route_preview", {}).get("terminal_route", "HUMAN_TRIAGE")

    return {
        "checkpoint": "Sprint 5",
        "message": "Sprint 5 checkpoint: terminal output assembly completed. Live agent workflow has not run yet.",
        "scenario_id": scenario_id,
        "episode_number": scenario_config.get("episode_number", "01"),
        "scenario_title": scenario_config.get("title", "Scenario Title"),
        "terminal_route": terminal_route,
        "safety_precheck": sprint_4_response.get("safety_precheck", {}),
        "adapter_status": adapter_response.get("adapter_status", "READY_FOR_AGENT_1"),
        "agent_1_input": adapter_response.get("agent_1_input", {}),
        "brief_preview_status": release_status,
        "scenario_brief_preview": brief_preview,
        "not_run": [
            "Gemini model calls",
            "ADK Runner execution",
            "Live Agent 1 execution",
            "Live Agent 2 execution",
            "Live Agent 3 execution",
            "Live Agent 4 execution",
            "Full ADK graph execution",
            "Public JSON endpoint"
        ]
    }
