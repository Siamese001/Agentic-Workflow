---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\agent_archetype_map.md'
original_relative_path: 'agent_archetype_map.md'
source_sha256: 0ff923e8bec5b860c3685dbbadc5b30bec305776b32bf9ba441179656f6bbb85
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Agent Archetype Classification Map

**Total agents**: 190

## Archetype Distribution

| Archetype | Count | Forced Consolidation |
|-----------|-------|---------------------|
| ReasoningAgent | 107 | no |
| WrapperProxyAgent | 22 | no |
| PolicyGateAgent | 22 | no |
| ObservabilityAgent | 12 | YES |
| StageAgent | 11 | YES |
| ValidationAgent | 6 | YES |
| OrchestratorAgent | 5 | YES |
| InspectionAgent | 3 | no |
| ToolRunnerAgent | 2 | no |

## Forced Consolidation Targets

### ObservabilityAgent (12 agents)
- Dominant base signature: `AtomicExecutionMixin+SovereignBaseAgent+SubatomicTestingMixin`
- Signature ratio: 0.5
- **FORCED**: No waivers allowed

| Agent | Layer | Domain LOC | BP Ratio | Bases |
|-------|-------|-----------|----------|-------|
| DeadlockDetectorAgent | L6 | 31 | 0.17 | AtomicExecutionMixin+SovereignBaseAgent |
| StrategicObservationAgent | L6 | 44 | 0.29 | AtomicExecutionMixin+SovereignBaseAgent |
| RuntimeTelemetryAgent | L6 | 54 | 0.32 | AtomicExecutionMixin+SubatomicTestingMixin+SovereignBaseAgent |
| DebateSynthesisAgent | L6 | 75 | 0.35 | AtomicExecutionMixin+SovereignBaseAgent |
| MetricsWitnessAgent | L6 | 121 | 0.33 | SubatomicTestingMixin+L0MaintenanceBaseAgent+AutonomyMixin+AdaptiveExecutionMixin+SelfDiagnosisMixin |
| ReportingAgent | L6 | 125 | 0.35 | SovereignBaseAgent |
| AutonomicMonitorAgent | L6 | 152 | 0.21 | AtomicExecutionMixin+SubatomicTestingMixin+SovereignBaseAgent |
| TelemetryAgent | L6 | 153 | 0.27 | AtomicExecutionMixin+SubatomicTestingMixin+SovereignBaseAgent |
| PerformanceAnalystAgent | L6 | 161 | 0.15 | AtomicExecutionMixin+SubatomicTestingMixin+SovereignBaseAgent |
| SovereignObservabilityAgent | L6 | 162 | 0.22 | SovereignBaseAgent+SubatomicTestingMixin+MCPHardenedMixin+RedisCacheMixin+event_emission_mixin+ContextPropagationMixin |
| MetricsAgent | L6 | 183 | 0.32 | AtomicExecutionMixin+SubatomicTestingMixin+SovereignBaseAgent |
| TracingAgent | L6 | 261 | 0.17 | AtomicExecutionMixin+SubatomicTestingMixin+SovereignBaseAgent |

### StageAgent (11 agents)
- Dominant base signature: `HOPStageCapability+LICAgentBase+SubatomicTestingMixin`
- Signature ratio: 0.64
- **FORCED**: No waivers allowed

| Agent | Layer | Domain LOC | BP Ratio | Bases |
|-------|-------|-----------|----------|-------|
| TrackObservabilityCostAgent | L6 | 11 | 0.57 | AtomicExecutionMixin+SubatomicTestingMixin+SovereignBaseAgent |
| LeadQualityAgent | apps_lic | 40 | 0.28 | SubatomicTestingMixin+LICAgentBase |
| HOP7GateDecisionAgent | apps_lic | 51 | 0.04 | HOPStageCapability+SubatomicTestingMixin+LICAgentBase |
| HOP9IntegrationAgent | apps_lic | 70 | 0.04 | HOPStageCapability+SubatomicTestingMixin+LICAgentBase |
| HOP4RoutingAgent | apps_lic | 98 | 0.03 | HOPStageCapability+SubatomicTestingMixin+LICAgentBase |
| HOP8QAReportAgent | apps_lic | 109 | 0.03 | HOPStageCapability+SubatomicTestingMixin+LICAgentBase |
| HOP6ValidationAgent | apps_lic | 111 | 0.03 | HOPStageCapability+SubatomicTestingMixin+LICAgentBase |
| HOP3SenderGroundingAgent | apps_lic | 121 | 0.10 | HOPStageCapability+SubatomicTestingMixin+LICAgentBase |
| HOP1ProfileAnalysisAgent | apps_lic | 217 | 0.13 | HOPStageCapability+LICAgentBase |
| HOP2ResearchAgent | apps_lic | 300 | 0.14 | HOPStageCapability+LICAgentBase |
| HOP5GenerationAgent | apps_lic | 353 | 0.01 | HOPStageCapability+SubatomicTestingMixin+LICAgentBase |

