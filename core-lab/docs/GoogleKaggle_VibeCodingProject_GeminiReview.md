The selection of the **wAI Scenario Lab** as your unified team submission is an outstanding strategic decision. It perfectly represents the core philosophy of startwithwai.tech—positioning AI as a disciplined, human-guided power tool rather than an unpredictable black box. By scoping the lab to text-based, synthetic, podcast-derived scenarios, you maintain a highly secure commercial boundary that acts as a natural marketing engine.  
With exactly three days remaining until the **July 6, 2026** submission deadline , a rigorous gap analysis of your current assets against the Kaggle evaluation rubric is critical to secure a winning, podium-grade submission.  
## **Rubric and Course Concept Gap Analysis**  
To achieve a perfect score on the **70-point Implementation Rubric**, your codebase must programmatically demonstrate at least three core concepts from the course. Your current plan successfully targets all of them, but contains several technical design gaps that would cause deductions or runtime crashes during judging:  
| | | | |  
|-|-|-|-|  
| **Rubric Concept** | **Plan Status** | **Identified Gap / Shortcoming** | **Priority** |   
| **Agent / Multi-Agent (ADK 2.0)** | **Conceptualized** | Running the agents as a flat, sequential Python chain inside the web UI rather than using the official, stateful **ADK 2.0 Graph Workflow API**. | **High (P0)** |   
| **MCP Server** | **Omitted** | Because file uploads and direct database connections were cut for the MVP, the agents do not consume external data, leaving the **MCP Server** requirement unfulfilled in the code. | **High (P0)** |   
| **Agent Skills** | **Partially Defined** | System prompts are at risk of context bloat. The skill schemas are not configured to meet the strict **Skill Registry YAML frontmatter** validation rules. | **Medium (P1)** |   
| **Security Features** | **Planned** | Need to ensure PII redaction and risk blocks are implemented as deterministic filters rather than non-deterministic model instructions. | **Medium (P1)** |   
| **Antigravity / Deployability** | **Planned** | Notebook must execute with zero local dependencies in Kaggle’s hosted runtime environment. | **High (P0)** |   
## **5 Critical Technical Shortcomings & Code Solutions**  
### **Shortcoming 1: The Missing MCP Server (Concept Gap)**  
Because you cut file uploads and database connections to preserve development speed, your agent pipeline operates on static strings. This means your codebase lacks a functioning **Model Context Protocol (MCP) server**, a key requirement for the Kaggle evaluation.  
#### **The Solution: The "Scenario Configuration" MCP Server**  
Do not hardcode the loading of wai_scenario_config.json inside your app. Instead, build a local **FastMCP Python Server** that exposes your scenario prompts, questions, and podcast metadata as dynamic MCP resources. This demonstrates the "factory model" of separating your data boundary from your core orchestration logic.  
Python  
  
# %%writefile wai_scenario_lab/mcp_server/scenario_config_server.py  
from fastmcp import FastMCP  
import json  
from pathlib import Path  
   
mcp = FastMCP("wAI Scenario Configuration")  
CONFIG_PATH = Path(__file__).parent.parent / "wai_scenario_config.json"  
   
@mcp.resource("scenario://list")  
def list_available_scenarios() -> str:  
    """Returns a list of all active podcast-themed scenarios."""  
    with open(CONFIG_PATH, "r") as f:  
        config = json.load(f)  
    return json.dumps(list(config["scenarios"].keys()))  
   
@mcp.resource("scenario://{scenario_id}/questions")  
def get_scenario_questions(scenario_id: str) -> str:  
    """Dynamic resource: Retrieves questions and context for a specific scenario."""  
    with open(CONFIG_PATH, "r") as f:  
        config = json.load(f)  
    scenario = config["scenarios"].get(scenario_id)  
    if not scenario:  
        raise ValueError(f"Scenario {scenario_id} not found.")  
    return json.dumps({  
        "title": scenario["title"],  
        "context": scenario["context"],  
        "questions": scenario["questions"]  
    })  
   
# Guarding STDIO: Never write debug logs to stdout, which corrupts JSON-RPC payloads  
if __name__ == "__main__":  
    import sys  
    import logging  
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)  
    mcp.run()  
   
### **Shortcoming 2: Kaggle Reproducibility and File Bootstrapping**  
Kaggle judges execute submitted notebooks from top to bottom in clean, sandboxed containers. If your repository expects pre-existing files on disk (like config.json or your skills folders) and does not programmatically generate them, the notebook will crash during execution, resulting in immediate deductions.  
#### **The Solution: Programmatic File Generation**  
Structure your entire Kaggle notebook using the %writefile bootstrapping pattern. Group all your configuration files, skills folders, and source code inside the notebook cells so that running the notebook writes your entire package cleanly to disk before launching execution:  
Python  
  
