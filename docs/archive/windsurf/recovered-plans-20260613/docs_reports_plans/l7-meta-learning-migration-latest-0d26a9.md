# L7 Meta-Learning Migration Plan with Latest Repo Changes

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Summary
Move `agentic_core/L7_meta_learning` to `system_learning/` with comprehensive import updates, L0_maintenance cleanup, and execute_ssot downstream file updates.

## Current State Analysis

### Files to Move
```
agentic_core/L7_meta_learning/
├── __init__.py
├── enforcement/
│   ├── __init__.py
│   ├── determinism.py
│   └── determinism_enforcer.py
└── types/
    ├── __init__.py
    ├── app_signal_types.py
    ├── apply_attempt_types.py
    ├── meta_learning_types.py
    ├── offline_replay_types.py
    └── rollout_types.py
```

### Test Files to Move
```
tests/agentic_core/L7_meta_learning/
├── __init__.py
├── test_app_signal_aggregation.py
├── test_meta_learning_contract.py
├── test_meta_learning_rollout.py
└── test_offline_replay_golden.py
```

### Current Dependencies (Latest Scan)
- **Direct imports**: 27 files import from `agentic_core.L7_meta_learning`
- **Key consumers**:
  - `agentic_core.L0_routing.meta_control.*` (4 files)
  - `apps_shared.scripts.*` (2 files)
  - `tests/` (9 test files)
  - Internal L7_meta_learning files (6 files)
  - Structure blueprint files (2 files)

### Stale L0_maintenance References Found
- **Test files with wrong paths**: 2 test files reference old L0_maintenance structure
- **Base agent file**: `L0MaintenanceBase.py` exists but tests reference `l0_maintenance_base_agent.py`

### Execute SSOT Downstream Files
- `agentic_core/L0_routing/scripts/execute_ssot.py` - Main SSOT execution script
- Multiple test files referencing execute_ssot functionality
- Structure blueprint and configuration files

## Implementation Plan

### Phase 1: Directory Structure Creation
1. Create `system_learning/` directory structure
2. Create `system_learning/enforcement/` and `system_learning/types/` subdirectories
3. Create `tests/system_learning/` directory

### Phase 2: L7 Meta-Learning File Migration
1. Move all Python files from `agentic_core/L7_meta_learning/` to `system_learning/`
2. Move all test files from `tests/agentic_core/L7_meta_learning/` to `tests/system_learning/`
3. Update internal imports within moved files

### Phase 3: L0_maintenance Reference Cleanup

#### Test File Fixes (2 files)
- `tests/agentic_core/L0_routing/scripts/test_l0_maintenance_base_agent.py`
  - Update import: `agentic_core.base_agents.l0_maintenance_base_agent` → `agentic_core.base_agents.L0MaintenanceBase`
- `tests/unit/agentic_core/L0_maintenance/scripts/test_l0_maintenance_base_agent.py`
  - Update import: `agentic_core.base_agents.l0_maintenance_base_agent` → `agentic_core.base_agents.L0MaintenanceBase`

### Phase 4: L7 Meta-Learning Import Updates (27 files)

#### Core System Files
- `agentic_core/L5_safety/config/structure_blueprint/_constants.py`
- `agentic_core/L5_safety/config/structure_blueprint/classification.py`
- `agentic_core/L5_safety/enforcement/module_collision_guardrail.py`
- `agentic_core/L5_safety/enforcement/module_collision_guardrail.py`

#### L0 Routing Meta Control (4 files)
- `agentic_core/L0_routing/meta_control/meta_apply.py`
- `agentic_core/L0_routing/meta_control/meta_apply_ops.py`
- `agentic_core/L0_routing/meta_control/config_store.py`
- `agentic_core/L0_routing/meta_control/config_store_types.py`

#### Apps Shared Scripts (2 files)
- `apps_shared/scripts/meta_learning_operator.py`
- `apps_shared/scripts/meta_learning_bridge.py`

#### Test Files (9 files)
- `tests/guardian/test_l7_determinism.py`
- `tests/apps_shared/scripts/test_meta_learning_operator.py`
- `tests/apps_shared/scripts/test_meta_learning_bridge.py`
- `tests/agentic_core/L0_routing/meta_control/test_*.py` (4 files)
- `tests/system_learning/*.py` (4 files - moved and updated)

#### Internal L7 Files (6 files)
- All moved files need internal import updates

### Phase 5: Execute SSOT Downstream Updates

