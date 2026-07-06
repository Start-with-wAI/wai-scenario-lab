# wAI Scenario Lab

wAI Scenario Lab is a lightweight multi-agent prototype for the Kaggle Vibecoding Agents Capstone Project. It is positioned for the **Agents for Business** track.

## Problem

Micro business owners often lose time and attention to recurring workflow friction: stressful communications, ideas that disappear before capture, or business content that stalls at the blank page. They usually do not need a full consulting engagement to take the next step. They need one bounded observation, one practical action, and a reminder that they remain responsible for decisions.

## Solution

The Scenario Lab lets a user choose one fictional business-friction scenario, answer four guided questions, and receive a concise Scenario Brief with:

- a short friction summary
- known facts, constraints, assumptions, and unknowns
- exactly one low-risk next step
- exactly one non-financial measurement
- a human-review reminder
- a related wAI podcast episode reference

Project principle: **One scenario, one insight, one measurement, and one responsible next step.**

## MVP Scenarios

- `cool_down_tax`: measures recovery time after stressful business communications.
- `brain_fog`: examines why ideas are lost before they can be captured.
- `blank_page`: identifies friction when starting business content.

All scenario questions, measurements, podcast references, and guardrails are loaded from [core-lab/wai_scenario_config.json](core-lab/wai_scenario_config.json).

## Why Agents

The workflow benefits from separate agent responsibilities: one agent structures user input, one analyzes workflow friction, one selects evidence and measurement, and one reviews safety and release quality. This separation makes the prototype easier to test, safer to constrain, and clearer to explain than a single unbounded prompt.

## Architecture

The active application lives in [core-lab](core-lab/).

Four-agent workflow:

1. **Scenario Guide**: presents the scenario, structures answers, identifies missing details, and strips obvious sensitive data.
2. **Workflow Analysis**: separates facts from assumptions and recommends one low-risk next action.
3. **Value and Evidence**: selects one configured non-financial measurement and prevents unsupported ROI claims.
4. **Safety and Quality Review**: checks privacy, high-risk domains, unsupported claims, one-action restraint, required disclosures, and human review.

The code includes an ADK-style graph workflow in [core-lab/app/workflow.py](core-lab/app/workflow.py) and a deterministic local adapter so tests and the demo can run without live Gemini credentials. The graph uses nodes for scenario input, scenario guide, workflow analysis, value/evidence, safety review, brief formatting, human review, approved output, blocked output, and clarification/human-triage paths.

Architecture details: [core-lab/docs/architecture/agent-graph.md](core-lab/docs/architecture/agent-graph.md)

## MCP Server

The local MCP server in [core-lab/mcp_server/scenario_config_server.py](core-lab/mcp_server/scenario_config_server.py) exposes scenario configuration to the agent workflow:

- available scenario IDs
- titles and descriptions
- guided questions
- podcast metadata
- primary and fallback measurements
- safety boundaries

It requires no secrets and no external network access for local tests.

## Agent Skills

Modular skills are stored under [core-lab/.agents/skills](core-lab/.agents/skills/):

- `scenario-guide`
- `workflow-analyst`
- `value-evidence-reviewer`
- `safety-reviewer`
- `brief-formatter`

These are intentionally concise and avoid proprietary assessment logic.

## Security And Privacy

The prototype warns users not to enter confidential or personal information. Deterministic checks scan for email addresses, phone numbers, password-like strings, account-like strings, high-risk domains, prohibited automation requests, unsupported ROI/savings claims, and absolute certainty language.

The app does not support file uploads, email access, cloud-drive access, account integrations, persistent user profiles, automated sending, automated publishing, purchasing, filing, or account changes.

Responsible AI details: [core-lab/docs/responsible-ai.md](core-lab/docs/responsible-ai.md)

## Setup

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Run The Demo Locally

```bash
cd core-lab
python scripts/run_sample_brief.py
python -m uvicorn app.fast_api_app:app --host 127.0.0.1 --port 8000
```

Open `/` and select one of the three scenarios.

## Run Tests

```bash
cd core-lab
python -m pytest tests/unit tests/integration
```

Some GCP/Agent Platform integration tests are skipped unless `RUN_GCP_INTEGRATION_TESTS=1` is set. The deterministic local tests do not require Google Cloud credentials.

Final test record: [core-lab/docs/final-test-results.md](core-lab/docs/final-test-results.md)

## Evaluation And Evidence

- Evaluation results: [core-lab/docs/evaluation/evaluation-results.md](core-lab/docs/evaluation/evaluation-results.md)
- Evidence folder: [core-lab/docs/evidence](core-lab/docs/evidence/)
- Kaggle checklist: [core-lab/docs/kaggle-submission-checklist.md](core-lab/docs/kaggle-submission-checklist.md)
- Demo script: [core-lab/docs/demo-script.md](core-lab/docs/demo-script.md)

## Kaggle Submission Notes

The Kaggle package still needs a public writeup under 2,500 words, a cover image, a YouTube video of 5 minutes or less, and a public project link. A live public demo is preferred; if unavailable, this repository can serve as the public project link with the setup instructions above.

Do not commit API keys, passwords, `.env` files, private customer data, or proprietary assessment material.

## Copyright

Copyright 2026 Start with wAI. Prepared for the Kaggle Vibecoding Agents Capstone competition. See [NOTICE.md](NOTICE.md) for attribution details.

