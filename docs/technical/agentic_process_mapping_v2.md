======================================================================================================================================================
  AGENTIC SYSTEM — PROCESS MAP                          FEEDBACK RAIL (arrows flow bottom-to-top on right)
======================================================================================================================================================
  LAYER SOVEREIGNTY: upward mutation FORBIDDEN · dynamic runtime mutation (monkeypatch/setattr/reload) FORBIDDEN
  L1:Propose  L0:Route  L5:Certify  L2:Execute  L4:Persist  L6:Observe
======================================================================================================================================================
                                                                                    ^(ML rules/chkpts)  ^(RAG/prompt weights)  ^(L6 vigilance re-route)
  FEEDBACK TARGETS:                                                                 |                   |                      |
  [A] Meta-Learning S9 ──> L0 updated rules    ──────────────────────────────────> +---[A: L0]         |                      |
  [B] Meta-Learning S9 ──> L1 RAG/prompt weights ──────────────────────────────────────────> +--[B:L1] |                      |
  [C] L6 vigilance   ──> L0 immediate re-route ──────────────────────────────────────────────────────> +--[C:L6->L0]
  [D] L5 fail        ──> RE-ROUTE back to L1   (shown inline at [4])
  [E] L6 broadcast   ──> STALL + force Path D  (shown inline at [2])
======================================================================================================================================================
  [1]  DOMAIN APPS  (zero internal authority — emit raw "what")                     |                   |                      |
======================================================================================================================================================
                                                                                    |                   |                      |
     +----------------------+    +----------------------+    +--------------------+ |                   |                      |
     |   apps_lic           |    |   apps_rg            |    |   apps_shared      | |                   |                      |
     |  (InMail Campaigns)  |    | (Resume Generation)  |    | (Cross-Domain)     | |                   |                      |
     |  38 agents · 4 eng   |    | 24 agents · 45 eng   |    |  9 orchestrators   | |                   |                      |
     |  => intent_delta     |    |  => intent_delta     |    |  => shared know.   | |                   |                      |
     |     tool_requests[]  |    |     tool_requests[]  |    |     + policies     | |                   |                      |
     |     state_diff_prop  |    |     state_diff_prop  |    |                    | |                   |                      |
     +----------+-----------+    +----------+-----------+    +---------+----------+ |                   |                      |
                |                           |                          |             |                   |                      |
                +---------------------------+--------------------------+             |                   |                      |
                                            |                                        |                   |                      |
                                            v (raw requests — no authority)          |                   |                      |
======================================================================================================================================================
  [2]  ENTRY PRODUCERS — L1 · L6 · L4  (parallel, no authority)                    |                   |                      |
