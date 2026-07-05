# **wAI Scenario Lab**  
## **Capstone Plan Summary for Jason**  
### **Project Concept**  
We will build a lightweight, public-facing **wAI Scenario Lab** for the Vibe Coding Capstone.  
A micro business owner will select one fictional business-friction scenario, answer three to five guided questions, and receive:  
- A short friction summary  
- One practical next step  
- One simple measurement  
- One human-review reminder  
- A link to the related wAI podcast episode  
The tool will demonstrate how we approach business problems without giving away a full paid assessment, automation, ROI model, or implementation plan.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAEklEQVR4nGP4//8/AxMDAwMDABf8AwDXbXN0AAAAAElFTkSuQmCC)  
## **Recommended Scenarios**  
We will use concepts from our first three published podcast episodes:  
1. **The Cool Down Tax  
 **Measures time lost after stressful business communications.  
2. **Brain Fog  
 **Examines why ideas are lost before they can be captured.  
3. **The Blank Page  
 **Identifies friction when starting business content.  
These are good capstone choices because they are already public, text-based, easy to test, and can all use the same application structure.  
We will avoid file uploads, email access, audio transcription, account integrations, automated actions, and other features that would increase risk or development time.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAEklEQVR4nGP4//8/AxMDAwMDABf8AwDXbXN0AAAAAElFTkSuQmCC)  
## **Agent Structure and Ownership**  
### **Verónica**  
**Agent 1: Scenario Guide**  
- Presents the selected scenario  
- Asks the guided questions  
- Clarifies incomplete answers  
- Produces structured user input  
**Agent 2: Workflow Analysis**  
- Identifies the friction point  
- Separates facts from assumptions  
- Recognizes constraints and unknowns  
- Recommends one low-risk next action  
Verónica will also lead:  
- Application architecture  
- Agent orchestration  
- Front-end development  
- User experience  
- Prompt integration  
- Deployment  
- Architecture visuals  
- Demo narrative and presentation  
### **Jason**  
**Agent 3: Value and Evidence**  
- Selects one useful measure  
- Validates available evidence  
- Prevents invented savings or unsupported ROI  
- Identifies when information is insufficient  
**Agent 4: Safety and Quality Review**  
- Checks privacy and sensitive information  
- Detects unsupported claims  
- Enforces the one-action limit  
- Identifies high-risk or out-of-scope requests  
- Confirms human review  
- Approves, revises, or blocks the final response  
Jason will also lead:  
- Measurement rules  
- Calculation validation  
- Evaluation dataset  
- Statistical testing summary  
- Rule adherence  
- Responsible AI documentation  
- Quality assurance  
This gives us two agents each and aligns the work with our respective strengths.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAEklEQVR4nGP4//8/AxMDAwMDABf8AwDXbXN0AAAAAElFTkSuQmCC)  
## **Four-Day Build Plan**  
### **Day 1: Scope and Architecture**  
We will:  
- Finalize the three scenarios ✅  
We should build the Scenario Lab around the first three published Relief Valve episodes:  
1. **Episode 01: The Cool Down Tax**  
2. **Episode 02: Brain Fog**  
3. **Episode 03: The Blank Page**  
These episodes are already publicly documented on the wAI website, including their basic problems, safety principles, and three levels of relief. Using concepts we have already released reduces the risk that the capstone exposes new proprietary business intelligence.  
   
- Define what the public prototype will and will not do  
   
