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

import re
import unittest
from fastapi.testclient import TestClient
from app.fast_api_app import app
from app.config_loader import load_scenario_config
from app.terminal_output import (
    build_deterministic_sanitized_input,
    build_deterministic_analysis_state,
    build_deterministic_calculation_state,
    build_safety_review_from_route_preview,
    prepare_sprint_5_terminal_output_response,
    TerminalOutputError,
)


def get_base_payload():
    return {
        "scenario_id": "cool_down_tax",
        "episode_number": "01",
        "scenario_title": "The Cool Down Tax",
        "answers": {
            "interaction_type": "Vendor delay",
            "frequency": "weekly",
            "minutes_lost": 45,
            "work_disrupted": "Scheduling follow ups"
        },
        "scenario_context": {
            "short_description": "Short description",
            "context": "Scenario context details",
            "measurement_preview": "Recovery time per incident"
        }
    }


def get_sprint_4_approved_response():
    return {
        "checkpoint": "Sprint 4",
        "message": "Sprint 4 checkpoint",
        "safety_precheck": {
            "release_status": "APPROVED",
            "sensitive_data_detected": False,
            "high_risk_domain_flag": False,
            "redaction_categories": []
        },
        "terminal_route_preview": {
            "terminal_route": "RENDER_BRIEF"
        }
    }


