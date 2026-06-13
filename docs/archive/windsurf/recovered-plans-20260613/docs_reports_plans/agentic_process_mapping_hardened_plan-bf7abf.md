# Agentic Process Mapping Gap Analysis & Remediation Plan (Hardened with Rigorous Testing)

This plan analyzes semantic gaps between the documented agentic architecture and actual repository implementation, providing a phased remediation approach with constitutional-grade testing requirements aligned with `.windsurfrules` §4.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

The agentic process mapping document describes a sophisticated 6-layer architecture with strict sovereignty boundaries, deterministic execution, and comprehensive governance. The actual repository shows 23 critical gaps in implementation completeness, layer separation, and architectural compliance. This hardened plan provides a 4-wave remediation strategy with rigorous testing requirements ensuring every changed logic surface has deterministic tests for success paths, branch paths, negative paths, failure/exception paths, and recovery behavior.

## Constitutional Testing Requirements Integration

All phases MUST comply with `.windsurfrules` §4 testing discipline:

### Mandatory Testing Standards
- **Branch Coverage**: Every changed conditional, guard, threshold, allowlist/denylist, retry path, fallback path, state transition, exception handler, or early return MUST have at least one direct test proving that branch outcome
- **Edge Cases**: Exact boundary values MUST be tested for threshold logic, including equality edges where behavior differs (`>`, `>=`, `<`, `<=`, `==`)
- **Exception Paths**: Every newly introduced `except` block MUST have at least one test that forces that exception path and proves the resulting fail-closed, rollback, escalation, or recovery behavior
- **Negative Controls**: REQUIRED for enforcement logic, fail-closed logic, and invariant guards
- **Determinism**: Same acceptance command MUST be shown stable across two independent invocations for affected decision surfaces
- **No False Confidence**: "No exception raised" is NOT sufficient proof of correctness. Tests MUST assert semantic postconditions, not just execution survival

### Required Test Categories Per Changed Logic Surface
1. **Success path** - Normal operation
2. **Branch paths** - All conditional branches
3. **Negative paths** - Invalid inputs, unauthorized access
4. **Failure/exception paths** - Error handling, recovery
5. **Boundary values** - Min, max, equality edges
6. **Malformed inputs** - Plausible but invalid data
7. **State transitions** - Allowed/disallowed, replay, interruption
8. **Side-effect safety** - Blocked path produces no side-effects
9. **Determinism** - Identical inputs produce identical outputs

### Evidence Requirements
Each phase MUST include in evidence:
- **Branch Inventory**: file path, function/method, branch type, branch condition, expected outcome, exact test name
- **Robustness Matrix**: surface name, ingress path, success/edge/failure/recovery/determinism/side-effect-safety case IDs
- **Defect Model**: exact defect mechanisms tests are intended to catch (off-by-one, guard omission, broad-except masking, stale cache reuse, unsigned side-effect, hidden fallback, order instability, replay drift, duplicate mutation, partial-write leak)

## Critical Gaps Identified (23 Total)

### Gap 1: Layer Sovereignty Violations
**Documented**: Strict layer boundaries with upward mutation forbidden
**Actual**: Cross-layer imports detected, circular dependencies possible
**Impact**: Architecture integrity compromised
**Testing Requirements**: AST-based import validation with negative controls for forbidden patterns, circular dependency detection tests

### Gap 2: L0 Routing Implementation Incomplete
**Documented**: Central traffic control with JIT context loading
**Actual**: Basic structure only, missing election and arbitration logic
**Impact**: No central authority for request routing
**Testing Requirements**: Route selection determinism tests, JIT context loading boundary tests, election logic branch coverage, arbitration conflict resolution matrix tests

### Gap 3: L1 Cognitive Studio Missing RAG Pipeline
**Documented**: Semantic retrieval with C0 informational context
**Actual**: Basic cognition layer, no FAISS integration or embedding pipeline
**Impact**: No semantic retrieval capabilities
**Testing Requirements**: Embedding determinism tests, retrieval ranking stability tests, empty result set handling, malformed metadata handling

### Gap 4: L3 Orchestration Handshake Not Implemented
**Documented**: Sequential handshake, conflict arbitration, deduplication
**Actual**: Skeleton classes only, no orchestration logic
**Impact**: No coordination between agents
**Testing Requirements**: Handshake state transition tests (all 6 states), conflict resolution strategy tests, tool deduplication tests, resource allocation boundary tests, concurrent access tests

### Gap 5: L4 State Management Fragmented
**Documented**: Unified persistence, telemetry ledger, workflow memory
**Actual**: No unified state management system
**Impact**: No audit trails or state consistency
**Testing Requirements**: ACID transaction tests, integrity verification tests (checksum validation), concurrent write tests, stale cache tests, replay mode tests