======================================================================================================================================================
                                                                                    |                   |                      |
              User Request / System Event / Admin Request                           |                   |                      |
                                 |                                                  |                   |                      |
           +---------------------+---------------------+                           |                   |                      |
           |                     |                     |                           |                   |                      |
           v                     v                     v                           |                   |                      |
  +------------------+  +-------------------+  +----------------------+            |                   |                      |
  |  L1: COGNITIVE   |  | L6: OBSERVABILITY |  |  L4: STATE & MEMORY  |            |                   |                      |
  |  STUDIO          |  | & ANOMALY DETECT  |  |  & PERSISTENCE       |            |                   |                      |
  |------------------|  |-------------------|  |----------------------|            |                   |                      |
  | P1: Priming      |  | Ingest metrics    |  | Cognitive registry   |            |                   |                      |
  | P2: Orchestrate  |  | Anomaly scoring   |  | Capability registry  |            |                   |                      |
  | P3: PTC Calib.   |  | Broadcast drift   |<-+--[E] recursive cycle |            |                   |                      |
  | P4: Synthesis    |  |   -> STALL+PathD  |  |   detected -> stall  |            |                   |                      |
  | Emits: U0 prompt |  | RCA engine        |  | Workflow memory      |            |                   |                      |
  | Cannot approve   |  | TieredVigilance --+--+--[C]-> L0 re-route ──+────────────+───────────────────+──────────────────────+
  | Cannot execute   |  | DetectionSignal   |  | Telemetry ledger     |            |                   |                      |
  |                  |  | emit_with_l4a()   |  | L4A: Detect signals  |            |                   |                      |
  | +--C0 RAG------+ |  |                   |  | L4B: Heal snapshots  |            |                   |                      |
  | |seed lookup   | |  | WRITE: Telemetry  |  | L4C: Drift snapshots |            |                   |                      |
  | |(read, top20) |<+--+------------------>|  | L4D: ChunkManifest   |            |                   |                      |
  | +---+----------+ |  |                   |  | L4E: ParentChildIdx  |            |                   |                      |
  | C0=info only     |  |                   |  | L4F: RetrievalEval   |            |                   |                      |
  | no tier mutation |  |                   |  | L4G: CompletenessSnap|            |                   |                      |
  +--------+---------+  +--------+----------+  +-----------+----------+            |                   |                      |
           |                     |                          |                       |                   |                      |
           | U0 query            | telemetry                | state reads           |                   |                      |
           v                     v                          |                       |                   |                      |
  +------------------+  +-------------------+              |                       |                   |                      |
  | EVALUATION SPINE |  | EVAL INTEGRATION  |              |                       |                   |                      |
  | [Quality+Optim]  |  |-------------------|              |                       |                   |                      |
  |------------------|  | EvalSnapshot->L4  |              |                       |                   |                      |
  | P@K, MRR, NDCG   |  | DriftAlert->L6    |              |                       |                   |                      |
  | Groundedness     |  | ImprovProposal--->+----[signals]->+---------------------->+───────────────────+> Meta-Learning S6    |
  | RRF + Reranker   |  | DPOBatch->L4      |              |                       |                   |                      |
  | Completeness Mon |  | EvalSummary->L6   |              |                       |                   |                      |
  | DPOBatchBuilder  |  +-------------------+              |                       |                   |                      |
  +--------+---------+                                     |                       |                   |                      |
           |                                               |                       |                   |                      |
           v                                               |                       |                   |                      |
======================================================================================================================================================
  [3]  C0 RAG PIPELINE  (informational only — no route/safety/tier mutation)        |                   |                      |
======================================================================================================================================================
                                                                                    |                   |                      |
  +------------------+                                                              |                   |                      |
  | 1. EMBED QUERY   |  U0 → ephemeral query vector                                 |                   |                      |
  +--------+---------+                                                              |                   |                      |
           |                                                                        |                   |                      |
           +----------(union)----------+                                            |                   |                      |
           |                           |                                            |                   |                      |
           v                           v                                            |                   |                      |
  +------------------+       +------------------+                                  |                   |                      |
  | 2a. VECTOR CANDS |       | 2b. LEXICAL RET. |                                  |                   |                      |
  |  cosine / FAISS  |       |  BM25 / exact    |                                  |                   |                      |
  +--------+---------+       +--------+---------+                                  |                   |                      |
           |                          |                                             |                   |                      |
           +----------(fusion)--------+                                             |                   |                      |
                       |                                                            |                   |                      |
                       v                                                            |                   |                      |
  +------------------+-+                                                            |                   |                      |
  | 3. CAND. FUSION  |   ScoreFusion / RRF · dedupe by chunk_id                    |                   |                      |
  +--------+---------+                                                              |                   |                      |
           v                                                                        |                   |                      |
  +------------------+                                                              |                   |                      |
  | 4. PARENT-CHILD  |   child chunk -> parent section + sibling window             |                   |                      |
  +--------+---------+                                                              |                   |                      |
           v                                                                        |                   |                      |
  +------------------+                                                              |                   |                      |
  | 5. COMPLETENESS  |   condition / exception / scope / temporal signals           |                   |                      |
  |    SCORING       |   ContextCompletenessScore ──> L6 telemetry + L4G            |                   |                      |
  +--------+---------+                                                              |                   |                      |
           v                                                                        |                   |                      |
  +------------------+                                                              |                   |                      |
  | 6. COMPLETENESS  |   blend: relevance_weight + completeness_weight              |                   |                      |
  |    RERANKER      |                                                              |                   |                      |
  +--------+---------+                                                              |                   |                      |
           v                                                                        |                   |                      |
  +------------------+                                                              |                   |                      |
  | 7. TOP-K +       |   IAnswerSupportValidator: sentence-coverage check           |                   |                      |
  |    SUPPORT VALID |   SupportedAnswerCheck ──> L4F (observe only)                |                   |                      |
  +--------+---------+                                                              |                   |                      |
           |                                                                        |                   |                      |
           v  (C0 context — informational only, bypasses routing logic)             |                   |                      |
      [C0 ──> ASSEMBLY at [6]]                                                      |                   |                      |
                                                                                    |                   |                      |
