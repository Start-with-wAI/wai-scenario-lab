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


def render_question_html(q: dict) -> str:
    """Renders a single question dynamically based on its configured type."""
    q_id = q.get("id")
    q_type = q.get("type")
    label = q.get("label", "")
    help_text = q.get("help_text", "")
    required = "required" if q.get("required") else ""

    help_html = f'<small class="help-text">{help_text}</small>' if help_text else ""

    if q_type == "text":
        max_length_val = q.get("max_length")
        max_length = f'maxlength="{max_length_val}"' if max_length_val is not None else ""
        return f"""
        <div class="form-group">
            <label for="{q_id}">{label}</label>
            {help_html}
            <input type="text" id="{q_id}" name="{q_id}" {required} {max_length} placeholder="Describe briefly..." />
        </div>
        """

    elif q_type == "textarea":
        max_length_val = q.get("max_length")
        max_length = f'maxlength="{max_length_val}"' if max_length_val is not None else ""
        return f"""
        <div class="form-group">
            <label for="{q_id}">{label}</label>
            {help_html}
            <textarea id="{q_id}" name="{q_id}" {required} {max_length} placeholder="Enter your response..."></textarea>
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
        <div class="form-group">
            <label for="{q_id}">{label}</label>
            {help_html}
            <div class="number-input-wrapper">
                <input type="number" id="{q_id}" name="{q_id}" {required} {min_attr} {max_attr} {step_attr} />
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
            options_html += f"""
            <label class="radio-label">
                <input type="radio" name="{q_id}" value="{opt_val}" {required} />
                <span>{opt_label}</span>
            </label>
            """
        return f"""
        <fieldset class="form-group">
            <legend>{label}</legend>
            {help_html}
            <div class="radio-group">
                {options_html}
            </div>
        </fieldset>
        """
    else:
        return f"""
        <div class="form-group">
            <label for="{q_id}">{label}</label>
            {help_html}
            <input type="text" id="{q_id}" name="{q_id}" {required} />
        </div>
        """


def render_episode_01_page(config: dict) -> str:
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

    questions_html = ""
    questions = scenario.get("questions", [])
    sorted_questions = sorted(questions, key=lambda x: x.get("order", 0))
    for q in sorted_questions:
        questions_html += render_question_html(q)

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
