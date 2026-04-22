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
- L0 emits a deterministic route contract: selected route, confidence, reason codes, freshness class,
  cache policy, and execution form.
- L3 is OPTIONAL and is invoked only when the selected route must be expanded into managed steps.
- Direct-return routes and single-pass routes may bypass L3 entirely.

[ PEDAGOGICAL LEGEND ]  🔵 Blue asks = query_vec / intent vector
                        🟠 Orange knows = raw_text_vector / contextual_text_vector
                        🟢 Green maps = knowledge_graph / entity_subgraph

 ┌──────────────────────────────────────────────┐
 │ L0 ROUTING (Dispatcher)                      │
 │ - Ingress: L1Plan + 🔵 query_vec             │
 │ - Pre-filter: tenant / ACL / region bounds   │
 │ - Enforce expiry / freshness requirements    │
 │ - Fast Fail: Reject invalid scope early      │
 │ - Score: cacheable / grounded / action /     │
 │   multi-hop / freshness / support needs      │
 │ - Emit route contract, not the work itself   │
 └──────────────────────┬───────────────────────┘
                        ▼
 ┌──────────────────────────────────────────────┐ yes  ┌────────────────────────────────────────┐        ┌────────────────────────────────────┐
 │ D1: Exact cache key hit by policy?           ├─────►│ R1A EXACT CACHE                        │◄───────┤ L4 STATE / ARCHIVE                 │
 │ - Check norm. query, route flags, shape      │      │ - Perfect keyed reuse, zero infer.     │        │ - Universal Persistence Boundary   │
 │ - Authorize: permissions, freshness, ACL     │      │ - Bypass deep pipeline entirely        ├─►[RET] │ - Cache Stores (Exact/Sem.)        │
 │ - Deterministic keyed reuse, 0 new thought   │      │ - Exact prior answer (NO C0 NEEDED)    │        │ - Canonical raw chunks 🟠          │
 │ - Terminal short-circuit route               │      │ - NO L3 NEEDED                         │        │ - Dense vector / sparse index 🟠   │
 └──────────────────────┬───────────────────────┘      └────────────────────────────────────────┘        │ - Knowledge graph & entities 🟢    │
                     no ▼                                                                                │ - Canonical source lineage         │
 ┌──────────────────────────────────────────────┐ yes  ┌────────────────────────────────────────┐        │ - Version manifests / schema       │
 │ D2: Semantic cache valid by policy?          ├─────►│ R1B SEMANTIC CACHE                     │◄───────┤ - No direct write path exists      │
 │ - Compare 🔵 query_vec to cached vec 🔵      │      │ - Policy-approved sim, bounded reuse   │        └──────────────────┬─────────────────┘
 │ - Validate freshness, support threshold      │      │ - Reuse-safe tasks, no deep reading    ├─►[RET]                    │
 │ - Approximate match bounds, shape fits       │      │ - Short-circuit exec (NO C0 NEEDED)    │                            │
 │ - Deny if volatile / high-risk / weak fit    │      │ - Terminal short-circuit route         │                            │
 │ - If approved, no orchestration required     │      │ - NO L3 NEEDED                         │                            │
 └──────────────────────┬───────────────────────┘      └────────────────────────────────────────┘                            │
                     no ▼                                                                                                    │
 ┌──────────────────────────────────────────────┐ yes  ┌────────────────────────────────────────┐                            │
 │ D3: Requires grounded context?               ├─────►│ R3 AGENTIC RAG (THE RESEARCH RUNNER)   │                            │
 │ - Factual/policy claims require backing      │      │ - Evidence class & support target      │                            │
 │ - User asks for citations/documents          │      │ - Route mode: fast / rewrite /         │                            │
 │ - Current/bounded-valid evidence needed      │      │   decompose / multi-index              │                            │
 │ - Multi-hop / synthesis / freshness needed   │      │ - Strictly grounded answer only        │                            │
 │ - Simple single-pass grounding may bypass L3 │      │ - Returns context only                 │                            │
 │ - Adaptive/multi-stage grounding invokes L3  │      └───────────────────┬────────────────────┘                            │
 └──────────────────────┬───────────────────────┘                          ▼                                                 │
                     no ▼                               ┌────────────────────────────────────────┐                            │
 ┌──────────────────────────────────────────────┐       │ C0 CONTEXT ENGINE (Ref Desk)           │◄──────────[ Read ]────────┘
 │ D4: Requires external action?                │       │ - C0.1 Plan: scope, freshness, ACL     │
 │ - Act on world, not just read                │       │ - C0.2 Fetch: 🔵 query vs 🟠 ctx_vec   │
 │ - Send email, API, write candidate changes   │       │ - C0.3 Graph: traverse entities 🟢     │
 │ - One bounded action may bypass L3           │       │ - C0.4 Shape: dedupe, rerank, prune    │
 │ - Multi-step action/workflow invokes L3      │       │ - C0.5 Contract: verify spans, score   │
 └────────────┬─────────────────────────┬───────┘       │ - C0.6 If weak: rewrite / broaden /    │
          yes │                      no │               │   decompose within route budget        │
              ▼                         ▼               └───────────────────┬────────────────────┘
 ┌──────────────────────┐  ┌────────────────────────┐                       │ [Evidence Contract]
 │ R4 ACTION            │  │ R5 FALLBACK            │                       ▼
 │ - Dispatch action    │  │ - Safest bound outcome │   ┌────────────────────────────────────────┐
 │ - External payload   │  │ - Abstain/clarify      │   │ PROMPT ASSEMBLY                        │◄──────────[ Load ]────────┘
 │ - Mutate state       │  │ - Ungrounded default   │   │ - PA.1 Load: system template, schema   │
 │ - Single action may  │  │ - Terminal safe route  │   │ - PA.2 Slot: context 🟠, contradict    │
 │   go direct to L2    │  │ - NO C0 NEEDED         │   │ - PA.3 Budget: trim/reserve tokens     │
 │ - Workflow action    │  │ - NO L3 NEEDED         │   │ - PA.4 Emit: PromptEnvelope, HMAC      │
 │   goes to L3         │  └────────────┬───────────┘   │ - Smallest high-signal grounded set    │
 └────────────┬─────────┘               │               └───────────────────┬────────────────────┘
              │                         │                                   │
              └─────────────────────────┴─────────────────┬─────────────────┘
                                                          │
                                                          ▼
                                       ┌──────────────────────────────────────────────┐
                                       │ D5: DOES THE SELECTED ROUTE REQUIRE          │
                                       │     ORCHESTRATION?                           │
                                       │ - More than one managed step?                │
                                       │ - Dependency order / branching / joins?      │
                                       │ - Retries across steps / checkpoints?        │
                                       │ - Multi-tool / multi-agent coordination?     │
                                       │ - Resumable workflow state?                  │
                                       │ - Sequencing 🔵 asks, 🟠 evidence, or 🟢     │
                                       │   graph traversals across steps?             │
                                       └──────────────────────┬───────────────────────┘
                                                          yes ▼                    no ├────────────────────────────────────────────────┐
                                       ┌──────────────────────────────────────────────┐                                                │
                                       │ L3 ORCHESTRATE (Workflow / DAG Runner)       │                                                │
                                       │ - Ingress: approved route package from L0    │                                                │
                                       │   plus PromptEnvelope / action contract      │                                                │
                                       │ - Expand route into bounded execution graph  │                                                │
                                       │   (linear steps, branches, DAG, tool chain)  │                                                │
                                       │ - Sequence step-level 🔵 asks when retrieval,│                                                │
                                       │   subqueries, or follow-on lookups are needed│                                                │
                                       │ - Carry forward validated 🟠 evidence packets│                                                │
                                       │   support sets, and grounded handoffs        │                                                │
                                       │ - Coordinate 🟢 graph/entity traversal when  │                                                │
                                       │   route logic depends on subgraph expansion  │                                                │
                                       │ - Resolve dependencies: what must finish     │                                                │
                                       │   before next step can unlock                │                                                │
                                       │ - Track per-step preconditions, state handoff│                                                │
                                       │   retry budget, timeout, and stop conditions │                                                │
                                       │ - Coordinate agent / tool sequencing, fan-out│                                                │
                                       │   fan-in, joins, and resumable checkpoints   │                                                │
                                       │ - Plan evolution allowed only inside policy, │                                                │
                                       │   scope, budget, and route contract bounds   │                                                │
                                       └──────────────────────┬───────────────────────┘                                                │
                                                              │                                                                        │
                                                              ▼                                                                        │
                       ┌──────────────────────────────────────────────────────────────┐                                                │
                       │ O1: Single-step execution?                                   │                                                │
                       │ - One bounded action / one tool / one model turn             │                                                │
                       │ - No graph expansion needed                                  │                                                │
                       │ - No multi-step 🔵/🟠/🟢 sequencing needed                     │                                                │
                       └──────────────────────┬───────────────────────┬───────────────┘                                                │
                                          yes ▼                    no ▼                                                                │
                       ┌────────────────────────────────────────┐  ┌────────────────────────────────────────────┐                      │
                       │ O1A DIRECT STEP PACKAGE                │  │ O2 MULTI-STEP WORKFLOW / DAG               │                      │
                       │ - Emit one step contract for L2        │  │ - Build nodes, edges, branch rules         │                      │
                       │ - Inputs, guardrails, expected outputs │  │ - Encode dependency order and join rules   │                      │
                       │ - May contain one 🔵 ask or one action │  │ - Mark parallel-safe vs serial-only paths  │                      │
                       │ - Send immediately to execution        │  │ - Assign where 🔵 asks, 🟠 evidence, and   │                      │
                       └──────────────────────┬─────────────────┘  │   🟢 graph steps enter the DAG             │                      │
                                              │                    └──────────────────────┬─────────────────────┘                      │
                                              │                                           ▼                                            │
                                              │                    ┌────────────────────────────────────────────┐                      │
                                              │                    │ O3 READY NODE SELECTION                    │◄────────────────┐    │
                                              │                    │ - Pick nodes whose dependencies are met    │                 │    │
                                              │                    │ - Respect budget / policy / concurrency    │                 │    │
                                              │                    │ - Hold blocked nodes until prerequisites   │                 │    │
                                              │                    │ - Ensure required 🟠 support is present    │                 │    │
                                              │                    │   before dependent execution unlocks       │                 │    │
                                              │                    └──────────────────────┬─────────────────────┘                 │    │
                                              │                                           ▼                                       │    │
                                              └─────────────────────────┬─────────────────┘                                       │    │
                                                                        │                                                         │    │
                                                                        ▼                                                         │    │
                                                         ┌────────────────────────────────────────────┐                           │    │
                                                         │ STEP CONTRACT TO L2                        │                           │    │
                                                         │ - Current node only, bounded autonomy      │                           │    │
                                                         │ - Tool / model / action spec               │                           │    │
                                                         │ - Inputs may include 🔵 query intent,      │                           │    │
                                                         │   🟠 grounded evidence, 🟢 graph payload   │                           │    │
                                                         │ - Expected artifact / support target       │                           │    │
                                                         └──────────────────────┬─────────────────────┘                           │    │
                                                                                │                                                 │    │
                                                                                ▼                                                 │    │
                                                                     [ Dispatch to [4] L2_EXECUTE ] ◄─────────────────────────────┼────┘
                                                                                │                                                 │
                                                                                ▼                                                 │
                                                         ┌────────────────────────────────────────────┐                           │
                                                         │ STEP RESULT RETURN                         │                           │
                                                         │ - Status, outputs, artifacts, errors       │                           │
                                                         │ - May return new 🟠 evidence, updated 🟢   │                           │
                                                         │   graph state, or next 🔵 ask candidates   │                           │
                                                         │ - Retry signal / branch result / handoff   │                           │
                                                         └──────────────────────┬─────────────────────┘                           │
                                                                                ▼                                                 │
                                                         ┌────────────────────────────────────────────┐                           │
                                                         │ O4 GRAPH STATE UPDATE                      │                           │
                                                         │ - Mark node done / failed / retry          │                           │
                                                         │ - Unlock dependents or trigger repair path │                           │
                                                         │ - Rejoin branches and test exit criteria   │                           │
                                                         │ - Merge returned 🟠 support and 🟢 graph   │                           │
                                                         │   outcomes into next-step readiness        │                           │
                                                         └──────────────────────┬─────────────────────┘                           │
                                                                                ▼                                                 │
                                                         ┌────────────────────────────────────────────┐                           │
                                                         │ O5 WORKFLOW COMPLETE?                      │                           │
                                                         │ - All required nodes sealed                │                           │
                                                         │ - All required 🟠 support satisfied        │                           │
                                                         │ - Exit package ready for control layer     │                           │
                                                         └──────────────────────┬─────────────────────┘                           │
                                                                            yes ▼                  no ────────────────────────────┘
                                                                 [ Return sealed work ]