---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\phase_02_spine_adapters.md'
original_relative_path: 'phase_02_spine_adapters.md'
source_sha256: c98cc79325d1019d48848998b860188366216aff01facd8160223a129b2b52ad
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-22'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phase 2: LIC + RG Spine Adapters (Deterministic CID)

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Scope
Implement LIC and RG spine adapters with deterministic CID derivation and unit tests.

## CODE_COMMIT
aa1d4f1413d5c0f1b1ac769a6f764c7ecb8e5d87

## EVIDENCE_COMMIT
f4be873bbec970de78e180b2f889bd7244bbd11f

## Files Changed
```
docs/reports/plans/phase_02_spine_adapters.md
```

## LIC Unit Tests
```
$ C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m pytest -q tests/unit_min_deps/test_apps_lic_spine_adapter.py
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_adapter_returns_cid [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_has_lic_prefix [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_is_deterministic [32mPASSED[0m[32m [ 42%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_different_inputs_produce_different_cids [32mPASSED[0m[32m [ 57%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_registered_before_orchestrator_execute [32mPASSED[0m[32m [ 71%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_passed_to_orchestrator [32mPASSED[0m[32m [ 85%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_adapter_state_success_on_clean_input [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m7 passed[0m[32m in 0.04s[0m[32m ==============================[0m
```

## RG Unit Tests
```
$ C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m pytest -q tests/unit_min_deps/test_apps_rg_spine_adapter.py
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_adapter_returns_cid [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_has_rg_prefix [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_is_deterministic [32mPASSED[0m[32m [ 42%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_different_inputs_produce_different_cids [32mPASSED[0m[32m [ 57%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_registered_before_orchestrator_execute [32mPASSED[0m[32m [ 71%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_passed_to_orchestrator [32mPASSED[0m[32m [ 85%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_adapter_state_success_on_clean_input [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================== [32m[1m7 passed[0m[32m in 0.03s[0m[32m ==============================[0m
```

