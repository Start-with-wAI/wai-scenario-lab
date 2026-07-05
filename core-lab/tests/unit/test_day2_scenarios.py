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
from app.config_loader import load_scenario_config
from app.form_validation import validate_scenario_form


class TestDay2Scenarios(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.config = load_scenario_config()

    def test_config_loading_and_question_counts(self):
        """Verify that all three MVP scenarios are loaded with exactly 4 questions each."""
        scenarios = self.config.get("scenarios", {})
        self.assertIn("cool_down_tax", scenarios)
        self.assertIn("brain_fog", scenarios)
        self.assertIn("blank_page", scenarios)

        # Verify question counts (each should have exactly 4 questions)
        self.assertEqual(len(scenarios["cool_down_tax"].get("questions", [])), 4)
        self.assertEqual(len(scenarios["brain_fog"].get("questions", [])), 4)
        self.assertEqual(len(scenarios["blank_page"].get("questions", [])), 4)

    def test_form_validation_cool_down_tax(self):
        """Verify form validation for the Cool Down Tax scenario."""
        scenario_config = self.config["scenarios"]["cool_down_tax"]
        
        # Valid data
        valid_answers = {
            "interaction_type": "Daily standup meeting sync",
            "frequency": "weekly",
            "minutes_lost": "30",
            "work_disrupted": "Coding tasks"
        }
        answers, errors = validate_scenario_form(valid_answers, scenario_config)
        self.assertEqual(errors, {})
        self.assertEqual(answers["minutes_lost"], 30)

        # Invalid minutes_lost
        invalid_answers = valid_answers.copy()
        invalid_answers["minutes_lost"] = "abc"
        answers, errors = validate_scenario_form(invalid_answers, scenario_config)
        self.assertIn("minutes_lost", errors)

    def test_form_validation_brain_fog(self):
        """Verify form validation for the Brain Fog scenario."""
        scenario_config = self.config["scenarios"]["brain_fog"]
        
        # Valid data
        valid_answers = {
            "idea_context": "Away from desk",
            "current_capture_method": "Notes app",
            "ideas_lost_weekly": "5",
            "capture_constraint": "Too many steps"
        }
        answers, errors = validate_scenario_form(valid_answers, scenario_config)
        self.assertEqual(errors, {})
        self.assertEqual(answers["ideas_lost_weekly"], 5)

        # Missing required ideas_lost_weekly
        invalid_answers = valid_answers.copy()
        invalid_answers["ideas_lost_weekly"] = ""
        answers, errors = validate_scenario_form(invalid_answers, scenario_config)
        self.assertIn("ideas_lost_weekly", errors)

    def test_form_validation_blank_page(self):
        """Verify form validation for the Blank Page scenario."""
        scenario_config = self.config["scenarios"]["blank_page"]
        
        # Valid data
        valid_answers = {
            "content_type": "Social post",
            "source_material": "Past emails",
            "minutes_to_start": "60",
            "starting_difficulty": "writing_opening"
        }
        answers, errors = validate_scenario_form(valid_answers, scenario_config)
        self.assertEqual(errors, {})
        self.assertEqual(answers["minutes_to_start"], 60)

        # Invalid starting_difficulty select choice
        invalid_answers = valid_answers.copy()
        invalid_answers["starting_difficulty"] = "invalid_difficulty"
        answers, errors = validate_scenario_form(invalid_answers, scenario_config)
        self.assertIn("starting_difficulty", errors)

    def test_api_analyze_e2e_approved(self):
        """E2E test: Verify that valid inputs yield an APPROVED state."""
        response = self.client.post("/api/analyze", json={
            "scenario_id": "cool_down_tax",
            "answers": {
                "interaction_type": "Code reviews with QA team",
                "frequency": "weekly",
                "minutes_lost": "20",
                "work_disrupted": "Refactoring code"
            }
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["scenario_id"], "cool_down_tax")
        self.assertEqual(data["brief_status"], "APPROVED")
        self.assertIn("what_we_heard", data)
        self.assertIn("one_next_step", data)

    def test_api_analyze_e2e_revise(self):
        """E2E test: Verify that containing absolute certainty words triggers REVISE state."""
        response = self.client.post("/api/analyze", json={
            "scenario_id": "cool_down_tax",
            "answers": {
                "interaction_type": "This is definitely a massive issue, it always fails and is guaranteed to ruin our build.",
                "frequency": "weekly",
                "minutes_lost": "30",
                "work_disrupted": "Testing"
            }
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["brief_status"], "REVISE")
        self.assertIn("revision_instructions", data)
        self.assertIn("words like 'definitely', 'always', 'guaranteed'", data["revision_instructions"])

    def test_api_analyze_e2e_blocked(self):
        """E2E test: Verify that containing prompt injection / adversarial words yields BLOCKED state."""
        response = self.client.post("/api/analyze", json={
            "scenario_id": "cool_down_tax",
            "answers": {
                "interaction_type": "I need urgent legal advice regarding a lawsuit or court dispute.",
                "frequency": "weekly",
                "minutes_lost": "30",
                "work_disrupted": "Testing"
            }
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["brief_status"], "BLOCKED")
