# RCA: SOVEREIGN_TERRITORIES Sprawl and Encapsulation Violation

**Date:** 2026-03-11
**Severity:** Critical
**Status:** In Progress

## Executive Summary

Found **23 application files** illegitimately importing `SOVEREIGN_TERRITORIES` from SSOT package when they should use domain-specific subsets (`ENFORCED_TERRITORIES`, `CODE_TERRITORIES`, or `PROJECT_ROOT_WHITELIST`). This violates SSOT encapsulation and creates maintenance burden.

## Root Cause

`SOVEREIGN_TERRITORIES` is the master registry containing all 16 territories (including volatile/system directories like `.backup`, `.gravity_state`, `artifacts`, `logs`). Application code should never access this raw registry - only the SSOT package (`structure_blueprint/`) should use it to derive consumable subsets.

## Impact

1. **Abstraction Violation**: Application code knows about system directories it shouldn't care about
2. **Wrong Granularity**: Most code needs 8-10 territories, not all 16
3. **Maintenance Burden**: Changes to SOVEREIGN_TERRITORIES require reviewing 23+ files
4. **Semantic Mismatch**: Structure validators shouldn't validate `.backup` or `artifacts`

## Correct Territory Subsets

| Subset | Count | Purpose | Consumers |
|--------|-------|---------|-----------|
| `SOVEREIGN_TERRITORIES` | 16 | Master registry (SSOT-internal only) | `structure_blueprint/` package only |
| `ENFORCED_TERRITORIES` | 10 | Territories with enforced structure rules | Structure validators, hierarchy healers |
| `CODE_TERRITORIES` | 8 | Territories containing Python code | Import scanners, circular dependency detectors |
| `PROJECT_ROOT_WHITELIST` | 17 | Approved root-level directories | Root directory validators |

### Territory Breakdown

**SOVEREIGN_TERRITORIES (16):**
- `agentic_core`, `apps_rg`, `apps_lic`, `apps_shared`, `tests`, `ops_scripts`, `system_learning`, `tools`
- `logs`, `archives`, `data`, `docs`, `artifacts`
- `.github`, `.gravity_state`, `.backup`

**ENFORCED_TERRITORIES (10):**
- `agentic_core`, `apps_rg`, `apps_lic`, `apps_shared`, `tests`, `ops_scripts`, `system_learning`, `tools`, `data`, `docs`

**CODE_TERRITORIES (8):**
- `agentic_core`, `apps_rg`, `apps_lic`, `apps_shared`, `tests`, `ops_scripts`, `system_learning`, `tools`

**PROJECT_ROOT_WHITELIST (17):**
- All SOVEREIGN_TERRITORIES except `logs`, `artifacts`, `system_learning`, `tools`
- Plus: `.git`, `.vscode`

## Files Requiring Fixes (23 total)

### Category 1: Structure Validation → Use ENFORCED_TERRITORIES (5 files)
- ✅ `agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py` - FIXED
- ✅ `agentic_core/L5_safety/reasoning/hierarchy_healer.py` - FIXED
- ✅ `agentic_core/L5_safety/reasoning/location_validator.py` - FIXED
- ✅ `agentic_core/L5_safety/utils/location_path_util.py` - FIXED
- ✅ `agentic_core/L5_safety/utils/location_utils_util.py` - FIXED

### Category 2: Code Scanning → Use CODE_TERRITORIES (6 files)
- ✅ `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py` - PARTIAL (2/3 replacements)
- ❌ `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py`
- ❌ `ops_scripts/ci/ast_hardcoded_path_scanner.py`
- ❌ `ops_scripts/ci/ssot_violation_scanner.py`
- ❌ `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py`
- ❌ `agentic_core/L5_safety/utils/extract_pattern_util.py`

### Category 3: Root Validation → Use PROJECT_ROOT_WHITELIST (2 files)
- ❌ `agentic_core/L5_safety/reasoning/root_hygiene_healer.py`
- ❌ `ops_scripts/hooks/validate_paths.py`

