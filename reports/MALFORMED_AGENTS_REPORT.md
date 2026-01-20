# Malformed Agents Audit Report

**Generated**: 2026-01-18T19:09:19.955402
**Total Malformed Files**: 25

---

## Summary

| Status | Count | Action |
|--------|-------|--------|
| EXACT_DUPLICATE | 0 | DELETE Orphan |
| DIVERGENT | 9 | MANUAL MERGE |
| ORPHAN_ONLY | 16 | MOVE to Class |

---

## Detailed Findings

### `agentic_core\L1_cognition\thought_engine\L1CognitionExerciserAgent.py`

* **Classes**: L1CognitionExerciserAgent
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `_get_thought_node` (line 19)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_chain_of_thought_executor` (line 27)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_tree_of_thoughts_node` (line 35)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_react_node` (line 43)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_intent_classifier` (line 51)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_mission_decomposer` (line 59)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L2_execution\ToolRegistry\DeadCodeDetectorAgent.py`

* **Classes**: ASTDeadCodeVisitor, DeadCodeDetectorAgent
* **Status**: `DIVERGENT`
* **Action**: MANUAL MERGE required

#### Orphan: `heal_repository` (line 394)

* **Comparison**: DIFFERS from `DeadCodeDetectorAgent.heal_repository` at line 367
* **Orphan Lines**: 17
* **Method Lines**: 3
* **Recommendation**: MERGE logic, then DELETE orphan

---

### `agentic_core\L2_execution\ToolRegistry\DriftDetectorAgent.py`

* **Classes**: DriftDetectorAgent
* **Status**: `DIVERGENT`
* **Action**: MANUAL MERGE required

#### Orphan: `heal_repository` (line 106)

* **Comparison**: DIFFERS from `DriftDetectorAgent.heal_repository` at line 97
* **Orphan Lines**: 18
* **Method Lines**: 3
* **Recommendation**: MERGE logic, then DELETE orphan

---

### `agentic_core\L2_execution\ToolRegistry\HistorianAgent.py`

* **Classes**: HistorianAgent, WatchmanHandler, WatchmanHandler
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `_lazy_load_git` (line 37)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L2_execution\ToolRegistry\SystemCommandExecutorAgent.py`

* **Classes**: Logger, SystemCommandExecutorAgent, ConsoleLogger, SafeSystemCommandExecutorAgent
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `run` (line 235)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L3_orchestration\OrchestratorAgentAndScopeManagerAgent.py`

* **Classes**: OrchestratorConfig, OrchestratorState, OrchestratorHealingService, OrchestratorStateManager, OrchestratorAgentAndScopeManagerAgent
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `_signal_handler` (line 60)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L3_orchestration\fission_logic\SubAtomicAgent.py`

* **Classes**: SubAtomicAgent, sub_atomic_agent_impl, nesting_depth_visitor
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `heal_repository` (line 126)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L3_orchestration\workflow_engines\CoordinateObservabilityOperationsAgent.py`

* **Classes**: StepStatus, StepResult, OrchestrationResult, CoordinateObservabilityOperationsAgent
* **Status**: `DIVERGENT`
* **Action**: MANUAL MERGE required

#### Orphan: `heal_repository` (line 90)

* **Comparison**: DIFFERS from `CoordinateObservabilityOperationsAgent.heal_repository` at line 77
* **Orphan Lines**: 17
* **Method Lines**: 3
* **Recommendation**: MERGE logic, then DELETE orphan

---

### `agentic_core\L3_orchestration\workflow_engines\DagExecutorAgent.py`

* **Classes**: DagNode, DagExecutionResult, DagExecutorAgent
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `__init__` (line 40)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `execute` (line 59)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L3_orchestration\workflow_engines\DagRuntimeInspectorAgent.py`

* **Classes**: DiagnosticReport, DagRuntimeInspectorAgent
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `__init__` (line 35)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L3_orchestration\workflow_engines\ResumeOrchestratorAgent.py`

* **Classes**: RgResumeOrchestratorAgent
* **Status**: `DIVERGENT`
* **Action**: MANUAL MERGE required

#### Orphan: `__init__` (line 52)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `run` (line 61)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_record_hop` (line 85)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `heal_repository` (line 93)

* **Comparison**: DIFFERS from `RgResumeOrchestratorAgent.heal_repository` at line 47
* **Orphan Lines**: 16
* **Method Lines**: 3
* **Recommendation**: MERGE logic, then DELETE orphan

---

### `agentic_core\L3_orchestration\workflow_engines\SignatureVerifierAgent.py`

* **Classes**: OperationResult, SignatureVerifierAgent
* **Status**: `DIVERGENT`
* **Action**: MANUAL MERGE required

#### Orphan: `execute` (line 53)

* **Comparison**: DIFFERS from `SignatureVerifierAgent.execute` at line 35
* **Orphan Lines**: 3
* **Method Lines**: 8
* **Recommendation**: MERGE logic, then DELETE orphan

#### Orphan: `heal_repository` (line 59)

* **Comparison**: DIFFERS from `SignatureVerifierAgent.heal_repository` at line 49
* **Orphan Lines**: 17
* **Method Lines**: 3
* **Recommendation**: MERGE logic, then DELETE orphan

---

