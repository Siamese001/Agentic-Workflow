# UNIFIED ARCHITECTURAL SPEC: AGENTIC RETRIEVAL & RAG PIPELINES (v14 - RAG HUB ALIGNMENT)

+=========================================================================================================================================================================================+
|                                                                ⚙️ SYSTEM ARCHITECTURE & MACRO TOPOLOGY: THE FOUR PIPELINES                                                              |
+=========================================================================================================================================================================================+
| PIPELINE & LIBRARY ANALOGY          | EXECUTION STATE | PATH AUTHORITY  | CORE OPERATIONAL FLOW                       | CHUNK | EMBED | READ | WRITE | PURPOSE & KEY OUTPUT             |
+-------------------------------------+-----------------+-----------------+---------------------------------------------+-------+-------+------+-------+----------------------------------+
| 🏗️ A: MODEL TRAINING                | Offline         | N/A             | Public Corpora -> Train -> Model Weights    |  NO   |  NO   |  NO  |  NO   | Defines base reasoning.          |
|   (Teaching librarian foundational) | (Pre-runtime)   | (Parametric)    |                                             |       |       |      |       | Output: Static LLM Weights.      |
+-------------------------------------+-----------------+-----------------+---------------------------------------------+-------+-------+------+-------+----------------------------------+
| 📥 B: INGESTION & INDEXING          | Offline         | WRITE PATH      | Raw Docs -> Clean -> Chunk -> Enrich        |  YES  |  YES  |  NO  |  YES  | Defines what the system knows.   |
|   (Adding new books to shelves)     | (Batch/One-time)| (Adds memory)   | -> Embed -> Store in Vector DB              |       |       |      |       | Output: Indexed chunks/vectors.  |
+-------------------------------------+-----------------+-----------------+---------------------------------------------+-------+-------+------+-------+----------------------------------+
| 🚀 C: INFERENCE / RUNTIME           | Real-time       | READ PATH       | User Query -> Embed -> Retrieve ->          |  NO   |  YES  | YES  |  NO   | Defines how the system answers.  |
|   (Answering questions using books) | (Per query)     | (Zero write)    | Agentic RAG -> Generate Answer              |       | (Qry) |      |       | Output: Answer + context.        |
+-------------------------------------+-----------------+-----------------+---------------------------------------------+-------+-------+------+-------+----------------------------------+
| 🔄 D: LEARNING & GROWTH             | Asynchronous    | WRITE PATH      | Telemetry/Failures -> Extract -> Chunk      |  YES  |  YES  | YES  |  YES  | Defines how the system improves. |
|   (Writing new books based on exp.) | (Post-runtime)  | (Adds memory)   | -> Embed -> Store in Vector DB              |       |       |      |       | Output: Evolved index/patterns.  |
+=========================================================================================================================================================================================+

