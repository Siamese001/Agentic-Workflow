# Semantic Gap Analysis - Agentic Architecture Major Arteries

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

**Total Gaps Identified:** 1239
**High Priority:** 593
**Medium Priority:** 634
**Low Priority:** 12
**Parse Failures:** 3

## Analysis Methodology

This analysis traces actual execution flows through L0-L6 layers using AST-based
code scanning to identify where architectural intent (lower latency, deterministic
lookups, cache-first patterns) diverges from implementation reality.

**Approach:**
1. Map critical hot paths across each layer
2. AST scan for import statements and cache usage patterns
3. Detect prompt assemblers and score canonical slot coverage for S0/D0/I0/C0/U0
4. Check for manifest-hash and boundary-snapshot evidence on prompt execution paths
5. Verify architecture SSOT components exist and expose expected contract markers
6. Scan layer connection integrity for upward imports, gateway bypasses, and non-L2 mutation risks
7. Audit Elevator Shaft, governance stamp, and airlock contract markers
8. Check embedding sovereignty and meta-learning pipeline contracts
9. Identify missing wirings between cache modules and consumers
10. Categorize gaps by layer, artery, and priority
11. Surface parse failures explicitly instead of silently dropping files from analysis

## Architecture Component Presence

| Component | File | Exists | Signals Present |
|-----------|------|--------|-----------------|
| sovereign_gateway | `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | yes | GenerationRequest, GenerationResponse, route_generation |
| write_gateway | `agentic_core/L2_execution/tools/write_gateway.py` | yes | WriteAmplificationError, WriteSizeCapError |
| classification_kernel | `agentic_core/L5_safety/core_kernel/classification_kernel.py` | yes | classify_file_standalone |
| agent_registry | `agentic_core/agents/agent_registry.py` | yes | AGENT_REGISTRY, AgentExecutionProfile |
| meta_learning_pipeline | `agentic_core/utils/meta_learning_engine_util.py` | yes | MetaLearningStorage |

## Prompt Taxonomy Coverage

| File | Slot Coverage | Manifest Hash | Boundary Snapshot |
|------|---------------|---------------|-------------------|
| `agentic_core/L0_routing/engines/assembly_stage.py` | S0=present, D0=present, I0=present, C0=present, U0=present | yes | no |
| `agentic_core/L0_routing/engines/execution_orchestrator.py` | S0=missing, D0=present, I0=missing, C0=missing, U0=missing | no | no |
| `agentic_core/L0_routing/scripts/class_info.py` | S0=missing, D0=present, I0=missing, C0=present, U0=missing | no | no |
| `agentic_core/L1_cognition/engines/prompt_artifact_cache.py` | S0=present, D0=present, I0=present, C0=present, U0=missing | no | no |
| `agentic_core/L2_execution/enforcement/boundary_verifier.py` | S0=missing, D0=missing, I0=present, C0=missing, U0=missing | no | no |
| `agentic_core/L2_execution/engines/execution_gateway.py` | S0=missing, D0=missing, I0=present, C0=missing, U0=missing | no | no |
| `agentic_core/L2_execution/healers/qwen_vllm_inference.py` | S0=present, D0=missing, I0=missing, C0=missing, U0=missing | no | no |
| `agentic_core/L2_execution/types/execution_trace_types.py` | S0=missing, D0=missing, I0=present, C0=missing, U0=missing | no | no |
| `agentic_core/L2_execution/types/sandbox_envelope_types.py` | S0=missing, D0=missing, I0=present, C0=missing, U0=missing | no | no |

## Layer Connection Integrity

| File | Layer | Upward Imports | Direct Provider Imports | Embedding Mentions | Governance Mentions |
|------|-------|----------------|-------------------------|--------------------|---------------------|
| `agentic_core/L0_routing/__init__.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/config/__init__.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/config/path_constants.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/config/structure_blueprint_data.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/__init__.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/boot_sequence.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/boot_sequence_enforcer.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/boundary_contracts.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/crypto_trust_contracts.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/execution_gateway.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/governance_contracts.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/mutation_prohibition.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/runtime_guard.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/runtime_mutation_guard.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/trace_id_generator.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/traceability_contracts.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/enforcement/vigilance_routing.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/engines/__init__.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/engines/assembly_stage.py` | L0 | - | - | 1 | 0 |
| `agentic_core/L0_routing/engines/escalation_router.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/engines/execution_orchestrator.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/engines/path_router.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/engines/reasoning_policy_engine.py` | L0 | - | - | 2 | 0 |
| `agentic_core/L0_routing/engines/shadow_router_classifier.py` | L0 | - | agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types | 0 | 0 |
| `agentic_core/L0_routing/engines/shadow_routing_wiring.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/engines/timeshift_router.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/legacy_agent_name_allowlist.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/meta_control/__init__.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/meta_control/config_store.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/meta_control/config_store_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/meta_control/meta_apply.py` | L0 | - | - | 0 | 6 |
| `agentic_core/L0_routing/meta_control/meta_apply_ops.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/meta_control/meta_learning_bus.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/reasoning/RootCustomsAgent.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/reasoning/__init__.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/__init__.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/action_capability.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/add_dataclass_to_agents_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/add_subatomic_safe_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/add_subatomic_testing_to_agents_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/add_subatomic_tests_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/agent_analysis_config.py` | L0 | - | - | 3 | 0 |
| `agentic_core/L0_routing/scripts/agent_capability_supplement_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/agent_validation_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/aggressive_dedup_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/align_tests_structure_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/archive_duplicate_tests_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/archive_duplicates_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/auto_remediate_signatures_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/base_tool.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/base_tool_script.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/bloat_analysis_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/bulk_hierarchy_heal_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/bulk_mcp_harden_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/c_c_measurement.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/cache_data_access_get_info_request_init_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/cache_data_access_init_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/cache_init_util.py` | L0 | - | - | 1 | 0 |
| `agentic_core/L0_routing/scripts/call_personalization_api_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/check_duplicate_filenames_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/check_from_utils_duplicates_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/check_protected_files_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/check_rglob_usage_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/check_sovereign_base_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/check_syntax_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/chunk_type.py` | L0 | - | - | 3 | 0 |
| `agentic_core/L0_routing/scripts/class_info.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/code_entity.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/collision_resolver.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/colors.py` | L0 | - | - | 1 | 0 |
| `agentic_core/L0_routing/scripts/compare_archive_to_current_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/compare_autonomy_guardian_files_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/compare_ui_components_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/compliance_gate_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/comprehensive_archive_check_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/core_synthesis_executor.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/count_territories_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/coverage.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/dashboard_ssot_definitions_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/debris_hunter.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/debug_drilldown_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/debug_invocation_pipeline_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/debug_target_mismatch_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/delete_duplicates_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/demo_cli_functionality_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/diagnose_syntax_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/disposition.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/drift.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/emoji_fixer.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/error_handler.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/execute_safe_deletion_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/execute_ssot.py` | L0 | - | - | 25 | 0 |
| `agentic_core/L0_routing/scripts/execute_ssot_entrypoint.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/execution.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/execution_context.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/extract_agent_duplicates_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/extract_net.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/extract_unique_content_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/file_analysis.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_agents_in_low_heal_territories_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_base_class_agents_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_corrupted_files_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_infrastructure_target_issue_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_low_heal_territories_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_low_typed_documented_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_missing_agents_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_missing_invocation_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_missing_invocations_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_non_hardened_l0_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_open_heal_invocations_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_real_duplicates_v2_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/find_remaining_missing_heal_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/fission_executor_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/flatten_scripts_directory_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/forensic_discovery_prep.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/forward_rolling_facade.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/full_agent_discovery.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/function_tool.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/gatekeeper_lock_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/generate_dashboard_ssot_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/handler.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/hardened_anti_pattern_visitor.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/hardened_orchestrator_wrapper_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/heal_schema_visitor.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/identify_agents_without_tests_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/identify_low_quality_agents_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/investigate_overlaps_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/investigate_sovereign_base_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/layer_summary_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/list_layer_agents_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/logic_data_access_init_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/logic_init_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/populate_ssot_folders_util.py` | L0 | - | - | 2 | 0 |
| `agentic_core/L0_routing/scripts/reasoning.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/root_hygiene_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_all_guardians.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_architecture_governance.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py` | L0 | - | - | 14 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_change_package_activation.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_classification_compliance.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_contract_integrity.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_cross_layer_mutation.py` | L0 | - | - | 6 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_drift_detection.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_escalation_determinism.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_gateway_bypass.py` | L0 | - | - | 3 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_hygiene.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_location_alignment.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_guardian_manifest.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_hierarchy_agent_dry_run_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_hierarchy_healer_dry_run_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_hygiene_guardian_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_hygiene_naming_audit_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_naming_law_check_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_naming_scan_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/run_sovereign_compliance_audit_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/runtime_state_digest.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/scan_testing_compliance_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/sovereign_lockdown_check_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/sovereign_precommit_no_hardcoded_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/sovereign_precommit_no_raw_prompts_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/ssot_adapters.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/ssot_audit_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/ssot_cli.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/territory_ssot_definitions_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/validate_base_agents_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/validate_drilldown_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/validate_sovereign_structure_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/validate_table2_data_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_agent_status_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_all_checkpoint_files_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_base_agent_names_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_heal_invocation_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_healing_metrics_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_health_calculation_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_intentional_variants_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_manifest_cleanliness_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_manifest_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_mro_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_row_order_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/scripts/verify_territory_counts_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seam/seam_audit.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seams/c0_context_retriever.py` | L0 | - | - | 2 | 0 |
| `agentic_core/L0_routing/seams/canonical_truth_seam.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seams/elevator_shaft_seam.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seams/layer_emission_seam.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seams/learning_seam.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seams/observability_seam.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seams/redis_decision_cache.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seams/safety_enforcement_seam.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seams/safety_kernel_seam.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seams/safety_reasoning_seam.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seams/safety_validators_seam.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/seams/vigilance_seam.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/__init__.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/artifact_typed_compat_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/artifact_validate_compat_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/artifact_validators_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/boundary_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/crypto_trust_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/determinism_contracts_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/determinism_types.py` | L0 | - | - | 1 | 0 |
| `agentic_core/L0_routing/types/governance_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/guardian_contract_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/guardian_registry_types.py` | L0 | - | - | 4 | 0 |
| `agentic_core/L0_routing/types/integration_contract_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/reasoning_intensity_types.py` | L0 | - | - | 1 | 0 |
| `agentic_core/L0_routing/types/routing_artifact_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/routing_config_seal_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/routing_contracts_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/shadow_routing_types.py` | L0 | - | agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types | 0 | 0 |
| `agentic_core/L0_routing/types/traceability_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/v15_contracts_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/types/v15_p2_contracts_types.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/__init__.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/add_test_coverage_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/complexity_visitor_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/component_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/core_integrity_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/file_utils_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/find_misnamed_agents_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/fix_all_tunnels_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/fix_depth_violations_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/fix_mission_runner_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/fix_remaining_depth_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/force_annexation_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/gravity_audit_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/init_setup_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/json_formatter_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/manifest_guardian_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/path_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/project_root_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/scan_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/scorched_earth_merge_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/sovereign_alignment_v2_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/sovereign_convergence_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/ssot_discovery_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/structural_fix_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/subprocess_runner_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/timeout_decorator_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L0_routing/utils/trim_remaining_airlocks_util.py` | L0 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/__init__.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/config/__init__.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/config/react_config.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/enforcement/__init__.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/enforcement/budget_enforcer.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/enforcement/execution_status.py` | L1 | - | - | 1 | 0 |
| `agentic_core/L1_cognition/enforcement/mission_status.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/enforcement/react_strategy.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/CognitiveNode.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/__init__.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/cache_manager.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/capability_analyzer.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/codebase_mapper.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/cognitive_engine.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/deterministic_context_optimizer.py` | L1 | - | - | 1 | 0 |
| `agentic_core/L1_cognition/engines/domain_manager.py` | L1 | L0 | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/episodic_manager.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/memory_embedder.py` | L1 | - | - | 29 | 0 |
| `agentic_core/L1_cognition/engines/meta_client.py` | L1 | - | - | 8 | 0 |
| `agentic_core/L1_cognition/engines/meta_observability.py` | L1 | - | - | 1 | 0 |
| `agentic_core/L1_cognition/engines/perception_engine.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/pitch_engine.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/prompt_artifact_cache.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/query_planner.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/reasoning_cache.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/engines/semantic_manager.py` | L1 | - | - | 9 | 0 |
| `agentic_core/L1_cognition/engines/strategist_bio_writer.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/memory/__init__.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/memory/healing_memory_retriever.py` | L1 | - | - | 8 | 0 |
| `agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/reasoning/MetaLearningAgent.py` | L1 | - | - | 1 | 0 |
| `agentic_core/L1_cognition/reasoning/StrategicRecommendationAgent.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/reasoning/__init__.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/telemetry/telemetry_emitter.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/__init__.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/action_request_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/budget_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/cache_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/capability_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/client_types.py` | L1 | - | - | 2 | 0 |
| `agentic_core/L1_cognition/types/cognitive_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/domain_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/execution_intent_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/execution_phase_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/identity_type_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/memory_types.py` | L1 | - | - | 4 | 0 |
| `agentic_core/L1_cognition/types/observability_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/research_hop_phase_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/result_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/types/validation_types.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/agentic_constants_util.py` | L1 | L0 | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/consensus_util.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/constants_util.py` | L1 | L0 | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/execution_util.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/filter_inappropriate_content_util.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/guardrails_util.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/history_merger_util.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/profile_updater_util.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/prompts_util.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/template_finder_util.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/template_matcher_util.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/utils/token_updater_util.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/validators/__init__.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/validators/consensus_validator.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/validators/dark_reasoning_visitor_validator.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/validators/reasoningnode_validator.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/validators/semantic_gatekeeper_validator.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/validators/spiffe_validator.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L1_cognition/validators/truth_keeper_validator.py` | L1 | - | - | 0 | 0 |
| `agentic_core/L2_execution/UniversalWriteGateway.py` | L2 | - | - | 0 | 3 |
| `agentic_core/L2_execution/audit/__init__.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/audit/hash_chain_audit_log.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/capability/promotion_token.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/cid_registry.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/config/__init__.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/config/hybrid_retriever_config.py` | L2 | L0 | - | 0 | 0 |
| `agentic_core/L2_execution/config/mcp_registry.py` | L2 | - | - | 1 | 0 |
| `agentic_core/L2_execution/config/provider_type_config.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/config/strategist_bio_writer_config.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/config/transform_config.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/config/unified_workflow_config.py` | L2 | L0 | - | 0 | 3 |
| `agentic_core/L2_execution/coordination/__init__.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/coordination/lease_coordinator.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/determinism.py` | L2 | L0 | - | 5 | 0 |
| `agentic_core/L2_execution/determinism/__init__.py` | L2 | - | - | 1 | 0 |
| `agentic_core/L2_execution/determinism/canonicalize.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/determinism/dependency_locker.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/determinism/determinism_guard.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/determinism/digest_calculator.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/determinism/negative_control_harness.py` | L2 | - | - | 4 | 0 |
| `agentic_core/L2_execution/determinism/replay_guard.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/deterministic_providers.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | L2 | L0 | - | 1 | 0 |
| `agentic_core/L2_execution/enforcement/__init__.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/boundary_verifier.py` | L2 | - | - | 0 | 10 |
| `agentic_core/L2_execution/enforcement/budget_enforcer.py` | L2 | - | - | 0 | 2 |
| `agentic_core/L2_execution/enforcement/capability_chokepoint.py` | L2 | L0 | - | 0 | 6 |
| `agentic_core/L2_execution/enforcement/capability_revoker.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline.py` | L2 | L0 | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/deterministic_loop_detector.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/docker_sandbox.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/durable_write_wrapper.py` | L2 | L0 | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/filesystem_mcp.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/firecracker_manager.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/healer_pipe_order.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/key_derivation.py` | L2 | - | - | 1 | 1 |
| `agentic_core/L2_execution/enforcement/key_source.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/manifest_hash_validator.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/network_egress_guard.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/preventative_sandbox.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/provider_binding_determinism.py` | L2 | L0 | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/provider_substitution_prohibition.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/runtime_interceptor.py` | L2 | - | - | 1 | 2 |
| `agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/sovereign_sandbox_isolation.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/tool_policy_enforcer.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/transcript_freezer.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/enforcement/write_set_enforcer.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/engines/__init__.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/engines/action_node.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/engines/action_node_core.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/engines/batch_embedding_service.py` | L2 | - | - | 12 | 0 |
| `agentic_core/L2_execution/engines/execute_command_executor.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/engines/execution_gateway.py` | L2 | - | - | 0 | 5 |
| `agentic_core/L2_execution/engines/resource_predictor.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/engines/rollback_refiner.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/engines/secure_tools_impl.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/engines/tool_intent_executor.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/engines/tool_registry.py` | L2 | - | - | 9 | 0 |
| `agentic_core/L2_execution/engines/validation_orchestrator.py` | L2 | L0, L1 | - | 0 | 0 |
| `agentic_core/L2_execution/heal_result_adapter.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/__init__.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/architecture_governance_healer.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/architecture_governor_healer.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/bmg_embedding_similarity.py` | L2 | - | - | 6 | 0 |
| `agentic_core/L2_execution/healers/classification_compliance_healer.py` | L2 | L0 | - | 0 | 0 |
| `agentic_core/L2_execution/healers/drift_detection_healer.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/escalation_context.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/failure_signal_normalizer.py` | L2 | - | - | 4 | 0 |
| `agentic_core/L2_execution/healers/file_classification_healer.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/filesystem_ssot_healer.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/gravity_leak_healer.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/healing_provider_adapters.py` | L2 | - | google.generativeai, openai | 0 | 0 |
| `agentic_core/L2_execution/healers/healing_tier_config.py` | L2 | - | - | 6 | 0 |
| `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/healing_tier_router.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/healing_tier_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/hierarchy_agent_healer.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/hierarchy_compliance_healer.py` | L2 | L0 | - | 0 | 0 |
| `agentic_core/L2_execution/healers/monotonic_reentrancy_enforcer.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/qwen_circuit_breaker.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/qwen_determinism.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/qwen_gpu_validator.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/qwen_health.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/qwen_meta_learning.py` | L2 | - | - | 1 | 0 |
| `agentic_core/L2_execution/healers/qwen_vllm_inference.py` | L2 | - | vllm | 0 | 0 |
| `agentic_core/L2_execution/healers/signature_invalidator.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/tiering_allowlist.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/healers/vllm_process_manager.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/protocol.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` | L2 | - | - | 29 | 0 |
| `agentic_core/L2_execution/reasoning/RedisSovereignAgent.py` | L2 | - | - | 2 | 0 |
| `agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/reasoning/StructuredEngineAgent.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` | L2 | L0, L1 | - | 0 | 0 |
| `agentic_core/L2_execution/reasoning/ToolsmithAgent.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/reasoning/__init__.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/reasoning/definitions.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/reentry_loop.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/scripts/__init__.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/scripts/remediation_dispatcher.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/tools/__init__.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/tools/content_relevance_impl.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/tools/figma_mcp_client.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/tools/file_io_impl.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/tools/git_ops_impl.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/tools/job_analyzer_impl.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/tools/ptc_contract.py` | L2 | - | - | 0 | 3 |
| `agentic_core/L2_execution/tools/safe_subprocess.py` | L2 | L0 | - | 0 | 0 |
| `agentic_core/L2_execution/tools/time_utils_impl.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/tools/tool_chain_executor.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/tools/tool_verifier_impl.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/tools/unsafe_io_detector.py` | L2 | L0 | - | 0 | 0 |
| `agentic_core/L2_execution/tools/web_search_client.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/tools/write_gateway.py` | L2 | L0 | - | 0 | 0 |
| `agentic_core/L2_execution/types/__init__.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/agent_output_contract_types.py` | L2 | - | - | 0 | 1 |
| `agentic_core/L2_execution/types/blast_radius_controls_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/bullet_format_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/capability_token_types.py` | L2 | L0 | - | 0 | 14 |
| `agentic_core/L2_execution/types/commit_proof_invariant_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/ephemeral_vm_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/execution_trace_types.py` | L2 | - | - | 0 | 2 |
| `agentic_core/L2_execution/types/gateway_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/heal_contract_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/healer_registry_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/instruction_packet_types.py` | L2 | - | - | 0 | 10 |
| `agentic_core/L2_execution/types/keyword_classification_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/llm_replay_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/mcp_client_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/mcp_error_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/mcp_security_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/mcp_tool_types.py` | L2 | L0 | - | 0 | 6 |
| `agentic_core/L2_execution/types/ml_pattern_record_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/ml_write_intent_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/ptc_tool_contracts_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/replay_envelope_types.py` | L2 | - | - | 7 | 0 |
| `agentic_core/L2_execution/types/resource_prediction_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/rollback_refinement_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/sandbox_envelope_types.py` | L2 | - | - | 0 | 7 |
| `agentic_core/L2_execution/types/self_healing_trigger_types.py` | L2 | L0 | - | 0 | 0 |
| `agentic_core/L2_execution/types/structured_agent_output_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/token_enforcement_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/tool_args_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/tool_enforcement_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/tool_intent_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/vllm_backpressure_types.py` | L2 | - | agentic_core.L2_execution.types.vllm_token_budget_types | 0 | 0 |
| `agentic_core/L2_execution/types/vllm_concurrency_types.py` | L2 | - | agentic_core.L2_execution.types.vllm_serving_profile_types, agentic_core.L2_execution.types.vllm_token_budget_types | 0 | 0 |
| `agentic_core/L2_execution/types/vllm_gateway_adapter_types.py` | L2 | - | agentic_core.L2_execution.types.vllm_gateway_integration_types, agentic_core.L2_execution.types.vllm_invariant_verifier_types | 0 | 0 |
| `agentic_core/L2_execution/types/vllm_gateway_integration_types.py` | L2 | - | agentic_core.L2_execution.types.vllm_backpressure_types, agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types, agentic_core.L2_execution.types.vllm_serving_profile_types, agentic_core.L2_execution.types.vllm_token_budget_types | 0 | 0 |
| `agentic_core/L2_execution/types/vllm_infrastructure_fingerprint_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/vllm_invariant_contract_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/vllm_invariant_verifier_types.py` | L2 | - | agentic_core.L2_execution.types.vllm_invariant_contract_types | 0 | 0 |
| `agentic_core/L2_execution/types/vllm_replay_validator_types.py` | L2 | - | agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types | 0 | 0 |
| `agentic_core/L2_execution/types/vllm_serving_profile_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/vllm_token_budget_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/types/vm_status_types.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/utils/analysis_ops_util.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/utils/archive_util.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/utils/data_serializer_util.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/utils/deterministic_cleaner_util.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/utils/egress_util.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/utils/factory_util.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/utils/gemini_spy_util.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/utils/payload_formatter_util.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/utils/staging_buffer_util.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/utils/text_similarity_util.py` | L2 | - | - | 0 | 0 |
| `agentic_core/L2_execution/utils/tool_registry_util.py` | L2 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/arbitration/advisors.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/arbitration/arbitration_contract.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/arbitration/arbitrator.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/arbitration/run_advisors.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/config/__init__.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/config/orchestrator_config.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/enforcement/__init__.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/enforcement/enforce_orchestration_policy.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/enforcement/knowledge_graph_healing_strategy.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/enforcement/mission_runner.py` | L3 | L0, L2 | - | 0 | 0 |
| `agentic_core/L3_orchestration/enforcement/rl_strategy.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/enforcement/safety_strategy.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/AgentFactory.py` | L3 | L1 | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/__init__.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/action_router.py` | L3 | L2 | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/agent_gym_engine.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/autonomous_execution_engine.py` | L3 | L2 | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/bounded_task_decomposer.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/call_formatting_router.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/context_curator_engine.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/convergence_engine.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/coordinator_capability_orchestrator.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/dag_manager.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/decomposition_orchestrator.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/deterministic_orchestrator.py` | L3 | L0 | - | 1 | 0 |
| `agentic_core/L3_orchestration/engines/handshake_state_machine.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/nervous_system.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/omni_context_engine.py` | L3 | L2 | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/orchestration_plan_cache.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/orchestrator_engine.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/proactive_fission_scanner.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/reasoning_intensity_enforcer.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/recovery_coordinator_orchestrator.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/recursive_orchestrator.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/reflex_layer_pattern.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/rl_coordinator_orchestrator.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/sovereign_mcp_marketplace.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/sovereign_mcp_router.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py` | L3 | L1, L2 | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/engines/sub_atomic_engine_impl.py` | L3 | L2 | - | 3 | 0 |
| `agentic_core/L3_orchestration/ptc/builtin_tools.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/ptc/ptc_registry.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/ptc/tool_call_store.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/ptc/tool_contract.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/ptc/tool_invoker.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/CoverageAgent.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/DagEngineAgent.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/StateManagementAgent.py` | L3 | L2 | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/UnifiedAgent.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/reasoning/__init__.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/replay/deterministic_replay.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/scripts/__init__.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/scripts/guardian_heal_orchestrator.py` | L3 | L0, L2 | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/__init__.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/approval_contract_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/artifact_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/cognitive_diff_types.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/context_pruning_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/execution_phase_signal_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/execution_trace_types.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/forward_rolling_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/healer_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/hop_status_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/human_decision_artifact_types.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/injection_result_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/orchestrator_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/permission_scope_types.py` | L3 | L1 | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/rag_provider_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/recursion_monitor_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/recursive_orchestration_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/route_decision_artifact_types.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/route_type_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/scenario_type_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/telepathy_interface_types.py` | L3 | L2 | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/workflow_loader_types.py` | L3 | L0 | - | 0 | 0 |
| `agentic_core/L3_orchestration/types/workflow_types.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/utils/__init__.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L3_orchestration/utils/log_orchestration_metrics_util.py` | L3 | - | - | 0 | 0 |
| `agentic_core/L4_state/__init__.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/caching/__init__.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/caching/redis_mcp_client.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/config/ledger_retention_config.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/config/memory_store_config.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/config/versioned_configs.py` | L4 | - | - | 4 | 0 |
| `agentic_core/L4_state/config/vllm_routing_predicates.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/__init__.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/activation_flags.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/blast_radius.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/change_tracker.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/citation_enforcement.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/embedding_sovereignty_guard.py` | L4 | - | - | 8 | 0 |
| `agentic_core/L4_state/enforcement/genealogy_registry.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/graph_memory_bridge.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/knowledge_integrity_guard.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/metrics_emission.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/mission_historian.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/neo4j_store.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/phase_lock_store.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/promotion_authority.py` | L4 | - | - | 0 | 2 |
| `agentic_core/L4_state/enforcement/readonly_retrieval_scope.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/replay_bundle_store.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/telemetry_recorder.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/telemetry_recorder_enforcer.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/trace_event.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/enforcement/violation_event_store.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/engines/error_context_preserver.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/engines/fresh_data_validator.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/engines/ghost_mutation_detector.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/engines/memory_collision_detector.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/engines/readonly_retrieval_orchestrator.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/engines/replay_bundle_emitter.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/memory/__init__.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/memory/blackboard_store.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/memory/blob_storage_provider.py` | L4 | L0 | - | 0 | 0 |
| `agentic_core/L4_state/memory/bm25_store.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/memory/in_memory_vector_cache.py` | L4 | - | - | 5 | 0 |
| `agentic_core/L4_state/memory/in_memory_vector_store.py` | L4 | - | - | 3 | 0 |
| `agentic_core/L4_state/memory/prompt_version_store.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/memory/reasoning_memory.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/memory/runtime_models.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/memory/runtime_state_guard.py` | L4 | L0 | - | 0 | 0 |
| `agentic_core/L4_state/memory/semantic_cache_manager.py` | L4 | L2 | - | 9 | 0 |
| `agentic_core/L4_state/memory/sovereign_memory_store.py` | L4 | - | - | 1 | 0 |
| `agentic_core/L4_state/memory/sovereign_reasoning_memory_ledger.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/memory/sovereign_semantic_cache.py` | L4 | - | - | 1 | 0 |
| `agentic_core/L4_state/memory/verifiable_checkpoint_manager.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/reasoning/CachedStateLedger.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/reasoning/CheckpointManager.py` | L4 | L0 | - | 0 | 0 |
| `agentic_core/L4_state/reasoning/__init__.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/storage/filesystem_store.py` | L4 | - | - | 0 | 1 |
| `agentic_core/L4_state/storage/persistent_store.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/citation_bundle_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/context_priority_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/cycle_types.py` | L4 | L0 | - | 0 | 0 |
| `agentic_core/L4_state/types/detection_signal_store_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/memory_item_types.py` | L4 | - | - | 3 | 0 |
| `agentic_core/L4_state/types/micro_stage_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/replay_bundle_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/retrieval_anchor_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/retrieval_boundary_snapshot_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/state_checkpoint_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/state_validation_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/validation_context_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/vector_store_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/types/violation_event_types.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/utils/__init__.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/utils/circuit_breaker_util.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/utils/complexity_analyzer_util.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/utils/context_util.py` | L4 | L3 | - | 0 | 0 |
| `agentic_core/L4_state/utils/experience_buffer_util.py` | L4 | L0 | - | 0 | 0 |
| `agentic_core/L4_state/utils/get_existing_file_hashes_util.py` | L4 | L0 | - | 0 | 0 |
| `agentic_core/L4_state/utils/get_existing_filenames_util.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/utils/get_existing_files_util.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/utils/get_file_hash_util.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/utils/layer_gravity_util.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/utils/local_disk_adapter_util.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/utils/rag_enhancement_util.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/utils/sanitize_telemetry_util.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L4_state/utils/telemetry_sanitizer_util.py` | L4 | - | - | 0 | 0 |
| `agentic_core/L5_safety/config/blueprint_compiler.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/config/contract_stage_config.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/config/detection_signal_config.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/config/gravity_leak_config.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/config/input_config.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/__init__.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/_constants.py` | L5 | - | - | 2 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/_simulate_verify.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/artifacts.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/classification.py` | L5 | - | - | 1 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/derived.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/governance.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/semantics.py` | L5 | - | - | 3 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/sovereign_kernel.py` | L5 | - | - | 1 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint/territories.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/config/structure_blueprint_config.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/core_kernel/__init__.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/core_kernel/classification_kernel.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/AdapterBase.py` | L5 | - | - | 1 | 0 |
| `agentic_core/L5_safety/enforcement/DomainPlannerAdapter.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/HealingStrategy.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/HumanReviewAdapter.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/SurgicalHealingAdapter.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/__init__.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/activation_gate.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/agent_info_enforcer.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/airlock_guardrail.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/airlock_trimmer_enforcer.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/artifact_emission_prohibition_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/audit_healing_strategy.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/canary_token_defense_strategy.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/circuit_breaker_gate.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/circular_import_fixer_enforcer.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/compliance_audit_manager_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/conf_calib_gate.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/context_session_manager_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/d0_injection_engine_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/data_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/dependency_graph_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py` | L5 | - | - | 8 | 0 |
| `agentic_core/L5_safety/enforcement/error_recovery_guardrail.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/error_recovery_strategy.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/fast_dashboard_e2_e_pipeline_enforcer.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/git_health_sensor_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/git_kraken_healing_strategy.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/governance/__init__.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/governance/artifacts_guard.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/governance/cache_guard.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/governance/docs_structure_guard.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/governance/logs_guard.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/healing_invocation_audit_enforcer.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/hierarchy_validator_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/import_boundary_check_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/import_surgeon_enforcer.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/input_membrane_guardrail.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/input_validation_guardrail.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/mission_utils_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/mock_context_enforcer.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/module_collision_guardrail.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/namespace_medic_enforcer.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/phase_acceptance_guardrail.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/pii_vault_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/priority_violation_guard.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/process_guardrail.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/pytest_config_guardrail.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/rag_guardrail.py` | L5 | - | - | 3 | 0 |
| `agentic_core/L5_safety/enforcement/re_clear_loop_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/registry_verification_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/runtime_mutation_guardrail.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py` | L5 | L4 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/safety_eval_cache.py` | L5 | - | - | 0 | 3 |
| `agentic_core/L5_safety/enforcement/safety_guardrail.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/safety_layer_enforcer.py` | L5 | L1 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/sealed_interface_check_enforcer.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/secure_error_handler_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/security/__init__.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/security/credential_guard.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/sovereign_fence_validator_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/sovereign_policy_registry_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/ssot_guardrail.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/ssot_import_enforcer.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/structural_namespace_fence_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/system_enforcer.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/three_tier_compliance_enforcer.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/enforcement/vector_healing_strategy.py` | L5 | - | - | 8 | 0 |
| `agentic_core/L5_safety/enforcement/verification_gate.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/governance/lazy_seam_classifier.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/governance/lazy_seam_enforcer.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/governance/lazy_seam_scanner.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py` | L5 | L4 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/ArchitectureGovernorValidatorAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/AutonomousThreatEvolutionAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/BenchmarkingAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/BootstrapAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py` | L5 | L4 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py` | L5 | L4 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/CodeDetectorAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/CodeFormatterAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/CodeHealerAgent.py` | L5 | L0, L2, L3 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/CodeValidatorAgent.py` | L5 | L3 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py` | L5 | L3 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/CostGovernorAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/CredentialScannerAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/DependencyPruningAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/DocumentationAgent.py` | L5 | L3 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/DynamicSealAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/FileClassificationHealerAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/FileClassificationValidatorAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/FilesystemSSOTHealerAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/FilesystemSSOTValidatorAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/GitHygieneAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/GospelSyncAgent.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/GovernanceAgent.py` | L5 | L0, L2, L4 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/GravityLeakHealerAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py` | L5 | L0, L2, L4 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/GravityValidatorAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/HierarchyAgent.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/HierarchyHealerAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/HierarchyValidatorAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/InspectorExecutor.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/LocationAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` | L5 | L0, L2, L3, L4 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/LocationValidatorAgent.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/NamingAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/NeuralAutoImmuneAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py` | L5 | L4 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/RedSentinelAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/RedTeamAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/RegressionOracleAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/ReportLocationAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/ResourceManagerAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/RootHygieneAgent.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py` | L5 | L0, L1, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/SecurityManagerAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py` | L5 | L2, L4 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py` | L5 | L2, L3, L4 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/StructureHealerAgent.py` | L5 | L0, L2, L3 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/TypeMechanicAgent.py` | L5 | L3 | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/__init__.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/reasoning/guardian_decision.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/runners/__init__.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/runners/agent_roster_runner.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/runners/arch_governor_runner.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/runners/code_validator_runner.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/runners/hierarchy_runner.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/runners/orchestrator_runner.py` | L5 | L3 | - | 0 | 0 |
| `agentic_core/L5_safety/security/injection_regression_gate.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/security/secure_secrets.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/security/side_effect_guard.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/security/signature_verifier.py` | L5 | - | - | 0 | 9 |
| `agentic_core/L5_safety/static_checks/determinism_serialization_check.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/static_checks/powershell_ban.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/static_checks/ptc_invariants.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/static_checks/system_invariant_scanner.py` | L5 | - | - | 10 | 0 |
| `agentic_core/L5_safety/static_checks/write_gateway_enforcer.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/agent_audit_result_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/constitutional_governance_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/core_contracts_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/cst_transformers_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/file_health_score_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/heal_llm_seam_types.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/types/heal_model_map_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/heal_policy_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/healing_orchestration_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/health_status_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/human_decision_artifact_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/integrity_validation_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/learning_types.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/types/meta_learning_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/rag_validation_result_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/resource_management_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/rule_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/safety_profile_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/safety_types.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/types/security_validation_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/shift_report_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/simulation_schemas_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/sovereign_base_model_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/specificity_prose_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/ssot_relocator_types.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/types/surgical_context_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/tier_lattice_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/types/validation_result_types.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/types/verification_types.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/ConstitutionalOverseer_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/__init__.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/agent_categorizer_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/cache_invalidation_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/canonical_truth_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/capability_extractor_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/check_output_quality_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/code_tool_runner_core_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/cognitive_batch_processor_util.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/cst_transformers_types_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/decorators_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/enforce_length_limits_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/extract_pattern_util.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/fca_safety_gates_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/fix_inherited_invocation_util.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/force_app_depth_util.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/forge_fortress_util.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/gravity_visitor_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/guard_ddd_alignment_util.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/guard_observability_footprint_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/location_constants_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/location_path_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/location_utils_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/pre_deploy_check_util.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/register_all_validators_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/security_controls_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/set_complexity_health_100_util.py` | L5 | L0, L2 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/sovereign_lock_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/ssot_folder_check_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/subprocess_security_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/surgical_context_types_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/tiered_batch_util.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/unified_cst_healer_util.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/validate_dashboard_data_sourcing_util.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/utils/validate_generated_content_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/validate_path_ssot_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/validation_utils_util.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/utils/verify_no_mock_data_util.py` | L5 | L0 | - | 1 | 0 |
| `agentic_core/L5_safety/utils/verify_semantic_meta_learning_util.py` | L5 | - | - | 15 | 0 |
| `agentic_core/L5_safety/validators/__init__.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/achv_bullet_synthesizer_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/agentthoughtprocess_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/anti_pattern_scanner_validator.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/validators/ats_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/base_detector_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/budget_profile_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/campaign_balance_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/consensus_verdict_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/content_quality_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/context_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/ddd_alignment_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/deliverability_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/dependencygraph_validator.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/validators/global_mutation_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/golden_state_test_case_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/governance_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/gravity_validator.py` | L5 | L0 | - | 0 | 0 |
| `agentic_core/L5_safety/validators/hop_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/hypothesis_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/intelligence_query_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/intervention_server_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/lead_quality_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/magic_validator.py` | L5 | - | - | 1 | 0 |
| `agentic_core/L5_safety/validators/migration_helper_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/mission_preflight_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/path_fragility_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/read_file_args_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/reasoning_pattern_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/report_location_validator.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/validators/silent_swallower_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/structure_drift_validator.py` | L5 | L2 | - | 0 | 0 |
| `agentic_core/L5_safety/validators/type_erasure_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L5_safety/validators/verb_canonicalizer_validator.py` | L5 | - | - | 0 | 0 |
| `agentic_core/L6_observability/__init__.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/dashboards/__init__.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/dashboards/analyze_dashboard_color_bug_util.py` | L6 | L0 | - | 0 | 0 |
| `agentic_core/L6_observability/dashboards/core/DashboardDataGenerator.py` | L6 | L5 | - | 0 | 0 |
| `agentic_core/L6_observability/dashboards/core/StaticFileApp.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/dashboards/core/dashboard_handler.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/dashboards/core/experiencein_config.py` | L6 | L0, L1, L2 | - | 1 | 0 |
| `agentic_core/L6_observability/dashboards/dashboard_generator.py` | L6 | L0, L2, L5 | - | 0 | 0 |
| `agentic_core/L6_observability/dashboards/dashboard_qa.py` | L6 | L5 | - | 0 | 0 |
| `agentic_core/L6_observability/dashboards/renderers/dashboard_renderer.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/dashboards/verify_dashboard_e2e_playwright_util.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/enforcement/__init__.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/enforcement/agent_monitor.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/enforcement/outcome_logger.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/enforcement/rag_telemetry_collector.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/enforcement/reasoning_streamer.py` | L6 | L2 | - | 0 | 0 |
| `agentic_core/L6_observability/engines/PerformanceAnalystAgentSimple.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/engines/SovereignHealthMonitor.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/engines/TieredVigilanceEmitter.py` | L6 | L0 | - | 0 | 0 |
| `agentic_core/L6_observability/engines/__init__.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/engines/detection_signal_emitter.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/engines/determinism_digest_emitter.py` | L6 | - | - | 4 | 0 |
| `agentic_core/L6_observability/engines/dpo_pair_generator.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/engines/drift_detector.py` | L6 | - | - | 2 | 0 |
| `agentic_core/L6_observability/engines/entropy_telemetry_engine.py` | L6 | L2 | - | 0 | 0 |
| `agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/engines/provider_binding_fingerprint.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/engines/replay_key_computer.py` | L6 | - | - | 2 | 0 |
| `agentic_core/L6_observability/engines/semantic_clock_validator.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/engines/vigilance_dispatcher.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/golden_evaluation/__init__.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/golden_evaluation/injection_regression_suite.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/golden_evaluation/tool_use_ground_truth_evaluator.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/reasoning/ObservabilityProbeExecutorAgent.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/reasoning/__init__.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/types/__init__.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/types/detection_signal_types.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/types/dpo_types.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/types/monitor_types.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/types/sovereign_report_types.py` | L6 | - | - | 0 | 0 |
| `agentic_core/L6_observability/types/vigilance_event_types.py` | L6 | L0 | - | 0 | 0 |
| `agentic_core/L6_observability/utils/fix_testing_observability_util.py` | L6 | L0, L2 | - | 0 | 0 |
| `agentic_core/L6_observability/utils/integrity_report_generator_util.py` | L6 | L0, L2, L5 | - | 0 | 0 |
| `agentic_core/L6_observability/utils/system_telemetry_util.py` | L6 | - | - | 0 | 0 |
| `agentic_core/_compat/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/_compat/apps_engines_aliases.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/_compat/l5_safety_aliases.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/agents/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/agents/agent_registry.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/agents/types/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/agents/types/agent_execution_profile_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/base_agents/L0RoutingBase.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/base_agents/L1CognitionBase.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/base_agents/L2ExecutionBase.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/base_agents/L3OrchestrationBase.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/base_agents/L4StateBase.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/base_agents/L5SafetyBase.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/base_agents/L6ObservabilityBase.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/base_agents/LightweightBase.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/base_agents/SovereignBaseAgent.py` | UNKNOWN | - | - | 2 | 0 |
| `agentic_core/base_agents/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/cache/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/cache/cache_key_builders.py` | UNKNOWN | - | - | 3 | 1 |
| `agentic_core/cache/config_file_cache.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/cache/discovery_cache.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/cache/policy_registry_cache.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/cache/redis_cache_client.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/cache/schema_validator_cache.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/cache/tool_embedding_cache.py` | UNKNOWN | - | - | 15 | 0 |
| `agentic_core/config/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/agent_defaults_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/base_entity_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/colors_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/complexity_metrics_config.py` | UNKNOWN | - | - | 1 | 0 |
| `agentic_core/config/core/config_loader.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/constants_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/domain_constitution_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/env_loader.py` | UNKNOWN | - | - | 1 | 0 |
| `agentic_core/config/core/gateway_config.py` | UNKNOWN | - | - | 9 | 0 |
| `agentic_core/config/core/global_settings_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/hygiene_registry_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/injection_layer_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/legacy_artifacts_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/non_conforming_agent_finder_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/rag_config.py` | UNKNOWN | - | - | 7 | 0 |
| `agentic_core/config/core/reflection_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/config/core/registry_config.py` | UNKNOWN | - | - | 1 | 0 |
| `agentic_core/config/core/sovereign_config.py` | UNKNOWN | - | - | 7 | 0 |
| `agentic_core/config/core/yaml_injection_loader.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/enforcement/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/enforcement/sealed_interface_check_enforcer.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/IBlackboardLeaseVerifierProtocol.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/IHealerProtocol.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/IHealingStrategyProtocol.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/IMemoryStoreProtocol.py` | UNKNOWN | - | - | 1 | 0 |
| `agentic_core/interfaces/IOrchestratorProtocol.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/IValidatorProtocol.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/determinism.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/determinism_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/embeddings.py` | UNKNOWN | - | - | 3 | 0 |
| `agentic_core/interfaces/execution.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/execution_agents.py` | UNKNOWN | - | - | 2 | 0 |
| `agentic_core/interfaces/execution_contracts.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/gateway.py` | UNKNOWN | - | - | 1 | 0 |
| `agentic_core/interfaces/meta_control.py` | UNKNOWN | - | - | 0 | 2 |
| `agentic_core/interfaces/meta_learning.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/mixins.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/observability.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/orchestration.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/routing_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/safety.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/spine.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/state_agents.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/structure_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/validators.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/interfaces/write_gateway.py` | UNKNOWN | - | - | 0 | 2 |
| `agentic_core/knowledge/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/document_loaders/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/document_loaders/csv_document_loader_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/document_loaders/csv_loader.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/document_loaders/html_loader.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/document_loaders/pdf_document_loader_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/document_loaders/pdf_loader.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/document_loaders/research_cache.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/document_loaders/source_document_types.py` | UNKNOWN | - | - | 1 | 0 |
| `agentic_core/knowledge/document_loaders/text_document_loader_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/document_loaders/text_loader.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/engine/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/engine/rag_orchestrator.py` | UNKNOWN | - | - | 5 | 0 |
| `agentic_core/knowledge/healing/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/healing/wiki_healer.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py` | UNKNOWN | - | - | 4 | 0 |
| `agentic_core/knowledge/research_cache/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/research_cache/cache_store_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/static_index/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/static_index/action_verbs_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/knowledge/static_index/skill_taxonomy_types.py` | UNKNOWN | - | - | 1 | 0 |
| `agentic_core/mixins/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/adaptive_execution_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ast_enforcement_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/atomic_execution_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/audit_trail_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/autonomy_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/batching_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/caching_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/capability_discovery_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/circuit_breaker_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/cognitive_recovery_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/config_compat_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/configuration_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/context_management_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/context_propagation_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/cost_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/cst_healer_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/domain_agent_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/embedding_mixin.py` | UNKNOWN | - | - | 10 | 0 |
| `agentic_core/mixins/event_emission_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/feature_flagged_agent_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/golden_context_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/hallucination_detection_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/hardening_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/healer_agent_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/healer_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/healing_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/healing_policy_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/hitl_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/hygiene_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/infrastructure_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/inspection_capability_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/instructional_injection_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/lifecycle_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/llm_provider_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/mcp_hardened_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/mcp_operation_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/meta_learning_client_mixin.py` | UNKNOWN | - | - | 6 | 0 |
| `agentic_core/mixins/meta_learning_contract_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/meta_learning_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/metrics_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/migration_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/performance_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/redis_cache_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/replay_guard_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/runtime_safety_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/safety_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/secrets_management_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/self_diagnosis_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/semantic_cache_mixin.py` | UNKNOWN | - | - | 1 | 0 |
| `agentic_core/mixins/ssot_adaptive_execution_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_audit_trail_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_caching_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_circuit_breaker_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_cognitive_recovery_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_context_propagation_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_feature_flag_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_hallucination_detection_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_meta_learning_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_metrics_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_mixin_stack.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_rate_limit_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_self_diagnosis_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_state_validation_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/ssot_tracing_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/state_validation_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/structural_healing_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/subatomic_testing_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/tool_reliability_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/tracing_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/mixins/validator_mixin.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/contracts/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/contracts/context_contracts.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/contracts/slot_contracts.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/core/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/core/governance_hub.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/core/invariant_registry.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/core/prompt_assembler.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/core/prompt_entry_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/core/prompt_loader.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/core/sovereign_prompt_renderer.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/meta_prompts/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/optimization/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/optimization/optimization_strategy.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/registry/backups/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/scripts/audit_registry_linkages.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/scripts/cleanup_duplicates_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/scripts/detect_template_drift.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/scripts/dry_run_compiler.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/scripts/file_intent.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/scripts/harden_templates.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/scripts/import_violation_visitor.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/scripts/synchronize_registry_hashes.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/scripts/template_render_visitor.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/security/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/security/assembly_injection_neutralizer.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/security/detectors/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/security/detectors/injection_detector.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/security/detectors/pii_scrubber.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/security/utils/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/security/utils/injection_scan_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/security/utils/normalization_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/security/validators/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/security/validators/output_schema_validator.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/prompt_governance/validation/validate_assembly.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/boundary_validator.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/anomaly_report_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/capability_gap_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/contextual_router_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/detection_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/feature_flags_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/heal_result_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/injection_type_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/instructional_injections.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/model_provider_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/model_tier_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/prompt_injection_loader_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/reasoning_types.py` | UNKNOWN | - | - | 2 | 0 |
| `agentic_core/runtime/config/review_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/security_level_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/shared_infrastructure_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/signal_quality_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/config/validation_severity_config.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/enforcement/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/enforcement/envelope_factory.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/engine/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/engine/agent_engine.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/engine/ast_relocator.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/exceptions/SovereignError.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/exceptions/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/exceptions/healer_exceptions.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/exceptions/runtime_exceptions.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/exceptions/workflow_exceptions.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/execution_bound_token.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/execution_trace.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/mathematical_determinism.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/sovereignty_bootstrap.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/sovereignty_exceptions.py` | UNKNOWN | - | - | 0 | 1 |
| `agentic_core/runtime/types/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/types/cache_entry_types.py` | UNKNOWN | - | - | 15 | 0 |
| `agentic_core/runtime/types/circuit_breaker_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/types/claim_type_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/types/cost_governor_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/types/expansion_strategy_types.py` | UNKNOWN | - | - | 1 | 0 |
| `agentic_core/runtime/types/recovery_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/types/sovereign_events_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/types/state_types.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/utils/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/utils/discovery_parser_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/utils/discovery_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/utils/dynamic_loader_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/utils/file_cache_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/utils/main_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/utils/runtime_bootstrapper_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/utils/sovereign_dependency_error_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/utils/sovereign_index_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/utils/sovereign_scan_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/runtime/utils/trait_system_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/seams/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/seams/contracts/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/seams/contracts/activation.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/seams/contracts/forward_rolling.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/seams/contracts/mcp.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/seams/contracts/safety_agents.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/seams/orchestration_protocols.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/__init__.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/ast_fuzzy.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/ast_fuzzy_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/canonical_json_util.py` | UNKNOWN | - | - | 0 | 1 |
| `agentic_core/utils/canonical_serializer_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/decorators_base_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/decorators_compat_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/decorators_shim_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/decorators_util.py` | UNKNOWN | - | - | 0 | 1 |
| `agentic_core/utils/detection_protocol_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/fs_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/meta_learning_engine_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/meta_learning_storage_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/meta_learning_types_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/project_root_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/report_location_validator_types_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/review_protocol_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/security_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/state_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/structural_healing_engine_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/timeout_decorator_impl_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/timeout_decorator_util.py` | UNKNOWN | - | - | 0 | 0 |
| `agentic_core/utils/verification_types_util.py` | UNKNOWN | - | - | 0 | 0 |

## Parse Failures

| File | Error Type | Message |
|------|------------|---------|
| `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | IndentationError | unexpected indent (FileClassificationAgent.py, line 2075) |
| `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | IndentationError | unexpected indent (FileClassificationAgent.py, line 2075) |
| `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | IndentationError | unexpected indent (FileClassificationAgent.py, line 2075) |

