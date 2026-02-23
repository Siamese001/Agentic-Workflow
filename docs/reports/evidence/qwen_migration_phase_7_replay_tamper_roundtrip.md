# Phase 7 Evidence: Deterministic Replay Tamper Round-Trip Validation

## Scope
Phase 7 validates deterministic replay tamper round-trip with production-path verification.
Ensures tampered artifacts are rejected with stable 64-hex replay_hash deltas.

## CODE_COMMIT
9a60b006843eaff3551b1f25856328a12bd035bc

## EVIDENCE_COMMIT
PENDING

## FILES_CHANGED_CODE
tests/unit_min_deps/test_vllm_replay_tamper_roundtrip.py
tools/evidence/qwen_migration_phase7_replay_tamper_roundtrip_runner.py

## INSPECTED_FILES
tests/unit_min_deps/test_vllm_replay_tamper_roundtrip.py
tools/evidence/qwen_migration_phase7_replay_tamper_roundtrip_runner.py

## Inline Evidence Output (verbatim)

```
=== PHASE 7 EVIDENCE: REPLAY TAMPER ROUND-TRIP ===

TEST_SCOPE=TARGETED
TEST_TARGETS:
  [0]: ['python', '-m', 'pytest', '-q', 'tests/unit_min_deps/test_vllm_replay_tamper_roundtrip.py']
SCOPE_JUSTIFICATION:
  - test_vllm_replay_tamper_roundtrip.py added for production-path tamper validation
  - Existing replay validator tests impacted by Phase 7 tamper round-trip logic
  - Evidence runner validates deterministic tamper detection with inline proofs
PHASE_TOUCHED_FILES:
  tests/unit_min_deps/test_vllm_replay_tamper_roundtrip.py
  tools/evidence/qwen_migration_phase7_replay_tamper_roundtrip_runner.py

git status --porcelain (before):


=== PYTEST TARGET [0] ===
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 3 items

tests/unit_min_deps/test_vllm_replay_tamper_roundtrip.py::test_replay_tamper_round_trip PASSED [ 33%]
tests/unit_min_deps/test_vllm_replay_tamper_roundtrip.py::test_replay_tamper_determinism_re_run PASSED [ 66%]
tests/unit_min_deps/test_vllm_replay_tamper_roundtrip.py::test_negative_control_tamper_detection_disabled PASSED [100%]

============================ slowest 10 durations =============================
0.01s call     tests/unit_min_deps/test_vllm_replay_tamper_roundtrip.py::test_replay_tamper_round_trip

(8 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 3 passed in 0.05s ==============================
EXIT CODE: 0

=== PASS/FAIL/NEGATIVE CONTROL PROOFS ===
PASS SCENARIO:
  valid=True
  replay_hash=10d75d29ab8a6c87b9f64b93a44ffdd7bc04bb4969b20bab49552b27fa00d047
OK: PASS scenario asserted

FAIL SCENARIO:
  valid=False
  stored_replay_hash=10d75d29ab8a6c87b9f64b93a44ffdd7bc04bb4969b20bab49552b27fa00d047
  computed_replay_hash=09ad6fd1992eff4e2baa216d46affd020f8ae7aefc7301c0b5b3f396fea890b5
  differs_from_original=True
OK: FAIL scenario asserted

DETERMINISM RE-RUN LOCK:
  original_hash_deterministic=True
  tampered_hash_deterministic=True
OK: Determinism re-run lock asserted

NEGATIVE CONTROL:
  disabled_validator_passes=True
  production_validator_rejects=True
  OK: Enforcement check correctly fails when tamper detection disabled
OK: NEGATIVE CONTROL asserted

git status --porcelain (final):



=== RUNNER PROOF CHECKLIST ===
- [x] TEST_SCOPE=TARGETED enforced
- [x] All pytest targets executed and passed
- [x] PASS scenario: original artifact validates with production verifier
- [x] FAIL scenario: tampered artifact rejected with hash delta
- [x] DETERMINISM: re-run lock proven with identical hashes
- [x] NEGATIVE CONTROL: enforcement fails when tamper detection disabled
- [x] All 64-hex values regex-validated
- [x] Final git status clean

OK: All governance proofs asserted and passed
```

## Git Status
(clean)
