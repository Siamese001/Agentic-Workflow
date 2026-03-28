# UNIFIED ARCHITECTURAL SPEC: AGENTIC RETRIEVAL & RAG PIPELINES (v8 - FLOWCHART INTEGRITY HUB)

+=========================================================================================================================================================================================+
|                                                                SYSTEM ARCHITECTURE & MACRO TOPOLOGY: THE FOUR PIPELINES                                                                 |
+=========================================================================================================================================================================================+
| [ PIPELINE A: MODEL TRAINING ]       Public/licensed corpora -> model training -> model weights (No vector DB population)                                                               |
| [ PIPELINE B: INGESTION / INDEXING ] External documents -> chunk -> ENRICH (Text->Knowledge Object) -> embed -> vector DB (Builds retrieval substrate)                                  |
| [ PIPELINE C: INFERENCE / RUNTIME ]  User query -> exact cache -> semantic cache -> AGENTIC RAG -> agentic action -> fallback (Consumes stores; never creates chunks)                   |
| [ PIPELINE D: LEARNING / GROWTH ]    L4/L6 Telemetry -> fixed embed (bge-m3) -> Vector DB -> Meta-Learning (Analyzes vectors; never retrains model)                                     |
+=========================================================================================================================================================================================+

+=========================================================================================================================================================================================+
|                                                                PIPELINE B: INGESTION & INDEX BUILD (OFFLINE PRE-RUNTIME)                                                                |
+=========================================================================================================================================================================================+
| [ RAW SOURCES ] -> PDFs, Docs, DBs, SharePoint, Web Fetch, L4 Execution Telemetry, L2 Incident Traces                                                                                   |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 1. DATA PREP ] ----> Document Load / Trace Parse -> Text Extract -> Clean & Normalize                                                                                                 |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 2. CHUNKING ] -----> Split into base text units (paragraph-level, sliding window, execution events) -> Generate Base ChunkManifest (L4D)                                              |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 3. ENRICHMENT ] ---> [⭐️ CORE LOGIC: SEMANTIC ENRICHMENT LAYER ]                                                                                                                      |
|       |                LLM Prompt transforms the raw 'Dumb Text Chunk' into a structured 'Semantic Knowledge Object'.                                                                   |
|       |                Payload: [ Title | Summary | Key Concepts | Agentic Patterns | Execution Insight | Query Expansion Terms ]                                                         |
|       v                                                                                                                                                                                 |
| [ 4. METADATA ] -----> Bind doc_id, source, security labels, ADG edges (reads_from, writes_to), healer_used, success_status, trace_id, replay_key, ParentChildIndex (L4E)               |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 5. EMBEDDING ] ----> Convert ENRICHED KNOWLEDGE OBJECT → tokens → vector array (e.g., [0.21, -0.33, 0.77...])                                                                         |
|       |                +------------------------------------------------------------------------------------------------------------------------------------+                           |
|       |                | ⚠️ DISAMBIGUATION: TOKEN MATRIX vs. EMBEDDING PIPELINE                                                                             |                           |
|       |                | Token Matrix: Internal to transformer (vocab x hidden_dim). Maps words to initial shelf coordinates.                               |                           |
|       |                | Embedding Model: e.g., BGE-M3. Summarizes ENRICHED CONCEPTS into final semantic vector for FAISS archive.                          |                           |
|       |                +------------------------------------------------------------------------------------------------------------------------------------+                           |
|       |                | ⚙️ EMBEDDING EXECUTION FLOW (RUNTIME INSTANTIATION)                                                                                |                           |
|       |                | 1. IDENTIFIER:  [BAAI/bge-m3]                                                                                                      |                           |
|       |                |                       │                                                                                                            |                           |
|       |                |                       ▼                                                                                                            |                           |
|       |                | 2. NETWORK I/O: (Download weights & config from Hugging Face)                                                                      |                           |
|       |                |                       │                                                                                                            |                           |
|       |                |                       ▼                                                                                                            |                           |
|       |                | 3. RAM ALLOC:   [MODEL ARCHITECTURE + WEIGHTS LOADED IN MEMORY]                                                                    |                           |
|       |                |                       │                                                                                                            |                           |
|       |                |                       ▼                                                                                                            |                           |
|       |                | 4. EXECUTION:   .encode(enriched_structured_payload) <--- (Shift from text similarity to concept similarity)                       |                           |
|       |                |                       │                                                                                                            |                           |
|       |                |                       ▼                                                                                                            |                           |
|       |                | 5. OUTPUT:      [HIGH-SIGNAL EMBEDDING VECTOR ARRAY]                                                                               |                           |
|       |                +------------------------------------------------------------------------------------------------------------------------------------+                           |
|       +------------------------------------+------------------------------------+                                                                                                       |
|       |                                    |                                    |                                                                                                       |
|       v                                    v                                    v                                                                                                       |
| [ VECTOR DB ]                        [ METADATA DB ]                      [ CANONICAL STORE ]                                                                                           |
| Stores vectors + Enriched Payload    Stores entity relations / ADG        Stores original files & telemetry (Blob/S3/Postgres)                                                          |
| (FAISS - Concept Clustered)          (ParentChildRegistry L4E)            (ChunkManifestRegistry L4D)                                                                                   |
|                                      ADG: 8.2k Nodes, 224k Edges                                                                                                                        |
|                                                                                                                                                                                         |
| THE HARD RULE: No ingestion -> no chunks -> empty vector DB -> no RAG retrieval possible. Knowledge grows via index expansion, NOT model retraining.                                    |
+=========================================================================================================================================================================================+

