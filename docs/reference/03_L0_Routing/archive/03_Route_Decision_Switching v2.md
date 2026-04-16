====================================================================================================
[3] ROUTE DECISION + SWITCHING
[3] THE HALLWAY DIRECTOR | DECIDING WHICH AISLE, DESK, OR OUTSIDE LANE TO USE
====================================================================================================
- The dispatcher takes the approved L1 plan and decides whether the request should short-circuit
  through exact reuse, bounded semantic reuse, grounded context assembly, external action
  dispatch, or safe fallback.
- L0 decides the path, but it does not itself do retrieval, think deeply, or perform the work.
- L0 consumes the L1 plan contract, applies route policy, and emits one bounded route outcome.

[ PEDAGOGICAL LEGEND ]  🔵 Blue asks = query_vec / intent vector
                        🟠 Orange knows = raw_text_vector / contextual_text_vector

                         [ L0 INGRESS: L1Plan + route_signal + normalized_query + query_vec ]
                                                         │
                                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PRE-ROUTING GATE | FRONT DESK SECURITY BEFORE ANY CACHE OR RETRIEVAL                             │
│ [ G1 TENANT/SCOPE ]──[ G2 TIME/VERSION ]──[ G3 POLICY BIND ]──[ G4 ROUTE PERMISSION ]            │
│ - tenant / ACL / region / confidentiality filters                                                │
│ - effective / expiry dates and freshness band requirements                                       │
│ - version bind and route policy bind                                                             │
│ - route authority remains separate from retrieval authority                                      │
│ - verify this request is even allowed to attempt reuse / grounding / action                      │
│ - reject invalid scope before any cache lookup or retrieval exposure                             │
│ invariant: pre-filter first so invalid scope never contaminates cache reuse or retrieval recall  │
└────────────────────────────────────────────┬─────────────────────────────────────────────────────┘
                                          [ pass ]
                                             ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ D1: THE "RETURN CART" CHECK (EXACT CACHE)                                                        │
│ [ K1 CHECK SLIP ]──[gate]►[ K2 SECURITY ]──[test]►[ K3 MATCH ]──[decide]►[ R1A / continue ]      │
│ - normalized query         - permissions/freshness      - exact cache key by policy              │
│ - route flags/task class   - tenant/scope isolation     - route_signal + version bind            │
│ - symbolic ticket/version  - no patron-data mixing      - exact shape/output contract            │
│ - exact requested form     - safe-to-reuse only         - zero new thinking if hit               │
│ - exact policy/schema      - stale items evicted        - deterministic keyed reuse only         │
│                                                                                                  │
│ SELECT R1A ONLY IF ALL ARE TRUE:                                                                 │
│ - exact cache key matches current normalized request + route policy + version bind               │
│ - cached artifact is still fresh enough for the request's freshness band                         │
│ - same tenant / ACL / confidentiality scope                                                      │
│ - output contract exactly matches the requested answer shape                                     │
│ - no extra grounding, tool action, or regeneration is required                                   │
│                                                                                                  │
│ DO NOT SELECT R1A IF ANY ARE TRUE:                                                               │
│ - exact key miss                             - permission / tenant / region mismatch             │
│ - stale or expired artifact                  - answer contract differs from what run requires    │
│ - policy/schema/version mismatch             - request explicitly requires fresh evidence/action │
└────────────────────────────────────────────┬─────────────────────────────────────────────────────┘
                               ┌─[ hit: exact fresh key ]─┴─[ miss: exact key ]─┐
                               ▼                                                ▼
┌────────────────────────┐                   ┌─────────────────────────────────────────────────────┐
│ R1A HAND THEM THE BOOK │                   │ D2: THE "RECENT ANSWERS" CHECK (SEMANTIC CACHE)     │
│ - perfect keyed reuse  │                   │ [ S1 COMPARE NOTES ]──[bound]►[ S2 CHECK RULES ]    │
│ - zero extra inference │                   │ - compare 🔵 query_vec to cached vec                │
│ - update access log    │                   │ - same section / tenant / version                   │
│ - bypass deep pipeline │                   │ - approximate match only                            │
│ - exact prior answer   │                   │ - bounded to reuse-safe task classes                │
└──────────┬─────────────┘                   │ - approve support threshold                         │
           │                                 │ - freshness / policy valid                          │
           │                                 │ - no unsafe semantic reuse                          │
           │                                 │ - answer form still fits                            │
           │                                 └────────────────────┬────────────────────────────────┘
           │                                   ┌─[ pass: safe threshold ]─┴─[ fail: below limit ]─┐
           │                                   ▼                                                  ▼
           │               ┌─────────────────────────┐         ┌──────────────────────────────────┐
           │               │ R1B HAND THEM OLD NOTES │         │ D3: GROUNDED RETRIEVAL NEXT?     │
           │               │ - policy-approved sim   │         │ - read/support with evidence     │
           │               │ - bounded sem reuse     │         │ [ C1 CHECK CLAIM TYPE ]          │
           │               │ - no deep reading       │         │ [ C2 CHECK EVIDENCE NEED ]       │
           │               │ - no retrieval now      │         │ [ C3 CHECK FRESH/CITATION ]      │
           │               └────────────┬────────────┘         │ [ C4 CHECK SUFF. OF MEMORY]      │
           │                            │                      └────────────────┬─────────────────┘
           │                            │               ┌─[ yes: read/support ]─┴─[ no: check action ]─┐
           │                            │               ▼                                              ▼
           │                            │ ┌────────────────────────┐      ┌──────────────────────────────┐
           │                            │ │ R3 THE RESEARCH RUNNER │      │ D4: EXTERNAL ACTION NEXT?    │
           │                            │ │ - evidence class       │      │ - act on world (do/act)      │
           │                            │ │ - support target       │      │ - send email, API, event     │
           │                            │ │ - citation requirement │      │ - write candidate changes    │
           │                            │ │ - grounded answer only │      └──────────────┬───────────────┘
           │                            │ └────────────┬───────────┘            ┌─[ yes: do/act ]─┴─[ no: fallback ]─┐
           │                            │              │                        ▼                                    ▼
           │                            │              │                ┌────────────────┐                   ┌────────────────┐
           │                            │              │                │R4 OUTSIDE HELP │                   │R5 SAFE DEFAULT │
           │                            │              │                │- action payload│                   │- abstain/abort │
           │                            │              │                │- act on world  │                   │- bounded backup│
           │                            │              │                │- NO C0 NEEDED  │                   │- NO C0 NEEDED  │
           │                            │              │                └───────┬────────┘                   └───────┬────────┘
           ◄──[ EARLY RETURNS ]─────────┴──────────────┼────────────────────────┴────────────────────────────────────┴─┐
                                                       │                                                               │
                                                 [ context ]                                                [ BYPASS C0 RETRIEVAL ]
                                                       ▼                                                               │
