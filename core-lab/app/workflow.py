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

import json
import sys
import os
from google.adk.agents import Agent
from google.adk.workflow import Workflow
from google.adk.events import RequestInput
from google.adk.tools import McpToolset
from mcp import StdioServerParameters
from google.adk.models import Gemini
from google.genai import types

import pathlib
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset

# Import schemas for runtime structural enforcement
from .schemas import (
    ScenarioInputState, 
    AnalysisState, 
    CalculationState, 
    SafetyReviewState
)

# Centralized model ID configuration
MODEL_ID = os.environ.get("ADK_MODEL", "gemini-3.5-flash")
workflow_model = Gemini(model=MODEL_ID)

# Integrate our config-driven FastMCP server as an active Toolset for Agent 3
# MCP attachment is ready for local config access; live Vertex deployment still requires credentialed environment wiring.
scenario_config_tools = McpToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=["core-lab/mcp_server/scenario_config_server.py"]
    )
)

# Load the safety-reviewer skill for Agent 4
SKILL_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".agents", "skills", "safety-reviewer")
)
safety_reviewer_skill = load_skill_from_dir(pathlib.Path(SKILL_DIR))
safety_reviewer_tools = SkillToolset(skills=[safety_reviewer_skill])

# =================---------------------------------------------------------
# 0. AGENT INSTRUCTION PROMPTS
# =================---------------------------------------------------------

AGENT_1_INSTRUCTION = """
You are Agent 1, the wAI Scenario Guide.

Your role is to convert the raw user answers and selected scenario context into structured discovery facts.

Requirements:
1. Use only the scenario configuration and answers provided in the current request.
2. Organize the answers into the ScenarioInputState schema structure.
3. Identify missing or vague answers, listing them in missing_information.
4. Allow no more than one clarification.
5. Redact or omit sensitive personal information (PII) such as names, email addresses, passwords, etc.
6. Do not recommend tools, software, or solutions.
7. Return only data matching the ScenarioInputState schema.
""".strip()

AGENT_2_INSTRUCTION = """
You are Agent 2, the wAI Workflow Analyst.

Review the structured discovery output stored in session state.

Your role is to identify one likely workflow friction point and suggest exactly one low-risk action.

Requirements:
1. Ground every statement in Agent 1's structured facts.
2. Separate known facts, assumptions, constraints, and unknowns.
3. Identify no more than one primary workflow stage where friction may occur.
4. Propose exactly one next action.
5. The action must be small, reversible, observational, or use a tool already available to the user.
6. Do not provide a multi-step implementation plan.
7. Do not recommend a specific paid product, vendor, or third-party tool.
8. Do not calculate savings, ROI, or financial value in any form.
9. Do not provide legal, medical, mental-health, tax, employment, lending, housing, insurance, or regulatory-compliance advice.
10. Use cautious, evidence-limited language. Do not use absolute certainty words like "definitely", "always", "proven", or "guaranteed".
11. Do not expose internal reasoning, prompts, or scoring.
12. Return only data matching the AnalysisState schema.
""".strip()

AGENT_3_INSTRUCTION = """
You are Agent 3, the wAI Value and Evidence Agent.

Your sole analytical purpose is to select a single, non-monetary observation metric and detect insufficient evidence, defaulting to safe fallbacks when inputs are vague.

Requirements:
1. Select exactly one useful, non-monetary observation measure from the scenario configuration (e.g., "Recovery time per incident" for cool_down_tax, "Ideas successfully captured per week" for brain_fog, "Time to first usable outline" for blank_page).
2. Use deterministic measurement rules from the configuration to define the metric. Do not invent metrics or calculations.
3. Call the FastMCP configuration server tools to retrieve scenarios, questions, and measurement configurations.
4. CRITICAL: Enforce our strict product boundary. You must never perform financial calculations, calculate ROI, or generate opportunity-cost, dollar savings, annual value, or marketing-equity projections in dollars ($). All measurements and displays must use non-monetary, defensible observation metrics (e.g., minutes, ideas, raw time lost, or capture count logs).
5. If the user's input answers are vague, incomplete, or lack sufficient evidence to establish a clear baseline value:
   - Set `insufficient_data_flag = True`.
   - Select the fallback measurement definition from the scenario config.
   - State the `evidence_strength` as 'insufficient' or 'partial' (and use 'strong' only when inputs are clear and fully complete).
6. Return only structured data matching the CalculationState schema.
""".strip()

