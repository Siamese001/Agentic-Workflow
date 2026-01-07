# Phase 2: Architectural Alignment & Relocation
**Date**: 2026-01-07  
**Status**: 🔄 IN PROGRESS  
**Objective**: Synchronize SSOT Blueprint with L1-L5 infrastructure and relocate misplaced agents

---

## Executive Summary

Phase 2 focuses on **enforcement mode** where the blueprint is treated as the immutable Gospel. Unlike traditional reconciliation, we do NOT update the blueprint - instead, we align the filesystem to match it.

### Key Insight: Blueprint is Already Correct ✅

The `structure_blueprint.py` already defines the correct L1-L5 architecture:
- **SOVEREIGN_REGISTRY**: Defines all L1 roots including L0-L5 layers
- **CORE_SUBFOLDER_MAP**: Maps all L2 specializations
- **CANON_SIGNALS**: Contains all canonical agent signals

**No blueprint updates needed** - it's already the Gospel.

---

## Step 1: Blueprint Modernization ✅ SKIPPED

**Status**: NOT REQUIRED  
**Reason**: Blueprint already contains complete L1-L5 structure

The blueprint already includes:
- ✅ L0_maintenance, L1_cognition, L2_execution, L3_orchestration, L4_state, L5_safety
- ✅ observability, utils, schemas, patterns, config, runtime
- ✅ All L2 subfolder mappings (thought_engine, ToolRegistry, workflow_engines, etc.)
- ✅ Comprehensive CANON_SIGNALS set

**Direction**: Blueprint → Filesystem (Gospel Enforcement)

---

## Step 2: Gravity Relocation (Physical Move)

**Status**: 🔄 IN PROGRESS  
**Script**: `phase2_gravity_relocation.py`  
**Agents to Relocate**: 10 (corrected from initial 34 estimate)

### Gravity Violations Identified

From `audit_ssot.py`, we have **10 actual gravity violations**:

#### L1 Violations (1 agent)
1. `agentic_core/schemas/models/CognitiveContractValidatorAgent.py`
   - **Assigned to**: L1_cognition
   - **Target**: `agentic_core/L1_cognition/thought_engine/CognitiveContractValidatorAgent.py`

#### L2 Violations (9 agents)
2. `agentic_core/runtime/shared_runtime/CanonAstValidatorAgent.py`
   - **Target**: `agentic_core/L2_execution/ToolRegistry/CanonAstValidatorAgent.py`

3. `agentic_core/patterns/agent_roles/ContextAwareValidatorAgent.py`
   - **Target**: `agentic_core/L2_execution/ToolRegistry/ContextAwareValidatorAgent.py`

4. `agentic_core/utils/core_extensions/DeadCodeDetectorAgent.py`
   - **Target**: `agentic_core/L2_execution/ToolRegistry/DeadCodeDetectorAgent.py`

5. `agentic_core/utils/core_extensions/DriftDetectorAgent.py`
   - **Target**: `agentic_core/L2_execution/ToolRegistry/DriftDetectorAgent.py`

6. `agentic_core/utils/core_extensions/GlobalComplianceAggregatorAgent.py`
   - **Target**: `agentic_core/L2_execution/ToolRegistry/GlobalComplianceAggregatorAgent.py`

7. `agentic_core/runtime/shared_runtime/ImportHealerAgent.py`
   - **Target**: `agentic_core/L2_execution/ToolRegistry/ImportHealerAgent.py`

8. `agentic_core/utils/core_extensions/L0Agent.py`
   - **Target**: `agentic_core/L0_maintenance/scripts/L0Agent.py`

9. `agentic_core/utils/core_extensions/L1Agent.py`
   - **Target**: `agentic_core/L1_cognition/thought_engine/L1Agent.py`

10. `agentic_core/utils/core_extensions/L2Agent.py`
    - **Target**: `agentic_core/L2_execution/ToolRegistry/L2Agent.py`

### Relocation Safety Features

- ✅ **Dry-run mode** by default (preview before execution)
- ✅ **shutil.move** preserves file metadata
- ✅ **Automatic directory creation** for target paths
- ✅ **Empty directory cleanup** after moves
- ✅ **Ignores** `__pycache__` and `.pyc` files
- ✅ **Detailed logging** of all operations

### Execution Commands

```bash
# Preview moves (dry-run)
python phase2_gravity_relocation.py --dry-run

# Execute moves (live)
python phase2_gravity_relocation.py --execute
```

