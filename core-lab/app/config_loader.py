# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import logging

logger = logging.getLogger(__name__)

# Resolve config path relative to this file's directory (core-lab/app/)
CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "wai_scenario_config.json")
)


class ConfigLoadError(Exception):
    """Raised when config loading or validation fails."""
    pass


def load_scenario_config() -> dict:
    """Loads the active configuration file safely.

    Raises:
        ConfigLoadError: If config file is missing or contains malformed JSON.
    """
    if not os.path.exists(CONFIG_PATH):
        logger.error(f"Configuration file not found at {CONFIG_PATH}")
        raise ConfigLoadError("Scenario configuration file is missing.")

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Malformed configuration JSON at {CONFIG_PATH}: {e}")
        raise ConfigLoadError("Scenario configuration is malformed.")
    except Exception as e:
        logger.error(f"Unexpected error loading configuration at {CONFIG_PATH}: {e}")
        raise ConfigLoadError("Unexpected error loading configuration.")


def get_public_episode_01_config() -> dict:
    """Retrieves selected config items for Episode 01.

    Returns:
        A dictionary containing app metadata, shared UI copy, and Episode 01 scenario config.

    Raises:
        ConfigLoadError: If required keys are missing or the scenario is not found.
    """
    config = load_scenario_config()

    app_meta = config.get("app")
    shared_ui = config.get("shared_ui")
    scenarios = config.get("scenarios")

    if not app_meta or not shared_ui or not scenarios:
        raise ConfigLoadError("Required top-level keys ('app', 'shared_ui', 'scenarios') not found in config.")

    cool_down_tax = scenarios.get("cool_down_tax")
    if not cool_down_tax:
        raise ConfigLoadError("Scenario 'cool_down_tax' not found in config.")

    return {
        "app": app_meta,
        "shared_ui": shared_ui,
        "scenario": cool_down_tax
    }


def render_question_html(q: dict, value: any = None, error: str = None) -> str:
    """Renders a single question dynamically based on its configured type."""
    q_id = q.get("id")
    q_type = q.get("type")
    label = q.get("label", "")
    help_text = q.get("help_text", "")
    required = "required" if q.get("required") else ""

    val_str = str(value) if value is not None else ""
    help_html = f'<small class="help-text">{help_text}</small>' if help_text else ""
    error_html = f'<span class="field-error" id="{q_id}-error" role="alert">{error}</span>' if error else ""
    aria_describedby = f'aria-describedby="{q_id}-error"' if error else ""
    has_error_class = "has-error" if error else ""

    if q_type == "text":
        max_length_val = q.get("max_length")
        max_length = f'maxlength="{max_length_val}"' if max_length_val is not None else ""
        return f"""
        <div class="form-group {has_error_class}">
            <label for="{q_id}">{label}</label>
            {help_html}
            {error_html}
            <input type="text" id="{q_id}" name="{q_id}" {required} {max_length} value="{val_str}" {aria_describedby} placeholder="Describe briefly..." />
        </div>
        """

    elif q_type == "textarea":
        max_length_val = q.get("max_length")
        max_length = f'maxlength="{max_length_val}"' if max_length_val is not None else ""
        return f"""
        <div class="form-group {has_error_class}">
            <label for="{q_id}">{label}</label>
            {help_html}
            {error_html}
            <textarea id="{q_id}" name="{q_id}" {required} {max_length} {aria_describedby} placeholder="Enter your response...">{val_str}</textarea>
        </div>
        """

    elif q_type == "number":
        min_val = q.get("min")
        max_val = q.get("max")
        step_val = q.get("step")
        unit = q.get("unit", "")

        min_attr = f'min="{min_val}"' if min_val is not None else ""
        max_attr = f'max="{max_val}"' if max_val is not None else ""
        step_attr = f'step="{step_val}"' if step_val is not None else ""

        unit_html = f'<span class="number-unit">{unit}</span>' if unit else ""

        return f"""
        <div class="form-group {has_error_class}">
            <label for="{q_id}">{label}</label>
            {help_html}
            {error_html}
            <div class="number-input-wrapper">
                <input type="number" id="{q_id}" name="{q_id}" {required} {min_attr} {max_attr} {step_attr} value="{val_str}" {aria_describedby} />
                {unit_html}
            </div>
        </div>
        """

    elif q_type == "radio":
        options = q.get("options", [])
        options_html = ""
        for opt in options:
            opt_val = opt.get("value", "")
            opt_label = opt.get("label", "")
            checked = "checked" if val_str == opt_val else ""
            options_html += f"""
            <label class="radio-label">
                <input type="radio" name="{q_id}" value="{opt_val}" {required} {checked} />
                <span>{opt_label}</span>
            </label>
            """
        return f"""
        <fieldset class="form-group {has_error_class}">
            <legend>{label}</legend>
            {help_html}
            {error_html}
            <div class="radio-group">
                {options_html}
            </div>
        </fieldset>
        """
    else:
        return f"""
        <div class="form-group {has_error_class}">
            <label for="{q_id}">{label}</label>
            {help_html}
            {error_html}
            <input type="text" id="{q_id}" name="{q_id}" {required} value="{val_str}" {aria_describedby} />
        </div>
        """


