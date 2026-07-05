# Sprint 5: Terminal Output Assembly and Scenario Brief Preview

## 1. Sprint Goal

Complete the deterministic terminal output assembly layer for Episode 01. The flow is:

```
validated Episode 01 form input
→ normalized workflow payload
→ workflow adapter
→ deterministic safety precheck
→ terminal route preview
→ Scenario Brief preview or withheld state
```

## 2. Why This Sprint Matters

Sprint 5 turns the earlier checkpoints into a user‑visible, reviewable Scenario Brief preview.

- Sprint 1 created the config‑driven public intake.
- Sprint 2 added validation and normalized payloads.
- Sprint 3 prepared Agent 1 input and dry‑run workflow traceability.
- Sprint 4 added deterministic safety routing.
- Sprint 5 now assembles the terminal output and renders the safety‑gated preview.

## 3. End-to-End Sprint 5 Flow

```
POST /
→ validate Episode 01 form
→ build workflow payload
→ prepare workflow adapter response
→ run deterministic safety routing response
→ prepare Sprint 5 terminal output response
→ render checkpoint page
```

## 4. Files Created

- `core-lab/app/terminal_output.py`
- `core-lab/tests/unit/test_terminal_output.py`
- `core-lab/docs/sprint-5-terminal-output-checkpoint.md`
- `core-lab/docs/evidence/sprint-05/`

Key functions in `terminal_output.py`:

- `TerminalOutputError`
- `build_deterministic_sanitized_input`
- `build_deterministic_analysis_state`
- `build_deterministic_calculation_state`
- `build_safety_review_from_route_preview`
- `prepare_sprint_5_terminal_output_response`

## 5. Files Modified

- `core-lab/app/config_loader.py`
- `core-lab/app/fast_api_app.py`
- `core-lab/tests/unit/test_config_loader.py`
- `core-lab/tests/unit/test_workflow_adapter.py`
- `core-lab/docs/walkthrough.md`

## 6. Terminal Output Assembly

`terminal_output.py` constructs deterministic state objects that match the existing schema and then invokes Jason’s assembler service.

The assembled response contains:

- **sanitized_input_state** – cleaned user input
- **analysis_state** – deterministic analysis results
- **calculation_state** – deterministic calculation results
- **safety_review_state** – safety‑gated review information
- **terminal_route** – the route chosen by the deterministic safety precheck (`RENDER_BRIEF`, `RENDER_LIMITATION_BANNER`, `HUMAN_TRIAGE`, `TERMINATE_BLOCKED`)
- **brief_preview_status** – `APPROVED`, `APPROVED_WITH_LIMITATION`, `REVISE`, or `BLOCKED`
- **safety_precheck_snapshot** – a snapshot of the safety precheck decision
- **adapter_status** – status of the workflow adapter
- **agent_1_input_visibility** – whether Agent 1 input is shown
- **intentionally_not_executed** – list of agents excluded from execution

## 7. Scenario Brief Assembly

Sprint 5 uses the existing service:

```python
from app.services.brief_assembler import assemble_brief
```

No new brief builder was created. The assembled Scenario Brief includes:

- scenario title
- what we heard
- friction summary
- assumptions
- one next step
- rationale
- one non‑monetary measurement
- unknowns
- redaction status
- human‑review reminder
- responsible‑use limitation
- episode CTA

## 8. Safety‑Gated Rendering

| Safety / Route State                     | Rendering Behavior                                                   |
| ---------------------------------------- | -------------------------------------------------------------------- |
| `APPROVED` / `RENDER_BRIEF`             | Renders full deterministic Scenario Brief preview                    |
| `APPROVED_WITH_LIMITATION` / `RENDER_LIMITATION_BANNER` | Renders preview with a limitation banner                          |
| `REVISE` / `HUMAN_TRIAGE`               | Withholds completed brief details; shows human‑review message       |
| `BLOCKED` / `TERMINATE_BLOCKED`         | Withholds completed brief details; shows out‑of‑scope blocked message |

## 9. Human Triage and Blocked States

Sensitive or out‑of‑scope inputs must not expand into a completed Scenario Brief.

Examples verified during Sprint 5:

- Email address `owner@example.test` triggers **Human Triage** – brief is withheld and a human‑review notice is shown.
- Legal request `I want to sue my landlord in court over eviction.` triggers **Blocked** – brief is withheld and an out‑of‑scope message is shown.

