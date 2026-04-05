==============================================================================================================================
  AGENTIC SYSTEM — PROCESS MAP  (box-and-arrow / feedback-loop view)
  Read: https://github.com/... for layer sovereignty rules
==============================================================================================================================

  LAYER SOVEREIGNTY  ·  upward mutation FORBIDDEN  ·  dynamic runtime mutation FORBIDDEN
  ┌─────────────┬────────────┬──────────────┬─────────────┬─────────────┬─────────────┐
  │ L1: Propose │ L0: Route  │ L5: Certify  │ L2: Execute │ L4: Persist │ L6: Observe │
  └─────────────┴────────────┴──────────────┴─────────────┴─────────────┴─────────────┘

==============================================================================================================================
  [1]  DOMAIN APPS  (zero internal authority — emit raw "what")
==============================================================================================================================

     +----------------------+       +----------------------+       +----------------------+
     |   apps_lic           |       |   apps_rg            |       |   apps_shared        |
     |  (InMail Campaigns)  |       | (Resume Generation)  |       | (Cross-Domain Infra) |
     |  38 reasoning agents |       | 24 reasoning agents  |       |  9 orchestrators     |
     |  4 engines           |       | 45 engines           |       | 11 enforcement strats|
     |  => intent_delta     |       |  => intent_delta     |       |  => shared knowledge |
     |     tool_requests[]  |       |     tool_requests[]  |       |     + policies       |
     |     state_diff_prop  |       |     state_diff_prop  |       |                      |
     +----------+-----------+       +----------+-----------+       +-----------+----------+
                |                              |                               |
                | (Campaign Requests)          | (Resume Requests)             | (Shared Services)
                v                              v                               v
==============================================================================================================================
  [2]  ENTRY PRODUCERS  — L1 · L6 · L4  (run in parallel, no authority)
==============================================================================================================================

                   User Request / System Event / Admin Request
                                      |
           +---------------------------+---------------------------+
           |                           |                           |
           v                           v                           v
  +-------------------+     +---------------------+     +------------------------+
  |   L1: COGNITIVE   |     |  L6: OBSERVABILITY  |     |  L4: STATE & MEMORY    |
  |   STUDIO          |     |  & ANOMALY DETECT   |     |  & PERSISTENCE         |
  |-------------------|     |---------------------|     |------------------------|
  | P1: Priming       |     | Ingest metrics      |     | Cognitive registry     |
  | P2: Orchestration |     | Anomaly scoring     |     | Capability registry    |
  | P3: PTC Calib.    |     | Broadcast drift     |     | Workflow memory        |
  | P4: Synthesis     |     | RCA engine          |     | Telemetry ledger       |
  |                   |     | TieredVigilance     |     | L4A: Detection signals |
  | Emits: U0 prompt  |     | EntropyTelemetry    |     | L4B: Healing snapshots |
  | Cannot approve    |     | DetectionSignal     |     | L4C: Drift snapshots   |
  | Cannot execute    |     | →emit_with_l4a()    |     | L4D: ChunkManifest     |
  |                   |     |                     |     | L4E: ParentChildIndex  |
  |  +---C0 RAG----+  |     | WRITE: Structured   |     | L4F: RetrievalEval     |
  |  |seed lookup  |<-+-----|--Telemetry--------->|     | L4G: Completeness Snap |
  |  |(read, top20)|  |     |                     |     |                        |
  |  +-------------+  |     | [BROADCAST]         |     | BlackboardStore (KV)   |
  |  C0 = info only   |     | Break recursive     |     | PhaseLockStore         |
  |  no route/tier    |     | cycles → Path D     |     | PromptVersionStore     |
  |  mutation         |     |                     |     | PromotionAuthority     |
  +--------+----------+     +---------+-----------+     +-----------+------------+
           |                          |                             |
           | U0 query                 | telemetry write             | state reads
           v                          v                             |
  +-------------------+     +---------------------+                |
  | EVALUATION SPINE  |     | EVALUATION          |                |
  | [Quality & Optim] |     | INTEGRATION         |                |
  |-------------------|     |---------------------|                |
  | Metrics: P@K, MRR |     | EvalSnapshot → L4   |                |
  | Groundedness      |     | DriftAlert  → L6    |                |
  | ReciprocalRankFus |     | ImprovProposal      |                |
  | HeuristicReranker |     |   → Meta-Learning   |                |
  | RetrievalPipeline |     | DPOBatch → L4       |                |
  | Chunking variants |     | EvalSummary → L6    |                |
  | CompletenessMonit |     +----------+----------+                |
  | DPOBatchBuilder   |                |                           |
  | OfflineEvalRunner |                v (eval snapshots)          |
  +--------+----------+                                            |
           |                                                       |
           v (quality metrics + improvement signals)               |
  [→ Observability & Meta-Learning Bus]                            |
           |                                                       |
           +-------------------------------------------------------+
           |
           v
