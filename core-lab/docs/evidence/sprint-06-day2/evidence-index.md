# Sprint 06 Day 2 Evidence Index

## Scope

This evidence supports Verónica’s Day 2 work:

1. ADK 2.0 graph-compatible workflow routing
2. Dynamic scenario questionnaire landing page
3. Config-driven support for all three MVP scenarios
4. Safe Scenario Brief rendering
5. REVISE and BLOCKED withheld-output behavior
6. Local automated test validation

## Branch and Commit

* Branch: `veronica-day2-scenario-ui`
* Commit: `0264784 Documentation updates`
* Capture date: `2026-07-05`
* Captured by: Antigravity AI Coding Assistant

## Screenshots

| File                                                    | Evidence                                 | Status   |
| ------------------------------------------------------- | ---------------------------------------- | -------- |
| [01-branch-status.png](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/screenshots/01-branch-status.png)                        | Branch and working-tree status           | Captured |
| [02-landing-page-scenario-selection.png](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/screenshots/02-landing-page-scenario-selection.png)      | Landing page shows all three scenarios   | Captured |
| [03-cool-down-tax-dynamic-form.png](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/screenshots/03-cool-down-tax-dynamic-form.png)           | Cool Down Tax form renders dynamically   | Captured |
| [04-brain-fog-dynamic-form.png](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/screenshots/04-brain-fog-dynamic-form.png)               | Brain Fog form renders dynamically       | Captured |
| [05-blank-page-dynamic-form-select-field.png](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/screenshots/05-blank-page-dynamic-form-select-field.png) | Blank Page form renders select field     | Captured |
| [06-approved-scenario-brief.png](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/screenshots/06-approved-scenario-brief.png)              | Approved Scenario Brief renders safely   | Captured |
| [07-revise-pii-withheld-output.png](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/screenshots/07-revise-pii-withheld-output.png)           | PII case withholds completed brief       | Captured |
| [08-blocked-high-risk-withheld-output.png](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/screenshots/08-blocked-high-risk-withheld-output.png)    | High-risk case withholds completed brief | Captured |
| [09-test-results-passing.png](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/screenshots/09-test-results-passing.png)                 | Automated tests pass                     | Captured |
| [10-git-status-clean.png](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/screenshots/10-git-status-clean.png)                     | Final branch status                      | Captured |

## Recordings

| File                               | Evidence                            | Status        |
| ---------------------------------- | ----------------------------------- | ------------- |
| [RECORDING-NOT-CAPTURED.md](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/recordings/RECORDING-NOT-CAPTURED.md) | Notice explaining missing videos    | Not captured  |

## Terminal Outputs

| File                                      | Evidence                          | Status   |
| ----------------------------------------- | --------------------------------- | -------- |
| [01-branch-status.txt](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/terminal-output/01-branch-status.txt)      | Branch, latest commit, git status | Captured |
| [02-test-results.txt](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/terminal-output/02-test-results.txt)       | Local pytest results              | Captured |
| [03-server-run-command.txt](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/docs/evidence/sprint-06-day2/terminal-output/03-server-run-command.txt) | Local UI/server run command       | Captured |

## Known Limitations

*   **Deterministic Adapter Execution**: The local UI pipeline uses the graph-compatible deterministic adapter nodes to process answers rather than executing live GCP Vertex AI Agent Engine instances, enabling offline testing.
*   **Video Recording Incompatibility**: MP4 video recording is not supported in the execution agent's head-free sandbox environment. It has been replaced by comprehensive screenshots and raw terminal outputs.
*   **GCP Integration Test Status**: The 4 integration tests targeting live GCP Vertex AI API endpoints (`test_agent_stream`, `test_adk_run_sse`, `test_adk_run`, `test_run_session`) are skipped/expected to fail without live GCP credentials or Agent Platform API enablement. All 97 other unit/pipeline tests pass.

## Manual Verification Steps

To manually run the FastAPI UI:
```bash
cd core-lab
uv run python -m uvicorn app.fast_api_app:app --reload --host 127.0.0.1 --port 8000
```
Open:
`http://127.0.0.1:8000/`

Follow these tests:
1.  **Cool Down Tax Approved Path**: Click "The Cool Down Tax" and enter valid values (e.g. trigger: "Late vendor shipments", frequency: weekly, minutes: 45, disruption: "Client support"). Submit and verify that the Scenario Brief renders safely.
2.  **Brain Fog Approved Path**: Click "Brain Fog" and enter valid values. Submit and verify brief renders safely.
3.  **Blank Page Approved Path**: Click "The Blank Page" and select options. Submit and verify brief renders safely.
4.  **PII Revise Path**: Enter "Client complaint from bob@example.com" on the triggers field. Verify that the Scenario Brief details are withheld, showing only the REVISE instructions.
5.  **High-Risk Blocked Path**: Enter "I need urgent legal advice regarding a lawsuit" on the triggers field. Verify that details are withheld, showing only the BLOCKED message.

Run the test suite:
```bash
uv run pytest tests/unit tests/integration
```

## Privacy and Security Review

*   No secrets or API keys are included or visible in any evidence files.
*   No `.env` file contents are leaked or visible.
*   All PII examples used (such as `bob@example.com`) are entirely synthetic and used solely to demonstrate REVISE withheld behavior.