### Gap 6: L6 Observability Missing
**Documented**: Anomaly detection, RCA, drift monitoring
**Actual**: No observability layer implemented
**Impact**: No system health monitoring
**Testing Requirements**: Anomaly detection threshold tests, false positive/negative tests, RCA category classification tests, drift signal statistical significance tests

### Gap 7: Four Execution Paths Not Implemented
**Documented**: Path A (read-only), B (policy-check), C (direct), D (human review)
**Actual**: No path selection logic implemented
**Impact**: No controlled execution flows
**Testing Requirements**: Path selection determinism tests, path boundary enforcement tests, unauthorized path access negative controls

### Gap 8: Assembly Stage Missing
**Documented**: Sandbox airlock with deterministic composition
**Actual**: No assembly stage implementation
**Impact**: No input validation or sanitization
**Testing Requirements**: Injection detection tests, hostile input vector tests, sanitization effectiveness tests, component validation boundary tests, security hash integrity tests

### Gap 9: Meta-Learning Pipeline Incomplete
**Documented**: 9-stage pipeline with audit→commit flow
**Actual**: Partial implementation in system_learning/
**Impact**: No continuous improvement capability
**Testing Requirements**: Pipeline stage transition tests, audit trail completeness tests, proposal validation tests, activation mechanism tests

### Gap 10: Determinism Guarantees Not Enforced
**Documented**: Mathematical determinism with replay mode
**Actual**: Some determinism components but no guarantees
**Impact**: Non-reproducible behavior
**Testing Requirements**: Replay mode stability tests (same input twice), timestamp independence tests, randomness elimination tests

### Gaps 11-23: [Abbreviated for brevity - full testing requirements apply to all]
- Cryptographic Primitives Missing
- Agent Registry Limited
- Sovereign LLM Gateway Partial
- Universal Write Gateway Isolated
- Classification Kernel SSOT Not Consumed
- Structure Blueprint Not Enforced
- Apps_* Integration Missing
- Tool Allowlist Not Enforced
- Telemetry System Missing
- Healing Subsystem Fragmented
- Configuration Management Decentralized
- Testing Strategy Not Architecture-Aligned
- Documentation-Implementation Drift

## Remediation Plan - 4 Waves (Hardened)

### Wave 1: Foundation & Sovereignty (Phases 1-3)
**Objective**: Establish layer boundaries and SSOT enforcement with constitutional testing

#### Phase 1: Layer Sovereignty Enforcement
**Scope**: AST-based import validation, CI integration, sovereignty tests

**Implementation**:
- Create `LayerSovereigntyEnforcer` with AST-based import analysis
- Implement upward mutation violation detection
- Add layer hierarchy validation (L0-L6 authority levels)
- Create allowed cross-layer import exceptions
- Integrate with CI pipeline

**Testing Requirements (§4 Compliance)**:
1. **Success Path Tests**:
   - `test_extract_layer_from_path_returns_layer_when_valid_path`
   - `test_extract_target_layer_from_import_returns_layer_when_direct_import`
   - `test_check_upward_mutation_returns_false_when_downward_or_same_level`

2. **Branch Path Tests**:
   - `test_check_upward_mutation_returns_true_when_lower_imports_higher`
   - `test_check_upward_mutation_returns_false_when_allowed_exception`
   - `test_extract_layer_returns_none_when_non_layer_path`

3. **Negative Control Tests**:
   - `test_analyze_file_detects_violation_when_upward_mutation`
   - `test_scan_repository_blocks_when_sovereignty_violation`
   - `test_ci_pipeline_fails_when_violations_detected`

4. **Edge Case Tests**:
   - `test_extract_layer_handles_empty_path`
   - `test_extract_layer_handles_malformed_path`
   - `test_check_upward_mutation_handles_unknown_layer`

5. **Exception Path Tests**:
   - `test_analyze_file_logs_warning_when_syntax_error`
   - `test_analyze_file_continues_when_unicode_decode_error`
   - `test_scan_repository_handles_missing_directory`

6. **Determinism Tests**:
   - `test_scan_repository_produces_identical_results_when_run_twice`
   - `test_violation_report_stable_when_same_violations`

7. **Circular Dependency Tests**:
   - `test_validate_circular_dependencies_detects_when_bidirectional_imports`
   - `test_validate_circular_dependencies_returns_empty_when_no_cycles`

**Branch Inventory Required**: All conditionals in `LayerSovereigntyEnforcer` methods

**Robustness Matrix Required**: Import validation, layer extraction, violation detection

**Defect Model**: Guard omission (missing layer check), broad-except masking (silent import failures), order instability (violation report ordering)

