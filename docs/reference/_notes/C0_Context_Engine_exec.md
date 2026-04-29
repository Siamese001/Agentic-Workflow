====================================================================================================
                         C0 CONTEXT ENGINE EXEC FLOWCHART
====================================================================================================

                         ┌──────────────────────────────────────────────┐
                         │ L0 ROUTECONTRACT                             │
                         │ route says: grounding_required = true         │
                         │ bounds: source scope, freshness, budget, ACL  │
                         └───────────────────────┬──────────────────────┘
                                                 │
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.0 PREFLIGHT                                                                                   │
│ "Is C0 allowed to run?"                                                                          │
│                                                                                                  │
│ Checks: route grants grounding | support target | ACL/source scope | origin trust | budget        │
│ Output: C0PreflightStatus                                                                        │
└───────────────────────┬──────────────────────────────────────────────────────────────┬───────────┘
                        │                                                              │
                        │ eligible                                                     │ blocked
                        ▼                                                              ▼
┌──────────────────────────────────────────────┐                    ┌──────────────────────────────────┐
│ C0.1 RETRIEVAL PLAN                          │                    │ STOP AS EVIDENCE GAP             │
│ "What should we search, where, and how?"     │                    │ no route change                  │
│                                              │                    │ no answer                        │
│ Plans lanes:                                 │                    │ no runtime disposition           │
│ dense | sparse/BM25 | metadata | cache       │                    └──────────────────────────────────┘
│ code | trace | table | ticket | graph_seed   │
│                                              │
│ Output: RetrievalPlan                        │
└───────────────────────┬──────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.2 EVIDENCE FETCH                                                                              │
│ "What candidates can we retrieve, and what proves origin?"                                       │
│                                                                                                  │
│ Executes only planned lanes.                                                                     │
│ Hydrates: source_id | version | snapshot | ACL | span | lineage | origin label | citation risk    │
│                                                                                                  │
│ Output: CandidateEvidencePool                                                                    │
│ Key rule: candidates are not trusted yet                                                         │
└───────────────────────┬──────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────────── graph enabled? ───────────────────────┐
              │                                                               │
              │ yes                                                           │ no
              ▼                                                               ▼
┌──────────────────────────────────────────────┐                ┌──────────────────────────────────┐
│ C0.3 GRAPH RAG                               │                │ SKIP GRAPH                       │
│ "What relationships matter?"                 │                │ CandidateEvidencePool goes       │
│                                              │                │ directly to C0.4                 │
│ Expands bounded graph context:               │                └─────────────────┬────────────────┘
│ lineage | owners | dependencies              │                                  │
│ contradictions | supersession | stale signs  │                                  │
│ rejected neighbors with reasons              │                                  │
│                                              │                                  │
│ Output: GraphExpandedEvidencePool            │                                  │
│ Key rule: GraphDB adapter, not SQLite walk   │                                  │
└───────────────────────┬──────────────────────┘                                  │
                        │                                                         │
                        └──────────────────────────────┬──────────────────────────┘
                                                       │
                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.4 SHAPE / RERANK / STRATIFY                                                                   │
│ "What should be must-use, supporting, contradiction, background, or excluded?"                    │
│                                                                                                  │
│ Does: dedupe | merge provenance | rerank | preserve contradictions | trim to token budget         │
│                                                                                                  │
│ Strata:                                                                                          │
│ MUST_USE | SUPPORTING | CONTRADICTS | BACKGROUND | EXCLUDED                                      │
│                                                                                                  │
│ Output: ShapedEvidenceSet                                                                        │
│ Key rule: contradictions are signal, not noise                                                   │
└───────────────────────┬──────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.5 FINAL EVIDENCE CONTRACT                                                                     │
│ "Is evidence strong enough, and what may Prompt Assembly pack?"                                  │
│                                                                                                  │
│ Verifies: citations | freshness | authority | ACL | contradiction status | source parity          │
│                                                                                                  │
│ Emits exactly one FinalEvidenceContract                                                          │
│ Status: PASS | WEAK_WITH_CAVEATS | CONFLICTED | EMPTY | BLOCKED                                  │
└───────────────┬──────────────────────────────────────────────────────────────┬───────────────────┘
                │                                                              │
                │ PASS or acceptable caveated support                           │ weak / empty / conflicted / blocked
                ▼                                                              ▼
┌──────────────────────────────────────────────┐                ┌──────────────────────────────────────────────┐
│ HANDOFF TO PROMPT ASSEMBLY                   │                │ C0.6 WEAK SUPPORT REFINEMENT                 │
│                                              │                │ "Can support improve inside same authority?" │
│ PA receives verified refs only:              │                │                                              │
│ must_use | supporting | contradictions       │                │ Allowed strategies:                          │
│ background | gaps | lineage | packability    │                │ query rewrite                                │
│                                              │                │ broaden within scope                         │
│ C0 still does not assemble the prompt         │                │ decompose evidence need                      │
└──────────────────────────────────────────────┘                │ stop with gap report                         │
                                                                └───────────────┬──────────────────────────────┘
                                                                                │
                                             ┌──────────────────────────────────┴──────────────────────────────┐
                                             │                                                                 │
                                             │ safe refinement available                                        │ no safe refinement
                                             ▼                                                                 ▼
                          ┌──────────────────────────────────────────┐                     ┌─────────────────────────────┐
                          │ RE-ENTER OWNED C0 STAGE ONLY             │                     │ FINAL GAP REPORT            │
                          │                                          │                     │ keep weak / empty /         │
                          │ C0.1 for new plan                        │                     │ conflicted / blocked status │
                          │ C0.4 for reshape only                    │                     │                             │
                          │ C0.5 for verification only               │                     │ no answer                   │
                          │                                          │                     │ no reroute authority        │
                          │ bounded by max_refine_attempts           │                     │ no runtime disposition      │
                          └─────────────────────┬────────────────────┘                     └─────────────────────────────┘
                                                │
                                                └────────────── back through C0 path only


====================================================================================================
                         CONTROL AND PROOF SPINE
====================================================================================================

  Runtime Gates around C0:
    G08 Retrieval/Grounding
    G09 Evidence Quality
    G13 Retrieved Content Trust
    G17 Privacy/Cross-context
    G23 Security/Leakage
    G24 Replay where required

  C0-wide proof:
    c0.stage
      -> c0.0.preflight
      -> c0.1.retrieval_plan
      -> c0.2.evidence_fetch
      -> c0.3.graph_traverse when enabled
      -> c0.4.shape_rerank_stratify
      -> c0.5.evidence_contract
      -> c0.6.refinement when invoked

  Must prove:
    source lineage preserved
    freshness checked
    ACL checked
    contradictions surfaced
    weak stays weak
    retrieved text stayed data
    exactly one FinalEvidenceContract
    no answer, no route change, no prompt assembly, no execution, no L4 write


====================================================================================================
                         ONE-LINE ARROW
====================================================================================================

  Route grants grounding
      -> C0.0 preflight
      -> C0.1 plan lanes
      -> C0.2 fetch candidates
      -> C0.3 expand graph if enabled
      -> C0.4 shape evidence
      -> C0.5 verify and contract
      -> C0.6 refine only if weak and authorized
      -> Prompt Assembly packs verified refs