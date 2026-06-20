---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\ssot-consolidation-wave-plan.md'
original_relative_path: '_archive\\2026-05\\ssot-consolidation-wave-plan.md'
source_sha256: 42abff3a860013dde940e8b8b9a0d0ff81b16acf306d09d365f78aec4fd05260
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# SSOT Consolidation Wave-Based Execution Plan

**Date:** 2026-04-06  
**Status:** Planning Phase - No Code Changes  
**Reference:** `docs/reports/plans/20260406-SSOT-Consolidation-Analysis.md`

---

## PLAN OVERVIEW

This plan breaks down the SSOT consolidation work into 5 waves, each with clear objectives, scope, and dependencies. Each wave is designed to be independently testable and reversible.

**Total Waves:** 5  
**Estimated Duration:** 8-13 hours (across all waves)  
**Risk Profile:** Progressive (Low → Medium)  
**Rollback Strategy:** Each wave can be independently reverted via git revert

---

## WAVE 1: Eliminate LAYER_OVERRIDES Hardcoding

**Priority:** HIGH  
**Risk:** LOW  
**Estimated Duration:** 2-3 hours  
**Dependencies:** None (can start immediately)

### Objectives
- Remove hardcoded LAYER_OVERRIDES dict from `_constants.py`
- Remove builder functions `_build_lcd_subfolders_template()` and `_build_layer_definition()`
- Establish yaml_loader as single source for layer data
- Update all consumers to use YAML loader

### Scope

**Files to Modify:**
1. `agentic_core/L5_safety/config/structure_blueprint/_constants.py`
   - Remove lines 86-112: `_build_lcd_subfolders_template()` function
   - Remove lines 118-531: `LAYER_OVERRIDES` dict
   - Remove lines 534-600: `_build_layer_definition()` function
   - Keep: Type definitions, operational config constants, utility functions

2. `agentic_core/L5_safety/config/structure_blueprint/yaml_loader.py`
   - Add `get_layer_overrides_dict()` helper function
   - Returns dict directly from `load_layer_overrides()`

3. `agentic_core/L5_safety/config/structure_blueprint/territories.py`
   - Change import: Remove `LAYER_OVERRIDES` from _constants
   - Add import: `from yaml_loader import get_layer_overrides_dict`
   - Update logic to use YAML-loaded data

4. `tests/unit/agentic_core/L0_routing/core/test_l0_routing_override.py`
   - Change import: Remove `LAYER_OVERRIDES` from structure_blueprint
   - Add import: `from yaml_loader import load_layer_overrides`
   - Update test to load from YAML instead of Python dict

**Files to Create:** None

**Files to Delete:** None

### Verification Steps
1. Run `pytest tests/unit/agentic_core/L0_routing/core/test_l0_routing_override.py` - PASS
2. Run `pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/` - PASS
3. Run `pytest tests/unit_min_deps/test_leaf_domain_contract.py` - PASS
4. Verify no files import LAYER_OVERRIDES from _constants (grep search)
5. Verify yaml_loader.load_layer_overrides() returns expected data (manual check)

### Rollback Strategy
```bash
git revert <commit-hash>  # Single wave revert
```

### Success Criteria
- LAYER_OVERRIDES no longer exists in _constants.py
- All tests pass
- No files import LAYER_OVERRIDES from _constants
- yaml_loader is the single source for layer data

---

## WAVE 2: Extract AST Signals to YAML

**Priority:** MEDIUM  
**Risk:** LOW  
**Estimated Duration:** 1-2 hours  
**Dependencies:** None (can run in parallel with Wave 1)

### Objectives
- Extract hardcoded AST signal definitions from Python to YAML
- Make AST signals editable without code changes
- Establish yaml_loader as single source for AST signal data

### Scope

**Files to Modify:**
1. `config/structure_blueprint/ast_signals.yaml` (CREATE)
   - Extract AST signals from build_sovereign_territories() lines 817-897
   - Structure:
     ```yaml
     schema_version: "1.0.0"
     last_updated: "2026-04-06"
     ast_signals:
       agentic_core/base_agents:
         class_patterns: [".*Base$"]
         base_classes: ["SovereignBaseAgent", "CanonBaseAgent", ...]
         keyword_signals: ["sovereign", "base", "inheritance", ...]
         weight: 100
       agentic_core/L5_safety/enforcement:
         class_patterns: [".*Guardrail.*", ".*Barrier.*", ...]
         base_classes: ["BaseGuardrail", "SafetyAirlock"]
         keyword_signals: ["mutation_check", "deletion_block", ...]
         weight: 25
       # ... all other AST signals
     ```

