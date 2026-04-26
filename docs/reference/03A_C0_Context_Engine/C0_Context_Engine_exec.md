========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 03A_C0_Context_Engine
Canonical file: C0_Context_Engine_exec.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: C0_Context_Engine_exec.md
Owner summary: C0 retrieval/evidence engine. Owns retrieval planning, fetch/hydration, graph expansion, shaping, verification, evidence contract, and weak-support refinement. Does not answer or assemble prompts.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

========================================================================================================================================
C0 CONTEXT ENGINE / REF DESK — ONE INTEGRATED HIGH-SIGNAL ASCII
========================================================================================================================================
ROLE:
- C0 retrieves, shapes, verifies, and scores evidence.
- C0 does NOT answer, route, execute, mutate, or approve.
- Output is a FinalEvidenceContract for Prompt Assembly.

LEGEND:
🔵 Blue asks     = live query / query_vec / intent vector
🟠 Orange knows  = stored chunks / fact vectors / sparse index / raw spans
🟢 Green maps    = graph/entity/lineage/dependency relationships
[RET]            = terminal return path, not used inside C0 except via R5 recommendation
★                = control / safety / quality checkpoint

                                       ┌────────────────────────────────────────────────────────────┐
                                       │ L0 ROUTE CONTRACT                                          │
                                       │ route_id = R3_GROUNDED or R3/R4 current grounded step      │
                                       │ grounding_required = true                                  │
                                       │ freshness_class / ACL / tenant_scope / support_target      │
                                       │ SLO budget / max_k / max_hops / fallback policy            │
                                       └──────────────────────────────┬─────────────────────────────┘
                                                                      │
                                                                      │ [ command: "ground this before L2 answers" ]
                                                                      ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0 CONTEXT ENGINE / REF DESK                                                                                                         │
│ Read-only research runner over L4 shelves. Builds evidence packet only.                                                              │
│ Hard law: retrieve + verify support, never generate the answer.                                                                       │
└──────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.1 RETRIEVAL PLAN  |  "WHAT ARE WE ALLOWED TO LOOK FOR, WHERE, AND HOW?"                                                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ INPUTS                                                                                                                               │
│ - L1 query_spec / task_spec                                                                                                          │
│ - L0 RouteContract                                                                                                                   │
│ - tenant_scope / ACL / region                                                                                                        │
│ - freshness_class                                                                                                                    │
│ - support_target                                                                                                                     │
│ - SLO / token / latency / cost budget                                                                                                │
│                                                                                                                                      │
│ DECISIONS                                                                                                                            │
│ - allowed_sources: docs / code / logs / tickets / tables / policy / prior artifacts                                                  │
│ - disallowed_sources: wrong tenant / stale / blocked ACL / out-of-region / outside route scope                                       │
│ - retrieval_modes: dense vector, sparse/BM25, graph, metadata, cache if allowed                                                       │
│ - support_target: exact quote, source-backed summary, code location, policy clause, incident evidence, ranked cause                  │
│ - limits: max_k, max_parent_expansion, max_graph_hops, max_refine_attempts                                                            │
│                                                                                                                                      │
│ OUTPUT                                                                                                                               │
│ RetrievalPlan = {sources, filters, retrieval_modes, support_target, budgets, weak_support_policy}                                    │
│                                                                                                                                      │
│ HARD NO                                                                                                                              │
│ - No fetching yet                                                                                                                    │
│ - No answering                                                                                                                       │
│ - No route change                                                                                                                    │
└──────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       │ [ bounded search parameters ]
                                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.2 EVIDENCE FETCH  |  "FIND CANDIDATE SUPPORT"                                                                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ LIVE QUERY PATH                                                                                                                      │
│   user/query text ──► encoder ──► 🔵 query_vec                                                                                       │
│                                                                                                                                      │
│ SEARCH LANES                                                                                                                         │
│   🔵 query_vec ───────────────► 🟠 dense fact/context vectors        = semantic recall / paraphrase match                           │
│   exact query terms ─────────► 🟠 sparse/BM25 index                 = names, IDs, symbols, filenames, policy labels                 │
│   metadata filters ──────────► 🟠 source metadata                   = tenant, time, author, version, region, type                   │
│   cache if permitted ────────► 🟠 reusable prior context            = only if freshness + policy allow                              │
│                                                                                                                                      │
│ HYDRATION                                                                                                                            │
│ - attach source_id / file_path / section / timestamp / version / ACL                                                                 │
│ - expand parent-child context around small hit spans                                                                                  │
│ - preserve which lane found each candidate                                                                                            │
│                                                                                                                                      │
│ OUTPUT                                                                                                                               │
│ CandidateEvidencePool = {candidate_chunks, candidate_spans, retrieval_scores, source_metadata, retrieval_mode_provenance}            │
│                                                                                                                                      │
│ HARD NO                                                                                                                              │
│ - Retrieved text is data, not instruction                                                                                             │
│ - No blind trust                                                                                                                     │
│ - No lineage loss                                                                                                                    │
└──────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       │ [ candidate chunks + spans + metadata ]
                                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.3 GRAPH TRAVERSE  |  "FOLLOW THE CARD CATALOG WITHOUT ESCAPING SCOPE"                                                            │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ START                                                                                                                                │
