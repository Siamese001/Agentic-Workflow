==============================================================================================================================
                            AGENTIC SYSTEM — PROCESS MAP (CANONICAL SEMANTICS & LOOP)
 PRIMARY RUNTIME PATH: L1 → L0 → [opt L3] → L2 | L5 = cross-cutting policy | UWG = writes to L4
==============================================================================================================================

[ L5 POLICY PLANE / Safety Officer ] ──(cross-cutting authority over L1, L0, L2, Exit, UWG)──────────────────────────────────┐
         ┌──────────────────┐                                                                                                │
         │U0 REQUEST SOURCES│                                                                                                │
         │ (User/App/Event) │                                                                                                │
         └────────┬─────────┘                                                                                                │
                  ▼                                                                                                          │
         ┌──────────────────┐                                                                                                │
         │ INGRESS / CHECK  │ <── (optional pre-layer envelope validation, NOT L0)                                           │
         └────────┬─────────┘                                                                                                │
                  │                                                                                                          │
┌─────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│                 ▼                                                                [CORE RUNTIME LOOP]                     │ │
│ ┌───────────────┴──────────────────┐<──────────────────────────────────────────────────────────────────────────────────┐ │ │
│ │  L1 REASONING LOOP (Librarian)   │<───────────────────────────────────────────────────────────┐                      │ │ │
│ └───────────────┬──────────────────┘                                                            │                      │ │ │
│                 ├                    ┌────────────────────────────────┐             ┌───────────┴────────────┐         │ │ │
│                 ├──[query]─────────> │ C0 CONTEXT ENGINE (Ref Desk)   │─[evidence]─>│     PROMPT ASSEMBLY    │         │ │ │
│                 │                    │ retrieve•curate•compress•ground│             │ (System•Context•Task)  │         │ │ │
│                 │                    └───────────────▲────────────────┘             └───────────▲────────────┘         │ │ │
│                 │                                    │                                          │                      │ │ │
│                 │                                    └───────── [reads] ────────────────────────┤                      │ │ │
│                 │ [plan]                                                                        │ [state load]         │ │ │
│                 ▼                                                                               │                      │ │ │
│ ┌──────────────────────────────────┐                                                ┌───────────┴────────────┐         │ │ │
│ │     L0 ROUTING (Dispatcher)      │                                                │       L4 STATE /       │         │ │ │
│ │ R1A exact cache • R1Bsem cache   │                                                │       Archivist        │         │ │ │
│ │ R3 agentic RAG • R4 action       │                                                └───────────▲────────────┘         │ │ │
│ │ R5 fallback                      │                                                            │                      │ │ │
│ └───────────────┬──────────────────┘                                                            │                      │ │ │
│                 │                                                                               │ [writes]             │ │ │
│                 │ [dispatch]                                                                    │                      │ │ │
│                 ▼                                                                               │                      │ │ │
│ ┌──────────────────────────────────┐                                                            │                      │ │ │
│ │ L3 ORCHESTRATOR [opt] (Sec Head) │                                                            │                      │ │ │
│ └───────────────┬──────────────────┘                                                            │                      │ │ │
│                 ▼ [EXECUTE]                                                                     │                      │ │ │
│ ┌──────────────────────────────────┐                                                            │                      │ │ │
│ │  L2 EXECUTION (Execution Staff)  │                                                            │                      │ │ │
│ └───────────────┬──────────────────┘                                                            │                      │ │ │
│                 ▼ [L2 EXECUTION OUTPUT]                                                         │                      │ │ │
└─────────────────┼───────────────────────────────────────────────────────────────────────────────┼────────────────────────┘ │
                  │                                                                               │                            │
