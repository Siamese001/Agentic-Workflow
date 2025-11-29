# WINDSURF VALIDATION SUMMARY REPORT

**Overall Compliance: 0.0%** (0/377 keys)

## Category Breakdown

| Category | Passed | Total | Failed | Pass Rate |
|----------|--------|-------|--------|-----------|
| agent_ops | 0 | 9 | 9 | 0.0% |
| agentic_core_structure | 0 | 27 | 27 | 0.0% |
| apps_layer | 0 | 16 | 16 | 0.0% |
| cache_policy | 0 | 17 | 17 | 0.0% |
| deployment | 0 | 7 | 7 | 0.0% |
| engine_structure | 0 | 20 | 20 | 0.0% |
| evaluation | 0 | 9 | 9 | 0.0% |
| import_and_lint | 0 | 8 | 8 | 0.0% |
| layer_purity_L1 | 0 | 18 | 18 | 0.0% |
| layer_purity_L2 | 0 | 20 | 20 | 0.0% |
| layer_purity_L3 | 0 | 18 | 18 | 0.0% |
| layer_purity_L4 | 0 | 14 | 14 | 0.0% |
| layer_purity_L5 | 0 | 13 | 13 | 0.0% |
| mcp | 0 | 5 | 5 | 0.0% |
| observability | 0 | 14 | 14 | 0.0% |
| prompt_system | 0 | 22 | 22 | 0.0% |
| pytest | 0 | 3 | 3 | 0.0% |
| rag_kg_temporal | 0 | 8 | 8 | 0.0% |
| root_structure | 0 | 24 | 24 | 0.0% |
| safety | 0 | 9 | 9 | 0.0% |
| schemas | 0 | 18 | 18 | 0.0% |
| tests_L1 | 0 | 8 | 8 | 0.0% |
| tests_L2 | 0 | 9 | 9 | 0.0% |
| tests_L3 | 0 | 9 | 9 | 0.0% |
| tests_L4 | 0 | 8 | 8 | 0.0% |
| tests_L5 | 0 | 8 | 8 | 0.0% |
| tests_global_tree | 0 | 19 | 19 | 0.0% |
| tests_misc | 0 | 10 | 10 | 0.0% |
| zero_loss | 0 | 7 | 7 | 0.0% |

## Failed Keys (377 total)

### agentic_core_structure (27 failures)

- ❌ agentic_core_exists
- ❌ l1_planning_folder_exists
- ❌ l1_planning_planners_folder_exists
- ❌ l1_planning_schemas_folder_exists
- ❌ l1_planning_utils_folder_exists
- ❌ l2_execution_folder_exists
- ❌ l2_execution_tools_folder_exists
- ❌ l2_execution_engines_folder_exists
- ❌ l2_execution_wrappers_folder_exists
- ❌ l2_execution_utils_folder_exists
- ❌ l3_orchestration_folder_exists
- ❌ l3_orchestration_framework_folder_exists
- ❌ l3_orchestration_engines_folder_exists
- ❌ l3_orchestration_utils_folder_exists
- ❌ l4_memory_state_folder_exists
- ❌ l4_memory_state_providers_folder_exists
- ❌ l4_memory_state_temporal_folder_exists
- ❌ l4_memory_state_mappings_folder_exists
- ❌ l5_safety_folder_exists
- ❌ l5_safety_filters_folder_exists
- ❌ l5_safety_policies_folder_exists
- ❌ l5_safety_validators_folder_exists
- ❌ agentic_core_has_no_tests
- ❌ agentic_core_has_no_cache_dirs
- ❌ agentic_core_has_init_files_where_required
- ❌ agentic_core_subfolders_exact_match_allowed_set
- ❌ agentic_core_no_unexpected_subfolders

### root_structure (24 failures)