We do **not** need:  
- Audio transcription  
- Email access  
- File uploads  
- Cloud-drive access  
- Account integrations  
- Persistent user profiles  
- Automated message sending  
- Full content generation  
That keeps the build achievable within three to four days while still demonstrating a real-world agent application. The Kaggle capstone evaluates areas including problem definition, solution design, implementation quality, effective use of agent technologies, and overall user experience.  
- Design the common user journey  
All three can use the same technical pattern:  
1. User selects a scenario.  
2. User answers three to five text questions.  
3. Agent 1 gathers and clarifies the facts. Notify & strip PII.  
4. Agent 2 identifies the workflow friction.  
5. Agent 3 identifies one useful measurement.  
6. Agent 4 checks safety, evidence, restraint, and quality.  
7. The application generates a short Scenario Brief.  
This common structure means we can build one reusable agent pipeline and change only the scenario configuration, questions, measurements, and output language.  
- Define agent inputs and outputs  
8. INPUTS  
-    
9. OUTPUTS  
- Friction summary  
- One immediate low-risk action  
- One measurement, such as recovery minutes per incident, ideas successfully captured per week, time to first usable outline  
- One reminder that the user reviews and controls any response  
- Link to Episode  
- Create measurement and safety rules  
10. recovery minutes per incident  
11. ideas successfully captured per week, time to first usable outline  
- Scaffold the repository and application  
**End-of-day result:** working application shell, scenario configurations, agent schemas, and frozen MVP scope.  
### **Day 2: Build the Complete Pipeline**  
We will:  
- Build the reusable questionnaire  
- Implement all four agents  
- Connect the agents in sequence  
- Validate structured outputs  
- Build the Scenario Brief results screen  
- Complete the first scenario, likely The Cool Down Tax  
**End-of-day result:** one complete scenario working from beginning to end.  
### **Day 3: Add Scenarios and Evaluate**  
We will:  
- Add Brain Fog and The Blank Page  
- Create at least 18 test cases  
- Test normal, vague, sensitive, contradictory, and scope-pushing inputs  
- Measure relevance, calculation accuracy, safety, restraint, and clarity  
- Refine prompts and rules  
- Freeze features  
**End-of-day result:** three tested scenarios and documented evaluation results.  
### **Day 4: Deploy and Present**  
We will:  
- Deploy the public prototype  
- Complete the README and architecture documentation  
- Write the responsible AI and evaluation sections  
- Create presentation visuals  
- Rehearse and record the demo  
- Review the repository for secrets or proprietary material  
- Submit the capstone  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAEklEQVR4nGP4//8/AxMDAwMDABf8AwDXbXN0AAAAAElFTkSuQmCC)  
## **Responsible AI Approach**  
Jason will own the responsible AI section.  
The prototype will:  
- Clearly disclose that AI is being used  
- Tell users not to enter confidential or personal information  
- Keep humans responsible for all decisions  
- Avoid legal, medical, tax, employment, lending, housing, insurance, or compliance advice  
- Label assumptions and insufficient evidence  
- Avoid invented savings, ROI, or guarantees  
- Prevent automatic sending, publishing, purchasing, or account changes  
Agent 4 will enforce these rules before any Scenario Brief is released.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAEklEQVR4nGP4//8/AxMDAwMDABf8AwDXbXN0AAAAAElFTkSuQmCC)  
## **Commercial Protection**  
The public capstone will show how we think, but it will stop before delivering a complete commercial solution.  
It will not include:  
- Full AI readiness scoring  
- Complete workflow redesign  
- Automation recipes  
- Proprietary prompts  
- Vendor-selection methods  
- Full ROI models  
- Technology-stack audits  
- Content-generation systems  
- AI policy generators  
- Client-specific implementation plans  
The capstone should leave viewers thinking:  
We clearly understand how to structure and evaluate the problem.  
It should not allow them to reproduce the complete paid solution without us.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAEklEQVR4nGP4//8/AxMDAwMDABf8AwDXbXN0AAAAAElFTkSuQmCC)  
## **Proposed Final Output**  
The user receives a short **Scenario Brief** containing:  
1. The identified friction  
2. Known facts and constraints  
3. One practical next action  
4. One useful measurement  
5. Any assumptions or missing evidence  
6. A human-review reminder  
7. A related podcast episode link  
The central product principle is:  
One scenario, one insight, one measurement, and one responsible next step.  
   
