# Phases 3-4: Spine Adapter Production Closure (Consolidated)

## Scope
Phase 3: Single-evidence-per-response contract implementation
Phase 4: Production-grade spine adapter hardening (CID invariants, import stability, governance)

## CODE_COMMIT
03a61d116dda49020c42eb7602181b1495c6737e

## EVIDENCE_COMMIT
6b1d8a29bf34e8fd562ba15bfa2d102023fa3968

## FILES_CHANGED (in CODE_COMMIT)
```
docs/reports/plans/phase_03_04_consolidated.md
```

## INSPECTED_FILES (context snapshots, not necessarily changed)
```
tools/evidence/phase03_04_consolidated_evidence_runner.py
apps_lic/engines/__init__.py
apps_rg/engines/__init__.py
tests/unit_min_deps/test_apps_lic_spine_adapter.py
tests/unit_min_deps/test_apps_rg_spine_adapter.py
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
2026-02-22 14:33:00 [[32m    INFO[0m] agentic_core.L5_safety.reasoning.InspectorExecutor: [InspectorExecutor] Inspector
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
2026-02-22 14:33:20 [[1m[31m   ERROR[0m] agentic_core.L2_execution.audit.hash_chain_audit_log: [audit] hash mismatch at entry 1
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
2026-02-22 14:33:20 [[33m WARNING[0m] agentic_core.utils.decorators_util: [standard_heal] MockAgent: Non-canonical key '_policy_from_kwargs' detected. Consider using canonical keys for better schema compliance.
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
3.39s call     tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_scan_produces_deterministic_results
3.14s call     tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_lazy_upward_import_metric_is_deterministic
3.11s call     tests/governance/test_agent_heal_audit.py::TestDeterminism::test_byte_identical_json_runs
3.04s call     tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_determinism
3.04s call     tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_audit_determinism
2.74s call     tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_scan_produces_deterministic_results
1.75s call     tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_dynamic_violation_summary
1.59s call     tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_matches_scanner_total
1.59s call     tests/governance/test_vllm_isolation.py::test_transitive_import_graph_clean
1.57s call     tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_enforcement_no_unregistered_seams
[33m================= [32m1145 passed[0m, [33m[1m4 warnings[0m[33m in 72.92s (0:01:12)[0m[33m =================[0m
```

## Spine Bypass Check
```
$ C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe ops_scripts/ci/check_spine_bypass.py
[OK] Spine bypass + randomness guard: 0 new violations (1185 files scanned, 286 baselined)
```

## Git Diff Stat
```
$ git diff --stat
...wn 1 - L1 [U0] Transformation & RAG Pipeline.md |  12 +-
 ...ll-Down 2 - L0 Routing Gate & Elevator Shaft.md |  39 +++--
 ...3 - L2 Unified Execution Core & Healing Loop.md | 112 +++++++-------
 docs/technical/agentic_process_mapping.md          | 165 ++++++++++++---------
 .../phase03_04_consolidated_evidence_runner.py     |  48 +++---
 5 files changed, 198 insertions(+), 178 deletions(-)
```