### ValidationAgent (6 agents)
- Dominant base signature: `RGAgentBase+RGValidationCapability`
- Signature ratio: 0.67
- **FORCED**: No waivers allowed

| Agent | Layer | Domain LOC | BP Ratio | Bases |
|-------|-------|-----------|----------|-------|
| DeliverabilityAgent | apps_lic | 34 | 0.35 | LICEngineValidationCapability+SubatomicTestingMixin+LICAgentBase |
| CampaignBalanceAgent | apps_lic | 37 | 0.39 | LICEngineValidationCapability+SubatomicTestingMixin+LICAgentBase |
| SectionBalanceAgent | apps_rg | 41 | 0.13 | RGValidationCapability+RGAgentBase |
| BrandComplianceAgent | apps_rg | 43 | 0.27 | RGValidationCapability+RGAgentBase |
| ATSCompatibilityAgent | apps_rg | 72 | 0.19 | RGValidationCapability+RGAgentBase |
| FactCheckAgent | apps_rg | 90 | 0.09 | RGValidationCapability+RGAgentBase |

### OrchestratorAgent (5 agents)
- Dominant base signature: `SovereignBaseAgent`
- Signature ratio: 0.6
- **FORCED**: No waivers allowed

| Agent | Layer | Domain LOC | BP Ratio | Bases |
|-------|-------|-----------|----------|-------|
| CoordinateObservabilityOperationsAgent | L6 | 45 | 0.37 | AtomicExecutionMixin+SubatomicTestingMixin+SovereignBaseAgent |
| DispatchOutreachToolsAgent | apps_lic | 52 | 0.23 | SovereignBaseAgent |
| OrchestrationHandshakeAgent | L3 | 86 | 0.29 | SubatomicTestingMixin+SovereignBaseAgent+CoreOrchestrationAgent |
| DispatchResumeToolsAgent | apps_rg | 90 | 0.16 | SovereignBaseAgent |
| LicS2SupervisorAgent | apps_lic | 238 | 0.41 | SovereignBaseAgent |

## All Archetypes Detail

### ReasoningAgent (107 agents)

