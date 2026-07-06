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

"""Safe Config-driven MCP Server for wAI Scenario Lab.

Exposes resources and tools matching the active configuration file.
This prototype is designed to support reflective observation and non-financial measurement
(e.g., minutes lost, ideas captured) to help users analyze workflow friction.
It explicitly avoids performing financial valuations, opportunity cost estimations,
consequential decision support, or professional (legal/medical/tax) advice.
"""

import json
import os
import sys
import logging
from mcp.server.fastmcp import FastMCP

# Configure logging strictly to sys.stderr so MCP JSON-RPC stdout is not corrupted
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("scenario_config_server")

# Initialize FastMCP
mcp = FastMCP("Scenario Config Server")

# Resolve active configuration path
CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "wai_scenario_config.json")
)


def _load_config() -> dict:
    """Loads the active configuration file safely."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config at {CONFIG_PATH}: {e}")
        # Return a structured empty fallback
        return {"scenarios": {}}


@mcp.tool()
def list_available_scenarios() -> list[dict]:
    """Lists the IDs and short descriptions of all available scenarios in the configuration."""
    config = _load_config()
    scenarios = config.get("scenarios", {})
    results = []
    for sid, val in scenarios.items():
        results.append({
            "scenario_id": sid,
            "title": val.get("title", sid),
            "short_description": val.get("short_description", "")
        })
    return results


@mcp.tool()
def get_scenario_metadata(scenario_id: str) -> dict:
    """Retrieves metadata for a specific scenario, such as title, context, and completion time.

    Args:
        scenario_id: Unique scenario identifier (e.g. 'cool_down_tax', 'brain_fog', 'blank_page').
    """
    config = _load_config()
    scenario = config.get("scenarios", {}).get(scenario_id)
    if not scenario:
        raise ValueError(f"Scenario '{scenario_id}' not found.")

    return {
        "scenario_id": scenario_id,
        "title": scenario.get("title"),
        "short_description": scenario.get("short_description"),
        "context": scenario.get("context"),
        "estimated_completion_minutes": scenario.get("estimated_completion_minutes"),
        "measurement_preview": scenario.get("measurement_preview")
    }


@mcp.tool()
def get_scenario_questions(scenario_id: str) -> list[dict]:
    """Retrieves the list of questions for a specific scenario.

    Args:
        scenario_id: Unique scenario identifier.
    """
    config = _load_config()
    scenario = config.get("scenarios", {}).get(scenario_id)
    if not scenario:
        raise ValueError(f"Scenario '{scenario_id}' not found.")

    return scenario.get("questions", [])


@mcp.tool()
def get_scenario_measurement(scenario_id: str) -> dict:
    """Retrieves the measurement definitions (primary and fallback) for a specific scenario.

    Args:
        scenario_id: Unique scenario identifier.
    """
    config = _load_config()
    scenario = config.get("scenarios", {}).get(scenario_id)
    if not scenario:
        raise ValueError(f"Scenario '{scenario_id}' not found.")

    # Return only the measurement definition structure
    return scenario.get("measurement", {})


@mcp.tool()
def select_observation_measure(scenario_id: str, use_fallback: bool = False) -> dict:
    """Selects the primary or fallback observation measure for a scenario based on validated inputs.

    Args:
        scenario_id: Unique scenario identifier.
        use_fallback: Set to True if evidence is insufficient/vague and fallback metric should be triggered.
    """
    config = _load_config()
    scenario = config.get("scenarios", {}).get(scenario_id)
    if not scenario:
        raise ValueError(f"Scenario '{scenario_id}' not found.")

    measurement_config = scenario.get("measurement", {})
    key = "fallback" if use_fallback else "primary"
    selected = measurement_config.get(key, {})

    if not selected:
        raise ValueError(f"Measurement metric '{key}' is not defined for scenario '{scenario_id}'.")

    # Double check that we are not outputting financial terms in the calculation or period
    for field in ("name", "calculation", "period"):
        val = str(selected.get(field, "")).lower()
        if any(bad in val for bad in ["$", "roi", "dollar", "savings", "cost", "value", "equity"]):
            logger.warning(f"Detected financial term in measure config for '{key}' of '{scenario_id}': {field}")

    return {
        "name": selected.get("name"),
        "unit": selected.get("unit"),
        "calculation_method": selected.get("calculation"),
        "tracking_period": selected.get("period"),
        "is_fallback": use_fallback
    }


if __name__ == "__main__":
    mcp.run()

