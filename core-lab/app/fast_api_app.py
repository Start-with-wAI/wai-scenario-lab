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

import contextlib
import os
from collections.abc import AsyncIterator

import google.auth
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from google.cloud import logging as google_cloud_logging

from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.reasoning_engine_adapter import (
    attach_reasoning_engine_routes,
)
from app.app_utils.telemetry import (
    setup_agent_engine_telemetry,
    setup_telemetry,
)
from app.app_utils.typing import Feedback
from fastapi import Request
from fastapi.responses import HTMLResponse
from app.config_loader import (
    get_public_episode_01_config,
    render_episode_01_page,
    render_error_page,
    ConfigLoadError,
)
from app.form_validation import (
    validate_episode_01_form,
    build_episode_01_workflow_payload,
)

load_dotenv()
setup_telemetry()
# Must run before get_fast_api_app to set the tracer provider resource.
setup_agent_engine_telemetry()
import logging

_, project_id = google.auth.default()

if os.getenv("INTEGRATION_TEST") == "TRUE":
    class MockCloudLogger:
        def log_struct(self, data, severity="INFO"):
            logging.info(f"MockCloudLogger [{severity}]: {data}")
    logger = MockCloudLogger()
else:
    try:
        logging_client = google_cloud_logging.Client()
        logger = logging_client.logger(__name__)
    except Exception:
        class MockCloudLogger:
            def log_struct(self, data, severity="INFO"):
                logging.info(f"MockCloudLogger [{severity}]: {data}")
        logger = MockCloudLogger()
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Runner for the A2A path, sharing the same session/artifact services as the
    # adk_api and reasoning_engine paths (see services.py). Imported here so the
    # agent is built after env/telemetry setup.
    from app.agent import app as adk_app
    from app.agent import root_agent

    runner = Runner(
        app=adk_app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        auto_create_session=True,
    )
    # Shared by the A2A path and the reasoning_engine adapter routes.
    app.state.runner = runner
    app.state.agent_app_name = adk_app.name
    await attach_a2a_routes(
        app,
        agent=root_agent,
        runner=runner,
        task_store=InMemoryTaskStore(),
        rpc_path=f"/a2a/{adk_app.name}",
    )
    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=services.ARTIFACT_SERVICE_URI,
    allow_origins=allow_origins,
    session_service_uri=services.SESSION_SERVICE_URI,
    otel_to_cloud=False,
    lifespan=lifespan,
)
app.title = "core-lab"
app.description = "API for interacting with the Agent core-lab"


# Proxy routes so the Vertex AI Console Playground (reasoning_engine SDK) can
# talk to this agent alongside the native adk_api routes.
attach_reasoning_engine_routes(app)


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


@app.get("/", response_class=HTMLResponse)
def public_episode_01():
    try:
        config = get_public_episode_01_config()
        return HTMLResponse(content=render_episode_01_page(config), status_code=200)
    except ConfigLoadError as e:
        return HTMLResponse(content=render_error_page(str(e)), status_code=500)
    except Exception as e:
        err_msg = f"Internal server error: {e}"
        if hasattr(logger, "log_struct"):
            logger.log_struct({"error": err_msg}, severity="ERROR")
        else:
            logging.error(err_msg)
        return HTMLResponse(content=render_error_page("An unexpected internal server error occurred."), status_code=500)


@app.post("/", response_class=HTMLResponse)
async def public_episode_01_submit(request: Request):
    try:
        config = get_public_episode_01_config()
        form_data = await request.form()
        form_dict = {key: val for key, val in form_data.items()}

        normalized_answers, field_errors = validate_episode_01_form(form_dict, config["scenario"])

        if field_errors:
            html_content = render_episode_01_page(config, values=normalized_answers, errors=field_errors)
            return HTMLResponse(content=html_content, status_code=400)

        # Successful validation
        payload = build_episode_01_workflow_payload(config, normalized_answers)
        import json
        payload_pretty = json.dumps(payload, indent=2, ensure_ascii=False)

        success_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>wAI Scenario Lab - Input Validated</title>
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

        .card {{
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.02) 0%, rgba(255, 255, 255, 0) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 40px;
            max-width: 650px;
            width: 90%;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }}

        .badge {{
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 600;
            background-color: rgba(16, 185, 129, 0.15);
            color: #34d399;
            padding: 6px 12px;
            border-radius: 12px;
            border: 1px solid rgba(16, 185, 129, 0.3);
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

        pre {{
            background-color: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 20px;
            overflow-x: auto;
            font-family: monospace;
            font-size: 0.9rem;
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

        .temp-banner {{
            background-color: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 0.9rem;
            color: #fef3c7;
            margin-bottom: 24px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="badge">Success</div>
        <h1>Sprint 2 Checkpoint</h1>
        <div class="temp-banner">
            <strong>Sprint 2 checkpoint: input validated and normalized. Agent workflow has not run yet.</strong>
        </div>
        <p>The form data has passed all server-side validation checks. Below is the normalized workflow payload ready for Sprint 3:</p>
        <pre>{payload_pretty}</pre>
        <a href="/" class="btn-back">← Edit My Answers</a>
    </div>
</body>
</html>
"""
        return HTMLResponse(content=success_html, status_code=200)
    except ConfigLoadError as e:
        return HTMLResponse(content=render_error_page(str(e)), status_code=500)
    except Exception as e:
        err_msg = f"Internal server error in POST: {e}"
        if hasattr(logger, "log_struct"):
            logger.log_struct({"error": err_msg}, severity="ERROR")
        else:
            logging.error(err_msg)
        return HTMLResponse(content=render_error_page("An unexpected internal server error occurred."), status_code=500)


# Safe route reordering: move GET / and POST / routes to the front of app.routes
# to override ADK's default redirect while keeping them intact.
_get_route = None
_post_route = None
for r in list(app.routes):
    if getattr(r, "path", None) == "/":
        if "GET" in getattr(r, "methods", []):
            if getattr(r, "name", None) != "redirect_root_to_dev_ui":
                _get_route = r
                app.routes.remove(r)
        elif "POST" in getattr(r, "methods", []):
            _post_route = r
            app.routes.remove(r)

if _post_route:
    app.routes.insert(0, _post_route)
if _get_route:
    app.routes.insert(0, _get_route)


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
