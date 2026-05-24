# When to use JudgePanelRunner vs LLMJudgeGateway

| Use | Module | When |
|-----|--------|------|
| **Proof panel** (N providers, same contract) | `agentic_core.runtime.judges.panel.JudgePanelRunner` | `apps_rg` GRADE_ONLY `judge_packet` path; requires registered `JudgeProviderAdapter` per provider key |
| **Single profile judge** | `agentic_core.runtime.judges.LLMJudgeGateway` | One `JudgeProfile` ref, one provider call, spine/RB13 flows |

`apps_rg` executive summary proof path: `run_llm_judges(judge_packet=...)` → `x1d_panel_bridge` → `JudgePanelRunner`.