===========================================================================================================================================================================================
PIPELINE C: INFERENCE / QUERY TIME (INTEGRATED CASCADING AGENT)
===========================================================================================================================================================================================
PIPELINE SEPARATION (CORE TRUTH): Ingestion (Pipeline B) & Learning (Pipeline D) create chunks/embeddings. Inference (Pipeline C) NEVER creates chunks.

[ START: INBOUND USER QUERY / TASK ]
          |
          v
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| QUERY PRE-PROCESSING (SHARED)                                                                                                                                                           |
| Action: Normalize Query (raw_text) -> Tokenize -> Embed via API (Generate q_vector representing Query Intent)                                                                           |
| EMBEDDING CONSISTENCY RULE: Query embedding model MUST exactly match indexing model (e.g., bge-m3). Model change requires full re-indexing.                                             |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
          | (Produces both raw_text and q_vector for downstream layers)
          v
================================================================( L1 ADVISORY / L0 AUTHORITY BOUNDARY )====================================================================================
| L1 VECTOR SEARCH IS ADVISORY (Calculates similarity); L0 RETAINS AUTHORITY (Dispatcher selects path/agent based on metadata & cluster stats).                                           |
===========================================================================================================================================================================================
          |
          v
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| 1. LAYER 1: EXACT CACHE          | 2. LAYER 2: SEMANTIC CACHE       | 3. LAYER 3: AGENTIC RAG (C0)     | 4. LAYER 4: AGENTIC ACTION       | 5. LAYER 5: LLM FALLBACK         |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| SIGNAL: Hash(raw_text)           | SIGNAL: [q_vector]               | SIGNAL: [q_vec + intent]         | SIGNAL: [raw_text + schemas]     | SIGNAL: [raw_text]               |
| EMBED:  Bypassed                 | EMBED:  Required                 | EMBED:  Required                 | EMBED:  Bypassed                 | EMBED:  Bypassed                 |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| COND: Exact Call Number?         | COND: Familiar Request?          | COND: Topic in Archival Stacks?  | COND: External Action?           | COND: No External Matches?       |
| (O(1) Hash Lookup)               | (Vector Score > 0.95)            | (Search Semantic Vector DB)      | (API / DB Mutation)              | (Parametric Memory)              |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| -- NO (Miss) ---->               | -- NO (Empty) ---->              | -- NO (Skip) ---->               | -- NO (None) ---->               | -- YES (Execute)                 |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| YES                              | YES                              | YES                              | YES                              | YES                              |
| v                                | v                                | v                                | v                                | v                                |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| INTERNAL MECHANICS:              | INTERNAL MECHANICS:              | INTERNAL MECHANICS:              | INTERNAL MECHANICS:              | INTERNAL MECHANICS:              |
| - SHA-256 / Exact Match          | - Cosine Sim > 0.95              | - 4a. Vector Match on CONCEPTS   | - LangGraph Orchestration        | - System Prompt Inject           |
| - RAG Priming Phase:             | - GPTCache Lookup                | - 4b. Lexical Match on EXPANSION | - Tool Auth / Sandbox            | - Token Matrix Eval              |
|   > Seed Pack Lookup             | - LRU Eviction                   | - 4c. Parent-Child Expansion     | - API / DB Sandbox Binding       | - Next-Token Predict             |
|   > Hydrate via KG (P1)          | - Zero-token return              | - 4d. Completeness Score (<0.5)  | - Execution Telemetry / Parse    | - Unrestricted Gen               |
|   > Emit Intent + C0 (P4)        |                                  | - 4e. Adaptive W_comp Rerank     | - State Sync to Canonical Store  |                                  |
| - TTL Validation                 |                                  | - 5. Assembly: High-Signal C0    |                                  |                                  |
|                                  |                                  |      (Includes execution notes)  |                                  |                                  |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| ANALOGY: Librarian hands exact   | ANALOGY: Librarian safely reuses | ANALOGY: Archivist retrieves     | ANALOGY: Specialist Librarian    | ANALOGY: Librarian answers       |
| index card back.                 | past entry.                      | curated index cards & notes.     | dispatched for governed act.     | directly from internal memory.   |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| ZONE: Shared Mem Cache           | ZONE: Shared Mem Cache           | ZONE: Durable Store              | ZONE: App Process Heap           | ZONE: LLM Weights                |
| INFRA: Redis, Memcached          | INFRA: Redis, GPTCache           | INFRA: FAISS, Pinecone           | INFRA: LangGraph                 | INFRA: Token Matrix              |
| TRUTH: Never Authoritative       | TRUTH: Never Authoritative       | TRUTH: Document/Concept Grounding| TRUTH: Execution Engine          | TRUTH: Parametric Eval           |
| MUTATION: Read-Only              | MUTATION: Read-Only              | MUTATION: Read-Only              | MUTATION: Read/Write             | MUTATION: Read-Only              |
| BUDGET: Zero Token               | BUDGET: Low Token                | BUDGET: High Token               | BUDGET: Max Token                | BUDGET: Med/High Token           |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| RAG INTEGRITY HUB: SOVEREIGNTY INVARIANTS (Write-once, content-hash indexed, NEVER authorizes execution. NO route_mode, safety_threshold, or execution_tier.)                |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| [N/A - EXTERNAL TO HUB]          | [N/A - EXTERNAL TO HUB]          | [ L3: AGENTIC RAG (READS) ]      | [ L4/L6: TELEMETRY (WRITES) ]    | [N/A - EXTERNAL TO HUB]          |
|                                  |                                  |   ┌──────────────────────────┐   |   ┌──────────────────────────┐   |                                  |
|                                  |                                  |   │ 1. ChunkManifest (L4D)   │   |   │ 3. RetrievalEval (L4F)   │   |                                  |
|                                  |                                  |   ├──────────────────────────┤   |   ├──────────────────────────┤   |                                  |
|                                  |                                  |   │ DOM: Ingest/Substrate    │   |   │ DOM: Execution Quality   │   |                                  |
|                                  |                                  |   │ KEY: chunk_id(SHA-256)   │   |   │ KEY: trace_id/query_hash │   |                                  |
|                                  |                                  |   │ DAT: [22]EnrichedManifst │   |   │ DAT: [19]SuppAnswerCheck │   |                                  |
|                                  |                                  |   │ MEC: Payload integrity,  │   |   │ MEC: Log Prec/Recall/MRR │   |                                  |
|                                  |                                  |   │      Map struct to head, │   |   │      Store F1(Grounded), │   |                                  |
|                                  |                                  |   │      Exact knowledge ret │   |   │      Emit Shadow signals │   |                                  |
|                                  |                                  |   └──────────┬───────────────┘   |   └──────────┬───────────────┘   |                                  |
|                                  |                                  |              │                   |              │                   |                                  |
|                                  |                                  |   ┌──────────▼───────────────┐   |   ┌──────────▼───────────────┐   |                                  |
|                                  |                                  |   │ 2. ParentChildIdx (L4E)  │   |   │ 4. CompletnessSnap (L4G) │   |                                  |
|                                  |                                  |   ├──────────────────────────┤   |   ├──────────────────────────┤   |                                  |
|                                  |                                  |   │ DOM: Graph & Relatnships │   |   │ DOM: Ctx Health/Support  │   |                                  |
|                                  |                                  |   │ KEY: parent_id/child_id  │   |   │ KEY: trace_id/snap_hash  │   |                                  |
|                                  |                                  |   │ DAT: ADG Edges           │   |   │ DAT: [18] ContextComp    │   |                                  |
|                                  |                                  |   │ MEC: Resolve pull_cntxt, │   |   │ MEC: Capture CtxCompScor │   |                                  |
|                                  |                                  |   │      Define depth(1-5),  │   |   │      Log missing_signals │   |                                  |
|                                  |                                  |   │      Hydrate sibling win │   |   │      Feed CmpRAGProposer │   |                                  |
|                                  |                                  |   └──────────────────────────┘   |   └──────────────────────────┘   |                                  |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+

