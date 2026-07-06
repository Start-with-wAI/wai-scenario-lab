# Copyright 2026 Google LLC
# Modifications copyright 2026 Start with wAI.
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
from fastapi.responses import HTMLResponse, JSONResponse
from app.config_loader import (
    get_public_scenario_lab_config,
    render_scenario_lab_page,
    render_error_page,
    render_checkpoint_page,
    ConfigLoadError,
    load_scenario_config,
)
from app.workflow_adapter import (
    prepare_workflow_adapter_response,
    WorkflowAdapterError,
)
from app.safety_router import (
    prepare_sprint_4_safety_routing_response,
    SafetyRouterError,
)
from app.terminal_output import (
    prepare_sprint_5_terminal_output_response,
    TerminalOutputError,
)
from app.form_validation import (
    validate_scenario_form,
    build_workflow_payload,
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


from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    scenario_id: str
    answers: dict


@app.get("/", response_class=HTMLResponse)
def public_landing_page():
    try:
        config = get_public_scenario_lab_config()
        return HTMLResponse(content=render_scenario_lab_page(config), status_code=200)
    except ConfigLoadError as e:
        return HTMLResponse(content=render_error_page(str(e)), status_code=500)
    except Exception as e:
        err_msg = f"Internal server error: {e}"
        if hasattr(logger, "log_struct"):
            logger.log_struct({"error": err_msg}, severity="ERROR")
        else:
            logging.error(err_msg)
        return HTMLResponse(content=render_error_page("An unexpected internal server error occurred."), status_code=500)


@app.post("/api/analyze")
def api_analyze_scenario(req: AnalysisRequest):
    """JSON API endpoint that validates scenario answers and executes the workflow."""
    try:
        config = load_scenario_config()
        scenario_config = config.get("scenarios", {}).get(req.scenario_id)
        if not scenario_config:
            return JSONResponse(status_code=404, content={"error": f"Scenario {req.scenario_id} not found."})
            
        normalized_answers, field_errors = validate_scenario_form(req.answers, scenario_config)
        if field_errors:
            return JSONResponse(status_code=400, content={"error": "Validation failed", "field_errors": field_errors})
            
        from app.workflow import run_scenario_lab_sample
        result = run_scenario_lab_sample(req.scenario_id, answers=normalized_answers)
        return result
    except Exception as e:
        err_msg = f"Internal server error in API analyze: {e}"
        if hasattr(logger, "log_struct"):
            logger.log_struct({"error": err_msg}, severity="ERROR")
        else:
            logging.error(err_msg)
        return JSONResponse(status_code=500, content={"error": "An unexpected internal server error occurred."})


@app.post("/", response_class=HTMLResponse)
async def public_landing_page_submit(request: Request):
    try:
        form_data = await request.form()
        form_dict = {key: val for key, val in form_data.items()}
        scenario_id = form_dict.get("scenario_id", "cool_down_tax")
        
        # Load configuration
        config = load_scenario_config()
        scenario_config = config.get("scenarios", {}).get(scenario_id)
        if not scenario_config:
            return HTMLResponse(content=render_error_page(f"Scenario {scenario_id} not found."), status_code=404)
            
        normalized_answers, field_errors = validate_scenario_form(form_dict, scenario_config)

        if field_errors:
            # Fallback legacy render if validation fails on form submit
            legacy_config = {
                "app": config.get("app", {}),
                "shared_ui": config.get("shared_ui", {}),
                "scenario": scenario_config
            }
            from app.config_loader import render_episode_01_page
            html_content = render_episode_01_page(legacy_config, values=normalized_answers, errors=field_errors)
            return HTMLResponse(content=html_content, status_code=400)

        # Successful validation
        payload = build_workflow_payload(scenario_config, normalized_answers)

        # Workflow Adapter processing
        adapter_response = prepare_workflow_adapter_response(payload)

        # Safety Routing processing
        sprint_4_response = prepare_sprint_4_safety_routing_response(payload, adapter_response)

        # Terminal Output Assembly
        sprint_5_response = prepare_sprint_5_terminal_output_response(
            config, payload, adapter_response, sprint_4_response
        )
        checkpoint_html = render_checkpoint_page(sprint_5_response)
        return HTMLResponse(content=checkpoint_html, status_code=200)
    except ConfigLoadError as e:
        return HTMLResponse(content=render_error_page(str(e)), status_code=500)
    except (WorkflowAdapterError, SafetyRouterError, TerminalOutputError) as e:
        return HTMLResponse(content=render_error_page(str(e)), status_code=400)
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

