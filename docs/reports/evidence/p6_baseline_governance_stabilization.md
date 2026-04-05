# Evidence: P6 — Baseline & Governance Stabilization

**Date:** 2026-02-19
**Objective:** Eliminate nondeterminism and transient-path contamination
in governance scanners/hooks; make enforcement deterministic and
location-insensitive.

---

## Scanners/Hook Entrypoints Audited

| # | Path | Issue Found |
|---|------|-------------|
| 1 | `ops_scripts/hooks/validate_folder_purity.py` | Substring filter, missing transient exclusions, unsorted rglob |
| 2 | `ops_scripts/ci/check_anti_patterns.py` | Substring filter, missing transient exclusions, unsorted rglob |
| 3 | `ops_scripts/ci/validate_import_dependencies.py` | Already parts-based; exclusion set adequate |
| 4 | `tests/governance/test_cross_layer_import_freeze.py` | No `__pycache__` exclusion in rglob |
| 5 | `tests/governance/test_upward_import_enforcement.py` | No `__pycache__` exclusion in 3 rglob scan functions, unsorted |

---

## Exclusions Applied

Transient directories now excluded (hard-coded set per scanner):

`__pycache__`, `.git`, `.venv`, `venv`, `.pytest_cache`,
`.pytest_tmp`, `.mypy_cache`, `.ruff_cache`, `.coverage`, `dist`,
`build`, `.tox`, `.nox`, `node_modules`, `archives`, `.backup`,
`_quarantine`

---

## Changes Made

### `ops_scripts/hooks/validate_folder_purity.py`
- Added `_EXCLUDE_DIRS` set and `_is_excluded()` helper (parts-based).
- Replaced substring `"tests" in str(py_file)` with parts-based check.
- Added `sorted()` to all 3 `rglob` calls for deterministic traversal.

### `ops_scripts/ci/check_anti_patterns.py`
- Added `_EXCLUDE_DIRS` set.
- Replaced `any(exclude_dir in str(f))` with parts-based
  `set(f.relative_to(...).parts) & _EXCLUDE_DIRS`.
- Added `sorted()` to all `rglob` calls.

### `tests/governance/test_cross_layer_import_freeze.py`
- Added `__pycache__` exclusion to `_scan_layer` rglob loop.

### `tests/governance/test_upward_import_enforcement.py`
- Added `__pycache__` exclusion + `sorted()` to 3 scan functions:
  `scan_all_layer_files`, `collect_lazy_upward_imports`,
  `detect_lazy_seam_violations`.

---

## COMMANDS RUN (exact)

```
python -m pytest tests/governance/test_cross_layer_import_freeze.py -q --override-ini="addopts=" --override-ini="log_cli=false" --no-header --tb=no
python -m pytest tests/governance/test_upward_import_enforcement.py -q --override-ini="addopts=" --override-ini="log_cli=false" --no-header --tb=no
python -m pytest tests/governance -q --override-ini="addopts=" --override-ini="log_cli=false" --no-header --tb=no
```

---

## OUTPUTS (exact)

### test_cross_layer_import_freeze.py

```
....
4 passed in 1.95s
```

### test_upward_import_enforcement.py

```
....................
20 passed in 12.84s
```

### Full governance suite

```
614 passed in 51.05s
```

---

## COMMIT

```
f31681a123897a6b17d021c0588141b371b45d0d
```

---

PASS: No transient-path baseline inflation; deterministic scanning
enforced.