+=========================================================================================================================================================================================+
| SYSTEM INVARIANTS, EVALUATION SPINE & EXECUTION PATTERNS (APPLIES TO L3/L4)                                                                                                             |
+=========================================================================================================================================================================================+
| RAG EXECUTION: PARALLEL: 4a+4b (Concurrent) | ITERATIVE: 4c (Recursive parent expansion) | CONDITIONAL: 4d (Score-based adaptive rerank weights)                                        |
| EVAL METRICS:  Precision@K, Recall@K, MRR, NDCG, Groundedness (F1) | CHUNKING: FixedToken, OverlapWindow, SectionAware, Semantic Object                                                 |
| ADG CACHE:     Nodes: 8,234 | Edges: 224,969 | RAG TOPOLOGY: retrieves_via(52), pulls_context(32), scores_groundedness(40), generates_prompt(215)                                       |
+=========================================================================================================================================================================================+

===========================================================================================================================================================================================
PIPELINE D: META-LEARNING FEEDBACK LOOP (OFFLINE POST-RUNTIME DECISION TREE)
===========================================================================================================================================================================================
[ L4/L6 TELEMETRY & TRACES ] -> [ EVALUATION RUNNERS (Shadow/Replay) ] -> Emits [ EvaluationSignals ] -> [ CompletenessRAGProposer ]

