================================================================================
ARCHIVE RESTORATION FINDINGS & RECOMMENDATIONS
================================================================================

Analysis Date: 2026-01-20
Total Files Analyzed: 463
Current Codebase: 232 agents, 1343 classes

================================================================================
ARCHIVE SUMMARY
================================================================================

  legacy_agents:
    Files: 54, Agents: 53, High-Unique: 29

  Reachout Engine Archive:
    Files: 110, Agents: 138, High-Unique: 19

  consolidated_agents:
    Files: 24, Agents: 22, High-Unique: 13

  legacy_orchestrators:
    Files: 20, Agents: 19, High-Unique: 12

  legacy_validators:
    Files: 18, Agents: 19, High-Unique: 12

  deprecated_agents:
    Files: 21, Agents: 20, High-Unique: 6

  apps_lic:
    Files: 104, Agents: 0, High-Unique: 0

  apps_rg:
    Files: 104, Agents: 2, High-Unique: 0

  apps_shared:
    Files: 48, Agents: 0, High-Unique: 0

================================================================================
HIGH PRIORITY RESTORATIONS (Unique Agents)
================================================================================

Total: 54 files

  [100%] k5_cta_agent.py
    Archive: Reachout Engine Archive
    Domain: SHARED
    Agents: ['CTAAgent']
    RESTORE TO: apps_shared/base_agents/

  [100%] bullet.py
    Archive: Reachout Engine Archive
    Domain: RESUME
    Agents: ['BulletEntityExtractionAgent', 'BulletMetricsEnrichmentAgent', 'BulletNarrativeSynthesisAgent', 'BulletEvidenceLinkerAgent', 'BulletConfidenceScoringAgent', 'BulletCoordinatorAgent', 'BulletProvenanceAuditorAgent', 'AsyncBulletGeneratorAgent', 'AsyncBulletCritiqueAgent']
    Purpose: Extracts key entities from bullet text....
    RESTORE TO: apps_rg/engines/

  [100%] drafting.py
    Archive: Reachout Engine Archive
    Domain: RESUME
    Agents: ['StructureLeadAgent', 'NarrativeStylistAgent', 'ComplianceEditorAgent', 'EvidenceLiaisonAgent', 'CritiqueRoutingPanel', 'DraftingGuildCoordinator']
    Purpose: Produces the structural outline for the draft....
    RESTORE TO: apps_rg/engines/

  [100%] hil.py
    Archive: Reachout Engine Archive
    Domain: SHARED
    Agents: ['VirtualReviewerPersonaAgent', 'VirtualReviewerCouncilAgent', 'HILFeedbackSummarizerAgent', 'HILReconciliationAgent', 'HILAmbiguityDetectorAgent', 'HILFeedbackRouterAgent']
    Purpose: Persona-specialized reviewer that interprets human feedback....
    RESTORE TO: apps_shared/base_agents/

  [100%] prompting.py
    Archive: Reachout Engine Archive
    Domain: SHARED
    Agents: ['PromptEngineerAgent']
    Purpose: LLM-driven prompt engineering that adapts to task complexity....
    RESTORE TO: apps_shared/base_agents/

  [100%] rag.py
    Archive: Reachout Engine Archive
    Domain: SHARED
    Agents: ['RAG_SearchAgent']
    Purpose: Agentic RAG conductor that orchestrates resume search tooling....
    RESTORE TO: apps_shared/base_agents/

  [100%] strategy.py
    Archive: Reachout Engine Archive
    Domain: SHARED
    Agents: ['QueryComplexityClassifier', 'ToTStrategistAgent']
    Purpose: Classifies query complexity for dynamic routing....
    RESTORE TO: apps_shared/base_agents/

  [100%] validation_LIC.py
    Archive: Reachout Engine Archive
    Domain: OUTREACH
    Agents: ['HOP6_ValidationAgent', 'HOP8_QAReportAgent']
    Purpose: v13.0: HOP-6 Validation Agent - Rule-based validation from config.

CRITICAL ENH...
    RESTORE TO: apps_lic/engines/

  [100%] DeadlockDetectorAgent.py
    Archive: legacy_agents
    Domain: SHARED
    Agents: ['DeadlockDetectorAgent']
    Purpose: Detects potential deadlocks in asyncio tasks.

