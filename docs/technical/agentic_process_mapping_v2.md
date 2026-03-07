=================================================================================================================================================================================================================
  AGENTIC SYSTEM — PROCESS MAP (ULTRA-WIDESCREEN EDITION)                                          LAYER SOVEREIGNTY: upward mutation FORBIDDEN · dynamic runtime mutation
                                                                                                   (monkeypatch/setattr/reload) FORBIDDEN
=================================================================================================================================================================================================================
  [ EXECUTION CONTROL BUS (LEFT) ]                                                                 [ META-LEARNING & TELEMETRY BUS (RIGHT) ]
  [C] L6 -> L0 : Immediate Vigilance Re-route (Flows down to L0)                                   [T] TELEMETRY  : Metrics and read events flow down to ML S2-S5
  [D] L5 -> L1 : Safety Fail Re-entry (Flows up to L1)                                             [P] PROPOSALS  : DPO/Drift/ML/Eval signals flow to ML S6/S8
  [E] L6 -> D  : Broadcast Drift -> Stall + Force Path D                                           [U] ML COMMITS : S9 Commit -> Updates L0 Rules [A] & L1 Weights [B]
=================================================================================================================================================================================================================

    [C]     [D]     [E]                                                                                                                                     [T]     [P]     [U]
     |       ^       |     [1] DOMAIN APPS (zero internal authority — emit raw "what")                                                                       |       |       ^
     |       |       |                                                                                                                                       |       |       |
     |       |       |       +-------------------------+      +-------------------------+      +-----------------------+                                     |       |       |
     |       |       |       | apps_lic                |      | apps_rg                 |      | apps_shared           |                                     |       |       |
     |       |       |       | (InMail Campaigns)      |      | (Resume Generation)     |      | (Cross-Domain)        |                                     |       |       |
     |       |       |       | 38 agents · 4 eng       |      | 24 agents · 45 eng      |      | 9 orchestrators       |                                     |       |       |
     |       |       |       | => intent_delta         |      | => intent_delta         |      | => shared know.       |                                     |       |       |
     |       |       |       |    tool_requests[]      |      |    tool_requests[]      |      |    + policies         |                                     |       |       |
     |       |       |       |    state_diff_prop      |      |    state_diff_prop      |      |                       |                                     |       |       |
     |       |       |       +------------+------------+      +------------+------------+      +-----------+-----------+                                     |       |       |
     |       |       |                    |                            |                               |                                                     |       |       |
     |       |       |                    +----------------------------+-------------------------------+                                                     |       |       |
     |       |       |                                                 |                                                                                     |       |       |
     |       |       |                                                 v (raw requests — no authority)                                                       |       |       |