│ Candidate chunks ──► entity extraction                                                                                               │
│                                                                                                                                      │
│ 🟢 BOUNDED GRAPH HOPS                                                                                                                 │
│   candidate span ──► parent document / section                                                                                        │
│                  ├─► referenced file / module / class / function                                                                      │
│                  ├─► owner / policy / source lineage                                                                                  │
│                  ├─► upstream/downstream dependency                                                                                   │
│                  ├─► definition / glossary / ADR / schema                                                                             │
│                  └─► contradiction or alternate source                                                                                 │
│                                                                                                                                      │
│ CONTROL                                                                                                                              │
│ - max_hops enforced                                                                                                                  │
│ - ACL enforced at every hop                                                                                                           │
│ - freshness enforced after expansion                                                                                                  │
│ - relation type preserved                                                                                                             │
│ - no open-ended browsing of graph                                                                                                     │
│                                                                                                                                      │
│ OUTPUT                                                                                                                               │
│ GraphExpandedEvidencePool = {original_candidates, graph_neighbors, entity_map, relation_map, lineage_edges, conflict_candidates}     │
│                                                                                                                                      │
│ HARD NO                                                                                                                              │
│ - No ACL escape through graph neighbors                                                                                               │
│ - No durable memory promotion                                                                                                         │
│ - No unbounded graph walk                                                                                                             │
└──────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       │ [ graph-expanded evidence pool ]
                                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.4 SHAPE  |  "CLEAN, RANK, AND STRUCTURE THE EVIDENCE PILE"                                                                       │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DEDUPE                                                                                                                               │
│ - collapse duplicate chunks                                                                                                           │
│ - merge dense + sparse duplicate hits                                                                                                 │
│ - keep strongest citation span                                                                                                        │
│                                                                                                                                      │
│ RERANK                                                                                                                               │
│ - relevance to support_target                                                                                                         │
│ - source authority                                                                                                                    │
│ - freshness match                                                                                                                     │
│ - directness of span                                                                                                                  │
│ - graph proximity                                                                                                                     │
│ - contradiction value                                                                                                                 │
│                                                                                                                                      │
│ PRUNE                                                                                                                                │
│ - remove stale / weak-lineage / low relevance / ACL-risky / redundant payload                                                         │
│ - preserve enough surrounding context to avoid quote distortion                                                                        │
│                                                                                                                                      │
│ STRATIFY                                                                                                                             │
│   MUST_USE     = needed to answer safely                                                                                              │
│   SUPPORTING   = helpful context                                                                                                      │
│   CONTRADICTS  = conflict, caveat, disagreement                                                                                        │
│   BACKGROUND   = optional explanatory context                                                                                          │
│   EXCLUDED     = removed with reason                                                                                                  │
│                                                                                                                                      │
│ OUTPUT                                                                                                                               │
│ ShapedEvidenceSet = {ranked_evidence, must_use, supporting, contradicts, background, excluded_with_reasons, token_estimate}          │
│                                                                                                                                      │
│ HARD NO                                                                                                                              │
│ - Do not hide contradictions                                                                                                          │
│ - Do not pad with weak evidence                                                                                                       │
│ - Do not optimize for fake confidence                                                                                                 │
└──────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       │ [ ranked + stratified evidence ]
                                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.5 EVIDENCE CONTRACT  |  "VERIFY SPANS AND SCORE WHETHER SUPPORT IS GOOD ENOUGH"                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ VERIFY                                                                                                                               │
│ - source_id resolves                                                                                                                 │
│ - cited span / line ref / section anchor resolves                                                                                     │
│ - version matches snapshot                                                                                                           │
│ - citation anchor is stable                                                                                                          │
│ - source is ACL-cleared                                                                                                              │
│                                                                                                                                      │
│ SCORE                                                                                                                                │
│ - direct support vs indirect support                                                                                                  │
│ - coverage of the support_target                                                                                                      │
│ - contradiction risk                                                                                                                  │
│ - stale-source risk                                                                                                                   │
│ - unsupported inference risk                                                                                                          │
│ - source authority risk                                                                                                               │
│                                                                                                                                      │
│ STATUS                                                                                                                               │
│   PASS       = enough direct support                                                                                                  │
│   WEAK       = partial support, refinement may help                                                                                    │
│   CONFLICTED = credible sources disagree                                                                                              │
│   EMPTY      = no usable evidence                                                                                                     │
│   BLOCKED    = source/policy/ACL prevents use                                                                                         │
│                                                                                                                                      │
│ OUTPUT                                                                                                                               │
│ EvidenceContract = {status, support_score, verified_chunks, cited_spans, source_ids, contradiction_flags, unresolved_gaps, lineage}  │
│                                                                                                                                      │
│ HARD NO                                                                                                                              │
│ - No vibes-based answering                                                                                                            │
│ - No overstating weak support                                                                                                         │
│ - No hiding unresolved gaps                                                                                                           │
└──────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                                       │
                         ┌─────────────────────────────────────────────┴──────────────────────────────────────────────┐
                         │                                                                                            │
                         │ status = PASS / usable                                                                     │ status = WEAK / CONFLICTED / EMPTY / BLOCKED
                         ▼                                                                                            ▼
