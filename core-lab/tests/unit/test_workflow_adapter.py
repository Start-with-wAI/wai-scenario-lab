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
from app.workflow_adapter import (
    build_agent_1_input,
    build_graph_transition_trace,
    prepare_episode_01_workflow_adapter_response,
    WorkflowAdapterError,
)


def get_valid_payload():
    return {
        "scenario_id": "cool_down_tax",
        "episode_number": "01",
        "scenario_title": "The Cool Down Tax",
        "answers": {
            "interaction_type": "Vendor delay",
            "frequency": "weekly",
            "minutes_lost": 45,
            "work_disrupted": "Project follow-up and scheduling"
        },
        "scenario_context": {
            "short_description": "Mock short description",
            "context": "Mock context details",
            "measurement_preview": "Recovery time per incident"
        }
    }


class TestWorkflowAdapter(unittest.TestCase):

    def test_build_agent_1_input_valid(self):
        payload = get_valid_payload()
        res = build_agent_1_input(payload)
        self.assertEqual(res["adapter_status"], "READY_FOR_AGENT_1")
        self.assertEqual(res["scenario_id"], "cool_down_tax")
        self.assertEqual(res["user_answers"]["minutes_lost"], 45)
        self.assertEqual(res["selected_scenario"]["title"], "The Cool Down Tax")
        self.assertEqual(res["selected_scenario"]["measurement_preview"], "Recovery time per incident")

    def test_build_agent_1_input_missing_scenario_id(self):
        payload = get_valid_payload()
        del payload["scenario_id"]
        with self.assertRaises(WorkflowAdapterError) as ctx:
            build_agent_1_input(payload)
        self.assertIn("Missing required payload key: 'scenario_id'", str(ctx.exception))

    def test_build_agent_1_input_missing_answers(self):
        payload = get_valid_payload()
        del payload["answers"]
        with self.assertRaises(WorkflowAdapterError) as ctx:
            build_agent_1_input(payload)
        self.assertIn("Missing required payload key: 'answers'", str(ctx.exception))

    def test_build_agent_1_input_missing_minutes_lost_in_answers(self):
        payload = get_valid_payload()
        del payload["answers"]["minutes_lost"]
        with self.assertRaises(WorkflowAdapterError) as ctx:
            build_agent_1_input(payload)
        self.assertIn("Missing required answer key: 'minutes_lost'", str(ctx.exception))

    def test_build_graph_transition_trace(self):
        payload = get_valid_payload()
        trace = build_graph_transition_trace(payload)
        self.assertEqual(len(trace), 7)
        
        # Verify transition sequence
        expected_nodes = [
            "START",
            "scenario_guide_agent",
            "workflow_analyst_agent",
            "value_evidence_agent",
            "safety_quality_agent",
            "evaluate_safety_gate",
            "terminal_route_pending"
        ]
        
        for idx, node_name in enumerate(expected_nodes):
            self.assertEqual(trace[idx]["node"], node_name)
            self.assertEqual(trace[idx]["execution"], "not_run")
            self.assertEqual(trace[idx]["step"], idx + 1)

    def test_prepare_response_checkpoint_message(self):
        payload = get_valid_payload()
        res = prepare_episode_01_workflow_adapter_response(payload)
        self.assertEqual(res["checkpoint"], "Sprint 3")
        self.assertEqual(
            res["message"],
            "Sprint 3 checkpoint: normalized input prepared for workflow adapter. Agent workflow has not run yet."
        )
        self.assertEqual(res["adapter_status"], "READY_FOR_AGENT_1")
        self.assertIn("Gemini model calls", res["not_run"])

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
            "Sprint 5 checkpoint: terminal output assembly completed. Live agent workflow has not run yet.",
            response.text
        )
        self.assertIn("READY_FOR_AGENT_1", response.text)
        self.assertIn("RENDER_BRIEF", response.text)
        self.assertIn("safety_precheck", response.text)

    def test_post_route_invalid(self):
        client = TestClient(app)
        response = client.post("/", data={
            "interaction_type": "",
            "frequency": "weekly",
            "minutes_lost": "abc",
            "work_disrupted": "Scheduling"
        })
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("Sprint 3 checkpoint", response.text)
        self.assertNotIn("READY_FOR_AGENT_1", response.text)
        self.assertIn("Please describe the type", response.text)
        self.assertIn("digits only", response.text)

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
