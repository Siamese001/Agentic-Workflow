# RCA: Why HierarchyAgent --heal --execute Doesn't Accomplish SSOT Enforcement

**Date:** 2026-01-21
**Author:** Cascade AI
**Status:** Analysis Complete

---

## Executive Summary

The `HierarchyAgent` has **significant functional gaps** that prevent it from performing the full SSOT enforcement we did manually. The agent is designed primarily for `agentic_core/` hierarchy management and **completely ignores** the `tests/`, `apps_rg/`, `apps_lic/`, and `apps_shared/` folders.

---

## 1. Root Cause Analysis

### Gap 1: Scope Limited to `agentic_core/` Only

**Code Evidence:**

```python
# HierarchyAgent.py:263-265
agentic_core_path = self.project_root / "agentic_core"
if not agentic_core_path.exists():
    return results
```

**Impact:** The `relocate_misplaced_files()` method only operates on `agentic_core/`. It never touches:
- `tests/` - 29 non-SSOT subfolders we manually reorganized
- `apps_rg/engines/utils/` - files we manually flattened
- `apps_lic/engines/utils/` - files we manually flattened
- `apps_shared/` - not scanned at all

### Gap 2: Depth Enforcement Only for Files IN Violations, Not Subfolders

**Code Evidence:**

```python
# HierarchyAgent.py:559-564
if depth > expected:
    # DEEP: Flatten (move up) - Keep the filename, remove intermediate folders
    new_parts = rel.parts[:expected] + (rel.parts[-1],)
    target_path = self.project_root.joinpath(*new_parts)
    action = "FLATTENED"
```

**Issue:** The flattening logic only moves individual files, but **does not recursively process or remove the nested `utils/` subdirectory**. After flattening, empty directories remain.

### Gap 3: No Test Folder Categorization Logic

**What We Did Manually:**
```python
# Categorized 255 test files by type:
- test_*_e2e.py → tests/e2e/
- test_*_integration.py → tests/integration/
- unit tests → tests/unit/
- fixtures, conftest.py → tests/fixtures/
```

**What HierarchyAgent Does:**
- Nothing. There is no `categorize_test_files()` or equivalent method.
- The SSOT defines `tests` with approved subfolders, but no agent enforces files into those subfolders.

### Gap 4: User Approval Bottleneck

**Code Evidence:**

```python
# HierarchyAgent.py:343-347
if not self._prompt_user_for_move_approval(
    py_file, dest, f"Relocate from illegal layer '{bad_layer_l2}'"
):
    Logger.info(f"      [SKIPPED] User declined: {py_file.name}")
    return
```

**Issue:** Every file move requires interactive user approval. With 255+ files to move, this is impractical. The `--execute` flag doesn't bypass this - it only enables the healing mode, not auto-approval.

### Gap 5: `_enforce_apps_depth()` Uses Wrong Key

**Code Evidence (before our fix):**

```python
# HierarchyAgent.py:684-686 (ORIGINAL)
def _enforce_apps_depth(self) -> int:
    return self._enforce_depth_for_root(
        "apps_rg", lambda r: r.startswith("apps_"), "apps_depth", "APPS"
    )
```

**Issue:** All `apps_*` folders were checked against `apps_rg`'s depth value. If `apps_rg` had depth 3 but `apps_shared` needed depth 2, everything failed.

---

## 2. Functional Coverage Matrix

| Capability | HierarchyAgent | What We Did Manually |
|------------|----------------|---------------------|
| Create missing L2/L3 dirs in `agentic_core/` | ✅ Yes | N/A |
| Relocate files in `agentic_core/` non-approved subfolders | ✅ Yes (with prompts) | ✅ Done |
| Flatten deep files in `agentic_core/` | ✅ Yes | N/A |
| Reorganize `tests/` by test type | ❌ **NO** | ✅ 255 files moved |
| Remove non-SSOT `tests/` subfolders | ❌ **NO** | ✅ 29 folders removed |
| Flatten `apps_lic/engines/utils/` | ❌ **NO** | ✅ 95 files flattened |
| Flatten `apps_rg/engines/utils/` | ❌ **NO** | ✅ 50+ files flattened |
| Auto-approve bulk operations | ❌ **NO** | ✅ Scripted |
| Enforce `apps_*` depth correctly | ⚠️ Buggy | ✅ Fixed logic |

