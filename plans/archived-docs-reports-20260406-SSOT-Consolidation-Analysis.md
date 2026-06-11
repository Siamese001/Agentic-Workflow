---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\20260406-SSOT-Consolidation-Analysis.md'
original_relative_path: '20260406-SSOT-Consolidation-Analysis.md'
source_sha256: 91aa829309184d7222e6371d96a461b28d079a957a252149fa08d5c8264c38f8
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# SSOT Consolidation Analysis Report

**Date:** 2026-04-06  
**ADG Snapshot:** 04062026_0445 (87,503 nodes, 623,027 edges)  
**Analysis Scope:** Structure Blueprint Configuration Drift

---

## EXECUTIVE SUMMARY

Identified significant SSOT (Single Source of Truth) drift between YAML configuration files and Python hardcoded data in the structure_blueprint module. The YAML files in `config/structure_blueprint/` are intended as the SSOT, but extensive hardcoded data exists in `agentic_core/L5_safety/config/structure_blueprint/_constants.py`, creating maintenance burden and drift risk.

**Key Finding:** ~1,400 lines of hardcoded structural data in Python duplicates YAML SSOT, making file/folder SSOT updates overly complicated.

---

## CURRENT STATE

### YAML SSOT (Intended Single Source)

**Location:** `config/structure_blueprint/`

1. **`layers.yaml`** (95 lines)
   - Layer-specific template overrides (L0-L6)
   - Purpose statements, routing rules, forbidden capabilities
   - Extra subfolders definitions

2. **`territories.yaml`** (495 lines)
   - Territory definitions for all project roots
   - Depth, purpose, subfolders structure
   - Wildcard patterns for apps_*

3. **`yaml_loader.py`** (86 lines)
   - Loads YAML files from config directory
   - Provides API: `load_territories()`, `load_layer_overrides()`, `get_territory()`, `get_layer_override()`
   - Cached loader with simple interface

### Python Hardcoded Data (Drift Source)

**Location:** `agentic_core/L5_safety/config/structure_blueprint/_constants.py` (1,845 lines)

1. **LAYER_OVERRIDES** (Lines 118-531, ~413 lines)
   - Hardcoded layer definitions duplicating `layers.yaml`
   - Includes purpose, notes, routing rules, extra subfolders
   - Builder functions: `_build_lcd_subfolders_template()`, `_build_layer_definition()`

2. **build_sovereign_territories()** (Lines 603-1618, ~1,015 lines)
   - **MARKED DEPRECATED** but still present and used internally
   - Hardcoded territory definitions duplicating `territories.yaml`
   - Builds agentic_core structure with all layers
   - Contains AST signals (lines 817-897)
   - Returns SOVEREIGN_TERRITORIES dict

3. **SOVEREIGN_TERRITORIES** (Materialized at import time)
   - Result of build_sovereign_territories()
   - Deprecated but still imported by territories.py
   - Used by new API functions get_territory_metadata(), get_all_territories()

4. **Type Definitions** (Lines 51-79)
   - SubfolderDefinition TypedDict
   - TerritoryDefinition TypedDict
   - **These should remain** (pure types, no data)

5. **Utility Functions** (Lines 1618+)
   - _deep_freeze() helper
   - **These should remain** (pure utilities)

### Backward Compatibility Shim

**Location:** `agentic_core/L5_safety/config/structure_blueprint_config.py` (175 lines)

- Re-exports entire public API from modular package
- Contains unrelated constants (MAX_RETRIES, DEFAULT_SLEEP, THRESHOLD, etc.)
- 18 explicit backward-compat re-exports
- Mirrors package `__all__` (163 names)

---

## CONSOLIDATION OPPORTUNITIES

### Priority 1: Eliminate Hardcoded LAYER_OVERRIDES

**Current State:**
- Lines 118-531 in `_constants.py` (~413 lines)
- Duplicates data from `config/structure_blueprint/layers.yaml`
- Builder functions `_build_lcd_subfolders_template()`, `_build_layer_definition()`