**Acceptance Criteria**:
- `python -m pytest tests/guardian/test_layer_sovereignty_enforcer.py -v` exits 0
- `python -m agentic_core.L5_safety.enforcement.layer_sovereignty_enforcer` exits 0
- Branch inventory shows 100% coverage of changed conditionals
- Evidence includes robustness matrix and defect model

#### Phase 2: SSOT Component Integration
**Scope**: Classification Kernel integration, Structure Blueprint activation, path validation

**Implementation**:
- Integrate Classification Kernel across all layers
- Activate Structure Blueprint validation
- Implement runtime path validation checks
- Add naming discipline enforcement

**Testing Requirements (§4 Compliance)**:
1. **Success Path Tests**:
   - `test_classify_file_returns_correct_type_when_valid_agent`
   - `test_validate_path_returns_true_when_within_territory`
   - `test_is_path_allowed_returns_true_when_sovereign_territory`

2. **Branch Path Tests**:
   - `test_classify_file_returns_utility_when_util_suffix`
   - `test_validate_path_returns_false_when_outside_territory`
   - `test_is_path_allowed_handles_depth_enforcement`

3. **Negative Control Tests**:
   - `test_validate_path_rejects_when_traversal_attempt`
   - `test_is_path_allowed_blocks_when_forbidden_pattern`
   - `test_classify_file_fails_closed_when_ambiguous`

4. **Edge Case Tests**:
   - `test_classify_file_handles_empty_file`
   - `test_validate_path_handles_root_level_file`
   - `test_is_path_allowed_handles_exact_depth_boundary`

5. **Malformed Input Tests**:
   - `test_classify_file_handles_syntax_error`
   - `test_validate_path_handles_double_slash`
   - `test_is_path_allowed_handles_non_canonical_path`

6. **Cache Tests**:
   - `test_classify_file_cache_hit_returns_same_result`
   - `test_classify_file_cache_miss_performs_classification`
   - `test_classification_cache_context_clears_on_entry_and_exit`

7. **Determinism Tests**:
   - `test_classify_file_identical_input_produces_identical_output_twice`
   - `test_validate_path_deterministic_across_invocations`

**Branch Inventory Required**: All conditionals in classification and validation logic

**Robustness Matrix Required**: File classification, path validation, cache behavior

**Defect Model**: Stale cache reuse, guard omission (missing path checks), hidden fallback (default classification)

**Acceptance Criteria**:
- `python -m pytest tests/architecture/test_classification_kernel_integration.py -v` exits 0
- `python -m pytest tests/architecture/test_structure_blueprint_validation.py -v` exits 0
- Classification cache hit rate > 80% in evidence
- Branch inventory shows 100% coverage

#### Phase 3: Core Control Spine
**Scope**: L0 Routing completion, Agent Registry enhancement, Gateway integration

**Implementation**:
- Complete L0 Routing implementation (P1-P4 pipeline)
- Enhance Agent Registry with execution profiles
- Integrate Sovereign LLM Gateway
- Connect Universal Write Gateway

**Testing Requirements (§4 Compliance)**:
1. **Success Path Tests**:
   - `test_route_request_returns_decision_when_valid_context`
   - `test_classify_intent_returns_category_when_valid_prompt`
   - `test_evaluate_ruleset_returns_approved_when_healthy_system`

2. **Branch Path Tests**:
   - `test_select_route_mode_returns_read_only_when_query_intent`
   - `test_select_route_mode_returns_human_review_when_low_confidence`
   - `test_select_route_mode_returns_direct_execution_when_high_confidence`
   - `test_select_route_mode_returns_policy_check_when_default`

3. **Negative Control Tests**:
   - `test_route_request_raises_error_when_ruleset_rejects`
   - `test_evaluate_ruleset_returns_rejected_when_unhealthy_system`
   - `test_evaluate_ruleset_returns_rejected_when_rate_limit_exceeded`

4. **Edge Case Tests**:
   - `test_classify_intent_handles_empty_prompt`
   - `test_route_request_handles_missing_l4_state`
   - `test_forecast_tool_requirements_handles_unknown_intent`

5. **State Transition Tests**:
   - `test_route_request_transitions_through_p1_p2_p3_p4_pipeline`
   - `test_route_request_stops_at_p2_when_ruleset_fails`

6. **Determinism Tests**:
   - `test_classify_intent_identical_prompt_produces_identical_category_twice`
   - `test_route_request_deterministic_trace_id_generation`
   - `test_forecast_tool_requirements_stable_for_same_intent`

7. **Matrix Tests** (intent × confidence × request_type):
   - `test_route_mode_selection_matrix_query_high_confidence_user`
   - `test_route_mode_selection_matrix_execution_low_confidence_admin`
   - `test_route_mode_selection_matrix_modification_medium_confidence_system`

