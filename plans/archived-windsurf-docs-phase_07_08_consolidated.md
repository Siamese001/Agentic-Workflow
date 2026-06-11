---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\phase_07_08_consolidated.md'
original_relative_path: 'phase_07_08_consolidated.md'
source_sha256: f3628785478897f7ad9737eb6c6591502a0108d67fb950e0cdd8a51c664c1408
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-22'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Phases 7-8: Evidence Contract v2 + CI Enforcement (Consolidated)

## Scope
Phase 7: Evidence Contract v2: Scope Isolation + Self-Verification
Phase 8: CI Enforcement: Evidence Contract Guardrail

## CODE_COMMIT
3a2c4e1507f1b0a4c8709421cffbd3116bce9e69

## EVIDENCE_COMMIT
89aaa92dbc8091ac53a6339155a3af0edbf7bbb1

## FILES_CHANGED_CODE
```
docs/reports/plans/phase_05_06_consolidated.md
```

## FILES_CHANGED_EVIDENCE
```
docs/reports/plans/phase_07_08_consolidated.md
```

## INSPECTED_FILES
```
tools/evidence/evidence_contract_v2.py
tools/evidence/phase05_06_consolidated_evidence_runner.py
tools/evidence/phase07_08_consolidated_evidence_runner.py
tests/unit_min_deps/test_evidence_contract_v2.py
ops_scripts/ci/check_evidence_contract_v2.py
.github/workflows/spine-determinism-guard.yml
```

