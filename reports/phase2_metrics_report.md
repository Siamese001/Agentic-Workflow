# Phase 2: Manual Review Duplicate Metrics
**Generated:** 2026-01-06 06:43:44

| Agent | Canonical | Duplicate | Can Lines | Dup Lines | Can Methods | Dup Methods | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CheckpointManagerAgent | `ValidationContext/CheckpointManagerAgent.py` | `shared_runtime/CheckpointManagerAgent.py` | 259 | 63 | 11 | 5 | ✅ DELETE duplicate |
| CognitiveContractManagerAgent | `ToolRegistry/CognitiveContractManagerAgent.py` | `models/CognitiveContractManagerAgent.py` | 258 | 548 | 11 | 16 | ⚠️ REVIEW needed |
| DeadCodeDetectorAgent | `guardrails/DeadCodeDetectorAgent.py` | `core_extensions/DeadCodeDetectorAgent.py` | 222 | 356 | 11 | 21 | ⚠️ REVIEW needed |
| FileManagerAgent | `filesystem/FileManagerAgent.py` | `core_extensions/FileManagerAgent.py` | 233 | 298 | 10 | 23 | ⚠️ REVIEW needed |
| GovernanceAgent | `validators/GovernanceAgent.py` | `thought_engine/GovernanceAgent.py` | 206 | 798 | 2 | 29 | ⚠️ REVIEW needed |
| HealerAgent | `ToolRegistry/HealerAgent.py` | `guardrails/HealerAgent.py` | 602 | 1338 | 4 | 39 | ⚠️ REVIEW needed |
| MetaLearningAgent | `learning/MetaLearningAgent.py` | `thought_engine/MetaLearningAgent.py` | 337 | 213 | 13 | 6 | ✅ DELETE duplicate |
| MetaLearningAgent | `learning/MetaLearningAgent.py` | `meta_learning/MetaLearningAgent.py` | 337 | 224 | 13 | 6 | ✅ DELETE duplicate |
| PromptGovernorAgent | `ToolRegistry/PromptGovernorAgent.py` | `rendering/PromptGovernorAgent.py` | 258 | 280 | 11 | 8 | ⚠️ REVIEW needed |
| TerritoryHealerAgent | `workflow_engines/TerritoryHealerAgent.py` | `guardrails/TerritoryHealerAgent.py` | 335 | 250 | 8 | 8 | ✅ DELETE duplicate |

---

## Delete Commands (After Review)

```bash
git rm "agentic_core/runtime/shared_runtime/CheckpointManagerAgent.py"
git rm "agentic_core/L1_cognition/thought_engine/MetaLearningAgent.py"
git rm "agentic_core/L3_orchestration/meta_learning/MetaLearningAgent.py"
git rm "agentic_core/L5_safety/guardrails/TerritoryHealerAgent.py"
git commit -m "chore: remove Phase 2 duplicate agents"
```