+=========================================================================================================================================================================================+
|                                                                📥 PIPELINE B: INGESTION & INDEX BUILD (OFFLINE PRE-RUNTIME)                                                             |
+=========================================================================================================================================================================================+
| [ RAW SOURCES ] -> PDFs, Docs, DBs, SharePoint, Web Fetch, L4 Execution Telemetry, L2 Incident Traces                                                                                   |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 1. DATA PREP ] ----> Document Load / Trace Parse -> Text Extract -> Clean & Normalize                                                                                                 |
|       |                                                                                                                                                                                 |
|       v                                                                                                                                                                                 |
| [ 2. CHUNKING ] -----> Split into base text units (paragraph-level, sliding window, execution events) -> Generate Base ChunkManifest (L4D)                                              |
|       |                MODES: FixedToken, OverlapWindow, SectionAware, Semantic Object                                                                                                  |
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
|       |                | ⚙️ EMBEDDING EXECUTION FLOW (RUNTIME INSTANTIATION)                                                                                |                           |
|       |                | 1. IDENTIFIER:  [BAAI/bge-m3]                                   [ HUGGING FACE HUB ]                                               |                           |
|       |                |                       │                                                  │                                                         |                           |
|       |                |                       ▼                                                  │                                                         |                           |
|       |                | 2. NETWORK I/O: (Download weights & config) <────────────────────────────┘                                                         |                           |
|       |                |                       │                                                                                                            |                           |
|       |                |                       ▼                                                                                                            |                           |
|       |                | 3. RAM ALLOC:   [MODEL ARCHITECTURE + WEIGHTS LOADED IN MEMORY]                                                                    |                           |
|       |                |                       │                                                                                                            |                           |
|       |                |                       ▼                                                                                                            |                           |
|       |                | 4. EXECUTION:   .encode(enriched_structured_payload) <--- (Shift from text similarity to concept similarity)                       |                           |
|       |                |                       │                                                                                                            |                           |
|       |                |                       ▼                                                                                                            |                           |
|       |                | 5. OUTPUT:      [ 🟠 ENRICHED FACT VECTOR (fact_vec) ] <--- (Permanent concept vector; stored in Vector DB)                        |                           |
|       |                |                 🏛️ ANALOGY: The Dewey Decimal "Concept Coordinate" (🟠 fact_vec) stamped permanently on a new book's spine.        |                           |
|       |                +------------------------------------------------------------------------------------------------------------------------------------+                           |
|       +------------------------------------+------------------------------------+                                                                                                       |
|       |                                    |                                    |                                                                                                       |
|       v                                    v                                    v                                                                                                       |
|  🗄️ [ VECTOR DB ]                    🗃️ [ METADATA DB ]                   📦 [ CANONICAL STORE ]                                                                                        |
|  Durable knowledge store             (L4 SQLite) Canonical Truth          Stores original files & telemetry (Blob/S3/Postgres)                                                          |
|  Stores 🟠 fact_vecs (documents)     Stores entity relations / ADG        (ChunkManifestRegistry L4D)                                                                                   |
|  (FAISS/Chroma - Concept Clustered)  (ParentChildRegistry L4E)            ADG CACHE: 8,234 Nodes, 225k Edges                                                                            |
|                                      TOPOLOGY: retrieves_via(52), pulls_context(32), scores_groundedness(40), generates_prompt(215)                                                     |
+=========================================================================================================================================================================================+

===========================================================================================================================================================================================
🚀 PIPELINE C: INFERENCE / QUERY TIME (INTEGRATED CASCADING AGENT) - NO CHUNKING
===========================================================================================================================================================================================
[ START: INBOUND USER QUERY / TASK ]
          |
          v
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 🔍 QUERY PRE-PROCESSING (SHARED)                                                                                                                                                        |
| EMBEDDING CONSISTENCY RULE: Query embedding model MUST exactly match indexing model (e.g., bge-m3). Model change requires full re-indexing.                                             |
| 🏛️ ANALOGY: If the Library was cataloged in French (bge-m3), the Patron's slip MUST be translated into French. Otherwise, the coordinates mean nothing.                               |
|                                                                                                                                                                                         |
| ⚙️ EMBEDDING EXECUTION FLOW (API-DRIVEN INFERENCE)                                                                                                                                      |
| 1. INPUT:       [RAW USER QUERY]                                                                                                                                                        |
|                       │                                                                                                                                                                 |
|                       ▼                                                                                                                                                                 |
| 2. NORMALIZE:   (Strip conversational noise / tokenize string)                                                                                                                          |
|                       │                                                                                                                                                                 |
|                       ▼                                                  [ EXTERNAL INFERENCE API ]                                                                                     |
| 3. NETWORK I/O: (Transmit lightweight text payload) ─────────────────────> (Weights pre-loaded in VRAM)                                                                                 |
|                       │                                                  │                                                                                                              |
|                       ▼                                                  │                                                                                                              |
| 4. EXECUTION:   .encode(normalized_query) <──────────────────────────────┘                                                                                                              |
|                       │                            (Generates pure intent representation)                                                                                               |
|                       ▼                                                                                                                                                                 |
| 5. OUTPUT:      [ 🔵 EPHEMERAL INTENT VECTOR (intent_vec) ] <--- (Bundled with raw_text into Dual-Rail Payload)                                                                         |
|                 🏛️ ANALOGY: A temporary "Seeker Coordinate" (🔵 intent_vec) acting as a homing beacon to measure the physical distance to nearby books.                                 |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
                                                                |
