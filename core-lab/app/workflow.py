import json
import sys
import os
from google.adk.agents import Agent, Workflow
from google.adk.models import Gemini
from google.adk.workflows import RequestInput
from google.adk.tools import McpToolset

# Import schemas for runtime structural enforcement
from app.schemas import (
    ScenarioInputState, 
    AnalysisState, 
    CalculationState, 
    SafetyReviewState
)

# Centralized model ID configuration
MODEL_ID = os.environ.get("ADK_MODEL", "gemini-3.5-flash")
workflow_model = Gemini(model=MODEL_ID)

# Integrate our FastMCP calculator server as an active Toolset
# This satisfies the MCP Server and Tool-use capstone criteria
calculator_tools = McpToolset(server_url="stdio://python core-lab/mcp_server/roi_calculator_server.py")

# =================---------------------------------------------------------
# 1. SPECIALIST AGENTS INITIALIZATION (Multi-Agent System)
# =================---------------------------------------------------------

scenario_guide_agent = Agent(
    name="scenario_guide",
    model=workflow_model,
    instruction=(
        "You are Verónica's Scenario Guide Agent. Your task is to process raw user "
        "answers and organize them into the ScenarioInputState schema. Redact all PII. "
        "Do not invent solutions or recommend software tools."
    ),
    mode="SingleTurn"
)

workflow_analyst_agent = Agent(
    name="workflow_analyst",
    model=workflow_model,
    instruction=(
        "You are Verónica's Workflow Analysis Agent. Identify the primary workflow friction "
        "and suggest EXACTLY ONE manual, low-risk action. Do not outline multi-step plans "
        "or name specific software vendors. Adhere strictly to the AnalysisState schema."
    ),
    mode="SingleTurn"
)

value_evidence_agent = Agent(
    name="value_evidence",
    model=workflow_model,
    instruction=(
        "You are Jason's Value and Evidence Agent. Call our FastMCP calculators to perform "
        "deterministic math. Do not execute mental arithmetic. If the inputs are vague "
        "or missing, set the insufficient_data_flag to True and trigger our fallback measure. "
        "Adhere to the CalculationState schema."
    ),
    tools=[calculator_tools],
    mode="SingleTurn"
)

safety_quality_agent = Agent(
    name="safety_quality",
    model=workflow_model,
    instruction=(
        "You are Jason's Safety and Quality Review Agent. Evaluate the combined outputs "
        "against our privacy, scope, and commercial boundaries. Enforce the one-action limit. "
        "Apply the correct release_status. Adhere to the SafetyReviewState schema."
    ),
    # Portable Agent Skill loaded dynamically to keep our core context clean
    skills=["./core-lab/.agents/skills/safety-reviewer"],
    mode="SingleTurn"
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

# Human-in-the-Loop Node using the ADK 2.0 RequestInput API
human_triage_node = RequestInput(
    name="human_triage",
    prompt="A safety review flagged a revision requirement. Jason, please review and adjust the brief."
)

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
            "RENDER_BRIEF": "COMPLETED",
            "RENDER_LIMITATION_BANNER": "COMPLETED_WITH_LIMITATION",
            "TERMINATE_BLOCKED": "BLOCKED_SCREEN",
            "HUMAN_TRIAGE": human_triage_node
        }),
        
        # Human triaged decisions bypass the gate and return to safety verification
        (human_triage_node, safety_quality_agent)
    ]
)