=================================================================================================================================================================================================================
    [C]     [D]     [E]    [2] ENTRY PRODUCERS — L1 · L6 · L4 (parallel, no authority)                                                                      [T]     [P]     [U]
     |       |       |                            User Request / System Event / Admin Request                                                                |       |       |
     |       |       |                                                 |                                                                                     |       |       |
     |       |       |                     +---------------------------+---------------------------+                                                         |       |       |
     |       |       |                     v                           v                           v                                                         |       |       |
     |       |       |     +-------------------+       +-------------------+       +-------------------+                                                     |       |       |
     |       |       |     | L1: COGNITIVE     |       | L6: OBSERVABILITY |       | L4: STATE &       |                                                     |       |       |
     |       |       |     | STUDIO            |       | & ANOMALY DETECT  |       | PERSISTENCE       |                                                     |       |       +<---- [B] S9 -> L1 Weights
     |       |       |     |-------------------|       |-------------------|       |-------------------|                                                     |       |       |
     |       |       |     | P1: Priming       |       | Ingest metrics    |       | Cog registry      |                                                     |       |       |
     |       |       |     | P2: Orchestrate   |       | Anomaly scoring   |       | Cap registry      |                                                     |       |       |
     |       |       |     | P3: PTC Calib.    |       | RCA engine        |       | recursive cycle   |                                                     |       |       |
     |       |       |<----------------------------------| TieredVigilance |       | detected -> stall |                                                     |       |       |
     |       |       |     | P4: Synthesis     |       | DetectionSignal   |       | Workflow memory   |                                                     |       |       |
     |<----------------------| [C] re-route L0 |       | emit_with_l4a()   |       | Telemetry ledger  |                                                     |       |       |
     |       |       |     | Emits: U0 prompt  |       | WRITE: Telemetry  |---+   | L4A: Detect       |                                                     |       |       |
     |       |       |     | Cannot approve    |       +---------+---------+   |   | L4B: Heal         |                                                     |       |       |
     |       |       |     | Cannot execute    |                 |             |   | L4C: Drift        |                                                     |       |       |
     |       |       |     |                   |                 v telemetry   |   | L4D: Manifest     |                                                     |       |       |
     |       |       |     | +--C0 RAG-------+ |       +-------------------+   |   | L4E: ParChildIdx  |                                                     |       |       |
     |       |       |     | |seed lookup    | |       | EVAL INTEGRATION  |<--+   | L4F: RetEval      |                                                     |       |       |
     |       |       |     | |(read, top20)  | |       |-------------------|       | L4G: CompSnap     |                                                     |       |       |
     |       |       |     | +---+-----------+ |       | EvalSnapshot->L4  |       +---------+---------+                                                     |       |       |
     |       |       |     | C0=info only    | |       | DriftAlert->L6    |                 |                                                               |       |       |
     |       |       |     +---------+---------+       | DPOBatch->L4      |                 |                                                               |       |       |
     |       |       |               | U0 query        | EvalSummary->L6   |                 |                                                               |       |       |
     |       |       |               v                 | ImprovProposal    |-----------------|----------------------------------------------------------------------->+       | (To ML S6/S8)
     |       |       |     +-------------------+       +-------------------+                 |                                                               |       |       |
     |       |       |     | EVALUATION SPINE  |                                             |                                                               |       |       |
     |       |       |     | [Quality+Optim]   |                                             |                                                               |       |       |
     |       |       |     |-------------------|                                             |                                                               |       |       |
     |       |       |     | P@K, MRR, NDCG    |--+ (Metrics)                                |                                                               |       |       |
     |       |       |     | Groundedness      |---------------------------------------------|--------------------------------------------------------------->+      |       | (To ML S2-S5)
     |       |       |     | RRF + Reranker    |                                             |                                                               |       |       |
     |       |       |     | Completeness Mon  |                                             |                                                               |       |       |
     |       |       |     | DPOBatchBuilder   |                                             |                                                               |       |       |
     |       |       |     +---------+---------+                                             |                                                               |       |       |
     |       |       |               |                                                       |                                                               |       |       |
     |       |       |               v                                                       |                                                               |       |       |
=================================================================================================================================================================================================================
    [C]     [D]     [E]    [3] C0 RAG PIPELINE  (informational only — no route/safety/tier mutation)                                                        [T]     [P]     [U]
     |       |       |                                                                                                                                       |       |       |
     |       |       |     +------------------+                                                                                                              |       |       |
     |       |       |     | 1. EMBED QUERY   |  U0 → ephemeral query vector                                                                                 |       |       |
     |       |       |     +--------+---------+                                                                                                              |       |       |
     |       |       |              +----------(union)----------+                                                                                            |       |       |
     |       |       |              v                           v                                                                                            |       |       |
     |       |       |     +------------------+       +------------------+                                                                                   |       |       |
     |       |       |     | 2a. VECTOR CANDS |       | 2b. LEXICAL RET. |                                                                                   |       |       |
     |       |       |     |  cosine / FAISS  |       |  BM25 / exact    |                                                                                   |       |       |
     |       |       |     +--------+---------+       +--------+---------+                                                                                   |       |       |
     |       |       |              +----------(fusion)---------+                                                                                            |       |       |
     |       |       |                          v                                                                                                            |       |       |
     |       |       |     +------------------+                                                                                                              |       |       |
     |       |       |     | 3. CAND. FUSION  |   ScoreFusion / RRF · dedupe by chunk_id                                                                     |       |       |
     |       |       |     +--------+---------+                                                                                                              |       |       |
     |       |       |              v                                                                                                                        |       |       |
     |       |       |     +------------------+                                                                                                              |       |       |
     |       |       |     | 4. PARENT-CHILD  |   child chunk -> parent section + sibling window                                                             |       |       |
     |       |       |     +--------+---------+                                                                                                              |       |       |
     |       |       |              v                                                                                                                        |       |       |
     |       |       |     +------------------+                                                                                                              |       |       |
     |       |       |     | 5. COMPLETENESS  |   ContextCompletenessScore (emits to L6 telemetry + L4G) ----------------------------------------------------->+       |       |
     |       |       |     |    SCORING       |                                                                                                              |       |       |
     |       |       |     +--------+---------+                                                                                                              |       |       |
     |       |       |              v                                                                                                                        |       |       |
     |       |       |     +------------------+                                                                                                              |       |       |
     |       |       |     | 6. COMPLETENESS  |   blend: relevance_weight + completeness_weight                                                              |       |       |
     |       |       |     |    RERANKER      |                                                                                                              |       |       |
     |       |       |     +--------+---------+                                                                                                              |       |       |
     |       |       |              v                                                                                                                        |       |       |
     |       |       |     +------------------+                                                                                                              |       |       |
     |       |       |     | 7. TOP-K +       |   IAnswerSupportValidator: sentence-coverage check                                                           |       |       |
     |       |       |     |    SUPPORT VALID |   SupportedAnswerCheck ------------------------------------------------------------------------------------->+       |       |
     |       |       |     +--------+---------+                                                                                                              |       |       |
     |       |       |              |                                                                                                                        |       |       |
     |       |       |              v (C0 context — informational only, bypasses routing logic -> goes to [6])                                               |       |       |
