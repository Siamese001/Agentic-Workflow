# Phase 3: Layer Inference Refactoring Audit

**Date:** January 12, 2025  
**Objective:** Identify all duplicate layer inference implementations for migration to canonical_truth.py  
**Status:** AUDIT IN PROGRESS

---

## Duplicate Layer Inference Functions Found

### Summary
Found **10 duplicate implementations** of layer inference logic across the codebase:

| File | Function | Lines | Status |
|------|----------|-------|--------|
| `scripts/ast_layer_stats.py` | `get_layer()` | 31-34 | DUPLICATE |
| `scripts/agent_discovery_audit.py` | `infer_layer()` | 50-53 | DUPLICATE |
| `scripts/scan_testing_compliance.py` | `infer_layer()` | 74-77 | DUPLICATE |
| `scripts/ssot_audit.py` | `get_layer()` | 34-37 | DUPLICATE |
| `scripts/full_agent_discovery.py` | `infer_layer()` | 368-371 | **CRITICAL** |
| `agentic_core/utils/general_helpers/mission_utils.py` | `get_layer_rank()` | 39-42 | DUPLICATE |
| `agentic_core/utils/core_extensions/ssot_scanner.py` | `get_layer_assignment()` | 125-128 | DUPLICATE |
| `agentic_core/L5_safety/guardrails/GravityEnforcerAgent.py` | `get_layer_from_path()` | 98-112 | DUPLICATE |
| `agentic_core/L5_safety/guardrails/GravityEnforcerAgent.py` | `get_layer_from_import()` | 114-117 | DUPLICATE |
| `archives/deprecated_agents/GravityComplianceValidatorAgent.py` | `get_layer_rank()` | 41-44 | ARCHIVED |

---

## Critical Migration Targets

### 1. **full_agent_discovery.py** (HIGHEST PRIORITY)
**File:** `scripts/full_agent_discovery.py`  
**Function:** `infer_layer()` (lines 368-371)  
**Impact:** Used to assign layer to ALL 281 agents in discovery  
**Migration:** Replace with `get_canonical_layer()` from canonical_truth.py

**Current Implementation:**
```python
def infer_layer(file_path: Path) -> str:
    """Infer canonical layer from file path."""
    path_str = str(file_path)
    # Core layers - check specific layers first
    if 'L0_maintenance' in path_str: return 'L0'
    if 'L1_cognition' in path_str: return 'L1'
    # ... etc
```

**Proposed Fix:**
```python
from agentic_core.config.blueprint_sovereign.canonical_truth import get_canonical_layer

# Replace all calls to infer_layer() with get_canonical_layer()
layer = get_canonical_layer(file_path)
```

---

### 2. **GravityEnforcerAgent.py** (HIGH PRIORITY)
**File:** `agentic_core/L5_safety/guardrails/GravityEnforcerAgent.py`  
**Functions:** 
- `get_layer_from_path()` (lines 98-112)
- `get_layer_from_import()` (lines 114-117)

**Impact:** Used for gravity violation detection (upward dependency checks)  
**Migration:** Replace with `get_canonical_layer()`

---

### 3. **ssot_scanner.py** (MEDIUM PRIORITY)
**File:** `agentic_core/utils/core_extensions/ssot_scanner.py`  
**Function:** `get_layer_assignment()` (lines 125-128)  
**Impact:** Used by unified_validator for agent scanning  
**Migration:** Replace with `get_canonical_layer()`

---

## Path Parsing Patterns Found

### Pattern 1: String Contains Check
```python
if 'L0_maintenance' in path_str: return 'L0'
if 'L1_cognition' in path_str: return 'L1'
```
**Found in:** 6 files  
**Issue:** No path normalization, Windows/Linux inconsistency

### Pattern 2: Split and Iterate
```python
parts = path_str.split('/')
for part in parts:
    if part.startswith('L') and part[1].isdigit():
        return part[:2]
```
**Found in:** 2 files  
**Issue:** Doesn't handle backslashes (Windows paths)

### Pattern 3: Regex Pattern Matching
```python
if f'/{layer}_' in path_str or f'\\{layer}_' in path_str:
    return layer
```
**Found in:** 2 files  
**Issue:** Fragile, doesn't handle all edge cases