==============================================================================================================================
  [3]  C0 RAG PIPELINE  (informational only — no route/safety/tier mutation)
==============================================================================================================================

  User Query (U0)
       |
       v
  +---------------------------+
  | 1. EMBED QUERY            |
  |    → ephemeral query vec  |
  +---------------------------+
       |
       +---------(union)--------+
       |                        |
       v                        v
  +-------------+        +-------------+
  | 2a. VECTOR  |        | 2b. LEXICAL |
  |   CANDIDATES|        |   RETRIEVAL |
  | cosine/FAISS|        |  BM25/exact |
  +------+------+        +------+------+
         |                      |
         +-------(fusion)-------+
                    |
                    v
  +---------------------------+
  | 3. CANDIDATE FUSION       |
  |    ScoreFusion / RRF      |
  |    dedupe by chunk_id     |
  +---------------------------+
                    |
                    v
  +---------------------------+
  | 4. PARENT-CHILD EXPANSION |
  |    child → parent+sibling |
  +---------------------------+
                    |
                    v
  +---------------------------+
  | 5. COMPLETENESS SCORING   |
  |    condition/exception/   |
  |    scope/temporal signals |
  |    score → L6 + L4G       |
  +---------------------------+
                    |
                    v
  +---------------------------+
  | 6. COMPLETENESS RERANKER  |
  |    relevance + complete.  |
  +---------------------------+
                    |
                    v
  +---------------------------+
  | 7. TOP-K + SUPPORT VALID  |
  |    sentence coverage chk  |
  |    → L4F (observe only)   |
  +---------------------------+
                    |
                    v (C0 context — informational only, bypasses routing)
             [C0 → ASSEMBLY]

==============================================================================================================================
  [4]  L5 SAFETY ENFORCEMENT PLANE  (cross-cutting — consulted by ALL layers)
==============================================================================================================================

     L1 emits intent  ·  L1 emits anomaly  ·  L1 emits C0 dependency
                              |
                              v
     +----------------+  +----------------+  +----------------+  +----------------+
     | [1] CLASSIF.   |  | [2] STRUCTURE  |  | [3] AGENT REG  |  | [4] SOVEREIGN  |
     |    KERNEL      |<>|    BLUEPRINT   |<>|  (FROZEN SSOT) |<>|   LLM GATEWAY  |
     |----------------|  |----------------|  |----------------|  |----------------|
     | FileType (AST) |  | Territory enf. |  | Agent profiles |  | Sole LLM egress|
     | 19-priority Q  |  | Path allow/deny|  | Exec modes     |  | Provider abstr.|
     | LRU cache 1024 |  | Test placement |  | Model allowlist|  | Injection detec|
     | Zero deps      |  | 62 components  |  | registry_diges |  | Hash-chain aud.|
     +-------+--------+  +-------+--------+  +-------+--------+  +-------+--------+
             |                   |                    |                   |
             | L0/L2/L6          | CI/L2              | L0/L2/L2.3        | L2 agents
             v                   v                    v                   v
       [agent discov.]    [path allow/deny]    [profile lookup]   [LLM routing]
       [file valid.]      [cross-domain blk]   [allowlist chk]    [model resolv.]
       [audit categ.]     [test placement]     [digest incl.]     [replay supp.]
             |                   |                    |                   |
             +-------------------+--------------------+-------------------+
                                            |
                                            v (L5 checks passed)
                              [SEE: L5 Safety Enforcement Plane.md]

