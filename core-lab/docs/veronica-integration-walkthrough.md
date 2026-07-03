# Verónica Integration Walkthrough

This walkthrough explains the updates completed to integrate Verónica's Day 1 work with Jason's committed `core-lab` scaffold. It is written for Jason, reviewers, and future contributors who need a simple explanation of what changed and how to validate it locally.

## Purpose of This Work

Jason's work established the active `core-lab/` scaffold on `main`. Verónica's work existed in a separate branch with scenario configuration, guided-question structure, validation logic, Scenario Brief concepts, and documentation.

Rather than directly merging two competing repository structures, this update ports Verónica's useful assets into Jason's `core-lab/` structure. The result is one active implementation path instead of duplicate root-level `app/`, `docs/`, `tests/`, and `mcp_server/` folders.

The active source of truth is now:

```text
core-lab/
```

## Branch Used

```text
veronica-day1-adapt-main
```

This branch is based on `main` after Jason's scaffold work was merged.

## What Was Integrated

### 1. Scenario configuration

Updated:

```text
core-lab/wai_scenario_config.json
```

The configuration now supports the three MVP fictional scenarios:

1. `cool_down_tax`
2. `brain_fog`
3. `blank_page`

The config includes scenario metadata, guided questions, validation messages, guardrails, episode CTA content, and measurement definitions.

### 2. Schema contracts

Updated:

```text
core-lab/app/schemas.py
```

The schema layer now provides stronger data contracts for the Scenario Lab, including:

- Scenario input structure
- Analysis output structure
- Measurement output structure
- Safety review status structure
- Scenario Brief output structure
- Redaction metadata
- Episode CTA metadata
- Validation limits for assumptions, unknowns, cautious language, and one-action restraint

This helps keep the app's output structured, testable, and bounded.

### 3. Agent identity and workflow wiring

Updated:

```text
core-lab/app/agent.py
core-lab/app/workflow.py
```

The generic sample agent behavior was replaced with the wAI Scenario Lab identity. The workflow now represents the intended four-agent sequence:

1. Scenario Guide
2. Workflow Analysis
3. Value and Evidence
4. Safety and Quality Review

The workflow is intentionally bounded. It demonstrates the agent flow without claiming to finalize Jason's full measurement methodology or safety framework.

### 4. Safety utilities

Added:

```text
core-lab/app/services/safety.py
```

This service provides deterministic checks for:

- Sensitive information
- High-risk domains
- Unsupported claims
- Prohibited automation requests
- Basic text sanitization

These checks support the Safety and Quality Review path. They do not replace human judgment or claim legal compliance.

### 5. Scenario Brief assembler

Added:

```text
core-lab/app/services/brief_assembler.py
```

This service assembles a Scenario Brief using sanitized inputs, workflow analysis, measurement output, release status, disclosures, and episode CTA content from configuration.

Approved outputs include:

- one next action
- one measurement
- human-review reminder
- responsible-use limitation
- scenario-specific podcast CTA

Blocked or revision paths do not render completed Scenario Brief sections.

### 6. Safe MCP configuration server

Added:

```text
core-lab/mcp_server/scenario_config_server.py
```

This MCP server exposes safe scenario configuration capabilities:

- list available scenarios
- get scenario metadata
- get scenario questions
- get scenario measurement definitions
- select a primary or fallback observation measure

It intentionally avoids ROI, dollar savings, opportunity cost, annual value, five-year value, marketing equity, and productivity guarantees.

The existing ROI calculator MCP file remains present but should be treated cautiously until Jason reviews whether it should be removed, renamed, or kept outside the MVP path.

### 7. Tests

Added:

```text
core-lab/tests/unit/test_safety.py
core-lab/tests/unit/test_brief_assembler.py
core-lab/tests/unit/test_scenario_config_mcp.py
core-lab/tests/integration/test_phase4_pipeline.py
```

The tests cover:

