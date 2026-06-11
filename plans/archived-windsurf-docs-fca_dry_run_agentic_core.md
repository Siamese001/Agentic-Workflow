---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\fca_dry_run_agentic_core.md'
original_relative_path: 'fca_dry_run_agentic_core.md'
source_sha256: 01697f9012da5d2c1a08832f4ae654bac37a5d0c4c68707fdca9f2efc73ea7b4
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# FCA Dry-Run Report: agentic_core/

**Date**: 2026-02-11
**Branch**: `agentic-core-v5.3`
**Mode**: `dry_run=True, validate_only=True`
**Files scanned**: 1040

## Summary

| Metric | Value |
|---|---|
| Files analyzed | 1040 |
| Compliant | 467 |
| Audit findings (logger) | 671 |
| Layer violations | 168 |

## Classification Distribution

| FileType | Count |
|---|---|
| SCRIPT | 193 |
| UTILITY | 165 |
| CLASS | 136 |
| VALIDATOR | 111 |
| AGENT | 109 |
| IGNORE | 70 |
| TYPES | 69 |
| CONFIG | 64 |
| MIXIN | 49 |
| STRATEGY | 16 |
| EXCEPTION | 16 |
| ORCHESTRATOR | 12 |
| PROTOCOL | 11 |
| SERVICE | 9 |
| ADAPTER | 5 |
| null | 3 |
| FACTORY | 2 |

## Audit Naming Violations (by FileType)

| FileType | Violations |
|---|---|
| SCRIPT | 147 |
| CLASS | 107 |
| VALIDATOR | 65 |
| UTILITY | 51 |
| CONFIG | 34 |
| TYPES | 27 |
| STRATEGY | 15 |
| AGENT | 12 |
| ORCHESTRATOR | 12 |
| EXCEPTION | 12 |
| SERVICE | 8 |
| PROTOCOL | 5 |
| ADAPTER | 3 |
| null | 3 |
| FACTORY | 2 |

## Layer Alignment Violations (by Type)

| Violation Type | Count |
|---|---|
| `NON_AGENT_IN_REASONING` | 62 |
| `NESTED_LCD_SUBTREE` | 37 |
| `OBSERVABILITY_OUTSIDE_L6` | 35 |
| `CONFIG_SUFFIX_MISSING` | 19 |
| `L5_SUBPROCESS_NOT_ALLOWED` | 9 |
| `AGENT_LAYER_MISPLACEMENT` | 4 |
| `AGENT_OUTSIDE_REASONING` | 1 |
| `L6_SUBPROCESS_NOT_ALLOWED` | 1 |

## Audit Findings Detail

### COMPOUND_SUFFIX (1)

- `[COMPOUND_SUFFIX] expansion_strategy_types.py has 2 suffixes: ['_types', '_strategy']. Suggested: expansion_types_types.py`

### CROSS_LAYER (2)

- `[CROSS_LAYER] refactor_l1_mcp_imports_util.py contains layer indicator 'L1' but lives in L0_maintenance. Either rename the file to remove the layer prefix, or move it to L1_cognition/.`
- `[CROSS_LAYER] verify_l2_fix_util.py contains layer indicator 'L2' but lives in L0_maintenance. Either rename the file to remove the layer prefix, or move it to L2_execution/.`

### DETECT (503)

