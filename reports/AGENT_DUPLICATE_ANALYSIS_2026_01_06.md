# Agent Duplicate Analysis Report
**Generated:** January 06, 2026  
**Total Duplicate Class Names Found:** 32  
**Action Required:** Yes - cleanup recommended

---

## Executive Summary

The agent discovery scan found **32 class names** that appear in multiple files. This creates:
- Confusion about which is the canonical implementation
- Potential import conflicts
- Maintenance burden (changes must be made in multiple places)
- Dashboard count discrepancies (fixed separately)

### Why HygieneGuardianAgent Duplicate Wasn't Found Earlier

The duplicate `agentic_core/L5_safety/agents/HygieneGuardianAgent.py` existed alongside `agentic_core/L5_safety/validators/HygieneGuardianAgent.py`. It was **deleted earlier in this session** as part of the L5 Safety base class count fix. The discovery script was correctly finding both, but the duplicate was in a non-standard location (`agents/` instead of `validators/`).

---

## Findings by Priority

### 🔴 CRITICAL - Delete Immediately (Empty/Placeholder Files)

| File | Size | Recommendation | Rationale |
|------|------|----------------|-----------|
| `agentic_core/L3_orchestration/meta_learning/MetaLearningAgent.py` | **0 chars** | **DELETE** | Empty placeholder file. Real implementation is at `L1_cognition/learning/MetaLearningAgent.py` (11,595 chars) |

### 🟠 HIGH - Consolidate (Same Class in Multiple Files)

| Class Name | Locations | Recommendation |
|------------|-----------|----------------|
| **IntegrityGateExecutorAgent** (4 copies) | `healer_executive.py`, `IntegrityGateExecutorAgent.py`, `peer_intelligence_auditor_impl.py`, `section_scope_integrator_engine.py` | **CONSOLIDATE** to single canonical file, import elsewhere |
| **BiasAuditorAgent** (3 copies) | `L0_maintenance/scripts/`, `runtime/shared_runtime/`, `L5_safety/validators/` | **KEEP L5** (validators), deprecate others |
| **SafetyInspectorAgent** (3 copies) | `L1_cognition/`, `L2_execution/`, `L5_safety/guardrails/` | **KEEP L5** (safety domain), deprecate others |

### 🟡 MEDIUM - Layer Misplacement (Same Class in Wrong Layer)

| Class Name | Current Locations | Recommendation | Rationale |
|------------|-------------------|----------------|-----------|
| **ArchitectureGovernorAgent** | L2 `governance.py`, L3 `ArchitectureGovernorAgent.py` | **KEEP L3** | Architecture governance is orchestration-level |
| **ConcurrencyGuardianAgent** | L1 `concurrency_guardian.py`, L2 `security.py` | **KEEP L2** | Concurrency is execution-level concern |
| **DeadlockDetectorAgent** | L2 `concurrency.py`, L3 `deadlock_detector.py` | **KEEP L3** | Deadlock detection spans workflows |
| **DependencySentinelAgent** | L1 `DependencySentinelAgent.py`, L2 `governance.py` | **KEEP L2** | Dependency management is execution |
| **FissionManagerAgent** | L3 `FissionManagerAgent.py`, L3 `WorkflowFissionManagerAgent.py` | **MERGE** into `FissionManagerAgent.py` |
| **GitAgent** | L2 `GitAgent.py`, L2 `infrastructure.py` | **KEEP** `GitAgent.py`, remove from multi-class file |
| **HierarchyHealerAgent** | `config/blueprint_sovereign/`, `L5_safety/guardrails/` | **KEEP L5** | Healing belongs in safety layer |
| **MemoryLeakDetectorAgent** | L2 `concurrency.py`, L3 `memory_leak_detector.py` | **KEEP L3** | Memory management spans workflows |
| **NamingAgent** | L1 `canon_agents_quality.py`, `utils/core_extensions/` | **KEEP utils** | Naming is a utility function |
| **NeuralAutoImmuneAgent** | `NeuralAutoImmuneAgent.py`, `PolicyNeuralAutoImmuneAgent.py` | **MERGE** - Policy variant should extend base |
| **PatternEnforcerAgent** | L1 `canon_agents_pattern.py`, L2 `engineering.py` | **KEEP L1** | Pattern enforcement is cognitive |
| **RedSentinelAgent** | L2 `security.py`, L5 `RedSentinelAgent.py` | **KEEP L5** | Security belongs in safety layer |
| **TestPilotAgent** | L2 `repair.py`, L3 `TestPilotAgent.py` | **KEEP L3** | Test orchestration spans workflows |
| **ToolsmithAgent** | L2 `repair.py`, L2 `ToolsmithAgent.py` | **KEEP** standalone file |

### 🟢 LOW - App-Specific Duplicates (Expected/Acceptable)

