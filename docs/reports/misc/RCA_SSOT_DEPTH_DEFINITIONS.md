# RCA Report: SSOT Folder Depth Definition Inconsistencies

**Date:** 2026-01-21
**Author:** Cascade AI
**Status:** Analysis Complete - Implementation Plan Ready

---

## Executive Summary

The SSOT folder depth enforcement system has **fundamental design flaws** that required extensive workarounds during remediation. The current implementation uses:

1. **Exact depth matching** (`depth != expected_depth`) instead of **maximum depth bounds**
2. **A growing `VARIABLE_DEPTH_SUBFOLDERS` exception list** that now contains 29 entries
3. **Inconsistent depth values** across similar folder types (`apps_shared: 2` vs `apps_rg/apps_lic: 3`)

This report identifies root causes and proposes a unified depth model.

---

## 1. Root Cause Analysis

### Finding 1: Depth Semantics Are Inverted

**Problem:** The `depth` value in `SOVEREIGN_REGISTRY` is interpreted as an **exact required depth**, not a **maximum allowed depth**.

```python
# Current enforcement logic (HierarchyAgent.py:541)
if depth != expected_depth:  # EXACT match required
    violations += 1
```

**Impact:** Files at valid intermediate depths are flagged as violations.

| File Path | Actual Depth | Expected (SSOT) | Result |
|-----------|--------------|-----------------|--------|
| `apps_shared/utils/file.py` | 2 | 2 | ✅ Pass |
| `apps_shared/utils/helpers/file.py` | 3 | 2 | ❌ Fail |
| `tests/unit/test_file.py` | 2 | 3 | ❌ Fail |
| `tests/core/arch/test_file.py` | 3 | 3 | ✅ Pass |

**Root Cause:** The original design assumed all files would be at a single canonical depth, which doesn't match real-world repository structures.

---

### Finding 2: VARIABLE_DEPTH_SUBFOLDERS Is a Code Smell

**Problem:** The `VARIABLE_DEPTH_SUBFOLDERS` set has grown to **29 entries**, effectively exempting most of the codebase from depth enforcement.

```python
VARIABLE_DEPTH_SUBFOLDERS: frozenset[str] = frozenset({
    "utils", "config", "common", "observability", "L6_observability",
    "L3_orchestration", "L0_maintenance", "L1_cognition", "L2_execution",
    "L4_state", "L5_safety", "schemas", "prompt_governance", "runtime",
    "patterns", "semantic_memory", "knowledge", "engines", "domain",
    "core", "code_standards_fixtures", "hygiene_test_fixtures",
    "maintenance", "dashboard", "unified", "security", "depth_aligned"
})
```

**Impact:**
- The exception list is **larger than the rule set**
- Adding new subfolders requires updating this list
- The "depth" value becomes meaningless when most folders are exempt

**Root Cause:** Workaround for Finding 1 - instead of fixing the depth semantics, exceptions were added.

---

### Finding 3: Inconsistent Depth Values Across Similar Folders

**Current State:**

| Root Folder | Depth | Rationale |
|-------------|-------|-----------|
| `agentic_core` | 3 | Layered architecture (L0-L6) |
| `apps_rg` | 3 | Nested `engines/utils/` |
| `apps_lic` | 3 | Nested `engines/utils/` and `shared/validation/` |
| `apps_shared` | 2 | Flat utilities |
| `tests` | 3 | Nested fixtures |
| `scripts` | 1 | Flat utilities |

**Problem:** `apps_shared` has depth 2 while `apps_rg` and `apps_lic` have depth 3, despite similar structures.

**Root Cause:** Ad-hoc depth assignments based on current file locations rather than architectural intent.

---

### Finding 4: Enforcement Logic Is Fragmented

**Problem:** Depth enforcement is split across multiple methods with different behaviors:

| Method | Root Folders | Variable Depth Check |
|--------|--------------|---------------------|
| `_enforce_apps_depth()` | `apps_rg`, `apps_lic`, `apps_shared` | ✅ Yes (after fix) |
| `_enforce_tests_depth()` | `tests` | ✅ Yes (after fix) |
| `_enforce_universal_depth()` | `agentic_core` (non-Python) | ❌ No |
| `_enforce_depth_for_root()` | Generic | ✅ Yes |

**Root Cause:** Incremental additions without refactoring to a unified model.

---

## 2. Recommendations

### Recommendation 1: Adopt Maximum Depth Semantics

**Change:** Interpret `depth` as the **maximum allowed depth**, not exact depth.

```python
# Proposed enforcement logic
if depth > max_depth:  # MAXIMUM bound, not exact match
    violations += 1
```

**Benefits:**
- Files at any depth ≤ max_depth are valid
- No need for `VARIABLE_DEPTH_SUBFOLDERS` exceptions
- Simpler mental model

---

### Recommendation 2: Introduce Minimum Depth for Structural Enforcement

**Change:** Add optional `min_depth` to enforce that files aren't placed too shallow.

```python
SOVEREIGN_REGISTRY = {
    "agentic_core": {
        "min_depth": 2,  # Files must be in L*/subfolder/, not L*/ directly
        "max_depth": 5,  # Allow deep nesting for complex modules
    },
    "apps_rg": {
        "min_depth": 2,  # Files must be in engines/*, not engines/ directly
        "max_depth": 4,  # Allow engines/utils/helpers/
    },
    ...
}
```

**Benefits:**
- Prevents files from being placed at the root of subfolders
- Allows controlled nesting without arbitrary limits

---

### Recommendation 3: Unified Depth Model

**Proposed SSOT:**