- ❌ root_exists_agentic_core
- ❌ root_exists_apps
- ❌ root_exists_prompt_governance
- ❌ root_exists_observability
- ❌ root_exists_schemas
- ❌ root_exists_tests
- ❌ root_exists_runtime
- ❌ depth_max_3
- ❌ no_directory_level_4
- ❌ no_empty_directories
- ❌ folders_must_contain_files
- ❌ no_unexpected_root_folders
- ❌ no_code_at_root
- ❌ no_tests_at_root
- ❌ no_cache_at_root
- ❌ valid_agentic_core_tree
- ❌ valid_apps_tree
- ❌ valid_prompt_governance_tree
- ❌ valid_schemas_tree
- ❌ valid_tests_tree
- ❌ valid_runtime_tree
- ❌ valid_observability_tree
- ❌ root_subfolders_exact_match_allowed_set
- ❌ root_no_unexpected_subfolders

### prompt_system (22 failures)

- ❌ prompt_governance_folder_exists
- ❌ prompt_manifests_folder_exists
- ❌ prompt_acls_folder_exists
- ❌ prompt_definitions_folder_exists
- ❌ prompt_governance_metadata_folder_exists
- ❌ prompt_versions_folder_exists
- ❌ prompt_layered_injection_bundles_folder_exists
- ❌ prompt_domains_folder_exists
- ❌ prompt_injection_policies_folder_exists
- ❌ all_prompts_in_prompt_governance
- ❌ prompts_schema_first
- ❌ prompts_versioned
- ❌ prompt_registry_present
- ❌ prompt_registry_resolves_all_prompts
- ❌ prompt_builder_uses_injection_v5
- ❌ prompt_builder_applies_layered_injection
- ❌ prompt_builder_attaches_schemas
- ❌ prompt_builder_attaches_examples
- ❌ no_inline_prompts_in_L1_L5
- ❌ no_prompt_files_in_agentic_core
- ❌ prompt_governance_subfolders_exact_match_allowed_set
- ❌ prompt_governance_no_unexpected_subfolders

### engine_structure (20 failures)

- ❌ l2_resume_engine_exists
- ❌ l2_outreach_engine_exists
- ❌ l3_resume_engine_exists
- ❌ l3_outreach_engine_exists
- ❌ resume_engine_parallel_to_outreach_engine
- ❌ engines_use_allowed_shared_sources_only
- ❌ no_cross_engine_imports_l2
- ❌ no_cross_engine_imports_l3
- ❌ no_shared_business_logic
- ❌ resume_engine_has_clear_entrypoints
- ❌ outreach_engine_has_clear_entrypoints
- ❌ resume_engine_has_adapters
- ❌ outreach_engine_has_adapters
- ❌ resume_engine_has_pipelines
- ❌ outreach_engine_has_pipelines
- ❌ engines_have_separate_config
- ❌ l2_engines_subfolders_exact_match_allowed_set
- ❌ l2_engines_no_unexpected_subfolders
- ❌ l3_engines_subfolders_exact_match_allowed_set
- ❌ l3_engines_no_unexpected_subfolders

### layer_purity_L2 (20 failures)

- ❌ L2_exists
- ❌ L2_no_import_L3
- ❌ L2_no_import_L4
- ❌ L2_no_import_L5
- ❌ L2_no_import_apps
- ❌ L2_no_import_prompt_governance
- ❌ L2_tools_only_call_external_apis_or_L4
- ❌ L2_no_planning_logic
- ❌ L2_no_inline_prompts
- ❌ L2_engines_no_planning_logic
- ❌ L2_tools_folder_has_init
- ❌ L2_engines_folder_has_init
- ❌ L2_wrappers_folder_has_init
- ❌ L2_utils_folder_has_init
- ❌ L2_tools_declare_failure_modes
- ❌ L2_tools_declare_timeouts
- ❌ L2_tools_declare_retries
- ❌ L2_tools_declare_circuit_breakers
- ❌ L2_subfolders_exact_match_allowed_set
- ❌ L2_no_unexpected_subfolders

### tests_global_tree (19 failures)

- ❌ tests_root_exists
- ❌ single_global_tests_tree
- ❌ tests_L1_planning_folder_exists
- ❌ tests_L2_execution_folder_exists
- ❌ tests_L3_orchestration_folder_exists
- ❌ tests_L4_memory_state_folder_exists
- ❌ tests_L5_safety_folder_exists
- ❌ tests_integration_folder_exists
- ❌ tests_e2e_folder_exists
- ❌ tests_regression_folder_exists
- ❌ tests_fixtures_folder_exists
- ❌ tests_data_folder_exists
- ❌ tests_helpers_file_present
- ❌ no_tests_in_agentic_core
- ❌ no_tests_in_apps
- ❌ no_tests_at_root
- ❌ no_alternate_test_trees
- ❌ tests_root_subfolders_exact_match_allowed_set
- ❌ tests_root_no_unexpected_subfolders