---

## 3. Missing Methods

The HierarchyAgent needs these methods to match our manual work:

### 3.1 `reorganize_tests_by_type()`
```python
def reorganize_tests_by_type(self) -> dict:
    """Move test files from non-SSOT subfolders to unit/integration/e2e/functional/fixtures."""
    approved = {"unit", "integration", "e2e", "functional", "fixtures"}
    tests_path = self.project_root / "tests"

    for subfolder in tests_path.iterdir():
        if subfolder.is_dir() and subfolder.name not in approved:
            for file in subfolder.rglob("*"):
                if file.is_file():
                    target = self._categorize_test_file(file)
                    # Move file to target
```

### 3.2 `flatten_apps_depth_violations()`
```python
def flatten_apps_depth_violations(self) -> dict:
    """Flatten files in apps_*/subfolder/subsubfolder/ to apps_*/subfolder/."""
    for app_dir in ["apps_rg", "apps_lic", "apps_shared"]:
        expected_depth = SOVEREIGN_REGISTRY[app_dir]["depth"]
        # Find files deeper than expected and flatten
```

### 3.3 `enforce_all_roots()` (unified enforcement)
```python
def enforce_all_roots(self) -> dict:
    """Enforce SSOT on ALL root folders, not just agentic_core."""
    roots = ["agentic_core", "apps_rg", "apps_lic", "apps_shared", "tests", "scripts"]
    for root in roots:
        self._enforce_root_ssot(root)
```

---

## 4. Recommendations

### Immediate Fixes

1. **Add `--auto-approve` flag** to bypass interactive prompts for CI/batch operations
2. **Fix `_enforce_apps_depth()`** to check each `apps_*` folder with its own depth (already done in this session)
3. **Extend scope** to include `tests/`, `apps_*` folders

### Structural Improvements

1. **Create `TestsReorganizationAgent`** - dedicated agent for test folder SSOT
2. **Create `AppsDepthEnforcerAgent`** - dedicated agent for apps folder flattening
3. **Or extend HierarchyAgent** with methods for all root folders

### Architecture Decision

The current design assumes:
- `agentic_core/` is the primary concern
- Other folders are "simpler" and don't need enforcement

Reality:
- `tests/` has the most violations (29 non-SSOT subfolders)
- `apps_*/engines/utils/` has nested files violating depth rules
- All roots need equal enforcement attention

---

## 5. Why `--heal --execute` Didn't Work

| Flag | What It Does | What It Doesn't Do |
|------|--------------|-------------------|
| `--heal` | Enables healing mode (vs dry-run) | Doesn't bypass user prompts |
| `--execute` | Triggers `heal_repository()` | Doesn't auto-approve moves |

**The actual execution path:**
1. `heal_repository()` calls `heal_hierarchy()`
2. `heal_hierarchy()` calls `relocate_misplaced_files()`
3. `relocate_misplaced_files()` only scans `agentic_core/`
4. For each file, `_prompt_user_for_move_approval()` waits for input
5. `tests/`, `apps_*` are never touched

---

## 6. Conclusion

The HierarchyAgent is **not designed** to do what we did manually. It's a specialized `agentic_core/` hierarchy manager, not a full SSOT enforcer for the entire repository.

**To achieve automated SSOT enforcement:**
1. Extend HierarchyAgent to cover all roots
2. Add test file categorization logic
3. Add apps depth flattening logic
4. Add `--auto-approve` flag for batch operations
5. Or create separate agents for each domain

---

*Report generated by Cascade AI during RCA of SSOT enforcement gaps.*