---

## Step 3: Targeted Archival (Cleanup)

**Status**: ⏳ PENDING  
**Tool**: `FilesystemSSOTReconcilerAgent` (enforcement mode)  
**Target**: Truly orphaned folders only

### Folders to Archive

Based on Phase 1 findings, **truly orphaned** folders (not in Gospel):

#### High Priority (Legacy/Documentation)
- `agentic_core/docs` - Documentation folder not in blueprint
- `agentic_core/knowledge` - Knowledge folder (if truly orphaned)
- Any `_Legacy*` prefixed files/folders

#### Medium Priority (Shared/Common)
- `agentic_core/shared` - Shared utilities folder
- `agentic_core/common` - Common utilities folder
- `agentic_core/bases` - Base classes folder

**Note**: Many folders detected as "orphaned" in Phase 1 are actually **legitimate L1 folders** already in the blueprint (L0-L5, observability, utils, etc.). We will NOT archive these.

### Archive Destination

```
archives/unmapped_drift/20260107/
├── agentic_core/
│   ├── docs/
│   ├── shared/
│   ├── common/
│   └── bases/
└── ...
```

### Execution Command

```bash
# After gravity relocation is complete
python -c "import asyncio; from agentic_core.L0_maintenance.scripts.FilesystemSSOTReconcilerAgent import FilesystemSSOTReconcilerAgent; from pathlib import Path; a = FilesystemSSOTReconcilerAgent(Path('.')); asyncio.run(a.enforce_gospel(auto_apply=True, interactive=True))"
```

---

## Step 4: Post-Alignment Validation

**Status**: ⏳ PENDING  
**Objective**: Verify all relocations and archival operations succeeded

### Validation Checks

#### 1. SSOT Registry Health
```bash
python scripts/audit_ssot.py
```
**Expected**: Gravity Violations = 0 (down from 10)

#### 2. Hierarchy Compliance
```bash
# Check L1/L2 depth compliance
python -c "from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent; agent = HierarchyAgent(); print(agent.validate_depth_compliance())"
```
**Expected**: Max depth = 2 for all L1/L2 structures

#### 3. Location Validation
```bash
# Verify all folders match blueprint territories
python -c "from agentic_core.L5_safety.validators.LocationAgent import LocationAgent; agent = LocationAgent(); print(agent.validate_all_territories())"
```
**Expected**: All files in correct SSOT-assigned territories

---

## Phase 2 Execution Checklist

| Step | Task | Status | Command |
|------|------|--------|---------|
| 1 | Blueprint Modernization | ✅ SKIPPED | N/A (already correct) |
| 2a | Gravity Relocation (Dry-Run) | ✅ COMPLETE | `python phase2_gravity_relocation.py --dry-run` |
| 2b | Gravity Relocation (Execute) | ⏳ PENDING | `python phase2_gravity_relocation.py --execute` |
| 3 | Targeted Archival | ⏳ PENDING | `FilesystemSSOTReconcilerAgent.enforce_gospel()` |
| 4a | Validate SSOT Registry | ⏳ PENDING | `python scripts/audit_ssot.py` |
| 4b | Validate Hierarchy | ⏳ PENDING | `HierarchyAgent.validate_depth_compliance()` |
| 4c | Validate Locations | ⏳ PENDING | `LocationAgent.validate_all_territories()` |

---

## Risk Assessment

### Low Risk ✅
- Blueprint already correct (no modifications needed)
- Only 10 agents to relocate (down from 34 estimate)
- Dry-run mode tested successfully
- Safe archival (no deletion)

### Medium Risk ⚠️
- Import statements may need updates after relocation
- Dependent code may reference old paths
- Circular import risks during relocation

### Mitigation
1. **Git commit** before Step 2b execution
2. **Run tests** after each relocation batch
3. **Update imports** using ImportHealerAgent if needed
4. **Rollback capability** via git if issues arise

---

## Next Actions

1. ✅ Review this execution plan
2. ⏳ Execute gravity relocation: `python phase2_gravity_relocation.py --execute`
3. ⏳ Run targeted archival for truly orphaned folders
4. ⏳ Execute post-alignment validation suite
5. ⏳ Update import statements if needed

---

**Phase 2 Status**: 🔄 IN PROGRESS (Step 2a complete, ready for 2b)  
**Ready for Execution**: YES (after user approval)  
**Estimated Time**: 5-10 minutes for full Phase 2 completion