======================================================================================================================================================
  [4]  L5 SAFETY ENFORCEMENT PLANE  (cross-cutting — consulted by ALL layers)       |                   |                      |
======================================================================================================================================================
                                                                                    |                   |                      |
  L1 emits intent · L1 emits anomaly · L1 emits C0 dependency                      |                   |                      |
                           |                                                         |                   |                      |
                           v                                                         |                   |                      |
  +--------------+  +--------------+  +--------------+  +--------------+            |                   |                      |
  | [1] CLASSIF. |  | [2] STRUCT.  |  | [3] AGENT    |  | [4] SOVR.    |            |                   |                      |
  |    KERNEL    |<>|    BLUEPRINT |<>|    REGISTRY  |<>|    LLM GW    |            |                   |                      |
  |--------------|  |--------------|  |--------------|  |--------------|            |                   |                      |
  | FileType AST |  | Territory    |  | Agent profls |  | Sole egress  |            |                   |                      |
  | 19-priority Q|  | Path val.    |  | Exec modes   |  | Prov. abstr. |            |                   |                      |
  | LRU 1024     |  | Test SSOT    |  | Allowlists   |  | Inject detec |            |                   |                      |
  | Zero deps    |  | 62 compon.   |  | reg_digest() |  | Hash audit   |            |                   |                      |
  +------+-------+  +------+-------+  +------+-------+  +------+-------+            |                   |                      |
         |                 |                 |                 |                     |                   |                      |
         +─────────────────+─────────────────+─────────────────+                    |                   |                      |
                                       |                                             |                   |                      |
                           (L5 checks passed)                                        |                   |                      |
                                       |                                             |                   |                      |
         [D] L5 FAIL ──> RE-ROUTE ─────+──────────────────────────────────────────> +--[B:L1 re-entry]  |                      |
                                       |                                             |                   |                      |
                                       v                                             |                   |                      |
======================================================================================================================================================
  [5]  L0 ROUTING  +  META-LEARNING BUS                                             |                   |                      |
