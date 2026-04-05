# Phase 2: L3 Guardian-Heal Orchestrator Entrypoints — Evidence

## Commit

`TBD — will be populated after commit`

## Files Created/Modified

| Action   | File                                                        |
|----------|-------------------------------------------------------------|
| Created  | `ops_scripts/root_scripts/_guardian_heal_dry_run.py`        |
| Modified | `pyproject.toml` (added `[project.scripts]` entry)          |
| Modified | `agentic_core/L3_orchestration/__init__.py` (noqa: F401)    |
| Modified | `agentic_core/L3_orchestration/scripts/__init__.py` (noqa)  |
| Modified | `ops_scripts/hooks/import_dep_baseline.txt`                 |
| Created  | `artifacts/evidence/phase_1_guardian_heal_orchestrator_integration.md` |
| Created  | `artifacts/evidence/phase_2_guardian_heal_orchestrator_entrypoints.md` |

## Verification Commands

### 1. Import smoke test

```text
$ python -c "from agentic_core.L3_orchestration.scripts import run_pipeline; print('OK')"
OK
```

### 2. CLI smoke test

```text
$ python agentic_core/L3_orchestration/scripts/guardian_heal_orchestrator.py --help
usage: guardian_heal_orchestrator.py [-h] [--scan | --dry-run | --apply] ...
L0 Thin Router — Guardian-Dispatcher-Healer pipeline
```

### 3. pytest ssot_equivalence

```text
3 passed, 5 failed (pre-existing, same as Phase 1)
```

### 4. Import dependency validation (ops wrapper)

```text
$ python ops_scripts/ci/validate_import_dependencies.py ops_scripts/root_scripts/_guardian_heal_dry_run.py
OK: Import Dependency Validation Passed (1 files)
```

## Changes Summary

- Fixed Phase 1 gap: added `noqa: F401` to both `__init__.py` re-exports to prevent ruff from stripping them.
- Created `_guardian_heal_dry_run.py` ops wrapper mirroring `_ssot_dry_run.py` conventions.
- Added `[project.scripts]` console entrypoint in `pyproject.toml`.
- Updated `import_dep_baseline.txt` for pre-existing `.backup/vo_at_main.py` error.

## Converge Confidence

**88%**