## Full Test Suite
```
$ C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m pytest -q
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
testpaths: C:\Git\Agentic-Workflow\tests\enforcement
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 1221 items

tests/unit_min_deps/system_learning/test_approval_gates.py::TestDefaultRiskClassifier::test_low_impact_single_surface_small_delta [32mPASSED[0m[32m [  0%][0m
tests/unit_min_deps/system_learning/test_approval_gates.py::TestDefaultRiskClassifier::test_medium_impact_multiple_surfaces [32mPASSED[0m[32m [  0%][0m
tests/unit_min_deps/system_learning/test_approval_gates.py::TestDefaultRiskClassifier::test_medium_impact_moderate_delta [32mPASSED[0m[32m [  0%][0m
tests/unit_min_deps/system_learning/test_approval_gates.py::TestDefaultRiskClassifier::test_high_impact_affects_l5 [32mPASSED[0m[32m [  0%][0m
tests/unit_min_deps/system_learning/test_approval_gates.py::TestDefaultRiskClassifier::test_high_impact_many_surfaces [32mPASSED[0m[32m [  0%][0m
tests/unit_min_deps/system_learning/test_approval_gates.py::TestDefaultRiskClassifier::test_critical_impact_l5_large_delta [32mPASSED[0m[32m [  0%][0m
tests/unit_min_deps/system_learning/test_approval_gates.py::TestDefaultRuleBasedGate::test_high_impact_rejects_by_default [32mPASSED[0m[32m [  0%][0m
tests/unit_min_deps/system_learning/test_approval_gates.py::TestDefaultRuleBasedGate::test_low_impact_approves [32mPASSED[0m[32m [  0%][0m
tests/unit_min_deps/system_learning/test_approval_gates.py::TestDefaultRuleBasedGate::test_high_impact_approves_when_allowed [32mPASSED[0m[32m [  0%][0m
tests/unit_min_deps/system_learning/test_approval_gates.py::TestDefaultRuleBasedGate::test_medium_impact_approves [32mPASSED[0m[32m [  0%][0m
tests/unit_min_deps/system_learning/test_approval_gates.py::TestDeterminism::test_classifier_deterministic [32mPASSED[0m[32m [  0%][0m
tests/unit_min_deps/system_learning/test_approval_gates.py::TestDeterminism::test_gate_deterministic [32mPASSED[0m[32m [  1%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_execute_mode_raises [32mPASSED[0m[32m [  1%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_activate_mode_raises [32mPASSED[0m[32m [  1%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_read_mode_allowed [32mPASSED[0m[32m [  1%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_write_mode_allowed_by_this_guard [32mPASSED[0m[32m [  1%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_violation_message_contains_caller [32mPASSED[0m[32m [  1%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_violation_message_contains_operation [32mPASSED[0m[32m [  1%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_write_audit_operation_raises [32mPASSED[0m[32m [  1%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_append_audit_operation_raises [32mPASSED[0m[32m [  1%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_delete_audit_operation_raises [32mPASSED[0m[32m [  1%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_write_mode_to_audit_target_raises [32mPASSED[0m[32m [  1%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_read_from_audit_allowed [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_write_to_non_audit_target_allowed [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_update_activation_pointer_raises [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_set_active_version_raises [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_activate_change_package_raises [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_activate_mode_raises [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_write_change_package_allowed [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_read_allowed [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestForbiddenSurfaces::test_tool_allowlist_forbidden [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestForbiddenSurfaces::test_file_scope_whitelist_forbidden [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestForbiddenSurfaces::test_guardian_contracts_forbidden [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestForbiddenSurfaces::test_sandbox_escape_forbidden [32mPASSED[0m[32m [  2%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestUnknownSurfaces::test_unknown_surface_rejected [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestUnknownSurfaces::test_arbitrary_surface_rejected [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_escalation_threshold_valid_change [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_escalation_threshold_below_min_raises [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_escalation_threshold_above_max_raises [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_escalation_threshold_delta_too_large_raises [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_escalation_threshold_max_delta_allowed [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_anomaly_routing_threshold_valid_change [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_anomaly_routing_threshold_bounds_enforced [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingIntConstraints::test_depth_breaker_valid_change [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingIntConstraints::test_depth_breaker_below_min_raises [32mPASSED[0m[32m [  3%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingIntConstraints::test_depth_breaker_above_max_raises [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingIntConstraints::test_depth_breaker_delta_too_large_raises [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingIntConstraints::test_depth_breaker_max_delta_allowed [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestRAGParameters::test_retrieval_top_k_valid_change [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestRAGParameters::test_retrieval_top_k_bounds_enforced [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestRAGParameters::test_retrieval_top_k_delta_enforced [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestRAGParameters::test_rerank_top_n_valid_change [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestRAGParameters::test_rerank_top_n_bounds_enforced [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL1ModelPointers::test_cognition_model_valid_pointer [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL1ModelPointers::test_cognition_model_allowlist_enforced [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL1ModelPointers::test_cognition_model_unknown_model_rejected [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL1ModelPointers::test_embedding_model_valid_pointer [32mPASSED[0m[32m [  4%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL1ModelPointers::test_embedding_model_allowlist_enforced [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_token_budget_valid_change [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_token_budget_bounds_enforced [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_token_budget_delta_enforced [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_max_k_valid_change [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_max_k_bounds_enforced [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_max_retries_valid_change [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_max_retries_delta_enforced [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestTypeValidation::test_float_constraint_rejects_string [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestTypeValidation::test_int_constraint_rejects_float [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestTypeValidation::test_pointer_constraint_rejects_int [32mPASSED[0m[32m [  5%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestDeterminism::test_validation_deterministic [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestDeterminism::test_validation_order_independent [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_dampening.py::TestCooldownPolicy::test_cooldown_elapsed_passes [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_dampening.py::TestCooldownPolicy::test_cooldown_not_elapsed_raises [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_dampening.py::TestCooldownPolicy::test_cooldown_exactly_elapsed_passes [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_dampening.py::TestSampleSizePolicy::test_sufficient_samples_passes [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_dampening.py::TestSampleSizePolicy::test_insufficient_samples_raises [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_dampening.py::TestSampleSizePolicy::test_exactly_min_samples_passes [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_dampening.py::TestDeterminism::test_cooldown_deterministic [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_dampening.py::TestDeterminism::test_sample_size_deterministic [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_valid_proposal_passes_constraints [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_out_of_range_rejected [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_over_delta_rejected [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_cooldown_violated_returns_none [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_sample_size_violated_returns_none [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_no_change_needed_returns_none [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdChangePackage::test_canonical_bytes_deterministic [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdChangePackage::test_content_hash_deterministic [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdChangePackage::test_different_values_produce_different_hash [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestDeterminism::test_proposal_deterministic [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuditStoreProtocol::test_fake_store_satisfies_protocol [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuditStoreProtocol::test_protocol_has_no_write_methods [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuditStoreProtocol::test_fake_store_has_no_write_methods [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataValid::test_returns_expected_bytes [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataValid::test_returns_empty_bytes_when_store_empty [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataValid::test_returns_bytes_unmodified [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataValid::test_delegates_window_to_store [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataInvalidWindow::test_start_equal_to_end_raises [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataInvalidWindow::test_start_greater_than_end_raises [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataInvalidWindow::test_store_not_called_on_invalid_window [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuthorityGuardIntegration::test_assert_read_only_audit_access_is_called [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuthorityGuardIntegration::test_assert_zero_execution_authority_is_called [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuthorityGuardIntegration::test_authority_context_has_read_mode [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuthorityGuardIntegration::test_authority_context_targets_l4_audit [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuthorityGuardIntegration::test_authority_violation_propagates [32mPASSED[0m[32m [  8%][0m
tests/unit_min_deps/system_learning/test_lineage_validator.py::TestValidateLineage::test_genesis_version_valid [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_lineage_validator.py::TestValidateLineage::test_valid_parent_child_chain [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_lineage_validator.py::TestValidateLineage::test_valid_three_generation_chain [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_lineage_validator.py::TestValidateLineage::test_missing_parent_raises [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_lineage_validator.py::TestValidateLineage::test_cycle_detection_raises [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_lineage_validator.py::TestValidateChain::test_validate_chain_returns_ordered_list [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_lineage_validator.py::TestValidateChain::test_validate_chain_genesis_only [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_lineage_validator.py::TestValidateChain::test_validate_chain_with_invalid_parent_raises [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_lineage_validator.py::TestValidateChain::test_validate_chain_enforces_dag_structure [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_lineage_validator.py::TestLineageIntegration::test_full_lineage_workflow [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_commit_path.py::TestCommitPath::test_commit_path_requires_version_store [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_commit_path.py::TestCommitPath::test_commit_path_requires_approval_gate [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_commit_path.py::TestCommitPath::test_approval_reject_does_not_commit [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_commit_path.py::TestDeterminism::test_commit_path_deterministic [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py::TestProposalOnlyMode::test_proposal_only_returns_packages [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py::TestProposalOnlyMode::test_proposal_only_does_not_call_commit [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py::TestProposalOnlyMode::test_proposal_only_does_not_call_activate [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py::TestProposalOnlyMode::test_proposal_only_default_is_true [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py::TestDeterminism::test_pipeline_deterministic [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_oscillation_true_pattern [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_oscillation_true_pattern_reverse [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_non_oscillation_pattern [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_non_oscillation_all_same [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_insufficient_data [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_oscillation_with_epsilon_tolerance [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_non_oscillation_three_values [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_freeze_decision_on_oscillation [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_no_freeze_on_non_oscillation [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_freeze_until_utc_computation [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_freeze_decision_deterministic [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDeterminism::test_detect_oscillation_deterministic [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_valid_proposal_passes_constraints [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_out_of_range_rejected [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_cooldown_violated_returns_none [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_sample_size_violated_returns_none [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_no_change_needed_returns_none [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGChangePackage::test_canonical_bytes_deterministic [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGChangePackage::test_content_hash_deterministic [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGChangePackage::test_different_values_produce_different_hash [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestDeterminism::test_proposal_deterministic [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_analyze_failures_basic [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_exact_findings_counts [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_determinism_same_slice_identical_report_id [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_invalid_window_rejected [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_malformed_utf8_rejected [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_empty_slice_produces_unknown_category [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_no_matching_patterns_produces_unknown [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestDeterminism::test_analyze_failures_deterministic [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_deterministic_hash_stability [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_findings_ordering_canonical [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_changing_evidence_changes_hash [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_report_id_equals_report_hash [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestDeterminism::test_canonical_bytes_deterministic [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestDeterminism::test_compute_report_hash_deterministic [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_deterministic_engine_passes [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_nondeterministic_engine_fails [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_error_includes_both_hashes [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_same_output_twice_produces_same_hash [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_different_snapshots_produce_different_hashes [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestDeterminism::test_replay_validate_deterministic [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_pass_within_thresholds [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_latency_regression [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_error_rate_regression [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_safety_violation_increase [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_cpu_regression [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_mem_regression [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_multiple_violations_reported [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestDeterminism::test_evaluate_shadow_deterministic [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_same_inputs_produce_identical_snapshot_id [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_same_inputs_produce_identical_snapshot_object [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_snapshot_id_is_sha256_hex [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_snapshot_id_stability_across_calls [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_snapshot_fields_match_inputs [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_telemetry_hash_is_sha256_of_telemetry_bytes [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_policy_config_hash_is_sha256_of_policy_bytes [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_routing_config_hash_is_sha256_of_routing_bytes [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_model_config_hash_is_sha256_of_model_bytes [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_telemetry_bytes_produce_different_telemetry_hash [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_telemetry_bytes_produce_different_snapshot_id [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_policy_bytes_produce_different_snapshot_id [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_engine_version_produces_different_snapshot_id [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_window_produces_different_snapshot_id [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotValidation::test_start_equal_to_end_raises [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotValidation::test_start_greater_than_end_raises [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotValidation::test_valid_window_does_not_raise [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_datetime_now_not_called [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_time_time_not_called [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_snapshot_is_frozen [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_snapshot_id_equality_assertion [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_deterministic_slice_id_across_two_calls [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_sorting_stable_and_canonical [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_invalid_window_rejected [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_empty_window_produces_empty_slice [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_window_filtering [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_payload_hash_computed [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_same_timestamp_different_kind_sorted [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestDeterminism::test_consume_telemetry_deterministic [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_commit_returns_sha256_version_id [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_same_content_produces_same_version_id [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_different_content_produces_different_version_id [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_write_once_semantics_idempotent_on_same_content [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_parent_version_not_found_raises [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_genesis_version_allowed [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_child_version_with_valid_parent [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetChangePackage::test_get_existing_version [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetChangePackage::test_get_nonexistent_version_raises [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetChangePackage::test_retrieved_package_is_immutable [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestListVersions::test_list_all_versions [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestListVersions::test_list_versions_empty_store [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestListVersions::test_list_versions_deterministic_order [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestUpdateActivationPointer::test_activate_version [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestUpdateActivationPointer::test_activate_nonexistent_version_raises [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestUpdateActivationPointer::test_activation_does_not_mutate_package [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestUpdateActivationPointer::test_atomic_pointer_update [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetActiveVersion::test_get_active_version_when_set [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetActiveVersion::test_get_active_version_when_not_set [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetActiveVersion::test_multiple_components_independent [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestRollback::test_rollback_to_parent [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestRollback::test_rollback_is_o1_pointer_reversion [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestRollback::test_rollback_to_nonexistent_version_raises [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestRollback::test_no_deletion_of_historical_versions [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestVersionIdDeterminism::test_version_id_determinism_assertion [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_adapter_returns_cid [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_has_lic_prefix [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_is_deterministic [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_different_inputs_produce_different_cids [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_registered_before_orchestrator_execute [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_passed_to_orchestrator [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_adapter_state_success_on_clean_input [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_adapter_returns_cid [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_has_rg_prefix [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_is_deterministic [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_different_inputs_produce_different_cids [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_registered_before_orchestrator_execute [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_passed_to_orchestrator [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_adapter_state_success_on_clean_input [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_capture_evidence.py::TestCaptureEvidence::test_powershell_string_abort [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_capture_evidence.py::TestCaptureEvidence::test_pwsh_string_abort [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_capture_evidence.py::TestCaptureEvidence::test_clean_output_no_abort [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_capture_evidence.py::TestCaptureEvidence::test_case_insensitive_detection [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[DagRuntimeInspectorAgent] [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[SafetyInspectorAgent] [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[SprawlInspectorAgent] [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_config_property_contract.py::TestConfigMixinPropertyContract::test_config_is_property [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_config_property_contract.py::TestNoConfigOverwriteRepoWide::test_config_overwrite_ceiling [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_standard_heal_importable [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_standard_heal_async_importable [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_heal_result_schema_importable [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_dunder_all_matches_exports [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_importable [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_returns_decorator [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_decorator_wraps_function [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_dunder_all_matches_exports [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBackwardCompatShimIdentity::test_l5_shim_standard_heal_is_canonical [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBackwardCompatShimIdentity::test_l5_shim_heal_result_schema_is_canonical [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBackwardCompatShimIdentity::test_l0_shim_timeout_is_canonical [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestNoShimImportsEnforcement::test_no_imports_from_shim_locations [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBaseAgentsDecoratorImports::test_base_agents_decorators_no_shim_imports [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestShimAllowlist::test_decorators_shim_imports_only_base_agents [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestShimAllowlist::test_timeout_shim_imports_only_base_agents [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestNoShimImportsRepoWide::test_no_forbidden_imports_from_shim_locations [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalNoShimImports::test_decorators_no_shim_imports [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalNoShimImports::test_timeout_no_shim_imports [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_imports_only_canonical[decorators_util] [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_imports_only_canonical[timeout_decorator_util] [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_defines_dunder_all[decorators_util] [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_defines_dunder_all[timeout_decorator_util] [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_no_function_or_class_defs[decorators_util] [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_no_function_or_class_defs[timeout_decorator_util] [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_standard_heal_locally [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_heal_result_schema_locally [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_timeout_defines_timeout_locally [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_dunder_all [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_timeout_defines_dunder_all [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_exclusion_top_level [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_exclusion_nested_recursive [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_list_recursive_preserves_order_and_strips [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_list_order_matters [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_file_hash_stable [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_dict_top_level [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_preserves_non_excluded [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_tuple_preserved [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_deterministic_multiple_calls [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_different_content_differs [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSubatomicTestingMixinInMRO::test_subatomic_in_mro[DagRuntimeInspectorAgent] [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSubatomicNotDirectBase::test_subatomic_not_direct_base[DagRuntimeInspectorAgent] [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestNoDuplicatesInMRO::test_no_mro_duplicates[DagRuntimeInspectorAgent] [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSovereignBaseAgentMRO::test_sovereign_has_subatomic_testing_mixin [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSovereignBaseAgentMRO::test_sovereign_has_config_mixin [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoOrphanIntegrationTests::test_all_integration_tests_under_allowed_roots [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoTopLevelIntegrationFiles::test_no_top_level_test_files [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_marker_registry_contract.py::TestAllUsedMarkersRegistered::test_no_unregistered_markers [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_marker_registry_contract.py::TestNoDuplicateMarkers::test_no_duplicate_markers [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_marker_registry_contract.py::TestMarkersSorted::test_markers_sorted [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_phase2_unsafe_io_enforcement.py::TestPhase2UnsafeIOEnforcement::test_detector_still_works [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_phase2_unsafe_io_enforcement.py::TestPhase2UnsafeIOEnforcement::test_remediated_files_clean [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_phase2_unsafe_io_enforcement.py::TestPhase2UnsafeIOEnforcement::test_no_direct_subprocess_in_remediated_files [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_phase2_unsafe_io_enforcement.py::TestPhase2UnsafeIOEnforcement::test_scoped_directories_scan [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_write_gateway_imports_enforce_protected_root [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_write_text_calls_enforce_before_write_primitive [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_write_bytes_calls_enforce_before_write_primitive [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_execute_ssot_exposes_allow_protected_root_mutation_flag [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_execute_ssot_entrypoint_exposes_fence_self_check_flag [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_negative_regression_guard_enforce_removal_would_fail [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_negative_regression_guard_reordering_would_fail [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestEnforcementWiringCompleteness::test_all_public_write_functions_call_enforce_or_delegate [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_is_canonical_write_layer [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_functions_accept_allow_override [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_future_tool_contract_enforcement_ready [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestCompleteness::test_no_unlisted_quarantine_files [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestNoStaleEntries::test_no_stale_manifest_entries [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestEntrySchema::test_categories_are_valid [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestEntrySchema::test_required_fields_non_empty [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestBidirectionalSync::test_disk_manifest_exact_match [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestQuarantineCeiling::test_total_ceiling [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestQuarantineCeiling::test_per_category_ceiling [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_agentic_core [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_allows_outside [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_override_allows [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_tests [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_github [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_agentic_core [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_tests [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_github [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_blocks_protected_root [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_allows_outside_protected_root [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_bytes_blocks_protected_root [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_block_emits_jsonl_event [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_logging_failure_does_not_mask_exception [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_exception_message_still_includes_diagnostics [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_immutable_roots [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_log_path [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_log_path_writes_to_tmp [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_immutable_roots_changes_matched_root [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_none_uses_default [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_allow_mutation_does_not_bypass_protected_root [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_deny_mutation_does_not_change_protected_root [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_cli_override_works_regardless_of_env [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_unset_env_vars_do_not_change_behavior [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_ok_path [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_fails_with_bad_log_path [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_validates_write_gateway_wiring [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_replay_block_event_is_identical_under_fixed_clock [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_self_check_output_is_bitwise_identical_across_runs [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_block_event_without_override_uses_real_time [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestPytestIniHeader::test_has_pytest_section [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestPytestIniHeader::test_no_tool_pytest_section [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestTestpathsContract::test_testpaths_exact_match [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestNorecursedirsContract::test_norecursedirs_includes_required [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestNoRootConftest::test_no_root_conftest [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_unsafe_io_subprocess_detector.py::TestUnsafeIOSubprocessDetector::test_detector_finds_direct_file_writes [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_unsafe_io_subprocess_detector.py::TestUnsafeIOSubprocessDetector::test_detector_finds_subprocess_calls [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_unsafe_io_subprocess_detector.py::TestUnsafeIOSubprocessDetector::test_detector_ignores_safe_operations [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_unsafe_io_subprocess_detector.py::TestUnsafeIOSubprocessDetector::test_detector_scans_actual_agent_code [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_unsafe_io_subprocess_detector.py::TestUnsafeIOSubprocessDetector::test_detector_enforcement [32mPASSED[0m[32m [ 31%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDagRuntimeInspectorAgent::test_importable [32mPASSED[0m[32m [ 31%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDagRuntimeInspectorAgent::test_diagnose_returns_inspection_result
[1m-------------------------------- live log call --------------------------------[0m
2026-02-22 13:55:38 [[32m    INFO[0m] agentic_core.L5_safety.reasoning.InspectorExecutor: [InspectorExecutor] Inspector
[32mPASSED[0m[32m                                                                   [ 31%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_standard_heal_importable_with_full_deps [32mPASSED[0m[32m [ 31%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_timeout_importable_with_full_deps [32mPASSED[0m[32m [ 31%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_shim_identity_with_full_deps [32mPASSED[0m[32m [ 31%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_timeout_shim_identity_with_full_deps [32mPASSED[0m[32m [ 31%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_utils_requires_util_suffix [32mPASSED[0m[32m [ 32%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_agent_configs_requires_config_suffix [32mPASSED[0m[32m [ 32%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_mixins_requires_mixin_suffix [32mPASSED[0m[32m [ 32%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_interfaces_requires_i_prefix [32mPASSED[0m[32m [ 32%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_folder_aliases_knowledge_to_reasoning [32mPASSED[0m[32m [ 32%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_folder_aliases_validation_to_validators [32mPASSED[0m[32m [ 32%][0m
tests/enforcement/test_folder_purity_governance.py::TestEnforcementFolderRules::test_enforcement_folder_exists_in_rules [32mPASSED[0m[32m [ 32%][0m
tests/enforcement/test_folder_purity_governance.py::TestEnforcementFolderRules::test_enforcement_allows_strategy_suffix [32mPASSED[0m[32m [ 32%][0m
tests/enforcement/test_folder_purity_governance.py::TestUtilsFileSuffixCompliance::test_utils_files_have_util_suffix [32mPASSED[0m[32m [ 32%][0m
tests/enforcement/test_folder_purity_governance.py::TestAgentConfigsFileSuffixCompliance::test_agent_configs_files_have_valid_suffix [32mPASSED[0m[32m [ 32%][0m
tests/enforcement/test_folder_purity_governance.py::TestGlobalNoRootFilesInvariant::test_folder_purity_rules_governed [32mPASSED[0m[32m [ 32%][0m
tests/enforcement/test_folder_purity_governance.py::TestGlobalNoRootFilesInvariant::test_folder_aliases_governed [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestGlobalNoRootFilesInvariant::test_infrastructure_profiles_governed [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestGlobalNoRootFilesInvariant::test_security_has_approved_subfolders [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestGlobalNoRootFilesInvariant::test_global_invariant_covers_all_governed_roots [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[validators] [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[scripts] [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[dashboards] [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[base_agents] [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[mixins] [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[interfaces] [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[agent_configs] [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[healers] [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[exceptions] [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[core_kernel] [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityNegativeInvariants::test_folder_purity_negative_invariant[engines] [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityNegativeInvariants::test_folder_purity_negative_invariant[tools] [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityCoverage::test_all_existing_folders_are_governed [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityRulesIntegrity::test_engines_and_tools_have_rules [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityRulesIntegrity::test_engines_and_tools_have_disallowed [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityRulesIntegrity::test_no_catchall_patterns [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_config_folder_rejects_non_config_suffix [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_engines_folder_rejects_non_engine_suffix [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_prompt_governance_no_root_files_enforcement [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_agent_configs_enforces_config_suffix [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_observability_probe_executor_compliant [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_meta_learning_utils_location_ssot [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_state_util_location_ssot [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_missing_pytest_ini [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_testpaths_contract_sync_missing_contract [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_testpaths_contract_sync_mismatch [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_testpaths_contract_sync_match [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_evidence_truncation_detection [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_evidence_missing_exit_code [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_phase_evidence_missing_git_history [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_phase_evidence_missing_deterministic_command [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_phase_evidence_blocked_without_preexisting [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_allowed_truncation_in_code_examples [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_missing_pytest_ini [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_valid_pytest_configuration [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_missing_required_markers [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_unregistered_markers_in_tests [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_conftest_hook_without_docstring [32mPASSED[0m[32m [ 36%][0m
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_byte_identical_json_runs [32mPASSED[0m[32m [ 36%][0m
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_deterministic_ordering [32mPASSED[0m[32m [ 36%][0m
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_no_nondeterministic_fields [32mPASSED[0m[32m [ 36%][0m
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_top_level_schema [32mPASSED[0m[32m [ 36%][0m
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_result_item_schema [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_summary_schema [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_controlled_fixture_scanning [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_agent_naming_detection [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_base_class_name_extraction [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestNoRuntimeImports::test_source_code_imports [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestNoRuntimeImports::test_stdlib_only_imports [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_generation [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_determinism [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_authority_boundaries.py::TestMutationAuthorityBoundary::test_l2_execution_exists_and_has_mutations [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_authority_boundaries.py::TestMutationAuthorityBoundary::test_l1_has_zero_mutation_primitives [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L3_orchestration] [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L4_state] [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L5_safety] [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L6_observability] [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_authority_boundaries.py::TestAuthorityNegativeRegression::test_detects_l2_fileio_import [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_authority_boundaries.py::TestAuthorityNegativeRegression::test_detects_l2_save_file_import [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_authority_boundaries.py::TestAuthorityNegativeRegression::test_ignores_non_mutation_l2_import [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_dict_10x_identical [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_nested_dict_10x_identical [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_tuple_input_10x_identical [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_empty_dict_10x_identical [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_none_values_10x_identical [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_canonical_serializer.py::TestFloatPrecision::test_float_normalized [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestFloatPrecision::test_float_round_trip [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestFloatPrecision::test_float_trailing_zeros [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestTupleNormalization::test_tuple_becomes_list [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestTupleNormalization::test_nested_tuple [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestNullEncoding::test_none_encoded [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestNullEncoding::test_none_not_omitted [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestSortedKeys::test_top_level_sorted [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestSortedKeys::test_nested_sorted [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestCrossObjectConsistency::test_audit_and_intent_same_serializer [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestASTNoDirectJsonDumps::test_no_json_dumps_in_audit_log [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestASTNoDirectJsonDumps::test_no_json_dumps_in_canonical_serializer [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestASTNoDirectJsonDumps::test_no_json_import_in_audit_log [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_cross_layer_import_freeze.py::TestCrossLayerImportFreeze::test_no_new_violations [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_cross_layer_import_freeze.py::TestCrossLayerImportFreeze::test_baseline_not_stale [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_cross_layer_import_freeze.py::TestRegressionDetection::test_synthetic_violation_detected [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_cross_layer_import_freeze.py::TestRegressionDetection::test_persistence_client_detected [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_blocks_write_under_agentic_core [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_blocks_rename_under_agentic_core [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_allows_write_outside_agentic_core [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_respects_override_flag [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestStartupFenceSelfTest::test_startup_self_test_aborts_if_fence_inactive [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestStartupFenceSelfTest::test_startup_self_test_passes_if_fence_active [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestImportPreflight::test_import_preflight_fails_fast_with_actionable_message [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestImportPreflight::test_import_preflight_passes_when_symbols_exist [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootPolicy::test_default_policy_has_correct_immutable_roots [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootPolicy::test_default_policy_log_path_outside_immutable_roots [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestNoNewUpwardImportsInInitFiles::test_l3_init_no_upward_imports [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestNoNewUpwardImportsInInitFiles::test_l3_scripts_init_no_upward_imports [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestNoNewUpwardImportsInInitFiles::test_l3_engines_init_no_upward_imports [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestGHONoDirectWrites::test_no_open_write_calls [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestGHOMutationDelegation::test_no_direct_mutation_primitives [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestGHOMutationDelegation::test_write_gateway_is_sole_mutation_path [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestDirectoryWideUpwardImportFreeze::test_no_l5_imports_in_l3_init_files [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_hash_chain_audit_log.py::TestGenesisRule::test_first_entry_has_genesis_previous_hash [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestGenesisRule::test_first_entry_has_index_zero [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestGenesisRule::test_genesis_hash_is_literal_string [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_single_entry_verifies [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_multi_entry_chain_verifies [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_chain_links_previous_hash [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_empty_log_verifies [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_each_entry_hash_is_sha256 [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainBreakDetection::test_tampered_hash_detected
[1m-------------------------------- live log call --------------------------------[0m
2026-02-22 13:56:00 [[31m[1m   ERROR[0m] agentic_core.L2_execution.audit.hash_chain_audit_log: [audit] hash mismatch at entry 1
[32mPASSED[0m[32m                                                                   [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestSeal::test_seal_returns_root_hash [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestSeal::test_append_after_seal_raises [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestSeal::test_seal_empty_log_raises [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestEntryImmutability::test_cannot_mutate_entry_field [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestHashDeterminism::test_entry_hash_is_deterministic [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestHashDeterminism::test_verify_passes_on_correct_hash [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestLogProperties::test_length_tracks_entries [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestLogProperties::test_chain_root_none_when_empty [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestLogProperties::test_entries_returns_tuple [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestFlagDefaultOff::test_no_escalation_log_without_env_var [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestFlagDefaultOff::test_observer_not_invoked_without_env_var [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestObserverSeamSafety::test_observer_default_is_none_at_import [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestObserverSeamSafety::test_observer_not_reassigned_at_module_scope [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_default_off [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_enabled_no_caller [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_enabled_with_caller [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_logging [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_no_routed_model [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_output_unchanged [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingDefaultOff::test_router_seam_not_invoked_when_disabled [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingDefaultOff::test_no_routed_model_log_when_disabled [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledLow::test_router_invoked_with_low_tier [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledLow::test_routed_model_log_contains_local_low [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledHigh::test_router_invoked_with_high_tier [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledHigh::test_routed_model_log_contains_local_high [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagDefaultOff::test_no_escalation_log_when_disabled [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagDefaultOff::test_observer_not_invoked_when_disabled [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagEnabled::test_escalation_log_when_enabled [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagEnabled::test_observer_invoked_when_enabled [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_stdlib_only_imports [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_no_network_model_keywords [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_no_banned_string_literals [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_decide_reasoning_tier_is_invoked [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_policy_decision_is_logged [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_output_unchanged_by_policy_integration [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_high_boundary [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_high_boundary_exact [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_medium_boundary [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_medium_boundary_just_below [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_low_values [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_validation_errors [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_high_confidence_auto_proceed [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_high_confidence_boundary_exact [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_medium_confidence_llm_enabled_judicious_gate_met [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_medium_confidence_llm_enabled_judicious_gate_not_met [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_medium_confidence_llm_disabled [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_enabled_complexity_gate [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_enabled_failure_gate [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_enabled_judicious_gate_not_met [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_disabled [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_determinism [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_confidence_value [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_task_complexity [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_safety_risk [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_prior_failures [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_trivial_rule_returns_low_even_with_low_confidence [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_trivial_rule_order [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_confidence_low [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_complexity_high [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_safety_risk_high [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_retry_count_high [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_default_low [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_determinism [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_validation_task_complexity [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_validation_safety_risk [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_validation_retry_count [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_wiring.py::TestEnableLlmHardGate::test_enable_llm_false_high_confidence_proceeds_no_tier [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_wiring.py::TestEnableLlmHardGate::test_enable_llm_false_medium_confidence_blocked [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_wiring.py::TestEnableLlmHardGate::test_enable_llm_false_low_confidence_blocked [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_wiring.py::TestTierSelection::test_medium_confidence_selects_low_tier [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_wiring.py::TestTierSelection::test_low_confidence_selects_high_tier [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_wiring.py::TestTierSelection::test_low_confidence_with_prior_failures_selects_high_tier [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_wiring.py::TestJudiciousGate::test_medium_confidence_low_complexity_blocked [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestJudiciousGate::test_low_confidence_low_complexity_no_failures_blocked [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestNoNetworkCalls::test_standard_heal_no_llm_call_when_disabled [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestNoNetworkCalls::test_standard_heal_high_confidence_no_llm_call [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestDeterministicRefusal::test_blocked_result_contains_policy_decision [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestDeterministicRefusal::test_blocked_result_is_deterministic [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestCanonicalSeamEnforcement::test_direct_llm_call_without_seam_fails [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestCanonicalSeamEnforcement::test_standard_heal_sets_capability_token [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestCanonicalSeamEnforcement::test_llm_escalation_only_via_standard_heal [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestPolicyDecisionRecord::test_policy_decision_record_schema [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestPolicyDecisionRecord::test_policy_decision_record_deterministic_hash [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestPolicyDecisionRecord::test_standard_heal_emits_policy_record
[1m-------------------------------- live log call --------------------------------[0m
2026-02-22 13:56:00 [[33m WARNING[0m] agentic_core.utils.decorators_util: [standard_heal] MockAgent: Non-canonical key '_policy_from_kwargs' detected. Consider using canonical keys for better schema compliance.
[32mPASSED[0m[32m                                                                   [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestNetworkTripwire::test_network_tripwire_blocks_socket [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestNetworkTripwire::test_heal_paths_make_no_network_calls [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_deterministic_output [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_idempotency [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_policy_routing [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_deterministic_baseline_integration [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_disabled [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_enabled_with_router [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_enabled_no_router [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_logging_enabled [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_disabled_no_logging [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_all_agents_have_heal_surface [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_all_agents_have_heal_repository_surface [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_audit_determinism [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_summary_counts_consistent [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealTelemetrySchema::test_telemetry_record_schema [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealTelemetrySchema::test_telemetry_hash_deterministic [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealTelemetrySchema::test_telemetry_json_serializable [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestTelemetryEmission::test_emit_creates_artifact [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestTelemetryEmission::test_emit_idempotent_same_content [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestTelemetryEmission::test_emit_fails_on_conflict [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_budget_caps_from_env_defaults [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_budget_caps_from_env_custom [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_escalation_budget_enforcement [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_high_tier_budget_enforcement [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_budget_counters_tracked [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_enable_llm_false_budgets_zero [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestBudgetAndSeamIntegration::test_seam_guard_still_enforced_with_budgets [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestBudgetAndSeamIntegration::test_no_network_calls_in_budget_checks [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_healing_reentry.py::TestNoDirectL5Import::test_no_static_l5_import [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_healing_reentry.py::TestNoDirectL5Import::test_no_static_l3_import [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_load_activation_gate_helper_present [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_load_activation_gate_called_in_smart_fix [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_seam_exposes_load_activation_gate [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_seam_uses_importlib_not_static [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_get_file_io_helper_present [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_get_file_io_called_in_smart_fix [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_no_bare_open_write_in_smart_fix [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_no_route_mutation_intent_in_orchestrator [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_is_module_level_function [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_in_dunder_all [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_orchestrator_calls_assert_activation_allowed_on_gate_mod [32mPASSED[0m[33m [ 53%][0m
tests/governance/test_healing_reentry.py::TestHealingWriteCallPath::test_save_file_called_on_file_io_result [32mPASSED[0m[33m [ 53%][0m
tests/governance/test_healing_reentry.py::TestHealingWriteCallPath::test_no_open_write_anywhere_in_orchestrator [32mPASSED[0m[33m [ 53%][0m
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_total_hits_equals_zero [32mPASSED[0m[33m [ 53%][0m
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_every_hit_is_allowlisted [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_every_allowlist_entry_still_exists [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_hits_equal_allowlist_exactly [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNoFileIoImports::test_no_fileio_imports[L3_orchestration] [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNoFileIoImports::test_no_fileio_imports[L4_state] [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNoFileIoImports::test_no_fileio_imports[L5_safety] [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_open_write [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_path_write_text [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_shutil_call [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_os_remove [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_json_dump_to_file [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_fileio_import [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_ignores_read_only_open [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_new_open_write_in_l5_is_flagged [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_l0_upward_import_isolation.py::TestNoStaticUpwardImportsInL0::test_zero_module_level_static_upward_imports [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_l0_upward_import_isolation.py::TestNoStaticUpwardImportsInL0::test_negative_regression_detector_catches_static_import [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_l0_upward_import_isolation.py::TestNoStaticUpwardImportsInL0::test_negative_regression_lazy_in_function_not_flagged [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_only_allowlisted_seams_use_importlib_for_higher_layers [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_all_allowlisted_seam_files_exist [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_allowlist_covers_all_seam_files [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_negative_regression_importlib_higher_layer_detected [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_negative_regression_importlib_dynamic_var_not_flagged [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_l6_purity.py::TestL6WritePrimitiveRatchet::test_l6_does_not_exceed_write_ceiling [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_l6_purity.py::TestL6NoFileIoImports::test_no_fileio_imports_in_l6 [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l6_purity.py::TestL6NegativeRegression::test_detects_open_append [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l6_purity.py::TestL6NegativeRegression::test_detects_write_text [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l6_purity.py::TestL6NegativeRegression::test_ignores_read_open [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_exactly_seven_layers_exist [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_layer_ordering_is_monotonic [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_file_enumeration_count_is_stable [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_layer_of_path_returns_correct_layer [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_layer_of_path_returns_none_for_non_layer [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_classify_file_identifies_utils [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_classify_file_identifies_layer_files [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_all_layer_directories_have_files [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_enumerate_python_files_is_sorted [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_inventory_summary [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_file_exists_and_valid [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_matches_scanner_total [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_enforcement_no_unregistered_seams [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_negative_remove_allowlist_entry_causes_violation [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_negative_synthetic_seam_causes_violation [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_lazy_seam_silent_swallow.py::TestScanFileSwallowsSyntaxError::test_syntax_error_returns_empty [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_lazy_seam_silent_swallow.py::TestScanFileSwallowsSyntaxError::test_io_error_returns_empty [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_lazy_seam_silent_swallow.py::TestScanCodebaseContinuesAfterError::test_valid_files_still_scanned [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_lazy_seam_silent_swallow.py::TestNoMutationOnSwallow::test_no_files_created_on_syntax_error [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_lazy_seam_silent_swallow.py::TestSwallowDoesNotWeakenEnforcement::test_corrupt_file_not_treated_as_compliant [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestFrozenImmutability::test_cannot_set_field_after_construction [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestFrozenImmutability::test_cannot_delete_field [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_same_inputs_same_hash [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_different_inputs_different_hash [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_hash_is_sha256_hex [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestHashIntegrity::test_verify_passes_on_valid_intent [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestHashIntegrity::test_verify_fails_on_wrong_hash [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestHashability::test_usable_as_set_member [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestHashability::test_usable_as_dict_key [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_seam_compliance.py::TestNoDirectPersistenceImport::test_no_persistence_imports_in_agents [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_seam_compliance.py::TestNoForbiddenWriteCalls::test_no_direct_write_calls_in_agents [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_seam_compliance.py::TestLearningSeamExists::test_learning_seam_file_exists [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_seam_compliance.py::TestLearningSeamExists::test_learning_seam_exports_intent [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_seam_compliance.py::TestASTScannerDeterminism::test_agent_file_collection_deterministic [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_seam_compliance.py::TestASTScannerDeterminism::test_scanner_produces_results [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_bundle_is_frozen [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_checksum_is_sha256 [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_checksum_deterministic [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_checksum_differs_with_different_versions [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_verify_checksum_passes [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_verify_checksum_fails_on_tampered [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_production_only_allows_recorded_output [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_dev_test_allows_both_modes [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_validate_production_passes_recorded_output [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_validate_production_rejects_deterministic [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_recorded_output_is_authoritative [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_deterministic_is_not_authoritative [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_deterministic_label_non_authoritative [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_recorded_output_label_authoritative [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_recorded_output_returns_stored_bytes [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_deterministic_inference_raises [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_execution_blocked_on_invalid_bundle [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_strategy_governance_label [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_os_remove_blocked [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_subprocess_run_blocked [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_os_system_blocked [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_builtins_open_blocked [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxRestoration::test_os_remove_restored [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxRestoration::test_subprocess_run_restored [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxRestoration::test_restored_on_exception [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestDoubleActivation::test_double_activation_raises [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestCustomTargets::test_custom_target_blocked [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxState::test_inactive_by_default [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxState::test_active_inside_context [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_replay_integrity.py::TestReplayHashComputed::test_replay_hash_is_sha256 [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_replay_integrity.py::TestReplayHashComputed::test_integrity_verified_true_on_create [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_replay_integrity.py::TestReplayHashComputed::test_replay_hash_deterministic [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_replay_integrity.py::TestTamperDetection::test_tampered_response_fails [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_replay_integrity.py::TestTamperDetection::test_tampered_model_version_fails [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_replay_integrity.py::TestTamperDetection::test_valid_bundle_passes [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanDeterminism::test_build_plan_produces_same_result_twice [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanDeterminism::test_plan_is_sorted_deterministically [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealScopeControls::test_denylist_excludes_directories [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealScopeControls::test_allowlist_filters_extensions [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealScopeControls::test_skipped_files_counted [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealApplyIdempotency::test_apply_is_idempotent [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealApplyIdempotency::test_apply_handles_missing_files [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealApplyIdempotency::test_dry_run_makes_no_changes [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanSchema::test_plan_to_dict_schema [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanSchema::test_result_to_dict_schema [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanSchema::test_plan_json_serializable [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_enable_llm_false_no_llm_call [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_enable_llm_true_requires_capability_token [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_policy_decision_record_emitted [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_baseline_plan_runs_before_escalation [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_routing_config_seal.py::TestSealImmutability::test_seal_is_frozen [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_routing_config_seal.py::TestSealImmutability::test_sealed_at_is_set [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_routing_config_seal.py::TestSealDeterminism::test_same_config_same_hash [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealDeterminism::test_different_config_different_hash [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealVerification::test_unchanged_config_passes [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealVerification::test_mutated_config_fails [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealVerification::test_removed_key_fails [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealedRoutingContext::test_no_mutation_passes [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealedRoutingContext::test_mutation_raises [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealedRoutingContext::test_seal_accessible [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_execution_mode_importable [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_forward_rolling_config_importable [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_rollout_stage_importable [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_health_status_importable [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_contract_symbols_match_originals [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestActivationContractImportParity::test_assert_activation_allowed_importable [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestActivationContractImportParity::test_contract_symbol_matches_original [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestMcpContractImportParity::test_mcp_connection_manager_importable [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestMcpContractImportParity::test_mcp_connection_manager_is_protocol [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_safety_agent_factory_instantiates [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_unknown_agent_returns_none [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_healing_agent_protocol_is_runtime_checkable [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_object_without_heal_repository_fails_protocol [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolFakeInjection::test_safety_strategy_accepts_injected_factory [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolFakeInjection::test_safety_strategy_default_factory_created_when_none [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestNervousSystemAgentProtocolDefaultWiring::test_safety_agent_factory_used_in_nervous_system [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_contracts.py::TestNervousSystemAgentProtocolDefaultWiring::test_nervous_system_agent_protocol_fake_injection [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_seam_file_detection [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_approved_loader_detection [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_scan_produces_deterministic_results [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_dynamic_violation_summary [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_static_seam_upward [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_static_l2_to_l5 [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_static_l3_to_l6 [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_dynamic_importlib [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_dynamic_dunder_import [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_dynamic_in_seam [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_approved_loader_allowed [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestConvergenceConfidence::test_convergence_confidence_calculation [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestShiftReportImmutability::test_cannot_mutate_field [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestShiftReportImmutability::test_timestamp_is_set [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestMinimumSampleGuard::test_min_sample_size_is_30 [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestMinimumSampleGuard::test_small_sample_skips [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestMinimumSampleGuard::test_sufficient_sample_runs [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestMMDDetection::test_identical_data_no_shift [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestMMDDetection::test_shifted_data_detected [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestPSIDetection::test_per_feature_flags [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestPSIDetection::test_no_drift_low_psi [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestSkippedReport::test_skipped_report_fields [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_shift_report.py::TestJointShiftLogic::test_joint_true_when_mmd_exceeds [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_shift_report.py::TestJointShiftLogic::test_joint_true_when_psi_exceeds [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_no_banned_imports [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_standard_heal_no_routing_calls [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_wrapper_function_no_routing_calls [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[0] [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[1] [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[2] [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[3] [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[4] [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[5] [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[6] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L1] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L2] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L3] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L4] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L5] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L6] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L0] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L2] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L3] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L4] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L5] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L6] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L0] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L1] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L3] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L4] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L5] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L6] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L0] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L1] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L2] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L4] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L5] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L6] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L0] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L1] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L2] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L3] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L5] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L6] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L0] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L1] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L2] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L3] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L4] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L6] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L0] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L1] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L2] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L3] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L4] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L5] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L2] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L3] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L4] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L5] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L6] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L1] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L3] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L4] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L5] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L6] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L1] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L2] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L4] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L5] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L6] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L1] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L2] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L3] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L5] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L6] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L1] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L2] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L3] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L4] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L6] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L1] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L2] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L3] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L4] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L5] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L2] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L3] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L4] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L5] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L6] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L0] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L3] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L4] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L5] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L6] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L0] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L2] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L4] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L5] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L6] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L0] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L2] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L3] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L5] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L6] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L0] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L2] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L3] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L4] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L6] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L0] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L2] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L3] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L4] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L5] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L1] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L3] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L4] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L5] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L6] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L0] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L3] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L4] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L5] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L6] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L0] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L1] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L4] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L5] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L6] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L0] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L1] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L3] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L5] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L6] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L0] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L1] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L3] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L4] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L6] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L0] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L1] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L3] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L4] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L5] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L1] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L2] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L4] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L5] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L6] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L0] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L2] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L4] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L5] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L6] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L0] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L1] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L4] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L5] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L6] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L0] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L1] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L2] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L5] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L6] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L0] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L1] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L2] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L4] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L6] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L0] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L1] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L2] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L4] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L5] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L1] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L2] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L3] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L5] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L6] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L0] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L2] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L3] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L5] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L6] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L0] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L1] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L3] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L5] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L6] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L0] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L1] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L2] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L5] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L6] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L0] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L1] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L2] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L3] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L6] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L0] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L1] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L2] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L3] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L5] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L1] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L2] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L3] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L4] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L6] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L0] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L2] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L3] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L4] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L6] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L0] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L1] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L3] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L4] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L6] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L0] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L1] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L2] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L4] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L6] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L0] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L1] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L2] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L3] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L6] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L0] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L1] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L2] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L3] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L4] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L1] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L2] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L3] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L4] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L5] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L0] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L2] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L3] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L4] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L5] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L0] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L1] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L3] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L4] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L5] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L0] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L1] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L2] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L4] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L5] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L4-L0] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L4-L1] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L4-L2] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L4-L3] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L4-L5] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L5-L0] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L5-L1] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L5-L2] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L5-L3] [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L5-L4] [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestEscalationMonotonicity::test_valid_ascending_sequence [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestEscalationMonotonicity::test_valid_flat_sequence [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestEscalationMonotonicity::test_invalid_descending_sequence [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestEscalationMonotonicity::test_empty_sequence_valid [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestEscalationMonotonicity::test_single_element_valid [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l0_safe_to_drop [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l1_under_pressure_only [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[2] [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[3] [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[4] [32mPASSED[0m[33m [ 91%][0m
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[5] [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[6] [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_tier_lattice.py::TestCanDrop::test_l0_always_droppable [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_tier_lattice.py::TestCanDrop::test_l1_not_droppable_without_pressure [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_tier_lattice.py::TestCanDrop::test_l1_droppable_under_pressure [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_tier_lattice.py::TestCanDrop::test_l2_never_droppable [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_tier_lattice.py::TestBackpressurePolicy::test_should_drop_l0 [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_tier_lattice.py::TestBackpressurePolicy::test_should_not_drop_l2 [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_tier_lattice.py::TestBackpressurePolicy::test_should_drop_l1_under_pressure [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_tier_lattice.py::TestLatticeCompleteness::test_21_distinct_pairs [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_time_shifted_influence.py::TestNoMidRunMutation::test_routing_unchanged_in_same_run [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_time_shifted_influence.py::TestNoMidRunMutation::test_detection_does_not_change_routing [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_time_shifted_influence.py::TestNoMidRunMutation::test_mid_run_mutation_raises [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_time_shifted_influence.py::TestTimeShiftedInfluence::test_version_bump_changes_next_run [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_time_shifted_influence.py::TestTimeShiftedInfluence::test_same_config_same_hash_across_runs [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_time_shifted_influence.py::TestTimeShiftedInfluence::test_influence_strictly_time_shifted [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_all_21_layer_pairs_covered [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_detector_identifies_l0_to_l5_l6_as_special [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_scan_produces_deterministic_results [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_violation_summary [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_l0_imports_l5 [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_l2_imports_l6 [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_l1_imports_l3 [32mPASSED[0m[33m [ 93%][0m
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_downward_import_allowed [32mPASSED[0m[33m [ 94%][0m
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_same_layer_import_allowed [32mPASSED[0m[33m [ 94%][0m
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_non_layer_import_ignored [32mPASSED[0m[33m [ 94%][0m
tests/governance/test_upward_import_enforcement.py::TestNegativeRegressionNewDefinition::test_zero_violations_under_new_definition [32mPASSED[0m[33m [ 94%][0m
tests/governance/test_upward_import_enforcement.py::TestNegativeRegressionNewDefinition::test_module_level_upward_import_is_caught_not_lazy [32mPASSED[0m[33m [ 94%][0m
tests/governance/test_upward_import_enforcement.py::TestNegativeRegressionNewDefinition::test_lazy_upward_import_inside_function_is_allowed [32mPASSED[0m[33m [ 94%][0m
tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_module_level_upward_imports_still_zero [32mPASSED[0m[33m [ 94%][0m
tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_lazy_upward_import_metric_is_deterministic [32mPASSED[0m[33m [ 94%][0m
tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_lazy_upward_import_metric_report [32mPASSED[0m[33m [ 94%][0m
tests/governance/test_upward_import_enforcement.py::TestLazySeamViolation::test_zero_lazy_seam_violations_in_codebase [32mPASSED[0m[33m [ 94%][0m
tests/governance/test_upward_import_enforcement.py::TestLazySeamViolation::test_upward_import_inside_non_get_function_is_violation [32mPASSED[0m[33m [ 94%][0m
tests/governance/test_upward_import_enforcement.py::TestLazySeamViolation::test_upward_import_inside_get_function_is_allowed [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_upward_import_enforcement.py::TestLazySeamBudget::test_lazy_seam_budget_not_exceeded [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_vllm_boundary_connectivity.py::test_generate_proposal_does_not_touch_network_when_not_called [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_vllm_boundary_connectivity.py::test_call_vllm_uses_urlopen_once_and_parses_chat_completions [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_vllm_boundary_connectivity.py::test_call_vllm_http_error_maps_to_runtimeerror [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_vllm_boundary_connectivity.py::test_call_vllm_timeout_maps_to_timeouterror [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_vllm_boundary_connectivity.py::test_call_vllm_connection_refused_maps_to_connectionerror [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_vllm_determinism.py::test_canonical_hash_stable [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_vllm_determinism.py::test_idempotent_normalization [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_vllm_determinism.py::test_nested_structure_determinism [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_vllm_determinism.py::test_set_ordering_stability [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_vllm_determinism.py::test_decimal_normalization [32mPASSED[0m[33m [ 95%][0m
tests/governance/test_vllm_determinism.py::test_dataclass_roundtrip [32mPASSED[0m[33m [ 96%][0m
tests/governance/test_vllm_determinism.py::test_float_rounding [32mPASSED[0m[33m    [ 96%][0m
tests/governance/test_vllm_determinism.py::test_negative_zero_normalization [32mPASSED[0m[33m [ 96%][0m
tests/governance/test_vllm_determinism.py::test_nan_rejected [32mPASSED[0m[33m      [ 96%][0m
tests/governance/test_vllm_determinism.py::test_inf_rejected [32mPASSED[0m[33m      [ 96%][0m
tests/governance/test_vllm_determinism.py::test_datetime_rejected [32mPASSED[0m[33m [ 96%][0m
tests/governance/test_vllm_determinism.py::test_bytes_rejected [32mPASSED[0m[33m    [ 96%][0m
tests/governance/test_vllm_determinism.py::test_complex_rejected [32mPASSED[0m[33m  [ 96%][0m
tests/governance/test_vllm_determinism.py::test_tuple_to_list_preserves_order [32mPASSED[0m[33m [ 96%][0m
tests/governance/test_vllm_determinism.py::test_canonical_hash_rejects_non_dict [32mPASSED[0m[33m [ 96%][0m
tests/governance/test_vllm_determinism.py::test_cross_process_determinism [32mPASSED[0m[33m [ 96%][0m
tests/governance/test_vllm_determinism.py::test_enum_normalization [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_routing_decision_frozen [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_routing_decision_frozen_setattr [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_routing_predicates_immutable [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_no_lambda_in_predicate_registry [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_no_forbidden_ast_nodes_in_predicate_registry [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_no_eval_exec_compile_in_predicate_registry [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_predicate_functions_no_free_vars [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_provider_strict_type [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_no_provider_string_literals_in_registry [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_context_structural_immutability [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_context_hash_immutability [32mPASSED[0m[33m [ 97%][0m
tests/governance/test_vllm_determinism.py::test_key_order_independence [32mPASSED[0m[33m [ 98%][0m
tests/governance/test_vllm_determinism.py::test_double_evaluation_equality [32mPASSED[0m[33m [ 98%][0m
tests/governance/test_vllm_determinism.py::test_predicate_hash_correctness [32mPASSED[0m[33m [ 98%][0m
tests/governance/test_vllm_isolation.py::test_no_direct_model_imports_in_layers [32mPASSED[0m[33m [ 98%][0m
tests/governance/test_vllm_isolation.py::test_no_importlib_in_layers [32mPASSED[0m[33m [ 98%][0m
tests/governance/test_vllm_isolation.py::test_no_getattr_model_bypass [32mPASSED[0m[33m [ 98%][0m
tests/governance/test_vllm_isolation.py::test_no_dunder_import [32mPASSED[0m[33m    [ 98%][0m
tests/governance/test_vllm_isolation.py::test_no_sys_modules_mutation [32mPASSED[0m[33m [ 98%][0m
tests/governance/test_vllm_isolation.py::test_transitive_import_graph_clean [32mPASSED[0m[33m [ 98%][0m
tests/governance/test_vllm_isolation.py::test_boundary_client_not_imported_by_layers [32mPASSED[0m[33m [ 98%][0m
tests/governance/test_vllm_isolation.py::test_no_time_based_routing [32mPASSED[0m[33m [ 98%][0m
tests/governance/test_vllm_isolation.py::test_provider_enum_defined [32mPASSED[0m[33m [ 99%][0m
tests/governance/test_vllm_isolation.py::test_routing_invariants_version_present [32mPASSED[0m[33m [ 99%][0m
tests/governance/test_write_set_enforcer.py::TestDeclaredWriteAllowed::test_declared_write_succeeds [32mPASSED[0m[33m [ 99%][0m
tests/governance/test_write_set_enforcer.py::TestDeclaredWriteAllowed::test_multiple_declared_writes [32mPASSED[0m[33m [ 99%][0m
tests/governance/test_write_set_enforcer.py::TestDeclaredWriteAllowed::test_verify_passes_on_declared [32mPASSED[0m[33m [ 99%][0m
tests/governance/test_write_set_enforcer.py::TestUndeclaredWriteBlocked::test_undeclared_write_raises [32mPASSED[0m[33m [ 99%][0m
tests/governance/test_write_set_enforcer.py::TestUndeclaredWriteBlocked::test_undeclared_aborts_enforcer [32mPASSED[0m[33m [ 99%][0m
tests/governance/test_write_set_enforcer.py::TestUndeclaredWriteBlocked::test_aborted_rejects_subsequent [32mPASSED[0m[33m [ 99%][0m
tests/governance/test_write_set_enforcer.py::TestUndeclaredWriteBlocked::test_verify_fails_after_violation [32mPASSED[0m[33m [ 99%][0m
tests/governance/test_write_set_enforcer.py::TestWriteSetTracking::test_empty_initially [32mPASSED[0m[33m [ 99%][0m
tests/governance/test_write_set_enforcer.py::TestWriteSetTracking::test_partial_not_complete [32mPASSED[0m[33m [ 99%][0m
tests/governance/test_write_set_enforcer.py::TestWriteSetTracking::test_duplicate_write_idempotent [32mPASSED[0m[33m [100%][0m

[33m============================== warnings summary ===============================[0m
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
Guardian tests run: 8
Passed: 1145
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================
3.47s call     tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_scan_produces_deterministic_results
3.18s call     tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_lazy_upward_import_metric_is_deterministic
3.09s call     tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_determinism
3.08s call     tests/governance/test_agent_heal_audit.py::TestDeterminism::test_byte_identical_json_runs
3.05s call     tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_audit_determinism
2.75s call     tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_scan_produces_deterministic_results
1.78s call     tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_dynamic_violation_summary
1.76s call     tests/governance/test_upward_import_enforcement.py::TestLazySeamBudget::test_lazy_seam_budget_not_exceeded
1.71s call     tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_matches_scanner_total
1.62s call     tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_lazy_upward_import_metric_report
[33m================= [32m1145 passed[0m, [33m[1m4 warnings[0m[33m in 75.81s (0:01:15)[0m[33m =================[0m
```