======================================================================================================================================================
                                                                                    |                   |                      |
  +------------------------------------+     +----------------------------------+   |                   |                      |
  |  L0 – ROUTING                      |     |  META-LEARNING & OPTIM. BUS      |   |                   |                      |
  |  (Central Traffic Control)         |     |  IMMUTABLE stage order:          |<──+───────────────────+  (receives all       |
  |------------------------------------|     |  S1 AUDIT -> S2 TELEM -> S3 CFG  |   |                       feedback signals)  |
  | Classify intent vs L4 state        |     |  -> S4 SNAP -> S5 RCA -> S6 PROP |   |                   |                      |
  | JIT context via Elevator Shaft     |     |  -> S7 VAL -> S8 INTAKE -> S9 CMT|   |                   |                      |
  | Cannot evaluate / cannot execute   |     |----------------------------------|   |                   |                      |
  | P1: Assign TraceID + PolicyHash    |     | S1 AUDIT     read audit slice    |   |                   |                      |
  | P2: Deterministic election         |     | S2 TELEMETRY read events         |   |                   |                      |
  | P3: Tool budget arbitration        |     | S3 CONFIG    get configs         |   |                   |                      |
  | P4: Seal + dispatch signed plan    |     | S4 SNAPSHOT  engine+cfg+clock   |   |                   |                      |
  |                                    |     | S5 RCA       analyze failures    |   |                   |                      |
  | ML signals (all -> S6 PROPOSE):    |     | S6 PROPOSE   L0/RAG/L1/L5 order |   |                   |                      |
  | [1] Pattern Analysis (intent logs) +---->|              + DPO/RLHF         |   |                   |                      |
  | [2] Threshold Tuning (risk limits) +---->| S7 VALIDATE  Replay+Shadow+Damp |   |                   |                      |
  | [3] Path Optimization (routing)    +---->| S8 INTAKE    HealingOutcome+     |   |                   |                      |
  |                                    |     |    HEAL-OPT  Config optimizer    |   |                   |                      |
  | Agent Exec Profile Enforcement:    |     |    PATTERN   PatternAnalysis     |   |                   |                      |
  | LOW=deterministic / HIGH=LLM-only  |     |    EMBED     semantic ctx (C0)   |   |                   |                      |
  | Unregistered -> HARD FAIL          |     | S9 COMMIT    proposal_only=True  |   |                   |                      |
  | Registry hash in determinism digest|     |    ApprovalGate -> VersionStore  |   |                   |                      |
  | ShadowRouterClassifier (drift)     |     |    -> Activator (dual inject req)|   |                   |                      |
  | TimeshiftRouter (N+1 signals)      |     +────────────┬─────────────────────+   |                   |                      |
  | EscalationRouter (prior violations)|                  |                         |                   |                      |
  | MetaLearningBus FIFO queue         |       S9 COMMIT writes optimized rules      |                   |                      |
  +------------------------------------+                  |                         |                   |                      |
               |                                          +─────────────────────────+───────────────────+  [A][B] back to L0/L1|
               v (dispatches signed execution plan)                                 |                   |                      |
======================================================================================================================================================
  [6]  ASSEMBLY STAGE  (sandbox airlock — deterministic composition)                |                   |                      |
======================================================================================================================================================
                                                                                    |                   |                      |
  C0 RAG context (from [3]) ──────────────────────────────────────────┐            |                   |                      |
  Signed plan from L0 ────────────────────────────────────────────────+──>         |                   |                      |
                                                                       |            |                   |                      |
  +------------------------------------------------------------------++            |                   |                      |
  |  ASSEMBLY STAGE                                                   |            |                   |                      |
  |-------------------------------------------------------------------|            |                   |                      |
  |  [S0] System prompt    — hard-coded constitutions (L4)            |            |                   |                      |
  |  [I0] Instructional    — identity / mixin behaviors (L4)          |            |                   |                      |
  |  [D0] Injections       — semantic fences / tool fences (L5)       |            |                   |                      |
  |  [C0] Dependency       — RAG injected knowledge (info only)       |            |                   |                      |
  |  [U0] User prompt      — raw intent from L1                       |            |                   |                      |
  |  BLOCK hostile input vectors                                      |            |                   |                      |
  |  SPLIT into atomic tasks · => Governed Payload -> Paths A/B/C/D  |            |                   |                      |
  +------------------------------------------------------------------+            |                   |                      |
               |                                                                    |                   |                      |
               v (governed payload)                                                 |                   |                      |
               +──────────────┬─────────────────┬────────────────────+             |                   |                      |
               |              |                 |                    |              |                   |                      |
               v              v                 v                    v              |                   |                      |
======================================================================================================================================================
  [7]  EXECUTION PATHS  A / B / C / D                                               |                   |                      |
