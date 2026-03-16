████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█  META-LEARNING PIPELINE & SYSTEM LEARNING LOOP ─────────────────────────────────────────────────────────────────────── [ ARCHITECTURE OVERVIEW ] █
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

┌────────────────────────────────────┐ ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [ OBSERVABILITY & INGESTION ]      │ │ THE META-LEARNING STATE MACHINE (L4)                                                                      │
│ L1: COGNITIVE / L6: OBS            │ ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ├─ Intent Ingestion                │═│ [STAGE 1] AUDIT SNAPSHOT FREEZE: AuditStore.read_audit_slice() → error sigs & latency dists               │
│ ├─ Drift & Threat Signals          │>│ ├─ Enhanced: ADG dependency traces for blast radius analysis                                              │
│ ├─ Real-time Telemetry             │ │ └─ Immutability: Snapshot frozen at semantic clock tick T                                                 │
│ └─ ADG Dependency Tracking         │ ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
└─────────────────┬──────────────────┘ │ [STAGE 2] TELEMETRY EVENT COLLECTION: TelemetryStore.read_events() → maps agent & policy violations       │
                  │                    │ └─ Enhanced: ADG fan-in/fan-out metrics correlated with execution patterns                                │
                  │                    ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
┌─────────────────▼──────────────────┐ │ [STAGE 3] CONFIGURATION SNAPSHOT: ConfigProvider.get_current_configs() → active weights & thresholds      │
│ [ CONTROL SPINE ]                  │ │ └─ ADG Validation: Verification of import chains & configuration dependency mapping                       │
│ L0: TRAFFIC / L3: ORCH / L5: SF    │ ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ├─ Active Routing Rules            │ │ [STAGE 4] META-LEARNING SNAPSHOT ASSEMBLY: MetaLearningSnapshot(engine_version, SemanticClock)            │
│ ├─ Orchestration Weights           │ │ ├─ Core: Generates single immutable snapshot                                                              │
│ └─ Safety Thresholds               │ │ └─ ADG Digest: Includes full ADG integrity hash for graph versioning                                      │
└─────────────────▲──────────────────┘ ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
                  │                    │ [STAGE 5] ROOT CAUSE ANALYSIS (RCA): analyze_failures() → RCAReport (Blast radius via ADG traversal)      │
                  │                    │ └─ Pattern Detection: FailureFingerprinter extracts semantic signatures                                   │
                  │                    ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
                  │                    │ [STAGE 6] PROPOSAL GENERATION: L0/L1/L5/RAG Proposers generate ChangePackages (proposal_only=True)        │
                  │                    │ └─ RLHFOptimizer: Tunes thresholds via DPO batch preference analysis                                      │
            (Feedback Bus)             ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
                  │                    │ [STAGE 7] VALIDATION GAUNTLET (REGRESSION SHIELD)                                                         │
                  │                    │ ├─ Shadow & Replay Validation: Verifies performance via ADG simulation traversal                          │
                  │                    │ └─ Rejection Rules: OSCILLATE (flapping), REGRESSION (latency), VIOLATION (layer breach)                  │
                  │                    ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
                  │                    │ [STAGE 8] PATTERN EXTRACTION & LEARNING: PatternAnalysisEngine → motifs in Singleton RAG Factory (C0)     │
                  │                    │ └─ Learning: Success/Failure patterns embedded for future similarity retrieval                            │
                  │                    ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
                  └────────────────────│ [STAGE 9] COMMIT & ACTIVATION: Activator binds CommitProofInvariant to VersionStore; ADG Cache Refresh    │
                                       │ └─ Deployment: Proven config propagates to control spine via Feedback Bus                                 │
                                       └───────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CORE META-LEARNING DATA CONTRACTS & INTERACTIONS                 [ ENHANCED ACCESS: tools/adg/enhanced_redis_mcp_client.py (HASH/SET/LIST) ]     │