- `[DETECT] base_entity_config.py (TYPES) -> base_entity_types.py`
- `[DETECT] config_loader.py (UTILITY) -> config_loader_util.py`
- `[DETECT] constants_config.py (UTILITY) -> constants_util.py`
- `[DETECT] domain_constitution_config.py (UTILITY) -> domain_constitution_util.py`
- `[DETECT] env_loader.py (SERVICE) -> SovereignEnv.py`
- `[DETECT] gateway_config.py (TYPES) -> gateway_types.py`
- `[DETECT] hygiene_registry_config.py (UTILITY) -> hygiene_registry_util.py`
- `[DETECT] legacy_artifacts_config.py (TYPES) -> legacy_artifacts_types.py`
- `[DETECT] rag_config.py (TYPES) -> rag_types.py`
- `[DETECT] reflection_config.py (TYPES) -> reflection_types.py`
- `[DETECT] registry_config.py (UTILITY) -> registry_util.py`
- `[DETECT] sovereign_config.py (SERVICE) -> SovereignConfigManager.py`
- `[DETECT] classification_kernel.py (UTILITY) -> classification_kernel_util.py`
- `[DETECT] research_cache.py (CLASS) -> ResearchCache.py`
- `[DETECT] source_document_types.py (None) -> SourceDocument.py`
- `[DETECT] rag_orchestrator.py (ORCHESTRATOR) -> SovereignRagOrchestrator.py`
- `[DETECT] wiki_healer.py (STRATEGY) -> DeepWikiHealingStrategy.py`
- `[DETECT] cache_store_util.py (CLASS) -> ResearchCache.py`
- `[DETECT] action_verbs_types.py (UTILITY) -> action_verbs_util.py`
- `[DETECT] skill_taxonomy_types.py (UTILITY) -> skill_taxonomy_util.py`
- `[DETECT] legacy_agent_name_allowlist.py (UTILITY) -> legacy_agent_name_allowlist_util.py`
- `[DETECT] audit_healing_strategy.py (STRATEGY) -> AuditHealingStrategy.py`
- `[DETECT] boot_sequence.py (CLASS) -> BootSequence.py`
- `[DETECT] git_health_sensor.py (VALIDATOR) -> git_health_sensor_validator.py`
- `[DETECT] git_kraken_healing_strategy.py (STRATEGY) -> GitKrakenHealingStrategy.py`
- `[DETECT] ssot_guardrail.py (TYPES) -> ssot_guardrail_types.py`
- `[DETECT] v15_execution_gateway.py (VALIDATOR) -> v15_execution_validator.py`
- `[DETECT] v15_p3_contracts.py (EXCEPTION) -> v15_p3_contracts_exceptions.py`
- `[DETECT] v15_p4_contracts.py (EXCEPTION) -> v15_p4_contracts_exceptions.py`
- `[DETECT] v15_p5_contracts.py (EXCEPTION) -> v15_p5_contracts_exceptions.py`
- `[DETECT] v15_p6_contracts.py (EXCEPTION) -> v15_p6_contracts_exceptions.py`
- `[DETECT] v15_runtime_guard.py (UTILITY) -> v15_runtime_guard_util.py`
- `[DETECT] vector_healing_strategy.py (STRATEGY) -> VectorHealingStrategy.py`
- `[DETECT] sovereign_healing_engine.py (CLASS) -> SovereignHealingEngine.py`
- `[DETECT] action_capability.py (CONFIG) -> action_capability_config.py`
- `[DETECT] add_agent_suffix_plan_util.py (SCRIPT) -> add_agent_suffix_plan.py`
- `[DETECT] add_dataclass_to_agents_util.py (SCRIPT) -> add_dataclass_to_agents.py`
- `[DETECT] agent_capability_supplement_util.py (SCRIPT) -> agent_capability_supplement.py`
- `[DETECT] agent_validation_util.py (SCRIPT) -> agent_validation.py`
- `[DETECT] aggressive_dedup_util.py (SCRIPT) -> aggressive_dedup.py`
- `[DETECT] align_tests_structure_util.py (SCRIPT) -> align_tests_structure.py`
- `[DETECT] analyze_agent_count_waterfall_util.py (SCRIPT) -> analyze_agent_count_waterfall.py`
- `[DETECT] analyze_app_files_util.py (SCRIPT) -> analyze_app_files.py`
- `[DETECT] analyze_archive_util.py (SCRIPT) -> analyze_archive.py`
- `[DETECT] analyze_extract.py (UTILITY) -> analyze_extract_util.py`
- `[DETECT] archive_duplicates_util.py (SCRIPT) -> archive_duplicates.py`
- `[DETECT] archive_duplicate_tests_util.py (SCRIPT) -> archive_duplicate_tests.py`
- `[DETECT] ast_layer_stats_util.py (SCRIPT) -> ast_layer_stats.py`
- `[DETECT] audit_all_agents_mro_util.py (SCRIPT) -> audit_all_agents_mro.py`
- `[DETECT] audit_code_quality_metrics_util.py (SCRIPT) -> audit_code_quality_metrics.py`
- ... +453 more

### DUAL-TAG (4)

- `[DUAL-TAG] domain_agent_mixin.py carries conflicting tags: {'AGENT', 'MIXIN'}. Resolving via folder context.`
- `[DUAL-TAG] feature_flagged_agent_mixin.py carries conflicting tags: {'AGENT', 'MIXIN'}. Resolving via folder context.`
- `[DUAL-TAG] healer_agent_mixin.py carries conflicting tags: {'AGENT', 'MIXIN'}. Resolving via folder context.`
- `[DUAL-TAG] expansion_strategy_types.py carries conflicting tags: {'STRATEGY', 'TYPES'}. Resolving via folder context.`

### FOLDER_PURITY (76)

- `[FOLDER_PURITY] sovereign_healing_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] agent_audit_result.py in types/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] guardian_contract.py in types/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] guardian_registry.py in types/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] integration_contract.py in types/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] v15_contracts.py in types/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] v15_p2_contracts.py in types/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] budget_enforcer.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] cache_manager.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] capability_analyzer.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] codebase_mapper.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] CognitiveNode.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] cognitive_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] domain_manager.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] episodic_manager.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] guardrails.py in reasoning/ violates purity rules. Should be in validators/`
- `[FOLDER_PURITY] history_merger.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] memory_embedder.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] meta_client.py in reasoning/ violates purity rules. Should be in validators/`
- `[FOLDER_PURITY] meta_observability.py in reasoning/ violates purity rules. Should be in validators/`
- `[FOLDER_PURITY] perception_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] pitch_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] profile_updater.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] query_planner.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] reasoning_cache.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] semantic_manager.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] strategist_bio_writer.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] template_finder.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] template_matcher.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] token_updater.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] action_node.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] action_node_core.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] batch_embedding_service.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] execute_command_executor.py in reasoning/ violates purity rules. Should be in validators/`
- `[FOLDER_PURITY] secure_tools_impl.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] validation_orchestrator.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] action_router.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] AgentFactory.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] agent_gym_engine.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] autonomous_execution_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] call_formatting_router.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] context_curator_engine.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] convergence_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] coordinator_capability_orchestrator.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] dag_manager.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] decomposition_orchestrator.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] enforce_orchestration_policy.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] log_orchestration_metrics.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] nervous_system.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] omni_context_engine.py in reasoning/ violates purity rules. Should be in reasoning/`
- ... +26 more

### FOLDER_SUFFIX (14)

