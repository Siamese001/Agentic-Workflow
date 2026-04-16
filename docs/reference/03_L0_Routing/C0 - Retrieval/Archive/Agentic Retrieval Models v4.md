# UNIFIED ARCHITECTURAL SPEC: AGENTIC RETRIEVAL & RAG PIPELINES

+======================================================================================================================================================+
|                                  SYSTEM ARCHITECTURE & MACRO TOPOLOGY: THE THREE PIPELINES                                                           |
+======================================================================================================================================================+
| [ PIPELINE A: MODEL TRAINING ]       Public/licensed corpora -> model training -> model weights (No vector DB population)                            |
| [ PIPELINE B: INGESTION / INDEXING ] External documents -> chunk -> embed -> vector DB (Builds retrieval substrate)                                  |
| [ PIPELINE C: INFERENCE / RUNTIME ]  User query -> exact cache -> semantic cache -> RAG -> agentic action (Consumes stores; never creates chunks)    |
+======================================================================================================================================================+

+======================================================================================================================================================+
|                                        PIPELINE B: INGESTION & INDEX BUILD (OFFLINE PRE-RUNTIME)                                                     |
+======================================================================================================================================================+
| [ RAW SOURCES ] -> PDFs, Docs, DBs, SharePoint, Web Fetch                                                                                            |
|       |                                                                                                                                              |
|       v                                                                                                                                              |
| [ 1. DATA PREP ] ----> Document Load -> Text Extract -> Clean & Normalize                                                                            |
|       |                                                                                                                                              |
|       v                                                                                                                                              |
| [ 2. CHUNKING ] -----> Split into semantic units (e.g., paragraph-level, sliding window)                                                             |
|       |                                                                                                                                              |
|       v                                                                                                                                              |
| [ 3. METADATA ] -----> Bind doc_id, page, source, security labels, timestamps                                                                        |
|       |                                                                                                                                              |
|       v                                                                                                                                              |
| [ 4. EMBEDDING ] ----> Convert chunk → tokens → vector array (e.g., [0.21, -0.33, 0.77...])                                                          |
|       |                                                                                                                                              |
|       +------------------------------------+------------------------------------+                                                                    |
|       |                                    |                                    |                                                                    |
|       v                                    v                                    |                                                                    |
| [ VECTOR DB ]                        [ METADATA DB ]                      [ CANONICAL STORE ]                                                        |
| Stores vectors + chunk text          Stores entity relations              Stores original files (Blob/S3/Postgres)                                   |
|                                                                                                                                                      |
| THE HARD RULE: No ingestion -> no chunks -> empty vector DB -> no RAG retrieval possible.                                                            |
+======================================================================================================================================================+



========================================================================================================================================================
PIPELINE C: INFERENCE / QUERY TIME (INTEGRATED CASCADING AGENT)
========================================================================================================================================================
PIPELINE SEPARATION (CORE TRUTH): Ingestion (Pipeline B) creates chunks and embeddings. Inference (Pipeline C) NEVER creates chunks; it only searches existing ones.

[ START: INBOUND USER QUERY ]
          |
          v
+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| QUERY PRE-PROCESSING (SHARED)                                                                                                                                 |
| Action: Normalize Query (Case folding, punctuation) -> Tokenize -> Embed via API (Generate q_vector)                                                          |
| EMBEDDING CONSISTENCY RULE: Query embedding model MUST exactly match indexing model. Changing the model requires re-embedding the entire corpus.              |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
          |
          v
                                  LAYER CLASSIFICATION                                  STORAGE & DURABILITY                  AUTHORITY, COMPUTE & SUBSTRATE
                                  ----------------------------------------------------  ------------------------------------  ---------------------------------------
+-----------------------+  YES  +----------------------------------------------------+  +----------------------------------+  +-------------------------------------+
| Exact Call Number?    |------>| LAYER 1: EXACT CACHE                               |  | ZONE: [ SHARED MEMORY CACHE ]    |  | TRUTH: Never Authoritative          |
| (O(1) Hash Lookup)    |       | ANALOGY: Librarian hands exact index card back     |  | STATE: Ephemeral (Cross-request) |  | BUDGET: Zero Token [O(1) Hash]      |
+-----------------------+       | USE CASE: Instant recall; bypasses LLM entirely.   |  | INFRA: Redis, Memcached          |  | MUTATION: Read-Only (Shortcut)      |
          | NO (Miss)           +----------------------------------------------------+  +----------------------------------+  +-------------------------------------+
          v