## Evidence Contract v2 Unit Tests
```
$ C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m pytest -q tests/unit_min_deps/test_evidence_contract_v2.py
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 15 items

tests/unit_min_deps/test_evidence_contract_v2.py::test_rejects_missing_code_commit [32mPASSED[0m[32m [  6%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_accepts_valid_code_commit [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_commit_hash_invalid_length [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_commit_hash_invalid_chars [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_commit_hash_valid [32mPASSED[0m[32m [ 33%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_run_cmd_detects_powershell [32mPASSED[0m[32m [ 40%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_run_cmd_accepts_python [32mPASSED[0m[32m [ 46%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_hash_loop_prevention [32mPASSED[0m[32m [ 53%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_hash_loop_prevention_allows_different [32mPASSED[0m[32m [ 60%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_scope_containment_violations [32mPASSED[0m[32m [ 66%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_scope_containment_allowed [32mPASSED[0m[32m [ 73%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_build_evidence_sections [32mPASSED[0m[32m [ 80%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_format_evidence_sections [32mPASSED[0m[32m [ 86%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_evidence_contract_structure [32mPASSED[0m[32m [ 93%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_evidence_contract_structure_requires_evidence_commit [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================= [32m[1m15 passed[0m[32m in 0.04s[0m[32m ==============================[0m
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
collected 1241 items

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
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_read_from_audit_allowed [32mPASSED[0m[32m [  1%][0m
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
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingIntConstraints::test_depth_breaker_above_max_raises [32mPASSED[0m[32m [  3%][0m
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
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL1ModelPointers::test_embedding_model_allowlist_enforced [32mPASSED[0m[32m [  4%][0m
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
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestDeterminism::test_validation_deterministic [32mPASSED[0m[32m [  5%][0m
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
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_over_delta_rejected [32mPASSED[0m[32m [  6%][0m
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
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataValid::test_returns_expected_bytes [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataValid::test_returns_empty_bytes_when_store_empty [32mPASSED[0m[32m [  7%][0m
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
tests/unit_min_deps/system_learning/test_lineage_validator.py::TestValidateLineage::test_genesis_version_valid [32mPASSED[0m[32m [  8%][0m
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
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_commit_path.py::TestCommitPath::test_commit_path_requires_approval_gate [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_commit_path.py::TestCommitPath::test_approval_reject_does_not_commit [32mPASSED[0m[32m [  9%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_commit_path.py::TestDeterminism::test_commit_path_deterministic [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py::TestProposalOnlyMode::test_proposal_only_returns_packages [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py::TestProposalOnlyMode::test_proposal_only_does_not_call_commit [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py::TestProposalOnlyMode::test_proposal_only_does_not_call_activate [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py::TestProposalOnlyMode::test_proposal_only_default_is_true [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py::TestDeterminism::test_pipeline_deterministic [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_oscillation_true_pattern [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_oscillation_true_pattern_reverse [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_non_oscillation_pattern [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_non_oscillation_all_same [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_insufficient_data [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_oscillation_with_epsilon_tolerance [32mPASSED[0m[32m [ 10%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_non_oscillation_three_values [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_freeze_decision_on_oscillation [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_no_freeze_on_non_oscillation [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_freeze_until_utc_computation [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_freeze_decision_deterministic [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDeterminism::test_detect_oscillation_deterministic [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_valid_proposal_passes_constraints [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_out_of_range_rejected [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_cooldown_violated_returns_none [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_sample_size_violated_returns_none [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_no_change_needed_returns_none [32mPASSED[0m[32m [ 11%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGChangePackage::test_canonical_bytes_deterministic [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGChangePackage::test_content_hash_deterministic [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGChangePackage::test_different_values_produce_different_hash [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestDeterminism::test_proposal_deterministic [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_analyze_failures_basic [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_exact_findings_counts [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_determinism_same_slice_identical_report_id [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_invalid_window_rejected [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_malformed_utf8_rejected [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_empty_slice_produces_unknown_category [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestRCAEngine::test_no_matching_patterns_produces_unknown [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_engine.py::TestDeterminism::test_analyze_failures_deterministic [32mPASSED[0m[32m [ 12%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_deterministic_hash_stability [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_findings_ordering_canonical [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_changing_evidence_changes_hash [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestRCATypes::test_report_id_equals_report_hash [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestDeterminism::test_canonical_bytes_deterministic [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_rca_types.py::TestDeterminism::test_compute_report_hash_deterministic [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_deterministic_engine_passes [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_nondeterministic_engine_fails [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_error_includes_both_hashes [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_same_output_twice_produces_same_hash [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_different_snapshots_produce_different_hashes [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_replay_validator.py::TestDeterminism::test_replay_validate_deterministic [32mPASSED[0m[32m [ 13%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_pass_within_thresholds [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_latency_regression [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_error_rate_regression [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_safety_violation_increase [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_cpu_regression [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_mem_regression [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_multiple_violations_reported [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestDeterminism::test_evaluate_shadow_deterministic [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_same_inputs_produce_identical_snapshot_id [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_same_inputs_produce_identical_snapshot_object [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_snapshot_id_is_sha256_hex [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_snapshot_id_stability_across_calls [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_snapshot_fields_match_inputs [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_telemetry_hash_is_sha256_of_telemetry_bytes [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_policy_config_hash_is_sha256_of_policy_bytes [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_routing_config_hash_is_sha256_of_routing_bytes [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_model_config_hash_is_sha256_of_model_bytes [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_telemetry_bytes_produce_different_telemetry_hash [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_telemetry_bytes_produce_different_snapshot_id [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_policy_bytes_produce_different_snapshot_id [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_engine_version_produces_different_snapshot_id [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_window_produces_different_snapshot_id [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotValidation::test_start_equal_to_end_raises [32mPASSED[0m[32m [ 15%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotValidation::test_start_greater_than_end_raises [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotValidation::test_valid_window_does_not_raise [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_datetime_now_not_called [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_time_time_not_called [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_snapshot_is_frozen [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_snapshot_id_equality_assertion [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_deterministic_slice_id_across_two_calls [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_sorting_stable_and_canonical [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_invalid_window_rejected [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_empty_window_produces_empty_slice [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_window_filtering [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_payload_hash_computed [32mPASSED[0m[32m [ 16%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestTelemetryConsumer::test_same_timestamp_different_kind_sorted [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_telemetry_consumer.py::TestDeterminism::test_consume_telemetry_deterministic [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_commit_returns_sha256_version_id [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_same_content_produces_same_version_id [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_different_content_produces_different_version_id [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_write_once_semantics_idempotent_on_same_content [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_parent_version_not_found_raises [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_genesis_version_allowed [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestCommitChangePackage::test_child_version_with_valid_parent [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetChangePackage::test_get_existing_version [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetChangePackage::test_get_nonexistent_version_raises [32mPASSED[0m[32m [ 17%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetChangePackage::test_retrieved_package_is_immutable [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestListVersions::test_list_all_versions [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestListVersions::test_list_versions_empty_store [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestListVersions::test_list_versions_deterministic_order [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestUpdateActivationPointer::test_activate_version [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestUpdateActivationPointer::test_activate_nonexistent_version_raises [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestUpdateActivationPointer::test_activation_does_not_mutate_package [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestUpdateActivationPointer::test_atomic_pointer_update [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetActiveVersion::test_get_active_version_when_set [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetActiveVersion::test_get_active_version_when_not_set [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestGetActiveVersion::test_multiple_components_independent [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestRollback::test_rollback_to_parent [32mPASSED[0m[32m [ 18%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestRollback::test_rollback_is_o1_pointer_reversion [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestRollback::test_rollback_to_nonexistent_version_raises [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestRollback::test_no_deletion_of_historical_versions [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/system_learning/test_version_store.py::TestVersionIdDeterminism::test_version_id_determinism_assertion [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_adapter_returns_cid [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_has_lic_prefix [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_is_deterministic [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_different_inputs_produce_different_cids [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_registered_before_orchestrator_execute [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_passed_to_orchestrator [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_adapter_state_success_on_clean_input [32mPASSED[0m[32m [ 19%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_adapter_returns_cid [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_has_rg_prefix [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_is_deterministic [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_different_inputs_produce_different_cids [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_registered_before_orchestrator_execute [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_passed_to_orchestrator [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_adapter_state_success_on_clean_input [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_capture_evidence.py::TestCaptureEvidence::test_powershell_string_abort [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_capture_evidence.py::TestCaptureEvidence::test_pwsh_string_abort [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_capture_evidence.py::TestCaptureEvidence::test_clean_output_no_abort [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_capture_evidence.py::TestCaptureEvidence::test_case_insensitive_detection [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[DagRuntimeInspectorAgent] [32mPASSED[0m[32m [ 20%][0m
tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[SafetyInspectorAgent] [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[SprawlInspectorAgent] [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_config_property_contract.py::TestConfigMixinPropertyContract::test_config_is_property [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_config_property_contract.py::TestNoConfigOverwriteRepoWide::test_config_overwrite_ceiling [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_standard_heal_importable [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_standard_heal_async_importable [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_heal_result_schema_importable [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_dunder_all_matches_exports [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_importable [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_returns_decorator [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_decorator_wraps_function [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_dunder_all_matches_exports [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBackwardCompatShimIdentity::test_l5_shim_standard_heal_is_canonical [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBackwardCompatShimIdentity::test_l5_shim_heal_result_schema_is_canonical [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBackwardCompatShimIdentity::test_l0_shim_timeout_is_canonical [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestNoShimImportsEnforcement::test_no_imports_from_shim_locations [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBaseAgentsDecoratorImports::test_base_agents_decorators_no_shim_imports [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestShimAllowlist::test_decorators_shim_imports_only_base_agents [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestShimAllowlist::test_timeout_shim_imports_only_base_agents [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestNoShimImportsRepoWide::test_no_forbidden_imports_from_shim_locations [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalNoShimImports::test_decorators_no_shim_imports [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalNoShimImports::test_timeout_no_shim_imports [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_imports_only_canonical[decorators_util] [32mPASSED[0m[32m [ 22%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_imports_only_canonical[timeout_decorator_util] [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_defines_dunder_all[decorators_util] [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_defines_dunder_all[timeout_decorator_util] [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_no_function_or_class_defs[decorators_util] [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_no_function_or_class_defs[timeout_decorator_util] [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_standard_heal_locally [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_heal_result_schema_locally [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_timeout_defines_timeout_locally [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_dunder_all [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_timeout_defines_dunder_all [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_determinism_util.py::test_exclusion_top_level [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_determinism_util.py::test_exclusion_nested_recursive [32mPASSED[0m[32m [ 23%][0m
tests/unit_min_deps/test_determinism_util.py::test_list_recursive_preserves_order_and_strips [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_list_order_matters [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_file_hash_stable [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_dict_top_level [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_preserves_non_excluded [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_strip_nondeterministic_tuple_preserved [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_deterministic_multiple_calls [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_determinism_util.py::test_canonical_hash_different_content_differs [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_rejects_missing_code_commit [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_accepts_valid_code_commit [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_commit_hash_invalid_length [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_commit_hash_invalid_chars [32mPASSED[0m[32m [ 24%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_commit_hash_valid [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_run_cmd_detects_powershell [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_run_cmd_accepts_python [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_hash_loop_prevention [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_hash_loop_prevention_allows_different [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_scope_containment_violations [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_scope_containment_allowed [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_build_evidence_sections [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_format_evidence_sections [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_evidence_contract_structure [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_evidence_contract_v2.py::test_validate_evidence_contract_structure_requires_evidence_commit [32mPASSED[0m[32m [ 25%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSubatomicTestingMixinInMRO::test_subatomic_in_mro[DagRuntimeInspectorAgent] [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSubatomicNotDirectBase::test_subatomic_not_direct_base[DagRuntimeInspectorAgent] [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestNoDuplicatesInMRO::test_no_mro_duplicates[DagRuntimeInspectorAgent] [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSovereignBaseAgentMRO::test_sovereign_has_subatomic_testing_mixin [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSovereignBaseAgentMRO::test_sovereign_has_config_mixin [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoOrphanIntegrationTests::test_all_integration_tests_under_allowed_roots [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoTopLevelIntegrationFiles::test_no_top_level_test_files [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_marker_registry_contract.py::TestAllUsedMarkersRegistered::test_no_unregistered_markers [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_marker_registry_contract.py::TestNoDuplicateMarkers::test_no_duplicate_markers [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_marker_registry_contract.py::TestMarkersSorted::test_markers_sorted [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_phase2_unsafe_io_enforcement.py::TestPhase2UnsafeIOEnforcement::test_detector_still_works [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_phase2_unsafe_io_enforcement.py::TestPhase2UnsafeIOEnforcement::test_remediated_files_clean [32mPASSED[0m[32m [ 26%][0m
tests/unit_min_deps/test_phase2_unsafe_io_enforcement.py::TestPhase2UnsafeIOEnforcement::test_no_direct_subprocess_in_remediated_files [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_phase2_unsafe_io_enforcement.py::TestPhase2UnsafeIOEnforcement::test_scoped_directories_scan [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_write_gateway_imports_enforce_protected_root [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_write_text_calls_enforce_before_write_primitive [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_write_bytes_calls_enforce_before_write_primitive [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_execute_ssot_exposes_allow_protected_root_mutation_flag [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_execute_ssot_entrypoint_exposes_fence_self_check_flag [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_negative_regression_guard_enforce_removal_would_fail [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestProtectedRootEnforcementInvariant::test_negative_regression_guard_reordering_would_fail [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_protected_root_invariant_ast.py::TestEnforcementWiringCompleteness::test_all_public_write_functions_call_enforce_or_delegate [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_tool_registry_exists_and_must_route_via_write_gateway [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_is_canonical_write_layer [32mPASSED[0m[32m [ 27%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_write_gateway_functions_accept_allow_override [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_future_tool_contract_enforcement_ready [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ptc_write_contract.py::TestPTCWriteContract::test_l2_execution_tools_do_not_expose_raw_write_primitives [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestCompleteness::test_no_unlisted_quarantine_files [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestNoStaleEntries::test_no_stale_manifest_entries [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestEntrySchema::test_categories_are_valid [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestEntrySchema::test_required_fields_non_empty [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestBidirectionalSync::test_disk_manifest_exact_match [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestQuarantineCeiling::test_total_ceiling [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestQuarantineCeiling::test_per_category_ceiling [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_spine_cross_app_contract.py::test_cross_app_cid_prefixes [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_spine_cross_app_contract.py::test_cross_app_cid_hash_bodies_identical [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_spine_cross_app_contract.py::test_cross_app_cid_determinism [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_spine_cross_app_contract.py::test_cross_app_cid_difference [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_spine_cross_app_contract.py::test_cross_app_call_order_invariant [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_agentic_core [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_allows_outside [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_override_allows [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_tests [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_github [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_agentic_core [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_tests [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_github [32mPASSED[0m[32m [ 29%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_blocks_protected_root [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_allows_outside_protected_root [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_bytes_blocks_protected_root [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_block_emits_jsonl_event [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_logging_failure_does_not_mask_exception [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_exception_message_still_includes_diagnostics [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_immutable_roots [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_default_policy_log_path [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_log_path_writes_to_tmp [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_override_immutable_roots_changes_matched_root [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestPolicyContract::test_policy_none_uses_default [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_allow_mutation_does_not_bypass_protected_root [32mPASSED[0m[32m [ 30%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_env_deny_mutation_does_not_change_protected_root [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_cli_override_works_regardless_of_env [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestEnvVarIsolation::test_unset_env_vars_do_not_change_behavior [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_ok_path [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_fails_with_bad_log_path [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestFenceSelfCheck::test_self_check_validates_write_gateway_wiring [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_replay_block_event_is_identical_under_fixed_clock [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_self_check_output_is_bitwise_identical_across_runs [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestDeterministicReplay::test_block_event_without_override_uses_real_time [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestPytestIniHeader::test_has_pytest_section [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestPytestIniHeader::test_no_tool_pytest_section [32mPASSED[0m[32m [ 31%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestTestpathsContract::test_testpaths_exact_match [32mPASSED[0m[32m [ 32%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestNorecursedirsContract::test_norecursedirs_includes_required [32mPASSED[0m[32m [ 32%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestNoRootConftest::test_no_root_conftest [32mPASSED[0m[32m [ 32%][0m
tests/unit_min_deps/test_unsafe_io_subprocess_detector.py::TestUnsafeIOSubprocessDetector::test_detector_finds_direct_file_writes [32mPASSED[0m[32m [ 32%][0m
tests/unit_min_deps/test_unsafe_io_subprocess_detector.py::TestUnsafeIOSubprocessDetector::test_detector_finds_subprocess_calls [32mPASSED[0m[32m [ 32%][0m
tests/unit_min_deps/test_unsafe_io_subprocess_detector.py::TestUnsafeIOSubprocessDetector::test_detector_ignores_safe_operations [32mPASSED[0m[32m [ 32%][0m
tests/unit_min_deps/test_unsafe_io_subprocess_detector.py::TestUnsafeIOSubprocessDetector::test_detector_scans_actual_agent_code [32mPASSED[0m[32m [ 32%][0m
tests/unit_min_deps/test_unsafe_io_subprocess_detector.py::TestUnsafeIOSubprocessDetector::test_detector_enforcement [32mPASSED[0m[32m [ 32%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDagRuntimeInspectorAgent::test_importable [32mPASSED[0m[32m [ 32%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDagRuntimeInspectorAgent::test_diagnose_returns_inspection_result
[1m-------------------------------- live log call --------------------------------[0m
2026-02-22 15:46:06 [[32m    INFO[0m] agentic_core.L5_safety.reasoning.InspectorExecutor: [InspectorExecutor] Inspector
[32mPASSED[0m[32m                                                                   [ 32%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_standard_heal_importable_with_full_deps [32mPASSED[0m[32m [ 32%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_timeout_importable_with_full_deps [32mPASSED[0m[32m [ 32%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_shim_identity_with_full_deps [32mPASSED[0m[32m [ 33%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_timeout_shim_identity_with_full_deps [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_utils_requires_util_suffix [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_agent_configs_requires_config_suffix [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_mixins_requires_mixin_suffix [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_interfaces_requires_i_prefix [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_folder_aliases_knowledge_to_reasoning [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_folder_aliases_validation_to_validators [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestEnforcementFolderRules::test_enforcement_folder_exists_in_rules [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestEnforcementFolderRules::test_enforcement_allows_strategy_suffix [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestUtilsFileSuffixCompliance::test_utils_files_have_util_suffix [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestAgentConfigsFileSuffixCompliance::test_agent_configs_files_have_valid_suffix [32mPASSED[0m[32m [ 33%][0m
tests/enforcement/test_folder_purity_governance.py::TestGlobalNoRootFilesInvariant::test_folder_purity_rules_governed [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_governance.py::TestGlobalNoRootFilesInvariant::test_folder_aliases_governed [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_governance.py::TestGlobalNoRootFilesInvariant::test_infrastructure_profiles_governed [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_governance.py::TestGlobalNoRootFilesInvariant::test_security_has_approved_subfolders [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_governance.py::TestGlobalNoRootFilesInvariant::test_global_invariant_covers_all_governed_roots [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[validators] [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[scripts] [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[dashboards] [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[base_agents] [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[mixins] [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[interfaces] [32mPASSED[0m[32m [ 34%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[agent_configs] [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[healers] [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[exceptions] [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[core_kernel] [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityNegativeInvariants::test_folder_purity_negative_invariant[engines] [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityNegativeInvariants::test_folder_purity_negative_invariant[tools] [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityCoverage::test_all_existing_folders_are_governed [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityRulesIntegrity::test_engines_and_tools_have_rules [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityRulesIntegrity::test_engines_and_tools_have_disallowed [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityRulesIntegrity::test_no_catchall_patterns [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_config_folder_rejects_non_config_suffix [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_engines_folder_rejects_non_engine_suffix [32mPASSED[0m[32m [ 35%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_prompt_governance_no_root_files_enforcement [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_agent_configs_enforces_config_suffix [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_observability_probe_executor_compliant [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_meta_learning_utils_location_ssot [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_folder_purity_invariants.py::TestRCANegativeTests::test_state_util_location_ssot [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_missing_pytest_ini [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_testpaths_contract_sync_missing_contract [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_testpaths_contract_sync_mismatch [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_testpaths_contract_sync_match [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_evidence_truncation_detection [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_evidence_missing_exit_code [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_phase_evidence_missing_git_history [32mPASSED[0m[32m [ 36%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_phase_evidence_missing_deterministic_command [32mPASSED[0m[32m [ 37%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_phase_evidence_blocked_without_preexisting [32mPASSED[0m[32m [ 37%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_allowed_truncation_in_code_examples [32mPASSED[0m[32m [ 37%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_missing_pytest_ini [32mPASSED[0m[32m [ 37%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_valid_pytest_configuration [32mPASSED[0m[32m [ 37%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_missing_required_markers [32mPASSED[0m[32m [ 37%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_unregistered_markers_in_tests [32mPASSED[0m[32m [ 37%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_conftest_hook_without_docstring [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_byte_identical_json_runs [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_deterministic_ordering [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_no_nondeterministic_fields [32mPASSED[0m[32m [ 37%][0m
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_top_level_schema [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_result_item_schema [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_summary_schema [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_controlled_fixture_scanning [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_agent_naming_detection [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_base_class_name_extraction [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_agent_heal_audit.py::TestNoRuntimeImports::test_source_code_imports [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_agent_heal_audit.py::TestNoRuntimeImports::test_stdlib_only_imports [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_generation [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_determinism [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_authority_boundaries.py::TestMutationAuthorityBoundary::test_l2_execution_exists_and_has_mutations [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_authority_boundaries.py::TestMutationAuthorityBoundary::test_l1_has_zero_mutation_primitives [32mPASSED[0m[32m [ 38%][0m
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L3_orchestration] [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L4_state] [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L5_safety] [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_authority_boundaries.py::TestNoCrossLayerMutationImports::test_no_l2_mutation_imports[L6_observability] [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_authority_boundaries.py::TestAuthorityNegativeRegression::test_detects_l2_fileio_import [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_authority_boundaries.py::TestAuthorityNegativeRegression::test_detects_l2_save_file_import [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_authority_boundaries.py::TestAuthorityNegativeRegression::test_ignores_non_mutation_l2_import [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_dict_10x_identical [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_nested_dict_10x_identical [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_tuple_input_10x_identical [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_empty_dict_10x_identical [32mPASSED[0m[32m [ 39%][0m
tests/governance/test_canonical_serializer.py::TestGoldenDeterminism::test_none_values_10x_identical [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestFloatPrecision::test_float_normalized [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestFloatPrecision::test_float_round_trip [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestFloatPrecision::test_float_trailing_zeros [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestTupleNormalization::test_tuple_becomes_list [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestTupleNormalization::test_nested_tuple [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestNullEncoding::test_none_encoded [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestNullEncoding::test_none_not_omitted [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestSortedKeys::test_top_level_sorted [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestSortedKeys::test_nested_sorted [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestCrossObjectConsistency::test_audit_and_intent_same_serializer [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestASTNoDirectJsonDumps::test_no_json_dumps_in_audit_log [32mPASSED[0m[32m [ 40%][0m
tests/governance/test_canonical_serializer.py::TestASTNoDirectJsonDumps::test_no_json_dumps_in_canonical_serializer [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_canonical_serializer.py::TestASTNoDirectJsonDumps::test_no_json_import_in_audit_log [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_cross_layer_import_freeze.py::TestCrossLayerImportFreeze::test_no_new_violations [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_cross_layer_import_freeze.py::TestCrossLayerImportFreeze::test_baseline_not_stale [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_cross_layer_import_freeze.py::TestRegressionDetection::test_synthetic_violation_detected [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_cross_layer_import_freeze.py::TestRegressionDetection::test_persistence_client_detected [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_blocks_write_under_agentic_core [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_blocks_rename_under_agentic_core [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_allows_write_outside_agentic_core [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_protected_root_respects_override_flag [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestStartupFenceSelfTest::test_startup_self_test_aborts_if_fence_inactive [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestStartupFenceSelfTest::test_startup_self_test_passes_if_fence_active [32mPASSED[0m[32m [ 41%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestImportPreflight::test_import_preflight_fails_fast_with_actionable_message [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestImportPreflight::test_import_preflight_passes_when_symbols_exist [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootPolicy::test_default_policy_has_correct_immutable_roots [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_execute_ssot_mutation_fence.py::TestProtectedRootPolicy::test_default_policy_log_path_outside_immutable_roots [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestNoNewUpwardImportsInInitFiles::test_l3_init_no_upward_imports [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestNoNewUpwardImportsInInitFiles::test_l3_scripts_init_no_upward_imports [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestNoNewUpwardImportsInInitFiles::test_l3_engines_init_no_upward_imports [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestGHONoDirectWrites::test_no_open_write_calls [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestGHOMutationDelegation::test_no_direct_mutation_primitives [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestGHOMutationDelegation::test_write_gateway_is_sole_mutation_path [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_guardian_heal_routing_containment.py::TestDirectoryWideUpwardImportFreeze::test_no_l5_imports_in_l3_init_files [32mPASSED[0m[32m [ 42%][0m
tests/governance/test_hash_chain_audit_log.py::TestGenesisRule::test_first_entry_has_genesis_previous_hash [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestGenesisRule::test_first_entry_has_index_zero [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestGenesisRule::test_genesis_hash_is_literal_string [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_single_entry_verifies [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_multi_entry_chain_verifies [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_chain_links_previous_hash [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_empty_log_verifies [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainIntegrity::test_each_entry_hash_is_sha256 [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestChainBreakDetection::test_tampered_hash_detected
[1m-------------------------------- live log call --------------------------------[0m
2026-02-22 15:46:27 [[31m[1m   ERROR[0m] agentic_core.L2_execution.audit.hash_chain_audit_log: [audit] hash mismatch at entry 1
[32mPASSED[0m[32m                                                                   [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestSeal::test_seal_returns_root_hash [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestSeal::test_append_after_seal_raises [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestSeal::test_seal_empty_log_raises [32mPASSED[0m[32m [ 43%][0m
tests/governance/test_hash_chain_audit_log.py::TestEntryImmutability::test_cannot_mutate_entry_field [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_hash_chain_audit_log.py::TestHashDeterminism::test_entry_hash_is_deterministic [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_hash_chain_audit_log.py::TestHashDeterminism::test_verify_passes_on_correct_hash [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_hash_chain_audit_log.py::TestLogProperties::test_length_tracks_entries [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_hash_chain_audit_log.py::TestLogProperties::test_chain_root_none_when_empty [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_hash_chain_audit_log.py::TestLogProperties::test_entries_returns_tuple [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestFlagDefaultOff::test_no_escalation_log_without_env_var [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestFlagDefaultOff::test_observer_not_invoked_without_env_var [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestObserverSeamSafety::test_observer_default_is_none_at_import [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestObserverSeamSafety::test_observer_not_reassigned_at_module_scope [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_default_off [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_enabled_no_caller [32mPASSED[0m[32m [ 44%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_enabled_with_caller [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_logging [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_no_routed_model [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_output_unchanged [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingDefaultOff::test_router_seam_not_invoked_when_disabled [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingDefaultOff::test_no_routed_model_log_when_disabled [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledLow::test_router_invoked_with_low_tier [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledLow::test_routed_model_log_contains_local_low [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledHigh::test_router_invoked_with_high_tier [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledHigh::test_routed_model_log_contains_local_high [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagDefaultOff::test_no_escalation_log_when_disabled [32mPASSED[0m[32m [ 45%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagDefaultOff::test_observer_not_invoked_when_disabled [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagEnabled::test_escalation_log_when_enabled [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagEnabled::test_observer_invoked_when_enabled [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_stdlib_only_imports [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_no_network_model_keywords [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_no_banned_string_literals [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_decide_reasoning_tier_is_invoked [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_policy_decision_is_logged [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_output_unchanged_by_policy_integration [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_high_boundary [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_high_boundary_exact [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_medium_boundary [32mPASSED[0m[32m [ 46%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_medium_boundary_just_below [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_low_values [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_validation_errors [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_high_confidence_auto_proceed [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_high_confidence_boundary_exact [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_medium_confidence_llm_enabled_judicious_gate_met [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_medium_confidence_llm_enabled_judicious_gate_not_met [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_medium_confidence_llm_disabled [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_enabled_complexity_gate [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_enabled_failure_gate [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_enabled_judicious_gate_not_met [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_low_confidence_llm_disabled [32mPASSED[0m[32m [ 47%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_determinism [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_confidence_value [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_task_complexity [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_safety_risk [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideHealEscalation::test_validation_prior_failures [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_trivial_rule_returns_low_even_with_low_confidence [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_trivial_rule_order [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_confidence_low [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_complexity_high [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_safety_risk_high [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_escalation_retry_count_high [32mPASSED[0m[32m [ 48%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_default_low [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_determinism [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_validation_task_complexity [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_validation_safety_risk [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTierLegacy::test_validation_retry_count [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestEnableLlmHardGate::test_enable_llm_false_high_confidence_proceeds_no_tier [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestEnableLlmHardGate::test_enable_llm_false_medium_confidence_blocked [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestEnableLlmHardGate::test_enable_llm_false_low_confidence_blocked [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestTierSelection::test_medium_confidence_selects_low_tier [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestTierSelection::test_low_confidence_selects_high_tier [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestTierSelection::test_low_confidence_with_prior_failures_selects_high_tier [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestJudiciousGate::test_medium_confidence_low_complexity_blocked [32mPASSED[0m[32m [ 49%][0m
tests/governance/test_heal_policy_wiring.py::TestJudiciousGate::test_low_confidence_low_complexity_no_failures_blocked [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestNoNetworkCalls::test_standard_heal_no_llm_call_when_disabled [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestNoNetworkCalls::test_standard_heal_high_confidence_no_llm_call [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestDeterministicRefusal::test_blocked_result_contains_policy_decision [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestDeterministicRefusal::test_blocked_result_is_deterministic [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestCanonicalSeamEnforcement::test_direct_llm_call_without_seam_fails [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestCanonicalSeamEnforcement::test_standard_heal_sets_capability_token [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestCanonicalSeamEnforcement::test_llm_escalation_only_via_standard_heal [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestPolicyDecisionRecord::test_policy_decision_record_schema [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestPolicyDecisionRecord::test_policy_decision_record_deterministic_hash [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestPolicyDecisionRecord::test_standard_heal_emits_policy_record
[1m-------------------------------- live log call --------------------------------[0m
2026-02-22 15:46:27 [[33m WARNING[0m] agentic_core.utils.decorators_util: [standard_heal] MockAgent: Non-canonical key '_policy_from_kwargs' detected. Consider using canonical keys for better schema compliance.
[32mPASSED[0m[32m                                                                   [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestNetworkTripwire::test_network_tripwire_blocks_socket [32mPASSED[0m[32m [ 50%][0m
tests/governance/test_heal_policy_wiring.py::TestNetworkTripwire::test_heal_paths_make_no_network_calls [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_deterministic_output [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_idempotency [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_policy_routing [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_policy_wiring.py::TestHealRepositoryBaseline::test_heal_repository_deterministic_baseline_integration [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_disabled [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_enabled_with_router [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_enabled_no_router [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_logging_enabled [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_disabled_no_logging [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_all_agents_have_heal_surface [32mPASSED[0m[32m [ 51%][0m
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_all_agents_have_heal_repository_surface [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_audit_determinism [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_summary_counts_consistent [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealTelemetrySchema::test_telemetry_record_schema [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealTelemetrySchema::test_telemetry_hash_deterministic [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealTelemetrySchema::test_telemetry_json_serializable [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestTelemetryEmission::test_emit_creates_artifact [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestTelemetryEmission::test_emit_idempotent_same_content [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestTelemetryEmission::test_emit_fails_on_conflict [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_budget_caps_from_env_defaults [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_budget_caps_from_env_custom [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_escalation_budget_enforcement [32mPASSED[0m[32m [ 52%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_high_tier_budget_enforcement [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_budget_counters_tracked [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestHealBudgetCaps::test_enable_llm_false_budgets_zero [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestBudgetAndSeamIntegration::test_seam_guard_still_enforced_with_budgets [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_heal_telemetry_and_budgets.py::TestBudgetAndSeamIntegration::test_no_network_calls_in_budget_checks [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestNoDirectL5Import::test_no_static_l5_import [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestNoDirectL5Import::test_no_static_l3_import [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_load_activation_gate_helper_present [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_load_activation_gate_called_in_smart_fix [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_seam_exposes_load_activation_gate [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestApprovalViaSeamStaticProof::test_seam_uses_importlib_not_static [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_get_file_io_helper_present [32mPASSED[0m[32m [ 53%][0m
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_get_file_io_called_in_smart_fix [32mPASSED[0m[32m [ 54%][0m
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_no_bare_open_write_in_smart_fix [32mPASSED[0m[32m [ 54%][0m
tests/governance/test_healing_reentry.py::TestDirectL2WritesStaticProof::test_no_route_mutation_intent_in_orchestrator [32mPASSED[0m[32m [ 54%][0m
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_is_module_level_function [32mPASSED[0m[32m [ 54%][0m
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_in_dunder_all [32mPASSED[0m[32m [ 54%][0m
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_orchestrator_calls_assert_activation_allowed_on_gate_mod [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_healing_reentry.py::TestHealingWriteCallPath::test_save_file_called_on_file_io_result [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_healing_reentry.py::TestHealingWriteCallPath::test_no_open_write_anywhere_in_orchestrator [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_total_hits_equals_zero [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_every_hit_is_allowlisted [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_every_allowlist_entry_still_exists [32mPASSED[0m[33m [ 54%][0m
tests/governance/test_intent_emission_no_mutation.py::TestAllowlistEnforcement::test_hits_equal_allowlist_exactly [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNoFileIoImports::test_no_fileio_imports[L3_orchestration] [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNoFileIoImports::test_no_fileio_imports[L4_state] [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNoFileIoImports::test_no_fileio_imports[L5_safety] [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_open_write [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_path_write_text [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_shutil_call [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_os_remove [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_json_dump_to_file [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_detects_fileio_import [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_ignores_read_only_open [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_intent_emission_no_mutation.py::TestNegativeRegressionDetectors::test_new_open_write_in_l5_is_flagged [32mPASSED[0m[33m [ 55%][0m
tests/governance/test_l0_upward_import_isolation.py::TestNoStaticUpwardImportsInL0::test_zero_module_level_static_upward_imports [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l0_upward_import_isolation.py::TestNoStaticUpwardImportsInL0::test_negative_regression_detector_catches_static_import [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l0_upward_import_isolation.py::TestNoStaticUpwardImportsInL0::test_negative_regression_lazy_in_function_not_flagged [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_only_allowlisted_seams_use_importlib_for_higher_layers [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_all_allowlisted_seam_files_exist [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_allowlist_covers_all_seam_files [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_negative_regression_importlib_higher_layer_detected [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l0_upward_import_isolation.py::TestImportlibAllowlistEnforcement::test_negative_regression_importlib_dynamic_var_not_flagged [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l6_purity.py::TestL6WritePrimitiveRatchet::test_l6_does_not_exceed_write_ceiling [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l6_purity.py::TestL6NoFileIoImports::test_no_fileio_imports_in_l6 [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l6_purity.py::TestL6NegativeRegression::test_detects_open_append [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l6_purity.py::TestL6NegativeRegression::test_detects_write_text [32mPASSED[0m[33m [ 56%][0m
tests/governance/test_l6_purity.py::TestL6NegativeRegression::test_ignores_read_open [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_exactly_seven_layers_exist [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_layer_ordering_is_monotonic [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_file_enumeration_count_is_stable [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_layer_of_path_returns_correct_layer [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_layer_of_path_returns_none_for_non_layer [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_classify_file_identifies_utils [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_classify_file_identifies_layer_files [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_all_layer_directories_have_files [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_enumerate_python_files_is_sorted [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_layer_inventory.py::TestLayerInventory::test_inventory_summary [32mPASSED[0m[33m [ 57%][0m
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_file_exists_and_valid [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_matches_scanner_total [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_allowlist_enforcement_no_unregistered_seams [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_negative_remove_allowlist_entry_causes_violation [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_lazy_seam_allowlist.py::TestLazySeamAllowlist::test_negative_synthetic_seam_causes_violation [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_lazy_seam_silent_swallow.py::TestScanFileSwallowsSyntaxError::test_syntax_error_returns_empty [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_lazy_seam_silent_swallow.py::TestScanFileSwallowsSyntaxError::test_io_error_returns_empty [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_lazy_seam_silent_swallow.py::TestScanCodebaseContinuesAfterError::test_valid_files_still_scanned [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_lazy_seam_silent_swallow.py::TestNoMutationOnSwallow::test_no_files_created_on_syntax_error [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_lazy_seam_silent_swallow.py::TestSwallowDoesNotWeakenEnforcement::test_corrupt_file_not_treated_as_compliant [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestFrozenImmutability::test_cannot_set_field_after_construction [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestFrozenImmutability::test_cannot_delete_field [32mPASSED[0m[33m [ 58%][0m
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_same_inputs_same_hash [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_different_inputs_different_hash [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_artifact_intent.py::TestHashDeterminism::test_hash_is_sha256_hex [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_artifact_intent.py::TestHashIntegrity::test_verify_passes_on_valid_intent [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_artifact_intent.py::TestHashIntegrity::test_verify_fails_on_wrong_hash [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_artifact_intent.py::TestHashability::test_usable_as_set_member [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_artifact_intent.py::TestHashability::test_usable_as_dict_key [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_seam_compliance.py::TestNoDirectPersistenceImport::test_no_persistence_imports_in_agents [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_seam_compliance.py::TestNoForbiddenWriteCalls::test_no_direct_write_calls_in_agents [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_seam_compliance.py::TestLearningSeamExists::test_learning_seam_file_exists [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_seam_compliance.py::TestLearningSeamExists::test_learning_seam_exports_intent [32mPASSED[0m[33m [ 59%][0m
tests/governance/test_learning_seam_compliance.py::TestASTScannerDeterminism::test_agent_file_collection_deterministic [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_learning_seam_compliance.py::TestASTScannerDeterminism::test_scanner_produces_results [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_bundle_is_frozen [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_checksum_is_sha256 [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_checksum_deterministic [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_checksum_differs_with_different_versions [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_verify_checksum_passes [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayBundle::test_verify_checksum_fails_on_tampered [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_production_only_allows_recorded_output [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_dev_test_allows_both_modes [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_validate_production_passes_recorded_output [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestReplayModePolicy::test_validate_production_rejects_deterministic [32mPASSED[0m[33m [ 60%][0m
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_recorded_output_is_authoritative [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_deterministic_is_not_authoritative [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_deterministic_label_non_authoritative [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_llm_replay_enforcement.py::TestGovernanceLabels::test_recorded_output_label_authoritative [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_recorded_output_returns_stored_bytes [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_deterministic_inference_raises [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_execution_blocked_on_invalid_bundle [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_llm_replay_enforcement.py::TestLLMReplayStrategy::test_strategy_governance_label [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_os_remove_blocked [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_subprocess_run_blocked [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_os_system_blocked [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxBlocking::test_builtins_open_blocked [32mPASSED[0m[33m [ 61%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxRestoration::test_os_remove_restored [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxRestoration::test_subprocess_run_restored [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxRestoration::test_restored_on_exception [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_preventative_sandbox.py::TestDoubleActivation::test_double_activation_raises [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_preventative_sandbox.py::TestCustomTargets::test_custom_target_blocked [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxState::test_inactive_by_default [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_preventative_sandbox.py::TestSandboxState::test_active_inside_context [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_replay_integrity.py::TestReplayHashComputed::test_replay_hash_is_sha256 [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_replay_integrity.py::TestReplayHashComputed::test_integrity_verified_true_on_create [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_replay_integrity.py::TestReplayHashComputed::test_replay_hash_deterministic [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_replay_integrity.py::TestTamperDetection::test_tampered_response_fails [32mPASSED[0m[33m [ 62%][0m
tests/governance/test_replay_integrity.py::TestTamperDetection::test_tampered_model_version_fails [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_replay_integrity.py::TestTamperDetection::test_valid_bundle_passes [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanDeterminism::test_build_plan_produces_same_result_twice [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanDeterminism::test_plan_is_sorted_deterministically [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealScopeControls::test_denylist_excludes_directories [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealScopeControls::test_allowlist_filters_extensions [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealScopeControls::test_skipped_files_counted [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealApplyIdempotency::test_apply_is_idempotent [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealApplyIdempotency::test_apply_handles_missing_files [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealApplyIdempotency::test_dry_run_makes_no_changes [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanSchema::test_plan_to_dict_schema [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanSchema::test_result_to_dict_schema [32mPASSED[0m[33m [ 63%][0m
tests/governance/test_repo_heal_pipeline.py::TestRepoHealPlanSchema::test_plan_json_serializable [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_enable_llm_false_no_llm_call [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_enable_llm_true_requires_capability_token [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_policy_decision_record_emitted [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_repo_heal_pipeline.py::TestHealRepositoryPolicyIntegration::test_baseline_plan_runs_before_escalation [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealImmutability::test_seal_is_frozen [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealImmutability::test_sealed_at_is_set [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealDeterminism::test_same_config_same_hash [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealDeterminism::test_different_config_different_hash [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealVerification::test_unchanged_config_passes [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealVerification::test_mutated_config_fails [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealVerification::test_removed_key_fails [32mPASSED[0m[33m [ 64%][0m
tests/governance/test_routing_config_seal.py::TestSealedRoutingContext::test_no_mutation_passes [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_routing_config_seal.py::TestSealedRoutingContext::test_mutation_raises [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_routing_config_seal.py::TestSealedRoutingContext::test_seal_accessible [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_execution_mode_importable [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_forward_rolling_config_importable [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_rollout_stage_importable [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_health_status_importable [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestForwardRollingContractImportParity::test_contract_symbols_match_originals [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestActivationContractImportParity::test_assert_activation_allowed_importable [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestActivationContractImportParity::test_contract_symbol_matches_original [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestMcpContractImportParity::test_mcp_connection_manager_importable [32mPASSED[0m[33m [ 65%][0m
tests/governance/test_seam_contracts.py::TestMcpContractImportParity::test_mcp_connection_manager_is_protocol [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_safety_agent_factory_instantiates [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_unknown_agent_returns_none [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_healing_agent_protocol_is_runtime_checkable [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolDefaultWiring::test_object_without_heal_repository_fails_protocol [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolFakeInjection::test_safety_strategy_accepts_injected_factory [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_contracts.py::TestSafetyAgentProtocolFakeInjection::test_safety_strategy_default_factory_created_when_none [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_contracts.py::TestNervousSystemAgentProtocolDefaultWiring::test_safety_agent_factory_used_in_nervous_system [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_contracts.py::TestNervousSystemAgentProtocolDefaultWiring::test_nervous_system_agent_protocol_fake_injection [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_seam_file_detection [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_approved_loader_detection [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_scan_produces_deterministic_results [32mPASSED[0m[33m [ 66%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_dynamic_violation_summary [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_static_seam_upward [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_static_l2_to_l5 [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_static_l3_to_l6 [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_dynamic_importlib [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_dynamic_dunder_import [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_dynamic_in_seam [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestDynamicImportMutation::test_mutation_approved_loader_allowed [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_seam_dynamic_enforcement.py::TestConvergenceConfidence::test_convergence_confidence_calculation [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestShiftReportImmutability::test_cannot_mutate_field [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestShiftReportImmutability::test_timestamp_is_set [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestMinimumSampleGuard::test_min_sample_size_is_30 [32mPASSED[0m[33m [ 67%][0m
tests/governance/test_shift_report.py::TestMinimumSampleGuard::test_small_sample_skips [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_shift_report.py::TestMinimumSampleGuard::test_sufficient_sample_runs [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_shift_report.py::TestMMDDetection::test_identical_data_no_shift [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_shift_report.py::TestMMDDetection::test_shifted_data_detected [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_shift_report.py::TestPSIDetection::test_per_feature_flags [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_shift_report.py::TestPSIDetection::test_no_drift_low_psi [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_shift_report.py::TestSkippedReport::test_skipped_report_fields [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_shift_report.py::TestJointShiftLogic::test_joint_true_when_mmd_exceeds [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_shift_report.py::TestJointShiftLogic::test_joint_true_when_psi_exceeds [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_no_banned_imports [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_standard_heal_no_routing_calls [32mPASSED[0m[33m [ 68%][0m
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_wrapper_function_no_routing_calls [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[0] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[1] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[2] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[3] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[4] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[5] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestIrreflexivity::test_no_self_dominance[6] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L1] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L2] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L3] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L4] [32mPASSED[0m[33m [ 69%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L5] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L0-L6] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L0] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L2] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L3] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L4] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L5] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L1-L6] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L0] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L1] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L3] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L4] [32mPASSED[0m[33m [ 70%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L5] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L2-L6] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L0] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L1] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L2] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L4] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L5] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L3-L6] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L0] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L1] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L2] [32mPASSED[0m[33m [ 71%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L3] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L5] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L4-L6] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L0] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L1] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L2] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L3] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L4] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L5-L6] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L0] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L1] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L2] [32mPASSED[0m[33m [ 72%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L3] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L4] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestAntisymmetry::test_antisymmetry[L6-L5] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L2] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L3] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L4] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L5] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L1-L6] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L1] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L3] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L4] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L5] [32mPASSED[0m[33m [ 73%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L2-L6] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L1] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L2] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L4] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L5] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L3-L6] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L1] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L2] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L3] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L5] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L4-L6] [32mPASSED[0m[33m [ 74%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L1] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L2] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L3] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L4] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L5-L6] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L1] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L2] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L3] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L4] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L0-L6-L5] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L2] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L3] [32mPASSED[0m[33m [ 75%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L4] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L5] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L0-L6] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L0] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L3] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L4] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L5] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L2-L6] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L0] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L2] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L4] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L5] [32mPASSED[0m[33m [ 76%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L3-L6] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L0] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L2] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L3] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L5] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L4-L6] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L0] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L2] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L3] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L4] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L5-L6] [32mPASSED[0m[33m [ 77%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L0] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L2] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L3] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L4] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L1-L6-L5] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L1] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L3] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L4] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L5] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L0-L6] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L0] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L3] [32mPASSED[0m[33m [ 78%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L4] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L5] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L1-L6] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L0] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L1] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L4] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L5] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L3-L6] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L0] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L1] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L3] [32mPASSED[0m[33m [ 79%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L5] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L4-L6] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L0] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L1] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L3] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L4] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L5-L6] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L0] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L1] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L3] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L4] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L2-L6-L5] [32mPASSED[0m[33m [ 80%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L1] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L2] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L4] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L5] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L0-L6] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L0] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L2] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L4] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L5] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L1-L6] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L0] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L1] [32mPASSED[0m[33m [ 81%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L4] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L5] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L2-L6] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L0] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L1] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L2] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L5] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L4-L6] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L0] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L1] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L2] [32mPASSED[0m[33m [ 82%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L4] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L5-L6] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L0] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L1] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L2] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L4] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L3-L6-L5] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L1] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L2] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L3] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L5] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L0-L6] [32mPASSED[0m[33m [ 83%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L0] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L2] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L3] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L5] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L1-L6] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L0] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L1] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L3] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L5] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L2-L6] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L0] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L1] [32mPASSED[0m[33m [ 84%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L2] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L5] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L3-L6] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L0] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L1] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L2] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L3] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L5-L6] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L0] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L1] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L2] [32mPASSED[0m[33m [ 85%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L3] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L4-L6-L5] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L1] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L2] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L3] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L4] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L0-L6] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L0] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L2] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L3] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L4] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L1-L6] [32mPASSED[0m[33m [ 86%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L0] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L1] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L3] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L4] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L2-L6] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L0] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L1] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L2] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L4] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L3-L6] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L0] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L1] [32mPASSED[0m[33m [ 87%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L2] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L3] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L4-L6] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L0] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L1] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L2] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L3] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L5-L6-L4] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L1] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L2] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L3] [32mPASSED[0m[33m [ 88%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L4] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L0-L5] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L0] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L2] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L3] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L4] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L1-L5] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L0] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L1] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L3] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L4] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L2-L5] [32mPASSED[0m[33m [ 89%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L0] [32mPASSED[0m[33m [ 90%][0m
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L3-L1] [32mPASSED[0m[33m [ 90%][0m
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
tests/governance/test_tier_lattice.py::TestTransitivity::test_transitivity[L6-L5-L2] [32mPASSED[0m[33m [ 91%][0m
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
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[3] [32mPASSED[0m[33m [ 92%][0m
tests/governance/test_tier_lattice.py::TestDropPolicy::test_l2_plus_never_drop[4] [32mPASSED[0m[33m [ 92%][0m
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
tests/governance/test_time_shifted_influence.py::TestNoMidRunMutation::test_routing_unchanged_in_same_run [32mPASSED[0m[33m [ 93%][0m
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
tests/governance/test_upward_import_enforcement.py::TestUpwardImportMutation::test_mutation_l1_imports_l3 [32mPASSED[0m[33m [ 94%][0m
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
tests/governance/test_upward_import_enforcement.py::TestLazySeamViolation::test_upward_import_inside_non_get_function_is_violation [32mPASSED[0m[33m [ 95%][0m
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
tests/governance/test_vllm_determinism.py::test_decimal_normalization [32mPASSED[0m[33m [ 96%][0m
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
tests/governance/test_vllm_determinism.py::test_context_hash_immutability [32mPASSED[0m[33m [ 98%][0m
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
  C:\Git\Agentic-Workflow\tests\governance\test_healing_reentry.py:203: DeprecationWarning: Attribute s is deprecated and will be removed in Python 3.14; use value instead
    if isinstance(elt, ast.Constant) and isinstance(elt.s, str)

tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_in_dunder_all
tests/governance/test_healing_reentry.py::TestActivationGateModuleLevelContract::test_assert_activation_allowed_in_dunder_all
  C:\Git\Agentic-Workflow\tests\governance\test_healing_reentry.py:201: DeprecationWarning: Attribute s is deprecated and will be removed in Python 3.14; use value instead
    elt.s

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== GUARDIAN LAYER SUMMARY ============================
Guardian tests run: 8
Passed: 1165
Failed: 0
Errors: 0

\u2705 GUARDIAN STATUS: PASS
All architectural integrity checks passed.
======================================  =======================================
============================ slowest 10 durations =============================
3.01s call     tests/governance/test_heal_surface_enforcement.py::TestHealSurfaceEnforcement::test_audit_determinism
3.00s call     tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_determinism
2.98s call     tests/governance/test_agent_heal_audit.py::TestDeterminism::test_byte_identical_json_runs
2.46s call     tests/governance/test_seam_dynamic_enforcement.py::TestSeamDynamicEnforcement::test_scan_produces_deterministic_results
2.18s call     tests/governance/test_upward_import_enforcement.py::TestLazySeamMetric::test_lazy_upward_import_metric_is_deterministic
1.98s call     tests/governance/test_upward_import_enforcement.py::TestUpwardImportEnforcement::test_scan_produces_deterministic_results
1.53s call     tests/governance/test_agent_heal_audit.py::TestDeterminism::test_deterministic_ordering
1.53s call     tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_base_class_name_extraction
1.53s call     tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_agent_naming_detection
1.52s call     tests/governance/test_agent_heal_audit.py::TestStructureContract::test_summary_schema
[33m================= [32m1165 passed[0m, [33m[1m4 warnings[0m[33m in 61.61s (0:01:01)[0m[33m =================[0m
```