**Proposed Consolidation:**
1. Remove LAYER_OVERRIDES dict from `_constants.py`
2. Remove `_build_lcd_subfolders_template()` and `_build_layer_definition()` functions
3. Update all consumers to use `yaml_loader.load_layer_overrides()` instead
4. Update territories.py to load from YAML instead of importing LAYER_OVERRIDES

**Impact Analysis:**
- **Files to update:** 1 test file uses LAYER_OVERRIDES directly
  - `tests/unit/agentic_core/L0_routing/core/test_l0_routing_override.py`
- **Risk:** Low - test is checking invariant, can be updated to use YAML loader
- **Lines removed:** ~413 lines
- **Complexity reduction:** Eliminates duplicate data source

### Priority 2: Eliminate build_sovereign_territories()

**Current State:**
- Lines 603-1618 in `_constants.py` (~1,015 lines)
- **MARKED DEPRECATED** but still used by territories.py
- Duplicates data from `config/structure_blueprint/territories.yaml`
- Contains hardcoded AST signals (lines 817-897)

**Proposed Consolidation:**
1. Remove build_sovereign_territories() function from `_constants.py`
2. Remove SOVEREIGN_TERRITORIES materialization
3. Create new `territories_loader.py` module that:
   - Loads from `territories.yaml` via yaml_loader
   - Applies layer definitions from `layers.yaml`
   - Builds complete territory structure dynamically
   - Returns immutable Mapping (same API as get_all_territories())
4. Update territories.py to use new loader instead of importing from _constants

**Impact Analysis:**
- **Files to update:** 
  - `tools/migrate/_migrate_test_files_phase4.py` (migration script, can be deleted after migration)
  - `tests/unit_min_deps/test_leaf_domain_contract.py` (uses build_sovereign_territories)
- **Risk:** Medium - requires careful migration of territory building logic
- **Lines removed:** ~1,015 lines
- **Complexity reduction:** Eliminates deprecated code path, true SSOT in YAML

### Priority 3: Extract AST Signals to YAML

**Current State:**
- Lines 817-897 in build_sovereign_territories() (~80 lines)
- Hardcoded AST signal definitions for various paths
- Class patterns, base classes, keyword signals, weights

**Proposed Consolidation:**
1. Create `config/structure_blueprint/ast_signals.yaml`
2. Extract all AST signal definitions to YAML format
3. Add `load_ast_signals()` function to yaml_loader.py
4. Update territory loader to merge AST signals from YAML

**Impact Analysis:**
- **Risk:** Low - pure data extraction
- **Lines moved:** ~80 lines from Python to YAML
- **Maintainability:** Easier to update AST signals without code changes

### Priority 4: Consolidate Unrelated Constants

**Current State:**
- Lines 41-48 in `structure_blueprint_config.py`:
  ```python
  MAX_RETRIES = 3
  DEFAULT_SLEEP = 1.0
  THRESHOLD = 0.95
  BUFFER_SIZE = 8192
  BATCH_SIZE = 32
  MAX_DEPTH = 6
  MAX_FILES = 1000
  DEFAULT_TIMEOUT = 300
  ```

**Proposed Consolidation:**
1. These constants are already imported from `agentic_core.L0_routing.config.path_constants` (see __init__.py lines 20-29)
2. Remove duplicate definitions from structure_blueprint_config.py
3. Keep only re-export statements

**Impact Analysis:**
- **Risk:** None - duplicates of existing constants
- **Lines removed:** 8 lines
- **Clarity:** Removes confusion about source of truth

### Priority 5: Simplify _constants.py

**Current State:**
- 1,845 lines total (after Priority 1 & 2: ~417 lines remaining)
- Contains types, utilities, and some operational config constants

**Proposed Consolidation:**
1. **Keep in _constants.py:**
   - Type definitions (SubfolderDefinition, TerritoryDefinition)
   - Pure utility functions (_deep_freeze)
   - Operational config constants (GRAVITY_CONFIG, HEALING_CONFIG, MISSION_CONFIG, MCP_CAPABILITIES, AGENT_RESILIENCE_CONFIG)
   - Root lists (UPSTREAM_SOVEREIGN_ROOTS, DOWNSTREAM_ROOTS)

