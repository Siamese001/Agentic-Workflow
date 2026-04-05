========================================================================================================================================================================================
[ ABOVE GOVERNANCE & SAFETY CONTEXT | governed packet enters from routing/orchestration (Patron arriving with a reading list) ]
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INVARIANT: no execution, mutation, or external call proceeds without L5 certification (Head Librarian's Stamp) against active policy + structure + registry
========================================================================================================================================================================================
                                                                    │
                                                               [ walks in ]
                                                                    ▼
========================================================================================================================================================================================
[ GOVERNANCE & SAFETY | L5 ENFORCEMENT PLANE | SINGLE-BOX v25 TRIPLE-CLICK (The Grand Library) ]
========================================================================================================================================================================================

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G1: GOVERNANCE INVOCATION | Front Desk Triage                                                                                                                                │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ - receive request for governance review (Patron submits reading request)                                                                                                     │
│ - identify mode: STATIC_CHECK (Card Catalog) | RUNTIME_CHECK (Reading Room) | HUMAN_REENTRY (Appeals)                                                                        │
│ - route into appropriate enforcement lane (Point to correct library wing)                                                                                                    │
│ [OUT: governance mode + review request (Patron Slip issued)]                                                                                                                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    │
                                                              [ hands slip ]
                                                                    ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G2: AUTHORITY CONTEXT RESOLUTION | The Master Charter Desk                                                                                                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ - resolve active policy set (Fetch the current Rulebook)                                                                                                                     │
│ - resolve structure blueprint (Fetch the Stack Map)                                                                                                                          │
│ - resolve registry constraints (Fetch the Authorized Patron List)                                                                                                            │
│ - bind governing context to the request (Attach rules to Patron Slip)                                                                                                        │
│ [INVARIANT: downstream enforcement uses resolved authority only, never ad hoc rules (Library strictly follows the Charter)]                                                  │
│ [OUT: governed validation context (Stamped Reference Folder)]                                                                                                                │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    │
                                                              [ enters wing ]
                                                                    ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DUAL ENFORCEMENT RAILS (CO-LOCATED, LOGICALLY ISOLATED)                                                                                                                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                                                              │
│  ── STATIC LANE (PREVENTION | Floor Plan Blueprint + Dewey Decimal Classifier + Authorized Patron Registry) ───────────────────────────────────────────────────────────────  │
│   ┌──────────────────────────────┐          ┌──────────────────────────────┐          ┌──────────────────────────────┐                                                       │
│   │ STRUCTURE ENFORCEMENT        │[ maps to]│ CLASSIFICATION KERNEL        │[ tags to]│ REGISTRY VALIDATION          │                                                       │
│   │ (Floor Plan / Stack Map)     │───→→───→ │ (Dewey Decimal System)       │───→→───→ │ (Patron Identity Ledger)     │                                                       │
│   │ - path / territory / layers  │          │ - AST type classification    │          │ - agent must exist           │                                                       │
│   │ - depth + placement rules    │          │ - dual-tag conflict detect   │          │ - allowed_models enforced    │                                                       │
│   │ - cross-domain violations    │          │                              │          │ - execution_mode lock        │                                                       │
│   │                              │          │                              │          │ - registry_digest match      │                                                       │
│   │ [no structural drift]        │          │ [type SSOT]                  │          │ [identity + capability gate] │                                                       │
│   └──────────────┬───────────────┘          └──────────────┬───────────────┘          └──────────────┬───────────────┘                                                       │
│                  │                                         │                                         │                                                                       │
│                  └─────────────────────────────────────────┴─────────────────────────────────────────┘                                                                       │
│                                                                    │                                                                                                         │
│                                                              [ drops down ]                                                                                                  │
│                                                                    ▼                                                                                                         │
│                                                                                                                                                                              │
│  ── RUNTIME LANE (CONTAINMENT | Restricted Section Desk + Interlibrary Loan Exit) ────────────────────────────────────────────────────────────────────────────────────────   │
│                                      ┌──────────────────────────────────────────────┐                                                                                        │
│                                      │ POLICY VALIDATION CHOKEPOINT                 │                                                                                        │
│                                      │ (Restricted Access Desk)                     │                                                                                        │
│                                      │ - risk tiering                               │                                                                                        │
│                                      │ - validate tools / actions / plan            │                                                                                        │
│                                      │ - approve / reject / remediate               │                                                                                        │
│                                      │ [hard stop on violation]                     │                                                                                        │
│                                      └──────────────┬───────────────────────────────┘                                                                                        │
│                                                     │                                                                                                                        │
│                                               [ asks exit ]                                                                                                                  │
│                                                     ▼                                                                                                                        │
│                                      ┌──────────────────────────────────────────────┐                                                                                        │
│                                      │ LLM GATEWAY (SOVEREIGN EGRESS)               │                                                                                        │
│                                      │ (Interlibrary Loan Booth)                    │                                                                                        │
│                                      │ - symbolic → provider resolution             │                                                                                        │
│                                      │ - prompt injection detection                 │                                                                                        │
│                                      │ - audit log + replay envelope                │                                                                                        │
│                                      │ - fail-closed (no silent fallback)           │                                                                                        │
│                                      │ [only path to external models/archives]      │                                                                                        │
│                                      └──────────────┬───────────────────────────────┘                                                                                        │
│                                                     │                                                                                                                        │
│                                             [ submits review ]                                                                                                               │
│                                                     ▼                                                                                                                        │
│                                                                                                                                                                              │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DECISION RAIL (EXPLICIT, TERMINAL AUTHORITY | The Head Librarian's Desk)                                                                                                     │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│         ┌───────────────────────┬────────────────────────┬────────────────────────┐                                                                                          │
│         │ REJECT                │ REMEDIATE              │ CERTIFY                │                                                                                          │
│         │ (Revoke Card)         │ (Suggest Edits)        │ (Stamp of Approval)    │                                                                                          │
│         ├───────────────────────┼────────────────────────┼────────────────────────┤                                                                                          │
│         │ - stop execution      │ - sanitize / adjust    │ - attach compliance    │                                                                                          │
│         │ - return upstream     │ - re-enter L5          │ - bind capability_token│                                                                                          │
│         │                       │ - same policy refs     │ - bind sandbox_envelope│                                                                                          │
│         │                       │                        │ - emit audit record    │                                                                                          │
│         └───────────────┬───────┴───────────────┬────────┴───────────────┬────────┘                                                                                          │
│                         │                       │                        │                                                                                                   │
│                    [ tears up ]           [ hands back ]       [ stamps approved ]                                                                                           │
│                         ▼                       ▼                        ▼                                                                                                   │
│                 [ FAIL / RETURN ]        [ RE-VALIDATE LOOP ]      [ GOVERNED EXECUTION CONTINUES ]                                                                          │
│                                                                                                                                                                              │
│ [INVARIANT: every human modification, plan change, tool call, or LLM request must traverse this rail before gaining execution authority]                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    │
                                                              [ walks out ]
                                                                    ▼
========================================================================================================================================================================================
[ BELOW GOVERNANCE & SAFETY CONTEXT | certified outputs propagate to execution / exit / observability (Patron leaves with stamped books) ]
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
OUTPUTS = GovernanceResult | compliance_hash | audit_log | replay_envelope | capability_token | sandbox_envelope
INVARIANT = learning signals may inform future thresholds but cannot alter the current certified run
========================================================================================================================================================================================