======================================================================================================================================================
                                                                                    |                   |                      |
  +============+  +==============+  +==============+  +===================+         |                   |                      |
  | PATH A     |  | PATH B       |  | PATH C       |  | PATH D            |         |                   |                      |
  | Read-Only  |  | Policy 1st   |  | Direct Exec  |  | Human Review 1st  |         |                   |                      |
  +============+  +==============+  +==============+  +===================+         |                   |                      |
        |                |                 |                   |                    |                   |                      |
        v                v                 v                   v                    |                   |                      |
  +-----+------+  +------+------+  +-------+------+  +--------+----------+         |                   |                      |
  | Final Resp |  | L3:ORCHEST. |  | L3:ORCHEST.  |  | HUMAN REVIEW      |         |                   |                      |
  | No mutation|  |-------------|  |--------------|  |-------------------|         |                   |                      |
  | Logged     |  | Seq HS      |  | Seq HS       |  | MODIFY_DIFF must  |         |                   |                      |
  |            |  | Conflict Arb|  | Eval vs DAG  |  | ref plan_hash     |         |                   |                      |
  |            |  | Dedup tools |  | Seq branches |  | Zero authority    |         |                   |                      |
  |            |  | Gate halluc.|  | Coord agents |  | Drift Monitor ────+─────────+───────────────────+> Meta-Learning S6    |
  |            |  | HSM states  |  | Route/escal. |  | Policy Monitor ───+─────────+───────────────────+> L0/L5 thresholds   |
  |            |  | NervousSystem  |              |  | DPO pair -> RLHF ─+─────────+───────────────────+> Meta-Learning S6   |
  |            |  | MCPRegistrar|  |              |  +--------+----------+         |                   |                      |
  |            |  | ReasoningInt|  |              |           |                    |                   |                      |
  |            |  +------+------+  +-------+------+           | (if approved)      |                   |                      |
  |            |         |                 |                   |                    |                   |                      |
  |            |         v                 v                   |                    |                   |                      |
  |            |  +------+-------------------------------------------+             |                   |                      |
  |            |  |  L5: SAFETY  [cross-path guard]                   |             |                   |                      |
  |            |  |---------------------------------------------------|             |                   |                      |
  |            |  | Risk tier classify · Compliance hash/stamp        |             |                   |                      |
  |            |  | Validate proposal vs policy                       |             |                   |                      |
  |            |  | Enforce -> Approve / Remediate / Reject           |             |                   |                      |
  |            |  | RE-CLEAR mandatory for human MODIFY_DIFF          |             |                   |                      |
  |            |  | ML optimization signal ───────────────────────────+─────────────+───────────────────+> Meta-Learning S6   |
  |            |  +------+----------------------------+--------------+             |                   |                      |
  |            |         |                            |                             |                   |                      |
  |            |    (Pass)|                      (Fail)|                            |                   |                      |
  |            |         v                            v                             |                   |                      |
  |            |  [STAMP WORK CONTRACT]     [D] RE-ROUTE ──────────────────────────+> L1 re-entry      |                      |
  |            |  [sandbox permission]                                              |                   |                      |
  |            |         |                                                          |                   |                      |
  |            |         v                                                          |                   |                      |
======================================================================================================================================================
  [8]  L2 UNIFIED EXECUTION CORE  (PTC Sandbox)                                     |                   |                      |
