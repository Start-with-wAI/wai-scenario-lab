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
from unittest.mock import patch, mock_open
import json

from app.config_loader import (
    load_scenario_config,
    get_public_episode_01_config,
    render_question_html,
    render_episode_01_page,
    ConfigLoadError,
)


class TestConfigLoader(unittest.TestCase):

    def test_load_scenario_config_success(self):
        # Test loading the actual configuration file in the project
        config = load_scenario_config()
        self.assertIsInstance(config, dict)
        self.assertIn("app", config)
        self.assertIn("shared_ui", config)
        self.assertIn("scenarios", config)

    @patch("os.path.exists", return_value=False)
    def test_load_scenario_config_missing_file(self, mock_exists):
        with self.assertRaises(ConfigLoadError) as ctx:
            load_scenario_config()
        self.assertIn("missing", str(ctx.exception).lower())

    @patch("builtins.open", new_callable=mock_open, read_data="invalid json {")
    @patch("os.path.exists", return_value=True)
    def test_load_scenario_config_malformed_json(self, mock_exists, mock_file):
        with self.assertRaises(ConfigLoadError) as ctx:
            load_scenario_config()
        self.assertIn("malformed", str(ctx.exception).lower())

    def test_get_public_episode_01_config_success(self):
        config = get_public_episode_01_config()
        self.assertIn("app", config)
        self.assertIn("shared_ui", config)
        self.assertIn("scenario", config)
        self.assertEqual(config["scenario"]["scenario_id"], "cool_down_tax")
        self.assertEqual(config["scenario"]["episode_number"], "01")

    def test_render_question_html_text(self):
        q = {
            "id": "test_text",
            "type": "text",
            "label": "Test Text Label",
            "help_text": "Help text here",
            "required": True,
            "max_length": 100,
        }
        html = render_question_html(q)
        self.assertIn('type="text"', html)
        self.assertIn('id="test_text"', html)
        self.assertIn('name="test_text"', html)
        self.assertIn('required', html)
        self.assertIn('maxlength="100"', html)
        self.assertIn("Test Text Label", html)
        self.assertIn("Help text here", html)

    def test_render_question_html_textarea(self):
        q = {
            "id": "test_area",
            "type": "textarea",
            "label": "Test Area Label",
            "required": False,
            "max_length": 500,
        }
        html = render_question_html(q)
        self.assertIn("<textarea", html)
        self.assertIn('id="test_area"', html)
        self.assertNotIn("required", html)
        self.assertIn('maxlength="500"', html)

    def test_render_question_html_number(self):
        q = {
            "id": "test_num",
            "type": "number",
            "label": "Test Num Label",
            "required": True,
            "min": 0,
            "max": 10,
            "step": 1,
            "unit": "clicks",
        }
        html = render_question_html(q)
        self.assertIn('type="number"', html)
        self.assertIn('id="test_num"', html)
        self.assertIn('min="0"', html)
        self.assertIn('max="10"', html)
        self.assertIn('step="1"', html)
        self.assertIn("clicks", html)

    def test_render_question_html_radio(self):
        q = {
            "id": "test_radio",
            "type": "radio",
            "label": "Test Radio Label",
            "required": True,
            "options": [
                {"value": "opt1", "label": "Option 1"},
                {"value": "opt2", "label": "Option 2"},
            ],
        }
        html = render_question_html(q)
        self.assertIn("<fieldset", html)
        self.assertIn('type="radio"', html)
        self.assertIn('value="opt1"', html)
        self.assertIn("Option 1", html)

    def test_render_episode_01_page(self):
        config = {
            "app": {"name": "Test App Name"},
            "shared_ui": {
                "landing_headline": "Test Headline",
                "landing_supporting_copy": "Test Supporting Copy",
                "privacy_notice": "Test Privacy Notice",
                "transparency_notice": "Test Transparency Notice",
                "question_submit_label": "Submit Btn",
            },
            "scenario": {
                "title": "Test Scenario Title",
                "episode_number": "01",
                "short_description": "Test Episode Desc",
                "context": "Test Context Info",
                "measurement_preview": "Test Measure Preview",
                "questions": [
                    {
                        "id": "q1",
                        "type": "text",
                        "label": "Q1 Label",
                        "required": True,
                    }
                ],
            },
        }
        html = render_episode_01_page(config)
        self.assertIn("Test App Name", html)
        self.assertIn("Test Headline", html)
        self.assertIn("Test Privacy Notice", html)
        self.assertIn("Test Transparency Notice", html)
        self.assertIn("Test Scenario Title", html)
        self.assertIn("Test Episode Desc", html)
        self.assertIn("Test Measure Preview", html)
        self.assertIn("Q1 Label", html)
        self.assertIn("Submit Btn", html)

    def test_root_route_success(self):
        from fastapi.testclient import TestClient
        from app.fast_api_app import app

        client = TestClient(app)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("The Cool Down Tax", response.text)
        self.assertIn("interaction_type", response.text)
        self.assertIn("frequency", response.text)
        self.assertIn("minutes_lost", response.text)
        self.assertIn("work_disrupted", response.text)

