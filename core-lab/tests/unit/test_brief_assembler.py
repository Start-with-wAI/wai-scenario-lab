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

import pytest
from app.services.brief_assembler import assemble_brief


@pytest.fixture
def sample_inputs():
    scenario_config = {
        "scenario_id": "cool_down_tax",
        "title": "The Cool Down Tax",
        "episode_number": "01",
        "episode_cta": {
            "title": "Explore Episode 01",
            "description": "Episode details.",
            "url": "https://example.com/episode-01"
        }
    }
    sanitized_input = {
        "scenario_id": "cool_down_tax",
        "stated_problem": "Client complaint from test@example.com",  # Should be sanitized
        "frequency": "weekly",
        "estimated_time_loss": 30,
        "current_process": "N/A",
        "primary_constraint": "client follow-up",
        "available_tools": [],
        "missing_information": []
    }
    analysis_state = {
        "friction_summary": "Workflow recovery creates drag.",
        "workflow_stage": "Client interactions",
        "known_facts": ["Occurs weekly"],
        "assumptions": ["Assumes average time lost is consistent."],
        "constraints": ["Follow-up work delayed."],
        "unknowns": ["Vendor response speed."],
        "proposed_next_action": "Record the recovery duration of next three emails.",
        "action_rationale": "Objective baseline details support standard pausing rules."
    }
    calculation_state = {
        "recommended_measure": "Recovery time per incident",
        "measure_unit": "minutes",
        "baseline_value": 30.0,
        "baseline_display": "30 minutes",
        "measurement_period": "Track the next three incidents.",
        "calculation_method": "Use the user's reported minutes_lost value.",
        "assumptions": ["Assumes time lost is constant."],
        "evidence_strength": "strong",
        "insufficient_data_flag": False
    }
    required_disclosures = {
        "human_review_reminder": "Use this brief as a starting point.",
        "responsible_use_limitation": "This prototype does not provide financial or tax advice."
    }
    return {
        "scenario_config": scenario_config,
        "sanitized_input": sanitized_input,
        "analysis_state": analysis_state,
        "calculation_state": calculation_state,
        "required_disclosures": required_disclosures
    }


def test_assemble_brief_approved(sample_inputs):
    safety_review = {
        "release_status": "APPROVED",
        "sensitive_data_detected": False,
        "redaction_categories": []
    }
    
    brief = assemble_brief(
        scenario_config=sample_inputs["scenario_config"],
        sanitized_input=sample_inputs["sanitized_input"],
        analysis_state=sample_inputs["analysis_state"],
        calculation_state=sample_inputs["calculation_state"],
        safety_review=safety_review,
        required_disclosures=sample_inputs["required_disclosures"]
    )
    
    assert brief["brief_status"] == "APPROVED"
    assert "result_id" in brief
    assert brief["scenario_id"] == "cool_down_tax"
    assert "what_we_heard" in brief
    assert "test@example.com" not in brief["what_we_heard"]  # Sensitive text redacted
    assert brief["one_next_step"] == sample_inputs["analysis_state"]["proposed_next_action"]
    assert brief["measurement"]["name"] == "Recovery time per incident"
    assert brief["human_review_reminder"] == sample_inputs["required_disclosures"]["human_review_reminder"]
    assert brief["responsible_use_limitation"] == sample_inputs["required_disclosures"]["responsible_use_limitation"]
    assert brief["episode_cta"]["title"] == "Explore Episode 01"


def test_assemble_brief_approved_with_limitation(sample_inputs):
    safety_review = {
        "release_status": "APPROVED_WITH_LIMITATION",
        "sensitive_data_detected": False,
        "redaction_categories": []
    }
    
    brief = assemble_brief(
        scenario_config=sample_inputs["scenario_config"],
        sanitized_input=sample_inputs["sanitized_input"],
        analysis_state=sample_inputs["analysis_state"],
        calculation_state=sample_inputs["calculation_state"],
        safety_review=safety_review,
        required_disclosures=sample_inputs["required_disclosures"]
    )
    
    assert brief["brief_status"] == "APPROVED_WITH_LIMITATION"
    assert "what_we_heard" in brief


def test_assemble_brief_revise_withholds_details(sample_inputs):
    safety_review = {
        "release_status": "REVISE",
        "sensitive_data_detected": True,
        "redaction_categories": ["email_address"],
        "revision_instructions": "Remove the email test@example.com."
    }
    
    brief = assemble_brief(
        scenario_config=sample_inputs["scenario_config"],
        sanitized_input=sample_inputs["sanitized_input"],
        analysis_state=sample_inputs["analysis_state"],
        calculation_state=sample_inputs["calculation_state"],
        safety_review=safety_review,
        required_disclosures=sample_inputs["required_disclosures"]
    )
    
    assert brief["brief_status"] == "REVISE"
    assert "what_we_heard" not in brief
    assert "one_next_step" not in brief
    assert "message" in brief
    assert brief["revision_instructions"] == "Remove the email test@example.com."


def test_assemble_brief_blocked_withholds_details(sample_inputs):
    safety_review = {
        "release_status": "BLOCKED",
        "sensitive_data_detected": False,
        "redaction_categories": []
    }
    
    brief = assemble_brief(
        scenario_config=sample_inputs["scenario_config"],
        sanitized_input=sample_inputs["sanitized_input"],
        analysis_state=sample_inputs["analysis_state"],
        calculation_state=sample_inputs["calculation_state"],
        safety_review=safety_review,
        required_disclosures=sample_inputs["required_disclosures"]
    )
    
    assert brief["brief_status"] == "BLOCKED"
    assert "what_we_heard" not in brief
    assert "one_next_step" not in brief
    assert "message" in brief