┌───────────────────────────────────────────────────────────────────────────────────────────────┐                      │
│ C0 CONTEXT ENGINE | THE REFERENCE DESK                                                        │                      │
│ retrieves and grounds only. never routes. never executes.                                     │                      │
├───────────────────────────────────────────────────────────────────────────────────────────────┤                      │
│ C0.1 RETRIEVAL PLAN                                                                           │                      │
│ - source scope             - freshness window           - access / security filters           │                      │
│ - retrieval mode           - ACL prefilter              - version / tenant bind               │                      │
│ C0.2 EVIDENCE FETCH                                                                           │                      │
│ - dense recall: 🔵 query_vec against 🟠 raw_text_vector and contextual_text_vector            │                      │
│ - sparse recall: exact term / code / schema match                                             │                      │
│ - metadata hydration       - parent lookup keys         - cache reuse where allowed           │                      │
│ C0.3 EVIDENCE SHAPING                                                                         │                      │
│ - dedupe                   - parent/child expand        - provenance retention                │                      │
│ - rerank by support        - contradiction retain       - preserve citations                  │                      │
│ - top validated winners only                            - no generic defaults                 │                      │
│ C0.4 EVIDENCE CONTRACT                                                                        │                      │
│ - support scoring          - verified chunks/cited spans- source_ids / dates                  │                      │
│ - coverage_score / gaps    - contradiction_status       - abstain / next_action hint          │                      │
└───────────────────────────────────────────────┬───────────────────────────────────────────────┘                      │
                                            [ prompt ]                                                                 │
                                                ▼                                                                      │
┌───────────────────────────────────────────────────────────────────────────────────────────────┐                      │
│ PROMPT ASSEMBLY | PREPARING THE WORKSPACE                                                     │                      │
│ packages grounded context only. does not retrieve.                                            │                      │
├───────────────────────────────────────────────────────────────────────────────────────────────┤                      │
│ PA.1 LOAD STATIC BLOCKS                                                                       │                      │
│ - system template          - policy refs                - output schema                       │                      │
│ - persona / mode           - S0 invariants              - role / mixin blocks                 │                      │
│ PA.2 SLOT CONTEXT + TASK                                                                      │                      │
│ - must-use evidence        - optional evidence          - citation anchors                    │                      │
│ - contradiction flags      - slot C0 before U0          - forbid U0/C0 policy invention       │                      │
│ PA.3 TOKEN BUDGETER                                                                           │                      │
│ - trim / stratify needed   - reserve safety / schema    - preserve instruction order          │                      │
│ - overflow->refine/abstain - validate slot precedence   - check boundary limits               │                      │
│ PA.4 PROMPT CONTRACT                                                                          │                      │
│ - PromptEnvelope           - PromptAssemblyStatus       - citations_required                  │                      │
│ - authority slot order     - signed artifact            - HMAC / replay metadata              │                      │
└───────────────────────────────────────────────┬───────────────────────────────────────────────┘                      │
                                                ▼                                                                      │
┌───────────────────────────────────────────────────────────────────────────────────────────────┐                      │
│ L4 READ-ONLY KNOWLEDGE SUBSTRATE                                                              │                      │
│ - canonical raw chunks       - parent-child index         - dense search index                │                      │
│ - sparse keyword index       - metadata / registry        - canonical source lineage          │                      │
│ - access/freshness filters   - versioned manifests        - template_id / schema_version      │                      │
│ invariant: L4 serves read surfaces only here. No direct write path exists.                    │                      │
└───────────────────────────────────────────────┬───────────────────────────────────────────────┘                      │
                                                └─────────────────────────┬────────────────────────────────────────────┴─┐
                                                                          ▼                                              ▼
                                                                 [ PromptEnvelope ]                              [ Action / Fallback ]
                                                                          │                                              │
                                                                          └───────────────────────┬──────────────────────┘
                                                                                                  ▼
                                                                                   [ DISPATCH TO READING ROOM [4] ]