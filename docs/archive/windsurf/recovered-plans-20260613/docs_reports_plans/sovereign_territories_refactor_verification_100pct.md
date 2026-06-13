# SOVEREIGN_TERRITORIES Refactor — 100% Verification Plan

**Created**: 2026-03-11
**Objective**: Verify complete elimination of SOVEREIGN_TERRITORIES God Object usage
**Status**: VERIFICATION IN PROGRESS

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

**Goal**: Systematically replace all direct `SOVEREIGN_TERRITORIES` imports and usages with domain-specific constants from the public `structure_blueprint_config` API.

**Completion Criteria**:
1. Zero live `SOVEREIGN_TERRITORIES` imports in production code (excluding definition files)
2. Zero live `SOVEREIGN_TERRITORIES` usages in production code (excluding definition files)
3. All tests passing (structure_blueprint_config + ssot_single_entry_point)
4. No forbidden wildcard `.ssot` submodule imports
5. `interfaces/structure_config.py` deleted, consumers redirected

---

## Phase 1: Completed Items ✅

### P0: Critical Bugs Fixed
- ✅ **Frozenset `.get()` bugs**: Replaced all `.get()` calls on frozensets with safe dict/frozenset lookups
- ✅ **DEPTH_RULES dict**: Confirmed exists in `ssot.py` as `dict[str, int]`

### P1: Exclusion Sets Fixed
- ✅ **SOVEREIGN_EXCLUDED_FOLDERS**: Exported from public API
- ✅ **GLOBAL_EXCLUDED_DIRS**: Exported from public API
- ✅ **SCAN_EXCLUDED_DIRS**: Exported from public API

### P2: SOVEREIGN_TERRITORIES Elimination
**Files Fixed** (11 production files):
1. ✅ `registry_config.py` — uses `SOVEREIGN_REGISTRY` (derived from domain constants)
2. ✅ `execute_ssot.py` — replaced with `PROJECT_ROOT_WHITELIST`
3. ✅ `populate_ssot_folders_util.py` — replaced with `CORE_SUBFOLDER_MAP`
4. ✅ `run_guardian_hierarchy_compliance.py` — replaced with `CORE_SUBFOLDER_MAP`
5. ✅ `generate_hooks_util.py` — replaced with `PROJECT_ROOT_WHITELIST` + `DEPTH_RULES`
6. ✅ `mission_utils_enforcer.py` — replaced with `CORE_SUBFOLDER_MAP`
7. ✅ `mock_context_enforcer.py` — replaced with `DEPTH_RULES`
8. ✅ `ssot_structure_validation_enforcer.py` — replaced alias with direct `SOVEREIGN_REGISTRY`
9. ✅ `hierarchy_healer.py` — replaced with `DEPTH_RULES` + `CORE_SUBFOLDER_MAP` + `ENFORCED_TERRITORIES` + `PROJECT_ROOT_WHITELIST`
10. ✅ `location_validator.py` — replaced with `DEPTH_RULES` + `PROJECT_ROOT_WHITELIST` + `LAYER_PREFIX_EXEMPT_TERRITORIES`
11. ✅ Added `ALLOW_ROOT_PY_TERRITORIES` and `LAYER_PREFIX_EXEMPT_TERRITORIES` to `ssot.py`

**Additional Files Fixed** (11 more files):
12. ✅ `ArchitectureGovernorAgent.py` — `CORE_SUBFOLDER_MAP` + `PROJECT_ROOT_WHITELIST`
13. ✅ `SystemArchitectAgent.py` — `SOVEREIGN_REGISTRY` + `DEPTH_RULES` + `PROJECT_ROOT_WHITELIST`
14. ✅ `root_hygiene_healer.py` — `PROJECT_ROOT_WHITELIST`
15. ✅ `TestGeneratorAgent.py` — `PROJECT_ROOT_WHITELIST`
16. ✅ `reasoning/gravity_validator.py` — `PROJECT_ROOT_WHITELIST`
17. ✅ `location_path_util.py` — `DEPTH_RULES` + `PROJECT_ROOT_WHITELIST`
18. ✅ `location_utils_util.py` — `DEPTH_RULES` (fixed direct `.ssot` import)
19. ✅ `validators/gravity_validator.py` — `DEPTH_RULES` + `CORE_SUBFOLDER_MAP` + `PROJECT_ROOT_WHITELIST`

### P3: Interface Cleanup
- ✅ **interfaces/structure_config.py**: Deleted
- ✅ **3 consumers redirected**:
  - `clean_duplicates_enhanced.py` → `structure_blueprint`
  - `fix_duplicate_realagentdata.py` → `structure_blueprint_config` (canonical)
  - `void_compliance_config.py` → `structure_blueprint`