Monitors:
- Task execution time
-...
    RESTORE TO: apps_shared/base_agents/

  [100%] ASCIIEnforcerAgent.py
    Archive: legacy_agents
    Domain: SHARED
    Agents: ['ASCIIEnforcerAgent']
    Purpose: Enforce ASCII-only characters for LinkedIn compatibility
GAP 1.10 from v10.22...
    RESTORE TO: apps_shared/base_agents/

  [100%] CodeSSOTEnforcerAgent.py
    Archive: legacy_agents
    Domain: INFRASTRUCTURE
    Agents: ['CodeSSOTEnforcerAgent']
    Purpose: Ultra high-signal code-level SSOT enforcer using AST analysis.

Enforces that co...
    RESTORE TO: apps_shared/base_agents/

  [100%] DocEnforcerAgent.py
    Archive: legacy_agents
    Domain: SHARED
    Agents: ['DocEnforcerAgent']
    Purpose: ROLE: Documentation Surgeon....
    RESTORE TO: apps_shared/base_agents/

  [100%] HierarchyEnforcerAgent.py
    Archive: legacy_agents
    Domain: SHARED
    Agents: ['HierarchyEnforcerAgent']
    Purpose: Enforces the canonical L4 hierarchy across agentic_core.
Drills down from L2 -> ...
    RESTORE TO: apps_shared/base_agents/

  [100%] LegacyNamingAgent.py
    Archive: legacy_agents
    Domain: SHARED
    Agents: ['_LegacyNamingAgent']
    Purpose: KEYS: 47 (Naming Conventions)
ROLE: Enforces Snake_Case/PascalCase....
    RESTORE TO: apps_shared/base_agents/

  [100%] LegacySafetyInspectorAgent.py
    Archive: legacy_agents
    Domain: SHARED
    Agents: ['_LegacySafetyInspectorAgent']
    Purpose: KEYS: 0 (Secrets), 1 (TODO/FIXME), 2 (Print), 3 (Debugger), 4 (Empty Except), 5 ...
    RESTORE TO: apps_shared/base_agents/

  [100%] NamingEnforcerAgent.py
    Archive: legacy_agents
    Domain: SHARED
    Agents: ['NamingEnforcerAgent']
    Purpose: ROLE: Semantic Naming Guardian....
    RESTORE TO: apps_shared/base_agents/

  [100%] PythonFileSovereigntyEnforcerAgent.py
    Archive: legacy_agents
    Domain: SHARED
    Agents: ['PythonFileSovereigntyEnforcerAgent']
    Purpose: L5 Safety agent - enforces dedicated ClassNameAgent.py file naming standard.

Te...
    RESTORE TO: apps_shared/base_agents/

  [100%] TypeEnforcerAgent.py
    Archive: legacy_agents
    Domain: SHARED
    Agents: ['TypeEnforcerAgent']
    Purpose: ROLE: Type Guardian. Enforces PEP 484....
    RESTORE TO: apps_shared/base_agents/

  [100%] BlueprintHierarchyHealerAgent.py
    Archive: legacy_agents
    Domain: SHARED
    Agents: ['_BlueprintHierarchyHealerAgent']
    Purpose: [L3 AGENT] The Structural Surgeon.
Directive: Physically relocate files to satis...
    RESTORE TO: apps_shared/base_agents/

  [100%] BlueprintHierarchyHealerAgent_1.py
    Archive: legacy_agents
    Domain: SHARED
    Agents: ['_BlueprintHierarchyHealerAgent']
    Purpose: [L3 AGENT] The Structural Surgeon.
Directive: Physically relocate files to satis...
    RESTORE TO: apps_shared/base_agents/

================================================================================
MEDIUM PRIORITY RESTORATIONS (Unique Utilities/Models)
================================================================================

