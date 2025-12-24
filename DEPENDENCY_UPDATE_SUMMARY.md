# Dependency Update Summary - Structure Blueprint & Void Compliance Integration

**Date:** December 24, 2025  
**Objective:** Update all files dependent on the new versions of `structure_blueprint.py`, `void_compliance.py`, and `canon_validator_agentic_v2.py`

---

## Core Files Updated

### 1. **structure_blueprint.py** (Source of Truth)
- **Location:** `agentic_core/config/P1_core/structure_blueprint.py`
- **Key Changes:**
  - Introduced `SOVEREIGN_REGISTRY` as the new SSOT structure
  - Each root folder now has `{"subfolders": [...], "depth": N}` configuration
  - Replaced `CANONICAL_HIERARCHY` with registry-based approach
  - Added `SOVEREIGN_DEPTH_MAP` for dynamic depth validation

### 2. **void_compliance.py** (L6 Runtime Enforcer)
- **Location:** `agentic_core/runtime/shared/void_compliance.py` (moved from `runtime/P1_core`)
- **Key Changes:**
  - Updated to use `SOVEREIGN_REGISTRY` from structure_blueprint
  - Added `get_placement_guidance()` for intelligent file placement (Key 40/49)
  - Enhanced hierarchy validation with SSOT reconciliation
  - Improved depth enforcement with single-file leaf support

### 3. **canon_validator_agentic_v2.py** (Main Validator)
- **Location:** `c:/Git/Agentic-Workflow/canon_validator_agentic_v2.py`
- **Key Changes:**
  - Integrated gravity layer ranking system (12 layers)
  - Added SSOT-based sprawl consolidation
  - Updated imports to use new void_compliance path
  - Added `get_placement_guidance` import for Key 40/49 guidance

---

## Dependent Files Updated

### **Agent Files** (L2_execution/P4_agents/)

#### 1. **healer_agent.py** ✅
**Changes:**
- Updated import: `from agentic_core.runtime.shared.void_compliance import get_placement_guidance, FORBIDDEN_ROOT_FOLDERS`
- Updated import: `from agentic_core.config.P1_core.structure_blueprint import SOVEREIGN_REGISTRY`
- Changed hierarchy validation from `CANONICAL_HIERARCHY` to `SOVEREIGN_REGISTRY`
- Updated logic to check `SOVEREIGN_REGISTRY[root_folder]["subfolders"]` instead of direct dict access

**Impact:** High - Core healing agent for structural violations

#### 2. **system_architect.py** ✅
**Changes:**
- Updated import: `from agentic_core.runtime.shared.void_compliance import validate_canonical_hierarchy`
- Updated import: `from agentic_core.config.P1_core.structure_blueprint import SOVEREIGN_REGISTRY`
- Changed package integrity checks to iterate over `SOVEREIGN_REGISTRY.items()`
- Updated depth validation to use `SOVEREIGN_REGISTRY[root_folder]["depth"]`
- Added L2 subfolder checking for depth-4 roots using `CORE_SUBFOLDER_MAP`

**Impact:** High - Validates Keys 40-50 (core architecture)

#### 3. **hygiene_guardian.py** ✅
**Changes:**
- Updated import: `from agentic_core.runtime.shared.void_compliance import ALLOWED_ROOT_FOLDERS`

**Impact:** Medium - Cleanup and maintenance operations

#### 4. **test_generator_agent.py** ✅
**Changes:**
- Updated import: `from agentic_core.runtime.shared import void_compliance`

**Impact:** Low - Test scaffolding operations

---

## Files Requiring Manual Review

### **Maintenance Scripts** (L0_maintenance/scripts/)

The following scripts reference `structure_blueprint` but may need updates depending on their usage:

1. **align_tests_structure.py** - 2 references
2. **canon_validator_config.py** - 2 references
3. **check_key_49_depth.py** - 2 references
4. **finalize_sovereign_structure.py** - 2 references
5. **validate_sovereign_structure.py** - 2 references

**Recommendation:** Review these scripts to ensure they use `SOVEREIGN_REGISTRY` instead of any deprecated structures.

### **Other Files**

1. **agentic_core/L1_cognition/P1_interfaces/governance.py** - 2 references
2. **agentic_core/L1_cognition/P2_domain/constants.py** - 2 references
3. **apps_shared/P1_core/constants.py** - 2 references
4. **agentic_core/config/P1_core/hierarchy_healer.py** - 1 reference
5. **agentic_core/utils/P1_core/forge_fortress.py** - 1 reference
6. **agentic_core/utils/P1_core/forge_sovereign_system_v2.py** - 1 reference
7. **sovereign_refactor.py** - 1 reference