### layer_purity_L1 (18 failures)

- ❌ L1_exists
- ❌ L1_no_import_L2
- ❌ L1_no_import_L3
- ❌ L1_no_import_L4
- ❌ L1_no_import_L5
- ❌ L1_no_import_apps
- ❌ L1_no_import_runtime
- ❌ L1_no_import_prompt_governance
- ❌ L1_no_direct_tool_calls
- ❌ L1_no_state_mutation
- ❌ L1_no_inline_prompts
- ❌ L1_planners_folder_has_init
- ❌ L1_schemas_folder_has_init
- ❌ L1_utils_folder_has_init
- ❌ L1_planners_are_pure_functions
- ❌ L1_only_imports_allowed_libraries
- ❌ L1_subfolders_exact_match_allowed_set
- ❌ L1_no_unexpected_subfolders

### layer_purity_L3 (18 failures)

- ❌ L3_exists
- ❌ L3_no_import_L4
- ❌ L3_no_import_L5
- ❌ L3_no_import_apps
- ❌ L3_no_direct_tool_calls
- ❌ L3_no_planning_logic
- ❌ L3_orchestration_framework_present
- ❌ L3_dag_nodes_have_input_schema
- ❌ L3_dag_nodes_have_output_schema
- ❌ L3_dag_nodes_have_failure_modes
- ❌ L3_self_correction_layer_present
- ❌ L3_self_correction_deterministic
- ❌ L3_engines_no_business_logic
- ❌ L3_framework_folder_has_init
- ❌ L3_engines_folder_has_init
- ❌ L3_utils_folder_has_init
- ❌ L3_subfolders_exact_match_allowed_set
- ❌ L3_no_unexpected_subfolders

### schemas (18 failures)

- ❌ schemas_root_exists
- ❌ schemas_shared_folder_exists
- ❌ schemas_l1_planning_folder_exists
- ❌ schemas_l2_execution_folder_exists
- ❌ schemas_l3_orchestration_folder_exists
- ❌ schemas_l4_memory_folder_exists
- ❌ schemas_l5_safety_folder_exists
- ❌ schemas_follow_tree
- ❌ schema_files_have_versions
- ❌ schema_versions_semantic
- ❌ no_schema_breaking_changes
- ❌ all_schemas_valid_jsonschema
- ❌ pydantic_models_match_schemas
- ❌ cross_layer_interfaces_declared
- ❌ every_public_interface_has_schema
- ❌ schema_regression_tests_exist
- ❌ schemas_root_subfolders_exact_match_allowed_set
- ❌ schemas_root_no_unexpected_subfolders

### cache_policy (17 failures)

- ❌ runtime_cache_root_exists
- ❌ runtime_cache_has_pycache
- ❌ runtime_cache_has_venv
- ❌ runtime_cache_has_mypy
- ❌ runtime_cache_has_pytest
- ❌ runtime_cache_has_ruff
- ❌ runtime_cache_has_tmp
- ❌ no_cache_outside_canonical_root
- ❌ no_cache_in_agentic_core
- ❌ no_cache_in_apps
- ❌ no_cache_in_tests
- ❌ no_cache_in_prompt_governance
- ❌ no_cache_in_schemas
- ❌ cache_alias_mapping_correct
- ❌ allowed_cache_subdirs_only
- ❌ runtime_cache_subfolders_exact_match_allowed_set
- ❌ runtime_cache_no_unexpected_subfolders

### apps_layer (16 failures)

- ❌ apps_folder_exists
- ❌ apps_resume_engine_folder_exists
- ❌ apps_outreach_engine_folder_exists
- ❌ apps_resume_engine_has_adapters
- ❌ apps_outreach_engine_has_adapters
- ❌ apps_resume_engine_has_pipelines
- ❌ apps_outreach_engine_has_pipelines
- ❌ apps_entrypoints_are_thin
- ❌ no_L1_logic_in_apps
- ❌ no_L2_logic_in_apps
- ❌ no_L3_logic_in_apps
- ❌ no_L4_logic_in_apps
- ❌ no_L5_logic_in_apps
- ❌ no_tests_in_apps
- ❌ apps_subfolders_exact_match_allowed_set
- ❌ apps_no_unexpected_subfolders