Total: 77 files

  [79%] workflow.py
    Archive: Reachout Engine Archive
    Domain: OUTREACH
    Entities: ['ProfileAnalysisAgent', 'RoutingAgent', 'ScaffoldAgent', 'SelfConsistencySynthesizer', 'GenerationOrchestrator']
    RESTORE TO: apps_lic/engines/utils/

  [79%] workflow_LIC v11_10.py
    Archive: Reachout Engine Archive
    Domain: OUTREACH
    Entities: ['ProfileAnalysisAgent', 'RoutingAgent', 'ScaffoldAgent', 'SelfConsistencySynthesizer', 'GenerationOrchestrator']
    RESTORE TO: apps_lic/engines/utils/

  [78%] TypeHintEnforcementAgent.py
    Archive: consolidated_agents
    Domain: SHARED
    Entities: ['TypeHintEnforcementAgent', 'TypeHintEnforcementAgent']
    RESTORE TO: apps_shared/common_utils/

  [77%] run_learning_v10_7.py
    Archive: Reachout Engine Archive
    Domain: SHARED
    Entities: ['HotReloadRuleManager', 'LogReaderAgent', 'AsyncLogSummarizerAgent', 'AsyncPatternFinderAgent', 'AsyncHypothesisGeneratorAgent']
    RESTORE TO: apps_shared/common_utils/

  [75%] workflow_LIC_v12.py
    Archive: Reachout Engine Archive
    Domain: OUTREACH
    Entities: ['ProfileAnalysisAgent', 'RoutingAgent', 'ScaffoldAgent', 'ConstraintFeasibilityChecker', 'QAAgent']
    RESTORE TO: apps_lic/engines/utils/

  [75%] StructuralHealerAgent.py
    Archive: legacy_agents
    Domain: INFRASTRUCTURE
    Entities: ['ImportUpdater', 'StructuralHealerAgent']
    RESTORE TO: apps_shared/common_utils/

  [75%] CanonValidatorAgent.py
    Archive: legacy_validators
    Domain: INFRASTRUCTURE
    Entities: ['CanonEntry', 'CanonValidatorAgent']
    RESTORE TO: apps_shared/common_utils/

  [75%] ContentCleanlinessValidatorAgent.py
    Archive: legacy_validators
    Domain: INFRASTRUCTURE
    Entities: ['ContentCleanlinessValidatorAgent', 'ErrorCodeRegistry', 'ConstraintFeasibilityChecker', 'ContentCleanlinessValidatorAgent']
    RESTORE TO: apps_shared/common_utils/

  [71%] rag.py
    Archive: Reachout Engine Archive
    Domain: OUTREACH
    Entities: ['SignalQualityScorer', 'ClaimConfidenceScorer', 'RAGReflexionSystem', 'RecipientAgent', 'OrganizationAgent']
    RESTORE TO: apps_lic/engines/utils/

  [71%] rag_LIC v11_10.py
    Archive: Reachout Engine Archive
    Domain: OUTREACH
    Entities: ['SignalQualityScorer', 'ClaimConfidenceScorer', 'RAGReflexionSystem', 'RecipientAgent', 'OrganizationAgent']
    RESTORE TO: apps_lic/engines/utils/

  [71%] rag_LIC.py
    Archive: Reachout Engine Archive
    Domain: OUTREACH
    Entities: ['SignalQualityScorer', 'ClaimConfidenceScorer', 'RAGReflexionSystem', 'RecipientAgent', 'OrganizationAgent']
    RESTORE TO: apps_lic/engines/utils/

  [67%] workflow_LIC.py
    Archive: Reachout Engine Archive
    Domain: OUTREACH
    Entities: ['HOP2_ResearchAgent', 'HOP5_GenerationAgent', 'HOP6_ValidationAgent', 'HOP8_QAReportAgent', 'HOPOrchestrator']
    RESTORE TO: apps_lic/engines/utils/

  [67%] toggles.py
    Archive: Reachout Engine Archive
    Domain: OUTREACH
    Entities: ['ReasoningToggles']
    RESTORE TO: apps_lic/engines/utils/

  [67%] models.py
    Archive: Reachout Engine Archive
    Domain: OUTREACH
    Entities: ['SpecialistDraftPacket', 'EvidenceClarificationRecord', 'EvidenceBriefRecord', 'EvidenceLiaisonPacket', 'CritiqueFindingRecord']
    RESTORE TO: apps_lic/engines/utils/

  [67%] MemoryLeakDetectorAgent.py
    Archive: legacy_agents
    Domain: SHARED
    Entities: ['MemoryLeakDetectorAgent', 'DeadlockAnalyzer', 'RaceAnalyzer']
    RESTORE TO: apps_shared/common_utils/

================================================================================
REVIEW NEEDED (Partial Overlap)
================================================================================

