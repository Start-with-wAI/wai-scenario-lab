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

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator


def _clean_string_list(values: List[str]) -> List[str]:
    """Trim, de-duplicate, and remove empty entries from string lists."""
    cleaned: List[str] = []
    seen: set[str] = set()

    for item in values:
        normalized = item.strip()
        if not normalized:
            continue

        key = normalized.casefold()
        if key not in seen:
            seen.add(key)
            cleaned.append(normalized)

    return cleaned


def _validate_cautious_language(value: str) -> str:
    """Enforce cautious, evidence-limited language and reject absolute statements."""
    normalized = value.strip().casefold()
    prohibited_openings = (
        "the real reason",
        "we determined",
        "you definitely",
        "this proves",
        "the cause is",
    )
    if any(normalized.startswith(opening) for opening in prohibited_openings):
        raise ValueError(
            "must use cautious, evidence-limited language starting openings"
        )
    
    prohibited_words = {"definitely", "always", "guaranteed", "proven"}
    words = set(re.findall(r"\b\w+\b", normalized))
    if prohibited_words & words:
        raise ValueError(
            "must use cautious language; do not use absolute certainty words like "
            "'definitely', 'always', 'guaranteed', or 'proven'"
        )
    return value


class ScenarioInputState(BaseModel):
    """Initial user answers gathered by Verónica's Agent 1: Scenario Guide."""

    scenario_id: str = Field(
        ...,
        min_length=1,
        max_length=80,
        description="Stable identifier for the selected scenario.",
    )
    stated_problem: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Concise summary of the workflow problem stated by the user.",
    )
    frequency: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Reported frequency or configured frequency option.",
    )
    estimated_time_loss: Optional[int] = Field(
        default=None,
        ge=0,
        le=480,
        description="Validated estimated minutes lost, when provided.",
    )
    current_process: Optional[str] = Field(
        default=None,
        max_length=500,
        description="User's current method or process, when stated.",
    )
    primary_constraint: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Main obstacle explicitly supported by the user's answers.",
    )
    available_tools: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Tools or devices explicitly mentioned by the user.",
    )
    missing_information: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Material information that remains unknown.",
    )

    @field_validator("scenario_id")
    @classmethod
    def validate_scenario_id(cls, value: str) -> str:
        """Restrict scenario IDs to lowercase letters, numbers, and underscores."""
        normalized = value.strip()
        if not normalized.replace("_", "").isalnum() or normalized.lower() != normalized:
            raise ValueError(
                "scenario_id must use lowercase letters, numbers, and underscores only"
            )
        return normalized

    @field_validator("available_tools", "missing_information")
    @classmethod
    def clean_lists(cls, values: List[str]) -> List[str]:
        return _clean_string_list(values)


class AnalysisState(BaseModel):
    """Workflow breakdown produced by Verónica's Agent 2: Workflow Analysis."""

    friction_summary: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="One cautious workflow observation grounded in Agent 1's facts.",
    )
    workflow_stage: str = Field(
        ...,
        min_length=1,
        max_length=160,
        description="The single process stage or transition where friction may occur.",
    )
    known_facts: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="Sanitized, verifiable facts from the user's input.",
    )
    assumptions: List[str] = Field(
        default_factory=list,
        max_length=2,
        description="Zero to two clearly labeled assumptions.",
    )
    constraints: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="The user's stated operational or financial limits.",
    )
    unknowns: List[str] = Field(
        default_factory=list,
        max_length=3,
        description="Material information that remains unknown.",
    )
    proposed_next_action: str = Field(
        ...,
        min_length=1,
        max_length=350,
        description="Exactly one low-risk, reversible, or observational next action.",
    )
    action_rationale: str = Field(
        ...,
        min_length=1,
        max_length=280,
        description="One sentence connecting the proposed action to the stated friction.",
    )

    @field_validator("known_facts", "assumptions", "constraints", "unknowns")
    @classmethod
    def clean_lists(cls, values: List[str]) -> List[str]:
        return _clean_string_list(values)

    @field_validator("assumptions")
    @classmethod
    def limit_assumptions(cls, values: List[str]) -> List[str]:
        if len(values) > 2:
            raise ValueError("assumptions may contain no more than two items")
        return values

    @field_validator("unknowns")
    @classmethod
    def limit_unknowns(cls, values: List[str]) -> List[str]:
        if len(values) > 3:
            raise ValueError("unknowns may contain no more than three items")
        return values

    @field_validator("friction_summary")
    @classmethod
    def validate_friction_cautious(cls, value: str) -> str:
        return _validate_cautious_language(value)

    @field_validator("proposed_next_action")
    @classmethod
    def enforce_single_action(cls, value: str) -> str:
        normalized = value.strip()

        # Check for numbered/sequenced lists
        if re.search(r"(^|\s)(1\.|2\.|3\.|first,|second,|third,)", normalized, re.I):
            raise ValueError(
                "proposed_next_action must not contain a numbered or sequenced plan"
            )

        # Check for bullet points
        if "\n-" in normalized or "\n*" in normalized:
            raise ValueError(
                "proposed_next_action must contain one action, not a bullet list"
            )

        # Check single sentence
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", normalized)
            if s.strip()
        ]
        if len(sentences) > 1:
            raise ValueError(
                "proposed_next_action must be expressed as one concise action sentence"
            )

        # Check word count limit
        if len(normalized.split()) > 50:
            raise ValueError("proposed_next_action must not exceed 50 words")

        return normalized

    @field_validator("action_rationale")
    @classmethod
    def require_single_sentence_rationale(cls, value: str) -> str:
        normalized = value.strip()
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", normalized)
            if s.strip()
        ]
        if len(sentences) > 1:
            raise ValueError("action_rationale must contain exactly one sentence")
        
        # Check word count limit
        if len(normalized.split()) > 35:
            raise ValueError("action_rationale must not exceed 35 words")
            
        return normalized

    @model_validator(mode="after")
    def separate_categories(self) -> AnalysisState:
        """Prevent same statement from appearing in conflicting categories."""
        fact_keys = {item.casefold() for item in self.known_facts}
        assumption_keys = {item.casefold() for item in self.assumptions}
        unknown_keys = {item.casefold() for item in self.unknowns}

        if fact_keys & assumption_keys:
            raise ValueError("the same statement cannot be both a known fact and an assumption")
        if fact_keys & unknown_keys:
            raise ValueError("the same statement cannot be both a known fact and an unknown")
        if assumption_keys & unknown_keys:
            raise ValueError("the same statement cannot be both an assumption and an unknown")

        return self