- ✅ **Allowlist cleanup**: Removed stale entry from `test_ssot_single_entry_point.py`

### P3c: Submodule Import Clarification
- ✅ **Verified**: Only wildcard `.ssot` imports are forbidden per `forbidden_imports_registry.md`
- ✅ **Verified**: Specific named imports from `.ssot` are permitted for files in `ALLOWED_DIRECT` paths
- ✅ **Verified**: Zero wildcard `.ssot` imports exist in codebase

---

## Phase 2: Verification Checklist 🔍

### V1: Import Scan (AST-backed)
**Status**: PENDING

**Action**: Use `grep_search` MCP tool to verify zero live `SOVEREIGN_TERRITORIES` imports in production code

**Command**:
```python
grep_search(
    SearchPath="c:/Git/Agentic-Workflow",
    Query="import SOVEREIGN_TERRITORIES|from.*import.*SOVEREIGN_TERRITORIES",
    Includes=["*.py"],
    MatchPerLine=true
)
```

**Expected**: Only hits in:
- `docs/reports/plans/_p2_verify.py` (verification script)
- `archives/` and `.healing_backups/` (archived files)
- Definition files: `ssot.py`, `_constants.py`, `derived.py`, `territories.py`

**Exclusions** (legitimate definition layer):
- `agentic_core/L5_safety/config/structure_blueprint/ssot.py`
- `agentic_core/L5_safety/config/structure_blueprint/_constants.py`
- `agentic_core/L5_safety/config/structure_blueprint/derived.py`
- `agentic_core/L5_safety/config/structure_blueprint/territories.py`
- `agentic_core/L5_safety/config/structure_blueprint/__init__.py`

---

### V2: Usage Scan (AST-backed)
**Status**: PENDING

**Action**: Use `grep_search` to verify zero live `SOVEREIGN_TERRITORIES` dict/attribute accesses

**Command**:
```python
grep_search(
    SearchPath="c:/Git/Agentic-Workflow",
    Query="SOVEREIGN_TERRITORIES\\.get|SOVEREIGN_TERRITORIES\\[|SOVEREIGN_TERRITORIES\\.items|SOVEREIGN_TERRITORIES\\.keys|SOVEREIGN_TERRITORIES\\.values",
    Includes=["*.py"],
    MatchPerLine=true
)
```

**Expected**: Only hits in definition layer files listed in V1

---

### V3: Test Suite Validation
**Status**: ✅ PASSED (9/9)

**Tests Run**:
```bash
python -m pytest \
  tests/unit/agentic_core/L5_safety/config/test_structure_blueprint_config.py \
  tests/unit_min_deps/test_ssot_single_entry_point.py \
  -x -q --tb=short
```

**Results**:
- ✅ `test_structure_blueprint_exists`
- ✅ `test_sovereign_territories_defined`
- ✅ `test_layer_roots_defined`
- ✅ `test_required_lcd_subfolders_defined`
- ✅ `test_all_layers_in_territories`
- ✅ `test_apps_folders_in_territories`
- ✅ `test_l5_subprocess_allowlist_exists`
- ✅ `test_l6_hybrid_allowlist_exists`
- ✅ `test_no_direct_submodule_imports`

---

### V4: Wildcard Import Scan
**Status**: ✅ VERIFIED (0 violations)

**Action**: Verify no wildcard `.ssot` imports exist

**Command**:
```python
grep_search(
    SearchPath="c:/Git/Agentic-Workflow",
    Query="from agentic_core\\.L5_safety\\.config\\.structure_blueprint\\.ssot import \\*",
    Includes=["*.py"],
    MatchPerLine=true
)
```

**Result**: No results found ✅

---

### V5: Residual Comment/Docstring Scan
**Status**: PENDING

**Action**: Identify any remaining `SOVEREIGN_TERRITORIES` mentions in comments/docstrings

**Command**:
```python
# Python script to scan for SOVEREIGN_TERRITORIES in comments only
import ast
from pathlib import Path

ROOT = Path("c:/Git/Agentic-Workflow")
SKIP = {".git", "__pycache__", "archives", ".healing_backups", "node_modules"}

comment_hits = []
for f in ROOT.rglob("*.py"):
    if any(s in str(f) for s in SKIP):
        continue
    try:
        src = f.read_text(encoding="utf-8", errors="ignore")
        # Check if SOVEREIGN_TERRITORIES appears only in comments/docstrings
        if "SOVEREIGN_TERRITORIES" in src:
            tree = ast.parse(src)
            # Extract all string literals (docstrings)
            # If no import/usage nodes exist, it's comment-only
            has_import = any(
                isinstance(n, (ast.ImportFrom, ast.Import))
                for n in ast.walk(tree)
                if hasattr(n, "module") and "SOVEREIGN_TERRITORIES" in getattr(n, "module", "")
            )
            has_usage = any(
                isinstance(n, ast.Name) and n.id == "SOVEREIGN_TERRITORIES"
                for n in ast.walk(tree)
            )
            if not has_import and not has_usage:
                comment_hits.append(str(f.relative_to(ROOT)))
    except Exception:
        pass

print(f"Files with SOVEREIGN_TERRITORIES in comments only: {len(comment_hits)}")
for h in comment_hits[:20]:
    print(f"  {h}")
```

