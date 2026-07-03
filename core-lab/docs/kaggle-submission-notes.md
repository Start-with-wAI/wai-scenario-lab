# Kaggle Submission Notes

This document provides concise details and outlines for the Kaggle submission writeup and demo video.

---

## Submission Details

### 1. Track Recommendation
*   **Primary**: Agents for Business
*   **Secondary**: Agents for Good (as a framing for supporting micro business owners and promoting safe, educational AI practices)

### 2. Core Problem
Micro business owners frequently feel operational workflow friction (e.g., losing time after stressful client emails, losing notes, or stalling on writing marketing outlines), but they often struggle to define their problems clearly enough to utilize AI responsibly. They run the risk of leaking client PII or over-automating critical processes without proper boundaries.

### 3. Proposed Solution
A highly bounded, 4-agent educational prototype called **wAI Scenario Lab**. It guides owners through predefined scenarios, structures their observations, and outputs exactly one practical next action and exactly one non-monetary observation measurement.

### 4. Why It Matters
wAI Scenario Lab helps business owners practice structured, AI-assisted operational reflection without:
- Exposing proprietary or private business data.
- Creating dependency on complex, automated software decisions.
- Risking compliance issues (by explicitly withholding legal, medical, tax, or direct financial advice).

---

## Course Concepts Visualized

*   **Multi-Agent Architecture**: Built on Google ADK 2.0 graph workflow, utilizing 4 specialized agents (Scenario Guide, Workflow Analyst, Value and Evidence, Safety and Quality Review) with structured schema transitions.
*   **Model Context Protocol (MCP)**: Implements `scenario_config_server.py` to expose configuration metadata, scenario question resources, and observation selection tools to the agent context without hardcoding configuration into prompts.
*   **Safety and Privacy Controls**: Implements deterministic pre-filters to redact PII (emails, phone numbers, passwords) and block high-risk regulatory or prohibited direct automation requests.
*   **Config-Driven Design**: UI text, questions, and metrics are completely driven by `wai_scenario_config.json`, allowing scenarios to be added or revised without code changes.
*   **Testable Evaluation**: Validated with a 28-test suite (covering safety, MCP configuration, brief assembler, and pipeline checks).
*   **Antigravity-Assisted Development**: Built pair-programming with the Google DeepMind Antigravity coding assistant to align schemas and ensure compliance constraints.

---

## Demo Video Outline (Under 5 Minutes)

1.  **Problem & Audience (0:45)**:
    - Pitch the challenges faced by micro business owners.
    - Introduce wAI Scenario Lab as the educational gateway.
2.  **Scenario Selection & Config-Driven Design (0:45)**:
    - Briefly show how scenarios like `cool_down_tax` are loaded directly from `wai_scenario_config.json`.
3.  **Run Sample Brief (1:00)**:
    - Execute `scripts/run_sample_brief.py` to demonstrate the pipeline.
    - Highlight the output: exactly one action, exactly one non-monetary measurement, and the required disclosures.
4.  **Show Safety & Compliance Gate (1:00)**:
    - Change input to trigger `REVISE` (submitting PII/emails) or `BLOCKED` (asking for legal advice).
    - Show that Scenario Brief details are withheld, demonstrating the safety gate.
5.  **Test Suite Walkthrough (0:30)**:
    - Show `pytest` execution verifying safety logic, configuration server, and brief assembler.
6.  **Explain Responsible AI Boundaries (0:30)**:
    - Highlight the intentional exclusion of ROI/monetary math and professional/regulatory advice.
7.  **Future Enhancements (0:30)**:
    - Outline next steps (e.g. enabling Agent Platform API in dev project, wiring live Human-in-the-Loop triage UI, adding additional podcast episode scenarios).

---

## Known Limitations

- **Educational Prototype**: Designed as an offline simulator and educational tool, not a finished production application.
- **Predefined Scenarios Only**: Users must choose from predefined configurations; freeform scenario creation is disabled.
- **No Direct Integrations**: Does not connect to email clients, calendars, financial systems, or database backends.
- **No File Uploads**: Does not allow document uploads to prevent intellectual property leakage.
- **No Automatic Decisions**: Only suggests observation prompts; does not perform actions on behalf of the user.
- **GCP Environment Dependency**: Full integration tests querying Gemini models require enabling the Agent Platform API (`aiplatform.googleapis.com`) on the active Google Cloud project.
