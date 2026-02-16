# Phase 1: Folder Purity Governance Hardening + Full Violation Enumeration

## Wave 1: Baseline + Discovery + Full Inventory

### Baseline Capture

```
git status --porcelain=v1: (clean)
git rev-parse HEAD: ee3af9e26d472ea0f9b9f1fed0b7a3cc2d28eaca
```

### Enforcement Definition Locations

**FOLDER_PURITY_RULES SSOT:**
- `agentic_core/L5_safety/config/structure_blueprint/classification.py:150-197`

**_enforce_folder_purity implementation:**
- `agentic_core/L5_safety/reasoning/FileClassificationAgent.py:616` (method call)

### Current FOLDER_PURITY_RULES Keys (from classification.py)

```python
FOLDER_PURITY_RULES = {
    "reasoning": [r".*Agent\.py$"],
    "validators": [r".*_validator\.py$", r".*Validator.*\.py$"],
    "config": [r".*_config\.py$", r".*_config\.yaml$", r".*_config\.json$"],
    "types": [r".*_types\.py$", r".*_protocol\.py$", r"I[A-Z].*Protocol\.py$", r".*Error\.py$", r".*Exception\.py$"],
    "utils": [r".*_util\.py$", r".*_mixin\.py$", r".*_helper\.py$", r".*_collector\.py$", r".*_monitor\.py$"],
    "scripts": [r"^[a-z][a-z0-9_]*\.py$", r".*_util\.py$"],
    "enforcement": [r".*_guardrail\.py$", r".*_enforcer\.py$", r".*_gate\.py$", r".*_manager\.py$", r".*_shield\.py$", r".*_firewall\.py$", r".*_sanitizer\.py$", r".*_governor\.py$", r".*_policy\.py$", r".*_guard\.py$", r".*_strategy\.py$", r".*Strategy\.py$", r".*Adapter\.py$", r".*Monitor\.py$", r".*Factory\.py$", r".*Gateway\.py$", r".*_adapter\.py$", r"^[a-z][a-z0-9_]*\.py$"],
    "dashboards": [r".*\.html$", r".*\.js$", r".*\.css$", r".*\.yaml$", r".*\.json$", r".*\.py$"],
}
```

**MISSING from rules:** `engines/`, `tools/`

### Inventory: engines/ Files