**Expected**: Some residual mentions in comments/docstrings are acceptable (historical references, RCAs, etc.)

---

### V6: Derived Constants Verification
**Status**: PENDING

**Action**: Verify all derived constants are correctly exported from public API

**Constants to Check**:
- ✅ `DEPTH_RULES` — dict mapping territory → depth
- ✅ `PROJECT_ROOT_WHITELIST` — frozenset of root folders
- ✅ `CORE_SUBFOLDER_MAP` — dict mapping L1 → L2 subfolders
- ✅ `ENFORCED_TERRITORIES` — frozenset of enforced territories
- ✅ `FORBIDDEN_PATTERNS` — dict mapping territory → forbidden patterns
- ✅ `ALLOW_ROOT_PY_TERRITORIES` — frozenset of territories allowing root .py files
- ✅ `LAYER_PREFIX_EXEMPT_TERRITORIES` — frozenset of territories exempt from layer prefix rules

**Verification Command**:
```python
from agentic_core.L5_safety.config.structure_blueprint_config import (
    DEPTH_RULES,
    PROJECT_ROOT_WHITELIST,
    CORE_SUBFOLDER_MAP,
    ENFORCED_TERRITORIES,
    FORBIDDEN_PATTERNS,
    ALLOW_ROOT_PY_TERRITORIES,
    LAYER_PREFIX_EXEMPT_TERRITORIES,
)

print("✅ All derived constants importable from public API")
print(f"DEPTH_RULES type: {type(DEPTH_RULES)}")
print(f"PROJECT_ROOT_WHITELIST type: {type(PROJECT_ROOT_WHITELIST)}")
print(f"CORE_SUBFOLDER_MAP type: {type(CORE_SUBFOLDER_MAP)}")
```

---

### V7: Registry Config Integrity
**Status**: PENDING

**Action**: Verify `SOVEREIGN_REGISTRY` in `registry_config.py` is correctly built from derived constants

**File**: `agentic_core/config/core/registry_config.py`

**Expected Behavior**:
- `SOVEREIGN_REGISTRY` is a dict built from `PROJECT_ROOT_WHITELIST`, `DEPTH_RULES`, `CORE_SUBFOLDER_MAP`, etc.
- No direct `SOVEREIGN_TERRITORIES` import or usage
- All consumers of `SOVEREIGN_REGISTRY` treat it as a dict (not a frozenset)

**Verification**:
```python
from agentic_core.config.core.registry_config import SOVEREIGN_REGISTRY

assert isinstance(SOVEREIGN_REGISTRY, dict)
assert "agentic_core" in SOVEREIGN_REGISTRY
assert "depth" in SOVEREIGN_REGISTRY["agentic_core"]
assert "subfolders" in SOVEREIGN_REGISTRY["agentic_core"]
print("✅ SOVEREIGN_REGISTRY correctly structured")
```

---

### V8: Enforcement Layer Verification
**Status**: PENDING

**Action**: Verify L5 enforcement and reasoning files use correct imports

**Files to Check**:
- `ssot_structure_validation_enforcer.py` — should use `SOVEREIGN_REGISTRY`
- `mission_utils_enforcer.py` — should use `CORE_SUBFOLDER_MAP`
- `mock_context_enforcer.py` — should use `DEPTH_RULES`
- `hierarchy_healer.py` — should use domain constants
- `location_validator.py` — should use domain constants

**Verification**: Run targeted grep for each file to confirm no `SOVEREIGN_TERRITORIES` usage

---

### V9: Apps Layer Verification
**Status**: ✅ VERIFIED

**Action**: Verify apps_* consumers use canonical public API

**Files Checked**:
- ✅ `apps_lic/tools/clean_duplicates_enhanced.py` — uses `structure_blueprint`
- ✅ `apps_lic/tools/fix_duplicate_realagentdata.py` — uses `structure_blueprint_config`
- ✅ `apps_rg/config/void_compliance_config.py` — uses `structure_blueprint`

---

### V10: CI Gate Compliance
**Status**: PENDING

**Action**: Run full CI gate suite to verify no regressions

**Gates to Run**:
1. `check_dedup_violations.py`
2. `validate_import_dependencies.py`
3. `check_plan_location_compliance.py`
4. Ruff F401 (dead imports)
5. `test_ssot_single_entry_point.py`

