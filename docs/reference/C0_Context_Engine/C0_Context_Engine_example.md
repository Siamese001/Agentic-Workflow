========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: C0_Context_Engine
Canonical file: C0_Context_Engine_example.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: C0_Context_Engine_example.md
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

========================================================================================================================
C0 CONTEXT ENGINE / REF DESK
Example query: "Find the exact termination language in Contract X, Clause 17B."
========================================================================================================================

[ FROM L0 ROUTE CONTRACT ]
- route_id: R3_SIMPLE_GROUNDED_READ
- grounding_required: true
- support_target: exact quote / clause language
- allowed_sources: legal_contract_repository
- retrieval_modes allowed: dense + sparse/BM25 + metadata + graph
- max_k: 3
- max_graph_hops: 1
- max_refine_attempts: 1

        │
        │  JUSTIFICATION:
        │  L0 decided this cannot be answered from memory or cache.
        │  It needs grounded source evidence before L2 can answer.
        ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.1 RETRIEVAL PLAN                                                                                               │
│ "What are we allowed to look for, where, and how?"                                                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DOES                                                                                                               │
│ - Converts L1/L0 intent into a bounded search plan.                                                               │
│ - Decides source lanes: dense, sparse/BM25, metadata, graph.                                                      │
│ - Sets filters: Contract X, latest effective version, tenant/ACL, legal repository.                               │
│ - Marks exact terms: "Contract X", "Clause 17B", "termination".                                                  │
│ - Sets limits: top_k, max_hops, max_refine_attempts, token budget.                                                 │
│                                                                                                                    │
│ DOES NOT                                                                                                           │
│ - Does not fetch.                                                                                                  │
│ - Does not rank evidence.                                                                                          │
│ - Does not answer.                                                                                                 │
│                                                                                                                    │
│ OUTPUT                                                                                                             │
│ RetrievalPlan = {                                                                                                  │
│   query_text: "Contract X Clause 17B termination language",                                                        │
│   retrieval_modes: [dense_vector, sparse_BM25, metadata_filter, graph_traverse],                                   │
│   required_exact_terms: ["Contract X", "17B"],                                                                     │
│   filters: {doc_name: "Contract X", version: "latest_effective", acl: "legal_contracts:read"},                   │
│   support_target: "exact_quote_with_clause_anchor",                                                               │
│   limits: {dense_top_k: 3, sparse_top_k: 3, max_graph_hops: 1, max_refine_attempts: 1}                              │
│ }                                                                                                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        │  JUSTIFICATION:
        │  "17B" is an exact identifier. Dense semantic retrieval alone is unsafe because it may find
        │  termination-like language but miss the exact clause.
        ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.2 EVIDENCE FETCH                                                                                                │