| Agent | Layer | Domain LOC | BP Ratio |
|-------|-------|-----------|----------|
| BudgetAgent | L1 | 15 | 0.68 |
| HistorianAgent | L2 | 18 | 0.59 |
| StructuredEngineAgent | L2 | 20 | 0.00 |
| PII_SanitizerSpecialistAgent | apps_lic | 20 | 0.01 |
| CostGovernorAgent | L5 | 22 | 0.60 |
| LocationAgent | L5 | 24 | 0.13 |
| ValidatorAgent | apps_lic | 26 | 0.08 |
| NamingAgent | L5 | 28 | 0.37 |
| SovereignCognitivePlaneAgent | L1 | 29 | 0.44 |
| CartographerAgent | unknown | 29 | 0.61 |
| TypeHintFixerAgent | L5 | 36 | 0.16 |
| SovereignReasoningMemory | unknown | 38 | 0.14 |
| RgStrategicPlannerAgent | apps_rg | 44 | 0.32 |
| UnifiedAgent | L3 | 51 | 0.04 |
| PIISanitizerAgent | L5 | 54 | 0.34 |
| SprawlInspectorAgent | L5 | 54 | 0.41 |
| RgTemplateOptimizerAgent | apps_rg | 54 | 0.25 |
| AppBase | apps_shared | 55 | 0.12 |
| InterfaceBoundaryAgent | L5 | 56 | 0.41 |
| OutreachSignalRouterAgent | apps_lic | 56 | 0.06 |
| ProactiveAgent | apps_rg | 56 | 0.34 |
| OmniContext | L3 | 57 | 0.08 |
| DocumentationAgent | L5 | 58 | 0.40 |
| GospelSyncAgent | L0 | 65 | 0.42 |
| ConstitutionalReviewerAgent | L5 | 69 | 0.35 |
| SovereignSemanticCache | unknown | 73 | 0.19 |
| AgentFactory | L3 | 79 | 0.00 |
| AutonomousThreatEvolutionAgent | L5 | 79 | 0.37 |
| CognitiveDispositionAgent | L5 | 79 | 0.61 |
| SherlockAgent | L1 | 82 | 0.35 |
| RgStrategicPlannerAgent | L2 | 83 | 0.43 |
| DependencyPruningAgent | L5 | 89 | 0.43 |
| SovereignRAGManager | unknown | 93 | 0.28 |
| SupremeCourt | L1 | 94 | 0.15 |
| ToxicDependencyAuditor | L5 | 99 | 0.30 |
| ComplexityAnalyzerAgent | L5 | 101 | 0.22 |
| SubAtomicRegistryAgent | L2 | 116 | 0.18 |
| CoverageAgent | L3 | 116 | 0.56 |
| RedisSovereignAgent | unknown | 117 | 0.34 |
| CachedStateLedgerAgent | unknown | 118 | 0.31 |
| GitHygieneAgent | L5 | 119 | 0.58 |
| CodeDetectorAgent | L5 | 120 | 0.27 |
| MetaLearningAgent | L1 | 121 | 0.40 |
| RedTeamAgent | L5 | 124 | 0.46 |
| RagHealthCheckAgent | L5 | 129 | 0.28 |
| DDDAlignmentAgent | L5 | 131 | 0.27 |
| ChaosEngineeringAgent | L5 | 139 | 0.17 |
| TypeMechanicAgent | L5 | 144 | 0.11 |
| AdversarialProbeAgent | L5 | 146 | 0.17 |
| EmbeddingSovereignAgent | L2 | 148 | 0.40 |
| ReportLocationAgent | L5 | 148 | 0.27 |
| StructuralValidatorAgent | L5 | 155 | 0.22 |
| RgReflectionAgent | apps_rg | 158 | 0.13 |
| BoundaryTestingAgent | L5 | 161 | 0.16 |
| LLMPromptGovernorAgent | L1 | 166 | 0.38 |
| CredentialScannerAgent | L5 | 167 | 0.35 |
| RootHygieneAgent | L5 | 173 | 0.33 |
| ContentQualityAgent | apps_rg | 173 | 0.12 |
| SovereignPineconeStoreAgent | unknown | 175 | 0.25 |
| ResourceManagerAgent | L5 | 177 | 0.15 |
| RedSentinelAgent | L5 | 182 | 0.23 |
| AutonomousPromptEvolutionAgent | L1 | 183 | 0.30 |
| GravityLeakRepairAgent | L5 | 186 | 0.53 |
| StructuralEngineerAgent | L5 | 190 | 0.12 |
| PeerIntelligenceAuditorAgent | L2 | 191 | 0.27 |
| SovereignPineconeMcpClientAgent | L2 | 196 | 0.05 |
| HealValidatorAgent | L5 | 202 | 0.19 |
| SecurityManagerAgent | L5 | 205 | 0.19 |
| ContextCurator | L3 | 209 | 0.08 |
| ASTValidatorAgent | L1 | 212 | 0.35 |
| SovereignActionPlaneAgent | L5 | 212 | 0.16 |
| ContextCuratorAgent | L1 | 213 | 0.19 |
| PromptRegistryAgent | L5 | 215 | 0.12 |
| PreCommitSovereignAgent | L5 | 217 | 0.24 |
| RegressionOracleAgent | L5 | 218 | 0.33 |
| SovereignMcpRouter | L3 | 238 | 0.02 |
| BenchmarkingAgent | L0 | 242 | 0.10 |
| PredictiveCostAuditorAgent | L5 | 248 | 0.22 |
| TestGeneratorAgent | L5 | 249 | 0.06 |
| RgReflectionAgent | L1 | 258 | 0.28 |
| CodeEnforcerAgent | L5 | 261 | 0.24 |
| DAGMutatorAgent | L3 | 262 | 0.23 |
| SubatomicHopAgent | L3 | 266 | 0.22 |
| StructureEnforcerAgent | L5 | 272 | 0.19 |
| AgentGym | L3 | 273 | 0.09 |
| GitAgent | L2 | 275 | 0.25 |
| DuplicateCodeDetectorAgent | L5 | 280 | 0.18 |
| StructureHealerAgent | L5 | 284 | 0.24 |
| CodeValidatorAgent | L5 | 294 | 0.23 |
| ToolsmithAgent | L2 | 309 | 0.22 |
| SystemArchitectAgent | L5 | 334 | 0.11 |
| OutreachValidationExecutorAgent | apps_lic | 357 | 0.26 |
| StrategicRecommendationAgent | L1 | 372 | 0.15 |
| AdversarialRedTeamerAgent | L5 | 386 | 0.10 |
| CodeHealerAgent | L5 | 439 | 0.17 |
| PineconeSovereignAgent | L5 | 444 | 0.27 |
| MemoryArchitectAgent | unknown | 484 | 0.12 |
| SSOTFolderCleanupAgent | L0 | 519 | 0.18 |
| GovernanceAgent | L5 | 551 | 0.21 |
| NervousSystemAgent | L3 | 570 | 0.32 |
| CodeDeduplicationAgent | L5 | 642 | 0.28 |
| LocationValidatorAgent | L5 | 721 | 0.04 |
| FilesystemSSOTReconcilerAgent | L0 | 1086 | 0.07 |
| ArchitectureGovernorAgent | L5 | 1255 | 0.18 |
| HierarchyAgent | L5 | 1339 | 0.17 |
| LocationHealerAgent | L5 | 2184 | 0.09 |
| FileClassificationAgent | L5 | 3842 | 0.08 |

