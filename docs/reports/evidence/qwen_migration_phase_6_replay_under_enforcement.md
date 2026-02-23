# Phase 6 Evidence: Deterministic Replay Under Invariant Enforcement

## Scope
Phase 6 extends replay artifacts to include invariant violations in canonical form.
Replay hash computation includes violations for tamper detection.
Cross-phase integrity between Phase 4 (Replay) and Phase 5 (Invariants).

## CODE_COMMIT
039db9b6516f80655426621b22bc885e1fcbf1f6

## EVIDENCE_COMMIT
b807b96c972e4916914148f463c6180ca61d1c19

## FILES_CHANGED_CODE
agentic_core/L2_execution/types/vllm_replay_validator.py
tests/unit_min_deps/test_vllm_replay_with_violations.py
tools/evidence/qwen_migration_phase6_evidence_runner.py

## INSPECTED_FILES
agentic_core/L2_execution/types/vllm_replay_validator.py
tests/unit_min_deps/test_vllm_replay_with_violations.py
tools/evidence/qwen_migration_phase6_evidence_runner.py

## Inline Evidence Output (verbatim)

```
TEST_SCOPE=TARGETED
TEST_TARGETS:
  [0]: ['python', '-m', 'pytest', '-q', 'tests/unit_min_deps/test_vllm_replay_with_violations.py']
  [1]: ['python', '-m', 'pytest', '-q', 'tests\\agentic_core\\L2_execution\\types\\test_vllm_replay_validator.py']
  [2]: ['python', '-m', 'pytest', '-q', 'tests\\unit_min_deps\\test_vllm_replay_with_violations.py']
SCOPE_JUSTIFICATION:
  - vllm_replay_validator.py modified to include invariant violations in canonical form
  - test_vllm_replay_with_violations.py added to verify replay hash determinism with violations
  - Existing tests referencing canonical_response_hash impacted by Phase 6 changes
PHASE_TOUCHED_FILES:
  agentic_core/L2_execution/types/vllm_replay_validator.py
  tests/unit_min_deps/test_vllm_replay_with_violations.py
  tools/evidence/qwen_migration_phase6_evidence_runner.py

git status --porcelain (before):


=== PYTEST TARGET [0] ===
EXIT CODE: 0
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4 items

tests/unit_min_deps/test_vllm_replay_with_violations.py::test_replay_hash_identical_with_same_violations PASSED [ 25%]
tests/unit_min_deps/test_vllm_replay_with_violations.py::test_replay_hash_changes_when_violation_id_changes PASSED [ 50%]
tests/unit_min_deps/test_vllm_replay_with_violations.py::test_replay_hash_changes_when_violation_hash_changes PASSED [ 75%]
tests/unit_min_deps/test_vllm_replay_with_violations.py::test_replay_hash_deterministic_without_violations PASSED [100%]

============================ slowest 10 durations =============================
0.01s call     tests/unit_min_deps/test_vllm_replay_with_violations.py::test_replay_hash_identical_with_same_violations

(9 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 4 passed in 0.04s ==============================

=== PYTEST TARGET [1] ===
EXIT CODE: 0
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 9 items

tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_hash_deterministic_two_runs PASSED [ 11%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_hash_changes_on_fingerprint_change PASSED [ 22%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_hash_changes_on_prompt_change PASSED [ 33%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_validator_accepts_valid_artifact PASSED [ 44%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_validator_rejects_tampered_artifact PASSED [ 55%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_canonical_prompt_hash PASSED [ 66%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_canonical_local_request_hash PASSED [ 77%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_canonical_response_hash PASSED [ 88%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_artifact_with_none_local_request PASSED [100%]

============================ slowest 10 durations =============================
(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 9 passed in 0.05s ==============================

=== PYTEST TARGET [2] ===
EXIT CODE: 0
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4 items

tests/unit_min_deps/test_vllm_replay_with_violations.py::test_replay_hash_identical_with_same_violations PASSED [ 25%]
tests/unit_min_deps/test_vllm_replay_with_violations.py::test_replay_hash_changes_when_violation_id_changes PASSED [ 50%]
tests/unit_min_deps/test_vllm_replay_with_violations.py::test_replay_hash_changes_when_violation_hash_changes PASSED [ 75%]
tests/unit_min_deps/test_vllm_replay_with_violations.py::test_replay_hash_deterministic_without_violations PASSED [100%]

============================ slowest 10 durations =============================
0.01s call     tests/unit_min_deps/test_vllm_replay_with_violations.py::test_replay_hash_identical_with_same_violations

(9 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 4 passed in 0.04s ==============================

=== PASS/FAIL/NEGATIVE CONTROL PROOFS ===
PASS SCENARIO:
  route_to_gemini=False
  violations_count=0
OK: replay_hash (PASS) validated as 64-hex
  replay_hash=a23d51d0e33659182f52cfb6c28f16dc24d4bd4770f1cf0dbe49134093c5268b
  replay_hash_deterministic=True
OK: PASS scenario asserted

FAIL SCENARIO:
OK: violation_hash (FAIL) validated as 64-hex
  invariant_id=INV_REPLAY_HASH_PRESENT_WHEN_ENABLED
  severity=FAIL
  violation_hash=04c9ec6eb405b611b506e5947267660186eaaab6581c90c009e5c30a87dc2a6a
  route_to_gemini=True
  failure_type=None
  violations_count=1
OK: replay_hash (FAIL) validated as 64-hex
  replay_hash=d3acce5104524a8995cc58cd40ae9f8092c21e9209399880308de695e12c62ae
  replay_hash_deterministic=True
OK: FAIL scenario asserted

NEGATIVE CONTROL:
OK: replay_hash (tampered, normal) validated as 64-hex
  replay_hash_with_tamper=db9a3c141f619230c2a6cf288dd5443a380f9d0216710a771f6384cbf6dea074
  differs_from_fail_hash=True
OK: replay_hash (no violations) validated as 64-hex
  replay_hash_without_violations=0c82ce33639c8ddd86f3b87fb7b7b38aa0a837ed03633af930f8838a6c8f11cc
  tamper_detection_disabled=True
  OK: Enforcement check correctly fails when violations disabled
OK: NEGATIVE CONTROL asserted

git status --porcelain (final):


=== RUNNER PROOF CHECKLIST ===
- [x] TEST_SCOPE=TARGETED enforced
- [x] All pytest targets executed and passed
- [x] PASS scenario: route_to_gemini=False, violations_count=0, 64-hex hash
- [x] PASS scenario: determinism re-run identical
- [x] FAIL scenario: route_to_gemini=True, failure_type=None (invariant violations handled separately)
- [x] FAIL scenario: violations_count>=1, invariant_id present, severity=FAIL
- [x] FAIL scenario: 64-hex violation_hash and replay_hash validated
- [x] FAIL scenario: determinism re-run identical
- [x] NEGATIVE CONTROL: tamper detection disabled => hash unchanged
- [x] NEGATIVE CONTROL: enforcement check fails when tamper detection disabled
- [x] All 64-hex values regex-validated
- [x] Final git status clean

OK: All governance proofs asserted and passed
```

## Git Status
(clean)
