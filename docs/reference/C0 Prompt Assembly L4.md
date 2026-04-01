=========================================================================================================================================================
                            [ TRIPLE-CLICK: C0 CONTEXT ENGINE ➔ PROMPT ASSEMBLY ➔ L4 RUNTIME INTERACTION ]
=========================================================================================================================================================
[ INVARIANTS ]
- C0 retrieves; Prompt Assembly packages      - Prompt Assembly does not invent facts       - L4 supplies templates / refs only
- Prompt Assembly does not retrieve           - C0 does not invent policy                   - Insufficient support -> refine, clarify, or abstain
=========================================================================================================================================================

                                [ L1 SYNTHESIS / MODEL CALL | Senior Librarian ]
                                        ▲                                ▲                           ▲
                 ┌──────────────────────┴────────────────────────────────┼───────────────────────────┼──────────────────────┐
                 │ Contract: L1Plan                                      │ Contract: PromptEnvelope  │ Contract:            │
                 │ - proposed_route                                      │ - system/policy/ctx blocks│ PromptAssemblyStatus │
                 │ - query_spec ─────────┐           ┌───────── task_spec│ - task_block/schema       │ - insufficient_evid  │
                 │ - task_spec ──────────│───────────│────────┐          │ - citations_required      │ - unresolved_gaps    │
                 └───────────────────────│───────────│────────│──────────│ - prompt_hash / manifest  │ - next_action        │
                                         ▼           ▼        │          └───────────────────────────┴──────────────────────┘
=========================================│===========│========│==========================================================================================
 [ C0 CONTEXT ENGINE | Reference Desk ]  │           │        │         [ PROMPT ASSEMBLY | Reading Packet Builder ]
=========================================│===========│========│==========================================================================================
  ┌────────────────────────┐             │           │        │          ┌────────────────────────────────┐
  │ C0.1 RETRIEVAL PLAN    │<────────────┘           │        │          │ PA.1 LOAD STATIC BLOCKS        │<────────────────────────┐
  │ - source scope         │<─────┐                  │        │          │ - system template              │                         │
  │ - freshness window     │      │                  │        │          │ - policy refs                  │                         │
  │ - access/sec filters   │      │                  │        │          │ - output schema                │                         │
  │ - retrieval mode       │      │                  │        │          │ - persona / mode               │                         │
  └──────────┬─────────────┘      │                  │        │          └──────────┬─────────────────────┘                         │
             ▼                    │                  │        │                     ▼                                       │
  ┌────────────────────────┐      │                  │        │          ┌──────────▼─────────────────────┐                         │
  │ C0.2 EVIDENCE FETCH    │<─────┤                  │        └─────────>│ PA.2 SLOT CONTEXT+TASK         │<──┐                     │
  │ - vector retrieval over│      │                  │             ┌────>│ - must-use evidence            │   │                     │
  │   fact_vec index       │      │                  │             │     │ - optional evidence            │   │                     │
  │ - lexical retrieval    │      │                  │             │     │ - citation anchors             │   │                     │
  │ - optional cache reuse │      │                  │             │     │ - contradiction flags          │   │                     │
  │ - metadata hydration   │      │                  │             │     └──────────┬─────────────────────┘   │                     │
  └──────────┬─────────────┘      │                  │             │                ▼                 │     │                     │
             ▼                 (Loop 1: ContextRefineRequest)      │     ┌──────────▼─────────────────────┐   │                     │
  ┌────────────────────────┐ <─────────────────────────────────────┼─────│ PA.3 TOKEN BUDGETER            │   │                     │
  │ C0.3 EVIDENCE SHAPING  │  - max_tokens                         │     │ - trim/stratify if needed      │   │                     │
  │ - dedupe               │  - preserve_citations / sources       │     │ - request refine if over budget│   │                     │
  │ - parent/child expand  │  - prioritize_must_use                │     │ - preserve provenance          │   │                     │
  │ - freshness filter     │                                       │     │ - preserve inst. order         │   │                     │
  │ - provenance retention │                                       │     └──────────┬─────────────────────┘   │                     │
  └──────────┬─────────────┘                                       │                ▼                 │     │                     │
             ▼                 ┌───────────────────────────────┐   │     ┌──────────▼─────────────────────┐   │                     │
  ┌────────────────────────┐   │ Contract: EvidenceBundle      │   │     │ PA.4 PROMPT CONTRACT           │   │                     │
  │ C0.4 EVIDENCE CONTRACT │──>│ - verified_chunks, cited_spans│───┘     │ - emit PromptEnvelope  ────────│───│─> (Up to L1 Call)   │
  │ - support scoring      │   │ - source_ids / dates          │         │ - emit Status  ────────────────│───│─> (Up to L1 Loop)   │
  │ - emit EvidenceBundle  │   │ - coverage_score, gaps        │         └────────────────────────────────┘   │                     │
  └──────────▲─────────────┘   │ - support_status, next_action │                                              │                     │
             │                 └───────────────────────────────┘                                              │                     │
             │                                                                                                │                     │
             │ [reads to C0.1 / C0.2]                                                                         │ [reads to PA.1]     │
             │                                                                                                │                     │
             └─────────────────────────────────────────────────────┐                                          │                     │
                                                                   │                                          │                     │
                                                     ==============┴================┴=========================┴=====================┴
                                                     [ L4 | Archive + Rules Shelf ] ── (Read-Only)
                                                     ========================================================================
                                                     (To C0)                     (To Prompt Assembly)
                                                     - Approved knowledge        - System template & refs
                                                       indices (offline          - PA template version
                                                       pre-indexed fact_vec)     - Output schema / reqs
                                                     - Metadata / registry       - Persona / mode settings
                                                     - Access/Fresh filters