- `[FOLDER_SUFFIX] agent_audit_result.py in types/ missing required suffix. Suggested: agent_audit_result_types.py`
- `[FOLDER_SUFFIX] guardian_contract.py in types/ missing required suffix. Suggested: guardian_contract_types.py`
- `[FOLDER_SUFFIX] guardian_registry.py in types/ missing required suffix. Suggested: guardian_registry_types.py`
- `[FOLDER_SUFFIX] integration_contract.py in types/ missing required suffix. Suggested: integration_contract_types.py`
- `[FOLDER_SUFFIX] v15_contracts.py in types/ missing required suffix. Suggested: v15_contracts_types.py`
- `[FOLDER_SUFFIX] v15_p2_contracts.py in types/ missing required suffix. Suggested: v15_p2_contracts_types.py`
- `[FOLDER_SUFFIX] local_disk_adapter.py in utils/ missing required suffix. Suggested: local_disk_adapter_util.py`
- `[FOLDER_SUFFIX] blueprint_compiler.py in config/ missing required suffix. Suggested: blueprint_compiler_config.py`
- `[FOLDER_SUFFIX] sovereign_report.py in types/ missing required suffix. Suggested: sovereign_report_types.py`
- `[FOLDER_SUFFIX] capability_gap_types.py in config/ missing required suffix. Suggested: capability_gap_types_config.py`
- `[FOLDER_SUFFIX] reasoning_types.py in config/ missing required suffix. Suggested: reasoning_types_config.py`
- `[FOLDER_SUFFIX] meta_learning_engine.py in utils/ missing required suffix. Suggested: meta_learning_engine_util.py`
- `[FOLDER_SUFFIX] meta_learning_storage.py in utils/ missing required suffix. Suggested: meta_learning_storage_util.py`
- `[FOLDER_SUFFIX] structural_healing_engine.py in utils/ missing required suffix. Suggested: structural_healing_engine_util.py`

### FORBIDDEN (4)

- `[FORBIDDEN] _constants.py: Leading Underscore Violation (non-__init__ file). Fix: remove leading underscore or rename to descriptive name.`
- `[FORBIDDEN] _simulate_verify.py: Leading Underscore Violation (non-__init__ file). Fix: remove leading underscore or rename to descriptive name.`
- `[FORBIDDEN] _verify.py: Leading Underscore Violation (non-__init__ file). Fix: remove leading underscore or rename to descriptive name.`
- `[FORBIDDEN] _config_compat.py: Leading Underscore Violation (non-__init__ file). Fix: remove leading underscore or rename to descriptive name.`

### PASSIVE_AGENT_NAMING (8)

- `[PASSIVE_AGENT_NAMING] SubatomicHopAgent.py: SubatomicHopAgent is a dataclass/BaseModel with no active methods. Rename to *_util.py or *_types.py.`
- `[PASSIVE_AGENT_NAMING] CodeFormatterAgent.py: CodeFormatterAgent is a dataclass/BaseModel with no active methods. Rename to *_util.py or *_types.py.`
- `[PASSIVE_AGENT_NAMING] DuplicateCodeDetectorAgent.py: DuplicateCodeDetectorAgent is a dataclass/BaseModel with no active methods. Rename to *_util.py or *_types.py.`
- `[PASSIVE_AGENT_NAMING] StructuralEngineerAgent.py: StructuralEngineerAgent is a dataclass/BaseModel with no active methods. Rename to *_util.py or *_types.py.`
- `[PASSIVE_AGENT_NAMING] TerritoryChangeHandlerAgent.py: TerritoryChangeHandlerAgent is a dataclass/BaseModel with no active methods. Rename to *_util.py or *_types.py.`
- `[PASSIVE_AGENT_NAMING] TestGeneratorAgent.py: TestGeneratorAgent is a dataclass/BaseModel with no active methods. Rename to *_util.py or *_types.py.`
- `[PASSIVE_AGENT_NAMING] TypeHintFixerAgent.py: TypeHintFixerAgent is a dataclass/BaseModel with no active methods. Rename to *_util.py or *_types.py.`
- `[PASSIVE_AGENT_NAMING] UnusedCleanupAgent.py: UnusedCleanupAgent is a dataclass/BaseModel with no active methods. Rename to *_util.py or *_types.py.`

### TERRITORY (59)

