# Verónica Integration Walkthrough

This walkthrough explains the work completed on `veronica-day1-adapt-main` to integrate Verónica's Scenario Lab assets with Jason's committed `core-lab/` scaffold. It is written for Jason, reviewers, and future contributors who need a clear day-by-day view of what was completed, what is active, what is intentionally bounded, and how to validate the branch locally.

The organization follows the Gemini Review 3-Day Parallel Execution Plan:

1. Day 1: Scaffolding, FastMCP, and specifications
2. Day 2: ADK graph orchestration and agent implementations
3. Day 3: automated testing, documentation, and video-readiness

## Current Branch State

```text
Branch: veronica-day1-adapt-main
Base: main, after Jason's core-lab scaffold was merged
Status: Review checkpoint branch
Active source of truth: core-lab/
```

This branch is not a direct merge of Verónica's earlier root-level scaffold. Instead, it ports the useful scenario, schema, validation, Scenario Brief, safety, MCP, and documentation work into Jason's active `core-lab/` structure.

## Why This Integration Approach Was Used

Jason's merged work established the active `core-lab/` scaffold on `main`. Verónica's work existed separately with scenario configuration, guided-question structure, validation logic, Scenario Brief concepts, low-fidelity flow decisions, and documentation.

Directly merging both structures would have created competing root-level folders, duplicate workflows, and unclear runtime ownership. This branch keeps one active implementation path:

```text
core-lab/
```

The result is a shared foundation that preserves Jason's scaffold while integrating Verónica's Day 1 product, scenario, schema, and workflow work.

---

# Day 1: Scaffolding, FastMCP, and Specifications

## Plan Reference

From the Gemini Review 3-Day Parallel Execution Plan:

- Verónica: set up the Kaggle notebook skeleton using `%writefile` blocks, scaffold the `wai_scenario_lab/` directory structure, and integrate `wai_scenario_config.json`.
- Jason: write Gherkin-style behavioral specifications for all three scenarios and draft the custom FastMCP configuration server.
- Deliverable: a fully compiled repository folder structure, functional MCP resource endpoints, and executable behavioral test specifications.

## What Was Completed in This Branch

### 1. Active `core-lab/` repository structure preserved

Jason's `core-lab/` scaffold remains the active implementation structure. Verónica's Day 1 work was integrated into that scaffold rather than creating competing root-level app, docs, tests, or MCP folders.

Relevant path:

```text
core-lab/
```

### 2. Scenario configuration integrated

Updated:

```text
core-lab/wai_scenario_config.json
```

The configuration supports the three MVP fictional, podcast-derived scenarios:

1. `cool_down_tax`
2. `brain_fog`
3. `blank_page`

The configuration includes:

- shared app metadata
- shared UI copy
- privacy and transparency notices
- required-answer rules
- high-risk domain boundaries
- sensitive-data categories
- agent input and output interfaces
- Scenario Brief schema expectations
- all 12 guided questions across the three scenarios
- validation messages
- primary and fallback observation measurements
- clarification prompts
- scenario-specific guardrails
- episode CTA metadata

This completes the reusable scenario-configuration foundation.

### 3. Reviewer-facing integration plan added

Added:

```text
core-lab/docs/integration-plan.md
```

This documents the decision to port Verónica's assets into Jason's `core-lab/` scaffold instead of merging duplicate structures.

### 4. Repository scaffold documentation added

Added:

```text
core-lab/docs/repository-scaffold.md
```

This gives Jason and reviewers a map of the active repository structure and explains how the files support the capstone.

### 5. Safe FastMCP scenario configuration server added

Added:

```text
core-lab/mcp_server/scenario_config_server.py
```

This is the intended MVP MCP server.

It exposes safe configuration capabilities:

- list available scenarios
- retrieve scenario metadata
- retrieve scenario questions
- retrieve scenario measurement definitions
- select a primary or fallback observation measure

It intentionally avoids ROI, dollar savings, opportunity cost, annual value, five-year value, marketing equity, and productivity guarantees.

### 6. ROI MCP server deprecated for the public MVP

Updated:

```text
core-lab/mcp_server/roi_calculator_server.py
```

The old ROI calculator server remains only as a deprecated scaffold artifact for review context. It is not the active MVP MCP server.

Reason:

