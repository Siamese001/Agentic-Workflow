# Phase 8 Evidence: Canonical Payload Echo + Drift Detection

## Scope
Phase 8 strengthens replay validation by proving the exact canonical payload used for hashing is identical across re-runs, and that any canonical payload drift is detected deterministically.

## CODE_COMMIT
19f7d2ff5998a2fa7c84b6459498cfd9d22ff7f9

## EVIDENCE_COMMIT
f391d7675593370562ab86dfd51c54b7e2f47904

## FILES_CHANGED_CODE
agentic_core/L2_execution/types/vllm_replay_validator.py
tests/unit_min_deps/test_vllm_canonical_payload_lock.py
tools/evidence/qwen_migration_phase8_canonical_payload_lock_runner.py

## INSPECTED_FILES
agentic_core/L2_execution/types/vllm_replay_validator.py
tests/unit_min_deps/test_vllm_canonical_payload_lock.py
tools/evidence/qwen_migration_phase8_canonical_payload_lock_runner.py

## Inline Evidence Output (verbatim)

```
=== PHASE 8 EVIDENCE: CANONICAL PAYLOAD LOCK ===

TEST_SCOPE=TARGETED
TEST_TARGETS:
  [0]: ['python', '-m', 'pytest', '-q', 'tests/unit_min_deps/test_vllm_canonical_payload_lock.py']
  [1]: ['python', '-m', 'pytest', '-q', 'tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py']
SCOPE_JUSTIFICATION:
  - vllm_replay_validator.py extended with canonical_payload_hash method for Phase 8
  - test_vllm_canonical_payload_lock.py added for canonical payload stability validation
  - Evidence runner validates deterministic canonical payload echo with inline proofs
PHASE_TOUCHED_FILES:
  agentic_core/L2_execution/types/vllm_replay_validator.py
  tests/unit_min_deps/test_vllm_canonical_payload_lock.py
  tools/evidence/qwen_migration_phase8_canonical_payload_lock_runner.py

git status --porcelain (before):


=== PYTEST TARGET [0] ===
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_test_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4 items

tests/unit_min_deps/test_vllm_canonical_payload_lock.py::test_canonical_payload_stability_pass PASSED [ 25%]
tests/unit_min_deps/test_vllm_canonical_payload_lock.py::test_canonical_payload_drift_detection_fail PASSED [ 50%]
tests/unit_min_deps/test_vllm_canonical_payload_lock.py::test_canonical_payload_determinism_re_run PASSED [ 75%]
tests/unit_min_deps/test_vllm_canonical_payload_lock.py::test_negative_control_canonical_payload_disabled PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 4 passed in 0.05s ==============================
EXIT CODE: 0

=== PYTEST TARGET [1] ===
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
EXIT CODE: 0

=== PASS/FAIL/NEGATIVE CONTROL PROOFS ===
PASS SCENARIO:
  replay_hash=aa290aef7a6d4efca357525f949e1806be3b3c43945ea199869a367d096836df
OK: replay_hash validated as 64-hex: aa290aef7a6d4efca357525f949e1806be3b3c43945ea199869a367d096836df
  canonical_payload_hash=aa290aef7a6d4efca357525f949e1806be3b3c43945ea199869a367d096836df
OK: canonical_payload_hash validated as 64-hex: aa290aef7a6d4efca357525f949e1806be3b3c43945ea199869a367d096836df
  payload_digest_deterministic=True
OK: PASS scenario asserted

FAIL SCENARIO:
  original_replay_hash=aa290aef7a6d4efca357525f949e1806be3b3c43945ea199869a367d096836df
OK: original_replay_hash validated as 64-hex: aa290aef7a6d4efca357525f949e1806be3b3c43945ea199869a367d096836df
  mutated_replay_hash=c841b09df2388a3c460a4154efb0217b3a1bbee1cf140496f1ac75fd1f9d884e
OK: mutated_replay_hash validated as 64-hex: c841b09df2388a3c460a4154efb0217b3a1bbee1cf140496f1ac75fd1f9d884e
  original_canonical_payload_hash=aa290aef7a6d4efca357525f949e1806be3b3c43945ea199869a367d096836df
OK: original_canonical_payload_hash validated as 64-hex: aa290aef7a6d4efca357525f949e1806be3b3c43945ea199869a367d096836df
  mutated_canonical_payload_hash=c841b09df2388a3c460a4154efb0217b3a1bbee1cf140496f1ac75fd1f9d884e
OK: mutated_canonical_payload_hash validated as 64-hex: c841b09df2388a3c460a4154efb0217b3a1bbee1cf140496f1ac75fd1f9d884e
  drift_detected=True
OK: FAIL scenario asserted

DETERMINISM RE-RUN LOCK:
  pass_replay_deterministic=True
  pass_canonical_deterministic=True
  fail_replay_deterministic=True
  fail_canonical_deterministic=True
OK: Determinism re-run lock asserted

NEGATIVE CONTROL:
  disabled_validator_passes=True
  canonical_payload_accessible=True
  production_validator_valid=True
  OK: Enforcement check correctly fails when canonical payload validation disabled
OK: NEGATIVE CONTROL asserted
OK: All 6 required hash fields validated: ['canonical_payload_hash', 'mutated_canonical_payload_hash', 'mutated_replay_hash', 'original_canonical_payload_hash', 'original_replay_hash', 'replay_hash']

git status --porcelain (final):



=== RUNNER PROOF CHECKLIST ===
- [x] TEST_SCOPE=TARGETED enforced
- [x] All pytest targets executed and passed
- [x] PASS scenario: identical replay_hash and canonical_payload_hash
- [x] FAIL scenario: drift detected in both hashes
- [x] DETERMINISM: re-run lock proven with identical outputs
- [x] NEGATIVE CONTROL: enforcement fails when canonical payload disabled
- [x] Per-hash 64-hex validation lines printed for all fields
- [x] Final git status clean

OK: All governance proofs asserted and passed
```

## Git Status
(clean)
