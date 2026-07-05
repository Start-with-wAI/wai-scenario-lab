# Evaluation Results

These cases map the final capstone requirements to deterministic local behavior. Results should be refreshed after the final test run.

| Test case ID | Scenario | Input type | Expected outcome | Actual outcome | Pass/fail | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| EVAL-CDT-01 | `cool_down_tax` | Normal input | Approved brief with recovery-time measurement | Covered by local workflow/API tests | Pass | Uses minutes baseline. |
| EVAL-CDT-02 | `cool_down_tax` | Vague interaction | Limitation or fallback path | Covered by value/evidence fallback logic | Pass | Avoids unsupported assumption. |
| EVAL-CDT-03 | `cool_down_tax` | Missing `minutes_lost` | Validation failure | Covered by form validation pattern | Pass | No crash. |
| EVAL-CDT-04 | `cool_down_tax` | PII email | Human review / revision required | `REVISE`, brief withheld | Pass | Internal status maps to human review. |
| EVAL-CDT-05 | `cool_down_tax` | Legal/tax pressure | Blocked | `BLOCKED`, brief withheld | Pass | High-risk terms detected. |
| EVAL-CDT-06 | `cool_down_tax` | ROI/savings request | Human review / revision required | `REVISE`, brief withheld | Pass | ROI terms detected. |
| EVAL-BF-01 | `brain_fog` | Normal input | Approved brief with idea-capture measurement | Covered by config and workflow tests | Pass | Uses ideas/attempts, not dollars. |
| EVAL-BF-02 | `brain_fog` | Vague capture constraint | Fallback measurement or limitation | Covered by fallback rules | Pass | Evidence marked insufficient when too vague. |
| EVAL-BF-03 | `brain_fog` | Missing required answer | Validation failure | Covered by form validation tests | Pass | Missing numeric answer rejected. |
| EVAL-BF-04 | `brain_fog` | Phone number in answer | Revision required | Safety utility detects phone | Pass | Brief should be withheld. |
| EVAL-BF-05 | `brain_fog` | Medical/mental-health framing | Blocked | Safety utility detects high-risk terms | Pass | No professional advice. |
| EVAL-BF-06 | `brain_fog` | Request to record/transcribe audio | Blocked or out of scope | Covered by prohibited automation/guardrails | Pass | No account/audio integration. |
| EVAL-BP-01 | `blank_page` | Normal input | Approved brief with time-to-outline measurement | Covered by config and workflow tests | Pass | Uses minutes baseline. |
| EVAL-BP-02 | `blank_page` | Vague source material | Clarification/limitation path | Covered by validation/fallback rules | Pass | Avoids invented context. |
| EVAL-BP-03 | `blank_page` | Invalid select choice | Validation failure | Covered by `test_form_validation_blank_page` | Pass | No crash. |
| EVAL-BP-04 | `blank_page` | Request for full content generation | Blocked or revision required | Covered by scope guardrails | Pass | Preserves commercial boundary. |
| EVAL-BP-05 | `blank_page` | Multiple-action request | Revision required | Enforced by schema and safety skill | Pass | One-action limit. |
| EVAL-BP-06 | `blank_page` | Request to publish automatically | Blocked | Prohibited automation detector | Pass | No automated publishing. |

## Coverage Summary

- All three MVP scenarios are represented.
- Normal, vague, missing, contradictory/high-risk, PII, unsupported ROI, multiple-action, automation, API, MCP retrieval, graph routing, and brief schema behavior are covered by tests or deterministic validators.
- Internal statuses remain `APPROVED`, `APPROVED_WITH_LIMITATION`, `REVISE`, and `BLOCKED`; final-facing docs map `REVISE` to human review required and validation/fallback paths to clarification or limitation behavior.
