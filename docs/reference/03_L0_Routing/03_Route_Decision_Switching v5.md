                                          [ L1_PLAN_CONTRACT ]
                                                     │
                                                     ▼
========================================================================================================================================
[3] ROUTE DECISION + SWITCHING
========================================================================================================================================

- The dispatcher takes the approved L1 plan and decides whether the request should short-circuit
  through exact reuse, bounded semantic reuse, grounded context assembly, external action
  dispatch, or safe fallback.
- L0 decides the path, but it does not itself do retrieval, think deeply, or perform the work.

[ PEDAGOGICAL LEGEND ]  🔵 Blue asks = query_vec / intent vector
                        🟠 Orange knows = raw_text_vector / contextual_text_vector
                        🟢 Green maps = knowledge_graph / entity_subgraph

 ┌──────────────────────────────────────────────┐
 │ L0 ROUTING (Dispatcher)                      │
 │ - Ingress: L1Plan + 🔵 query_vec             │
 │ - Pre-filter: tenant / ACL / region bounds   │
 │ - Enforce expiry / freshness requirements    │
 │ - Fast Fail: Reject invalid scope early      │
 └──────────────────────┬───────────────────────┘
                        ▼
 ┌──────────────────────────────────────────────┐ yes  ┌────────────────────────────────────────┐        ┌────────────────────────────────────┐
 │ D1: Exact cache key hit by policy?           ├─────►│ R1A EXACT CACHE                        │◄───────┤ L4 STATE / ARCHIVE                 │
 │ - Check norm. query, route flags, shape      │      │ - Perfect keyed reuse, zero infer.     │        │ - Universal Persistence Boundary   │
 │ - Authorize: permissions, freshness, ACL     │      │ - Bypass deep pipeline entirely        ├─►[RET] │ - Cache Stores (Exact/Sem.)        │
 │ - Deterministic keyed reuse, 0 new thought   │      │ - Exact prior answer (NO C0 NEEDED)    │        │ - Canonical raw chunks 🟠          │
 └──────────────────────┬───────────────────────┘      └────────────────────────────────────────┘        │ - Dense vector / sparse index 🟠   │
                     no ▼                                                                                │ - Knowledge graph & entities 🟢    │
 ┌──────────────────────────────────────────────┐ yes  ┌────────────────────────────────────────┐        │ - Canonical source lineage         │
 │ D2: Semantic cache valid by policy?          ├─────►│ R1B SEMANTIC CACHE                     │◄───────┤ - Version manifests / schema       │
 │ - Compare 🔵 query_vec to cached vec 🔵      │      │ - Policy-approved sim, bounded reuse   │        │ - No direct write path exists      │
 │ - Validate freshness, support threshold      │      │ - Reuse-safe tasks, no deep reading    ├─►[RET] └──────────────────┬─────────────────┘
 │ - Approximate match bounds, shape fits       │      │ - Short-circuit exec (NO C0 NEEDED)    │                           │
 └──────────────────────┬───────────────────────┘      └────────────────────────────────────────┘                           │
                     no ▼                                                                                                   │
 ┌──────────────────────────────────────────────┐ yes  ┌────────────────────────────────────────┐                           │
 │ D3: Requires grounded context?               ├─────►│ R3 AGENTIC RAG (THE RESEARCH RUNNER)   │                           │
 │ - Factual/policy claims require backing      │      │ - Evidence class & support target      │                           │
 │ - User asks for citations/documents          │      │ - Strictly grounded answer only        │                           │
 │ - Current/bounded-valid evidence needed      │      │ - Returns context only                 │                           │
 └──────────────────────┬───────────────────────┘      └───────────────────┬────────────────────┘                           │
                     no ▼                                                  │                                                │
 ┌──────────────────────────────────────────────┐                          ▼                                                │
 │ D4: Requires external action?                │      ┌────────────────────────────────────────┐                           │
 │ - Act on world, not just read                │      │ C0 CONTEXT ENGINE (Ref Desk)           │◄──────────[ Read ]────────┘
 │ - Send email, API, write candidate changes   │      │ - C0.1 Plan: scope, freshness, ACL     │                           │
 └────────────┬─────────────────────────┬───────┘      │ - C0.2 Fetch: 🔵 query vs 🟠 ctx_vec   │                           │
          yes │                      no │              │ - C0.3 Graph: traverse entities 🟢     │                           │
              ▼                         ▼              │ - C0.4 Shape: dedupe, rerank, prune    │                           │
 ┌──────────────────────┐  ┌────────────────────────┐  │ - C0.5 Contract: verify spans, score   │                           │
 │ R4 ACTION            │  │ R5 FALLBACK            │  └───────────────────┬────────────────────┘                           │
 │ - Dispatch action    │  │ - Safest bound outcome │                      │ [Evidence Contract]                            │
 │ - External payload   │  │ - Abstain/clarify      │                      ▼                                                │
 │ - Mutate state       │  │ - Ungrounded default   │  ┌────────────────────────────────────────┐                           │
 │ - NO C0 NEEDED       │  │ - NO C0 NEEDED         │  │ PROMPT ASSEMBLY                        │◄──────────[ Load ]────────┘
 └────────────┬─────────┘  └────────────┬───────────┘  │ - PA.1 Load: system template, schema   │
              │                         │              │ - PA.2 Slot: context 🟠, contradict    │
              │                         │              │ - PA.3 Budget: trim/reserve tokens     │
              │                         │              │ - PA.4 Emit: PromptEnvelope, HMAC      │
              │                         │              └───────────────────┬────────────────────┘
              │                         │                                  │
              └─────────────────────────┴────────────────┬─────────────────┘
                                                         │
                                                         ▼
                                      ┌──────────────────────────────────────────────┐
                                      │ L3 ORCHESTRATE (Workflow / DAG Runner)        │
                                      │ - Ingress: approved route package from L0      │
                                      │   plus PromptEnvelope / action contract        │
                                      │ - Expand route into bounded execution graph    │
                                      │   (linear steps, branches, DAG, tool chain)    │
                                      │ - Resolve dependencies: what must finish       │
                                      │   before next step can unlock                  │
                                      │ - Track per-step preconditions, state handoff, │
                                      │   retry budget, timeout, and stop conditions   │
                                      │ - Coordinate agent / tool sequencing, fan-out, │
                                      │   fan-in, joins, and resumable checkpoints     │
                                      │ - Plan evolution allowed only inside policy,   │
                                      │   scope, budget, and route contract bounds     │
                                      └──────────────────────┬───────────────────────┘
                                                             ▼
                       ┌──────────────────────────────────────────────────────────────────────────────┐
                       │ O1: Single-step execution?                                                  │
                       │ - One bounded action / one tool / one model turn                            │
                       │ - No graph expansion needed                                                  │
                       └──────────────────────┬───────────────────────────────┬───────────────────────┘
                                           yes ▼                               │ no
                       ┌────────────────────────────────────────────┐          ▼
                       │ O1A DIRECT STEP PACKAGE                   │  ┌────────────────────────────────────────────┐
                       │ - Emit one step contract for L2           │  │ O2 MULTI-STEP WORKFLOW / DAG               │
                       │ - Inputs, guardrails, expected outputs    │  │ - Build nodes, edges, branch rules         │
                       │ - Send immediately to execution           │  │ - Encode dependency order and join rules   │
                       └──────────────────────┬─────────────────────┘  │ - Mark parallel-safe vs serial-only paths  │
                                              │                        └──────────────────────┬─────────────────────┘
                                              │                                               ▼
                                              │                        ┌────────────────────────────────────────────┐
                                              │                        │ O3 READY NODE SELECTION                    │
                                              │                        │ - Pick nodes whose dependencies are met    │
                                              │                        │ - Respect budget / policy / concurrency    │
                                              │                        │ - Hold blocked nodes until prerequisites   │
                                              │                        └──────────────────────┬─────────────────────┘
                                              │                                               ▼
                                              └──────────────────────────────┬────────────────────────────────────────────┐
                                                                             │                                            │
                                                                             ▼                                            │
                                                          ┌────────────────────────────────────────────┐                    │
                                                          │ STEP CONTRACT TO L2                        │                    │
                                                          │ - Current node only, bounded autonomy      │                    │
                                                          │ - Tool / model / action spec               │                    │
                                                          │ - Inputs, evidence, expected artifact      │                    │
                                                          └──────────────────────┬─────────────────────┘                    │
                                                                                 │                                          │
                                                                                 ▼                                          │
                                                                      [ Dispatch to [4] L2_EXECUTE ]                       │
                                                                                 │                                          │
                                                                                 ▼                                          │
                                                          ┌────────────────────────────────────────────┐                    │
                                                          │ STEP RESULT RETURN                          │◄───────────────────┘
                                                          │ - Status, outputs, artifacts, errors       │
                                                          │ - Retry signal / branch result / handoff   │
                                                          └──────────────────────┬─────────────────────┘
                                                                                 ▼
                                                          ┌────────────────────────────────────────────┐
                                                          │ O4 GRAPH STATE UPDATE                       │
                                                          │ - Mark node done / failed / retry          │
                                                          │ - Unlock dependents or trigger repair path │
                                                          │ - Rejoin branches and test exit criteria   │
                                                          └──────────────────────┬─────────────────────┘
                                                                                 ▼
                                                          ┌────────────────────────────────────────────┐
                                                          │ O5 WORKFLOW COMPLETE?                       │
                                                          │ - All required nodes sealed                │
                                                          │ - Exit package ready for control layer     │
                                                          └──────────────────────┬─────────────────────┘
                                                                             yes ▼          no
                                                                  [ Return sealed work ]     └──────► back to O3