==================┼===============================================================================┼============================│
[5] POST-L2 CONTROL + EVALUATION                                                                  │                            │
==================┼===============================================================================┼============================│
                  ▼                                                                               │                            │
 ┌────────────────┴─────────────────┐                                                             │                            │
 │ LIVE EVALUATION SPINE            │                                                             │                            │
 │ current-run judgment             │                                                             │                            │
 │ - policy checks                  │                                                             │                            │
 │ - schema / sandbox validity      │                                                             │                            │
 │ - outcome checks                 │                                                             │                            │
 │ - trajectory checks              │                                                             │                            │
 │ - release-time regression checks │                                                             │                            │
 └────────────────┬─────────────────┘                                                             │                            │
                  │                                                                               │                            │
 ┌────────────────▼─────────────────┐<───[approve / deny / rework / reroute]────────┐           │                            │
 │ EXIT SPINE                       │                                               │           │                            │
 │ Checkout / disposition authority │             ┌─────────────────────────┐       │           │                            │
 │ - allow / finish                 ├──[ESCALATE]─> HITL                    │       │           │                            │
 │ - deny                           │             │ human review            │       │           │                            │
 │ - reroute / control              │             └────────────┬────────────┘       │           │                            │
 │ - escalate to HITL               │                          ▼                    │           │                            │
 │ - commit if needed               │             ┌─────────────────────────┐       │           │                            │
 └─┬──────────────┬───────────────┬─┘             │ HUMAN DISPOSITION       ├───────┘           │                            │
   │              │               │               └─────────────────────────┘                   │                            │
   ▼              ▼               ▼                                                             │                            │
[ALLOW /       [COMMIT ->      [DENY /                                                          │                            │
 FINISH]        UWG -> L4]      REROUTE]                                                        │                            │
                                                                                                │                            │
================================================================================================┼============================│
[6] SHADOW EVALUATION + FUTURE-RUN LEARNING                                                     │                            │
================================================================================================┼============================│
                  │                                                                             │                            │
                  ▼ [Runtime evidence + L4 artifacts]                                           │                            │
 ┌────────────────┴───────────────────────────┐                                                 │                            │
 │ SHADOW EVALUATION SPINE                    │                                                 │                            │
 │ Review / scoring / signalization           │                                                 │                            │
 │ - telemetry grading                        │                                                 │                            │
 │ - broader drift / replay / trend analysis  │                                                 │                            │
 │ - heavier regression/calibration analytics │                                                 │                            │
 └────────────────┬───────────────────────────┘                                                 │                            │
                  │                                                                             │                            │
         ┌────────┴────────┐                                                                    │                            │
         │                 │                                                                    │                            │
         ▼                 ▼                                                                    │                            │
    [L6 OBSERVE]     [BUS P / BUS T]                                                            │                            │
                           │                                                                    │                            │
                           ▼                                                                    │                            │
             ┌─────────────┴────────────────────┐                                               │                            │
             │ EVOLUTION / SYSTEM LEARNING LOOP │                                               │                            │
             │ future-runs only                 │                                               │                            │
             │ - RCA                            │                                               │                            │
             │ - proposal drafting              │                                               │                            │
             │ - approval                       │                                               │                            │
             │ - promotion to BUS U             │                                               │                            │
             └─────────────┬────────────────────┘                                               │                            │
                           │                                                                    │                            │
                           ▼                                                                    │                            │
               [BUS U FUTURE RUNS ONLY]                                                         │                            │
                                                                                                │                            │
────────────────────────────────────────────────────────────────────────────────────────────────┴────────────────────────────┘

===============================================================================================================================================================================
[ U0: RAW USER INTENT ] ──(raw_query)──┐
                                       │
=======================================▼=======================================================================================================================================
  [ L1: COGNITIVE STUDIO ] ── Structured Planner (No Tool Execution, No Vector Retrieval Ownership)
===============================================================================================================================================================================
  ┌─────────────────────────────┐   ┌─────────────────────────────┐   ┌─────────────────────────────┐   ┌─────────────────────────────────────┐
  │ P1: INGEST & PRIME          │──>│ P2: INTENT EXTRACTION       │──>│ P3: PLAN & TOOL BUDGET      │──>│ P4: CONTEXT SPEC & ROUTE HINT       │──>[ Contract: L1Plan ]
  │ Hydrate context, parse      │   │ Map intent, detect gaps     │   │ Plan, Verify, Budget        │   │ Define required context spec        │   (route_hint, query_spec)
  └─────────────────────────────┘   └─────────────────────────────┘   └─────────────────────────────┘   └─────────────────────────────────────┘             │
                                                                                                                                                            │
============================================================================================================================================================▼==================
  [ L0: ROUTING BUS & POLICY GATEWAY | Front Desk ] ── Thin Deterministic Authority
===============================================================================================================================================================================
  L0 evaluates [ L1Plan + raw_query ]. Sequences ops to protect compute: 1. O(1) Hash ➔ 2. Fast Policy Triage ➔ 3. Embed [ 🔵 query_vec ] ➔ 4. Route