#### agentic_core engines (55 files)
- agentic_core/L0_routing/engines/__init__.py
- agentic_core/L1_cognition/engines/CognitiveNode.py
- agentic_core/L1_cognition/engines/cache_manager.py
- agentic_core/L1_cognition/engines/capability_analyzer.py
- agentic_core/L1_cognition/engines/codebase_mapper.py
- agentic_core/L1_cognition/engines/cognitive_engine.py
- agentic_core/L1_cognition/engines/domain_manager.py
- agentic_core/L1_cognition/engines/episodic_manager.py
- agentic_core/L1_cognition/engines/memory_embedder.py
- agentic_core/L1_cognition/engines/meta_client.py
- agentic_core/L1_cognition/engines/meta_observability.py
- agentic_core/L1_cognition/engines/perception_engine.py
- agentic_core/L1_cognition/engines/pitch_engine.py
- agentic_core/L1_cognition/engines/query_planner.py
- agentic_core/L1_cognition/engines/reasoning_cache.py
- agentic_core/L1_cognition/engines/semantic_manager.py
- agentic_core/L1_cognition/engines/strategist_bio_writer.py
- agentic_core/L2_execution/engines/action_node.py
- agentic_core/L2_execution/engines/action_node_core.py
- agentic_core/L2_execution/engines/batch_embedding_service.py
- agentic_core/L2_execution/engines/execute_command_executor.py
- agentic_core/L2_execution/engines/secure_tools_impl.py
- agentic_core/L2_execution/engines/tool_registry.py
- agentic_core/L2_execution/engines/validation_orchestrator.py
- agentic_core/L3_orchestration/engines/AgentFactory.py
- agentic_core/L3_orchestration/engines/DagRuntimeInspectorAgent.py
- agentic_core/L3_orchestration/engines/action_router.py
- agentic_core/L3_orchestration/engines/agent_gym_engine.py
- agentic_core/L3_orchestration/engines/autonomous_execution_engine.py
- agentic_core/L3_orchestration/engines/call_formatting_router.py
- agentic_core/L3_orchestration/engines/context_curator_engine.py
- agentic_core/L3_orchestration/engines/convergence_engine.py
- agentic_core/L3_orchestration/engines/coordinator_capability_orchestrator.py
- agentic_core/L3_orchestration/engines/dag_manager.py
- agentic_core/L3_orchestration/engines/decomposition_orchestrator.py
- agentic_core/L3_orchestration/engines/nervous_system.py
- agentic_core/L3_orchestration/engines/omni_context_engine.py
- agentic_core/L3_orchestration/engines/orchestrator_engine.py
- agentic_core/L3_orchestration/engines/proactive_fission_scanner.py
- agentic_core/L3_orchestration/engines/recovery_coordinator_orchestrator.py
- agentic_core/L3_orchestration/engines/recursive_orchestrator.py
- agentic_core/L3_orchestration/engines/reflex_layer_pattern.py
- agentic_core/L3_orchestration/engines/rl_coordinator_orchestrator.py
- agentic_core/L3_orchestration/engines/sovereign_mcp_marketplace.py
- agentic_core/L3_orchestration/engines/sovereign_mcp_router.py
- agentic_core/L3_orchestration/engines/sovereign_rag_orchestrator.py
- agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py
- agentic_core/L3_orchestration/engines/sub_atomic_engine_impl.py
- agentic_core/L6_observability/engines/PerformanceAnalystAgentSimple.py
- agentic_core/L6_observability/engines/SovereignHealthMonitor.py
- agentic_core/L6_observability/engines/TieredVigilanceEmitter.py

#### apps_lic engines (52 files)
- apps_lic/engines/ArchitectureVisualizerAgent.py
- apps_lic/engines/CampaignBalanceAgent.py
- apps_lic/engines/CulturalDecoderAgent.py
- apps_lic/engines/DeliverabilityAgent.py
- apps_lic/engines/DispatchOutreachToolsAgent.py
- apps_lic/engines/ExecutiveStrategyAgent.py
- apps_lic/engines/GovernanceShieldAgent.py
- apps_lic/engines/HOP3SenderGroundingAgent.py
- apps_lic/engines/HOP5GenerationAgent.py
- apps_lic/engines/HOP7GateDecisionAgent.py
- apps_lic/engines/HOP8QAReportAgent.py
- apps_lic/engines/HOP9IntegrationAgent.py
- apps_lic/engines/HOPPipelineExecutor.py
- apps_lic/engines/Hop1ProfileAnalysisAgent.py
- apps_lic/engines/Hop2ResearchAgent.py
- apps_lic/engines/Hop4RoutingAgent.py
- apps_lic/engines/Hop6ValidationAgent.py
- apps_lic/engines/IntelligenceLibrarianAgent.py
- apps_lic/engines/LICValidationExecutor.py
- apps_lic/engines/LeadQualityAgent.py
- apps_lic/engines/LicCodeInterpreter.py
- apps_lic/engines/LicHealingOrchestrator.py
- apps_lic/engines/LicReflectionAgent.py
- apps_lic/engines/LicS2SupervisorAgent.py
- apps_lic/engines/LicTemplateOptimizerAgent.py
- apps_lic/engines/LogReaderAgent.py
- apps_lic/engines/MessageArchitectAgent.py
- apps_lic/engines/MessageComplianceAgent.py
- apps_lic/engines/MessageDiversityValidator.py
- apps_lic/engines/OutreachCapabilityMonitorAgent.py
- apps_lic/engines/OutreachLearningAgent.py
- apps_lic/engines/OutreachMessageAgent.py
- apps_lic/engines/OutreachProactiveAgent.py
- apps_lic/engines/OutreachSignalRouterAgent.py
- apps_lic/engines/OutreachTestPilotAgent.py
- apps_lic/engines/OutreachValidationExecutorAgent.py
- apps_lic/engines/PIISanitizerSpecialistAgent_util.py (VIOLATION: _util suffix in engines/)
- apps_lic/engines/PersonaPlannerValidator.py (VIOLATION: Validator suffix in engines/)
- apps_lic/engines/PreMortemAgent.py
- apps_lic/engines/QAConductorAgent.py
- apps_lic/engines/TwoPhaseDeduplicationAgent.py
- apps_lic/engines/ValidatorAgent.py
- apps_lic/engines/check_schema_policy_validator.py (VIOLATION: _validator suffix in engines/)
- apps_lic/engines/code_quality_guardrail_types.py (VIOLATION: _types suffix in engines/)

