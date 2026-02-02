#!/usr/bin/env python3
"""Update imports for Phase 1.4 renamed CONFIG files"""
import re
from pathlib import Path

renames = {
    "config_mixin": "config_mixin_config",
    "feature_flags": "feature_flags_config",
    "settings": "settings_config",
    "SovereignConfigManager": "sovereign_config_manager_config",
    "config_impl": "config_impl_config",
    "BaseEntity": "base_entity_config",
    "CsvDocumentLoader": "csv_document_loader_config",
    "PDFDocumentLoader": "pdf_document_loader_config",
    "TextDocumentLoader": "text_document_loader_config",
    "dashboard_live_server": "dashboard_live_server_config",
    "dashboard_ssot_definitions": "dashboard_ssot_definitions_config",
    "territory_ssot_definitions": "territory_ssot_definitions_config",
    "verify_manifest_cleanliness": "verify_manifest_cleanliness_config",
    "ManifestGuardian": "manifest_guardian_config",
    "TransformOperation": "transform_operation_config",
    "RagConfig": "rag_config_config",
    "ProviderType": "provider_type_config",
    "HybridRetriever": "hybrid_retriever_config",
    "PeerIntelligenceAuditorAgent": "peer_intelligence_auditor_agent_config",
    "StrategistBioWriter": "strategist_bio_writer_config",
    "DAGMutatorAgent": "dag_mutator_agent_config",
    "SemanticCacheManager": "semantic_cache_manager_config",
    "ArchivalGatekeeper": "archival_gatekeeper_config",
    "InputValidationGuardrailAgent": "input_validation_guardrail_agent_config",
    "ConfigurationSecurityGuardrailAgent": "configuration_security_guardrail_agent_config",
    "ContractStageAgent": "contract_stage_agent_config",
    "InputValidator": "input_validator_config",
    "ReflectionEngine": "reflection_engine_config",
    "structure_blueprint": "structure_blueprint_config",
    "SharedInfrastructure": "shared_infrastructure_config",
    "AnomalyReport": "anomaly_report_config",
    "InjectionType": "injection_type_config",
    "PlaceholderDetectorAgent": "placeholder_detector_agent_config",
    "ArchetypeIndicator": "archetype_indicator_config",
    "SovereignConfigLoader": "sovereign_config_loader_config",
    "ClerkExtractor": "clerk_extractor_config",
    "void_compliance": "void_compliance_config",
    "FeedbackCategory": "feedback_category_config",
    "find_misnamed_agents": "find_misnamed_agents_config",
    "GraphRAGFusion": "graph_rag_fusion_config",
    "InputGuardrail": "input_guardrail_config",
    "MetricAugmenter": "metric_augmenter_config",
    "MetricConfig": "metric_config_config",
    "NodeNegotiator": "node_negotiator_config",
    "PromptEnhancer": "prompt_enhancer_config",
    "PromptRegistry": "prompt_registry_config",
    "refine_config_ranking": "refine_config_ranking_config",
    "RelevanceScorer": "relevance_scorer_config",
    "RoutingTier": "routing_tier_config",
    "SDKCategory": "sdk_category_config",
    "Settings": "settings_config",
    "SignalWeighter": "signal_weighter_config",
    "titanium_search_tool": "titanium_search_tool_config",
    "TokenBudget": "token_budget_config",
    "config_loader": "config_loader_config",
    "environment": "environment_config",
    "security_utils": "security_utils_config",
}

def update_file(fp):
    try:
        content = fp.read_text(encoding='utf-8')
        orig = content
        for old, new in renames.items():
            content = re.sub(rf'(from\s+\S+\.){old}(\s+import)', rf'\g<1>{new}\2', content)
            content = re.sub(rf'(import\s+\S+\.){old}(\s|$)', rf'\g<1>{new}\2', content)
        if content != orig:
            fp.write_text(content, encoding='utf-8')
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