================================================================( L1 ADVISORY -> L0 AUTHORITY BOUNDARY )===================================================================================
| 🧑‍🏫 [ L1: SENIOR RESEARCH LIBRARIAN (ADVISORY) ]                                                                                                                                         |
| ROLE:   Calculates vector similarity and searches exact hashes against the query payload. L1 = advisory only. Runs BEFORE embedding.                                                    |
| OUTPUT: Proposes match signals (e.g., "Exact Hash Found" or "Vector Similarity: 0.98").                                                                                                 |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
                                                                | (Handoff)
                                                                v
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 🚦 [ L0: FRONT DESK DISPATCHER (AUTHORITY) ]                                                                                                                                            |
| ROLE:   Retains final routing authority based on L1 advice, operational budget, metadata & cluster stats. L0 = decision maker. Retrieval never decides execution.                       |
| OUTPUT: Places signals onto the Dual-Rail Bus and triggers the correct execution layer.                                                                                                 |
===========================================================================================================================================================================================
                                                      [ DUAL-RAIL SIGNAL ROUTING BUS ]
[RAW_TEXT]  ───────┬──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┐
                   │                                  │                                  │                                  │                                  │
[🔵 intent] ───────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
                   │                                  │                                  │                                  │                                  │
                   ▼ (Text)                           ▼ (🔵intent)                       ▼ (🔵intent vs 🟠fact)             ▼ (Text)                           ▼ (Text)
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| ⚡ 1. LAYER 1: EXACT CACHE       | 🧠 2. LAYER 2: SEMANTIC CACHE    | 📚 3. LAYER 3: AGENTIC RAG (C0)| 🛠️ 4. LAYER 4: AGENTIC ACTION    | 🔮 5. LAYER 5: LLM FALLBACK      |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| 🏛️ ANALOGY: Skip vector math;    | 🏛️ ANALOGY: Compare new slip     | 🏛️ ANALOGY: Walk slip (🔵intent)| 🏛️ ANALOGY: Escalate to an       | 🏛️ ANALOGY: Answer directly      |
| lookup exact text call number.   | (🔵intent) vs old slips (🔵intent)| to stacks to find books (🟠fact)| active specialist (Text only).   | from head memory (Text only).    |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| SIGNAL: Hash(raw_text)           | SIGNAL: 🔵intent vs 🔵intent     | SIGNAL: 🔵 intent vs 🟠 fact     | SIGNAL: [raw_text + schemas]     | SIGNAL: raw_text (No vector)     |
| EMBED:  NO embeddings used       | EMBED:  Required                 | EMBED:  Required                 | EMBED:  Bypassed                 | EMBED:  Bypassed                 |
| INFRA:  Redis (RAM-first cache)  | INFRA:  Redis (RAM-first cache)  | INFRA:  Vector DB (FAISS/Chroma) | INFRA:  Local Process Heap       | INFRA:  Token Matrix Weights     |
| STORE:  key=SHA256, val=response | STORE:  [🔵intent_vec] (queries) | STORE:  [🟠fact_vec] (documents) | STORE:  App Memory (Exec state)  | STORE:  Static Parametric Mem    |
| TRUTH:  Ephemeral / NOT Truth    | TRUTH:  Evictable / Can be Stale | TRUTH:  ONLY Auth. Knowledge Ret.| TRUTH:  SQLite=Canonical Truth   | TRUTH:  Parametric Truth         |
| SPEED:  Faster=Less Authoritative| SPEED:  Faster=Less Authoritative| SPEED:  Slower=More Authoritative| SPEED:  Variable Execution Pacing| SPEED:  Variable Generation Pace |
| BUDGET: Zero Token               | BUDGET: Low Token                | BUDGET: High Token               | BUDGET: Max Token                | BUDGET: Med/High Token           |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   |
| EVAL: Exact Call Number?         | EVAL: Familiar Request?          | EVAL: 🟠 fact_vec in Vector DB?  | EVAL: External Action?           | EVAL: No External Matches?       |
| ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    |
| └─ [MISS] -> Trigger Layer 2 ───>| └─ [MISS] -> Trigger Layer 3 ───>| └─ [MISS] -> Trigger Layer 4 ───>| └─ [MISS] -> Trigger Layer 5 ───>| └─ [FAIL] -> System Exception    |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| INTERNAL MECHANICS:              | INTERNAL MECHANICS:              | INTERNAL MECHANICS:              | INTERNAL MECHANICS:              | INTERNAL MECHANICS:              |
| ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |
| │ 1. SHA-256 / Exact Match     │ | │ 1. Cosine Sim > 0.95         │ | │ 1. Match: 🔵intent vs 🟠fact │ | │ 1. LangGraph Orchestration   │ | │ 1. System Prompt Inject      │ |
| └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | │  [PARALLEL 4a+4b: Concurrnt] │ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ |
|                ▼                 |                ▼                 | └──────────────┬───────────────┘ |                ▼                 |                ▼                 |
| ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |                ▼                 | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |
| │ 2. RAG Priming Phase:        │ | │ 2. GPTCache Lookup           │ | ┌──────────────────────────────┐ | │ 2. Tool Auth / Sandbox Bind  │ | │ 2. Token Matrix Eval         │ |
| │  > Seed Pack Lookup          │ | │  > Fetch cached intent       │ | │ 2. Parent-Child Expansion    │ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ |
| │  > Hydrate via KG (P1)       │ | │  > Skip RAG execution        │ | │  [ITERATIVE 4c: Recursive]   │ |                ▼                 |                ▼                 |
| │  > Emit Intent + C0 (P4)     │ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |
| └──────────────┬───────────────┘ |                ▼                 |                ▼                 | │ 3. Exec Telemetry & Parse    │ | │ 3. Next-Token Predict        │ |
|                ▼                 | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ |
| ┌──────────────────────────────┐ | │ 3. LRU Eviction Protocol     │ | │ 3. Score & Rerank (4d + 4e)  │ |                ▼                 |                ▼                 |
| │ 3. TTL Validation Check      │ | └──────────────┬───────────────┘ | │  [COND 4d: Adapt Weights]    │ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |
| └──────────────────────────────┘ |                ▼                 | └──────────────┬───────────────┘ | │ 4. Sync Canonical Store      │ | │ 4. Unrestricted Generation   │ |
|                                  | ┌──────────────────────────────┐ |                ▼                 | └──────────────────────────────┘ | └──────────────────────────────┘ |
|                                  | │ 4. Zero-Token Return         │ | ┌──────────────────────────────┐ |                                  |                                  |
|                                  | └──────────────────────────────┘ | │ 4. Assembly: High-Signal C0  │ |                                  |                                  |
|                                  |                                  | │    (Includes exec notes)     │ |                                  |                                  |
|                                  |                                  | └──────────────────────────────┘ |                                  |                                  |
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
|                                  |                                  |   │ MEC: Payload integrity,  │   |   │ MEC: Log Prec/Recall/MRR │   |                                  |
|                                  |                                  |   │      Map struct to head, │   |   │      Store NDCG, F1(Grd) │   |                                  |
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
|                                  |                                  |   │      Define depth(1-5),  │   |   │      Feed CmpRAGProposer │   |                                  |
|                                  |                                  |   │      Feed CmpRAGProposer │   |   │      Feed CmpRAGProposer │   |                                  |
|                                  |                                  |   └──────────────────────────┘   |   └──────────────────────────┘   |                                  |
+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+