=================================================================================================================================================================================================================
    [C]     [D]     [E]    [4] L5 SAFETY ENFORCEMENT PLANE  (cross-cutting — consulted by ALL layers)                                                       [T]     [P]     [U]
     |       |       |                                                                                                                                       |       |       |
     |       |       |      L1 emits intent · L1 emits anomaly · L1 emits C0 dependency                                                                      |       |       |
     |       |       |                               |                                                                                                       |       |       |
     |       |       |                               v                                                                                                       |       |       |
     |       |       |      +--------------+  +--------------+  +--------------+  +--------------+                                                           |       |       |
     |       |       |      | [1] CLASSIF. |  | [2] STRUCT.  |  | [3] AGENT    |  | [4] SOVR.    |                                                           |       |       |
     |       |       |      |    KERNEL    |<>|    BLUEPRINT |<>|    REGISTRY  |<>|    LLM GW    |                                                           |       |       |
     |       |       |      |--------------|  |--------------|  |--------------|  |--------------|                                                           |       |       |
     |       |       |      | FileType AST |  | Territory    |  | Agent profls |  | Sole egress  |                                                           |       |       |
     |       |       |      | 19-priority Q|  | Path val.    |  | Exec modes   |  | Prov. abstr. |                                                           |       |       |
     |       |       |      | LRU 1024     |  | Test SSOT    |  | Allowlists   |  | Inject detec |                                                           |       |       |
     |       |       |      | Zero deps    |  | 62 compon.   |  | reg_digest() |  | Hash audit   |                                                           |       |       |
     |       |       |      +------+-------+  +------+-------+  +------+-------+  +------+-------+                                                           |       |       |
     |       |       |             |                 |                 |                 |                                                                   |       |       |
     |       |       |             +─────────────────+────────┬────────+─────────────────+                                                                   |       |       |
     |       |       |                                        |                                                                                              |       |       |
     |       +<------------------- [D] L5 FAIL triggers RE-ROUTE (Passes checks)                                                                             |       |       |
     |       |       |             (Flows up to L1 via Left)  |                                                                                              |       |       |
     |       |       |                                        v                                                                                              |       |       |
