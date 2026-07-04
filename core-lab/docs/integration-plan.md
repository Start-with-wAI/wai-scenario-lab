# Integration Plan: Adapting Verónica's Day 1 Assets into Jason's Core-Lab Scaffold

## Executive Summary

This integration plan outlines the strategy for migrating and merging Verónica's Day 1 manual draft implementation (from the `veronica` branch) into Jason's production-ready `core-lab/` scaffold (on the `main` branch). 

Currently, `main` contains the runnable FastAPI application infrastructure, featuring an advanced ADK 2.0 graph-based workflow, MCP calculator integration, and a human-in-the-loop triage system. However, its agents are configured with dummy weather/time behavior, and the schemas lack validation. Conversely, the `veronica` branch contains the actual business logic—comprising detailed prompt instructions, strict Pydantic output schemas, custom validation rules for compliance, and a robust evaluation plan—but is implemented in a flat, linear pipeline format at the repository root.

By following this plan, we will port Verónica's domain expertise into Jason's graph-based scaffold, resolving schema incompatibilities and mitigating compliance risks (such as unauthorized financial calculations and high-risk domain policy checks) to create a single, secure, and fully verified runnable application in `core-lab/`.

---

## Source Branch Comparison

| Feature/Dimension | `main` Branch (`core-lab/` Scaffold) | `veronica` Branch (Day 1 Manual Draft) | Integration Target |
| :--- | :--- | :--- | :--- |
| **Workflow Architecture** | Graph-based `Workflow` with edge routing and Human-in-the-Loop node. | Flat, linear `SequentialAgent` pipeline. | **Graph-based Workflow** (Jason's ADK 2.0 structure). |
| **Orchestration Logic** | Runs 4 sequential agents with a deterministic safety gate and revision loops. | Runs 2 agents in sequence. | **4-Agent Graph** with safety gates and revision loops. |
| **Schemas & Validators** | Minimal skeleton Pydantic models; no field/model validation. | Comprehensive Pydantic models with custom validators for safety and formatting. | **Verónica's Schema Validation Rules** integrated into Jason's model structures. |
| **Agent Prompts** | Minimal placeholders. | In-depth instructions detailing domain and formatting constraints. | **Verónica's Instructions** adapted for graph execution. |
| **External Integrations** | Active FastMCP calculator server (`roi_calculator_server.py`). | None. | **MCP Server Integration** (Jason's structure). |
| **Evaluation Suite** | 2 dummy cases (weather/greeting); generic quality metrics. | Detailed plan for 18 distinct test cases across 3 scenarios; clear release criteria. | **Verónica's 18 Case Dataset** and release criteria in ADK evaluation framework. |
| **Code Location** | Encapsulated in `core-lab/`. | Scattered across repository root. | **Encapsulated in `core-lab/`** (root folders ignored/deleted). |

---

## File Mapping Table

To maintain a clean, single-project structure and avoid competing implementation structures, all useful assets from the `veronica` branch will be ported into the `core-lab/` directory.

| Source File (Branch `veronica`) | Target File (Branch `main`) | Action | Rationale / Integration Details |
| :--- | :--- | :--- | :--- |
| `app/schemas/agent_1.py` | `core-lab/app/schemas.py` | **Merge** | Merge type definitions (converting string fields to `List[str]`) and add custom Pydantic validators (`validate_scenario_id` and `clean_string_lists`) to `ScenarioInputState`. |
| `app/schemas/agent_2.py` | `core-lab/app/schemas.py` | **Merge** | Merge structure and validators (assumptions limit, unknowns limit, cautious language check, single-action check, and category exclusivity validation) to `AnalysisState`. |
| `app/workflow.py` | `core-lab/app/workflow.py` | **Merge** | Extract `AGENT_1_INSTRUCTION` and `AGENT_2_INSTRUCTION` prompts and insert them into the `scenario_guide_agent` and `workflow_analyst_agent` graph node definitions. Discard the linear `SequentialAgent` runner code. |
| `app/config/wai_scenario_config.json` | `core-lab/wai_scenario_config.json` | **Ignore** | File contents are identical. The `core-lab/` path is already the active config source of truth. |
| `requirements.txt` | `core-lab/pyproject.toml` | **Ignore/Merge** | Core-lab uses `pyproject.toml` and `uv` to manage dependencies. Add any missing packages (`pydantic-settings`, `python-dotenv`) to `pyproject.toml` using `uv add`. |
| `docs/evaluation/README_eval.md` | `core-lab/docs/evaluation-guide.md` | **Port** | Save as the formal evaluation baseline and guide for designing the testing suite. |
| All other root-level `app/`, `docs/`, `mcp_server/`, `tests/` | None | **Ignore / Delete** | These files contain only historical documentation, obsolete templates, or duplicate structures that conflict with the active runnable `core-lab/` application. |

---

## Technical & Compliance Risks

### 1. MCP Dollar-Savings and ROI Calculator Risk (Critical)
*   **Risk**: The current MCP calculator server (`roi_calculator_server.py`) contains tools (`calculate_task_tax`, `calculate_content_factory_value`) that compute opportunity costs and marketing equity in dollars ($). This directly conflicts with:
    *   Verónica's Agent 2 instructions: *"Do not calculate savings, ROI, or financial value."*
    *   The `CalculationState` schema: expects non-financial metrics like minutes, ideas, or attempts.
    *   Scenario configurations: None of the three scenarios (`cool_down_tax`, `brain_fog`, `blank_page`) allow financial calculations or dollar-based metrics.
*   **Mitigation**: Refactor the MCP server tools to compute **time savings and productivity metrics** (e.g., hours/minutes lost, capturing yields, or completed outline counts) rather than dollar figures. Prompt instructions in Agent 3 (`value_evidence`) must explicitly prohibit generating financial projections or dollar amounts.

### 2. "Tax" Domain Policy Block Risk
*   **Risk**: The MCP tool `calculate_task_tax` contains the word "tax". Since tax advice is flagged as a high-risk domain boundary (`high_risk_domains_placeholder_for_jason`), the safety and quality review agent (`safety_quality`) is highly likely to flag any traces containing the word "tax" as a policy violation, leading to false-positive `BLOCKED` states.
*   **Mitigation**: Rename the tool in the MCP server to `calculate_task_time_loss` or `calculate_time_tax_impact` and ensure the prompt guidelines make clear that "tax" is used purely as a metaphor for time overhead, not financial/government tax.

### 3. Schema Data Structure Mismatches
*   **Risk**: Jason's scaffold schema defines `available_tools`, `missing_information`, `known_facts`, and `constraints` as simple strings. Verónica's schemas define them as `List[str]`. Storing list structures in string fields (or vice versa) will cause serialization errors at runtime or downstream agent validation failures.
*   **Mitigation**: Update all fields in `core-lab/app/schemas.py` to match Verónica's type declarations exactly, and adapt the downstream Agent 3 and Agent 4 schemas to consume lists.

### 4. Graph Edge Routing Errors
*   **Risk**: Verónica's agents might return states that do not match the expected formats in `core-lab/app/schemas.py` or return partial data that triggers router failures in `evaluate_safety_gate`.
*   **Mitigation**: Enforce the exact schemas on Verónica's agents during initial build steps, and wrap the router `evaluate_safety_gate` in robust error handling to default to `HUMAN_TRIAGE` instead of crashing.

---

## Proposed Phases & Timeline

### Phase 2: Schema & Prompt Integration (Build Phase)
*   **Objective**: Port Verónica's instructions, schemas, and validators into the graph scaffold and remove sample weather/time code.
*   **Tasks**:
    1. Update `core-lab/app/schemas.py` to incorporate Verónica's Pydantic schemas and custom field validators.
    2. Update `core-lab/app/workflow.py` with Verónica's detailed agent prompts.
    3. Modify `core-lab/app/agent.py` to remove weather/time tools and expose the Scenario Lab graph workflow via the FastAPI app wrapper.
    4. Refactor `core-lab/mcp_server/roi_calculator_server.py` to remove dollar value output and rename the "tax" tool.
    5. Sync all python dependencies in `core-lab/pyproject.toml` and run `agents-cli install`.

### Phase 3: Dataset Setup & Agent Evaluation (Iteration Loop)
*   **Objective**: Configure the formal evaluation suite and iteratively tune the prompts.
*   **Tasks**:
    1. Create a comprehensive evaluation dataset in `core-lab/tests/eval/datasets/scenario-dataset.json` containing the **18 test cases** (6 cases per scenario: 2 normal, 1 vague, 1 sensitive, 1 scope-pressure, 1 unusual).
    2. Configure LLM-as-judge metrics in `core-lab/tests/eval/eval_config.yaml` to grade compliance (e.g. single-action restriction, cautious language, no dollar calculations).
    3. Run `agents-cli eval generate` followed by `agents-cli eval grade`.
    4. Tune prompts in `core-lab/app/workflow.py` iteratively until the agent meets all compliance and quality targets.

### Phase 4: Automated Testing & Validation (Pre-Deployment)
*   **Objective**: Ensure the entire app compiles, runs locally, and passes unit/integration tests.
*   **Tasks**:
    1. Refactor `core-lab/tests/unit/test_roi_calculator.py` to test the new time-loss and non-financial outputs of the MCP server.
    2. Refactor `core-lab/tests/integration/test_agent.py` and `core-lab/tests/integration/test_server_e2e.py` to use wAI Scenario Lab payload formats.
    3. Run `uv run pytest tests/unit tests/integration` and fix all code quality or test failures.
    4. Run `agents-cli lint` to check PEP8 and ruff styling rules.

### Phase 5: Dev Deployment & Final Verification
*   **Objective**: Deploy the integrated application to the staging/dev environment.
*   **Tasks**:
    1. Request final human approval to deploy.
    2. Execute `agents-cli deploy` to publish the agent to the dev runtime.
    3. Perform manual E2E verification of the deployed endpoint in the Vertex AI Console Playground.

---

## Acceptance Criteria

### Phase 2 (Build)
- [ ] No sample weather/time code remains in `core-lab/app/agent.py`.
- [ ] The app launches successfully via `uvicorn app.fast_api_app:app` without schema import errors.
- [ ] Pydantic validation successfully triggers and raises validation errors when Agent 1 or Agent 2 output constraints are violated (e.g., more than 2 assumptions, or non-cautious language in friction summary).
- [ ] The MCP server tools return only non-financial metrics (time, counts) and do not calculate dollars.

### Phase 3 (Evaluation)
- [ ] The dataset contains 18 distinct test cases matching the scenarios and case types.
- [ ] The evaluation run (`agents-cli eval grade`) confirms:
  - 100% success on sensitive-data cases (PII redacted).
  - 100% success on high-risk domain cases (requests for tax/legal advice are blocked or redirected).
  - Zero cases of unsupported financial claims or dollar-savings calculations.
  - 100% compliance with the single-action limit constraint.

### Phase 4 (Testing)
- [ ] `agents-cli lint` returns no syntax or formatting issues.
- [ ] Unit tests for the MCP calculator pass successfully.
- [ ] Integration tests and FastAPI end-to-end endpoints respond correctly to mock Scenario Lab requests.
- [ ] `pytest` execution returns zero failures.

### Phase 5 (Deployment)
- [ ] Deployment completes with no Cloud Trace or permission errors.
- [ ] The Vertex AI Console Playground shows successful session initialization and execution of the 4-agent graph.