2. `agentic_core/L5_safety/config/structure_blueprint/yaml_loader.py`
   - Add `load_ast_signals()` function
   - Add `get_ast_signal(path)` function
   - Cache loaded data

3. `agentic_core/L5_safety/config/structure_blueprint/_constants.py`
   - Remove lines 817-897: Hardcoded AST signals from build_sovereign_territories()
   - Note: build_sovereign_territories() still exists but will load AST signals from YAML

**Files to Create:**
- `config/structure_blueprint/ast_signals.yaml`

**Files to Delete:** None

### Verification Steps
1. Verify `ast_signals.yaml` is valid YAML (syntax check)
2. Run `yaml_loader.load_ast_signals()` in REPL - returns expected data
3. Run `pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/` - PASS
4. Verify AST signals match original hardcoded values (manual comparison)

### Rollback Strategy
```bash
git revert <commit-hash>  # Single wave revert
```

### Success Criteria
- AST signals exist only in YAML file
- yaml_loader.load_ast_signals() returns correct data
- All tests pass
- AST signal data matches original hardcoded values

---

## WAVE 3: Eliminate build_sovereign_territories()

**Priority:** HIGH  
**Risk:** MEDIUM  
**Estimated Duration:** 4-6 hours  
**Dependencies:** Wave 1 (LAYER_OVERRIDES), Wave 2 (AST Signals)

### Objectives
- Remove deprecated build_sovereign_territories() function
- Remove SOVEREIGN_TERRITORIES materialization
- Create new territories_loader.py module
- Establish YAML as single source for all territory data

### Scope

**Files to Modify:**
1. `agentic_core/L5_safety/config/structure_blueprint/territories_loader.py` (CREATE)
   - Import from yaml_loader: load_territories, load_layer_overrides, load_ast_signals
   - Implement build_territories_from_yaml() function
     - Load base territories from territories.yaml
     - Apply layer overrides from layers.yaml
     - Merge AST signals from ast_signals.yaml
     - Return immutable Mapping
   - Add get_all_territories_yaml() wrapper
   - Add get_territory_yaml(name) wrapper

2. `agentic_core/L5_safety/config/structure_blueprint/territories.py`
   - Remove import: `SOVEREIGN_TERRITORIES` from _constants
   - Add import: `from territories_loader import get_all_territories_yaml`
   - Update get_territory_metadata() to use territories_loader
   - Update get_all_territories() to use territories_loader
   - Remove deprecation warning (no longer needed)

3. `agentic_core/L5_safety/config/structure_blueprint/_constants.py`
   - Remove lines 603-1618: build_sovereign_territories() function
   - Remove SOVEREIGN_TERRITORIES materialization (if separate)
   - Keep: Type definitions, operational config constants, utility functions

4. `tests/unit_min_deps/test_leaf_domain_contract.py`
   - Remove import: build_sovereign_territories from _constants
   - Add import: get_all_territories from territories
   - Update test to use new API

5. `tools/migrate/_migrate_test_files_phase4.py` (DELETE)
   - Migration script no longer needed after consolidation
   - All consumers should use new API

**Files to Create:**
- `agentic_core/L5_safety/config/structure_blueprint/territories_loader.py`

**Files to Delete:**
- `tools/migrate/_migrate_test_files_phase4.py`

### Verification Steps
1. Run `pytest tests/unit_min_deps/test_leaf_domain_contract.py` - PASS
2. Run `pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/` - PASS
3. Run `pytest tests/integration/agentic_core/test_depth_violation_no_archive_invariant.py` - PASS
4. Verify no files import build_sovereign_territories (grep search)
5. Verify no files import SOVEREIGN_TERRITORIES from _constants (grep search)
6. Verify territories_loader returns expected data (manual check)
7. Run full test suite: `pytest tests/` - PASS

### Rollback Strategy
```bash
git revert <commit-hash>  # Single wave revert
git checkout HEAD~1 -- tools/migrate/_migrate_test_files_phase4.py  # Restore deleted file
```

### Success Criteria
- build_sovereign_territories() no longer exists
- SOVEREIGN_TERRITORIES no longer exists in _constants
- territories_loader is single source for territory data
- All tests pass
- No files import deprecated functions

---

## WAVE 4: Clean Up Backward Compatibility Shim

**Priority:** LOW  
**Risk:** NONE  
**Estimated Duration:** 30 minutes  
**Dependencies:** None (can run anytime)

### Objectives
- Remove duplicate constants from structure_blueprint_config.py
- Ensure shim only contains re-export statements
- Maintain backward compatibility

### Scope

**Files to Modify:**
1. `agentic_core/L5_safety/config/structure_blueprint_config.py`
   - Remove lines 41-48: Duplicate constants (MAX_RETRIES, DEFAULT_SLEEP, etc.)
   - These are already imported from L0 path_constants (see __init__.py lines 20-29)
   - Keep: Re-export statements, __all__ definition, lifecycle trace