def render_episode_01_page(config: dict, values: dict | None = None, errors: dict | None = None) -> str:
    """Renders the complete Episode 01 questionnaire HTML page using config settings."""
    app_meta = config["app"]
    shared_ui = config["shared_ui"]
    scenario = config["scenario"]

    app_name = app_meta.get("name", "wAI Scenario Lab")
    landing_headline = shared_ui.get("landing_headline", "")
    landing_supporting_copy = shared_ui.get("landing_supporting_copy", "")
    privacy_notice = shared_ui.get("privacy_notice", "")
    transparency_notice = shared_ui.get("transparency_notice", "")

    ep_title = scenario.get("title", "")
    ep_num = scenario.get("episode_number", "01")
    ep_desc = scenario.get("short_description", "")
    ep_context = scenario.get("context", "")
    ep_measure = scenario.get("measurement_preview", "")

    val_dict = values or {}
    err_dict = errors or {}

    error_summary_html = ""
    if err_dict:
        error_summary_html = """
        <div class="error-summary" role="alert">
            <h3 class="error-summary-title">Please review the highlighted fields</h3>
            <p>Some answers need attention. Review the highlighted fields and make the requested corrections.</p>
        </div>
        """

    questions_html = ""
    questions = scenario.get("questions", [])
    sorted_questions = sorted(questions, key=lambda x: x.get("order", 0))
    for q in sorted_questions:
        q_id = q.get("id")
        questions_html += render_question_html(q, value=val_dict.get(q_id), error=err_dict.get(q_id))

    submit_label = shared_ui.get("question_submit_label", "Analyze My Scenario")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_name} - {ep_title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

        :root {{
            --bg-color: #0b0f19;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent-color: #6366f1;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --font-sans: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}

        body {{
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: var(--font-sans);
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
        }}

        .container {{
            max-width: 720px;
            width: 100%;
            padding: 40px 20px;
            box-sizing: border-box;
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 20px;
        }}

        .logo {{
            font-size: 1.25rem;
            font-weight: 700;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
        }}

        .badge {{
            font-size: 0.75rem;
            font-weight: 600;
            background-color: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            padding: 4px 10px;
            border-radius: 12px;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }}

        h1 {{
            font-size: 2.25rem;
            font-weight: 700;
            line-height: 1.25;
            margin-bottom: 16px;
            letter-spacing: -0.03em;
            background: linear-gradient(135deg, #ffffff 0%, #d1d5db 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .lead {{
            font-size: 1.1rem;
            color: var(--text-secondary);
            margin-bottom: 32px;
        }}

        .notice-box {{
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 40px;
            backdrop-filter: blur(12px);
        }}

        .notice-title {{
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--accent-color);
            margin-bottom: 12px;
        }}

        .notice-item {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 12px;
        }}

        .notice-item:last-child {{
            margin-bottom: 0;
        }}

        .episode-card {{
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.02) 0%, rgba(255, 255, 255, 0) 100%);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 32px;
            margin-bottom: 40px;
        }}

        .episode-tag {{
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--accent-color);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 8px;
        }}

        .episode-title {{
            font-size: 1.75rem;
            font-weight: 700;
            margin: 0 0 16px 0;
            background: linear-gradient(135deg, #ffffff 0%, #e5e7eb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .episode-desc {{
            font-size: 1.05rem;
            color: var(--text-secondary);
            margin-bottom: 20px;
        }}

        .episode-context {{
            font-size: 0.95rem;
            color: var(--text-secondary);
            border-left: 2px solid var(--accent-color);
            padding-left: 16px;
            margin-bottom: 24px;
        }}

        .measurement-preview {{
            display: flex;
            align-items: center;
            gap: 12px;
            background-color: rgba(16, 185, 129, 0.06);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: 12px;
            padding: 12px 16px;
            font-size: 0.9rem;
            color: #a7f3d0;
        }}

        .measurement-preview svg {{
            color: var(--success-color);
            fill: none;
            stroke: currentColor;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }}

        .form-group {{
            margin-bottom: 28px;
        }}

        label {{
            display: block;
            font-size: 0.95rem;
            font-weight: 500;
            margin-bottom: 8px;
        }}

        .help-text {{
            display: block;
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }}

        input[type="text"],
        input[type="number"],
        textarea {{
            width: 100%;
            padding: 14px 16px;
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            color: var(--text-primary);
            font-family: var(--font-sans);
            font-size: 0.95rem;
            box-sizing: border-box;
            transition: all 0.2s ease;
        }}

        input[type="text"]:focus,
        input[type="number"]:focus,
        textarea:focus {{
            outline: none;
            border-color: var(--accent-color);
            background-color: rgba(255, 255, 255, 0.05);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
        }}

        textarea {{
            resize: vertical;
            min-height: 100px;
        }}

        .radio-group {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-top: 10px;
        }}

        .radio-label {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .radio-label:hover {{
            background-color: rgba(255, 255, 255, 0.04);
            border-color: rgba(255, 255, 255, 0.15);
        }}

        .radio-label input[type="radio"] {{
            margin: 0;
            accent-color: var(--accent-color);
        }}

        fieldset {{
            border: none;
            padding: 0;
            margin: 0;
        }}

        fieldset legend {{
            font-size: 0.95rem;
            font-weight: 500;
            margin-bottom: 8px;
            color: var(--text-primary);
        }}

        .btn-submit {{
            display: block;
            width: 100%;
            padding: 16px;
            background: var(--accent-gradient);
            color: #ffffff;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }}

        .btn-submit:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        }}

        .btn-submit:active {{
            transform: translateY(0);
        }}

        .number-input-wrapper {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .number-input-wrapper input {{
            flex-grow: 1;
        }}

        .number-unit {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            background-color: rgba(255, 255, 255, 0.05);
            padding: 14px 16px;
            border-radius: 10px;
            border: 1px solid var(--card-border);
            white-space: nowrap;
        }}

        /* Error Styles */
        .error-summary {{
            background-color: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 32px;
        }}

        .error-summary-title {{
            color: #fca5a5;
            margin: 0 0 6px 0;
            font-size: 1.05rem;
            font-weight: 600;
        }}

        .error-summary p {{
            color: var(--text-secondary);
            margin: 0;
            font-size: 0.9rem;
        }}

        .field-error {{
            display: block;
            color: #f87171;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 8px;
        }}

        .form-group.has-error input[type="text"],
        .form-group.has-error input[type="number"],
        .form-group.has-error textarea {{
            border-color: rgba(239, 68, 68, 0.5);
            background-color: rgba(239, 68, 68, 0.02);
        }}

        .form-group.has-error input[type="text"]:focus,
        .form-group.has-error input[type="number"]:focus,
        .form-group.has-error textarea:focus {{
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
            border-color: #ef4444;
        }}

        .form-group.has-error .radio-label {{
            border-color: rgba(239, 68, 68, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <span class="logo">{app_name}</span>
            <span class="badge">Prototype</span>
        </header>

        <main>
            <h1>{landing_headline}</h1>
            <p class="lead">{landing_supporting_copy}</p>

            {error_summary_html}

            <section class="notice-box" aria-label="Privacy and transparency">
                <div class="notice-title">Important Notices</div>
                <div class="notice-item"><strong>Privacy Notice:</strong> {privacy_notice}</div>
                <div class="notice-item"><strong>Transparency Notice:</strong> {transparency_notice}</div>
            </section>

            <section class="episode-card">
                <div class="episode-tag">Episode {ep_num}</div>
                <h2 class="episode-title">{ep_title}</h2>
                <p class="episode-desc">{ep_desc}</p>
                <div class="episode-context">{ep_context}</div>

                <div class="measurement-preview">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                    </svg>
                    <span>Possible measurement: <strong>{ep_measure}</strong></span>
                </div>
            </section>

            <form method="post" action="/">
                {questions_html}
                <button type="submit" class="btn-submit">{submit_label}</button>
            </form>
        </main>
    </div>
</body>
</html>
"""


def render_error_page(error_message: str) -> str:
    """Renders a simple, clean, user-friendly HTML error page for configuration failures."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application Error</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

        body {{
            margin: 0;
            padding: 0;
            background-color: #0b0f19;
            color: #f3f4f6;
            font-family: 'Outfit', sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}

        .error-page {{
            text-align: center;
            padding: 40px;
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            max-width: 500px;
            width: 90%;
        }}

        .error-icon {{
            font-size: 3rem;
            color: #ef4444;
            margin-bottom: 20px;
        }}

        h1 {{
            font-size: 1.75rem;
            margin-bottom: 12px;
        }}

        p {{
            color: #9ca3af;
            font-size: 1rem;
            margin-bottom: 0;
        }}
    </style>
</head>
<body>
    <div class="error-page">
        <div class="error-icon">⚠️</div>
        <h1>Configuration Error</h1>
        <p>{error_message}</p>
    </div>
</body>
</html>
"""


def render_checkpoint_page(response: dict) -> str:
    """Renders the Sprint 5 / Sprint 4 checkpoint success page with escaped JSON and Scenario Brief previews."""
    import json
    import html

    checkpoint_msg = response.get("message", "")
    adapter_status = response.get("adapter_status", "")
    checkpoint_name = response.get("checkpoint", "Sprint 4")

    is_sprint_5 = checkpoint_name == "Sprint 5"
    is_sprint_4 = checkpoint_name == "Sprint 4" or (not is_sprint_5 and "safety_precheck" in response)

    agent_1_input_pretty = json.dumps(response.get("agent_1_input", {}), indent=2, ensure_ascii=False)
    not_run_pretty = json.dumps(response.get("not_run", []), indent=2, ensure_ascii=False)

    safety_precheck_pretty = ""
    terminal_route_pretty = ""
    safety_trace_pretty = ""
    graph_trace_pretty = ""
    brief_preview_pretty = ""

    if is_sprint_5:
        brief_preview_pretty = json.dumps(response.get("scenario_brief_preview", {}), indent=2, ensure_ascii=False)
        terminal_route = response.get("terminal_route", "HUMAN_TRIAGE")
        brief_status = response.get("brief_preview_status", "REVISE")
    elif is_sprint_4:
        safety_precheck_pretty = json.dumps(response.get("safety_precheck", {}), indent=2, ensure_ascii=False)
        terminal_route_pretty = json.dumps(response.get("terminal_route_preview", {}), indent=2, ensure_ascii=False)
        safety_trace_pretty = json.dumps(response.get("safety_routing_trace", []), indent=2, ensure_ascii=False)
    else:
        graph_trace_pretty = json.dumps(response.get("graph_transition_trace", []), indent=2, ensure_ascii=False)

    esc_msg = html.escape(checkpoint_msg)
    esc_status = html.escape(adapter_status)
    esc_input = html.escape(agent_1_input_pretty)
    esc_not_run = html.escape(not_run_pretty)
    esc_brief_status = html.escape(str(response.get("brief_preview_status", "UNKNOWN")))
    esc_safety_precheck = html.escape(json.dumps(
        {"safety_precheck": response.get("safety_precheck", {})},
        indent=2,
        ensure_ascii=False
    ))

    badge_text = "Sprint 5 Checkpoint" if is_sprint_5 else ("Sprint 4 Checkpoint" if is_sprint_4 else "Checkpoint 3")
    title_text = "Terminal Output & Brief Preview" if is_sprint_5 else ("Safety Routing Verification" if is_sprint_4 else "Workflow Adapter Verification")

    # Render Sprint 5 specifics
    sprint_5_html = ""
    if is_sprint_5:
        esc_brief_json = html.escape(brief_preview_pretty)
        brief_preview_data = response.get("scenario_brief_preview", {})

        # Status badge colors
        badge_style = "background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3);"
        if brief_status == "APPROVED_WITH_LIMITATION":
            badge_style = "background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3);"
        elif brief_status == "REVISE":
            badge_style = "background-color: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3);"
        elif brief_status == "BLOCKED":
            badge_style = "background-color: rgba(220, 38, 38, 0.2); color: #ef4444; border: 1px solid rgba(220, 38, 38, 0.4);"

        # Render the brief details or withheld states
        if terminal_route in ("RENDER_BRIEF", "RENDER_LIMITATION_BANNER"):
            limitation_banner_html = ""
            if terminal_route == "RENDER_LIMITATION_BANNER":
                limitation_banner_html = f"""
                <div class="limitation-banner">
                    <strong>Limitation Warning:</strong> Use with caution: This brief is based on incomplete or uncertain information. Treat the measurement as an observation prompt rather than a conclusion.
                </div>
                """

            # Build assumptions
            assumptions_list = "".join(f"<li>{html.escape(item)}</li>" for item in brief_preview_data.get("assumptions", []))
            assumptions_html = f"<ul class='brief-bullets'>{assumptions_list}</ul>" if assumptions_list else "<p>None.</p>"

            # Build unknowns
            unknowns_list = "".join(f"<li>{html.escape(item)}</li>" for item in brief_preview_data.get("unknowns", []))
            unknowns_html = f"<ul class='brief-bullets'>{unknowns_list}</ul>" if unknowns_list else "<p>None.</p>"

            measurement_data = brief_preview_data.get("measurement", {})
            evidence_badge = "background-color: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3);"
            if measurement_data.get("evidence_strength") == "partial":
                evidence_badge = "background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3);"
            
            redaction_data = brief_preview_data.get("redaction", {})
            redaction_status_html = ""
            if redaction_data.get("applied"):
                redaction_cats = ", ".join(redaction_data.get("categories", []))
                redaction_status_html = f"""
                <div class="disclosure-box" style="border-color: rgba(245, 158, 11, 0.2); background: rgba(245, 158, 11, 0.02); color: #fbbf24;">
                    <strong>Sensitive Information Redacted:</strong> [{redaction_cats}] data was detected and sanitized to protect privacy.
                </div>
                """

            episode_cta = brief_preview_data.get("episode_cta", {})

            sprint_5_html = f"""
            <div class="section-title">Terminal Route Preview Result</div>
            <p>Terminal Route: <span class="badge" style="background-color: rgba(16, 185, 129, 0.15); color: #34d399; margin: 0; border: 1px solid rgba(16, 185, 129, 0.3);">{html.escape(terminal_route)}</span></p>
            <p>brief_preview_status: <strong>{esc_brief_status}</strong></p>

            <div class="section-title">Deterministic Scenario Brief Preview</div>
            <p style="color: #9ca3af; font-size: 0.9rem; margin-top: -10px;"><em>Disclaimer: This is a static, deterministic Scenario Brief preview for verification. No live LLM or agent generation has run.</em></p>

            <div class="brief-card">
                <div class="brief-header">
                    <div class="brief-title">{html.escape(brief_preview_data.get("scenario_title", "Scenario Title"))}</div>
                    <span class="badge" style="{badge_style}">{html.escape(brief_status)}</span>
                </div>

                {limitation_banner_html}

                <div class="brief-section">
                    <div class="brief-section-title">What We Heard</div>
                    <div class="brief-text">{html.escape(brief_preview_data.get("what_we_heard", ""))}</div>
                </div>

                <div class="brief-section">
                    <div class="brief-section-title">Where Friction May Be Occurring</div>
                    <div class="brief-text">{html.escape(brief_preview_data.get("where_friction_may_be_occurring", ""))}</div>
                </div>

                <div class="brief-section">
                    <div class="brief-section-title">Assumptions</div>
                    {assumptions_html}
                </div>

                <div class="brief-section">
                    <div class="brief-section-title">Proposed Next Step</div>
                    <div class="brief-text"><strong>Action:</strong> {html.escape(brief_preview_data.get("one_next_step", ""))}</div>
                    <div class="brief-text" style="margin-top: 6px;"><strong>Rationale:</strong> {html.escape(brief_preview_data.get("why_this_step", ""))}</div>
                </div>

                <div class="brief-section">
                    <div class="brief-section-title">Observation Measurement</div>
                    <div class="metric-box">
                        <div class="metric-value">{html.escape(measurement_data.get("baseline_display", ""))}</div>
                        <div class="brief-text"><strong>Metric:</strong> {html.escape(measurement_data.get("name", ""))}</div>
                        <div class="brief-text"><strong>Period:</strong> {html.escape(measurement_data.get("period", ""))}</div>
                        <div class="brief-text"><strong>Method:</strong> {html.escape(measurement_data.get("calculation_method", ""))}</div>
                        <div class="brief-text" style="margin-top: 8px;">
                            <strong>Evidence Strength:</strong> 
                            <span class="badge" style="{evidence_badge} font-size: 0.7rem; padding: 2px 6px; margin: 0;">{html.escape(measurement_data.get("evidence_strength", ""))}</span>
                        </div>
                    </div>
                </div>

                <div class="brief-section">
                    <div class="brief-section-title">Unknowns</div>
                    {unknowns_html}
                </div>

                {redaction_status_html}

                <div class="disclosure-box">
                    <strong>Human Review Reminder:</strong> {html.escape(brief_preview_data.get("human_review_reminder", ""))}
                </div>

                <div class="disclosure-box">
                    <strong>Responsible Use Limitation:</strong> {html.escape(brief_preview_data.get("responsible_use_limitation", ""))}
                </div>

                <div class="cta-box">
                    <div class="brief-title" style="font-size: 1.1rem; margin-bottom: 4px;">{html.escape(episode_cta.get("title", "Learn More"))}</div>
                    <p style="font-size: 0.9rem; margin-bottom: 12px; color: #9ca3af;">{html.escape(episode_cta.get("description", ""))}</p>
                    <a href="{html.escape(episode_cta.get("url", "#"))}" target="_blank" class="cta-button">Listen to Podcast Episode</a>
                </div>
            </div>

            <div class="section-title">Assembled Scenario Brief JSON</div>
            <pre>{esc_brief_json}</pre>
            <div class="section-title">Safety Precheck Snapshot</div>
            <pre>{esc_safety_precheck}</pre>
            """
        elif terminal_route == "HUMAN_TRIAGE":
            sprint_5_html = f"""
            <div class="section-title">Terminal Route Preview Result</div>
            <p>Terminal Route: <span class="badge" style="background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; margin: 0; border: 1px solid rgba(245, 158, 11, 0.3);">{html.escape(terminal_route)}</span></p>
            <p>brief_preview_status: <strong>{esc_brief_status}</strong></p>

            <div class="withheld-box">
                <div class="withheld-title">Human Triage Required</div>
                <p style="margin: 0; color: #fca5a5;">This scenario needs human review before a Scenario Brief can be shown.</p>
                <p style="margin-top: 10px; margin-bottom: 0; font-size: 0.9rem; color: #f87171;">
                    <strong>Instructions:</strong> {html.escape(brief_preview_data.get("revision_instructions", ""))}
                </p>
            </div>

            <div class="section-title">Assembled Scenario Brief JSON</div>
            <pre>{esc_brief_json}</pre>
            """
        elif terminal_route == "TERMINATE_BLOCKED":
            sprint_5_html = f"""
            <div class="section-title">Terminal Route Preview Result</div>
            <p>Terminal Route: <span class="badge" style="background-color: rgba(239, 68, 68, 0.15); color: #fca5a5; margin: 0; border: 1px solid rgba(239, 68, 68, 0.3);">{html.escape(terminal_route)}</span></p>
            <p>brief_preview_status: <strong>{esc_brief_status}</strong></p>

            <div class="withheld-box" style="background-color: rgba(239, 68, 68, 0.15); border-color: rgba(239, 68, 68, 0.4); color: #f87171;">
                <div class="withheld-title">Scenario Blocked</div>
                <p style="margin: 0; color: #fca5a5;">This scenario is outside the safe scope of the demo, so no Scenario Brief was generated.</p>
            </div>

            <div class="section-title">Assembled Scenario Brief JSON</div>
            <pre>{esc_brief_json}</pre>
            """
    else:
        # Sprint 4 or 3 layout
        esc_precheck = html.escape(safety_precheck_pretty)
        esc_terminal = html.escape(terminal_route_pretty)
        esc_safety_trace = html.escape(safety_trace_pretty)

        if is_sprint_4:
            sprint_5_html = f"""
                <div class="section-title">Deterministic Safety Precheck Result</div>
                <p><span class="badge" style="background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3);">Deterministic Precheck (No Agent 4)</span></p>
                <pre>{esc_precheck}</pre>

                <div class="section-title">Terminal Route Preview</div>
                <p>Maps the release status to the appropriate final redirect page:</p>
                <pre>{esc_terminal}</pre>

                <div class="section-title">Safety Routing Trace</div>
                <pre>{esc_safety_trace}</pre>
            """
        else:
            esc_trace = html.escape(graph_trace_pretty)
            sprint_5_html = f"""
                <div class="section-title">Dry-Run Graph Transition Trace</div>
                <p>The sequential transition path configured for this agent graph is tracked below:</p>
                <pre>{esc_trace}</pre>
            """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>wAI Scenario Lab - {badge_text}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

        body {{
            margin: 0;
            padding: 0;
            background-color: #0b0f19;
            color: #f3f4f6;
            font-family: 'Outfit', sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}

        .container {{
            max-width: 800px;
            width: 95%;
            padding: 40px 0;
            box-sizing: border-box;
        }}

        .card {{
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.02) 0%, rgba(255, 255, 255, 0) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            margin-bottom: 30px;
        }}

        .badge {{
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 600;
            background-color: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            padding: 6px 12px;
            border-radius: 12px;
            border: 1px solid rgba(99, 102, 241, 0.3);
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        h1 {{
            font-size: 1.75rem;
            margin: 0 0 12px 0;
            background: linear-gradient(135deg, #ffffff 0%, #d1d5db 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        p {{
            color: #9ca3af;
            font-size: 1rem;
            margin: 0 0 24px 0;
            line-height: 1.5;
        }}

        .status-box {{
            background-color: rgba(99, 102, 241, 0.05);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 10px;
            padding: 14px 16px;
            font-size: 0.95rem;
            color: #c7d2fe;
            margin-bottom: 24px;
        }}

        .checkpoint-banner {{
            background-color: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 10px;
            padding: 14px 16px;
            font-size: 0.95rem;
            color: #a7f3d0;
            margin-bottom: 24px;
        }}

        .section-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #e5e7eb;
            margin: 28px 0 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 8px;
        }}

        pre {{
            background-color: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 20px;
            overflow-x: auto;
            font-family: monospace;
            font-size: 0.85rem;
            color: #a7f3d0;
            margin-bottom: 24px;
        }}

        .btn-back {{
            display: inline-block;
            padding: 12px 24px;
            background-color: rgba(255, 255, 255, 0.05);
            color: #f3f4f6;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 500;
            transition: all 0.2s ease;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}

        .btn-back:hover {{
            background-color: rgba(255, 255, 255, 0.1);
        }}

        /* Sprint 5 Specific Styles */
        .brief-card {{
            background: rgba(255, 255, 255, 0.015);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 24px;
        }}
        .brief-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            padding-bottom: 16px;
            margin-bottom: 20px;
        }}
        .brief-title {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #ffffff;
        }}
        .limitation-banner {{
            background-color: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.25);
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 0.9rem;
            color: #fbbf24;
            margin-bottom: 20px;
            line-height: 1.5;
        }}
        .brief-section {{
            margin-bottom: 24px;
        }}
        .brief-section-title {{
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #9ca3af;
            margin-bottom: 8px;
        }}
        .brief-text {{
            font-size: 1rem;
            color: #e5e7eb;
            line-height: 1.6;
        }}
        .brief-bullets {{
            margin: 8px 0;
            padding-left: 20px;
            color: #e5e7eb;
        }}
        .brief-bullets li {{
            margin-bottom: 6px;
            line-height: 1.5;
        }}
        .metric-box {{
            background-color: rgba(99, 102, 241, 0.03);
            border: 1px solid rgba(99, 102, 241, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-top: 10px;
        }}
        .metric-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #818cf8;
            margin-bottom: 8px;
        }}
        .disclosure-box {{
            background-color: rgba(255, 255, 255, 0.01);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 8px;
            padding: 14px;
            font-size: 0.85rem;
            color: #9ca3af;
            line-height: 1.5;
            margin-top: 16px;
        }}
        .cta-box {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(168, 85, 247, 0.08) 100%);
            border: 1px solid rgba(99, 102, 241, 0.15);
            border-radius: 12px;
            padding: 20px;
            margin-top: 24px;
            text-align: center;
        }}
        .cta-button {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #6366f1;
            color: #ffffff;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 12px;
            transition: background-color 0.2s;
        }}
        .cta-button:hover {{
            background-color: #4f46e5;
        }}
        .withheld-box {{
            background-color: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.25);
            border-radius: 12px;
            padding: 24px;
            color: #fca5a5;
            margin-top: 24px;
            margin-bottom: 24px;
            line-height: 1.5;
        }}
        .withheld-title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: #ef4444;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="badge">{badge_text}</div>
            <h1>{title_text}</h1>

            <div class="checkpoint-banner">
                <strong>{esc_msg}</strong>
            </div>

            <div class="status-box">
                Adapter Status: <strong>{esc_status}</strong>
            </div>

            {sprint_5_html}

            <div class="section-title">Agent 1 Input Preparation</div>
            <p>The following structured payload was prepared by the workflow adapter:</p>
            <pre>{esc_input}</pre>

            <div class="section-title">Intentionally Not Executed Yet</div>
            <p>To preserve product boundaries, the following live tasks have been bypassed in this checkpoint:</p>
            <pre>{esc_not_run}</pre>

            <a href="/" class="btn-back">← Edit My Answers</a>
        </div>
    </div>
</body>
</html>
"""
