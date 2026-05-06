====================================================================================================
                         C0 CONTEXT ENGINE EXEC FLOWCHART
                zero-loss overwrite with 🔵 🟠 🟢 signal placement only
====================================================================================================

SIGNAL LEGEND
-------------
🔵 Blue  = live query / query_vec / intent vector / step-specific ask
🟠 Orange = stored chunks / fact vectors / sparse terms / metadata / source spans
🟢 Green = graph_sig / lineage / dependency / ACL / citation / relationship edges


                         ┌──────────────────────────────────────────────┐
                         │ L0 ROUTECONTRACT                             │
                         │ route says: grounding_required = true         │
                         │ bounds: source scope, freshness, budget, ACL  │
                         │                                              │
                         │ Carries support target and scope, not vectors │
                         └───────────────────────┬──────────────────────┘
                                                 │
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.0 PREFLIGHT                                                                                   │
│ "Is C0 allowed to run?"                                                                          │
│                                                                                                  │
│ Checks: route grants grounding | support target | ACL/source scope | origin trust | budget        │
│                                                                                                  │
│ Signal posture:                                                                                  │
│ 🔵 reads live ask / support target / query intent                                                 │
│ 🟠 checks allowed source classes, snapshots, freshness, ACL                                       │
│ 🟢 checks whether graph traversal is permitted under route bounds                                 │
│                                                                                                  │
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
│ 🔵 dense query_vec / intent vector            │                    │                                  │
│ 🟠 sparse/BM25 | metadata | cache             │                    │ Signal posture:                  │
│ 🟠 code | trace | table | ticket              │                    │ 🔵 request could not be grounded │
│ 🟢 graph_seed                                 │                    │ 🟠 usable sources blocked/missing│
│                                              │                    │ 🟢 graph may be disallowed       │
│ Output: RetrievalPlan                        │                    └──────────────────────────────────┘
└───────────────────────┬──────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.2 EVIDENCE FETCH                                                                              │
│ "What candidates can we retrieve, and what proves origin?"                                       │
│                                                                                                  │
│ Executes only planned lanes.                                                                     │
│                                                                                                  │
│ Retrieval mechanics:                                                                             │
│ 🔵 live query_vec searches against dense index                                                    │
│ 🟠 fact vectors return nearest-neighbor candidates                                                │
│ 🟠 sparse/BM25 returns lexical/exact-match candidates                                             │
│ 🟠 metadata filters by tenant, source, version, freshness, ACL, author, time                      │
│ 🟢 graph_seed IDs are collected only if graph is enabled                                          │
│                                                                                                  │
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
│ Expands bounded graph context:               │                │                                  │
│ 🟢 lineage | owners | dependencies            │                │ Signal posture:                  │
│ 🟢 contradictions | supersession | stale signs │                │ 🔵 query intent already planned  │
│ 🟢 rejected neighbors with reasons            │                │ 🟠 candidates remain available   │
│                                              │                │ 🟢 graph expansion not applied   │
│ Uses:                                        │                └─────────────────┬────────────────┘
│ 🔵 support target to constrain expansion      │                                  │
│ 🟠 source nodes / chunk nodes / span refs      │                                  │
│ 🟢 relationship edges                         │                                  │
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
│ Ranking signals:                                                                                 │
│ 🔵 relevance to live intent / support target                                                      │
│ 🟠 dense score against fact vectors                                                               │
│ 🟠 BM25 / sparse exactness                                                                        │
│ 🟠 metadata fit, freshness, source authority, citation stability                                  │
│ 🟢 graph proximity, lineage strength, dependency relation, contradiction relation                 │
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
│ Verification signals:                                                                            │
│ 🔵 claims/support target are matched against evidence need                                        │
│ 🟠 cited spans, fact vectors, sparse hits, metadata, source snapshots                             │
│ 🟢 lineage, dependency, contradiction, supersession, ACL graph relationships                      │
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
│ 🟠 must_use | supporting | contradictions     │                │ Allowed strategies:                          │
│ 🟠 background | gaps | packability            │                │ 🔵 query rewrite                             │
│ 🟢 lineage | dependency refs                  │                │ 🔵 decompose evidence need                   │
│                                              │                │ 🟠 broaden sparse / metadata / source search │
│ C0 still does not assemble the prompt         │                │ 🟢 expand bounded graph_seed if permitted    │
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
                          │ 🔵 C0.1 for new plan                     │                     │ conflicted / blocked status │
                          │ 🟠 C0.4 for reshape only                 │                     │                             │
                          │ 🟠🟢 C0.5 for verification only          │                     │ no answer                   │
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
    🔵 live query / support target preserved
    🟠 source lineage preserved
    🟠 freshness checked
    🟠 ACL checked
    🟢 graph expansion bounded
    🟢 contradictions surfaced
    weak stays weak
    retrieved text stayed data
    exactly one FinalEvidenceContract
    no answer, no route change, no prompt assembly, no execution, no L4 write


====================================================================================================
                         ONE-LINE ARROW
====================================================================================================

  Route grants grounding
      -> C0.0 preflight checks 🔵 ask against 🟠 source scope and 🟢 graph permission
      -> C0.1 plans 🔵 dense query, 🟠 sparse/metadata/cache lanes, 🟢 graph_seed
      -> C0.2 fetches 🔵 query_vec against 🟠 fact vectors / sparse / metadata
      -> C0.3 expands 🟢 graph relationships if enabled
      -> C0.4 shapes using 🔵 relevance + 🟠 evidence quality + 🟢 lineage / contradiction signals
      -> C0.5 verifies 🟠 spans and 🟢 lineage against 🔵 support target
      -> C0.6 refines only if weak and authorized
      -> Prompt Assembly packs verified 🟠 evidence refs and 🟢 lineage refs