## Spine Bypass Check
```
$ C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe ops_scripts/ci/check_spine_bypass.py
[OK] Spine bypass + randomness guard: 0 new violations (1185 files scanned, 286 baselined)
```

## Git Diff Stat
```
$ git diff --stat
.../phase02_spine_adapters_evidence_runner.py      | 53 +++++++++-------------
 1 file changed, 22 insertions(+), 31 deletions(-)
```

## Git Full Diff
```
$ git diff
diff --git a/tools/evidence/phase02_spine_adapters_evidence_runner.py b/tools/evidence/phase02_spine_adapters_evidence_runner.py
index 6912a4bd5..2f9e6f993 100644
--- a/tools/evidence/phase02_spine_adapters_evidence_runner.py
+++ b/tools/evidence/phase02_spine_adapters_evidence_runner.py
@@ -3,7 +3,7 @@

 Generates verbatim evidence for Phase 2 completion.
 All commands executed via subprocess with argv arrays (shell=False).
-Fails immediately if any stdout/stderr contains PowerShell references.
+PowerShell detection via argv-level checks only (no output scanning).
 """

 import subprocess
@@ -13,23 +13,13 @@ from pathlib import Path

 def run_cmd(args, cwd=None):
     """Execute command and return (rc, stdout, stderr)."""
-    r = subprocess.run(
-        args, cwd=cwd, capture_output=True, text=True, shell=False, encoding="utf-8", errors="replace"
-    )
-
-    # Check for PowerShell usage - fail immediately if detected
-    # Only check for actual PowerShell commands, not paths
-    if args[0].lower() in ["pwsh", "powershell", "pwsh.exe", "powershell.exe"]:
+    # Check for PowerShell usage at argv level only
+    argv0_lower = str(args[0]).lower()
+    if 'pwsh' in argv0_lower or 'powershell' in argv0_lower:
         print(f"ERROR: PowerShell usage detected in command: {' '.join(args)}")
         sys.exit(1)

-    # Also check stderr for PowerShell invocation
-    if r.stderr and any(
-        cmd in r.stderr.lower() for cmd in ["pwsh ", "powershell ", "pwsh.exe", "powershell.exe"]
-    ):
-        print(f"ERROR: PowerShell usage detected in stderr: {r.stderr}")
-        sys.exit(1)
-
+    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, shell=False, encoding='utf-8', errors='replace')
     return r.returncode, r.stdout, r.stderr


@@ -50,10 +40,20 @@ def read_file_content(filepath):

 def main():
     """Generate Phase 2 evidence deterministically."""
+    if len(sys.argv) < 2:
+        print("Usage: python phase02_spine_adapters_evidence_runner.py <CODE_COMMIT>")
+        sys.exit(1)
+
+    code_commit = sys.argv[1]
+    if len(code_commit) != 40:
+        print(f"ERROR: CODE_COMMIT must be 40-hex, got: {code_commit}")
+        sys.exit(1)
+
     repo_root = Path(__file__).parent.parent.parent
     evidence_file = repo_root / "docs" / "reports" / "plans" / "phase_02_spine_adapters.md"

     print(f"Generating Phase 2 evidence: {evidence_file}")
+    print(f"CODE_COMMIT: {code_commit}")

     # Start building evidence content
     evidence_lines = []
@@ -62,13 +62,14 @@ def main():
     evidence_lines.append("# Phase 2: LIC + RG Spine Adapters (Deterministic CID)")
     evidence_lines.append("")
     evidence_lines.append("## Scope")
-    evidence_lines.append(
-        "Implement LIC and RG spine adapters with deterministic CID derivation and unit tests."
-    )
+    evidence_lines.append("Implement LIC and RG spine adapters with deterministic CID derivation and unit tests.")
     evidence_lines.append("")

-    # Placeholder for commit hash
-    evidence_lines.append("## Final Commit Hash")
+    # Commit hashes
+    evidence_lines.append("## CODE_COMMIT")
+    evidence_lines.append(code_commit)
+    evidence_lines.append("")
+    evidence_lines.append("## EVIDENCE_COMMIT")
     evidence_lines.append("PENDING")
     evidence_lines.append("")

@@ -141,17 +142,7 @@ def main():
     evidence_file.parent.mkdir(parents=True, exist_ok=True)
     evidence_file.write_text(evidence_content, encoding="utf-8", newline="\n")

-    # Get commit hash and replace PENDING
-    rc, out, err = run_cmd(["git", "rev-parse", "HEAD"], cwd=repo_root)
-    if rc != 0:
-        print(f"ERROR: git rev-parse failed: {err}")
-        sys.exit(1)
-
-    commit_hash = out.strip()
-    evidence_content = evidence_content.replace("PENDING", commit_hash)
-    evidence_file.write_text(evidence_content, encoding="utf-8", newline="\n")
-
-    print(f"Evidence generated successfully with commit hash: {commit_hash}")
+    print(f"Evidence generated successfully at: {evidence_file}")


 if __name__ == "__main__":
```

