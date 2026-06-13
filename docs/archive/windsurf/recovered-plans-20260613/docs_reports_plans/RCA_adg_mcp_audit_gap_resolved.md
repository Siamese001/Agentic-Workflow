# RCA: ADG Failed to Catch MCP Errors and Stubs

**Status:** ✅ RESOLVED
**Resolved:** 2025 (this session)
**Scope:** ADG static scanner, ADG invariant scanner, ruff lint configuration

---

## 1. Summary

Six classes of bugs were manually fixed in the MCP layer. The ADG static analysis and CI enforcement pipeline failed to detect any of them. This document identifies the root causes and confirms the corrective actions taken.

---

## 2. Bugs That Were Missed and Why

### Bug 1 — `mcp_authority` used without import (undefined name)

**Files:** `sovereign_mcp_router.py`, `sovereign_filesystem_mcp.py`, `sovereign_mcp_marketplace.py`
**Error class:** `NameError` at runtime — `mcp_authority` used as a bare name with no import
**Rule that should catch it:** ruff `F821` (undefined-name)
**Root cause:** `F821` was in the **global `ignore` list** in `pyproject.toml` with comment *"codebase uses lazy/conditional imports extensively"*. This blanket suppression silenced real undefined-name bugs alongside intentional lazy patterns.

### Bug 2 — `HardenedRouter` referenced but never defined/imported

**File:** `apps_shared/utils/router_factory_util.py`
**Error class:** `NameError` — `HardenedRouter` had no binding anywhere in the module
**Root cause:** Same — F821 globally suppressed.

### Bug 3 — `LLMClient`, `SequentialThinkingClient` used before definition

**File:** `apps_shared/types/model_router_types.py`
**Error class:** `NameError` — class bodies referenced names not yet defined
**Root cause:** Same — F821 globally suppressed.

### Bug 4 — `FallbackClient.generate` defined twice (duplicate method)

**File:** `apps_shared/types/model_router_types.py`
**Error class:** Silent bug — second definition silently shadows first
**Rule that should catch it:** ruff `F811` (redefined-while-unused); ADG Rule D (new)
**Root cause:** F811 was globally suppressed with comment *"backward-compat aliases and decorator wrappers"*. ADG had no duplicate-method detection rule.

### Bug 5 — Unreachable code after `raise` in exception handlers

**Files:** `sovereign_mcp_router.py`, `sovereign_mcp_marketplace.py`
**Error class:** Dead code — `Logger.warning(...)` after `raise` is never executed
**Rule that should catch it:** ADG Rule G (new) — no prior check existed
**Root cause:** ADG had no control-flow analysis plane. Neither ruff nor ADG detected this pattern.

### Bug 6 — Wrong MCP tool prefix (`mcp12_*` instead of `mcp8_*`)

**File:** `agentic_core/L3_orchestration/reasoning/mcp_manager.py`
**Error class:** Silent misconfiguration — dispatched calls went to non-existent tools
**Root cause:** No ADG dispatch-table validation rule exists. Addressed by manual fix only.

---

## 3. Root Cause Classification

| Root Cause | Bugs Affected |
|---|---|
| `F821` globally suppressed in `pyproject.toml` | 1, 2, 3 |
| `F823` globally suppressed in `pyproject.toml` | 1, 2, 3 (secondary) |
| No ADG `duplicate_method` detection (Rule D) | 4 |
| No ADG `unreachable_after_raise` detection (Rule G) | 5 |
| No ADG dispatch-table validation | 6 |

---

## 4. Corrective Actions Taken

### [x] Fix 1 — Re-enable ruff F821 for `agentic_core/**` and `apps_*/`

**File:** `pyproject.toml`
**Change:** Removed `F821` and `F823` from global `ignore` list. Added both only to per-file-ignores for `ops_scripts/**`, `tools/**`, and `system_learning/**` — the only directories where lazy/dynamic import patterns are legitimately used.

```toml
# BEFORE (incorrect — global suppression)
ignore = [
    "F821",  # undefined-name: codebase uses lazy/conditional imports extensively
    "F823",  # undefined-local: lazy imports resolved at runtime
    ...
]

# AFTER (correct — narrowed to legitimate dynamic-import directories)
[tool.ruff.lint.per-file-ignores]
"ops_scripts/**/*.py" = [..., "F821", "F823"]
"tools/**/*.py" = [..., "F821", "F823"]
"system_learning/**/*.py" = [..., "F821", "F823"]
```