class CalculationState(BaseModel):
    """Quantitative evaluation and metrics validated by Jason's Agent 3: Value and Evidence."""

    recommended_measure: str = Field(..., description="The primary or fallback metric to track.")
    measure_unit: str = Field(..., description="Unit of measurement (e.g., minutes, ideas, attempts).")
    baseline_value: Optional[float] = Field(None, description="Calculated starting value from the FastMCP tool.")
    baseline_display: str = Field(..., description="User-facing display string of the starting baseline.")
    calculation_method: str = Field(..., description="Plain-language tracking instructions for the user.")
    assumptions: List[str] = Field(..., description="Mathematical or timing assumptions used.")
    evidence_strength: str = Field(..., description="Rating: strong, partial, or insufficient.")
    measurement_period: str = Field(..., description="Suggested observation timeframe.")
    insufficient_data_flag: bool = Field(False, description="True if fallback measure was triggered.")

    @field_validator("evidence_strength")
    @classmethod
    def validate_evidence_strength(cls, value: str) -> str:
        allowed = {"strong", "partial", "insufficient"}
        if value not in allowed:
            raise ValueError(f"evidence_strength must be one of {allowed}, got '{value}'")
        return value


class SafetyReviewState(BaseModel):
    """The final safety, privacy, and compliance gate enforced by Jason's Agent 4: Safety and Quality Review."""

    privacy_status: str = Field(..., description="Verification of PII and identifier redaction.")
    sensitive_data_detected: bool = Field(False, description="True if unauthorized PII was flagged.")
    unsupported_claims: bool = Field(False, description="True if LLM attempted to invent savings or ROI.")
    scope_violation: bool = Field(False, description="True if user requested out-of-scope advice.")
    high_risk_domain_flag: bool = Field(False, description="True if medical, tax, or legal topics were detected.")
    human_review_present: bool = Field(True, description="Confirms presence of the mandatory human pilot notice.")
    required_disclosures_present: bool = Field(True, description="Confirms presence of the responsible AI disclaimer.")
    quality_score: int = Field(..., ge=1, le=10, description="Overall structural quality score.")
    release_status: str = Field(..., description="Status: APPROVED, APPROVED_WITH_LIMITATION, REVISE, or BLOCKED.")
    revision_instructions: Optional[str] = Field("", description="Required corrections if state is REVISE.")

    @field_validator("release_status")
    @classmethod
    def validate_release_status(cls, value: str) -> str:
        allowed = {"APPROVED", "APPROVED_WITH_LIMITATION", "REVISE", "BLOCKED"}
        if value not in allowed:
            raise ValueError(f"release_status must be one of {allowed}, got '{value}'")
        return value


