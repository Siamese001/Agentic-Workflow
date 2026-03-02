# Wave 3 — FilesystemSSOTReconcilerAgent logs/ Drift via force=True

## Scope
Add `force: bool = False` kwarg to `FilesystemSSOTReconcilerAgent.heal_repository()`.
When `force=True` the skip-gate is bypassed and `detect_root_drift()` is called,
archiving forbidden root folders (e.g. `logs/`). Wire `force=True` in `execute_ssot.py`
when healing is active.

## CODE_COMMIT
aec30ceb695b759cb00fb7f57a04b650aad9ae69

## EVIDENCE_COMMIT
PENDING

## FILES_CHANGED_CODE
agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py
tests/agentic_core/L5_safety/test_wave3_reconciler_force.py

## FILES_CHANGED_EVIDENCE
docs/reports/evidence/wave3_evidence.md

## INSPECTED_FILES
agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py
agentic_core/L0_routing/scripts/execute_ssot.py
tests/agentic_core/L5_safety/test_wave3_reconciler_force.py

## pytest wave3
$ python -m pytest -q --color=no tests/agentic_core/L5_safety/test_wave3_reconciler_force.py
collected 4 items

tests/agentic_core/L5_safety/test_wave3_reconciler_force.py::test_heal_repository_has_force_param PASSED [ 25%]
tests/agentic_core/L5_safety/test_wave3_reconciler_force.py::test_execute_ssot_passes_force_true PASSED [ 50%]
tests/agentic_core/L5_safety/test_wave3_reconciler_force.py::test_detect_root_drift_still_exists PASSED [ 75%]
tests/agentic_core/L5_safety/test_wave3_reconciler_force.py::test_logs_in_forbidden_root_folders PASSED [100%]

4 passed in 0.18s
