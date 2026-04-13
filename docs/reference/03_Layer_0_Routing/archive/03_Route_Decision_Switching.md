======================================================================================================================================
[3] ROUTE DECISION + SWITCHING
[3] THE HALLWAY DIRECTOR | DECIDING WHICH AISLE, DESK, OR OUTSIDE LANE TO USE
======================================================================================================================================
- The dispatcher that takes the approved L1 plan and decides whether the request should short-circuit through exact reuse,
  bounded semantic reuse, grounded context assembly, external action dispatch, or safe fallback.
- This is route authority, not reasoning authority. L0 decides the path, but it does not itself do retrieval, think deeply,
  or perform the work.
 [ PEDAGOGICAL LEGEND ]  🔵 Blue asks = query_vec / intent vector   🟠 Orange knows = raw_text_vector / contextual_text_vector
                                              [ L0 INGRESS: L1Plan + route_signal + normalized_query + query_vec ]
                                                                       │
                                                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PRE-ROUTING GATE | FRONT DESK SECURITY BEFORE ANY CACHE OR RETRIEVAL                                                               │
│ - tenant / ACL / region / confidentiality filters                                                                                  │
│ - effective / expiry dates and freshness band requirements                                                                         │
│ - version bind and route policy bind                                                                                               │
│ - route authority remains separate from retrieval authority                                                                        │
│ invariant: pre-filter first so invalid scope never contaminates cache reuse or retrieval recall                                    │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ D1: THE "RETURN CART" CHECK (EXACT CACHE)                                                                                          │
│ [ K1 CHECK THE SLIP ]───[ gate ]──►[ K2 SECURITY GUARD ]────[ test ]──►[ K3 MATCH TEST ]                                           │
│ - normalized query                  - permissions / freshness           - exact cache key by policy                                │
│ - route flags / task class          - tenant / scope isolation          - route_signal + version bind                              │
│ - symbolic ticket / version         - no patron-data mixing             - zero new thinking if hit                                 │
│ - exact shape / output contract     - safe-to-reuse only                - stale items evicted if invalid                           │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                              ┌────────────────────────────────[ hit ]─┴─[ miss ]───────────────────────────────────────┐
                              ▼                                                                                         ▼
┌─────────────────────────┐                                      ┌───────────────────────────────────────────────────────────────────┐
│ R1A HAND THEM THE BOOK  │                                      │ D2: THE "RECENT ANSWERS" CHECK (SEMANTIC CACHE)                   │
│ - perfect keyed reuse   │                                      │ [ S1 COMPARE NOTES ]───────[ bound ]──►[ S2 CHECK RULES ]         │
│ - zero extra inference  │                                      │ - compare 🔵 query_vec to cached vec   - approve support threshold│
│ - update access log only│                                      │ - same section / tenant / version      - freshness / policy valid │
│ - bypass deep pipeline  │                                      │ - approximate match only               - no unsafe semantic reuse │
└───────────┬─────────────┘                                      └──────────────────────────┬────────────────────────────────────────┘
            │                                                     ┌────────────────[ pass ]─┴─[ fail ]────────────┐
            │                                                     ▼                                               ▼
            │                                           ┌─────────────────────────┐             ┌────────────────────────────────────┐
            │                                           │ R1B HAND THEM OLD NOTES │             │ D3: NEED REAL BOOKS? (GROUNDED)    │
            │                                           │ - policy-approved sim   │             └────────────┬───────────────────────┘
            │                                           │ - bounded sem reuse     │            ┌───────[ yes]┴[ no ]───────┐
            │                                           │ - no deep reading       │            ▼                           ▼
            │                                           └────────────┬────────────┘ ┌─────────────────────────┐ ┌───────────────────────┐
            │                                                        │              │ R3 THE RESEARCH RUNNER  │ │ D4: OUTSIDE HELP?     │
            │                                                        │              │ - evidence class        │ └───────────┬───────────┘
            │                                                        │              │ - support target        │       ┌─[yes]─┴─[no]─┐
            │                                                        │              │ - citation requirement  │       ▼              ▼
            │                                                        │              │ - grounded answer only  │ ┌───────────────┐ ┌───────────────┐
            │                                                        │              └───────────┬─────────────┘ │R4 OUTSIDE HELP│ │R5 SAFE DEFAULT│
            │                                                        │                          │               │action dispatch│ │abstain/clarify│
            │                                                        │                          │               │packet only    │ │bounded backup │
            │                                                        │                          │               └───────┬───────┘ └───────┬───────┘
