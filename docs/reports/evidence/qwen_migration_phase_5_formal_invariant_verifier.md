# Phase 5 Evidence: Formal Invariant Verifier

## Scope
Phase 5 implements runtime invariant verification at the execution boundary (Phase 3 adapter/controller seam).
All violations are deterministically serializable with canonical JSON and SHA256 hashing.
FAIL violations trigger Gemini fallback. Phase 1-4 behavior preserved.

## CODE_COMMIT
cda00fa3e29fdd4a933b495187ab9f8da8a381ff

## EVIDENCE_COMMIT
97c90afd356eb5513562470873ce60192f343611

## FILES_CHANGED_CODE
agentic_core/L2_execution/types/vllm_gateway_adapter.py
agentic_core/L2_execution/types/vllm_gateway_integration.py
agentic_core/L2_execution/types/vllm_invariant_contract.py
agentic_core/L2_execution/types/vllm_invariant_verifier.py
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py
tests/unit_min_deps/test_vllm_invariant_contract.py
tests/unit_min_deps/test_vllm_invariant_verifier.py

## FILES_CHANGED_EVIDENCE
docs/reports/evidence/qwen_migration_phase_5_formal_invariant_verifier.md
tools/evidence/qwen_migration_phase5_evidence_runner.py

## INSPECTED_FILES
agentic_core/L2_execution/types/vllm_invariant_contract.py
agentic_core/L2_execution/types/vllm_invariant_verifier.py
agentic_core/L2_execution/types/vllm_gateway_adapter.py
agentic_core/L2_execution/types/vllm_gateway_integration.py
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
collected 9 items

tests/unit_min_deps/test_vllm_invariant_verifier.py::test_verify_no_violations_on_valid_local_request PASSED [ 11%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_missing_max_tokens PASSED [ 22%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_temperature_not_zero PASSED [ 33%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_missing_seed PASSED [ 44%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_missing_fingerprint_hash PASSED [ 55%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_inv_gemini_fallback_requires_reason PASSED [ 66%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_gemini_fallback_with_reason_no_violation PASSED [ 77%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_multiple_violations_sorted_deterministically PASSED [ 88%]
tests/unit_min_deps/test_vllm_invariant_verifier.py::test_violations_are_deterministic PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 9 passed in 0.04s ==============================
```

## Phase 5 Integration Tests (Invariant Enforcement)
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4 items

tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_local_success_with_zero_violations PASSED [ 25%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_with_fingerprint_produces_no_violations PASSED [ 50%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_result_has_invariant_violations_field PASSED [ 75%]
tests/agentic_core/L2_execution/types/test_vllm_invariant_enforcement.py::test_adapter_preserves_phase_1_4_behavior PASSED [100%]

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 4 passed in 0.05s ==============================
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

## Git Status
(clean)

## Runner Self-Check Proof
Balanced PowerShell guard policy:
- Hard-fail on shell=True
- Hard-fail on argv[0] containing 'powershell' or 'pwsh'
- Warn-only on output mentions (no false positives)