=================================================================================================================================================================================================================
    [C]     [D]     [E]    [5] L0 ROUTING  +  META-LEARNING BUS                                                                                             [T]     [P]     [U]
     |       |       |                                                                                                                                       |       |       |
     +------>|       |     +------------------------------------+   +----------------------------------+                                                     |       |       |
             |       |     | L0 – ROUTING (Central Traffic)     |   | META-LEARNING & OPTIM. BUS       |<----------------------------------------------------+       |       | (Reads [T])
             |       |     |------------------------------------|   | IMMUTABLE stage order:           |<------------------------------------------------------------+       | (Reads [P])
             |       |     | Classify intent vs L4 state        |   | S1 AUDIT -> S2 TELEM -> S3 CFG   |                                                     |       |       |
             |       |     | JIT context via Elevator Shaft     |   | -> S4 SNAP -> S5 RCA -> S6 PROP  |                                                     |       |       |
             |       |     | Cannot eval / cannot execute       |   | -> S7 VAL -> S8 INTAKE -> S9 CMT |                                                     |       |       |
             |       |     | P1: Assign TraceID + PolicyHash    |   |----------------------------------|                                                     |       |       |
             |       |     | P2: Deterministic election         |   | S1 AUDIT     read audit slice    |                                                     |       |       |
             |       |     | P3: Tool budget arbitration        |   | S2 TELEMETRY read events         |                                                     |       |       |
             |       |     | P4: Seal + dispatch signed plan    |   | S3 CONFIG    get configs         |                                                     |       |       |
             |       |     |                                    |   | S4 SNAPSHOT  engine+cfg+clock    |                                                     |       |       |
             |       |     | ML signals (all -> S6 PROPOSE):    |   | S5 RCA       analyze failures    |                                                     |       |       |
             |       |     | [1] Pattern Analysis (intent logs) |-->| S6 PROPOSE   L0/RAG/L1/L5 order  |                                                     |       |       |
             |       |     | [2] Threshold Tuning (risk limits) |-->|              + DPO/RLHF          |                                                     |       |       |
             |       |     | [3] Path Optimization (routing)    |-->| S7 VALIDATE  Replay+Shadow+Damp  |                                                     |       |       |
             |       |     |                                    |   | S8 INTAKE    HealingOutcome+     |                                                     |       |       |
             |       |     | Agent Exec Profile Enforcement:    |   |    HEAL-OPT  Config optimizer    |                                                     |       |       |
             |       |     | LOW=deterministic / HIGH=LLM-only  |   |    PATTERN   PatternAnalysis     |                                                     |       |       |
             |       |     | Unregistered -> HARD FAIL          |   |    EMBED     semantic ctx (C0)   |                                                     |       |       |
             |       |     | Registry hash in determinism digest|   | S9 COMMIT    proposal_only=True  |                                                     |       |       |
             |       |     | ShadowRouterClassifier (drift)     |   |    ApprovalGate -> VersionStore  |                                                     |       |       |
             |       |     | TimeshiftRouter (N+1 signals)      |   |    -> Activator (dual inject req)|                                                     |       |       |
             |       |     | EscalationRouter (prior violations)|   +------------------+---------------+                                                     |       |       |
             |       |     +--^---------------------------------+                      |                                                                     |       |       |
             |       |        |                                                        +------------------------------------------------------------------------------------>+ (Writes [U])
             |       |        +-----[A] L0 updated rules ------------------------------+  (S9 Commit outputs updates to L0 Rules and L1 Weights)                             |
             |       |                                                                                                                                                       |
             |       |                  |                                                                                                                                    |
             |       |                  v (dispatches signed execution plan)                                                                                                 |
=================================================================================================================================================================================================================
    [C]     [D]     [E]    [6] ASSEMBLY STAGE  (sandbox airlock — deterministic composition)                                                                [T]     [P]     [U]
     |       |       |                                                                                                                                       |       |       |
     |       |       |     C0 RAG context (from [3]) ───────────────────────┐                                                                                |       |       |
     |       |       |     Signed plan from L0 ─────────────────────────────+──>                                                                             |       |       |
     |       |       |                                                      |                                                                                |       |       |
     |       |       |     +------------------------------------------------+-------------------+                                                            |       |       |
     |       |       |     | [S0] System prompt  — hard-coded constitutions (L4)                |                                                            |       |       |
     |       |       |     | [I0] Instructional  — identity / mixin behaviors (L4)              |                                                            |       |       |
     |       |       |     | [D0] Injections     — semantic fences / tool fences (L5)           |                                                            |       |       |
     |       |       |     | [C0] Dependency     — RAG injected knowledge (info only)           |                                                            |       |       |
     |       |       |     | [U0] User prompt    — raw intent from L1                           |                                                            |       |       |
     |       |       |     | BLOCK hostile input vectors                                        |                                                            |       |       |
     |       |       |     | SPLIT into atomic tasks · => Governed Payload -> Paths A/B/C/D     |                                                            |       |       |
     |       |       |     +--------------------------------------------------------------------+                                                            |       |       |
     |       |       |                  |                                                                                                                    |       |       |
     |       |       |                  v (governed payload)                                                                                                 |       |       |