# Cell 1: Create directory tree  
import os  
DIRS = [  
    'wai_scenario_lab',  
    'wai_scenario_lab/mcp_server',  
    'wai_scenario_lab/app',  
    'wai_scenario_lab/.agents/skills/safety-reviewer'  
]  
for d in DIRS:  
    os.makedirs(d, exist_ok=True)  
   
### **Shortcoming 3: Context Bloat & Loose Skill Formatting**  
System prompts that contain extensive legal rules, privacy conditions, and output schemas quickly cause "context rot" and model latency. Furthermore, your planned skills must match the strict asynchronous validation standards of the **Skill Registry**. If your SKILL.md is missing required frontmatter fields, or if your description exceeds 1024 characters, the ADK platform will reject it.  
#### **The Solution: Conforming to the Skill Registry Standard**  
Every skill must be placed in a directory containing a conformant SKILL.md file using a **hybrid Markdown + YAML frontmatter** format to optimize parser efficiency:  
# **%%writefile wai_scenario_lab/.agents/skills/safety-reviewer/SKILL.md**  
## **name: safety-reviewer **  
## **description: Validates output for privacy, sensitive PII data, and limits actions to exactly one option. Use this skill when reviewing generated Scenario Briefs before final release.**  
# **Instructions**  
1. Inspect the combined output from Agents 1, 2, and 3.  
2. Confirm the release contains exactly **one** practical next action.  
3. Ensure no financial savings or ROI calculations are guaranteed.  
4. Verify the mandatory human-review disclaimer is present: "Use this brief as a starting point. You remain responsible...".  
To express the cost efficiency of keeping instructions out of the active prompt, the relationship can be mathematically represented as:  
   
$$\text{Token Footprint} = \text{Base Prompt} + \sum_{i=1}^{n} \text{Active Skill}_i$$   
   
By loading only the safety-reviewer skill on demand, the active token footprint remains highly compressed, preventing model drift and reducing latency.  
### **Shortcoming 4: Translating the Sequential Workflow to an ADK 2.0 Graph**  
Your current plan lists four sequential agents. In ADK 2.0, chaining agents sequentially using standard models can result in instruction drift. To maximize implementation points, you should utilize the **ADK 2.0 Graph Workflow API**, combining your AI agents with deterministic execution nodes and an explicit  **Human-in-the-Loop** pause gate.  
Python  
  
# %%writefile wai_scenario_lab/app/workflow.py  
from google.adk.agents import Agent, Workflow  
from google.adk.models import Gemini  
from google.adk.workflows import RequestInput  
import json  
   
# Define our specialist agents set to SingleTurn mode for deterministic execution  
workflow_model = Gemini(model="gemini-3.5-flash")  
   
agent_1 = Agent(  
    name="scenario_guide",  
    model=workflow_model,  
    instruction="Extract structured facts from the user answers. Set missing details as unknown.",  
    mode="SingleTurn"  
)  
   
agent_2 = Agent(  
    name="workflow_analyst",  
    model=workflow_model,  
    instruction="Identify exactly one workflow bottleneck and recommend exactly one action.",  
    mode="SingleTurn"  
)  
   
# Deterministic transition router  
def safety_router(context, event):  
    payload = json.loads(event.output)  
    # If sensitive data or out-of-scope tasks are flagged, route to human intervention  
    if payload.get("sensitive_data_detected") or payload.get("high_risk_domain_flag"):  
        return "HUMAN_TRIAGE"  
    return "APPROVED"  
   
# Define the execution graph  
workflow = Workflow(  
    name="wAI_Scenario_Lab_Pipeline",  
    edges=  
)  
   
### **Shortcoming 5: Missing Gherkin Testing and Verification**  
The Day 5 curriculum shifts the software development lifecycle from "vibe coding" (relying on raw, untested natural language prompts) to **Spec-Driven Development (SDD)**, where behavior-driven Gherkin specifications are treated as the executable source of truth. Currently, your plan lists tests but does not define how they are run or trace back to specific scenario IDs.  
#### **The Solution: Stable Scenario IDs & Automated pytest-bdd Execution**  
Define a Gherkin .feature file utilizing stable @id tags to map execution paths directly back to your podcast case studies. This ensures that any changes to agent prompts do not cause silent regressions in your deterministic rules.  
Gherkin  
  