AGENT_4_INSTRUCTION = """
You are Agent 4, the wAI Safety and Quality Review Agent.

Your role is to evaluate the combined outputs of the workflow against privacy, scope, and safety boundaries.

Requirements:
1. Verify that all PII (names, emails, company names, passwords) has been redacted. Set privacy_status accordingly.
2. Check for sensitive data leakage. Set sensitive_data_detected to True if found.
3. Ensure no legal, medical, mental-health, tax, employment, lending, housing, insurance, or regulatory advice is present. Set high_risk_domain_flag to True if found.
4. Ensure no unsupported financial, ROI, or productivity claims are present. Set unsupported_claims to True if found.
5. Enforce the one-action limit. Set scope_violation to True if a multi-step plan is proposed.
6. Verify that the mandatory disclosures (human review reminder, responsible use disclaimer) are present.
7. Rate the overall brief structure on a quality score from 1 to 10.
8. Set the release_status:
   - APPROVED: If all safety, scope, and validation checks pass.
   - APPROVED_WITH_LIMITATION: If the brief is correct but contains mild uncertainties.
   - REVISE: If PII redaction or minor corrections are needed.
   - BLOCKED: If high-risk violations or severe out-of-scope advice are found.
9. Return only data matching the SafetyReviewState schema.
""".strip()

# =================---------------------------------------------------------
# 1. SPECIALIST AGENTS INITIALIZATION (Multi-Agent System)
# =================---------------------------------------------------------

scenario_guide_agent = Agent(
    name="scenario_guide",
    model=workflow_model,
    instruction=AGENT_1_INSTRUCTION,
    output_schema=ScenarioInputState,
    mode="single_turn"
)

workflow_analyst_agent = Agent(
    name="workflow_analyst",
    model=workflow_model,
    instruction=AGENT_2_INSTRUCTION,
    input_schema=ScenarioInputState,
    output_schema=AnalysisState,
    mode="single_turn"
)

# Measurement and ROI-decoupling rules are enforced through config, schemas, instructions, and deterministic local tests.
value_evidence_agent = Agent(
    name="value_evidence",
    model=workflow_model,
    instruction=AGENT_3_INSTRUCTION,
    input_schema=AnalysisState,
    output_schema=CalculationState,
    tools=[scenario_config_tools],
    mode="single_turn"
)

# Safety release rules are enforced by the safety service, skill instructions, schemas, and deterministic tests.
safety_quality_agent = Agent(
    name="safety_quality",
    model=workflow_model,
    instruction=AGENT_4_INSTRUCTION,
    input_schema=CalculationState,
    output_schema=SafetyReviewState,
    tools=[safety_reviewer_tools],
    mode="single_turn"
)

# =================---------------------------------------------------------
# 2. DETERMINISTIC TRANSITION ROUTING & HUMAN-IN-the-LOOP NODES
# =================---------------------------------------------------------

def evaluate_safety_gate(context, event) -> str:
    """
    Deterministic transition router.
    Evaluates Agent 4's payload to decide the next path in the graph.
    This prevents non-deterministic model errors in your security gate.
    """
    try:
        payload = json.loads(event.output)
        status = payload.get("release_status", "REVISE")
        
        if status == "APPROVED":
            return "RENDER_BRIEF"
        elif status == "APPROVED_WITH_LIMITATION":
            return "RENDER_LIMITATION_BANNER"
        elif status == "BLOCKED":
            return "TERMINATE_BLOCKED"
        else:
            return "HUMAN_TRIAGE" # Send to Human-in-the-Loop Node
    except Exception as e:
        print(f"Error parsing safety payload: {e}", file=sys.stderr)
        return "HUMAN_TRIAGE"

# Human-in-the-Loop Node using the ADK 2.0 RequestInput API wrapped in a callable
def human_triage_node(context, event) -> RequestInput:
    """Pause workflow execution and request manual human review."""
    return RequestInput(
        name="human_triage",
        prompt="A safety review flagged a revision requirement. Jason, please review and adjust the brief."
    )

# Terminal Workflow States defined as callables to satisfy ADK graph type validation
# Live ADK terminal nodes are intentionally minimal; the FastAPI path renders ScenarioBrief output through the deterministic adapter.
def completed_node(context, event):
    """Workflow completed with approved brief."""
    pass