=================================================================================================================================================================================================================
    [C]     [D]     [E]    [7] EXECUTION PATHS  A / B / C / D                                                                                               [T]     [P]     [U]
     |       |       |                                                                                                                                       |       |       |
     |       |       +-----------> (STALL trigger limits execution to Path D if active)                                                                      |       |       |
     |       |       |                                                                                                                                       |       |       |
     |       |       |     +============+  +==============+  +==============+  +===================+                                                         |       |       |
     |       |       |     | PATH A     |  | PATH B       |  | PATH C       |  | PATH D            |                                                         |       |       |
     |       |       |     | Read-Only  |  | Policy 1st   |  | Direct Exec  |  | Human Review 1st  |                                                         |       |       |
     |       |       |     +======+=====+  +======+=======+  +======+=======+  +========+==========+                                                         |       |       |
     |       |       |            |               |                 |                   |                                                                    |       |       |
     |       |       |            v               v                 v                   v                                                                    |       |       |
     |       |       |     +------+-----+  +------+-------+  +------+-------+  +--------+----------+                                                         |       |       |
     |       |       |     | Final Resp |  | L3:ORCHEST.  |  | L3:ORCHEST.  |  | HUMAN REVIEW      |                                                         |       |       |
     |       |       |     | No mutation|  |--------------|  |--------------|  |-------------------|                                                         |       |       |
     |       |       |     | Logged     |  | Seq HS       |  | Seq HS       |  | MODIFY_DIFF must  |                                                         |       |       |
     |       |       |     |            |  | Conflict Arb |  | Eval vs DAG  |  | ref plan_hash     |                                                         |       |       |
     |       |       |     |            |  | Dedup tools  |  | Seq branches |  | Zero authority    |                                                         |       |       |
     |       |       |     |            |  | Gate halluc. |  | Coord agents |  | Drift Monitor --------------------------------------------------------------------->+       |
     |       |       |     |            |  | HSM states   |  | Route/escal. |  | Policy Monitor -------------------------------------------------------------------->+       |
     |       |       |     |            |  | NervousSystem|  |              |  | DPO pair->RLHF -------------------------------------------------------------------->+       |
     |       |       |     |            |  | MCPRegistrar |  |              |  +--------+----------+                                                         |       |       |
     |       |       |     |            |  | ReasoningInt |  |              |           |                                                                    |       |       |
     |       |       |     |            |  +------+-------+  +------+-------+           |                                                                    |       |       |
     |       |       |     |            |         |                 |                   |                                                                    |       |       |
     |       |       |     |            |         v                 v                   v                                                                    |       |       |
     |       |       |     |            |  +------+-------------------------------------+----------+                                                         |       |       |
     |       |       |     |            |  | L5: SAFETY  [cross-path guard]                        |                                                         |       |       |
     |       |       |     |            |  |-------------------------------------------------------|                                                         |       |       |
     |       |       |     |            |  | Risk tier classify · Compliance hash/stamp            |                                                         |       |       |
     |       |       |     |            |  | Validate proposal vs policy                           |                                                         |       |       |
     |       |       |     |            |  | Enforce -> Approve / Remediate / Reject               |                                                         |       |       |
     |       |       |     |            |  | RE-CLEAR mandatory for human MODIFY_DIFF              |                                                         |       |       |
     |       |       |     |            |  | ML optimization signal -------------------------------------------------------------------------------------------------->+       |
     |       |       |     |            |  +------+----------------------------+-------------------+                                                         |       |       |
     |       |       |     |            |         | (Pass)                       | (Fail)                                                                    |       |       |
     |       +<-------------------------|---------+                              v                                                                           |       |       |
     |       |       |     |            |  [STAMP WORK CONTRACT]          [D] RE-ROUTE TO L1                                                                 |       |       |
     |       |       |     |            |  [sandbox permission]           (Flows up on Left Bus)                                                             |       |       |
     |       |       |     |            |         |                                                                                                          |       |       |
     |       |       |     |            |         v                                                                                                          |       |       |