┌───────────────────────────────────▼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ▼ Reusable Answer                  ▼ Needs Fact/Context               ▼ Action Required                  ▼ General/Safe Intel               ▼ Ambiguous/Unsafe              │
│ [ R1. CACHE REUSE ]                [ R2. AGENTIC RAG (C0) ]           [ R3. AGENTIC ACTION ]             [ R4. PARAMETRIC ANSWER ]          [ R5. GUARDRAILS ]              │
│ (Exact or Semantic Reuse)          (Auth: EXECUTE_RAG)                (Escalate to Active API)           (Low-risk only)                    (CLARIFY or ABSTAIN)            │
│                                                                                                                                                                             │
├──> ┌──────────────────────────┐                   ▼                                  ▼                                  ▼                                  ▼                │
│    │ R1A. EXACT CACHE         │        [ Triggers C0 Pipeline ]           [ Exec Action ]                    [ Exec Parametric ]               [ Ask Clarification ]        │
│    │ O(1) Key-Value Lookup    │         (Latency: ~1.5s)                   (Latency: ~800ms)                  (Latency: ~400ms)                 (Latency: ~10ms)            │
│    │ 🔤 SHA256(norm_query)    │                   │                                                                                                                        │
│    │ vs 🔤 Redis TTL: 24h      │                   │                                                                                                                        │
│    └──────────────────────────┘                   │                                                                                                                        │
│          (Latency: < 1ms)                         │                                                                                                                        │
└──> ┌──────────────────────────┐                   │                                                                                                                        │
│    │ R1B. SEMANTIC REUSE      │                   │                                                                                                                        │
│    │ Eval post-embedding      │                   │                                                                                                                        │
│    │ 🔵 query_vec             │                   │                                                                                                                        │
│    │ vs 🟣 cached_query_vec   │                   │                                                                                                                        │
│    └──────────────────────────┘                   │                                                                                                                        │
│           (Latency: ~50ms)                        │                                                                                                                        │
====================================================│=========================================================================================================================┘
                                                    ▼
===============================================================================================================================================================================
  [ C0: RAG PIPELINE ] ── Read-Only Evidence Assembly
===============================================================================================================================================================================
  Receives [ L1Plan + 🔵 query_vec ]. Executes pure info retrieval. Does NOT read prior AI generated reasoning traces as facts.
  * NOTE: [ 🟠 fact_vec ] is a precomputed offline artifact. It is a read-only indexed substrate (ChromaDB), NOT generated during inference.

                                ┌───────────────────────────────────────┐ Takes ownership of [ 🔵 query_vec ] from L0
                                │ 1. ACCEPT QUERY_VEC & INITIATE        │──➔ Routes: [ 🔵 query_vec ]
                                └───────────────────┬───────────────────┘
                                                    │
                                                    ▼
                               ┌───────────────────────────────────────┐
                               │ 1b. SEMANTIC EVIDENCE CACHE           │──(Hit >0.95 Sim)──> Yields Hydrated Evidence Bundle ─────────────────────────────────────────┐
                               │ Maps query_vec to prior context       │                                                                                              │
                               └────────────────────┬──────────────────┘                                                                                              │
                                                    │ (Miss)                                                                                                          │
                                                    ├──> ┌───────────────────────────────────────┐                                                                    │
                                                    │    │ 2a. VECTOR SEARCH (Semantic)          │──> Top-K_vec ──┐                                                   │
                                                    │    │ Compares [ 🔵 query_vec ]             │              │   ┌───────────────────────┐   ┌──────────────────┐ │
                                                    │    │ vs [ 🟠 fact_vec ] index              │              ├──>│ 3. SCORE FUSION (RRF) │──>│ 4. CROSS-ENCODER │─┤
                                                    │    └───────────────────────────────────────┘              │   │ Hybrid Interleaving   │   │ Deep Q vs Doc    │ │
                                                    └──> ┌───────────────────────────────────────┐              │   └───────────────────────┘   └──────────────────┘ │
                                                         │ 2b. LEXICAL SEARCH (BM25)             │──> Top-K_lex ──┘                                                  │
                                                         │ Exact token match scoring             │                                                                   │
                                                         └───────────────────────────────────────┘                                                                   │
                                                                                                                                                                     │
 ┌────────────────────────────────────┐   ┌──────────────────────────────────────────┐    ┌───────────────────────────────────────────────────────────────────────────▼───────┐
 │ [ Contract: C0EvidenceBundle ]     │<──│ 6. COMPLETENESS CHECK                    │<── │ 5. CONTEXT BUILD (Assembly & Provenance)                                          │
 │ - verified_chunks                  │   │ Checks Coverage vs L1Plan spec           │    │ Stitch chunks, Expand Parent/Child, Filter by Freshness                           │
 │ - cited_spans                      │   │ Evaluates support_status                 │    │ Retains strict provenance metadata (Sources/Dates)                                │
 │ - source_ids / dates               │   │ Abstains if gap is critical              │    │ Drops unsupported or unverified artifacts                                         │
 │ - coverage_score                   │   └──────────────────────────────────────────┘    └───────────────────────────────────────────────────────────────────────────────────┘
 │ - support_status                   │
 │ - recommended_next_action          │───(Closes Loop)──> [ L1: SYNTHESIS / ANSWER COMPOSITION ] ══> [ FINAL RESPONSE ]
 └────────────────────────────────────┘
