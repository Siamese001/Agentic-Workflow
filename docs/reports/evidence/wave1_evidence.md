# Wave 1 — CognitiveDispositionAgent Sync Wrapper

## Scope
Add synchronous `analyze_violation()` wrapper and batch async `analyze_violations()`
to `CognitiveDispositionAgent` so callers can invoke cognitive analysis without
managing `asyncio.run()` directly.

## CODE_COMMIT
f894a07a9d97001b2b727e3cccfb2188560ea657

## EVIDENCE_COMMIT
PENDING

## FILES_CHANGED_CODE
agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py
tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py

## FILES_CHANGED_EVIDENCE
docs/reports/evidence/wave1_evidence.md

## INSPECTED_FILES
agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py
tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py

## pytest wave1
$ python -m pytest -q --color=no tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py
collected 4 items

tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py::test_analyze_violation_sync_exists PASSED [ 25%]
tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py::test_analyze_violations_async_exists PASSED [ 50%]
tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py::test_analyze_violation_async_still_exists PASSED [ 75%]
tests/agentic_core/L5_safety/test_wave1_cda_sync_wrapper.py::test_get_analytics_still_exists PASSED [100%]

4 passed in 0.16s
