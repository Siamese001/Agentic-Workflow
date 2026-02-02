#!/usr/bin/env python3
"""Update imports for Phase 1.3 renamed validators"""
import re
from pathlib import Path

# Phase 1.3 renames - old name to new name mapping
renames = {
    "security_security_controls": "security_security_controls_validator",
    "DeliverabilityDeterministic": "deliverability_deterministic_validator",
    "GovernanceShieldDeterministic": "governance_shield_deterministic_validator",
    "HOPValidationDeterministic": "hop_validation_deterministic_validator",
    "IntelligenceLibrarianDeterministic": "intelligence_librarian_deterministic_validator",
    "LeadQualityDeterministic": "lead_quality_deterministic_validator",
    "check_from_utils_duplicates": "check_from_utils_duplicates_validator",
    "check_sovereign_base": "check_sovereign_base_validator",
    "comprehensive_archive_check": "comprehensive_archive_check_validator",
    "validate_dashboard_changes": "validate_dashboard_changes_validator",
    "verify_all_checkpoint_files": "verify_all_checkpoint_files_validator",
    "verify_base_agent_names": "verify_base_agent_names_validator",
    "verify_health_calculation": "verify_health_calculation_validator",
    "verify_heal_invocation": "verify_heal_invocation_validator",
    "verify_l2_fix": "verify_l2_fix_validator",
    "verify_row_order": "verify_row_order_validator",
    "verify_territory_counts": "verify_territory_counts_validator",
    "ASTValidatorAgent": "ast_validator_agent_validator",
    "AutonomousPromptEvolutionAgent": "autonomous_prompt_evolution_agent_validator",
    "DarkReasoningVisitor": "dark_reasoning_visitor_validator",
    "semantic_gatekeeper": "semantic_gatekeeper_validator",
    "SpiffeManager": "spiffe_manager_validator",
    "ExecuteCommandArgs": "execute_command_args_validator",
    "ToolsUseATool": "tools_use_a_tool_validator",
    "TelepathyInterface": "telepathy_interface_validator",
    "CachedStateLedgerAgent": "cached_state_ledger_agent_validator",
    "SovereignSemanticCacheAgent": "sovereign_semantic_cache_agent_validator",
    "CognitiveBatchProcessor": "cognitive_batch_processor_validator",
    "AirlockProtocol": "airlock_protocol_validator",
    "ConstitutionalOverseer": "constitutional_overseer_validator",
    "SafetyGuardrail": "safety_guardrail_validator",
    "SafetyInspectorAgent": "safety_inspector_agent_validator",
    "AdversarialProbeAgent": "adversarial_probe_agent_validator",
    "BoundaryTestingAgent": "boundary_testing_agent_validator",
    "ChaosEngineeringAgent": "chaos_engineering_agent_validator",
    "GravityVisitor": "gravity_visitor_validator",
    "AutonomicMonitorAgent": "autonomic_monitor_agent_validator",
    "GovernanceHub": "governance_hub_validator",
    "SovereignPromptRenderer": "sovereign_prompt_renderer_validator",
    "CostGovernor": "cost_governor_validator",
    "BudgetProfile": "budget_profile_validator",
    "ConsensusVerdict": "consensus_verdict_validator",
    "Hypothesis": "hypothesis_validator",
    "RetryPolicy": "retry_policy_validator",
    "SafetyProfile": "safety_profile_validator",
    "SimScenario": "sim_scenario_validator",
    "SovereignBaseModel": "sovereign_base_model_validator",
    "ValidationResult": "validation_result_validator",
    "MemoryItem": "memory_item_validator",
    "canonical_truth": "canonical_truth_validator",
    "FileCache": "file_cache_validator",
    "file_utils": "file_utils_validator",
    "SovereignIndex": "sovereign_index_validator",
    "SovereignScanner": "sovereign_scanner_validator",
    "ssot_discovery": "ssot_discovery_validator",
    "check_schema_policy": "check_schema_policy_validator",
    "HOP4RoutingAgent": "hop4_routing_agent_validator",
    "HOP6ValidationAgent": "hop6_validation_agent_validator",
    "MessageDiversityValidatorAgent": "message_diversity_validator_agent_validator",
    "OutreachValidationExecutorAgent": "outreach_validation_executor_agent_validator",
    "PersonaPlanner": "persona_planner_validator",
    "ValidatorAgent": "validator_agent_validator",
    "LICAgentBaseAgent": "lic_agent_base_agent_validator",
    "safety_validate_ethical_standards": "safety_validate_ethical_standards_validator",
    "safety_validate_outreach_constraints": "safety_validate_outreach_constraints_validator",
    "HallucinationDetector": "hallucination_detector_validator",
    "ValidationGate": "validation_gate_validator",
    "Cache": "cache_validator",
    "CacheEntry": "cache_entry_validator",
    "CheckpointIntegrityError": "checkpoint_integrity_error_validator",
    "check_depth": "check_depth_validator",
    "EvidenceRanker": "evidence_ranker_validator",
    "FactLedger": "fact_ledger_validator",
    "guard_ddd_alignment": "guard_ddd_alignment_validator",
    "KNodeScanner": "k_node_scanner_validator",
    "KnowledgeResult": "knowledge_result_validator",
    "resume_prompts": "resume_prompts_validator",
    "SignalQualityPipeline": "signal_quality_pipeline_validator",
    "TalentSignalEnhancer": "talent_signal_enhancer_validator",
    "Validation": "validation_validator",
    "ValidationContextManager": "validation_context_manager_validator",
    "io_operations": "io_operations_validator",
    "json_parser": "json_parser_validator",
    "text_processing": "text_processing_validator",
    "test_dict": "test_dict_validator",
    "test_schemas_test_memory_schema_validation": "test_schemas_test_memory_schema_validation_validator",
}

def update_file(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        for old, new in renames.items():
            # Match import patterns
            content = re.sub(
                rf'(from\s+\S+\.){old}(\s+import)',
                rf'\g<1>{new}\2',
                content
            )
            content = re.sub(
                rf'(import\s+\S+\.){old}(\s|$)',
                rf'\g<1>{new}\2',
                content
            )
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except:
        return False

updated = 0
for py in Path('.').rglob('*.py'):
    if 'phase1' in py.name or 'update_' in py.name:
        continue
    if update_file(py):
        updated += 1
        print(f"✓ {py}")

print(f"\n✓ Updated {updated} files")
