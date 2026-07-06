# Kaggle Submission Checklist

| Requirement | Repository evidence | Status | Notes |
| --- | --- | --- | --- |
| Kaggle Writeup under 2,500 words | External Kaggle Writeup; README supports content | Pending | Must be completed in Kaggle. |
| Media Gallery | `core-lab/docs/evidence/README.md` | Partial | Final screenshots are captured; add cover image and video. |
| Cover image | Evidence placeholder | Pending | Do not invent. |
| YouTube video <= 5 minutes | `core-lab/docs/demo-script.md` | Pending | Must be recorded and published. |
| Public project link | GitHub repo or live demo | Pending | Live demo preferred; repo acceptable with setup docs. |
| README | `README.md` | Ready | Final-facing root README updated. |
| Code | `core-lab/app/`, `core-lab/mcp_server/` | Ready | Active app lives under `core-lab/`. |
| ADK or graph workflow | `core-lab/app/workflow.py`, `core-lab/docs/architecture/agent-graph.md` | Ready with caveat | Live ADK calls need credentials; deterministic adapter supports local demo/tests. |
| MCP server | `core-lab/mcp_server/scenario_config_server.py` | Ready | Config-only, no secrets or network required. |
| Antigravity evidence | `core-lab/docs/evidence/antigravity-task-or-diff.png`, demo script | Captured with caveat | Verify this is the intended Antigravity/task evidence for the final video. |
| Security features | `core-lab/app/services/safety.py`, `core-lab/docs/responsible-ai.md` | Ready | Deterministic safety checks documented. |
| Deployability | `core-lab/Dockerfile`, `core-lab/deployment/`, README commands | Partial | Verify public demo or present local reproducibility. |
| Agent skills | `core-lab/.agents/skills/` | Ready | Five concise skill folders exist. |
| Tests | `core-lab/tests/`, `core-lab/docs/final-test-results.md` | Ready | Latest local run: `97 passed, 4 skipped in 19.63s`. |
| Evaluation results | `core-lab/docs/evaluation/evaluation-results.md` | Ready | 18 cases mapped. |
| No secrets | `.gitignore`, safety scan, no `.env` committed | Ready with caveat | Root requirements local path fixed; rerun scan before submission. |
| One Kaggle submission per team | Rules checklist | Team action | Team lead must confirm in Kaggle. |
| Team size <= 5 | Rules checklist | Team action | Confirm official team roster. |
| No multiple Kaggle accounts | Rules checklist | Team action | Confirm each participant uses one account. |
| No private code sharing outside team | Rules checklist | Team action | Keep repo/share path official. |
| License compatibility | `NOTICE.md`, `pyproject.toml`, dependency list | Needs final review | wAI copyright notice added; confirm final repo license and third-party licenses. |
| CC-BY 4.0 winner implications | Rules source reviewed | Team action | Be prepared to license winning submission accordingly. |
| Reproducible code and docs | README, requirements, pyproject, fresh venv test, `pip check` | Ready | Fresh environment install, dependency check, and local tests passed. |
| No proprietary/restricted data | Config uses fictional scenarios | Ready | Do not add private client data. |