class TestTerminalOutput(unittest.TestCase):

    def test_build_deterministic_sanitized_input_valid(self):
        payload = get_base_payload()
        res = build_deterministic_sanitized_input(payload)
        self.assertEqual(res["scenario_id"], "cool_down_tax")
        self.assertEqual(res["stated_problem"], "Vendor delay")
        self.assertEqual(res["frequency"], "weekly")
        self.assertEqual(res["estimated_time_loss"], 45)
        self.assertEqual(res["current_process"], "Scheduling follow ups")
        self.assertEqual(res["primary_constraint"], "Recovery time after stressful business interaction")

    def test_build_deterministic_sanitized_input_missing_problem(self):
        payload = get_base_payload()
        del payload["answers"]["interaction_type"]
        with self.assertRaises(TerminalOutputError):
            build_deterministic_sanitized_input(payload)

    def test_build_deterministic_analysis_state_action_format(self):
        payload = get_base_payload()
        res = build_deterministic_analysis_state(payload)
        action = res["proposed_next_action"]
        
        # Check single action and no numbered lists
        self.assertFalse(re.search(r"(^|\s)(1\.|2\.|3\.|first,|second,|third,)", action, re.I))
        self.assertNotIn("\n-", action)
        self.assertNotIn("\n*", action)
        
        # Expressed as a single sentence
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", action) if s.strip()]
        self.assertEqual(len(sentences), 1)

    def test_build_deterministic_analysis_state_no_bullet_lists(self):
        payload = get_base_payload()
        res = build_deterministic_analysis_state(payload)
        action = res["proposed_next_action"]
        self.assertNotIn("\n-", action)
        self.assertNotIn("\n*", action)

    def test_build_deterministic_calculation_state_non_monetary(self):
        payload = get_base_payload()
        config = load_scenario_config()
        scenario_config = config.get("scenarios", {}).get("cool_down_tax", {})
        res = build_deterministic_calculation_state(payload, scenario_config)
        self.assertEqual(res["measure_unit"], "minutes")
        self.assertEqual(res["baseline_value"], 45.0)
        self.assertEqual(res["baseline_display"], "45 minutes")

    def test_build_deterministic_calculation_state_no_financial_terms(self):
        payload = get_base_payload()
        config = load_scenario_config()
        scenario_config = config.get("scenarios", {}).get("cool_down_tax", {})
        res = build_deterministic_calculation_state(payload, scenario_config)
        
        # Verify no monetary words
        method = res["calculation_method"]
        self.assertNotIn("ROI", method)
        self.assertNotIn("$", method)
        self.assertNotIn("dollar", method)
        self.assertNotIn("cost", method)
        self.assertNotIn("equity", method)

    def test_build_safety_review_from_route_preview_approved(self):
        sprint_4_res = get_sprint_4_approved_response()
        res = build_safety_review_from_route_preview(sprint_4_res)
        self.assertEqual(res["release_status"], "APPROVED")
        self.assertFalse(res["sensitive_data_detected"])
        self.assertFalse(res["high_risk_domain_flag"])

    def test_build_safety_review_from_route_preview_blocked(self):
        sprint_4_res = {
            "safety_precheck": {
                "release_status": "BLOCKED",
                "sensitive_data_detected": False,
                "high_risk_domain_flag": True
            },
            "terminal_route_preview": {
                "terminal_route": "TERMINATE_BLOCKED"
            }
        }
        res = build_safety_review_from_route_preview(sprint_4_res)
        self.assertEqual(res["release_status"], "BLOCKED")
        self.assertTrue(res["high_risk_domain_flag"])
        self.assertTrue(res["scope_violation"])

    def test_prepare_sprint_5_terminal_output_approved(self):
        payload = get_base_payload()
        adapter_res = {"adapter_status": "READY_FOR_AGENT_1"}
        sprint_4_res = get_sprint_4_approved_response()
        config = load_scenario_config()
        
        res = prepare_sprint_5_terminal_output_response(config, payload, adapter_res, sprint_4_res)
        self.assertEqual(res["checkpoint"], "Sprint 5")
        self.assertEqual(res["terminal_route"], "RENDER_BRIEF")
        self.assertEqual(res["brief_preview_status"], "APPROVED")
        
        brief = res["scenario_brief_preview"]
        self.assertEqual(brief["brief_status"], "APPROVED")
        self.assertEqual(brief["one_next_step"], "Track the recovery time for the next three similar interactions before changing the process.")
        self.assertEqual(brief["measurement"]["unit"], "minutes")

    def test_prepare_sprint_5_terminal_output_human_triage_withheld(self):
        payload = get_base_payload()
        adapter_res = {"adapter_status": "READY_FOR_AGENT_1"}
        sprint_4_res = {
            "safety_precheck": {
                "release_status": "REVISE",
                "sensitive_data_detected": True,
                "redaction_categories": ["email_address"]
            },
            "terminal_route_preview": {
                "terminal_route": "HUMAN_TRIAGE"
            }
        }
        config = load_scenario_config()
        
        res = prepare_sprint_5_terminal_output_response(config, payload, adapter_res, sprint_4_res)
        self.assertEqual(res["terminal_route"], "HUMAN_TRIAGE")
        self.assertEqual(res["brief_preview_status"], "REVISE")
        
        brief = res["scenario_brief_preview"]
        self.assertEqual(brief["brief_status"], "REVISE")
        self.assertNotIn("one_next_step", brief)
        self.assertIn("Details withheld", brief["message"])

    def test_prepare_sprint_5_terminal_output_blocked_withheld(self):
        payload = get_base_payload()
        adapter_res = {"adapter_status": "READY_FOR_AGENT_1"}
        sprint_4_res = {
            "safety_precheck": {
                "release_status": "BLOCKED",
                "sensitive_data_detected": False,
                "high_risk_domain_flag": True
            },
            "terminal_route_preview": {
                "terminal_route": "TERMINATE_BLOCKED"
            }
        }
        config = load_scenario_config()
        
        res = prepare_sprint_5_terminal_output_response(config, payload, adapter_res, sprint_4_res)
        self.assertEqual(res["terminal_route"], "TERMINATE_BLOCKED")
        self.assertEqual(res["brief_preview_status"], "BLOCKED")
        
        brief = res["scenario_brief_preview"]
        self.assertEqual(brief["brief_status"], "BLOCKED")
        self.assertNotIn("one_next_step", brief)

    def test_post_route_valid_approved(self):
        client = TestClient(app)
        response = client.post("/", data={
            "interaction_type": "Vendor delay",
            "frequency": "weekly",
            "minutes_lost": "45",
            "work_disrupted": "Scheduling"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sprint 5 checkpoint: terminal output assembly completed. Live agent workflow has not run yet.", response.text)
        self.assertIn("RENDER_BRIEF", response.text)
        self.assertIn("APPROVED", response.text)

    def test_post_route_valid_brief_preview_status(self):
        client = TestClient(app)
        response = client.post("/", data={
            "interaction_type": "Vendor delay",
            "frequency": "weekly",
            "minutes_lost": "45",
            "work_disrupted": "Scheduling"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("brief_preview_status", response.text)

    def test_post_route_valid_measurement_present(self):
        client = TestClient(app)
        response = client.post("/", data={
            "interaction_type": "Vendor delay",
            "frequency": "weekly",
            "minutes_lost": "45",
            "work_disrupted": "Scheduling"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("45 minutes", response.text)
        self.assertIn("Recovery time per incident", response.text)

    def test_post_route_valid_disclosures_present(self):
        client = TestClient(app)
        response = client.post("/", data={
            "interaction_type": "Vendor delay",
            "frequency": "weekly",
            "minutes_lost": "45",
            "work_disrupted": "Scheduling"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Human Review Reminder", response.text)
        self.assertIn("Responsible Use Limitation", response.text)

    def test_post_route_sensitive_email_routes_to_triage(self):
        client = TestClient(app)
        response = client.post("/", data={
            "interaction_type": "Vendor delay",
            "frequency": "weekly",
            "minutes_lost": "45",
            "work_disrupted": "Emailing owner@example.test"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("HUMAN_TRIAGE", response.text)
        self.assertIn("This scenario needs human review before a Scenario Brief can be shown.", response.text)
        self.assertNotIn("Track the recovery time", response.text)  # Details withheld

    def test_post_route_blocked_legal_routes_to_blocked(self):
        client = TestClient(app)
        response = client.post("/", data={
            "interaction_type": "Vendor delay",
            "frequency": "weekly",
            "minutes_lost": "45",
            "work_disrupted": "I want to sue my landlord in court over eviction."
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("TERMINATE_BLOCKED", response.text)
        self.assertIn("This scenario is outside the safe scope of the demo, so no Scenario Brief was generated.", response.text)
        self.assertNotIn("Track the recovery time", response.text)  # Details withheld

    def test_post_route_invalid_bad_inputs(self):
        client = TestClient(app)
        response = client.post("/", data={
            "interaction_type": "",
            "frequency": "weekly",
            "minutes_lost": "abc",
            "work_disrupted": "Scheduling"
        })
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("Sprint 5 checkpoint", response.text)

    def test_get_route_valid(self):
        client = TestClient(app)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("The Cool Down Tax", response.text)

    def test_adk_routes_routable(self):
        client = TestClient(app)
        response = client.get("/docs")
        self.assertEqual(response.status_code, 200)
        response = client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)