**Branch Inventory Required**: All conditionals in routing, classification, ruleset evaluation

**Robustness Matrix Required**: Route selection, intent classification, ruleset evaluation, tool forecasting

**Defect Model**: Order instability (route selection), guard omission (ruleset checks), hidden fallback (default route)

**Acceptance Criteria**:
- `python -m pytest tests/unit/agentic_core/L0_routing/test_central_traffic_control.py -v` exits 0
- Matrix test coverage for all intent × confidence × request_type combinations
- Evidence shows deterministic trace ID generation across two runs
- Branch inventory shows 100% coverage

### Wave 2: Execution Paths & Assembly (Phases 4-6)
**Objective**: Implement controlled execution flows with rigorous validation testing

#### Phase 4: Assembly Stage Implementation
**Scope**: Sandbox airlock, input validation, sanitization, composition

**Testing Requirements (§4 Compliance)**:
1. **Success Path Tests**:
   - `test_validate_component_returns_true_when_valid_content`
   - `test_sanitize_component_removes_script_tags`
   - `test_compose_payload_returns_governed_payload_when_valid_components`

2. **Hostile Input Tests** (REQUIRED):
   - `test_validate_user_prompt_detects_injection_when_sql_injection_attempt`
   - `test_validate_user_prompt_detects_injection_when_command_injection_attempt`
   - `test_block_hostile_input_vectors_neutralizes_when_drop_table_pattern`
   - `test_block_hostile_input_vectors_neutralizes_when_rm_rf_pattern`
   - `test_sanitize_component_removes_when_path_traversal_attempt`

3. **Boundary Tests**:
   - `test_validate_component_rejects_when_size_exceeds_1mb`
   - `test_validate_component_accepts_when_size_exactly_1mb`
   - `test_split_into_atomic_tasks_limits_to_5_tasks`

4. **Exception Path Tests**:
   - `test_validate_component_raises_security_error_when_encoding_invalid`
   - `test_compose_payload_raises_assembly_error_when_hostile_input_detected`

5. **Side-Effect Safety Tests**:
   - `test_validate_component_produces_no_side_effect_when_validation_fails`
   - `test_compose_payload_produces_no_mutation_when_security_check_fails`

6. **Tool Allowlist Tests**:
   - `test_validate_tool_allowlist_allows_when_read_only_path_and_search_tool`
   - `test_validate_tool_allowlist_blocks_when_read_only_path_and_execute_tool`
   - `test_validate_tool_allowlist_allows_when_execute_path_and_create_tool`

7. **Security Hash Tests**:
   - `test_create_security_hash_identical_components_produce_identical_hash_twice`
   - `test_create_security_hash_different_components_produce_different_hash`

**Branch Inventory Required**: All conditionals in validation, sanitization, composition

**Robustness Matrix Required**: Component validation, hostile input detection, tool allowlist validation, security hash generation

**Defect Model**: Unsigned side-effect (mutation before validation), guard omission (missing injection check), broad-except masking (silent validation failures)

**Acceptance Criteria**:
- `python -m pytest tests/unit/agentic_core/L2_execution/assembly/test_sandbox_airlock.py -v` exits 0
- All hostile input patterns blocked (evidence shows 10+ hostile patterns tested)
- Side-effect safety proven for blocked paths
- Branch inventory shows 100% coverage

#### Phase 5: Four Execution Paths
**Scope**: Path A (read-only), B (policy-check), C (direct), D (human review)

**Testing Requirements (§4 Compliance)**:
1. **Path Selection Tests**:
   - `test_determine_execution_path_returns_read_only_when_route_mode_a`
   - `test_determine_execution_path_returns_policy_check_when_route_mode_b`
   - `test_determine_execution_path_returns_execute_directly_when_route_mode_c`
   - `test_determine_execution_path_returns_human_review_when_route_mode_d`

2. **Path Enforcement Tests**:
   - `test_read_only_path_allows_search_tool`
   - `test_read_only_path_blocks_write_tool`
   - `test_execute_path_allows_create_tool`
   - `test_human_review_path_allows_all_tools_for_review`

3. **Mutation Scope Tests**:
   - `test_read_only_path_defines_empty_allowed_paths`
   - `test_execute_path_defines_artifacts_allowed_paths`
   - `test_human_review_path_extends_timeout`

4. **Negative Control Tests**:
   - `test_read_only_path_rejects_mutation_attempt`
   - `test_policy_check_path_blocks_when_policy_fails`
   - `test_execute_path_blocks_when_tool_not_allowlisted`

5. **Determinism Tests**:
   - `test_path_selection_deterministic_for_same_route_mode_twice`
   - `test_mutation_scope_identical_for_same_path_twice`

**Branch Inventory Required**: All conditionals in path selection and enforcement

