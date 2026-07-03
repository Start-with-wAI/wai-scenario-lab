from pydantic import BaseModel, Field
from typing import List, Optional

class ScenarioInputState(BaseModel):
    """Initial user answers gathered by Verónica's Agent 1: Scenario Guide."""
    scenario_id: str = Field(..., description="ID of the chosen podcast scenario.")
    stated_problem: str = Field(..., description="The core frustration reported by the user.")
    frequency: str = Field(..., description="Estimated weekly or monthly frequency of the incident.")
    estimated_time_loss: float = Field(..., description="Minutes of productive time lost per occurrence.")
    current_process: str = Field(..., description="How the user currently handles this task.")
    primary_constraint: str = Field(..., description="The main obstacle causing the bottleneck.")
    available_tools: Optional[str] = Field("", description="Any software or tools currently in use.")
    missing_information: Optional[str] = Field("", description="Key facts missing from the initial answers.")

class AnalysisState(BaseModel):
    """Workflow breakdown produced by Verónica's Agent 2: Workflow Analysis."""
    friction_summary: str = Field(..., description="Grounded summary of the operational bottleneck.")
    workflow_stage: str = Field(..., description="Specific stage of the workflow where the leak occurs.")
    known_facts: str = Field(..., description="Sanitized, verifiable facts from the user's input.")
    assumptions: List[str] = Field(..., description="Material assumptions needed to evaluate the workflow.")
    constraints: str = Field(..., description="The user's stated operational or financial limits.")
    unknowns: List[str] = Field(..., description="Unclear or unmeasured variables in the workflow.")
    proposed_next_action: str = Field(..., description="Exactly one low-risk, manual action item.")
    action_rationale: str = Field(..., description="Why this action is the correct starting point.")

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
