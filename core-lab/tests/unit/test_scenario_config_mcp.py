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

import pytest
from mcp_server.scenario_config_server import (
    _load_config,
    list_available_scenarios,
    get_scenario_metadata,
    get_scenario_questions,
    get_scenario_measurement,
    select_observation_measure
)


def test_config_loading():
    config = _load_config()
    assert "scenarios" in config
    assert "cool_down_tax" in config["scenarios"]
    assert "brain_fog" in config["scenarios"]
    assert "blank_page" in config["scenarios"]


def test_scenario_questions_count():
    for sid in ["cool_down_tax", "brain_fog", "blank_page"]:
        questions = get_scenario_questions(sid)
        assert len(questions) == 4, f"Scenario '{sid}' must have exactly four questions"


def test_get_scenario_metadata():
    metadata = get_scenario_metadata("cool_down_tax")
    assert metadata["scenario_id"] == "cool_down_tax"
    assert "title" in metadata
    assert "short_description" in metadata
    assert "context" in metadata


def test_get_scenario_measurement():
    measurement = get_scenario_measurement("brain_fog")
    assert "primary" in measurement
    assert "fallback" in measurement


def test_select_observation_measure():
    # Test primary
    measure = select_observation_measure("cool_down_tax", use_fallback=False)
    assert measure["is_fallback"] is False
    assert "unit" in measure
    assert "calculation_method" in measure

    # Test fallback
    fallback_measure = select_observation_measure("cool_down_tax", use_fallback=True)
    assert fallback_measure["is_fallback"] is True
    assert fallback_measure["name"] == "Number of stressful interactions"

    # Verify no financial terms exist in the selected metrics
    for metric in [measure, fallback_measure]:
        for val in (metric["name"], metric["calculation_method"], metric["tracking_period"]):
            v_low = val.lower()
            assert not any(bad in v_low for bad in ["$", "roi", "dollar", "savings", "cost", "equity", "annual value", "five-year value"]), \
                f"Financial term found in selected measure: {val}"

