======================================================================================================================================================================
                                          AGENTIC SYSTEM — WIDESCREEN META-LEARNING PIPELINE & FEEDBACK CYCLES
======================================================================================================================================================================
  [ THE TOP LAYER: INGESTION & OBSERVABILITY ]                                [ THE SIDE LAYER: STATE & THE META-LEARNING PIPELINE ]
+---------------------------------------------------+                         +--------------------------------------------------------------------------------------+
| L1: COGNITIVE STUDIO / L6: OBSERVABILITY          |                         | L4: STATE, MEMORY & PERSISTENCE (THE LEARNING HUB)                                   |
|---------------------------------------------------|                         |--------------------------------------------------------------------------------------|
| - [L1] RAG Hydration & Intent Ingestion.          |                         | STAGE 1-4: IMMUTABLE DATA FREEZE & SNAPSHOT                                          |
| - [L6] ANOMALY ENGINE: Emits Drift Scores &       |======(Raw Output)======>| [STAGE 1] AUDIT: AuditStore.read_audit_slice(window_start, window_end)               |
|        Threat Signals during live requests.       |                         | [STAGE 2] TELEMETRY: TelemetryStore.read_events(window_start, window_end)            |
+---------------------------------------------------+                         | [STAGE 3] CONFIG: ConfigProvider.get_current_configs()                               |
                          ^                                                   | [STAGE 4] SNAPSHOT: MetaLearningSnapshot(engine_version, SemanticClockSnapshot)      |
                          |                                                   +--------------------------------------------------------------------------------------+
                          |                                                                             ||
                          |                                                                             vv
==========================|=============================================================================||============================================================
  [ THE CONTROL SPINE ]   |                                                                             ||
+-------------------------|---------------------------------------------------------------+             ||
| L0: TRAFFIC CONTROL / L3: ORCHESTRATION / L5: SAFETY|                                       |             ||
|-------------------------|---------------------------------------------------------------|             ||
| - [L0] Updates routing rules via active updates.    |                                       |             ||
| - [L3] Tunes orchestration weights.                 |                                       || (Frozen Snapshot for stable analysis)
| - [L5] Updates safety rule strictness.              |                                       |             ||
+-----------------------------------------------------------------------------------------+             ||
                          ^                                                                             vv
                          |                                                   +--------------------------------------------------------------------------------------+
                          |                                                   | STAGE 5-6: ROOT CAUSE ANALYSIS & PROPOSAL GENERATION                                 |
                          |                                                   |--------------------------------------------------------------------------------------|
                          |                                                   | [STAGE 5] RCA: analyze_failures() -> RCAReport (Categorizes Failure Type).           |
                          | (The Feedback Bus: Applies Updates)               | [STAGE 6] PROPOSE: Target specific optimization areas (Resource, Syntax, RLHF).      |
                          |                                                   |   - Generates targeted `ChangePackages` (Strictly `proposal_only=True`).             |
                          |                                                   |   - Embeds RLHF DPO threshold adjustments.                                          |
                          |                                                   |                                                                                      |
                          |                                                   | PROPOSER PROTOCOLS (Protocol-based dependency injection):                            |
                          |                                                   | - L0Proposer: Routing weight optimization proposals                                  |
                          |                                                   | - L1Proposer: Cognitive priming and RAG threshold proposals                          |
                          |                                                   | - L5Proposer: Safety rule strictness and risk tier proposals                         |
                          |                                                   | - RAGProposer: Retrieval profile and embedding config proposals                      |
                          |                                                   |                                                                                      |
                          |                                                   | OPTIMIZATION ENGINES:                                                                |
                          |                                                   | - RLHFOptimizer: propose_from_dpo(dpo_batch_bytes) -> ChangePackage                  |
                          |                                                   | - HealingConfigOptimizer: Tunes healing tier thresholds from outcome data            |
                          |                                                   | - PatternAnalysisEngine: Extracts semantic patterns from execution traces            |
                          |                                                   | - HealingConfidenceScorer: Recalibrates confidence scoring weights                   |
                          |                                                   | - FailureFingerprinter: Categorizes failure signatures for RCA                       |
                          |                                                   | - RiskCorrelator: Correlates risk signals across layers                              |
                          |                                                   +--------------------------------------------------------------------------------------+
                          |                                                                             ||
                          |                                                                             vv
                          |                                                   +--------------------------------------------------------------------------------------+
                          |                                                   | STAGE 7: VALIDATION GAUNTLET (THE REGRESSION SHIELD)                                 |
                          |                                                   |--------------------------------------------------------------------------------------|
                          |                                                   | [STAGE 7] VALIDATE: Evaluates proposals via Replay & Shadow Evaluators.             |
                          |                                                   | [!] OSCILLATE RULE: Strictly rejects flapping thresholds.                            |
                          |                                                   | [!] STABILITY CHECK: Requires mathematical stability before rule commit.             |
                          |                                                   |                                                                                      |
                          |                                                   | ARBITRATION & APPROVAL:                                                              |
                          |                                                   | - ArbitrationEngine: Resolves conflicting proposals across proposers                 |
                          |                                                   | - ArbitrationPolicy: Defines conflict resolution strategy                            |
                          |                                                   | - ApprovalGate (Protocol): decide(change_package) -> ApprovalDecision                |
                          |                                                   | - DefaultRuleBasedGate: Risk-based approval with configurable thresholds             |
                          |                                                   | - RiskTierClassifier: classify(change_package) -> RiskTier                           |
                          +===================================================| [STAGE 8] PATTERN: Extracts semantic patterns -> Singleton RAG Factory (C0).        |
                                                                              | [STAGE 9] COMMIT: Activator commits proven `ChangePackages` to VersionStore.         |
                                                                              | [!] INJECTION RULE: Dual Injection required (VersionStore + ApprovalGate).           |
                                                                              +--------------------------------------------------------------------------------------+
======================================================================================================================================================================
  CORE META-LEARNING DATA CONTRACTS
======================================================================================================================================================================
| [14] ChangePackage        : [source, target, changes:bytes, confidence:float, reason:tuple, timestamp_utc] -> proposal_only=True by default.                      |
| [15] CommitProofInvariant : Proof MUST bind to true implementation commit. No churn commits permitted.                                                            |
| [32] PipelineConfig       : [engine_version, config_surface_version, shadow_thresholds, cooldown_policy, sample_policy, oscillation_policy,                      |
|                              enabled_proposers, require_replay_validation, require_shadow_validation, proposal_only] -> Immutable pipeline configuration          |
| [33] PipelineDependencies : [audit_store, telemetry_store, config_provider, baseline_metrics_provider, l0_proposer, rag_proposer, l1_proposer, l5_proposer,      |
|                              version_store, activator, approval_gate, healing_outcome_intake_adapter, healing_config_optimizer, l4_state_writer,                  |
|                              pattern_analysis_engine, resource_predictor_bytes, rollback_refinement_decision_bytes, dpo_batch_bytes, rlhf_optimizer,              |
|                              healing_confidence_scorer, failure_fingerprinter, risk_correlator, arbitration_engine, arbitration_policy] -> Protocol-based DI      |
| [34] ApprovalDecision     : Enum[APPROVE, REJECT, DEFER] -> Approval gate decision for ChangePackage activation                                                  |
| [35] RCAReport            : [failure_category, root_cause, affected_components, recommended_actions] -> Root cause analysis output                               |
======================================================================================================================================================================