## L0 Layer Gaps

### EMBEDDING-PLACEMENT-GAP-04f677f1e8: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/engines/assembly_stage.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/engines/assembly_stage.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-2c8acf1841: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/scripts/execute_ssot.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/scripts/execute_ssot.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-52c5d7e45c: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_gateway_bypass.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_gateway_bypass.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-5d85f88948: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/types/guardian_registry_types.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/types/guardian_registry_types.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-61abd1cb6d: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_cross_layer_mutation.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_cross_layer_mutation.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-64201b4a85: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-a207aef1a1: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/scripts/colors.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/scripts/colors.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-ad365b0cd9: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/scripts/chunk_type.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/scripts/chunk_type.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-b85263990f: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/scripts/cache_init_util.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/scripts/cache_init_util.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-d280158168: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/engines/reasoning_policy_engine.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/engines/reasoning_policy_engine.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-d3af3638d6: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/types/determinism_types.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/types/determinism_types.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-d441d60bd3: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/seams/c0_context_retriever.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/seams/c0_context_retriever.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-dbf4983004: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/scripts/agent_analysis_config.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/scripts/agent_analysis_config.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-ebb7959240: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/types/reasoning_intensity_types.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/types/reasoning_intensity_types.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-f73b1a2b33: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L0_routing/scripts/populate_ssot_folders_util.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L0_routing/scripts/populate_ssot_folders_util.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### GATEWAY-BYPASS-RISK-e73ce33bac: Sovereign Gateway Bypass Risk