=================================================================================================================================================================================================================
    [C]     [D]     [E]    [8] L2 UNIFIED EXECUTION CORE  (PTC Sandbox)                                                                                     [T]     [P]     [U]
     |       |       |                                                                                                                                       |       |       |
     |       |       |     +=========================================================================+                                                       |       |       |
     |       |       |     | L2 – UNIFIED EXECUTION CORE                                             |                                                       |       |       |
     |       |       |     |-------------------------------------------------------------------------|                                                       |       |       |
     |       |       |     | CAPABILITY CHOKEPOINT: authorize_and_execute() on EVERY call            |                                                       |       |       |
     |       |       |     | NETWORK EGRESS GUARD: SovereignLLMGateway (no direct HTTP)              |                                                       |       |       |
     |       |       |     | ISOLATION: DockerSandbox.run_code() / FirecrackerManager                |                                                       |       |       |
     |       |       |     | PROTOCOL: pre_commit -> validate -> execute -> heal                     |                                                       |       |       |
     |       |       |     |                                                                         |                                                       |       |       |
     |       |       |     | +--[P1: INIT]---------------------------------------------------------+ |                                                       |       |       |
     |       |       |     | | Validate signed plan + PTC ToolBudget                               | |                                                       |       |       |
     |       |       |     | | CapabilityToken: scoped + unexpired                                 | |                                                       |       |       |
     |       |       |     | | FREEZE clean state · CLAIM write access                             | |                                                       |       |       |
     |       |       |     | +--[P2: EXECUTE]-----+ +-------------------------+                      |                                                       |       |       |
     |       |       |     | | Enforce ToolCall   | | UNIVERSAL WRITE GATEWAY | ML Feedback Signals: |                                                       |       |       |
     |       |       |     | | -> ToolResult sch. | | sole mutation auth      | Failure Classifier ------------------------------------------------------------------>+       |
     |       |       |     | | STDOUT: structured | | replay -> sim diffs     | Resource Predictor ------------------------------------------------------------------>+       |
     |       |       |     | | CID Registry track | | Non-UWG -> Error        | RL Rollback Refiner ----------------------------------------------------------------->+       |
     |       |       |     | | declare effect cls | +-------------------------+                      |                                                       |       |       |
     |       |       |     | | undeclared -> abort+ C0 RAG (read-only):                              |                                                       |       |       |
     |       |       |     | | CEIL: term. stuck    FAISS BLAS locked                                |                                                       |       |       |
     |       |       |     | |                      SHA-256 integrity chk                            |                                                       |       |       |
     |       |       |     | +--[P3: EVALUATE / HEAL]----------------------------------------------+ |                                                       |       |       |
     |       |       |     | | Result ──(Pass)──────────────────────────────────────────────────>  | |                                                       |       |       |
     |       |       |     | |        ──(Fail)──> L2.3 CONFIDENCE-TIER HEALING                     | |                                                       |       |       |
     |       |       |     | |   EscalationContext -> FailureSignal -> tier router                 | |                                                       |       |       |
     |       |       |     | |   heal_confidence: LOCAL(>=0.75)/QWEN(>=0.40)/GEMINI              | |                                                       |       |       |
     |       |       |     | |   retry_count >= 3 -> force GEMINI                                  | |                                                       |       |       |
     |       |       |     | |   healer result -> (loop back to execute on success)                | |                                                       |       |       |
     |       |       |     | |   HealingOutcome ────────────────────────────────────────────────--------------------------------------------------------------------->+       |
     |       |       |     | +--[P4: SYNTHESIZE]---------------------------------------------------+ |                                                       |       |       |
     |       |       |     | | Aggregate outputs · Validate schema · Final artifact                | |                                                       |       |       |
     |       |       |     | | EMIT PTC ToolTranscript ONLY (context isolation)                    | |                                                       |       |       |
     |       |       |     | +---------------------------------------------------------------------+ |                                                       |       |       |
     |       |       |     +=========================================================================+                                                       |       |       |
     |       |       |                  |                               |                                                                                    |       |       |
     |       |       |                  | (ToolTranscript)              | (transcript -> L4/L6)                                                              |       |       |
     |       |       |                  v                               v                                                                                    |       |       |
=================================================================================================================================================================================================================
    [C]     [D]     [E]    [9] OUTCOME  (state commits + all feedback arrows complete their loops above)                                                    [T]     [P]     [U]
     |       |       |                                                                                                                                       |       |       |
     |       |       |     +---------------------------+                                                                                                     |       |       |
     |       |       |     |  OUTCOME / LOGGING        |                                                                                                     |       |       |
     |       |       |     |---------------------------|                                                                                                     |       |       |
     |       |       |     |  Answer via Transcript    |                                                                                                     |       |       |
     |       |       |     |  ExecutionTrace envelope  |                                                                                                     |       |       |
     |       |       |     |  Update team memory       |                                                                                                     |       |       |
     |       |       |     |  Reconcile data/reality   |                                                                                                     |       |       |
     |       |       |     |  Metrics: latency, cost,  |                                                                                                     |       |       |
     |       |       |     |  accuracy, correction rate|---------------------------------------------------------------------------------------------------->+       |       |
     |       |       |     +---------------------------+                                                                                                     |       |       |
     |       |       |                  |                                                                                                                    |       |       |
     |       |       |                  v  commits final state -> L4 Activity Ledger                                                                         |       |       |
     |       |       |                  |                                                                                                                    |       |       |
=================================================================================================================================================================================================================