FEEDBACK TRIGGERS (N queries influence N+1 config via Meta-Learning Columnar Flow):

+-------------------------+             +-------------------------+             +-------------------------+             +-------------------------+             +-------------------------+
| 1. EVAL: COMPLETENESS   |             | 2. EVAL: FRAGMENTATION  |             | 3. EVAL: GROUNDEDNESS   |             | 4. EVAL: LEXICAL GAP    |             | 5. EVAL: SIGNAL VOLUME  |
+-------------------------+             +-------------------------+             +-------------------------+             +-------------------------+             +-------------------------+
| COND: Score < 0.5?      | -- NO ----> | COND: Boundary Errors?  | -- NO ----> | COND: Fully Supported?  | -- NO ----> | COND: High Missing Cond?| -- NO ----> | COND: Low Observations? |
| (mean_completeness)     |             | (High fragmentation)    |             | (Support score < 0.5)   |             | (Lexical exact match)   |             | (Dampening gate active) |
+-------------------------+             +-------------------------+             +-------------------------+             +-------------------------+             +-------------------------+
          | YES                                   | YES                                   | YES                                   | YES                                   | YES
          v                                       v                                       v                                       v                                       v
+-------------------------+             +-------------------------+             +-------------------------+             +-------------------------+             +-------------------------+
| PROPOSAL: Depth++       |             | PROPOSAL: Enrichment+   |             | PROPOSAL: Hybrid Mode   |             | PROPOSAL: Lexical Boost |             | ACTION: None            |
| (Modifies Step 4c)      |             | (Modifies L4D Prompts)  |             | (Enable Parallel 4a+4b) |             | (Increase 4e weight)    |             | (Awaiting N queries)    |
+-------------------------+             +-------------------------+             +-------------------------+             +-------------------------+             +-------------------------+
          |                                       |                                       |                                       |                                       |
          +---------------------------------------+-------------------+-------------------+---------------------------------------+---------------------------------------+
                                                                      |
                                                                      v
                                                      [ CompletenessChangePackage ]
                                                      (proposal_only=True) -> L5 Board

===========================================================================================================================================================================================
DETAILED OPERATIONAL, DATA CONTRACT & FAILURE MODE MATRIX
===========================================================================================================================================================================================
FEATURE                   | 1. L1: EXACT CACHE        | 2. L2: SEMANTIC CACHE     | 3. L3: AGENTIC RAG (C0)   | 4. L4: AGENTIC ACTION     | 5. L5: LLM FALLBACK
--------------------------|---------------------------|---------------------------|---------------------------|---------------------------|------------------------------------------------
EMBEDDING DEPENDENCY      | None                      | Strict / Brittle          | Strict / Concept-Driven   | None (Relies on APIs)     | None (Token Matrix internal)
MATCHING LOGIC            | Exact Match / O(1) Hash   | Embed Similarity (>0.95)  | Concept Similarity(Top-K) | Dynamic Tool Selection    | Next-Token Prediction
DATA PAYLOAD              | Strings, hashes, JSON     | Queries vs Queries        | Queries vs KNOWLEDGE OBJs | API requests, JSON, code  | System Prompt vs Weights
LATENCY & COST PROFILE    | Ultra-Low / Zero Cost     | Medium Latency / Low Cost | High Latency / High Cost  | Variable / High Cost      | Variable / Medium Cost
PRIMARY FAILURE MODE      | Cache Misses & Stale Data | False Positives           | Missing Intent Expansions | Infinite Loops / Failure  | Hallucination / Outdated Memory
DATA CONTRACTS            | [1] CacheHit              | [5] SemanticMatch         | [13] RagQuery, [18] Cmp   | [22] EnrichedManifest     | [40] FallbackGen
                          |                           |                           | [14] RagResult, [19] Supp | [25] ChangePackage, [30]  | 
===========================================================================================================================================================================================