**Priority:** HIGH

**Architectural Intent:**
All outbound LLM egress should flow through SovereignLLMGateway only.

**Implementation Reality:**
agentic_core/L0_routing/engines/shadow_router_classifier.py imports provider SDK seams directly: agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types

**Impact:**
Direct SDK imports create possible provider bypasses outside the sole gateway seam.

**Evidence Files:
- `agentic_core/L0_routing/engines/shadow_router_classifier.py`

**Recommended Fix:**
Route all provider interactions through SovereignLLMGateway and remove direct SDK imports.

---

### GATEWAY-BYPASS-RISK-ff428c98d4: Sovereign Gateway Bypass Risk

**Priority:** HIGH

**Architectural Intent:**
All outbound LLM egress should flow through SovereignLLMGateway only.

**Implementation Reality:**
agentic_core/L0_routing/types/shadow_routing_types.py imports provider SDK seams directly: agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types

**Impact:**
Direct SDK imports create possible provider bypasses outside the sole gateway seam.

**Evidence Files:
- `agentic_core/L0_routing/types/shadow_routing_types.py`

**Recommended Fix:**
Route all provider interactions through SovereignLLMGateway and remove direct SDK imports.

---

### PATHD-PLAN-HASH-GAP-e2ffa7e47b: Path D Re-Clear Contract

**Priority:** HIGH

**Architectural Intent:**
Human MODIFY_DIFF flows must bind to original_plan_hash before L5 re-clear.

**Implementation Reality:**
agentic_core/L0_routing/types/governance_types.py shows Path D or HITL markers without clear original_plan_hash evidence.

**Impact:**
Human patch flows may lose plan provenance or bypass strict re-clear assumptions.

**Evidence Files:
- `agentic_core/L0_routing/types/governance_types.py`

**Recommended Fix:**
Require original_plan_hash and structured_patch_schema markers on all Path D decision artifacts.

---

### ELEVATOR-SHAFT-GAP-01bd191154: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/full_agent_discovery.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/full_agent_discovery.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-01e607be58: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/validate_table2_data_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/validate_table2_data_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-04f677f1e8: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/engines/assembly_stage.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/engines/assembly_stage.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-051031435a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/call_personalization_api_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/call_personalization_api_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-0575a8e713: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/layer_summary_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/layer_summary_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-05d35e41f1: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/compare_ui_components_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/compare_ui_components_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-063abb3ea9: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/cache_data_access_init_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/cache_data_access_init_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-07251203a6: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/debug_drilldown_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/debug_drilldown_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-076d7cba04: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/__init__.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/__init__.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-080a3597a3: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/territory_ssot_definitions_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/territory_ssot_definitions_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-0a8881cea4: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seams/vigilance_seam.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seams/vigilance_seam.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-0cf808e328: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-0de89986dc: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_open_heal_invocations_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_open_heal_invocations_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-0fab5858db: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/types/v15_p2_contracts_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/types/v15_p2_contracts_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-0fe12b3015: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_missing_invocation_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_missing_invocation_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-0fe7c65d09: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/check_sovereign_base_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/check_sovereign_base_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-10e336ec1a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/trim_remaining_airlocks_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/trim_remaining_airlocks_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-14aae23ca2: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/list_layer_agents_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/list_layer_agents_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-171becfe95: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seams/safety_kernel_seam.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seams/safety_kernel_seam.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-17d7094311: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_agent_status_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_agent_status_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-19178ec014: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_all_guardians.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_all_guardians.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-1a396b5bc0: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_naming_scan_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_naming_scan_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-1acdeeed73: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/config/__init__.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/config/__init__.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-1b21cb31a8: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/debug_invocation_pipeline_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/debug_invocation_pipeline_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-1b8a01cfa1: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/execute_ssot_entrypoint.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/execute_ssot_entrypoint.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-1d430486c1: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_row_order_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_row_order_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-1d7f033237: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/json_formatter_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/json_formatter_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-1e3d9d1df6: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/check_syntax_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/check_syntax_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-1e6b871ed4: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/scan_testing_compliance_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/scan_testing_compliance_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-1f8d794d52: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/engines/execution_orchestrator.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/engines/execution_orchestrator.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-1fb26db410: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/mutation_prohibition.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/mutation_prohibition.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-209ceb9154: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_hierarchy_agent_dry_run_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_hierarchy_agent_dry_run_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-2137112911: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/structural_fix_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/structural_fix_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-22711ef48a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/ssot_audit_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/ssot_audit_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-2349dcc5b6: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/code_entity.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/code_entity.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-23b8fb9bd7: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/generate_dashboard_ssot_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/generate_dashboard_ssot_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-241d471227: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/bulk_mcp_harden_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/bulk_mcp_harden_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-24cd0bd117: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/extract_unique_content_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/extract_unique_content_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-25de567c4f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_hierarchy_healer_dry_run_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_hierarchy_healer_dry_run_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-298d194f42: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seams/canonical_truth_seam.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seams/canonical_truth_seam.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-2b8ffa1e73: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/action_capability.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/action_capability.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-2c25d785da: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/types/integration_contract_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/types/integration_contract_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-2c8acf1841: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/execute_ssot.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/execute_ssot.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-2d12cbfc5a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/fix_depth_violations_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/fix_depth_violations_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-3013aeab8a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/investigate_overlaps_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/investigate_overlaps_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-30b851c283: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/sovereign_precommit_no_hardcoded_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/sovereign_precommit_no_hardcoded_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-3191b98da4: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/subprocess_runner_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/subprocess_runner_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-3780187a37: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_infrastructure_target_issue_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_infrastructure_target_issue_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-37ee926ffe: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/reasoning/RootCustomsAgent.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/reasoning/RootCustomsAgent.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-3abd60bc81: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/aggressive_dedup_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/aggressive_dedup_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-3dfec9be3a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/check_duplicate_filenames_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/check_duplicate_filenames_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-3eebfafd08: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/hardened_anti_pattern_visitor.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/hardened_anti_pattern_visitor.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-3fdba89326: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/sovereign_lockdown_check_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/sovereign_lockdown_check_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-41bef03290: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_healing_metrics_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_healing_metrics_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-41c6eaaf9b: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/add_subatomic_safe_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/add_subatomic_safe_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-4227455ec4: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/meta_control/__init__.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/meta_control/__init__.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-4281655850: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_territory_counts_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_territory_counts_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-45eacd0a7e: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/__init__.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/__init__.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-48355655af: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_remaining_missing_heal_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_remaining_missing_heal_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-483fed0570: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/engines/escalation_router.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/engines/escalation_router.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-4d5b445696: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/execution.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/execution.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-4ea0642699: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_low_heal_territories_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_low_heal_territories_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-4f025fbfa4: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_agents_in_low_heal_territories_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_agents_in_low_heal_territories_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-4fa05c9135: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/types/artifact_validate_compat_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/types/artifact_validate_compat_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-4fa40603fb: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_escalation_determinism.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_escalation_determinism.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-50d3d50368: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/identify_agents_without_tests_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/identify_agents_without_tests_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-52c5d7e45c: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_gateway_bypass.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_gateway_bypass.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5338e608e9: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/c_c_measurement.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/c_c_measurement.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-55d931b546: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/comprehensive_archive_check_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/comprehensive_archive_check_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5683233d37: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/identify_low_quality_agents_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/identify_low_quality_agents_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5790ce2d53: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_drift_detection.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_drift_detection.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5867e1845e: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_sovereign_compliance_audit_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_sovereign_compliance_audit_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5a2d943ac6: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/path_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/path_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5a7b998e3f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/sovereign_convergence_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/sovereign_convergence_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5c2efa7130: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/sovereign_alignment_v2_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/sovereign_alignment_v2_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5ca807f9a6: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_all_checkpoint_files_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_all_checkpoint_files_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5cd3907113: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_classification_compliance.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_classification_compliance.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5d85f88948: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/types/guardian_registry_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/types/guardian_registry_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5ee6363512: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/logic_init_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/logic_init_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-602172e2f8: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/diagnose_syntax_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/diagnose_syntax_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-60a30968cf: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/sovereign_precommit_no_raw_prompts_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/sovereign_precommit_no_raw_prompts_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-617c97f3e7: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/investigate_sovereign_base_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/investigate_sovereign_base_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-61abd1cb6d: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_cross_layer_mutation.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_cross_layer_mutation.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-62395c3c36: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/types/routing_config_seal_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/types/routing_config_seal_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-630ccbf72f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/ssot_discovery_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/ssot_discovery_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-63d37c5b40: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/heal_schema_visitor.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/heal_schema_visitor.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-63f80cdad0: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/fix_mission_runner_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/fix_mission_runner_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-64201b4a85: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-644696d36b: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/check_from_utils_duplicates_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/check_from_utils_duplicates_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-654dc84d15: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seam/seam_audit.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seam/seam_audit.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-679a5fcc72: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/drift.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/drift.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-68d25271b9: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_missing_invocations_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_missing_invocations_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-69f172c694: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_naming_law_check_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_naming_law_check_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-6c424e5ab2: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/init_setup_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/init_setup_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-6ce59d0a1d: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/project_root_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/project_root_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-6e876e7b95: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/add_subatomic_tests_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/add_subatomic_tests_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-6fcfc75796: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/gravity_audit_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/gravity_audit_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-703997ff66: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/ssot_adapters.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/ssot_adapters.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-709658d72b: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/validate_sovereign_structure_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/validate_sovereign_structure_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-70bd9040e7: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/collision_resolver.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/collision_resolver.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-7115f0d80b: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/timeout_decorator_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/timeout_decorator_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-71e4f87a68: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/bloat_analysis_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/bloat_analysis_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-720919beeb: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_contract_integrity.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_contract_integrity.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-72e5c236a4: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/__init__.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/__init__.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-731d502b76: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/delete_duplicates_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/delete_duplicates_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-7578995422: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/engines/__init__.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/engines/__init__.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-79a5bf6e88: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/bulk_hierarchy_heal_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/bulk_hierarchy_heal_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-7a1050e65e: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/check_protected_files_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/check_protected_files_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-7f3dfe9167: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/validate_drilldown_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/validate_drilldown_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-805e8a9056: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/flatten_scripts_directory_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/flatten_scripts_directory_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-8667b337e0: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/fix_remaining_depth_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/fix_remaining_depth_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-8850d7cab0: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/force_annexation_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/force_annexation_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-8912ce271b: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_heal_invocation_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_heal_invocation_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-89c19ccf30: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/engines/timeshift_router.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/engines/timeshift_router.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-89e4c49e95: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/scorched_earth_merge_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/scorched_earth_merge_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-8af430ca0f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/runtime_guard.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/runtime_guard.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-8bf361dcb8: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_base_class_agents_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_base_class_agents_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-8c5906406e: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/__init__.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/__init__.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-8d2172925f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_intentional_variants_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_intentional_variants_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-8d4b3db95a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/types/routing_contracts_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/types/routing_contracts_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-8f7c227d32: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_change_package_activation.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_change_package_activation.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-901ec34a39: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/config/path_constants.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/config/path_constants.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-907a75c36d: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/vigilance_routing.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/vigilance_routing.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-91396515dd: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/manifest_guardian_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/manifest_guardian_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-9148a27501: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seams/safety_reasoning_seam.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seams/safety_reasoning_seam.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-920d1da217: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/function_tool.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/function_tool.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-9327a630e4: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/legacy_agent_name_allowlist.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/legacy_agent_name_allowlist.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-9914b3ce2f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/fix_all_tunnels_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/fix_all_tunnels_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-9a9e6f3ada: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/runtime_mutation_guard.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/runtime_mutation_guard.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-9d19f701d3: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/config/structure_blueprint_data.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/config/structure_blueprint_data.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-9fbd6ebde8: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_real_duplicates_v2_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_real_duplicates_v2_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-a0968d0385: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/forensic_discovery_prep.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/forensic_discovery_prep.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-a1fea70c74: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_manifest_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_manifest_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-a207aef1a1: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/colors.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/colors.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-a20cda3452: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/forward_rolling_facade.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/forward_rolling_facade.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-a3495bbebc: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seams/layer_emission_seam.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seams/layer_emission_seam.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-a3aa2b3fad: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/execute_safe_deletion_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/execute_safe_deletion_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-a4085b35a9: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/complexity_visitor_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/complexity_visitor_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-a5baeb3f4f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/debris_hunter.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/debris_hunter.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-a719c412c4: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_health_calculation_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_health_calculation_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-a80be22bf6: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/engines/shadow_routing_wiring.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/engines/shadow_routing_wiring.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-a9a3f406f4: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/coverage.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/coverage.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-aa40f7c784: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/boot_sequence.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/boot_sequence.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-aab5b6b7c8: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_hygiene.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_hygiene.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-aac9d210c3: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/align_tests_structure_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/align_tests_structure_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-abcf689982: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/emoji_fixer.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/emoji_fixer.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-ad365b0cd9: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/chunk_type.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/chunk_type.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-b0395f520f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/compare_archive_to_current_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/compare_archive_to_current_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-b0d5202a5f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/cache_data_access_get_info_request_init_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/cache_data_access_get_info_request_init_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-b17d273844: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/types/artifact_typed_compat_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/types/artifact_typed_compat_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-b4d84516a9: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-b67a1895e4: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seams/redis_decision_cache.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seams/redis_decision_cache.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-b67b86dc3a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/add_dataclass_to_agents_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/add_dataclass_to_agents_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-b85263990f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/cache_init_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/cache_init_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-b939d062d6: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/extract_agent_duplicates_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/extract_agent_duplicates_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-baeaadf682: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/archive_duplicates_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/archive_duplicates_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-be06589f10: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/compliance_gate_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/compliance_gate_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-bf0bce3531: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/agent_validation_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/agent_validation_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-bf20d852d0: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/debug_target_mismatch_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/debug_target_mismatch_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-c1646a40c9: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/check_rglob_usage_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/check_rglob_usage_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-c29cb4934b: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-c309501b0b: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/root_hygiene_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/root_hygiene_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-c98bd1e972: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/reasoning.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/reasoning.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-ca7d298bbb: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_location_alignment.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_location_alignment.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-cbbd1c2894: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/dashboard_ssot_definitions_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/dashboard_ssot_definitions_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-cbd50668ee: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_manifest.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_manifest.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-cc37501b07: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seams/observability_seam.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seams/observability_seam.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-cd97504ccc: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_mro_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_mro_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-cdba37344c: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/logic_data_access_init_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/logic_data_access_init_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-cff85af5ad: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/disposition.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/disposition.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d00b61b0da: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/count_territories_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/count_territories_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d1dfe089e8: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/base_tool.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/base_tool.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d280158168: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/engines/reasoning_policy_engine.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/engines/reasoning_policy_engine.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d34dff5a33: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seams/safety_enforcement_seam.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seams/safety_enforcement_seam.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d441d60bd3: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seams/c0_context_retriever.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seams/c0_context_retriever.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d45cb3bc2a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/file_analysis.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/file_analysis.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d534372834: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/agent_capability_supplement_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/agent_capability_supplement_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d5c34f5246: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_base_agent_names_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_base_agent_names_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d76549b389: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/demo_cli_functionality_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/demo_cli_functionality_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d85aadcf2b: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/auto_remediate_signatures_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/auto_remediate_signatures_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d86eae2dbb: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/base_tool_script.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/base_tool_script.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-da976dd3f1: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_hygiene_guardian_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_hygiene_guardian_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-db3762a6be: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/hardened_orchestrator_wrapper_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/hardened_orchestrator_wrapper_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-dbb7c534e3: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/component_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/component_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-dbf4983004: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/agent_analysis_config.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/agent_analysis_config.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-df2e1042a8: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seams/learning_seam.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seams/learning_seam.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e004b97115: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/error_handler.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/error_handler.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e0ef22eeb0: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/types/__init__.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/types/__init__.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e166f11386: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/compare_autonomy_guardian_files_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/compare_autonomy_guardian_files_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e1b29c7822: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_non_hardened_l0_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_non_hardened_l0_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e1f79b973a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/runtime_state_digest.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/runtime_state_digest.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e41c24a4a1: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/archive_duplicate_tests_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/archive_duplicate_tests_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e47cc1b50d: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_low_typed_documented_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_low_typed_documented_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e4f2baa803: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/boot_sequence_enforcer.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/boot_sequence_enforcer.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e77bca4c9e: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/types/guardian_contract_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/types/guardian_contract_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e80ffd573c: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/scan_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/scan_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e8373d5f2f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/seams/safety_validators_seam.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/seams/safety_validators_seam.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-ea4f7e43e7: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/reasoning/__init__.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/reasoning/__init__.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-ebb7959240: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/types/reasoning_intensity_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/types/reasoning_intensity_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-ed04008e69: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_hygiene_naming_audit_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_hygiene_naming_audit_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-ed1f39349d: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/gatekeeper_lock_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/gatekeeper_lock_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-eecc03251d: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_architecture_governance.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_architecture_governance.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-f06a058609: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/file_utils_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/file_utils_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-f0cd5c643a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_manifest_cleanliness_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_manifest_cleanliness_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-f0d5935404: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/core_integrity_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/core_integrity_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-f1e6290738: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/add_test_coverage_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/add_test_coverage_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-f2946d1fcf: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/handler.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/handler.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-f2c2f1eee2: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/engines/path_router.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/engines/path_router.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-f400cfdd8a: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_missing_agents_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_missing_agents_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-f514699394: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/add_subatomic_testing_to_agents_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/add_subatomic_testing_to_agents_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-f73b1a2b33: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/populate_ssot_folders_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/populate_ssot_folders_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-f822a2bfc4: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/types/v15_contracts_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/types/v15_contracts_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-f88702ec50: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/class_info.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/class_info.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-fb12ac7665: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/ssot_cli.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/ssot_cli.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-fc856a9c9e: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/extract_net.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/extract_net.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-fcabbc3a8c: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/meta_control/meta_learning_bus.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/meta_control/meta_learning_bus.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-fd9209f5fd: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_corrupted_files_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_corrupted_files_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-fd9a500efd: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/validate_base_agents_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/validate_base_agents_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-fe0653ac85: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/utils/find_misnamed_agents_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/utils/find_misnamed_agents_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-ff2c0f1307: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/fission_executor_util.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/fission_executor_util.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-ff7681c241: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L0_routing/scripts/core_synthesis_executor.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L0_routing/scripts/core_synthesis_executor.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### L0-GAP-002: Reasoning Policy Engine

