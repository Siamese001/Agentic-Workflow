# qwen-migration Phase 2: vLLM Serving Profile + Concurrency Hardening

## Scope
Phase 2 of Qwen vLLM migration: authoritative serving profiles for 32GB GPU, KV-cache stress validation, and backpressure + overload escalation enforcement. No 32B tier. No quantized tier. Phase 1 routing invariants preserved.

## CODE_COMMIT
9145d07ba71a421330fa38723ed0dceab3417fd9

## EVIDENCE_COMMIT
PENDING

## FILES_CHANGED_CODE
```
agentic_core/L2_execution/types/vllm_backpressure_types.py
agentic_core/L2_execution/types/vllm_concurrency_types.py
agentic_core/L2_execution/types/vllm_serving_profile_types.py
pytest.ini
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py
tests/unit_min_deps/test_testpaths_contract.py
tools/evidence/qwen_migration_phase2_evidence_runner.py
```

## INSPECTED_FILES
```
agentic_core/L2_execution/types/vllm_serving_profile_types.py
agentic_core/L2_execution/types/vllm_concurrency_types.py
agentic_core/L2_execution/types/vllm_backpressure_types.py
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py
```

## Serving Profile Constants Tests (WAVE 1)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 26 items

tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_fast_7b_model_id PASSED [  3%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_strong_14b_model_id PASSED [  7%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_fast_7b_max_model_len PASSED [ 11%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_strong_14b_max_model_len PASSED [ 15%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_fast_7b_max_num_seqs PASSED [ 19%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_strong_14b_max_num_seqs PASSED [ 23%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_gpu_memory_utilization PASSED [ 26%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_gpu_vram_gb PASSED [ 30%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_14b_ceiling PASSED [ 34%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_14b_max_model_len_within_ceiling PASSED [ 38%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_profile_local_fast_7b_is_valid PASSED [ 42%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_profile_local_strong_14b_is_valid PASSED [ 46%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_registry_contains_both_tiers PASSED [ 50%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_get_profile_local_fast PASSED [ 53%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_get_profile_local_strong PASSED [ 57%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_get_profile_unknown_raises PASSED [ 61%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_invalid_max_model_len_zero_raises PASSED [ 65%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_invalid_max_num_seqs_zero_raises PASSED [ 69%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_invalid_gpu_utilization_zero_raises PASSED [ 73%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_14b_exceeds_ceiling_raises PASSED [ 76%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_co_change_both_increase_raises PASSED [ 80%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_co_change_only_model_len_increase_ok PASSED [ 84%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_co_change_only_num_seqs_increase_ok PASSED [ 88%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_co_change_both_decrease_ok PASSED [ 92%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_no_32b_in_registry PASSED [ 96%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_no_quantized_in_registry PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 26 passed in 0.05s ==============================
```

## KV Cache Headroom Under Concurrency Tests (WAVE 2)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 14 items

tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_worst_case_prompt_passes_preflight PASSED [  7%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_no_truncation_at_ceiling PASSED [ 14%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_no_unexpected_fallback PASSED [ 21%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_no_absolute_exceeded PASSED [ 28%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_max_concurrency_within_budget PASSED [ 35%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_healing_json_artifact_passes PASSED [ 42%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_deterministic_repeated_run PASSED [ 50%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_14b_worst_case_prompt_passes_preflight PASSED [ 57%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_14b_no_truncation_at_ceiling PASSED [ 64%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_14b_no_unexpected_fallback PASSED [ 71%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_14b_max_concurrency_within_budget PASSED [ 78%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_14b_deterministic_repeated_run PASSED [ 85%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_output_cap_never_exceeds_absolute PASSED [ 92%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_stress_result_fields_present PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 14 passed in 0.05s ==============================
```

## Queue Overflow Fallback Tests (WAVE 3)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 10 items

tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_full_queue_escalates_to_gemini PASSED [ 10%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_full_queue_failure_type_is_queue_overflow PASSED [ 20%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_full_queue_model_id_is_gemini PASSED [ 30%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_full_queue_reason_is_queue_full PASSED [ 40%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_partial_queue_does_not_escalate PASSED [ 50%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_empty_queue_does_not_escalate PASSED [ 60%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_queue_at_max_minus_one_does_not_escalate PASSED [ 70%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_queue_depth_recorded_in_decision PASSED [ 80%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_max_queue_depth_constant PASSED [ 90%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_full_queue_repeated_is_deterministic PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 10 passed in 0.04s ==============================
```

## Queue Timeout Fallback Tests (WAVE 3)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 9 items

tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timed_out_queue_escalates_to_gemini PASSED [ 11%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timed_out_queue_failure_type_is_queue_overflow PASSED [ 22%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timed_out_queue_model_id_is_gemini PASSED [ 33%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timed_out_queue_reason_is_queue_timeout PASSED [ 44%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_within_timeout_does_not_escalate PASSED [ 55%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_zero_wait_does_not_escalate PASSED [ 66%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timeout_constant_value PASSED [ 77%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timed_out_queue_repeated_is_deterministic PASSED [ 88%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_queue_is_full_takes_priority_over_timeout PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 9 passed in 0.04s ==============================
```

## Circuit Breaker Backpressure Tests (WAVE 3)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 14 items

tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_breaker_starts_closed PASSED [  7%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_breaker_opens_after_threshold_failures PASSED [ 14%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_breaker_does_not_open_before_threshold PASSED [ 21%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_breaker_resets_on_success PASSED [ 28%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_breaker_reset_restores_closed PASSED [ 35%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_failure_threshold_constant PASSED [ 42%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_escalates_to_gemini PASSED [ 50%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_failure_type_is_circuit_breaker PASSED [ 57%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_model_id_is_gemini PASSED [ 64%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_reason PASSED [ 71%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_closed_breaker_empty_queue_does_not_escalate PASSED [ 78%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_takes_priority_over_empty_queue PASSED [ 85%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_takes_priority_over_full_queue PASSED [ 92%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_repeated_is_deterministic PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 14 passed in 0.04s ==============================
```

## Stress Test Demo
```
7B profile=LOCAL_FAST_7B requests=4 all_within_budget=True any_truncation=False any_unexpected_fallback=False
14B profile=LOCAL_STRONG_14B requests=2 all_within_budget=True any_truncation=False any_unexpected_fallback=False
OK: stress test demo passed
```

## Queue Overflow Escalation Demo
```
escalate_to_gemini=True
failure_type=VLLMFailureType.QUEUE_OVERFLOW
model_id=gemini-2.5-pro
reason=queue_full
OK: queue overflow escalation confirmed
```

## Circuit Breaker Escalation Demo
```
circuit_breaker_open=True
escalate_to_gemini=True
failure_type=VLLMFailureType.CIRCUIT_BREAKER_OPEN
model_id=gemini-2.5-pro
OK: circuit breaker escalation confirmed
```

## Runner Self-Check Proof
```
shell=False: ENFORCED (subprocess.run called with shell=False, never shell=True)
argv arrays: ENFORCED (all invocations use list argv, never shell string)
pwsh/PowerShell guard: ENFORCED (regex='pwsh|powershell', flags=IGNORECASE)
argv[0] guard: hard-fail if argv[0] matches pwsh/PowerShell
output guard: hard-fail if any captured output matches pwsh/PowerShell
OK: runner self-check passed
```

## Git Status
```

```