==============================================================================================================================
  [5]  L0 ROUTING  +  META-LEARNING BUS  (authority node — central traffic control)
==============================================================================================================================

              L5 certified ──────────────────────────────────────────────────> L4 state reads
                    |                                                               |
                    v                                                               |
  +--------------------------------------+      +--------------------------------+ |
  |  L0 – ROUTING                        |      |  META-LEARNING & OPTIM. BUS   |<+
  |  (Central Traffic Control)           |      |  Stage order IMMUTABLE:        |
  |--------------------------------------|      |  AUDIT→TELEM→CFG→SNAP→RCA→     |
  | Classify intent vs L4 routing state  |      |  PROPOSE→VALIDATE→INTAKE→CMT  |
  | JIT context via Elevator Shaft       |      |--------------------------------|
  | Cannot evaluate / cannot execute     |      | S1 AUDIT     read audit slice  |
  |                                      |      | S2 TELEMETRY read events       |===> Writes optimized
  | P1: Assign TraceID + PolicyHash      |      | S3 CONFIG    get configs       |     rules &
  | P2: Deterministic election           |      | S4 SNAPSHOT  engine+cfg+clock  |     checkpoints
  | P3: Tool budget arbitration          |      | S5 RCA       analyze failures  |     → L0/L1/L4
  | P4: Seal + dispatch signed plan      |      |              ↑                 |
  |                                      |      | (all three ML signals below)   |
  | ML signals ──────────────────────────+────> | S6 PROPOSE   L0/RAG/L1/L5     |
  | [1] Pattern Analysis (intent logs)   |      |              + DPO/RLHF        |
  | [2] Threshold Tuning (risk limits)   |      | S7 VALIDATE  Replay+Shadow+    |
  | [3] Path Optimization (routing)      |      |              Dampening+Oscill. |
  |                                      |      | S8 INTAKE    HealingOutcome+   |
  | Agent Exec Profile Enforcement:      |      |    HEAL-OPT  Config optimizer  |
  | LOW=deterministic / HIGH=LLM-only    |      |    PATTERN   PatternAnalysis   |
  | Unregistered → HARD FAIL             |      |    EMBED     semantic ctx C0   |
  | Registry hash in determinism digest  |      | S9 COMMIT    proposal_only=T   |
  |                                      |      |    ApprovalGate → VersionStore |
  | ShadowRouterClassifier (drift detect)|      |    → Activator (dual inject    |
  | TimeshiftRouter (N+1 from signals)   |      |      REQUIRED or HARD FAIL)    |
  | EscalationRouter (prior violations)  |      +--------------------------------+
  | MetaLearningBus FIFO queue           |
  | ConfigStore (time-shifted configs)   |
  +--------------------------------------+
               |
               v (dispatches signed execution plan)

==============================================================================================================================
  [6]  ASSEMBLY STAGE  (sandbox airlock — deterministic composition)
==============================================================================================================================

                    C0 RAG context ──────────────────────────┐
                    Signed plan from L0 ────────────────────>│
                                                             │
  +---------------------------------------------------------+│
  |  ASSEMBLY STAGE                                         |│
  |---------------------------------------------------------|<
  |  [S0] System prompt    — hard-coded constitutions (L4)  |
  |  [I0] Instructional    — identity / mixin behaviors (L4)|
  |  [D0] Injections       — semantic fences / tool fences  |
  |  [C0] Dependency       — RAG injected knowledge (C0)    |
  |  [U0] User prompt      — raw intent from L1             |
  |                                                         |
  |  BLOCK hostile input vectors                            |
  |  SPLIT into atomic tasks (limit scope)                  |
  |  => Governed Payload → Paths A / B / C / D             |
  +---------------------------------------------------------+
               |
               v (governed payload)
               +────────────────┬───────────────┬──────────────────+
               |                |               |                  |
               v                v               v                  v

