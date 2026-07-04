# Phase 3 Recovery Report

## 1. Executive Summary

This recovery report evaluates the current progress of **Phase 3: Dataset Setup & Agent Evaluation** (and its prerequisite Phase 2 tasks) following a system crash that interrupted the previous Antigravity run.

The evaluation reveals that:
- **Phase 2 (Build Phase)** is **partially completed**:
  - The reconciled Pydantic schemas and custom field validators are successfully integrated into [schemas.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/schemas.py) and committed.
  - The 4-agent graph-based workflow is implemented in the working copy of [workflow.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py) but lacks logic to construct or return the final [ScenarioBrief](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/schemas.py#L352) object when approved.
  - The generic weather/time behavior has been successfully deleted from [agent.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/agent.py).
  - The external Model Context Protocol (MCP) server in [roi_calculator_server.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/mcp_server/roi_calculator_server.py) has **not** been refactored yet. It still calculates dollar-based ROI metrics and uses the risky "tax" naming convention, which violates our core compliance boundaries.
- **Phase 3 (Evaluation Phase)** has **not started**:
  - The 18-case scenario dataset (`scenario-dataset.json`) is completely missing.
  - The evaluation configuration in [eval_config.yaml](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/tests/eval/eval_config.yaml) has not been updated with LLM-as-judge compliance metrics.
- **Integration testing** is currently blocked by a Google Cloud platform issue:
  - Running `uv run pytest` fails 4 out of 12 tests due to a `403 Forbidden` API permission error on the target GCP project `sunny-sandbox-455515-h5` (Agent Platform API is disabled).

---

## 2. Git Status Summary

The repository is on the branch `veronica-day1-adapt-main`. The git status shows:
- **Modified files (unstaged)**:
  - [core-lab/app/agent.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/agent.py)
  - [core-lab/app/workflow.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py)
- **Staged / Untracked files**: None.
- **Root directories**: Historical root directories (`/app`, `/docs`, `/mcp_server`, `/notebooks`, `/tests`) are completely empty on disk (all files have been successfully ported to `/core-lab` in previous commits).
- **Conflict markers**: None exist in the working directory.

---

## 3. File-by-File Findings

### [core-lab/app/agent.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/agent.py)
- **Status**: Modified (unstaged changes in working copy).
- **Behavior**: Generic weather/time functions and the original single-agent `root_agent` are deleted. Exposes `root_agent` (imported from [workflow.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py)) and the ADK `app` instance correctly.
- **Sample Endpoint**: Contains [run_scenario_lab_sample](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/agent.py#L31), which simulates a mock 4-agent run. This is a synchronous mock path that is not hooked up to any active testing suite.

### [core-lab/app/workflow.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py)
- **Status**: Modified (unstaged changes in working copy).
- **Behavior**: Successfully sets up the 4 specialized agents (`scenario_guide_agent`, `workflow_analyst_agent`, `value_evidence_agent`, `safety_quality_agent`) using detailed, domain-specific instruction prompts.
- **Schemas**: Imports and enforces the correct validated schemas (`ScenarioInputState`, `AnalysisState`, `CalculationState`, `SafetyReviewState`) as agent `output_schema` properties.
- **Routing**: [evaluate_safety_gate](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py#L165) deterministically routes APPROVED, APPROVED_WITH_LIMITATION, and BLOCKED flows. However, all terminal nodes (e.g., [completed_node](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py#L196)) are empty placeholders (`pass`). The final output is never assembled into the expected [ScenarioBrief](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/schemas.py#L352) structure.

### [core-lab/app/schemas.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/schemas.py)
- **Status**: Unmodified (already committed).
- **Behavior**: Contains the fully reconciled Pydantic schemas and custom field validators for input structure, list cleaning, and cautious language checking.

### [core-lab/mcp_server/roi_calculator_server.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/mcp_server/roi_calculator_server.py)
- **Status**: Unmodified.
- **Behavior**: **Major Gap**. It has not been updated yet. The server still contains the `calculate_task_tax` tool (which violates the "tax" policy naming convention) and returns monetary dollar values (`one_year_opportunity_cost`), which breaks compliance constraints for wAI Scenario Lab.

### [core-lab/wai_scenario_config.json](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/wai_scenario_config.json)
- **Status**: Unmodified (already committed).
- **Behavior**: Contains the verified configuration schemas for the three wAI Scenario Lab scenarios.

### [core-lab/tests/scenarios.feature](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/tests/scenarios.feature)
- **Status**: Unmodified.
- **Behavior**: Defines Gherkin scenarios for `cool_down_tax`, `brain_fog`, and `blank_page`. However, there are no step definitions or test runners mapped to this file. It is currently dead test code.

---

## 4. What Appears Completed

- **Schema Reconcilement**: All custom validation logic and fields from Day 1 branch have been successfully ported to [schemas.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/schemas.py).
- **Agent Prompts Integration**: Verónica's agent prompts and Jason's graph routing structure are correctly combined in [workflow.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py).
- **FastAPI / CLI Entrypoints**: FastAPI lifespan hooks are configured, and compatibility targets (`root_agent` and `app`) are correctly exported in [agent.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/agent.py).
- **Generic Behavior Removal**: Simulated weather/time behavior has been purged from [agent.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/agent.py).

---

## 5. What Appears Partial or Risky

- **MCP Calculator Compliance Risk (Critical)**: [roi_calculator_server.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/mcp_server/roi_calculator_server.py) exposes financial/monetary metrics and uses the term "tax". This creates a significant risk of triggering false-positives in our safety filter (`safety_quality_agent`) and violating wAI's non-financial calculation constraint.
- **Missing ScenarioBrief Construction (High)**: When the workflow reaches [completed_node](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py#L196) (APPROVED status), it does not compile the accumulated session state into a [ScenarioBrief](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/schemas.py#L352) structure.
- **Unwired BDD Feature (Medium)**: [scenarios.feature](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/tests/scenarios.feature) is not hooked up to a testing framework.
- **Disabled GCP Agent Platform API (Blocker for E2E Tests)**: The Google Cloud Project `sunny-sandbox-455515-h5` lacks the `aiplatform.googleapis.com` (Agent Platform API) enablement, causing all agent model calls in integration tests to fail with a `403 Forbidden` response.

---

## 6. What Should Be Reverted

- **None**: No changes made to [agent.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/agent.py) or [workflow.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py) represent incorrect work; they are simply incomplete.

---

## 7. Recommended Phase 3a Tasks (Immediate Recovery & Refactoring)

Phase 3a must focus on completing Phase 2's build dependencies and removing compliance/functional blockers:

1. **GCP Project Setup**: Ask the user to enable the Agent Platform API (`aiplatform.googleapis.com`) on the GCP project `sunny-sandbox-455515-h5`.
2. **Refactor MCP Calculator**: Update [roi_calculator_server.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/mcp_server/roi_calculator_server.py) to:
   - Rename the `calculate_task_tax` tool to `calculate_task_time_loss`.
   - Remove all dollar-based outputs (e.g. `one_year_opportunity_cost`, `weekly_marketing_equity`) and return only time/non-monetary counts.
3. **Assemble ScenarioBrief**: Implement a final assembly node in [workflow.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py) (replacing [completed_node](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py#L196) and [completed_with_limitation_node](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py#L200)) to merge the state of all 4 agents into the final [ScenarioBrief](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/schemas.py#L352) structure.
4. **Fix Unit Tests**: Refactor [test_roi_calculator.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/tests/unit/test_roi_calculator.py) to match the new MCP tool outputs.

---

## 8. Recommended Phase 3b Tasks (Dataset Setup & Evaluation)

Once the core codebase is functional and compliant, we can execute the original Phase 3 tasks:

1. **Create Evaluation Dataset**: Generate the 18-case test suite at `core-lab/tests/eval/datasets/scenario-dataset.json` covering all 3 scenarios and case types.
2. **Configure Evaluation Quality Metrics**: Add compliance-specific LLM-as-judge metrics (no dollars, cautious language checks, single-action checks) to [eval_config.yaml](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/tests/eval/eval_config.yaml).
3. **Run Evaluation Loop**: Execute `agents-cli eval generate` followed by `agents-cli eval grade`. Tune prompts in [workflow.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py) until we hit 100% compliance and pass our quality thresholds.
4. **Integration Test Refactoring**: Update [test_agent.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/tests/integration/test_agent.py) to use actual scenario payloads (e.g. `cool_down_tax` details) instead of "Why is the sky blue?".

---

## 9. Exact Files That Should Be Changed Next

1. [core-lab/mcp_server/roi_calculator_server.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/mcp_server/roi_calculator_server.py) (Refactor tools to remove financial values and rename "tax" tool).
2. [core-lab/tests/unit/test_roi_calculator.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/tests/unit/test_roi_calculator.py) (Align assertions with non-financial MCP tools).
3. [core-lab/app/workflow.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py) (Add the ScenarioBrief compiler node to construct the final output).
4. [core-lab/tests/eval/eval_config.yaml](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/tests/eval/eval_config.yaml) (Add compliance-specific LLM metrics).

---

## 10. Exact Files That Should Not Be Touched Yet

1. [core-lab/app/schemas.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/schemas.py) (Already fully reconciled; no changes needed).
2. [core-lab/wai_scenario_config.json](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/wai_scenario_config.json) (Production-ready and matches our scenario standards).
3. [core-lab/app/fast_api_app.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/fast_api_app.py) (FastAPI shell functions correctly).