**Priority:** MEDIUM

**Architectural Intent:**
Cache immutable policy configurations to avoid repeated L4 state lookups

**Implementation Reality:**
reasoning_policy_engine.py does not use policy_registry_cache.py

**Impact:**
Policy config fetched from L4 state on every request

**Evidence Files:
- `agentic_core/L0_routing/engines/reasoning_policy_engine.py`

**Recommended Fix:**
Wrap policy_config retrieval with PolicyRegistryCache.get_or_fetch()

---

### NON-L2-MUTATION-RISK-01bd191154: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/full_agent_discovery.py appears to perform write-like operations outside the expected execution choke point: append, get_git_commit

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/full_agent_discovery.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-01e607be58: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/validate_table2_data_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/validate_table2_data_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-04f677f1e8: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/engines/assembly_stage.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/engines/assembly_stage.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-05d35e41f1: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/compare_ui_components_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/compare_ui_components_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-0cf808e328: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/apps_taxonomy_guard.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-0de89986dc: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_open_heal_invocations_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_open_heal_invocations_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-0fe12b3015: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_missing_invocation_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_missing_invocation_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-10e336ec1a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/trim_remaining_airlocks_util.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/trim_remaining_airlocks_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-118d2d363f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/meta_control/meta_apply.py appears to perform write-like operations outside the expected execution choke point: _atomic_write_json, assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/meta_control/meta_apply.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-17d7094311: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_agent_status_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_agent_status_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-19178ec014: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_all_guardians.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_all_guardians.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-1a396b5bc0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_naming_scan_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_naming_scan_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-1b21cb31a8: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/debug_invocation_pipeline_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/debug_invocation_pipeline_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-1e6b871ed4: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/scan_testing_compliance_util.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/scan_testing_compliance_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-1fb26db410: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/mutation_prohibition.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, rename, write, write_bytes, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/mutation_prohibition.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-2137112911: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/structural_fix_util.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write, writelines

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/structural_fix_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-22711ef48a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/ssot_audit_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/ssot_audit_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-2349dcc5b6: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/code_entity.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/code_entity.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-23b8fb9bd7: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/generate_dashboard_ssot_util.py appears to perform write-like operations outside the expected execution choke point: write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/generate_dashboard_ssot_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-241d471227: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/bulk_mcp_harden_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/bulk_mcp_harden_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-24cd0bd117: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/extract_unique_content_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/extract_unique_content_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-2c25d785da: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/types/integration_contract_types.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/types/integration_contract_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-2c8acf1841: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/execute_ssot.py appears to perform write-like operations outside the expected execution choke point: _get_write_gateway, _write_mandatory_json_output, append, assert_no_persistent_write, get_write_gateway, grant_write_permission, persist_record, persist_to_disk

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/execute_ssot.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-2d12cbfc5a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/fix_depth_violations_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/fix_depth_violations_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-3013aeab8a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/investigate_overlaps_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/investigate_overlaps_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-30b851c283: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/sovereign_precommit_no_hardcoded_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/sovereign_precommit_no_hardcoded_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-3191b98da4: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/subprocess_runner_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/subprocess_runner_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-37ee926ffe: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/reasoning/RootCustomsAgent.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/reasoning/RootCustomsAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-3abd60bc81: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/aggressive_dedup_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/aggressive_dedup_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-3dfec9be3a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/check_duplicate_filenames_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/check_duplicate_filenames_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-3eebfafd08: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/hardened_anti_pattern_visitor.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/hardened_anti_pattern_visitor.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-41c6eaaf9b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/add_subatomic_safe_util.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/add_subatomic_safe_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4281655850: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_territory_counts_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_territory_counts_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4d5b445696: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/execution.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/execution.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4ea0642699: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_low_heal_territories_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_low_heal_territories_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4f025fbfa4: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_agents_in_low_heal_territories_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_agents_in_low_heal_territories_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4fa40603fb: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_escalation_determinism.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_escalation_determinism.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-50d3d50368: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/identify_agents_without_tests_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/identify_agents_without_tests_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-52c5d7e45c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_gateway_bypass.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_gateway_bypass.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5338e608e9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/c_c_measurement.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/c_c_measurement.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-55d931b546: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/comprehensive_archive_check_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/comprehensive_archive_check_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5683233d37: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/identify_low_quality_agents_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/identify_low_quality_agents_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5790ce2d53: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_drift_detection.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_drift_detection.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5a7b998e3f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/sovereign_convergence_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/sovereign_convergence_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5c2efa7130: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/sovereign_alignment_v2_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/sovereign_alignment_v2_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5cd3907113: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_classification_compliance.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_classification_compliance.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-602172e2f8: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/diagnose_syntax_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/diagnose_syntax_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-60a30968cf: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/sovereign_precommit_no_raw_prompts_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/sovereign_precommit_no_raw_prompts_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-61abd1cb6d: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_cross_layer_mutation.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_cross_layer_mutation.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-630ccbf72f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/ssot_discovery_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/ssot_discovery_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-63d37c5b40: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/heal_schema_visitor.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/heal_schema_visitor.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-63f80cdad0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/fix_mission_runner_util.py appears to perform write-like operations outside the expected execution choke point: append, writelines

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/fix_mission_runner_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-64201b4a85: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-644696d36b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/check_from_utils_duplicates_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/check_from_utils_duplicates_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-654dc84d15: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/seam/seam_audit.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/seam/seam_audit.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-679a5fcc72: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/drift.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/drift.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-68d25271b9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_missing_invocations_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_missing_invocations_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-69f172c694: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_naming_law_check_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_naming_law_check_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-6e876e7b95: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/add_subatomic_tests_util.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/add_subatomic_tests_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-6fcfc75796: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/gravity_audit_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/gravity_audit_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-709658d72b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/validate_sovereign_structure_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/validate_sovereign_structure_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-70bd9040e7: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/collision_resolver.py appears to perform write-like operations outside the expected execution choke point: append, rename

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/collision_resolver.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-71e4f87a68: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/bloat_analysis_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/bloat_analysis_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-720919beeb: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_contract_integrity.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_contract_integrity.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-731d502b76: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/delete_duplicates_util.py appears to perform write-like operations outside the expected execution choke point: delete_duplicates

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/delete_duplicates_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-79a5bf6e88: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/bulk_hierarchy_heal_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/bulk_hierarchy_heal_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-7a1050e65e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/check_protected_files_util.py appears to perform write-like operations outside the expected execution choke point: append, get_commit_message

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/check_protected_files_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-805e8a9056: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/flatten_scripts_directory_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/flatten_scripts_directory_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-80f6bbd724: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/meta_control/config_store.py appears to perform write-like operations outside the expected execution choke point: _atomic_write_json, append, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/meta_control/config_store.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8667b337e0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/fix_remaining_depth_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/fix_remaining_depth_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8850d7cab0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/force_annexation_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/force_annexation_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-89e4c49e95: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/scorched_earth_merge_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/scorched_earth_merge_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8c0efc5c69: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/execution_gateway.py appears to perform write-like operations outside the expected execution choke point: _commit_mutation, append, prepare_commit

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/execution_gateway.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8d2172925f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/verify_intentional_variants_util.py appears to perform write-like operations outside the expected execution choke point: append, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/verify_intentional_variants_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8d4b3db95a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/types/routing_contracts_types.py appears to perform write-like operations outside the expected execution choke point: append, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/types/routing_contracts_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8f7c227d32: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_change_package_activation.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_change_package_activation.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-91396515dd: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/manifest_guardian_util.py appears to perform write-like operations outside the expected execution choke point: write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/manifest_guardian_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-96b0ce3dd5: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/meta_control/meta_apply_ops.py appears to perform write-like operations outside the expected execution choke point: _atomic_write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/meta_control/meta_apply_ops.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-9914b3ce2f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/fix_all_tunnels_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/fix_all_tunnels_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-9fbd6ebde8: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_real_duplicates_v2_util.py appears to perform write-like operations outside the expected execution choke point: append, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_real_duplicates_v2_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a0968d0385: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/forensic_discovery_prep.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, atomic_write, get_git_commit, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/forensic_discovery_prep.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a207aef1a1: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/colors.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/colors.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a20cda3452: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/forward_rolling_facade.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/forward_rolling_facade.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a3aa2b3fad: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/execute_safe_deletion_util.py appears to perform write-like operations outside the expected execution choke point: delete_duplicates

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/execute_safe_deletion_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a4085b35a9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/complexity_visitor_util.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, getwriter, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/complexity_visitor_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a5baeb3f4f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/debris_hunter.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/debris_hunter.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a9a3f406f4: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/coverage.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/coverage.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-aa40f7c784: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/boot_sequence.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/boot_sequence.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-aab5b6b7c8: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_hygiene.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_hygiene.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-aac9d210c3: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/align_tests_structure_util.py appears to perform write-like operations outside the expected execution choke point: write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/align_tests_structure_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-abcf689982: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/emoji_fixer.py appears to perform write-like operations outside the expected execution choke point: write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/emoji_fixer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ad365b0cd9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/chunk_type.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/chunk_type.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ad990f9e8e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/types/routing_artifact_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/types/routing_artifact_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b0395f520f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/compare_archive_to_current_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/compare_archive_to_current_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b12a427fe6: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/trace_id_generator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/trace_id_generator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b4d84516a9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, delete_empty_folders, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b67a1895e4: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/seams/redis_decision_cache.py appears to perform write-like operations outside the expected execution choke point: delete

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/seams/redis_decision_cache.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b67b86dc3a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/add_dataclass_to_agents_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/add_dataclass_to_agents_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b939d062d6: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/extract_agent_duplicates_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/extract_agent_duplicates_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-baeaadf682: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/archive_duplicates_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/archive_duplicates_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-be06589f10: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/compliance_gate_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/compliance_gate_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-bf0bce3531: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/agent_validation_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/agent_validation_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-bf20d852d0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/debug_target_mismatch_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/debug_target_mismatch_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c1646a40c9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/check_rglob_usage_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/check_rglob_usage_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c29cb4934b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c309501b0b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/root_hygiene_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/root_hygiene_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c98bd1e972: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/reasoning.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/reasoning.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ca7d298bbb: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_location_alignment.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_location_alignment.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-cbd50668ee: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_manifest.py appears to perform write-like operations outside the expected execution choke point: write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_manifest.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-cff85af5ad: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/disposition.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/disposition.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d3af3638d6: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/types/determinism_types.py appears to perform write-like operations outside the expected execution choke point: StateCommitInvalid, append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/types/determinism_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d43a714ba0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/types/artifact_validators_types.py appears to perform write-like operations outside the expected execution choke point: validate_stale_write_incident

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/types/artifact_validators_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d45cb3bc2a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/file_analysis.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/file_analysis.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d534372834: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/agent_capability_supplement_util.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/agent_capability_supplement_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d85aadcf2b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/auto_remediate_signatures_util.py appears to perform write-like operations outside the expected execution choke point: append, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/auto_remediate_signatures_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-da976dd3f1: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_hygiene_guardian_util.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_hygiene_guardian_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-dbf4983004: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/agent_analysis_config.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/agent_analysis_config.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e1f1b73f31: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/enforcement/boundary_contracts.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/enforcement/boundary_contracts.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e1f79b973a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/runtime_state_digest.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/runtime_state_digest.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e41c24a4a1: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/archive_duplicate_tests_util.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/archive_duplicate_tests_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e4cbb2f1ec: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/types/determinism_contracts_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/types/determinism_contracts_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e77bca4c9e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/types/guardian_contract_types.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/types/guardian_contract_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e80ffd573c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/scan_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/scan_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ed04008e69: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_hygiene_naming_audit_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_hygiene_naming_audit_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ed1f39349d: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/gatekeeper_lock_util.py appears to perform write-like operations outside the expected execution choke point: append, check_commit_message_override, get_commit_message

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/gatekeeper_lock_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-eecc03251d: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/run_guardian_architecture_governance.py appears to perform write-like operations outside the expected execution choke point: append, write_guardian_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/run_guardian_architecture_governance.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f06a058609: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/file_utils_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/file_utils_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f0d5935404: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/core_integrity_util.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/core_integrity_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f1e6290738: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/add_test_coverage_util.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/add_test_coverage_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f2946d1fcf: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/handler.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/handler.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f514699394: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/add_subatomic_testing_to_agents_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/add_subatomic_testing_to_agents_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f73b1a2b33: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/populate_ssot_folders_util.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/populate_ssot_folders_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f88702ec50: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/class_info.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/class_info.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-fb12ac7665: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/ssot_cli.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/ssot_cli.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-fc856a9c9e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/extract_net.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/extract_net.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-fcabbc3a8c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/meta_control/meta_learning_bus.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/meta_control/meta_learning_bus.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-fd9209f5fd: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/find_corrupted_files_util.py appears to perform write-like operations outside the expected execution choke point: append, safe_write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/find_corrupted_files_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-fd9a500efd: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/validate_base_agents_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/validate_base_agents_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-fe0653ac85: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/utils/find_misnamed_agents_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/utils/find_misnamed_agents_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ff2c0f1307: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/fission_executor_util.py appears to perform write-like operations outside the expected execution choke point: append, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/fission_executor_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ff7681c241: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L0_routing/scripts/core_synthesis_executor.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L0_routing/scripts/core_synthesis_executor.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