| Class Name | Locations | Recommendation | Rationale |
|------------|-----------|----------------|-----------|
| **ReflectionAgent** | L2 `planning.py`, `apps_rg/agents.py` | **KEEP BOTH** | App-specific customization is valid |
| **StrategicPlannerAgent** | L2 `planning.py`, `apps_rg/agents.py` | **KEEP BOTH** | App-specific customization is valid |
| **TemplateOptimizerAgent** | `apps_lic/agents.py`, `apps_rg/agents.py` | **KEEP BOTH** | Different apps, different templates |
| **WorkflowOrchestratorAgent** | L0 `runtime_shared_workflow_integration.py`, `apps_lic/` | **KEEP BOTH** | App-specific orchestration |
| **ResumeOrchestratorAgent** | L3 workflow_engines, `apps_rg/` | **KEEP BOTH** | App wraps core |

### 🔵 INFO - Blueprint/Reference Duplicates (Keep As-Is)

| Class Name | Locations | Recommendation | Rationale |
|------------|-----------|----------------|-----------|
| **AutonomyGuardianAgent** | `blueprint_sovereign/AutonomyGuardianAgent_blueprint.py`, `L5_safety/validators/` | **KEEP BOTH** | Blueprint is reference implementation |

### ⚪ ARCHIVE - Already Deprecated

| Class Name | Archive Location | Recommendation |
|------------|------------------|----------------|
| `agent_capabilities.py` | `archives/runtime/registry/` | Already archived, no action needed |
| `k5_cta_agent.py` | `archives/` (2 locations) | Already archived |
| `runtime_observability_agentic_spans.py` | `archives/observability/` (2 locations) | Already archived |
| `test_agentic_canon.py` | `archives/` | Already archived |

---

## Semantic Duplicates (P1Core* Pattern)

Several agents have both a "P1Core" prefixed version and a non-prefixed version:

| Base Name | Files | Recommendation |
|-----------|-------|----------------|
| **SemanticTerritoryMapperAgent** | `P1CoreSemanticTerritoryMapperAgent.py`, `SemanticTerritoryMapperAgent.py` | **DELETE P1Core** variant - naming convention deprecated |
| **TerritoryHealerAgent** | `P1CoreTerritoryHealerAgent.py`, `TerritoryHealerAgent.py` | **DELETE P1Core** variant |
| **SovereignPineconeStoreAgent** | `pinecone_pinecone_store.py`, `SovereignPineconeStoreAgent.py` | **KEEP** `SovereignPineconeStoreAgent.py` |
| **SovereignRedisOrchestratorAgent** | `P2_tools_autonomous_redis_orchestrator.py`, `SovereignRedisOrchestratorAgent.py` | **KEEP** standalone file |
| **SystemArchitectAgent** | `SystemArchitectAgent.py`, `system_architect.py` | **MERGE** into `SystemArchitectAgent.py` |
| **StructuralEngineerAgent** | `engineering.py`, `StructuralEngineerAgent.py` | **KEEP** standalone file |

---

## Recommended Actions

### Immediate (This Sprint)

1. **DELETE** empty `L3_orchestration/meta_learning/MetaLearningAgent.py`
2. **DELETE** P1Core* prefixed files (deprecated naming)
3. **CONSOLIDATE** IntegrityGateExecutorAgent to single file

### Short-Term (Next 2 Sprints)

4. Move misplaced agents to correct layers (see MEDIUM priority table)
5. Update imports across codebase after moves
6. Add `# CANONICAL: True` comment to authoritative versions

### Long-Term

7. Implement import guards to prevent duplicate class registration
8. Add CI check for duplicate class names in discovery JSON

---

## Impact Analysis

| Metric | Before | After Cleanup |
|--------|--------|---------------|
| Duplicate class names | 32 | ~10 (app-specific only) |
| Empty/placeholder files | 1 | 0 |
| P1Core* deprecated files | 4 | 0 |
| Multi-class files with duplicates | 8 | 0 |

---

## Appendix: Full Duplicate List

```
ArchitectureGovernorAgent (2x)
AutonomousThreatEvolutionAgent (2x)
AutonomyGuardianAgent (2x) - KEEP (blueprint pattern)
BiasAuditorAgent (3x)
CanonValidatorAgent (2x)
ConcurrencyGuardianAgent (2x)
DeadlockDetectorAgent (2x)
DependencySentinelAgent (2x)
DriftDetectorAgent (2x)
FissionManagerAgent (2x)
GitAgent (2x)
HierarchyHealerAgent (2x)
IntegrityGateExecutorAgent (4x)
MemoryLeakDetectorAgent (2x)
NamingAgent (2x)
NeuralAutoImmuneAgent (2x)
PatternEnforcerAgent (2x)
RedSentinelAgent (2x)
ReflectionAgent (2x) - KEEP (app-specific)
ResumeOrchestratorAgent (2x) - KEEP (app-specific)
SafetyInspectorAgent (3x)
SemanticTerritoryMapperAgent (2x)
SovereignPineconeStoreAgent (2x)
SovereignRedisOrchestratorAgent (2x)
StrategicPlannerAgent (2x) - KEEP (app-specific)
StructuralEngineerAgent (2x)
SystemArchitectAgent (2x)
TemplateOptimizerAgent (2x) - KEEP (app-specific)
TerritoryHealerAgent (2x)
TestPilotAgent (2x)
ToolsmithAgent (2x)
WorkflowOrchestratorAgent (2x) - KEEP (app-specific)
```
