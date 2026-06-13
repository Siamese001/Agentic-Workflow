# SOVEREIGN_TERRITORIES Removal Audit

**Date:** 2026-03-11T19:10:00Z
**Context:** User confirmed SOVEREIGN_TERRITORIES was completely removed, but 71 downstream files still reference it.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

**Status:** ❌ **INCOMPLETE REMOVAL**

- **71 downstream files** still reference `SOVEREIGN_TERRITORIES`
- **3 definition files** (allowed — these define/export it)
- **Total references:** 74 files

**Critical finding:** The removal is incomplete. While the definition may have been replaced with `PROJECT_ROOT_WHITELIST`, downstream consumers were not updated.

---

## File Categories

### 1. Definition/Export Files (3 files — ALLOWED)

These files define or re-export `SOVEREIGN_TERRITORIES`:

| File | Refs | Status |
|---|---|---|
| `agentic_core/L5_safety/config/structure_blueprint/_constants.py` | 5 | Defines `build_sovereign_territories()` and `SOVEREIGN_TERRITORIES` |
| `agentic_core/L5_safety/config/structure_blueprint/__init__.py` | 3 | Re-exports from `_constants.py` |
| `agentic_core/L5_safety/config/structure_blueprint_config.py` | 1 | Backward-compat shim |

**Action:** If SOVEREIGN_TERRITORIES was removed, these files should export `PROJECT_ROOT_WHITELIST` instead, or the symbol should be deprecated with a migration path.

### 2. Core Infrastructure (11 files — HIGH PRIORITY)

These are active production files in `agentic_core/`:

