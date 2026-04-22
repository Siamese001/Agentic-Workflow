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
                                      ┌────────────────────────────────────────┐
                                      │ L3 ORCHESTRATE                         │
                                      │ - Expand approved route into steps     │
                                      │ - Coordinate agent / tool sequence     │
                                      │ - Manage retries, branches, handoffs   │
                                      │ - Hold plan evolution within bounds    │
                                      │ - Send one bounded step at a time      │
                                      │   to L2 for execution                  │
                                      └───────────────────┬────────────────────┘
                                                          │
                                                          ▼
                                              [ Dispatch to [4] L2_EXECUTE ]