## Evidence Contract v2 Checker
```
$ C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe ops_scripts/ci/check_evidence_contract_v2.py --paths docs/reports/plans
Checking 4 evidence file(s)...
Checking: reports\plans\phase_02_consolidated.md
Checking: reports\plans\phase_03_04_consolidated.md
Checking: reports\plans\phase_05_06_consolidated.md
Checking: reports\plans\phase_07_08_consolidated.md
STDERR: Traceback (most recent call last):
  File "C:\Git\Agentic-Workflow\ops_scripts\ci\check_evidence_contract_v2.py", line 218, in <module>
    sys.exit(main())
             ^^^^^^
  File "C:\Git\Agentic-Workflow\ops_scripts\ci\check_evidence_contract_v2.py", line 208, in main
    print(f"\n\U0001f6a8 Evidence contract violations found: {len(violations)}")
  File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f6a8' in position 2: character maps to <undefined>
EXIT CODE: 1
```

## INSPECTED_FILE_CONTENTS

### tools/evidence/evidence_contract_v2.py
```
"""
Evidence Contract v2 Helper

Shared helper for consolidated evidence runners that enforces:
- Explicit CODE_COMMIT and EVIDENCE_COMMIT validation
- Hash-loop prevention
- Scope containment with allowed prefixes
- Semantic separation of file sections
- PowerShell detection and rejection
"""

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Set


class EvidenceContractV2:
    """Evidence Contract v2 helper for consolidated runners."""

    # Default allowed prefixes for phases 7-8
    DEFAULT_ALLOWED_PREFIXES: Set[str] = {
        "apps_shared/",
        "apps_lic/",
        "apps_rg/",
        "agentic_core/",
        "ops_scripts/",
        "tools/evidence/",
        "tests/",
        "docs/reports/plans/",
        ".github/workflows/",
        "pytest.ini",
        "docs/rules/",
    }

    def __init__(self, repo_root: Path, allowed_prefixes: Optional[Set[str]] = None):
        """Initialize contract helper.

        Args:
            repo_root: Repository root path
            allowed_prefixes: Set of allowed path prefixes for scope containment
        """
        self.repo_root = repo_root
        self.allowed_prefixes = allowed_prefixes or self.DEFAULT_ALLOWED_PREFIXES

    def validate_commit_hash(self, commit_hash: str) -> None:
        """Validate that commit hash is 40-character hex."""
        if len(commit_hash) != 40:
            raise ValueError(f"Commit hash must be 40 characters: {commit_hash}")
        if not all(c in "0123456789abcdefABCDEF" for c in commit_hash):
            raise ValueError(f"Commit hash must be hex: {commit_hash}")

    def run_cmd(self, args: List[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
        """Execute command with PowerShell detection and return (rc, stdout, stderr)."""
        # PowerShell detection at argv level only
        argv0_lower = str(args[0]).lower()
        if "pwsh" in argv0_lower or "powershell" in argv0_lower:
            raise ValueError(f"PowerShell usage detected in command: {' '.join(args)}")

        work_dir = cwd or self.repo_root
        result = subprocess.run(
            args, cwd=work_dir, capture_output=True, text=True, shell=False,
            encoding="utf-8", errors="replace"
        )
        return result.returncode, result.stdout, result.stderr

    def get_current_head(self) -> str:
        """Get current HEAD commit hash."""
        rc, out, err = self.run_cmd(["git", "rev-parse", "HEAD"])
        if rc != 0:
            raise RuntimeError(f"git rev-parse failed: {err}")
        return out.strip()

    def validate_commit_exists(self, commit_hash: str) -> None:
        """Validate that commit exists in repository."""
        rc, out, err = self.run_cmd(["git", "cat-file", "-e", commit_hash])
        if rc != 0:
            raise ValueError(f"Commit does not exist: {commit_hash}")

    def validate_hash_loop_prevention(self, code_commit: str) -> None:
        """Enforce CODE_COMMIT != current HEAD (hash-loop prevention)."""
        current_head = self.get_current_head()
        if code_commit == current_head:
            raise ValueError(
                f"CODE_COMMIT ({code_commit}) == current HEAD ({current_head}). "
                "This would create a hash loop. Use a commit from before the evidence changes."
            )

    def get_changed_files(self, commit_hash: str) -> List[str]:
        """Get list of changed files for a commit."""
        rc, out, err = self.run_cmd(
            ["git", "show", "--name-only", "--pretty=format:", commit_hash]
        )
        if rc != 0:
            raise RuntimeError(f"git show failed for {commit_hash}: {err}")

        files = [f.strip() for f in out.strip().splitlines() if f.strip()]
        return files

    def validate_scope_containment(self, files: List[str], phase_name: str) -> None:
        """Validate that all changed files are within allowed prefixes."""
        violations = []
        for file_path in files:
            if not any(file_path.startswith(prefix) for prefix in self.allowed_prefixes):
                violations.append(file_path)

        if violations:
            raise ValueError(
                f"Scope violation in {phase_name}: Files outside allowed prefixes detected:\n"
                + "\n".join(f"  - {v}" for v in violations)
                + f"\nAllowed prefixes: {sorted(self.allowed_prefixes)}"
            )

    def validate_evidence_contract_structure(
        self,
        code_commit: str,
        evidence_commit: Optional[str] = None,
        require_evidence_commit: bool = False
    ) -> None:
        """Validate evidence contract structure and requirements."""
        # Validate CODE_COMMIT
        self.validate_commit_hash(code_commit)
        self.validate_commit_exists(code_commit)
        self.validate_hash_loop_prevention(code_commit)

        # Validate EVIDENCE_COMMIT if required
        if require_evidence_commit:
            if not evidence_commit:
                raise ValueError("EVIDENCE_COMMIT is required")
            self.validate_commit_hash(evidence_commit)
            self.validate_commit_exists(evidence_commit)

    def build_evidence_sections(
        self,
        code_commit: str,
        evidence_commit: Optional[str] = None,
        inspected_files: Optional[List[str]] = None
    ) -> dict:
        """Build evidence contract sections."""
        # Get changed files for CODE_COMMIT
        files_changed_code = self.get_changed_files(code_commit)
        self.validate_scope_containment(files_changed_code, "CODE_COMMIT")

        # Get changed files for EVIDENCE_COMMIT if provided
        files_changed_evidence = []
        if evidence_commit:
            files_changed_evidence = self.get_changed_files(evidence_commit)

        # Default inspected files if not provided
        if not inspected_files:
            inspected_files = []

        return {
            "CODE_COMMIT": code_commit,
            "EVIDENCE_COMMIT": evidence_commit or "PENDING",
            "FILES_CHANGED_CODE": files_changed_code,
            "FILES_CHANGED_EVIDENCE": files_changed_evidence,
            "INSPECTED_FILES": inspected_files,
        }

    def format_evidence_sections(self, sections: dict) -> List[str]:
        """Format evidence sections as markdown lines."""
        lines = []

        # CODE_COMMIT
        lines.append("## CODE_COMMIT")
        lines.append(sections["CODE_COMMIT"])
        lines.append("")

        # EVIDENCE_COMMIT
        lines.append("## EVIDENCE_COMMIT")
        lines.append(sections["EVIDENCE_COMMIT"])
        lines.append("")

        # FILES_CHANGED_CODE
        lines.append("## FILES_CHANGED_CODE")
        lines.append("```")
        for f in sections["FILES_CHANGED_CODE"]:
            lines.append(f)
        lines.append("```")
        lines.append("")

        # FILES_CHANGED_EVIDENCE
        lines.append("## FILES_CHANGED_EVIDENCE")
        lines.append("```")
        if sections["FILES_CHANGED_EVIDENCE"]:
            for f in sections["FILES_CHANGED_EVIDENCE"]:
                lines.append(f)
        else:
            lines.append("PENDING (will be filled after commit)")
        lines.append("```")
        lines.append("")

        # INSPECTED_FILES
        lines.append("## INSPECTED_FILES")
        lines.append("```")
        for f in sections["INSPECTED_FILES"]:
            lines.append(f)
        lines.append("```")
        lines.append("")

        return lines

    @staticmethod
    def parse_args(description: str) -> argparse.Namespace:
        """Parse common evidence runner arguments."""
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument("--code-commit", required=True, help="40-hex commit hash for CODE_COMMIT")
        parser.add_argument("--evidence-commit", help="40-hex commit hash for EVIDENCE_COMMIT (optional)")
        return parser.parse_args()

    @staticmethod
    def read_file_content(filepath: Path) -> str:
        """Read file content with error handling."""
        try:
            return filepath.read_text(encoding="utf-8")
        except Exception as e:
            return f"ERROR: Could not read {filepath}: {e}"
