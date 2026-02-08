# Import Complexity (Blast Radius) Report

**Blast radius** = number of internal imports. A high blast radius means
changes to this agent ripple through more of the codebase.

- **Agents analyzed**: 190
- **Average blast radius**: 4.3
- **Max blast radius**: FileClassificationAgent (27)

## Per-Agent Breakdown

| Agent | Layer | Total | Internal | Stdlib | 3rd Party | Blast Radius |
|-------|-------|-------|----------|--------|-----------|-------------|
| FileClassificationAgent | L5_safety | 40 | 27 | 11 | 2 | 27 |
| LocationHealerAgent | L5_safety | 40 | 26 | 12 | 2 | 26 |
| LocationValidatorAgent | L5_safety | 28 | 22 | 5 | 1 | 22 |
| SubAtomicRegistryAgent | L2_execution | 33 | 21 | 11 | 1 | 21 |
| HierarchyAgent | L5_safety | 26 | 18 | 7 | 1 | 18 |
| ArchitectureGovernorAgent | L5_safety | 28 | 16 | 11 | 1 | 16 |
| GenerativeGuardAgent | L5_safety | 25 | 16 | 8 | 1 | 16 |
| FilesystemSSOTReconcilerAgent | L0_maintenance | 23 | 11 | 11 | 1 | 11 |
| L5SafetyExerciserAgent | L5_safety | 16 | 11 | 4 | 1 | 11 |
| AutonomyGuardianAgent | L5_safety | 20 | 10 | 9 | 1 | 10 |
| CodeHealerAgent | L5_safety | 24 | 10 | 13 | 1 | 10 |
| GovernanceAgent | L5_safety | 19 | 10 | 8 | 1 | 10 |
| SSOTFolderCleanupAgent | L0_maintenance | 15 | 8 | 6 | 1 | 8 |
| CoverageAgent | L3_orchestration | 14 | 8 | 4 | 2 | 8 |
| AutonomicMonitorAgent | L6_observability | 14 | 8 | 5 | 1 | 8 |
| NervousSystemAgent | L3_orchestration | 10 | 7 | 2 | 1 | 7 |
| CodeDeduplicationAgent | L5_safety | 23 | 7 | 10 | 6 | 7 |
| DDDAlignmentAgent | L5_safety | 14 | 7 | 6 | 1 | 7 |
| DuplicateCodeDetectorAgent | L5_safety | 12 | 7 | 5 | 0 | 7 |
| PineconeSovereignAgent | L5_safety | 18 | 7 | 8 | 3 | 7 |
| PolicyNeuralAutoImmuneAgent | L5_safety | 11 | 7 | 3 | 1 | 7 |
| StructuralValidatorAgent | L5_safety | 18 | 7 | 11 | 0 | 7 |
| TestCoverageGuardianAgent | L5_safety | 17 | 7 | 9 | 1 | 7 |
| PeerIntelligenceAuditorAgent | L2_execution | 10 | 6 | 3 | 1 | 6 |
| DagRuntimeInspectorAgent | L3_orchestration | 7 | 6 | 1 | 0 | 6 |
| RagHealthCheckAgent | L5_safety | 10 | 6 | 3 | 1 | 6 |
| RedTeamAgent | L5_safety | 10 | 6 | 3 | 1 | 6 |
| ReportLocationAgent | L5_safety | 14 | 6 | 7 | 1 | 6 |
| SignatureVerifierAgent | L5_safety | 9 | 6 | 2 | 1 | 6 |
| SovereignActionPlaneAgent | L5_safety | 14 | 6 | 7 | 1 | 6 |
| ReportingAgent | L6_observability | 11 | 6 | 4 | 1 | 6 |
| HOP1ProfileAnalysisAgent | apps_lic | 12 | 6 | 5 | 1 | 6 |
| HOP2ResearchAgent | apps_lic | 13 | 6 | 6 | 1 | 6 |
| OutreachSignalRouterAgent | apps_lic | 13 | 6 | 6 | 1 | 6 |
| SovereignRAGManagerAgent | knowledge | 9 | 6 | 3 | 0 | 6 |
| DocstringComplianceAgent | L0_maintenance | 9 | 5 | 3 | 1 | 5 |
| SherlockAgent | L1_cognition | 11 | 5 | 5 | 1 | 5 |
| EmbeddingSovereignAgent | L2_execution | 17 | 5 | 9 | 3 | 5 |
| AgentFactory | L3_orchestration | 7 | 5 | 1 | 1 | 5 |
| SubatomicHopAgent | L3_orchestration | 11 | 5 | 5 | 1 | 5 |
| AdversarialRedTeamerAgent | L5_safety | 11 | 5 | 5 | 1 | 5 |
| BoundaryTestingAgent | L5_safety | 9 | 5 | 3 | 1 | 5 |
| ChaosEngineeringAgent | L5_safety | 10 | 5 | 3 | 2 | 5 |
| GravityLeakRepairAgent | L5_safety | 13 | 5 | 7 | 1 | 5 |
| InterfaceBoundaryAgent | L5_safety | 9 | 5 | 4 | 0 | 5 |
| PredictiveCostAuditorAgent | L5_safety | 11 | 5 | 5 | 1 | 5 |
| SystemArchitectAgent | L5_safety | 12 | 5 | 6 | 1 | 5 |
| TokenBudgetInspectorAgent | L5_safety | 8 | 5 | 2 | 1 | 5 |
| CoordinateObservabilityOperationsAgent | L6_observability | 12 | 5 | 6 | 1 | 5 |
| MetricsAgent | L6_observability | 14 | 5 | 8 | 1 | 5 |
| TelemetryAgent | L6_observability | 13 | 5 | 7 | 1 | 5 |
| TrackObservabilityCostAgent | L6_observability | 10 | 5 | 4 | 1 | 5 |
| HOP3SenderGroundingAgent | apps_lic | 12 | 5 | 6 | 1 | 5 |
| HOP4RoutingAgent | apps_lic | 10 | 5 | 4 | 1 | 5 |
| HOP5GenerationAgent | apps_lic | 12 | 5 | 6 | 1 | 5 |
| HOP6ValidationAgent | apps_lic | 11 | 5 | 5 | 1 | 5 |
| HOP7GateDecisionAgent | apps_lic | 10 | 5 | 4 | 1 | 5 |
| HOP8QAReportAgent | apps_lic | 12 | 5 | 6 | 1 | 5 |
| HOP9IntegrationAgent | apps_lic | 11 | 5 | 5 | 1 | 5 |
| ASTValidatorAgent | L1_cognition | 10 | 4 | 5 | 1 | 4 |
| BudgetAgent | L1_cognition | 7 | 4 | 2 | 1 | 4 |
| LLMPromptGovernorAgent | L1_cognition | 10 | 4 | 5 | 1 | 4 |
| SupremeCourtAgent | L1_cognition | 8 | 4 | 3 | 1 | 4 |
| GitAgent | L2_execution | 12 | 4 | 7 | 1 | 4 |
| ToolsmithAgent | L2_execution | 12 | 4 | 7 | 1 | 4 |
| DAGMutatorAgent | L3_orchestration | 15 | 4 | 6 | 5 | 4 |
| OrchestrationHandshakeAgent | L3_orchestration | 9 | 4 | 4 | 1 | 4 |
| SubAtomicAgent | L3_orchestration | 7 | 4 | 2 | 1 | 4 |
| sovereign_mcp_router | L3_orchestration | 9 | 4 | 4 | 1 | 4 |
| MemoryArchitectAgent | L4_state | 16 | 4 | 9 | 3 | 4 |
| RedisSovereignAgent | L4_state | 12 | 4 | 5 | 3 | 4 |
| SovereignPineconeStoreAgent | L4_state | 9 | 4 | 4 | 1 | 4 |
| sovereign_semantic_cache | L4_state | 12 | 4 | 7 | 1 | 4 |
| AdversarialProbeAgent | L5_safety | 8 | 4 | 3 | 1 | 4 |
| AutonomousThreatEvolutionAgent | L5_safety | 12 | 4 | 7 | 1 | 4 |
| ComplexityAnalyzerAgent | L5_safety | 11 | 4 | 6 | 1 | 4 |
| CompositeGuardrailAgent | L5_safety | 10 | 4 | 5 | 1 | 4 |
| DependencyDiplomatAgent | L5_safety | 7 | 4 | 2 | 1 | 4 |
| DependencyPruningAgent | L5_safety | 10 | 4 | 5 | 1 | 4 |
| GitHygieneAgent | L5_safety | 10 | 4 | 5 | 1 | 4 |
| GitSafetyHandlerAgent | L5_safety | 9 | 4 | 4 | 1 | 4 |
| GlobalComplianceAggregatorAgent | L5_safety | 8 | 4 | 3 | 1 | 4 |
| HygieneGuardianAgent | L5_safety | 11 | 4 | 6 | 1 | 4 |
| LocationAgent | L5_safety | 7 | 4 | 2 | 1 | 4 |
| MCPGuardianAgent | L5_safety | 10 | 4 | 5 | 1 | 4 |
| PromptRegistryAgent | L5_safety | 14 | 4 | 8 | 2 | 4 |
| RedSentinelAgent | L5_safety | 13 | 4 | 8 | 1 | 4 |
| RegressionOracleAgent | L5_safety | 8 | 4 | 3 | 1 | 4 |
| SelfUpdatingSafetyEngineAgent | L5_safety | 14 | 4 | 9 | 1 | 4 |
| SprawlInspectorAgent | L5_safety | 11 | 4 | 6 | 1 | 4 |
| PerformanceAnalystAgent | L6_observability | 9 | 4 | 5 | 0 | 4 |
| RuntimeTelemetryAgent | L6_observability | 9 | 4 | 5 | 0 | 4 |
| SovereignObservabilityAgent | L6_observability | 8 | 4 | 3 | 1 | 4 |
| LeadQualityAgent | apps_lic | 6 | 4 | 1 | 1 | 4 |
| PII_SanitizerSpecialistAgent | apps_lic | 12 | 4 | 5 | 3 | 4 |
| BenchmarkingAgent | L0_maintenance | 13 | 3 | 8 | 2 | 3 |
| AgentInfo | L1_cognition | 8 | 3 | 4 | 1 | 3 |
| StrategicRecommendationAgent | L1_cognition | 10 | 3 | 6 | 1 | 3 |
| StrategistAgent | L1_cognition | 7 | 3 | 3 | 1 | 3 |
| HistorianAgent | L2_execution | 10 | 3 | 4 | 3 | 3 |
| RgStrategicPlannerAgent | L2_execution | 8 | 3 | 4 | 1 | 3 |
| SemanticGatekeeperAgent | L3_orchestration | 10 | 3 | 6 | 1 | 3 |
| context_curator_engine | L3_orchestration | 6 | 3 | 2 | 1 | 3 |
| CartographerAgent | L4_state | 8 | 3 | 4 | 1 | 3 |
| CodeFormatterAgent | L5_safety | 8 | 3 | 4 | 1 | 3 |
| CodeValidatorAgent | L5_safety | 13 | 3 | 10 | 0 | 3 |
| CognitiveDispositionAgent | L5_safety | 9 | 3 | 5 | 1 | 3 |
| ConstitutionalReviewerAgent | L5_safety | 5 | 3 | 1 | 1 | 3 |
| CostGovernorAgent | L5_safety | 7 | 3 | 3 | 1 | 3 |
| CredentialScannerAgent | L5_safety | 11 | 3 | 7 | 1 | 3 |
| DocumentationAgent | L5_safety | 7 | 3 | 3 | 1 | 3 |
| NamingAgent | L5_safety | 6 | 3 | 2 | 1 | 3 |
| OmniContextAgent | L5_safety | 7 | 3 | 3 | 1 | 3 |
| PIISanitizerAgent | L5_safety | 8 | 3 | 4 | 1 | 3 |
| PreCommitSovereignAgent | L5_safety | 12 | 3 | 6 | 3 | 3 |
| SafetyInspectorAgent | L5_safety | 9 | 3 | 5 | 1 | 3 |
| StructuralEngineerAgent | L5_safety | 9 | 3 | 5 | 1 | 3 |
| StructureHealerAgent | L5_safety | 15 | 3 | 11 | 1 | 3 |
| TestGeneratorAgent | L5_safety | 10 | 3 | 6 | 1 | 3 |
| TypeHintFixerAgent | L5_safety | 6 | 3 | 2 | 1 | 3 |
| TypeMechanicAgent | L5_safety | 6 | 3 | 3 | 0 | 3 |
| UnusedCleanupAgent | L5_safety | 8 | 3 | 4 | 1 | 3 |
| toxic_dependency_auditor | L5_safety | 5 | 3 | 2 | 0 | 3 |
| MetricsWitnessAgent | L6_observability | 8 | 3 | 4 | 1 | 3 |
| StrategicObservationAgent | L6_observability | 7 | 3 | 4 | 0 | 3 |
| CampaignBalanceAgent | apps_lic | 8 | 3 | 4 | 1 | 3 |
| DeliverabilityAgent | apps_lic | 8 | 3 | 4 | 1 | 3 |
| ValidatorAgent | apps_lic | 8 | 3 | 4 | 1 | 3 |
| ATSCompatibilityAgent | apps_rg | 8 | 3 | 4 | 1 | 3 |
| BrandComplianceAgent | apps_rg | 6 | 3 | 2 | 1 | 3 |
| AppBase | apps_shared | 9 | 3 | 5 | 1 | 3 |
| BootstrapAgent | L0_maintenance | 5 | 2 | 2 | 1 | 2 |
| GospelSyncAgent | L0_maintenance | 7 | 2 | 5 | 0 | 2 |
| AutonomousPromptEvolutionAgent | L1_cognition | 10 | 2 | 6 | 2 | 2 |
| ContextCuratorAgent | L1_cognition | 10 | 2 | 7 | 1 | 2 |
| MetaLearningAgent | L1_cognition | 9 | 2 | 7 | 0 | 2 |
| RgReflectionAgent | L1_cognition | 7 | 2 | 4 | 1 | 2 |
| AgentPlan | L2_execution | 6 | 2 | 3 | 1 | 2 |
| SovereignMCPGatewayAgent | L2_execution | 6 | 2 | 3 | 1 | 2 |
| SovereignPineconeMcpClientAgent | L2_execution | 7 | 2 | 4 | 1 | 2 |
| UiValidationAgent | L2_execution | 5 | 2 | 2 | 1 | 2 |
| AgentCategory | L3_orchestration | 15 | 2 | 11 | 2 | 2 |
| AgentGym | L3_orchestration | 8 | 2 | 5 | 1 | 2 |
| CachedStateLedgerAgent | L4_state | 10 | 2 | 6 | 2 | 2 |
| CodeDetectorAgent | L5_safety | 16 | 2 | 13 | 1 | 2 |
| CodeEnforcerAgent | L5_safety | 16 | 2 | 12 | 2 | 2 |
| ConfigurationSecurityGuardrailAgent | L5_safety | 8 | 2 | 5 | 1 | 2 |
| DynamicSealAgent | L5_safety | 7 | 2 | 3 | 2 | 2 |
| HealValidatorAgent | L5_safety | 13 | 2 | 7 | 4 | 2 |
| NeuralAutoImmuneAgent | L5_safety | 5 | 2 | 2 | 1 | 2 |
| RootHygieneAgent | L5_safety | 9 | 2 | 6 | 1 | 2 |
| SemanticMapperAgent | L5_safety | 5 | 2 | 2 | 1 | 2 |
| SemanticTerritoryMapperAgent | L5_safety | 5 | 2 | 2 | 1 | 2 |
| input_validation_guardrail | L5_safety | 8 | 2 | 5 | 1 | 2 |
| verification_gate | L5_safety | 7 | 2 | 5 | 0 | 2 |
| DeadlockDetectorAgent | L6_observability | 9 | 2 | 7 | 0 | 2 |
| DebateSynthesisAgent | L6_observability | 8 | 2 | 5 | 1 | 2 |
| TracingAgent | L6_observability | 21 | 2 | 9 | 10 | 2 |
| GovernanceShieldAgent | apps_lic | 7 | 2 | 4 | 1 | 2 |
| IntelligenceLibrarianAgent | apps_lic | 6 | 2 | 3 | 1 | 2 |
| LicS2SupervisorAgent | apps_lic | 4 | 2 | 1 | 1 | 2 |
| MessageDiversityValidator | apps_lic | 3 | 2 | 1 | 0 | 2 |
| OutreachAgent | apps_lic | 3 | 2 | 1 | 0 | 2 |
| OutreachAgent__LicTemplateOptimizerAgent | apps_lic | 3 | 2 | 1 | 0 | 2 |
| OutreachAgent__MessageComplianceAgent | apps_lic | 3 | 2 | 1 | 0 | 2 |
| OutreachAgent__OutreachProactiveAgent | apps_lic | 4 | 2 | 2 | 0 | 2 |
| OutreachValidationExecutorAgent | apps_lic | 7 | 2 | 4 | 1 | 2 |
| CampaignPlannerAgent | apps_rg | 6 | 2 | 3 | 1 | 2 |
| ContentQualityAgent | apps_rg | 7 | 2 | 4 | 1 | 2 |
| FactCheckAgent | apps_rg | 5 | 2 | 2 | 1 | 2 |
| SectionBalanceAgent | apps_rg | 5 | 2 | 2 | 1 | 2 |
| DiscoveredAgent | runtime | 8 | 2 | 6 | 0 | 2 |
| omni_context_engine | L3_orchestration | 3 | 1 | 1 | 1 | 1 |
| sovereign_reasoning_memory_ledger | L4_state | 7 | 1 | 5 | 1 | 1 |
| AgentPermission | L5_safety | 13 | 1 | 10 | 2 | 1 |
| CachedSafetyShieldAgent | L5_safety | 4 | 1 | 2 | 1 | 1 |
| ResourceManagerAgent | L5_safety | 10 | 1 | 8 | 1 | 1 |
| SafetyDetectorAgent | L5_safety | 11 | 1 | 9 | 1 | 1 |
| SafetyExecutorAgent | L5_safety | 12 | 1 | 10 | 1 | 1 |
| StructureEnforcerAgent | L5_safety | 11 | 1 | 9 | 1 | 1 |
| TerritoryChangeHandlerAgent | L5_safety | 11 | 1 | 7 | 3 | 1 |
| DispatchOutreachToolsAgent | apps_lic | 6 | 1 | 4 | 1 | 1 |
| MessageArchitectAgent | apps_lic | 5 | 1 | 3 | 1 | 1 |
| OutreachAgent__OutreachLearningAgent | apps_lic | 9 | 1 | 8 | 0 | 1 |
| ContentStrategyAgent | apps_rg | 5 | 1 | 3 | 1 | 1 |
| DispatchResumeToolsAgent | apps_rg | 11 | 1 | 6 | 4 | 1 |
| ProactiveAgent | apps_rg | 4 | 1 | 2 | 1 | 1 |
| RgReflectionAgent__RgReflectionAgent | apps_rg | 5 | 1 | 3 | 1 | 1 |
| RgStrategicPlannerAgent__RgStrategicPlannerAgent | apps_rg | 4 | 1 | 2 | 1 | 1 |
| RgTemplateOptimizerAgent | apps_rg | 4 | 1 | 2 | 1 | 1 |

## Layer Summary

| Layer | Agents | Avg Blast Radius | Max Blast Radius |
|-------|--------|-----------------|------------------|
| L0_maintenance | 6 | 5.2 | 11 |
| L1_cognition | 12 | 3.2 | 5 |
| L2_execution | 11 | 4.9 | 21 |
| L3_orchestration | 14 | 4.1 | 8 |
| L4_state | 7 | 3.1 | 4 |
| L5_safety | 84 | 5.2 | 27 |
| L6_observability | 14 | 4.1 | 8 |
| apps_lic | 27 | 3.4 | 6 |
| apps_rg | 12 | 1.7 | 3 |
| apps_shared | 1 | 3.0 | 3 |
| knowledge | 1 | 6.0 | 6 |
| runtime | 1 | 2.0 | 2 |