**Robustness Matrix Required**: Path selection, tool enforcement, mutation scope definition

**Defect Model**: Guard omission (missing path check), hidden fallback (default path), unsigned side-effect (mutation before path check)

**Acceptance Criteria**:
- `python -m pytest tests/unit/agentic_core/L2_execution/test_execution_paths.py -v` exits 0
- All four paths tested with positive and negative controls
- Mutation scope enforcement proven
- Branch inventory shows 100% coverage

#### Phase 6: L3 Orchestration Logic
**Scope**: Sequential handshake, conflict arbitration, tool deduplication

**Testing Requirements (§4 Compliance)**:
1. **State Transition Tests** (REQUIRED for all 6 states):
   - `test_handshake_transitions_initiated_to_validated_when_request_valid`
   - `test_handshake_transitions_validated_to_coordinated_when_resources_available`
   - `test_handshake_transitions_coordinated_to_arbitrated_when_conflicts_detected`
   - `test_handshake_transitions_arbitrated_to_executed_when_conflicts_resolved`
   - `test_handshake_transitions_executed_to_completed_when_execution_finishes`
   - `test_handshake_transitions_to_failed_when_validation_fails`

2. **Disallowed Transition Tests**:
   - `test_handshake_rejects_when_initiated_to_coordinated_without_validation`
   - `test_handshake_rejects_when_repeated_same_transition_twice`

3. **Conflict Resolution Strategy Tests**:
   - `test_resolve_by_weight_selects_highest_weight_agent`
   - `test_resolve_by_role_selects_highest_role_priority_agent`
   - `test_resolve_by_temporal_keeps_existing_allocation`
   - `test_escalate_conflict_logs_escalation_when_unresolvable`

4. **Resource Allocation Tests**:
   - `test_coordinate_resources_allocates_when_no_conflicts`
   - `test_coordinate_resources_detects_conflict_when_resource_already_allocated`
   - `test_complete_handshake_releases_resources_when_completed`

5. **Tool Deduplication Tests**:
   - `test_deduplicate_tools_merges_when_overlapping_tools_detected`
   - `test_deduplicate_tools_returns_no_overlap_when_distinct_tools`

6. **Concurrent Access Tests**:
   - `test_coordinate_resources_handles_duplicate_invocation`
   - `test_coordinate_resources_handles_already_held_resource`

7. **Determinism Tests**:
   - `test_conflict_resolution_deterministic_for_same_conflict_twice`
   - `test_resource_allocation_stable_ordering_when_tie_scores`

**Branch Inventory Required**: All conditionals in handshake, conflict resolution, resource allocation

**Robustness Matrix Required**: State transitions, conflict resolution, resource allocation, tool deduplication

**Defect Model**: Partial-write leak (incomplete state transition), duplicate mutation (double resource allocation), order instability (conflict resolution tie-break)

**Acceptance Criteria**:
- `python -m pytest tests/unit/agentic_core/L3_orchestration/test_sequential_handshake.py -v` exits 0
- All 6 state transitions tested with allowed/disallowed/repeated cases
- Conflict resolution matrix tested for all strategies
- Concurrent access scenarios proven safe
- Branch inventory shows 100% coverage

### Wave 3: State & Observability (Phases 7-9)
**Objective**: Add persistence, monitoring, and learning with ACID guarantees

#### Phase 7: L4 State Management
**Scope**: Unified persistence, telemetry ledger, workflow memory, integrity verification

**Testing Requirements (§4 Compliance)**:
1. **ACID Transaction Tests**:
   - `test_store_state_commits_when_successful`
   - `test_store_state_rolls_back_when_integrity_check_fails`
   - `test_store_state_handles_concurrent_writes_with_versioning`

2. **Integrity Verification Tests**:
   - `test_state_record_verify_integrity_returns_true_when_checksum_valid`
   - `test_state_record_verify_integrity_returns_false_when_checksum_invalid`
   - `test_retrieve_state_logs_warning_when_integrity_check_fails`

3. **Workflow State Transition Tests**:
   - `test_workflow_state_transitions_pending_to_running`
   - `test_workflow_state_transitions_running_to_completed`
   - `test_workflow_state_transitions_running_to_failed_when_error`
   - `test_workflow_state_rejects_invalid_transition`

4. **Telemetry Ledger Tests**:
   - `test_log_telemetry_records_entry_when_valid`
   - `test_query_telemetry_filters_by_trace_id`
   - `test_query_telemetry_filters_by_time_range`
   - `test_query_telemetry_returns_empty_when_no_matches`

5. **Cache Tests**:
   - `test_retrieve_state_cache_miss_queries_database`
   - `test_retrieve_state_stale_cache_refreshes`

