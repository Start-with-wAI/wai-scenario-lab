# Final Capstone Readiness Audit

Audit date: 2026-07-05
Repository: `Start-with-wAI/wai-scenario-lab`
Current branch: `veronica-day2-scenario-ui`
Audit rerun scope: active repository files, final docs, evidence folder, archived cleanup location, dependency files, scenario config, skills, MCP server, existing virtual environment, and a fresh throwaway reproducibility environment.

## Commands Run During This Audit

| Command | Result | Finding |
| --- | --- | --- |
| `git status --short` | Pass | Worktree contains expected final cleanup moves/additions; changes are not committed yet. |
| `rg -n "roi_calculator_server|deprecated-roi-calculator|test_roi_calculator|calculate_task_tax|calculate_content_factory_value|financial calculator|calculator server|MCP calculator" ...` | Pass | No active references found outside archive exclusions. |
| `rg -n "file:///|C:\\Users|http://127\\.0\\.0\\.1:8000|http://localhost:8000" ...` | Pass with one test-only hit | Only active local URL hit is `core-lab/tests/integration/test_server_e2e.py`, which is expected test configuration. |
| `.venv\Scripts\python.exe -m compileall app mcp_server scripts tests` | Pass | App, MCP server, scripts, and tests compile. |
| `.venv\Scripts\python.exe -m pytest tests/unit tests/integration` | Pass | Existing project venv: `97 passed, 4 skipped in 19.63s`. |
| `.venv\Scripts\python.exe -m pip check` | Pass | Existing project venv: `No broken requirements found.` |
| Fresh venv `pip install -r requirements.txt` | Pass | Dependencies installed into a brand-new throwaway environment. |
| Fresh venv `pip check` | Pass | Fresh reproducibility venv: `No broken requirements found.` |
| Fresh venv `pytest tests/unit tests/integration` | Pass | Fresh reproducibility venv: `97 passed, 4 skipped in 20.22s`. |

## Current Readiness Summary

The repository is now reproducible from a brand-new virtual environment using the root `requirements.txt`. The original P0 gaps for missing docs, missing skills, reproducible root requirements, stale ROI calculator references, local absolute file paths, final evidence capture, project-owned datetime warnings, existing-venv dependency validation, and fresh-environment dependency validation have been addressed.

The remaining work is concentrated in final Kaggle submission assets and final repository hygiene.

## What Is Ready

- Root and `core-lab` README files explain the active project and setup path.
- `requirements.txt` no longer contains an absolute local editable dependency.
- Fresh environment install from `requirements.txt` passes.
- Existing project venv and fresh reproducibility venv both pass `pip check`.
- Existing project venv and fresh reproducibility venv both pass the unit/integration suite.
- Final docs exist:
  - `core-lab/docs/architecture/agent-graph.md`
  - `core-lab/docs/evaluation/evaluation-results.md`
  - `core-lab/docs/kaggle-submission-checklist.md`
  - `core-lab/docs/demo-script.md`
  - `core-lab/docs/evidence/README.md`
  - `core-lab/docs/final-test-results.md`
- Five agent skill folders exist under `core-lab/.agents/skills/` with YAML frontmatter.
- MCP scenario config server exists at `core-lab/mcp_server/scenario_config_server.py`, and `core-lab/mcp_server/__init__.py` exists for package clarity.
- No active references to `roi_calculator_server.py` or old calculator tool names were found in the active code/docs scan.
- Final evidence screenshots exist directly under `core-lab/docs/evidence/` and are indexed by `core-lab/docs/evidence/README.md`.
- Historical docs and the legacy standalone demo are archived under `core-lab/docs/archive/final-cleanup-2026-07-05/`.
- Deprecated project-owned `datetime.utcnow()` usage has been replaced with timezone-aware UTC timestamps.
- Known third-party dependency warnings are filtered in pytest configuration, keeping test output clean.

## Remaining P0 Before Kaggle Submission

1. Complete the external Kaggle submission assets.
   - Kaggle writeup.
   - Cover image / media gallery.
   - Public YouTube demo URL in `core-lab/docs/evidence/youtube-demo-link.txt`.
   - Public project link or live demo link.
   - Final license review.
   - Team/rules confirmations.

2. Remove generated browser profile folders from evidence if they are still present.
   - `core-lab/docs/evidence/_edge-profile/`
   - `core-lab/docs/evidence/_edge-profile2/`

3. Decide the final position on live ADK graph execution.
   - Local deterministic adapter tests pass.
   - Live ADK/Gemini execution remains credential-dependent.
   - `core-lab/app/workflow.py` terminal graph nodes are intentionally minimal; the FastAPI path renders ScenarioBrief output through the deterministic adapter.

## Remaining P1 Cleanup

1. Finalize deployability evidence.
   - Deployability remains `Partial` until a public demo is provided or the submission explicitly presents local reproducibility as the project link.

2. Finalize license review.
   - `core-lab/docs/kaggle-submission-checklist.md` still marks license compatibility as `Needs final review`.

## Remaining P2 Polish

1. Consider adding a compact `core-lab/docs/README.md` index for final judge-facing docs.
2. Update `core-lab/docs/archive/final-cleanup-2026-07-05/README.md` inventory to mention archived sprint evidence subfolders explicitly.
3. Make `core-lab/docs/evaluation/evaluation-results.md` more command-backed if the final writeup needs stronger evidence mapping.
4. Review `core-lab/docs/GoogleKaggle_VibeCodingProject_GeminiReview.md`; it is a primary source document, but it still contains stale pre-cleanup concerns about skills being only partially defined.

## Development And Testing Assessment

- Required for tested local functionality: complete; no failing local tests found.
- Required for dependency sanity and reproducibility: complete; fresh venv install, `pip check`, and tests pass.
- Required for submission completeness: finish external Kaggle assets and update checklist evidence after those assets exist.

## Documentation Assessment

- Final docs are present and mostly aligned.
- `core-lab/docs/kaggle-submission-checklist.md` records the latest passing local test run and fresh-environment reproducibility check.
- `core-lab/docs/evidence/README.md` correctly reflects the flattened evidence folder, but the YouTube URL is still a placeholder.

## Current Best Answers

| Question | Answer | Confidence | Evidence |
| --- | --- | --- | --- |
| Are there still dependencies on `roi_calculator_server.py`? | No active references found. | High | Active `rg` scan returned no matches. |
| Do tests pass in the existing project venv? | Yes. | High | `97 passed, 4 skipped in 19.63s`. |
| Do tests pass in a fresh reproducibility venv? | Yes. | High | `97 passed, 4 skipped in 20.22s`. |
| Is `pip check` fixed? | Yes for both the existing project venv and fresh reproducibility venv. | High | Both returned `No broken requirements found.` |
| Is clean install reproducibility proven? | Yes. | High | Fresh venv install from `requirements.txt` passed, then `pip check` and tests passed. |
| Do the four workflow TODO comments still need to be accomplished? | Not for the tested local FastAPI/deterministic workflow; only live Vertex/ADK deployment remains caveated. | Medium-high | Comments were rewritten as caveats; local tests pass. |
| Is the capstone fully submission-ready? | Not yet. | High | External Kaggle/media/link/license items remain pending. |