## 10. UI Rendering Updates

`config_loader.py` now supports Sprint 5 rendering fields:

- `brief_preview_status`
- `terminal_route_preview`
- `scenario_brief_preview`
- `assembled_brief_json`
- `safety_precheck_snapshot`
- `agent_1_input_preparation`
- `intentionally_not_executed`
- `withheld_state_message`

## 11. Route Integration

`fast_api_app.py` integrates the Sprint 5 output assembly into the valid `POST /` endpoint while keeping the existing routes available:

```
GET /
POST /
/docs
/openapi.json
/dev-ui
```

## 12. Tests Added and Updated

- `core-lab/tests/unit/test_terminal_output.py` – new tests for deterministic output assembly and route decisions.
- Updated existing tests to align with the new response schema.

## 13. Automated Test Results

```
uv run pytest tests/unit/test_terminal_output.py -q
20 passed
```

```
uv run pytest tests/unit -q
82 passed, 29 warnings
```

All warnings are non‑blocking.

## 14. Manual Verification

| Case | Input | Expected Result | Status |
| ---- | ----- | --------------- | ------ |
| Approved | Vendor delay, weekly, 45 min, Scheduling | Scenario Brief preview renders | Passed |
| Human triage | Fake email `owner@example.test` | Completed brief withheld, human‑review notice | Passed |
| Blocked | `I want to sue my landlord in court over eviction.` | Completed brief withheld, out‑of‑scope notice | Passed |

## 15. Evidence Screenshots

```
core-lab/docs/evidence/sprint-05/
```

| Screenshot | What it proves |
| ---------- | -------------- |
| `01-valid-form-before-submit.png` | Demo‑safe form input before submission |
| `02-approved-brief-preview.png` | Approved input renders Scenario Brief preview |
| `03-brief-measurement-and-disclosures.png` | Non‑monetary measurement and disclosures render |
| `04-safety-precheck-snapshot.png` | Safety precheck snapshot remains visible |
| `05-human-triage-withheld-brief.png` | Sensitive input withholds completed brief details |
| `06-blocked-withheld-brief.png` | High‑risk input blocks completed brief rendering |
| `07-tests-passing.png` | Unit tests pass |

## 16. Teamwork Integration

Verónica’s contributions:

- Public intake form and config‑driven Episode 01 flow
- Validation and normalized payload generation
- Agent 1 input visibility
- User‑facing Scenario Brief preview UI

Jason’s contributions:

- Value and evidence discipline
- Non‑monetary measurement boundary
- Deterministic safety precheck implementation
- Safety routing logic
- Scenario Brief schema and assembler (`brief_assembler.py`)
- Responsible‑use compliance checks

Sprint 5 connects both sides into a single testable public demo path.

## 17. Responsible AI and Compliance Notes

- The output is a deterministic prototype preview; live agents do not run.
- Human review remains required for sensitive content.
- The demo avoids legal, medical, mental‑health, tax, financial‑planning, employment, lending, housing, insurance, or regulatory advice.
- No ROI, dollar savings, opportunity‑cost, financial projection, or marketing equity calculations are introduced.
- Sensitive information is routed to human‑triage or blocked states.
- The flow supports transparent AI use and responsible disclosure expectations.

## 18. Known Warnings

- `BaseAgentConfig` deprecation warning
- ADK experimental feature warnings
- FastAPI / Starlette TestClient deprecation warning
- OpenTelemetry logger deprecation warnings
- Vertex AI template deprecation warnings
- `python_multipart` pending deprecation warning
- Duplicate ADK operation ID warning
- `datetime.utcnow()` deprecation warning in `brief_assembler.py`

These are slated for cleanup in future sprints and do not block Sprint 5.

## 19. Known Limitations

- Deterministic preview only; no live agent execution.
- No Gemini or Vertex AI calls.
- No full ADK graph execution.
- No public JSON endpoint.
- No persistence or user accounts.
- Episode 01 only.

## 20. Sprint 6 Readiness

Recommended focus for Sprint 6:

- Final public demo polish and UI refinements
- Health‑endpoint verification
- Capabilities‑endpoint verification
- Complete evidence index and README updates
- Walkthrough cleanup and reviewer‑ready run instructions
- Remove any remaining ROI or monetary placeholders
- Verify branch readiness before merge

## 21. Sprint 5 Completion Status

```
Sprint 5 Status: Complete and committed.
```
