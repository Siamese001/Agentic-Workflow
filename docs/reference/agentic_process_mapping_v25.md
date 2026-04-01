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






