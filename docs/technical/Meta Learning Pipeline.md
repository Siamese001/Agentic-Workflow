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
                          |                                                   +--------------------------------------------------------------------------------------+
                          |                                                                             ||
                          |                                                                             vv
                          |                                                   +--------------------------------------------------------------------------------------+
                          |                                                   | STAGE 7: VALIDATION GAUNTLET (THE REGRESSION SHIELD)                                 |
                          |                                                   |--------------------------------------------------------------------------------------|
                          |                                                   | [STAGE 7] VALIDATE: Evaluates proposals via Replay & Shadow Evaluators.             |
                          |                                                   | [!] OSCILLATE RULE: Strictly rejects flapping thresholds.                            |
                          |                                                   | [!] STABILITY CHECK: Requires mathematical stability before rule commit.             |
                          +===================================================| [STAGE 8] PATTERN: Extracts semantic patterns -> Singleton RAG Factory (C0).        |
                                                                              | [STAGE 9] COMMIT: Activator commits proven `ChangePackages` to VersionStore.         |
                                                                              | [!] INJECTION RULE: Dual Injection required (VersionStore + ApprovalGate).           |
                                                                              +--------------------------------------------------------------------------------------+
======================================================================================================================================================================
  CORE META-LEARNING DATA CONTRACTS
======================================================================================================================================================================
| [14] ChangePackage        : [source, target, changes:bytes, confidence:float, reason:tuple, timestamp_utc] -> proposal_only=True by default.                 |
| [15] CommitProofInvariant : Proof MUST bind to true implementation commit. No churn commits permitted.                                                           |
======================================================================================================================================================================
