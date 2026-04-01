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
│                 ▼                                                                    [CORE RUNTIME LOOP]                 │ │
│ ┌───────────────┴──────────────────┐<──────────────────────────────────────────────────────────────────────────────────┐ │ │
│ │  L1 REASONING LOOP (Librarian)   │<───────────────────────────────────────────────────────────┐                      │ │ │
│ └───────────────┬──────────────────┘                                                            │                      │ │ │
│                 ├                    ┌────────────────────────────────┐             ┌───────────┴────────────┐         │ │ │
│                 ├──[query]─────────> │ C0 CONTEXT ENGINE (Ref Desk)   │─[evidence]─>│    PROMPT ASSEMBLY     │         │ │ │
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
│ └───────────────┬──────────────────┘                                                            │ [writes]             │ │ │
│                 │                                                                               │                      │ │ │
│                 │ [dispatch]                                                                    │                      │ │ │
│                 ▼                                                                               │                      │ │ │
│ ┌──────────────────────────────────┐                                                            │                      │ │ │
│ │ L3 ORCHESTRATOR [opt] (Sec Head) │                                                            │                      │ │ │
│ └───────────────┬──────────────────┘                                                            │                      │ │ │
│                 ▼ [EXECUTE]                                                                     │                      │ │ │
│ ┌──────────────────────────────────┐                                                            │                      │ │ │
│ │  L2 EXECUTION (Execution Staff)  │                                                            │                      │ │ │
│ └───────────────┬──────────────────┘                                                            │                      │ │ │
│                 ▼ [VERIFY]                                                                      │                      │ │ │
│ ┌──────────────────────────────────┐                                                ┌───────────┴────────────┐         │ │ │
│ │UNIVERSAL EXIT SPINE (EVAL+G-GATE)├─────── [commit if needed] ────────────────────>│          UWG           │         │ │ │
│ └───────────────┬───────────┬──────┘                                                │      (WriteGate)       │         │ │ │
│                 │           │ [deny -> L1] OR [reroute/control -> L0/L3]            └────────────────────────┘         │ │ │
│                 │           └──────────────────────────────────────────────────────────────────────────────────────────┘ │ │
│                 │ [allow/finish]                                                                                         │ │
└─────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
                  │           ┌─────────────────────┐                                                                        │
                  ├──────────>│ HUMAN REVIEW / HITL │──(approve/resume)──> [back to EXIT SPINE]                              │
                  │[escalate] │    (Senior Desk)    │                                                                        │
                  │           └─────────┬───────────┘                                                                        │
                  ▼                     │ [manual resp]                                                                      │
        ┌─────────┴─────────┐           │                                                                                    │
        │ RESPONSE / OUTCOME│<──────────┘                                                                                    │
        └───────────────────┘                                                                                                │
                                                                                                                             │
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┤
                                                                                                                             │
  [ Runtime evidence + L4 artifacts gathered across all layers ] <───────────────────────────────────────────────────────────┤
                                                                                                                             │
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                       L6 OBSERVABILITY (Observe • Trace • Aggregate • Monitor)                                             │
└─────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────┤
                              ▼                                                                                              │
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ EVOLUTION LOOP (versioned promotion - future runs only)                                                                    │
│ Inputs: T telemetry • P preference/grades • U update proposals                                                             │
│ • proposes semantic-memory updates   • proposes policy updates   • proposes cache optimization                             │
└─────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────┤
                              ▼                                                                                              │
[ PROMOTE TO: Primes L1 Reasoning • Updates L5 Policy • Updates L4 Semantic Memory ] ──────────(Feedback)────────────────────┘

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


=======================================================================================================================================================================================================================
[4] 🎼 L3 (ORCH) — EXECUTION PATHS & SEQUENCING
=======================================================================================================================================================================================================================
 [ SCOPE RULES ]: L3 handles sequential handshakes, conflict arbitration, overlapping tools, and DAG resolution. It does NOT execute the tools itself.

+========================================+========================================+========================================+=============================================+
| MODE ALPHA                             | MODE BETA                              | MODE GAMMA                             | MODE DELTA (HUMAN REVIEW FIRST)             |
|----------------------------------------|----------------------------------------|----------------------------------------|---------------------------------------------|
| READ-ONLY RESPONSE                     | POLICY CHECK FIRST                     | EXECUTE SCRIPT DIRECT                  | 1. Generate review artifact                 |
| - No system mutation                   | - Sequential Handshake                 | - Conflict Arbitration                 | 2. Freeze execution                         |
| - Logged outcome                       | - Gate: Hallucination                  | - Eval Result vs DAG                   | 3. Human decision [APPROVE|MODIFY|REJECT]  |
| - ML consumes outcome                  | - Seed: Strict heal                    | - Route: Complete/L2                   | 4. Route patch to L5 re-clearance           |
|                                        |                                        |                                        | HARD RULE: Human input is untrusted until L5|
+========================================+========================================+========================================+=============================================+