## Git Full Diff
```
$ git diff
diff --git a/docs/technical/Drill-Down 1 - L1 [U0] Transformation & RAG Pipeline.md b/docs/technical/Drill-Down 1 - L1 [U0] Transformation & RAG Pipeline.md
index 310c7b471..305f50856 100644
--- a/docs/technical/Drill-Down 1 - L1 [U0] Transformation & RAG Pipeline.md
+++ b/docs/technical/Drill-Down 1 - L1 [U0] Transformation & RAG Pipeline.md
@@ -113,7 +113,8 @@
 |                  [ LOOP: FALLBACK TO 2.0 EXPANSION ]     +-----------------------------------------------------------------------------------------+     |
 |                  (Triggers broader metadata filters)     | 4.0 DETERMINISTIC ASSEMBLY, FENCING & CRYPTOGRAPHIC PACKAGING                           |     |
 |                                                          |-----------------------------------------------------------------------------------------|     |
-|                                                          | [4.1] Budget Math: Total(128k) = L4_Rules(10k) + C0(90k) + U0(8k) + Reserved_Out(20k)   |     |
+|                                                          | [4.1] Token Budgeting: Calculates dynamic limits and explicitly emits TokenControl      |     |
+|                                                          |       Artifact (prompt_hash, token_ceilings) validated against L4 thresholds.           |     |
 |                                                          | [4.2] Delimiter Fencing: Wraps truth in `<grounding_context> [C0] </grounding_context>` |     |
 |                                                          | [4.3] XML Role Hydration: Maps strictly to System, User, and Assistant message arrays   |     |
 |                                                          | [4.4] Payload Freeze: Computes SHA-256 hash of final string to prevent L0 tampering     |     |
@@ -121,9 +122,10 @@
 |                                                                                          ||                                                              |
 +==========================================================================================||==============================================================+
                                                                                            ||
-                                                                                           || (Emits: SHA-256 Locked [U0] Payload -> { intent_vector,
-                                                                                           ||          tool_candidates, est_complexity, raw_reasoning,
-                                                                                           ||          grounding_context [C0], payload_hash })
+                                                                                           || (Emits: SHA-256 Locked [U0] Payload & TokenControl Artifact
+                                                                                           ||          -> { intent_vector, tool_candidates, est_complexity,
+                                                                                           ||             raw_reasoning, grounding_context [C0],
+                                                                                           ||             payload_hash, TokenControl Artifact })
                                                                                            v
                                                      +---------------------------------------------------------------------+
                                                      | TO: L0 – ROUTING (THE FIRST AUTHORITY GATE)                         |
@@ -159,4 +161,4 @@
                           +---------------------------+
                           | PATH D: HUMAN REVIEW      |
                           | (Stall + Escalation Flag) |
-                          +---------------------------+
+                          +---------------------------+
\ No newline at end of file
diff --git a/docs/technical/Drill-Down 2 - L0 Routing Gate & Elevator Shaft.md b/docs/technical/Drill-Down 2 - L0 Routing Gate & Elevator Shaft.md
index 9cb78831e..df8ddf0b5 100644
--- a/docs/technical/Drill-Down 2 - L0 Routing Gate & Elevator Shaft.md
+++ b/docs/technical/Drill-Down 2 - L0 Routing Gate & Elevator Shaft.md
@@ -5,11 +5,11 @@

                                                     [ FROM: L1 – THINKING LAYER ]
                                                     +---------------------------------------------------------------------------------+
-                                                    | PAYLOAD: { "hash": "a94a8fe5ccb19", "auth_tier": "L1_VERIFIED",                 |
+                                                    | PAYLOAD: { "payload_hash": "a94a8fe5ccb19", "auth_tier": "L1_VERIFIED",         |
                                                     |            "intent_vector": <768-dim float32>,                                  |
                                                     |            "tool_candidates": ["resume_writer", "jd_parser"],                  |
-                                                    |            "est_complexity": 0.74,                                              |
-                                                    |            "raw_reasoning": "<CoT trace>",                                     |
+                                                    |            "TokenControl": {"prompt_hash": "...", "ceilings": 4096},            |
+                                                    |            "est_complexity": 0.74, "raw_reasoning": "<CoT trace>",              |
                                                     |            "body": Array[ <System: S0>, <Context: C0>, <User: U0> ] }           |
                                                     +---------------------------------------------------------------------------------+
                                                                       ||
@@ -25,7 +25,7 @@
 |  | L1 Proposal Signal:                       |   | anomaly_score   — cross-layer telemetry output    |                                                  |
 |  |  - intent_vector                          |   | drift_metric    — embedding drift from baseline   |                                                  |
 |  |  - tool_candidates                        |   | injection_flag  — TRUE if jailbreak detected      |                                                  |
-|  |  - est_complexity                         |   | context_usage   — % of context window consumed    |                                                  |
+|  |  - TokenControl Artifact                  |   | context_usage   — % of context window consumed    |                                                  |
 |  |  - raw_reasoning                          |   +---------------------------------------------------+                                                  |
 |  +------------------------------------------+                      ||                                                                                   |
 |                    ||                                               ||                                                                                   |
@@ -34,7 +34,7 @@
 |                               +-----------------------------------------------------------------------------------------+                                |
 |                               | 1.0 CONTEXTUAL INGESTION & ENRICHMENT                                                   |                                |
 |                               |-----------------------------------------------------------------------------------------|                                |
-|   [ L4 ROUTING STATE ]        | [1.1] Cryptographic Handshake: Re-hashes payload. IF hash(body) != hash_header -> DROP  |  ( READ: Global Config,   )    |
+|   [ L4 ROUTING STATE ]        | [1.1] Cryptographic Handshake: Re-hashes payload. IF hash(body) != payload_hash -> DROP |  ( READ: Global Config,   )    |
 |   +--------------------+      | [1.2] Trace_ID Binding: Assigns Immutable Trace_ID + attaches current Policy Hash       | <==( Active Capability Inv,)    |
 |   | - RBAC Matrix      | <==> | [1.3] Signal Correlation: Correlates L1.intent_vector with L6.anomaly_score             |  ( Routing Weights/Rules, )    |
 |   | - Fallback Rules   |      | [1.4] State Lock: Grabs ephemeral Redis lock for Session ID to prevent race conditions  |  ( System Budgets         )    |
@@ -79,7 +79,7 @@
 |                               | [4.1] Tool Inventory Check: Are L1.tool_candidates actually online in L2?               |                                |
 |                               |       - Queries live capability registry (L4 [TOOL] CAPABILITY INVENTORY)              |                                |
 |                               |       - Any missing tool -> immediate reject back to L1 for replanning                 |                                |
-|                               | [4.2] Budget Forecasting: L1.est_complexity * unit_cost vs. remaining system budget     |                                |
+|                               | [4.2] Budget Forecasting: Validates L1 `TokenControl` ceilings vs. L4 system limits     |                                |
 |                               |       - IF cost > budget ceiling -> reject to L1 (triggers CoT -> ToT escalation)      |                                |
 |                               |       - IF budget OK -> proceed to Assembly Stage                                      |                                |
 |                               | [4.3] Reject Path: Emits rejection reason + signal back to L1 Cognitive Router          |  ( WRITE: Routing Decision,  ) |
@@ -101,8 +101,7 @@
 |                               | [5.6] SPLIT Into Atomic Tasks: Breaks compound intent into minimal-scope sub-tasks      |                                |
 |                               |       - Limits blast radius of any single sub-task failure                              |                                |
 |                               |       - Each sub-task gets independent RBAC token                                       |                                |
-|                               | [5.7] Token Cap Verification: Final tiktoken pass to ensure 0% chance of OOM error      |                                |
-|                               |       Budget: Total(128k) = S0+D0+I0(10k) + C0(90k) + U0(8k) + Reserved_Out(20k)       |                                |
+|                               | [5.7] Token Cap Verification: Final tiktoken pass mapping to L1 `TokenControl` limits   |                                |
 |                               +-----------------------------------------------------------------------------------------+                                |
 |                                                         ||                                                                                               |
 |                                                         v                                                                                                |
@@ -115,14 +114,19 @@
 |                               | [6.2] RBAC Binding: Attaches specific L4 authorization tokens to each DAG node          |                                |
 |                               |       - Token scope = minimum required permissions only (least-privilege)               |                                |
 |                               | [6.3] Path Evaluation: Emits locked DAG payload to explicit Execution Path (A, B, C, D) |                                |
+|                               | [6.4] Custody Handoff Rule: DAG logical workflow state and DAG-branch retries are       |                                |
+|                               |       explicitly assigned to L3 Orchestrator; physical tool execution and compute       |                                |
+|                               |       healing are strictly assigned to L2 Sandbox.                                      |                                |
 |                               +-----------------------------------------------------------------------------------------+                                |
 |                                                         ||                                                                                               |
 |                                                         v                                                                                                |
 |                               +-----------------------------------------------------------------------------------------+                                |
-|                               | 7.0 POLICY-AWARE DISPATCH                                                               |                                |
+|                               | 7.0 POLICY-AWARE DISPATCH & CONTRACT SEALING                                            |                                |
 |                               |-----------------------------------------------------------------------------------------|                                |
 |                               | [7.1] Route Mode Stamp: Stamps final "Route Mode" (A/B/C/D) on the artifact             |                                |
-|                               | [7.2] Decision Object Seal: Encrypts and seals the final Decision Object                |                                |
+|                               | [7.2] Cryptographic Signing: Generates the strict InstructionPacket contract [trace_id, |                                |
+|                               |       policy_hash, route_mode, token_budget, allowed_tools[], signature(HMAC-SHA256)]   |                                |
+|                               |       using the L0 Service Key to seal the payload against downstream tampering.        |                                |
 |                               | [7.3] Queue Emission: Emits payload to specific downstream queue for target path        |                                |
 |                               +-----------------------------------------------------------------------------------------+                                |
 |                                                         ||                                                                                               |
@@ -137,7 +141,7 @@
 |                                                                                                                                                          |
 +=========================================================||===========================================================================================||==+
                                                           ||
-                                                          || (Emits: RBAC-Locked DAG Payload => Path A, B, C, or D)
+                                                          || (Emits: Cryptographically Signed InstructionPacket => Path A, B, C, or D)
                                                           v
            +-----------------------------+-----------------------------+-----------------------------+-----------------------------+
            | IF (Tier 1 & Read-Only)     | IF (Tier 2-3 & Rule Bound)  | IF (Tier 1-2 & Trusted Auth)| IF (Tier 4-5 OR Conf < 0.88)|
@@ -147,10 +151,13 @@
   | READ-ONLY       |           | POLICY CHECK    |           | EXECUTE DIRECTLY|           | HUMAN REVIEW    |
   | RESPONSE        |           | FIRST (L3+L5)   |           | (L3 + L2)       |           | (Stall + Flag)  |
   +=================+           +=================+           +=================+           +=================+
-  | - No mutation   |           | - L3 Orchestrate|           | - L3 Orchestrate|           | - Prepares      |
-  | - Logged outcome|           | - L5 Validate   |           | - L2 Execute    |           |   review artifact|
-  | - ML consumes   |           | - L2 Execute    |           | - ML: Efficiency|           | - Manual        |
-  |   outcome       |           |   if approved   |           |   Tuner active  |           |   approve/reject|
+  | - No mutation   |           | - L3 Orchestrate|           | - L3 Orchestrate|           | - Requests      |
+  | - Logged outcome|           | - L5 Validate   |           | - L2 Execute    |           |   HumanDecision-|
+  | - ML consumes   |           | - L2 Execute    |           | - ML: Efficiency|           |   Artifact      |
+  |   outcome       |           |   if approved   |           |   Tuner active  |           |   [trace_id,    |
+  |                 |           |                 |           |                 |           |   policy_hash,  |
+  |                 |           |                 |           |                 |           |   action,       |
+  |                 |           |                 |           |                 |           |   reviewer_sig] |
   +=================+           +=================+           +=================+           +=================+

   [ L0 REJECT -> L1 REPLAN PATH ]
@@ -160,4 +167,4 @@
   | L1 Cognitive Router receives signal -> selects alternate methodology                      |
   | Retry budget: configurable via L4 (default: 3 attempts)                                  |
   | On exhaustion: L0 forces PATH D (Human Review) regardless of Risk Tier                   |
-  +-------------------------------------------------------------------------------------------+
+  +-------------------------------------------------------------------------------------------+
\ No newline at end of file
diff --git a/docs/technical/Drill-Down 3 - L2 Unified Execution Core & Healing Loop.md b/docs/technical/Drill-Down 3 - L2 Unified Execution Core & Healing Loop.md
index e15032af9..ff86a2ed1 100644
--- a/docs/technical/Drill-Down 3 - L2 Unified Execution Core & Healing Loop.md
+++ b/docs/technical/Drill-Down 3 - L2 Unified Execution Core & Healing Loop.md
@@ -5,13 +5,12 @@

                                    [ FROM: L0 ROUTING — PATH B, C, OR D ]
                                    +---------------------------------------------------------------------------------+
-                                   | PAYLOAD: { "task_id": "dag_node_4", "rbac_token": "jwt_write_scoped",           |
-                                   |            "action_type": "python_exec", "code_block": "df.dropna().to_sql()",  |
-                                   |            "route_mode": "PATH_C", "trace_id": "trc_88x2_node4",               |
-                                   |            "dag": { "nodes": [...], "edges": [...] } }                          |
+                                   | INSTRUCTION PACKET: { "trace_id": "trc_88x2_node4", "policy_hash": "abc123x",   |
+                                   |   "route_mode": "PATH_C", "token_budget": 4096, "allowed_tools": ["python"],    |
+                                   |   "signature": "<HMAC-SHA256>", "dag": { "nodes": [...], "edges": [...] } }     |
                                    +---------------------------------------------------------------------------------+
                                                          ||
-                                                         || (Push: RBAC-Locked DAG Payload)
+                                                         || (Push: Cryptographically Signed InstructionPacket)
                                                          v
 +==========================================================================================================================================================+
 | \\\ L3 – ORCHESTRATION (ENTRY GATE & BLAST-RADIUS MINIMIZER)                                                                                        /// |
@@ -20,13 +19,17 @@
 |  +-------------------------------------------------------------------------------------------+                                                           |
 |  | L3 ORCHESTRATION HANDSHAKE                                                                |                                                           |
 |  |-------------------------------------------------------------------------------------------|                                                           |
-|  | - [HNDS] SEQUENTIAL HANDSHAKE: Verifies DAG node ordering before any action is proposed   |                                                           |
-|  | - [SYNC] WORK INSTRUCTION SYNTHESIS: Translates DAG node into concrete action descriptor  |                                                           |
+|  | - [DAG]   OWNS LOGICAL WORKFLOW & DAG BRANCH RETRIES: L3 assumes ownership of workflow    |                                                           |
+|  |           state and navigation. If a logical branch fails, L3 replans the DAG path.       |                                                           |
+|  | - [RULE]  DOES NOT EXECUTE OR HEAL: L3 strictly orchestrates. It possesses zero physical  |                                                           |
+|  |           tool execution authority and does not perform compute-level healing.            |                                                           |
+|  | - [HNDS]  SEQUENTIAL HANDSHAKE: Verifies DAG node ordering before any action is proposed  |                                                           |
+|  | - [SYNC]  WORK INSTRUCTION SYNTHESIS: Translates DAG node into concrete action descriptor |                                                           |
 |  | - [SHRED] MINIMIZE BLAST RADIUS: Decomposes compound intent into atomic sub-actions       |                                                           |
 |  |           Each sub-action is independently scoped — failure cannot cascade sideways       |                                                           |
 |  | - [GATE]  BLOCK HALLUCINATION: Rejects any proposed action that references non-existent   |                                                           |
 |  |           tools, schemas, or data paths before forwarding to L5                           |                                                           |
-|  | - [ESC]   ESCALATE TO L5 GUARD: All proposed actions forwarded to L5 Safety — no bypass  |                                                           |
+|  | - [ESC]   ESCALATE TO L5 GUARD: All proposed actions forwarded to L5 Safety — no bypass   |                                                           |
 |  +-------------------------------------------------------------------------------------------+                                                           |
 |                                         ||                                                                                                               |
 |                                         || (1. Proposed Action)                                                                                         |
@@ -40,15 +43,16 @@
 |  |-------------------------------------------------------------------------------------------|<====>| - Guardian Script Definitions            |         |
 |  | - Runs BLOCKING guardian scripts (no async — L2 cannot proceed until L5 returns)          |      | - Policy & Permissions Schema            |         |
 |  | - Evaluates Policy + Permissions against proposed action                                  |      | - Sandbox Constraints                    |         |
-|  | - [CONF_CALIB] Risk Gate: Limits blind execution via confidence calibration thresholds    |      +------------------------------------------+         |
+|  | - [STMP]  VERIFY L0 HMAC SIGNATURE: Drops payload if InstructionPacket signature is bad   |      +------------------------------------------+         |
+|  | - [CONF_CALIB] Risk Gate: Limits blind execution via confidence calibration thresholds    |                                                           |
 |  | - [RISK]  RISK TIER CLASSIFY: Assigns tier 1–5 to proposed action                        |                                                           |
-|  | - [STMP]  COMPLIANCE HASH/STAMP: Stamps action with policy version hash                  |                                                           |
 |  | - [STOP]  HARD STOP REJECTION: Immediately blocks tier 4–5 actions                       |                                                           |
-|  | - [BLOCK] BLOCK HOSTILE INPUT: Strips any residual injection vectors                     |                                                           |
+|  | - [BLOCK] ACTIVE HOSTILE INPUT CUT: Strips any residual injection vectors                 |                                                           |
 |  |                                                                                           |                                                           |
-|  | OUTCOME:  ALLOW  -> emits approved_action.json -> proceeds to L2.1 Validator             |                                                           |
-|  |           BLOCK  -> emits rejection signal -> re-routes to L1 for replanning             |                                                           |
-|  |           ESCALATE -> forwards to HUMAN REVIEW (PATH D)                                  |                                                           |
+|  | OUTCOME:  ALLOW  -> emits SandboxEnvelope [trace_id, tool_id, sanitized_args,             |                                                           |
+|  |                     stdout_byte_limit, compute_ms_limit] -> proceeds to L2.1 Validator    |                                                           |
+|  |           BLOCK  -> emits rejection signal -> re-routes to L3 or L1 for logical replan    |                                                           |
+|  |           ESCALATE -> forwards to HUMAN REVIEW GATE (PATH D)                              |                                                           |
 |  +-------------------------------------------------------------------------------------------+                                                           |
 |                                                                                                                                                          |
 |  ML Integration:                                                                                                                                         |
@@ -58,10 +62,10 @@
 |                                                                                                                                                          |
 +==========================================================================================================================================================+
                                          ||
-                                         || (2. IF ALLOW: approved_action.json)
+                                         || (2. IF ALLOW: SandboxEnvelope [trace, tool, args, limits])
                                          v
 +==========================================================================================================================================================+
-| \\\ L2 – UNIFIED EXECUTION CORE (SINGULAR BOTTLENECK FOR SYSTEM MUTATION)                                                                           /// |
+| \\\ L2 – UNIFIED EXECUTION CORE (PTC SANDBOX: ACTION & IMPLEMENTATION FACTORY FLOOR)                                                                /// |
 |==========================================================================================================================================================|
 |                                                                                                                                                          |
 |   [ PRE-EXECUTION AUTHORITY & LOCKING ]                                                                                                                  |
@@ -83,11 +87,11 @@
 |   | [3.1] Abstract Syntax Tree (AST) Parsing: Deconstructs LLM code into logical nodes                                               |                   |
 |   | [3.2] Node Blocklist: Physically strips `os.system`, `subprocess`, `shutil`, and raw `eval()` calls                              |                   |
 |   | [3.3] SQL Injection Guard: Parametrizes all raw strings before passing to database drivers                                       |                   |
-|   | [CID]  RESTRICT UNREGISTERED INTENTS: Rejects any action referencing a tool not in L4 capability registry                       |                   |
-|   | [ZERO_TRUST] SCOPE MINIMAL TOOL ACCESS: Each action granted only the minimum permissions required                               |                   |
+|   | [CID]  RESTRICT UNREGISTERED INTENTS: Rejects any action referencing a tool not in L4 capability registry                        |                   |
+|   | [ZERO_TRUST] SCOPE MINIMAL TOOL ACCESS: Each action granted only the minimum permissions required                                |                   |
 |   | [3.4] Sandbox Dry-Run / Diff Analysis: Simulates action in read-only mode, generates expected diff                               |                   |
-|   |        IF diff matches approved_action.json -> proceed to Execution                                                              |                   |
-|   |        IF diff diverges -> treat as VALIDATION FAIL -> route to L2.3 Healer                                                     |                   |
+|   |        IF diff matches approved SandboxEnvelope -> proceed to Execution                                                          |                   |
+|   |        IF diff diverges -> treat as VALIDATION FAIL -> route to L2.3 Healer Agent                                                |                   |
 |   +----------------------------------------------------------------------------------------------------------------------------------+                   |
 |                             ||                                                                                                                           |
 |                             v                                                                                                                            |
@@ -97,7 +101,8 @@
 |   | [4.1] Micro-VM Boot: Isolated Firecracker instance (<150ms)     |      | • [OOM Guard]: Kills VM if RAM > cgroup_limit (512MB)           |          |
 |   | [4.2] Execution Ceilings: Hard cgroup CPU/Memory starvation caps| <==> | • [Latency Check]: Ceiling [CEIL] triggers L2.3 if > 2000ms     |          |
 |   | [4.3] Virtual Network: Zero external ingress/egress allowed     |      | • [Diff Engine]: Generates JSON Patch (RFC 6902) post-run       |          |
-|   | SOLE DURABLE MUTATION POINT — only L2.2 may write to state      |      +-----------------------------------------------------------------+          |
+|   | [4.4] UWG INTERCEPT: All durable mutations intercepted by       |      +-----------------------------------------------------------------+          |
+|   |       Universal Write Gateway (UWG). No direct disk/DB access.  |                                                                                   |
 |   | [QUOTA] KILL INFINITE COMPUTE BURN: Hard cycle ceiling enforced |                                                                                   |
 |   | [FEEDBACK] INJECT FAILURE CONTEXT: On error, enriches error     |                                                                                   |
 |   |            payload with execution trace before routing to healer|                                                                                   |
@@ -106,28 +111,31 @@
 |           +-----------------++-----------------+                                                                                                         |
 |           || (Exit Code 0: Success)           || (Exit Code >0: Failure / Validation Fail)                                                               |
 |           v                                   v                                                                                                          |
-|   +---------------------------+      +-----------------------------------------------------------------+                                                 |
-|   | 5.0 COMMIT & RELEASE      |      | 6.0 THE DETERMINISTIC HEALER & RECOVERY ENGINE [L2.3: IHealer] |                                                 |
-|   |---------------------------|      |-----------------------------------------------------------------|                                                 |
-|   | [5.1] JSON Patch Apply    |      | [UNDO]    RESET STATE: Destroys micro-VM, reverts to            |                                                 |
-|   |       (RFC 6902 diff)     |      |           boundary_snapshot.json Merkle baseline                |                                                 |
-|   | [5.2] Telemetry Emit      |      | [CIRCUIT] KILL RUN: Prevents loop limits / infinite retry spin  |                                                 |
-|   | [5.3] Mutex Release       |      | [ROOT]    CAPTURE ROOT CAUSE: Extracts stack trace + error log  |                                                 |
-|   | [5.4] [WRITE] COMMIT      |      | [RESET]   REVERT STATE: Restores pre-execution snapshot         |                                                 |
-|   |       VERIFIED STATE      |      | [CURE]    FIX AND RETRY: Correction Strategy Synthesis          |                                                 |
-|   |       CHANGE to L4        |      |           Generates revised_action_proposal.json                |                                                 |
-|   +---------------------------+      | [6.1] Cap: If retries > 3, hard abort to Path D (Human Review)  |                                                 |
-|                                      +-----------------------------------------------------------------+                                                 |
+|   +-----------------------------------+      +-----------------------------------------------------------------+                                         |
+|   | 5.0 COMMIT & RELEASE              |      | 6.0 THE DETERMINISTIC RECOVERY ENGINE [L2.3: IHealer]           |                                         |
+|   |-----------------------------------|      |-----------------------------------------------------------------|                                         |
+|   | [5.1] JSON Patch Apply            |      | Healer Agent [♦ I::IHealer ♦]                                   |                                         |
+|   |       (RFC 6902 diff)             |      | [AUTH]    SOLE AUTHORITY FOR PHYSICAL TOOL RETRIES & COMPUTE    |                                         |
+|   | [5.2] Telemetry Emit              |      |           RECOVERY. (Workflow retries are owned by L3).         |                                         |
+|   | [5.3] Mutex Release               |      | [UNDO]    RESET STATE: Destroys micro-VM, reverts to            |                                         |
+|   | [5.4] [UWG] UNIVERSAL WRITE       |      |           boundary_snapshot.json Merkle baseline                |                                         |
+|   |       GATEWAY (Deny-By-Default)   |      | [CIRCUIT] KILL RUN: Prevents loop limits / infinite retry spin  |                                         |
+|   |       * Mediates ALL FS, DB,      |      | [ROOT]    CAPTURE ROOT CAUSE: Extracts stack trace + error log  |                                         |
+|   |         Ledger, and Vector Writes |      | [RESET]   REVERT STATE: Restores pre-execution snapshot         |                                         |
+|   |       * Enforces [trace_id, target|      | [CURE]    FIX AND RETRY: Correction Strategy Synthesis          |                                         |
+|   |         diff, ts] standard        |      |           Generates revised_action_proposal.json                |                                         |
+|   +-----------------------------------+      | [6.1] Cap: If retries > 3, hard abort to Path D (Human Review)  |                                         |
+|                                              +-----------------------------------------------------------------+                                         |
 |                                                         ||                                                                                               |
 |   [ DATA MUTATION & RAG SYNC ]                          || (4. Error Root / Rollback Req)                                                               |
 |   +-----------------------------------------------------------------+                                                                                   |
 |   | • Sandbox Snapshot Revert (on failure — byte-for-byte restore)  |                                                                                   |
-|   | • Embedding Generation: Computes new vector for mutated content  |                                                                                   |
-|   | • Vector Store Write: Async push to external vector store        |                                                                                   |
-|   | • [TRTH] ANCHOR KNOWLEDGE DRIFT: Prevents stale embeddings       |                                                                                   |
-|   |   from persisting across sessions — drift detected and flagged   |                                                                                   |
-|   | • [ASYNC_SYNC]: Vector store write is non-blocking after L2.2    |                                                                                   |
-|   |   confirms commit — state update does not block response path    |                                                                                   |
+|   | • Embedding Generation: Computes new vector for mutated content |                                                                                   |
+|   | • UWG Vector Store Write: Async push to external vector store   |                                                                                   |
+|   | • [TRTH] ANCHOR KNOWLEDGE DRIFT: Prevents stale embeddings      |                                                                                   |
+|   |   from persisting across sessions — drift detected and flagged  |                                                                                   |
+|   | • [ASYNC_SYNC]: Vector store write is non-blocking after UWG    |                                                                                   |
+|   |   confirms commit — state update does not block response path   |                                                                                   |
 |   +-----------------------------------------------------------------+                                                                                   |
 |                                                                                                                                                          |
 |   ML Integration (feeds Meta-Learning Bus):                                                                                                              |
@@ -146,7 +154,7 @@
 |  revised_action_proposal.json  ====>  L3 ORCHESTRATION  ====>  L5 SAFETY GATE  ====>  L2.1 VALIDATOR  ====>  L2.2 EXECUTION                             |
 |                                                                                                                                                          |
 |  INVARIANT: Any healed or revised plan MUST re-clear L5 Safety before retry.                                                                             |
-|             There is ZERO direct path from L2.3 Healer to L2.2 Execution.                                                                               |
+|             There is ZERO direct path from Healer Agent to L2.2 Execution.                                                                               |
 |             Bypassing L5 on a healed plan is a HARD CONSTITUTIONAL VIOLATION.                                                                            |
 |                                                                                                                                                          |
 |  [SEED] FORCE STRICT HEAL DETERMINISM: During L3 re-entry after healing, non-deterministic                                                               |
@@ -161,27 +169,11 @@
 +==========================================================================================================================================================+
 | FINAL DECISION / OUTCOME LOGGING                                                                                                                         |
 |==========================================================================================================================================================|
-| - Outcome and state diffs are versioned and committed to L4 audit log                                                                                    |
-| - [SYNC]  UPDATE SHARED TEAM MEMORY: Non-blocking state update occurs only after L2.2 confirms commit                                                    |
+| - Outcome and state diffs are versioned and committed to L4 audit log via ExecutionTrace contract                                                        |
+|   [trace_id, plan_hash, actor, target_resource, state_diff, timestamp, replay_key(Hash of trace+plan+transcript)]                                        |
+| - [SYNC]  UPDATE SHARED TEAM MEMORY: Mediated by UWG, occurs only after successful Sandbox confirm                                                       |
 | - [RECON] VERIFY DATA MATCHES REALITY: Detects ghost mutations across state layers (L4 vs. live state)                                                   |
 | - Metrics captured: Execution Latency, Outcome Accuracy, Compute Cost, Human Correction Rate                                                             |
 |                                                                                                                                                          |
 |  +===(ZERO-LOSS LOOP: COMMIT TO L4 VIA META-LEARNING BUS)=================================================================>  L4 ANCHOR (VERSIONED UPDATE) |
-+==========================================================================================================================================================+
-
-+==========================================================================================================================================================+
-| CRITICAL DISSEMINATION GUARANTEES (L2 SCOPE)                                                                                                            |
-|==========================================================================================================================================================|
-| 1.  NO SKIPPING THE SAFETY GATES: Every proposed action — including healed ones — must clear L5 before L2 entry.                                        |
-| 2.  ALWAYS ATTACH THE SAFETY FENCES: [D0] fences from L5 Elevator Shaft remain active throughout L2 execution.                                          |
-| 3.  ONLY LOAD DATA WHEN NEEDED: [JIT] context loading prevents stale or over-broad context injection.                                                    |
-| 4.  HEALED PLANS MUST RE-CLEAR SAFETY: Zero trust on corrected actions — trust is not inherited from prior approved_action.json.                         |
-| 5.  DON'T LOSE DATA ON ERROR: [FEEDBACK] enriches error payload before routing to healer — full context preserved.                                       |
-| 6.  ISOLATE EVERY CHANGE IN SANDBOX: Firecracker micro-VM ensures zero durable damage on failure.                                                        |
-| 7.  ONLY USE PRE-APPROVED SYSTEM TOOLS: [CID] physically blocks rogue function calls not in L4 capability registry.                                      |
-| 8.  BREAK TASKS INTO TINY PIECES: [SHRED] at L3 minimizes blast radius — each atomic sub-action is independently scoped.                                 |
-| 9.  PROTECT KNOWLEDGE FROM AGENT DRIFT: [TRTH] anchoring prevents agents from corrupting the vector truth store.                                         |
-| 10. STOP AGENTS FROM BURNING MONEY: [QUOTA] + [CEIL] kill infinite loops and compute spikes before they propagate.                                       |
-| 11. RECORD THE WHY, NOT WHAT: [ROOT] RCA captures decision logic and stack trace — not just the error code.                                              |
-| 12. DOUBLE-CHECK DATA MATCHES THE WORLD: [RECON] detects ghost or hidden mutations across state layers post-commit.                                      |
-+==========================================================================================================================================================+
++==========================================================================================================================================================+
\ No newline at end of file
diff --git a/docs/technical/agentic_process_mapping.md b/docs/technical/agentic_process_mapping.md
index 67c797cdd..ad132c42f 100644
--- a/docs/technical/agentic_process_mapping.md
+++ b/docs/technical/agentic_process_mapping.md
@@ -16,22 +16,23 @@
                               |   • Message Architecture & Compliance                    |          |   • Content Quality & Strategy                           |          |   • InfrastructureUpgradesOrchestrator                   |
                               |   • Outreach Learning & Validation                       |          |   • Fact Check & Strategic Planning                      |          |                                                          |
                               |                                                          |          |                                                          |          | enforcement/ (11 strategies)                             |
-                              | engines/ (4 engines)                                     |          | engines/ (47 engines)                                    |          |   • AdaptiveretrievalgateStrategy                        |
+                              | engines/ (5 engines)                                     |          | engines/ (48 engines)                                    |          |   • AdaptiveretrievalgateStrategy                        |
                               |   • control_plane.py (orchestration)                     |          |   • achievement_prioritizer_engine                       |          |   • CircuitbreakerStrategy                               |
                               |   • hop_stage_registry.py (workflow)                     |          |   • ats_compatibility_engine                             |          |   • DecomposedqueryagentStrategy                         |
                               |   • message_body_composer.py                             |          |   • content_quality_engine                               |          |                                                          |
-                              |                                                          |          |   • resume_orchestrator_engine                           |          | config/ (6 configs)                                      |
-                              | config/ (9 configs)                                      |          |   • skill_ordering_engine                                |          |   • environment_config.py                                |
-                              |   • agent_specs.json (HOP pipeline specs)                |          |   • template_optimizer_engine                            |          |   • integration_config.py                                |
-                              |   • loader_config.py                                     |          |                                                          |          |                                                          |
-                              |                                                          |          | config/ (5 configs)                                      |          | data/ (2 knowledge bases)                                |
-                              | tools/ (48 tools)                                        |          |   • agent_spec_config.py (Pydantic schemas)              |          |   • master_resume.json (Amit's experience)               |
-                              | types/ (20 domain models)                                |          |   • reasoning_toggles_config.py                          |          |   • sender_knowledge_base.json                           |
-                              | validators/ (6 validators)                               |          |                                                          |          |                                                          |
-                              | enforcement/ (1 strategy)                                |          | tools/ (33 tools)                                        |          | types/ (3 shared types)                                  |
-                              |   • ExecutiveStrategyAgent                               |          | types/ (16 domain models)                                |          | validators/ (2 validators)                               |
-                              +----------------------------------------------------------+          | validators/ (5 validators)                               |          +----------------------------------------------------------+
-                                                       |                                            +----------------------------------------------------------+                                       |
+                              |   • lic_spine_adapter.py                                 |          |   • resume_orchestrator_engine                           |          | config/ (6 configs)                                      |
+                              |                                                          |          |   • skill_ordering_engine                                |          |   • environment_config.py                                |
+                              | config/ (9 configs)                                      |          |   • template_optimizer_engine                            |          |   • integration_config.py                                |
+                              |   • agent_specs.json (HOP pipeline specs)                |          |   • rg_spine_adapter.py                                  |          |                                                          |
+                              |   • loader_config.py                                     |          |                                                          |          | data/ (2 knowledge bases)                                |
+                              |                                                          |          | config/ (5 configs)                                      |          |   • master_resume.json (Amit's experience)               |
+                              | tools/ (48 tools)                                        |          |   • agent_spec_config.py (Pydantic schemas)              |          |   • sender_knowledge_base.json                           |
+                              | types/ (20 domain models)                                |          |   • reasoning_toggles_config.py                          |          |                                                          |
+                              | validators/ (6 validators)                               |          |                                                          |          | types/ (3 shared types)                                  |
+                              | enforcement/ (1 strategy)                                |          | tools/ (33 tools)                                        |          | validators/ (2 validators)                               |
+                              |   • ExecutiveStrategyAgent                               |          | types/ (16 domain models)                                |          | utils/ (1 module)                                        |
+                              +----------------------------------------------------------+          | validators/ (5 validators)                               |          |   • determinism_util.py (canon+hash)                     |
+                                                       |                                            +----------------------------------------------------------+          +----------------------------------------------------------+
                                                        | (Campaign Workflow Requests)                                            | (Resume Generation Requests)                                        | (Shared Services & Knowledge)
                                                        v                                                                         v                                                                     v

@@ -45,21 +46,24 @@
           |  NoSQL / Documents |          +------------------------------------------------------+  +-----------------------------------------------------+  +---------------------------------------------------------------------------+                                  ||
           | [C0] & [CACHE_LOCK]|          | L1: COGNITIVE STUDIO [PHASE 1-4 / PTC COMPILER]      |  | L6: OBSERVABILITY & ANOMALY DETECTION               |  | L4: STATE, MEMORY & PERSISTENCE [♦ I::IMemoryStore ♦]                     | <==(Pulls Updated Weights & Checkpoints)==||
           +--------------------+          |------------------------------------------------------|  |-----------------------------------------------------|  |---------------------------------------------------------------------------|                                  ||
-                   |                      | - Generates [U0: USER PROMPT] (ZERO auth)            |  | - P1: INGESTION: Execution Latency, Error Rates     |  | - P1: COGNITIVE REGISTRY: Active Models, Prompts, Templates, Calibration  |                                  ||
-                   | (Semantic Search)    | - Reads L4 active model version                      |  | - P2: ANOMALY ENGINE: anomaly_score, Detect Drift   |  | - P2: CAPABILITY REGISTRY: Tool Availability, API Credentials, Policies   |                                  ||
-                   +--------------------->| - Retrieval from RAG index (READ only)               |  | - P3: BROADCAST: Emit anomaly, drift, injection     |  | - P3: WORKFLOW MEMORY: Active Job States, Pending Steps, Dependency DAG   |                                  ||
-                                          | - Augments prompt with [C0] Context                  |  | - P4: ARCHIVER: Store Raw Metrics, System Snapshots |  | - P4: TELEMETRY LEDGER: Routing Decisions, Execution Logs, Error Reports  |                                  ||
-                                          | - Cannot approve / Cannot execute                    |  |-----------------------------------------------------|  |---------------------------------------------------------------------------|                                  ||
-                                          | - P1: PRIMING: Hydrate via Knowledge Graph, Sem-Mem  |  | - [TLM] CROSS-LAYER TELEMETRY                       |  | [ RULES ] - L4 never authorizes. L4 never executes.                       |                                  ||
-                                          | - P2: ORCHESTRATION: Coordinator, Tool Agents Draft  |  | - [SGNL] ANOMALY SIGNAL GENERATOR                   |  |           - Future executions use updated versions via L0.                |                                  ||
-                                          | - P3: PTC CALIBRATION: Simulate CoT, Calc Complexity |  | - [RCA] ROOT CAUSE ANALYSIS (RCA)                   |  |           - All ML improvements written as versioned updates.             |                                  ||
-                                          | - P4: SYNTHESIS: Emit intent, tools, raw_reasoning   |  | =>[BROADCAST] BREAK RECURSIVE CYCLES                |  | [ PROMPTS]- [S0: SYSTEM] Rulebooks (ABSOLUTE Authority)                   |                                  ||
-                                          | - [LOG] LOG ORIGINAL USER INTENT                     |  |   (Triggers Stall & Forces Path D)                  |  |           - [I0: INSTRUCTIONAL] Mixins (GOVERNED Authority)               |                                  ||
-                                          | ML Integration:                                      |  | ML Integration:                                     |  | [ STATE ] - [TMPL] REASONING TEMPLATES, [SYNC] TEAM MEMORY                |                                  ||
-                                          | • Model calibration                                  |  | • Improves anomaly classifiers                      |  |           - [TOOL] TOOL INVENTORY (Python/Bash enabled)                   |                                  ||
-                                          | • Drift detection                                    |  | • Refines signal grouping                           |  | [ RAG ]   - [TRTH] ANCHOR KNOWLEDGE DRIFT [♦ I::IMemoryStore ♦]           |                                  ||
-                                          +------------------------------------------------------+  +-----------------------------------------------------+  |           - Embedding Model Reference                                     |                                  ||
-                                                    || (WRITE: [U0] & Script Proposals)                       || (WRITE: Structured Telemetry)               | [ LOGS ]  - Drift Metrics, Escalations, Meta-Learning                     |                                  ||
+                   |                      | [1. WORKING MEMORY] - Reads L4 model/RAG index       |  | - [1.1] INGESTION: Execution Latency, Error Rates   |  | - [1.1] COGNITIVE REGISTRY: Active Models, Prompts, Templates, Calib      |                                  ||
+                   | (Semantic Search)    | - Hydrate Task Schema, Conv History, Env Snapshot    |  | - [1.2] ANOMALY ENGINE: anomaly_score, Detect Drift |  | - [1.2] CAPABILITY REGISTRY: Tool Availability, API Credentials, Policies   |                                  ||
+                   +--------------------->| - Augments prompt with [C0] Context (ZERO auth)      |  | - [1.3] BROADCAST: Emit anomaly, drift, injection   |  | - [1.3] WORKFLOW MEMORY: Active Job States, Pending Steps, Dependency DAG   |                                  ||
+                                          | [2. THOUGHT GENERATION & PLANNING]                   |  | - [1.4] ARCHIVER: Store Raw Metrics, Sys Snapshots  |  | - [1.4] TELEMETRY LEDGER: Routing Decisions, Execution Logs, Error Reports  |                                  ||
+                                          | - [2.1] PRIMING: Hydrate via Knowledge Graph, Sem-Mem|  | - [METRICS] Validates quantitative execution claims |  |---------------------------------------------------------------------------|                                  ||
+                                          | - [2.2] ORCHESTRATION: Coordinator, Tool Agents Draft|  |             (e.g. comparing TokenControl baseline)  |  | [ RULES ] - L4 never authorizes. L4 never executes.                       |                                  ||
+                                          | - [2.3] PTC CALIBRATION: Simulate CoT, Calc Complex  |  |-----------------------------------------------------|  |           - Future executions use updated versions via L0.                |                                  ||
+                                          | - [2.4] SYNTHESIS: Emit intent, tools, raw_reasoning |  | - [TLM] CROSS-LAYER TELEMETRY                       |  |           - All ML improvements written as versioned updates.             |                                  ||
+                                          | - Emits Plan_Provenance Artifact (trace_id)          |  | - [SGNL] ANOMALY SIGNAL GENERATOR                   |  | [ PROMPTS]- [S0: SYSTEM] Rulebooks (ABSOLUTE Authority)                   |                                  ||
+                                          | [3. COGNITIVE SAFETY CHECK (PRE-COMPUTE)]            |  | - [RCA] ROOT CAUSE ANALYSIS (RCA)                   |  |           - [I0: INSTRUCTIONAL] Mixins (GOVERNED Authority)               |                                  ||
+                                          | - [3.1] Dynamic Guardrails (Pre-Compute local filter)|  | =>[BROADCAST] BREAK RECURSIVE CYCLES                |  | [ STATE ] - [TMPL] REASONING TEMPLATES, [SYNC] TEAM MEMORY                |                                  ||
+                                          | - [3.2] Emits TokenControl Artifact (locks budget)   |  |   (Triggers Stall & Forces Path D)                  |  |           - [TOOL] TOOL INVENTORY (Python/Bash enabled)                   |                                  ||
+                                          | - [3.3] LOG ORIGINAL USER INTENT                     |  | ML Integration:                                     |  | [ RAG ]   - [TRTH] ANCHOR KNOWLEDGE DRIFT [♦ I::IMemoryStore ♦]           |                                  ||
+                                          | ML Integration:                                      |  | • Improves anomaly classifiers                      |  |           - [SUPERVISOR]: Knowledge Supervisor (Dense Retrain/Growth Loop)|                                  ||
+                                          | • Model calibration                                  |  | • Refines signal grouping                           |  |           - [HYBRID RAG]: RetrievalQuery -> Rerank -> CitationBundle      |                                  ||
+                                          | • Drift detection                                    |  |                                                     |  | [ LOGS ]  - Drift Metrics, Escalations, Meta-Learning                     |                                  ||
+                                          +------------------------------------------------------+  +-----------------------------------------------------+  |           - [MEMORY]: Case-Associative Schema & Semantic Hooks            |                                  ||
+                                                    || (WRITE: [U0] & Script Proposals)                       || (WRITE: Structured Telemetry)               |           - [EPISODIC]: Links Episodic Signals to Policy Outcomes         |                                  ||
                                                     =========================================================================================================+---------------------------------------------------------------------------+                                  ||
                                                                                  (READ: Model Config, RAG Config, Detection Config Parameters)                                                                                                                              ||
                                                                                                                                                                                                                                                                             ||
@@ -75,16 +79,19 @@
                                                                | - Classifies intent vs. L4 Routing State                                  |          +---------------------------------------------------------------------+                                               ||
                                                                | - [JIT] Load context on-demand via the "Elevator Shaft" (L0 <-> L5)       |          | [ META-LEARNING & OPTIMIZATION BUS ]                                |                                               ||
                                                                | - Cannot evaluate rules / Cannot execute                                  |          |---------------------------------------------------------------------|                                               ||
-                                                               | - P1: INGEST: Assign Trace_ID, Policy Hash, Correlate L1 vs L6            |          | 1. [PULL] DATA FOR TRAINING (From L4 Black Box Audit)               |                                               ||
-                                                               | - P2: ELECTION: Deterministic Ruleset, Learned ML, Guardian Override      |          | 2. ANALYZE: [RCA] ROOT CAUSE ANALYSIS                               |                                               ||
-                                                               | - P3: ARBITRATION: Check Tool Inventory, Budget Forecast, Rate Limits     |          | 3. OPTIMIZE & COMMIT: Writes versions to L4 Anchor                  |====(Writes Optimized Rules & Checkpoints)====>||
-                                                               | - P4: DISPATCH: Stamp Route Mode, Encrypt/Seal Signed Execution Plan      |          +---------------------------------------------------------------------+                                               ||
+                                                               | - [1.1] INGEST: Assign Trace_ID, Policy Hash, Correlate L1 vs L6          |          | 1. [PULL] DATA FOR TRAINING (From L4 Black Box Audit)               |                                               ||
+                                                               | - [1.2] ELECTION: Deterministic Ruleset, Learned ML, Guardian Override    |          | 2. ANALYZE: [RCA] ROOT CAUSE ANALYSIS                               |                                               ||
+                                                               |   * IF (Risk_Score < 0.2) AND (Op == READ) -> Path A (Fast Lane)          |          | 3. OPTIMIZE & COMMIT: Writes versions to L4 Anchor                  |====(Writes Optimized Rules & Checkpoints)====>||
+                                                               |   * IF (Ambiguity > Threshold) -> Consult Learned Router Model (L4)       |          +---------------------------------------------------------------------+                                               ||
+                                                               |   * IF (L6 Signal == CRITICAL) -> Force Path D (Human Review)             |                                                                                                                                ||
+                                                               | - [1.3] ARBITRATION: Check Tool Inventory, Budget Forecast, Rate Limits   |                                                                                                                                ||
+                                                               | - [1.4] DISPATCH: Stamp Route Mode, Encrypt/Seal Signed Execution Plan    |                                                                                                                                ||
                                                                | ML Integration:                                                           |                                                                                                                                ||
                                                                | [1. Pattern Analysis ]=======(Match Intent Logs)==========================|===============================================================================================================================>||
                                                                | [2. Threshold Tuning ]=======(Assess Risk Limits)=========================|===============================================================================================================================>||
                                                                | [3. Path Optimization]=======(Optimize Routing)===========================|===============================================================================================================================>||
                                                                +---------------------------------------------------------------------------+                                                                                                                                ||
-                                                                                                   v (Dispatches Signed Execution Plan)                                                                                                                                     ||
+                                                                                                   v Dispatches InstructionPacket (See Core Data Contracts)                                                                                                                 ||
                                                                +---------------------------------------------------------------------------+                                                                                                                                ||
                                                                | ASSEMBLY STAGE (SANDBOX AIRLOCK & DETERMINISTIC COMPOSITION)              |                                                                                                                                ||
                                                                |---------------------------------------------------------------------------|                                                                                                                                ||
@@ -94,7 +101,7 @@
                                                                | [C0: DEPENDENCY]    - Elevator Shaft/RAG injected knowledge               |                                                                                                                                ||
                                                                | [U0: USER PROMPT]   - Raw intent (L1)                                     |                                                                                                                                ||
                                                                | => Final Package = Validated Script ready for Path B/C Execution          |                                                                                                                                ||
-                                                               | => [BLOCK] BLOCK HOSTILE INPUT VECTORS (Neutralize Attack Paths)          |                                                                                                                                ||
+                                                               | => [BLOCK] L5 Hostile Input Vector Neutralization applied                 |                                                                                                                                ||
                                                                | => [SPLIT] SPLIT INTO ATOMIC TASKS (Limit Scope, Prevent Collateral)      |                                                                                                                                ||
                                                                | - Emits: Governed Payload => Passes to Paths A / B / C / D                |                                                                                                                                ||
                                                                +---------------------------------------------------------------------------+                                                                                                                                ||
@@ -111,36 +118,36 @@
               +-----------------------------------+         +-----------------------------------+      |      +-----------------------------------+       +-----------------------------------+                                                                         ||
               | Final Response                    |         | L3 – ORCHESTRATION [♦ I::IOrch ♦] |      |      | L3 – ORCHESTRATION [♦ I::IOrch ♦] |       | L3 – ORCHESTRATION [♦ I::IOrch ♦] |                                                                         ||
               |-----------------------------------|         |-----------------------------------|      |      |-----------------------------------|       |-----------------------------------|                                                                         ||
-              | - No system mutation              |         | - [HNDS] SEQUENTIAL HANDSHAKE     |      |      | - [HNDS] SEQUENTIAL HANDSHAKE     |       | - Prepares review artifact        |                                                                         ||
-              | - Logged outcome                  |         | - [SYNC] WORK INSTRUCT SYNTH      |      |      | - [SYNC] WORK INSTRUCT SYNTH      |       +-----------------------------------+                                                                         ||
-              |                                   |         | - [ESC] ESCALATE TO L5 GUARD      |      |      | - [ESC] ESCALATE TO L5 GUARD      |                         |                                                                                             ||
-              | ML consumes outcome               |         | - [GATE] Block hallucination      |      |      | - P1: EVALUATE Result vs DAG      |                         v                                                                                             ||
-              |                                   |         | - [SEED] Force strict heal        |      |      | - P2: SEQUENCE Branches & Parallel|       ML Integration:                                                                                                 ||
-              |                                   |         | - P1: EVALUATE Result vs DAG      |      |      | - P3: COORDINATE Cross-Agent Sync |       [1. Efficiency Tuner]             |======(Evaluate Pipeline Bottlenecks)=======================================>||
-              |                                   |         | - P2: SEQUENCE Branches & Parallel|      |      | - P4: ROUTE Complete, Escalate, L2|       [2. Planning Optimization]        |======(Tune Orchestration Efficiency)=======================================>||
-              +-----------------------------------+         | - P3: COORDINATE Cross-Agent Sync |      |      +-----------------------------------+                                                                                                                     ||
-                              |                             | - P4: ROUTE Complete, Escalate, L2|      |                           |                                                                                                                                    ||
-                              |                             +-----------------------------------+      |                [IF] LOGIC VIOLATION DETECTED?                                                                                                                  ||
+              | - No system mutation              |         | - [DAG] OWNS LOGICAL WORKFLOW &   |      |      | - [DAG] OWNS LOGICAL WORKFLOW &   |       | - Prepares review artifact        |                                                                         ||
+              | - Logged outcome                  |         |         DAG BRANCH RETRIES        |      |      |         DAG BRANCH RETRIES        |       | - [RULE] DOES NOT EXECUTE OR HEAL |                                                                         ||
+              |                                   |         | - [RULE] DOES NOT EXECUTE OR HEAL |      |      | - [RULE] DOES NOT EXECUTE OR HEAL |       +-----------------------------------+                                                                         ||
+              | ML consumes outcome               |         | - [HNDS] SEQUENTIAL HANDSHAKE     |      |      | - [HNDS] SEQUENTIAL HANDSHAKE     |                         |                                                                                             ||
+              |                                   |         | - [SYNC] WORK INSTRUCT SYNTH      |      |      | - [SYNC] WORK INSTRUCT SYNTH      |                         v                                                                                             ||
+              |                                   |         | - [2.1] EVALUATE Result vs DAG    |      |      | - [2.1] EVALUATE Result vs DAG    |       ML Integration:                                                                                                 ||
+              |                                   |         | - [2.2] SEQUENCE Branches & Sync  |      |      | - [2.2] SEQUENCE Branches & Sync  |       [1. Efficiency Tuner]             |======(Evaluate Pipeline Bottlenecks)=======================================>||
+              +-----------------------------------+         | - [2.3] ROUTE Complete or Escalate|      |      | - [2.3] ROUTE Complete or Escalate|       [2. Planning Optimization]        |======(Tune Orchestration Efficiency)=======================================>||
+                              |                             +-----------------------------------+      |      +-----------------------------------+                                                                                                                     ||
+                              |                                            |                           |                           |                                                                                                                                    ||
+                              |                                            |                           |                [IF] LOGIC VIOLATION DETECTED?                                                                                                                  ||
                               |                                            |                           |                <=======(Yes: [!] ESCALATE)=========+                                                                                                           ||
                               |                                            v (Passes to Safety Guard)  |                           |                        |                                                                                                           ||
                               |                             +-----------------------------------+      |                           |                        |                           +-----------------------------------+                                           ||
-                              |                             | L5: SAFETY [♦ I::IValidator ♦]    | <====+===========================+                        |                           | HUMAN REVIEW                      |                                           ||
+                              |                             | L5: SAFETY [♦ I::IValidator ♦]    | <====+===========================+                        |                           | HUMAN REVIEW GATE                 |                                           ||
                               |                             |-----------------------------------|    (No)                                                   |                           |-----------------------------------|                                           ||
-                              |                             | - [RISK] RISK TIER CLASSIFY       |      |                                                    |                           | - Manual approve/reject           |                                           ||
-                              |                             | - [STMP] COMPLIANCE HASH/STAMP    |      |                                                    |                           |                                   |                                           ||
-                              |                             | - [STOP] HARD STOP REJECTION      |      |                                                    |                           | ML Integration:                   |                                           ||
-                              |                             | - [BLOCK] BLOCK HOSTILE INPUT     |      |                                                    |                           | [1. Reviewer Calibration]         |======(Evaluate Human Reviewer Bias)==========>||
-                              |                             | - P1: VALIDATE Proposal vs Policy |      |                                                    |                           +-----------------------------------+                                           ||
-                              |                             | - P2: ENFORCE Approve, Remediate  |      v                                                    +---------------------------+                |                                                              ||
-                              |                             | - P3: REMEDIATE Safety Retry/Fix  |======(Track False Positive & Negatives)================================================================|=============================================================>||
-                              |                             | - P4: CERTIFY Audit Logs & Hashes |======(Analyze Safety Block Accuracy)===================================================================|=============================================================>||
-                              |                             | ML: Policy Optimization           |======(Tune Safety Rule Strictness)=====================================================================|=============================================================>||
-                              |                             |                                   |======(Adapt Risk Threshold Configs)====================================================================|=============================================================>||
-                              |                             +-----------------------------------+                                                                                                        | (If Approved)                                                ||
-                              |                                            |                                                                                                                             |                                                              ||
-                              |                 [RE-ROUTE TO L1] <==(Fail)-+-(Pass)==> [AUTH] STAMP WORK CONTRACT (Sandbox Permission Granted)                                                           |                                                              ||
-                              |                   (If Rejected)            |           (Applies to Paths B & C)                                                                                      |                                                              ||
-                              |                                            v (Grants Sandbox Execution Permission)                                                                                       v (Routes Human Decision)                                      ||
+                              |                             | - [RISK] RISK TIER CLASSIFY       |      |                                                    |                           | - Evidence Pack: Policy Eval, Risk|                                           ||
+                              |                             | - [STMP] VERIFY L0 HMAC SIGNATURE |      |                                                    |                           |   Score, Logs, State Snapshots    |                                           ||
+                              |                             | - [STOP] HARD STOP REJECTION      |      |                                                    |                           | - Action: Approve / Modify / Reject                                           ||
+                              |                             | - [BLOCK] ACTIVE HOSTILE INPUT CUT|      |                                                    |                           | - Output: HumanDecisionArtifact   |                                           ||
+                              |                             | - [3.1] VALIDATE Proposal vs Policy|     |                                                    |                           | - [LOOP] Bidirectional Policy Sync|                                           ||
+                              |                             | - [3.2] ENFORCE Approve, Remediate|      |                                                    |                           |   -> Inject to L0 Guardian        |                                           ||
+                              |                             | - [3.3] REMEDIATE Safety Retry/Fix|      |                                                    |                           |   -> Revise/Retool via L2 Healer  |                                           ||
+                              |                             | ML: Policy Optimization           |      v                                                    |                           | ML Integration:                   |                                           ||
+                              |                             |                                   |======(Track False Positive & Negatives)===================+---------------------------+ [1. Reviewer Calibration]         |======(Evaluate Human Reviewer Bias)==========>||
+                              |                             +-----------------------------------+======(Analyze Safety Block Accuracy)===================================================|=============================================================>||              ||
+                              |                                            |                     ======(Tune Safety Rule Strictness)=====================================================|=============================================================>||              ||
+                              |                 [RE-ROUTE TO L1] <==(Fail)-+-(Pass)==> [AUTH] STA======(Adapt Risk Threshold Configs)====================================================|=============================================================>||              ||
+                              |                   (If Rejected)            |           (Applies to Paths B & C)                                                                          | (If Approved)                                                ||              ||
+                              |                                            v (Grants Sandbox Execution Permission)                                                                       v (Routes Human Decision)                                      ||              ||
                               |                             +=======================================================================================================================================================================================================+   ||
                               |                             | \\\ L2 – UNIFIED EXECUTION CORE (PTC SANDBOX: ACTION & IMPLEMENTATION FACTORY FLOOR)                                                                                                              /// |   ||
                               |                             |=======================================================================================================================================================================================================|   ||
@@ -151,25 +158,28 @@
                               |                             |  |    -> [FREEZ] FREEZE CLEAN SYSTEM STATE                         |  [2. Resource Predictor] =======(Optimize Sandbox Compute Cost)=================================================================>||
                               |                             |  |    -> [CLAIM] CLAIM EXCLUSIVE WRITE ACCESS                      |  [3. RL Rollback Refiner]=======(Self-Correct Healer Logic)=====================================================================>||
                               |                             |  |    -> [GUARD] PRESERVE EXISTING CODE INTEGRITY                  |                                                                                                                                  |   ||
-                              |                             |  |         v                                                       |  [ INFERENCE & TOKEN COMPRESSION ]                                                                                               |   ||
-                              |                             |  |   [P2: PTC EXECUTION] [♦ I::IMemoryStore ♦]                     |  - N tools called in 1 inference pass                                                                                            |   ||
-                              |                             |  |    -> Invoke Tool, Capture Output, Invoke Chained Tools         |  - Context window isolated from raw data                                                                                         |   ||
-                              |                             |  |    -> [TOOL 1..N] await query_database(sql_N)                   |  - Token Cost: ~37% LOWER                                                                                                        |   ||
-                              |                             |  |    -> [FILTER] AGGREGATE RAW DATA IN SANDBOX                    |                                                                                                                                  |   ||
-                              |                             |  |    -> [WRITE] COMMIT VERIFIED STATE CHANGE                      |  [ DATA MUTATION ]               [ EXTERNAL RAG ]                                                                                |   ||
+                              |                             |  |         v Enters via SandboxEnvelope (See Core Data Contracts)                                                                                                                                     |   ||
+                              |                             |  |   [P2: PTC EXECUTION] [♦ I::IMemoryStore ♦]                     |  [ INFERENCE & TOKEN COMPRESSION ]                                                                                               |   ||
+                              |                             |  |    -> Invoke Tool, Capture Output, Invoke Chained Tools         |  - N tools called in 1 inference pass                                                                                            |   ||
+                              |                             |  |    -> [TOOL 1..N] await query_database(sql_N)                   |  - Context window isolated from raw data                                                                                         |   ||
+                              |                             |  |    -> [FILTER] AGGREGATE RAW DATA IN SANDBOX                    |  - Token Cost: ~37% LOWER (vs. legacy baseline in L6)                                                                            |   ||
+                              |                             |  |    -> [UWG] UNIVERSAL WRITE GATEWAY (Deny-By-Default)           |                                                                                                                                  |   ||
+                              |                             |  |       * Mediates ALL FS, DB, Ledger, and Vector Writes          |  [ DATA MUTATION ]               [ EXTERNAL RAG ]                                                                                |   ||
                               |                             |  |    -> [CEIL] TERMINATE STUCK COMPUTE CYCLES                     |  - Sandbox Snapshot Revert       +--------------+                                                                                |   ||
                               |                             |  |         v                                                       |  - Embedding generation          | Vector Store |                                                                                |   ||
-                              |                             |  |   [Evaluation     ]--+                                          |  - Vector store write ---------> +--------------+                                                                                |   ||
+                              |                             |  |   [Evaluation     ]--+                                          |  - UWG Vector store write -----> +--------------+                                                                                |   ||
                               |                             |  |         | (Fail)     |                                          |  - [TRTH] ANCHOR KNOWLEDGE DRIFT | [ASYNC_SYNC] |                                                                                |   ||
                               |                             |  |         v            |                                          |    OVER TIME                     +--------------+                                                                                |   ||
-                              |                             |  +-- [P3: PTC HEALER ]  |                                          |                                                                                                                                  |   ||
-                              |                             |  |   [♦ I::IHealer ♦]   |                                          |                                                                                                                                  |   ||
-                              |                             |  |    -> Detect Failures, Apply Retry Policies, Escalate           |                                                                                                                                  |   ||
+                              |                             |  +-- [P3: PTC HEALER]   |                                          |                                                                                                                                  |   ||
+                              |                             |  |   Healer Agent [♦ I::IHealer ♦]                                 |                                                                                                                                  |   ||
+                              |                             |  |    -> [AUTH] SOLE AUTHORITY FOR PHYSICAL TOOL RETRIES           |                                                                                                                                  |   ||
+                              |                             |  |              & COMPUTE RECOVERY                                 |                                                                                                                                  |   ||
+                              |                             |  |    -> Validator Sub-Agent: PreCommitSnapshot, ProposedAction    |                                                                                                                                  |   ||
                               |                             |  |    -> [ROOT] CAPTURE ROOT CAUSE                                 |                                                                                                                                  |   ||
                               |                             |  |    -> [RESET] REVERT CLEAN STATE                                |                                                                                                                                  |   ||
                               |                             |  |    -> [PARSE] STACK TRACE / MACHINE FAILURE                     |                                                                                                                                  |   ||
                               |                             |  |    -> [PATCH] RECOMPILE SCRIPT                                  |                                                                                                                                  |   ||
-                              |                             |  |    -> [CURE] FIX AND RETRY OR ESCALATE TO L5                    |                                                                                                                                  |   ||
+                              |                             |  |    -> [CURE] FIX AND RETRY OR ESCALATE TO L3                    |                                                                                                                                  |   ||
                               |                             |  |         v                                                       |                                                                                                                                  |   ||
                               |                             |  |   [P4: SYNTHESIZER] (Pass)<--+                                  |                                                                                                                                  |   ||
                               |                             |  |    -> Aggregate Outputs, Validate Schema, Final Artifact        |                                                                                                                                  |   ||
@@ -180,15 +190,22 @@
               +----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+    ||
               | FINAL DECISION / OUTCOME LOGGING                                                                                                                                                                                                                   |    ||
               |----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|    ||
-              | - Outcome and state diffs are logged and versioned                                                                                                                                                                                                 |    ||
+              | - Outcome and state diffs are logged via ExecutionTrace contract (See Core Data Contracts below)                                                                                                                                                   |    ||
               | - [L1 UPDATE] FINAL ANSWER GENERATED USING ONLY STDOUT SUMMARY (Maintains PTC Context Isolation)                                                                                                                                                   |    ||
-              | - [SYNC] UPDATE SHARED TEAM MEMORY & ACTIVITY LEDGER (Non-blocking state update occurs only after L2.2 confirms)                                                                                                                                   |    ||
+              | - [SYNC] UPDATE SHARED TEAM MEMORY & ACTIVITY LEDGER (Mediated by Universal Write Gateway)                                                                                                                                                         |    ||
               | - [RECON] VERIFY DATA MATCHES REALITY (Detect ghost mutations across state layers)                                                                                                                                                                 |    ||
               | - Metrics captured: Execution Latency, Outcome Accuracy, Compute Cost, Human Correction Rate                                                                                                                                                       |    ||
               +----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+    ||
                                                                                        |                                                                                                                                                                                ||
                                                                                        +===(Commits Final State to Activity Ledger)====================================================================================================================================>||

+==============================================================================================================================================================================================================================================================================
+  CORE DATA CONTRACTS & CRYPTOGRAPHIC PRIMITIVES (ENFORCEABLE BOUNDARIES)
+==============================================================================================================================================================================================================================================================================
+| [1] InstructionPacket (L0 -> L2/L3/L5)  : [trace_id, policy_hash, route_mode, token_budget, allowed_tools[], signature(HMAC-SHA256)]                                                                                                                                       |
+| [2] SandboxEnvelope (L2 Entry)          : [trace_id, tool_id, sanitized_args, stdout_byte_limit, compute_ms_limit] (Filtered strictly by allowed_tools[])                                                                                                                  |
+| [3] ExecutionTrace (L6/L4 Audit)        : [trace_id, plan_hash, actor, target_resource, state_diff, timestamp, replay_key(Hash of trace+plan+transcript)] -> Append-only.                                                                                                  |
+| [4] HumanDecisionArtifact (Path D)      : [trace_id, policy_hash, reviewer_id, action:[APPROVE|MODIFY_DIFF|REJECT], reviewer_signature]                                                                                                                                    |
 ==============================================================================================================================================================================================================================================================================
   CRITICAL DISSEMINATION GUARANTEES
 ==============================================================================================================================================================================================================================================================================
@@ -207,4 +224,4 @@
 | 13. REMOVE ALL PROMPT HIJACK ATTEMPTS: Neutralizes "ignore instructions" attacks.                                                                                                                                                                                          |
 | 14. SHARE MEMORY ACROSS ALL AGENTS: Prevents agents from colliding/stalling.                                                                                                                                                                                               |
 | 15. DOUBLE-CHECK DATA MATCHES THE WORLD: Detects "ghost" or hidden mutations.                                                                                                                                                                                              |
-==============================================================================================================================================================================================================================================================================
+==============================================================================================================================================================================================================================================================================
\ No newline at end of file
diff --git a/tools/evidence/phase03_04_consolidated_evidence_runner.py b/tools/evidence/phase03_04_consolidated_evidence_runner.py
index 184b49fe3..4233aacaa 100644
--- a/tools/evidence/phase03_04_consolidated_evidence_runner.py
+++ b/tools/evidence/phase03_04_consolidated_evidence_runner.py
@@ -76,16 +76,30 @@ def main():
     evidence_lines.append("PENDING")
     evidence_lines.append("")

-    # CODE_SCOPE
-    evidence_lines.append("## CODE_SCOPE")
+    # FILES_CHANGED: derived from git show on CODE_COMMIT
+    rc, show_out, show_err = run_cmd(
+        ["git", "show", "--name-only", "--pretty=format:", code_commit], cwd=repo_root
+    )
+    changed_files = [f for f in show_out.strip().splitlines() if f.strip()]
+    evidence_lines.append("## FILES_CHANGED (in CODE_COMMIT)")
+    evidence_lines.append("```")
+    for f in changed_files:
+        evidence_lines.append(f)
+    evidence_lines.append("```")
+    evidence_lines.append("")
+
+    # INSPECTED_FILES: context files whose contents are embedded for verification
+    inspected = [
+        "tools/evidence/phase03_04_consolidated_evidence_runner.py",
+        "apps_lic/engines/__init__.py",
+        "apps_rg/engines/__init__.py",
+        "tests/unit_min_deps/test_apps_lic_spine_adapter.py",
+        "tests/unit_min_deps/test_apps_rg_spine_adapter.py",
+    ]
+    evidence_lines.append("## INSPECTED_FILES (context snapshots, not necessarily changed)")
     evidence_lines.append("```")