- sensitive-data detection
- high-risk request handling
- unsupported ROI or dollar-value language
- scenario config loading
- three MVP scenario availability
- exactly four guided questions per scenario
- Scenario Brief assembly
- blocked/revision behavior
- required human-review and responsible-use language
- sample `cool_down_tax` pipeline behavior

### 8. Documentation

Added or updated:

```text
core-lab/docs/architecture.md
core-lab/docs/commercial-boundaries.md
core-lab/docs/evaluation.md
core-lab/docs/integration-plan.md
core-lab/docs/phase-3-recovery-report.md
core-lab/docs/repository-scaffold.md
core-lab/docs/responsible-ai.md
core-lab/docs/veronica-integration-walkthrough.md
```

These documents explain architecture, boundaries, evaluation, responsible AI notes, repository organization, and the integration approach.

## Local Setup Walkthrough

Use these commands from PowerShell on Windows.

### 1. Open the repo

```powershell
cd C:\Users\MissV\Documents\Google\wai-scenario-lab\wai-scenario-lab
```

### 2. Confirm the branch

```powershell
git checkout veronica-day1-adapt-main
git pull
git status
```

Expected branch:

```text
veronica-day1-adapt-main
```

### 3. Enter the active project folder

```powershell
cd core-lab
```

### 4. Create a virtual environment if one does not already exist

```powershell
python -m venv .venv
```

### 5. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, use:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

You should see something like this at the beginning of the prompt:

```text
(.venv)
```

### 6. Install dependencies

If the project uses `uv`, run:

```powershell
python -m pip install --upgrade pip
python -m pip install uv
uv sync
```

If `uv sync` is not available in the environment, install from the project metadata instead:

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
```

## Local Validation Walkthrough

Run these commands from inside `core-lab/` with the virtual environment activated.

### Static compile checks

```powershell
python -m py_compile app/services/safety.py
python -m py_compile app/services/brief_assembler.py
python -m py_compile mcp_server/scenario_config_server.py
python -m py_compile app/workflow.py
python -m py_compile app/agent.py
```

All of these should complete without output if they pass.

### Local tests

```powershell
python -m pytest tests/unit tests/integration
```

Latest local result reported by Verónica:

```text
28 tests passed
4 GCP integration tests failed due to 403 Forbidden on sunny-sandbox-455515-h5 because the Agent Platform API is disabled or permissions are missing
```

The 403 failures are deployment-environment issues, not local Scenario Lab logic failures. They should be skipped or marked as deployment-only before final judge-facing validation.

## What This Does Not Complete

This work does not finalize:

- Jason's full measurement methodology
- Jason's full safety scoring framework
- GCP deployment configuration
- polished UI
- public demo video
- Kaggle writeup
- root-level duplicate cleanup
- final PR merge into `main`

## Responsible-Use Boundaries Preserved

The integration intentionally avoids:

- legal advice
- medical advice
- tax advice
- financial planning advice
- employment, lending, housing, insurance, or regulatory-compliance decisions
- ROI calculations
- dollar-savings calculations
- opportunity-cost calculations
- marketing-equity claims
- productivity guarantees
- automatic actions
- file uploads
- external account connections
- real client data

The app remains an educational prototype that uses fictional scenarios to help micro business owners practice clearer workflow-friction thinking.

## Summary for Jason

The branch does not directly merge Verónica's old root-level scaffold into `main`. Instead, it ports the useful Day 1 scenario, schema, validation, and documentation work into Jason's existing `core-lab/` scaffold.

The result is a cleaner shared foundation:

- Jason's scaffold remains the active structure.
- Verónica's scenario and Scenario Brief work is integrated into that structure.
- The app now has a bounded wAI Scenario Lab identity.
- The workflow has a testable four-agent path.
- Safety, MCP configuration, brief assembly, and tests are present for review.

Recommended next step: Jason reviews this branch before additional implementation or cleanup work continues.