**Files to Create:** None

**Files to Delete:** None

### Verification Steps
1. Run `pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/` - PASS
2. Verify imports still work: `from structure_blueprint_config import MAX_RETRIES` (REPL check)
3. Verify __all__ still mirrors package __all__ (manual check)

### Rollback Strategy
```bash
git revert <commit-hash>  # Single wave revert
```

### Success Criteria
- Duplicate constants removed
- All imports still work
- Backward compatibility maintained
- All tests pass

---

## WAVE 5: Rename and Simplify _constants.py

**Priority:** LOW  
**Risk:** LOW  
**Estimated Duration:** 1-2 hours  
**Dependencies:** Wave 3 (after removal of large functions)

### Objectives
- Rename _constants.py to reflect actual content
- Evaluate operational config constants for YAML migration
- Update all imports
- Update documentation

### Scope

**Phase 5A: Evaluate Operational Config**

**Analysis Required:**
- GRAVITY_CONFIG - Structural data or runtime config?
- HEALING_CONFIG - Structural data or runtime config?
- MISSION_CONFIG - Structural data or runtime config?
- MCP_CAPABILITIES - Structural data or runtime config?
- AGENT_RESILIENCE_CONFIG - Structural data or runtime config?

**Decision Criteria:**
- If structural (defines folder structure, naming rules): Move to YAML
- If runtime (timeouts, thresholds, feature flags): Keep in Python

**Phase 5B: Rename File**

**Files to Modify:**
1. `agentic_core/L5_safety/config/structure_blueprint/_constants.py`
   - Rename to `types.py` (if only types remain)
   - OR rename to `operational_config.py` (if operational config remains)

2. `agentic_core/L5_safety/config/structure_blueprint/__init__.py`
   - Update import: `from .types import ...` (or operational_config)
   - Update all internal references

3. `agentic_core/L5_safety/config/structure_blueprint/territories.py`
   - Update import: `from .types import ...` (if types moved)
   - Update import: `from .operational_config import ...` (if config moved)

4. All other files importing _constants:
   - Update import paths (grep search and replace)

**Phase 5C: Update Documentation**

**Files to Modify:**
1. Module docstrings in renamed file
2. Package __init__.py docstring
3. Any external documentation references

**Files to Create:** None

**Files to Delete:**
- `agentic_core/L5_safety/config/structure_blueprint/_constants.py` (after rename)

### Verification Steps
1. Run `pytest tests/unit/agentic_core/L5_safety/config/structure_blueprint/` - PASS
2. Run `pytest tests/` - PASS (full suite)
3. Verify no files import _constants (grep search)
4. Verify all imports resolve correctly (manual check)
5. Verify documentation is updated

### Rollback Strategy
```bash
git revert <commit-hash>  # Single wave revert
git mv types.py _constants.py  # Reverse rename if needed
```

### Success Criteria
- File renamed to reflect actual content
- All imports updated
- No files import _constants
- All tests pass
- Documentation updated

---

## EXECUTION ORDER

### Option 1: Sequential (Recommended for Safety)
```
Wave 1 → Wave 2 → Wave 3 → Wave 4 → Wave 5
```
**Advantages:** Clear dependency chain, easy to debug, progressive risk  
**Disadvantages:** Longer total duration

### Option 2: Parallel (Faster but Riskier)
```
[Wave 1, Wave 2, Wave 4] → Wave 3 → Wave 5
```
**Advantages:** Faster completion  
**Disadvantages:** Harder to debug if multiple waves fail

### Option 3: Incremental (Hybrid)
```
Wave 1 → [Wave 2, Wave 4] → Wave 3 → Wave 5
```
**Advantages:** Balance of speed and safety  
**Disadvantages:** Requires coordination

**Recommended:** Option 1 (Sequential) for first execution

---

## GATE CHECKPOINTS

### Pre-Wave Gate (Before Each Wave)
- [ ] Previous wave tests pass
- [ ] No uncommitted changes
- [ ] Feature branch is clean
- [ ] Rollback strategy documented

### Post-Wave Gate (After Each Wave)
- [ ] Wave-specific tests pass
- [ ] No regression in related tests
- [ ] Grep confirms no deprecated imports
- [ ] Manual verification of data correctness
- [ ] Commit message follows conventions

### Final Gate (After All Waves)
- [ ] Full test suite passes
- [ ] No deprecated imports in codebase
- [ ] YAML files are valid
- [ ] Documentation updated
- [ ] Rollback plan archived

---

## TESTING STRATEGY

### Unit Tests
- Each wave includes specific test updates
- Run unit tests for modified modules
- Run unit tests for dependent modules