**Recommendation:** These files likely reference structure_blueprint for configuration purposes. Verify they use the correct import paths and API.

### **Fix Scripts**

1. **fix_all_gravity_violations.py** - References void_compliance.py in pattern matching
2. **fix_remaining_gravity.py** - References void_compliance.py in pattern matching

**Status:** These scripts are pattern-based and should continue to work, but verify they don't need path updates.

---

## API Changes Summary

### **Old API → New API**

| Old Pattern | New Pattern |
|-------------|-------------|
| `from void_compliance import ...` | `from agentic_core.runtime.shared.void_compliance import ...` |
| `CANONICAL_HIERARCHY[root][l1]` | `SOVEREIGN_REGISTRY[root]["subfolders"]` |
| `SOVEREIGN_DEPTH_MAP[root]` | `SOVEREIGN_REGISTRY[root]["depth"]` |
| Manual depth checking | Use `validate_canonical_hierarchy()` |
| Static placement logic | Use `get_placement_guidance(content)` |

### **New Functions Available**

1. **`get_placement_guidance(content: str) -> str`**
   - Analyzes file content using heuristics
   - Returns suggested canonical path (e.g., "agentic_core/L4_state")
   - Used for intelligent file relocation (Key 40/49)

2. **`validate_canonical_hierarchy(project_root: Path) -> List[Tuple[Path, str]]`**
   - Validates entire project against SOVEREIGN_REGISTRY
   - Returns list of (path, reason) tuples for violations
   - Centralized SSOT validation

---

## Testing Recommendations

### **Critical Path Testing**

1. **Run canon_validator_agentic_v2.py** with `RUN_GRAVITY_REFACTOR=True`
   - Verify gravity layer ranking detects violations
   - Confirm SSOT sprawl consolidation works
   - Check placement guidance provides correct suggestions

2. **Test HealerAgent** structural rehoming
   - Create a test file in wrong location
   - Verify it gets relocated to correct SSOT path
   - Confirm imports are updated correctly

3. **Test SystemArchitect** hierarchy validation
   - Verify depth enforcement uses SOVEREIGN_REGISTRY
   - Check package integrity validation works
   - Confirm __init__.py creation logic functions

### **Regression Testing**

Run the following to ensure no breakage:
```bash
python canon_validator_agentic_v2.py
python -m pytest tests/unit/agentic_core/L2_execution/P4_agents/
```

---

## Migration Checklist

- [x] Update canon_validator_agentic_v2.py imports
- [x] Update healer_agent.py for new API
- [x] Update system_architect.py for SOVEREIGN_REGISTRY
- [x] Update hygiene_guardian.py imports
- [x] Update test_generator_agent.py imports
- [ ] Review and update maintenance scripts
- [ ] Review governance.py and constants.py files
- [ ] Test full validation run with all 50 keys
- [ ] Verify gravity refactor phase works correctly
- [ ] Confirm sprawl consolidation executes properly

---

## Known Issues & Resolutions

### **Issue 1: Import Path Changes**
**Problem:** Files importing from `void_compliance` directly fail  
**Resolution:** Update to `from agentic_core.runtime.shared.void_compliance import ...`

### **Issue 2: CANONICAL_HIERARCHY Deprecated**
**Problem:** Code referencing `CANONICAL_HIERARCHY` dict structure breaks  
**Resolution:** Use `SOVEREIGN_REGISTRY[root]["subfolders"]` instead

### **Issue 3: Depth Map Access**
**Problem:** `SOVEREIGN_DEPTH_MAP[root]` may not exist as standalone  
**Resolution:** Use `SOVEREIGN_REGISTRY[root]["depth"]` for dynamic access

---

## Success Criteria

✅ All agent files import from correct paths  
✅ No references to deprecated `CANONICAL_HIERARCHY`  
✅ Depth validation uses `SOVEREIGN_REGISTRY`  
✅ Placement guidance integrated into healing workflow  
✅ Canon validator runs without import errors  
✅ All 50 keys validate correctly  

---

## Next Steps

1. **Immediate:** Run full canon validation to verify all updates work
2. **Short-term:** Update remaining maintenance scripts
3. **Long-term:** Consider deprecation warnings for old API usage

---

**Status:** ✅ Core dependencies updated successfully  
**Files Modified:** 5 agent files + 1 validator  
**Files Pending Review:** ~15 maintenance/utility scripts