- `[TERRITORY] add_test_coverage_util.py (SCRIPT) is in utils`
- `[TERRITORY] complexity_visitor_util.py (CONFIG) is in utils`
- `[TERRITORY] core_integrity_util.py (VALIDATOR) is in utils`
- `[TERRITORY] fix_all_tunnels_util.py (SCRIPT) is in utils`
- `[TERRITORY] fix_depth_violations_util.py (SCRIPT) is in utils`
- `[TERRITORY] fix_mission_runner_util.py (SCRIPT) is in utils`
- `[TERRITORY] fix_remaining_depth_util.py (SCRIPT) is in utils`
- `[TERRITORY] force_annexation_util.py (SCRIPT) is in utils`
- `[TERRITORY] gravity_audit_util.py (SCRIPT) is in utils`
- `[TERRITORY] json_formatter_util.py (CLASS) is in utils`
- `[TERRITORY] manifest_guardian_util.py (CONFIG) is in utils`
- `[TERRITORY] scorched_earth_merge_util.py (SCRIPT) is in utils`
- `[TERRITORY] sovereign_alignment_v2_util.py (SCRIPT) is in utils`
- `[TERRITORY] sovereign_convergence_util.py (SCRIPT) is in utils`
- `[TERRITORY] structural_fix_util.py (SCRIPT) is in utils`
- `[TERRITORY] trim_remaining_airlocks_util.py (SCRIPT) is in utils`
- `[TERRITORY] deterministic_cleaner_util.py (VALIDATOR) is in utils`
- `[TERRITORY] egress_util.py (CLASS) is in utils`
- `[TERRITORY] staging_buffer_util.py (EXCEPTION) is in utils`
- `[TERRITORY] circuit_breaker_util.py (CLASS) is in utils`
- `[TERRITORY] experience_buffer_util.py (CLASS) is in utils`
- `[TERRITORY] local_disk_adapter.py (ADAPTER) is in utils`
- `[TERRITORY] rag_enhancement_util.py (VALIDATOR) is in utils`
- `[TERRITORY] structure_blueprint_config.py (UTILITY) is in config`
- `[TERRITORY] agent_categorizer_util.py (CLASS) is in utils`
- `[TERRITORY] capability_extractor_util.py (CLASS) is in utils`
- `[TERRITORY] cognitive_batch_processor_util.py (VALIDATOR) is in utils`
- `[TERRITORY] extract_pattern_util.py (SCRIPT) is in utils`
- `[TERRITORY] fix_inherited_invocation_util.py (SCRIPT) is in utils`
- `[TERRITORY] force_app_depth_util.py (SCRIPT) is in utils`
- `[TERRITORY] forge_fortress_util.py (SCRIPT) is in utils`
- `[TERRITORY] gravity_visitor_util.py (VALIDATOR) is in utils`
- `[TERRITORY] pre_deploy_check_util.py (SCRIPT) is in utils`
- `[TERRITORY] set_complexity_health_100_util.py (SCRIPT) is in utils`
- `[TERRITORY] sovereign_lock_util.py (SCRIPT) is in utils`
- `[TERRITORY] ssot_folder_check_util.py (SCRIPT) is in utils`
- `[TERRITORY] subprocess_security_util.py (EXCEPTION) is in utils`
- `[TERRITORY] tiered_batch_util.py (VALIDATOR) is in utils`
- `[TERRITORY] unified_cst_healer_util.py (TYPES) is in utils`
- `[TERRITORY] validate_dashboard_data_sourcing_util.py (SCRIPT) is in utils`
- `[TERRITORY] validate_dashboard_ssot_util.py (SCRIPT) is in utils`
- `[TERRITORY] validate_path_ssot_util.py (SCRIPT) is in utils`
- `[TERRITORY] verify_no_mock_data_util.py (SCRIPT) is in utils`
- `[TERRITORY] verify_semantic_meta_learning_util.py (SCRIPT) is in utils`
- `[TERRITORY] fix_testing_observability_util.py (SCRIPT) is in utils`
- `[TERRITORY] integrity_report_generator_util.py (VALIDATOR) is in utils`
- `[TERRITORY] system_telemetry_util.py (CLASS) is in utils`
- `[TERRITORY] discovery_parser_util.py (CLASS) is in utils`
- `[TERRITORY] discovery_util.py (CLASS) is in utils`
- `[TERRITORY] dynamic_loader_util.py (CLASS) is in utils`
- ... +9 more

## Layer Violations Detail

### AGENT_LAYER_MISPLACEMENT (4)

| File | Current | Suggested | Confidence | Evidence |
|---|---|---|---|---|
| `agentic_core/L0_maintenance/reasoning/FilesystemSSOTReconcilerAgent.py` | L0_maintenance | L5_safety | HIGH | agentic_core.L5_safety.enforcement.archival_gatekeeper_gate, agentic_core.L5_safety.reasoning.HierarchyAgent, agentic_core.L5_safety.reasoning.LocationValidatorAgent |
| `agentic_core/L0_maintenance/reasoning/SSOTFolderCleanupAgent.py` | L0_maintenance | L5_safety | HIGH | agentic_core.L5_safety.config.structure_blueprint_config, agentic_core.L5_safety.reasoning.CognitiveDispositionAgent, agentic_core.L5_safety.enforcement.archival_gatekeeper_gate |
| `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` | L2_execution | L1_cognition | HIGH | google.generativeai, openai |
| `agentic_core/L2_execution/reasoning/SubAtomicRegistryAgent.py` | L2_execution | L5_safety | HIGH | agentic_core.L5_safety.reasoning.StructureValidatorAgent, agentic_core.L5_safety.reasoning.CodeEnforcerAgent, agentic_core.L5_safety.reasoning.CodeEnforcerAgent |

### AGENT_OUTSIDE_REASONING (1)

| File | Agent Classes | Current Folder |
|---|---|---|
| `agentic_core/L3_orchestration/types/orchestrator_types.py` | IOrchestratorAgent | types |

### CONFIG_SUFFIX_MISSING (19)

| File | Message |
|---|---|
| `agentic_core/config/core/config_loader.py` | 'config_loader.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'config_loader_config.py' |
| `agentic_core/config/core/env_loader.py` | 'env_loader.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'env_loader_config.py'. |
| `agentic_core/L5_safety/config/blueprint_compiler.py` | 'blueprint_compiler.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'blueprint_compiler_ |
| `agentic_core/L5_safety/config/structure_blueprint/artifacts.py` | 'artifacts.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'artifacts_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/classification.py` | 'classification.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'classification_config.p |
| `agentic_core/L5_safety/config/structure_blueprint/derived.py` | 'derived.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'derived_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/governance.py` | 'governance.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'governance_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/semantics.py` | 'semantics.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'semantics_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | 'ssot.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'ssot_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/territories.py` | 'territories.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'territories_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/_verify.py` | '_verify.py' lives in a config/ directory but is missing the '_config' suffix. Rename to '_verify_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/enforcement/blueprint_hash.py` | 'blueprint_hash.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'blueprint_hash_config.p |
| `agentic_core/L5_safety/config/structure_blueprint/enforcement/cross_layer.py` | 'cross_layer.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'cross_layer_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/enforcement/import_graph.py` | 'import_graph.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'import_graph_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/enforcement/leaf_node.py` | 'leaf_node.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'leaf_node_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/enforcement/mixin_ast.py` | 'mixin_ast.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'mixin_ast_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/enforcement/territory_diff.py` | 'territory_diff.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'territory_diff_config.p |
| `agentic_core/L5_safety/config/structure_blueprint/enforcement/types.py` | 'types.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'types_config.py'. |
| `agentic_core/L5_safety/config/structure_blueprint/enforcement/volatile_rules.py` | 'volatile_rules.py' lives in a config/ directory but is missing the '_config' suffix. Rename to 'volatile_rules_config.p |

