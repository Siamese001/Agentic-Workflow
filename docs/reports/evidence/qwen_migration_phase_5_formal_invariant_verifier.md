# Phase 5 Evidence: Formal Invariant Verifier

## Scope
Phase 5 implements runtime invariant verification at the execution boundary (Phase 3 adapter/controller seam).
All violations are deterministically serializable with canonical JSON and SHA256 hashing.
FAIL violations trigger Gemini fallback. Phase 1-4 behavior preserved.

## CODE_COMMIT
a4ef70c1b1ff9e4d2a0f2250ec47dcd2721251c4

## EVIDENCE_COMMIT
8b560d1bc5a88f946bcefc219530a2905eaee2ab

## FILES_CHANGED_CODE
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py
tools/evidence/qwen_migration_phase5_evidence_runner.py

## FILES_CHANGED_EVIDENCE
docs/reports/evidence/qwen_migration_phase_5_formal_invariant_verifier.md

## INSPECTED_FILES
agentic_core/L2_execution/types/vllm_invariant_contract_types.py
agentic_core/L2_execution/types/vllm_invariant_verifier_types.py
agentic_core/L2_execution/types/vllm_gateway_adapter_types.py
agentic_core/L2_execution/types/vllm_gateway_integration_types.py
tests/unit_min_deps/test_vllm_invariant_contract.py
tests/unit_min_deps/test_vllm_invariant_verifier.py
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py

## Unit_min_deps Tests (Invariant Contract)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 8 items

tests/unit_min_deps/test_vllm_invariant_contract.py::test_invariant_violation_canonical_json_stable PASSED [ 12%]
tests/unit_min_deps/test_vllm_invariant_contract.py::test_invariant_violation_canonical_json_sorted_keys PASSED [ 25%]
tests/unit_min_deps/test_vllm_invariant_contract.py::test_invariant_violation_hash_deterministic PASSED [ 37%]
tests/unit_min_deps/test_vllm_invariant_contract.py::test_invariant_violation_hash_changes_on_content_change PASSED [ 50%]
tests/unit_min_deps/test_vllm_invariant_contract.py::test_invariant_violation_as_dict_includes_hash PASSED [ 62%]
tests/unit_min_deps/test_vllm_invariant_contract.py::test_invariant_id_enum_values_stable PASSED [ 75%]
tests/unit_min_deps/test_vllm_invariant_contract.py::test_invariant_severity_enum_values PASSED [ 87%]
tests/unit_min_deps/test_vllm_invariant_contract.py::test_invariant_violation_frozen PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 8 passed in 0.04s ==============================
```

## Unit_min_deps Tests (Invariant Verifier)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 14 items

tests/unit_min_deps/test_vllm_invariant_verifier.py::test_verify_no_violations_on_valid_local_request PASSED [  7%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_missing_max_tokens PASSED [ 14%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_temperature_not_zero PASSED [ 21%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_missing_seed PASSED [ 28%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_missing_fingerprint_hash PASSED [ 35%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_gemini_fallback_requires_reason PASSED [ 42%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_gemini_fallback_with_reason_no_violation PASSED [ 50%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_multiple_violations_sorted_deterministically PASSED [ 57%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_violations_are_deterministic PASSED [ 64%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_replay_hash_missing_when_enabled PASSED [ 71%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_replay_hash_present_when_enabled_no_violation PASSED [ 78%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_replay_hash_disabled_no_violation PASSED [ 85%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_gpu_import_policy_violation PASSED [ 92%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_gpu_import_policy_ok_no_violation PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 14 passed in 0.04s ==============================
```

## Phase 5 Integration Tests (Invariant Enforcement)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 5 items

tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_local_success_with_zero_violations PASSED [ 20%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_with_fingerprint_produces_no_violations PASSED [ 40%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_result_has_invariant_violations_field PASSED [ 60%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_preserves_phase_1_4_behavior PASSED [ 80%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_fail_violation_triggers_gemini_with_violations_attached PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 5 passed in 0.06s ==============================
```

## Phase 1-4 Regression Tests
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 29 items

tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_canonical_serialization_stable PASSED [  3%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_hash_changes_on_field_change PASSED [  6%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_deterministic_test_instance PASSED [ 10%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_canonical_json_stable_keys PASSED [ 13%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_sha256_hex_consistent PASSED [ 17%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_as_dict_roundtrip PASSED [ 20%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_hash_deterministic_two_runs PASSED [ 24%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_hash_changes_on_fingerprint_change PASSED [ 27%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_hash_changes_on_prompt_change PASSED [ 31%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_validator_accepts_valid_artifact PASSED [ 34%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_validator_rejects_tampered_artifact PASSED [ 37%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_canonical_prompt_hash PASSED [ 41%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_canonical_local_request_hash PASSED [ 44%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_canonical_response_hash PASSED [ 48%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_artifact_with_none_local_request PASSED [ 51%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_seam_proof_marker_present PASSED [ 55%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_emit_seam_proof_returns_marker PASSED [ 58%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_no_gemini PASSED [ 62%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_explicit_max_tokens PASSED [ 65%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_profile_max_model_len PASSED [ 68%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_telemetry_failure_type_none PASSED [ 72%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_token_budget_exceed_routes_gemini PASSED [ 75%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_token_budget_exceed_failure_type PASSED [ 79%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_token_budget_exceed_provider_gemini PASSED [ 82%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_queue_full_routes_gemini PASSED [ 86%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_breaker_open_routes_gemini PASSED [ 89%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_record_local_failure_increments_breaker PASSED [ 93%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_record_local_success_resets_breaker PASSED [ 96%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_reset_singletons_clears_state PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 29 passed in 0.07s ==============================
```

## All L2 Execution Tests
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 649 items

tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_breaker_starts_closed PASSED [  0%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_breaker_opens_after_threshold_failures PASSED [  0%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_breaker_does_not_open_before_threshold PASSED [  1%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_breaker_resets_on_success PASSED [  1%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_breaker_reset_restores_closed PASSED [  2%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_failure_threshold_constant PASSED [  2%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_escalates_to_gemini PASSED [  3%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_failure_type_is_circuit_breaker PASSED [  3%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_model_id_is_gemini PASSED [  4%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_reason PASSED [  4%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_closed_breaker_empty_queue_does_not_escalate PASSED [  4%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_takes_priority_over_empty_queue PASSED [  5%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_takes_priority_over_full_queue PASSED [  5%]
tests/agentic_core/L2_execution/types/test_circuit_breaker_respects_backpressure.py::test_open_breaker_repeated_is_deterministic PASSED [  6%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_worst_case_prompt_passes_preflight PASSED [  6%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_no_truncation_at_ceiling PASSED [  7%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_no_unexpected_fallback PASSED [  7%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_no_absolute_exceeded PASSED [  8%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_max_concurrency_within_budget PASSED [  8%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_healing_json_artifact_passes PASSED [  8%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_7b_deterministic_repeated_run PASSED [  9%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_14b_worst_case_prompt_passes_preflight PASSED [  9%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_14b_no_truncation_at_ceiling PASSED [ 10%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_14b_no_unexpected_fallback PASSED [ 10%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_14b_max_concurrency_within_budget PASSED [ 11%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_14b_deterministic_repeated_run PASSED [ 11%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_output_cap_never_exceeds_absolute PASSED [ 12%]
tests/agentic_core/L2_execution/types/test_kv_cache_headroom_under_concurrency.py::test_stress_result_fields_present PASSED [ 12%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_full_queue_escalates_to_gemini PASSED [ 13%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_full_queue_failure_type_is_queue_overflow PASSED [ 13%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_full_queue_model_id_is_gemini PASSED [ 13%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_full_queue_reason_is_queue_full PASSED [ 14%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_partial_queue_does_not_escalate PASSED [ 14%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_empty_queue_does_not_escalate PASSED [ 15%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_queue_at_max_minus_one_does_not_escalate PASSED [ 15%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_queue_depth_recorded_in_decision PASSED [ 16%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_max_queue_depth_constant PASSED [ 16%]
tests/agentic_core/L2_execution/types/test_queue_overflow_fallback.py::test_full_queue_repeated_is_deterministic PASSED [ 17%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timed_out_queue_escalates_to_gemini PASSED [ 17%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timed_out_queue_failure_type_is_queue_overflow PASSED [ 17%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timed_out_queue_model_id_is_gemini PASSED [ 18%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timed_out_queue_reason_is_queue_timeout PASSED [ 18%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_within_timeout_does_not_escalate PASSED [ 19%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_zero_wait_does_not_escalate PASSED [ 19%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timeout_constant_value PASSED [ 20%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_timed_out_queue_repeated_is_deterministic PASSED [ 20%]
tests/agentic_core/L2_execution/types/test_queue_timeout_fallback.py::test_queue_is_full_takes_priority_over_timeout PASSED [ 21%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_fast_7b_model_id PASSED [ 21%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_strong_14b_model_id PASSED [ 21%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_fast_7b_max_model_len PASSED [ 22%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_strong_14b_max_model_len PASSED [ 22%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_fast_7b_max_num_seqs PASSED [ 23%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_local_strong_14b_max_num_seqs PASSED [ 23%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_gpu_memory_utilization PASSED [ 24%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_gpu_vram_gb PASSED [ 24%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_14b_ceiling PASSED [ 25%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_14b_max_model_len_within_ceiling PASSED [ 25%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_profile_local_fast_7b_is_valid PASSED [ 26%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_profile_local_strong_14b_is_valid PASSED [ 26%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_registry_contains_both_tiers PASSED [ 26%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_get_profile_local_fast PASSED [ 27%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_get_profile_local_strong PASSED [ 27%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_get_profile_unknown_raises PASSED [ 28%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_invalid_max_model_len_zero_raises PASSED [ 28%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_invalid_max_num_seqs_zero_raises PASSED [ 29%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_invalid_gpu_utilization_zero_raises PASSED [ 29%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_14b_exceeds_ceiling_raises PASSED [ 30%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_co_change_both_increase_raises PASSED [ 30%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_co_change_only_model_len_increase_ok PASSED [ 30%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_co_change_only_num_seqs_increase_ok PASSED [ 31%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_co_change_both_decrease_ok PASSED [ 31%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_no_32b_in_registry PASSED [ 32%]
tests/agentic_core/L2_execution/types/test_serving_profile_constants.py::test_no_quantized_in_registry PASSED [ 32%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_local_fast_routes_correctly_low_severity PASSED [ 33%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_local_fast_routes_correctly_medium_severity PASSED [ 33%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_local_strong_routes_correctly_high_severity PASSED [ 34%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_gemini_backstop_token_budget_exceeded PASSED [ 34%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_gemini_backstop_circuit_breaker_open PASSED [ 34%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_gemini_backstop_queue_overflow PASSED [ 35%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_gemini_backstop_gpu_health_failed PASSED [ 35%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_gemini_backstop_schema_validation_failed PASSED [ 36%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_gemini_backstop_low_confidence PASSED [ 36%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_failure_escalation_invariants_priority PASSED [ 37%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_gemini_backstop_always_present PASSED [ 37%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_no_32b_model_in_routing_module_ast PASSED [ 38%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_no_quantized_tier_in_routing_module_ast PASSED [ 38%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_no_gpu_imports_in_routing_module_ast PASSED [ 39%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_tiered_routing_decision_frozen PASSED [ 39%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_routing_deterministic_across_runs PASSED [ 39%]
tests/agentic_core/L2_execution/types/test_tiered_routing_without_32b.py::test_local_tier_only_when_budget_ok PASSED [ 40%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_passes_small_prompt PASSED [ 40%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_fails_oversized_prompt PASSED [ 41%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_token_budget_exceeded_failure_type PASSED [ 41%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_telemetry_fields_present PASSED [ 42%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_deterministic_across_runs PASSED [ 42%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_prompt_tokens_matches_estimator PASSED [ 43%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_output_tokens_matches_cap PASSED [ 43%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_budget_margin_correct PASSED [ 43%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_undefined_task_class_routes_gemini PASSED [ 44%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_result_frozen PASSED [ 44%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_contradictory_state_rejected PASSED [ 45%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_failed_without_failure_type_rejected PASSED [ 45%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_preflight_max_model_len_preserved PASSED [ 46%]
tests/agentic_core/L2_execution/types/test_token_budget_preflight_fallback.py::test_safety_margin_applied PASSED [ 46%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_constants_are_hardcoded PASSED [ 47%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_task_class_caps_within_absolute PASSED [ 47%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_healing_json_artifact_cap PASSED [ 47%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_patch_suggestion_cap PASSED [ 48%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_multi_file_summary_cap PASSED [ 48%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_undefined_task_class_returns_none PASSED [ 49%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_enforce_output_cap_raises_for_undefined PASSED [ 49%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_enforce_output_cap_clamps_to_task_cap PASSED [ 50%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_enforce_output_cap_exact_cap PASSED [ 50%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_no_local_request_exceeds_absolute PASSED [ 51%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_token_estimation_deterministic PASSED [ 51%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_token_estimation_empty_string PASSED [ 52%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_token_estimation_minimum_one PASSED [ 52%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_token_estimation_proportional PASSED [ 52%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_no_32b_model_in_constants PASSED [ 53%]
tests/agentic_core/L2_execution/types/test_token_cap_enforced.py::test_no_quantized_tier_in_constants PASSED [ 53%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_starts_empty PASSED [ 54%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_acquire_increments PASSED [ 54%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_release_decrements PASSED [ 55%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_full_acquire_fails PASSED [ 55%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_snapshot_is_immutable PASSED [ 56%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_controller_full_snapshot PASSED [ 56%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_registry_creates_breaker_on_first_access PASSED [ 56%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_registry_per_tier_isolation PASSED [ 57%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_registry_record_success_resets PASSED [ 57%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_registry_reset_all PASSED [ 58%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_open_breaker_supersedes_empty_queue PASSED [ 58%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_open_breaker_supersedes_full_queue PASSED [ 59%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_full_queue_routes_to_gemini PASSED [ 59%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_queue_timeout_routes_to_gemini PASSED [ 60%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_empty_queue_closed_breaker_local_path PASSED [ 60%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_breaker_open_no_local_attempt PASSED [ 60%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_breaker_closed_after_reset_allows_local PASSED [ 61%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_breaker_closed_to_open_transition PASSED [ 61%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_breaker_open_to_closed_via_success PASSED [ 62%]
tests/agentic_core/L2_execution/types/test_vllm_backpressure_integration.py::test_breaker_does_not_open_below_threshold PASSED [ 62%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_seam_proof_marker_present PASSED [ 63%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_emit_seam_proof_returns_marker PASSED [ 63%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_no_gemini PASSED [ 64%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_explicit_max_tokens PASSED [ 64%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_profile_max_model_len PASSED [ 65%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_local_success_telemetry_failure_type_none PASSED [ 65%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_token_budget_exceed_routes_gemini PASSED [ 65%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_token_budget_exceed_failure_type PASSED [ 66%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_token_budget_exceed_provider_gemini PASSED [ 66%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_queue_full_routes_gemini PASSED [ 67%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_breaker_open_routes_gemini PASSED [ 67%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_record_local_failure_increments_breaker PASSED [ 68%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_adapter_record_local_success_resets_breaker PASSED [ 68%]
tests/agentic_core/L2_execution/types/test_vllm_gateway_adapter.py::test_reset_singletons_clears_state PASSED [ 69%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_canonical_serialization_stable PASSED [ 69%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_hash_changes_on_field_change PASSED [ 69%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_deterministic_test_instance PASSED [ 70%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_canonical_json_stable_keys PASSED [ 70%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_sha256_hex_consistent PASSED [ 71%]
tests/agentic_core/L2_execution/types/test_vllm_infrastructure_fingerprint.py::test_fingerprint_as_dict_roundtrip PASSED [ 71%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_local_success_with_zero_violations PASSED [ 72%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_with_fingerprint_produces_no_violations PASSED [ 72%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_result_has_invariant_violations_field PASSED [ 73%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_preserves_phase_1_4_behavior PASSED [ 73%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_fail_violation_triggers_gemini_with_violations_attached PASSED [ 73%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_low_severity_selects_fast_7b PASSED [ 74%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_medium_severity_selects_fast_7b PASSED [ 74%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_high_severity_selects_strong_14b PASSED [ 75%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_low_severity_profile_model_id PASSED [ 75%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_high_severity_profile_model_id PASSED [ 76%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_profile_max_model_len_low PASSED [ 76%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_profile_max_model_len_high PASSED [ 77%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_has_explicit_max_tokens PASSED [ 77%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_max_tokens_matches_task_cap PASSED [ 78%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_temperature_is_zero PASSED [ 78%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_top_p_is_one PASSED [ 78%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_seed_is_fixed PASSED [ 79%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_uses_profile_max_model_len PASSED [ 79%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_14b_uses_14b_max_model_len PASSED [ 80%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_profile_name_recorded PASSED [ 80%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_undefined_task_class_raises FAILED [ 81%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_healing_json_artifact PASSED [ 81%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_is_deterministic PASSED [ 82%]
tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_model_matches_profile PASSED [ 82%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_hash_deterministic_two_runs PASSED [ 82%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_hash_changes_on_fingerprint_change PASSED [ 83%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_hash_changes_on_prompt_change PASSED [ 83%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_validator_accepts_valid_artifact PASSED [ 84%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_validator_rejects_tampered_artifact PASSED [ 84%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_canonical_prompt_hash PASSED [ 85%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_canonical_local_request_hash PASSED [ 85%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_canonical_response_hash PASSED [ 86%]
tests/agentic_core/L2_execution/types/test_vllm_replay_validator.py::test_replay_artifact_with_none_local_request PASSED [ 86%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_telemetry_fields_present PASSED [ 86%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_provider_is_local_model PASSED [ 87%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_model_tier_is_fast PASSED [ 87%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_high_severity_model_tier_is_strong PASSED [ 88%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_token_budget_ok_true PASSED [ 88%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_failure_type_is_none PASSED [ 89%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_queue_depth_zero PASSED [ 89%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_breaker_state_closed PASSED [ 90%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_max_model_len_matches_profile PASSED [ 90%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_local_success_14b_max_model_len PASSED [ 91%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_telemetry_fields_present PASSED [ 91%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_provider_is_gemini PASSED [ 91%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_model_tier_is_remote PASSED [ 92%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_failure_type PASSED [ 92%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_token_budget_ok_false PASSED [ 93%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_token_budget_exceed_local_request_is_none PASSED [ 93%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_queue_full_telemetry_fields_present PASSED [ 94%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_queue_full_provider_is_gemini PASSED [ 94%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_queue_full_failure_type PASSED [ 95%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_queue_full_queue_full_flag PASSED [ 95%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_queue_full_local_request_is_none PASSED [ 95%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_breaker_open_telemetry_fields_present PASSED [ 96%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_breaker_open_provider_is_gemini PASSED [ 96%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_breaker_open_failure_type PASSED [ 97%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_breaker_open_breaker_state_in_telemetry PASSED [ 97%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_breaker_open_local_request_is_none PASSED [ 98%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_telemetry_as_dict_key_order_stable FAILED [ 98%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_telemetry_deterministic_same_input PASSED [ 99%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_telemetry_prompt_tokens_estimated_consistent PASSED [ 99%]
tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_telemetry_max_output_tokens_matches_cap PASSED [100%]

================================== FAILURES ===================================
_______________ test_shaped_request_undefined_task_class_raises _______________
tests\agentic_core\L2_execution\types\test_vllm_profile_selection.py:127: in test_shaped_request_undefined_task_class_raises
    shape_local_request("hello", "undefined_class", PROFILE_LOCAL_FAST_7B)
agentic_core\L2_execution\types\vllm_gateway_integration.py:96: in shape_local_request
    max_tokens = min(max_output, profile.max_model_len)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   TypeError: '<' not supported between instances of 'int' and 'NoneType'
___________________ test_telemetry_as_dict_key_order_stable ___________________
tests\agentic_core\L2_execution\types\test_vllm_telemetry_end_to_end.py:303: in test_telemetry_as_dict_key_order_stable
    assert keys[-1] == "failure_type"
E   AssertionError: assert 'fingerprint_hash' == 'failure_type'
E
E     - failure_type
E     + fingerprint_hash
============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
=========================== short test summary info ===========================
FAILED tests/agentic_core/L2_execution/types/test_vllm_profile_selection.py::test_shaped_request_undefined_task_class_raises
FAILED tests/agentic_core/L2_execution/types/test_vllm_telemetry_end_to_end.py::test_telemetry_as_dict_key_order_stable
======================== 2 failed, 221 passed in 0.28s ========================
```

NOTE: Pre-existing test failures in test_vllm_profile_selection.py and test_vllm_telemetry_end_to_end.py
are not related to Phase 5 invariant verifier changes.

## Governance Tests (Pre-existing Violations)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 726 items

tests/governance/test_agent_heal_audit.py::TestDeterminism::test_byte_identical_json_runs PASSED [  0%]
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_deterministic_ordering PASSED [  0%]
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_no_nondeterministic_fields PASSED [  0%]
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_top_level_schema PASSED [  0%]
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_result_item_schema PASSED [  0%]
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_summary_schema PASSED [  0%]
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_controlled_fixture_scanning PASSED [  0%]
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_agent_naming_detection PASSED [  1%]
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_base_class_name_extraction PASSED [  1%]
tests/governance/test_agent_heal_audit.py::TestNoRuntimeImports::test_source_code_imports PASSED [  1%]
tests/governance/test_agent_heal_audit.py::TestNoRuntimeImports::test_stdlib_only_imports PASSED [  1%]
tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_generation PASSED [  1%]
tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_determinism PASSED [  1%]
tests/governance/test_authority_boundaries.py::TestMutationAuthorityBoundary::test_l2_execution_exists_and_has_mutations PASSED [  1%]
tests/governance/test_authority_boundaries.py::TestMutationAuthorityBoundary::test_l1_has_zero_mutation_primitives PASSED [  2%]
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L3_orchestration] PASSED [  2%]
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L4_state] PASSED [  2%]
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L5_safety] PASSED [  2%]
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L6_observability] PASSED [  2%]
tests/governance/test_authority_boundaries.py::TestAuthorityNegativeRegression::test_detects_l2_fileio_import PASSED [  2%]
tests/governance/test_authority_boundaries.py::TestAuthorityNegativeRegression::test_detects_l2_save_file_import PASSED [  2%]
tests/governance/test_authority_boundaries.py::TestAuthorityNegativeRegression::test_ignores_non_mutation_l2_import PASSED [  3%]
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_dict_10x_identical PASSED [  3%]
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_nested_dict_10x_identical PASSED [  3%]
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_tuple_input_10x_identical PASSED [  3%]
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_empty_dict_10x_identical PASSED [  3%]
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_none_values_10x_identical PASSED [  3%]
tests/governance/test_canonical_serializer.py::TestFloatPrecision::test_float_normalized PASSED [  3%]
tests/governance/test_canonical_serializer.py::TestFloatPrecision::test_float_round_trip PASSED [  3%]
tests/governance/test_canonical_serializer.py::TestFloatPrecision::test_float_trailing_zeros PASSED [  4%]
tests/governance/test_canonical_serializer.py::TestTupleNormalization::test_tuple_becomes_list PASSED [  4%]
tests/governance/test_canonical_serializer.py::TestTupleNormalization::test_nested_tuple PASSED [  4%]
tests/governance/test_canonical_serializer.py::TestNullEncoding::test_none_encoded PASSED [  4%]
tests/governance/test_canonical_serializer.py::TestNullEncoding::test_none_not_omitted PASSED [  4%]
tests/governance/test_canonical_serializer.py::TestSortedKeys::test_top_level_sorted PASSED [  4%]
tests/governance/test_canonical_serializer.py::TestSortedKeys::test_nested_sorted PASSED [  4%]
tests/governance/test_canonical_serializer.py::TestCrossObjectConsistency::test_audit_and_intent_same_serializer PASSED [  5%]
tests/governance/test_canonical_serializer.py::TestASTNoDirectJsonDumps::test_no_json_dumps_in_audit_log PASSED [  5%]
tests/governance/test_canonical_serializer.py::TestASTNoDirectJsonDumps::test_no_json_dumps_in_canonical_serializer PASSED [  5%]
tests/governance/test_canonical_serializer.py::TestASTNoDirectJsonDumps::test_no_json_import_in_audit_log PASSED [  5%]
tests/governance/test_cross_layer_import_freeze.py::TestCrossLayerImportFreeze::test_no_new_violations FAILED [  5%]
tests/governance/test_cross_layer_import_freeze.py::TestCrossLayerImportFreeze::test_baseline_not_stale PASSED [  5%]
tests/governance/test_cross_layer_import_freeze.py::TestRegressionDetection::test_synthetic_violation_detected PASSED [  5%]
tests/governance/test_cross_layer_import_freeze.py::TestRegressionDetection::test_persistence_client_detected PASSED [  6%]
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_blocks_write_under_agentic_core PASSED [  6%]
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_blocks_rename_under_agentic_core PASSED [  6%]
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_allows_write_outside_agentic_core PASSED [  6%]
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_respects_override_flag PASSED [  6%]
tests/governance/test_execute_ssot_mutation_fence.py::TestStartupFenceSelfTest::test_startup_self_test_aborts_if_fence_inactive PASSED [  6%]
tests/governance/test_execute_ssot_mutation_fence.py::TestStartupFenceSelfTest::test_startup_self_test_passes_if_fence_active PASSED [  6%]
tests/governance/test_execute_ssot_mutation_fence.py::TestImportPreflight::test_import_preflight_fails_fast_with_actionable_message PASSED [  7%]
tests/governance/test_execute_ssot_mutation_fence.py::TestImportPreflight::test_import_preflight_passes_when_symbols_exist PASSED [  7%]
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootPolicy::test_default_policy_has_correct_immutable_roots PASSED [  7%]
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootPolicy::test_default_policy_log_path_outside_immutable_roots PASSED [  7%]
tests/governance/test_guardian_heal_routing_containment.py::TestNoNewUpwardImportsInInitFiles::test_l3_init_no_upward_imports PASSED [  7%]
tests/governance/test_guardian_heal_routing_containment.py::TestNoNewUpwardImportsInInitFiles::test_l3_scripts_init_no_upward_imports PASSED [  7%]
tests/governance/test_guardian_heal_routing_containment.py::TestNoNewUpwardImportsInInitFiles::test_l3_engines_init_no_upward_imports PASSED [  7%]
tests/governance/test_guardian_heal_routing_containment.py::TestGHONoDirectWrites::test_no_open_write_calls PASSED [  7%]
tests/governance/test_guardian_heal_routing_containment.py::TestGHOMutationDelegation::test_no_direct_mutation_primitives PASSED [  8%]
tests/governance/test_guardian_heal_routing_containment.py::TestGHOMutationDelegation::test_write_gateway_is_sole_mutation_path PASSED [  8%]
tests/governance/test_guardian_heal_routing_containment.py::TestDirectoryWideUpwardImportFreeze::test_no_l5_imports_in_l3_init_files PASSED [  8%]
tests/governance/test_hash_chain_audit_log.py::TestGenesisRule::test_first_entry_has_genesis_previous_hash PASSED [  8%]
tests/governance/test_hash_chain_audit_log.py::TestGenesisRule::test_first_entry_has_index_zero PASSED [  8%]
tests/governance/test_hash_chain_audit_log.py::TestGenesisRule::test_genesis_hash_is_literal_string PASSED [  8%]
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_single_entry_verifies PASSED [  8%]
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_multi_entry_chain_verifies PASSED [  9%]
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_chain_links_previous_hash PASSED [  9%]
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_empty_log_verifies PASSED [  9%]
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_each_entry_hash_is_sha256 PASSED [  9%]
tests/governance/test_hash_chain_audit_log.py::TestChainBreakDetection::test_tampered_hash_detected
-------------------------------- live log call --------------------------------
2026-02-23 13:38:07 [   ERROR] agentic_core.L2_execution.audit.hash_chain_audit_log: [audit] hash mismatch at entry 1
PASSED                                                                   [  9%]
tests/governance/test_hash_chain_audit_log.py::TestSeal::test_seal_returns_root_hash PASSED [  9%]
tests/governance/test_hash_chain_audit_log.py::TestSeal::test_append_after_seal_raises PASSED [  9%]
tests/governance/test_hash_chain_audit_log.py::TestSeal::test_seal_empty_log_raises PASSED [ 10%]
tests/governance/test_hash_chain_audit_log.py::TestEntryImmutability::test_cannot_mutate_entry_field PASSED [ 10%]
tests/governance/test_hash_chain_audit_log.py::TestHashDeterminism::test_entry_hash_is_deterministic PASSED [ 10%]
tests/governance/test_hash_chain_audit_log.py::TestHashDeterminism::test_verify_passes_on_correct_hash PASSED [ 10%]
tests/governance/test_hash_chain_audit_log.py::TestLogProperties::test_length_tracks_entries PASSED [ 10%]
tests/governance/test_hash_chain_audit_log.py::TestLogProperties::test_chain_root_none_when_empty PASSED [ 10%]
tests/governance/test_hash_chain_audit_log.py::TestLogProperties::test_entries_returns_tuple PASSED [ 10%]
tests/governance/test_heal_escalation_flag_contract.py::TestFlagDefaultOff::test_no_escalation_log_without_env_var PASSED [ 11%]
tests/governance/test_heal_escalation_flag_contract.py::TestFlagDefaultOff::test_observer_not_invoked_without_env_var PASSED [ 11%]
tests/governance/test_heal_escalation_flag_contract.py::TestObserverSeamSafety::test_observer_default_is_none_at_import PASSED [ 11%]
tests/governance/test_heal_escalation_flag_contract.py::TestObserverSeamSafety::test_observer_not_reassigned_at_module_scope PASSED [ 11%]
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_default_off PASSED [ 11%]
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_enabled_no_caller PASSED [ 11%]
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_enabled_with_caller PASSED [ 11%]
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_logging PASSED [ 11%]
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_no_routed_model PASSED [ 12%]
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_output_unchanged PASSED [ 12%]
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingDefaultOff::test_router_seam_not_invoked_when_disabled PASSED [ 12%]
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingDefaultOff::test_no_routed_model_log_when_disabled PASSED [ 12%]
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledLow::test_router_invoked_with_low_tier PASSED [ 12%]
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledLow::test_routed_model_log_contains_local_low PASSED [ 12%]
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledHigh::test_router_invoked_with_high_tier PASSED [ 12%]
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledHigh::test_routed_model_log_contains_local_high PASSED [ 13%]
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagDefaultOff::test_no_escalation_log_when_disabled PASSED [ 13%]
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagDefaultOff::test_observer_not_invoked_when_disabled PASSED [ 13%]
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagEnabled::test_escalation_log_when_enabled PASSED [ 13%]
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagEnabled::test_observer_invoked_when_enabled PASSED [ 13%]
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_stdlib_only_imports PASSED [ 13%]
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_no_network_model_keywords PASSED [ 13%]
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_no_banned_string_literals PASSED [ 14%]
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_decide_reasoning_tier_is_invoked PASSED [ 14%]
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_policy_decision_is_logged PASSED [ 14%]
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_output_unchanged_by_policy_integration PASSED [ 14%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_high_boundary PASSED [ 14%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_high_boundary_exact PASSED [ 14%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_medium_boundary PASSED [ 14%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_medium_boundary_just_below PASSED [ 15%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_low_values PASSED [ 15%]
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_validation_errors PASSED [ 15%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_high_confidence_auto_proceed PASSED [ 15%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_high_confidence_boundary_exact PASSED [ 15%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_medium_confidence_llm_enabled_judicious_gate_met PASSED [ 15%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_medium_confidence_llm_enabled_judicious_gate_not_met PASSED [ 15%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_medium_confidence_llm_disabled PASSED [ 15%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_enabled_complexity_gate PASSED [ 16%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_enabled_failure_gate PASSED [ 16%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_enabled_judicious_gate_not_met PASSED [ 16%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_disabled PASSED [ 16%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_determinism PASSED [ 16%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_confidence_value PASSED [ 16%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_task_complexity PASSED [ 16%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_safety_risk PASSED [ 17%]
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_prior_failures PASSED [ 17%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_trivial_rule_returns_low_even_with_low_confidence PASSED [ 17%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_trivial_rule_order PASSED [ 17%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_confidence_low PASSED [ 17%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_complexity_high PASSED [ 17%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_safety_risk_high PASSED [ 17%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_retry_count_high PASSED [ 18%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_default_low PASSED [ 18%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_determinism PASSED [ 18%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_validation_task_complexity PASSED [ 18%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_validation_safety_risk PASSED [ 18%]
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_validation_retry_count PASSED [ 18%]
tests/governance/test_heal_policy_wiring.py::TestEnableLlmHardGate::test_enable_llm_false_high_confidence_proceeds_no_tier PASSED [ 18%]
tests/governance/test_heal_policy_wiring.py::TestEnableLlmHardGate::test_enable_llm_false_medium_confidence_blocked PASSED [ 19%]
tests/governance/test_heal_policy_wiring.py::TestEnableLlmHardGate::test_enable_llm_false_low_confidence_blocked PASSED [ 19%]
tests/governance/test_heal_policy_wiring.py::TestTierSelection::test_medium_confidence_selects_low_tier PASSED [ 19%]
tests/governance/test_heal_policy_wiring.py::TestTierSelection::test_low_confidence_selects_high_tier PASSED [ 19%]
tests/governance/test_heal_policy_wiring.py::TestTierSelection::test_low_confidence_with_prior_failures_selects_high_tier PASSED [ 19%]
tests/governance/test_heal_policy_wiring.py::TestJudiciousGate::test_medium_confidence_low_complexity_blocked PASSED [ 19%]
tests/governance/test_heal_policy_wiring.py::TestJudiciousGate::test_low_confidence_low_complexity_no_failures_blocked PASSED [ 19%]
tests/governance/test_heal_policy_wiring.py::TestNoNetworkCalls::test_standard_heal_no_llm_call_when_disabled PASSED [ 19%]
tests/governance/test_heal_policy_wiring.py::TestNoNetworkCalls::test_standard_heal_high_confidence_no_llm_call PASSED [ 20%]
tests/governance/test_heal_policy_wiring.py::TestDeterministicRefusal::test_blocked_result_contains_policy_decision PASSED [ 20%]
tests/governance/test_heal_policy_wiring.py::TestDeterministicRefusal::test_blocked_result_is_deterministic PASSED [ 20%]
tests/governance/test_heal_policy_wiring.py::TestCanonicalSeamEnforcement::test_direct_llm_call_without_seam_fails PASSED [ 20%]
tests/governance/test_heal_policy_wiring.py::TestCanonicalSeamEnforcement::test_standard_heal_sets_capability_token PASSED [ 20%]
tests/governance/test_heal_policy_wiring.py::TestCanonicalSeamEnforcement::test_llm_escalation_only_via_standard_heal PASSED [ 20%]
tests/governance/test_heal_policy_wiring.py::TestPolicyDecisionRecord::test_policy_decision_record_schema PASSED [ 20%]
tests/governance/test_heal_policy_wiring.py::TestPolicyDecisionRecord::test_policy_decision_record_deterministic_hash PASSED [ 21%]
tests/governance/test_heal_policy_wiring.py::TestPolicyDecisionRecord::test_standard_heal_emits_policy_record
-------------------------------- live log call --------------------------------
2026-02-23 13:38:07 [ WARNING] agentic_core.utils.decorators_util: [standard_heal] MockAgent: Non-canonical key '_policy_from_kwargs' detected. Consider using canonical keys for better schema compliance.
PASSED                                                                   [ 21%]
tests/governance/test_heal_policy_wiring.py::TestNetworkTripwire::test_network_tripwire_blocks_socket PASSED [ 21%]
tests/governance/test_heal_policy_wiring.py::TestNetworkTripwire::test_heal_paths_make_no_network_calls PASSED [ 21%]
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_deterministic_output PASSED [ 21%]
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_idempotency PASSED [ 21%]
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_policy_routing PASSED [ 21%]
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_deterministic_baseline_integration PASSED [ 22%]
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_disabled PASSED [ 22%]
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_enabled_with_router PASSED [ 22%]
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_enabled_no_router PASSED [ 22%]
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_logging_enabled PASSED [ 22%]
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_disabled_no_logging PASSED [ 22%]
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_all_agents_have_heal_surface PASSED [ 22%]
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_all_agents_have_heal_repository_surface PASSED [ 23%]
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_audit_determinism PASSED [ 23%]
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_summary_counts_consistent PASSED [ 23%]
tests/governance/test_heal_telemetry_and_budgets.py::TestHealTelemetrySchema::test_telemetry_record_schema PASSED [ 23%]
tests/governance/test_heal_telemetry_and_budgets.py::TestHealTelemetrySchema::test_telemetry_hash_deterministic PASSED [ 23%]
tests/governance/test_heal_telemetry_and_budgets.py::TestHealTelemetrySchema::test_telemetry_json_serializable PASSED [ 23%]
tests/governance/test_heal_telemetry_and_budgets.py::TestTelemetryEmission::test_emit_creates_artifact PASSED [ 23%]
tests/governance/test_heal_telemetry_and_budgets.py::TestTelemetryEmission::test_emit_idempotent_same_content PASSED [ 23%]
tests/governance/test_heal_telemetry_and_budgets.py::TestTelemetryEmission::test_emit_fails_on_conflict PASSED [ 24%]
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_budget_caps_from_env_defaults PASSED [ 24%]
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_budget_caps_from_env_custom PASSED [ 24%]
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_escalation_budget_enforcement PASSED [ 24%]
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_high_tier_budget_enforcement PASSED [ 24%]
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_budget_counters_tracked PASSED [ 24%]
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_enable_llm_false_budgets_zero PASSED [ 24%]
tests/governance/test_heal_telemetry_and_budgets.py::TestBudgetAndSeamIntegration::test_seam_guard_still_enforced_with_budgets PASSED [ 25%]
tests/governance/test_heal_telemetry_and_budgets.py::TestBudgetAndSeamIntegration::test_no_network_calls_in_budget_checks PASSED [ 25%]
tests/governance/test_healing_reentry.py::TestNoDirectL5Import::test_no_static_l5_import PASSED [ 25%]
tests/governance/test_healing_reentry.py::TestNoDirectL5Import::test_no_static_l3_import PASSED [ 25%]
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_load_activation_gate_helper_present PASSED [ 25%]
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_load_activation_gate_called_in_smart_fix PASSED [ 25%]
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_seam_exposes_load_activation_gate PASSED [ 25%]
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_seam_uses_importlib_not_static PASSED [ 26%]
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_get_file_io_helper_present PASSED [ 26%]
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_get_file_io_called_in_smart_fix PASSED [ 26%]
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_no_bare_open_write_in_smart_fix PASSED [ 26%]
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_no_route_mutation_intent_in_orchestrator PASSED [ 26%]
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_is_module_level_function PASSED [ 26%]
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_in_dunder_all PASSED [ 26%]
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_orchestrator_calls_assert_activation_allowed_on_gate_mod PASSED [ 26%]
tests/governance/test_healing_reentry.py::TestHealingWriteCallPath::test_save_file_called_on_file_io_result PASSED [ 27%]
tests/governance/test_healing_reentry.py::TestHealingWriteCallPath::test_no_open_write_anywhere_in_orchestrator PASSED [ 27%]
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_total_hits_equals_zero FAILED [ 27%]
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_every_hit_is_allowlisted FAILED [ 27%]
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_every_allowlist_entry_still_exists PASSED [ 27%]
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_hits_equal_allowlist_exactly FAILED [ 27%]
tests/governance/test_intent_emission_no_mutation.py::TestNoFileIoImports::test_no_fileio_imports[L3_orchestration] PASSED [ 27%]
tests/governance/test_intent_emission_no_mutation.py::TestNoFileIoImports::test_no_fileio_imports[L4_state] PASSED [ 28%]
tests/governance/test_intent_emission_no_mutation.py::TestNoFileIoImports::test_no_fileio_imports[L5_safety] PASSED [ 28%]
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_open_write PASSED [ 28%]
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_path_write_text PASSED [ 28%]
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_shutil_call PASSED [ 28%]
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_os_remove PASSED [ 28%]
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_json_dump_to_file PASSED [ 28%]
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_fileio_import PASSED [ 29%]
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_ignores_read_only_open PASSED [ 29%]
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_new_open_write_in_l5_is_flagged PASSED [ 29%]
tests/governance/test_l0_upward_import_isolation.py::TestNoStaticUpwardImportsInL0::test_zero_module_level_static_upward_imports PASSED [ 29%]
tests/governance/test_l0_upward_import_isolation.py::TestNoStaticUpwardImportsInL0::test_negative_regression_detector_catches_static_import PASSED [ 29%]
tests/governance/test_l0_upward_import_isolation.py::TestNoStaticUpwardImportsInL0::test_negative_regression_lazy_in_function_not_flagged PASSED [ 29%]
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_only_allowlisted_seams_use_importlib_for_higher_layers PASSED [ 29%]
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_all_allowlisted_seam_files_exist PASSED [ 30%]
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_allowlist_covers_all_seam_files PASSED [ 30%]
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_negative_regression_importlib_higher_layer_detected PASSED [ 30%]
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_negative_regression_importlib_dynamic_var_not_flagged PASSED [ 30%]
tests/governance/test_l6_purity.py::TestL6WritePrimitiveRatchet::test_l6_does_not_exceed_write_ceiling PASSED [ 30%]
tests/governance/test_l6_purity.py::TestL6NoFileIoImports::test_no_fileio_imports_in_l6 PASSED [ 30%]
tests/governance/test_l6_purity.py::TestL6NegativeRegression::test_detects_open_append PASSED [ 30%]
tests/governance/test_l6_purity.py::TestL6NegativeRegression::test_detects_write_text PASSED [ 30%]
tests/governance/test_l6_purity.py::TestL6NegativeRegression::test_ignores_read_open PASSED [ 31%]
tests/governance/test_layer_inventory.py::TestLayerInventory::test_exactly_seven_layers_exist PASSED [ 31%]
tests/governance/test_layer_inventory.py::TestLayerInventory::test_layer_ordering_is_monotonic PASSED [ 31%]
tests/governance/test_layer_inventory.py::TestLayerInventory::test_file_enumeration_count_is_stable PASSED [ 31%]
tests/governance/test_layer_inventory.py::TestLayerInventory::test_layer_of_path_returns_correct_layer PASSED [ 31%]
tests/governance/test_layer_inventory.py::TestLayerInventory::test_layer_of_path_returns_none_for_non_layer PASSED [ 31%]
tests/governance/test_layer_inventory.py::TestLayerInventory::test_classify_file_identifies_utils PASSED [ 31%]
tests/governance/test_layer_inventory.py::TestLayerInventory::test_classify_file_identifies_layer_files PASSED [ 32%]
tests/governance/test_layer_inventory.py::TestLayerInventory::test_all_layer_directories_have_files PASSED [ 32%]
tests/governance/test_layer_inventory.py::TestLayerInventory::test_enumerate_python_files_is_sorted PASSED [ 32%]
tests/governance/test_layer_inventory.py::TestLayerInventory::test_inventory_summary PASSED [ 32%]
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_file_exists_and_valid PASSED [ 32%]
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_matches_scanner_total FAILED [ 32%]
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_enforcement_no_unregistered_seams FAILED [ 32%]
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_negative_remove_allowlist_entry_causes_violation PASSED [ 33%]
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_negative_synthetic_seam_causes_violation PASSED [ 33%]
tests/governance/test_lazy_seam_silent_swallow.py::TestScanFileSwallowsSyntaxError::test_syntax_error_returns_empty PASSED [ 33%]
tests/governance/test_lazy_seam_silent_swallow.py::TestScanFileSwallowsSyntaxError::test_io_error_returns_empty PASSED [ 33%]
tests/governance/test_lazy_seam_silent_swallow.py::TestScanCodebaseContinuesAfterError::test_valid_files_still_scanned PASSED [ 33%]
tests/governance/test_lazy_seam_silent_swallow.py::TestNoMutationOnSwallow::test_no_files_created_on_syntax_error PASSED [ 33%]
tests/governance/test_lazy_seam_silent_swallow.py::TestSwallowDoesNotWeakenEnforcement::test_corrupt_file_not_treated_as_compliant PASSED [ 33%]
tests/governance/test_learning_artifact_intent.py::TestFrozenImmutability::test_cannot_set_field_after_construction PASSED [ 34%]
tests/governance/test_learning_artifact_intent.py::TestFrozenImmutability::test_cannot_delete_field PASSED [ 34%]
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_same_inputs_same_hash PASSED [ 34%]
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_different_inputs_different_hash PASSED [ 34%]
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_hash_is_sha256_hex PASSED [ 34%]
tests/governance/test_learning_artifact_intent.py::TestHashIntegrity::test_verify_passes_on_valid_intent PASSED [ 34%]
tests/governance/test_learning_artifact_intent.py::TestHashIntegrity::test_verify_fails_on_wrong_hash PASSED [ 34%]
tests/governance/test_learning_artifact_intent.py::TestHashability::test_usable_as_set_member PASSED [ 34%]
tests/governance/test_learning_artifact_intent.py::TestHashability::test_usable_as_dict_key PASSED [ 35%]
tests/governance/test_learning_seam_compliance.py::TestNoDirectPersistenceImport::test_no_persistence_imports_in_agents PASSED [ 35%]
tests/governance/test_learning_seam_compliance.py::TestNoForbiddenWriteCalls::test_no_direct_write_calls_in_agents PASSED [ 35%]
tests/governance/test_learning_seam_compliance.py::TestLearningSeamExists::test_learning_seam_file_exists PASSED [ 35%]
tests/governance/test_learning_seam_compliance.py::TestLearningSeamExists::test_learning_seam_exports_intent PASSED [ 35%]
tests/governance/test_learning_seam_compliance.py::TestASTScannerDeterminism::test_agent_file_collection_deterministic PASSED [ 35%]
tests/governance/test_learning_seam_compliance.py::TestASTScannerDeterminism::test_scanner_produces_results PASSED [ 35%]
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_bundle_is_frozen PASSED [ 36%]
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_checksum_is_sha256 PASSED [ 36%]
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_checksum_deterministic PASSED [ 36%]
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_checksum_differs_with_different_versions PASSED [ 36%]
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_verify_checksum_passes PASSED [ 36%]
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_verify_checksum_fails_on_tampered PASSED [ 36%]
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_production_only_allows_recorded_output PASSED [ 36%]
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_dev_test_allows_both_modes PASSED [ 37%]
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_validate_production_passes_recorded_output PASSED [ 37%]
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_validate_production_rejects_deterministic PASSED [ 37%]
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_recorded_output_is_authoritative PASSED [ 37%]
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_deterministic_is_not_authoritative PASSED [ 37%]
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_deterministic_label_non_authoritative PASSED [ 37%]
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_recorded_output_label_authoritative PASSED [ 37%]
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_recorded_output_returns_stored_bytes PASSED [ 38%]
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_deterministic_inference_raises PASSED [ 38%]
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_execution_blocked_on_invalid_bundle PASSED [ 38%]
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_strategy_governance_label PASSED [ 38%]
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_os_remove_blocked PASSED [ 38%]
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_subprocess_run_blocked PASSED [ 38%]
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_os_system_blocked PASSED [ 38%]
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_builtins_open_blocked PASSED [ 38%]
tests/governance/test_preventative_sandbox.py::TestSandboxRestoration::test_os_remove_restored PASSED [ 39%]
tests/governance/test_preventative_sandbox.py::TestSandboxRestoration::test_subprocess_run_restored PASSED [ 39%]
tests/governance/test_preventative_sandbox.py::TestSandboxRestoration::test_restored_on_exception PASSED [ 39%]
tests/governance/test_preventative_sandbox.py::TestDoubleActivation::test_double_activation_raises PASSED [ 39%]
tests/governance/test_preventative_sandbox.py::TestCustomTargets::test_custom_target_blocked PASSED [ 39%]
tests/governance/test_preventative_sandbox.py::TestSandboxState::test_inactive_by_default PASSED [ 39%]
tests/governance/test_preventative_sandbox.py::TestSandboxState::test_active_inside_context PASSED [ 39%]
tests/governance/test_replay_integrity.py::TestReplayHashComputed::test_replay_hash_is_sha256 PASSED [ 40%]
tests/governance/test_replay_integrity.py::TestReplayHashComputed::test_integrity_verified_true_on_create PASSED [ 40%]
tests/governance/test_replay_integrity.py::TestReplayHashComputed::test_replay_hash_deterministic PASSED [ 40%]
tests/governance/test_replay_integrity.py::TestTamperDetection::test_tampered_response_fails PASSED [ 40%]
tests/governance/test_replay_integrity.py::TestTamperDetection::test_tampered_model_version_fails PASSED [ 40%]
tests/governance/test_replay_integrity.py::TestTamperDetection::test_valid_bundle_passes PASSED [ 40%]
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanDeterminism::test_build_plan_produces_same_result_twice PASSED [ 40%]
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanDeterminism::test_plan_is_sorted_deterministically PASSED [ 41%]
tests/governance/test_repo_heal_pipeline.py::TestRepoHealScopeControls::test_denylist_excludes_directories PASSED [ 41%]
tests/governance/test_repo_heal_pipeline.py::TestRepoHealScopeControls::test_allowlist_filters_extensions PASSED [ 41%]
tests/governance/test_repo_heal_pipeline.py::TestRepoHealScopeControls::test_skipped_files_counted PASSED [ 41%]
tests/governance/test_repo_heal_pipeline.py::TestRepoHealApplyIdempotency::test_apply_is_idempotent PASSED [ 41%]
tests/governance/test_repo_heal_pipeline.py::TestRepoHealApplyIdempotency::test_apply_handles_missing_files PASSED [ 41%]
tests/governance/test_repo_heal_pipeline.py::TestRepoHealApplyIdempotency::test_dry_run_makes_no_changes PASSED [ 41%]
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanSchema::test_plan_to_dict_schema PASSED [ 42%]
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanSchema::test_result_to_dict_schema PASSED [ 42%]
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanSchema::test_plan_json_serializable PASSED [ 42%]
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_enable_llm_false_no_llm_call PASSED [ 42%]
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_enable_llm_true_requires_capability_token PASSED [ 42%]
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_policy_decision_record_emitted PASSED [ 42%]
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_baseline_plan_runs_before_escalation PASSED [ 42%]
tests/governance/test_routing_config_seal.py::TestSealImmutability::test_seal_is_frozen PASSED [ 42%]
tests/governance/test_routing_config_seal.py::TestSealImmutability::test_sealed_at_is_set PASSED [ 43%]
tests/governance/test_routing_config_seal.py::TestSealDeterminism::test_same_config_same_hash PASSED [ 43%]
tests/governance/test_routing_config_seal.py::TestSealDeterminism::test_different_config_different_hash PASSED [ 43%]
tests/governance/test_routing_config_seal.py::TestSealVerification::test_unchanged_config_passes PASSED [ 43%]
tests/governance/test_routing_config_seal.py::TestSealVerification::test_mutated_config_fails PASSED [ 43%]
tests/governance/test_routing_config_seal.py::TestSealVerification::test_removed_key_fails PASSED [ 43%]
tests/governance/test_routing_config_seal.py::TestSealedRoutingContext::test_no_mutation_passes PASSED [ 43%]
tests/governance/test_routing_config_seal.py::TestSealedRoutingContext::test_mutation_raises PASSED [ 44%]
tests/governance/test_routing_config_seal.py::TestSealedRoutingContext::test_seal_accessible PASSED [ 44%]
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_execution_mode_importable PASSED [ 44%]
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_forward_rolling_config_importable PASSED [ 44%]
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_rollout_stage_importable PASSED [ 44%]
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_health_status_importable PASSED [ 44%]
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_contract_symbols_match_originals PASSED [ 44%]
tests/governance/test_seam_contracts.py::TestActivationContractImportParity::test_assert_activation_allowed_importable PASSED [ 45%]
tests/governance/test_seam_contracts.py::TestActivationContractImportParity::test_contract_symbol_matches_original PASSED [ 45%]
tests/governance/test_seam_contracts.py::TestMcpContractImportParity::test_mcp_connection_manager_importable PASSED [ 45%]
tests/governance/test_seam_contracts.py::TestMcpContractImportParity::test_mcp_connection_manager_is_protocol PASSED [ 45%]
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_safety_agent_factory_instantiates PASSED [ 45%]
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_unknown_agent_returns_none PASSED [ 45%]
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_healing_agent_protocol_is_runtime_checkable PASSED [ 45%]
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_object_without_heal_repository_fails_protocol PASSED [ 46%]
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolFakeInjection::test_safety_strategy_accepts_injected_factory PASSED [ 46%]
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolFakeInjection::test_safety_strategy_default_factory_created_when_none PASSED [ 46%]
tests/governance/test_seam_contracts.py::TestNervousSystemAgentProtocolDefaultWiring::test_safety_agent_factory_used_in_nervous_system PASSED [ 46%]
tests/governance/test_seam_contracts.py::TestNervousSystemAgentProtocolDefaultWiring::test_nervous_system_agent_protocol_fake_injection PASSED [ 46%]
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_seam_file_detection PASSED [ 46%]
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_approved_loader_detection PASSED [ 46%]
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_scan_produces_deterministic_results PASSED [ 46%]
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_dynamic_violation_summary PASSED [ 47%]
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_static_seam_upward PASSED [ 47%]
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_static_l2_to_l5 PASSED [ 47%]
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_static_l3_to_l6 PASSED [ 47%]
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_dynamic_importlib PASSED [ 47%]
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_dynamic_dunder_import PASSED [ 47%]
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_dynamic_in_seam PASSED [ 47%]
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_approved_loader_allowed PASSED [ 48%]
tests/governance/test_seam_dynamic_enforcement.py::TestConvergenceConfidence::test_convergence_confidence_calculation PASSED [ 48%]
tests/governance/test_shift_report.py::TestShiftReportImmutability::test_cannot_mutate_field PASSED [ 48%]
tests/governance/test_shift_report.py::TestShiftReportImmutability::test_timestamp_is_set PASSED [ 48%]
tests/governance/test_shift_report.py::TestMinimumSampleGuard::test_min_sample_size_is_30 PASSED [ 48%]
tests/governance/test_shift_report.py::TestMinimumSampleGuard::test_small_sample_skips PASSED [ 48%]
tests/governance/test_shift_report.py::TestMinimumSampleGuard::test_sufficient_sample_runs PASSED [ 48%]
tests/governance/test_shift_report.py::TestMMDDetection::test_identical_data_no_shift PASSED [ 49%]
tests/governance/test_shift_report.py::TestMMDDetection::test_shifted_data_detected PASSED [ 49%]
tests/governance/test_shift_report.py::TestPSIDetection::test_per_feature_flags PASSED [ 49%]
tests/governance/test_shift_report.py::TestPSIDetection::test_no_drift_low_psi PASSED [ 49%]
tests/governance/test_shift_report.py::TestSkippedReport::test_skipped_report_fields PASSED [ 49%]
tests/governance/test_shift_report.py::TestJointShiftLogic::test_joint_true_when_mmd_exceeds PASSED [ 49%]
tests/governance/test_shift_report.py::TestJointShiftLogic::test_joint_true_when_psi_exceeds PASSED [ 49%]
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_no_banned_imports PASSED [ 50%]
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_standard_heal_no_routing_calls PASSED [ 50%]
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_wrapper_function_no_routing_calls PASSED [ 50%]
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[0] PASSED [ 50%]
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[1] PASSED [ 50%]
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[2] PASSED [ 50%]
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[3] PASSED [ 50%]
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[4] PASSED [ 50%]
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[5] PASSED [ 51%]
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[6] PASSED [ 51%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L1] PASSED [ 51%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L2] PASSED [ 51%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L3] PASSED [ 51%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L4] PASSED [ 51%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L5] PASSED [ 51%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L6] PASSED [ 52%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L0] PASSED [ 52%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L2] PASSED [ 52%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L3] PASSED [ 52%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L4] PASSED [ 52%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L5] PASSED [ 52%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L6] PASSED [ 52%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L0] PASSED [ 53%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L1] PASSED [ 53%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L3] PASSED [ 53%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L4] PASSED [ 53%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L5] PASSED [ 53%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L6] PASSED [ 53%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L0] PASSED [ 53%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L1] PASSED [ 53%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L2] PASSED [ 54%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L4] PASSED [ 54%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L5] PASSED [ 54%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L6] PASSED [ 54%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L0] PASSED [ 54%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L1] PASSED [ 54%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L2] PASSED [ 54%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L3] PASSED [ 55%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L5] PASSED [ 55%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L6] PASSED [ 55%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L0] PASSED [ 55%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L1] PASSED [ 55%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L2] PASSED [ 55%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L3] PASSED [ 55%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L4] PASSED [ 56%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L6] PASSED [ 56%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L0] PASSED [ 56%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L1] PASSED [ 56%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L2] PASSED [ 56%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L3] PASSED [ 56%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L4] PASSED [ 56%]
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L5] PASSED [ 57%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L2] PASSED [ 57%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L3] PASSED [ 57%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L4] PASSED [ 57%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L5] PASSED [ 57%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L6] PASSED [ 57%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L1] PASSED [ 57%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L3] PASSED [ 57%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L4] PASSED [ 58%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L5] PASSED [ 58%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L6] PASSED [ 58%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L1] PASSED [ 58%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L2] PASSED [ 58%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L4] PASSED [ 58%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L5] PASSED [ 58%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L6] PASSED [ 59%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L1] PASSED [ 59%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L2] PASSED [ 59%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L3] PASSED [ 59%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L5] PASSED [ 59%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L6] PASSED [ 59%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L1] PASSED [ 59%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L2] PASSED [ 60%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L3] PASSED [ 60%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L4] PASSED [ 60%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L6] PASSED [ 60%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L1] PASSED [ 60%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L2] PASSED [ 60%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L3] PASSED [ 60%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L4] PASSED [ 61%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L5] PASSED [ 61%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L2] PASSED [ 61%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L3] PASSED [ 61%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L4] PASSED [ 61%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L5] PASSED [ 61%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L6] PASSED [ 61%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L0] PASSED [ 61%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L3] PASSED [ 62%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L4] PASSED [ 62%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L5] PASSED [ 62%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L6] PASSED [ 62%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L0] PASSED [ 62%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L2] PASSED [ 62%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L4] PASSED [ 62%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L5] PASSED [ 63%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L6] PASSED [ 63%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L0] PASSED [ 63%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L2] PASSED [ 63%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L3] PASSED [ 63%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L5] PASSED [ 63%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L6] PASSED [ 63%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L0] PASSED [ 64%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L2] PASSED [ 64%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L3] PASSED [ 64%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L4] PASSED [ 64%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L6] PASSED [ 64%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L0] PASSED [ 64%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L2] PASSED [ 64%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L3] PASSED [ 65%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L4] PASSED [ 65%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L5] PASSED [ 65%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L1] PASSED [ 65%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L3] PASSED [ 65%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L4] PASSED [ 65%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L5] PASSED [ 65%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L6] PASSED [ 65%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L0] PASSED [ 66%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L3] PASSED [ 66%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L4] PASSED [ 66%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L5] PASSED [ 66%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L6] PASSED [ 66%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L0] PASSED [ 66%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L1] PASSED [ 66%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L4] PASSED [ 67%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L5] PASSED [ 67%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L6] PASSED [ 67%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L0] PASSED [ 67%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L1] PASSED [ 67%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L3] PASSED [ 67%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L5] PASSED [ 67%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L6] PASSED [ 68%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L0] PASSED [ 68%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L1] PASSED [ 68%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L3] PASSED [ 68%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L4] PASSED [ 68%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L6] PASSED [ 68%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L0] PASSED [ 68%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L1] PASSED [ 69%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L3] PASSED [ 69%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L4] PASSED [ 69%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L5] PASSED [ 69%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L1] PASSED [ 69%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L2] PASSED [ 69%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L4] PASSED [ 69%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L5] PASSED [ 69%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L6] PASSED [ 70%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L0] PASSED [ 70%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L2] PASSED [ 70%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L4] PASSED [ 70%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L5] PASSED [ 70%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L6] PASSED [ 70%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L0] PASSED [ 70%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L1] PASSED [ 71%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L4] PASSED [ 71%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L5] PASSED [ 71%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L6] PASSED [ 71%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L0] PASSED [ 71%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L1] PASSED [ 71%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L2] PASSED [ 71%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L5] PASSED [ 72%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L6] PASSED [ 72%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L0] PASSED [ 72%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L1] PASSED [ 72%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L2] PASSED [ 72%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L4] PASSED [ 72%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L6] PASSED [ 72%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L0] PASSED [ 73%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L1] PASSED [ 73%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L2] PASSED [ 73%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L4] PASSED [ 73%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L5] PASSED [ 73%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L1] PASSED [ 73%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L2] PASSED [ 73%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L3] PASSED [ 73%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L5] PASSED [ 74%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L6] PASSED [ 74%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L0] PASSED [ 74%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L2] PASSED [ 74%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L3] PASSED [ 74%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L5] PASSED [ 74%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L6] PASSED [ 74%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L0] PASSED [ 75%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L1] PASSED [ 75%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L3] PASSED [ 75%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L5] PASSED [ 75%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L6] PASSED [ 75%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L0] PASSED [ 75%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L1] PASSED [ 75%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L2] PASSED [ 76%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L5] PASSED [ 76%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L6] PASSED [ 76%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L0] PASSED [ 76%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L1] PASSED [ 76%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L2] PASSED [ 76%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L3] PASSED [ 76%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L6] PASSED [ 76%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L0] PASSED [ 77%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L1] PASSED [ 77%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L2] PASSED [ 77%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L3] PASSED [ 77%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L5] PASSED [ 77%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L1] PASSED [ 77%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L2] PASSED [ 77%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L3] PASSED [ 78%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L4] PASSED [ 78%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L6] PASSED [ 78%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L0] PASSED [ 78%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L2] PASSED [ 78%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L3] PASSED [ 78%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L4] PASSED [ 78%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L6] PASSED [ 79%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L0] PASSED [ 79%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L1] PASSED [ 79%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L3] PASSED [ 79%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L4] PASSED [ 79%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L6] PASSED [ 79%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L0] PASSED [ 79%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L1] PASSED [ 80%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L2] PASSED [ 80%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L4] PASSED [ 80%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L6] PASSED [ 80%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L0] PASSED [ 80%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L1] PASSED [ 80%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L2] PASSED [ 80%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L3] PASSED [ 80%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L6] PASSED [ 81%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L0] PASSED [ 81%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L1] PASSED [ 81%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L2] PASSED [ 81%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L3] PASSED [ 81%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L4] PASSED [ 81%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L1] PASSED [ 81%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L2] PASSED [ 82%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L3] PASSED [ 82%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L4] PASSED [ 82%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L5] PASSED [ 82%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L0] PASSED [ 82%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L2] PASSED [ 82%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L3] PASSED [ 82%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L4] PASSED [ 83%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L5] PASSED [ 83%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L0] PASSED [ 83%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L1] PASSED [ 83%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L3] PASSED [ 83%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L4] PASSED [ 83%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L5] PASSED [ 83%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L0] PASSED [ 84%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L1] PASSED [ 84%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L2] PASSED [ 84%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L4] PASSED [ 84%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L5] PASSED [ 84%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L4-L0] PASSED [ 84%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L4-L1] PASSED [ 84%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L4-L2] PASSED [ 84%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L4-L3] PASSED [ 85%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L4-L5] PASSED [ 85%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L5-L0] PASSED [ 85%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L5-L1] PASSED [ 85%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L5-L2] PASSED [ 85%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L5-L3] PASSED [ 85%]
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L5-L4] PASSED [ 85%]
tests/governance/test_tier_lattice.py::TestEscalationMonotonicity::test_valid_ascending_sequence PASSED [ 86%]
tests/governance/test_tier_lattice.py::TestEscalationMonotonicity::test_valid_flat_sequence PASSED [ 86%]
tests/governance/test_tier_lattice.py::TestEscalationMonotonicity::test_invalid_descending_sequence PASSED [ 86%]
tests/governance/test_tier_lattice.py::TestEscalationMonotonicity::test_empty_sequence_valid PASSED [ 86%]
tests/governance/test_tier_lattice.py::TestEscalationMonotonicity::test_single_element_valid PASSED [ 86%]
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l0_safe_to_drop PASSED [ 86%]
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l1_under_pressure_only PASSED [ 86%]
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[2] PASSED [ 87%]
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[3] PASSED [ 87%]
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[4] PASSED [ 87%]
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[5] PASSED [ 87%]
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[6] PASSED [ 87%]
tests/governance/test_tier_lattice.py::TestCanDrop::test_l0_always_droppable PASSED [ 87%]
tests/governance/test_tier_lattice.py::TestCanDrop::test_l1_not_droppable_without_pressure PASSED [ 87%]
tests/governance/test_tier_lattice.py::TestCanDrop::test_l1_droppable_under_pressure PASSED [ 88%]
tests/governance/test_tier_lattice.py::TestCanDrop::test_l2_never_droppable PASSED [ 88%]
tests/governance/test_tier_lattice.py::TestBackpressurePolicy::test_should_drop_l0 PASSED [ 88%]
tests/governance/test_tier_lattice.py::TestBackpressurePolicy::test_should_not_drop_l2 PASSED [ 88%]
tests/governance/test_tier_lattice.py::TestBackpressurePolicy::test_should_drop_l1_under_pressure PASSED [ 88%]
tests/governance/test_tier_lattice.py::TestLatticeCompleteness::test_21_distinct_pairs PASSED [ 88%]
tests/governance/test_time_shifted_influence.py::TestNoMidRunMutation::test_routing_unchanged_in_same_run PASSED [ 88%]
tests/governance/test_time_shifted_influence.py::TestNoMidRunMutation::test_detection_does_not_change_routing PASSED [ 88%]
tests/governance/test_time_shifted_influence.py::TestNoMidRunMutation::test_mid_run_mutation_raises PASSED [ 89%]
tests/governance/test_time_shifted_influence.py::TestTimeShiftedInfluence::test_version_bump_changes_next_run PASSED [ 89%]
tests/governance/test_time_shifted_influence.py::TestTimeShiftedInfluence::test_same_config_same_hash_across_runs PASSED [ 89%]
tests/governance/test_time_shifted_influence.py::TestTimeShiftedInfluence::test_influence_strictly_time_shifted PASSED [ 89%]
tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_all_21_layer_pairs_covered PASSED [ 89%]
tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_detector_identifies_l0_to_l5_l6_as_special PASSED [ 89%]
tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_scan_produces_deterministic_results PASSED [ 89%]
tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_violation_summary PASSED [ 90%]
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_l0_imports_l5 PASSED [ 90%]
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_l2_imports_l6 PASSED [ 90%]
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_l1_imports_l3 PASSED [ 90%]
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_downward_import_allowed PASSED [ 90%]
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_same_layer_import_allowed PASSED [ 90%]
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_non_layer_import_ignored PASSED [ 90%]
tests/governance/test_upward_import_enforcement.py::TestNegativeRegressionNewDefinition::test_zero_violations_under_new_definition FAILED [ 91%]
tests/governance/test_upward_import_enforcement.py::TestNegativeRegressionNewDefinition::test_module_level_upward_import_is_caught_not_lazy PASSED [ 91%]
tests/governance/test_upward_import_enforcement.py::TestNegativeRegressionNewDefinition::test_lazy_upward_import_inside_function_is_allowed PASSED [ 91%]
tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_module_level_upward_imports_still_zero FAILED [ 91%]
tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_lazy_upward_import_metric_is_deterministic PASSED [ 91%]
tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_lazy_upward_import_metric_report PASSED [ 91%]
tests/governance/test_upward_import_enforcement.py::TestLazySeamViolation::test_zero_lazy_seam_violations_in_codebase FAILED [ 91%]
tests/governance/test_upward_import_enforcement.py::TestLazySeamViolation::test_upward_import_inside_non_get_function_is_violation PASSED [ 92%]
tests/governance/test_upward_import_enforcement.py::TestLazySeamViolation::test_upward_import_inside_get_function_is_allowed PASSED [ 92%]
tests/governance/test_upward_import_enforcement.py::TestLazySeamBudget::test_lazy_seam_budget_not_exceeded FAILED [ 92%]
tests/governance/test_vllm_boundary_connectivity.py::test_generate_proposal_does_not_touch_network_when_not_called PASSED [ 92%]
tests/governance/test_vllm_boundary_connectivity.py::test_call_vllm_uses_urlopen_once_and_parses_chat_completions PASSED [ 92%]
tests/governance/test_vllm_boundary_connectivity.py::test_call_vllm_http_error_maps_to_runtimeerror PASSED [ 92%]
tests/governance/test_vllm_boundary_connectivity.py::test_call_vllm_timeout_maps_to_timeouterror PASSED [ 92%]
tests/governance/test_vllm_boundary_connectivity.py::test_call_vllm_connection_refused_maps_to_connectionerror PASSED [ 92%]
tests/governance/test_vllm_determinism.py::test_canonical_hash_stable PASSED [ 93%]
tests/governance/test_vllm_determinism.py::test_idempotent_normalization PASSED [ 93%]
tests/governance/test_vllm_determinism.py::test_nested_structure_determinism PASSED [ 93%]
tests/governance/test_vllm_determinism.py::test_set_ordering_stability PASSED [ 93%]
tests/governance/test_vllm_determinism.py::test_decimal_normalization PASSED [ 93%]
tests/governance/test_vllm_determinism.py::test_dataclass_roundtrip PASSED [ 93%]
tests/governance/test_vllm_determinism.py::test_float_rounding PASSED    [ 93%]
tests/governance/test_vllm_determinism.py::test_negative_zero_normalization PASSED [ 94%]
tests/governance/test_vllm_determinism.py::test_nan_rejected PASSED      [ 94%]
tests/governance/test_vllm_determinism.py::test_inf_rejected PASSED      [ 94%]
tests/governance/test_vllm_determinism.py::test_datetime_rejected PASSED [ 94%]
tests/governance/test_vllm_determinism.py::test_bytes_rejected PASSED    [ 94%]
tests/governance/test_vllm_determinism.py::test_complex_rejected PASSED  [ 94%]
tests/governance/test_vllm_determinism.py::test_tuple_to_list_preserves_order PASSED [ 94%]
tests/governance/test_vllm_determinism.py::test_canonical_hash_rejects_non_dict PASSED [ 95%]
tests/governance/test_vllm_determinism.py::test_cross_process_determinism PASSED [ 95%]
tests/governance/test_vllm_determinism.py::test_enum_normalization PASSED [ 95%]
tests/governance/test_vllm_determinism.py::test_routing_decision_frozen PASSED [ 95%]
tests/governance/test_vllm_determinism.py::test_routing_decision_frozen_setattr PASSED [ 95%]
tests/governance/test_vllm_determinism.py::test_routing_predicates_immutable PASSED [ 95%]
tests/governance/test_vllm_determinism.py::test_no_lambda_in_predicate_registry PASSED [ 95%]
tests/governance/test_vllm_determinism.py::test_no_forbidden_ast_nodes_in_predicate_registry PASSED [ 96%]
tests/governance/test_vllm_determinism.py::test_no_eval_exec_compile_in_predicate_registry PASSED [ 96%]
tests/governance/test_vllm_determinism.py::test_predicate_functions_no_free_vars PASSED [ 96%]
tests/governance/test_vllm_determinism.py::test_provider_strict_type PASSED [ 96%]
tests/governance/test_vllm_determinism.py::test_no_provider_string_literals_in_registry PASSED [ 96%]
tests/governance/test_vllm_determinism.py::test_context_structural_immutability PASSED [ 96%]
tests/governance/test_vllm_determinism.py::test_context_hash_immutability PASSED [ 96%]
tests/governance/test_vllm_determinism.py::test_key_order_independence PASSED [ 96%]
tests/governance/test_vllm_determinism.py::test_double_evaluation_equality PASSED [ 97%]
tests/governance/test_vllm_determinism.py::test_predicate_hash_correctness PASSED [ 97%]
tests/governance/test_vllm_isolation.py::test_no_direct_model_imports_in_layers PASSED [ 97%]
tests/governance/test_vllm_isolation.py::test_no_importlib_in_layers PASSED [ 97%]
tests/governance/test_vllm_isolation.py::test_no_getattr_model_bypass PASSED [ 97%]
tests/governance/test_vllm_isolation.py::test_no_dunder_import PASSED    [ 97%]
tests/governance/test_vllm_isolation.py::test_no_sys_modules_mutation PASSED [ 97%]
tests/governance/test_vllm_isolation.py::test_transitive_import_graph_clean PASSED [ 98%]
tests/governance/test_vllm_isolation.py::test_boundary_client_not_imported_by_layers PASSED [ 98%]
tests/governance/test_vllm_isolation.py::test_no_time_based_routing PASSED [ 98%]
tests/governance/test_vllm_isolation.py::test_provider_enum_defined PASSED [ 98%]
tests/governance/test_vllm_isolation.py::test_routing_invariants_version_present PASSED [ 98%]
tests/governance/test_write_set_enforcer.py::TestDeclaredWriteAllowed::test_declared_write_succeeds PASSED [ 98%]
tests/governance/test_write_set_enforcer.py::TestDeclaredWriteAllowed::test_multiple_declared_writes PASSED [ 98%]
tests/governance/test_write_set_enforcer.py::TestDeclaredWriteAllowed::test_verify_passes_on_declared PASSED [ 99%]
tests/governance/test_write_set_enforcer.py::TestUndeclaredWriteBlocked::test_undeclared_write_raises PASSED [ 99%]
tests/governance/test_write_set_enforcer.py::TestUndeclaredWriteBlocked::test_undeclared_aborts_enforcer PASSED [ 99%]
tests/governance/test_write_set_enforcer.py::TestUndeclaredWriteBlocked::test_aborted_rejects_subsequent PASSED [ 99%]
tests/governance/test_write_set_enforcer.py::TestUndeclaredWriteBlocked::test_verify_fails_after_violation PASSED [ 99%]
tests/governance/test_write_set_enforcer.py::TestWriteSetTracking::test_empty_initially PASSED [ 99%]
tests/governance/test_write_set_enforcer.py::TestWriteSetTracking::test_partial_not_complete PASSED [ 99%]
tests/governance/test_write_set_enforcer.py::TestWriteSetTracking::test_duplicate_write_idempotent PASSED [100%]

================================== FAILURES ===================================
______________ TestCrossLayerImportFreeze.test_no_new_violations ______________
tests\governance\test_cross_layer_import_freeze.py:101: in test_no_new_violations
    assert len(all_violations) <= BASELINED_VIOLATION_COUNT, (
E   AssertionError: New cross-layer import violations (152 > 149):
E     agentic_core\L0_routing\enforcement\execution_gateway.py:27 imports agentic_core.L2_execution.enforcement.manifest_hash_validator
E     agentic_core\L0_routing\enforcement\execution_gateway.py:71 imports agentic_core.L2_execution.enforcement.healer_pipe_order
E     agentic_core\L0_routing\enforcement\mutation_prohibition.py:233 imports agentic_core.L2_execution.tools.write_gateway
E     agentic_core\L0_routing\engines\escalation_router.py:16 imports agentic_core.L4_state.config.versioned_configs
E     agentic_core\L0_routing\engines\escalation_router.py:22 imports agentic_core.L4_state.enforcement.violation_event_store
E     agentic_core\L0_routing\engines\timeshift_router.py:20 imports agentic_core.L4_state.config.versioned_configs
E     agentic_core\L0_routing\engines\timeshift_router.py:26 imports agentic_core.L4_state.types.detection_signal_store_types
E     agentic_core\L0_routing\meta_control\meta_apply.py:44 imports agentic_core.L2_execution.types.capability_token_types
E     agentic_core\L0_routing\scripts\colors.py:28 imports agentic_core.L4_state.reasoning.CheckpointManagerAgent
E     agentic_core\L0_routing\scripts\execute_ssot.py:42 imports agentic_core.L2_execution.tools.safe_subprocess
E     agentic_core\L0_routing\scripts\execute_ssot.py:48 imports agentic_core.L2_execution.tools
E     agentic_core\L0_routing\scripts\forensic_discovery_prep.py:45 imports agentic_core.L2_execution.tools.safe_subprocess
E     agentic_core\L0_routing\scripts\full_agent_discovery.py:63 imports agentic_core.L2_execution.tools.safe_subprocess
E     agentic_core\L1_cognition\engines\memory_embedder.py:21 imports agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent
E     agentic_core\L1_cognition\engines\meta_client.py:23 imports agentic_core.L4_state.reasoning.RedisSovereignAgent
E     agentic_core\L1_cognition\engines\meta_client.py:29 imports agentic_core.L4_state.reasoning.PineconeSovereignAgent
E     agentic_core\L1_cognition\engines\meta_client.py:35 imports agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent
E     agentic_core\L3_orchestration\enforcement\mission_runner.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L3_orchestration\enforcement\mission_runner_enforcer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L3_orchestration\engines\action_router.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L3_orchestration\engines\autonomous_execution_engine.py:6 imports agentic_core.L2_execution.tools
E     agentic_core\L3_orchestration\engines\autonomous_execution_engine.py:44 imports agentic_core.L4_state.checkpoint_manager
E     agentic_core\L3_orchestration\engines\omni_context_engine.py:8 imports agentic_core.L2_execution.reasoning.base
E     agentic_core\L3_orchestration\engines\sovereign_mcp_router.py:52 imports agentic_core.L4_state.P1_core.ValidationContext
E     agentic_core\L3_orchestration\engines\sovereign_rag_orchestrator.py:10 imports agentic_core.L2_execution.tools
E     agentic_core\L3_orchestration\engines\sovereign_rag_orchestrator.py:30 imports agentic_core.L4_state.config.versioned_configs
E     agentic_core\L3_orchestration\engines\sovereign_rag_orchestrator.py:36 imports agentic_core.L4_state.types.retrieval_anchor_types
E     agentic_core\L3_orchestration\engines\sovereign_redis_orchestrator.py:24 imports redis
E     agentic_core\L3_orchestration\engines\sub_atomic_engine_impl.py:10 imports agentic_core.L2_execution.enforcement.SovereignLLMGateway
E     agentic_core\L3_orchestration\engines\sub_atomic_engine_impl.py:26 imports agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent
E     agentic_core\L3_orchestration\ptc\tool_call_store.py:14 imports agentic_core.L4_state.storage.filesystem_store
E     agentic_core\L3_orchestration\ptc\tool_call_store.py:15 imports agentic_core.L4_state.storage.persistent_store
E     agentic_core\L3_orchestration\reasoning\StateManagementAgent.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py:32 imports agentic_core.L2_execution.tools
E     agentic_core\L3_orchestration\scripts\guardian_heal_orchestrator.py:83 imports agentic_core.L2_execution.scripts.remediation_dispatcher
E     agentic_core\L3_orchestration\types\telepathy_interface_types.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\config\gravity_leak_config.py:4 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\config\structure_blueprint\_simulate_verify.py:19 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\config\structure_blueprint\_verify.py:24 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\config\structure_blueprint\enforcement\blueprint_hash.py:16 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\agent_info.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\agent_info_enforcer.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\airlock_trimmer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\airlock_trimmer_enforcer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\archival_gatekeeper.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\archival_gatekeeper_gate.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\circular_import_fixer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\circular_import_fixer_enforcer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\fast_dashboard_e2_e_pipeline_enforcer.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\final_airlock_trimmer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\final_airlock_trimmer_enforcer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\governance\artifacts_guard.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\governance\cache_guard.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\governance\docs_structure_guard.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\governance\logs_guard.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\hardcoded_path_refactorer.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\hardcoded_path_refactorer_enforcer.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\healing_invocation_audit.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\healing_invocation_audit_enforcer.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\import_surgeon.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\import_surgeon_enforcer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\module_collision_guard.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\module_collision_guardrail.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\mutation_prohibition.py:20 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\mutation_prohibition_enforcer.py:20 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\namespace_medic.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\namespace_medic_enforcer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\pytest_config_guard.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\pytest_config_guardrail.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\safe_subprocess_handler.py:21 imports agentic_core.L4_state.utils.telemetry_sanitizer
E     agentic_core\L5_safety\enforcement\safe_subprocess_handler_enforcer.py:21 imports agentic_core.L4_state.utils.telemetry_sanitizer
E     agentic_core\L5_safety\enforcement\security\credential_guard.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\sovereign_healing_engine.py:6 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\sovereign_healing_engine_enforcer.py:6 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\ssot_import_enforcer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\system.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\enforcement\system_enforcer.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\governance\lazy_seam_classifier.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\governance\lazy_seam_scanner.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\AdversarialProbeAgent.py:21 imports agentic_core.L4_state.memory
E     agentic_core\L5_safety\reasoning\AdversarialRedTeamerAgent.py:34 imports agentic_core.L2_execution.reasoning.base
E     agentic_core\L5_safety\reasoning\ArchitectureGovernorAgent.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\AutonomyGuardianAgent.py:8 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\BenchmarkingAgent.py:8 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\BoundaryTestingAgent.py:27 imports agentic_core.L4_state.memory
E     agentic_core\L5_safety\reasoning\ChaosEngineeringAgent.py:28 imports agentic_core.L4_state.memory
E     agentic_core\L5_safety\reasoning\CodeDeduplicationAgent.py:13 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\CodeEnforcerAgent.py:5 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\CodeHealerAgent.py:43 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\CognitiveDispositionAgent.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\CredentialScannerAgent.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\DependencyPruningAgent.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\DocstringComplianceAgent.py:10 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\DuplicateCodeDetectorAgent.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\DynamicSealAgent.py:4 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\FileClassificationAgent.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\FilesystemSSOTReconcilerAgent.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\GenerativeGuardAgent.py:11 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\GovernanceAgent.py:11 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\GovernanceAgent.py:58 imports agentic_core.L4_state.utils.complexity_analyzer
E     agentic_core\L5_safety\reasoning\GravityLeakRepairAgent.py:6 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\GravityLeakRepairAgent.py:43 imports agentic_core.L4_state.utils.layer_gravity_util
E     agentic_core\L5_safety\reasoning\GravityLeakRepairAgent.py:312 imports agentic_core.L4_state.utils.layer_gravity_util
E     agentic_core\L5_safety\reasoning\HierarchyAgent.py:11 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\IntegrityGateExecutorAgent.py:10 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\L5SafetyExerciserAgent.py:11 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\LocationHealerAgent.py:33 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\LocationHealerAgent.py:2149 imports agentic_core.L4_state.memory.runtime_state_guard
E     agentic_core\L5_safety\reasoning\PolicyNeuralAutoImmuneAgent.py:22 imports agentic_core.L4_state.reasoning.RedisSovereignAgent
E     agentic_core\L5_safety\reasoning\PreCommitSovereignAgent.py:4 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\PredictiveCostAuditorAgent.py:27 imports agentic_core.L2_execution.reasoning.base
E     agentic_core\L5_safety\reasoning\RedSentinelAgent.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\RedSentinelAgent.py:137 imports agentic_core.L2_execution.enforcement.llm_router_mcp_client
E     agentic_core\L5_safety\reasoning\RegressionOracleAgent.py:11 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\ReportLocationAgent.py:38 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\RootHygieneAgent.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\SafetyInspectorAgent.py:307 imports agentic_core.L2_execution.enforcement.llm_router_mcp_client
E     agentic_core\L5_safety\reasoning\SelfUpdatingSafetyEngineAgent.py:8 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\SovereignActionPlaneAgent.py:14 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\SprawlInspectorAgent.py:10 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py:10 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\StructuralEngineerAgent.py:31 imports agentic_core.L4_state.utils.complexity_analyzer
E     agentic_core\L5_safety\reasoning\StructuralValidatorAgent.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\StructuralValidatorAgent.py:34 imports agentic_core.L4_state.utils.layer_gravity_util
E     agentic_core\L5_safety\reasoning\StructureEnforcerAgent.py:5 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\StructureHealerAgent.py:38 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\SystemArchitectAgent.py:10 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\reasoning\TestGeneratorAgent.py:14 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\types\heal_llm_seam.py:19 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\types\learning_types.py:8 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\types\safety_types.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\types\ssot_relocator_types.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\types\validation_result_types.py:33 imports agentic_core.L2_execution.reasoning.IntegrityGateExecutorAgent
E     agentic_core\L5_safety\utils\cognitive_batch_processor_util.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\utils\extract_pattern_util.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\utils\fix_inherited_invocation_util.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\utils\force_app_depth_util.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\utils\forge_fortress_util.py:5 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\utils\set_complexity_health_100_util.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\utils\tiered_batch_util.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\utils\unified_cst_healer_util.py:19 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\validators\dependencygraph_validator.py:5 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\validators\report_location_validator.py:29 imports agentic_core.L2_execution.tools
E     agentic_core\L5_safety\validators\structure_drift_validator.py:14 imports agentic_core.L2_execution.tools
E     agentic_core\L6_observability\dashboards\core\experiencein_config.py:18 imports agentic_core.L2_execution.enforcement.redis
E     agentic_core\L6_observability\dashboards\dashboard_generator.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L6_observability\enforcement\reasoning_streamer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L6_observability\enforcement\reasoning_streamer_enforcer.py:3 imports agentic_core.L2_execution.tools
E     agentic_core\L6_observability\utils\fix_testing_observability_util.py:1 imports agentic_core.L2_execution.tools
E     agentic_core\L6_observability\utils\integrity_report_generator_util.py:27 imports agentic_core.L2_execution.tools
E   assert 152 <= 149
E    +  where 152 = len(['agentic_core\\L0_routing\\enforcement\\execution_gateway.py:27 imports agentic_core.L2_execution.enforcement.manifest_hash_validator', 'agentic_core\\L0_routing\\enforcement\\execution_gateway.py:71 imports agentic_core.L2_execution.enforcement.healer_pipe_order', 'agentic_core\\L0_routing\\enforcement\\mutation_prohibition_enforcer.py:233 imports agentic_core.L2_execution.tools.write_gateway', 'agentic_core\\L0_routing\\engines\\escalation_router.py:16 imports agentic_core.L4_state.config.versioned_configs', 'agentic_core\\L0_routing\\engines\\escalation_router.py:22 imports agentic_core.L4_state.enforcement.violation_event_store', 'agentic_core\\L0_routing\\engines\\timeshift_router.py:20 imports agentic_core.L4_state.config.versioned_configs', ...])
____________ TestAllowlistEnforcement.test_total_hits_equals_zero _____________
tests\governance\test_intent_emission_no_mutation.py:174: in test_total_hits_equals_zero
    assert len(hits) == 0, f"Expected zero mutation hits, got {len(hits)}.\n" + "\n".join(
E   AssertionError: Expected zero mutation hits, got 5.
E       ('agentic_core/L4_state/storage/filesystem_store.py', '__init__', 'Call:.mkdir()')
E       ('agentic_core/L4_state/storage/filesystem_store.py', '_get_next_version', 'Call:.mkdir()')
E       ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.rename()')
E       ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.unlink()')
E       ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.write_text()')
E   assert 5 == 0
E    +  where 5 = len({('agentic_core/L4_state/storage/filesystem_store.py', '__init__', 'Call:.mkdir()'), ('agentic_core/L4_state/storage/filesystem_store.py', '_get_next_version', 'Call:.mkdir()'), ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.rename()'), ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.unlink()'), ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.write_text()')})
___________ TestAllowlistEnforcement.test_every_hit_is_allowlisted ____________
tests\governance\test_intent_emission_no_mutation.py:181: in test_every_hit_is_allowlisted
    assert not unexpected, "Non-allowlisted mutation primitives found:\n" + "\n".join(
E   AssertionError: Non-allowlisted mutation primitives found:
E       ('agentic_core/L4_state/storage/filesystem_store.py', '__init__', 'Call:.mkdir()')
E       ('agentic_core/L4_state/storage/filesystem_store.py', '_get_next_version', 'Call:.mkdir()')
E       ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.rename()')
E       ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.unlink()')
E       ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.write_text()')
E   assert not {('agentic_core/L4_state/storage/filesystem_store.py', '__init__', 'Call:.mkdir()'), ('agentic_core/L4_state/storage/filesystem_store.py', '_get_next_version', 'Call:.mkdir()'), ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.rename()'), ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.unlink()'), ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.write_text()')}
_________ TestAllowlistEnforcement.test_hits_equal_allowlist_exactly __________
tests\governance\test_intent_emission_no_mutation.py:195: in test_hits_equal_allowlist_exactly
    assert hits == _ALLOWLIST, (
E   AssertionError: Hits do not match allowlist exactly.
E       Extra: [('agentic_core/L4_state/storage/filesystem_store.py', '__init__', 'Call:.mkdir()'), ('agentic_core/L4_state/storage/filesystem_store.py', '_get_next_version', 'Call:.mkdir()'), ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.rename()'), ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.unlink()'), ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.write_text()')]
E       Missing: []
E   assert {('agentic_co...rite_text()')} == frozenset()
E
E     Extra items in the left set:
E     ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.unlink()')
E     ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.rename()')
E     ('agentic_core/L4_state/storage/filesystem_store.py', '_get_next_version', 'Call:.mkdir()')
E     ('agentic_core/L4_state/storage/filesystem_store.py', '__init__', 'Call:.mkdir()')
E     ('agentic_core/L4_state/storage/filesystem_store.py', 'put', 'Call:.write_text()')...
E
E     ...Full output truncated (30 lines hidden), use '-vv' to show
_________ TestLazySeamAllowlist.test_allowlist_matches_scanner_total __________
tests\governance\test_lazy_seam_allowlist.py:70: in test_allowlist_matches_scanner_total
    assert allowlist_total == scanner_total, (
E   AssertionError: Allowlist has 68 entries but scanner found 77
E   assert 68 == 77
___ TestLazySeamAllowlist.test_allowlist_enforcement_no_unregistered_seams ____
tests\governance\test_lazy_seam_allowlist.py:89: in test_allowlist_enforcement_no_unregistered_seams
    assert len(violations) == 0, (
E   AssertionError: Found 9 unregistered lazy seams. All seams must be registered in the allowlist.
E   assert 9 == 0
E    +  where 9 = len([{'description': 'Lazy seam not found in allowlist: assert_no_persistent_write in agentic_core\\L0_routing\\enforcement\\mutation_prohibition_enforcer.py', 'file_path': 'agentic_core\\L0_routing\\enforcement\\mutation_prohibition_enforcer.py', 'function_name': 'assert_no_persistent_write', 'type': 'LAZY_SEAM_UNREGISTERED'}, {'description': 'Lazy seam not found in allowlist: print_execution_plan in agentic_core\\L0_routing\\scripts\\execute_ssot.py', 'file_path': 'agentic_core\\L0_routing\\scripts\\execute_ssot.py', 'function_name': 'print_execution_plan', 'type': 'LAZY_SEAM_UNREGISTERED'}, {'description': 'Lazy seam not found in allowlist: print_execution_plan in agentic_core\\L0_routing\\scripts\\execute_ssot.py', 'file_path': 'agentic_core\\L0_routing\\scripts\\execute_ssot.py', 'function_name': 'print_execution_plan', 'type': 'LAZY_SEAM_UNREGISTERED'}, {'description': 'Lazy seam not found in allowlist: print_execution_plan in agentic_core\\L0_routing\\scripts\\execute_ssot.py', 'file_path': 'agentic_core\\L0_routing\\scripts\\execute_ssot.py', 'function_name': 'print_execution_plan', 'type': 'LAZY_SEAM_UNREGISTERED'}, {'description': 'Lazy seam not found in allowlist: print_execution_plan in agentic_core\\L0_routing\\scripts\\execute_ssot.py', 'file_path': 'agentic_core\\L0_routing\\scripts\\execute_ssot.py', 'function_name': 'print_execution_plan', 'type': 'LAZY_SEAM_UNREGISTERED'}, {'description': 'Lazy seam not found in allowlist: print_execution_plan in agentic_core\\L0_routing\\scripts\\execute_ssot.py', 'file_path': 'agentic_core\\L0_routing\\scripts\\execute_ssot.py', 'function_name': 'print_execution_plan', 'type': 'LAZY_SEAM_UNREGISTERED'}, ...])
---------------------------- Captured stdout call -----------------------------
Scanning codebase for lazy seams (Phase 3B universe)...
Found 77 lazy seams
Allowlist contains 68 allowed seams
_ TestNegativeRegressionNewDefinition.test_zero_violations_under_new_definition _
tests\governance\test_upward_import_enforcement.py:729: in test_zero_violations_under_new_definition
    assert violations == [], (
E   AssertionError: NEW_DEFINITION violation(s) reintroduced ? Phase 1 regression:
E       UPWARD_IMPORT: L3 -> L4 in tool_call_store.py:14 (agentic_core.L4_state.storage.filesystem_store)
E       UPWARD_IMPORT: L3 -> L4 in tool_call_store.py:15 (agentic_core.L4_state.storage.persistent_store)
E   assert [ImportViolat...WARD_IMPORT')] == []
E
E     Left contains 2 more items, first extra item: ImportViolation(source_file=WindowsPath('C:/Git/Agentic-Workflow/agentic_core/L3_orchestration/ptc/tool_call_store.py'...r=4, import_statement='agentic_core.L4_state.storage.filesystem_store', line_number=14, violation_type='UPWARD_IMPORT')
E
E     Full diff:
E     - []
E     + [
E     +     ImportViolation(...
E
E     ...Full output truncated (16 lines hidden), use '-vv' to show
_______ TestLazySeamMetric.test_module_level_upward_imports_still_zero ________
tests\governance\test_upward_import_enforcement.py:787: in test_module_level_upward_imports_still_zero
    assert violations == [], (
E   AssertionError: Phase 1 regression ? module-level upward import reintroduced:
E       UPWARD_IMPORT: L3 -> L4 in tool_call_store.py:14 (agentic_core.L4_state.storage.filesystem_store)
E       UPWARD_IMPORT: L3 -> L4 in tool_call_store.py:15 (agentic_core.L4_state.storage.persistent_store)
E   assert [ImportViolat...WARD_IMPORT')] == []
E
E     Left contains 2 more items, first extra item: ImportViolation(source_file=WindowsPath('C:/Git/Agentic-Workflow/agentic_core/L3_orchestration/ptc/tool_call_store.py'...r=4, import_statement='agentic_core.L4_state.storage.filesystem_store', line_number=14, violation_type='UPWARD_IMPORT')
E
E     Full diff:
E     - []
E     + [
E     +     ImportViolation(...
E
E     ...Full output truncated (16 lines hidden), use '-vv' to show
______ TestLazySeamViolation.test_zero_lazy_seam_violations_in_codebase _______
tests\governance\test_upward_import_enforcement.py:835: in test_zero_lazy_seam_violations_in_codebase
    assert violations == [], f"LAZY_SEAM_VIOLATION(s) found ({len(violations)}):\n" + "\n".join(
E   AssertionError: LAZY_SEAM_VIOLATION(s) found (9):
E       LAZY_SEAM_VIOLATION: L0->L2 in mutation_prohibition.py:233 (agentic_core.L2_execution.tools.write_gateway)
E       LAZY_SEAM_VIOLATION: L0->L3 in execute_ssot.py:2691 (agentic_core.L3_orchestration.arbitration.arbitration_contract)
E       LAZY_SEAM_VIOLATION: L0->L3 in execute_ssot.py:2692 (agentic_core.L3_orchestration.arbitration.arbitrator)
E       LAZY_SEAM_VIOLATION: L0->L3 in execute_ssot.py:2693 (agentic_core.L3_orchestration.arbitration.run_advisors)
E       LAZY_SEAM_VIOLATION: L0->L3 in execute_ssot.py:2729 (agentic_core.L3_orchestration.ptc.builtin_tools)
E       LAZY_SEAM_VIOLATION: L0->L3 in execute_ssot.py:2730 (agentic_core.L3_orchestration.ptc.ptc_registry)
E       LAZY_SEAM_VIOLATION: L0->L3 in execute_ssot.py:2731 (agentic_core.L3_orchestration.ptc.tool_call_store)
E       LAZY_SEAM_VIOLATION: L0->L3 in execute_ssot.py:2732 (agentic_core.L3_orchestration.ptc.tool_contract)
E       LAZY_SEAM_VIOLATION: L0->L3 in execute_ssot.py:2733 (agentic_core.L3_orchestration.ptc.tool_invoker)
E   assert [ImportViolat...LATION'), ...] == []
E
E     Left contains 9 more items, first extra item: ImportViolation(source_file=WindowsPath('C:/Git/Agentic-Workflow/agentic_core/L0_routing/enforcement/mutation_prohibit...mport_statement='agentic_core.L2_execution.tools.write_gateway', line_number=233, violation_type='LAZY_SEAM_VIOLATION')
E
E     Full diff:
E     - []
E     + [
E     +     ImportViolation(...
E
E     ...Full output truncated (72 lines hidden), use '-vv' to show
____________ TestLazySeamBudget.test_lazy_seam_budget_not_exceeded ____________
tests\governance\test_upward_import_enforcement.py:887: in test_lazy_seam_budget_not_exceeded
    assert total <= LAZY_SEAM_BUDGET_BASELINE, (
E   AssertionError: Lazy seam budget exceeded: 77 > 68. Add a new _get_* loader or reduce upward imports.
E   assert 77 <= 68
============================== warnings summary ===============================
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_in_dunder_all
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_in_dunder_all
  c:\Git\Agentic-Workflow\tests\governance\test_healing_reentry.py:203: DeprecationWarning: Attribute s is deprecated and will be removed in Python 3.14; use value instead
    if isinstance(elt, ast.Constant) and isinstance(elt.s, str)

tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_in_dunder_all
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_in_dunder_all
  c:\Git\Agentic-Workflow\tests\governance\test_healing_reentry.py:201: DeprecationWarning: Attribute s is deprecated and will be removed in Python 3.14; use value instead
    elt.s

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 7
Passed: 716
Failed: 10
Errors: 0

\u274c GUARDIAN STATUS: FAIL
Architectural violations detected. Review failed tests.
======================================  =======================================
============================ slowest 10 durations =============================
3.13s call     tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_determinism
3.10s call     tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_audit_determinism
3.07s call     tests/governance/test_agent_heal_audit.py::TestDeterminism::test_byte_identical_json_runs
2.51s call     tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_scan_produces_deterministic_results
2.31s call     tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_lazy_upward_import_metric_is_deterministic
2.02s call     tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_scan_produces_deterministic_results
1.55s call     tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_all_agents_have_heal_surface
1.55s call     tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_generation
1.55s call     tests/governance/test_agent_heal_audit.py::TestStructureContract::test_summary_schema
1.54s call     tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_agent_naming_detection
=========================== short test summary info ===========================
FAILED tests/governance/test_cross_layer_import_freeze.py::TestCrossLayerImportFreeze::test_no_new_violations
FAILED tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_total_hits_equals_zero
FAILED tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_every_hit_is_allowlisted
FAILED tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_hits_equal_allowlist_exactly
FAILED tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_matches_scanner_total
FAILED tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_enforcement_no_unregistered_seams
FAILED tests/governance/test_upward_import_enforcement.py::TestNegativeRegressionNewDefinition::test_zero_violations_under_new_definition
FAILED tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_module_level_upward_imports_still_zero
FAILED tests/governance/test_upward_import_enforcement.py::TestLazySeamViolation::test_zero_lazy_seam_violations_in_codebase
FAILED tests/governance/test_upward_import_enforcement.py::TestLazySeamBudget::test_lazy_seam_budget_not_exceeded
================= 10 failed, 716 passed, 4 warnings in 57.81s =================
```

## Scope Isolation Proof
PHASE_TOUCHED_FILES:
  agentic_core/L2_execution/types/vllm_gateway_adapter_types.py
  agentic_core/L2_execution/types/vllm_gateway_integration_types.py
  agentic_core/L2_execution/types/vllm_invariant_contract_types.py
  agentic_core/L2_execution/types/vllm_invariant_verifier_types.py
  tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py
  tests/unit_min_deps/test_vllm_invariant_contract.py
  tests/unit_min_deps/test_vllm_invariant_verifier.py

GOVERNANCE_VIOLATION_FILES:
  agentic_core/L0_routing/enforcement/mutation_prohibition.py
  agentic_core/L0_routing/scripts/execute_ssot.py

OK: intersection is empty

## Proof: FAIL Violation Triggers Gemini Fallback
```
route_to_gemini=True
local_request_present=False
violations_count=1
violations_field_exists=True
violation_0_id=INV_REPLAY_HASH_PRESENT_WHEN_ENABLED
violation_0_severity=FAIL
violation_0_hash=04c9ec6eb405b611b506e5947267660186eaaab6581c90c009e5c30a87dc2a6a
OK: FAIL violation triggers Gemini fallback with violations attached
```

## Git Status
(clean)

## Runner Self-Check Proof
Balanced PowerShell guard policy:
- Hard-fail on shell=True
- Hard-fail on argv[0] containing 'powershell' or 'pwsh'
- Warn-only on output mentions (no false positives)