### Inventory: tools/ Files

#### agentic_core tools (14 files)
- agentic_core/L2_execution/tools/content_relevance_impl.py
- agentic_core/L2_execution/tools/data_serializer_util.py (VIOLATION: _util suffix in tools/)
- agentic_core/L2_execution/tools/figma_mcp_client.py
- agentic_core/L2_execution/tools/file_io_impl.py
- agentic_core/L2_execution/tools/gemini_spy_util.py (VIOLATION: _util suffix in tools/)
- agentic_core/L2_execution/tools/git_ops_impl.py
- agentic_core/L2_execution/tools/job_analyzer_impl.py
- agentic_core/L2_execution/tools/payload_formatter_util.py (VIOLATION: _util suffix in tools/)
- agentic_core/L2_execution/tools/text_similarity_util.py (VIOLATION: _util suffix in tools/)
- agentic_core/L2_execution/tools/time_utils_impl.py
- agentic_core/L2_execution/tools/tool_chain_executor.py
- agentic_core/L2_execution/tools/tool_verifier_impl.py
- agentic_core/L2_execution/tools/web_search_client.py

#### apps_lic tools (47 files)
- PascalCase tools (legitimate): AdjustToneWeights.py, AggregateCampaignState.py, etc.
- snake_case tools (legitimate): analyze_duplicates_detailed.py, call_personalization_api.py, etc.

#### apps_rg tools (32 files)
- PascalCase tools (legitimate): AdjustSectionWeights.py, AssessContentRelevance.py, etc.
- apps_rg/tools/ConfidencemetricsStrategy.py (VIOLATION: Strategy suffix in tools/)
- apps_rg/tools/text_util.py (VIOLATION: _util suffix in tools/)

### Violation Summary Table

| Folder | Path | Filename | Violation | Target Folder |
|--------|------|----------|-----------|---------------|
| engines | apps_lic/engines/ | PIISanitizerSpecialistAgent_util.py | _util suffix | utils |
| engines | apps_lic/engines/ | PersonaPlannerValidator.py | Validator suffix | validators |
| engines | apps_lic/engines/ | check_schema_policy_validator.py | _validator suffix | validators |
| engines | apps_lic/engines/ | code_quality_guardrail_types.py | _types suffix | types |
| tools | agentic_core/L2_execution/tools/ | data_serializer_util.py | _util suffix | utils |
| tools | agentic_core/L2_execution/tools/ | gemini_spy_util.py | _util suffix | utils |
| tools | agentic_core/L2_execution/tools/ | payload_formatter_util.py | _util suffix | utils |
| tools | agentic_core/L2_execution/tools/ | text_similarity_util.py | _util suffix | utils |
| tools | apps_rg/tools/ | ConfidencemetricsStrategy.py | Strategy suffix | reasoning |
| tools | apps_rg/tools/ | text_util.py | _util suffix | utils |
| engines | agentic_core/L3_orchestration/engines/ | DagRuntimeInspectorAgent.py | Agent suffix | reasoning |
| engines | agentic_core/L6_observability/engines/ | PerformanceAnalystAgentSimple.py | Agent suffix | reasoning |

---

## Wave 2: Extend Ruleset (engines/ + tools/)

(To be appended after Wave 2 execution)

---

## Wave 3: Architecture Tests

(To be appended after Wave 3 execution)
