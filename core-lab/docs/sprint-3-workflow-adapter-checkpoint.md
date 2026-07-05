# Sprint 3 Checkpoint: Normalized Payload to Workflow Adapter

This document outlines the workflow adapter functions, input structures, dry-run transition traces, testing, and execution details for Sprint 3.

## What Sprint 3 Added

1. **Workflow Adapter Module**:
   - Created [workflow_adapter.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow_adapter.py) implementing basic payload validations, Agent 1 input construction, and a dry-run graph trace builder.
   - Declared custom exception `WorkflowAdapterError(Exception)` to handle workflow-related input issues.

2. **Checkpoint Success Page Rendering Helper**:
   - Added `render_checkpoint_page()` inside [config_loader.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/config_loader.py).
   - This helper uses `html.escape` to safely render output data (such as JSON blocks) within HTML `<pre>` blocks, guarding against HTML injection or formatting corruption.

3. **HTTP POST Integration**:
   - Updated `POST /` inside [fast_api_app.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/fast_api_app.py) to forward successfully validated payload data to the workflow adapter and render the checkpoint page with status **HTTP 200**.

4. **Comprehensive Test Suite**:
   - Created [test_workflow_adapter.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/tests/unit/test_workflow_adapter.py) containing unit tests covering validation, trace outputs, error responses, and endpoint routing.

---

## Active Adapter Helpers

- `build_agent_1_input(workflow_payload: dict) -> dict` — Inspects the incoming payload keys and constructs the input dictionary required by the first agent node (`scenario_guide_agent`).
- `build_graph_transition_trace(workflow_payload: dict) -> list[dict]` — Formulates the deterministic list of graph steps representing the sequence of agents and gates.
- `prepare_episode_01_workflow_adapter_response(workflow_payload: dict) -> dict` — Builds the response envelope wrapping status, trace, prepared inputs, and unexecuted tasks.

---

## Agent 1 Input Shape

```json
{
  "scenario_id": "cool_down_tax",
  "selected_scenario": {
    "episode_number": "01",
    "title": "The Cool Down Tax",
    "context": "Mock context details",
    "measurement_preview": "Recovery time per incident"
  },
  "user_answers": {
    "interaction_type": "Vendor delayed shipping without notice",
    "frequency": "weekly",
    "minutes_lost": 45,
    "work_disrupted": "Billing and project coordination"
  },
  "adapter_status": "READY_FOR_AGENT_1"
}
```

---

## Dry-Run Graph Transition Trace

The trace outlines the sequence of graph execution without invoking live LLMs:
1. `START` (status: `READY`)
2. `scenario_guide_agent` (status: `INPUT_PREPARED`)
3. `workflow_analyst_agent` (status: `WAITING_FOR_AGENT_1_OUTPUT`)
4. `value_evidence_agent` (status: `WAITING_FOR_AGENT_2_OUTPUT`)
5. `safety_quality_agent` (status: `WAITING_FOR_AGENT_3_OUTPUT`)
6. `evaluate_safety_gate` (status: `WAITING_FOR_AGENT_4_RELEASE_STATUS`)
7. `terminal_route_pending` (status: `PENDING_SPRINT_4`)

All nodes are marked as `execution: "not_run"`.

---

## Intentionally Not Executed Yet

To ensure clean validation boundaries:
- No Gemini model calls or API calls are made.
- No Vertex AI / Google Cloud platform connections are initialized.
- No ADK Runner invocation or agent execution occurs.
- No final Scenario Brief is generated.
- No safety gate logic is triggered.

---

## How this prepares Sprint 4

In Sprint 4, the prepared `Agent 1` input will be passed to the live `scenario_guide_agent`, and the dry-run transition trace will be replaced by actual step-by-step agent execution updates as the graph traverses from START to a final brief release state.

---

## How to Run Tests

Run the unit test suite:
```bash
uv run pytest tests/unit
```

---

## How to Verify Manually

1. **Start the Local Server**:
   ```bash
   uv run uvicorn app.fast_api_app:app --host 127.0.0.1 --port 8000
   ```

2. **Submit the Questionnaire**:
   - Open a browser to `http://127.0.0.1:8000/`.
   - Fill in the form and click **Analyze My Scenario**.
   - Verify the success page outputs the trace, Agent 1 inputs, and includes the message:
     `Sprint 3 checkpoint: normalized input prepared for workflow adapter. Agent workflow has not run yet.`

---

## Evidence Screenshots

### 1. Client-Side Browser Native Validation Blocker
* **Screenshot**: `docs/evidence/sprint-03/01-native-validation-blocked.png`
* **What it proves**: Submitting an empty form is successfully blocked at the browser level by native HTML5 validation constraints, preventing unnecessary requests to the server.
* **Related Route/Command**: `POST /` (invalid/empty form)
* **Known Limitations**: The native HTML5 validation stops empty submissions at the browser level before reaching the server.

### 2. Workflow Checkpoint Success with Prepared Inputs and Graph Trace
* **Screenshot**: `docs/evidence/sprint-03/02-checkpoint-success-payload-trace.png`
* **What it proves**: Valid form submissions correctly pass to the workflow adapter, which returns the prepared Agent 1 input structure, the deterministic dry-run graph transition trace, and the list of unexecuted components alongside the Sprint 3 checkpoint message.
* **Related Route/Command**: `POST /` (valid input)
* **Known Limitations**: No live agent execution or model calls happened yet (all nodes marked `not_run`).

