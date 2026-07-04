# Responsible AI & Safety Guardrails

The wAI Scenario Lab is designed from the ground up to prioritize user privacy, safety, and strict regulatory boundaries. 

## Key Principles & Guardrails

### 1. AI Transparency
Users must be clearly informed that the Scenario Lab is an educational prototype that uses artificial intelligence to analyze answers. This is enforced by displaying transparency and privacy notices before a scenario begins, and embedding required disclaimers directly into the final rendered Scenario Brief.

### 2. Zero Sensitive Data (PII Redaction)
The application has a strict zero-PII policy. Users are cautioned against entering names, emails, company names, or other personal data. Agent 1 is instructed to sanitize and redact any personal identifiers. Agent 4 performs a final check; if unauthorized PII is detected, the brief is flagged as `REVISE` or `BLOCKED`.

### 3. Mandatory Human Review
The prototype acts as an advisory assistant, not a decision-maker. All generated briefs must display the `human_review_reminder` reminding users that they remain responsible for verifying that any suggested action fits their business context.

### 4. No Professional Advice
The AI must not provide legal, medical, mental-health, tax, financial, employment, lending, housing, insurance, or regulatory compliance advice. Any user inputs pushing the agent into these domains are blocked.

### 5. Technical Boundaries
To prevent security and operational escalation, the system enforces the following boundaries:
*   **No external account connections**: The app does not connect to email, calendar, or external accounts.
*   **No automatic actions**: The app does not write, send, or execute actions on behalf of the user.
*   **No file uploads**: The app accepts only plain text and numeric form answers.

### 6. No Financial ROI or Guaranteed Savings Claims
The system does not estimate dollar savings, ROI, or financial values. LLM attempts to calculate financial benefits are blocked. Measurements must be expressed in non-financial units (e.g., minutes lost, number of ideas, capture attempts).

### 7. Agent 4 Safety Role
Agent 4 (Safety and Quality Review Agent) acts as the final gatekeeper. It is equipped with a portable agent skill located in [.agents/skills/safety-reviewer/](file:///C:/Users/jason/Documents/antigravity/bold-hubble/wai-scenario-lab/core-lab/.agents/skills/safety-reviewer/SKILL.md) which instructs it to:
- Inspect the output for any leaked PII (names, emails, phones) and flag it if found.
- Detect any dollar-denominated claims, ROI, or financial projections and enforce fallback non-monetary units.
- Block prohibited domains (legal, medical, etc.).
- Ensure the mandatory AI disclosure/reminder is appended.

### 8. Architectural Enforcement & Deprecations
To guarantee that these principles are not just guidelines but system-level constraints, we implement the following:
*   **Pydantic Input/Output Schemas**: All 4 agents in [workflow.py](file:///C:/Users/jason/Documents/antigravity/bold-hubble/wai-scenario-lab/core-lab/app/workflow.py) use strict Pydantic schemas (e.g. `ValueEvidenceInput` and `SafetyReviewOutput`) to validate intermediate payloads, preventing session data tampering.
*   **Deprecation of ROI Calculator**: The server [roi_calculator_server.py](file:///C:/Users/jason/Documents/antigravity/bold-hubble/wai-scenario-lab/core-lab/mcp_server/roi_calculator_server.py) has been deprecated and excluded from the active pipeline to completely eliminate the capability of the system to calculate monetary opportunity costs or financial ROI.
*   **Stateful Agent Edges**: Agent 4 reviews the consolidated state before any output is returned to the user interface, acting as a deterministic safety gate.

