# Final Test Results

Run date: 2026-07-05
Environment: Windows PowerShell, repository path `wai-scenario-lab/core-lab`

## Commands Run

| Command | Result | Notes |
| --- | --- | --- |
| `python --version` | Pass | Global Python is `3.13.14`. |
| `python -m compileall app mcp_server scripts tests` | Pass | Compiled app, MCP server, scripts, and tests successfully. |
| `python -m pytest tests/unit tests/integration` | Fail in global Python | Collection failed because global Python did not have the `mcp` package installed. This was an environment dependency issue, not a test assertion failure. |
| `.\.venv\Scripts\python.exe --version` | Pass | Project virtual environment Python is `3.13.14`. |
| `.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration` | Pass | Latest run: `97 passed, 4 skipped in 18.10s`. |
| `.\.venv\Scripts\python.exe scripts\run_sample_brief.py` | Pass | Produced an approved Cool Down Tax Scenario Brief through local deterministic workflow. |
| `.\.venv\Scripts\python.exe -m pip check` | Pass | `No broken requirements found.` |

## Skipped Tests

Four tests are skipped by default because they require live GCP/Agent Platform or ADK streaming credentials. They can be enabled by setting `RUN_GCP_INTEGRATION_TESTS=1` in an appropriately configured environment.

## Warnings

Known third-party warnings filtered by pytest configuration:

- ADK experimental feature warnings.
- OpenTelemetry and Vertex AI deprecation warnings from installed dependencies.
- FastAPI/Starlette `httpx` deprecation warning.
- `python_multipart` pending deprecation warning from ADK's FastAPI helper.
- Duplicate ADK dev server OpenAPI operation ID warning from imported ADK routes.
- Pytest cache warning from the read-only `.pytest_cache` directory; pytest cache provider is disabled for local runs.

Project-owned `datetime.utcnow()` usage was replaced with timezone-aware UTC timestamps, and known third-party dependency warnings are filtered in pytest configuration.

## Fixes Applied Before Final Test Run

- Replaced root `requirements.txt` with reproducible project dependencies and removed the absolute local editable dependency.
- Added missing `python-multipart` dependency to `core-lab/pyproject.toml`.
- Added `core-lab/mcp_server/__init__.py` for package clarity.
- Added missing modular agent skills.
- Updated final-facing docs and checklist.
- Added scenario status mapping in `wai_scenario_config.json` to explain final-facing status terms.
- Replaced deprecated `datetime.utcnow()` usage with timezone-aware UTC timestamps.
- Restored `pip` in the project virtual environment with `ensurepip` and confirmed dependency consistency with `pip check`.

## Post-Archive Verification

After moving unused historical docs and the legacy standalone demo scaffold into `core-lab/docs/archive/final-cleanup-2026-07-05/`, the full local test suite was rerun with the project virtual environment:

| Command | Result | Notes |
| --- | --- | --- |
| `.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration` | Pass | `97 passed, 4 skipped in 18.10s`. |
| `.\.venv\Scripts\python.exe -m pip check` | Pass | `No broken requirements found.` |

A scan of active docs excluding `core-lab/docs/archive/**` found no remaining absolute local file URLs, local Windows user paths, or localhost URLs in judge-facing documentation.

## Remaining Known Issues

- Live ADK/Gemini graph execution still requires credentials and Google Cloud setup; local deterministic graph simulation is what passed.
- Final Kaggle writeup, cover image, YouTube video, and public project link must still be completed outside the automated test suite.
- A brand-new clean environment install is still recommended before submission, although the existing project virtual environment now passes `pip check`.