==============================================================================================================================
  [7]  EXECUTION PATHS  A / B / C / D
==============================================================================================================================

  +================+   +=================+   +=================+   +==================+
  | PATH A         |   | PATH B          |   | PATH C          |   | PATH D           |
  | Read-Only Resp |   | Policy-Check 1st|   | Direct Script   |   | Human Review 1st |
  +================+   +=================+   +=================+   +==================+
          |                    |                     |                      |
          v                    v                     v                      v
  +-------+--------+   +-------+--------+   +-------+--------+   +---------+--------+
  | Final Response |   | L3: ORCHEST.   |   | L3: ORCHEST.   |   | HUMAN REVIEW     |
  | No mutation    |   |----------------|   |----------------|   |------------------|
  | Logged outcome |   | Seq Handshake  |   | Seq Handshake  |   | MODIFY_DIFF must |
  |                |   | Conflict Arb.  |   | Conflict Arb.  |   | ref plan_hash    |
  |                |   | Dedup tools    |   | Eval vs DAG    |   | Zero authority   |
  |                |   | Gate halluc.   |   | Seq branches   |   | DPO → RLHF       |
  |                |   | Force heal     |   | Coord agents   |   |                  |
  |                |   | Eval vs DAG    |   | Route/escalate |   | [Drift Monitor]--|---> Meta-Learning
  |                |   | HSM states     |   |                |   | [Policy Monitor]-|---> L0/L5 tune
  |                |   | NervousSystem  |   |                |   +------------------+
  |                |   | MCPRegistrar   |   |                |            |
  |                |   | ReasoningIntens|   |                |            | (if approved/modified)
  |                |   +-------+--------+   +-------+--------+            |
  |                |           |                     |                    |
  |                |           v                     v                    |
  |                |   +-------+----------------------------------------------+
  |                |   |  L5: SAFETY  [cross-path guard]                       |
  |                |   |-------------------------------------------------------|
  |                |   | Risk tier classify · Compliance hash/stamp             |
  |                |   | Validate proposal vs policy                            |
  |                |   | Enforce → Approve / Remediate / Reject                 |
  |                |   | RE-CLEAR mandatory for human MODIFY_DIFF               |
  |                |   | ML: policy optimization → Meta-Learning                |
  |                |   +-------+----------------------------------------------+
  |                |           |                     |
  |                |           | (Pass)              | (Fail)
  |                |           v                     v
  |                |   [STAMP WORK CONTRACT]   [RE-ROUTE → L1]
  |                |   Sandbox permission        (rejected)
  |                |           |
  |                |           v

==============================================================================================================================
  [8]  L2 UNIFIED EXECUTION CORE  (PTC Sandbox — action & implementation factory)
