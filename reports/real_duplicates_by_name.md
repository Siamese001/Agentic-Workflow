# Real Duplicate Agents (By Name)
**Generated:** 2026-01-06 06:33:11
**Duplicate Agent Names:** 19
**Files to Delete:** 21

| Agent Name | Canonical Path | Duplicate Path | Rationale |
| --- | --- | --- | --- |
| CheckpointManagerAgent | `agentic_core\L4_state\ValidationContext\CheckpointManagerAgent.py` | `agentic_core\runtime\shared_runtime\CheckpointManagerAgent.py` | Runtime duplicate — consolidate to primary location |
| CodeSSOTEnforcerAgent | `agentic_core\L5_safety\validators\CodeSSOTEnforcerAgent.py` | `agentic_core\config\blueprint_sovereign\CodeSSOTEnforcerAgent.py` | Leftover blueprint template — production version is canonical |
| CognitiveContractManagerAgent | `agentic_core\L2_execution\ToolRegistry\CognitiveContractManagerAgent.py` | `agentic_core\schemas\models\CognitiveContractManagerAgent.py` | Exact duplicate — likely copy-paste or migration artifact |
| ComplianceOrchestratorAgent | `agentic_core\L5_safety\validators\ComplianceOrchestratorAgent.py` | `agentic_core\config\blueprint_sovereign\ComplianceOrchestratorAgent.py` | Leftover blueprint template — production version is canonical |
| DeadCodeDetectorAgent | `agentic_core\L5_safety\guardrails\DeadCodeDetectorAgent.py` | `agentic_core\utils\core_extensions\DeadCodeDetectorAgent.py` | Exact duplicate — likely copy-paste or migration artifact |
| DocstringComplianceAgent | `agentic_core\L5_safety\validators\DocstringComplianceAgent.py` | `agentic_core\config\blueprint_sovereign\DocstringComplianceAgent.py` | Leftover blueprint template — production version is canonical |
| FileManagerAgent | `agentic_core\L4_state\filesystem\FileManagerAgent.py` | `agentic_core\utils\core_extensions\FileManagerAgent.py` | Exact duplicate — likely copy-paste or migration artifact |
| FilesystemAgent | `agentic_core\L5_safety\validators\FilesystemAgent.py` | `agentic_core\config\blueprint_sovereign\FilesystemAgent.py` | Leftover blueprint template — production version is canonical |
| GovernanceAgent | `agentic_core\L5_safety\validators\GovernanceAgent.py` | `agentic_core\L1_cognition\thought_engine\GovernanceAgent.py` | Exact duplicate — likely copy-paste or migration artifact |
| GovernanceAgent | `agentic_core\L5_safety\validators\GovernanceAgent.py` | `agentic_core\config\blueprint_sovereign\GovernanceAgent.py` | Leftover blueprint template — production version is canonical |
| HealerAgent | `agentic_core\L2_execution\ToolRegistry\HealerAgent.py` | `agentic_core\L5_safety\guardrails\HealerAgent.py` | Exact duplicate — likely copy-paste or migration artifact |
| HierarchyAgent | `agentic_core\L5_safety\validators\HierarchyAgent.py` | `agentic_core\config\blueprint_sovereign\HierarchyAgent.py` | Leftover blueprint template — production version is canonical |
| InferenceTypeHintAgent | `agentic_core\L5_safety\validators\InferenceTypeHintAgent.py` | `agentic_core\config\blueprint_sovereign\InferenceTypeHintAgent.py` | Leftover blueprint template — production version is canonical |
| LocationAgent | `agentic_core\L5_safety\validators\LocationAgent.py` | `agentic_core\config\blueprint_sovereign\LocationAgent.py` | Leftover blueprint template — production version is canonical |
| MetaLearningAgent | `agentic_core\L1_cognition\learning\MetaLearningAgent.py` | `agentic_core\L1_cognition\thought_engine\MetaLearningAgent.py` | Exact duplicate — likely copy-paste or migration artifact |
| MetaLearningAgent | `agentic_core\L1_cognition\learning\MetaLearningAgent.py` | `agentic_core\L3_orchestration\meta_learning\MetaLearningAgent.py` | Exact duplicate — likely copy-paste or migration artifact |
| PascalSovereigntyEnforcerAgent | `agentic_core\L5_safety\validators\PascalSovereigntyEnforcerAgent.py` | `agentic_core\config\blueprint_sovereign\PascalSovereigntyEnforcerAgent.py` | Leftover blueprint template — production version is canonical |
| PromptGovernorAgent | `agentic_core\L2_execution\ToolRegistry\PromptGovernorAgent.py` | `agentic_core\prompt_governance\rendering\PromptGovernorAgent.py` | Exact duplicate — likely copy-paste or migration artifact |
| RegressionOracleAgent | `agentic_core\L5_safety\validators\RegressionOracleAgent.py` | `agentic_core\config\blueprint_sovereign\RegressionOracleAgent.py` | Leftover blueprint template — production version is canonical |
| TerritoryHealerAgent | `agentic_core\L3_orchestration\workflow_engines\TerritoryHealerAgent.py` | `agentic_core\L5_safety\guardrails\TerritoryHealerAgent.py` | Exact duplicate — likely copy-paste or migration artifact |
| TypeHintEnforcementAgent | `agentic_core\L5_safety\validators\TypeHintEnforcementAgent.py` | `agentic_core\config\blueprint_sovereign\TypeHintEnforcementAgent.py` | Leftover blueprint template — production version is canonical |

---

## Delete Commands

**IMPORTANT:** Review each file before deleting. Use diff to compare:
```bash
code --diff "canonical_path" "duplicate_path"
```

### Delete Duplicates
```bash
git rm "agentic_core\runtime\shared_runtime\CheckpointManagerAgent.py"
git rm "agentic_core\config\blueprint_sovereign\CodeSSOTEnforcerAgent.py"
git rm "agentic_core\schemas\models\CognitiveContractManagerAgent.py"
git rm "agentic_core\config\blueprint_sovereign\ComplianceOrchestratorAgent.py"
git rm "agentic_core\utils\core_extensions\DeadCodeDetectorAgent.py"
git rm "agentic_core\config\blueprint_sovereign\DocstringComplianceAgent.py"
git rm "agentic_core\utils\core_extensions\FileManagerAgent.py"
git rm "agentic_core\config\blueprint_sovereign\FilesystemAgent.py"
git rm "agentic_core\L1_cognition\thought_engine\GovernanceAgent.py"
git rm "agentic_core\config\blueprint_sovereign\GovernanceAgent.py"
git rm "agentic_core\L5_safety\guardrails\HealerAgent.py"
git rm "agentic_core\config\blueprint_sovereign\HierarchyAgent.py"
git rm "agentic_core\config\blueprint_sovereign\InferenceTypeHintAgent.py"
git rm "agentic_core\config\blueprint_sovereign\LocationAgent.py"
git rm "agentic_core\L1_cognition\thought_engine\MetaLearningAgent.py"
git rm "agentic_core\L3_orchestration\meta_learning\MetaLearningAgent.py"
git rm "agentic_core\config\blueprint_sovereign\PascalSovereigntyEnforcerAgent.py"
git rm "agentic_core\prompt_governance\rendering\PromptGovernorAgent.py"
git rm "agentic_core\config\blueprint_sovereign\RegressionOracleAgent.py"
git rm "agentic_core\L5_safety\guardrails\TerritoryHealerAgent.py"
git rm "agentic_core\config\blueprint_sovereign\TypeHintEnforcementAgent.py"
```