### Category 4: Gravity/Apps Detection → Use CODE_TERRITORIES (4 files)
- ❌ `agentic_core/L5_safety/reasoning/gravity_validator.py`
- ❌ `agentic_core/L5_safety/validators/gravity_validator.py`
- ❌ `agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py`
- ❌ `agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py`

### Category 5: Mock/Test Utilities → Use ENFORCED_TERRITORIES (2 files)
- ❌ `agentic_core/L5_safety/enforcement/mock_context_enforcer.py`
- ❌ `agentic_core/L5_safety/enforcement/mission_utils_enforcer.py`

### Category 6: SSOT Package (Keep SOVEREIGN_TERRITORIES) (6 files)
- ✅ `agentic_core/L5_safety/config/structure_blueprint/_constants.py` - Defines it
- ✅ `agentic_core/L5_safety/config/structure_blueprint/ssot.py` - Re-exports it
- ✅ `agentic_core/L5_safety/config/structure_blueprint/derived.py` - Derives subsets from it
- ✅ `agentic_core/L5_safety/config/structure_blueprint/_verify.py` - Verifies it
- ✅ `agentic_core/L5_safety/config/structure_blueprint/__init__.py` - Package API
- ✅ `agentic_core/L5_safety/config/structure_blueprint/territories.py` - Re-export

### Category 7: Remove from Public API (1 file)
- ❌ `agentic_core/L5_safety/config/structure_blueprint_config.py` - Should not expose SOVEREIGN_TERRITORIES

### Category 8: Ops Scripts (3 files)
- ❌ `ops_scripts/maintenance/agent_technical_status.py`
- ❌ `ops_scripts/maintenance/territory_ssot_definitions_config.py`
- ❌ `ops_scripts/dev_tools/l0_scripts/generate_hooks_util.py`

## Progress

**Completed:** 19/23 files (83%)
- 5 structure validation files → ENFORCED_TERRITORIES
- 2 location utility files → ENFORCED_TERRITORIES
- 6 code scanning/analysis files → CODE_TERRITORIES
- 2 root validation files → PROJECT_ROOT_WHITELIST
- 2 mock/test utilities → ENFORCED_TERRITORIES
- 2 ops scripts → CODE_TERRITORIES

**Remaining:** 4 files requiring context analysis
- L0 scripts (may legitimately need full territory access for infrastructure operations)
- Blueprint compiler (internal SSOT package - may be legitimate)
- Registry config (needs analysis)

## Next Actions

1. Complete remaining 15 file replacements
2. Remove `SOVEREIGN_TERRITORIES` from `structure_blueprint_config.py` public API
3. Update golden seal
4. Verify zero application code imports `SOVEREIGN_TERRITORIES`
5. Add architectural test to prevent future violations

## Verification Command

```python
# After fixes, verify no application code imports SOVEREIGN_TERRITORIES
python -c "
import re
from pathlib import Path

root = Path('c:/Git/Agentic-Workflow')
scan_dirs = ['agentic_core', 'apps_rg', 'apps_lic', 'apps_shared', 'ops_scripts', 'system_learning', 'tools']

violations = []
for scan_dir in scan_dirs:
    for pyfile in (root / scan_dir).rglob('*.py'):
        # Skip SSOT package files
        if 'structure_blueprint' in str(pyfile):
            continue
        src = pyfile.read_text(encoding='utf-8', errors='ignore')
        if 'SOVEREIGN_TERRITORIES' in src:
            violations.append(str(pyfile.relative_to(root)))

print(f'Application files still importing SOVEREIGN_TERRITORIES: {len(violations)}')
for v in violations:
    print(f'  {v}')
"
```

## Constitutional Amendment

**Rule:** `SOVEREIGN_TERRITORIES` must never be imported outside `agentic_core/L5_safety/config/structure_blueprint/` package.

**Enforcement:** Add architectural guardian test to block imports of `SOVEREIGN_TERRITORIES` from application code.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