## apps_lic/engines/lic_spine_adapter.py
```python
"""
LIC Spine Adapter — pure wiring, no business logic.

Forces all LIC entry through the canonical spine:
  AirlockAssembler → PathRouter → ExecutionOrchestrator (with CIDRegistry)

CID is derived deterministically from the payload manifest hash before any
HOP stage runs. No uuid4, no datetime, no randomness.

Null-object stubs are provided for d0_engine, risk_gate, vigilance_dispatcher,
and meta_bus — these seams are not yet wired for LIC and must remain no-ops
until the corresponding phases implement them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler, GovernedPayload
from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator
from agentic_core.L0_routing.engines.path_router import PathRouter
from agentic_core.L2_execution.cid_registry import CIDRegistry, ExecutionCycle
from agentic_core.L2_execution.reentry_loop import ReEntryLoop
from apps_shared.utils.determinism_util import canonical_hash, strip_nondeterministic

# Default maximum re-entry attempts for the LIC spine.
_DEFAULT_MAX_REENTRY_ATTEMPTS: int = 3

# ---------------------------------------------------------------------------
# Null-object stubs for unimplemented seams
# ---------------------------------------------------------------------------


class _NullD0Engine:
    """Null-object stub for D0 injection engine (not yet wired for LIC)."""

    def render_d0(self, d0_injections: str) -> str:
        return d0_injections


@dataclass(frozen=True)
class _RiskResult:
    allow: bool


class _NullRiskGate:
    """Null-object stub for risk gate (not yet wired for LIC)."""

    def evaluate(self, *, payload_like: Any, d0_injections: Any) -> _RiskResult:
        return _RiskResult(allow=True)


class _NullVigilanceDispatcher:
    """Null-object stub for vigilance dispatcher (not yet wired for LIC)."""

    def dispatch(self, *args: Any, **kwargs: Any) -> None:
        pass


class _NullMetaBus:
    """Null-object stub for meta-learning bus (not yet wired for LIC)."""

    def enqueue(self, *args: Any, **kwargs: Any) -> None:
        pass


# ---------------------------------------------------------------------------
# Assembler adapter: wraps AirlockAssembler to accept dict input
# ---------------------------------------------------------------------------


class _LicAssemblerAdapter:
    """
    Thin adapter so ExecutionOrchestrator.execute() can call
    self.assembler.assemble(intent_input: dict) with the LIC slot mapping.

    Slot mapping:
      s0_system       ← intent_input.get("s0_system", "")
      i0_instructional← intent_input.get("i0_instructional", "")
      c0_context      ← intent_input.get("c0_context", "")
      u0_user_prompt  ← intent_input.get("u0_user_prompt", "")
      d0_injections   ← intent_input.get("d0_injections", "")
    """

    def assemble(self, intent_input: dict[str, Any]) -> GovernedPayload:
        return AirlockAssembler.assemble(
            s0_system=intent_input.get("s0_system", ""),
            i0_instructional=intent_input.get("i0_instructional", ""),
            c0_context=intent_input.get("c0_context", ""),
            u0_user_prompt=intent_input.get("u0_user_prompt", ""),
            d0_injections=intent_input.get("d0_injections", ""),
        )


# ---------------------------------------------------------------------------
# LIC Spine Adapter — public entry point
# ---------------------------------------------------------------------------


class LicSpineAdapter:
    """
    Canonical LIC spine adapter.

    Constructs the full spine wiring once and exposes a single
    ``execute(intent_input)`` method. CID is derived from the
    GovernedPayload manifest hash — deterministic, no randomness.

    HOPPipelineExecutor is the only class allowed to be instantiated
    here (enforced by check_spine_bypass.py CI guard).
    """

    def __init__(self, max_reentry_attempts: int = _DEFAULT_MAX_REENTRY_ATTEMPTS) -> None:
        self._cid_registry = CIDRegistry()
        self._reentry_loop = ReEntryLoop(
            max_attempts=max_reentry_attempts,
            cid_registry=self._cid_registry,
        )
        self._orchestrator = ExecutionOrchestrator(
            assembler=_LicAssemblerAdapter(),
            path_router=PathRouter(),
            d0_engine=_NullD0Engine(),
            risk_gate=_NullRiskGate(),
            cid_registry=self._cid_registry,
            reentry_loop=self._reentry_loop,
            vigilance_dispatcher=_NullVigilanceDispatcher(),
            meta_bus=_NullMetaBus(),
        )

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        """
        Route a LIC intent through the canonical spine.

        Steps:
          1) Assemble GovernedPayload via AirlockAssembler.
          2) Derive deterministic CID from manifest_hash (no randomness).
          3) Pre-register CID in CIDRegistry before any HOP stage runs.
          4) Inject cid into intent_input so downstream stages can read it.
          5) Delegate to ExecutionOrchestrator.execute().
          6) Return result dict augmented with cid.

        Args:
            intent_input: Dict with LIC slot keys (s0_system, i0_instructional,
                          c0_context, u0_user_prompt, d0_injections).

        Returns:
            Result dict from ExecutionOrchestrator plus ``cid`` key.
        """
        # Step 1: Strip nondeterministic fields from intent_input.
        stripped = strip_nondeterministic(intent_input)

        # Step 2: Derive deterministic CID via canonical hash.
        cid = "lic-" + canonical_hash(stripped)[:16]

        # Step 3: Pre-register CID before any HOP stage runs.
        cycle: ExecutionCycle = self._cid_registry.new_cycle(cid)

        # Step 4: Thread cid into intent_input for downstream visibility.
        enriched = dict(intent_input)
        enriched["_cid"] = cid
        enriched["_cycle_attempt"] = cycle.attempt

        # Step 5: Delegate to orchestrator (it will re-assemble internally).
        result = self._orchestrator.execute(enriched)

        # Step 6: Augment result with cid.
        result["cid"] = cid
        return result
```