6. **Cleanup Tests**:
   - `test_cleanup_old_data_deletes_when_beyond_retention`
   - `test_cleanup_old_data_preserves_when_within_retention`

7. **Determinism Tests**:
   - `test_store_state_identical_record_produces_identical_checksum_twice`
   - `test_query_telemetry_stable_ordering_when_same_filters`

**Branch Inventory Required**: All conditionals in persistence, retrieval, cleanup

**Robustness Matrix Required**: State storage, integrity verification, workflow transitions, telemetry logging

**Defect Model**: Partial-write leak (incomplete transaction), stale cache reuse, duplicate mutation (double write)

**Acceptance Criteria**:
- `python -m pytest tests/unit/agentic_core/L4_state/test_unified_state_manager.py -v` exits 0
- ACID transaction rollback proven
- Integrity verification failure handling proven
- Concurrent write safety proven
- Branch inventory shows 100% coverage

#### Phase 8: L6 Observability
**Scope**: Anomaly detection, RCA, drift monitoring, health scoring

**Testing Requirements (§4 Compliance)**:
1. **Anomaly Detection Threshold Tests**:
   - `test_detect_performance_anomalies_triggers_when_exceeds_threshold`
   - `test_detect_performance_anomalies_silent_when_below_threshold`
   - `test_detect_performance_anomalies_triggers_at_exact_threshold`

2. **False Positive/Negative Tests**:
   - `test_detect_error_rate_anomalies_avoids_false_positive_when_transient_spike`
   - `test_detect_behavioral_anomalies_catches_true_positive_when_sustained_deviation`

3. **RCA Category Classification Tests**:
   - `test_determine_rca_category_returns_syntax_when_syntax_error_in_telemetry`
   - `test_determine_rca_category_returns_import_when_import_error_in_telemetry`
   - `test_determine_rca_category_returns_runtime_when_performance_anomaly`
   - `test_determine_rca_category_returns_unknown_when_insufficient_data`

4. **Drift Detection Tests**:
   - `test_detect_drift_signals_triggers_when_exceeds_2_std_dev`
   - `test_detect_drift_signals_silent_when_within_threshold`
   - `test_detect_drift_signals_updates_baseline_when_significant_shift`

5. **Statistical Significance Tests**:
   - `test_drift_signal_calculates_significance_correctly`
   - `test_anomaly_confidence_scales_with_severity_factor`

6. **Determinism Tests**:
   - `test_detect_performance_anomalies_identical_telemetry_produces_identical_anomalies_twice`
   - `test_calculate_performance_severity_deterministic_for_same_factor`

**Branch Inventory Required**: All conditionals in detection, classification, drift analysis

**Robustness Matrix Required**: Anomaly detection, RCA classification, drift detection, severity calculation

**Defect Model**: Off-by-one (threshold boundaries), order instability (anomaly ordering), hidden fallback (default category)

**Acceptance Criteria**:
- `python -m pytest tests/unit/agentic_core/L6_observability/test_anomaly_detector.py -v` exits 0
- Threshold boundary tests proven (exact, below, above)
- False positive/negative scenarios tested
- Statistical significance calculations verified
- Branch inventory shows 100% coverage

#### Phase 9: Meta-Learning Pipeline
**Scope**: 9-stage pipeline, audit trails, proposal validation, activation

**Testing Requirements (§4 Compliance)**:
1. **Pipeline Stage Transition Tests** (all 9 stages):
   - `test_pipeline_transitions_through_all_9_stages_when_valid`
   - `test_pipeline_stops_at_validation_when_proposal_invalid`
   - `test_pipeline_stops_at_audit_when_audit_fails`

2. **Audit Trail Tests**:
   - `test_audit_trail_records_all_pipeline_stages`
   - `test_audit_trail_immutable_after_commit`

3. **Proposal Validation Tests**:
   - `test_validate_proposal_accepts_when_meets_criteria`
   - `test_validate_proposal_rejects_when_missing_required_field`
   - `test_validate_proposal_rejects_when_conflicts_with_existing`

4. **Activation Tests**:
   - `test_activate_proposal_applies_changes_when_validated`
   - `test_activate_proposal_rolls_back_when_activation_fails`

5. **Determinism Tests**:
   - `test_pipeline_execution_deterministic_for_same_proposal_twice`

**Branch Inventory Required**: All conditionals in pipeline stages, validation, activation

**Robustness Matrix Required**: Stage transitions, proposal validation, activation, rollback

**Defect Model**: Partial-write leak (incomplete activation), guard omission (missing validation), hidden fallback (default approval)

**Acceptance Criteria**:
- `python -m pytest tests/unit/system_learning/test_meta_learning_pipeline.py -v` exits 0
- All 9 stages tested with success/failure paths
- Rollback behavior proven
- Branch inventory shows 100% coverage

