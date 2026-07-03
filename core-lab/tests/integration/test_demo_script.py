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

import os
import sys
import subprocess


def test_demo_script_execution():
    """Verifies that the demo script runs locally, succeeds, and prints required sections."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "run_sample_brief.py")
    )
    
    # Assert script exists
    assert os.path.exists(script_path), f"Demo script not found at {script_path}"
    
    # Run the demo script as a subprocess
    # sys.executable ensures it uses the same python binary (and activated virtual environment)
    process = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        check=False
    )
    
    # Check that execution was successful (Exit Code 0)
    assert process.returncode == 0, f"Demo script failed with stderr:\n{process.stderr}"
    
    output = process.stdout
    
    # Check that required content is printed
    assert "=== wAI SCENARIO LAB BRIEF (APPROVED) ===" in output
    assert "Action:" in output
    assert "Metric:" in output
    assert "Human Review Reminder:" in output
    assert "Responsible Use Limitation:" in output
    
    # Double-check that it does not contain ROI or financial math output
    assert "$" not in output
    assert "opportunity cost" not in output
    assert "marketing equity" not in output