### L5_SUBPROCESS_NOT_ALLOWED (9)

- `agentic_core/L5_safety/config/structure_blueprint/_simulate_verify.py`: '_simulate_verify.py' imports subprocess in L5 but is NOT on the L5_SUBPROCESS_ALLOWLIST. Move execution logic to L2 or add to allowlist with justific
- `agentic_core/L5_safety/enforcement/safe_subprocess_handler_enforcer.py`: 'safe_subprocess_handler.py' imports subprocess in L5 but is NOT on the L5_SUBPROCESS_ALLOWLIST. Move execution logic to L2 or add to allowlist with j
- `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py`: 'ArchitectureGovernorAgent.py' imports subprocess in L5 but is NOT on the L5_SUBPROCESS_ALLOWLIST. Move execution logic to L2 or add to allowlist with
- `agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py`: 'AutonomyGuardianAgent.py' imports subprocess in L5 but is NOT on the L5_SUBPROCESS_ALLOWLIST. Move execution logic to L2 or add to allowlist with jus
- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`: 'FileClassificationAgent.py' imports subprocess in L5 but is NOT on the L5_SUBPROCESS_ALLOWLIST. Move execution logic to L2 or add to allowlist with j
- `agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py`: 'PreCommitSovereignAgent.py' imports subprocess in L5 but is NOT on the L5_SUBPROCESS_ALLOWLIST. Move execution logic to L2 or add to allowlist with j
- `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py`: 'SovereignActionPlaneAgent.py' imports subprocess in L5 but is NOT on the L5_SUBPROCESS_ALLOWLIST. Move execution logic to L2 or add to allowlist with
- `agentic_core/L5_safety/utils/pre_deploy_check_util.py`: 'pre_deploy_check_util.py' imports subprocess in L5 but is NOT on the L5_SUBPROCESS_ALLOWLIST. Move execution logic to L2 or add to allowlist with jus
- `agentic_core/L5_safety/utils/subprocess_security_util.py`: 'subprocess_security_util.py' imports subprocess in L5 but is NOT on the L5_SUBPROCESS_ALLOWLIST. Move execution logic to L2 or add to allowlist with

### L6_SUBPROCESS_NOT_ALLOWED (1)

- `agentic_core/L6_observability/dashboards/verify_dashboard_e2e_playwright_util.py`: 'verify_dashboard_e2e_playwright_util.py' imports subprocess in L6 but is NOT on the L6_HYBRID_ALLOWLIST.

### NESTED_LCD_SUBTREE (37)

- `agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py`: Leaf domain 'knowledge' must not sprout LCD subfolder 'reasoning/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/anomaly_report_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/capability_gap_types.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/contextual_router_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/detection_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/feature_flags_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/heal_result_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/injection_type_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/model_provider_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/model_tier_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/prompt_injection_loader_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/reasoning_types.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/review_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/security_level_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/shared_infrastructure_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/signal_quality_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/config/validation_severity_config.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'config/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/enforcement/envelope_factory.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'enforcement/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/types/cache_entry_types.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'types/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/types/circuit_breaker_types.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'types/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/types/claim_type_types.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'types/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/types/cost_governor_types.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'types/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/types/expansion_strategy_types.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'types/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/types/recovery_types.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'types/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/types/sovereign_events_types.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'types/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/types/state_types.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'types/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/utils/discovery_parser_util.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'utils/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/utils/discovery_util.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'utils/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/utils/dynamic_loader_util.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'utils/'. Only L0–L6 layer roots may have LCD subtrees.
- `agentic_core/runtime/utils/file_cache_util.py`: Leaf domain 'runtime' must not sprout LCD subfolder 'utils/'. Only L0–L6 layer roots may have LCD subtrees.
- ... +7 more

### NON_AGENT_IN_REASONING (62)

| File | Message |
|---|---|
| `agentic_core/L0_maintenance/reasoning/sovereign_healing_engine.py` | 'sovereign_healing_engine.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or |
| `agentic_core/L1_cognition/reasoning/budget_enforcer.py` | 'budget_enforcer.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcem |
| `agentic_core/L1_cognition/reasoning/cache_manager.py` | 'cache_manager.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcemen |
| `agentic_core/L1_cognition/reasoning/capability_analyzer.py` | 'capability_analyzer.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enfo |
| `agentic_core/L1_cognition/reasoning/codebase_mapper.py` | 'codebase_mapper.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcem |
| `agentic_core/L1_cognition/reasoning/CognitiveNode.py` | 'CognitiveNode.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcemen |
| `agentic_core/L1_cognition/reasoning/cognitive_engine.py` | 'cognitive_engine.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforce |
| `agentic_core/L1_cognition/reasoning/domain_manager.py` | 'domain_manager.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforceme |
| `agentic_core/L1_cognition/reasoning/episodic_manager.py` | 'episodic_manager.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforce |
| `agentic_core/L1_cognition/reasoning/guardrails.py` | 'guardrails.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcement/  |
| `agentic_core/L1_cognition/reasoning/history_merger.py` | 'history_merger.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforceme |
| `agentic_core/L1_cognition/reasoning/memory_embedder.py` | 'memory_embedder.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcem |
| `agentic_core/L1_cognition/reasoning/meta_client.py` | 'meta_client.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcement/ |
| `agentic_core/L1_cognition/reasoning/meta_observability.py` | 'meta_observability.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enfor |
| `agentic_core/L1_cognition/reasoning/perception_engine.py` | 'perception_engine.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforc |
| `agentic_core/L1_cognition/reasoning/pitch_engine.py` | 'pitch_engine.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcement |
| `agentic_core/L1_cognition/reasoning/profile_updater.py` | 'profile_updater.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcem |
| `agentic_core/L1_cognition/reasoning/query_planner.py` | 'query_planner.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcemen |
| `agentic_core/L1_cognition/reasoning/reasoning_cache.py` | 'reasoning_cache.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcem |
| `agentic_core/L1_cognition/reasoning/semantic_manager.py` | 'semantic_manager.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforce |
| `agentic_core/L1_cognition/reasoning/strategist_bio_writer.py` | 'strategist_bio_writer.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or en |
| `agentic_core/L1_cognition/reasoning/template_finder.py` | 'template_finder.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcem |
| `agentic_core/L1_cognition/reasoning/template_matcher.py` | 'template_matcher.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforce |
| `agentic_core/L1_cognition/reasoning/token_updater.py` | 'token_updater.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcemen |
| `agentic_core/L2_execution/reasoning/action_node.py` | 'action_node.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcement/ |
| `agentic_core/L2_execution/reasoning/action_node_core.py` | 'action_node_core.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforce |
| `agentic_core/L2_execution/reasoning/batch_embedding_service.py` | 'batch_embedding_service.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or  |
| `agentic_core/L2_execution/reasoning/execute_command_executor.py` | 'execute_command_executor.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or |
| `agentic_core/L2_execution/reasoning/secure_tools_impl.py` | 'secure_tools_impl.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforc |
| `agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py` | 'SovereignMCPGatewayAgent.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or |
| `agentic_core/L2_execution/reasoning/tool_registry.py` | 'tool_registry.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcemen |
| `agentic_core/L3_orchestration/reasoning/action_router.py` | 'action_router.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcemen |
| `agentic_core/L3_orchestration/reasoning/AgentFactory.py` | 'AgentFactory.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcement |
| `agentic_core/L3_orchestration/reasoning/agent_gym_engine.py` | 'agent_gym_engine.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforce |
| `agentic_core/L3_orchestration/reasoning/autonomous_execution_engine.py` | 'autonomous_execution_engine.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ |
| `agentic_core/L3_orchestration/reasoning/call_formatting_router.py` | 'call_formatting_router.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or e |
| `agentic_core/L3_orchestration/reasoning/context_curator_engine.py` | 'context_curator_engine.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or e |
| `agentic_core/L3_orchestration/reasoning/convergence_engine.py` | 'convergence_engine.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enfor |
| `agentic_core/L3_orchestration/reasoning/coordinator_capability_orchestrator.py` | 'coordinator_capability_orchestrator.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move t |
| `agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py` | 'DagRuntimeInspectorAgent.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or |
| `agentic_core/L3_orchestration/reasoning/dag_manager.py` | 'dag_manager.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforcement/ |
| `agentic_core/L3_orchestration/reasoning/enforce_orchestration_policy.py` | 'enforce_orchestration_policy.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils |
| `agentic_core/L3_orchestration/reasoning/log_orchestration_metrics.py` | 'log_orchestration_metrics.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ o |
| `agentic_core/L3_orchestration/reasoning/nervous_system.py` | 'nervous_system.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforceme |
| `agentic_core/L3_orchestration/reasoning/omni_context_engine.py` | 'omni_context_engine.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enfo |
| `agentic_core/L3_orchestration/reasoning/proactive_fission_scanner.py` | 'proactive_fission_scanner.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ o |
| `agentic_core/L3_orchestration/reasoning/reflex_layer_pattern.py` | 'reflex_layer_pattern.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enf |
| `agentic_core/L3_orchestration/reasoning/sovereign_mcp_marketplace.py` | 'sovereign_mcp_marketplace.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ o |
| `agentic_core/L3_orchestration/reasoning/sovereign_mcp_router.py` | 'sovereign_mcp_router.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enf |
| `agentic_core/L3_orchestration/reasoning/sub_atomic_engine_impl.py` | 'sub_atomic_engine_impl.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or e |
| `agentic_core/L5_safety/reasoning/cache_invalidation_utils.py` | 'cache_invalidation_utils.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or |
| `agentic_core/L5_safety/reasoning/code_tool_runner_core.py` | 'code_tool_runner_core.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or en |
| `agentic_core/L5_safety/reasoning/ConstitutionalOverseerAgent.py` | 'ConstitutionalOverseerAgent.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ |
| `agentic_core/L5_safety/reasoning/DependencyDiplomatAgent.py` | 'DependencyDiplomatAgent.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or  |
| `agentic_core/L5_safety/reasoning/GlobalComplianceAggregatorAgent.py` | 'GlobalComplianceAggregatorAgent.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to ut |
| `agentic_core/L5_safety/reasoning/OmniContextAgent.py` | 'OmniContextAgent.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enforce |
| `agentic_core/L5_safety/reasoning/SemanticMapperAgent.py` | 'SemanticMapperAgent.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or enfo |
| `agentic_core/L5_safety/reasoning/SemanticTerritoryMapperAgent.py` | 'SemanticTerritoryMapperAgent.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils |
| `agentic_core/L5_safety/reasoning/SignatureVerifierAgent.py` | 'SignatureVerifierAgent.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or e |
| `agentic_core/L5_safety/reasoning/TokenBudgetInspectorAgent.py` | 'TokenBudgetInspectorAgent.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ o |
| `agentic_core/L6_observability/reasoning/PerformanceAnalystAgentSimple.py` | 'PerformanceAnalystAgentSimple.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to util |
| `agentic_core/L6_observability/reasoning/SovereignHealthMonitor.py` | 'SovereignHealthMonitor.py' is in reasoning/ but contains no Agent, Orchestrator, or Executor class. Move to utils/ or e |

### OBSERVABILITY_OUTSIDE_L6 (35)

| File | Keyword | Current Layer |
|---|---|---|
| `agentic_core/L0_maintenance/scripts/audit_code_quality_metrics_util.py` | metric | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/audit_dashboard_naming_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/audit_dashboard_ssot_flow_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/audit_dashboard_ssot_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/clean_dashboard_html_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/compare_dashboard_data_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/dashboard_live_server_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/dashboard_qa_deep_audit_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/dashboard_ssot_definitions_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/dashboard_style_report_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/dashboard_verifier.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/debug_dashboard_rendering_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/diagnose_dashboard_live_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/diagnose_user_dashboard_view_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/enforce_dashboard_freshness_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/extract_dashboard_errors_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/generate_blueprint_metrics_util.py` | metric | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/generate_dashboard_ssot_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/inspect_dashboard_browser_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/rca_dashboard_row_collapse_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/regenerate_dashboard_full_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/regenerate_dashboard_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/start_dashboard_server_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/sync_dashboard_agent_count_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/trace_dashboard_generation_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/validate_dashboard_changes_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/validate_dashboard_totals_util.py` | dashboard | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/verify_healing_metrics_util.py` | metric | L0_maintenance |
| `agentic_core/L0_maintenance/scripts/windsurf_realtime_dashboard_util.py` | dashboard | L0_maintenance |
| `agentic_core/L2_execution/enforcement/dashboard_e2_e_pipeline.py` | dashboard | L2_execution |
| `agentic_core/L4_state/enforcement/telemetry_recorder.py` | telemetry | L4_state |
| `agentic_core/L4_state/utils/sanitize_telemetry_util.py` | telemetry | L4_state |
| `agentic_core/L5_safety/enforcement/fast_dashboard_e2_e_pipeline_enforcer.py` | dashboard | L5_safety |
| `agentic_core/L5_safety/utils/validate_dashboard_data_sourcing_util.py` | dashboard | L5_safety |
| `agentic_core/L5_safety/utils/validate_dashboard_ssot_util.py` | dashboard | L5_safety |