2. **Evaluate for YAML migration:**
   - GRAVITY_CONFIG, HEALING_CONFIG, MISSION_CONFIG, MCP_CAPABILITIES, AGENT_RESILIENCE_CONFIG
   - If these are structural data, move to YAML
   - If these are runtime configuration, keep in Python

3. **Rename file:** Consider renaming to `types.py` or `operational_config.py` to reflect actual content

**Impact Analysis:**
- **Risk:** Low - clarification only
- **Lines reduced:** From 1,845 to ~200-400 lines (depending on operational config decision)

---

## DEPENDENCY GRAPH ANALYSIS

### Import Chain (Current)

```
structure_blueprint_config.py (shim)
  └─> structure_blueprint package __init__.py
        ├─> _constants.py (hardcoded LAYER_OVERRIDES, SOVEREIGN_TERRITORIES)
        ├─> yaml_loader.py (loads YAML, but unused for core data)
        ├─> territories.py (imports SOVEREIGN_TERRITORIES from _constants)
        ├─> ssot.py (imports ROOT_WHITELIST from _constants)
        └─> derived.py (computes from territories)
```

### Import Chain (Proposed)

```
structure_blueprint_config.py (shim)
  └─> structure_blueprint package __init__.py
        ├─> types.py (renamed _constants.py, only types + operational config)
        ├─> yaml_loader.py (SSOT for all structural data)
        ├─> territories_loader.py (NEW: builds territories from YAML)
        ├─> territories.py (uses territories_loader)
        ├─> ssot.py (imports from territories_loader)
        └─> derived.py (computes from territories)
```

---

## MIGRATION PLAN

### Phase 1: Eliminate LAYER_OVERRIDES Hardcoding (Low Risk)

1. Update `yaml_loader.py` to add `get_layer_overrides_dict()` helper
2. Update `territories.py` to load layer overrides from YAML instead of _constants
3. Update test file `test_l0_routing_override.py` to use YAML loader
4. Remove LAYER_OVERRIDES and builder functions from `_constants.py`
5. Run tests to verify

**Estimated effort:** 2-3 hours

### Phase 2: Extract AST Signals to YAML (Low Risk)

1. Create `config/structure_blueprint/ast_signals.yaml`
2. Extract AST signal data from build_sovereign_territories()
3. Add `load_ast_signals()` to yaml_loader.py
4. Update territory building logic to load from YAML
5. Run tests to verify

**Estimated effort:** 1-2 hours

### Phase 3: Eliminate build_sovereign_territories() (Medium Risk)

1. Create `territories_loader.py` module
2. Implement territory building logic using YAML loader
3. Update territories.py to use new loader
4. Update test file `test_leaf_domain_contract.py`
5. Delete migration script `_migrate_test_files_phase4.py`
6. Remove build_sovereign_territories() and SOVEREIGN_TERRITORIES from _constants.py
7. Run full test suite

**Estimated effort:** 4-6 hours

### Phase 4: Clean Up Shim (Low Risk)

1. Remove duplicate constants from structure_blueprint_config.py
2. Verify all imports still work
3. Run backward compatibility tests

**Estimated effort:** 30 minutes

### Phase 5: Rename and Simplify (Low Risk)

1. Evaluate operational config constants for YAML migration
2. Rename _constants.py to types.py or operational_config.py
3. Update all imports
4. Update documentation

**Estimated effort:** 1-2 hours

**Total estimated effort:** 8-13 hours

---

## RISK ASSESSMENT

### Low Risk Items
- Priority 1: LAYER_OVERRIDES elimination (1 test file affected)
- Priority 3: AST signals extraction (pure data move)
- Priority 4: Duplicate constants removal (no functional change)
- Priority 5: File rename (mechanical change)

### Medium Risk Items
- Priority 2: build_sovereign_territories() elimination (core data path, deprecated but used)

### Risk Mitigation
1. Run full test suite after each phase
2. Keep backward compatibility shim intact
3. Use feature flags if needed for gradual rollout
4. Document migration path for external consumers

---

## BENEFITS