## L1 Layer Gaps

### L1-GAP-001: Cognitive Engine Tool Resolution

**Priority:** HIGH

**Architectural Intent:**
Cache expensive tool embedding computations to avoid repeated API calls

**Implementation Reality:**
cognitive_engine.py does not use tool_embedding_cache.py

**Impact:**
Tool embeddings recomputed on every cognition cycle

**Evidence Files:
- `agentic_core/L1_cognition/engines/cognitive_engine.py`

**Recommended Fix:**
Import ToolEmbeddingCache and wrap embedding generation with cache.get_or_fetch()

---

### LAYER-UPWARD-IMPORT-33c74c35e9: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L1_cognition/engines/domain_manager.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L1_cognition/engines/domain_manager.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-4a6337e0d1: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L1_cognition/utils/constants_util.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L1_cognition/utils/constants_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-a01f63debe: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L1_cognition/utils/agentic_constants_util.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L1_cognition/utils/agentic_constants_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### PROMPT-TAXONOMY-GAP-1f8d794d52: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
execution_orchestrator.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=present, I0=missing, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L0_routing/engines/execution_orchestrator.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, I0, C0, U0

---

### PROMPT-TAXONOMY-GAP-2fb9c2152f: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
prompt_artifact_cache.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=present, D0=present, I0=present, C0=present, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L1_cognition/engines/prompt_artifact_cache.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: U0

---

### PROMPT-TAXONOMY-GAP-455d7b7dca: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
sandbox_envelope_types.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=missing, I0=present, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L2_execution/types/sandbox_envelope_types.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, D0, C0, U0

---

### PROMPT-TAXONOMY-GAP-53e1b1633f: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
execution_trace_types.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=missing, I0=present, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L2_execution/types/execution_trace_types.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, D0, C0, U0

---

### PROMPT-TAXONOMY-GAP-8a6344918d: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
qwen_vllm_inference.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=present, D0=missing, I0=missing, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L2_execution/healers/qwen_vllm_inference.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: D0, I0, C0, U0

---

### PROMPT-TAXONOMY-GAP-94ab5260b1: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
execution_gateway.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=missing, I0=present, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L2_execution/engines/execution_gateway.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, D0, C0, U0

---

### PROMPT-TAXONOMY-GAP-d23b3738f0: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
boundary_verifier.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=missing, I0=present, C0=missing, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/boundary_verifier.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, D0, C0, U0

---

### PROMPT-TAXONOMY-GAP-f88702ec50: Prompt Taxonomy Assembly Coverage

**Priority:** HIGH

**Architectural Intent:**
Assembled prompts should cover canonical taxonomy slots S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture.

**Implementation Reality:**
class_info.py appears to assemble or package prompts but has incomplete taxonomy evidence: S0=missing, D0=present, I0=missing, C0=present, U0=missing

**Impact:**
Prompt packages may omit required rulebooks, fences, instructional identity, dependency context, or raw user intent, causing drift from the governed prompt model.

**Evidence Files:
- `agentic_core/L0_routing/scripts/class_info.py`

**Recommended Fix:**
Add explicit slot assembly or manifest fields for the missing taxonomy slots: S0, I0, U0

---

### L1-GAP-PROMPT-bd4796a6e6: Prompt Artifact Retrieval

**Priority:** MEDIUM

**Architectural Intent:**
Cache parsed prompt templates to avoid repeated file I/O and parsing

**Implementation Reality:**
prompts_util.py does not use prompt_artifact_cache

**Impact:**
Prompt templates re-read and re-parsed on every request

**Evidence Files:
- `agentic_core/L1_cognition/utils/prompts_util.py`

**Recommended Fix:**
Wrap prompt loading with prompt_artifact_cache.get_or_fetch()

---

### PROMPT-MANIFEST-GAP-1f8d794d52: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
execution_orchestrator.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L0_routing/engines/execution_orchestrator.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-2fb9c2152f: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
prompt_artifact_cache.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L1_cognition/engines/prompt_artifact_cache.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-455d7b7dca: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
sandbox_envelope_types.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L2_execution/types/sandbox_envelope_types.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-53e1b1633f: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
execution_trace_types.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L2_execution/types/execution_trace_types.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-8a6344918d: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
qwen_vllm_inference.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L2_execution/healers/qwen_vllm_inference.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-94ab5260b1: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
execution_gateway.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L2_execution/engines/execution_gateway.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-d23b3738f0: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
boundary_verifier.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/boundary_verifier.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

### PROMPT-MANIFEST-GAP-f88702ec50: Prompt Package Manifest Integrity

**Priority:** MEDIUM

**Architectural Intent:**
Governed prompt assembly should emit a manifest hash for parity and auditability.

**Implementation Reality:**
class_info.py shows no manifest hash evidence.

**Impact:**
You cannot prove deterministic prompt-package parity across runs.

**Evidence Files:
- `agentic_core/L0_routing/scripts/class_info.py`

**Recommended Fix:**
Emit and persist a manifest hash for the final governed prompt package.

---

## L2 Layer Gaps

### EMBEDDING-PLACEMENT-GAP-0b6740e0c1: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/types/replay_envelope_types.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/types/replay_envelope_types.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-26e357cc9a: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/determinism/__init__.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/determinism/__init__.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-4e6b3cb947: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/SovereignLLMGateway.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-6467cc85be: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/healers/qwen_meta_learning.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/healers/qwen_meta_learning.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-72006d5e91: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/determinism.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/determinism.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-7b73f1f736: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/reasoning/RedisSovereignAgent.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/reasoning/RedisSovereignAgent.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-8010bc340b: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/healers/failure_signal_normalizer.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/healers/failure_signal_normalizer.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-a9f4e00527: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/key_derivation.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/key_derivation.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-be16c001de: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/config/mcp_registry.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/config/mcp_registry.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-d5360a7cc2: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/engines/tool_registry.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/engines/tool_registry.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-db8b515ec9: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/runtime_interceptor.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/runtime_interceptor.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-e08f66b45f: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/determinism/negative_control_harness.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/determinism/negative_control_harness.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-f9886d0a48: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L2_execution/healers/healing_tier_config.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L2_execution/healers/healing_tier_config.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### GATEWAY-BYPASS-RISK-283e1f9eeb: Sovereign Gateway Bypass Risk

**Priority:** HIGH

**Architectural Intent:**
All outbound LLM egress should flow through SovereignLLMGateway only.

**Implementation Reality:**
agentic_core/L2_execution/types/vllm_gateway_adapter_types.py imports provider SDK seams directly: agentic_core.L2_execution.types.vllm_gateway_integration_types, agentic_core.L2_execution.types.vllm_invariant_verifier_types

**Impact:**
Direct SDK imports create possible provider bypasses outside the sole gateway seam.

**Evidence Files:
- `agentic_core/L2_execution/types/vllm_gateway_adapter_types.py`

**Recommended Fix:**
Route all provider interactions through SovereignLLMGateway and remove direct SDK imports.

---

### GATEWAY-BYPASS-RISK-5de3900449: Sovereign Gateway Bypass Risk

**Priority:** HIGH

**Architectural Intent:**
All outbound LLM egress should flow through SovereignLLMGateway only.

**Implementation Reality:**
agentic_core/L2_execution/types/vllm_replay_validator_types.py imports provider SDK seams directly: agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types

**Impact:**
Direct SDK imports create possible provider bypasses outside the sole gateway seam.

**Evidence Files:
- `agentic_core/L2_execution/types/vllm_replay_validator_types.py`

**Recommended Fix:**
Route all provider interactions through SovereignLLMGateway and remove direct SDK imports.

---

### GATEWAY-BYPASS-RISK-8a6344918d: Sovereign Gateway Bypass Risk

**Priority:** HIGH

**Architectural Intent:**
All outbound LLM egress should flow through SovereignLLMGateway only.

**Implementation Reality:**
agentic_core/L2_execution/healers/qwen_vllm_inference.py imports provider SDK seams directly: vllm

**Impact:**
Direct SDK imports create possible provider bypasses outside the sole gateway seam.

**Evidence Files:
- `agentic_core/L2_execution/healers/qwen_vllm_inference.py`

**Recommended Fix:**
Route all provider interactions through SovereignLLMGateway and remove direct SDK imports.

---

### GATEWAY-BYPASS-RISK-9fc93580bd: Sovereign Gateway Bypass Risk

**Priority:** HIGH

**Architectural Intent:**
All outbound LLM egress should flow through SovereignLLMGateway only.

**Implementation Reality:**
agentic_core/L2_execution/types/vllm_invariant_verifier_types.py imports provider SDK seams directly: agentic_core.L2_execution.types.vllm_invariant_contract_types

**Impact:**
Direct SDK imports create possible provider bypasses outside the sole gateway seam.

**Evidence Files:
- `agentic_core/L2_execution/types/vllm_invariant_verifier_types.py`

**Recommended Fix:**
Route all provider interactions through SovereignLLMGateway and remove direct SDK imports.

---

### GATEWAY-BYPASS-RISK-a3223a2f1e: Sovereign Gateway Bypass Risk

**Priority:** HIGH

**Architectural Intent:**
All outbound LLM egress should flow through SovereignLLMGateway only.

**Implementation Reality:**
agentic_core/L2_execution/types/vllm_concurrency_types.py imports provider SDK seams directly: agentic_core.L2_execution.types.vllm_serving_profile_types, agentic_core.L2_execution.types.vllm_token_budget_types

**Impact:**
Direct SDK imports create possible provider bypasses outside the sole gateway seam.

**Evidence Files:
- `agentic_core/L2_execution/types/vllm_concurrency_types.py`

**Recommended Fix:**
Route all provider interactions through SovereignLLMGateway and remove direct SDK imports.

---

### GATEWAY-BYPASS-RISK-d8a744b255: Sovereign Gateway Bypass Risk

**Priority:** HIGH

**Architectural Intent:**
All outbound LLM egress should flow through SovereignLLMGateway only.

**Implementation Reality:**
agentic_core/L2_execution/healers/healing_provider_adapters.py imports provider SDK seams directly: google.generativeai, openai

**Impact:**
Direct SDK imports create possible provider bypasses outside the sole gateway seam.

**Evidence Files:
- `agentic_core/L2_execution/healers/healing_provider_adapters.py`

**Recommended Fix:**
Route all provider interactions through SovereignLLMGateway and remove direct SDK imports.

---

### GATEWAY-BYPASS-RISK-db2a859e49: Sovereign Gateway Bypass Risk

**Priority:** HIGH

**Architectural Intent:**
All outbound LLM egress should flow through SovereignLLMGateway only.

**Implementation Reality:**
agentic_core/L2_execution/types/vllm_gateway_integration_types.py imports provider SDK seams directly: agentic_core.L2_execution.types.vllm_backpressure_types, agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types, agentic_core.L2_execution.types.vllm_serving_profile_types, agentic_core.L2_execution.types.vllm_token_budget_types

**Impact:**
Direct SDK imports create possible provider bypasses outside the sole gateway seam.

**Evidence Files:
- `agentic_core/L2_execution/types/vllm_gateway_integration_types.py`

**Recommended Fix:**
Route all provider interactions through SovereignLLMGateway and remove direct SDK imports.

---

### GATEWAY-BYPASS-RISK-e3540a9895: Sovereign Gateway Bypass Risk

**Priority:** HIGH

**Architectural Intent:**
All outbound LLM egress should flow through SovereignLLMGateway only.

**Implementation Reality:**
agentic_core/L2_execution/types/vllm_backpressure_types.py imports provider SDK seams directly: agentic_core.L2_execution.types.vllm_token_budget_types

**Impact:**
Direct SDK imports create possible provider bypasses outside the sole gateway seam.

**Evidence Files:
- `agentic_core/L2_execution/types/vllm_backpressure_types.py`

**Recommended Fix:**
Route all provider interactions through SovereignLLMGateway and remove direct SDK imports.

---

### GOVERNANCE-STAMP-GAP-089b6591d4: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-116721669f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/capability/promotion_token.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/capability/promotion_token.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-26b74d59d3: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/firecracker_manager.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/firecracker_manager.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-26f0ba74c8: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/types/token_enforcement_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/types/token_enforcement_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-2a5a3a48e6: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/healers/qwen_gpu_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/healers/qwen_gpu_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-2ea4135613: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-401804b7b4: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/provider_substitution_prohibition.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/provider_substitution_prohibition.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-462f37c35b: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/healers/signature_invalidator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/healers/signature_invalidator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4e6b3cb947: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/SovereignLLMGateway.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-59e441e584: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/docker_sandbox.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/docker_sandbox.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-5de3900449: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/types/vllm_replay_validator_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/types/vllm_replay_validator_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6b19ef1f64: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/deterministic_loop_detector.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/deterministic_loop_detector.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-7edfab05a8: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/healer_pipe_order.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/healer_pipe_order.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-7fd9eed8f5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/filesystem_mcp.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/filesystem_mcp.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-80b001c868: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/provider_binding_determinism.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/provider_binding_determinism.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-82ece49bbe: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/tool_policy_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/tool_policy_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-83850aa0d5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/manifest_hash_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/manifest_hash_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-86a09ba68a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/sovereign_sandbox_isolation.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/sovereign_sandbox_isolation.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-9a37d3de15: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/capability_revoker.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/capability_revoker.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-9a90bf15a6: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/durable_write_wrapper.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/durable_write_wrapper.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a3b0931c1c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/network_egress_guard.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/network_egress_guard.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a8d0dfb3fd: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/preventative_sandbox.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/preventative_sandbox.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-b019179ea3: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/write_set_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/write_set_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-b9c84d5715: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/__init__.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/__init__.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d929891aa9: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/transcript_freezer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/transcript_freezer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e1b20d1815: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/types/tool_enforcement_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/types/tool_enforcement_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f16a55c4a9: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/key_source.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/key_source.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### L2-GAP-VALIDATOR-2a5a3a48e6: Schema Validation Hot Path

**Priority:** HIGH

**Architectural Intent:**
Cache compiled JSON schema validators to avoid repeated compilation

**Implementation Reality:**
qwen_gpu_validator.py does not use schema_validator_cache

**Impact:**
Schema validators recompiled on every validation request

**Evidence Files:
- `agentic_core/L2_execution/healers/qwen_gpu_validator.py`

**Recommended Fix:**
Wrap validator compilation with schema_validator_cache.get_or_fetch()

---

### L2-GAP-VALIDATOR-462f37c35b: Schema Validation Hot Path

**Priority:** HIGH

**Architectural Intent:**
Cache compiled JSON schema validators to avoid repeated compilation

**Implementation Reality:**
signature_invalidator.py does not use schema_validator_cache

**Impact:**
Schema validators recompiled on every validation request

**Evidence Files:
- `agentic_core/L2_execution/healers/signature_invalidator.py`

**Recommended Fix:**
Wrap validator compilation with schema_validator_cache.get_or_fetch()

---

### L2-GAP-VALIDATOR-5de3900449: Schema Validation Hot Path

**Priority:** HIGH

**Architectural Intent:**
Cache compiled JSON schema validators to avoid repeated compilation

**Implementation Reality:**
vllm_replay_validator_types.py does not use schema_validator_cache

**Impact:**
Schema validators recompiled on every validation request

**Evidence Files:
- `agentic_core/L2_execution/types/vllm_replay_validator_types.py`

**Recommended Fix:**
Wrap validator compilation with schema_validator_cache.get_or_fetch()

---

### L2-GAP-VALIDATOR-83850aa0d5: Schema Validation Hot Path

**Priority:** HIGH

**Architectural Intent:**
Cache compiled JSON schema validators to avoid repeated compilation

**Implementation Reality:**
manifest_hash_validator.py does not use schema_validator_cache

**Impact:**
Schema validators recompiled on every validation request

**Evidence Files:
- `agentic_core/L2_execution/enforcement/manifest_hash_validator.py`

**Recommended Fix:**
Wrap validator compilation with schema_validator_cache.get_or_fetch()

---

### LAYER-UPWARD-IMPORT-0fb7489114: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/types/capability_token_types.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/types/capability_token_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-16c0accaf1: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/engines/validation_orchestrator.py imports higher-authority layer references: L0, L1

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/engines/validation_orchestrator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-2ea4135613: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-3c429f5da9: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/tools/unsafe_io_detector.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/tools/unsafe_io_detector.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-3eabf7816b: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/tools/write_gateway.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/tools/write_gateway.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-456822948e: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/capability_chokepoint.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/capability_chokepoint.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-4e6b3cb947: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/SovereignLLMGateway.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-72006d5e91: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/determinism.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/determinism.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-7d5b5d80f2: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/utils/tool_registry_util.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/utils/tool_registry_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-80b001c868: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/provider_binding_determinism.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/provider_binding_determinism.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-9a90bf15a6: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/durable_write_wrapper.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/durable_write_wrapper.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-ae1b70e6e4: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/config/unified_workflow_config.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/config/unified_workflow_config.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-bae9c8ca70: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/types/mcp_tool_types.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/types/mcp_tool_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-bf99a25319: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/tools/safe_subprocess.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/tools/safe_subprocess.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-c3a3fba755: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/healers/classification_compliance_healer.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/healers/classification_compliance_healer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-cb41b1920b: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/config/hybrid_retriever_config.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/config/hybrid_retriever_config.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-f10d541381: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/types/self_healing_trigger_types.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/types/self_healing_trigger_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-fb6423ef84: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py imports higher-authority layer references: L0, L1

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-ffaf401b39: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L2_execution/healers/hierarchy_compliance_healer.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L2_execution/healers/hierarchy_compliance_healer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### ELEVATOR-SHAFT-GAP-16c0accaf1: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L2_execution/engines/validation_orchestrator.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L2_execution/engines/validation_orchestrator.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-6d12ce38a2: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L2_execution/engines/execute_command_executor.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L2_execution/engines/execute_command_executor.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-82ece49bbe: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/tool_policy_enforcer.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/tool_policy_enforcer.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-984315233b: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L2_execution/tools/tool_chain_executor.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L2_execution/tools/tool_chain_executor.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d23b3738f0: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L2_execution/enforcement/boundary_verifier.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/boundary_verifier.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e9023cf94f: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L2_execution/engines/tool_intent_executor.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L2_execution/engines/tool_intent_executor.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### PROMPT-VALIDATOR-GAP-04f677f1e8: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
assembly_stage.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L0_routing/engines/assembly_stage.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-1f8d794d52: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
execution_orchestrator.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L0_routing/engines/execution_orchestrator.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-2fb9c2152f: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
prompt_artifact_cache.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L1_cognition/engines/prompt_artifact_cache.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-455d7b7dca: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
sandbox_envelope_types.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L2_execution/types/sandbox_envelope_types.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-53e1b1633f: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
execution_trace_types.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L2_execution/types/execution_trace_types.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-8a6344918d: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
qwen_vllm_inference.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L2_execution/healers/qwen_vllm_inference.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-94ab5260b1: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
execution_gateway.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L2_execution/engines/execution_gateway.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-d23b3738f0: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
boundary_verifier.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L2_execution/enforcement/boundary_verifier.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

### PROMPT-VALIDATOR-GAP-f88702ec50: Prompt Pre-flight Validation

**Priority:** LOW

**Architectural Intent:**
Prompt execution paths should support validator boundary snapshots before execution.

**Implementation Reality:**
class_info.py shows no boundary_snapshot evidence.

**Impact:**
Prompt healing and pre-flight diagnostics may be blind to assembly defects.

**Evidence Files:
- `agentic_core/L0_routing/scripts/class_info.py`

**Recommended Fix:**
Wire validator output to emit boundary_snapshot.json for prompt-package inspection.

---

## L3 Layer Gaps

