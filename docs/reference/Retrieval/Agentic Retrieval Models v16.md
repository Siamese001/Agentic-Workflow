# UNIFIED ARCHITECTURAL SPEC: AGENTIC RETRIEVAL & RAG PIPELINES (v16.5 - FULL SINGLE-PANE INTEGRATION)

+=========================================================================================================================================================================================+
|                                                                ⚙️ SYSTEM ARCHITECTURE & MACRO TOPOLOGY: THE FOUR PIPELINES                                                              |
+=========================================================================================================================================================================================+
| PIPELINE & LIBRARY ANALOGY          | EXECUTION STATE | PATH AUTHORITY  | CORE OPERATIONAL FLOW                       | CHUNK | EMBED | READ | WRITE | PURPOSE & KEY OUTPUT             |
+-------------------------------------+-----------------+-----------------+---------------------------------------------+-------+-------+------+-------+----------------------------------+
| 🏗️ A: MODEL TRAINING                | Offline         | N/A             | Public Corpora -> Train -> Model Weights    |  NO   |  NO   |  NO  |  NO   | Defines base reasoning.          |
|   (Teaching librarian foundational) | (Pre-runtime)   | (Parametric)    | Internal Matrix (vocab_size x hidden_dim)   |       |       |      |       | Output: Static LLM Weights.      |
+-------------------------------------+-----------------+-----------------+---------------------------------------------+-------+-------+------+-------+----------------------------------+
| 📥 B: INGESTION & INDEXING          | Offline         | WRITE PATH      | Raw Docs -> Clean -> Chunk -> Enrich        |  YES  |  YES  |  NO  |  YES  | Defines what the system knows.   |
|   (Adding new books to shelves)     | (Batch/One-time)| (Adds memory)   | -> Embed -> Store in Master Archival DB     |       |       |      |       | Output: Indexed chunks/vectors.  |
+-------------------------------------+-----------------+-----------------+---------------------------------------------+-------+-------+------+-------+----------------------------------+
| 🚀 C: INFERENCE / RUNTIME           | Real-time       | READ PATH       | User Query -> Embed -> Retrieve ->          |  NO   |  YES  | YES  |  NO   | Defines how the system answers.  |
|   (Answering questions using books) | (Per query)     | (Zero write)    | Agentic RAG -> Generate Answer              |       | (Qry) |      |       | Output: Answer + context.        |
+-------------------------------------+-----------------+-----------------+---------------------------------------------+-------+-------+------+-------+----------------------------------+
| 🔄 D: LEARNING & GROWTH             | Asynchronous    | WRITE PATH      | Telemetry/Failures -> Extract -> Chunk      |  YES  |  YES  | YES  |  YES  | Defines how the system improves. |
|   (Writing new books based on exp.) | (Post-runtime)  | (Adds memory)   | -> Embed -> Store in Master Archival DB     |       |       |      |       | Output: Evolved index/patterns.  |
+=========================================================================================================================================================================================+