### [x] Fix 2 — Add `_DuplicateMethodVisitor` (Rule D) to static scanner

**File:** `agentic_core/adg/extraction/static_scanner.py`
**Change:** Added `_is_property_accessor()` helper and `_DuplicateMethodVisitor` class. Emits `duplicate_method` edges for any `FunctionDef`/`AsyncFunctionDef` name appearing more than once in the immediate body of a `ClassDef`. Property `setter`/`deleter`/`getter` decorators are exempt.

### [x] Fix 3 — Add `_UnreachableCodeAfterRaiseVisitor` (Rule G) to static scanner

**File:** `agentic_core/adg/extraction/static_scanner.py`
**Change:** Added `_UnreachableCodeAfterRaiseVisitor` class. Emits `unreachable_after_raise` edges for any statement that immediately follows a `raise` statement in the same block (exception handlers, function bodies, if/while/for branches).

### [x] Fix 4 — Wire both new visitors into `_scan_file`

**File:** `agentic_core/adg/extraction/static_scanner.py`
**Change:** Added `GH` and `GU` visitor calls after the `G16` eval spine visitor in `_scan_file`.

### [x] Fix 5 — Add Rule D and Rule G to `InvariantScanner`

**File:** `agentic_core/adg/ci/invariant_scanner.py`
**Change:**
- Added `_POLICY_DUPLICATE_METHOD` and `_POLICY_UNREACHABLE_AFTER_RAISE` constants
- Added `_rule_d_duplicate_method()` method — reports `duplicate_method` edges as `RULE_D` violations
- Added `_rule_g_unreachable_after_raise()` method — reports `unreachable_after_raise` edges as `RULE_G` violations
- Wired both into `InvariantScanner.scan()`
- Updated `__all__` to export new policy constants

### [x] Fix 6 — Write regression tests

**File:** `tests/adg/test_adg_mcp_audit_rules.py`
**Change:** Added 24 tests covering:
- `_is_property_accessor` (positive/negative)
- `_DuplicateMethodVisitor` (positive: plain dup, async dup, 3x dup, nested class)
- `_DuplicateMethodVisitor` (negative: property getter/setter, unique names, no class, different classes)
- `_UnreachableCodeAfterRaiseVisitor` (positive: except handler, raise expr, function body, if branch)
- `_UnreachableCodeAfterRaiseVisitor` (negative: raise is last stmt, normal function, raise in else)
- `InvariantScanner._rule_d_duplicate_method` (violation + no false positive)
- `InvariantScanner._rule_g_unreachable_after_raise` (violation + no false positive)
- End-to-end: exact MCP bug reproduction for both rules

---

## 5. Why F821/F811 Were Suppressed Globally in the First Place

The original suppressions were added to handle:
- **F821/F823**: `TYPE_CHECKING`-guarded imports (e.g., `if TYPE_CHECKING: from X import Y`). However, ruff correctly handles these as type-only references and does NOT fire F821 on them. The global suppression was over-broad.
- **F811**: Property getter/setter descriptor patterns. However, ruff correctly exempts `@property`/`@x.setter` pairs from F811. The global suppression was over-broad.

The real reason F821 fired on many files was because the codebase had accumulated multiple genuine undefined-name bugs. The suppression masked real errors rather than handling legitimate patterns.

---

## 6. Residual Gap (not fixed in this session)

- **Dispatch-table validation** (Bug 6): No ADG rule validates that tool names in `_TOOL_DISPATCH` maps correspond to registered MCP tools. Addressing this requires either a registry snapshot or a dedicated MCP tool-name linting pass. Tracked as a future enhancement.

---

## 7. Evidence

| Artifact | Location |
|---|---|
| ruff config fix | `pyproject.toml` — removed F821/F823 from `ignore`, added to per-file-ignores |
| New visitor: `_DuplicateMethodVisitor` | `agentic_core/adg/extraction/static_scanner.py` |
| New visitor: `_UnreachableCodeAfterRaiseVisitor` | `agentic_core/adg/extraction/static_scanner.py` |
| New rule: `RULE_D` | `agentic_core/adg/ci/invariant_scanner.py` |
| New rule: `RULE_G` | `agentic_core/adg/ci/invariant_scanner.py` |
| Regression tests (24 tests) | `tests/adg/test_adg_mcp_audit_rules.py` |

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

