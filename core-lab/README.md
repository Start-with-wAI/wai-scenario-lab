# wAI Scenario Lab

wAI Scenario Lab is an educational multi-agent prototype that helps micro business owners examine one fictional workflow-friction scenario and receive one practical next action, one observation measurement, and responsible-use reminders. 

The project demonstrates building secure, compliant, and config-driven AI agent workflows utilizing the Google Agent Development Kit (ADK) 2.0.

---

## Architecture Overview

### Active Implementation
The `core-lab/` directory is the single active, runnable implementation source of truth.

### MVP Scenarios (Config-Driven)
All scenario configurations, metadata, questions, and metrics are defined in [wai_scenario_config.json](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/wai_scenario_config.json):
*   **`cool_down_tax`**: Examines outsized emotional and time recovery overhead after a difficult business interaction.
*   **`brain_fog`**: Identifies capture friction for ideas that occur at inconvenient times.
*   **`blank_page`**: Examines content creation start friction before reaching a draft outline.

### Four-Agent Graph Workflow
Execution is structured as a sequential graph workflow:
1.  **Scenario Guide (Agent 1)**: Pre-processes inputs, redacts sensitive details, and structures raw user answers.
2.  **Workflow Analysis (Agent 2)**: Identifies a single process friction point and proposes exactly one practical next action.
3.  **Value and Evidence (Agent 3)**: Resolves non-financial baseline measurements and metrics for observation.
4.  **Safety and Quality Review (Agent 4)**: Enforces safety gates, quality metrics, and professional advice boundaries.

---

## Capstone Concepts Demonstrated

-   **Multi-Agent Graph Orchestration**: Structured state transitions and Human-in-the-Loop loops using Google ADK 2.0.
-   **Model Context Protocol (MCP)**: Exposes config metadata and metrics dynamically to Agent 3 using a safe [scenario_config_server.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/mcp_server/scenario_config_server.py).
-   **Deterministic Safety Pre-filters**: Programmatically blocks high-risk domains and redacts personal data (PII) before LLM invocation.
-   **Scenario Brief Assembler**: Assembles final Pydantic-validated brief outcomes and ensures non-approved (`REVISE` / `BLOCKED`) flows withhold sensitive information.
-   **Grounded Disclosures**: Disclosures and CTA URLs are injected dynamically from the config file to prevent LLM hallucinations.
-   **Testing & Evaluation Suite**: Verified with 28 passing unit and offline integration tests.

---

## Local Setup & Execution

### Requirements
- **uv**: Astral's Python package manager. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

### Setup Commands
Install dependencies in the workspace virtual environment:
```bash
cd core-lab
uv sync
```

### Run Local Demo
To demonstrate the complete wAI Scenario Lab pipeline on a sample payload offline (without network or GCP credentials):
```bash
uv run python scripts/run_sample_brief.py
```

### Run Test Suite
Run local unit and integration tests:
```bash
uv run pytest tests/unit tests/integration
```

> ⚠️ **Test Results Note**: 28 local/offline tests pass successfully. 4 integration tests querying Gemini models (`test_agent_stream`, `test_adk_run_sse`, etc.) fail with a `403 Forbidden` error if the target Google Cloud project lacks the Agent Platform API (`aiplatform.googleapis.com`) enablement or required developer permissions. This does not impact local capstone validation.

---

## Responsible-Use Boundaries

wAI Scenario Lab enforces strict compliance and ethical guidelines:
1.  **No Professional Advice**: Does not provide legal, medical, tax, financial planning, employment, lending, housing, insurance, or regulatory compliance advice.
2.  **No Monetary ROI/Savings Calculations**: Decouples calculations entirely from dollar figures, annual savings, opportunity costs, marketing equity, or guaranteed productivity gains. Outputs are limited to non-financial metrics (e.g. minutes, incident counts).
3.  **PII Privacy Redaction**: Personal names, company names, emails, and passwords are programmatically redacted.
4.  **Human-in-the-Loop Required**: All suggested actions and measurements are observational starting points; users remain responsible for decisions.