# %%writefile wai_scenario_lab/tests/scenarios.feature  
@id_cool_down_tax_01  
Feature: Scenario 1 - The Cool Down Tax Verification  
  As a micro-business owner  
  I want the Scenario Lab to evaluate my communication friction  
  So that I can receive exactly one grounded next step  
   
  Scenario: Processing normal input for Episode 01  
    Given the user has selected scenario "cool_down_tax"  
    And has reported a "minutes_lost" value of 45  
    When the multi-agent graph execution completes  
    Then the status of the Scenario Brief must be "APPROVED"  
    And the brief must contain the measurement "Recovery time per incident"  
   
##   
   
## **Act-Now 3-Day Parallel Execution Plan**  
With the July 6, 2026 deadline fast approaching , here is your day-by-day technical execution plan, dividing responsibilities to play to your and Verónica's individual strengths :  
### **Day 1: Scaffolding, FastMCP, and Gherkin Specifications**  
- ~~**Verónica (P0):**~~ ~~ Sets up the Kaggle notebook skeleton using ~~ ~~%writefile~~ ~~ blocks. Scaffolds the ~~ ~~wai_scenario_lab/~~ ~~ directory structure and integrates the ~~ ~~wai_scenario_config.json~~ ~~ configuration file.~~  
- ~~**Jason (P0):**~~ ~~ Writes the Gherkin ~~ ~~.feature~~ ~~ test specifications for all three scenarios, embedding stable ~~ ~~@id~~ ~~ tags. Drafts the custom ~~ ~~**FastMCP Configuration Server**~~ ~~ to programmatically expose questions as dynamic resources.~~  
- ~~**Deliverable:**~~ ~~ A fully compiled repository folder structure, functional MCP resource endpoints, and executable behavioral test specifications.~~  
[https://github.com/Start-with-wAI/wai-scenario-lab/blob/veronica-day1-adapt-main/core-lab/docs/veronica-integration-walkthrough.md](https://github.com/Start-with-wAI/wai-scenario-lab/blob/veronica-day1-adapt-main/core-lab/docs/veronica-integration-walkthrough.md "https://github.com/Start-with-wAI/wai-scenario-lab/blob/veronica-day1-adapt-main/core-lab/docs/veronica-integration-walkthrough.md")   
### **Day 2: ADK 2.0 Graph Orchestration and Agent Implementations**  
- **Verónica (P0):** Codes the ADK 2.0 graph workflow, setting up the transition paths, function nodes, and edges. Integrates the dynamic questionnaire form on the landing page.  
- ~~**Jason (P0):**~~ ~~ Standardizes the modular skills folders under ~~ ~~.agents/skills/~~ ~~. Writes the Pydantic input models to enforce strict schema validation on the ~~ ~~Scenario Brief~~ ~~ payload. Codes the ~~ ~~RequestInput~~ ~~ Human-in-the-Loop gateway to intercept high-risk or out-of-scope requests.~~  
- **Deliverable:** A fully operational multi-agent graph running locally, capable of transitioning from user input to final reviewed output.  
[https://github.com/Start-with-wAI/wai-scenario-lab/blob/jason-day2-agent-implementations/core-lab/docs/jason-quality-walkthrough.md](https://github.com/Start-with-wAI/wai-scenario-lab/blob/jason-day2-agent-implementations/core-lab/docs/jason-quality-walkthrough.md "https://github.com/Start-with-wAI/wai-scenario-lab/blob/jason-day2-agent-implementations/core-lab/docs/jason-quality-walkthrough.md")   
### **Day 3: Automated Testing, Documentation, and Video Recording**  
- **Jason (P0):** Executes automated tests using pytest against your 18 evaluation test cases. Generates the project's  **STRIDE Threat Model** using the Antigravity CLI and documents wAI's responsible AI approach.  
- **Verónica (P0):** Polishes the UI and deploys the prototype. Drafts the technical README and compiles the Kaggle Writeup (<2500 words).  
- Together: Review previous winning submissions at: [https://www.kaggle.com/competitions/agents-intensive-capstone-project/discussion/663531](https://www.kaggle.com/competitions/agents-intensive-capstone-project/discussion/663531 "https://www.kaggle.com/competitions/agents-intensive-capstone-project/discussion/663531")   
- **Together (P0):** Film the 5-minute YouTube walk-through. Verónica presents the user journey and architecture, while Jason demonstrates Antigravity 2.0 in action (showing task lists and code diffs) and explains your strict security/HIL boundaries. Submit the Writeup before 11:59 PM PT!  
   
