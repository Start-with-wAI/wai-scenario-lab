# Sprint 4 Checkpoint: Deterministic Safety Routing

This document details the features, routing logic, unit tests, and screenshot verification for Sprint 4.

## What Sprint 4 Added

1. **Safety Router Module**:
   - Created [safety_router.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/safety_router.py) to manage answer composition, execute deterministic scans using Jason's safety utilities, map release status to terminal routes, and format response payloads.

2. **FASTAPI Integration**:
   - Updated the `POST /` success route in [fast_api_app.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/fast_api_app.py) to forward validated answers to the safety router and render the Sprint 4 checkpoint page.
   - Handled `SafetyRouterError` exceptions cleanly.

3. **Checkpoint Success Page Rendering Helper**:
   - Updated `render_checkpoint_page()` in [config_loader.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/config_loader.py) to render safety precheck logs, terminal route details, and routing traces.
   - Escapes all JSON outputs using `html.escape` to ensure safe browser rendering.

4. **Integration with Jason's Safety Utilities**:
   - Directly imports and uses `evaluate_safety_text()` from [safety.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/services/safety.py) to run sensitive data detection, high-risk domain keyword scans, prohibited automation checks, and unsupported benefits checks.

5. **Safety Tests**:
   - Created [test_safety_router.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/tests/unit/test_safety_router.py) to test all route mappings, trace behaviors, and endpoint responses.

---

## Supported Release Statuses & Terminal Route Mappings

The deterministic precheck maps safety results directly to preview routes:
- **`APPROVED`** → **`RENDER_BRIEF`**: Input contains no sensitive or high-risk content.
- **`APPROVED_WITH_LIMITATION`** → **`RENDER_LIMITATION_BANNER`**: Used for edge cases with slight validation flags.
- **`BLOCKED`** → **`TERMINATE_BLOCKED`**: Triggered by high-risk domains (e.g. legal/medical questions) or prohibited automation requests.
- **`REVISE`** → **`HUMAN_TRIAGE`**: Triggered by sensitive data (such as emails or passwords) or unsupported claims.
- **Missing / Malformed / Unknown** → **`HUMAN_TRIAGE`**: Fallback safe state.

---

## Intentionally Not Executed Yet

To maintain validation boundaries:
- No live Agent 1, 2, 3, or 4 execution occurs.
- No Vertex AI / Gemini LLM calls occur.
- No ADK Runner or workflow graph execution is active.
- No actual redirect or rendering of the final brief/blocked screens occurs.

---

## How Sprint 4 Prepares Sprint 5

In Sprint 5, the deterministic precheck results will guide the actual execution of the ADK graph. For example, if the precheck is `APPROVED`, the graph will execute Agents 1-3 to assemble the Scenario Brief, whereas if the precheck is `BLOCKED` or `REVISE`, it will directly route to terminal nodes or enqueue for human review without calling Gemini models.

---

## How to Run Tests

Run the full unit test suite:
```bash
uv run pytest tests/unit
```

---

## How to Verify Manually

1. **Start the Local Server**:
   ```bash
   uv run uvicorn app.fast_api_app:app --host 127.0.0.1 --port 8000
   ```

2. **Verify Approved Case**:
   - Enter `Vendor delay` and valid values in the form.
   - Click **Analyze My Scenario**. Check that it displays `release_status = APPROVED` and `terminal_route = RENDER_BRIEF`.

3. **Verify Revise Case**:
   - Submit answers including `owner@example.test` in the text.
   - Check that it displays `release_status = REVISE` and `terminal_route = HUMAN_TRIAGE`.

4. **Verify Blocked Case**:
   - Submit answers containing legal advice requests (e.g. `lawyer`, `suing my landlord`).
   - Check that it displays `release_status = BLOCKED` and `terminal_route = TERMINATE_BLOCKED`.

---

## Evidence Screenshots

| Screenshot Filename | What it Proves | Related Route or Command | Known Limitation |
| :--- | :--- | :--- | :--- |
| `01-valid-form-before-submit.png` | Clean Episode 01 questionnaire inputs populated before form submit | `GET /` | Shows Episode 01 questionnaire only |
| `02-approved-safety-route-preview.png` | Normal inputs route successfully to RENDER_BRIEF with release status APPROVED | `POST /` (valid data) | Deterministic precheck only; Agent 4 did not run |
| `03-revise-human-triage-preview.png` | Inputs containing sensitive email route to HUMAN_TRIAGE with status REVISE | `POST /` (email data) | Deterministic precheck only; Agent 4 did not run |
| `04-blocked-route-preview.png` | Inputs requesting legal advice route to TERMINATE_BLOCKED with status BLOCKED | `POST /` (legal data) | Deterministic precheck only; Agent 4 did not run |
| `05-tests-passing.png` | Pytest suite successfully executing and passing all 62 unit and routing tests | `uv run pytest tests/unit` | Tests execute locally |

---

## ROI Calculator Deprecation & Warning Remediation

As part of wAI's responsible AI guidelines and strict adherence to non-financial boundaries, the legacy ROI calculator server (`roi_calculator_server.py`) has been deprecated. Consequently, `test_roi_calculator.py` was removed from the active unit test suite and archived to [deprecated-roi-calculator.md](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/archive/deprecated-roi-calculator.md) for historical reference. The project now utilizes non-monetary observation metrics (e.g. time-loss in minutes) rather than calculating monetary opportunity costs or dollar savings.