=======================================================================================================================================================================================================================
[5] 🛡️ L5 (CHECK) — SOVEREIGN CONTROL PLANE & ASSEMBLY
=======================================================================================================================================================================================================================
 [ SCOPE RULES ]: L5 is the Security Commandant. If a rule is not explicitly defined, L5 cannot invent one. CONFIG_WITH_LOGIC detection blocks hostile payloads.

 ┌──────────────────────────────────────────────────┐ ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ L5 SAFETY & CLASSIFICATION KERNELS               │ │ GOVERNED PAYLOAD ASSEMBLY (ORDER MATTERS)                                                                        │
 ├──────────────────────────────────────────────────┤ ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ • AST-based 19-priority queue.                   │ │ [ S0 SYSTEM RULES ] ─→ [ D0 ENFORCEMENT ] ─→ [ C0 CONTEXT ] ─→ [ U0 REQUEST ]                                    │
 │ • LRU cache for high-speed intercepts.           │ │                                                                                                                  │
 │ • STRUCTURE BLUEPRINT (sovereign_kernel).        │ │ Rules command restrictions → restrictions guard references → references contextualize the request.               │
 │ • is_path_allowed() strictly enforces paths.     │ │ Action: Splits into atomic tasks and permanently blocks hostile vectors before handing off to L2.                │
 └──────────────────────────────────────────────────┘ └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

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

================================================================================================================================================================================================================================
[10] 🧠 ML (LEARN) — SYSTEM LEARNING BUS & DETERMINISM PROOF
================================================================================================================================================================================================================================
 [ SCOPE RULES ]: Executes offline/asynchronously (Pipeline D) for FUTURE-RUNS ONLY. Never mutates live execution.

 ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ SYSTEM LEARNING LOOP: PERSONA-MAPPED STATE MACHINE (PIPELINE D)                                                                                                       │
 ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │     [ BUS T / BUS P INGESTION ]                                                                                                                                       │
 │                 │                                                                                                                                                     │
 │                 ▼                                                                                                                                                     │
 │   ┌────────────────────────────┐      ┌────────────────────────────┐      ┌────────────────────────────┐                                                              │
 │   │ 1-3. SYSTEM FREEZE (L4/L6) │─────>│ 4. META-LEARN SNAPSHOT     │─────>│ 5. ROOT CAUSE ANALYSIS     │                                                              │
 │   │ • Audit Snapshot Freeze    │      │ • Bundle Clock & Rules     │      │ • Bad-Habit Heatmap        │                                                              │
 │   │ • Telemetry Collection     │      │ • C0 Context Sealed        │      │ • L3 Blast Radius Autopsy  │                                                              │
 │   │ • Config/Threshold Record  │      │ • Immutable Case File      │      │ • RL Rollback Triggers     │                                                              │
 │   └────────────────────────────┘      └────────────────────────────┘      └─────────────┬──────────────┘                                                              │
 │                                                                                         │                                                                             │
 │                                 ┌───────────────────────────────────────────────────────┘                                                                             │
 │                                 │                                                                                                                                     │
 │                                 ▼                                                                                                                                     │
 │   ┌────────────────────────────┐      ┌────────────────────────────┐      ┌────────────────────────────┐                                                              │
 │   │ 6. PROPOSAL GENERATION     │─────>│ 7. VALIDATION GAUNTLET     │─────>│ 8. PATTERN EXTRACTION      │                                                              │
 │   │ • L1/L3 propose tuning     │      │ • L5 filter / Shadow check │(Pass)│ • Update Semantic Store    │                                                              │
 │   │ • proposal_only=True       │      │ • Oscillation detection    │      │ • New approved motif       │                                                              │
 │   │ • NO live mutation auth    │      │ • [Fail -> Loop back to 6] │      │ • Assign New Call Number   │                                                              │
 │   └─────────────▲──────────────┘      └─────────────┬──────────────┘      └─────────────┬──────────────┘                                                              │
 │                 │                                   │                                   │                                                                             │
 │                 └────────────────(Reject)───────────┘                                   ▼                                                                             │
 │                                                                           ┌────────────────────────────┐      ┌────────────────────────────┐                          │
 │                                                                           │ 9. COMMIT & ACTIVATION     │─────>│ [ BUS U: UPDATES TO L1 ]   │                          │
 │                                                                           │ • UWG writes to Control    │      │ • Deploys to Live Engine   │                          │
 │                                                                           │ • DUAL INJECTION REQUIRED  │      │ • Primes L1 for next run   │                          │
 │                                                                           │ • Archivist Receipt logged │      │ • Completes Evolution Loop │                          │
 │                                                                           └────────────────────────────┘      └────────────────────────────┘                          │
 ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ DETERMINISM PROOF STANDARD                                                                                                                                            │
 │ - Digest chain requires: registry_digest, agent_inventory, tool_inventory_hash, meta_learning_config_hash.                                                            │
 │ - Replay strictness: ALL historical mutations must be mathematically reconstructable from the ExecutionTrace Audit Envelope.                                          │
 └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
==============================================================================================================================================================================================================================