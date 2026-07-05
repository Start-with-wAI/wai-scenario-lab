# wAI Scenario Lab

The wAI Scenario Lab is a configuration-driven, multi-agent prototype that helps micro business owners examine one common workflow frustration and receive:

- One grounded friction summary
- One practical next action
- One useful measurement
- One human-review reminder
- One related wAI podcast episode

The prototype is being developed for the Google and Kaggle Vibe Coding Agents Capstone Project.

## Project principle

One scenario, one insight, one measurement, and one responsible next step.

## Initial scenarios

1. The Cool Down Tax
2. Brain Fog
3. The Blank Page

Each scenario uses the same application structure and agent pipeline. Scenario-specific questions, measurements, boundaries, and podcast metadata are loaded from configuration.

## Agent structure

### Agent 1: Scenario Guide
Gathers the user’s answers, identifies missing information, and requests no more than one clarification.

### Agent 2: Workflow Analysis
Identifies the likely friction point, separates known facts from assumptions, and proposes one low-risk next action.

### Agent 3: Value and Evidence
Selects one useful measure, evaluates the available evidence, and prevents unsupported savings or ROI claims.

### Agent 4: Safety and Quality Review
Checks privacy, scope, unsupported claims, human-review language, and release readiness before a Scenario Brief is displayed.

## Repository structure

```text
wai-scenario-lab/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── core-lab/
│   ├── .agents/
│   │   ├── skills/
│   │   └── CONTEXT.md
│   ├── app/
│   │   ├── app_utils/
│   │   └── services/
│   ├── deployment/
│   │   └── terraform/
│   │       ├── shared/
│   │       └── single-project/
│   ├── docs/
│   │   ├── archive/
│   │   └── evidence/
│   ├── mcp_server/
│   ├── scripts/
│   ├── tests/
│   │   ├── eval/
│   │   ├── integration/
│   │   └── unit/
│   ├── Dockerfile
│   ├── GEMINI.md
│   ├── README.md
│   ├── agents-cli-manifest.yaml
│   ├── pyproject.toml
│   ├── uv.lock
│   └── wai_scenario_config.json
├── scenario-lab-demo/
│   ├── .htaccess
│   ├── README_SCENARIO_LAB_DEMO.md
│   ├── index.cgi
│   ├── main.py
│   └── passenger_wsgi.py
├── .gitignore
├── README.md
└── requirements.txt
```