-    evidence_lines.append("Phase 3:")
-    evidence_lines.append("  tools/evidence/phase03_04_consolidated_evidence_runner.py")
-    evidence_lines.append("Phase 4:")
-    evidence_lines.append("  apps_lic/engines/__init__.py")
-    evidence_lines.append("  apps_rg/engines/__init__.py")
-    evidence_lines.append("  tests/unit_min_deps/test_apps_lic_spine_adapter.py")
-    evidence_lines.append("  tests/unit_min_deps/test_apps_rg_spine_adapter.py")
+    for f in inspected:
+        evidence_lines.append(f)
     evidence_lines.append("```")
     evidence_lines.append("")

@@ -101,10 +115,6 @@ def main():
         ),
         ([sys.executable, "-m", "pytest", "-q"], "Full Test Suite"),
         ([sys.executable, "ops_scripts/ci/check_spine_bypass.py"], "Spine Bypass Check"),
-        (
-            ["git", "show", "--name-only", "--pretty=format:", code_commit],
-            f"Files Changed in CODE_COMMIT ({code_commit[:8]})",
-        ),
         (["git", "diff", "--stat"], "Git Diff Stat"),
         (["git", "diff"], "Git Full Diff"),
     ]
@@ -126,16 +136,8 @@ def main():
         evidence_lines.append("```")
         evidence_lines.append("")

