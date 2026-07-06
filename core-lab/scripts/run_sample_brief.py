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

"""Local offline demo script for wAI Scenario Lab.

Runs the cool_down_tax sample query and formats the output Scenario Brief.
Does not perform external network calls or require GCP credentials.
"""

import sys
import os
import json

# Ensure core-lab root is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.workflow import run_scenario_lab_sample


def format_brief(brief: dict) -> str:
    """Formats the Scenario Brief dictionary into a readable markdown string."""
    status = brief.get("brief_status", "REVISE")
    
    if status in ["REVISE", "BLOCKED"]:
        return (
            f"=== wAI SCENARIO LAB BRIEF ===\n"
            f"Status: {status}\n"
            f"Message: {brief.get('message', 'No details available.')}\n"
            f"Revision Instructions: {brief.get('revision_instructions', 'N/A')}\n"
            f"=============================="
        )
        
    m = brief.get("measurement", {})
    c = brief.get("episode_cta", {})
    
    lines = [
        f"=== wAI SCENARIO LAB BRIEF (APPROVED) ===",
        f"Result ID: {brief.get('result_id')}",
        f"Scenario: {brief.get('scenario_title')} (Episode {brief.get('episode_number')})",
        f"Generated At: {brief.get('generated_at')}",
        f"",
        f"--- What We Heard ---",
        brief.get("what_we_heard", ""),
        f"",
        f"--- Workflow Friction Point ---",
        brief.get("where_friction_may_be_occurring", ""),
        f"",
        f"--- Assumptions ---",
        "\n".join(f"- {a}" for a in brief.get("assumptions", [])),
        f"",
        f"--- Suggested Next Action (Manual & Bounded) ---",
        f"Action: {brief.get('one_next_step')}",
        f"Rationale: {brief.get('why_this_step')}",
        f"",
        f"--- Observation Measurement ---",
        f"Metric: {m.get('name')}",
        f"Baseline: {m.get('baseline_display')}",
        f"Tracking Period: {m.get('period')}",
        f"Calculation: {m.get('calculation_method')}",
        f"",
        f"--- Unknowns ---",
        "\n".join(f"- {u}" for u in brief.get("unknowns", [])),
        f"",
        f"--- Responsible AI Reminders ---",
        f"Human Review Reminder: {brief.get('human_review_reminder')}",
        f"Responsible Use Limitation: {brief.get('responsible_use_limitation')}",
        f"",
        f"--- Podcast Episode link ---",
        f"{c.get('title')}: {c.get('url')} ({c.get('description')})",
        f"========================================="
    ]
    return "\n".join(lines)


def main():
    print("Running wAI Scenario Lab Local Demo Pipeline...")
    
    # Run the sample payload
    try:
        brief = run_scenario_lab_sample(scenario_id="cool_down_tax")
        print("\nDemo Output:")
        print(format_brief(brief))
    except Exception as e:
        print(f"\nDemo Execution Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