### Wave 4: Integration & Hardening (Phases 10-12)
**Objective**: End-to-end integration and production readiness with comprehensive testing

#### Phase 10: Apps_* Integration
**Scope**: Connect apps_lic, apps_rg to core layers, schema emission

**Testing Requirements (§4 Compliance)**:
1. **Integration Tests**:
   - `test_apps_lic_integrates_with_l0_routing`
   - `test_apps_rg_integrates_with_l2_execution`
   - `test_apps_shared_integrates_with_l3_orchestration`

2. **Schema Emission Tests**:
   - `test_apps_lic_emits_standardized_schema`
   - `test_apps_rg_emits_standardized_schema`
   - `test_schema_validation_rejects_malformed_schema`

3. **End-to-End Tests**:
   - `test_user_request_flows_through_all_layers_to_apps_lic`
   - `test_user_request_flows_through_all_layers_to_apps_rg`

**Acceptance Criteria**:
- `python -m pytest tests/integration/test_apps_integration.py -v` exits 0
- End-to-end flow proven for both apps_lic and apps_rg
- Schema validation enforced

#### Phase 11: Cryptographic Integrity
**Scope**: HMAC-SHA256 signatures, hash chaining, replay mode, tamper detection

**Testing Requirements (§4 Compliance)**:
1. **Signature Tests**:
   - `test_sign_packet_generates_valid_signature`
   - `test_verify_signature_accepts_when_valid`
   - `test_verify_signature_rejects_when_invalid`
   - `test_verify_signature_rejects_when_missing`

2. **Hash Chaining Tests**:
   - `test_hash_chain_links_correctly`
   - `test_hash_chain_detects_tampering`

3. **Replay Mode Tests**:
   - `test_replay_mode_produces_identical_output_when_same_input`
   - `test_replay_mode_independent_of_timestamp`

4. **Tamper Detection Tests**:
   - `test_tamper_detection_triggers_when_payload_modified`
   - `test_tamper_detection_triggers_when_signature_modified`

5. **Side-Effect Safety Tests**:
   - `test_verify_signature_produces_no_side_effect_when_verification_fails`

**Branch Inventory Required**: All conditionals in signature, verification, hash chaining

**Robustness Matrix Required**: Signature generation, verification, hash chaining, tamper detection

**Defect Model**: Unsigned side-effect (mutation before verification), guard omission (missing signature check)

**Acceptance Criteria**:
- `python -m pytest tests/unit/agentic_core/L2_execution/test_cryptographic_integrity.py -v` exits 0
- Tamper detection proven
- Replay mode determinism proven
- Side-effect safety proven for verification failures
- Branch inventory shows 100% coverage

#### Phase 12: Production Hardening
**Scope**: Complete determinism guarantees, comprehensive testing, CI/CD enforcement

**Testing Requirements (§4 Compliance)**:
1. **Determinism Guarantee Tests**:
   - `test_full_system_deterministic_across_two_complete_runs`
   - `test_no_timestamp_dependencies_in_decision_logic`
   - `test_no_randomness_in_routing_or_classification`

2. **CI/CD Enforcement Tests**:
   - `test_ci_pipeline_fails_when_sovereignty_violation`
   - `test_ci_pipeline_fails_when_test_failure`
   - `test_ci_pipeline_fails_when_evidence_contract_violation`

3. **Comprehensive Integration Tests**:
   - `test_end_to_end_flow_all_four_paths`
   - `test_end_to_end_flow_with_conflict_resolution`
   - `test_end_to_end_flow_with_anomaly_detection`

**Acceptance Criteria**:
- `python -m pytest -q --color=no` (full suite) exits 0
- `python ops_scripts/ci/run_contract_gates.py` exits 0
- Evidence shows determinism across two independent full-system runs
- All 23 gaps addressed with proving tests

## Implementation Priority Matrix

### High Priority (Waves 1-2) - 6-
- Layer sovereignty enforcement with AST-based validation
- SSOT component integration with cache testing
- Core control spine with matrix testing
- Assembly stage with hostile input testing
- Four execution paths with negative controls
- L3 orchestration with state transition testing

### Medium Priority (Wave 3) - 4-
- L4 state management with ACID testing
- L6 observability with threshold boundary testing
- Meta-learning pipeline with rollback testing

### Lower Priority (Wave 4) - 3-
- Apps_* integration with end-to-end testing
- Cryptographic integrity with tamper detection
- Production hardening with determinism guarantees

## Success Metrics (Constitutional Compliance)

### Technical Metrics
- Zero cross-layer sovereignty violations (AST-verified)
- 100% SSOT component usage (import analysis)
- Complete execution path coverage (all 4 paths tested)
- Full determinism guarantees (replay mode proven)
- Branch inventory completeness (100% changed conditionals mapped)