#### SSOT Configuration Files
- Update any references in `docs/specs/execute_ssot_bucket_map.json`
- Update `docs/specs/execute_ssot_inventory.json`
- Update structure blueprint configurations

#### Test Files with Execute SSOT References
- Identify and update test files that reference L7_meta_learning in execute_ssot context
- Update folder purity invariants and enforcement tests

### Phase 6: Content Updates

#### Internal Import Changes
- Update `system_learning/types/__init__.py` imports
- Update any relative imports within moved files

#### Path References
- Update any hardcoded path references in documentation
- Update import statements in all dependent files

#### Structure Blueprint Updates
- Update L7_meta_learning subfolder definition in `_constants.py`
- Update module collision guard configurations
- Update classification references

### Phase 7: Test Validation
1. Run test suite to ensure all imports resolve correctly
2. Validate that moved tests still pass
3. Run integration tests for meta-learning functionality
4. Verify L0_maintenance base agent tests pass with corrected imports
5. Verify execute_ssot functionality works with new paths
6. Run folder purity invariants tests
7. Verify no broken imports remain

## Expected File Diffs

### New Directory Structure
```
system_learning/
├── __init__.py
├── enforcement/
│   ├── __init__.py
│   ├── determinism.py
│   └── determinism_enforcer.py
└── types/
    ├── __init__.py
    ├── app_signal_types.py
    ├── apply_attempt_types.py
    ├── meta_learning_types.py
    ├── offline_replay_types.py
    └── rollout_types.py

tests/system_learning/
├── __init__.py
├── test_app_signal_aggregation.py
├── test_meta_learning_contract.py
├── test_meta_learning_rollout.py
└── test_offline_replay_golden.py
```

### Import Pattern Changes
```python
# L7 Meta-Learning imports
# Before
from agentic_core.L7_meta_learning.types.meta_learning_types import MetaLearningChangePackageArtifact

# After
from system_learning.types.meta_learning_types import MetaLearningChangePackageArtifact

# L0_maintenance base agent imports
# Before
from agentic_core.base_agents.l0_maintenance_base_agent import L0MaintenanceBaseAgent

# After
from agentic_core.base_agents.L0MaintenanceBase import L0MaintenanceBase
```

### Execute SSOT Configuration Updates
```json
// Before
{
  "L7_meta_learning": {
    "path": "agentic_core/L7_meta_learning",
    "imports": ["agentic_core.L7_meta_learning.*"]
  }
}

// After
{
  "system_learning": {
    "path": "system_learning",
    "imports": ["system_learning.*"]
  }
}
```

## Risk Assessment

### Low Risk
- File moves are straightforward
- Import patterns are consistent
- Test files move with implementation
- L0_maintenance fixes are simple import path corrections

### Medium Risk
- 27 files need import updates for L7 migration (increased from 23)
- 2 test files need L0_maintenance import fixes
- Execute_ssot downstream files may need updates
- Structure blueprint configurations need updates
- Potential for missed import references

### High Risk
- Execute_ssot functionality may be impacted by path changes
- Folder purity invariants may fail with new structure
- Module collision guard configurations need precise updates

### Mitigation
- Comprehensive search for all import references including execute_ssot context
- Step-by-step validation after each phase
- Full test suite validation before completion
- Specific test runs for execute_ssot functionality
- Verify folder purity invariants pass

## Test Plan Cases

### Unit Tests
1. Verify all moved tests pass in new location
2. Test import resolution from new module path
3. Validate type definitions still work correctly
4. Test L0_maintenance base agent imports resolve correctly

### Integration Tests
1. Test meta-learning operator functionality
2. Verify L0 routing meta control integration
3. Test config store interactions
4. Verify L0_maintenance base agent functionality
5. Test execute_ssot functionality with new paths

### Execute SSOT Specific Tests
1. Test folder purity invariants with new structure
2. Verify module collision guard works correctly
3. Test structure blueprint validation
4. Run execute_ssot end-to-end tests

### Regression Tests
1. Run full test suite to ensure no broken imports
2. Verify existing meta-learning workflows unchanged
3. Test rollback and rollout functionality
4. Verify base agent test suite passes with corrected imports
5. Test execute_ssot complete pipeline

## Success Criteria
- All files moved successfully
- All imports updated and working (27 files)
- All tests pass in new location
- L0_maintenance base agent tests pass with corrected imports
- Execute_ssot functionality fully preserved
- Folder purity invariants pass
- No broken references remain
- Meta-learning functionality fully preserved
- Base agent functionality fully preserved
- Structure blueprint configurations updated correctly

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