### `agentic_core\L3_orchestration\workflow_engines\SovereignRagOrchestratorAgent.py`

* **Classes**: SovereignRagOrchestratorAgent
* **Status**: `DIVERGENT`
* **Action**: MANUAL MERGE required

#### Orphan: `heal_repository` (line 40)

* **Comparison**: DIFFERS from `SovereignRagOrchestratorAgent.heal_repository` at line 211
* **Orphan Lines**: 17
* **Method Lines**: 3
* **Recommendation**: MERGE logic, then DELETE orphan

---

### `agentic_core\L3_orchestration\workflow_engines\TokenBudgetInspectorAgent.py`

* **Classes**: DiagnosticReport, TokenBudgetInspectorAgent
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `__init__` (line 35)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L3_orchestration\workflow_engines\TrackObservabilityCostAgent.py`

* **Classes**: OperationResult, TrackObservabilityCostAgent
* **Status**: `DIVERGENT`
* **Action**: MANUAL MERGE required

#### Orphan: `execute` (line 51)

* **Comparison**: DIFFERS from `TrackObservabilityCostAgent.execute` at line 33
* **Orphan Lines**: 3
* **Method Lines**: 8
* **Recommendation**: MERGE logic, then DELETE orphan

#### Orphan: `heal_repository` (line 57)

* **Comparison**: DIFFERS from `TrackObservabilityCostAgent.heal_repository` at line 47
* **Orphan Lines**: 17
* **Method Lines**: 3
* **Recommendation**: MERGE logic, then DELETE orphan

---

### `agentic_core\L3_orchestration\workflow_engines\WorkflowOrchestratorAgent.py`

* **Classes**: WorkflowContext, HopExecutionContext, LicWorkflowOrchestratorAgent
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `__init__` (line 215)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `execute` (line 237)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L4_state\ValidationContext\L4StateExerciserAgent.py`

* **Classes**: L4StateExerciserAgent
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `_get_validation_context` (line 25)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_ledger` (line 33)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_memory_store` (line 41)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_filesystem_mcp` (line 49)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L5_safety\guardrails\ConstitutionalReviewerAgent.py`

* **Classes**: ConstitutionalReviewResult, ConstitutionalReviewerAgent
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `_run_self_tests` (line 141)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L5_safety\guardrails\L5SafetyExerciserAgent.py`

* **Classes**: L5SafetyExerciserAgent
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `_get_hierarchy_agent` (line 25)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_naming_agent` (line 33)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_import_agent` (line 41)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_red_team_agent` (line 49)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_get_healer_agent` (line 57)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L5_safety\guardrails\MultiProviderRouterAgent.py`

* **Classes**: Provider, ProviderConfig, RouterConfig, MultiProviderRouterAgent
* **Status**: `DIVERGENT`
* **Action**: MANUAL MERGE required

#### Orphan: `heal_repository` (line 671)

* **Comparison**: DIFFERS from `MultiProviderRouterAgent.heal_repository` at line 558
* **Orphan Lines**: 20
* **Method Lines**: 4
* **Recommendation**: MERGE logic, then DELETE orphan

#### Orphan: `_run_self_tests` (line 692)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L5_safety\guardrails\PromptInjectionDetectorAgent.py`

* **Classes**: BaseModel, PromptInjectionDetectorAgent, PIDetectionOutput
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `_run_self_tests` (line 127)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L5_safety\guardrails\TestCoverageGuardianAgent.py`

* **Classes**: TestCoverageGuardianAgent
* **Status**: `DIVERGENT`
* **Action**: MANUAL MERGE required

#### Orphan: `heal_repository` (line 462)

* **Comparison**: DIFFERS from `TestCoverageGuardianAgent.heal_repository` at line 457
* **Orphan Lines**: 17
* **Method Lines**: 3
* **Recommendation**: MERGE logic, then DELETE orphan

---

### `agentic_core\L5_safety\validators\BudgetManagerAgent.py`

* **Classes**: DependencyGraph, BudgetManager, ValidationContext
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `_get_file_key` (line 503)

* **Comparison**: IDENTICAL to `ValidationContext._get_file_key` at line 381
* **Recommendation**: DELETE the orphan function

#### Orphan: `_path_to_module` (line 507)

* **Comparison**: IDENTICAL to `ValidationContext._path_to_module` at line 385
* **Recommendation**: DELETE the orphan function

#### Orphan: `_clean_llm_code` (line 584)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `heal_repository` (line 595)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L5_safety\validators\CanonHealerAgent.py`

* **Classes**: NestVisitor
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `heal_repository` (line 60)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_run_self_tests` (line 161)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---

### `agentic_core\L5_safety\validators\GapClosureArchitectAgent.py`

* **Classes**: CompetencyItem, CompetenciesOutput, GapClosureArchitectAgent
* **Status**: `ORPHAN_ONLY`
* **Action**: MOVE Orphan into Class

#### Orphan: `__init__` (line 63)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_build_initial_prompt` (line 126)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_build_regeneration_prompt` (line 141)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_parse_competencies` (line 155)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_extract_gap_keywords` (line 181)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_calculate_gap_coverage` (line 197)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

#### Orphan: `_check_industry_first_ranking` (line 213)

* **Comparison**: NO matching class method found
* **Recommendation**: MOVE into appropriate class

---