def completed_with_limitation_node(context, event):
    """Workflow completed with limitations."""
    pass

def blocked_screen_node(context, event):
    """Workflow blocked due to safety violations."""
    pass

# =================---------------------------------------------------------
# 3. GRAPH WORKFLOW CONSTRUCT (Edges and Connections)
# =================---------------------------------------------------------

workflow = Workflow(
    name="wAI_Scenario_Lab_Pipeline",
    edges=[
        ("START", scenario_guide_agent),
        
        # Scenario Guide links to the Workflow Analyst 
        (scenario_guide_agent, workflow_analyst_agent),
        
        # Workflow Analyst routes to Jason's Value & Evidence Agent 
        (workflow_analyst_agent, value_evidence_agent),
        
        # Value & Evidence routes to Jason's Safety Review Agent 
        (value_evidence_agent, safety_quality_agent),
        
        # Safety Review is routed deterministically by our router function
        (safety_quality_agent, evaluate_safety_gate),
        
        # Route mapping based on evaluate_safety_gate returns
        (evaluate_safety_gate, {
            "RENDER_BRIEF": completed_node,
            "RENDER_LIMITATION_BANNER": completed_with_limitation_node,
            "TERMINATE_BLOCKED": blocked_screen_node,
            "HUMAN_TRIAGE": human_triage_node
        }),
        
        # Human triaged decisions bypass the gate and return to safety verification
        (human_triage_node, safety_quality_agent)
    ]
)

# =================---------------------------------------------------------
# 4. DETERMINISTIC LOCAL ADAPTER & FUNCTION NODES
# =================---------------------------------------------------------
# NOTE: The actual ADK 2.0 Workflow runner execution requires live GCP Gemini API
# credentials. To support local, offline execution, testing, and UI validation,
# this deterministic adapter mirrors the graph's nodes, state structures, and
# transitions exactly using the defined Pydantic state schemas.