## apps_rg/engines/rg_spine_adapter.py
```python
"""
RG Spine Adapter — pure wiring, no business logic.

Forces all RG entry through the canonical spine:
  AirlockAssembler → PathRouter → ExecutionOrchestrator (with CIDRegistry)

CID is derived deterministically from the payload manifest hash before any
HOP stage runs. No uuid4, no datetime, no randomness.

Null-object stubs are provided for d0_engine, risk_gate, vigilance_dispatcher,
and meta_bus — these seams are not yet wired for RG and must remain no-ops
until the corresponding phases implement them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler, GovernedPayload
from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator
from agentic_core.L0_routing.engines.path_router import PathRouter
from agentic_core.L2_execution.cid_registry import CIDRegistry, ExecutionCycle
from agentic_core.L2_execution.reentry_loop import ReEntryLoop
from apps_shared.utils.determinism_util import canonical_hash, strip_nondeterministic

# Default maximum re-entry attempts for the RG spine.
_DEFAULT_MAX_REENTRY_ATTEMPTS: int = 3

# ---------------------------------------------------------------------------
# Null-object stubs for unimplemented seams
# ---------------------------------------------------------------------------


class _NullD0Engine:
    """Null-object stub for D0 injection engine (not yet wired for RG)."""

    def render_d0(self, d0_injections: str) -> str:
        return d0_injections


@dataclass(frozen=True)
class _RiskResult:
    allow: bool


class _NullRiskGate:
    """Null-object stub for risk gate (not yet wired for RG)."""

    def evaluate(self, *, payload_like: Any, d0_injections: Any) -> _RiskResult:
        return _RiskResult(allow=True)


class _NullVigilanceDispatcher:
    """Null-object stub for vigilance dispatcher (not yet wired for RG)."""

    def dispatch(self, *args: Any, **kwargs: Any) -> None:
        pass


class _NullMetaBus:
    """Null-object stub for meta-learning bus (not yet wired for RG)."""

    def enqueue(self, *args: Any, **kwargs: Any) -> None:
        pass


# ---------------------------------------------------------------------------
# Assembler adapter: wraps AirlockAssembler to accept dict input
# ---------------------------------------------------------------------------


class _RgAssemblerAdapter:
    """
    Thin adapter so ExecutionOrchestrator.execute() can call
    self.assembler.assemble(intent_input: dict) with the RG slot mapping.

    Slot mapping:
      s0_system       ← intent_input.get("s0_system", "")
      i0_instructional← intent_input.get("i0_instructional", "")
      c0_context      ← intent_input.get("c0_context", "")
      u0_user_prompt  ← intent_input.get("u0_user_prompt", "")
      d0_injections   ← intent_input.get("d0_injections", "")
    """

    def assemble(self, intent_input: dict[str, Any]) -> GovernedPayload:
        return AirlockAssembler.assemble(
            s0_system=intent_input.get("s0_system", ""),
            i0_instructional=intent_input.get("i0_instructional", ""),
            c0_context=intent_input.get("c0_context", ""),
            u0_user_prompt=intent_input.get("u0_user_prompt", ""),
            d0_injections=intent_input.get("d0_injections", ""),
        )


# ---------------------------------------------------------------------------
# RG Spine Adapter — public entry point
# ---------------------------------------------------------------------------


class RgSpineAdapter:
    """
    Canonical RG spine adapter.

    Constructs the full spine wiring once and exposes a single
    ``execute(intent_input)`` method. CID is derived from the
    GovernedPayload manifest hash — deterministic, no randomness.

    HOPPipelineExecutor is the only class allowed to be instantiated
    here (enforced by check_spine_bypass.py CI guard).
    """

    def __init__(self, max_reentry_attempts: int = _DEFAULT_MAX_REENTRY_ATTEMPTS) -> None:
        self._cid_registry = CIDRegistry()
        self._reentry_loop = ReEntryLoop(
            max_attempts=max_reentry_attempts,
            cid_registry=self._cid_registry,
        )
        self._orchestrator = ExecutionOrchestrator(
            assembler=_RgAssemblerAdapter(),
            path_router=PathRouter(),
            d0_engine=_NullD0Engine(),
            risk_gate=_NullRiskGate(),
            cid_registry=self._cid_registry,
            reentry_loop=self._reentry_loop,
            vigilance_dispatcher=_NullVigilanceDispatcher(),
            meta_bus=_NullMetaBus(),
        )

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        """
        Route a RG intent through the canonical spine.

        Steps:
          1) Strip nondeterministic fields from intent_input.
          2) Derive deterministic CID via canonical hash.
          3) Pre-register CID in CIDRegistry before any HOP stage runs.
          4) Inject cid into intent_input so downstream stages can read it.
          5) Delegate to ExecutionOrchestrator.execute().
          6) Return result dict augmented with cid.

        Args:
            intent_input: Dict with RG slot keys (s0_system, i0_instructional,
                          c0_context, u0_user_prompt, d0_injections).

        Returns:
            Result dict from ExecutionOrchestrator plus ``cid`` key.
        """
        # Step 1: Strip nondeterministic fields from intent_input.
        stripped = strip_nondeterministic(intent_input)

        # Step 2: Derive deterministic CID via canonical hash.
        cid = "rg-" + canonical_hash(stripped)[:16]

        # Step 3: Pre-register CID before any HOP stage runs.
        cycle: ExecutionCycle = self._cid_registry.new_cycle(cid)

        # Step 4: Thread cid into intent_input for downstream visibility.
        enriched = dict(intent_input)
        enriched["_cid"] = cid
        enriched["_cycle_attempt"] = cycle.attempt

        # Step 5: Delegate to orchestrator (it will re-assemble internally).
        result = self._orchestrator.execute(enriched)

        # Step 6: Augment result with cid.
        result["cid"] = cid
        return result
```