```python
SOVEREIGN_REGISTRY = {
    "agentic_core": {
        "min_depth": 2,
        "max_depth": 5,
        "subfolders": ["L0_maintenance", "L1_cognition", ...],
        "purpose": "Core framework with layered architecture",
    },
    "apps_rg": {
        "min_depth": 2,
        "max_depth": 4,
        "subfolders": ["engines", "domain", "templates", ...],
        "purpose": "Resume generation application",
    },
    "apps_lic": {
        "min_depth": 2,
        "max_depth": 4,
        "subfolders": ["engines", "domain", "templates", ...],
        "purpose": "LinkedIn outreach application",
    },
    "apps_shared": {
        "min_depth": 2,
        "max_depth": 3,
        "subfolders": ["utils", "models", "config", ...],
        "purpose": "Shared utilities across applications",
    },
    "tests": {
        "min_depth": 1,  # Allow root-level test files (conftest.py, etc.)
        "max_depth": 4,
        "subfolders": ["unit", "integration", "e2e", ...],
        "purpose": "Test suites with nested fixtures",
    },
    "scripts": {
        "min_depth": 1,
        "max_depth": 1,
        "subfolders": [],
        "purpose": "Standalone utility scripts (no nesting)",
    },
}
```

---

### Recommendation 4: Deprecate VARIABLE_DEPTH_SUBFOLDERS

**Change:** Remove `VARIABLE_DEPTH_SUBFOLDERS` entirely once max_depth semantics are implemented.

**Migration Path:**
1. Implement min/max depth enforcement
2. Verify all files pass with new semantics
3. Remove `VARIABLE_DEPTH_SUBFOLDERS` and related checks
4. Update documentation

---

## 3. Implementation Plan

### Phase 1: Schema Update (Low Risk)

**Files to Modify:**
- `agentic_core/L5_safety/validators/structure_blueprint.py`

**Changes:**
1. Add `min_depth` and rename `depth` to `max_depth` in `SOVEREIGN_REGISTRY`
2. Add backward compatibility shim for `depth` key

```python
# Backward compatibility
def get_depth_bounds(root_key: str) -> tuple[int, int]:
    """Get (min_depth, max_depth) for a root folder."""
    config = SOVEREIGN_REGISTRY.get(root_key, {})
    max_depth = config.get("max_depth", config.get("depth", 3))
    min_depth = config.get("min_depth", 1)
    return min_depth, max_depth
```

**Estimated Effort:** 1 hour

---

### Phase 2: Enforcement Logic Update (Medium Risk)

**Files to Modify:**
- `agentic_core/L5_safety/validators/HierarchyAgent.py`
- `agentic_core/L5_safety/validators/LocationValidatorAgent.py`

**Changes:**
1. Update `_enforce_depth_for_root()` to use min/max bounds
2. Remove `VARIABLE_DEPTH_SUBFOLDERS` checks
3. Update violation messages

```python
def _enforce_depth_for_root(self, root_key: str, ...) -> int:
    min_depth, max_depth = get_depth_bounds(root_key)

    for file_path in all_files:
        depth = len(rel.parts) - 1

        if depth < min_depth:
            violations += 1
            Logger.warning(f"TOO SHALLOW: {rel} is depth {depth}, min is {min_depth}")
        elif depth > max_depth:
            violations += 1
            Logger.warning(f"TOO DEEP: {rel} is depth {depth}, max is {max_depth}")
```

**Estimated Effort:** 2 hours

---

### Phase 3: Cleanup (Low Risk)

**Files to Modify:**
- `agentic_core/L5_safety/validators/structure_blueprint.py`

**Changes:**
1. Remove `VARIABLE_DEPTH_SUBFOLDERS` constant
2. Remove all references to it in enforcement code
3. Update docstrings and comments

**Estimated Effort:** 30 minutes

---

### Phase 4: Verification

**Commands:**
```bash
# Run SSOT check
python -m agentic_core.L5_safety.validators.ssot_folder_check

# Run unit tests
pytest tests/L5_safety/ -v

# Run pre-commit hooks
pre-commit run --all-files
```

**Success Criteria:**
- `ssot_folder_check` exits with code 0
- All existing tests pass
- No new violations introduced

---

## 4. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing valid files | Low | High | Dry-run mode first, review all violations |
| Missing edge cases | Medium | Medium | Comprehensive test coverage |
| Backward compatibility | Low | Low | Shim for `depth` key |

---

## 5. Appendix: Current vs Proposed Depth Values

| Root Folder | Current `depth` | Proposed `min_depth` | Proposed `max_depth` |
|-------------|-----------------|----------------------|----------------------|
| `agentic_core` | 3 | 2 | 5 |
| `apps_rg` | 3 | 2 | 4 |
| `apps_lic` | 3 | 2 | 4 |
| `apps_shared` | 2 | 2 | 3 |
| `tests` | 3 | 1 | 4 |
| `scripts` | 1 | 1 | 1 |

---

## 6. Decision Required

**Option A: Implement Full min/max Depth Model**
- Pros: Clean architecture, no exceptions needed, future-proof
- Cons: Requires code changes, testing effort
- Estimated Effort: 4 hours

**Option B: Keep Current Model with VARIABLE_DEPTH_SUBFOLDERS**
- Pros: No code changes, already working
- Cons: Technical debt, growing exception list, confusing semantics
- Estimated Effort: 0 hours (status quo)

**Recommendation:** Option A - The current model is unsustainable as the codebase grows.

---

*Report generated by Cascade AI as part of RCA Hygiene Agents refinement.*