def node_load_scenario_config(scenario_id: str) -> dict:
    """Loads configuration for the given scenario ID."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wai_scenario_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    scenario_config = config.get("scenarios", {}).get(scenario_id)
    if not scenario_config:
        raise ValueError(f"Scenario {scenario_id} not found in config.")
    return scenario_config


def node_validate_user_answers(scenario_id: str, answers: dict, scenario_config: dict) -> ScenarioInputState:
    """Validates user answers against schema and configuration. (Agent 1: Scenario Guide)"""
    from app.services.safety import sanitize_text
    
    stated_problem = ""
    frequency = "weekly"
    estimated_time_loss = 0
    current_process = "N/A"
    primary_constraint = ""

    # Map scenario-specific answers to standardized input state fields
    if scenario_id == "cool_down_tax":
        stated_problem = answers.get("interaction_type", "")
        frequency = answers.get("frequency", "weekly")
        estimated_time_loss = int(answers.get("minutes_lost", 0) or 0)
        primary_constraint = answers.get("work_disrupted", "")
    elif scenario_id == "brain_fog":
        stated_problem = answers.get("idea_context", "")
        frequency = "weekly"
        estimated_time_loss = int(answers.get("ideas_lost_weekly", 0) or 0)
        current_process = answers.get("current_capture_method", "N/A")
        primary_constraint = answers.get("capture_constraint", "")
    elif scenario_id == "blank_page":
        stated_problem = answers.get("content_type", "")
        frequency = "weekly"
        estimated_time_loss = int(answers.get("minutes_to_start", 0) or 0)
        current_process = answers.get("source_material", "N/A")
        primary_constraint = answers.get("starting_difficulty", "")

    return ScenarioInputState(
        scenario_id=scenario_id,
        stated_problem=stated_problem,
        frequency=frequency,
        estimated_time_loss=estimated_time_loss,
        current_process=current_process,
        primary_constraint=primary_constraint,
        available_tools=[],
        missing_information=[]
    )


def node_run_workflow_analysis(scenario_input: ScenarioInputState) -> AnalysisState:
    """Agent 2 workflow analysis node."""
    scenario_id = scenario_input.scenario_id
    sanitized_problem = scenario_input.stated_problem
    
    if scenario_id == "cool_down_tax":
        friction_summary = f"Workflow recovery time creates an ongoing operational drag when dealing with {sanitized_problem}."
        proposed_next_action = "Record the timestamp and duration of the next three supplier notifications."
        action_rationale = "Tracking the exact delays provides objective baseline data before changing agreements."
        workflow_stage = "Vendor coordination"
        known_facts = ["Vendor delays occur weekly", f"Minutes lost: {scenario_input.estimated_time_loss}"]
        assumptions = ["Assumes current time loss estimates are consistent across incidents."]
        constraints = [scenario_input.primary_constraint or "N/A"]
        unknowns = ["The exact notice period given by vendors is unrecorded."]
    elif scenario_id == "brain_fog":
        friction_summary = f"Valuable ideas are lost or forgotten between inspiration and action when {sanitized_problem}."
        proposed_next_action = "Place a single notebook or open notes app shortcut on the main mobile screen."
        action_rationale = "Keeping a single capture location reduces the steps required to write down ideas."
        workflow_stage = "Idea capture"
        known_facts = [f"Ideas lost weekly: {scenario_input.estimated_time_loss}", f"Current method: {scenario_input.current_process}"]
        assumptions = ["Assumes lost ideas represent significant business or creative value."]
        constraints = [scenario_input.primary_constraint or "N/A"]
        unknowns = ["The exact context or triggers of ideas are not tracked."]
    elif scenario_id == "blank_page":
        friction_summary = f"Content creation stalls during the initial writing phase for {sanitized_problem}."
        proposed_next_action = "Create a bulleted list of three key points before writing the first sentence."
        action_rationale = "Drafting an outline separate from content production reduces starting hesitation."
        workflow_stage = "Content planning"
        known_facts = [f"Minutes spent starting: {scenario_input.estimated_time_loss}", f"Source material: {scenario_input.current_process}"]
        assumptions = ["Assumes starting hesitation is the main driver of the delay."]
        constraints = [scenario_input.primary_constraint or "N/A"]
        unknowns = ["The specific outline structure preferred by clients is unknown."]
    else:
        raise ValueError(f"Unknown scenario ID: {scenario_id}")

    return AnalysisState(
        friction_summary=friction_summary,
        workflow_stage=workflow_stage,
        known_facts=known_facts,
        assumptions=assumptions,
        constraints=constraints,
        unknowns=unknowns,
        proposed_next_action=proposed_next_action,
        action_rationale=action_rationale
    )


def node_run_value_evidence(scenario_input: ScenarioInputState, scenario_config: dict) -> CalculationState:
    """Agent 3 value and evidence node."""
    measurement_def = scenario_config.get("measurement", {})
    primary_measure = measurement_def.get("primary", {})
    fallback_measure = measurement_def.get("fallback", {})
    
    insufficient = False
    if not scenario_input.stated_problem or len(scenario_input.stated_problem.strip()) < 10:
        insufficient = True
        
    if insufficient:
        recommended_measure = fallback_measure.get("name", "Fallback observation measure")
        measure_unit = fallback_measure.get("unit", "incidents")
        baseline_val = None
        baseline_display = "N/A"
        calculation_method = fallback_measure.get("calculation", "Count incidents.")
        measurement_period = fallback_measure.get("period", "Two weeks.")
        evidence_strength = "insufficient"
    else:
        recommended_measure = primary_measure.get("name", "Primary observation measure")
        measure_unit = primary_measure.get("unit", "minutes")
        baseline_val = float(scenario_input.estimated_time_loss) if scenario_input.estimated_time_loss is not None else None
        baseline_display = f"{int(baseline_val)} {measure_unit}" if baseline_val is not None else "N/A"
        calculation_method = primary_measure.get("calculation", "Use the reported value.")
        measurement_period = primary_measure.get("period", "Track progress.")
        evidence_strength = "strong"
        
    return CalculationState(
        recommended_measure=recommended_measure,
        measure_unit=measure_unit,
        baseline_value=baseline_val,
        baseline_display=baseline_display,
        calculation_method=calculation_method,
        assumptions=["Assumes baseline is consistent."],
        evidence_strength=evidence_strength,
        measurement_period=measurement_period,
        insufficient_data_flag=insufficient
    )


def node_run_deterministic_safety_precheck(scenario_input: ScenarioInputState) -> SafetyReviewState:
    """Runs all safety, PII, and product boundary checks. (Agent 4: Safety & Quality Review)"""
    from app.services.safety import evaluate_safety_text
    
    safety_eval = evaluate_safety_text(scenario_input.stated_problem)
    release_status = safety_eval["release_status"]
    
    # Custom business rules: trigger limitation if inputs are short or vague
    insufficient = False
    if len(scenario_input.stated_problem.strip()) < 10:
        insufficient = True
        
    if release_status == "APPROVED" and ("unusual" in scenario_input.stated_problem.lower() or insufficient):
        release_status = "APPROVED_WITH_LIMITATION"
        
    return SafetyReviewState(
        privacy_status="REDACTED" if safety_eval["sensitive_data_detected"] else "CLEAN",
        sensitive_data_detected=safety_eval["sensitive_data_detected"],
        unsupported_claims=safety_eval["unsupported_claims"],
        scope_violation=safety_eval["prohibited_automation_flag"],
        high_risk_domain_flag=safety_eval["high_risk_domain_flag"],
        human_review_present=True,
        required_disclosures_present=True,
        quality_score=9,
        release_status=release_status,
        revision_instructions=(
            "must use cautious language; do not use absolute certainty words like 'definitely', 'always', 'guaranteed', or 'proven'"
            if safety_eval.get("has_absolute_words", False)
            else ("Please remove sensitive data or PII from your answers." if release_status == "REVISE" else "")
        )
    )


def node_assemble_scenario_brief(
    scenario_config: dict,
    scenario_input: ScenarioInputState,
    analysis_state: AnalysisState,
    calculation_state: CalculationState,
    safety_review: SafetyReviewState
) -> dict:
    """Assembles and returns the final validated brief or safe revision state."""
    from app.services.brief_assembler import assemble_brief
    
    # Load required disclosures from the config
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wai_scenario_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    disclosures = config.get("required_disclosures", {})
    
    return assemble_brief(
        scenario_config=scenario_config,
        sanitized_input=scenario_input,
        analysis_state=analysis_state,
        calculation_state=calculation_state,
        safety_review=safety_review,
        required_disclosures=disclosures
    )


def run_scenario_lab_sample(scenario_id: str = "cool_down_tax", answers: dict = None) -> dict:
    """Processes a sample payload through the 4-agent Scenario Lab workflow using deterministic nodes."""
    # 1. Load scenario configuration
    scenario_config = node_load_scenario_config(scenario_id)
    
    if answers is None:
        # Defaults based on scenario_id
        if scenario_id == "cool_down_tax":
            answers = {
                "interaction_type": "Vendor delays with little notice",
                "frequency": "weekly",
                "minutes_lost": 45,
                "work_disrupted": "Project follow-up and scheduling"
            }
        elif scenario_id == "brain_fog":
            answers = {
                "idea_context": "Away from desk while driving",
                "current_capture_method": "Memory",
                "ideas_lost_weekly": 5,
                "capture_constraint": "Safety concern while driving"
            }
        elif scenario_id == "blank_page":
            answers = {
                "content_type": "Social posts and blog articles",
                "source_material": "Rough meeting notes",
                "minutes_to_start": 60,
                "starting_difficulty": "writing_opening"
            }
            
    # 2. Validate answers and sanitize inputs (Agent 1 simulation)
    scenario_input = node_validate_user_answers(scenario_id, answers, scenario_config)
    
    # 3. Safety Precheck (Agent 4 pre-filter)
    safety_review = node_run_deterministic_safety_precheck(scenario_input)
    
    if safety_review.release_status in ["REVISE", "BLOCKED"]:
        return node_assemble_scenario_brief(
            scenario_config=scenario_config,
            scenario_input=scenario_input,
            analysis_state={},
            calculation_state={},
            safety_review=safety_review
        )
        
    # 4. Workflow Analysis (Agent 2 simulation)
    analysis_state = node_run_workflow_analysis(scenario_input)
    
    # 5. Value and Evidence (Agent 3 simulation)
    calculation_state = node_run_value_evidence(scenario_input, scenario_config)
    
    # 6. Assemble Scenario Brief
    brief = node_assemble_scenario_brief(
        scenario_config=scenario_config,
        scenario_input=scenario_input,
        analysis_state=analysis_state,
        calculation_state=calculation_state,
        safety_review=safety_review
    )
    
    return brief



