# Evidence: P3.2 / P4.2 / P5.2 — Write Gateway Refactoring

**Date:** 2026-02-20
**Objective:** Eliminate durable mutation primitives outside L2_execution.

---

## Summary

| Metric | Before | After | Target | Status |
|--------|--------|-------|--------|--------|
| L3/L4/L5 mutation primitives | 456 | 7 | ≤10 | ✅ PASS |
| L6 mutation primitives | 13 | 0 | 0 | ✅ PASS |
| Governance tests passing | — | 28/28 | 28/28 | ✅ PASS |
| Syntax errors | — | 0 | 0 | ✅ PASS |

---

## Approach

1. Created `agentic_core/L2_execution/tools/write_gateway.py` — centralized
   durable mutation authority providing: `write_text`, `write_bytes`,
   `write_json`, `open_write`, `append_text`, `ensure_dir`, `remove_file`,
   `remove_dir`, `copy_file`, `move_path`, `rename_path`, `touch`.

2. Multi-pass automated refactoring (regex + AST):
   - Pass 1 (`_refactor_mutations.py`): Common single-line patterns.
   - Pass 2 (`_refactor_pass2.py`): Multi-line patterns.
   - Pass 3 (`_refactor_pass3.py`): AST-based source rewriting.
   - Pass 4 (`_refactor_pass4.py`): Line-by-line brute force (reverted due to nesting bugs).
   - Final AST pass (`_refactor_ast.py`): Clean single-pass using `ast.unparse`.
   - Targeted pass (`_refactor_remaining.py`): os.unlink/os.rename in control flow.
   - With-open pass (`_refactor_withopen.py`): `with open() + json.dump/f.write/f.writelines`.

3. Manual edits for complex multi-statement `with open()` blocks with guard
   assertions (`assert_no_persistent_write`).

4. Scanner (`_scan_v2.py`) updated to exclude `_wg.*` calls and
   `open(sys.stdout.fileno(), ...)` stdout reconfiguration.

---

## Remaining 7 Allowlisted Items (L3/L4/L5)

All 7 remaining hits are **legitimate cases requiring file handles** that
cannot be trivially replaced with `_wg` calls:

| # | File | Line | Pattern | Justification |
|---|------|------|---------|---------------|
| 1 | `L3_orchestration/engines/autonomous_execution_engine.py` | 125 | `json.dump` into `NamedTemporaryFile` | Atomic write via tempfile + os.replace |
| 2 | `L3_orchestration/scripts/guardian_heal_orchestrator.py` | 96 | `json.dump` into `NamedTemporaryFile` | Atomic write via tempfile + os.replace |
| 3 | `L4_state/enforcement/mission_historian.py` | 34 | `open("w")` + csv.writer | CSV writer requires file handle |
| 4 | `L4_state/enforcement/mission_historian.py` | 50 | `open("a")` + csv.writer | CSV writer requires file handle |
| 5 | `L4_state/enforcement/mission_historian_enforcer.py` | 34 | `open("w")` + csv.writer | Enforcer mirror of #3 |
| 6 | `L4_state/enforcement/mission_historian_enforcer.py` | 50 | `open("a")` + csv.writer | Enforcer mirror of #4 |
| 7 | `L5_safety/config/structure_blueprint/_simulate_verify.py` | 144 | `open("w")` | Test simulation writing intentional bad syntax |

---

## L6 — Strict Zero Achieved

The 2 former L6 hits were `open(sys.stdout.fileno(), mode="w", ...)` in
`reasoning_streamer.py` and `reasoning_streamer_enforcer.py`. These are
**stdout reconfiguration** (not durable file writes) and are now correctly
excluded by the scanner.

---

## Governance Tests Updated

| Test File | Tests | Status |
|-----------|-------|--------|
| `test_intent_emission_no_mutation.py` | 15 | ✅ All pass |
| `test_l6_purity.py` | 5 | ✅ All pass |
| `test_authority_boundaries.py` | 9 | ✅ All pass |
| **Total** | **29** | **✅ All pass** |

### P3.3 Enforcement Updates

- `test_intent_emission_no_mutation.py`: Ceiling-based ratchet replaced
  with explicit 7-item allowlist keyed by
  `(relative_path, enclosing_function, syntactic_fingerprint)`.
  Tests assert: total == 7, every hit allowlisted, every allowlist
  entry still present, hits == allowlist exactly.
- `test_l6_purity.py`: L6 ceiling = 0 (strict zero).
- `test_authority_boundaries.py`: `_wg` + `fileno()` exclusions.
- New negative regression: `test_new_open_write_in_l5_is_flagged`.

---

## COMMIT

```
7ebf7e9dbadb88df8093b98d9e8884c9a1c86a5d
```

---

## COMMANDS RUN (exact)

```
python -m pytest tests/governance/test_intent_emission_no_mutation.py -q --override-ini="addopts=" --override-ini="log_cli=false" --no-header --tb=no
python -m pytest tests/governance/test_l6_purity.py -q --override-ini="addopts=" --override-ini="log_cli=false" --no-header --tb=no
python -m pytest tests/governance/test_authority_boundaries.py -q --override-ini="addopts=" --override-ini="log_cli=false" --no-header --tb=no
```

---

## OUTPUTS (exact)

### test_intent_emission_no_mutation.py

```
...............
15 passed in 3.65s
```

### test_l6_purity.py

```
.....
5 passed in 0.09s
```

### test_authority_boundaries.py

```
.........
9 passed in 0.75s
```

---

## Files Modified (Source)

### Write Gateway (new)
- `agentic_core/L2_execution/tools/write_gateway.py`

### Refactored Layers (mutation primitives replaced with `_wg` calls)
- 124 files changed across L3, L4, L5, L6

### Governance Tests (updated)
- `tests/governance/test_intent_emission_no_mutation.py`
- `tests/governance/test_l6_purity.py`
- `tests/governance/test_authority_boundaries.py`

### Tooling (new)
- `_scan_v2.py` — mutation primitive scanner
- `_refactor_mutations.py` — pass 1 regex
- `_refactor_pass2.py` — pass 2 multi-line regex
- `_refactor_pass3.py` — pass 3 AST
- `_refactor_ast.py` — final AST pass
- `_refactor_remaining.py` — targeted AST pass
- `_refactor_withopen.py` — with-open pattern pass