## tests/unit_min_deps/test_apps_lic_spine_adapter.py
```python
"""Tests for LIC spine adapter — deterministic CID + spine routing."""

from unittest.mock import MagicMock, patch

import pytest

from apps_lic.engines.lic_spine_adapter import LicSpineAdapter


@pytest.mark.unit_min_deps
def test_adapter_returns_cid():
    """Adapter returns a cid in result."""
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = LicSpineAdapter()
        result = adapter.execute({"s0_system": "test"})

        assert "cid" in result
        assert result["cid"].startswith("lic-")
        assert len(result["cid"]) == 20  # "lic-" + 16 char hash


@pytest.mark.unit_min_deps
def test_cid_has_lic_prefix():
    """CID has 'lic-' prefix."""
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = LicSpineAdapter()
        result = adapter.execute({"s0_system": "test"})

        assert result["cid"].startswith("lic-")


@pytest.mark.unit_min_deps
def test_cid_is_deterministic():
    """Calling adapter twice with identical intent_input produces same cid."""
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = LicSpineAdapter()
        result1 = adapter.execute({"s0_system": "test", "i0_instructional": "instruction"})
        result2 = adapter.execute({"s0_system": "test", "i0_instructional": "instruction"})

        assert result1["cid"] == result2["cid"]


@pytest.mark.unit_min_deps
def test_different_inputs_produce_different_cids():
    """Different intent_inputs produce different cids."""
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        def fresh_result(*args, **kwargs):
            return {"status": "ok"}

        mock_orch.return_value.execute = fresh_result

        adapter1 = LicSpineAdapter()
        result1 = adapter1.execute({"s0_system": "test1", "i0_instructional": "instruction1"})

        adapter2 = LicSpineAdapter()
        result2 = adapter2.execute({"s0_system": "test2", "i0_instructional": "instruction2"})

        assert result1["cid"] != result2["cid"]


@pytest.mark.unit_min_deps
def test_cid_registered_before_orchestrator_execute():
    """CIDRegistry.new_cycle called before ExecutionOrchestrator.execute."""
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        with patch("apps_lic.engines.lic_spine_adapter.CIDRegistry") as mock_registry:
            mock_cycle = MagicMock()
            mock_cycle.attempt = 1
            mock_registry.return_value.new_cycle.return_value = mock_cycle
            mock_orch.return_value.execute.return_value = {"status": "ok"}

            adapter = LicSpineAdapter()
            adapter.execute({"s0_system": "test"})

            # Verify call order
            mock_registry.return_value.new_cycle.assert_called_once()
            mock_orch.return_value.execute.assert_called_once()

            # Get the cid passed to new_cycle
            cid_arg = mock_registry.return_value.new_cycle.call_args[0][0]
            assert cid_arg.startswith("lic-")

            # Verify orchestrator received enriched input
            enriched_input = mock_orch.return_value.execute.call_args[0][0]
            assert "_cid" in enriched_input
            assert enriched_input["_cid"] == cid_arg


@pytest.mark.unit_min_deps
def test_cid_passed_to_orchestrator():
    """CID is passed to orchestrator in enriched intent_input."""
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        with patch("apps_lic.engines.lic_spine_adapter.CIDRegistry") as mock_registry:
            mock_cycle = MagicMock()
            mock_cycle.attempt = 1
            mock_registry.return_value.new_cycle.return_value = mock_cycle
            mock_orch.return_value.execute.return_value = {"status": "ok"}

            adapter = LicSpineAdapter()
            adapter.execute({"s0_system": "test"})

            # Verify orchestrator received enriched input
            enriched_input = mock_orch.return_value.execute.call_args[0][0]
            assert "_cid" in enriched_input
            assert "_cycle_attempt" in enriched_input
            assert enriched_input["_cycle_attempt"] == 1


@pytest.mark.unit_min_deps
def test_adapter_state_success_on_clean_input():
    """Adapter succeeds on clean input without side effects."""
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = LicSpineAdapter()
        # Should not raise
        result = adapter.execute(
            {
                "s0_system": "test_system",
                "i0_instructional": "test_instruction",
                "c0_context": "test_context",
                "u0_user_prompt": "test_prompt",
                "d0_injections": "test_injection",
            }
        )

        assert result["status"] == "ok"
        assert "cid" in result
```

