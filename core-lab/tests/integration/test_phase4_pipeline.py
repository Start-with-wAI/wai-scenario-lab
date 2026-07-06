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
from app.workflow import run_scenario_lab_sample


def test_integration_pipeline_approved():
    answers = {
        "interaction_type": "Vendor delays with little notice",
        "frequency": "weekly",
        "minutes_lost": 45,
        "work_disrupted": "Project follow-up and scheduling"
    }
    
    brief = run_scenario_lab_sample("cool_down_tax", answers=answers)
    
    assert brief["brief_status"] == "APPROVED"
    assert "result_id" in brief
    assert "one_next_step" in brief
    assert "measurement" in brief
    assert "human_review_reminder" in brief
    assert "responsible_use_limitation" in brief


def test_integration_pipeline_approved_with_limitation():
    answers = {
        "interaction_type": "Vendor delays in an unusual project type",
        "frequency": "weekly",
        "minutes_lost": 45,
        "work_disrupted": "Project follow-up and scheduling"
    }
    
    brief = run_scenario_lab_sample("cool_down_tax", answers=answers)
    
    assert brief["brief_status"] == "APPROVED_WITH_LIMITATION"
    assert "one_next_step" in brief


def test_integration_pipeline_blocked_by_high_risk_domain():
    # Mentions "lawsuit" (legal domain) which should trigger BLOCKED state
    answers = {
        "interaction_type": "Vendor delays triggering a lawsuit threat",
        "frequency": "weekly",
        "minutes_lost": 45,
        "work_disrupted": "Project follow-up and scheduling"
    }
    
    brief = run_scenario_lab_sample("cool_down_tax", answers=answers)
    
    assert brief["brief_status"] == "BLOCKED"
    assert "one_next_step" not in brief
    assert "message" in brief


def test_integration_pipeline_revised_by_sensitive_data():
    # Mentions email address which should trigger REVISE state
    answers = {
        "interaction_type": "Vendor delays from alice@vendor.com",
        "frequency": "weekly",
        "minutes_lost": 45,
        "work_disrupted": "Project follow-up and scheduling"
    }
    
    brief = run_scenario_lab_sample("cool_down_tax", answers=answers)
    
    assert brief["brief_status"] == "REVISE"
    assert "one_next_step" not in brief
    assert "message" in brief
    assert brief["revision_instructions"] != ""


def test_integration_pipeline_revised_by_unsupported_roi_claims():
    # Mentions ROI which should trigger REVISE state
    answers = {
        "interaction_type": "Vendor delays causing loss of 30% ROI",
        "frequency": "weekly",
        "minutes_lost": 45,
        "work_disrupted": "Project follow-up and scheduling"
    }
    
    brief = run_scenario_lab_sample("cool_down_tax", answers=answers)
    
    assert brief["brief_status"] == "REVISE"
    assert "one_next_step" not in brief
    assert "message" in brief