===============================================================================================================================================================================

====================================================================================================================================================================================================================================
[6] ⚙️ L2 UNIFIED EXECUTION CORE (PTC Sandbox)
====================================================================================================================================================================================================================================
 [ SCOPE RULES ]: L2 EXECUTES BLINDLY. L2 HARD CONSTRAINTS: Cannot modify policy (L5) | Cannot modify routing (L0) | Cannot write directly to archive (must use UWG).

 +----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 | * CAPABILITY CHOKEPOINT: authorize_and_execute() on EVERY call        * ISOLATION: DockerSandbox.run_code() / FirecrackerManager                                                                                                                    
 | * PROTOCOL: pre_commit -> validate -> execute -> heal                 * NETWORK EGRESS: SovereignLLMGateway -> Ext. Providers                                                                                                                       
 | * INFRA: Circuit breakers · Backoff · Timeout · Rate limits · Health checks · Readiness/Liveness probes                                                                                                                                             
 +----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

 ┌────────────────────────────┐      ┌────────────────────────────┐      ┌──────────────────────────────────────────┐      ┌────────────────────────────────────────┐
 │ 🟢 [P1: INIT]              │      │ 🛠️ [P2: EXECUTE]            │      │ 🏥 [P3: EVALUATE / HEAL]                 │      │ 📦 [P4: SYNTHESIZE]                    │
 │ Validate signed plan       │─────>│ Enforce ToolCall -> sch.   │─────>│ Result --(Pass)--------------------------│─────>│ Aggregate outputs                      │
 │ PTC ToolBudget             │      │ STDOUT: structured         │      │        --(Fail)--> L2.3 TIER HEALING     │      │ Validate schema                        │
 │ CapToken: scope/unexp      │      │ Declare effect cls         │      │ EscalationContext -> tier router         │      │ Final artifact                         │
 │ FREEZE clean state         │      │ CEIL: term. stuck          │      │ LOCAL(>=0.75)/QWEN(>=0.40)/GEMINI        │      │ EMIT PTC ToolTranscript ONLY           │
 │ CLAIM write access         │      │ 🔍 C0 RAG: BLAS lck, SHA   │      │ HealingOutcome (retries >= 3 -> GEM)     │      │ ExecTrace w/ replay                    │
 │                            │      │                            │      │ qwen_circuit_breaker.py / healer res     │      │ TranscriptMutationViolation grd        │
 └─────────────┬──────────────┘      └─────────────┬──────────────┘      └──────────────────────┬───────────────────┘      └──────────────────┬─────────────────────┘
               │                                   │                                            │                                             │
 ┌─────────────▼───────────────────────────────────▼────────────┐        ┌──────────────────────▼───────────────────┐                         │
 │ MUTATION SOVEREIGNTY                                         │        │ 🚪 UWG (Sidecar)                         │                         │
 │ Durable state mutations must pass through Universal Write    │        │ Sole mut, replay->diff | Non-UWG -> Error│                         +=========[ TX ➔ BUS T ]========> (To L4/L6)
 │ Gateway (UWG). Direct writes are prohibited. Dep graph       │        └──────────────────────────────────────────┘                         │
 │ ensures no bypass of gateway.                                │        ┌──────────────────────────────────────────┐                         │
 └──────────────────────────────────────────────────────────────┘        │ 📡 ML Feedback Signals                   │=========================[ TX ➔ BUS P ]========> (To Eval Spine/ML)
                                                                         │ (Failure Class, Predictor, RL Refine)    │
                                                                         └──────────────────────────────────────────┘