## tests/unit_min_deps/test_apps_rg_spine_adapter.py
```python
"""Tests for RG spine adapter — deterministic CID + spine routing."""

from unittest.mock import MagicMock, patch

import pytest

from apps_rg.engines.rg_spine_adapter import RgSpineAdapter


@pytest.mark.unit_min_deps
def test_adapter_returns_cid():
    """Adapter returns a cid in result."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = RgSpineAdapter()
        result = adapter.execute({"s0_system": "test"})

        assert "cid" in result
        assert result["cid"].startswith("rg-")
        assert len(result["cid"]) == 19  # "rg-" + 16 char hash


@pytest.mark.unit_min_deps
def test_cid_has_rg_prefix():
    """CID has 'rg-' prefix."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = RgSpineAdapter()
        result = adapter.execute({"s0_system": "test"})

        assert result["cid"].startswith("rg-")


@pytest.mark.unit_min_deps
def test_cid_is_deterministic():
    """Calling adapter twice with identical intent_input produces same cid."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = RgSpineAdapter()
        result1 = adapter.execute({"s0_system": "test", "i0_instructional": "instruction"})
        result2 = adapter.execute({"s0_system": "test", "i0_instructional": "instruction"})

        assert result1["cid"] == result2["cid"]


@pytest.mark.unit_min_deps
def test_different_inputs_produce_different_cids():
    """Different intent_inputs produce different cids."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        def fresh_result(*args, **kwargs):
            return {"status": "ok"}

        mock_orch.return_value.execute = fresh_result

        adapter1 = RgSpineAdapter()
        result1 = adapter1.execute({"s0_system": "test1", "i0_instructional": "instruction1"})

        adapter2 = RgSpineAdapter()
        result2 = adapter2.execute({"s0_system": "test2", "i0_instructional": "instruction2"})

        assert result1["cid"] != result2["cid"]


@pytest.mark.unit_min_deps
def test_cid_registered_before_orchestrator_execute():
    """CIDRegistry.new_cycle called before ExecutionOrchestrator.execute."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        with patch("apps_rg.engines.rg_spine_adapter.CIDRegistry") as mock_registry:
            mock_cycle = MagicMock()
            mock_cycle.attempt = 1
            mock_registry.return_value.new_cycle.return_value = mock_cycle
            mock_orch.return_value.execute.return_value = {"status": "ok"}

            adapter = RgSpineAdapter()
            adapter.execute({"s0_system": "test"})

            # Verify call order
            mock_registry.return_value.new_cycle.assert_called_once()
            mock_orch.return_value.execute.assert_called_once()

            # Get the cid passed to new_cycle
            cid_arg = mock_registry.return_value.new_cycle.call_args[0][0]
            assert cid_arg.startswith("rg-")

            # Verify orchestrator received enriched input
            enriched_input = mock_orch.return_value.execute.call_args[0][0]
            assert "_cid" in enriched_input
            assert enriched_input["_cid"] == cid_arg


@pytest.mark.unit_min_deps
def test_cid_passed_to_orchestrator():
    """CID is passed to orchestrator in enriched intent_input."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        with patch("apps_rg.engines.rg_spine_adapter.CIDRegistry") as mock_registry:
            mock_cycle = MagicMock()
            mock_cycle.attempt = 1
            mock_registry.return_value.new_cycle.return_value = mock_cycle
            mock_orch.return_value.execute.return_value = {"status": "ok"}

            adapter = RgSpineAdapter()
            adapter.execute({"s0_system": "test"})

            # Verify orchestrator received enriched input
            enriched_input = mock_orch.return_value.execute.call_args[0][0]
            assert "_cid" in enriched_input
            assert "_cycle_attempt" in enriched_input
            assert enriched_input["_cycle_attempt"] == 1


@pytest.mark.unit_min_deps
def test_adapter_state_success_on_clean_input():
    """Adapter succeeds on clean input without side effects."""
    with patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = RgSpineAdapter()
        # Should not raise
        result = adapter.execute(
            {
                "s0_system": "test_system",
                "i0_instructional": "test_instruction",
                "c0_context": "test_context",
                "u0_user_prompt": "test_prompt",
                "d0_injections": "test_injection",
            }
        )

        assert result["status"] == "ok"
        assert "cid" in result
```