- The public capstone is an educational Scenario Lab, not a business valuation or ROI calculator.
- Our plan says the prototype should avoid invented savings, unsupported ROI, full ROI models, opportunity-cost calculations, and marketing-equity claims.
- Agent 3's capstone role is to select one defensible observation measure and identify insufficient evidence, not to produce financial valuation outputs.

### 7. Behavioral specifications covered through pytest tests

The Gemini plan mentioned Gherkin-style behavioral specifications. In this branch, the executable behavior coverage is implemented through pytest unit and integration tests rather than `.feature` files.

Added:

```text
core-lab/tests/unit/test_scenario_config_mcp.py
core-lab/tests/unit/test_safety.py
core-lab/tests/unit/test_brief_assembler.py
core-lab/tests/integration/test_phase4_pipeline.py
core-lab/tests/integration/test_demo_script.py
```

These tests cover the expected behaviors behind the Gherkin-style plan:

- the three stable scenario IDs exist
- each scenario has the expected question structure
- safe MCP scenario configuration behavior works
- sensitive-data and high-risk checks work
- unsupported ROI and dollar-value language is blocked or flagged
- Scenario Brief assembly follows the approved structure
- blocked and revision statuses do not render completed briefs
- the local demo script can run without GCP

## Day 1 Status

```text
Complete enough for review.
```

The branch now has a compiled repository structure, scenario configuration, safe MCP configuration server, and executable behavior tests. The only difference from the Gemini wording is that tests are implemented with pytest rather than separate Gherkin `.feature` files.

---

# Day 2: ADK 2.0 Graph Orchestration and Agent Implementations

## Plan Reference

From the Gemini Review 3-Day Parallel Execution Plan:

- Verónica: code the ADK 2.0 graph workflow, set up transition paths, function nodes, and edges. Integrate the dynamic questionnaire form on the landing page.
- Jason: standardize modular skills folders, write Pydantic input models, and code the RequestInput Human-in-the-Loop gateway.
- Deliverable: a fully operational multi-agent graph running locally, capable of transitioning from user input to final reviewed output.

## What Was Completed in This Branch

### 1. wAI Scenario Lab agent identity added

Updated:

```text
core-lab/app/agent.py
```

The generic sample agent identity was replaced with the wAI Scenario Lab identity. The root agent now identifies the app as an educational prototype for micro business workflow friction and includes key safety boundaries:

- users should not submit sensitive or confidential information
- outputs are limited to one practical next action and one measurement
- the app does not provide legal, medical, tax, financial planning, employment, lending, housing, insurance, or regulatory-compliance advice
- the app does not calculate ROI, dollar savings, opportunity costs, annual value, marketing equity, or guaranteed productivity gains
- hidden prompts, chain-of-thought, internal routing details, and quality scores are not exposed

### 2. Four-agent ADK workflow structure added

Updated:

```text
core-lab/app/workflow.py
```

The workflow represents the intended four-agent sequence:

1. Scenario Guide
2. Workflow Analysis
3. Value and Evidence
4. Safety and Quality Review

The workflow includes:

- agent instructions
- state transitions
- deterministic safety routing
- terminal states for approved, approved-with-limitation, and blocked outcomes
- a human triage node using `RequestInput`

### 3. Active MCP exposure cleaned up

The workflow was adjusted so the public MVP path no longer relies on the deprecated ROI calculator server as the active Agent 3 tool path.

The intended MVP MCP server is:

```text
core-lab/mcp_server/scenario_config_server.py
```

This aligns Agent 3 with the capstone's safer measurement role:

- choose one observation measure
- use scenario configuration
- avoid unsupported financial claims
- avoid false precision
- flag insufficient evidence when needed

### 4. Pydantic schema contracts implemented

Updated:

```text
core-lab/app/schemas.py
```

The schema layer now provides structured contracts for:

- `ScenarioInputState`
- `AnalysisState`
- `CalculationState`
- `SafetyReviewState`
- `Measurement`
- `Redaction`
- `EpisodeCTA`
- `ScenarioBrief`

Validation includes:

- lowercase scenario IDs
- list cleanup and de-duplication
- cautious language checks
- assumption and unknown count limits
- one-action enforcement
- single-sentence rationale enforcement
- evidence-strength validation
- renderable Scenario Brief statuses only
- required human-review and responsible-use disclosures