### Integration Tests
- Run integration tests for structure_blueprint
- Run integration tests for L5_safety

### Regression Tests
- Run full test suite after Wave 3 (highest risk)
- Run full test suite after Wave 5 (final verification)

### Manual Verification
- REPL checks for import correctness
- Manual comparison of data before/after
- Visual inspection of YAML files

---

## RISK MITIGATION

### Low Risk Waves (1, 2, 4, 5)
- Can proceed with standard review
- Single developer can execute
- Rollback is straightforward

### Medium Risk Wave (3)
- Requires code review before merge
- Consider pair programming
- Test in staging environment first
- Have rollback command ready

### Contingency Plans
- If Wave 3 fails: Revert Wave 3, investigate, retry
- If tests fail: Stop wave, investigate, fix before proceeding
- If data mismatch: Compare YAML vs Python, fix YAML, retry

---

## SUCCESS METRICS

### Code Quality
- Lines of code removed: ~1,400
- Files deleted: 1 (migration script)
- Files created: 2 (ast_signals.yaml, territories_loader.py)
- Cyclomatic complexity reduction in _constants.py

### Maintainability
- YAML is single source for structural data
- File/folder updates require only YAML edits
- No duplicate data between YAML and Python
- Clear separation of concerns (types, data, logic)

### Test Coverage
- All existing tests pass
- New tests for yaml_loader functions
- New tests for territories_loader functions

### Performance
- No performance regression (lazy loading maintained)
- YAML loading is cached (no I/O overhead)

---

## POST-CONSOLIDATION TASKS

### Immediate (After Wave 5)
1. Update project documentation to reflect new structure
2. Add YAML schema validation to pre-commit hooks
3. Update developer onboarding guide
4. Archive rollback plan

### Short-term (1-2 weeks)
1. Monitor for any issues with new YAML-based structure
2. Gather feedback from team on ease of updates
3. Consider adding YAML editor support in IDE
4. Update CI/CD to validate YAML syntax

### Long-term (1-3 months)
1. Evaluate other hardcoded data for YAML migration
2. Consider adding YAML validation schema
3. Automate YAML-to-Python synchronization checks
4. Document lessons learned for future consolidations

---

## COMMUNICATION PLAN

### Before Execution
- Announce consolidation plan to team
- Schedule review meeting for Wave 3 (medium risk)
- Provide timeline and expected impact

### During Execution
- Update team after each wave completion
- Flag any issues or blockers immediately
- Provide progress updates in standup

### After Execution
- Share final results with team
- Document any lessons learned
- Update project documentation

---

## APPENDICES

### Appendix A: File Inventory

**Before Consolidation:**
- `_constants.py`: 1,845 lines
- `structure_blueprint_config.py`: 175 lines
- `yaml_loader.py`: 86 lines
- `territories.py`: 239 lines
- `layers.yaml`: 95 lines
- `territories.yaml`: 495 lines

**After Consolidation (Expected):**
- `types.py` or `operational_config.py`: ~200-400 lines
- `structure_blueprint_config.py`: ~167 lines (8 lines removed)
- `yaml_loader.py`: ~100 lines (AST signals loader added)
- `territories_loader.py`: ~150 lines (new file)
- `territories.py`: ~200 lines (simplified)
- `layers.yaml`: 95 lines (unchanged)
- `territories.yaml`: 495 lines (unchanged)
- `ast_signals.yaml`: ~100 lines (new file)

### Appendix B: Import Mapping

**Old Imports (Deprecated):**
```python
from agentic_core.L5_safety.config.structure_blueprint._constants import (
    LAYER_OVERRIDES,
    SOVEREIGN_TERRITORIES,
    build_sovereign_territories,
)
```

**New Imports (After Consolidation):**
```python
from agentic_core.L5_safety.config.structure_blueprint.yaml_loader import (
    load_layer_overrides,
    load_territories,
    load_ast_signals,
)
from agentic_core.L5_safety.config.structure_blueprint.territories_loader import (
    get_all_territories_yaml,
    get_territory_yaml,
)
from agentic_core.L5_safety.config.structure_blueprint.territories import (
    get_territory_metadata,
    get_all_territories,
)
```

### Appendix C: Rollback Commands

**Rollback Single Wave:**
```bash
git log --oneline -5  # Find commit hash
git revert <commit-hash>
git push origin <branch>
```

**Rollback All Waves:**
```bash
git reset --hard <pre-consolidation-commit>
git push origin <branch> --force
```

**Restore Deleted File:**
```bash
git checkout HEAD~1 -- tools/migrate/_migrate_test_files_phase4.py
```

---

**End of Wave-Based Execution Plan**
