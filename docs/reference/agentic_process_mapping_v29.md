========================================================================================================================
[3] ROUTE DECISION + SWITCHING
========================================================================================================================

- The dispatcher takes the approved L1 plan and decides whether the request should short-circuit
  through exact reuse, bounded semantic reuse, grounded context assembly, external action
  dispatch, or safe fallback.
- L0 decides the path, but it does not itself do retrieval, think deeply, or perform the work.
- L0 consumes the L1 plan contract, applies route policy, and emits one bounded route outcome.

[ PEDAGOGICAL LEGEND ]  🔵 Blue asks = query_vec / intent vector
                        🟠 Orange knows = raw_text_vector / contextual_text_vector

 ┌────────────────────────────────────────────┐
 │ L0 ROUTING (Dispatcher)                    │
 │ - Ingress: L1Plan + 🔵 query_vec           │
 │ - Pre-filter: tenant / ACL / region bounds │
 │ - Enforce expiry / freshness requirements  │
 │ - Fast Fail: Reject invalid scope early    │
 └─────────────────────┬──────────────────────┘
                       ▼
 ┌────────────────────────────────────────────┐ yes  ┌──────────────────────────────────────┐
 │ D1: Exact cache key hit by policy?         ├───►  │ R1A EXACT CACHE                      ├───► [ RETURN ]
 │ - Check norm. query, route flags, shape    │      │ - Perfect keyed reuse, zero infer.   │
 │ - Authorize: permissions, freshness, ACL   │      │ - Bypass deep pipeline entirely      │
 │ - Deterministic keyed reuse, 0 new thought │      │ - Exact prior answer (NO C0 NEEDED)  │
 └─────────────────────┬──────────────────────┘      └──────────────────────────────────────┘
                    no ▼
 ┌────────────────────────────────────────────┐ yes  ┌──────────────────────────────────────┐
 │ D2: Semantic cache valid by policy?        ├───►  │ R1B SEMANTIC CACHE                   ├───► [ RETURN ]
 │ - Compare 🔵 query_vec to cached vec 🔵    │      │ - Policy-approved sim, bounded reuse │
 │ - Validate freshness, support threshold    │      │ - Reuse-safe tasks, no deep reading  │
 │ - Approximate match bounds, shape fits     │      │ - Short-circuit exec (NO C0 NEEDED)  │
 └─────────────────────┬──────────────────────┘      └──────────────────────────────────────┘
                    no ▼
 ┌────────────────────────────────────────────┐ yes  ┌──────────────────────────────────────┐
 │ D3: Requires grounded context?             ├───►  │ R3 AGENTIC RAG (THE RESEARCH RUNNER) │
 │ - Factual/policy claims require backing    │      │ - Evidence class & support target    │
 │ - User asks for citations/documents        │      │ - Strictly grounded answer only      │
 │ - Current/bounded-valid evidence needed    │      │ - Returns context only               │
 └─────────────────────┬──────────────────────┘      └──────────────────┬───────────────────┘
                    no ▼                                                │
 ┌────────────────────────────────────────────┐                         ▼                             ┌────────────────────────────────┐
 │ D4: Requires external action?              │      ┌──────────────────────────────────────┐         │ L4 STATE / ARCHIVE             │
 │ - Act on world, not just read              │      │ C0 CONTEXT ENGINE (Ref Desk)         ├──[R]──► │ - Canonical raw chunks 🟠      │
 │ - Send email, API, write candidate changes │      │ - C0.1 Plan: scope, freshness, ACL   │         │ - Dense vector / sparse index 🟠│
 └───────────┬────────────────────────┬───────┘      │ - C0.2 Fetch: 🔵 query vs 🟠 ctx_vec │         │ - Canonical source lineage     │
         yes │                     no │              │ - C0.3 Shape: dedupe, rerank, prune  │         │ - Version manifests / schema   │
             ▼                        ▼              │ - C0.4 Contract: verify spans, score │         │ - No direct write path exists  │
   ┌───────────────────┐    ┌───────────────────────┐└──────────────────┬───────────────────┘         └────────────────┬───────────────┘
   │ R4 ACTION         │    │ R5 FALLBACK           │                   │ [Evidence Contract]                          │
   │ - Dispatch action │    │ - Safest bound outcome│                   ▼                                              │
   │ - External payload│    │ - Abstain/clarify     │      ┌──────────────────────────────────────┐                      │
   │ - Mutate state    │    │ - Ungrounded default  │      │ PROMPT ASSEMBLY                      │◄───[state load]──────┘
   │ - NO C0 NEEDED    │    │ - NO C0 NEEDED        │      │ - PA.1 Load: system template, schema │
   └─────────┬─────────┘    └───────────┬───────────┘      │ - PA.2 Slot: context 🟠, contradict  │
             │                          │                  │ - PA.3 Budget: trim/reserve tokens   │
             │                          │                  │ - PA.4 Emit: PromptEnvelope, HMAC    │
             │                          │                  └──────────────────┬───────────────────┘
             │                          │                                     │
             └──────────────────────────┴────────────┬────────────────────────┘
                                                     │
                                                     ▼
                                            [ Dispatch to [4] ]