### EMBEDDING-PLACEMENT-GAP-1d45a2de70: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/sub_atomic_engine_impl.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/sub_atomic_engine_impl.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-899023d1a7: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/deterministic_orchestrator.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/deterministic_orchestrator.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### LAYER-UPWARD-IMPORT-01ed8c61dc: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/orchestrator_engine.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/orchestrator_engine.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-0644131599: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/enforcement/safety_strategy.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/enforcement/safety_strategy.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-0eee0cad4a: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-11648d44b0: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py imports higher-authority layer references: L1, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-1d45a2de70: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/sub_atomic_engine_impl.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/sub_atomic_engine_impl.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-1dd25b1165: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/types/human_decision_artifact_types.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/types/human_decision_artifact_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-1fca771e91: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/types/telepathy_interface_types.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/types/telepathy_interface_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-2275b19be6: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/action_router.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/action_router.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-44184e5256: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-757ffa1d64: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/context_curator_engine.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/context_curator_engine.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-840868024e: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-8587851bdf: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/enforcement/knowledge_graph_healing_strategy.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/enforcement/knowledge_graph_healing_strategy.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-899023d1a7: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/deterministic_orchestrator.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/deterministic_orchestrator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-8fd0e1026e: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/enforcement/mission_runner.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/enforcement/mission_runner.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-9de18907d8: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/reasoning_intensity_enforcer.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/reasoning_intensity_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-a0075de1c3: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/decomposition_orchestrator.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/decomposition_orchestrator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-b2bbb81197: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/types/permission_scope_types.py imports higher-authority layer references: L1

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/types/permission_scope_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-ca0c22be28: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/types/execution_trace_types.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/types/execution_trace_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-d0203d20ce: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/AgentFactory.py imports higher-authority layer references: L1

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/AgentFactory.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-d3350a952a: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/types/workflow_loader_types.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/types/workflow_loader_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-e214372c70: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/StateManagementAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/StateManagementAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-e3af2097a9: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/autonomous_execution_engine.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/autonomous_execution_engine.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-e43415e3d5: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/types/cognitive_diff_types.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/types/cognitive_diff_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-ea2fec851b: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/types/route_decision_artifact_types.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/types/route_decision_artifact_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-efa1aaf8af: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/scripts/guardian_heal_orchestrator.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/scripts/guardian_heal_orchestrator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-f555fa9692: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/omni_context_engine.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/omni_context_engine.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### PATHD-PLAN-HASH-GAP-46b3989bd8: Path D Re-Clear Contract

**Priority:** HIGH

**Architectural Intent:**
Human MODIFY_DIFF flows must bind to original_plan_hash before L5 re-clear.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/handshake_state_machine.py shows Path D or HITL markers without clear original_plan_hash evidence.

**Impact:**
Human patch flows may lose plan provenance or bypass strict re-clear assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/handshake_state_machine.py`

**Recommended Fix:**
Require original_plan_hash and structured_patch_schema markers on all Path D decision artifacts.

---

### PATHD-PLAN-HASH-GAP-8fd0e1026e: Path D Re-Clear Contract

**Priority:** HIGH

**Architectural Intent:**
Human MODIFY_DIFF flows must bind to original_plan_hash before L5 re-clear.

**Implementation Reality:**
agentic_core/L3_orchestration/enforcement/mission_runner.py shows Path D or HITL markers without clear original_plan_hash evidence.

**Impact:**
Human patch flows may lose plan provenance or bypass strict re-clear assumptions.

**Evidence Files:
- `agentic_core/L3_orchestration/enforcement/mission_runner.py`

**Recommended Fix:**
Require original_plan_hash and structured_patch_schema markers on all Path D decision artifacts.

---

### PATHD-PLAN-HASH-GAP-d5d46f74ab: Path D Re-Clear Contract

**Priority:** HIGH

**Architectural Intent:**
Human MODIFY_DIFF flows must bind to original_plan_hash before L5 re-clear.

**Implementation Reality:**
agentic_core/mixins/hitl_mixin.py shows Path D or HITL markers without clear original_plan_hash evidence.

**Impact:**
Human patch flows may lose plan provenance or bypass strict re-clear assumptions.

**Evidence Files:
- `agentic_core/mixins/hitl_mixin.py`

**Recommended Fix:**
Require original_plan_hash and structured_patch_schema markers on all Path D decision artifacts.

---

### L3-GAP-001: Orchestration Plan Construction

**Priority:** MEDIUM

**Architectural Intent:**
Cache orchestration plans to avoid repeated planning for identical requests

**Implementation Reality:**
orchestrator_engine.py does not use orchestration_plan_cache

**Impact:**
Orchestration plans recomputed on every request

**Evidence Files:
- `agentic_core/L3_orchestration/engines/orchestrator_engine.py`

**Recommended Fix:**
Wrap plan construction with orchestration_plan_cache.get_or_fetch()

---

### NON-L2-MUTATION-RISK-01ed8c61dc: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/orchestrator_engine.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/orchestrator_engine.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-0eee0cad4a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-11648d44b0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-150484acf4: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/recursive_orchestrator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/recursive_orchestrator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-18dc77283b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/convergence_engine.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/convergence_engine.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-19ca07f3ff: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/types/approval_contract_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/types/approval_contract_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-1fca771e91: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/types/telepathy_interface_types.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/types/telepathy_interface_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-2d92d7aaa3: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/DagEngineAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/DagEngineAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-39568ca4f5: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/sovereign_mcp_router.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/sovereign_mcp_router.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-43b173a34c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/dag_manager.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/dag_manager.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-44184e5256: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py appears to perform write-like operations outside the expected execution choke point: _execute_commit_stage, append, write_blob

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-46b3989bd8: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/handshake_state_machine.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/handshake_state_machine.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4ce17bc985: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4e3753ea2c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/types/forward_rolling_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/types/forward_rolling_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-54cad16605: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/sovereign_mcp_marketplace.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/sovereign_mcp_marketplace.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-56c085874a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/orchestration_plan_cache.py appears to perform write-like operations outside the expected execution choke point: delete

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/orchestration_plan_cache.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5d6d23170e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/agent_gym_engine.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/agent_gym_engine.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-706369956a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py appears to perform write-like operations outside the expected execution choke point: delete

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-757ffa1d64: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/context_curator_engine.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/context_curator_engine.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-7a38f2cc80: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-7fd19b13e1: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/utils/log_orchestration_metrics_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/utils/log_orchestration_metrics_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-840868024e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py appears to perform write-like operations outside the expected execution choke point: append, append_result

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-84b62a3c6a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/ptc/tool_call_store.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/ptc/tool_call_store.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8587851bdf: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/enforcement/knowledge_graph_healing_strategy.py appears to perform write-like operations outside the expected execution choke point: _persist_kg_data, append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/enforcement/knowledge_graph_healing_strategy.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8813c2fada: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/CoverageAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/CoverageAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8fd0e1026e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/enforcement/mission_runner.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/enforcement/mission_runner.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-9c2bf92cb9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/arbitration/arbitrator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/arbitration/arbitrator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-9de18907d8: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/reasoning_intensity_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/reasoning_intensity_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-9f5a1cd008: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/DomainPlannerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a0075de1c3: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/decomposition_orchestrator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/decomposition_orchestrator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a16cf9de41: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/arbitration/run_advisors.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/arbitration/run_advisors.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a3a5fc23d0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/proactive_fission_scanner.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/proactive_fission_scanner.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ab291e78b5: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-af12babd07: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/replay/deterministic_replay.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/replay/deterministic_replay.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b60b518bb3: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/ptc/builtin_tools.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/ptc/builtin_tools.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c3ccc5161f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/types/recursive_orchestration_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/types/recursive_orchestration_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c844d8c457: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/types/injection_result_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/types/injection_result_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d0203d20ce: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/AgentFactory.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/AgentFactory.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d4b2a72cea: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/reflex_layer_pattern.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/reflex_layer_pattern.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e214372c70: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/StateManagementAgent.py appears to perform write-like operations outside the expected execution choke point: _write_manifest_raw, append, delete_state, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/StateManagementAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e3af2097a9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/autonomous_execution_engine.py appears to perform write-like operations outside the expected execution choke point: write_json_atomic

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/autonomous_execution_engine.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e43415e3d5: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/types/cognitive_diff_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/types/cognitive_diff_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-efa1aaf8af: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/scripts/guardian_heal_orchestrator.py appears to perform write-like operations outside the expected execution choke point: assert_no_persistent_write, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/scripts/guardian_heal_orchestrator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f29aa8a6a3: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/rl_coordinator_orchestrator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/rl_coordinator_orchestrator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f4fd22d1db: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/types/context_pruning_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/types/context_pruning_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f555fa9692: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/engines/omni_context_engine.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/engines/omni_context_engine.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f8c1f043c0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/reasoning/UnifiedAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/reasoning/UnifiedAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ffa95c9d39: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L3_orchestration/types/recursion_monitor_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L3_orchestration/types/recursion_monitor_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

## L4 Layer Gaps

### LAYER-UPWARD-IMPORT-1e406ff901: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L4_state/types/cycle_types.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L4_state/types/cycle_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-21bf857ac4: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L4_state/memory/runtime_state_guard.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L4_state/memory/runtime_state_guard.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-378d1036b5: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L4_state/memory/semantic_cache_manager.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L4_state/memory/semantic_cache_manager.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-46bdccdc1c: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L4_state/utils/context_util.py imports higher-authority layer references: L3

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L4_state/utils/context_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-4a803b4f70: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L4_state/reasoning/CheckpointManager.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L4_state/reasoning/CheckpointManager.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-a429804a95: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L4_state/utils/experience_buffer_util.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L4_state/utils/experience_buffer_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-c994d200d7: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L4_state/memory/blob_storage_provider.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L4_state/memory/blob_storage_provider.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-f1773f7a9c: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L4_state/utils/get_existing_file_hashes_util.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L4_state/utils/get_existing_file_hashes_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

## L5 Layer Gaps

### EMBEDDING-PLACEMENT-GAP-2d3498ab32: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/sovereign_kernel.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/sovereign_kernel.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-3e59c1be19: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/classification.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/classification.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-4f9a2de5bd: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/vector_healing_strategy.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/vector_healing_strategy.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-54da3d2303: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L5_safety/utils/verify_no_mock_data_util.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L5_safety/utils/verify_no_mock_data_util.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-61de1d0ac5: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/system_invariant_scanner.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/system_invariant_scanner.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-8cf30d3fa8: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L5_safety/utils/verify_semantic_meta_learning_util.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L5_safety/utils/verify_semantic_meta_learning_util.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-c69ffb0736: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L5_safety/validators/magic_validator.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L5_safety/validators/magic_validator.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-da5b366a8e: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/semantics.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/semantics.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-f2a4cba8e5: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/_constants.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/_constants.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-f5dba29c5a: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/AdapterBase.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/AdapterBase.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### GOVERNANCE-STAMP-GAP-0005b1f02d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/campaign_balance_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/campaign_balance_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-002d690c65: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-010c4201cf: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/gravity_visitor_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/gravity_visitor_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-012d8d732c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/hop_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/hop_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-01376cb830: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/data_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/data_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-01f6071537: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/__init__.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/__init__.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-031e477170: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/runners/agent_roster_runner.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/runners/agent_roster_runner.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-03211cab41: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-03454b8c76: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/governance/lazy_seam_scanner.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/governance/lazy_seam_scanner.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-05022f1381: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/safety_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/safety_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-066956c87c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DependencyPruningAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DependencyPruningAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-06d040686f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/rag_validation_result_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/rag_validation_result_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-07864021fd: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/specificity_prose_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/specificity_prose_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-0843c767d0: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/write_gateway_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/write_gateway_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-088b0c2b76: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-0da47233d2: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/heal_llm_seam_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/heal_llm_seam_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-0fd1d4135e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/__init__.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/__init__.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-100249a885: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/learning_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/learning_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-100a34d34a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/contract_stage_config.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/contract_stage_config.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-101bfef44b: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/silent_swallower_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/silent_swallower_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-115bee2b64: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/heal_policy_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/heal_policy_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-122a93ea1f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/activation_gate.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/activation_gate.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-12f340c751: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/location_utils_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/location_utils_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-1459737e70: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructureHealerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructureHealerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-14bb9ae04e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/mock_context_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/mock_context_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-152ac16342: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/import_surgeon_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/import_surgeon_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-1552e4b132: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/structural_namespace_fence_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/structural_namespace_fence_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-15c68411d7: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/RedSentinelAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/RedSentinelAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-167280a192: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/healing_orchestration_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/healing_orchestration_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-167a4b2b29: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/conf_calib_gate.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/conf_calib_gate.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-174a2d5cd2: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/guard_ddd_alignment_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/guard_ddd_alignment_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-175823f40e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GravityValidatorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GravityValidatorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-1a95ccba3a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/error_recovery_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/error_recovery_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-1b6318279d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/safety_profile_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/safety_profile_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-1bb7e862c0: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/__init__.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/__init__.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-1c7b2f1c60: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/runners/arch_governor_runner.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/runners/arch_governor_runner.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-1cd0e7824b: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/validate_path_ssot_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/validate_path_ssot_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-1d89c8793b: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/fix_inherited_invocation_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/fix_inherited_invocation_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-1ff343ebf6: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-2085319793: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/sovereign_base_model_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/sovereign_base_model_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-2286c89936: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/blueprint_compiler.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/blueprint_compiler.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-24cace2ecf: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/artifacts.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/artifacts.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-26148d9270: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ReportLocationAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ReportLocationAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-27e2e6cf1c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/tier_lattice_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/tier_lattice_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-280b7b55ca: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-2854189bc4: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/surgical_context_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/surgical_context_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-293b2276a5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/global_mutation_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/global_mutation_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-2a08d2438a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/FileClassificationValidatorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/FileClassificationValidatorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-2a91b8d8db: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/set_complexity_health_100_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/set_complexity_health_100_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-2d3498ab32: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/sovereign_kernel.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/sovereign_kernel.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-2d3caa6791: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeValidatorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeValidatorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-2fb32c99a5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/shift_report_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/shift_report_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-31ba914627: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/LocationValidatorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/LocationValidatorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-32543f49fb: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/registry_verification_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/registry_verification_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-34c9f8c2b9: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-34d6b77ee6: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/check_output_quality_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/check_output_quality_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-34ecc530d2: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GovernanceAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GovernanceAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-34ef15cf3b: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/location_path_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/location_path_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-3531396fb6: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-36e31d1cc4: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/resource_management_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/resource_management_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-370e339104: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/structure_drift_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/structure_drift_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-37a744605f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/ConstitutionalOverseer_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/ConstitutionalOverseer_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-394d552207: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/governance/lazy_seam_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/governance/lazy_seam_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-39505f8089: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/rule_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/rule_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-3a48df43cb: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ArchitectureGovernorValidatorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ArchitectureGovernorValidatorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-3b58f4cdc8: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-3bd433e1a3: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/anti_pattern_scanner_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/anti_pattern_scanner_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-3d83bb505e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/security/credential_guard.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/security/credential_guard.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-3da342afa1: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/constitutional_governance_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/constitutional_governance_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-3e59c1be19: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/classification.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/classification.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-3ff0f1f724: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/ssot_folder_check_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/ssot_folder_check_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-40447e186e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/FilesystemSSOTValidatorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/FilesystemSSOTValidatorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4108bb2638: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/FilesystemSSOTHealerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/FilesystemSSOTHealerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-41430c2687: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-419e1404f6: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/context_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/context_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-41b8f98ac9: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/validation_utils_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/validation_utils_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-432107c0ce: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/circular_import_fixer_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/circular_import_fixer_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4523ee8759: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/enforce_length_limits_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/enforce_length_limits_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4554767bcc: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/budget_profile_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/budget_profile_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-457f25a315: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/intervention_server_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/intervention_server_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-460980d8b0: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/healing_invocation_audit_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/healing_invocation_audit_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-46a4c4ffa0: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/cache_invalidation_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/cache_invalidation_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-46ca4ab236: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/__init__.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/__init__.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-47c68d3d10: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4830905231: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/input_config.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/input_config.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-486513e756: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4c1ada5674: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/read_file_args_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/read_file_args_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4c4e81951e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/security/side_effect_guard.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/security/side_effect_guard.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4c5e1f1065: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4c62648f63: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/ssot_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/ssot_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4e0bb57052: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/validate_generated_content_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/validate_generated_content_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4ea2fb85a9: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-4f9a2de5bd: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/vector_healing_strategy.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/vector_healing_strategy.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-543cd1ed9d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-54da3d2303: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/verify_no_mock_data_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/verify_no_mock_data_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-55d9d003c9: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/pytest_config_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/pytest_config_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-56578ede3b: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-5683356cbf: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/governance_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/governance_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-575c3b00d3: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/content_quality_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/content_quality_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-578a454212: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/BenchmarkingAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/BenchmarkingAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-57b1e023f0: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/decorators_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/decorators_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-57f7d0765b: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/meta_learning_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/meta_learning_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-58072f8ba1: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-588a971b81: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/namespace_medic_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/namespace_medic_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-5947b728a7: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/derived.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/derived.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-5b747de237: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-5c399eaa20: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/lead_quality_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/lead_quality_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-5d3101e616: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/import_boundary_check_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/import_boundary_check_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-5dfa5a94f5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-5ec6ad618f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GravityLeakHealerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GravityLeakHealerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-60cb2a81f5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/core_contracts_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/core_contracts_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6140717652: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-61de1d0ac5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/system_invariant_scanner.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/system_invariant_scanner.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-671e6db19e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/code_tool_runner_core_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/code_tool_runner_core_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6aadedffdf: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/core_kernel/__init__.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/core_kernel/__init__.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6adc8eefbb: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/_verify.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/_verify.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6ba200ea5a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/re_clear_loop_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/re_clear_loop_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6c30929c4f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/airlock_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/airlock_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6c7a614654: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/simulation_schemas_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/simulation_schemas_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6cc0142ac2: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/three_tier_compliance_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/three_tier_compliance_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6dbf25f54f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/verification_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/verification_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6e9c8037d7: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/context_session_manager_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/context_session_manager_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6eee9279e9: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-6fefc54056: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/process_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/process_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-72075c4e27: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-741d7717fd: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/airlock_trimmer_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/airlock_trimmer_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-743606c902: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/force_app_depth_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/force_app_depth_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-75752118f3: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/agentthoughtprocess_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/agentthoughtprocess_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-759a478e74: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/__init__.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/__init__.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-75a07ad0b7: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-771561facb: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-77e043cc35: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/golden_state_test_case_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/golden_state_test_case_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-785c5db424: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/RedTeamAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/RedTeamAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-7898e1dd3a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/verification_gate.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/verification_gate.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-78c7e27850: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/security/secure_secrets.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/security/secure_secrets.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-78e381ea8c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/ssot_import_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/ssot_import_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-7b2fae4218: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/governance.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/governance.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-7bf7f110de: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/RegressionOracleAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/RegressionOracleAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-7cb050f84f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/location_constants_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/location_constants_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-7d036eb2d7: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/logs_guard.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/logs_guard.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-7f7666319d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/LocationAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/LocationAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-810d22ce4e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/cognitive_batch_processor_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/cognitive_batch_processor_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8246559fe0: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/report_location_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/report_location_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-82cf5d20e5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/hierarchy_validator_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/hierarchy_validator_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-82eb18436b: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-83b7627e32: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ResourceManagerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ResourceManagerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-841e8be0cb: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/verb_canonicalizer_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/verb_canonicalizer_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-846f2a202f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/deliverability_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/deliverability_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-849d1fbf84: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/territories.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/territories.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8769dbf17c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/agent_audit_result_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/agent_audit_result_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-890d336ea6: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-89427eca30: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/dependencygraph_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/dependencygraph_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-89ce07df10: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8a113e7e97: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8b7f6e8070: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/sovereign_policy_registry_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/sovereign_policy_registry_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8ba2ec9c91: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/secure_error_handler_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/secure_error_handler_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8c0726bf4a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/security_validation_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/security_validation_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8c4ebe8af3: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/audit_healing_strategy.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/audit_healing_strategy.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8c5727b36d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8cc60b9d22: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/HierarchyValidatorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/HierarchyValidatorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8cf30d3fa8: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/verify_semantic_meta_learning_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/verify_semantic_meta_learning_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8dc38fb9b0: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/cst_transformers_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/cst_transformers_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8dc512cf0c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/ddd_alignment_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/ddd_alignment_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8e5e8f462f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/TestGeneratorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8e62e9ebc1: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-8ea31c62f5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-90581de3b0: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/DomainPlannerAdapter.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/DomainPlannerAdapter.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-9266521c0e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/surgical_context_types_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/surgical_context_types_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-92aafe2a7d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/phase_acceptance_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/phase_acceptance_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-92bb885714: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-937e387e98: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/HierarchyHealerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/HierarchyHealerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-94ba15b33e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-95c61f3b74: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/unified_cst_healer_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/unified_cst_healer_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-972edda74d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/human_decision_artifact_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/human_decision_artifact_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-975cdc6d03: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/register_all_validators_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/register_all_validators_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-977830f8ee: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/git_kraken_healing_strategy.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/git_kraken_healing_strategy.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-97bd6c232f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/cache_guard.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/cache_guard.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-98e7774a0a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/NeuralAutoImmuneAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/NeuralAutoImmuneAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-9a3bba984a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/__init__.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/__init__.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-9a4de56e3d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/_simulate_verify.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/_simulate_verify.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-9b481e6d95: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/fast_dashboard_e2_e_pipeline_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/fast_dashboard_e2_e_pipeline_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-9cca08ab2d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/input_membrane_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/input_membrane_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-9dcf7186b7: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/governance/lazy_seam_classifier.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/governance/lazy_seam_classifier.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-9e5b60bda3: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/sovereign_lock_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/sovereign_lock_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-9f0b82385b: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CredentialScannerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CredentialScannerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a03e650027: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/extract_pattern_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/extract_pattern_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a0fa297046: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/NamingAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/NamingAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a1ee228e3c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/migration_helper_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/migration_helper_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a314249cea: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/cst_transformers_types_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/cst_transformers_types_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a3fe546112: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/RootHygieneAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/RootHygieneAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a47dfb35af: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/mission_preflight_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/mission_preflight_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a5c7121f05: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/input_validation_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/input_validation_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a62e273b05: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GitHygieneAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GitHygieneAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a6ba2e78a5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/gravity_leak_config.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/gravity_leak_config.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a6f93d0bd8: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/SurgicalHealingAdapter.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/SurgicalHealingAdapter.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a72f687837: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a770b2fa3f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a91c5e225c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeFormatterAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeFormatterAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-a9d3bf2cfe: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/system_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/system_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-aa60687394: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ac02a8f0de: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ac1aed270a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/guard_observability_footprint_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/guard_observability_footprint_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ad373177f0: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/hypothesis_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/hypothesis_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ad79cc4727: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/consensus_verdict_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/consensus_verdict_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ad8809de96: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/runners/hierarchy_runner.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/runners/hierarchy_runner.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-b123ea8ce3: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/core_kernel/classification_kernel.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/core_kernel/classification_kernel.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-b1fe2a0e05: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/security/injection_regression_gate.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/security/injection_regression_gate.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-b26524324a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/tiered_batch_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/tiered_batch_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-b3964a12ee: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/artifact_emission_prohibition_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/artifact_emission_prohibition_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-b3c4e54a8e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GospelSyncAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GospelSyncAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-b3f9cf93e3: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-b69e8a5b32: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SystemArchitectAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-b705a8547e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/achv_bullet_synthesizer_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/achv_bullet_synthesizer_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-b9f3899933: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/ssot.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/ssot.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ba423f1972: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ba8fccfa2a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/d0_injection_engine_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/d0_injection_engine_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-bb15a521e0: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/integrity_validation_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/integrity_validation_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-bb3ecc2507: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SecurityManagerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SecurityManagerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-bdeeab6ae2: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/fca_safety_gates_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/fca_safety_gates_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-befbff71b2: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/health_status_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/health_status_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-bf873b7cb5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/HealingStrategy.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/HealingStrategy.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-bfda9ba571: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/security/__init__.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/security/__init__.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c15f7051c6: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c18f8d18da: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/sovereign_fence_validator_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/sovereign_fence_validator_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c1bb21b878: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/runners/code_validator_runner.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/runners/code_validator_runner.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c3a5089e48: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/agent_categorizer_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/agent_categorizer_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c5185f4f08: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/subprocess_security_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/subprocess_security_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c5e52caa23: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/HierarchyAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/HierarchyAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c673cab117: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/canonical_truth_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/canonical_truth_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c69ffb0736: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/magic_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/magic_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c6c9eba57e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/pii_vault_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/pii_vault_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c6cf8fef17: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c6e716e1b0: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c708c94394: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/AutonomousThreatEvolutionAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/AutonomousThreatEvolutionAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c79379af97: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c95c426855: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/determinism_serialization_check.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/determinism_serialization_check.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c968d1d87d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/LocationHealerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/LocationHealerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-c97b170dbe: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/FileClassificationHealerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/FileClassificationHealerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ca29f45979: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/ats_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/ats_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-cbd82269fc: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CostGovernorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CostGovernorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-cc92afe1d3: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/pre_deploy_check_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/pre_deploy_check_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ce526a9d82: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/sealed_interface_check_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/sealed_interface_check_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ce5670916f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/rag_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/rag_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ce5fd488d1: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/circuit_breaker_gate.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/circuit_breaker_gate.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ce7dcc0b3c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-cf48bcb32d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/security_controls_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/security_controls_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-cfefbe5157: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/reasoning_pattern_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/reasoning_pattern_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d0354eb8ca: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/canary_token_defense_strategy.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/canary_token_defense_strategy.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d15dde3f21: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/priority_violation_guard.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/priority_violation_guard.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d1cc373b95: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/gravity_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/gravity_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d2cd38243d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/type_erasure_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/type_erasure_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d34e7aefa9: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/runners/orchestrator_runner.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/runners/orchestrator_runner.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d63a8b5379: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/BootstrapAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/BootstrapAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d6702b5e27: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/detection_signal_config.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/detection_signal_config.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d693cc7fb7: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeHealerAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeHealerAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d71b8fb431: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DynamicSealAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DynamicSealAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d79fbeb702: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/runners/__init__.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/runners/__init__.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d7f7d47925: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/runtime_mutation_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/runtime_mutation_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d9a2ff54fa: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/artifacts_guard.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/artifacts_guard.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-d9a88f846c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/heal_model_map_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/heal_model_map_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-da5b366a8e: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/semantics.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/semantics.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-daaec18f9b: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-dcbfc1fcaa: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-dd62b38a9d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/intelligence_query_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/intelligence_query_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-de4adefad4: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/ssot_relocator_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/ssot_relocator_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-df0c99a6fa: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-dfb227f021: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/dependency_graph_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/dependency_graph_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e060b97182: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e1c11fed85: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e4e7cefcc6: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/TypeMechanicAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/TypeMechanicAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e574db9e7d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/mission_utils_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/mission_utils_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e6c386b9e7: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/compliance_audit_manager_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/compliance_audit_manager_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e6ef310943: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/agent_info_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/agent_info_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e75da4e059: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/guardian_decision.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/guardian_decision.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e86955f776: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e8a672e6aa: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/safety_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/safety_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e8f09d3559: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e973cfa986: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/safety_layer_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/safety_layer_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-e9905a4443: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-eb6f05ca17: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeDetectorAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeDetectorAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-eb8565d93c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/base_detector_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/base_detector_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ec568bb5fc: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/HumanReviewAdapter.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/HumanReviewAdapter.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ee0d857a4f: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/ptc_invariants.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/ptc_invariants.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ee50e64c26: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/error_recovery_strategy.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/error_recovery_strategy.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ef1689619d: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/InspectorExecutor.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/InspectorExecutor.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-ef43566f80: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/validators/path_fragility_validator.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/validators/path_fragility_validator.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-efb64fa0c2: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint_config.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint_config.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f0c3f673b7: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/validation_result_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/validation_result_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f10c1211cc: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/docs_structure_guard.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/docs_structure_guard.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f179966722: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/module_collision_guardrail.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/module_collision_guardrail.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f2a4cba8e5: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/_constants.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/_constants.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f33b93e449: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/git_health_sensor_enforcer.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/git_health_sensor_enforcer.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f42cab4581: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/powershell_ban.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/powershell_ban.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f4dc44a387: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f5dba29c5a: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/AdapterBase.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/AdapterBase.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f67cb4a296: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/types/file_health_score_types.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/types/file_health_score_types.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f6c5d0041c: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/validate_dashboard_data_sourcing_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/validate_dashboard_data_sourcing_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-f86b65bcf3: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DocumentationAgent.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DocumentationAgent.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-fb2ccbdeb2: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/capability_extractor_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/capability_extractor_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### GOVERNANCE-STAMP-GAP-fff9d78be6: Governance Stamp and Airlock Contract

**Priority:** HIGH

**Architectural Intent:**
Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.

**Implementation Reality:**
agentic_core/L5_safety/utils/forge_fortress_util.py appears to participate in the airlock but no governance-stamp markers were detected.

**Impact:**
Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.

**Evidence Files:
- `agentic_core/L5_safety/utils/forge_fortress_util.py`

**Recommended Fix:**
Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.

---

### LAYER-UPWARD-IMPORT-002d690c65: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-03211cab41: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-03454b8c76: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/governance/lazy_seam_scanner.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/governance/lazy_seam_scanner.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-05022f1381: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/types/safety_types.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/types/safety_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-066956c87c: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DependencyPruningAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DependencyPruningAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-088b0c2b76: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-0da47233d2: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/types/heal_llm_seam_types.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/types/heal_llm_seam_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-100249a885: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/types/learning_types.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/types/learning_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-1459737e70: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructureHealerAgent.py imports higher-authority layer references: L0, L2, L3

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructureHealerAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-14bb9ae04e: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/mock_context_enforcer.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/mock_context_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-152ac16342: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/import_surgeon_enforcer.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/import_surgeon_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-15c68411d7: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/RedSentinelAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/RedSentinelAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-174a2d5cd2: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/guard_ddd_alignment_util.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/guard_ddd_alignment_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-1d89c8793b: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/fix_inherited_invocation_util.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/fix_inherited_invocation_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-1ff343ebf6: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py imports higher-authority layer references: L4

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-2286c89936: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/config/blueprint_compiler.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/config/blueprint_compiler.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-26148d9270: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ReportLocationAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ReportLocationAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-280b7b55ca: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py imports higher-authority layer references: L2, L3, L4

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-2a91b8d8db: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/set_complexity_health_100_util.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/set_complexity_health_100_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-2d3caa6791: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeValidatorAgent.py imports higher-authority layer references: L3

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeValidatorAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-31ba914627: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/LocationValidatorAgent.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/LocationValidatorAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-34c9f8c2b9: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-34ecc530d2: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GovernanceAgent.py imports higher-authority layer references: L0, L2, L4

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GovernanceAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-3531396fb6: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-370e339104: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/validators/structure_drift_validator.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/validators/structure_drift_validator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-394d552207: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/governance/lazy_seam_enforcer.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/governance/lazy_seam_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-3bd433e1a3: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/validators/anti_pattern_scanner_validator.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/validators/anti_pattern_scanner_validator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-3d83bb505e: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/security/credential_guard.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/security/credential_guard.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-41430c2687: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-432107c0ce: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/circular_import_fixer_enforcer.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/circular_import_fixer_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-460980d8b0: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/healing_invocation_audit_enforcer.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/healing_invocation_audit_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-47c68d3d10: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-486513e756: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-4c5e1f1065: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-4c62648f63: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/ssot_guardrail.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/ssot_guardrail.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-4ea2fb85a9: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py imports higher-authority layer references: L0, L1, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-543cd1ed9d: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-54da3d2303: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/verify_no_mock_data_util.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/verify_no_mock_data_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-55d9d003c9: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/pytest_config_guardrail.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/pytest_config_guardrail.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-56578ede3b: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-578a454212: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/BenchmarkingAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/BenchmarkingAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-58072f8ba1: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py imports higher-authority layer references: L2, L4

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-588a971b81: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/namespace_medic_enforcer.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/namespace_medic_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-5b747de237: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py imports higher-authority layer references: L4

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-5dfa5a94f5: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-6adc8eefbb: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/_verify.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/_verify.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-6cc0142ac2: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/three_tier_compliance_enforcer.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/three_tier_compliance_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-6eee9279e9: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-72075c4e27: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py imports higher-authority layer references: L0, L2, L4

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-741d7717fd: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/airlock_trimmer_enforcer.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/airlock_trimmer_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-743606c902: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/force_app_depth_util.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/force_app_depth_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-78e381ea8c: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/ssot_import_enforcer.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/ssot_import_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-7bf7f110de: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/RegressionOracleAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/RegressionOracleAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-7d036eb2d7: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/logs_guard.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/logs_guard.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-810d22ce4e: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/cognitive_batch_processor_util.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/cognitive_batch_processor_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-8246559fe0: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/validators/report_location_validator.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/validators/report_location_validator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-89427eca30: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/validators/dependencygraph_validator.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/validators/dependencygraph_validator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-8a113e7e97: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-8c5727b36d: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-8e5e8f462f: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/TestGeneratorAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-8ea31c62f5: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-92bb885714: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-94ba15b33e: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-95c61f3b74: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/unified_cst_healer_util.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/unified_cst_healer_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-97bd6c232f: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/cache_guard.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/cache_guard.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-9a4de56e3d: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/_simulate_verify.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/_simulate_verify.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-9b481e6d95: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/fast_dashboard_e2_e_pipeline_enforcer.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/fast_dashboard_e2_e_pipeline_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-9dcf7186b7: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/governance/lazy_seam_classifier.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/governance/lazy_seam_classifier.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-9f0b82385b: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CredentialScannerAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CredentialScannerAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-a03e650027: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/extract_pattern_util.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/extract_pattern_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-a3fe546112: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/RootHygieneAgent.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/RootHygieneAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-a6ba2e78a5: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/config/gravity_leak_config.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/config/gravity_leak_config.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-a770b2fa3f: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py imports higher-authority layer references: L3

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-a9d3bf2cfe: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/system_enforcer.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/system_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-aa60687394: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-ac02a8f0de: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-b26524324a: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/tiered_batch_util.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/tiered_batch_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-b3c4e54a8e: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GospelSyncAgent.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GospelSyncAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-b69e8a5b32: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SystemArchitectAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-bf873b7cb5: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/HealingStrategy.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/HealingStrategy.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-c15f7051c6: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-c5e52caa23: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/HierarchyAgent.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/HierarchyAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-c6cf8fef17: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py imports higher-authority layer references: L4

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-c6e716e1b0: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-c79379af97: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-c968d1d87d: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/LocationHealerAgent.py imports higher-authority layer references: L0, L2, L3, L4

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/LocationHealerAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-cc92afe1d3: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/pre_deploy_check_util.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/pre_deploy_check_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-ce526a9d82: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/sealed_interface_check_enforcer.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/sealed_interface_check_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-ce7dcc0b3c: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py imports higher-authority layer references: L4

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-d1cc373b95: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/validators/gravity_validator.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/validators/gravity_validator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-d34e7aefa9: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/runners/orchestrator_runner.py imports higher-authority layer references: L3

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/runners/orchestrator_runner.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-d693cc7fb7: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeHealerAgent.py imports higher-authority layer references: L0, L2, L3

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeHealerAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-d71b8fb431: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DynamicSealAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DynamicSealAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-d9a2ff54fa: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/artifacts_guard.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/artifacts_guard.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-dcbfc1fcaa: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-de4adefad4: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/types/ssot_relocator_types.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/types/ssot_relocator_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-df0c99a6fa: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-e1c11fed85: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-e4e7cefcc6: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/TypeMechanicAgent.py imports higher-authority layer references: L3

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/TypeMechanicAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-e6ef310943: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/agent_info_enforcer.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/agent_info_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-e86955f776: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-e8f09d3559: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py imports higher-authority layer references: L4

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-e973cfa986: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/safety_layer_enforcer.py imports higher-authority layer references: L1

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/safety_layer_enforcer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-ee0d857a4f: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/ptc_invariants.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/ptc_invariants.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-f0c3f673b7: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/types/validation_result_types.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/types/validation_result_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-f10c1211cc: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/docs_structure_guard.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/docs_structure_guard.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-f4dc44a387: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-f6c5d0041c: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/validate_dashboard_data_sourcing_util.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/validate_dashboard_data_sourcing_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-f86b65bcf3: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DocumentationAgent.py imports higher-authority layer references: L3

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DocumentationAgent.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-fff9d78be6: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L5_safety/utils/forge_fortress_util.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L5_safety/utils/forge_fortress_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### ELEVATOR-SHAFT-GAP-115bee2b64: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L5_safety/types/heal_policy_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L5_safety/types/heal_policy_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-167280a192: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L5_safety/types/healing_orchestration_types.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L5_safety/types/healing_orchestration_types.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-1ff343ebf6: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-3b58f4cdc8: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-5d3101e616: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/import_boundary_check_enforcer.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/import_boundary_check_enforcer.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-771561facb: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-8b7f6e8070: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/sovereign_policy_registry_enforcer.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/sovereign_policy_registry_enforcer.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-c79379af97: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-d34e7aefa9: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L5_safety/runners/orchestrator_runner.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L5_safety/runners/orchestrator_runner.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-e8f09d3559: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### ELEVATOR-SHAFT-GAP-ef1689619d: JIT State Synchronization

**Priority:** MEDIUM

**Architectural Intent:**
Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/InspectorExecutor.py appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.

**Impact:**
The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/InspectorExecutor.py`

