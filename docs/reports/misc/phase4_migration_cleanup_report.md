# Phase 4 Hard Migration Cleanup Report
**Generated:** 2026-01-27
**Analysis Scope:** `agentic_core/` (excluding `tests/`, `archives/`)

---

## Executive Summary

After comprehensive scanning of the repository, I have verified which legacy agents can be safely deleted and which are still in active use.

**Result:**
- **8 files SAFE TO DELETE** (Group A legacy files)
- **6+ files STILL IN USE** (Group B specialized agents - require migration first)

---

## 1. FILES SAFE TO DELETE IMMEDIATELY

### Group A: Redundant Base/Transitional Files ✅

These files exist in `agentic_core/L5_safety/unified/` and are fully superseded by their `Unified*` counterparts. The only imports found are:
- `__init__.py` exports (which export the Unified versions, not these)
- `SubAtomicRegistryAgent.py` (migration registry mapping legacy names → Unified classes)
- `L0_maintenance/scripts/` (migration/rename scripts, not active code)

| Legacy File | Location | Superseded By | Status |
|-------------|----------|---------------|--------|
| `CodeDetectorAgent.py` | `L5_safety/unified/` | `UnifiedCodeDetectorAgent.py` | ✅ SAFE TO DELETE |
| `CodeEnforcerAgent.py` | `L5_safety/unified/` | `UnifiedCodeEnforcerAgent.py` | ✅ SAFE TO DELETE |
| `ResourceManagerAgent.py` | `L5_safety/unified/` | `UnifiedResourceManagerAgent.py` | ✅ SAFE TO DELETE |
| `SafetyDetectorAgent.py` | `L5_safety/unified/` | `UnifiedSafetyDetectorAgent.py` | ✅ SAFE TO DELETE |
| `SecurityManagerAgent.py` | `L5_safety/unified/` | `UnifiedSecurityManagerAgent.py` | ✅ SAFE TO DELETE |
| `StructuralValidatorAgent.py` | `L5_safety/unified/` | `UnifiedCodeValidatorAgent.py` | ✅ SAFE TO DELETE |
| `StructureEnforcerAgent.py` | `L5_safety/unified/` | `UnifiedStructureEnforcerAgent.py` | ✅ SAFE TO DELETE |
| `StructureHealerAgent.py` | `L5_safety/unified/` | `UnifiedStructureHealerAgent.py` | ✅ SAFE TO DELETE |

---

## 2. FILES STILL IN ACTIVE USE ⚠️

### Group B: Legacy Specialized Agents - CANNOT DELETE YET

These agents are still imported and used by active production code:

| Legacy File | Location | Active Usages | Action Required |
|-------------|----------|---------------|-----------------|
| `ImportAgent.py` | `L5_safety/gravity/` | **HealingStrategy.py**, **NervousSystemAgent.py**, **GovernanceAgent.py**, **LocationAgent.py**, **MissionPreflight.py**, **DecompositionOrchestratorAgent.py** | ❌ MIGRATE FIRST |
| `ImportLockAgent.py` | `L5_safety/gravity/` | **DecompositionOrchestratorAgent.py** | ❌ MIGRATE FIRST |
| `BiasAuditorAgent.py` | `L5_safety/validators/` | **bias_auditor.py** (runtime shim) | ❌ MIGRATE FIRST |
| `BudgetAgent.py` | `L1_cognition/thought_engine/` | **CanonBaseAgent.py** (imports from archives - broken reference) | ⚠️ CHECK ARCHIVES |
| `HallucinationHunterAgent.py` | `L5_safety/guardrails/` | No active imports found | ✅ SAFE TO DELETE |
| `PromptInjectionAgent.py` | `L5_safety/red_teaming/` | No active imports found | ✅ SAFE TO DELETE |

### Group B Files NOT FOUND in Repository

The following files from your list do not exist in `agentic_core/`:
- `DeadCodeDetectorAgent.py` - NOT FOUND (logic consolidated into `CodeDeduplicationAgent.py`)
- `DriftDetectorAgent.py` - Only `DriftDetector.py` exists (not an Agent file)
- `MethodChangeDetectorAgent.py` - NOT FOUND
- `CodeSSOTEnforcerAgent.py` - NOT FOUND
- `CodeStandardsEnforcerAgent.py` - NOT FOUND
- `PatternEnforcerAgent.py` - NOT FOUND (may be in archives)
- `CanonHealerAgent.py` - NOT FOUND
- `ImportHealerAgent.py` - NOT FOUND
- `StructuralHealerAgent.py` - NOT FOUND
- `GravityEnforcerAgent.py` - NOT FOUND
- `HierarchyEnforcerAgent.py` - NOT FOUND
- `NamingEnforcerAgent.py` - NOT FOUND
- `BiasDetectorAgent.py` - NOT FOUND (only `BiasAuditorAgent.py` exists)
- `HallucinationDetectorAgent.py` - NOT FOUND (only `HallucinationHunterAgent.py` exists)
- `PromptInjectionDetectorAgent.py` - NOT FOUND (only `PromptInjectionAgent.py` exists)
- `BudgetManagerAgent.py` - NOT FOUND (only `BudgetAgent.py` exists)
- `ProactiveResourceManagerAgent.py` - NOT FOUND

