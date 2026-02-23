# qwen-migration Phase 3: Runtime Integration + Telemetry Enforcement

## Scope
Phase 3 of Qwen vLLM migration: wire Phase 1 (token budgeting + tiered routing) and Phase 2 (serving profiles + backpressure/circuit breaker) into a deterministic call-path controller with telemetry emission. No new model tiers. No 32B. L2 purity preserved.

## CODE_COMMIT
0ac6055179f393d05c7b0a4cdaede5edcd21c368

## EVIDENCE_COMMIT
f299108a9214d00478f10539006175595139fe21

## FILES_CHANGED_CODE
```
agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
agentic_core/L2_execution/types/vllm_gateway_adapter.py
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py
```

## FILES_CHANGED_EVIDENCE
```
docs/reports/evidence/qwen_migration_phase_3_runtime_integration.md
```

## INSPECTED_FILES
```
agentic_core/L2_execution/types/vllm_gateway_integration.py
agentic_core/L2_execution/types/vllm_gateway_adapter.py
agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py
```

## Profile Selection + Request Shaping Tests (WAVE 1)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 19 items

tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_low_severity_selects_fast_7b PASSED [  5%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_medium_severity_selects_fast_7b PASSED [ 10%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_high_severity_selects_strong_14b PASSED [ 15%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_low_severity_profile_model_id PASSED [ 21%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_high_severity_profile_model_id PASSED [ 26%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_profile_max_model_len_low PASSED [ 31%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_profile_max_model_len_high PASSED [ 36%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_has_explicit_max_tokens PASSED [ 42%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_max_tokens_matches_task_cap PASSED [ 47%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_temperature_is_zero PASSED [ 52%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_top_p_is_one PASSED [ 57%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_seed_is_fixed PASSED [ 63%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_uses_profile_max_model_len PASSED [ 68%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_14b_uses_14b_max_model_len PASSED [ 73%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_profile_name_recorded PASSED [ 78%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_undefined_task_class_raises PASSED [ 84%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_healing_json_artifact PASSED [ 89%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_is_deterministic PASSED [ 94%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_model_matches_profile PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 19 passed in 0.05s ==============================
```

## Backpressure + Circuit Breaker Integration Tests (WAVE 2)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 20 items

tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_starts_empty PASSED [  5%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_acquire_increments PASSED [ 10%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_release_decrements PASSED [ 15%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_full_acquire_fails PASSED [ 20%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_snapshot_is_immutable PASSED [ 25%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_full_snapshot PASSED [ 30%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_registry_creates_breaker_on_first_access PASSED [ 35%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_registry_per_tier_isolation PASSED [ 40%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_registry_record_success_resets PASSED [ 45%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_registry_reset_all PASSED [ 50%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_open_breaker_supersedes_empty_queue PASSED [ 55%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_open_breaker_supersedes_full_queue PASSED [ 60%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_full_queue_routes_to_gemini PASSED [ 65%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_timeout_routes_to_gemini PASSED [ 70%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_empty_queue_closed_breaker_local_path PASSED [ 75%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_breaker_open_no_local_attempt PASSED [ 80%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_breaker_closed_after_reset_allows_local PASSED [ 85%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_breaker_closed_to_open_transition PASSED [ 90%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_breaker_open_to_closed_via_success PASSED [ 95%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_breaker_does_not_open_below_threshold PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 20 passed in 0.05s ==============================
```

## Telemetry End-to-End Tests (WAVE 3)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 30 items

tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_telemetry_fields_present PASSED [  3%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_provider_is_local_model PASSED [  6%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_model_tier_is_fast PASSED [ 10%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_high_severity_model_tier_is_strong PASSED [ 13%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_token_budget_ok_true PASSED [ 16%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_failure_type_is_none PASSED [ 20%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_queue_depth_zero PASSED [ 23%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_breaker_state_closed PASSED [ 26%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_max_model_len_matches_profile PASSED [ 30%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_14b_max_model_len PASSED [ 33%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_telemetry_fields_present PASSED [ 36%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_provider_is_gemini PASSED [ 40%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_model_tier_is_remote PASSED [ 43%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_failure_type PASSED [ 46%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_token_budget_ok_false PASSED [ 50%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_local_request_is_none PASSED [ 53%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_queue_full_telemetry_fields_present PASSED [ 56%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_queue_full_provider_is_gemini PASSED [ 60%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_queue_full_failure_type PASSED [ 63%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_queue_full_queue_full_flag PASSED [ 66%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_queue_full_local_request_is_none PASSED [ 70%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_breaker_open_telemetry_fields_present PASSED [ 73%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_breaker_open_provider_is_gemini PASSED [ 76%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_breaker_open_failure_type PASSED [ 80%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_breaker_open_breaker_state_in_telemetry PASSED [ 83%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_breaker_open_local_request_is_none PASSED [ 86%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_telemetry_as_dict_key_order_stable PASSED [ 90%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_telemetry_deterministic_same_input PASSED [ 93%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_telemetry_prompt_tokens_estimated_consistent PASSED [ 96%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_telemetry_max_output_tokens_matches_cap PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 30 passed in 0.05s ==============================
```

## Gateway Adapter Seam Tests (WAVE 1 Phase 3.1)
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

## Seam Proof: SovereignLLMGateway Uses VLLMGatewayAdapter
```
OK: SovereignLLMGateway uses VLLMGatewayAdapter -> evaluate_gateway_call
OK: seam proof verified
```

## Token Budget Fallback Proof
```
route_to_gemini=True
failure_type=TOKEN_BUDGET_EXCEEDED
token_budget_ok=False
provider_selected=gemini-2.5-pro
model_tier=remote
prompt_tokens_estimated=7346
budget_margin_tokens=-10
OK: token budget fallback confirmed
```

## Queue Full Fallback Proof
```
route_to_gemini=True
failure_type=QUEUE_OVERFLOW
queue_depth=8
queue_full=True
provider_selected=gemini-2.5-pro
model_tier=remote
OK: queue full fallback confirmed
```

## Circuit Breaker Open Fallback Proof
```
route_to_gemini=True
failure_type=CIRCUIT_BREAKER_OPEN
breaker_state=OPEN
breaker_failure_count=3
provider_selected=gemini-2.5-pro
model_tier=remote
OK: circuit breaker open fallback confirmed
```

## Local Success Telemetry Proof
```
route_to_gemini=False
provider_selected=Qwen/Qwen2.5-7B-Instruct
model_tier=fast
token_budget_ok=True
failure_type=None
local_request.max_tokens=600
local_request.max_model_len=8192
local_request.temperature=0.0
local_request.profile_name=LOCAL_FAST_7B
OK: local success telemetry confirmed (explicit max_tokens + profile max_model_len)
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

## Git Status
```
(clean)
```

