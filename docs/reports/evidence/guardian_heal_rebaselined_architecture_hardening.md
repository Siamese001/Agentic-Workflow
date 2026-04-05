# Guardian-Heal Rebaselined Architecture Hardening — Evidence File

**Branch:** `guardian-heal-orch`
**Base commit:** `fb5422e3dad13536a946fde1be9979266a229662`
**Date:** 2025-02-20

---

## Phase 1, Wave 1: Static Upward Import Isolation Audit

**Scope:** `agentic_core/L3_orchestration/` — all `.py` files scanned for
module-level static imports from higher layers (L4, L5, L6).

**Tool:** `grep_search` for patterns `from agentic_core.L[456]_` and
`import agentic_core.L[456]_` in `agentic_core/L3_orchestration/`.

**Result:** Zero new static upward imports found.

- `guardian_heal_orchestrator.py` imports only from L0 and L2 (downward/lateral).
- No `__init__.py` in L3 introduces upward imports.

**Verdict:** PASS — invariant preserved.

---

## Phase 1, Wave 2: Comprehensive Mutation Surface Audit

**Scope:** `agentic_core/L3_orchestration/` — scanned for direct mutation
primitives: `open(` with write mode, `write_text`, `write_bytes`, `unlink`,
`remove`, `rmtree`, `commit(`.

**Result:** Zero direct mutation primitives found outside `_wg.` delegation.

- `guardian_heal_orchestrator.py` uses `_wg.write_json()` and `_wg.remove_file()`
  exclusively — both route through L2 `write_gateway`.
- `assert_no_persistent_write("L0", "json.dump")` guard present (pre-existing
  layer label bug, but functionally correct).

**Verdict:** PASS — all mutation routes through L2 write gateway.

---

## Phase 1, Wave 3: Routing Containment & Execution Envelope

**Test file:** `tests/governance/test_guardian_heal_routing_containment.py`

**Tests (7 total, all AST-based static analysis):**

| # | Test | Invariant |
|---|------|-----------|
| 1 | `test_l3_init_no_upward_imports` | No upward imports in L3 `__init__.py` |
| 2 | `test_l3_scripts_init_no_upward_imports` | No upward imports in scripts `__init__.py` |
| 3 | `test_l3_engines_init_no_upward_imports` | No upward imports in engines `__init__.py` |
| 4 | `test_no_open_write_calls` | Zero direct `open(..., 'w')` in GHO |
| 5 | `test_no_direct_mutation_primitives` | No mutation primitives outside `_wg` |
| 6 | `test_write_gateway_is_sole_mutation_path` | `_wg.write_json` and `_wg.remove_file` present |
| 7 | `test_no_l5_imports_in_l3_init_files` | No L3 `__init__` imports L5 |

**Result:** 7/7 PASSED.

**Note:** Runtime routing tests (scan mode, dry-run, delegation) require
`L3_orchestration/__init__.py` which does not exist on main. This is a
pre-existing gap (the existing `test_guardian_heal_orchestrator.py` has the
same collection error). These tests will be added when the integration phase
creates the missing `__init__.py`.

**Verdict:** PASS — static containment verified.

---

## Phase 2, Wave 1: Silent Swallow Enforcement Semantics

**Test file:** `tests/governance/test_lazy_seam_silent_swallow.py`

**Tests (5 total):**

| # | Test | Invariant |
|---|------|-----------|
| 1 | `test_syntax_error_returns_empty` | `scan_file()` returns `[]` on SyntaxError |
| 2 | `test_io_error_returns_empty` | `scan_file()` returns `[]` on missing file |
| 3 | `test_valid_files_still_scanned` | Bad file does not prevent scanning good files |
| 4 | `test_no_files_created_on_syntax_error` | No mutation during swallowed exception |
| 5 | `test_corrupt_file_not_treated_as_compliant` | Swallow does not weaken enforcement |

**Result:** 5/5 PASSED.

**Verdict:** PASS — silent swallow semantics preserved without enforcement weakening.

---

## Phase 2, Wave 2: Deterministic Runtime Proof

**Method:** Run new governance tests twice, compare results.

**Run 1:** 12 passed, 0 failed, 0 errors (0.12s)
**Run 2:** 12 passed, 0 failed, 0 errors (0.11s)

**Verdict:** PASS — deterministic.

---

## Phase 2, Wave 3: Final Integrity Gate

### Full Test Suite

```
841 passed, 0 failed, 4 warnings in 70.53s
917 tests collected (including 76 deselected by default markers)
```

No regressions introduced.

### Test Collection Stability

```
917 tests collected (run 1)
917 tests collected (run 2)
```

Stable.

### Files Changed (additive only)

```
new file: tests/governance/test_guardian_heal_routing_containment.py
new file: tests/governance/test_lazy_seam_silent_swallow.py
new file: artifacts/evidence/guardian_heal_rebaselined_architecture_hardening.md
```

### Invariant Checklist

- [x] No new static upward imports in L3_orchestration
- [x] No direct mutation primitives outside L2 write gateway
- [x] All `_wg` calls route through L2 write gateway
- [x] No upward imports in any L3 `__init__.py`
- [x] Silent swallow returns empty list (not compliance)
- [x] No mutation during swallowed exception path
- [x] Enforcement semantics preserved despite swallow
- [x] Deterministic test results (12/12 x2)
- [x] Full suite regression-free (841 passed)
- [x] Additive-only changes (no legacy flow modification)
- [x] No `--no-verify` used

**Verdict:** ALL GATES PASS.
