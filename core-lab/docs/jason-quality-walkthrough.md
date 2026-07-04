# Day 2 & 3 Quality, Rules & Safety Walkthrough

This document compiles the complete integration review, safety configuration, evaluation runs, and threat modeling executed by Jason LaMontagne (Data, Rules, and Quality Lead).

---

## 1. Zero-Trust Git Merge & Baseline Setup
- **Identity Configured**:
  - Name: `Jason LaMontagne`
  - Email: `jason.l@startwithwai.tech`
- **Actions**:
  - Fetched remote tracking branches.
  - Merged Verónica's active integration branch (`origin/veronica-day1-adapt-main`) into local branch `jason`.
  - Checked out the new local development branch `jason-day2-agent-implementations`.

---

## 2. ROI Calculator Deprecation
- **Boundary Enforced**: Confirmed the deprecation notice headers in [roi_calculator_server.py](file:///C:/Users/jason/Documents/antigravity/bold-hubble/wai-scenario-lab/core-lab/mcp_server/roi_calculator_server.py).
- **Architecture**: The server is completely decoupled and excluded from the active multi-agent pipeline. No dollar-based financial calculations are allowed in the Scenario Lab.

---

## 3. ADK 2.0 Graph Workflow Schema Updates
- **Validation**: Programmatically bound input and output Pydantic schemas for all 4 sequential agents in [workflow.py](file:///C:/Users/jason/Documents/antigravity/bold-hubble/wai-scenario-lab/core-lab/app/workflow.py) to prevent tampering.
- **Agent 3 Prompt Grounding**: Instruction prompt updated to select only single, non-monetary observation metrics from configurations and use default fallback measurements when inputs are vague.
- **Agent 4 Safety Skill**: Equipped Agent 4 (Safety Review Agent) with a portable agent skill under [.agents/skills/safety-reviewer/SKILL.md](file:///C:/Users/jason/Documents/antigravity/bold-hubble/wai-scenario-lab/core-lab/.agents/skills/safety-reviewer/SKILL.md) to inspect and enforce:
  - PII Redaction checking
  - Strict non-financial product boundaries (no calculations in dollars, no ROI, no opportunity-cost projections)
  - Prohibited advice domains
  - One-action next step constraint
  - Mandatory disclosures (human-in-the-loop reminder and responsible use disclaimer)

---

## 4. Day 3 Agent Evaluations
- **Execution Command**:
  ```powershell
  $env:PYTHONPATH="C:\Users\jason\Documents\antigravity\bold-hubble\wai-scenario-lab\core-lab"; $env:VIRTUAL_ENV=""; uv --system-certs run --with pip-system-certs agents-cli eval run --dataset tests/eval/datasets/basic-dataset.json --config tests/eval/eval_config.yaml
  ```
- **Local Sandbox SSL Workaround**: Implemented `sitecustomize.py` to globally patch `ssl.create_default_context` and `urllib3.util.ssl_.create_urllib3_context` so that Python requests/aiohttp connect cleanly to Google OAuth and AI Platform endpoints through local proxy/sandbox firewalls.
- **Evaluation Summary**:
  - Passed all evaluation test cases successfully with a perfect mean score of `5.0000`.
  - Saved grade reports under [grade_results/](file:///C:/Users/jason/Documents/antigravity/bold-hubble/wai-scenario-lab/core-lab/artifacts/grade_results/).

---

## 5. STRIDE Threat Model
- Compiled a comprehensive STRIDE Threat Model detailing safety boundaries, threat matrices, and mitigations at [stride-threat-model.md](file:///C:/Users/jason/Documents/antigravity/bold-hubble/wai-scenario-lab/core-lab/docs/stride-threat-model.md).

---

## 6. Responsible AI Documentation
- Updated the project's [responsible-ai.md](file:///C:/Users/jason/Documents/antigravity/bold-hubble/wai-scenario-lab/core-lab/docs/responsible-ai.md) document to formalize the new safety skill checks, input/output validation schemas, and physical deprecation of financial calculations.