-    # File contents - dynamically determine which files were changed
-    files_to_include = [
-        "tools/evidence/phase03_04_consolidated_evidence_runner.py",
-        "apps_lic/engines/__init__.py",
-        "apps_rg/engines/__init__.py",
-        "tests/unit_min_deps/test_apps_lic_spine_adapter.py",
-        "tests/unit_min_deps/test_apps_rg_spine_adapter.py",
-    ]
-
-    for filepath in files_to_include:
+    # Inspected file contents (context snapshots for verification)
+    for filepath in inspected:
         full_path = repo_root / filepath
         if full_path.exists():
             evidence_lines.append(f"## {filepath}")
```

## tools/evidence/phase03_04_consolidated_evidence_runner.py
```python
#!/usr/bin/env python3
"""Phases 3-4 Consolidated Evidence Runner.

Single evidence file for entire Phases 3-4 run.
Python-only execution, argv-level PowerShell detection, LF endings.
"""

import subprocess
import sys
from pathlib import Path


def run_cmd(args, cwd=None):
    """Execute command and return (rc, stdout, stderr)."""
    # PowerShell detection at argv level only
    argv0_lower = str(args[0]).lower()
    if "pwsh" in argv0_lower or "powershell" in argv0_lower:
        print(f"ERROR: PowerShell usage detected in command: {' '.join(args)}")
        sys.exit(1)

    r = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, shell=False, encoding="utf-8", errors="replace"
    )
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
    """Generate Phases 3-4 consolidated evidence."""
    repo_root = Path(__file__).parent.parent.parent
    evidence_file = repo_root / "docs" / "reports" / "plans" / "phase_03_04_consolidated.md"

    print(f"Generating Phases 3-4 consolidated evidence: {evidence_file}")

    # Get CODE_COMMIT (current HEAD before evidence commit)
    rc, out, err = run_cmd(["git", "rev-parse", "HEAD"], cwd=repo_root)
    if rc != 0:
        print(f"ERROR: git rev-parse failed: {err}")
        sys.exit(1)
    code_commit = out.strip()

    # Start building evidence content
    evidence_lines = []

    # Header with scope
    evidence_lines.append("# Phases 3-4: Spine Adapter Production Closure (Consolidated)")
    evidence_lines.append("")
    evidence_lines.append("## Scope")
    evidence_lines.append("Phase 3: Single-evidence-per-response contract implementation")
    evidence_lines.append(
        "Phase 4: Production-grade spine adapter hardening (CID invariants, import stability, governance)"
    )
    evidence_lines.append("")

    # CODE_COMMIT (the commit containing actual code changes)
    evidence_lines.append("## CODE_COMMIT")
    evidence_lines.append(code_commit)
    evidence_lines.append("")

    # EVIDENCE_COMMIT (placeholder, will be filled after commit)
    evidence_lines.append("## EVIDENCE_COMMIT")
    evidence_lines.append("PENDING")
    evidence_lines.append("")

    # FILES_CHANGED: derived from git show on CODE_COMMIT
    rc, show_out, show_err = run_cmd(
        ["git", "show", "--name-only", "--pretty=format:", code_commit], cwd=repo_root
    )
    changed_files = [f for f in show_out.strip().splitlines() if f.strip()]
    evidence_lines.append("## FILES_CHANGED (in CODE_COMMIT)")
    evidence_lines.append("```")
    for f in changed_files:
        evidence_lines.append(f)
    evidence_lines.append("```")
    evidence_lines.append("")

    # INSPECTED_FILES: context files whose contents are embedded for verification
    inspected = [
        "tools/evidence/phase03_04_consolidated_evidence_runner.py",
        "apps_lic/engines/__init__.py",
        "apps_rg/engines/__init__.py",
        "tests/unit_min_deps/test_apps_lic_spine_adapter.py",
        "tests/unit_min_deps/test_apps_rg_spine_adapter.py",
    ]
    evidence_lines.append("## INSPECTED_FILES (context snapshots, not necessarily changed)")
    evidence_lines.append("```")
    for f in inspected:
        evidence_lines.append(f)
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
        evidence_lines.append(f"$ {' '.join(cmd)}")
        rc, out, err = run_cmd(cmd, cwd=repo_root)
        if rc != 0:
            print(f"WARNING: Command failed: {' '.join(cmd)}")
            print(f"Exit code: {rc}")
            print(f"Stderr: {err}")
            # Don't exit on test failures, capture them in evidence

        evidence_lines.append(out.strip() if out else "(no output)")
        if err:
            evidence_lines.append(f"STDERR: {err.strip()}")
        evidence_lines.append("```")
        evidence_lines.append("")

    # Inspected file contents (context snapshots for verification)
    for filepath in inspected:
        full_path = repo_root / filepath
        if full_path.exists():
            evidence_lines.append(f"## {filepath}")
            evidence_lines.append("```python")
            content = read_file_content(full_path)
            evidence_lines.append(content)
            evidence_lines.append("```")
            evidence_lines.append("")

    # Write evidence file with LF line endings and no trailing whitespace
    evidence_content = "\n".join(line.rstrip() for line in evidence_lines)
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(evidence_content, encoding="utf-8", newline="\n")

    print(f"Evidence generated successfully: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    print("EVIDENCE_COMMIT: PENDING (will be filled after commit)")


if __name__ == "__main__":
    main()
```

## apps_lic/engines/__init__.py
```python
"""apps_lic/engines/__init__.py — Sovereign Engine Registry.

Only canonical executors are eagerly imported. All other agents remain
importable directly from their modules, e.g.:
    from apps_lic.engines.DeliverabilityAgent import DeliverabilityAgent
    from apps_lic.engines.OutreachSignalRouterAgent import OutreachSignalRouterAgent
"""

try:
    from apps_lic.enforcement.ExecutiveStrategyAgent import (
        ExecutiveStrategyAgent,
        get_exec_interviewer_profile,
        get_exec_shadow_audit,
        get_exec_strategy_roadmap,
    )
except ImportError:
    ExecutiveStrategyAgent = None  # type: ignore[assignment,misc]
    get_exec_interviewer_profile = None  # type: ignore[assignment]
    get_exec_shadow_audit = None  # type: ignore[assignment]
    get_exec_strategy_roadmap = None  # type: ignore[assignment]

try:
    from apps_lic.reasoning.HOPPipelineExecutor import HOPPipelineExecutor
except ImportError:
    HOPPipelineExecutor = None  # type: ignore[assignment,misc]

try:
    from apps_lic.reasoning.LICValidationExecutor import LICValidationExecutor
except ImportError:
    LICValidationExecutor = None  # type: ignore[assignment,misc]

try:
    from apps_lic.reasoning.OutreachMessageAgent import OutreachMessageAgent
except ImportError:
    OutreachMessageAgent = None  # type: ignore[assignment,misc]

__all__ = [
    "ExecutiveStrategyAgent",
    "get_exec_shadow_audit",
    "get_exec_strategy_roadmap",
    "get_exec_interviewer_profile",
    "HOPPipelineExecutor",
    "LICValidationExecutor",
    "OutreachMessageAgent",
]
```

## apps_rg/engines/__init__.py
```python
"""apps_rg/engines/__init__.py — Sovereign Engine Registry.

Only canonical executors are eagerly imported. All other agents remain
importable directly from their modules, e.g.:
    from apps_rg.engines.RGValidationExecutor import RGValidationExecutor
    from apps_rg.reasoning.ATSCompatibilityAgent import ATSCompatibilityAgent
"""

# No eager imports - all modules imported directly to avoid import errors

__all__ = []
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