│ "Find candidate support without trusting it yet."                                                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DOES                                                                                                               │
│                                                                                                                    │
│  1) Dense lane                                                                                                     │
│     query text -> encoder model -> 🔵 query_vec                                                                    │
│     🔵 query_vec searches 🟠 stored dense chunk vectors                                                             │
│                                                                                                                    │
│  2) Sparse lane                                                                                                    │
│     exact terms "Contract X" and "17B" search 🟠 BM25 / lexical index                                             │
│                                                                                                                    │
│  3) Metadata lane                                                                                                  │
│     filters by document name, version, ACL, tenant, source type, date                                              │
│                                                                                                                    │
│  4) Hydration                                                                                                      │
│     turns vector/sparse hits into full candidate records:                                                          │
│     chunk_id + text + source_id + section + version + metadata + retrieval score + lane provenance                 │
│                                                                                                                    │
│ DOES NOT                                                                                                           │
│ - Does not decide final truth.                                                                                     │
│ - Does not do graph traversal yet.                                                                                 │
│ - Does not perform final rerank/prune.                                                                             │
│ - Does not answer.                                                                                                 │
│                                                                                                                    │
│ DENSE OUTPUT EXAMPLE                                                                                               │
│ dense_results = [                                                                                                  │
│   {chunk_id: "cx_044", score: 0.84, section: "Clause 16",                                                         │
│    text: "Either party may terminate this Agreement upon thirty days written notice..."},                          │
│                                                                                                                    │
│   {chunk_id: "cx_051", score: 0.81, section: "Clause 17A",                                                        │
│    text: "Termination for material breach requires written notice and a ten business day cure period..."},         │
│                                                                                                                    │
│   {chunk_id: "cx_072", score: 0.78, section: "Clause 20",                                                         │
│    text: "Upon termination, each party must return confidential materials within five business days..."}           │
│ ]                                                                                                                  │
│                                                                                                                    │
│ SPARSE / BM25 OUTPUT EXAMPLE                                                                                       │
│ sparse_results = [                                                                                                 │
│   {chunk_id: "cx_052", bm25_score: 19.7, section: "Clause 17B",                                                   │
│    matched_terms: ["Contract X", "17B"],                                                                          │
│    text: "Clause 17B - Immediate Termination. Company may terminate this Agreement immediately upon Vendor's       │
│           unauthorized disclosure of Confidential Information."},                                                  │
│                                                                                                                    │
│   {chunk_id: "amend_008", bm25_score: 15.2, section: "Amendment to Clause 17B",                                  │
│    matched_terms: ["17B"],                                                                                         │
│    text: "Amendment 2 modifies Clause 17B by replacing 'immediately' with 'upon written notice' for regulated     │
│           data incidents."}                                                                                        │
│ ]                                                                                                                  │
│                                                                                                                    │
│ OUTPUT                                                                                                             │
│ CandidateEvidencePool = {                                                                                          │
│   candidate_chunks: ["cx_044", "cx_051", "cx_072", "cx_052", "amend_008"],                                    │
│   source_metadata: {source_id, doc_name, section, version, ACL, timestamp},                                        │
│   retrieval_scores: {dense_scores, sparse_scores},                                                                 │
│   retrieval_mode_provenance: {dense_vector | sparse_BM25 | metadata_filter},                                      │
│   hydrated_text_spans: original source chunks attached to each hit                                                 │
│ }                                                                                                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        │  JUSTIFICATION:
        │  Dense finds meaning-near chunks.
        │  Sparse finds exact identifiers.
        │  Metadata prevents wrong-version or wrong-tenant evidence from entering.
        │
        │  Critical point:
        │  C0.2 does not output "just vectors."
        │  It outputs candidate chunk records whose vectors point back to original text and metadata.
        ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.3 GRAPH TRAVERSE                                                                                                │
│ "Follow connected evidence without escaping scope."                                                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DOES                                                                                                               │
│ - Starts from candidate chunks.                                                                                    │
│ - Extracts entities: Contract X, Clause 17B, Amendment 2, Confidential Information.                                │
│ - Follows bounded graph relationships.                                                                             │
│ - Finds parent document, amendments, definitions, related clauses, contradictions, lineage.                         │
│                                                                                                                    │
│ DOES NOT                                                                                                           │
│ - Does not redo vector similarity.                                                                                 │
│ - Does not perform final answer synthesis.                                                                         │
│ - Does not expand beyond ACL / max_hops / route scope.                                                             │
│                                                                                                                    │
│ GRAPH WALK EXAMPLE                                                                                                 │
│ cx_052 "Clause 17B"                                                                                                │
│   ├─ parent_document  -> doc_contract_x_2024                                                                        │
│   ├─ modified_by      -> amend_008                                                                                  │
│   ├─ uses_definition  -> cx_010 "Confidential Information"                                                         │
│   └─ related_clause   -> cx_072 "Post-Termination Duties"                                                          │
│                                                                                                                    │
│ OUTPUT                                                                                                             │
│ GraphExpandedEvidencePool = {                                                                                      │
│   original_candidates: ["cx_044", "cx_051", "cx_072", "cx_052", "amend_008"],                                  │
│   graph_neighbors: ["cx_010", "cx_072", "amend_008"],                                                            │
│   entity_map: {                                                                                                    │
│     "Contract X": ["doc_contract_x_2024", "doc_contract_x_amendment_2"],                                         │
│     "Clause 17B": ["cx_052", "amend_008"],                                                                       │
│     "Confidential Information": ["cx_010"]                                                                        │
│   },                                                                                                                │
│   relation_map: [                                                                                                  │
│     ["amend_008", "modifies", "cx_052"],                                                                         │
│     ["cx_052", "uses_defined_term", "cx_010"],                                                                   │
│     ["cx_052", "related_to", "cx_072"]                                                                           │
│   ],                                                                                                                │
│   conflict_candidates: [                                                                                            │
│     "Base clause says immediate termination; Amendment 2 modifies timing for regulated data incidents."            │
│   ]                                                                                                                 │
│ }                                                                                                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        │  JUSTIFICATION:
        │  The exact clause alone may not be enough.
        │  The graph reveals that an amendment changes the effective meaning.
        ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.4 SHAPE                                                                                                         │
│ "Dedupe, rerank, prune, and stratify the evidence."                                                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DOES                                                                                                               │
│ - Dedupe duplicate dense/sparse hits.                                                                               │
│ - Rerank using text, metadata, source authority, freshness, graph proximity, and support target.                    │
│ - Promote exact clause and amendment.                                                                               │
│ - Demote or exclude semantic false positives.                                                                       │
│ - Preserve contradictions instead of hiding them.                                                                   │
│ - Classify evidence as MUST_USE, SUPPORTING, CONTRADICTS, BACKGROUND, EXCLUDED.                                     │
│                                                                                                                    │
│ DOES NOT                                                                                                           │
│ - Does not redo the original vector search unless C0.6 later triggers a bounded refinement pass.                    │
│ - Does not answer.                                                                                                 │
│                                                                                                                    │
│ RERANK / PRUNE EXAMPLE                                                                                             │
│                                                                                                                    │
│ PROMOTE                                                                                                            │
│ - amend_008: latest amendment directly modifies Clause 17B                                                         │
│ - cx_052: exact requested Clause 17B                                                                                │
│                                                                                                                    │
│ SUPPORT                                                                                                            │
│ - cx_010: definition of Confidential Information                                                                    │
│ - cx_072: post-termination duties                                                                                   │
│                                                                                                                    │
│ EXCLUDE                                                                                                            │
│ - cx_044: semantically similar but wrong clause, Clause 16                                                          │
│ - cx_051: nearby but wrong clause, Clause 17A                                                                       │
│                                                                                                                    │
│ OUTPUT                                                                                                             │
│ ShapedEvidenceSet = {                                                                                              │
│   ranked_evidence: [                                                                                               │
│     {rank: 1, chunk_id: "amend_008", class: "MUST_USE", reason: "latest amendment modifies Clause 17B"},          │
│     {rank: 2, chunk_id: "cx_052",    class: "MUST_USE", reason: "exact requested clause"},                       │
│     {rank: 3, chunk_id: "cx_010",    class: "SUPPORTING", reason: "defines key term"},                           │
│     {rank: 4, chunk_id: "cx_072",    class: "SUPPORTING", reason: "related post-termination obligation"}         │
│   ],                                                                                                                │
│   excluded_with_reasons: [                                                                                          │
│     {chunk_id: "cx_044", reason: "wrong clause"},                                                                  │
│     {chunk_id: "cx_051", reason: "wrong clause"}                                                                   │
│   ],                                                                                                                │
│   contradiction_or_override_flags: [                                                                                 │
│     {base: "cx_052", override: "amend_008", issue: "effective timing changed by amendment"}                       │
│   ]                                                                                                                 │
│ }                                                                                                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        │  JUSTIFICATION:
        │  This is where dense false positives get corrected.
        │  Dense said Clause 16 looked similar.
        │  Sparse + metadata + graph prove Clause 17B and its amendment are the right evidence.
        ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.5 EVIDENCE CONTRACT                                                                                             │
│ "Verify the evidence is strong enough to pack into the prompt."                                                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DOES                                                                                                               │
│ - Verifies source_id resolves.                                                                                     │
│ - Verifies span / line / section anchor resolves.                                                                  │
│ - Verifies version and snapshot.                                                                                   │
│ - Verifies ACL clearance.                                                                                          │
│ - Scores direct support, freshness, coverage, authority, contradiction risk, unsupported-inference risk.            │
│ - Emits status: PASS, WEAK, CONFLICTED, EMPTY, BLOCKED.                                                            │
│                                                                                                                    │
│ DOES NOT                                                                                                           │
│ - Does not write final prose.                                                                                      │
│ - Does not approve final output.                                                                                   │
│                                                                                                                    │
│ OUTPUT                                                                                                             │
│ EvidenceContract = {                                                                                               │
│   status: "PASS_WITH_CAVEAT",                                                                                      │
│   support_score: 0.91,                                                                                             │
│   verified_chunks: ["amend_008", "cx_052", "cx_010", "cx_072"],                                                  │
│   cited_spans: [                                                                                                   │
│     {chunk_id: "amend_008", section: "Amendment to Clause 17B", span_status: "verified"},                        │
│     {chunk_id: "cx_052", section: "Clause 17B - Immediate Termination", span_status: "verified"}                 │
│   ],                                                                                                                │
│   caveat: "Base clause says immediate termination, but Amendment 2 changes timing for regulated data incidents.",  │
│   recommended_disposition: "proceed_with_caveat"                                                                   │
│ }                                                                                                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        │  JUSTIFICATION:
        │  Prompt Assembly and L2 need a clean contract:
        │  what evidence can be used, how strong it is, and what caveats must be preserved.
        ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.6 REFINE / BROADEN / DECOMPOSE                                                                                  │
│ "Only retry retrieval if support is weak and the route budget allows it."                                          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DOES                                                                                                               │
│ - Runs only if C0.5 is WEAK, EMPTY, CONFLICTED, or BLOCKED and refinement is allowed.                              │
│ - Chooses tactic: rewrite, broaden, narrow, decompose, graph_hop, or abstain.                                      │
│ - Can trigger one bounded second pass through C0.2 -> C0.4 -> C0.5.                                                │
│ - If still weak, recommends fallback/abstain/reroute.                                                              │
│                                                                                                                    │
│ DOES NOT                                                                                                           │
│ - Does not silently keep searching forever.                                                                        │
│ - Does not change the route by itself.                                                                             │
│ - Does not answer.                                                                                                 │
│                                                                                                                    │
│ EXAMPLE IF WEAK                                                                                                    │
│ WeakSupportDiagnosis = {                                                                                           │
│   issue: "amendment found but base Clause 17B missing",                                                           │
│   tactic: "narrow + graph_hop",                                                                                    │
│   refined_query: "Contract X base agreement Clause 17B Immediate Termination",                                    │
│   adjusted_filters: {include_base_contract: true, include_amendments: true},                                       │
│   max_additional_passes: 1                                                                                         │
│ }                                                                                                                  │
│                                                                                                                    │
│ OUTPUT IF SECOND PASS WORKS                                                                                        │
│ RefinedEvidenceContract = {status: "PASS_WITH_CAVEAT", support_score: 0.91}                                       │
│                                                                                                                    │
│ OUTPUT IF SECOND PASS FAILS                                                                                        │
│ FinalEvidenceContract = {status: "WEAK", recommended_disposition: "abstain_or_R5"}                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        │  JUSTIFICATION:
        │  C0 can improve weak evidence once within budget.
        │  But C0 cannot self-authorize a new route or pretend weak evidence is strong.
        ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FINAL C0 OUTPUT                                                                                                    │
│ FinalEvidenceContract                                                                                              │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PACKED FOR PROMPT ASSEMBLY                                                                                         │
│ - MUST_USE: Amendment 2 to Clause 17B                                                                               │
│ - MUST_USE: Base Clause 17B                                                                                         │
│ - SUPPORTING: definition of Confidential Information                                                                │
│ - SUPPORTING: post-termination duties                                                                               │
│ - EXCLUDED: Clause 16 and Clause 17A dense false positives                                                          │
│ - CAVEAT: amendment changes effective reading                                                                       │
│ - STATUS: PASS_WITH_CAVEAT                                                                                          │
│ - SUPPORT_SCORE: 0.91                                                                                               │
│ - LINEAGE: dense + sparse + metadata + graph                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        ▼

[ PROMPT ASSEMBLY ]
- Packs verified evidence as data, not instruction.
- Preserves authority order.
- Sends bounded PromptEnvelope to L2.

        │
        ▼

[ L2 EXECUTE ]
- Uses the evidence contract to answer.
- Does not invent unsupported claims.

        │
        ▼

[ EXIT EVAL & CONTROL ]
- Checks groundedness, citations, safety, schema, support, and final disposition.
========================================================================================================================