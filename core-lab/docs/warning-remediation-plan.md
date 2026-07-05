# Warning Remediation Plan

This plan documents the evaluation of the four active local validation warnings found during testing of the wAI Scenario Lab prototype, along with their sources, impact, and proposed remediations.

---

## Current Validation Baseline
- **Static Compile Checks**: Passed (`exit 0`)
- **Local Demo Script**: Runs and formats Scenario Brief successfully
- **Pytest Result**: 29 passed, 4 skipped (GCP Vertex AI integration tests skipped)
- **Warnings Evaluated on**: Python 3.13.14

---

## Summary Table

| Warning | Source | Code or Dependency | Recommended Action | Fix Now? | Risk Level | Files Affected |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`datetime.utcnow()` Deprecation** | `brief_assembler.py` | Our Code | Replace with `datetime.now(timezone.utc)` | **Yes** | Low | `core-lab/app/services/brief_assembler.py` |
| **`BaseAgentConfig` Deprecation** | `google-adk` | Dependency Noise | Document or filter in `pytest.ini_options` | No (Suppress/Defer) | Low | `core-lab/pyproject.toml` (if filtering) |
| **`PLUGGABLE_AUTH` Experimental** | `google-adk` | Dependency Noise | Document or filter in `pytest.ini_options` | No (Suppress/Defer) | Low | `core-lab/pyproject.toml` (if filtering) |
| **`StdioServerParameters` Deprecated** | `mcp` / `google-adk` | Dependency / API | Keep `StdioServerParameters` as session manager wraps it; defer changes | No (Defer) | Medium | `core-lab/app/workflow.py` |

---

## Detailed Analysis

### 1. `datetime.utcnow()` Warning
*   **Warning Text**: `DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).`
*   **Likely Source**: [brief_assembler.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/services/brief_assembler.py#L117)
*   **Why It Occurs**: Standard library deprecation in Python 3.12+ which warns against using naïve datetime objects.
*   **Recommended Fix**: Replace `datetime.utcnow()` with `datetime.now(timezone.utc)` after importing `timezone` from the `datetime` module.
*   **Risk Level**: **Low**. The change retains UTC precision, conforms to Pydantic schema validation, and fixes the warning cleanly.
*   **Exact Files to Change**:
    *   `core-lab/app/services/brief_assembler.py`
*   **Validation Commands**:
    ```bash
    python -m py_compile app/services/brief_assembler.py
    python -m pytest tests/unit/test_brief_assembler.py
    ```

---

### 2. `BaseAgentConfig` Deprecation Warning
*   **Warning Text**: `DeprecationWarning: BaseAgentConfig is deprecated and will be removed in future versions.`
*   **Likely Source**: `google-adk` internals (`google/adk/` modules).
*   **Why It Occurs**: The `google-adk` library uses deprecated config formats internally.
*   **Recommended Fix/Mitigation**: No action on source code. It is safe to suppress this warning in `pyproject.toml` or `pytest` configurations to clean up test output.
*   **Risk Level**: **Low**. Does not affect runtime behavior or Capstone submission readiness, as it is simple dependency warnings noise.
*   **Exact Files to Change**:
    *   `core-lab/pyproject.toml` (to add filterwarnings rules under `[tool.pytest.ini_options]`).
*   **Validation Commands**:
    ```bash
    python -m pytest tests/unit
    ```

---

### 3. `PLUGGABLE_AUTH` Experimental Feature Warning
*   **Warning Text**: `UserWarning: [EXPERIMENTAL] feature FeatureName.PLUGGABLE_AUTH is enabled.`
*   **Likely Source**: `google-adk` internals (`_feature_decorator.py:72`).
*   **Why It Occurs**: Emitted automatically by the ADK library when pluggable authentication features are loaded.
*   **Recommended Fix/Mitigation**: No action on source code. Pluggable authentication is handled by the ADK; disabling or changing it could break authentication hooks. Suppress in pytest configurations.
*   **Risk Level**: **Low**. Simply document as dependency noise.
*   **Exact Files to Change**: None.
*   **Validation Commands**:
    ```bash
    python scripts/run_sample_brief.py
    ```

---

### 4. `StdioServerParameters` Warning
*   **Warning Text**: `StdioServerParameters is not recommended. Please use StdioConnectionParams.`
*   **Likely Source**: `google-adk`'s MCP Session Manager (`google/adk/tools/mcp_tool/mcp_session_manager.py:398`).
*   **Why It Occurs**: The ADK session manager prefers its internal `StdioConnectionParams` helper class.
*   **Recommended Fix/Mitigation**: Keep using `StdioServerParameters` in [workflow.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/workflow.py). The session manager automatically intercepts and wraps `StdioServerParameters` inside `StdioConnectionParams` under the hood. Since `StdioConnectionParams` is an internal ADK wrapper rather than a public API class, writing direct imports for it could break compatibility in future ADK releases.
*   **Risk Level**: **Medium**. Defer changing this until after Jason's review to prevent ADK namespace/import regressions.
*   **Exact Files to Change (if updated later)**:
    *   `core-lab/app/workflow.py`
*   **Validation Commands**:
    ```bash
    python -m pytest tests/integration/test_demo_script.py
    ```

---

## Recommended Action Order

1.  **Fix `datetime.utcnow()` now** because it is in our application source code and presents zero risk.
2.  **Document or suppress `BaseAgentConfig` and `PLUGGABLE_AUTH`** warnings in `pyproject.toml` to clean up developer console output.
3.  **Defer `StdioServerParameters` changes** to prevent breaking MCP toolset orchestration.

---

## No-Action Items
-   **ADK Internal Warnings (`BaseAgentConfig` & `PLUGGABLE_AUTH`)**: Will not be modified. These belong to `google-adk` dependencies and do not block Kaggle submission or local dev work.
-   **StdioServerParameters**: Will not be replaced with internal ADK wrapper classes to keep toolset definitions standard and prevent breaking changes before Jason's review.

---

## Future Cleanup Branch
Suggest using this branch for future warning cleanups and package updates:
`veronica-warning-cleanup`