### WrapperProxyAgent (22 agents)

| Agent | Layer | Domain LOC | BP Ratio |
|-------|-------|-----------|----------|
| SubAtomicAgent | L3 | 0 | 0.32 |
| DependencyDiplomatAgent | L5 | 0 | 0.89 |
| NeuralAutoImmuneAgent | L5 | 0 | 0.79 |
| MCPHardenedMixin | apps_lic | 0 | 0.00 |
| OutreachAgent | apps_lic | 0 | 0.00 |
| OutreachAgent | apps_lic | 0 | 0.00 |
| OutreachAgent | apps_lic | 0 | 0.00 |
| OutreachAgent | apps_lic | 0 | 0.00 |
| OutreachAgent | apps_lic | 0 | 0.00 |
| DiscoveredAgent | unknown | 0 | 0.00 |
| SemanticTerritoryMapperAgent | L5 | 2 | 0.85 |
| OmniContextAgent | L5 | 4 | 0.68 |
| PolicyNeuralAutoImmuneAgent | L5 | 5 | 0.73 |
| SemanticMapperAgent | L5 | 6 | 0.69 |
| IntelligenceLibrarianAgent | apps_lic | 6 | 0.09 |
| StrategistAgent | L1 | 7 | 0.67 |
| MessageArchitectAgent | apps_lic | 8 | 0.07 |
| BootstrapAgent | L0 | 9 | 0.91 |
| UiValidationAgent | L2 | 10 | 0.97 |
| ContentStrategyAgent | apps_rg | 10 | 0.19 |
| CampaignPlannerAgent | apps_rg | 11 | 0.53 |
| TerritoryChangeHandlerAgent | L5 | 14 | 0.11 |

### PolicyGateAgent (22 agents)

| Agent | Layer | Domain LOC | BP Ratio |
|-------|-------|-----------|----------|
| CachedSafetyShield | L5 | 7 | 0.30 |
| GlobalComplianceAggregatorAgent | L5 | 8 | 0.78 |
| GenerativeGuardAgent | L5 | 64 | 0.29 |
| DocstringComplianceAgent | L0 | 69 | 0.38 |
| SemanticGatekeeperAgent | L3 | 74 | 0.40 |
| CompositeGuardrailAgent | L5 | 80 | 0.16 |
| SovereignMCPGateway | L2 | 84 | 0.00 |
| L5SafetyExerciserAgent | L5 | 89 | 0.27 |
| SafetyDetectorAgent | L5 | 111 | 0.17 |
| SafetyInspectorAgent | L5 | 117 | 0.46 |
| InputValidationGuardrail | L5 | 127 | 0.31 |
| ConfigurationSecurityGuardrail | L5 | 128 | 0.05 |
| AutonomyGuardianAgent | L5 | 131 | 0.84 |
| GitSafetyHandlerAgent | L5 | 134 | 0.24 |
| MCPGuardianAgent | L5 | 185 | 0.26 |
| DynamicSealAgent | L5 | 214 | 0.22 |
| GovernanceShieldAgent | apps_lic | 224 | 0.26 |
| VerificationGate | L5 | 229 | 0.04 |
| SafetyExecutorAgent | L5 | 230 | 0.16 |
| SelfUpdatingSafetyEngineAgent | L5 | 270 | 0.13 |
| HygieneGuardianAgent | L5 | 364 | 0.26 |
| TestCoverageGuardianAgent | L5 | 369 | 0.52 |

### InspectionAgent (3 agents)

| Agent | Layer | Domain LOC | BP Ratio |
|-------|-------|-----------|----------|
| DagRuntimeInspectorAgent | L3 | 3 | 0.27 |
| SignatureVerifierAgent | L5 | 3 | 0.52 |
| TokenBudgetInspectorAgent | L5 | 3 | 0.29 |

### ToolRunnerAgent (2 agents)

| Agent | Layer | Domain LOC | BP Ratio |
|-------|-------|-----------|----------|
| UnusedCleanupAgent | L5 | 39 | 0.00 |
| CodeFormatterAgent | L5 | 52 | 0.00 |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

