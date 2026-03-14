============================================================================================================================================
                         AGENTIC RAG — NON-LINEAR COMPLETENESS-AWARE RETRIEVAL PIPELINE (PARALLEL & ITERATIVE FLOW)
============================================================================================================================================
 [ L1: COGNITIVE PRIMING ]        [ L2: COMPLETENESS-AWARE RETRIEVAL PIPELINE — PARALLEL & ITERATIVE ]         [ L4: STATE & INTEGRITY ]
+-------------------------+   +-------------------------------------------------------------------------+   +------------------------------+
| RAG PRIMING PHASE       |   |                                                                         |   | RAG INTEGRITY HUB            |
|-------------------------|   |     STEP 4a: VECTOR (PARALLEL)         STEP 4b: LEXICAL (PARALLEL)        |   |------------------------------|
| - Seed Pack Lookup      |-->|  +------------------------------+   +------------------------------+    |-->| - ChunkManifestRegistry (L4D)|
| - Top-K: 20, Cutoff >=.5|   |  | IRetrieverVector (FAISS)     |   | IRetrieverLexical (BM25)     |    |   | - ParentChildIndex (L4E)     |
| - P1: Hydrate via KG    |   |  | - SHA-256 / BLAS SINGLETON   |   | - Scope/Condition/Error Spans|    |   | - RetrievalEvaluation (L4F)  |
| - P4: Emit Intent + C0  |   |  | - ADG: retrieves_via (52)    |   | - Structural Signals         |    |   | - CompletenessSnapshot (L4G) |
+-------------------------+   |  +------------------------------+   +------------------------------+    |   |                              |
                              |                 |                                  |                    |   | SOVEREIGNTY:                 |
                              |                 +----------------------------------+                    |   | - Write-once, content-hash   |
                              |                                  V                                      |   | - Never authorize/execute    |
                              |   +-------------------------------------------------------------------------+   | - Idempotent by hash         |
                              |   | STEP 4c: FUSION & PARENT-CHILD EXPANSION (ITERATIVE)                    |   +------------------------------+
                              |   |-------------------------------------------------------------------------|
                              |   | RRF / ScoreFusion → Dedupe by chunk_id                                  |
                              |   | IParentChildExpander: child → parent + sibling window                   |
                              |   | - Reads: ParentChildRegistry (L4E) <---------------------------+ (LOOP) |
                              |   | - ADG: pulls_context (32) | Depth: 1-5 levels (Configurable) ------+    |
                              |   +------------------------------|------------------------------------------+
                              |                                  V
                              |   +-------------------------------------------------------------------------+
                              |   | STEP 4d: COMPLETENESS SCORING (CONDITIONAL BRANCHING)                   |
                              |   |-------------------------------------------------------------------------|
                              |   | KeywordCompletenessScorer: if/when/unless, error scenarios, versioning   |
                              |   | - IF score >= 0.8: Skip aggressive reranking; use light weights         |
                              |   | - IF score < 0.5: Trigger aggressive reranking + deep expansion --------|--> (To Step 4e)
                              |   | - Output: ContextCompletenessScore -> L4G (Telemetry)                   |
                              |   +------------------------------|------------------------------------------+
                              |                                  V
                              |   +-------------------------------------------------------------------------+
                              |   | STEP 4e: COMPLETENESS RERANKING (ADAPTIVE WEIGHTS)                      |
                              |   |-------------------------------------------------------------------------|
                              |   | $final\_score = (w_{rel} \cdot S_{sim}) + (w_{comp} \cdot S_{comp})$     |
                              |   | - ADAPTIVE: If score < 0.5, set $w_{comp}$ to 0.5 (Dynamic Blend)       |
                              |   +------------------------------|------------------------------------------+
                              |                                  V
                              |   +-------------------------------------------------------------------------+
                              |   | STEP 5: TOP-K CONTEXT ASSEMBLY & ANSWER SUPPORT VALIDATION              |
                              |   |-------------------------------------------------------------------------|
                              |   | IAnswerSupportValidator: Sentence-coverage check vs. evidence corpus     |
                              |   | C0 SOVEREIGNTY: ✗ No routing mutation | ✗ No tier escalation | ✓ Context |
                              +---|-------------------------------------------------------------------------|
                                  | OUTPUT: C0 Context Package -> L0 Routing / L3 Orchestration             |
                                  +-------------------------------------------------------------------------+

============================================================================================================================================
 [ META-LEARNING FEEDBACK LOOP — CROSS-QUERY ADAPTATION ]
============================================================================================================================================
| CompletenessRAGProposer.propose(EvaluationSignals) -> CompletenessChangePackage (proposal_only=True)                              |
|------------------------------------------------------------------------------------------------------------------------------------------|
| 1. Low mean_completeness (<0.5)  -> Propose: parent_expansion_depth++ (Modifies Step 4c)                                                 |
| 2. High chunk_fragmentation      -> Propose: section-aware chunking strategy (L4D Ingestion)                                             |
| 3. Low fully_supported (<0.5)    -> Propose: hybrid retrieval mode (Enable Parallel 4a + 4b)                                             |
| 4. High missing_condition rate   -> Propose: lexical_exact_match_boost (Increase 4e completeness_weight)                                 |
| 5. Low observation count         -> No proposals (Dampening gate active)                                                                 |
============================================================================================================================================
 [ PIPELINE EXECUTION PATTERNS ]                                     [ EVALUATION SPINE — METRICS & CHUNKING ]
+-------------------------------------------------------------+     +----------------------------------------------------------------------+
| PARALLEL: 4a + 4b (Fork-Join) Concurrent Retrieval          |     | METRICS: Precision@K, Recall@K, MRR, NDCG, Groundedness (F1)         |
| ITERATIVE: 4c Recursive parent/grandparent expansion        |     | PIPELINES: Vector (4a), Hybrid (4a+4b), Hybrid+Reranked (4a+4b+4e)    |
| CONDITIONAL: 4d Score-based weight adjustment & reranking   |     | CHUNKING: FixedToken, OverlapWindow, SectionAware, Semantic          |
| FEEDBACK: N queries influence N+1 config via Meta-Learning  |     | RUNNERS: Offline, Replay, ShadowEvaluationRunner (L4)                |
+-------------------------------------------------------------+     +----------------------------------------------------------------------+

============================================================================================================================================
 RAG DATA CONTRACTS & SOVEREIGNTY INVARIANTS
============================================================================================================================================
| [13] RagQuery      : [query_text, top_k, filters, metadata]     | [19] SupportedAnswerCheck : [fully_supported, claim_spans, score]      |
| [14] RagResult     : [documents: list[RagDocument], metadata]   | [22] ChunkManifest (L4D)  : [chunk_id, heading_path, content_hash]      |
| [18] ContextComp   : [missing_signals, score, confidence]       | [25] ChangePackage        : [proposal_only=True, changes, hash]        |
|------------------------------------------------------------------------------------------------------------------------------------------|
| SOVEREIGNTY INVARIANT: Contracts [18]-[25] carry NO route_mode, safety_threshold, execution_tier, or auth_token fields.                  |
============================================================================================================================================
ADG CACHE: Nodes: 8,234 | Edges: 224,969 | RAG TOPOLOGY: retrieves_via(52), pulls_context(32), scores_groundedness(40), generates_prompt(215)