### layer_purity_L4 (14 failures)

- ❌ L4_exists
- ❌ L4_no_import_L1_L2_L3
- ❌ L4_providers_structure_valid
- ❌ L4_temporal_structure_valid
- ❌ L4_mappings_structure_valid
- ❌ L4_apis_exposed_for_memory_only
- ❌ L4_no_direct_tool_calls
- ❌ L4_no_inline_prompts
- ❌ L4_providers_folder_has_init
- ❌ L4_temporal_folder_has_init
- ❌ L4_mappings_folder_has_init
- ❌ L4_temporal_validity_fields_present
- ❌ L4_subfolders_exact_match_allowed_set
- ❌ L4_no_unexpected_subfolders

### observability (14 failures)

- ❌ observability_root_exists
- ❌ observability_trace_folder_exists
- ❌ observability_metrics_folder_exists
- ❌ observability_logs_folder_exists
- ❌ observability_cost_folder_exists
- ❌ event_model_fields_complete
- ❌ events_exportable_to_trace
- ❌ events_exportable_to_metrics
- ❌ events_exportable_to_logs
- ❌ no_pii_in_logs
- ❌ otel_trace_compliant
- ❌ agent_events_include_layer_and_recursion_depth
- ❌ observability_root_subfolders_exact_match_allowed_set
- ❌ observability_root_no_unexpected_subfolders

### layer_purity_L5 (13 failures)

- ❌ L5_exists
- ❌ L5_no_import_L1_L2_L3_L4
- ❌ L5_safety_filters_present
- ❌ L5_safety_policies_present
- ❌ L5_safety_validators_present
- ❌ L5_no_business_logic
- ❌ L5_no_inline_prompts
- ❌ L5_filters_folder_has_init
- ❌ L5_policies_folder_has_init
- ❌ L5_validators_folder_has_init
- ❌ L5_safety_policies_engine_specific
- ❌ L5_subfolders_exact_match_allowed_set
- ❌ L5_no_unexpected_subfolders

### tests_misc (10 failures)

- ❌ integration_tests_resume_exists
- ❌ integration_tests_outreach_exists
- ❌ e2e_tests_resume_exists
- ❌ e2e_tests_outreach_exists
- ❌ regression_tests_resume_exists
- ❌ regression_tests_outreach_exists
- ❌ fixtures_structure_valid
- ❌ data_samples_valid
- ❌ fixtures_and_data_no_pii
- ❌ tests_use_common_fixtures_where_possible

### tests_L2 (9 failures)

- ❌ tests_L2_execution_resume_exists
- ❌ tests_L2_execution_outreach_exists
- ❌ tests_L2_execution_tools_exists
- ❌ every_L2_executor_has_test
- ❌ every_tool_has_test
- ❌ L2_tests_cover_tool_failure_modes
- ❌ L2_tests_cover_retries_and_timeouts
- ❌ tests_L2_execution_subfolders_exact_match_allowed_set
- ❌ tests_L2_execution_no_unexpected_subfolders

### tests_L3 (9 failures)

- ❌ tests_L3_orchestration_resume_exists
- ❌ tests_L3_orchestration_outreach_exists
- ❌ tests_L3_orchestration_framework_exists
- ❌ every_L3_engine_has_test
- ❌ every_dag_node_has_test
- ❌ L3_tests_cover_self_correction
- ❌ L3_tests_cover_arbiter_behavior
- ❌ tests_L3_orchestration_subfolders_exact_match_allowed_set
- ❌ tests_L3_orchestration_no_unexpected_subfolders

### safety (9 failures)

- ❌ safety_filters_active
- ❌ pii_filter_active
- ❌ inj_shield_active
- ❌ hallucination_detector_active
- ❌ safety_runs_on_all_outbound_content
- ❌ safety_runs_on_all_mutating_actions
- ❌ safety_policies_engine_specific
- ❌ safety_logs_non_sensitive_summaries
- ❌ safety_guardrails_documented