class Measurement(BaseModel):
    """Quantitative measurement details embedded within a Scenario Brief."""

    name: str = Field(..., description="Name of the measurement.")
    baseline_value: Optional[float] = Field(None, description="Starting quantitative baseline.")
    baseline_display: str = Field(..., description="Formatted baseline string.")
    unit: str = Field(..., description="Unit of measurement.")
    period: str = Field(..., description="Timeframe for the measurement.")
    calculation_method: str = Field(..., description="Method used to calculate the metric.")
    evidence_strength: str = Field(..., description="Rating: strong, partial, or insufficient.")
    is_fallback: bool = Field(..., description="Indicates if fallback metric is used.")

    @field_validator("evidence_strength")
    @classmethod
    def validate_evidence_strength(cls, value: str) -> str:
        allowed = {"strong", "partial", "insufficient"}
        if value not in allowed:
            raise ValueError(f"evidence_strength must be one of {allowed}")
        return value


class Redaction(BaseModel):
    """Metadata detailing any PII or sensitive data redaction applied."""

    applied: bool = Field(..., description="Indicates if redaction was applied.")
    categories: List[str] = Field(default_factory=list, description="Categories of data redacted.")


class EpisodeCTA(BaseModel):
    """Call to Action link linking the scenario to the corresponding podcast episode."""

    title: str = Field(..., description="Title of the CTA.")
    description: str = Field(..., description="Brief description of the episode context.")
    url: str = Field(..., description="Web URL to listen or learn more.")


class ScenarioBrief(BaseModel):
    """Structured publication-ready Scenario Brief outcome."""

    result_id: str = Field(..., description="Unique output execution tracking ID.")
    scenario_id: str = Field(..., description="Selected scenario identifier.")
    scenario_title: str = Field(..., description="Title of the podcast episode scenario.")
    episode_number: str = Field(..., description="Episode number.")
    brief_status: str = Field(..., description="Must be APPROVED or APPROVED_WITH_LIMITATION.")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp.")
    what_we_heard: str = Field(..., description="Sanitized, grounded recap of the user prompt.")
    where_friction_may_be_occurring: str = Field(..., description="Cautious workflow observation summary.")
    assumptions: List[str] = Field(..., max_length=2, description="List of at most two assumptions.")
    one_next_step: str = Field(..., description="Exactly one low-risk, manual observational action.")
    why_this_step: str = Field(..., description="Single sentence justification for the proposed step.")
    measurement: Measurement = Field(..., description="Specific baseline measurement metrics.")
    unknowns: List[str] = Field(..., max_length=3, description="List of at most three unknown variables.")
    redaction: Redaction = Field(..., description="PII/sensitive data status.")
    human_review_reminder: str = Field(..., description="Required human-in-the-loop pilot disclosure.")
    responsible_use_limitation: str = Field(..., description="Required responsible AI limitations disclosure.")
    episode_cta: EpisodeCTA = Field(..., description="Reference link to wAI podcast episode.")

    @field_validator("brief_status")
    @classmethod
    def validate_brief_status(cls, value: str) -> str:
        allowed = {"APPROVED", "APPROVED_WITH_LIMITATION"}
        if value not in allowed:
            raise ValueError(
                f"Scenario Brief can only be rendered with APPROVED or APPROVED_WITH_LIMITATION, got '{value}'. "
                "REVISE and BLOCKED statuses must not render a completed Scenario Brief."
            )
        return value

    @field_validator("human_review_reminder", "responsible_use_limitation")
    @classmethod
    def require_disclosures(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Required transparency disclosure is missing or empty.")
        return value.strip()

    @field_validator("assumptions")
    @classmethod
    def check_assumptions_count(cls, values: List[str]) -> List[str]:
        if len(values) > 2:
            raise ValueError("assumptions cannot exceed 2 items")
        return values

    @field_validator("unknowns")
    @classmethod
    def check_unknowns_count(cls, values: List[str]) -> List[str]:
        if len(values) > 3:
            raise ValueError("unknowns cannot exceed 3 items")
        return values

    @field_validator("where_friction_may_be_occurring")
    @classmethod
    def validate_friction_cautious(cls, value: str) -> str:
        return _validate_cautious_language(value)

    @field_validator("one_next_step")
    @classmethod
    def enforce_single_action(cls, value: str) -> str:
        normalized = value.strip()
        if re.search(r"(^|\s)(1\.|2\.|3\.|first,|second,|third,)", normalized, re.I):
            raise ValueError("one_next_step must not contain numbered or sequenced plans")
        if "\n-" in normalized or "\n*" in normalized:
            raise ValueError("one_next_step must not contain bullet points")
        
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", normalized)
            if s.strip()
        ]
        if len(sentences) > 1:
            raise ValueError("one_next_step must be expressed as a single action sentence")
        
        if len(normalized.split()) > 50:
            raise ValueError("one_next_step must not exceed 50 words")
        return normalized

    @field_validator("why_this_step")
    @classmethod
    def enforce_single_rationale_sentence(cls, value: str) -> str:
        normalized = value.strip()
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", normalized)
            if s.strip()
        ]
        if len(sentences) > 1:
            raise ValueError("why_this_step must contain exactly one sentence")
        
        if len(normalized.split()) > 35:
            raise ValueError("why_this_step must not exceed 35 words")
        return normalized