===========================================================================================================================================================================================
🗄️ STORAGE SEPARATION & MEMORY MODEL
===========================================================================================================================================================================================
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 💾 MEMORY HIERARCHY & TRUTH: (Faster = less authoritative | Slower = more authoritative)                                                                                                |
|                                                                                                                                                                                         |
| 1. App Memory: Local process heap (execution state).                                                                                                                                    |
| 2. Redis:      Shared in-memory cache (RAM-first). Ephemeral, can be stale. Data can be evicted/recomputed. NOT source of truth.                                                        |
| 3. Vector DB:  Durable knowledge store (FAISS/Chroma). Stores 🟠 fact_vecs (documents).                                                                                                 |
| 4. SQLite:     (L4) Canonical source of truth.                                                                                                                                          |
|                                                                                                                                                                                         |
| 🔄 CACHE FLOW & AUTHORITY:                                                                                                                                                              |
| - L1 → exact match (NO embeddings). Redis key-value only: key = SHA256(query), value = response.                                                                                        |
| - L2 → semantic match (🔵 intent vs 🔵 intent). Stored in Redis.                                                                                                                        |
| - L3 → RAG (🔵 intent vs 🟠 fact). **Only L3 is authoritative knowledge retrieval.** |
|                                                                                                                                                                                         |
| 🧩 VECTOR SEPARATION:                                                                                                                                                                   |
| - 🔵 intent_vec (queries)   → Redis only (cache, ephemeral)                                                                                                                             |
| - 🟠 fact_vec (documents)   → Vector DB only (FAISS/Chroma, durable)                                                                                                                    |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

