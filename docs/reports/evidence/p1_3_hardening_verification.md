# P1.3 Hardening Verification Evidence

**Commit:** `fafa5646e` (P1.3 hardening — activation gate Option A contract, save_file call path,
location-insensitive baseline)
**Branch:** `soccer_epiphanies`
**Date:** 2026-02-18
**Verifier:** Cursor Agent deterministic guardian run

---

## Objective 1 — Activation gate contract is module-level (Option A) and locked by AST tests

### Contract confirmed in source

`agentic_core/L5_safety/enforcement/activation_gate.py`:

- `assert_activation_allowed` defined at `col_offset == 0` (module-level `def`, line 43)
- Exported in `__all__` (lines 79-82)
- No `ActivationGate()` class — module-level function is the sole public API

`agentic_core/L2_execution/engines/validation_orchestrator.py`:

- Calls `_gate_mod.assert_activation_allowed(trace_id=trace_id)` — attribute access on module
  variable, confirming Option A usage pattern

### Test run

```text
Command: python -m pytest tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract -v
```

```text
collected 3 items

TestActivationGateModuleLevelContract::test_assert_activation_allowed_is_module_level_function PASSED
TestActivationGateModuleLevelContract::test_assert_activation_allowed_in_dunder_all PASSED
TestActivationGateModuleLevelContract::test_orchestrator_calls_assert_activation_allowed_on_gate_mod PASSED

3 passed, 4 warnings in 0.03s
```

**PASS — Objective 1 satisfied.**

---

## Objective 2 — Healing apply + rollback use direct L2.2 FileIo.save_file via _get_file_io()

### Static confirmation in source

`agentic_core/L2_execution/engines/validation_orchestrator.py`:

- `_get_file_io()` defined at module level (lines 41-44)
- `_file_io.save_file(fixed_code, file_path)` called at healing apply site
- `_file_io.save_file(original_code, file_path)` called at rollback site
- Zero occurrences of `open(..., "w")` anywhere in file

### Test run

```text
Command: python -m pytest tests/governance/test_healing_reentry.py::TestHealingWriteCallPath -v
```

```text
collected 2 items

TestHealingWriteCallPath::test_save_file_called_on_file_io_result PASSED
TestHealingWriteCallPath::test_no_open_write_anywhere_in_orchestrator PASSED

2 passed in 0.03s
```

**PASS — Objective 2 satisfied.**

---

## Objective 3 — Import baseline comparison is location-insensitive

### Implementation in ops_scripts/ci/validate_import_dependencies.py

`_normalize_baseline_key(entry)` strips both:

1. **Absolute path prefix** — converts to repo-relative forward-slash path (handles absolute vs
   relative path mismatch between baseline and hook invocation, and Windows vs POSIX separators)
2. **`Line N:` segment** — strips line number so import-line shifts don't produce false positives

Both `load_import_baseline()` and the `new_errors` comparison normalize via the same function.

### Upward import + lazy seam governance tests

```text
Command: python -m pytest tests/governance/test_upward_import_enforcement.py
         tests/governance/test_lazy_seam_allowlist.py -v
Result:  20 passed in 13.64s
```

### Line-shift simulation (Wave 3 manual proof)

Simulated a blank-line insertion above the `timeout_decorator` import in
`validation_orchestrator.py`, shifting it from Line 23 to Line 24.

**Before fix (original line-number-keyed behavior):**

```text
ERROR: New Import Dependency Errors Found
  validation_orchestrator.py: Line 24: Module '...timeout_decorator' not found
Found 1 new import errors (1 total, 2007 baselined)
```

**After fix (repo-relative path + line-number normalization):**

```text
Command: python ops_scripts/ci/validate_import_dependencies.py
         agentic_core\L2_execution\engines\validation_orchestrator.py
Output:  OK: 1 baselined errors, 0 new errors
```

Simulation reverted via `git checkout agentic_core\L2_execution\engines\validation_orchestrator.py`.

Clean state confirmed:

```text
Output:  OK: 1 baselined errors, 0 new errors
```

**PASS — Objective 3 satisfied. No baseline file modification required for harmless line movement.**

---

## Full test_healing_reentry.py suite

```text
Command: python -m pytest tests/governance/test_healing_reentry.py -v --tb=short
```

```text
collected 15 items

TestNoDirectL5Import::test_no_static_l5_import                                          PASSED
TestNoDirectL5Import::test_no_static_l3_import                                          PASSED
TestApprovalViaSeamStaticProof::test_load_activation_gate_helper_present                PASSED
TestApprovalViaSeamStaticProof::test_load_activation_gate_called_in_smart_fix           PASSED
TestApprovalViaSeamStaticProof::test_seam_exposes_load_activation_gate                  PASSED
TestApprovalViaSeamStaticProof::test_seam_uses_importlib_not_static                     PASSED
TestDirectL2WritesStaticProof::test_get_file_io_helper_present                          PASSED
TestDirectL2WritesStaticProof::test_get_file_io_called_in_smart_fix                     PASSED
TestDirectL2WritesStaticProof::test_no_bare_open_write_in_smart_fix                     PASSED
TestDirectL2WritesStaticProof::test_no_route_mutation_intent_in_orchestrator            PASSED
TestActivationGateModuleLevelContract::test_assert_activation_allowed_is_module_level_function PASSED
TestActivationGateModuleLevelContract::test_assert_activation_allowed_in_dunder_all     PASSED
TestActivationGateModuleLevelContract::test_orchestrator_calls_assert_activation_allowed_on_gate_mod PASSED
TestHealingWriteCallPath::test_save_file_called_on_file_io_result                       PASSED
TestHealingWriteCallPath::test_no_open_write_anywhere_in_orchestrator                   PASSED

15 passed, 4 warnings in 0.05s
```

---

## Invariant statements

| # | Invariant | Status |
|---|-----------|--------|
| 1 | `assert_activation_allowed` is module-level in `activation_gate.py` (Option A) | LOCKED |
| 2 | Orchestrator calls it via attribute access on module variable | LOCKED |
| 3 | Healing apply uses `_get_file_io().save_file(fixed_code, file_path)` | LOCKED |
| 4 | Healing rollback uses `_get_file_io().save_file(original_code, file_path)` | LOCKED |
| 5 | Zero bare `open(..., "w")` anywhere in `validation_orchestrator.py` | LOCKED |
| 6 | Import baseline comparison is repo-relative-path- and line-number-insensitive | LOCKED |
| 7 | No new governance violations introduced | CONFIRMED |