### 5. Deterministic safety utilities implemented

Added:

```text
core-lab/app/services/safety.py
```

This service provides deterministic checks for:

- sensitive information
- email-like content
- phone-like content
- account-number-like content
- password-like content
- high-risk domains
- unsupported claims
- prohibited automation requests
- text sanitization

These checks support Jason's Agent 4 lane while keeping sensitive and high-risk behavior outside the public MVP output.

### 6. Scenario Brief assembler implemented

Added:

```text
core-lab/app/services/brief_assembler.py
```

The assembler combines sanitized inputs, workflow analysis, measurement output, safety review status, disclosures, and episode CTA content into the final Scenario Brief structure.

Approved outputs include:

- what we heard
- where friction may be occurring
- assumptions
- one next step
- why this step
- exactly one measurement
- unknowns
- redaction metadata
- human-review reminder
- responsible-use limitation
- episode CTA

For `REVISE` and `BLOCKED`, the assembler withholds completed Scenario Brief sections so unapproved content is not rendered.

### 7. Local deterministic demo path added

Added:

```text
core-lab/scripts/run_sample_brief.py
```

This script runs the `cool_down_tax` sample through a deterministic local demo path and prints a readable Scenario Brief.

Purpose:

- demonstrate the core pipeline without requiring GCP
- give reviewers a quick local validation path
- provide a stable demo output for the writeup and video

### 8. Demo output sample added

Added:

```text
core-lab/docs/demo-output-sample.md
```

This gives a readable example of the final Scenario Brief output.

## What Is Not Yet Fully Completed From Day 2

The dynamic questionnaire UI and landing page are not yet fully built in this branch. The branch prepares the backend configuration, workflow, schema, safety, and demo foundation needed for that UI work.

Day 2 UI work should continue on a new branch after Jason review or after this branch is merged.

## Day 2 Status

```text
Backend and orchestration foundation complete enough for review.
UI implementation remains next work.
```

---

# Day 3: Automated Testing, Documentation, and Video-Readiness

## Plan Reference

From the Gemini Review 3-Day Parallel Execution Plan:

- Jason: execute automated tests against the evaluation cases, generate the STRIDE Threat Model using Antigravity CLI, and document wAI's responsible AI approach.
- Verónica: polish the UI, deploy the prototype, draft the technical README, and compile the Kaggle Writeup under 2,500 words.
- Together: film the five-minute YouTube walkthrough, with Verónica presenting the user journey and architecture while Jason demonstrates Antigravity and explains security/HIL boundaries.
- Deliverable: tests, documentation, presentation materials, video, and final submission.

## What Was Completed in This Branch

### 1. README updated for judge-readiness

Updated:

```text
core-lab/README.md
```

The README now explains:

- the project name and purpose
- active implementation path
- MVP scenarios
- four-agent workflow
- capstone concepts demonstrated
- local setup
- local demo command
- test command
- GCP integration-test note
- responsible-use boundaries

### 2. Evaluation documentation added

Added:

```text
core-lab/docs/evaluation.md
```

This documents validation results and the distinction between:

- local/offline tests
- optional GCP deployment tests

GCP-dependent tests should be treated as deployment-only and skipped unless `RUN_GCP_INTEGRATION_TESTS=1` is set.

### 3. Responsible AI documentation added

Added:

```text
core-lab/docs/responsible-ai.md
```

This documents the responsible-use posture of the MVP, including:

- transparency
- sensitive-data avoidance
- human decision authority
- high-risk domain boundaries
- no professional advice
- no automatic account actions
- no unsupported ROI or savings claims

### 4. Commercial boundary documentation added

Added:

```text
core-lab/docs/commercial-boundaries.md
```

This explains what the public capstone demonstrates and what it intentionally does not expose.

The public prototype demonstrates:

- friction identification
- evidence organization
- one observation measure
- one responsible next step

It does not disclose:

- full diagnostic scoring
- complete implementation plans
- automation recipes
- proprietary prompts
- vendor-selection methods
- full ROI models
- content-generation systems
- file-taxonomy products
- AI acceptable-use policy generators
- client-specific workflows

### 5. Architecture documentation added

Added:

```text
core-lab/docs/architecture.md
```

This supports the Kaggle writeup and video by documenting the system architecture, agent flow, safety boundary, and configuration-driven design.

