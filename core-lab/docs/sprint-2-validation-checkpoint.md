# Sprint 2 Checkpoint: Server-side Validation and Normalized Input

This document describes the validation rules, active routes, and execution instructions for Sprint 2.

## What Sprint 2 Added

1. **Validation Utility Module**:
   - Created [form_validation.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/form_validation.py) containing:
     - `validate_episode_01_form()`: Validates form submission dictionary values against configuration-defined types and constraints.
     - `build_episode_01_workflow_payload()`: Normalizes validated answers and merges them with scenario metadata into a clean JSON-serializable workflow payload.

2. **Form Renderer Updates**:
   - Updated `render_episode_01_page()` and `render_question_html()` in [config_loader.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/config_loader.py) to support:
     - Pre-filling text/textarea input fields with previously entered values.
     - Restoring checked state on radio groups.
     - Preserving invalid number strings for user correction.
     - Displaying field-specific error messages and an error summary.

3. **HTTP POST Handler**:
   - Registered the `POST /` route in [fast_api_app.py](file:///c:/Users/MissV/Documents/Google/wai-scenario-lab/wai-scenario-lab/core-lab/app/fast_api_app.py) to capture form inputs and return:
     - **HTTP 400 Bad Request**: If validation fails (renders form with error summary and pre-filled inputs).
     - **HTTP 200 OK**: If validation succeeds (renders a checkpoint page showing the pretty-printed normalized JSON payload and the exact message: `Sprint 2 checkpoint: input validated and normalized. Agent workflow has not run yet.`).

4. **Routing Priority Reordering**:
   - Implemented a safe route-filtering block in `fast_api_app.py` that identifies both `GET /` and `POST /` and inserts them at the front of `app.routes` to override the default ADK `/` redirect while keeping all other endpoints (`/dev-ui`, `/docs`, `/openapi.json`) intact.

---

## Active Routes

- `GET /` — Renders the Episode 01 questionnaire.
- `POST /` — Validates submitted form fields, re-rendering the form on errors (400) or displaying the normalized payload (200).
- `/dev-ui` — ADK developer interface.
- `/docs` — API documentation.
- `/openapi.json` — API schema.

---

## Enforced Validation Rules (Config-Driven)

1. **`interaction_type`** (text):
   - Required: Yes
   - Constraints: Strips whitespace. Rejects empty or whitespace-only inputs. Enforces `max_length: 500`.

2. **`frequency`** (radio):
   - Required: Yes
   - Constraints: Must match one of the configured option values (`less_than_monthly`, `one_to_three_monthly`, `weekly`, `several_weekly`).

3. **`minutes_lost`** (number):
   - Required: Yes
   - Constraints: Must be a whole number, numeric, non-negative, and fit in the range `0` to `480`.

4. **`work_disrupted`** (textarea):
   - Required: Yes
   - Constraints: Strips whitespace. Rejects empty or whitespace-only inputs. Enforces `max_length: 500`.

---

## Intentionally Not Implemented Yet

- **ADK Agent Execution**: The multi-agent pipeline is not executed yet.
- **ADK Graph Execution**: The graph orchestrator does not run.
- **Scenario Brief Rendering**: The Scenario Brief schema is not populated.
- **`/brief.json` Route**: This route is not registered.
- **Episode 02/03 Content**: Form layouts and validation are disabled for other episodes.

---

## How to Run Tests

Run the full unit test suite:
```bash
uv run pytest tests/unit
```

---

## How to Verify Manually

1. **Start the Local Server**:
   ```bash
   uv run uvicorn app.fast_api_app:app --host 127.0.0.1 --port 8000
   ```

2. **Verify Invalid Form Submission**:
   - Open a browser or query via `curl`/`requests`.
   - Submit the form with empty or invalid values (e.g., negative `minutes_lost`).
   - Check that the server returns **HTTP 400** and the HTML page contains the error summary at the top and field-specific error messages.

3. **Verify Valid Form Submission**:
   - Submit the form with correct data.
   - Check that the server returns **HTTP 200** and shows the normalized payload page containing the text: `Sprint 2 checkpoint: input validated and normalized. Agent workflow has not run yet.`