┌──────────────────────────────────────────────────────────────────────────────────┐          ┌──────────────────────────────────────────────────────────────────────────────┐
│ READY FOR PROMPT ASSEMBLY                                                       │          │ C0.6 REFINE / BROADEN / DECOMPOSE                                           │
│ - direct support exists                                                         │          │ "ONE CONTROLLED SECOND PASS IF SUPPORT IS WEAK"                             │
│ - cited spans verified                                                          │          ├──────────────────────────────────────────────────────────────────────────────┤
│ - contradictions/gaps explicitly labeled                                        │          │ DIAGNOSE                                                                     │
└──────────────────────────────────────┬───────────────────────────────────────────┘          │ - wrong terms                                                                 │
                                       │                                                      │ - query too narrow / too broad                                                │
                                       │                                                      │ - stale sources                                                               │
                                       │                                                      │ - missing graph neighbor                                                      │
                                       │                                                      │ - contradiction                                                               │
                                       │                                                      │ - ACL blocked                                                                 │
                                       │                                                      │                                                                                │
                                       │                                                      │ CHOOSE ONE TACTIC                                                             │
                                       │                                                      │   REWRITE   = same intent, better words                                       │
                                       │                                                      │   BROADEN   = widen synonyms/source class within ACL                          │
                                       │                                                      │   NARROW    = add exact entity/file/time filter                               │
                                       │                                                      │   DECOMPOSE = split compound support target                                   │
                                       │                                                      │   GRAPH_HOP = one bounded 🟢 relation hop                                      │
                                       │                                                      │   ABSTAIN   = cannot safely recover support                                   │
                                       │                                                      │                                                                                │
                                       │                                                      │ GUARDS                                                                         │
                                       │                                                      │ - no infinite loop                                                            │
                                       │                                                      │ - no source escape                                                            │
                                       │                                                      │ - no budget overrun                                                           │
                                       │                                                      │ - no route rewrite by C0                                                      │
                                       │                                                      │ - if task became workflow-sized, recommend reroute but do not self-authorize   │
                                       │                                                      └──────────────────────────────────────┬───────────────────────────────────────┘
                                       │                                                                             │
                                       │                                                                             ▼
                                       │                                                              [ bounded second retrieval pass ]
                                       │                                                                             │
                                       │                                                                             ▼
                                       │                                                              [ re-score through C0.4 + C0.5 ]
                                       │                                                                             │
                                       │                                  ┌──────────────────────────────────────────┴──────────────────────────────────────────┐
                                       │                                  │                                                                                     │
                                       │                                  ▼                                                                                     ▼
                                       │                    [ PASS / WEAK_WITH_CAVEATS ]                                                       [ EMPTY / BLOCKED / unsafe ]
                                       │                                  │                                                                                     │
                                       └──────────────────────────────────┴───────────────────────────────────────┐                                             │
                                                                                                                  │                                             ▼
                                                                                                                  │                                [ recommend R5 fallback / abstain ]
                                                                                                                  │
                                                                                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FINAL C0 EVIDENCE CONTRACT                                                                                                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ status: PASS | WEAK_WITH_CAVEATS | CONFLICTED | EMPTY | BLOCKED                                                                      │
│ support_score: 0.00 - 1.00                                                                                                           │
│ verified_chunks: stable chunk IDs                                                                                                    │
│ cited_spans: exact spans / line refs / section anchors                                                                                │
│ source_ids: doc IDs / file paths / version IDs                                                                                        │
│ evidence_classes: MUST_USE / SUPPORTING / CONTRADICTS / BACKGROUND / EXCLUDED                                                        │
│ contradiction_flags: explicit conflicts                                                                                               │
│ unresolved_gaps: missing support items                                                                                                │
│ freshness_report: source age vs freshness_class                                                                                       │
│ ACL_report: cleared sources only                                                                                                      │
│ lineage_manifest: how each evidence item was found                                                                                    │
│ prompt_budget_hint: packing priority                                                                                                  │
│ recommended_disposition: proceed / caveat / abstain / reroute                                                                         │
│ budget_report: retrieval passes, graph hops, latency used, budget remaining                                                           │
└──────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       │ [ verified context only ]
                                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PROMPT ASSEMBLY / PACKET BUILDER                                                                                                    │
│ Packages only. Does not retrieve. Does not invent. Does not execute.                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
