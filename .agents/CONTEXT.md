# Local Project Context & Secure Coding Standards

## 1. Core Technical Architecture
- **Framework**: Google Agent Development Kit (google-adk>=2.0.0).
- **Orchestration**: Multi-agent Graph Workflow using the ADK 2.0 Graph API (functions, stateful edges, and RequestInput HIL pauses).
- **Data Transport**: Model Context Protocol (FastMCP Python) serving static scenario configurations and deterministic ROI tools on STDIO.

## 2. Paved Roads & Guardrails
- **No Mental Math**: LLMs must never perform financial or time calculations. All metrics (such as the Task Tax, Weekly Capture Yield, and Compound Time) must be calculated using deterministic Python functions exposed as FastMCP tools.
- **PII & Privacy Security**: Strictly redact any customer details, PII, names, or credentials locally before data enters any agent context.
- **No Code Drift**: Code is disposable. Acceptance criteria must be documented in BDD Gherkin .feature files (Given-When-Then format) with stable scenario IDs.
- **Out of Scope**: Block or gracefully revise any request attempting to rewrite/send emails, record/transcribe speech, connect to external APIs, or generate commercial implementations.