| File | Refs | Impact |
|---|---|---|
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | 11 | Blueprint verification |
| `agentic_core/L5_safety/config/structure_blueprint/derived.py` | 15 | Derives maps from territories |
| `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | 11 | SSOT validation |
| `agentic_core/L5_safety/config/structure_blueprint/territories.py` | 1 | Territory utilities |
| `agentic_core/L5_safety/config/blueprint_compiler.py` | 8 | Blueprint compilation |
| `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` | 2 | Architecture governance |
| `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` | 1 | Location healing |
| `agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py` | 1 | SSOT reconciliation |
| `agentic_core/L5_safety/reasoning/hierarchy_healer.py` | 3 | Hierarchy healing |
| `agentic_core/L5_safety/reasoning/root_hygiene_healer.py` | 2 | Root hygiene |
| `agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py` | 1 | SSOT enforcement |

**Action:** These must be refactored to use `PROJECT_ROOT_WHITELIST` or the new replacement API.

### 3. Utilities & Scripts (9 files — MEDIUM PRIORITY)

| File | Refs | Type |
|---|---|---|
| `agentic_core/L0_routing/config/__init__.py` | 1 | Config |
| `agentic_core/L0_routing/scripts/execute_ssot.py` | 3 | Script |
| `agentic_core/L0_routing/scripts/populate_ssot_folders_util.py` | 1 | Script |
| `agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py` | 4 | Script |
| `agentic_core/L5_safety/utils/extract_pattern_util.py` | 1 | Utility |
| `agentic_core/L5_safety/utils/location_path_util.py` | 1 | Utility |
| `agentic_core/L5_safety/utils/location_utils_util.py` | 1 | Utility |
| `agentic_core/config/core/registry_config.py` | 1 | Config |
| `ops_scripts/maintenance/territory_ssot_definitions_config.py` | 1 | Script |

### 4. Tests (25 files — MEDIUM PRIORITY)

Active test files that verify SOVEREIGN_TERRITORIES behavior:

| File | Refs | Test Focus |
|---|---|---|
| `tests/unit/agentic_core/L5_safety/reasoning/test_constants_quarantine_invariant.py` | 19 | Quarantine invariants |
| `tests/integration/agentic_core/L5_safety/reasoning/test_tests_support_phantom_subdirs.py` | 28 | Phantom subdirs |
| `tests/integration/agentic_core/L5_safety/reasoning/test_hierarchy_agent_phantom_dir_edge_cases.py` | 20 | Phantom dirs |
| `tests/integration/agentic_core/L5_safety/reasoning/test_hierarchy_agent_tests_structure.py` | 11 | Tests structure |
| `tests/integration/agentic_core/L5_safety/reasoning/test_depth_pipeline_execute_ssot.py` | 8 | Depth pipeline |
| `tests/architecture/test_contracts_fixture_placement.py` | 8 | Fixture placement |
| `tests/guardian/test_ssot_alignment.py` | 5 | SSOT alignment |
| `tests/architecture/test_phantom_folder_regression.py` | 5 | Phantom folders |
| `tests/integration/test_depth_violation_no_archive_invariant.py` | 4 | Depth violations |
| `tests/unit/agentic_core/L5_safety/validators/test_global_candidate_vacuum.py` | 3 | Gravity weights |
| `tests/integration/agentic_core/L5_safety/reasoning/test_blueprint_module_eviction.py` | 3 | Module eviction |
| `tests/unit/agentic_core/L5_safety/config/test_structure_blueprint_config.py` | 2 | Blueprint config |
| `tests/architecture/test_hierarchy_agent_invariants.py` | 2 | Hierarchy invariants |
| `tests/guardian/test_structure_blueprint_hardened.py` | 1 | Blueprint hardening |
| `tests/unit/agentic_core/L5_safety/validators/test_flat_directory_enforcement.py` | 1 | Flat dirs |
| `tests/integration/agentic_core/L5_safety/reasoning/test_heal_depth_violation_exhaustive.py` | 1 | Depth healing |
| *(+9 more test files in .healing_backups/)* | — | Backup tests |

### 5. Ops Scripts (4 files — LOW PRIORITY)

| File | Refs |
|---|---|
| `ops_scripts/ci/ast_hardcoded_path_scanner.py` | 3 |
| `ops_scripts/ci/ssot_violation_scanner.py` | 2 |
| `ops_scripts/general/generate_init_py.py` | 2 |
| `ops_scripts/hooks/validate_paths.py` | 1 |

### 6. Documentation Scripts (6 files — LOW PRIORITY)

Analysis/verification scripts in `docs/reports/plans/`:

| File | Refs |
|---|---|
| `docs/reports/plans/_adg_sovereign_verification.py` | 24 |
| `docs/reports/plans/_adg_sqlite_validation.py` | 17 |
| `docs/reports/plans/_p2_verify.py` | 11 |
| `docs/reports/plans/_full_audit.py` | 10 |
| `docs/reports/plans/_comprehensive_sovereign_scan.py` | 9 |
| `docs/reports/plans/_find_exact_usages.py` | 2 |
| `docs/reports/plans/_p2_scope.py` | 3 |

### 7. Archives & Backups (12 files — IGNORE)

Old healing backups and archives — can be ignored.

---

## Recommended Migration Path

### Phase 1: Verify Replacement API (IMMEDIATE)

1. **Confirm the replacement:** What replaced `SOVEREIGN_TERRITORIES`?
   - `PROJECT_ROOT_WHITELIST`? (mentioned in test file)
   - A new API in `structure_blueprint`?
   - Complete removal with no replacement?

2. **Document the migration pattern:**
   ```python
   # Old
   from agentic_core.L5_safety.config.structure_blueprint import SOVEREIGN_TERRITORIES
   territory = SOVEREIGN_TERRITORIES.get("apps_shared", {})

   # New (example — needs confirmation)
   from agentic_core.L5_safety.config.structure_blueprint import PROJECT_ROOT_WHITELIST
   # ... new API pattern ...
   ```

### Phase 2: Update Core Infrastructure (HIGH PRIORITY)

Refactor the 11 core infrastructure files in priority order:
1. `structure_blueprint/derived.py` (15 refs) — derives maps from territories
2. `structure_blueprint/_verify.py` (11 refs) — verification logic
3. `structure_blueprint/ssot.py` (11 refs) — SSOT validation
4. `blueprint_compiler.py` (8 refs) — compilation
5. Reasoning agents (5 files) — healing/governance

### Phase 3: Update Tests (MEDIUM PRIORITY)

Update the 25 test files to use the new API. Some tests may need to be rewritten or removed if they test SOVEREIGN_TERRITORIES-specific behavior.

### Phase 4: Update Scripts & Utils (LOW PRIORITY)

Update ops scripts and utilities.

### Phase 5: Deprecation Warning (OPTIONAL)

If backward compatibility is needed, add a deprecation warning:
```python
# In _constants.py
import warnings

def build_sovereign_territories():
    warnings.warn(
        "SOVEREIGN_TERRITORIES is deprecated. Use PROJECT_ROOT_WHITELIST instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... existing logic ...
```

---

## Impact Analysis

**Breaking changes if removed immediately:**
- 11 core infrastructure files will fail
- 25 test files will fail
- SSOT validation, healing, and governance will break

**Estimated effort:**
- Core infrastructure: 2- (complex refactoring)
- Tests: 1- (pattern replacement + verification)
- Scripts/utils:  (simple updates)
- **Total: 3.5-**

---

## Next Steps

1. **Clarify replacement API** — What is the official replacement for `SOVEREIGN_TERRITORIES`?
2. **Create migration guide** — Document old→new patterns
3. **Prioritize core files** — Start with `derived.py`, `_verify.py`, `ssot.py`
4. **Update tests incrementally** — Fix tests as core files are updated
5. **Run full test suite** — Verify no regressions

---

## Questions for User

1. What is the official replacement for `SOVEREIGN_TERRITORIES`?
2. Is `PROJECT_ROOT_WHITELIST` the new API, or is there a different pattern?
3. Should we maintain backward compatibility with a deprecation warning, or do a hard cutover?
4. Which files are highest priority for immediate refactoring?

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