======================================================================================================================================================
                                                                                    |                   |                      |
  +============================================================================+   |                   |                      |
  |  L2 – UNIFIED EXECUTION CORE                                               |   |                   |                      |
  |----------------------------------------------------------------------------|   |                   |                      |
  |  CAPABILITY CHOKEPOINT (G-12-3): authorize_and_execute() on EVERY call     |   |                   |                      |
  |  NETWORK EGRESS GUARD: ALL LLM HTTP -> SovereignLLMGateway (no direct)     |   |                   |                      |
  |  ISOLATION: DockerSandbox.run_code() / FirecrackerManager                  |   |                   |                      |
  |  PROTOCOL: pre_commit -> validate -> execute -> heal                        |   |                   |                      |
  |                                                                             |   |                   |                      |
  |  +--[P1: INIT]-------------------------------+                              |   |                   |                      |
  |  | Validate signed plan + PTC ToolBudget     |                              |   |                   |                      |
  |  | CapabilityToken: scoped + unexpired        |                              |   |                   |                      |
  |  | FREEZE clean state · CLAIM write access   |                              |   |                   |                      |
  |  +--[P2: EXECUTE]----+  +-------------------++                              |   |                   |                      |
  |   Enforce ToolCall   |  | UNIVERSAL WRITE    |  ML Feedback Signals:        |   |                   |                      |
  |   -> ToolResult sch. |  | GATEWAY (UWG)      |  Failure Classifier ─────────+───+───────────────────+> Meta-Learning S6   |
  |   STDOUT: structured |  | sole mutation auth |  Resource Predictor ─────────+───+───────────────────+> Meta-Learning S6   |
  |   CID Registry track |  | replay -> sim diffs|  RL Rollback Refiner ────────+───+───────────────────+> Meta-Learning S6   |
  |   declare effect cls |  | Non-UWG -> Error   |                              |   |                   |                      |
  |   undeclared -> abort+--+--------------------+  C0 RAG (read-only):         |   |                   |                      |
  |   CEIL: terminate stuck cycles                   FAISS BLAS locked           |   |                   |                      |
  |                                                  SHA-256 integrity check     |   |                   |                      |
  |  +--[P3: EVALUATE / HEAL]---------------------------------------+            |   |                   |                      |
  |  |  Result ──(Pass)──────────────────────────────────────────> |            |   |                   |                      |
  |  |          ──(Fail)──> L2.3 CONFIDENCE-TIER HEALING           |            |   |                   |                      |
  |  |    EscalationContext -> FailureSignal -> tier router         |            |   |                   |                      |
  |  |    heal_confidence: LOCAL(>=0.75) / QWEN(>=0.40) / GEMINI   |            |   |                   |                      |
  |  |    retry_count >= 3 -> force GEMINI                          |            |   |                   |                      |
  |  |    healer result -> (loop back to execute on success)        |            |   |                   |                      |
  |  |    HealingOutcome ────────────────────────────────────────── +────────────+───+───────────────────+> Meta-Learning S8   |
  |  +--[P4: SYNTHESIZE]--------------------------------------------+            |   |                   |                      |
  |     Aggregate outputs · Validate schema · Final artifact         |            |   |                   |                      |
  |     EMIT PTC ToolTranscript ONLY (context isolation)            |            |   |                   |                      |
  +============================================================================+   |                   |                      |
               |                              |                                     |                   |                      |
               | (ToolTranscript)             | (transcript -> L4/L6)              |                   |                      |
               v                              v                                     |                   |                      |
======================================================================================================================================================
  [9]  OUTCOME  (state commits + all feedback arrows complete their loops above)    |                   |                      |
======================================================================================================================================================
                                                                                    |                   |                      |
  +---------------------------+                                                     |                   |                      |
  |  OUTCOME / LOGGING        |                                                     |                   |                      |
  |---------------------------|                                                     |                   |                      |
  |  Answer via Transcript    |                                                     |                   |                      |
  |  ExecutionTrace envelope  |                                                     |                   |                      |
  |  Update team memory       |                                                     |                   |                      |
  |  Reconcile data/reality   |                                                     |                   |                      |
  |  Metrics: latency, cost,  |                                                     |                   |                      |
  |  accuracy, correction rate|                                                     |                   |                      |
  +---------------------------+                                                     |                   |                      |
               |                                                                    |                   |                      |
               v  commits final state -> L4 Activity Ledger                         |                   |                      |
               |                                                                    |                   |                      |
  Eval Spine metrics ─────────────────────────────────────────────────────────────>+───────────────────+> Meta-Learning S6    |
  L6 anomaly / drift signals ─────────────────────────────────────────────────────>+───────────────────+> Meta-Learning S6    |
  L2 ML signals (Fail/Res/RL) already routed above at [8]                          |                   |                      |
  Path D DPO + RLHF already routed above at [7]                                    |                   |                      |
               |                                                                    |                   |                      |
               +────────────────────────────────────────────────────────────────────────────────────────────────────────────────>
                                (all loops close: Meta-Learning S9 COMMIT writes updated rules/checkpoints back to [A] L0, [B] L1, L4)