================================================================================================================================================================================================================================
[7] ⚖️ EVAL SPINE & 🏆 G-GATE (GOLDEN COMPARISON)
================================================================================================================================================================================================================================
 [ SCOPE RULES ]: EXECUTES STRICTLY POST-L2. WRITES TO L4. DOES NOT FEED L1 INLINE. G-GATE IS A READ-ONLY SHADOW COMPARISON.
 AUTHORITY: READ-ONLY | NO EXECUTE | NO ROUTE | NO MUTATION | SIGNALS ONLY

    ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │ ⚖️ EVALUATION SPINE & 🏆 G-GATE (POST-EXECUTION QUALITY & REGRESSION MANIFOLD)                                                                                                              │
    │ [!] SHADOW-MODE ONLY: Does not mutate runtime. Does not bypass UWG. Emits signals strictly for continuous offline learning (Bus P/T).                                                        │
    │                                                                                                                                                                                              │
    │   [ FROM L2 EXECUTION ] ──(Raw Output, ExecTrace & Transcript)                                                                                                                               │
    │          │                                                                                                                                                                                   │
    │          ▼                                                ┌─────────────────────────┐                                                                                                        │
    │  ┌─────────────────────────┐                              │ [ GOLDEN DATASET ]      │                                                                                                        │
    │  │ 1. INGEST TRANSCRIPT    │                              │ Immutable baselines     │                                                                                                        │
    │  │ Load L2 execution trace │                              │ test_cases/ground_truth │                                                                                                        │
    │  │ Extract Context & Ans   │                              └──────────┬──────────────┘                                                                                                        │
    │  │ Check PTC isolation     │                                         │                                                                                                                       │
    │  └──────────┬──────────────┘                                         ▼                                                                                                                       │
    │             │                                             ┌─────────────────────────┐                                                                                                        │
    │             ▼                                             │ 3. GOLDEN GATE (G-GATE) │                                                                                                        │
    │  ┌─────────────────────────┐                              │ Fetch test baseline     │                                                                                                        │
    │  │ 2. METRIC CALCULATION   │                              │ Align input to golden   │                                                                                                        │
    │  │ Faithfulness scoring    │                              └──────────┬──────────────┘                                                                                                        │
    │  │ Groundedness scoring    │                                         │                                                                                                                       │
    │  │ Answer Relevancy score  │                                         │                                                                                                                       │
    │  └──────────┬──────────────┘                                         │                                                                                                                       │
    │             │                                                        │                                                                                                                       │
    │             └─────────────────────────────────┐   ┌──────────────────┘                                                                                                                       │
    │                                               ▼   ▼                                                                                                                                          │
    │                                      ┌─────────────────────────┐          ┌─────────────────────────┐                                                                                        │
    │                                      │ 4. REGRESSION DIFFING   │─────────>│ 5. SIGNAL EMISSION      │                                                                                        │
    │                                      │ Output vs Expected      │          │ Package system outcome  │──> (To L6 Observability)                                                               │
    │                                      │ Citation Match Rate     │          │ Combine metric & drift  │                                                                                        │
    │                                      │ API Call Drift detect   │          │ Prep DPO grades         │──> [ BUS P: DPO/GRADES ]                                                               │
    │                                      └─────────────────────────┘          └─────────────────────────┘                                                                                        │
    └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==================================================================================================================================================================================================================================