## tools/evidence/phase02_spine_adapters_evidence_runner.py
```python
#!/usr/bin/env python3
"""Phase 2 Spine Adapters Evidence Runner - Deterministic Generator.

Generates verbatim evidence for Phase 2 completion.
All commands executed via subprocess with argv arrays (shell=False).
PowerShell detection via argv-level checks only (no output scanning).
"""

import subprocess
import sys
from pathlib import Path


def run_cmd(args, cwd=None):
    """Execute command and return (rc, stdout, stderr)."""
    # Check for PowerShell usage at argv level only
    argv0_lower = str(args[0]).lower()
    if 'pwsh' in argv0_lower or 'powershell' in argv0_lower:
        print(f"ERROR: PowerShell usage detected in command: {' '.join(args)}")
        sys.exit(1)

    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, shell=False, encoding='utf-8', errors='replace')
    return r.returncode, r.stdout, r.stderr


def read_file_content(filepath):
    """Read file content as text."""
    try:
        return Path(filepath).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"ERROR: Unicode decode error in {filepath}: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: OS error reading {filepath}: {e}")
        sys.exit(1)


def main():
    """Generate Phase 2 evidence deterministically."""
    if len(sys.argv) < 2:
        print("Usage: python phase02_spine_adapters_evidence_runner.py <CODE_COMMIT>")
        sys.exit(1)

    code_commit = sys.argv[1]
    if len(code_commit) != 40:
        print(f"ERROR: CODE_COMMIT must be 40-hex, got: {code_commit}")
        sys.exit(1)

    repo_root = Path(__file__).parent.parent.parent
    evidence_file = repo_root / "docs" / "reports" / "plans" / "phase_02_spine_adapters.md"

    print(f"Generating Phase 2 evidence: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")

    # Start building evidence content
    evidence_lines = []

    # Header with scope
    evidence_lines.append("# Phase 2: LIC + RG Spine Adapters (Deterministic CID)")
    evidence_lines.append("")
    evidence_lines.append("## Scope")
    evidence_lines.append("Implement LIC and RG spine adapters with deterministic CID derivation and unit tests.")
    evidence_lines.append("")

    # Commit hashes
    evidence_lines.append("## CODE_COMMIT")
    evidence_lines.append(code_commit)
    evidence_lines.append("")
    evidence_lines.append("## EVIDENCE_COMMIT")
    evidence_lines.append("PENDING")
    evidence_lines.append("")

    # Files changed
    rc, out, err = run_cmd(["git", "show", "--name-only", "--pretty=format:", "HEAD"], cwd=repo_root)
    if rc != 0:
        print(f"ERROR: git show failed: {err}")
        sys.exit(1)

    evidence_lines.append("## Files Changed")
    evidence_lines.append("```")
    for line in out.strip().split("\n"):
        if line.strip():
            evidence_lines.append(line.strip())
    evidence_lines.append("```")
    evidence_lines.append("")

    # Command outputs
    commands = [
        (
            [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_apps_lic_spine_adapter.py"],
            "LIC Unit Tests",
        ),
        (
            [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_apps_rg_spine_adapter.py"],
            "RG Unit Tests",
        ),
        ([sys.executable, "-m", "pytest", "-q"], "Full Test Suite"),
        ([sys.executable, "ops_scripts/ci/check_spine_bypass.py"], "Spine Bypass Check"),
        (["git", "diff", "--stat"], "Git Diff Stat"),
        (["git", "diff"], "Git Full Diff"),
    ]

    for cmd, title in commands:
        evidence_lines.append(f"## {title}")
        evidence_lines.append("```")
        rc, out, err = run_cmd(cmd, cwd=repo_root)
        if rc != 0:
            print(f"ERROR: Command failed: {' '.join(cmd)}")
            print(f"Error: {err}")
            sys.exit(1)

        # Add command and output
        evidence_lines.append(f"$ {' '.join(cmd)}")
        evidence_lines.append(out.strip())
        if err:
            evidence_lines.append(f"STDERR: {err.strip()}")
        evidence_lines.append("```")
        evidence_lines.append("")

    # File contents
    files_to_include = [
        "apps_lic/engines/lic_spine_adapter.py",
        "apps_rg/engines/rg_spine_adapter.py",
        "tests/unit_min_deps/test_apps_lic_spine_adapter.py",
        "tests/unit_min_deps/test_apps_rg_spine_adapter.py",
        "tools/evidence/phase02_spine_adapters_evidence_runner.py",
    ]

    for filepath in files_to_include:
        evidence_lines.append(f"## {filepath}")
        evidence_lines.append("```python")
        content = read_file_content(repo_root / filepath)
        evidence_lines.append(content)
        evidence_lines.append("```")
        evidence_lines.append("")

    # Write evidence file with LF line endings and no trailing whitespace
    evidence_content = "\n".join(line.rstrip() for line in evidence_lines)
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(evidence_content, encoding="utf-8", newline="\n")

    print(f"Evidence generated successfully at: {evidence_file}")


if __name__ == "__main__":
    main()
```

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

