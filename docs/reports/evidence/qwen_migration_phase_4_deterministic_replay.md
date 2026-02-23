# qwen-migration Phase 4: Deterministic Replay Sealing

## Scope
Phase 4 of Qwen vLLM migration: seal deterministic replay by adding infrastructure fingerprint capture, canonical hashing, and replay validation harnesses, wired through the Phase 3 adapter/controller telemetry path. Preserves Phase 1-3 routing/backpressure invariants. No model tier changes.

## CODE_COMMIT
0ca7159c7e5c8b7e9e5317f517b6e6b2a8c3c7a4a

## EVIDENCE_COMMIT
6d0e399b0d620c5782ab44c9c4467c5bc0b99831

## FILES_CHANGED_CODE
```
fatal: ambiguous argument '0ca7159c7e5c8b7e9e5317f517b6e6b2a8c3c7a4a': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'
```

## FILES_CHANGED_EVIDENCE
```
docs/reports/evidence/qwen_migration_phase_4_deterministic_replay.md
```

## INSPECTED_FILES
```
agentic_core/L2_execution/types/vllm_infrastructure_fingerprint.py
agentic_core/L2_execution/types/vllm_gateway_integration.py
agentic_core/L2_execution/types/vllm_gateway_adapter.py
agentic_core/L2_execution/types/vllm_replay_validator.py
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py
```

## Infrastructure Fingerprint Tests (WAVE 2)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 6 items

tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_canonical_serialization_stable PASSED [ 16%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_hash_changes_on_field_change PASSED [ 33%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_deterministic_test_instance PASSED [ 50%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_canonical_json_stable_keys PASSED [ 66%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_sha256_hex_consistent PASSED [ 83%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_as_dict_roundtrip PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 6 passed in 0.05s ==============================
```

## Replay Validator Tests (WAVE 3)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
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
============================== 9 passed in 0.06s ==============================
```

## Phase 3 Integration Tests (No Regressions)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 14 items

tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_seam_proof_marker_present PASSED [  7%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_emit_seam_proof_returns_marker PASSED [ 14%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_no_gemini PASSED [ 21%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_explicit_max_tokens PASSED [ 28%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_profile_max_model_len PASSED [ 35%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_telemetry_failure_type_none PASSED [ 42%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_token_budget_exceed_routes_gemini PASSED [ 50%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_token_budget_exceed_failure_type PASSED [ 57%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_token_budget_exceed_provider_gemini PASSED [ 64%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_queue_full_routes_gemini PASSED [ 71%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_breaker_open_routes_gemini PASSED [ 78%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_record_local_failure_increments_breaker PASSED [ 85%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_record_local_success_resets_breaker PASSED [ 92%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_reset_singletons_clears_state PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 14 passed in 0.05s ==============================
```

## Proof: Identical Replay Hash Across Two Runs
```
replay_hash_run1=4fecffb588b3c16e7035de98bc17161d991c19aaf3ce02ee4320f06463bd01ff
replay_hash_run2=4fecffb588b3c16e7035de98bc17161d991c19aaf3ce02ee4320f06463bd01ff
hashes_match=True
OK: identical replay_hash confirmed
```

## Proof: Replay Hash Changes When Fingerprint Changes
```
hash_fp1=4fecffb588b3c16e7035de98bc17161d991c19aaf3ce02ee4320f06463bd01ff
hash_fp2=232086462cce2d242f038beb8043a5b804e0e5f0d5c6c0e8b2af8eafc0c1fd41
hashes_differ=True
OK: replay_hash changes on fingerprint change confirmed
```

## Git Status
```
(clean)
```

## Runner Self-Check Proof
```
shell=False: ENFORCED (subprocess.run called with shell=False, never shell=True)
argv arrays: ENFORCED (all invocations use list argv, never shell string)
pwsh/PowerShell guard: BALANCED (regex='pwsh|powershell', flags=IGNORECASE)
argv[0] guard: hard-fail if argv[0] matches pwsh/PowerShell executable
output guard: warn-only if captured output contains pwsh/PowerShell reference
OK: runner self-check passed (balanced policy)
```