+=========================================================================================================================================================================================+
|                                                                📥 PIPELINE B: INGESTION & INDEX BUILD (OFFLINE PRE-RUNTIME)                                                             |
+=========================================================================================================================================================================================+
| [ RAW SOURCES ] -> PDFs, Docs, DBs, SharePoint, Web Fetch, L4 Execution Telemetry, L2 Incident Traces                                           |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 1. DATA PREP ] ----> Document Load / Trace Parse -> Text Extract -> Clean & Normalize                                                         |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 2. CHUNKING ] -----> Split into base text units (paragraph-level, sliding window, execution events) -> Generate Base ChunkManifest (L4D)      |
|       |                MODES: FixedToken, OverlapWindow, SectionAware, Semantic Object                                                                                                  |
|       v                                                                                                                                                                                 |
| [ 3. ENRICHMENT ] ---> [⭐️ CORE LOGIC: SEMANTIC ENRICHMENT LAYER (L2 CONSERVATION LAB) ]                                                        |
|       |                LLM Prompt transforms the raw 'Dumb Text Chunk' into a structured 'Semantic Knowledge Object'.                                                                   |
|       |                Payload: [ Title | Summary | Key Concepts | Agentic Patterns | Execution Insight | Query Expansion Terms ]                                                         |
|       v                                                                                                                                                                                 |
| [ 4. METADATA ] -----> Bind doc_id, source, security labels, ADG edges (reads_from, writes_to), healer_used, success_status, trace_id, replay_key, ParentChildIndex (L4E)               |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 5. EMBEDDING ] ----> Convert ENRICHED KNOWLEDGE OBJECT → Tokenizer (Cataloging Clerk) → discrete catalog entries                                      |
|       |                +------------------------------------------------------------------------------------------------------------------------------------+                           |
|       |                | ⚙️ EXTERNAL EMBEDDING PIPELINE FLOW (BGE-M3 / The Reference Librarian)                             |                           |
|       |                | 1. IDENTIFIER:  [BAAI/bge-m3] downloaded from Hub to ~/.cache/huggingface/                                                         |                           |
|       |                | 2. RAM ALLOC:   [BGE MODEL TRAINED NEURAL NETWORK LOADED IN MEMORY]                                                                |                           |
|       |                | 3. EXECUTION:   .encode(tokens) -> pooling/projection -> final semantic summary formulation                                        |                           |
|       |                | 4. OUTPUT:      [ 🟠 ENRICHED FACT VECTOR (fact_vec) ] <--- The "Semantic Call Number"                                             |                           |
|       |                +------------------------------------------------------------------------------------------------------------------------------------+                           |
|       +------------------------------------+------------------------------------+                                                                                                       |
|       |                                    |                                    |                                                                                                       |
|       v                                    v                                    v                                                                                                       |
|  🗄️ [ MASTER ARCHIVE (VECTOR DB) ]   🗃️ [ METADATA DB ]                   📦 [ CANONICAL STORE ]                                                                                        |
|  Durable knowledge store             (L4 SQLite) Canonical Truth          Stores original files & telemetry (Blob/S3/Postgres)                                                          |
|  Stores 🟠 fact_vecs (documents)     Stores entity relations / ADG        (ChunkManifestRegistry L4D)                                           |
|  (FAISS/Chroma - Concept Clustered)  (ParentChildRegistry L4E)            ADG CACHE: 8,234 Nodes, 225k Edges                                                                            |
+=========================================================================================================================================================================================+

===========================================================================================================================================================================================
🚀 PIPELINE C: INFERENCE / QUERY TIME (INTEGRATED CASCADING AGENT)
===========================================================================================================================================================================================
[ RETRIEVAL STACK PRINCIPLE: Caches (L1/L2) optimize speed, Vector DB (L3) provides knowledge, L4 provides truth and auditability. ]

[ START: INBOUND USER QUERY / TASK ]
          |
          v
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 🔍 QUERY PRE-PROCESSING (SHARED EXTERNAL PIPELINE)                                                                                                      |
| 1. TOKENIZE:    Cataloging Clerk discretizes the raw user query string into discrete tokens.                                                                                            |
| 2. EXECUTION:   External BGE-M3 API -> .encode(tokens) -> pooling -> pure intent representation.                                                                                        |
| 3. OUTPUT:      [ 🔵 EPHEMERAL INTENT VECTOR (intent_vec) ] <--- The temporary "Semantic Seeker Call Number".                                                                           |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
                                                                |
================================================================( L1 ADVISORY -> L0 AUTHORITY BOUNDARY )===================================================================================
| 🚦 [ L0: FRONT DESK DISPATCHER (AUTHORITY) ]                                                                                                    |
| ROLE:   Retains final routing authority based on budget and exact thresholds. Retrieval NEVER decides execution.                                                                        |
| OUTPUT: Places Dual-Rail payload {text, 🔵 intent_vec} onto the bus and triggers the execution layer.                                                                                   |
===========================================================================================================================================================================================
                            [ DUAL-RAIL SIGNAL ROUTING BUS, MEMORY INVARIANTS & DATA CONTRACTS ]
[RAW_TEXT]  ───────┬──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┐
                   │                                  │                                  │                                  │                                  │