==============================================================================================================================

  +===========================================================================+
  |  L2 – UNIFIED EXECUTION CORE                                              |
  |---------------------------------------------------------------------------|
  |  CAPABILITY CHOKEPOINT (G-12-3): authorize_and_execute() — EVERY call    |
  |  NETWORK EGRESS GUARD: ALL LLM HTTP → SovereignLLMGateway (no direct)    |
  |  ISOLATION: DockerSandbox.run_code() / FirecrackerManager                 |
  |  PROTOCOL: pre_commit → validate → execute → heal                         |
  |  PROVIDER BINDING: provider+model+gw_version+sem_clock digest             |
  |                                                                           |
  |  +--[P1: INIT]-----------------------------+                              |
  |  | Validate signed plan + PTC ToolBudget   |                              |
  |  | CapabilityToken: scoped + unexpired      |                              |
  |  | FREEZE clean state (disables UWG/ML/etc)|                              |
  |  | CLAIM exclusive write access            |                              |
  |  +--[P2: EXECUTE]--+    +-----------------++                              |
  |                    |    |                  |                              |
  |   Enforce ToolCall-+    | UNIVERSAL WRITE  |   ML Feedback Signals:      |
  |   → ToolResult schema   | GATEWAY (UWG)    |   [Failure Classifier] ──────+──> Meta-Learning
  |   STDOUT: structured,   | sole mutation    |   [Resource Predictor] ──────+──> Meta-Learning
  |   max-bytes capped      | authority        |   [RL Rollback Refiner]──────+──> Meta-Learning
  |   CID Registry:         | replay_mode →    |                              |
  |   immutable cycle track | simulate diffs   |   EXTERNAL RAG (C0 only):   |
  |   declare effect class  | Non-UWG → Error  |   Local FAISS (BLAS locked) |
  |   undeclared → abort    +------------------+   SHA-256 integrity check   |
  |   CEIL: terminate stuck compute cycles                                    |
  |                                                                           |
  |  +--[P3: EVALUATE / HEAL]------------------------------------------+     |
  |  |                                                                  |     |
  |  |   Result ──(Pass)──────────────────────────────────────────────> |     |
  |  |           ──(Fail)──> L2.3 CONFIDENCE-TIER HEALING              |     |
  |  |                        |                                         |     |
  |  |   EscalationContext ──>| FailureSignal ──> tier router           |     |
  |  |   heal_confidence ────>| LOCAL(≥0.75) / QWEN(≥0.40) / GEMINI   |     |
  |  |   retry_count ≥3 ─────> force GEMINI                            |     |
  |  |   healer result ──────>| HealCheckResult → needs_llm_escalation |     |
  |  |                        |        |                                |     |
  |  |                        | (loop back to execute on heal success)  |     |
  |  +--[P4: SYNTHESIZE]-------+---------+-------------------------------+     |
  |     Aggregate outputs · Validate schema · Final artifact                   |
  |     EMIT PTC ToolTranscript ONLY  (context isolation enforced)             |
  |     [SEE: Zero Loss Determinism & Replay Core.md]                          |
  |     [SEE: PTC.md — ~37% token compression]                                 |
  |     [SEE: Healing & Escalation Loop.md]                                    |
  +===========================================================================+
               |                              |
               | (filtered ToolTranscript)    | (sandbox transcript → L4/L6)
               v                              v

==============================================================================================================================
  [9]  OUTCOME  +  FEEDBACK LOOPS
==============================================================================================================================

  +------------------------------------+
  |  FINAL DECISION / OUTCOME LOGGING  |
  |------------------------------------|
  |  Answer via ToolTranscript only    |
  |  ExecutionTrace audit envelope     |
  |  UPDATE team memory & ledger       |
  |  RECONCILE data vs reality         |
  |  Metrics: latency, accuracy, cost, |
  |           human correction rate    |
  +------------------+-----------------+
                     |
                     v (commits final state to Activity Ledger → L4)
                     |
  ┌──────────────────+──────────────────────────────────────────────────────────┐
  │  FEEDBACK LOOPS                                                              │
  ├──────────────────────────────────────────────────────────────────────────────┤
  │                                                                              │
  │  L2 ML signals ──────────────────────────────────────────> Meta-Learning    │
  │  L2 healer outcome ──> HealingOutcomeAggregator ─────────> Meta-Learning    │
  │  Eval Spine metrics ─────────────────────────────────────> Meta-Learning    │
  │  Path D human decisions ─> DPOPair ──> RLHF ─────────────> Meta-Learning    │
  │  L6 anomaly/drift ───────────────────────────────────────> Meta-Learning    │
  │                                                                              │
  │  Meta-Learning S9 COMMIT ────> Updated rules/checkpoints ──> L0/L1/L4      │
  │  Meta-Learning S6 PROPOSE ───> L0ThresholdTuner / CompletenessRAGProposer  │
  │                                                                              │
  │  L6 vigilance ───────────────> L0 re-route                                  │
  │  L6 broadcast (rec. cycle) ──> STALL → Path D                               │
  │  L5 fail ────────────────────> RE-ROUTE → L1                                │
  │  C0 RAG context ─────────────> Assembly (info only, no tier mutation)       │
  │  Eval Integration ───────────> ImprovementProposal → Meta-Learning          │
  │                                                                              │
  └──────────────────────────────────────────────────────────────────────────────┘