### 6. Kaggle submission notes added

Added:

```text
core-lab/docs/kaggle-submission-notes.md
```

This provides notes for the final writeup and video, including:

- recommended track framing
- problem statement
- solution summary
- course concepts visible in the code
- demo video outline
- known limitations

### 7. Phase recovery documentation retained for auditability

Added:

```text
core-lab/docs/phase-3-recovery-report.md
```

This remains as an internal recovery/audit artifact showing how work was stabilized after earlier tool or local-environment interruption.

### 8. Automated tests added and updated

Added or updated:

```text
core-lab/tests/unit/test_safety.py
core-lab/tests/unit/test_brief_assembler.py
core-lab/tests/unit/test_scenario_config_mcp.py
core-lab/tests/integration/test_phase4_pipeline.py
core-lab/tests/integration/test_demo_script.py
core-lab/tests/integration/test_agent.py
core-lab/tests/integration/test_server_e2e.py
```

Test coverage includes:

- scenario config loading
- MCP scenario configuration behavior
- sensitive-data handling
- high-risk domain handling
- unsupported claims
- one-action restraint
- Scenario Brief approval behavior
- blocked and revision behavior
- local demo script execution
- GCP-dependent test skipping unless explicitly enabled

### 9. Local validation completed

Reported local validation result:

```text
Static compile checks passed.
28 local/offline tests passed.
GCP-dependent tests are deployment-only and require RUN_GCP_INTEGRATION_TESTS=1 plus correct GCP permissions/API enablement.
```

Previously observed GCP failures were caused by `403 Forbidden` on `sunny-sandbox-455515-h5`, where Agent Platform API permissions or enablement were missing. That is a deployment-environment issue, not a failure of the local Scenario Lab logic.

## What Is Not Yet Fully Completed From Day 3

The following remain future work:

- STRIDE threat model generation
- polished UI
- deployment
- public repository or public demo readiness review
- final architecture visuals
- final 5-minute YouTube walkthrough
- final Kaggle Writeup under 2,500 words
- final submission before the deadline

## Day 3 Status

```text
Documentation and local validation foundation complete enough for review.
Final submission assets remain next work.
```

---

# File-by-File Summary

## Application and workflow

```text
core-lab/app/agent.py
core-lab/app/workflow.py
core-lab/app/schemas.py
```

Purpose:

- replace generic sample identity with wAI Scenario Lab identity
- define the four-agent workflow structure
- support deterministic routing and human triage
- enforce structured data contracts

## Services

```text
core-lab/app/services/safety.py
core-lab/app/services/brief_assembler.py
core-lab/app/services/__init__.py
```

Purpose:

- provide deterministic safety checks
- sanitize risky input
- assemble the approved Scenario Brief
- withhold completed brief details for `REVISE` or `BLOCKED` statuses

## MCP servers

```text
core-lab/mcp_server/scenario_config_server.py
core-lab/mcp_server/roi_calculator_server.py
```

Purpose:

- `scenario_config_server.py` is the intended MVP MCP server.
- `roi_calculator_server.py` is deprecated for the public capstone MVP and remains only as a scaffold artifact for Jason review.

## Configuration

```text
core-lab/wai_scenario_config.json
```

Purpose:

- central scenario, question, validation, measurement, guardrail, and CTA configuration

## Demo

```text
core-lab/scripts/run_sample_brief.py
core-lab/docs/demo-output-sample.md
```

Purpose:

- demonstrate a local offline `cool_down_tax` Scenario Brief without GCP credentials
- provide a stable sample output for README, writeup, and video planning

## Documentation

```text
core-lab/README.md
core-lab/docs/architecture.md
core-lab/docs/commercial-boundaries.md
core-lab/docs/evaluation.md
core-lab/docs/integration-plan.md
core-lab/docs/kaggle-submission-notes.md
core-lab/docs/phase-3-recovery-report.md
core-lab/docs/repository-scaffold.md
core-lab/docs/responsible-ai.md
core-lab/docs/veronica-integration-walkthrough.md
```

Purpose:

- explain setup, architecture, boundaries, evaluation, responsible AI, integration history, and submission planning

## Tests