Total: 182 files
These files have some unique content but significant overlap with current codebase.

  [49%] agent_tools_v10_7.py
    Archive: Reachout Engine Archive
    Entities: ['resolve_mcp_client', 'DraftingLLMTool', 'DraftingStrategistTool', 'DraftingRedTeamTool', 'DraftingRefinerTool']

  [48%] lic_cta_patterns.py
    Archive: apps_lic
    Entities: ['RecipientArchetype', 'CTAStyle', 'CTAPattern', 'CTATemplate', 'DateWindowConfig']

  [48%] lic_routing_rules.py
    Archive: apps_lic
    Entities: ['MessageRoute', 'RecipientArchetype', 'SignatureFormat', 'CTAFormat', 'RouteConditions']

  [47%] UnifiedOrchestratorAgent.py
    Archive: legacy_orchestrators
    Entities: ['SecurityLevel', 'AnalysisType', 'RefactorType', 'PhaseType', 'SecurityIssue']

  [47%] lic_vector_memory.py
    Archive: apps_lic
    Entities: ['VectorDocument', 'QueryResult', 'MemoryStats', 'LICVectorMemory', 'MockVectorMemory']

  [47%] lic_archetypes.py
    Archive: apps_lic
    Entities: ['RecipientArchetype', 'SubjectLineBrief', 'MessageBodyBrief', 'CTABrief', 'CreativeBrief']

  [47%] lic_code_interpreter.py
    Archive: apps_lic
    Entities: ['ScoredCandidate', 'ScoringCriteria', 'SimilarityResult', 'KeywordExtractionResult', 'LICCodeInterpreter']

  [47%] rg_creative_brief.py
    Archive: apps_rg
    Entities: ['VoiceType', 'ProvenanceStrategy', 'WordCountConstraint', 'CharCountConstraint', 'StructureConstraint']

  [47%] SelfRecoveringOrchestratorAgent.py
    Archive: legacy_orchestrators
    Entities: ['RecoveryStrategy', 'NodeFailurePattern', 'WorkflowMutation', 'SelfRecoveringOrchestratorAgent', 'create_self_recovering_orchestrator']

  [46%] Phase4OrchestratorAgent.py
    Archive: legacy_orchestrators
    Entities: ['MutationMode', 'FileBackup', 'MutationResult', 'RepairProposal', 'GitOpsManager']

================================================================================
SKIP (Already Exists or Low Quality)
================================================================================

Already in codebase: 150 files
Syntax errors/low quality: 0 files

================================================================================
EXECUTIVE SUMMARY
================================================================================

    HIGH PRIORITY (restore immediately):     54 files
    MEDIUM PRIORITY (restore as needed):     77 files
    REVIEW NEEDED (manual inspection):       182 files
    SKIP (exists or low quality):            150 files
    
    TOTAL RESTORATION CANDIDATES:            131 files
    

================================================================================
TOP 10 RESTORATION COMMANDS
================================================================================

cp "archives\Reachout Engine Archive\Agentic-LIC\src\lic_agentic\agents\k5_cta_agent.py" "apps_shared/k5_cta_agent.py"

cp "archives\Reachout Engine Archive\Agentic-LIC\stacks_v10_7\bullet.py" "apps_rg/engines/bullet.py"

cp "archives\Reachout Engine Archive\Agentic-LIC\stacks_v10_7\drafting.py" "apps_rg/engines/drafting.py"

cp "archives\Reachout Engine Archive\Agentic-LIC\stacks_v10_7\hil.py" "apps_shared/hil.py"

cp "archives\Reachout Engine Archive\Agentic-LIC\stacks_v10_7\prompting.py" "apps_shared/prompting.py"

cp "archives\Reachout Engine Archive\Agentic-LIC\stacks_v10_7\rag.py" "apps_shared/rag.py"

cp "archives\Reachout Engine Archive\Agentic-LIC\stacks_v10_7\strategy.py" "apps_shared/strategy.py"

cp "archives\Reachout Engine Archive\deprecated in v13\validation_LIC.py" "apps_lic/engines/validation_LIC.py"

cp "archives\legacy_agents\legacy_detectors\DeadlockDetectorAgent.py" "apps_shared/DeadlockDetectorAgent.py"

cp "archives\legacy_agents\legacy_enforcers\ASCIIEnforcerAgent.py" "apps_shared/ASCIIEnforcerAgent.py"