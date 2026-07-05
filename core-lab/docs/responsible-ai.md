# Responsible AI

wAI Scenario Lab is an educational prototype that uses AI to help micro business owners think through one fictional workflow-friction scenario. It is not a professional adviser or automation system.

## AI Disclosure

The UI and Scenario Brief disclose that AI is used to analyze the answers the user provides. The prototype is designed for reflection and planning support, not delegated decision-making.

## Privacy And PII Handling

Users are told not to enter confidential or personal information. Deterministic checks scan text for email addresses, phone numbers, password-like strings, account-like strings, and similar sensitive details. When detected, the app withholds the completed brief and routes the case to revision or human review.

The application does not support file uploads, email access, cloud-drive access, account integrations, persistent user profiles, or private client data storage.

## Human Review

Every completed Scenario Brief includes a human-review reminder. The suggested action is a starting point only. The user remains responsible for deciding whether it fits their business, customers, tools, and obligations.

## High-Risk Domain Exclusions

The prototype does not provide legal, medical, mental-health, tax, employment, lending, housing, insurance, financial planning, or regulatory compliance advice. Inputs that push into those domains are blocked or withheld.

## No Invented ROI

The Scenario Lab does not calculate dollar savings, ROI, opportunity cost, annual value, marketing equity, guarantees, or financial projections. Measurements are limited to observable non-financial units such as minutes, incidents, ideas, or attempts.

## No Automated Actions

The app does not send messages, publish content, purchase items, file documents, submit forms, connect accounts, change settings, or perform account actions. It recommends at most one manual, low-risk, reversible next step.

## Transparency Alignment

In plain language, the prototype aligns with Colorado AI Act-style transparency expectations by telling users AI is involved, limiting use to a low-risk educational context, and keeping humans responsible for decisions.

It aligns with FTC-style consumer protection expectations by avoiding inflated claims, unsupported savings, hidden automation, deceptive certainty, or advice outside the product's stated scope.

## Evidence

- Deterministic checks: `core-lab/app/services/safety.py`
- Output withholding: `core-lab/app/services/brief_assembler.py`
- Required disclosures: `core-lab/wai_scenario_config.json`
- Safety skill: `core-lab/.agents/skills/safety-reviewer/SKILL.md`
- Threat model: `core-lab/docs/stride-threat-model.md`
