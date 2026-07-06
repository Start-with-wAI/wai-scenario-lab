# wAI Scenario Lab Core

`core-lab/` is the active runnable application for the Kaggle Vibecoding Agents Capstone submission.

## What It Does

A micro business owner selects one fictional workflow-friction scenario, answers four guided questions, and receives a concise Scenario Brief with one friction summary, one practical next step, one non-financial measurement, assumptions or missing evidence, a human-review reminder, and a related podcast CTA.

## Active Scenarios

- `cool_down_tax`: recovery time after stressful business communications.
- `brain_fog`: ideas lost before capture.
- `blank_page`: friction when starting business content.

All scenario content is loaded from `wai_scenario_config.json`.

## Core Concepts Demonstrated

- Multi-agent workflow using an ADK-style graph plus deterministic local adapter.
- MCP server exposing scenario configuration to the workflow.
- Modular agent skills under `.agents/skills/`.
- Deterministic security and privacy checks.
- Local reproducibility through tests and sample script.

## Run Locally

```bash
python -m pip install -r ..\requirements.txt
python scripts/run_sample_brief.py
python -m uvicorn app.fast_api_app:app --host 127.0.0.1 --port 8000
```

From the repository root, use `cd core-lab` before running the commands above. On macOS/Linux, use `../requirements.txt`.

## Test Locally

```bash
python -m pytest tests/unit tests/integration
```

GCP/Agent Platform tests are skipped unless `RUN_GCP_INTEGRATION_TESTS=1` is set.

## Final Docs

- `docs/final-capstone-readiness-audit.md`
- `docs/architecture/agent-graph.md`
- `docs/responsible-ai.md`
- `docs/evaluation/evaluation-results.md`
- `docs/kaggle-submission-checklist.md`
- `docs/demo-script.md`
- `docs/final-test-results.md`

## Copyright

Copyright 2026 Start with wAI. Prepared for the Kaggle Vibecoding Agents Capstone competition. See the repository root NOTICE.md for attribution details.

