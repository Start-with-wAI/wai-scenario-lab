import sys
import os
import platform

# Ensure DreamHost user site-packages are in the path
dh_site_packages = "/home/dh_webmistress_v/.local/lib/python3.10/site-packages"
if dh_site_packages not in sys.path:
    sys.path.insert(0, dh_site_packages)

from fastapi import FastAPI
from a2wsgi import ASGIMiddleware

app = FastAPI(
    title="DreamHost FastAPI Smoke Test",
    description="A minimal FastAPI application running via WSGI/CGI on DreamHost",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "FastAPI via A2WSGI is responding",
        "runtime": "dreamhost-wsgi-smoke-test"
    }

@app.get("/health")
def read_health():
    return {
        "status": "healthy",
        "environment": "dreamhost-shared-hosting"
    }

@app.get("/adk-probe")
def adk_probe():
    try:
        import google.adk

        return {
            "status": "ok",
            "adk_imported": True,
            "adk_runtime_probe": "import_only_no_external_call",
            "module": str(google.adk),
            "note": "Google ADK imported successfully. This endpoint does not call Gemini or run the full workflow."
        }
    except Exception as exc:
        return {
            "status": "error",
            "adk_imported": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "adk_runtime_probe": "failed_import_only"
        }

@app.get("/adk-init-probe")
def adk_init_probe():
    import time
    start_time = time.perf_counter()

    response = {
        "status": "unknown",
        "adk_imported": False,
        "class_imports": {},
        "duration_ms": None,
        "note": "This probe imports and inspects ADK classes only. It does not call Gemini, Vertex AI, Google APIs, or run the full workflow."
    }

    try:
        import google.adk
        response["adk_imported"] = True
        response["adk_version"] = getattr(google.adk, "__version__", "unknown")

        try:
            from google.adk.agents import Agent
            response["class_imports"]["Agent"] = True
            response["inspected_agent_type"] = str(Agent)
        except Exception as exc:
            response["class_imports"]["Agent"] = False
            response["agent_import_error"] = f"{type(exc).__name__}: {exc}"

        try:
            from google.adk.models import Gemini
            response["class_imports"]["Gemini"] = True
            response["inspected_gemini_type"] = str(Gemini)
        except Exception as exc:
            response["class_imports"]["Gemini"] = False
            response["gemini_import_error"] = f"{type(exc).__name__}: {exc}"

        response["status"] = "ok"

    except Exception as exc:
        response["status"] = "failed"
        response["error"] = f"{type(exc).__name__}: {exc}"

    response["duration_ms"] = round((time.perf_counter() - start_time) * 1000.0, 2)
    return response

@app.get("/capabilities")
def read_capabilities():
    modules_to_test = [
        "fastapi",
        "pydantic",
        "a2wsgi",
        "uvicorn",
        "mcp",
        "google.adk"
    ]

    import_status = {}
    for module in modules_to_test:
        try:
            __import__(module)
            import_status[module] = {
                "imported": True,
                "error": None
            }
        except Exception as exc:
            import_status[module] = {
                "imported": False,
                "error": f"{type(exc).__name__}: {exc}"
            }

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "current_working_directory": os.getcwd(),
        "app_file": os.path.abspath(__file__),
        "app_directory": os.path.dirname(os.path.abspath(__file__)),
        "app_folder_marker": "scenario-lab-demo",
        "imports": import_status
    }

# Wrap the FastAPI ASGI app as a WSGI app for Passenger/CGI
wsgi_app = ASGIMiddleware(app)
