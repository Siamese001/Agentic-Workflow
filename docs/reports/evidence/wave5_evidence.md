# Wave 5 — LongPaths Advisory Suppression via Environment Guard

## Scope
Verify and enforce that the `AGENTIC_BYPASS_LONGPATHS_CHECK` environment guard
is present and adjacent to the `LongPathsEnabled` registry check in
`execute_ssot.py`. The guard was already present; this wave adds an AST-based
invariant test to prevent regression.

## CODE_COMMIT
4771b2da1d07503d9bedf3376adba920c28bc1cd

## EVIDENCE_COMMIT
PENDING

## FILES_CHANGED_CODE
tests/agentic_core/test_wave5_longpaths_guard.py

## FILES_CHANGED_EVIDENCE
docs/reports/evidence/wave5_evidence.md

## INSPECTED_FILES
agentic_core/L0_routing/scripts/execute_ssot.py
tests/agentic_core/test_wave5_longpaths_guard.py

## Guard Location
agentic_core/L0_routing/scripts/execute_ssot.py line ~1586:
  if os.getenv("AGENTIC_BYPASS_LONGPATHS_CHECK") == "1":
      logging.warning("AGENTIC_BYPASS_LONGPATHS_CHECK=1: skipping LongPathsEnabled hard-fail")

## pytest wave5
$ python -m pytest -q --color=no tests/agentic_core/test_wave5_longpaths_guard.py
collected 2 items

tests/agentic_core/test_wave5_longpaths_guard.py::test_longpaths_bypass_guard_present PASSED [ 50%]
tests/agentic_core/test_wave5_longpaths_guard.py::test_longpaths_guard_wraps_advisory PASSED [100%]

2 passed in 0.15s