**Recommended Fix:**
Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.

---

### L5-GAP-POLICY-8b7f6e8070: Safety Policy Enforcement

**Priority:** MEDIUM

**Architectural Intent:**
Cache immutable safety policies to avoid repeated L4 lookups

**Implementation Reality:**
sovereign_policy_registry_enforcer.py does not use policy_registry_cache

**Impact:**
Safety policies fetched from L4 on every enforcement check

**Evidence Files:
- `agentic_core/L5_safety/enforcement/sovereign_policy_registry_enforcer.py`

**Recommended Fix:**
Wrap policy retrieval with policy_registry_cache.get_or_fetch()

---

### NON-L2-MUTATION-RISK-0005b1f02d: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/campaign_balance_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/campaign_balance_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-002d690c65: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-010c4201cf: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/gravity_visitor_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/gravity_visitor_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-012d8d732c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/hop_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/hop_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-01376cb830: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/data_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/data_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-031e477170: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/runners/agent_roster_runner.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/runners/agent_roster_runner.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-03211cab41: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-03454b8c76: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/governance/lazy_seam_scanner.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/governance/lazy_seam_scanner.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-05022f1381: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/safety_types.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/safety_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-066956c87c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DependencyPruningAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DependencyPruningAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-07864021fd: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/specificity_prose_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/specificity_prose_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-0843c767d0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/write_gateway_enforcer.py appears to perform write-like operations outside the expected execution choke point: WriteGatewayVisitor, append, scan_file_for_writes

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/write_gateway_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-088b0c2b76: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-0da47233d2: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/heal_llm_seam_types.py appears to perform write-like operations outside the expected execution choke point: append, write_bytes

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/heal_llm_seam_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-100249a885: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/learning_types.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/learning_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-100a34d34a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/config/contract_stage_config.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/config/contract_stage_config.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-101bfef44b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/silent_swallower_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/silent_swallower_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-122a93ea1f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/activation_gate.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/activation_gate.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-12f340c751: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/location_utils_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/location_utils_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-1459737e70: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructureHealerAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructureHealerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-14bb9ae04e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/mock_context_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/mock_context_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-152ac16342: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/import_surgeon_enforcer.py appears to perform write-like operations outside the expected execution choke point: append, open_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/import_surgeon_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-15c68411d7: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/RedSentinelAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/RedSentinelAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-167280a192: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/healing_orchestration_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/healing_orchestration_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-167a4b2b29: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/conf_calib_gate.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/conf_calib_gate.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-174a2d5cd2: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/guard_ddd_alignment_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/guard_ddd_alignment_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-1a95ccba3a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/error_recovery_guardrail.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/error_recovery_guardrail.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-1cd0e7824b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/validate_path_ssot_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/validate_path_ssot_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-1d89c8793b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/fix_inherited_invocation_util.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/fix_inherited_invocation_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-2286c89936: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/config/blueprint_compiler.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/config/blueprint_compiler.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-26148d9270: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ReportLocationAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ReportLocationAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-280b7b55ca: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py appears to perform write-like operations outside the expected execution choke point: append, force_rename_class, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-2854189bc4: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/surgical_context_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/surgical_context_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-293b2276a5: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/global_mutation_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/global_mutation_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-2a08d2438a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/FileClassificationValidatorAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/FileClassificationValidatorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-2a91b8d8db: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/set_complexity_health_100_util.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/set_complexity_health_100_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-2d3caa6791: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeValidatorAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeValidatorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-31ba914627: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/LocationValidatorAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/LocationValidatorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-32543f49fb: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/registry_verification_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/registry_verification_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-34c9f8c2b9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py appears to perform write-like operations outside the expected execution choke point: append, open_write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-34ecc530d2: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GovernanceAgent.py appears to perform write-like operations outside the expected execution choke point: append, open_write, safe_delete

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GovernanceAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-3531396fb6: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/ssot_scanner_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-370e339104: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/structure_drift_validator.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/structure_drift_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-394d552207: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/governance/lazy_seam_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/governance/lazy_seam_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-39505f8089: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/rule_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/rule_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-3b58f4cdc8: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-3bd433e1a3: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/anti_pattern_scanner_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/anti_pattern_scanner_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-3d83bb505e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/security/credential_guard.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/security/credential_guard.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-3da342afa1: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/constitutional_governance_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/constitutional_governance_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-3e61462abc: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/safety_eval_cache.py appears to perform write-like operations outside the expected execution choke point: delete

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/safety_eval_cache.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-41430c2687: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py appears to perform write-like operations outside the expected execution choke point: _create_healing_commit, add_and_commit, append, commit, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-432107c0ce: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/circular_import_fixer_enforcer.py appears to perform write-like operations outside the expected execution choke point: append, open_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/circular_import_fixer_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-457f25a315: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/intervention_server_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/intervention_server_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-460980d8b0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/healing_invocation_audit_enforcer.py appears to perform write-like operations outside the expected execution choke point: append, open_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/healing_invocation_audit_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-47c68d3d10: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DocstringComplianceAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4830905231: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/config/input_config.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/config/input_config.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-486513e756: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py appears to perform write-like operations outside the expected execution choke point: append, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4c5e1f1065: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py appears to perform write-like operations outside the expected execution choke point: append, append_result, open_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4c62648f63: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/ssot_guardrail.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/ssot_guardrail.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4ea2fb85a9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-4f9a2de5bd: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/vector_healing_strategy.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/vector_healing_strategy.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-543cd1ed9d: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/human_review_queue_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-54da3d2303: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/verify_no_mock_data_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/verify_no_mock_data_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-55d9d003c9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/pytest_config_guardrail.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/pytest_config_guardrail.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-56578ede3b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5683356cbf: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/governance_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/governance_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-575c3b00d3: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/content_quality_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/content_quality_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-578a454212: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/BenchmarkingAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/BenchmarkingAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-58072f8ba1: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py appears to perform write-like operations outside the expected execution choke point: append, open_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-588a971b81: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/namespace_medic_enforcer.py appears to perform write-like operations outside the expected execution choke point: append, open_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/namespace_medic_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5947b728a7: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/derived.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/derived.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5b747de237: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5c399eaa20: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/lead_quality_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/lead_quality_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5d3101e616: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/import_boundary_check_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/import_boundary_check_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-5dfa5a94f5: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-61de1d0ac5: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/system_invariant_scanner.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/system_invariant_scanner.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-6adc8eefbb: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/_verify.py appears to perform write-like operations outside the expected execution choke point: append, open_write, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/_verify.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-6cc0142ac2: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/three_tier_compliance_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/three_tier_compliance_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-6e9c8037d7: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/context_session_manager_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/context_session_manager_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-6eee9279e9: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py appears to perform write-like operations outside the expected execution choke point: append, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/FilesystemSSOTReconcilerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-6fefc54056: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/process_guardrail.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/process_guardrail.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-72075c4e27: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py appears to perform write-like operations outside the expected execution choke point: append, write, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-741d7717fd: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/airlock_trimmer_enforcer.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/airlock_trimmer_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-743606c902: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/force_app_depth_util.py appears to perform write-like operations outside the expected execution choke point: write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/force_app_depth_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-75a07ad0b7: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-771561facb: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-785c5db424: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/RedTeamAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/RedTeamAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-78c7e27850: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/security/secure_secrets.py appears to perform write-like operations outside the expected execution choke point: write_bytes

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/security/secure_secrets.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-78e381ea8c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/ssot_import_enforcer.py appears to perform write-like operations outside the expected execution choke point: write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/ssot_import_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-7bf7f110de: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/RegressionOracleAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/RegressionOracleAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-7d036eb2d7: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/logs_guard.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/logs_guard.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-810d22ce4e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/cognitive_batch_processor_util.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/cognitive_batch_processor_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8246559fe0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/report_location_validator.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/report_location_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-82eb18436b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-83b7627e32: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ResourceManagerAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ResourceManagerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-841e8be0cb: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/verb_canonicalizer_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/verb_canonicalizer_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-846f2a202f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/deliverability_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/deliverability_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8769dbf17c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/agent_audit_result_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/agent_audit_result_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-89427eca30: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/dependencygraph_validator.py appears to perform write-like operations outside the expected execution choke point: append, open_write, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/dependencygraph_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-89ce07df10: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8a113e7e97: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py appears to perform write-like operations outside the expected execution choke point: append, rename_path

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8c0726bf4a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/security_validation_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/security_validation_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8c4ebe8af3: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/audit_healing_strategy.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/audit_healing_strategy.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8c5727b36d: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py appears to perform write-like operations outside the expected execution choke point: append, assert_no_persistent_write, rename_path, write_bytes, write_json, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/mutation_prohibition_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8dc38fb9b0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/cst_transformers_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/cst_transformers_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8dc512cf0c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/ddd_alignment_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/ddd_alignment_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8e5e8f462f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/TestGeneratorAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-8ea31c62f5: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_json, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-92aafe2a7d: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/phase_acceptance_guardrail.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/phase_acceptance_guardrail.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-92bb885714: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py appears to perform write-like operations outside the expected execution choke point: write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-94ba15b33e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-95c61f3b74: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/unified_cst_healer_util.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/unified_cst_healer_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-975cdc6d03: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/register_all_validators_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/register_all_validators_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-977830f8ee: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/git_kraken_healing_strategy.py appears to perform write-like operations outside the expected execution choke point: _create_healing_commit, append, commit

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/git_kraken_healing_strategy.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-97bd6c232f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/cache_guard.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/cache_guard.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-9a4de56e3d: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/config/structure_blueprint/_simulate_verify.py appears to perform write-like operations outside the expected execution choke point: append, open_write, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/config/structure_blueprint/_simulate_verify.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-9b481e6d95: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/fast_dashboard_e2_e_pipeline_enforcer.py appears to perform write-like operations outside the expected execution choke point: write_json, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/fast_dashboard_e2_e_pipeline_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-9dcf7186b7: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/governance/lazy_seam_classifier.py appears to perform write-like operations outside the expected execution choke point: write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/governance/lazy_seam_classifier.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-9f0b82385b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CredentialScannerAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CredentialScannerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a03e650027: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/extract_pattern_util.py appears to perform write-like operations outside the expected execution choke point: append, open_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/extract_pattern_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a1ee228e3c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/migration_helper_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/migration_helper_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a3fe546112: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/RootHygieneAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/RootHygieneAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a47dfb35af: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/mission_preflight_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/mission_preflight_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a5c7121f05: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/input_validation_guardrail.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/input_validation_guardrail.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a62e273b05: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/GitHygieneAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/GitHygieneAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a6ba2e78a5: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/config/gravity_leak_config.py appears to perform write-like operations outside the expected execution choke point: _backup_and_write_file, append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/config/gravity_leak_config.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a6f93d0bd8: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/SurgicalHealingAdapter.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/SurgicalHealingAdapter.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a72f687837: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py appears to perform write-like operations outside the expected execution choke point: append, safe_delete

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a770b2fa3f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-a9d3bf2cfe: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/system_enforcer.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/system_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-aa60687394: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py appears to perform write-like operations outside the expected execution choke point: PreCommitSovereignAgent, append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ac02a8f0de: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ac1aed270a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/guard_observability_footprint_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/guard_observability_footprint_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b123ea8ce3: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/core_kernel/classification_kernel.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/core_kernel/classification_kernel.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b26524324a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/tiered_batch_util.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/tiered_batch_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b3964a12ee: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/artifact_emission_prohibition_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/artifact_emission_prohibition_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b3f9cf93e3: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b69e8a5b32: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SystemArchitectAgent.py appears to perform write-like operations outside the expected execution choke point: append, open_write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-b705a8547e: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/achv_bullet_synthesizer_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/achv_bullet_synthesizer_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ba423f1972: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ba8fccfa2a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/d0_injection_engine_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/d0_injection_engine_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-bb15a521e0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/integrity_validation_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/integrity_validation_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-bb3ecc2507: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SecurityManagerAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SecurityManagerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-bdeeab6ae2: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/fca_safety_gates_util.py appears to perform write-like operations outside the expected execution choke point: append, check_rename_collisions

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/fca_safety_gates_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c15f7051c6: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c1bb21b878: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/runners/code_validator_runner.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/runners/code_validator_runner.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c3a5089e48: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/agent_categorizer_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/agent_categorizer_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c5e52caa23: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/HierarchyAgent.py appears to perform write-like operations outside the expected execution choke point: append, append_text, safe_delete, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/HierarchyAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c673cab117: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/canonical_truth_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/canonical_truth_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c69ffb0736: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/magic_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/magic_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c6cf8fef17: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c6e716e1b0: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/hardcoded_path_refactorer_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c79379af97: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c95c426855: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/determinism_serialization_check.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/determinism_serialization_check.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-c968d1d87d: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/LocationHealerAgent.py appears to perform write-like operations outside the expected execution choke point: _backup_and_write_file, append, safe_delete, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/LocationHealerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ca29f45979: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/ats_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/ats_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ce526a9d82: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/sealed_interface_check_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/sealed_interface_check_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ce5670916f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/rag_guardrail.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/rag_guardrail.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d0354eb8ca: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/canary_token_defense_strategy.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/canary_token_defense_strategy.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d15dde3f21: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/priority_violation_guard.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/priority_violation_guard.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d1cc373b95: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/gravity_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/gravity_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d2cd38243d: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/type_erasure_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/type_erasure_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d63a8b5379: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/BootstrapAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/BootstrapAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d693cc7fb7: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeHealerAgent.py appears to perform write-like operations outside the expected execution choke point: append, write

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeHealerAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d71b8fb431: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DynamicSealAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DynamicSealAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-d9a2ff54fa: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/artifacts_guard.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/artifacts_guard.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-daaec18f9b: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-dcbfc1fcaa: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-dd62b38a9d: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/intelligence_query_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/intelligence_query_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-de4adefad4: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/ssot_relocator_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/ssot_relocator_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-df0c99a6fa: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py appears to perform write-like operations outside the expected execution choke point: _persist_audit_report, append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-dfb227f021: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/dependency_graph_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/dependency_graph_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e060b97182: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e1c11fed85: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e4e7cefcc6: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/TypeMechanicAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/TypeMechanicAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e6ef310943: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/agent_info_enforcer.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/agent_info_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e75da4e059: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/guardian_decision.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/guardian_decision.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e86955f776: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e8f09d3559: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-e9905a4443: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-eb6f05ca17: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/CodeDetectorAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/CodeDetectorAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-eb8565d93c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/base_detector_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/base_detector_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ee0d857a4f: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/ptc_invariants.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/ptc_invariants.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-ef43566f80: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/validators/path_fragility_validator.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/validators/path_fragility_validator.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f0c3f673b7: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/validation_result_types.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/validation_result_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f10c1211cc: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/governance/docs_structure_guard.py appears to perform write-like operations outside the expected execution choke point: append, write_json

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/governance/docs_structure_guard.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f179966722: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/module_collision_guardrail.py appears to perform write-like operations outside the expected execution choke point: append, write_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/module_collision_guardrail.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f33b93e449: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/git_health_sensor_enforcer.py appears to perform write-like operations outside the expected execution choke point: _check_uncommitted_changes, append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/git_health_sensor_enforcer.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f42cab4581: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/static_checks/powershell_ban.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/static_checks/powershell_ban.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f4dc44a387: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py appears to perform write-like operations outside the expected execution choke point: append, append_text

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f5dba29c5a: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/enforcement/AdapterBase.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/enforcement/AdapterBase.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f67cb4a296: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/types/file_health_score_types.py appears to perform write-like operations outside the expected execution choke point: delete

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/types/file_health_score_types.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f6c5d0041c: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/validate_dashboard_data_sourcing_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/validate_dashboard_data_sourcing_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-f86b65bcf3: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/reasoning/DocumentationAgent.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/reasoning/DocumentationAgent.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