[8] 👁️ L6 (VERIFY) — OBSERVABILITY & REPLAY
==================================================================================================================================================================================================================================
 [ SCOPE RULES ]: DOES NOT EXECUTE. DOES NOT ROUTE. ONLY OBSERVES, VALIDATES, AND AUDITS.

    ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │ 👁️ L6 OBSERVABILITY, REPLAY, & MASTER CLOCK                                                                                                                                                 │
    │ [!] OBSERVATION & TIME SOVEREIGNTY: DOES NOT EXECUTE | DOES NOT ROUTE | SOLE TIME AUTHORITY | ENFORCES EXACT REPLAYABILITY                                                                   │
    │                                                                                                                                                                                              │
    │   [ INCOMING FROM L0/L2/L3/L5/EVAL SPINE ] ──(ExecTrace, Timestamps, Metrics, Anomalies)                                                                                                     │
    │          │                                                                                                                                                                                   │
    │          ▼                                                                                                                                                                                   │
    │  ┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────────────────────┐                                                     │
    │  │ 1. SEMANTIC CLOCK INGEST│────────>│ 2. DETERMINISM CHECK    │────────>│ 3. ANOMALY ENGINE       │────────>│ 5. L4 ARCHIVE PREP      │                                                     │
    │  │ Freeze exact timestamp  │         │ Validate RNG seeds      │ (Pass)  │ Detect structural drift │ (Clear) │ Seal ExecTrace envelope │──> [ BUS T: TELEMETRY -> L4 ]                         │
    │  │ Sync global execution   │         │ Verify PTC isolation    │         │ Check resource budgets  │         │ Format Outcome Metrics  │                                                     │
    │  │ Capture latency stats   │         │ Ensure replay strictness│         │ Monitor error rates     │         │ Route payload to UWG    │                                                     │
    │  └─────────────────────────┘         └──────────┬──────────────┘         └──────────┬──────────────┘         └─────────────────────────┘                                                     │
    │                                                 │ (Fail)                            │ (Anomaly)                                                                                              │
    │                                                 ▼                                   ▼                                                                                                        │
    │                                      ┌─────────────────────────┐<───────────────────┘                                                                                                        │
    │                                      │ 4. BROADCAST (BUS E/D)  │                                                                                                                             │
    │                                      │ Trigger HITL escalation │──> [ BUS E: ESCALATE TO HUMAN ]                                                                                             │
    │                                      │ Reroute / Force Re-entry│──> [ BUS D: DENY -> L1 ]                                                                                                    │
    │                                      └─────────────────────────┘                                                                                                                             │
    └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

===================================================================================================================================================================================================================================
[9] 💾 L4 (STORE) & 🚪 UWG (WRITE) — STATE, REGISTRY, & UNIVERSAL GATEWAY
=================================================================================================================================================================================================================================
 [ SCOPE RULES ]: L4 DOES NOT DECIDE. L4 DOES NOT EXECUTE. ONLY STORES, SERVES, AND LEARNS. UWG is the ONLY write path.

 ┌─────────────────────────────────────────────────────────┐ ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ L4: CANONICAL STATE & REGISTRIES                        │ │ UWG: UNIVERSAL WRITE GATEWAY & VIOLATION ENFORCEMENT                                                      │
 ├─────────────────────────────────────────────────────────┤ ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ • P1: COGNITIVE REG: Prompts, Calibrations              │ │ • All FS/DB/Vector writes route through single gateway with MutationRecord logging.                       │
 │ • P2: CAPABILITY REG: Tools, Policies                   │ │ • Allowed: artifacts/, docs/reports/, logs/, temp/, cache/. Blocked: .exe, .dll, .py, .js, .ts.           │
 │ • P3: WORKFLOW MEMORY: Pending Steps, DAG               │ │ • EPHEMERAL EXCEPTION: L4H (Redis) write-backs (TTL: 24h) MUST route via UWG to avert cache poisoning.  │
 │ • P4: TELEMETRY LEDGER: Exec Logs, System Outcomes      │ │                                                                                                           │
 │                                                         │ │ [ UWG AUTHORITY CHAIN & GRAVITY MATRIX DEMONSTRATION ]                                                    │
 │ [SYNC] L4 updates Shared Team Memory & Activity Ledger  │ │ [ L0/L2/L3/L4/L5/L6 ] ──(Solid ─→ Governed Req)──> [ UWG ] ──(Solid ─→ Digest Chain)──> [ ARCHIVE ]       │
 │ (Non-blocking state update occurs only after L2 seals). │ │           │                                                                                     ^         │
 │                                                         │ │           └- - - - - - - - - - (-→ Dashed: Direct FS/DB Write Bypassing Gateway) - - - - - - - -┘         │
 │                                                         │ │ [!] VIOLATION DETECTED: Direct write bypassing UWG → BLOCKED. Direct dashed line = gravity breach.        │
 └─────────────────────────────────────────────────────────┘ └───────────────────────────────────────────────────────────────────────────────────────────────────────────┘