### Maintainability
- **Single source of truth** in YAML files
- **Easier updates** to structure blueprint (edit YAML, no Python changes)
- **Reduced codebase** (~1,400 lines removed)
- **Clearer separation** between types, data, and logic

### Drift Elimination
- **No duplicate data** between YAML and Python
- **File/folder updates** become simple YAML edits
- **Reduced cognitive load** (one place to look for structure)

### Operational
- **Faster iteration** on structural changes
- **Non-developers** can update structure via YAML
- **Better tooling** potential (YAML validators, editors)
- **Easier auditing** (git diff on YAML is cleaner)

---

## FACT_CLASSIFICATION

### DIRECTLY_OBSERVED
- ADG health check: healthy (87,503 nodes, 623,027 edges)
- File sizes: _constants.py (1,845 lines), layers.yaml (95 lines), territories.yaml (495 lines)
- Code patterns: LAYER_OVERRIDES (lines 118-531), build_sovereign_territories() (lines 603-1618)
- Import patterns: 1 test uses LAYER_OVERRIDES, migration script references SOVEREIGN_TERRITORIES
- Deprecation warnings: build_sovereign_territories() marked deprecated

### DERIVED
- Lines of hardcoded data: ~1,400 lines (413 + 1,015 + ~80 AST signals)
- Consolidation potential: 75% reduction in _constants.py size
- Migration complexity: Medium (5 phases, 8-13 hours estimated)
- Risk profile: Low-Medium (most changes are low risk, one medium risk item)

### INFERRED
- Current state makes file/folder SSOT updates complicated (user stated)
- YAML files are intended as SSOT (based on yaml_loader.py existence)
- Migration to YAML-based SSOT is in progress but incomplete (deprecated functions still present)

### EXTERNAL
- User request: "too complicated to make file folder SSOT updates"
- User files mentioned: _constants.py, structure_blueprint_config.py

### ASSUMED
- Operational config constants (GRAVITY_CONFIG, etc.) may need YAML migration
- No external consumers depend on internal _constants module (only through public API)

### UNRESOLVED
- Operational config constants location decision (Python vs YAML)
- External consumer impact analysis (if any)
- AST signals usage patterns beyond territory building

---

## ARTIFACTS

**Generated Files:**
- `docs/reports/plans/20260406-SSOT-Consolidation-Analysis.md` (this report)

**Analyzed Files:**
- `config/structure_blueprint/layers.yaml`
- `config/structure_blueprint/territories.yaml`
- `agentic_core/L5_safety/config/structure_blueprint/_constants.py`
- `agentic_core/L5_safety/config/structure_blueprint_config.py`
- `agentic_core/L5_safety/config/structure_blueprint/yaml_loader.py`
- `agentic_core/L5_safety/config/structure_blueprint/territories.py`
- `agentic_core/L5_safety/config/structure_blueprint/ssot.py`
- `agentic_core/L5_safety/config/structure_blueprint/__init__.py`

**Test Files Referenced:**
- `tests/unit/agentic_core/L0_routing/core/test_l0_routing_override.py`
- `tests/unit_min_deps/test_leaf_domain_contract.py`
- `tests/unit/agentic_core/L5_safety/config/structure_blueprint/test_yaml_loader.py`

**Migration Scripts Referenced:**
- `tools/migrate/_migrate_test_files_phase4.py`

---

## RECOMMENDATIONS

### Immediate Actions
1. **Approve migration plan** - Review and prioritize consolidation phases
2. **Create feature branch** - Isolate migration work
3. **Execute Phase 1** - Start with low-risk LAYER_OVERRIDES elimination

### Long-term Actions
1. **Complete all 5 phases** - Full SSOT consolidation
2. **Add CI validation** - Ensure YAML remains in sync with Python
3. **Document YAML schema** - Make it easier for non-developers to edit
4. **Consider YAML validation tools** - Pre-commit hooks for schema validation

### Success Criteria
- All structural data flows through YAML files
- Python code contains only types, utilities, and runtime config
- File/folder SSOT updates require only YAML edits
- Test suite passes after migration
- No backward compatibility breaks (shim still works)

---

## UNRESOLVED

None identified - all gaps noted in FACT_CLASSIFICATION section.