---

## 3. Functionality Parity Verification ✅

The Unified agents consolidate all functionality from their legacy counterparts:

| Unified Agent | Consolidated Legacy Functionality |
|---------------|-----------------------------------|
| `UnifiedCodeDetectorAgent` | Dead code, deadlock, memory leak, method change detection |
| `UnifiedCodeEnforcerAgent` | Standards, patterns, type hints, sovereignty enforcement |
| `UnifiedCodeHealerAgent` | Import, canon, structural healing |
| `UnifiedResourceManagerAgent` | Budget, proactive allocation, fallback strategies |
| `UnifiedSafetyDetectorAgent` | Bias, hallucination, prompt injection detection |
| `UnifiedSafetyExecutorAgent` | Pre-execution safety, integrity gates |
| `UnifiedSecurityManagerAgent` | Permissions, vault, checkpoints |
| `UnifiedStructureEnforcerAgent` | Gravity, naming, documentation, ASCII |
| `UnifiedStructureHealerAgent` | Gravity, naming, territory healing |
| `UnifiedCodeValidatorAgent` | Syntax, canon, async, print validation |

---

## 4. Unified Supersedence Confirmation ✅

The following confirms Unified agents are the new standard:

1. **`SubAtomicRegistryAgent.py`** - Maps ALL legacy names to Unified classes
2. **`HealingStrategy.py`** - Uses `UnifiedCodeValidatorAgent`, `UnifiedStructureEnforcerAgent`, `UnifiedCodeEnforcerAgent`
3. **`SafetyStrategy.py`** - Uses `UnifiedCodeValidatorAgent`, `UnifiedStructureEnforcerAgent`
4. **`AgentFactoryAgent.py`** - Creates `UnifiedCodeEnforcerAgent` instances
5. **`CanonSwarmScheduler.py`** - Imports `UnifiedCodeEnforcerAgent`
6. **`autonomous_execution_engine.py`** - Uses `UnifiedResourceManagerAgent`
7. **`__init__.py`** - Exports only Unified agents

---

## 5. Deletion Commands

### Safe to Delete Now (Group A):

```powershell
# PowerShell commands to delete Group A legacy files
Remove-Item "c:\Git\Agentic-Workflow\agentic_core\L5_safety\unified\CodeDetectorAgent.py"
Remove-Item "c:\Git\Agentic-Workflow\agentic_core\L5_safety\unified\CodeEnforcerAgent.py"
Remove-Item "c:\Git\Agentic-Workflow\agentic_core\L5_safety\unified\ResourceManagerAgent.py"
Remove-Item "c:\Git\Agentic-Workflow\agentic_core\L5_safety\unified\SafetyDetectorAgent.py"
Remove-Item "c:\Git\Agentic-Workflow\agentic_core\L5_safety\unified\SecurityManagerAgent.py"
Remove-Item "c:\Git\Agentic-Workflow\agentic_core\L5_safety\unified\StructuralValidatorAgent.py"
Remove-Item "c:\Git\Agentic-Workflow\agentic_core\L5_safety\unified\StructureEnforcerAgent.py"
Remove-Item "c:\Git\Agentic-Workflow\agentic_core\L5_safety\unified\StructureHealerAgent.py"
```

### Additional Safe Deletions (Group B - No Active Imports):

```powershell
# These have no active imports in agentic_core/
Remove-Item "c:\Git\Agentic-Workflow\agentic_core\L5_safety\guardrails\HallucinationHunterAgent.py"
Remove-Item "c:\Git\Agentic-Workflow\agentic_core\L5_safety\red_teaming\PromptInjectionAgent.py"
```

---

## 6. Migration Required Before Deletion

The following files require import migration before deletion:

### `ImportAgent.py` - 6 Active Usages
```
- agentic_core/L5_safety/validators/HealingStrategy.py
- agentic_core/L3_orchestration/workflow_engines/NervousSystemAgent.py
- agentic_core/L5_safety/validators/GovernanceAgent.py
- agentic_core/L5_safety/validators/LocationAgent.py
- agentic_core/L5_safety/validators/MissionPreflight.py
- agentic_core/L3_orchestration/workflow_engines/DecompositionOrchestratorAgent.py
```

### `ImportLockAgent.py` - 1 Active Usage
```
- agentic_core/L3_orchestration/workflow_engines/DecompositionOrchestratorAgent.py
```

### `BiasAuditorAgent.py` - 1 Active Usage
```
- agentic_core/runtime/shared_runtime/bias_auditor.py (shim layer)
```

---

## Recommendations

1. **Execute Group A deletions immediately** - These are confirmed safe
2. **Execute HallucinationHunterAgent.py and PromptInjectionAgent.py deletions** - No active imports
3. **Plan migration for ImportAgent.py** - Consolidate into UnifiedStructureEnforcerAgent or create dedicated import validation in Unified agents
4. **Update bias_auditor.py shim** - Point to UnifiedSafetyDetectorAgent instead of BiasAuditorAgent
5. **Clean up CanonBaseAgent.py** - Remove broken import from archives

---

**Report Complete**