+-----------------------+  YES  +----------------------------------------------------+  +----------------------------------+  +-------------------------------------+
| Familiar Request?     |------>| LAYER 2: SEMANTIC CACHE                            |  | ZONE: [ SHARED MEMORY CACHE ]    |  | TRUTH: Never Authoritative          |
| (Vector Score > 0.95) |       | ANALOGY: Librarian safely reuses past logbook entry|  | STATE: Ephemeral unless backed   |  | BUDGET: Low Token [>0.95 Vector]    |
+-----------------------+       | USE CASE: High-precision reuse of prior thinking.  |  | INFRA: Redis Vec, GPTCache       |  | MUTATION: Read-Only (Shortcut)      |
          | NO (Miss)           +----------------------------------------------------+  +----------------------------------+  +-------------------------------------+
          v
====================================================================( AUTHORITY BOUNDARY )===========================================================================
          v
+-----------------------+  YES  +----------------------------------------------------+  +----------------------------------+  +-------------------------------------+
| Topic in the Stacks?  |------>| LAYER 3: SEMANTIC RAG                              |  | ZONE: [ CANONICAL DURABLE STORE ]|  | TRUTH: Document Grounding Authority |
| (Search Vector DB)    |       | ANALOGY: Librarian searches catalog & generates    |  | STATE: Persists across restarts  |  | SUBSTRATE: Discrete Chunk Vectors   |
+-----------------------+       | USE CASE: Broad recall / similarity search only.   |  | INFRA: Pinecone, FAISS, Postgres |  | ISOLATION: No LLM token matrices    |
          | NO (Empty)          +----------------------------------------------------+  +----------------------------------+  +-------------------------------------+
          v
+-----------------------+  YES  +----------------------------------------------------+  +----------------------------------+  +-------------------------------------+
| External Action?      |------>| LAYER 4: AGENTIC ACTION                            |  | ZONE: [ APP PROCESS HEAP ]       |  | TRUTH: Execution Engine Only        |
| (API / DB Mutation)   |       | ANALOGY: Librarian orders books, calls publisher   |  | STATE: Loses state on restart    |  | BUDGET: Max Token [API Loops]       |
+-----------------------+       | USE CASE: Orchestration, API execution, writing.   |  | INFRA: LangGraph, AutoGPT        |  | MUTATION: Read/Write (Mutator)      |
          | NO                  +----------------------------------------------------+  +----------------------------------+  +-------------------------------------+
          v
+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
| LAYER 5: FALLBACK TO GENERIC LLM (PARAMETRIC MEMORY)                                                                                                          |
| ANALOGY: Librarian answers directly from pure memory.                                                                                                         |
| SUBSTRATE: LLM Internal Token Matrix (Resides in weights). Used purely for computation, not search.                                                           |
| NO MAGIC DATA INVARIANT: If information was not trained into model weights and was not ingested into Layer 3 storage, the system cannot retrieve it.          |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------+

========================================================================================================================================================
DETAILED OPERATIONAL & FAILURE MODE MATRIX
========================================================================================================================================================

FEATURE                      1. L1: EXACT CACHE             2. L2: SEMANTIC CACHE          3. SEMANTIC RETRIEVAL (RAG)    4. AGENTIC ACTION (TOOL USE)
                             (Simplest: Literal Match)      (Intermediate: Safe Reuse)     (Complex: Broad Recall)        (Most Complex: Mutate)
---------------------------- ----------------------------   ----------------------------   ----------------------------   ------------------------------
EMBEDDING DEPENDENCY         None                           Strict / Brittle               Strict / Broad                 None (Relies on API schemas)
                             Exact string/hash matching     Model change = cache invalid   Model change = full re-index   Driven by LLM reasoning

MATCHING LOGIC               Exact Match / O(1) Hashing     Embedding Similarity Search    Embedding Similarity Search    Dynamic Tool Selection via LLM
                             Requested key matches stored   ANN search precision (>0.95)   ANN search Top-K matches       LLM evaluates intent to route

DATA PAYLOAD                 Strings, hashes, JSON objects  Queries (Vec) vs Queries (Vec) Queries (Vec) vs Chunks (Vec)  API requests, JSON, code out

LATENCY & COST PROFILE       Ultra-Low Latency / Zero Cost  Medium Latency / Low Cost      High Latency / High Cost       Variable Latency / High Cost
                             Pure in-memory fetch (<1ms)    Calls embedding model + DB     Calls embedding model & LLM    Multi-step LLM calls & APIs

EVALUATION METRIC            Hit Rate (Did key exist?)      Precision (Avoid false pos?)   Recall (NDCG, MAP)             Task Success Rate

GOVERNANCE & BOUNDARIES      Key Expiry (TTL)               Strict Admission Gates         Token Budgets                  Rate Limits (API)

MAINTENANCE (FRESHNESS)      LRU Eviction / Manual Clear    Deterministic Indexing         Periodic Vector Re-indexing    Tool Registry Updates

PRIMARY FAILURE MODE         Cache Misses & Stale Data      False Positives (Catastroph.)  Hallucination & Bad Context    Infinite Loops & Tool Failure