## Proposed File Moves

- `[FOLDER_PURITY] sovereign_healing_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] agent_audit_result.py in types/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] guardian_contract.py in types/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] guardian_registry.py in types/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] integration_contract.py in types/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] v15_contracts.py in types/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] v15_p2_contracts.py in types/ violates purity rules. Should be in enforcement/`
- `[TERRITORY] add_test_coverage_util.py (SCRIPT) is in utils`
- `[TERRITORY] complexity_visitor_util.py (CONFIG) is in utils`
- `[TERRITORY] core_integrity_util.py (VALIDATOR) is in utils`
- `[TERRITORY] fix_all_tunnels_util.py (SCRIPT) is in utils`
- `[TERRITORY] fix_depth_violations_util.py (SCRIPT) is in utils`
- `[TERRITORY] fix_mission_runner_util.py (SCRIPT) is in utils`
- `[TERRITORY] fix_remaining_depth_util.py (SCRIPT) is in utils`
- `[TERRITORY] force_annexation_util.py (SCRIPT) is in utils`
- `[TERRITORY] gravity_audit_util.py (SCRIPT) is in utils`
- `[TERRITORY] json_formatter_util.py (CLASS) is in utils`
- `[TERRITORY] manifest_guardian_util.py (CONFIG) is in utils`
- `[TERRITORY] scorched_earth_merge_util.py (SCRIPT) is in utils`
- `[TERRITORY] sovereign_alignment_v2_util.py (SCRIPT) is in utils`
- `[TERRITORY] sovereign_convergence_util.py (SCRIPT) is in utils`
- `[TERRITORY] structural_fix_util.py (SCRIPT) is in utils`
- `[TERRITORY] trim_remaining_airlocks_util.py (SCRIPT) is in utils`
- `[FOLDER_PURITY] budget_enforcer.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] cache_manager.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] capability_analyzer.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] codebase_mapper.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] CognitiveNode.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] cognitive_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] domain_manager.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] episodic_manager.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] guardrails.py in reasoning/ violates purity rules. Should be in validators/`
- `[FOLDER_PURITY] history_merger.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] memory_embedder.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] meta_client.py in reasoning/ violates purity rules. Should be in validators/`
- `[FOLDER_PURITY] meta_observability.py in reasoning/ violates purity rules. Should be in validators/`
- `[FOLDER_PURITY] perception_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] pitch_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] profile_updater.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] query_planner.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] reasoning_cache.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] semantic_manager.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] strategist_bio_writer.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] template_finder.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] template_matcher.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] token_updater.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] action_node.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] action_node_core.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] batch_embedding_service.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] execute_command_executor.py in reasoning/ violates purity rules. Should be in validators/`
- `[FOLDER_PURITY] secure_tools_impl.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] validation_orchestrator.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[TERRITORY] deterministic_cleaner_util.py (VALIDATOR) is in utils`
- `[TERRITORY] egress_util.py (CLASS) is in utils`
- `[TERRITORY] staging_buffer_util.py (EXCEPTION) is in utils`
- `[FOLDER_PURITY] action_router.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] AgentFactory.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] agent_gym_engine.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] autonomous_execution_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] call_formatting_router.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] context_curator_engine.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] convergence_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] coordinator_capability_orchestrator.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] dag_manager.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] decomposition_orchestrator.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] enforce_orchestration_policy.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] log_orchestration_metrics.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] nervous_system.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] omni_context_engine.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] orchestrator_engine.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] proactive_fission_scanner.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] recovery_coordinator_orchestrator.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] recursive_orchestrator.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] reflex_layer_pattern.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] rl_coordinator_orchestrator.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] sovereign_mcp_marketplace.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] sovereign_mcp_router.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] sovereign_rag_orchestrator.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] sovereign_redis_orchestrator.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] sub_atomic_engine_impl.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[TERRITORY] circuit_breaker_util.py (CLASS) is in utils`
- `[TERRITORY] experience_buffer_util.py (CLASS) is in utils`
- `[TERRITORY] local_disk_adapter.py (ADAPTER) is in utils`
- `[FOLDER_PURITY] local_disk_adapter.py in utils/ violates purity rules. Should be in enforcement/`
- `[TERRITORY] rag_enhancement_util.py (VALIDATOR) is in utils`
- `[FOLDER_PURITY] blueprint_compiler.py in config/ violates purity rules. Should be in enforcement/`
- `[TERRITORY] structure_blueprint_config.py (UTILITY) is in config`
- `[FOLDER_PURITY] AdapterBase.py in enforcement/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] cache_invalidation_utils.py in reasoning/ violates purity rules. Should be in utils/`
- `[FOLDER_PURITY] code_tool_runner_core.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] InspectorExecutor.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[TERRITORY] agent_categorizer_util.py (CLASS) is in utils`
- `[TERRITORY] capability_extractor_util.py (CLASS) is in utils`
- `[TERRITORY] cognitive_batch_processor_util.py (VALIDATOR) is in utils`
- `[TERRITORY] extract_pattern_util.py (SCRIPT) is in utils`
- `[TERRITORY] fix_inherited_invocation_util.py (SCRIPT) is in utils`
- `[TERRITORY] force_app_depth_util.py (SCRIPT) is in utils`
- `[TERRITORY] forge_fortress_util.py (SCRIPT) is in utils`
- `[TERRITORY] gravity_visitor_util.py (VALIDATOR) is in utils`
- `[TERRITORY] pre_deploy_check_util.py (SCRIPT) is in utils`
- `[TERRITORY] set_complexity_health_100_util.py (SCRIPT) is in utils`
- `[TERRITORY] sovereign_lock_util.py (SCRIPT) is in utils`
- `[TERRITORY] ssot_folder_check_util.py (SCRIPT) is in utils`
- `[TERRITORY] subprocess_security_util.py (EXCEPTION) is in utils`
- `[TERRITORY] tiered_batch_util.py (VALIDATOR) is in utils`
- `[TERRITORY] unified_cst_healer_util.py (TYPES) is in utils`
- `[TERRITORY] validate_dashboard_data_sourcing_util.py (SCRIPT) is in utils`
- `[TERRITORY] validate_dashboard_ssot_util.py (SCRIPT) is in utils`
- `[TERRITORY] validate_path_ssot_util.py (SCRIPT) is in utils`
- `[TERRITORY] verify_no_mock_data_util.py (SCRIPT) is in utils`
- `[TERRITORY] verify_semantic_meta_learning_util.py (SCRIPT) is in utils`
- `[FOLDER_PURITY] ObservabilityProbeExecutor.py in reasoning/ violates purity rules. Should be in reasoning/`
- `[FOLDER_PURITY] PerformanceAnalystAgentSimple.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] SovereignHealthMonitor.py in reasoning/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] sovereign_report.py in types/ violates purity rules. Should be in enforcement/`
- `[TERRITORY] fix_testing_observability_util.py (SCRIPT) is in utils`
- `[TERRITORY] integrity_report_generator_util.py (VALIDATOR) is in utils`
- `[TERRITORY] system_telemetry_util.py (CLASS) is in utils`
- `[FOLDER_PURITY] capability_gap_types.py in config/ violates purity rules. Should be in types/`
- `[FOLDER_PURITY] reasoning_types.py in config/ violates purity rules. Should be in types/`
- `[TERRITORY] discovery_parser_util.py (CLASS) is in utils`
- `[TERRITORY] discovery_util.py (CLASS) is in utils`
- `[TERRITORY] dynamic_loader_util.py (CLASS) is in utils`
- `[TERRITORY] file_cache_util.py (VALIDATOR) is in utils`
- `[TERRITORY] main_util.py (SCRIPT) is in utils`
- `[TERRITORY] runtime_bootstrapper_util.py (CLASS) is in utils`
- `[TERRITORY] sovereign_dependency_error_util.py (EXCEPTION) is in utils`
- `[TERRITORY] sovereign_index_util.py (VALIDATOR) is in utils`
- `[TERRITORY] subatomic_hop_util.py (EXCEPTION) is in utils`
- `[TERRITORY] trait_system_util.py (TYPES) is in utils`
- `[TERRITORY] meta_learning_engine.py (VALIDATOR) is in utils`
- `[FOLDER_PURITY] meta_learning_engine.py in utils/ violates purity rules. Should be in enforcement/`
- `[TERRITORY] meta_learning_storage.py (VALIDATOR) is in utils`
- `[FOLDER_PURITY] meta_learning_storage.py in utils/ violates purity rules. Should be in enforcement/`
- `[FOLDER_PURITY] structural_healing_engine.py in utils/ violates purity rules. Should be in enforcement/`

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