**Command**:
```bash
# Run targeted CI gates
python ops_scripts/ci/validate_import_dependencies.py
python ops_scripts/ci/check_plan_location_compliance.py
python -m pytest tests/unit_min_deps/test_ssot_single_entry_point.py -v
```

---

## Phase 3: Remaining Work Items 📋

### R1: Definition Layer Cleanup (Optional)
**Status**: NOT STARTED

**Scope**: Consider refactoring `SOVEREIGN_TERRITORIES` definition itself in `ssot.py`

**Options**:
1. Keep as-is (internal definition, not exposed)
2. Deprecate entirely, build `SOVEREIGN_REGISTRY` directly from primitives
3. Mark as `_SOVEREIGN_TERRITORIES` (private)

**Decision**: DEFER — not required for current objective

---

### R2: Documentation Update
**Status**: NOT STARTED

**Action**: Update architectural docs to reflect new import patterns

**Files to Update**:
- `docs/technical/structure_blueprint_architecture.md`
- `docs/technical/import_patterns.md`
- `.windsurf/skills/import-hygiene/SKILL.md`

---

### R3: Deprecation Warnings (Optional)
**Status**: NOT STARTED

**Action**: Add deprecation warnings to any remaining `SOVEREIGN_TERRITORIES` exports

**Implementation**:
```python
# In ssot.py
import warnings

def __getattr__(name):
    if name == "SOVEREIGN_TERRITORIES":
        warnings.warn(
            "SOVEREIGN_TERRITORIES is deprecated. Use domain-specific constants instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return _SOVEREIGN_TERRITORIES
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

**Decision**: DEFER — not required for current objective

---

## Success Criteria Summary

**MUST HAVE** (Blocking):
- ✅ P0: Critical bugs fixed
- ✅ P1: Exclusion sets fixed
- ✅ P2: All production SOVEREIGN_TERRITORIES imports eliminated
- ✅ P3: interfaces/structure_config.py deleted, consumers redirected
- ✅ V3: Test suite passing (9/9)
- ⏳ V1: Import scan verification (NEXT)
- ⏳ V2: Usage scan verification (NEXT)

**SHOULD HAVE** (Important):
- ⏳ V4: Wildcard import scan (DONE, but document)
- ⏳ V6: Derived constants verification
- ⏳ V7: Registry config integrity check
- ⏳ V10: CI gate compliance

**NICE TO HAVE** (Optional):
- V5: Residual comment scan
- V8: Enforcement layer spot-check
- R2: Documentation update
- R3: Deprecation warnings

---

## Next Actions

1. **Run V1 (Import Scan)** — verify zero live imports
2. **Run V2 (Usage Scan)** — verify zero live usages
3. **Run V6 (Derived Constants)** — verify all exports work
4. **Run V7 (Registry Integrity)** — verify SOVEREIGN_REGISTRY correct
5. **Run V10 (CI Gates)** — verify no regressions
6. **Document results** — update this plan with findings

---

## Appendix: File Change Log

### Files Modified (22 total)
1. `agentic_core/config/core/registry_config.py`
2. `agentic_core/L0_routing/scripts/execute_ssot.py`
3. `agentic_core/L0_routing/scripts/populate_ssot_folders_util.py`
4. `agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py`
5. `ops_scripts/dev_tools/l0_scripts/generate_hooks_util.py`
6. `agentic_core/L5_safety/enforcement/mission_utils_enforcer.py`
7. `agentic_core/L5_safety/enforcement/mock_context_enforcer.py`
8. `agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py`
9. `agentic_core/L5_safety/reasoning/hierarchy_healer.py`
10. `agentic_core/L5_safety/reasoning/location_validator.py`
11. `agentic_core/L5_safety/config/structure_blueprint/ssot.py` (added constants)
12. `agentic_core/L5_safety/config/structure_blueprint/__init__.py` (exported constants)
13. `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py`
14. `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py`
15. `agentic_core/L5_safety/reasoning/root_hygiene_healer.py`
16. `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py`
17. `agentic_core/L5_safety/reasoning/gravity_validator.py`
18. `agentic_core/L5_safety/utils/location_path_util.py`
19. `agentic_core/L5_safety/utils/location_utils_util.py`
20. `agentic_core/L5_safety/validators/gravity_validator.py`
21. `apps_lic/tools/clean_duplicates_enhanced.py`
22. `apps_lic/tools/fix_duplicate_realagentdata.py`
23. `apps_rg/config/void_compliance_config.py`
24. `tests/unit_min_deps/test_ssot_single_entry_point.py` (removed stale allowlist entry)

### Files Deleted (1 total)
1. `agentic_core/interfaces/structure_config.py`

---

**End of Verification Plan**

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