│ TIMESTAMP: 2026-03-14 07:56 UTC | STATUS: Deterministic Replay Enabled                                                                           │
├──────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ChangePackage        │ [changes:bytes, confidence:float, reason:tuple, adg_delta_digest] → Must pass Gauntlet to remove proposal_only flag.      │
│ CommitProofInvariant │ Proof MUST bind to implementation commit. Prevents churn/oscillation via historical causal consistency check.             │
│ PipelineConfig       │ Immutable engine settings (shadow_thresholds, enabled_proposers, oscillation_policy) governing meta-learning behavior.    │
│ PipelineDependencies │ Protocol-based injection (audit_store, rlhf_optimizer, risk_correlator) using Enhanced Redis MCP for ADG-aware analysis.  │
│ ApprovalDecision     │ Enum[APPROVE, REJECT, DEFER] → Final gate output based on RiskTier and validation results.                                │
│ RCAReport            │ [failure_category, root_cause, adg_blast_radius] → Maps failures across layers via ADG edge correlation.                  │
└──────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SYSTEM LEARNING LOOP — FAISS & EMBEDDING INTEGRATION (SIMPLIFIED FLOW)                                                                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [ EVENT ]         New Event / Failure (healing outcome, RCA signal, telemetry)                                                                   │
│   │                                                                                                                                              │
│   ▼                                                                                                                                              │
│ [ EMBEDDING ]     BGE-M3 (bmg_embed_text) | agentic_core.L2_execution.healers.bmg_embedding_similarity                                           │
│                   Converts failure_signature → 1024-dim float32 vector                                                                           │
│   │                                                                                                                                              │
│   ▼               << EmbeddingServiceFactory controls backend: [Plan A] LocalFAISSStore OR [Plan B] MetaLearningEmbeddingService (seed packs)    │
│ [ INDEX ]         LocalFAISSStore | system_learning.engines.local_faiss_store | IndexFlatIP + L2-normalisation                                   │
│                   Nearest-neighbour similarity search (top-k, cutoff via RetrievalProfile) → Yields [EmbArtifact, content_hash, score_round6]    │
│   │                                                                                                                                              │
│   ▼                                                                                                                                              │
│ [ ANALYSIS ]      PatternAnalysisEngine (W3) | system_learning.engines.pattern_analysis_engine                                                   │
│                   Deterministic semantic clustering; FailureFingerprinter extracts recurring motifs → Outputs PatternAnalysisReport (info/C0)    │
│   │                                                                                                                                              │
│   ▼                                                                                                                                              │
│ [ META-LEARN ]    HealingConfigOptimizer (thresholds) | RLHFOptimizer (DPO tuning) | L0/L1/L5/RAG Proposers (routing rules)                      │
│                   RetrievalProfileProposalManager (staged retrieval) → All outputs generate ChangePackages (proposal_only=True)                  │
│   │                                                                                                                                              │
│   ▼                                                                                                                                              │
│ [ IMPROVEMENT ]   SYSTEM IMPROVEMENT: Routing rules & healing policies committed ONLY AFTER Validation Gauntlet + ApprovalGate APPROVE.          │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┬─────────────────────────────────────────────────┬───────────────────────────────────────┐
│ WHAT FAISS DOES (LocalFAISSStore)                      │ WHAT FAISS DOES NOT DO                          │ LIBRARY ANALOGY                       │
├────────────────────────────────────────────────────────┼─────────────────────────────────────────────────┼───────────────────────────────────────┤
│ • Store vectors (IndexFlatIP, SSD seed packs)          │ • Train models (BGE-M3 weights static)          │ • LocalFAISSStore = Archive shelves   │
│ • Search similar (retrieve() → top-k nearest)          │ • Analyze failures (PatternAnalysisEngine owns) │ • BGE-M3 = Call numbers (index sys)   │
│ • Return neighbours (Artifact, hash, score_rd6)        │ • Change policies (mutation is proposal_only)   │ • EmbServiceFactory = Head Librarian  │
│ • Enforce determinism (W-C-DETERMINISM-DIGEST printed, │ • Learn patterns (RCA & PatternEngine own this) │ • PatternEngine = Research Librarian  │
│   BLAS thread lock, eps-guarded normalisation)         │                                                 │ • Optimizers = Policy Committee       │
│ • Apply kill-switch (is_disabled() env flag)           │                                                 │ • Gauntlet = Peer Review              │
└────────────────────────────────────────────────────────┴─────────────────────────────────────────────────┴───────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HOW KNOWLEDGE GROWS (EXECUTION TIMELINE)                                                                                                         │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [ RUN 1 ]  Failure A (healer_name|failure_type|component) → BGE-M3 Embed (1024-dim) → LocalFAISSStore.store() → Vector persisted in seed pack.   │
│                                                                                                                                                  │
│ [ RUN 20 ] Failure B (similar sig) → BGE-M3 Embed → LocalFAISSStore.retrieve(top_k, cutoff) → Returns neighbours (including Failure A).          │
│            PatternAnalysisEngine detects motif → PatternAnalysisReport → HealingConfigOptimizer/Proposers → ChangePackage (proposal_only=True).  │
│            Passes Validation Gauntlet → APPROVE → CommitProofInvariant → VersionStore → Routing rules & healing thresholds successfully updated! │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