---

## Canonical Implementation (SSOT)

**File:** `agentic_core/config/blueprint_sovereign/canonical_truth.py`  
**Function:** `get_canonical_layer(file_path: Union[str, Path]) -> str`

**Features:**
- ✅ Handles both str and Path objects
- ✅ Normalizes Windows/Linux paths (backslash → forward slash)
- ✅ Priority-ordered layer detection
- ✅ Comprehensive test coverage (9 tests)
- ✅ Zero internal dependencies

**Algorithm:**
1. Normalize path separators
2. Check LAYER_MARKERS dictionary (L0_maintenance → L0, etc.)
3. Fallback: Pattern-based detection (/L5/ in path)
4. Return "Unknown" if no match

---

## Migration Plan

### Phase 3A: Critical Files (Week 1)
1. **full_agent_discovery.py** - Replace `infer_layer()` with `get_canonical_layer()`
2. **GravityEnforcerAgent.py** - Replace both `get_layer_*()` functions
3. **ssot_scanner.py** - Replace `get_layer_assignment()`

### Phase 3B: Supporting Scripts (Week 2)
4. **ast_layer_stats.py** - Replace `get_layer()`
5. **agent_discovery_audit.py** - Replace `infer_layer()`
6. **scan_testing_compliance.py** - Replace `infer_layer()`
7. **ssot_audit.py** - Replace `get_layer()`

### Phase 3C: Utility Functions (Week 3)
8. **mission_utils.py** - Replace `get_layer_rank()` (or keep if different purpose)

---

## Testing Strategy

### Test 1: REFACT-01 (Zero Local Parsers)
**Objective:** Verify no duplicate implementations remain  
**Command:**
```bash
grep -r "def get_layer\|def infer_layer" --include="*.py" | grep -v canonical_truth.py
```
**Expected:** 0 matches (excluding archives)

### Test 2: Discovery Consistency
**Objective:** Verify agent_discovery_full.json has consistent layers  
**Steps:**
1. Run discovery with canonical layer function
2. Compare layer assignments before/after migration
3. Verify no agents changed layers unexpectedly

### Test 3: Gravity Validation
**Objective:** Verify gravity checks still work after migration  
**Steps:**
1. Run GravityEnforcerAgent on test files
2. Verify upward dependency violations still detected
3. Compare results before/after migration

---

## Risk Assessment

### High Risk
- **full_agent_discovery.py** - Core discovery logic, affects all 281 agents
- **Mitigation:** Backup agent_discovery_full.json, run E2E tests after migration

### Medium Risk
- **GravityEnforcerAgent.py** - Security-critical gravity checks
- **Mitigation:** Comprehensive gravity test suite, manual validation

### Low Risk
- Supporting scripts - Used for auditing/analysis, not production
- **Mitigation:** Spot-check results after migration

---

## Estimated Effort

| Phase | Files | Estimated Time |
|-------|-------|----------------|
| Phase 3A (Critical) | 3 files | 4-6 hours |
| Phase 3B (Scripts) | 4 files | 2-3 hours |
| Phase 3C (Utils) | 1 file | 1 hour |
| Testing & Validation | All | 3-4 hours |
| **TOTAL** | **8 files** | **10-14 hours** |

---

## Success Criteria

1. ✅ All duplicate `get_layer()` / `infer_layer()` functions removed
2. ✅ All files import from `canonical_truth.py`
3. ✅ REFACT-01 test passes (0 duplicate implementations)
4. ✅ Discovery generates same layer assignments
5. ✅ Gravity checks still detect violations
6. ✅ E2E dashboard tests pass

---

## Next Actions

1. **Backup current state** - Save agent_discovery_full.json
2. **Migrate full_agent_discovery.py** - Highest priority
3. **Run discovery** - Regenerate with canonical function
4. **Compare results** - Verify consistency
5. **Run E2E tests** - Validate dashboard
6. **Proceed to Phase 3B** - Migrate supporting scripts

---

**Report prepared by:** Cascade AI  
**Audit status:** COMPLETE  
**Ready for migration:** YES  
**Recommended start:** full_agent_discovery.py
