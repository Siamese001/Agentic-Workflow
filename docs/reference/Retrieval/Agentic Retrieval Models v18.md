# UNIFIED ARCHITECTURAL SPEC: AGENTIC RETRIEVAL & RAG PIPELINES (v16.19 - GRAPHRAG EXPANSION & VECTOR AGNOSTIC)

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
|       +------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------+
|       |                                    |                                                                                                                                            |
|       v                                    v                                                                                                                                            |
|  🗄️ [ MASTER ARCHIVE (VECTOR DB) ]   🗃️ [ L4 METADATA & CANONICAL STORE: THE KNOWLEDGE SUBSTRATE (GRAPH) ]                                                                            |
|  Durable Math Store (Vector Search)  Relational Truth (SQLite/Postgres: Canonical Data, ADG Edges, & Telemetry)                                                                         |
|  Stores ONLY [UUID : 🟠 fact_vec]      ┌────────────────────────────┐ ┌────────────────────────────┐                                                                                      |
|  (Requires Hydration from L4 Store)  │ 1. ChunkManifest (L4D)     │ │ 2. ParentChildIdx (L4E)    │                                                                                      |
|                                      ├────────────────────────────┤ ├────────────────────────────┤                                                                                      |
|                                      │ Catl: Master chunk library │ │ Catl: GraphRAG routing map │                                                                                      |
|                                      │ Look: SHA-256 Text Hash    │ │ Look: Parent & Child IDs   │                                                                                      |
|                                      │ Data: Enriched JSON Schema │ │ Data: Context graph edges  │                                                                                      |
|                                      └────────────────────────────┘ └────────────────────────────┘                                                                                      |
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
| OUTPUT: Evaluates and routes the pre-processed Dual-Rail payload: { TEXT: raw_query, INTENT: 🔵 intent_vec }.                                                                           |
===========================================================================================================================================================================================
                                                           [ L0 DUAL-RAIL SIGNAL ROUTING BUS & MEMORY INVARIANTS ]
[RAW_TEXT] ──┬──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┐
           │                                  │                                  │                                  │                                  │
[🔵 intent] ─┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
           │                                  │                                  │                                  │                                  │
           ▼ (Text)                           ▼ (🔵intent)                       ▼ (🔵intent vs 🟠fact)             ▼ (Text)                           ▼ (Text)