[ EARLY RETURN PATHS ]◄──────────────────────────────────────────────┘              [ context ] │             [ build ] │        [ emit ] │
                                                                                                ▼                       │                 │
┌───────────────────────────────────────────────────────────────────────────────────────────────┐                       │                 │
│ C0 CONTEXT ENGINE | THE REFERENCE DESK                                                        │                       │                 │
│ retrieves and grounds only. never routes. never executes.                                     │                       │                 │
├───────────────────────────────────────────────────────────────────────────────────────────────┤                       │                 │
│ C0.1 RETRIEVAL PLAN                                                                           │                       │                 │
│ - source scope             - freshness window         - access / security filters             │                       │                 │
│ - retrieval mode           - ACL prefilter            - version / tenant bind                 │                       │                 │
│ C0.2 EVIDENCE FETCH                                                                           │                       │                 │
│ - dense recall: 🔵 query_vec against 🟠 raw_text_vector and contextual_text_vector           │                       │                 │
│ - sparse recall: exact term / code / schema match                                             │                       │                 │
│ - metadata hydration       - parent lookup keys       - cache reuse where allowed             │                       │                 │
│ C0.3 EVIDENCE SHAPING                                                                         │                       │                 │
│ - dedupe                   - parent/child expand      - provenance retention                  │                       │                 │
│ - rerank by support        - contradiction retain     - preserve citations                    │                       │                 │
│ - top validated winners only                          - no generic defaults                   │                       │                 │
│ C0.4 EVIDENCE CONTRACT                                                                        │                       │                 │
│ - support scoring          - verified chunks / cited spans  - source_ids / dates              │                       │                 │
│ - coverage_score / gaps    - contradiction_status           - abstain / next_action hint      │                       │                 │
└───────────────────────────────────────────────┬───────────────────────────────────────────────┘                       │                 │
                                                │ [ prompt ]                                                            │                 │
                                                ▼                                                                       │                 │
┌───────────────────────────────────────────────────────────────────────────────────────────────┐                       │                 │
│ PROMPT ASSEMBLY | PREPARING THE WORKSPACE                                                     │                       │                 │
│ packages grounded context only. does not retrieve.                                            │                       │                 │
├───────────────────────────────────────────────────────────────────────────────────────────────┤                       │                 │
│ PA.1 LOAD STATIC BLOCKS                                                                       │                       │                 │
│ - system template             - policy refs                 - output schema                   │                       │                 │
│ - persona / mode              - S0 invariants               - role / mixin blocks             │                       │                 │
│ PA.2 SLOT CONTEXT + TASK                                                                      │                       │                 │
│ - must-use evidence           - optional evidence           - citation anchors                │                       │                 │
│ - contradiction flags         - slot C0 before U0           - forbid U0/C0 policy invention   │                       │                 │
│ PA.3 TOKEN BUDGETER                                                                           │                       │                 │
│ - trim / stratify if needed   - reserve safety / schema     - preserve instruction order      │                       │                 │
│ - overflow -> refine/abstain  - validate slot precedence    - check boundary limits           │                       │                 │
│ PA.4 PROMPT CONTRACT                                                                          │                       │                 │
│ - PromptEnvelope              - PromptAssemblyStatus        - citations_required              │                       │                 │
│ - authority slot order        - signed artifact             - HMAC / replay metadata          │                       │                 │
└───────────────────────────────────────────────┬───────────────────────────────────────────────┘                       │                 │
                                                │                                                                       │                 │
                                                ▼                                                                       │                 │
┌───────────────────────────────────────────────────────────────────────────────────────────────┐                       │                 │
│ L4 READ-ONLY KNOWLEDGE SUBSTRATE                                                              │                       │                 │
│ - canonical raw chunks          - parent-child index          - dense search index            │                       │                 │
│ - sparse keyword index          - metadata / registry         - canonical source lineage      │                       │                 │
│ - access / freshness filters    - versioned cache manifests   - template_id / schema_version  │                       │                 │
│ invariant: L4 serves read surfaces only here. No direct write path exists.                    │                       │                 │
└───────────────────────────────────────────────┬───────────────────────────────────────────────┘                       │                 │
                                                └─────────────────────────────────────────┬─────────────────────────────┴─────────────────┴─┐
                                                                                          ▼                             ▼                   ▼
                                                                                 [ PromptEnvelope ]             [ Action Packet ]    [ Fallback ]
                                                                                          │                             │                   │
                                                                                          └─────────────────────────────┼───────────────────┘
                                                                                                                        ▼
                                                                                                         [ DISPATCH TO READING ROOM [4] ]