```text
core-lab/tests/unit/test_safety.py
core-lab/tests/unit/test_brief_assembler.py
core-lab/tests/unit/test_scenario_config_mcp.py
core-lab/tests/integration/test_phase4_pipeline.py
core-lab/tests/integration/test_demo_script.py
core-lab/tests/integration/test_agent.py
core-lab/tests/integration/test_server_e2e.py
```

Purpose:

- verify deterministic logic
- verify Scenario Brief assembly
- verify safe MCP behavior
- verify local demo execution
- keep GCP integration tests explicit and deployment-only

---

# Local Setup Walkthrough

Use these commands from PowerShell on Windows.

## 1. Open the repository

```powershell
cd C:\Users\MissV\Documents\Google\wai-scenario-lab\wai-scenario-lab
```

## 2. Confirm the branch

```powershell
git checkout veronica-day1-adapt-main
git pull --rebase origin veronica-day1-adapt-main
git status
```

Expected branch:

```text
veronica-day1-adapt-main
```

## 3. Enter the active project folder

```powershell
cd core-lab
```

## 4. Create a virtual environment if one does not already exist

```powershell
python -m venv .venv
```

## 5. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, use:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

You should see this at the beginning of the prompt:

```text
(.venv)
```

## 6. Install dependencies

Preferred path if `uv` is available:

```powershell
python -m pip install --upgrade pip
python -m pip install uv
uv sync
```

Fallback path:

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
```

---

# Local Validation Walkthrough

Run these commands from inside `core-lab/` with the virtual environment activated.

## Static compile checks

```powershell
python -m py_compile app/services/safety.py
python -m py_compile app/services/brief_assembler.py
python -m py_compile mcp_server/scenario_config_server.py
python -m py_compile app/workflow.py
python -m py_compile app/agent.py
python -m py_compile scripts/run_sample_brief.py
```

All of these should complete without output if they pass.

## Run local demo

```powershell
python scripts/run_sample_brief.py
```

Expected behavior:

- runs without GCP credentials
- uses the `cool_down_tax` sample
- prints a readable Scenario Brief
- includes one next action
- includes one measurement
- includes human-review and responsible-use reminders

## Run local tests

```powershell
python -m pytest tests/unit tests/integration
```

Expected behavior after GCP tests are guarded:

```text
Local/offline tests pass.
GCP-dependent tests are skipped unless RUN_GCP_INTEGRATION_TESTS=1 is set.
```

To intentionally run GCP-dependent tests:

```powershell
$env:RUN_GCP_INTEGRATION_TESTS="1"
python -m pytest tests/integration
```

Those tests require a properly configured GCP project, Agent Platform API enablement, authentication, and permissions.

---

# Responsible-Use Boundaries Preserved

The integration intentionally avoids:

- legal advice
- medical advice
- mental-health advice
- tax advice
- financial planning advice
- employment, lending, housing, insurance, or regulatory-compliance decisions
- ROI calculations
- dollar-savings calculations
- opportunity-cost calculations
- annual-value calculations
- marketing-equity claims
- productivity guarantees
- automatic sending, publishing, purchasing, cancellation, or account changes
- file uploads
- external account connections
- real client data

The app remains an educational prototype that uses fictional scenarios to help micro business owners practice clearer workflow-friction thinking.

---

# What This Branch Does Not Finalize

This branch does not finalize:

- Jason's full measurement methodology
- Jason's full safety scoring framework
- GCP deployment configuration
- STRIDE threat model
- polished UI
- production deployment
- public demo video
- final Kaggle writeup
- final Kaggle submission
- final merge into `main`

---

# Summary for Jason

This branch ports Verónica's Day 1 Scenario Lab work into Jason's committed `core-lab/` scaffold and moves the project into an early runnable foundation.

The branch now provides:

- a single active implementation path under `core-lab/`
- three config-driven MVP scenarios
- structured agent schemas
- wAI Scenario Lab agent identity
- four-agent workflow structure
- deterministic safety utilities
- Scenario Brief assembler
- safe scenario configuration MCP server
- deprecated ROI MCP server warning
- local offline demo script
- local/offline tests
- README and reviewer documentation

Recommended next step:

```text
Jason reviews this branch before additional Day 2 UI or deployment work continues.
```

Recommended follow-on branch:

```text
veronica-day2-scenario-ui
```

That next branch should focus on the dynamic questionnaire UI, Scenario Brief interface, visual polish, deployment preparation, and final submission assets.