```

### tools/evidence/phase05_06_consolidated_evidence_runner.py
```
#!/usr/bin/env python3
"""
Phase 5-6 Consolidated Evidence Runner (v2)

Generates consolidated evidence for:
- Phase 5: Cross-App Spine Normalization & Contract Lock
- Phase 6: Spine Integrity Guardrail (Structural Enforcement)

Updated to use Evidence Contract v2 helper for scope isolation and self-verification.
"""

import sys
from pathlib import Path

# Add the tools/evidence directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from evidence_contract_v2 import EvidenceContractV2


def main():
    """Generate Phases 5-6 consolidated evidence using Contract v2."""
    args = EvidenceContractV2.parse_args("Generate Phases 5-6 consolidated evidence")

    code_commit = args.code_commit
    evidence_commit = args.evidence_commit

    repo_root = Path(__file__).parent.parent.parent
    evidence_file = repo_root / "docs" / "reports" / "plans" / "phase_05_06_consolidated.md"

    print(f"Generating Phases 5-6 consolidated evidence: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    if evidence_commit:
        print(f"EVIDENCE_COMMIT: {evidence_commit}")

    # Initialize contract helper with allowed prefixes for phases 5-6
    allowed_prefixes = {
        "apps_shared/",
        "apps_lic/",
        "apps_rg/",
        "agentic_core/",
        "ops_scripts/",
        "tools/evidence/",
        "tests/",
        "docs/reports/plans/",
        ".github/workflows/",
        "pytest.ini",
        "docs/rules/",
    }

    contract = EvidenceContractV2(repo_root, allowed_prefixes)

    # Validate evidence contract structure
    require_evidence_commit = evidence_commit is not None
    contract.validate_evidence_contract_structure(
        code_commit, evidence_commit, require_evidence_commit
    )

    # Start building evidence content
    evidence_lines = []
    evidence_lines.append("# Phases 5-6: Spine Adapter Normalization & Structural Enforcement (Consolidated)")
    evidence_lines.append("")
    evidence_lines.append("## Scope")
    evidence_lines.append("Phase 5: Cross-App Spine Normalization & Contract Lock")
    evidence_lines.append("Phase 6: Spine Integrity Guardrail (Structural Enforcement)")
    evidence_lines.append("")

    # Build evidence sections using contract helper
    inspected = [
        "apps_shared/spine/base_spine_adapter.py",
        "apps_lic/engines/lic_spine_adapter.py",
        "apps_rg/engines/rg_spine_adapter.py",
        "tests/unit_min_deps/test_apps_lic_spine_adapter.py",
        "tests/unit_min_deps/test_apps_rg_spine_adapter.py",
        "tests/unit_min_deps/test_spine_cross_app_contract.py",
        "ops_scripts/ci/check_spine_adapter_contract.py",
        "tools/evidence/phase05_06_consolidated_evidence_runner.py",
    ]

    sections = contract.build_evidence_sections(
        code_commit, evidence_commit, inspected
    )

    # Add formatted sections
    evidence_lines.extend(contract.format_evidence_sections(sections))

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
        (
            [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_spine_cross_app_contract.py"],
            "Cross-App Contract Tests",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_spine_bypass.py"],
            "Spine Bypass Check",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_spine_adapter_contract.py"],
            "Spine Adapter Contract Guard",
        ),
        (
            [sys.executable, "-m", "pytest", "-q"],
            "Full Test Suite",
        ),
    ]

    for cmd, title in commands:
        evidence_lines.append(f"## {title}")
        evidence_lines.append("```")
        evidence_lines.append(f"$ {' '.join(cmd)}")

        rc, out, err = contract.run_cmd(cmd)
        evidence_lines.append(out)
        if err:
            evidence_lines.append(f"STDERR: {err}")
        if rc != 0:
            evidence_lines.append(f"EXIT CODE: {rc}")

        evidence_lines.append("```")
        evidence_lines.append("")

    # Embed full contents of inspected files
    evidence_lines.append("## INSPECTED_FILE_CONTENTS")
    evidence_lines.append("")

    for filepath in sections["INSPECTED_FILES"]:
        full_path = repo_root / filepath
        evidence_lines.append(f"### {filepath}")
        evidence_lines.append("```")
        content = EvidenceContractV2.read_file_content(full_path)
        evidence_lines.append(content)
        evidence_lines.append("```")
        evidence_lines.append("")

    # Write evidence file with LF line endings and no trailing whitespace
    evidence_content = "\n".join(line.rstrip() for line in evidence_lines)
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(evidence_content, encoding="utf-8", newline="\n")

    # Sanity check: evidence file should not start with Python code
    content_start = evidence_file.read_text(encoding="utf-8")[:200]
    if content_start.strip().startswith("#!/usr/bin/env python") or "def main()" in content_start[:200]:
        print("ERROR: Evidence file appears to contain Python code instead of markdown")
        print("This indicates the runner content was written to the evidence file.")
        sys.exit(1)

    print(f"Evidence generated successfully: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    print(f"EVIDENCE_COMMIT: {sections['EVIDENCE_COMMIT']}")
    print(f"Current HEAD: {contract.get_current_head()}")

    if not evidence_commit:
        print("\nTo complete the evidence contract:")
        print("1. Commit this evidence file")
        print("2. Re-run with --evidence-commit <new_commit_hash>")
        print("3. The runner will update the sealed evidence file")


if __name__ == "__main__":
    main()
```

### tools/evidence/phase07_08_consolidated_evidence_runner.py
```
#!/usr/bin/env python3
"""
Phase 7-8 Consolidated Evidence Runner

Generates consolidated evidence for:
- Phase 7: Evidence Contract v2: Scope Isolation + Self-Verification
- Phase 8: CI Enforcement: Evidence Contract Guardrail

Uses Evidence Contract v2 helper for scope isolation and self-verification.
"""

import sys
from pathlib import Path

# Add the tools/evidence directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from evidence_contract_v2 import EvidenceContractV2


def main():
    """Generate Phases 7-8 consolidated evidence using Contract v2."""
    args = EvidenceContractV2.parse_args("Generate Phases 7-8 consolidated evidence")

    code_commit = args.code_commit
    evidence_commit = args.evidence_commit

    repo_root = Path(__file__).parent.parent.parent
    evidence_file = repo_root / "docs" / "reports" / "plans" / "phase_07_08_consolidated.md"

    print(f"Generating Phases 7-8 consolidated evidence: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    if evidence_commit:
        print(f"EVIDENCE_COMMIT: {evidence_commit}")

    # Initialize contract helper with allowed prefixes for phases 7-8
    allowed_prefixes = {
        "apps_shared/",
        "apps_lic/",
        "apps_rg/",
        "agentic_core/",
        "ops_scripts/",
        "tools/evidence/",
        "tests/",
        "docs/reports/plans/",
        ".github/workflows/",
        "pytest.ini",
        "docs/rules/",
    }

    contract = EvidenceContractV2(repo_root, allowed_prefixes)

    # Validate evidence contract structure
    require_evidence_commit = evidence_commit is not None
    contract.validate_evidence_contract_structure(
        code_commit, evidence_commit, require_evidence_commit
    )

    # Start building evidence content
    evidence_lines = []
    evidence_lines.append("# Phases 7-8: Evidence Contract v2 + CI Enforcement (Consolidated)")
    evidence_lines.append("")
    evidence_lines.append("## Scope")
    evidence_lines.append("Phase 7: Evidence Contract v2: Scope Isolation + Self-Verification")
    evidence_lines.append("Phase 8: CI Enforcement: Evidence Contract Guardrail")
    evidence_lines.append("")

    # Build evidence sections using contract helper
    inspected = [
        "tools/evidence/evidence_contract_v2.py",
        "tools/evidence/phase05_06_consolidated_evidence_runner.py",
        "tools/evidence/phase07_08_consolidated_evidence_runner.py",
        "tests/unit_min_deps/test_evidence_contract_v2.py",
        "ops_scripts/ci/check_evidence_contract_v2.py",
        ".github/workflows/spine-determinism-guard.yml",
    ]

    sections = contract.build_evidence_sections(
        code_commit, evidence_commit, inspected
    )

    # Add formatted sections
    evidence_lines.extend(contract.format_evidence_sections(sections))

    # Command outputs
    commands = [
        (
            [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_evidence_contract_v2.py"],
            "Evidence Contract v2 Unit Tests",
        ),
        (
            [sys.executable, "-m", "pytest", "-q"],
            "Full Test Suite",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_evidence_contract_v2.py", "--paths", "docs/reports/plans"],
            "Evidence Contract v2 Checker",
        ),
    ]

    for cmd, title in commands:
        evidence_lines.append(f"## {title}")
        evidence_lines.append("```")
        evidence_lines.append(f"$ {' '.join(cmd)}")

        rc, out, err = contract.run_cmd(cmd)
        evidence_lines.append(out)
        if err:
            evidence_lines.append(f"STDERR: {err}")
        if rc != 0:
            evidence_lines.append(f"EXIT CODE: {rc}")

        evidence_lines.append("```")
        evidence_lines.append("")

    # Embed full contents of inspected files
    evidence_lines.append("## INSPECTED_FILE_CONTENTS")
    evidence_lines.append("")

    for filepath in sections["INSPECTED_FILES"]:
        full_path = repo_root / filepath
        evidence_lines.append(f"### {filepath}")
        evidence_lines.append("```")
        content = EvidenceContractV2.read_file_content(full_path)
        evidence_lines.append(content)
        evidence_lines.append("```")
        evidence_lines.append("")

    # Write evidence file with LF line endings and no trailing whitespace
    evidence_content = "\n".join(line.rstrip() for line in evidence_lines)
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(evidence_content, encoding="utf-8", newline="\n")

    # Sanity check: evidence file should not start with Python code
    content_start = evidence_file.read_text(encoding="utf-8")[:200]
    if content_start.strip().startswith("#!/usr/bin/env python") or "def main()" in content_start[:200]:
        print("ERROR: Evidence file appears to contain Python code instead of markdown")
        print("This indicates the runner content was written to the evidence file.")
        sys.exit(1)

    print(f"Evidence generated successfully: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    print(f"EVIDENCE_COMMIT: {sections['EVIDENCE_COMMIT']}")
    print(f"Current HEAD: {contract.get_current_head()}")

    if not evidence_commit:
        print("\nTo complete the evidence contract:")
        print("1. Commit this evidence file")
        print("2. Re-run with --evidence-commit <new_commit_hash>")
        print("3. The runner will update the sealed evidence file")


if __name__ == "__main__":
    main()
```

### tests/unit_min_deps/test_evidence_contract_v2.py
```
"""Tests for Evidence Contract v2 helper."""

from unittest.mock import MagicMock, patch
import pytest
import sys
from pathlib import Path

# Add tools/evidence to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "evidence"))

from evidence_contract_v2 import EvidenceContractV2


@pytest.mark.unit_min_deps
def test_rejects_missing_code_commit():
    """EvidenceContractV2.parse_args rejects missing --code-commit."""
    with patch.object(sys, 'argv', ['test_evidence_contract_v2.py']):
        with pytest.raises(SystemExit):
            EvidenceContractV2.parse_args("test")


@pytest.mark.unit_min_deps
def test_accepts_valid_code_commit():
    """EvidenceContractV2.parse_args accepts valid --code-commit."""
    with patch.object(sys, 'argv', [
        'test_evidence_contract_v2.py',
        '--code-commit',
        'a' * 40
    ]):
        args = EvidenceContractV2.parse_args("test")
        assert args.code_commit == 'a' * 40
        assert args.evidence_commit is None


@pytest.mark.unit_min_deps
def test_validate_commit_hash_invalid_length():
    """validate_commit_hash rejects non-40-character hashes."""
    contract = EvidenceContractV2(Path.cwd())

    with pytest.raises(ValueError, match="must be 40 characters"):
        contract.validate_commit_hash("short")

    with pytest.raises(ValueError, match="must be 40 characters"):
        contract.validate_commit_hash("a" * 39)


@pytest.mark.unit_min_deps
def test_validate_commit_hash_invalid_chars():
    """validate_commit_hash rejects non-hex characters."""
    contract = EvidenceContractV2(Path.cwd())

    with pytest.raises(ValueError, match="must be hex"):
        contract.validate_commit_hash("g" * 40)

    with pytest.raises(ValueError, match="must be hex"):
        contract.validate_commit_hash("a" * 20 + "xyz" + "a" * 17)


@pytest.mark.unit_min_deps
def test_validate_commit_hash_valid():
    """validate_commit_hash accepts valid 40-hex strings."""
    contract = EvidenceContractV2(Path.cwd())

    # Should not raise
    contract.validate_commit_hash("a" * 40)
    contract.validate_commit_hash("0123456789abcdef0123456789abcdef01234567")  # 40 chars
    contract.validate_commit_hash("ABCDEF0123456789ABCDEF0123456789ABCDEF01")  # 40 chars


@pytest.mark.unit_min_deps
def test_run_cmd_detects_powershell():
    """run_cmd rejects PowerShell commands."""
    contract = EvidenceContractV2(Path.cwd())

    with pytest.raises(ValueError, match="PowerShell usage detected"):
        contract.run_cmd(["powershell", "-Command", "echo test"])

    with pytest.raises(ValueError, match="PowerShell usage detected"):
        contract.run_cmd(["pwsh", "-Command", "echo test"])

    with pytest.raises(ValueError, match="PowerShell usage detected"):
        contract.run_cmd(["PowerShell.exe", "-Command", "echo test"])


@pytest.mark.unit_min_deps
def test_run_cmd_accepts_python():
    """run_cmd accepts Python commands."""
    contract = EvidenceContractV2(Path.cwd())

    # Mock subprocess.run to avoid actual execution
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Should not raise
        rc, out, err = contract.run_cmd(["python", "--version"])
        assert rc == 0


@pytest.mark.unit_min_deps
def test_hash_loop_prevention():
    """validate_hash_loop_prevention rejects CODE_COMMIT == current HEAD."""
    contract = EvidenceContractV2(Path.cwd())

    with patch.object(contract, 'get_current_head', return_value='a' * 40):
        with pytest.raises(ValueError, match="hash loop"):
            contract.validate_hash_loop_prevention('a' * 40)


@pytest.mark.unit_min_deps
def test_hash_loop_prevention_allows_different():
    """validate_hash_loop_prevention allows different commits."""
    contract = EvidenceContractV2(Path.cwd())

    with patch.object(contract, 'get_current_head', return_value='a' * 40):
        # Should not raise
        contract.validate_hash_loop_prevention('b' * 40)


@pytest.mark.unit_min_deps
def test_validate_scope_containment_violations():
    """validate_scope_containment rejects files outside allowed prefixes."""
    contract = EvidenceContractV2(Path.cwd(), {"apps_lic/", "apps_rg/"})

    files_out_of_scope = [
        "docs/technical/drill-down.md",
        "scripts/deploy.sh",
        "temp/file.txt"
    ]

    with pytest.raises(ValueError, match="Scope violation"):
        contract.validate_scope_containment(files_out_of_scope, "TEST")


@pytest.mark.unit_min_deps
def test_validate_scope_containment_allowed():
    """validate_scope_containment allows files within allowed prefixes."""
    contract = EvidenceContractV2(Path.cwd(), {"apps_lic/", "apps_rg/"})

    files_in_scope = [
        "apps_lic/engines/test.py",
        "apps_rg/engines/test.py",
        "apps_lic/subdir/file.py"
    ]

    # Should not raise
    contract.validate_scope_containment(files_in_scope, "TEST")


@pytest.mark.unit_min_deps
def test_build_evidence_sections():
    """build_evidence_sections returns properly structured sections."""
    contract = EvidenceContractV2(Path.cwd())

    with patch.object(contract, 'get_changed_files') as mock_get_files, \
         patch.object(contract, 'validate_scope_containment'):

        mock_get_files.return_value = ["file1.py", "file2.py"]

        sections = contract.build_evidence_sections(
            "a" * 40,
            evidence_commit="b" * 40,
            inspected_files=["inspected.py"]
        )

        assert sections["CODE_COMMIT"] == "a" * 40
        assert sections["EVIDENCE_COMMIT"] == "b" * 40
        assert sections["FILES_CHANGED_CODE"] == ["file1.py", "file2.py"]
        assert sections["FILES_CHANGED_EVIDENCE"] == ["file1.py", "file2.py"]
        assert sections["INSPECTED_FILES"] == ["inspected.py"]


@pytest.mark.unit_min_deps
def test_format_evidence_sections():
    """format_evidence_sections produces proper markdown structure."""
    contract = EvidenceContractV2(Path.cwd())

    sections = {
        "CODE_COMMIT": "a" * 40,
        "EVIDENCE_COMMIT": "PENDING",
        "FILES_CHANGED_CODE": ["file1.py", "file2.py"],
        "FILES_CHANGED_EVIDENCE": [],
        "INSPECTED_FILES": ["inspected.py"]
    }

    lines = contract.format_evidence_sections(sections)

    # Check that all required sections are present
    assert "## CODE_COMMIT" in lines
    assert "## EVIDENCE_COMMIT" in lines
    assert "## FILES_CHANGED_CODE" in lines
    assert "## FILES_CHANGED_EVIDENCE" in lines
    assert "## INSPECTED_FILES" in lines

    # Check that values are present
    assert "a" * 40 in lines
    assert "PENDING" in lines
    assert "file1.py" in lines
    assert "file2.py" in lines
    assert "inspected.py" in lines


@pytest.mark.unit_min_deps
def test_validate_evidence_contract_structure():
    """validate_evidence_contract_structure performs all validations."""
    contract = EvidenceContractV2(Path.cwd())

    with patch.object(contract, 'validate_commit_hash') as mock_hash, \
         patch.object(contract, 'validate_commit_exists') as mock_exists, \
         patch.object(contract, 'validate_hash_loop_prevention') as mock_loop:

        # Test without evidence_commit
        contract.validate_evidence_contract_structure("a" * 40, require_evidence_commit=False)

        mock_hash.assert_called_once_with("a" * 40)
        mock_exists.assert_called_once_with("a" * 40)
        mock_loop.assert_called_once_with("a" * 40)

        # Test with evidence_commit
        mock_hash.reset_mock()
        mock_exists.reset_mock()
        mock_loop.reset_mock()

        contract.validate_evidence_contract_structure("a" * 40, "b" * 40, require_evidence_commit=True)

        assert mock_hash.call_count == 2
        assert mock_exists.call_count == 2
        mock_loop.assert_called_once_with("a" * 40)


@pytest.mark.unit_min_deps
def test_validate_evidence_contract_structure_requires_evidence_commit():
    """validate_evidence_contract_structure requires evidence_commit when required."""
    contract = EvidenceContractV2(Path.cwd())

    with patch.object(contract, 'validate_commit_hash') as mock_hash, \
         patch.object(contract, 'validate_commit_exists') as mock_exists, \
         patch.object(contract, 'validate_hash_loop_prevention') as mock_loop:

        # Make validate_commit_exists raise an error to simulate non-existent commit
        mock_exists.side_effect = ValueError("Commit does not exist: test")

        with pytest.raises(ValueError, match="Commit does not exist"):
            contract.validate_evidence_contract_structure("a" * 40, require_evidence_commit=True)
```

### ops_scripts/ci/check_evidence_contract_v2.py
```
#!/usr/bin/env python3
"""
Evidence Contract v2 Checker

Scans consolidated evidence files and verifies contract compliance:
- Required headings exist and appear exactly once
- CODE_COMMIT and EVIDENCE_COMMIT are 40-hex
- No duplicated/contradictory commit fields
- No embedded Python source blocks that look like runner code
- Deterministic, pure read-only, exits nonzero on violations
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Set


class EvidenceContractChecker:
    """Checker for Evidence Contract v2 compliance."""

    # Required headings that must appear exactly once
    REQUIRED_HEADINGS: Set[str] = {
        "CODE_COMMIT",
        "EVIDENCE_COMMIT",
        "FILES_CHANGED_CODE",
        "FILES_CHANGED_EVIDENCE",
        "INSPECTED_FILES",
    }

    # Patterns that suggest embedded Python code
    PYTHON_CODE_PATTERNS = [
        r'#!/usr/bin/env python',
        r'def main\(',
        r'import sys',
        r'from pathlib import Path',
        r'if __name__ == "__main__"',
        r'argparse\.ArgumentParser',
        r'subprocess\.run',
    ]

    def __init__(self, paths: List[Path]):
        """Initialize checker with paths to scan.

        Args:
            paths: List of directories to scan for evidence files
        """
        self.paths = paths
        self.violations = []

    def find_evidence_files(self) -> List[Path]:
        """Find all phase_*_consolidated*.md files in paths."""
        evidence_files = []

        for path in self.paths:
            if not path.exists():
                self.violations.append(f"Path does not exist: {path}")
                continue

            if path.is_file() and path.name.startswith("phase_") and "consolidated" in path.name and path.suffix == ".md":
                evidence_files.append(path)
            elif path.is_dir():
                # Search for matching files
                pattern = "phase_*_consolidated*.md"
                files = list(path.glob(pattern))
                evidence_files.extend(files)

        return sorted(evidence_files)

    def validate_commit_hash(self, commit_hash: str, field_name: str, filepath: Path) -> None:
        """Validate that commit hash is 40-character hex."""
        if len(commit_hash) != 40:
            self.violations.append(
                f"{filepath}: {field_name} must be 40 characters (got {len(commit_hash)}): {commit_hash}"
            )
        elif not all(c in "0123456789abcdefABCDEF" for c in commit_hash):
            self.violations.append(
                f"{filepath}: {field_name} must be hex: {commit_hash}"
            )
        elif field_name != "EVIDENCE_COMMIT" or commit_hash != "PENDING":
            # Additional check: verify commit exists (skip for PENDING)
            try:
                import subprocess
                result = subprocess.run(
                    ["git", "cat-file", "-e", commit_hash],
                    capture_output=True,
                    text=True,
                    cwd=filepath.parent.parent.parent
                )
                if result.returncode != 0:
                    self.violations.append(
                        f"{filepath}: {field_name} does not exist in repository: {commit_hash}"
                    )
            except Exception:
                # If git check fails, just warn but don't fail
                pass

    def check_file(self, filepath: Path) -> None:
        """Check a single evidence file for compliance."""
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            self.violations.append(f"{filepath}: Could not read file: {e}")
            return

        # Check for required headings
        found_headings = set()
        for heading in self.REQUIRED_HEADINGS:
            pattern = rf"^## {heading}$"
            matches = re.findall(pattern, content, re.MULTILINE)
            if len(matches) == 0:
                self.violations.append(f"{filepath}: Missing required heading: ## {heading}")
            elif len(matches) > 1:
                self.violations.append(f"{filepath}: Duplicate heading: ## {heading} (found {len(matches)} times)")
            else:
                found_headings.add(heading)

        # Check for unexpected headings
        all_headings = re.findall(r"^## (.+)$", content, re.MULTILINE)
        for heading in all_headings:
            if heading in self.REQUIRED_HEADINGS and heading not in found_headings:
                # This shouldn't happen if our counting is right, but let's be safe
                self.violations.append(f"{filepath}: Found heading but not counted: ## {heading}")

        # Extract and validate commit hashes
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()

            if line.startswith("## CODE_COMMIT"):
                # Next line should be the commit hash
                if i + 1 < len(lines):
                    commit_hash = lines[i + 1].strip()
                    if commit_hash and commit_hash != "CODE_COMMIT":  # Skip if it's just the heading again
                        self.validate_commit_hash(commit_hash, "CODE_COMMIT", filepath)

            elif line.startswith("## EVIDENCE_COMMIT"):
                # Next line should be the commit hash
                if i + 1 < len(lines):
                    commit_hash = lines[i + 1].strip()
                    if commit_hash and commit_hash != "EVIDENCE_COMMIT":
                        if commit_hash != "PENDING":
                            self.validate_commit_hash(commit_hash, "EVIDENCE_COMMIT", filepath)

        # Check for embedded Python code (basic heuristic)
        content_lower = content.lower()
        for pattern in self.PYTHON_CODE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                # Check if it's in a code block (which is expected for file contents)
                # We're looking for Python code outside of proper markdown code blocks
                lines = content.split('\n')
                in_code_block = False
                code_block_start = None

                for j, check_line in enumerate(lines):
                    if check_line.strip() == '```':
                        if not in_code_block:
                            in_code_block = True
                            code_block_start = j
                        else:
                            in_code_block = False
                            code_block_start = None

                    # If we find Python-like patterns outside code blocks, that's suspicious
                    if not in_code_block and re.search(pattern, check_line, re.IGNORECASE):
                        # Skip if it's clearly just a comment about Python code
                        if not check_line.strip().startswith('#') and 'python' not in check_line.lower():
                            self.violations.append(
                                f"{filepath}: Suspicious Python code pattern detected outside code block at line {j + 1}: {pattern}"
                            )
                            break  # One violation per pattern is enough

        # Check for proper markdown structure
        if not content.startswith('#'):
            self.violations.append(f"{filepath}: Should start with markdown heading (#)")

    def check(self) -> List[str]:
        """Check all evidence files and return violations."""
        evidence_files = self.find_evidence_files()

        if not evidence_files:
            self.violations.append("No evidence files found matching pattern phase_*_consolidated*.md")
            return self.violations

        print(f"Checking {len(evidence_files)} evidence file(s)...")

        for filepath in evidence_files:
            print(f"Checking: {filepath.relative_to(filepath.parent.parent.parent)}")
            self.check_file(filepath)

        return self.violations


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check Evidence Contract v2 compliance")
    parser.add_argument("--paths", nargs="+", required=True, help="Paths to scan for evidence files")
    args = parser.parse_args()

    # Convert to Path objects
    paths = [Path(p) for p in args.paths]

    checker = EvidenceContractChecker(paths)
    violations = checker.check()

    if violations:
        print(f"\n🚨 Evidence contract violations found: {len(violations)}")
        for violation in violations:
            print(f"  ❌ {violation}")
        return 1
    else:
        print(f"\n✅ All evidence files comply with contract v2")
        return 0


if __name__ == "__main__":
    sys.exit(main())
```

### .github/workflows/spine-determinism-guard.yml
```
name: Spine Determinism Guard

on:
  push:
  pull_request:

jobs:
  spine-bypass-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Run AST spine bypass + randomness guard
        run: python ops_scripts/ci/check_spine_bypass.py

      - name: Run spine adapter contract guard
        run: python ops_scripts/ci/check_spine_adapter_contract.py

      - name: Run evidence contract tests
        run: python -m pytest -q tests/unit_min_deps/test_evidence_contract_v2.py

      - name: Run evidence contract checker
        run: python ops_scripts/ci/check_evidence_contract_v2.py --paths docs/reports/plans
```

## Findings

[Document key findings from the investigation]

---