[🔵 intent] ───────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
                   │                                  │                                  │                                  │                                  │
                   ▼ (Text)                           ▼ (🔵intent)                       ▼ (🔵intent vs 🟠fact)             ▼ (Text)                           ▼ (Text)
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| ⚡ 1. LAYER 1: EXACT CACHE       | 🧠 2. LAYER 2: SEMANTIC CACHE    | 📚 3. LAYER 3: AGENTIC RAG (C0)| 🛠️ 4. LAYER 4: AGENTIC ACTION    | 🔮 5. LAYER 5: LLM FALLBACK      |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| 🏛️ ANALOGY: Skip vector math;    | 🏛️ ANALOGY: Compare new slip     | 🏛️ ANALOGY: Walk slip (🔵intent)| 🏛️ ANALOGY: Escalate to an       | 🏛️ ANALOGY: Answer directly      |
| lookup exact text call number.   | (🔵intent) vs old slips (🔵intent)| to Master Archive to find book  | active specialist (Text only).   | from internal reading matrix.    |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| SIGNAL: Hash(raw_text)           | SIGNAL: 🔵intent vs 🔵intent     | SIGNAL: 🔵 intent vs 🟠 fact     | SIGNAL: [raw_text + schemas]     | SIGNAL: raw_text (No vector)     |
| LOGIC:  Exact Match / O(1) Hash  | LOGIC:  Embed Sim (>0.95)        | LOGIC:  Concept Sim (Top-K)      | LOGIC:  Dynamic Tool Selection   | LOGIC:  Next-Token Prediction    |
| PAYLOAD:Strings, hashes, JSON    | PAYLOAD:🔵 intent vs 🔵 intent     | PAYLOAD:🔵 intent vs 🟠 fact     | PAYLOAD:API reqs, JSON, code     | PAYLOAD:Sys Prompt vs Weights    |
| EMBED:  NO embeddings used       | EMBED:  Required (External BGE)  | EMBED:  Required (External BGE)  | EMBED:  Bypassed                 | EMBED:  Internal Matrix Used     |
| INFRA:  Redis (RAM-first cache)  | INFRA:  GPTCache backed by Redis | INFRA:  FAISS / Master Archive   | INFRA:  Local Process Heap       | INFRA:  Token Embedding Matrix   |
| STORE:  key=SHA256, val=response | STORE:  [🔵intent_vec] (queries) | STORE:  [🟠fact_vec] (documents) | STORE:  App Memory (Exec state)  | STORE:  Static Parametric Mem    |
| VECTORS:NO vectors stored        | VECTORS:NEVER reads Vector DB    | VECTORS:NEVER writes to Redis    | VECTORS:NO vectors processed     | VECTORS:Internal mapped coords   |
| TRUTH:  Ephemeral / NOT Truth    | TRUTH:  Evictable / Can be Stale | TRUTH:  ONLY Auth. Knowledge Ret.| TRUTH:  SQLite=Canonical Truth   | TRUTH:  Parametric Truth         |
| PROFILE:Ultra-Low / Zero Cost    | PROFILE:Med Latency / Low Cost   | PROFILE:High Latency / High Cost | PROFILE:Variable / High Cost     | PROFILE:Variable / Med Cost      |
| FAILURE:Cache Misses/Stale Data  | FAILURE:False Positives          | FAILURE:Missing Intent Expansions| FAILURE:Infinite Loops / Failure | FAILURE:Hallucination / Outdated |
| CONTRCT:[1] CacheHit             | CONTRCT:[5] SemanticMatch        | CONTRCT:[13]RagQuery, [18]Cmp    | CONTRCT:[22]EnrichedManifest     | CONTRCT:[40] FallbackGen         |
|                                  |                                  |         [14]RagResult, [19]Supp  |         [25]ChangePackage, [30]  |                                  |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   |
| EVAL: Exact Call Number?         | EVAL: Familiar Request?          | EVAL: 🟠 fact_vec in FAISS DB?   | EVAL: External Action?           | EVAL: No External Matches?       |
| ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    |
| └─ [MISS] -> Trigger Layer 2 ───>| └─ [MISS] -> Trigger Layer 3 ───>| └─ [MISS] -> Trigger Layer 4 ───>| └─ [MISS] -> Trigger Layer 5 ───>| └─ [FAIL] -> System Exception    |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| INTERNAL MECHANICS:              | INTERNAL MECHANICS:              | INTERNAL MECHANICS:              | INTERNAL MECHANICS:              | INTERNAL MECHANICS:              |
| ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |
| │ 1. Redis SHA-256 Exact Match │ | │ 1. Cosine Sim > 0.95         │ | │ 1. Match: 🔵intent vs 🟠fact │ | │ 1. LangGraph Orchestration   │ | │ 1. System Prompt Inject      │ |
| └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | │  [PARALLEL 4a+4b: Concurrnt] │ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ |
|                ▼                 |                ▼                 | └──────────────┬───────────────┘ |                ▼                 |                ▼                 |
| ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |                ▼                 | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |
| │ 2. RAG Priming Phase:        │ | │ 2. GPTCache (via Redis)      │ | ┌──────────────────────────────┐ | │ 2. Tool Auth / Sandbox Bind  │ | │ 2. Token Embedding Matrix    │ |
| │  > Seed Pack Lookup          │ | │  > Fetch cached intent       │ | │ 2. Parent-Child Expansion    │ | └──────────────┬───────────────┘ | │  (vocab_size × hidden_dim)   │ |
| │  > Hydrate via KG (P1)       │ | │  > Skip RAG execution        │ | │  [ITERATIVE 4c: Recursive]   │ |                ▼                 | │  Maps to base shelf coords   │ |
| │  > Emit Intent + C0 (P4)     │ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | ┌──────────────────────────────┐ | └──────────────┬───────────────┘ |
| └──────────────┬───────────────┘ |                ▼                 |                ▼                 | │ 3. Exec Telemetry & Parse    │ |                ▼                 |
|                ▼                 | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | └──────────────┬───────────────┘ | ┌──────────────────────────────┐ |
| ┌──────────────────────────────┐ | │ 3. LRU Eviction Protocol     │ | │ 3. Score & Rerank (4d + 4e)  │ |                ▼                 | │ 3. Transformer Attention     │ |
| │ 3. TTL Validation Check      │ | └──────────────┬───────────────┘ | │  [COND 4d: Adapt Weights]    │ | ┌──────────────────────────────┐ | │  (Contextual Reading Room)   │ |
| └──────────────────────────────┘ |                ▼                 | └──────────────┬───────────────┘ | │ 4. Sync Canonical Store      │ | └──────────────┬───────────────┘ |
|                                  | ┌──────────────────────────────┐ |                ▼                 | └──────────────────────────────┘ |                ▼                 |
|                                  | │ 4. Zero-Token Return         │ | ┌──────────────────────────────┐ |                                  | ┌──────────────────────────────┐ |
|                                  | └──────────────────────────────┘ | │ 4. Assembly: High-Signal C0  │ |                                  | │ 4. Output Token Generation   │ |
|                                  |                                  | └──────────────────────────────┘ |                                  | └──────────────────────────────┘ |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
|                                  |                                  | 🛡️ RAG INTEGRITY HUB: SOVEREIGNTY INVARIANTS                        |                                  |
|                                  |                                  | (Write-once, content-hash indexed, NEVER authorizes execution.      |                                  |
|                                  |                                  | NO route_mode, safety_threshold, or execution_tier.)                |                                  |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
|                                  |                                  | [ L3: AGENTIC RAG (READS) ]      | [ L4/L6: TELEMETRY (WRITES) ]    |                                  |
|                                  |                                  |   ┌──────────────────────────┐   |   ┌──────────────────────────┐   |                                  |
|                                  |                                  |   │ 1. ChunkManifest (L4D)   │   |   │ 3. RetrievalEval (L4F)   │   |                                  |
|                                  |                                  |   ├──────────────────────────┤   |   ├──────────────────────────┤   |                                  |
|                                  |                                  |   │ DOM: Ingest/Substrate    │   |   │ DOM: Execution Quality   │   |                                  |
|                                  |                                  |   │ KEY: chunk_id(SHA-256)   │   |   │ KEY: trace_id/query_hash │   |                                  |
|                                  |                                  |   │ DAT: [22]EnrichedManifst │   |   │ DAT: [19]SuppAnswerCheck │   |                                  |
|                                  |                                  |   └──────────┬───────────────┘   |   └──────────┬───────────────┘   |                                  |
|                                  |                                  |              │                   |              │                   |                                  |
|                                  |                                  |   ┌──────────▼───────────────┐   |   ┌──────────▼───────────────┐   |                                  |
|                                  |                                  |   │ 2. ParentChildIdx (L4E)  │   |   │ 4. CompletnessSnap (L4G) │   |                                  |
|                                  |                                  |   ├──────────────────────────┤   |   ├──────────────────────────┤   |                                  |
|                                  |                                  |   │ DOM: Graph & Relatnships │   |   │ DOM: Ctx Health/Support  │   |                                  |
|                                  |                                  |   │ KEY: parent_id/child_id  │   |   │ KEY: trace_id/snap_hash  │   |                                  |
|                                  |                                  |   │ DAT: ADG Edges           │   |   │ DAT: [18] ContextComp    │   |                                  |
|                                  |                                  |   └──────────────────────────┘   |   └──────────────────────────┘   |                                  |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+

===========================================================================================================================================================================================
🔄 PIPELINE D: META-LEARNING FEEDBACK LOOP (OFFLINE POST-RUNTIME DECISION TREE)
===========================================================================================================================================================================================
[ L4/L6 TELEMETRY ] -> [ EVALUATION RUNNERS (Shadow/Replay: Prec@K, Recall@K, MRR, NDCG, F1-Groundedness) ] -> Emits [ EvaluationSignals ] -> [ CompletenessRAGProposer ]