===========================================================================================================================================================================================
🔄 PIPELINE D: META-LEARNING FEEDBACK LOOP (OFFLINE POST-RUNTIME DECISION TREE)
===========================================================================================================================================================================================
[ L4/L6 TELEMETRY ] -> [ EVALUATION RUNNERS (Shadow/Replay: Prec@K, Recall@K, MRR, NDCG, F1-Groundedness) ] -> Emits [ EvaluationSignals ] -> [ CompletenessRAGProposer ]

===========================================================================================================================================================================================
📊 DETAILED OPERATIONAL, DATA CONTRACT & FAILURE MODE MATRIX
===========================================================================================================================================================================================
FEATURE                   | 1. L1: EXACT CACHE        | 2. L2: SEMANTIC CACHE     | 3. L3: AGENTIC RAG (C0)   | 4. L4: AGENTIC ACTION     | 5. L5: LLM FALLBACK
--------------------------|---------------------------|---------------------------|---------------------------|---------------------------|------------------------------------------------
EMBEDDING DEPENDENCY      | NO embeddings used        | Strict / Brittle          | Strict / Concept-Driven   | None (Relies on APIs)     | None (Token Matrix internal)
MATCHING LOGIC            | Exact Match / O(1) Hash   | Embed Similarity (>0.95)  | Concept Similarity(Top-K) | Dynamic Tool Selection    | Next-Token Prediction
DATA PAYLOAD              | Strings, hashes, JSON     | 🔵 intent vs 🔵 intent      | 🔵 intent vs 🟠 fact        | API requests, JSON, code  | System Prompt vs Weights
LATENCY & COST PROFILE    | Ultra-Low / Zero Cost     | Medium Latency / Low Cost | High Latency / High Cost  | Variable / High Cost      | Variable / Medium Cost
PRIMARY FAILURE MODE      | Cache Misses & Stale Data | False Positives           | Missing Intent Expansions | Infinite Loops / Failure  | Hallucination / Outdated Memory
DATA CONTRACTS            | [1] CacheHit              | [5] SemanticMatch         | [13] RagQuery, [18] Cmp   | [22] EnrichedManifest     | [40] FallbackGen
                          |                           |                           | [14] RagResult, [19] Supp | [25] ChangePackage, [30]  | 
===========================================================================================================================================================================================