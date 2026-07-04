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

"""Scenario Brief Assembler Service.

Responsible for merging agent outputs, applying configuration disclosures/CTAs,
and validating the final ScenarioBrief using Pydantic contracts.
Ensures REVISE/BLOCKED paths never leak brief details.
"""

import uuid
from datetime import datetime
from typing import Any, Union
from pydantic import BaseModel

from app.schemas import (
    ScenarioBrief,
    Measurement as SchemaMeasurement,
    Redaction,
    EpisodeCTA
)
from app.services.safety import sanitize_text

# TODO: Jason to refine Agent 3 measurement and Agent 4 release rules in Phase 4.


def assemble_brief(
    scenario_config: dict,
    sanitized_input: Union[BaseModel, dict[str, Any]],
    analysis_state: Union[BaseModel, dict[str, Any]],
    calculation_state: Union[BaseModel, dict[str, Any]],
    safety_review: Union[BaseModel, dict[str, Any]],
    required_disclosures: dict[str, Any]
) -> dict[str, Any]:
    """Assembles a ScenarioBrief from agent states and scenario config.

    If safety review status is REVISE or BLOCKED, details are withheld to prevent unsafe rendering.
    """
    # Normalize inputs to dictionaries
    inp = sanitized_input.model_dump() if isinstance(sanitized_input, BaseModel) else dict(sanitized_input)
    ana = analysis_state.model_dump() if isinstance(analysis_state, BaseModel) else dict(analysis_state)
    calc = calculation_state.model_dump() if isinstance(calculation_state, BaseModel) else dict(calculation_state)
    safe = safety_review.model_dump() if isinstance(safety_review, BaseModel) else dict(safety_review)

    status = safe.get("release_status", "REVISE")

    # Non-approved paths must not render completed Scenario Brief sections
    if status in ["REVISE", "BLOCKED"]:
        return {
            "brief_status": status,
            "message": "Scenario Brief was not approved or requires revision. Details withheld.",
            "revision_instructions": safe.get("revision_instructions", "") if status == "REVISE" else ""
        }

    # Sanitize what we heard to ensure no PII is repeated in output
    raw_problem = inp.get("stated_problem", "")
    sanitized_problem = sanitize_text(raw_problem)
    frequency = inp.get("frequency", "weekly")
    time_loss = inp.get("estimated_time_loss", 0)

    # Build "what we heard" summary
    what_we_heard = (
        f"Stated frustration: {sanitized_problem}. "
        f"Time overhead: {time_loss} minutes per incident, occurring {frequency}."
    )

    # Build Measurement sub-model (Exactly one measurement)
    measurement_obj = SchemaMeasurement(
        name=calc.get("recommended_measure", "Observation measure"),
        baseline_value=calc.get("baseline_value"),
        baseline_display=calc.get("baseline_display", f"{time_loss} minutes"),
        unit=calc.get("measure_unit", "minutes"),
        period=calc.get("measurement_period", "Track the next three incidents."),
        calculation_method=calc.get("calculation_method", "Use the reported time loss."),
        evidence_strength=calc.get("evidence_strength", "strong"),
        is_fallback=calc.get("insufficient_data_flag", False)
    )

    # Build Redaction metadata
    # True if safety evaluation detected sensitive data or redacted PII
    redaction_applied = safe.get("sensitive_data_detected", False)
    redaction_obj = Redaction(
        applied=redaction_applied,
        categories=safe.get("redaction_categories", []) if redaction_applied else []
    )

    # Build Episode CTA from config, NOT from agent generation
    cta_config = scenario_config.get("episode_cta", {})
    episode_cta_obj = EpisodeCTA(
        title=cta_config.get("title", "Learn More"),
        description=cta_config.get("description", "Explore this scenario in the wAI podcast."),
        url=cta_config.get("url", "https://www.startwithwai.tech/")
    )

    # Build human-review and responsible-use text from config
    human_review = required_disclosures.get("human_review_reminder", "")
    responsible_use = required_disclosures.get("responsible_use_limitation", "")

    # Combine all fields into ScenarioBrief. Let Pydantic validate the structure.
    brief = ScenarioBrief(
        result_id=f"res_{uuid.uuid4().hex[:8]}",
        scenario_id=scenario_config.get("scenario_id", inp.get("scenario_id")),
        scenario_title=scenario_config.get("title", "Scenario Title"),
        episode_number=scenario_config.get("episode_number", "00"),
        brief_status=status,
        generated_at=datetime.utcnow(),
        what_we_heard=what_we_heard,
        where_friction_may_be_occurring=ana.get("friction_summary"),
        assumptions=ana.get("assumptions", []),
        one_next_step=ana.get("proposed_next_action"),
        why_this_step=ana.get("action_rationale"),
        measurement=measurement_obj,
        unknowns=ana.get("unknowns", []),
        redaction=redaction_obj,
        human_review_reminder=human_review,
        responsible_use_limitation=responsible_use,
        episode_cta=episode_cta_obj
    )

    return brief.model_dump(mode="json")
