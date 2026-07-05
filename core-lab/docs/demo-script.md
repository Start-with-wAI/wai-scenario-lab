# Five-Minute Demo Script

Target length: 5 minutes or less. Public YouTube video required.

## 0:00-0:30 Opening Problem - Verónica

Introduce wAI Scenario Lab as an Agents for Business prototype for micro business owners. State the problem: recurring workflow friction costs time and attention, but the user needs one bounded next step, not a full consulting engagement.

## 0:30-1:05 User Journey - Verónica

Show the landing page and scenario selection. Select one scenario, preferably `cool_down_tax`, and point out the AI disclosure and privacy warning. Complete the four-question form with fictional, non-sensitive answers.

## 1:05-1:45 Scenario Brief - Verónica

Show the approved Scenario Brief. Highlight the friction summary, one next step, one measurement, assumptions/unknowns, human-review reminder, and podcast CTA. Say the principle: one scenario, one insight, one measurement, one responsible next step.

## 1:45-2:35 Architecture And Graph - Verónica

Show `core-lab/docs/architecture/agent-graph.md` or `core-lab/app/workflow.py`. Explain the four agents: Scenario Guide, Workflow Analysis, Value and Evidence, and Safety and Quality Review. Clarify that the repo includes an ADK-style graph plus deterministic local adapter for reproducible testing without live credentials.

## 2:35-3:15 Measurement And MCP - Jason

Show `core-lab/mcp_server/scenario_config_server.py` and `core-lab/wai_scenario_config.json`. Explain that the MCP server exposes scenario IDs, questions, measurements, and podcast metadata from configuration. Emphasize non-financial measurements: minutes, incidents, ideas, attempts.

## 3:15-3:55 Safety Case - Jason

Run or show a safety-block case such as legal/tax pressure, email address, ROI request, or automatic publishing request. Explain deterministic controls in `core-lab/app/services/safety.py` and that unsafe or revision-required cases withhold the completed brief.

## 3:55-4:25 Tests And Evidence - Jason

Show local test output or `core-lab/docs/final-test-results.md`. Mention the 18-case evaluation matrix in `core-lab/docs/evaluation/evaluation-results.md`. Show Antigravity task/code-diff evidence if available; otherwise state that the final video must include it before submission.

## 4:25-5:00 Closing Value - Verónica And Jason

Close with the value: safe, bounded AI support for real micro-business friction. Remind judges the public prototype avoids proprietary assessments, account access, file uploads, automated actions, and unsupported ROI claims.

## Screens To Prepare

- Landing page
- Scenario selector
- Questionnaire
- Approved Scenario Brief
- Safety block or human-review-required case
- Agent graph/workflow code
- MCP server/config code
- Test results
- Antigravity task or code diff evidence
