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

import logging

logger = logging.getLogger(__name__)


def validate_scenario_form(form_data: dict, scenario_config: dict) -> tuple[dict, dict]:
    """Validates the scenario questionnaire fields against the active scenario configuration.

    Args:
        form_data: Raw dictionary of form submission values (usually strings).
        scenario_config: The scenario configuration dictionary.

    Returns:
        A tuple of (normalized_answers, field_errors), where:
        - normalized_answers: Cleaned/normalized values. Raw values are preserved for invalid inputs.
        - field_errors: A dictionary mapping field IDs to their validation error messages.
    """
    normalized_answers = {}
    field_errors = {}

    questions = scenario_config.get("questions", [])
    for q in questions:
        q_id = q.get("id")
        q_type = q.get("type")
        required = q.get("required", False)
        validation_msgs = q.get("validation", {})

        raw_val = form_data.get(q_id)
        if raw_val is None:
            raw_val = ""

        # Normalize string representation
        if isinstance(raw_val, str):
            val_stripped = raw_val.strip()
        else:
            val_stripped = str(raw_val).strip()

        # 1. Check Required field & Whitespace-only
        if required:
            if raw_val == "":
                field_errors[q_id] = validation_msgs.get("required") or "This field is required."
                normalized_answers[q_id] = raw_val
                continue
            elif val_stripped == "":
                field_errors[q_id] = validation_msgs.get("whitespace_only") or "Please enter a response rather than spaces only."
                normalized_answers[q_id] = raw_val
                continue

        # If not required and empty, save as empty string and continue
        if val_stripped == "":
            normalized_answers[q_id] = ""
            continue

        # 2. Type-specific validations
        if q_type in ("text", "textarea"):
            max_len = q.get("max_length")
            if max_len is not None and len(val_stripped) > max_len:
                field_errors[q_id] = validation_msgs.get("too_long") or f"Please shorten your response to {max_len} characters."
                normalized_answers[q_id] = raw_val
            else:
                normalized_answers[q_id] = val_stripped

        elif q_type in ("radio", "select"):
            options = q.get("options", [])
            allowed_values = [opt.get("value") for opt in options]
            if val_stripped not in allowed_values:
                field_errors[q_id] = validation_msgs.get("selection_reminder") or "Please select a valid option."
                normalized_answers[q_id] = raw_val
            else:
                normalized_answers[q_id] = val_stripped

        elif q_type == "number":
            try:
                # Parse as float first to check numeric representation
                val_float = float(val_stripped)

                # Check "Use whole numbers only."
                if not val_float.is_integer():
                    field_errors[q_id] = validation_msgs.get("whole_number") or "Please enter a whole number."
                    normalized_answers[q_id] = raw_val
                    continue

                val_int = int(val_float)

                # Check "Reject negative values."
                if val_int < 0:
                    field_errors[q_id] = validation_msgs.get("below_min") or "Please enter a value of 0 or more."
                    normalized_answers[q_id] = raw_val
                    continue

                min_val = q.get("min")
                max_val = q.get("max")

                if min_val is not None and val_int < min_val:
                    field_errors[q_id] = validation_msgs.get("below_min") or f"Please enter a value of {min_val} or more."
                    normalized_answers[q_id] = raw_val
                elif max_val is not None and val_int > max_val:
                    field_errors[q_id] = validation_msgs.get("above_max") or f"Please enter a value between {min_val or 0} and {max_val}."
                    normalized_answers[q_id] = raw_val
                else:
                    normalized_answers[q_id] = val_int

            except ValueError:
                field_errors[q_id] = validation_msgs.get("non_numeric") or "Please enter a number using digits only."
                normalized_answers[q_id] = raw_val

    return normalized_answers, field_errors


def build_workflow_payload(scenario_config: dict, normalized_answers: dict) -> dict:
    """Builds a normalized payload used to trigger the multi-agent workflow.

    Args:
        scenario_config: Loaded specific scenario config dictionary.
        normalized_answers: Validated and normalized user responses.

    Returns:
        A dictionary containing scenario metadata and normalized answers.
    """
    return {
        "scenario_id": scenario_config.get("scenario_id"),
        "episode_number": scenario_config.get("episode_number"),
        "scenario_title": scenario_config.get("title"),
        "answers": normalized_answers,
        "scenario_context": {
            "short_description": scenario_config.get("short_description"),
            "context": scenario_config.get("context"),
            "measurement_preview": scenario_config.get("measurement_preview")
        }
    }


# Backward compatibility aliases for tests
validate_episode_01_form = validate_scenario_form
build_episode_01_workflow_payload = build_workflow_payload