### Testing Metrics
- Every changed logic surface has success/branch/negative/failure/recovery tests
- Every exception handler has forced exception path test
- Every threshold has boundary value tests (exact, below, above)
- Every fail-closed claim has proving automated test
- Every state transition has allowed/disallowed/repeated tests
- Robustness matrix complete for all changed surfaces
- Defect model documented for all phases

### Operational Metrics
- Sub-second request routing (performance tests)
- 99.9% system availability (anomaly detection tests)
- Complete audit trail coverage (telemetry tests)
- Real-time anomaly detection (threshold tests)

### Architectural Metrics
- Documentation-implementation alignment (gap closure verified)
- Layer boundary compliance (sovereignty tests)
- Component integration completeness (integration tests)
- Test coverage for architectural rules (guardian tests)

## Evidence Requirements Per Phase

Each phase MUST produce evidence file in `docs/reports/plans/` with:

1. **Standard Sections** (§2 compliance):
   - `# <Phase Title>`
   - `## Scope`
   - `## CODE_COMMIT` (40-hex hash)
   - `## EVIDENCE_COMMIT` (40-hex hash or PENDING)
   - `## FILES_CHANGED_CODE`
   - `## FILES_CHANGED_EVIDENCE`
   - `## INSPECTED_FILES`
   - Command sections with full stdout, `EXIT CODE: N` only if N≠0

2. **Testing Sections** (§4 compliance):
   - `## BRANCH_INVENTORY` - All changed conditionals mapped to tests
   - `## ROBUSTNESS_MATRIX` - All changed surfaces with case IDs
   - `## DEFECT_MODEL` - Exact defect mechanisms being prevented
   - `## TEST_EXECUTION` - pytest output showing collected/executed counts
   - `## DETERMINISM_VERIFICATION` - Same command run twice with identical output

3. **Acceptance Verification**:
   - All acceptance criteria commands shown with exit code 0
   - Branch inventory shows 100% coverage
   - No contradictions (failure marker + success marker in same output)
   - ASCII-only (no bytes > 0x7F)

## Risk Mitigation (Testing-Focused)

### Technical Risks
- **Circular Dependencies**: AST-based detection with negative control tests
- **Performance Impact**: Performance regression tests with threshold boundaries
- **Complexity**: Modular implementation with integration tests at seams

### Testing Risks
- **False Confidence**: Branch-intent assertions required, not just statement coverage
- **Hidden Failures**: Negative controls required for all enforcement logic
- **Incomplete Coverage**: Branch inventory MUST show 100% of changed conditionals
- **Weak Assertions**: Semantic postconditions required, not just "no exception"

### Operational Risks
- **Service Disruption**: Rollback tests required for all state transitions
- **Data Loss**: ACID transaction tests with rollback verification
- **Security Breaches**: Hostile input tests with side-effect safety verification

## Timeline Estimate

- **Wave 1**: 6- (Foundation + rigorous testing)
- **Wave 2**: 4- (Execution paths + hostile input testing)
- **Wave 3**: 4- (State & observability + threshold testing)
- **Wave 4**: 3- (Integration + determinism verification)

**Total Estimated Duration**: 17- (increased from 14- due to constitutional testing requirements)

## Resource Requirements

### Development Team
- 2-3 senior developers (core architecture + test design)
- 1-2 mid-level developers (apps integration + test implementation)
- 1 QA engineer (test review + edge case identification)
- 1 DevOps engineer (CI/CD + evidence automation)

### Testing Infrastructure
- Deterministic test environment (no time-based behavior)
- Hostile input corpus (10+ attack patterns per surface)
- Replay mode infrastructure (identical runs verification)
- Evidence automation (branch inventory generation)

## Conclusion

The gap between documented architecture and actual implementation is significant but addressable with constitutional-grade testing discipline. The 4-wave remediation plan provides a structured approach to achieve architectural compliance while ensuring every changed logic surface has deterministic tests for success paths, branch paths, negative paths, failure/exception paths, and recovery behavior.

**Critical Success Factors**:
1. **Wave 1 Foundation**: Complete layer sovereignty and SSOT enforcement before proceeding
2. **Testing Discipline**: Every changed conditional MUST have proving test before phase completion
3. **Evidence Quality**: Branch inventory, robustness matrix, and defect model REQUIRED for all phases
4. **No False Confidence**: Statement coverage alone is insufficient; branch-intent assertions required
5. **Determinism First**: Replay mode stability proven for all decision surfaces

**Constitutional Compliance**: All phases align with `.windsurfrules` §4 testing requirements, ensuring no defect can recur through the same ingress path and every fail-closed claim has proving automated test.

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

