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

import unittest
from fastapi.testclient import TestClient
from app.fast_api_app import app
from app.safety_router import (
    combine_answers_for_safety_scan,
    run_deterministic_safety_precheck,
    map_release_status_to_terminal_route,
    build_safety_routing_trace,
    prepare_sprint_4_safety_routing_response,
    SafetyRouterError,
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


class TestSafetyRouter(unittest.TestCase):

    def test_combine_answers_for_safety_scan_valid(self):
        payload = get_base_payload()
        combined = combine_answers_for_safety_scan(payload)
        self.assertIn("Vendor delay", combined)
        self.assertIn("weekly", combined)
        self.assertIn("45", combined)
        self.assertIn("Scheduling follow ups", combined)

    def test_combine_answers_for_safety_scan_missing_fields(self):
        payload = get_base_payload()
        del payload["answers"]["work_disrupted"]
        with self.assertRaises(SafetyRouterError):
            combine_answers_for_safety_scan(payload)

    def test_run_deterministic_safety_precheck_approved(self):
        payload = get_base_payload()
        precheck = run_deterministic_safety_precheck(payload)
        self.assertEqual(precheck["release_status"], "APPROVED")
        self.assertFalse(precheck["sensitive_data_detected"])
        self.assertFalse(precheck["high_risk_domain_flag"])
        self.assertFalse(precheck["prohibited_automation_flag"])

    def test_run_deterministic_safety_precheck_revise_email(self):
        payload = get_base_payload()
        payload["answers"]["interaction_type"] = "Vendor email owner@example.test delayed shipping"
        precheck = run_deterministic_safety_precheck(payload)
        self.assertEqual(precheck["release_status"], "REVISE")
        self.assertTrue(precheck["sensitive_data_detected"])
        self.assertIn("email_address", precheck["redaction_categories"])

    def test_run_deterministic_safety_precheck_blocked_legal(self):
        payload = get_base_payload()
        payload["answers"]["work_disrupted"] = "I want to sue my landlord in court over the lease."
        precheck = run_deterministic_safety_precheck(payload)
        self.assertEqual(precheck["release_status"], "BLOCKED")
        self.assertTrue(precheck["high_risk_domain_flag"])
        self.assertIn("housing", precheck["flagged_domains"])

    def test_map_release_status_to_terminal_route(self):
        self.assertEqual(
            map_release_status_to_terminal_route("APPROVED")["terminal_route"],
            "RENDER_BRIEF"
        )
        self.assertEqual(
            map_release_status_to_terminal_route("APPROVED_WITH_LIMITATION")["terminal_route"],
            "RENDER_LIMITATION_BANNER"
        )
        self.assertEqual(
            map_release_status_to_terminal_route("BLOCKED")["terminal_route"],
            "TERMINATE_BLOCKED"
        )
        self.assertEqual(
            map_release_status_to_terminal_route("REVISE")["terminal_route"],
            "HUMAN_TRIAGE"
        )
        self.assertEqual(
            map_release_status_to_terminal_route("UNKNOWN")["terminal_route"],
            "HUMAN_TRIAGE"
        )

    def test_build_safety_routing_trace(self):
        trace = build_safety_routing_trace("APPROVED")
        self.assertEqual(len(trace), 3)
        self.assertEqual(trace[0]["node"], "safety_precheck")
        self.assertEqual(trace[0]["execution"], "deterministic_only")
        self.assertEqual(trace[1]["node"], "evaluate_safety_gate")
        self.assertEqual(trace[1]["execution"], "not_run")
        self.assertEqual(trace[2]["node"], "terminal_route_preview")
        self.assertEqual(trace[2]["status"], "RENDER_BRIEF")
        self.assertEqual(trace[2]["execution"], "not_run")

    def test_prepare_response_message(self):
        payload = get_base_payload()
        adapter_res = {"adapter_status": "READY_FOR_AGENT_1"}
        res = prepare_sprint_4_safety_routing_response(payload, adapter_res)
        self.assertEqual(res["checkpoint"], "Sprint 4")
        self.assertEqual(
            res["message"],
            "Sprint 4 checkpoint: deterministic safety routing preview completed. Agent workflow has not run yet."
        )
        self.assertEqual(res["safety_precheck"]["release_status"], "APPROVED")

    def test_post_route_valid(self):
        client = TestClient(app)
        response = client.post("/", data={
            "interaction_type": "Vendor delay",
            "frequency": "weekly",
            "minutes_lost": "45",
            "work_disrupted": "Scheduling"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Sprint 4 checkpoint: deterministic safety routing preview completed. Agent workflow has not run yet.",
            response.text
        )
        self.assertIn("Deterministic Precheck", response.text)
        self.assertIn("RENDER_BRIEF", response.text)

    def test_post_route_invalid(self):
        client = TestClient(app)
        response = client.post("/", data={
            "interaction_type": "",
            "frequency": "weekly",
            "minutes_lost": "abc",
            "work_disrupted": "Scheduling"
        })
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("Sprint 4 checkpoint", response.text)
        self.assertIn("Please describe the type", response.text)

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