+==========+==================================+==================================+==================================+==================================+==================================+
| EXEC TIER| 🟥 1. LAYER 1: EXACT CACHE       | 🧠 2. LAYER 2: SEMANTIC CACHE    | 📚 3. LAYER 3: AGENTIC RAG (C0)  | 🛠️ 4. LAYER 4: AGENTIC ACTION    | 🔮 5. LAYER 5: LLM FALLBACK      |
+==========+==================================+==================================+==================================+==================================+==================================+
| ANALOGY  | Skip vector math;                | Compare new slip                 | Walk slip (🔵intent)             | Escalate to an                   | Answer directly                  |
|          | lookup exact text call number.   | (🔵intent) vs old (🔵intent)       | to Master Archive to find book   | active specialist (Text only).   | from internal reading matrix.    |
+==========+==================================+==================================+==================================+==================================+==================================+
| 🎯 CORE EXECUTION INVARIANTS (HIGH SIGNAL)                                                                                                                                              |
+==========+==================================+==================================+==================================+==================================+==================================+
| EMBED    | NO embeddings used               | Required (External BGE)          | Required (External BGE)          | Bypassed                         | Internal Matrix Used             |
| LOGIC    | Exact Match / O(1) Hash          | Embed Sim (>0.95)                | Concept Sim (Top-K)              | Dynamic Tool Selection           | Next-Token Prediction            |
| INFRA    | Redis (RAM-first cache)          | GPTCache backed by Redis         | Vector DB / Master Archive       | Local Process Heap               | Token Embedding Matrix           |
| STORE    | key=SHA256, val=response         | [🔵intent_vec] (queries)         | [🟠fact_vec] (documents)         | App Memory (Exec state)          | Static Parametric Mem            |
| VECTORS  | NO vectors stored                | NEVER reads Vector DB            | NEVER writes to Redis            | NO vectors processed             | Internal mapped coords           |
+==========+==================================+==================================+==================================+==================================+==================================+
| 📉 SECONDARY METADATA (LOWER SIGNAL)                                                                                                                                                    |
+----------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+----------------------------------+
| SIGNAL   | Hash(raw_text)                   | 🔵intent vs 🔵intent             | 🔵 intent vs 🟠 fact             | [raw_text + schemas]             | raw_text (No vector)             |
| PAYLOAD  | Strings, hashes, JSON            | 🔵 intent vs 🔵 intent           | 🔵 intent vs 🟠 fact             | API reqs, JSON, code             | Sys Prompt vs Weights            |
| TRUTH    | Ephemeral / NOT Truth            | Evictable / Can be Stale         | ONLY Auth. Knowledge Ret.        | SQLite=Canonical Truth           | Parametric Truth                 |
| PROFILE  | Ultra-Low / Zero Cost            | Med Latency / Low Cost           | High Latency / High Cost         | Variable / High Cost             | Variable / Med Cost              |
| FAILURE  | Cache Misses/Stale Data          | False Positives                  | Missing Intent Expansions        | Infinite Loops / Failure         | Hallucination / Outdated         |
| CONTRCT  | [1] CacheHit                     | [5] SemanticMatch                | [13]RagQuery, [18]Cmp            | [22]EnrichedManifest             | [40] FallbackGen                 |
|          |                                  |                                  | [14]RagResult, [19]Supp          | [25]ChangePackage, [30]          |                                  |
+==========+==================================+==================================+==================================+==================================+==================================+
| CONTROL  | [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   | [ L0 DISPATCHER CONTROL FLOW ]   |
| FLOW     | EVAL: Exact Call Number?         | EVAL: Familiar Request?          | EVAL: 🟠 fact_vec in Vector DB?  | EVAL: External Action?           | EVAL: No External Matches?       |
|          | ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    | ├─ [HIT]  -> Execute & Return    |
|          | └─ [MISS] -> Trigger Layer 2 ───>| └─ [MISS] -> Trigger Layer 3 ───>| └─ [MISS] -> Trigger Layer 4 ───>| └─ [MISS] -> Trigger Layer 5 ───>| └─ [FAIL] -> System Exception    |
+==========+==================================+==================================+==================================+==================================+==================================+
| INTERNAL | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |
| SEQUENCE | │ 1. [🟥 Redis] SHA-256 Exact  │ | │ 1. [🧠 BGE-M3] Ext API Call  │ | │ 1. [📚 Vector] Entry Node    │ | │ 1. [🛠️ Heap] LangGraph Orch.│ | │ 1. [🛠️ Heap] Prompt Inject  │ |
|          | │  ├─ Hash raw input string    │ | │  ├─ Pass discrete tokens     │ | │  ├─ Semantic Vector Search   │ | │  ├─ Parse routing payload    │ | │  ├─ Load L5 persona rules    │ |
|          | │  ├─ Query O(1) exact dict    │ | │  ├─ Exec pooling/projection  │ | │  ├─ BM25 Keyword Search      │ | │  ├─ Determine req actions    │ | │  ├─ Bind raw_text input      │ |
|          | │  └─ Yield cached response    │ | │  └─ Yield 🔵 intent_vec      │ | │  └─ Yield Entry Chunk UUIDs  │ | │  └─ Init execution state     │ | │  └─ Setup converse history   │ |
|          | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ |
|          |                ▼                 |                ▼                 |                ▼                 |                ▼                 |                ▼                 |
|          | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |
|          | │ 2. [🟥 Redis] Auth & TTL     │ | │ 2. [🧠 GPTCache] Similarity  │ | │ 2. [🗃️ SQLite] GraphRAG Exp │ | │ 2. [🛠️ Heap] Auth/Sandbox   │ | │ 2. [🔮 Matrix] Embed Node   │ |
|          | │  ├─ Verify payload signature │ | │  ├─ Compare 🔵 vs cached 🔵  │ | │  ├─ Map UUID to Parent Node  │ | │  ├─ Check L5 policy rules    │ | │  ├─ vocab_size x hidden_dim  │ |
|          | │  ├─ Check staleness limits   │ | │  ├─ Cosine Sim > 0.95 thresh │ | │  ├─ Traverse Sibling Edges   │ | │  ├─ Mount isolated env       │ | │  ├─ Read token input array   │ |
|          | │  └─ Verify user clearance    │ | │  └─ Yield match cached UUID  │ | │  └─ Hydrate Multi-Hop Graph  │ | │  └─ Inject secure API keys   │ | │  └─ Map to base shelf coords │ |
|          | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ |
|          |                ▼                 |                ▼                 |                ▼                 |                ▼                 |                ▼                 |
|          | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |
|          | │ 3. [🟥 Redis] Hydrate Output │ | │ 3. [🟥 Redis] LRU Eviction   │ | │ 3. [🛠️ Heap] Score Subgraph │ | │ 3. [🛠️ Heap] Exec Telemetry │ | │ 3. [🔮 Matrix] Attention    │ |
|          | │  ├─ Extract cached string    │ | │  ├─ Update access timestamps │ | │  ├─ Cross-Encoder Node Rank  │ | │  ├─ Run python/API sub-steps │ | │  ├─ Multi-head self-attent.  │ |
|          | │  ├─ Format JSON output schema│ | │  ├─ Evict stale nodes        │ | │  ├─ Prune Low-Signal Nodes   │ | │  ├─ Evaluate return codes    │ | │  ├─ Feed-forward network pass│ |
|          | │  └─ Bypass all LLM steps     │ | │  └─ Confirm data freshness   │ | │  └─ MMR Diversity Filter     │ | │  └─ Capture stdout/stderr    │ | │  └─ Parametric synthesis     │ |
|          | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ |
|          |                ▼                 |                ▼                 |                ▼                 |                ▼                 |                ▼                 |
|          | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |
|          | │ 4. [🛠️ Heap] Zero-Token Ret. │ | │ 4. [🛠️ Heap] Low-Token Ret.  │ | │ 4. [🗃️ SQLite] C0 Handoff   │ | │ 4. [🗃️ SQLite] State Handoff│ | │ 4. [🔮 Matrix] Prompt Init  │ |
|          | │  ├─ Route direct to output   │ | │  ├─ Fetch text from Redis    │ | │  ├─ Sequence graph to text   │ | │  ├─ Write L4 SQLite records  │ | │  ├─ Init parametric context  │ |
|          | │  ├─ Emit L4 audit log event  │ | │  ├─ Append semantic metadata │ | │  ├─ Trim token budget window │ | │  ├─ Compile stdout payload   │ | │  ├─ Apply safety guardrails  │ |
|          | │  └─ Close execution thread   │ | │  └─ Route direct to output   │ | │  └─ Yield C0 to Reading Room │ | │  └─ Yield data to Reading Rm │ | │  └─ Yield to Reading Room    │ |
|          | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ | └──────────────┬───────────────┘ |
|          |                ▼                 |                ▼                 |                ▼                 |                ▼                 |                ▼                 |
|          | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌──────────────────────────────┐ |
|          | │ 5. [⚡ Fast] Terminal Exit   │ | │ 5. [⚡ Fast] Terminal Exit   │ | │ 5. [🧠 Matrix] Read C0 Graph│ | │ 5. [🧠 Matrix] Read L4 State│ | │ 5. [🧠 Matrix] Read L5 Input│ |
|          | │  ├─ Bypass downstream LLM    │ | │  ├─ Bypass downstream LLM    │ | │  ├─ CoT: Analyze Relations   │ | │  ├─ CoT: Evaluate tool output│ | │  ├─ CoT: Plan 0-shot answer  │ |
|          | │  ├─ No matrix math required  │ | │  ├─ No matrix math required  │ | │  ├─ ToT: Branch Hypotheses   │ | │  ├─ Reflexion: Check errors  │ | │  ├─ SC: Verify logical flow  │ |
|          | │  └─ Zero Generation Cost     │ | │  └─ Zero Generation Cost     │ | │  └─ Autoregressive Generate  │ | │  └─ Autoregressive Generate  │ | │  └─ Autoregressive Generate  │ |
|          | └──────────────────────────────┘ | └──────────────────────────────┘ | └──────────────────────────────┘ | └──────────────────────────────┘ | └──────────────────────────────┘ |
+==========+==================================+==================================+========================================================================================================+
| DOWNSTRM | ⏩ TERMINAL PATH                 | ⏩ TERMINAL PATH                 | 🧠 DOWNSTREAM TRANSFORMER MODEL (THE READING ROOM)                                                     |
| REASONING| (Bypasses generation entirely)   | (Bypasses generation entirely)   | (Autoregressive Generation, Chain of Thought, Tree of Thoughts, Self-Consistency, Reflexion)           |
+----------+----------------------------------+----------------------------------+--------------------------------------------------------------------------------------------------------+
| COGNITIVE| ┌──────────────────────────────┐ | ┌──────────────────────────────┐ | ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐ |
| SYNTHESIS| │ Return exactly as cached.    │ | │ Return text from semantic    │ | │ 1. [Ingest Payload] Merge C0 Context (L3), Tool State (L4), or Raw Prompt (L5) into input window │ |
|          | │ Zero LLM inference cost.     │ | │ vector match. No generation. │ | │ 2. [Cognitive Plan] Apply ToT branching, CoT reasoning paths, or Reflexion critique loops        │ |
|          | └──────────────────────────────┘ | └──────────────────────────────┘ | │ 3. [Attention Math] Query/Key/Value calculations against internal Token Embedding Matrix           │ |
|          |                                  |                                  | │ 4. [Generation Out] Sample & stream final output tokens deterministically based on synthesis       │ |
|          |                                  |                                  | └────────────────────────────────────────────────────────────────────────────────────────────────────┘ |
+==========+==================================+==================================+========================================================================================================+

===========================================================================================================================================================================================
🔄 PIPELINE D: META-LEARNING FEEDBACK LOOP & RAG INTEGRITY HUB (OFFLINE POST-RUNTIME)
===========================================================================================================================================================================================
🛡️ SOVEREIGNTY INVARIANTS: L4/L6 Telemetry is write-once, content-hash indexed, and NEVER authorizes execution. NO route_mode or safety_thresholds.

[ L4/L6 EXECUTION TELEMETRY: THE AUDIT TRAIL ] (Generated during Pipeline C Inference, Consumed here)
  │
  ├─> ┌────────────────────────────┐   ┌────────────────────────────┐
  │   │ 3. RetrievalEval (L4F)     │   │ 4. CompletnessSnap (L4G)   │
  │   ├────────────────────────────┤   ├────────────────────────────┤
  │   │ Eval: Search grader (MRR)  │   │ Eval: Final answer grader  │
  │   │ Look: Qry Hash + Trace ID  │   │ Look: Context window hash  │
  │   │ Data: Prec/Recall metrics  │   │ Data: Health/support score │
  │   └─────────────┬──────────────┘   └─────────────┬──────────────┘
  │                 │                                │
  ▼                 ▼                                ▼
[ EVALUATION RUNNERS (Shadow/Replay: Prec@K, Recall@K, MRR, NDCG, F1-Groundedness) ] ──> Emits [ EvaluationSignals ] ──> [ CompletenessRAGProposer ]