### agent_ops (9 failures)

- ❌ cost_tracking_defined
- ❌ latency_tracking_defined
- ❌ tool_reliability_metrics_defined
- ❌ model_reliability_metrics_defined
- ❌ error_taxonomy_defined
- ❌ canary_scenarios_exist
- ❌ agent_ops_feeds_metrics
- ❌ agent_ops_feeds_logs
- ❌ agent_ops_monitors_token_usage

### evaluation (9 failures)

- ❌ golden_datasets_present
- ❌ golden_datasets_cover_core_flows
- ❌ llm_as_judge_defined
- ❌ llm_as_judge_evaluates_quality
- ❌ regression_suite_defined
- ❌ regression_tests_all_pass
- ❌ toolpath_evaluation_defined
- ❌ toolpath_evaluation_passed
- ❌ evals_block_merges_on_regression

### tests_L1 (8 failures)

- ❌ tests_L1_planning_resume_exists
- ❌ tests_L1_planning_outreach_exists
- ❌ tests_L1_planning_shared_exists
- ❌ every_L1_planner_has_test
- ❌ L1_planning_tests_cover_core_flows
- ❌ L1_planning_tests_follow_naming_convention
- ❌ tests_L1_planning_subfolders_exact_match_allowed_set
- ❌ tests_L1_planning_no_unexpected_subfolders

### tests_L4 (8 failures)

- ❌ tests_L4_memory_state_temporal_exists
- ❌ tests_L4_memory_state_providers_exists
- ❌ tests_L4_memory_state_mappings_exists
- ❌ every_L4_provider_has_test
- ❌ every_L4_mapping_has_test
- ❌ L4_tests_cover_temporal_validity
- ❌ tests_L4_memory_state_subfolders_exact_match_allowed_set
- ❌ tests_L4_memory_state_no_unexpected_subfolders

### tests_L5 (8 failures)

- ❌ tests_L5_safety_filters_exists
- ❌ tests_L5_safety_policies_exists
- ❌ tests_L5_safety_validators_exists
- ❌ every_L5_policy_has_test
- ❌ L5_tests_cover_blocking_behavior
- ❌ L5_tests_cover_false_positive_rates
- ❌ tests_L5_safety_subfolders_exact_match_allowed_set
- ❌ tests_L5_safety_no_unexpected_subfolders

### import_and_lint (8 failures)

- ❌ no_import_errors
- ❌ ruff_zero_errors
- ❌ mypy_zero_blockers
- ❌ no_circular_imports
- ❌ import_dag_respected
- ❌ L4_imports_no_L1_L2_L3
- ❌ L5_imports_no_L1_L2_L3_L4
- ❌ no_cross_engine_imports_anywhere

### rag_kg_temporal (8 failures)

- ❌ rag_pipeline_defined
- ❌ kg_pipeline_defined
- ❌ temporal_kg_valid
- ❌ rag_calls_are_deterministic
- ❌ kg_lookups_are_deterministic
- ❌ temporal_validity_rules_defined
- ❌ rag_evaluated_with_golden_queries
- ❌ temporal_events_have_valid_at_invalid_at

### zero_loss (7 failures)

- ❌ zero_loss_dag_execution_completes
- ❌ dags_valid_and_acyclic
- ❌ no_behavior_loss_detected
- ❌ no_capability_loss_detected
- ❌ conflict_merges_preserved_behavior
- ❌ no_deleted_tests_without_reason
- ❌ no_deleted_schemas_without_reason

### deployment (7 failures)

- ❌ rest_endpoints_secure
- ❌ authn_authz_enforced
- ❌ environment_separation_valid
- ❌ model_versions_pinned
- ❌ rollback_strategy_defined
- ❌ session_management_defined
- ❌ secrets_not_hardcoded

### mcp (5 failures)

- ❌ mcp_tools_schema_defined
- ❌ mcp_access_respects_acls
- ❌ mcp_interactions_observable
- ❌ no_direct_external_calls_outside_mcp
- ❌ mcp_tools_registered_per_environment

### pytest (3 failures)

- ❌ pytest_zero_failures
- ❌ tests_run_fast_enough
- ❌ tests_cover_core_error_paths

