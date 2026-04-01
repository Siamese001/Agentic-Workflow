=========================================================================================================================
               [ TRIPLE-CLICK: C0 CONTEXT ENGINE ➔ PROMPT ASSEMBLY ➔ L4 RUNTIME INTERACTION ]
=========================================================================================================================
[ INVARIANTS ]
- C0 retrieves; Prompt Assembly packages      - Prompt Assembly does not invent facts
- Prompt Assembly does not retrieve           - C0 does not invent policy
- Insufficient support -> refine, clarify, or abstain
=========================================================================================================================

                                [ L1 REASONING LOOP / L1 COGNITIVE STUDIO ]
                                        ▲                                ▲                           ▲
                 ┌──────────────────────┴────────────────────────────────┼───────────────────────────┼──────────────────────┐
                 │ Contract: L1Plan                                      │ Contract: PromptEnvelope  │ Contract:            │
                 │ - proposed_route                                      │ - system/policy/ctx blocks│ PromptAssemblyStatus │
                 │ - query_spec ─────────┐           ┌───────── task_spec│ - task_block/schema       │ - insufficient_evid  │
                 │ - task_spec ──────────│───────────│────────┐          │ - citations_required      │ - unresolved_gaps    │
                 └───────────────────────│───────────│────────│──────────└───────────────────────────┴──────────────────────┘
                                         │           │        │
                     [ L0 Ingress: L1Plan + query_vec ]       │
                                         │           │        │
=========================================│===========│========│==========================================================
 [ C0 CONTEXT ENGINE | Reference Desk ]  ▼           │        │         [ PROMPT ASSEMBLY | Reading Packet Builder ]
=====================================================│========│==========================================================
  ┌────────────────────────┐                         │        │          ┌────────────────────────────────┐
  │ C0.1 RETRIEVAL PLAN    │<────────────────────────┘        │          │ PA.1 LOAD STATIC BLOCKS        │<──────┐
  │ - source scope         │<─────┐                           │          │ - system template              │       │
  │ - freshness window     │      │                           │          │ - policy refs                  │       │
  │ - access/sec filters   │      │                           │          │ - output schema                │       │
  │ - retrieval mode       │      │                           │          │ - persona / mode               │       │
  └──────────┬─────────────┘      │                           │          └──────────┬─────────────────────┘       │
             ▼                    │                           │                     ▼                         │
  ┌────────────────────────┐      │                           │          ┌────────────────────────────────┐       │
  │ C0.2 EVIDENCE FETCH    │<─────┤                           └─────────>│ PA.2 SLOT CONTEXT+TASK         │<──┐   │
  │ - fact_vec retrieval   │      │                                ┌────>│ - must-use evidence            │   │   │
  │ - lexical retrieval    │      │                                │     │ - optional evidence            │   │   │
  │ - cache reuse          │      │                                │     │ - citation anchors             │   │   │
  │ - metadata hydration   │      │                                │     │ - contradiction flags          │   │   │
  └──────────┬─────────────┘      │                                │     └──────────┬─────────────────────┘   │   │
             ▼                 (Loop 1: ContextRefineRequest)      │                ▼                         │   │
  ┌────────────────────────┐ <─────────────────────────────────────┼─────┌────────────────────────────────┐   │   │
  │ C0.3 EVIDENCE SHAPING  │  - max_tokens                         │     │ PA.3 TOKEN BUDGETER            │   │   │
  │ - dedupe               │  - preserve_citations                 │     │ - trim/stratify if needed      │   │   │
  │ - parent/child expand  │  - prioritize_must_use                │     │ - request refine if over limit │   │   │
  │ - provenance retention │                                       │     │ - preserve inst. order         │   │   │
  └──────────┬─────────────┘                                       │     └──────────┬─────────────────────┘   │   │
             ▼                 ┌───────────────────────────────┐   │                ▼                         │   │
  ┌────────────────────────┐   │ Contract: C0EvidenceBundle    │   │     ┌────────────────────────────────┐   │   │
  │ C0.4 EVIDENCE CONTRACT │──>│ - verified_chunks, cited_spans│───┘     │ PA.4 PROMPT CONTRACT           │   │   │
  │ - support scoring      │   │ - source_ids / dates          │         │ - emit PromptEnvelope  ────────│───┴───┘
  │ - emit C0EvidenceBundle│   │ - coverage_score / gaps       │         │ - emit PromptAssemblyStatus    │
  └──────────▲─────────────┘   │ - recommended_next_action     │         └────────────────────────────────┘
             │                 └───────────────────────────────┘
             │
             │ [reads to C0.1 / C0.2]                                          [reads to PA.1]
             │                                                                        │
             └───────────────────────────────────────┐                                │
                                                     │                                │
                                     ================▼================================▼=================
                                     [ L4 STATE / Archivist ] ── (Read-Only)
                                     ===================================================================
                                     (To C0)                          (To Prompt Assembly)
                                     - Approved knowledge indices     - System template & refs
                                     - Metadata / registry            - Output schema / reqs
                                     - Access/Freshness filters       - Persona / mode settings