### NON-L2-MUTATION-RISK-fb2ccbdeb2: Execution Mutation Boundary

**Priority:** MEDIUM

**Architectural Intent:**
L2 and the Universal Write Gateway are the sole durable mutation authority.

**Implementation Reality:**
agentic_core/L5_safety/utils/capability_extractor_util.py appears to perform write-like operations outside the expected execution choke point: append

**Impact:**
Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.

**Evidence Files:
- `agentic_core/L5_safety/utils/capability_extractor_util.py`

**Recommended Fix:**
Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.

---

## L6 Layer Gaps

### EMBEDDING-PLACEMENT-GAP-6a3fee6df4: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L6_observability/dashboards/core/experiencein_config.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L6_observability/dashboards/core/experiencein_config.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-8c98d6cc40: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L6_observability/engines/drift_detector.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L6_observability/engines/drift_detector.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-b223a64b33: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L6_observability/engines/determinism_digest_emitter.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L6_observability/engines/determinism_digest_emitter.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-c56d11c47a: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/L6_observability/engines/replay_key_computer.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/L6_observability/engines/replay_key_computer.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### LAYER-UPWARD-IMPORT-494fd9057d: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L6_observability/dashboards/dashboard_generator.py imports higher-authority layer references: L0, L2, L5

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L6_observability/dashboards/dashboard_generator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-4a4a62f9dc: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L6_observability/engines/TieredVigilanceEmitter.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L6_observability/engines/TieredVigilanceEmitter.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-6a3fee6df4: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L6_observability/dashboards/core/experiencein_config.py imports higher-authority layer references: L0, L1, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L6_observability/dashboards/core/experiencein_config.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-843704440e: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L6_observability/dashboards/core/DashboardDataGenerator.py imports higher-authority layer references: L5

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L6_observability/dashboards/core/DashboardDataGenerator.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-8baab37ffc: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L6_observability/engines/entropy_telemetry_engine.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L6_observability/engines/entropy_telemetry_engine.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-978e5a902a: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L6_observability/enforcement/reasoning_streamer.py imports higher-authority layer references: L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L6_observability/enforcement/reasoning_streamer.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-99676b18c0: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L6_observability/types/vigilance_event_types.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L6_observability/types/vigilance_event_types.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-a8e0ce692c: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L6_observability/utils/integrity_report_generator_util.py imports higher-authority layer references: L0, L2, L5

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L6_observability/utils/integrity_report_generator_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-af1397e0bb: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L6_observability/dashboards/dashboard_qa.py imports higher-authority layer references: L5

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L6_observability/dashboards/dashboard_qa.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-af14a6ed3f: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L6_observability/dashboards/analyze_dashboard_color_bug_util.py imports higher-authority layer references: L0

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L6_observability/dashboards/analyze_dashboard_color_bug_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### LAYER-UPWARD-IMPORT-c01d58e8eb: Layer Sovereignty Import Boundary

**Priority:** HIGH

**Architectural Intent:**
Lower layers must not import higher-authority layers upward across the L0-L6 spine.

**Implementation Reality:**
agentic_core/L6_observability/utils/fix_testing_observability_util.py imports higher-authority layer references: L0, L2

**Impact:**
Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.

**Evidence Files:
- `agentic_core/L6_observability/utils/fix_testing_observability_util.py`

**Recommended Fix:**
Replace upward imports with protocol seams, signed contracts, or read-only data contracts.

---

### PATHD-PLAN-HASH-GAP-2f262988f4: Path D Re-Clear Contract

**Priority:** HIGH

**Architectural Intent:**
Human MODIFY_DIFF flows must bind to original_plan_hash before L5 re-clear.

**Implementation Reality:**
agentic_core/L6_observability/types/dpo_types.py shows Path D or HITL markers without clear original_plan_hash evidence.

**Impact:**
Human patch flows may lose plan provenance or bypass strict re-clear assumptions.

**Evidence Files:
- `agentic_core/L6_observability/types/dpo_types.py`

**Recommended Fix:**
Require original_plan_hash and structured_patch_schema markers on all Path D decision artifacts.

---

### PATHD-PLAN-HASH-GAP-72be86db01: Path D Re-Clear Contract

**Priority:** HIGH

**Architectural Intent:**
Human MODIFY_DIFF flows must bind to original_plan_hash before L5 re-clear.

**Implementation Reality:**
agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py shows Path D or HITL markers without clear original_plan_hash evidence.

**Impact:**
Human patch flows may lose plan provenance or bypass strict re-clear assumptions.

**Evidence Files:
- `agentic_core/L6_observability/engines/hitl_dpo_pair_generator.py`

**Recommended Fix:**
Require original_plan_hash and structured_patch_schema markers on all Path D decision artifacts.

---

### L6-GAP-CONFIG-3eed2e9d41: Telemetry Configuration

**Priority:** LOW

**Architectural Intent:**
Cache parsed telemetry config files to avoid repeated I/O

**Implementation Reality:**
system_telemetry_util.py does not use config_file_cache

**Impact:**
Config files re-read and re-parsed on every telemetry event

**Evidence Files:
- `agentic_core/L6_observability/utils/system_telemetry_util.py`

**Recommended Fix:**
Wrap config loading with config_file_cache.get_or_fetch()

---

### L6-GAP-CONFIG-8baab37ffc: Telemetry Configuration

**Priority:** LOW

**Architectural Intent:**
Cache parsed telemetry config files to avoid repeated I/O

**Implementation Reality:**
entropy_telemetry_engine.py does not use config_file_cache

**Impact:**
Config files re-read and re-parsed on every telemetry event

**Evidence Files:
- `agentic_core/L6_observability/engines/entropy_telemetry_engine.py`

**Recommended Fix:**
Wrap config loading with config_file_cache.get_or_fetch()

---

### L6-GAP-CONFIG-aeb60076fa: Telemetry Configuration

**Priority:** LOW

**Architectural Intent:**
Cache parsed telemetry config files to avoid repeated I/O

**Implementation Reality:**
rag_telemetry_collector.py does not use config_file_cache

**Impact:**
Config files re-read and re-parsed on every telemetry event

**Evidence Files:
- `agentic_core/L6_observability/enforcement/rag_telemetry_collector.py`

**Recommended Fix:**
Wrap config loading with config_file_cache.get_or_fetch()

---

## UNKNOWN Layer Gaps

### EMBEDDING-PLACEMENT-GAP-0aed2b5d6b: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/runtime/config/reasoning_types.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/runtime/config/reasoning_types.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-4146708599: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/mixins/semantic_cache_mixin.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/mixins/semantic_cache_mixin.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-512dd31695: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/cache/cache_key_builders.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/cache/cache_key_builders.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-6a939d349f: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/interfaces/gateway.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/interfaces/gateway.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-6d48092b21: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/knowledge/document_loaders/source_document_types.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/knowledge/document_loaders/source_document_types.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-77e1a3435b: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/config/core/registry_config.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/config/core/registry_config.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-8a9df31d3a: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/config/core/complexity_metrics_config.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/config/core/complexity_metrics_config.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-a524e578d2: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/runtime/types/cache_entry_types.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/runtime/types/cache_entry_types.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-b8300fc4fb: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/runtime/types/expansion_strategy_types.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/runtime/types/expansion_strategy_types.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-c6dc97bb63: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/config/core/sovereign_config.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/config/core/sovereign_config.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-e3b13aed8e: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/base_agents/SovereignBaseAgent.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/base_agents/SovereignBaseAgent.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-e57194f067: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/knowledge/static_index/skill_taxonomy_types.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/knowledge/static_index/skill_taxonomy_types.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-ea346435e3: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/config/core/env_loader.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/config/core/env_loader.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-edf0c7ef72: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/config/core/gateway_config.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/config/core/gateway_config.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-f4269e062e: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/mixins/meta_learning_client_mixin.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/mixins/meta_learning_client_mixin.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

### EMBEDDING-PLACEMENT-GAP-fb88439bae: Embedding Sovereignty Boundary

**Priority:** HIGH

**Architectural Intent:**
Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.

**Implementation Reality:**
agentic_core/interfaces/execution_agents.py references embedding-related markers outside expected informational or factory surfaces.

**Impact:**
C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.

**Evidence Files:
- `agentic_core/interfaces/execution_agents.py`

**Recommended Fix:**
Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.

---

## Priority Matrix

| Layer | High | Medium | Low | Total |
|-------|------|--------|-----|-------|
| L0 | 18 | 363 | 0 | 381 |
| L1 | 12 | 9 | 0 | 21 |
| L2 | 71 | 6 | 9 | 86 |
| L3 | 31 | 49 | 0 | 80 |
| L4 | 8 | 0 | 0 | 8 |
| L5 | 420 | 207 | 0 | 627 |
| L6 | 17 | 0 | 3 | 20 |
| UNKNOWN | 16 | 0 | 0 | 16 |

## Next Steps

1. **High Priority Gaps:** Address immediately - these cause repeated expensive operations
2. **Medium Priority Gaps:** Schedule for next sprint - moderate latency impact
3. **Low Priority Gaps:** Backlog - minor optimizations
4. **Parse Failures:** Fix or explicitly waive broken files so analysis coverage is auditable

## Validation

After implementing fixes, rerun semantic gap analysis to verify:
- Cache modules are imported in hot path files
- Prompt assemblers explicitly cover S0, D0, I0, C0, and U0
- Governed prompt assembly emits a manifest hash
- Validator paths emit boundary_snapshot.json for prompt-package inspection
- Classification kernel, SovereignLLMGateway, AGENT_REGISTRY, meta_learning_pipeline, and write_gateway are all present and contract-visible
- No upward import edges violate the L0-L6 sovereignty matrix
- No direct provider SDK imports exist outside SovereignLLMGateway
- Non-L2 mutation paths are absent or explicitly mediated by Universal Write Gateway
- JIT / SemanticClock / CapabilityToken / SandboxEnvelope markers exist on the airlock path
- Embedding and FAISS signals stay inside informational RAG or factory-managed seams
- Meta-learning exposes all immutable stages plus dual injection and proposal_only defaults
- `get_or_fetch` pattern is used consistently
- Replay mode tests pass with warm cache (no redundant fetches)
- Side-effect envelope tests confirm cache-first behavior
- Parse failure count is zero or intentionally documented

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

