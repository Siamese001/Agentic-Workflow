+================================================================================================================================================+
|                                                               THE THREE PIPELINES                                                              |
+================================================================================================================================================+
| [ PIPELINE A: TRAINING ]                                                                                                                       |
| Public / licensed corpora -> model training -> model weights                                                                                   |
| (No vector DB population)                                                                                                                      |
|                                                                                                                                                |
| [ PIPELINE B: INGESTION / INDEXING ]                                                                                                           |
| Your documents -> chunk -> embed -> vector DB                                                                                                  |
| (Builds retrieval substrate)                                                                                                                   |
|                                                                                                                                                |
| [ PIPELINE C: INFERENCE / RUNTIME ]                                                                                                            |
| User query -> exact cache -> semantic cache -> RAG -> agentic action                                                                           |
| (Consumes prebuilt stores; never creates chunks)                                                                                               |
+================================================================================================================================================+

+================================================================================================================================================+
|                                           [ STAGE 0: INGESTION / INDEX BUILD (OFFLINE, PRE-RUNTIME) ]                                          |
+================================================================================================================================================+
| SOURCES:                                                                                                                                       |
| - PDFs / Docs / SharePoint / DB / Web fetch                                                                                                    |
|                                                                                                                                                |
| PIPELINE:                                                                                                                                      |
| Document -> Extract text -> Normalize -> Chunk -> Attach metadata                                                                              |
|          -> Embed chunks -> Store {vector + chunk text + metadata}                                                                             |
|                                                                                                                                                |
| OUTPUTS:                                                                                                                                       |
| - Source-of-truth document store                                                                                                               |
| - Vector database / ANN index                                                                                                                  |
|                                                                                                                                                |
| HARD RULE:                                                                                                                                     |
| No ingestion -> no chunks -> empty vector DB -> no RAG retrieval                                                                               |
+================================================================================================================================================+

+----------------------------------------------------------------------+-------------------------------------------------------------------------+
|                  EMBEDDINGS: TWO DIFFERENT STRUCTURES                |                            SYSTEM INVARIANTS                            |
+----------------------------------------------------------------------+-------------------------------------------------------------------------+
| A. LLM INTERNAL TOKEN EMBEDDING MATRIX                               | NO MAGIC DATA INVARIANT:                                                |
| - part of model weights                                              | If a source was not trained into model weights and was not ingested     |
| - rows = vocabulary tokens                                           | into retrieval storage, the system cannot retrieve it.                  |
| - columns = hidden dimensions                                        |                                                                         |
| - used for model computation / generation                            |-------------------------------------------------------------------------|
|                                                                      | EMBEDDING CONSISTENCY RULE:                                             |
| B. RAG CHUNK EMBEDDINGS                                              | The embedding model used to index chunks must match the embedding       |
| - one vector per chunk / passage                                     | model used for query search. Changing the embedding model requires      |
| - generated by embedding model                                       | re-embedding the corpus.                                                |
| - stored externally in vector DB                                     |                                                                         |
| - used only for retrieval                                            |                                                                         |
|                                                                      |                                                                         |
| RULE: Vector DB does not store token rows from the LLM embedding     |                                                                         |
| matrix. It stores final chunk-level vectors + text + metadata.       |                                                                         |
+----------------------------------------------------------------------+-------------------------------------------------------------------------+

+----------------------------------------------------------------------+-------------------------------------------------------------------------+
|                            VECTOR DB RECORD                          |                          SEMANTIC CACHE RECORD                          |
+----------------------------------------------------------------------+-------------------------------------------------------------------------+
| {                                                                    | {                                                                       |
|   chunk_id,                                                          |   query_text,                                                           |
|   doc_id,                                                            |   query_embedding,                                                      |
|   chunk_text,                                                        |   cached_response,                                                      |
|   embedding_vector,                                                  |   metadata: {model, version, timestamp, threshold}                      |
|   metadata: {source, page, timestamp, tags}                          | }                                                                       |
| }                                                                    |                                                                         |
|                                                                      | PURPOSE:                                                                |
| SEARCH ON:                                                           | reuse prior computation                                                 |
| - embedding_vector                                                   |                                                                         |
|                                                                      | NOT:                                                                    |
| RETURN TO RUNTIME:                                                   | document storage                                                        |
| - chunk_text + metadata + score                                      |                                                                         |
+----------------------------------------------------------------------+-------------------------------------------------------------------------+

+------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                     L1 vs L2 CACHE DEFINITIONS (PRE-CASCADE)                                                   |
+------------------------------------------------------------------------------------------------------------------------------------------------+
| L1 = EXACT CACHE (Redis KV / hash lookup)                            | L2 = SEMANTIC CACHE                                                     |
| - exact normalized key match                                         | - query embedding similarity                                            |
| - no embeddings required                                             | - stores prior query -> response artifacts                              |
|                                                                      | - thresholded reuse                                                     |
+------------------------------------------------------------------------------------------------------------------------------------------------+


[ START: INBOUND USER QUERY ]
          |
          v
+-----------------------+      YES      +-------------------------------+
| Exact Call Number?    |-------------->|  LAYER 1: THE INDEX CARD      |
| (O(1) Hash Lookup)    |               |  [Librarian pulls exact card] |
+-----------------------+               +-------------------------------+
          | NO (Cache Miss)
          v
+-----------------------+      YES      +-------------------------------+
| Familiar Request?     |-------------->|  LAYER 2: THE LOGBOOK         |
| (Vector Score > 0.95) |               |  [Embedding Lookup: Librarian |
|                       |               |   reuses exact past thinking] |
+-----------------------+               +-------------------------------+
          | NO (Cache Miss)
          v
+-----------------------+      YES      +-------------------------------+
| Topic in the Stacks?  |-------------->|  LAYER 3: THE CATALOG         |
| (Search Vector DB)    |               |  [Embedding Lookup: Librarian |
|                       |               |   finds ideas for synthesis]  |
+-----------------------+               +-------------------------------+
          | NO (Insufficient Context)
          v
+-----------------------+      YES      +-------------------------------+
| External Action?      |-------------->|  LAYER 4: THE SPECIAL ORDER   |
| (API / DB Mutation)   |               |  [Librarian calls publishers] |
+-----------------------+               +-------------------------------+
          | NO
          v
+-----------------------+
| FALLBACK: GENERIC LLM |
| (Parametric Memory)   |
| [Librarian answers    |
|  from pure memory]    |
+-----------------------+


1. L1: EXACT CACHE (REDIS KV)  2. L2: SEMANTIC CACHE          3. SEMANTIC RETRIEVAL (RAG)    4. AGENTIC ACTION (TOOL USE)
(Simplest: Literal Match)      (Intermediate: Safe Reuse)     (Complex: Broad Recall)        (Most Complex: Execute & Mutate)

MENTAL MODEL                   MENTAL MODEL                   MENTAL MODEL                   MENTAL MODEL
----------------------------   ----------------------------   ----------------------------   ----------------------------
Layer 1: Instant recall        Layer 2: Safely reuse exact    Layer 3: Generate new thinking Layer 4: Act on thinking
                               thinking (High Precision)      (High Recall)

WHAT IT IS                     WHAT IT IS                     WHAT IT IS                     WHAT IT IS
----------------------------   ----------------------------   ----------------------------   ----------------------------
Fast in-memory datastore       Binary decision system using   Vector search to retrieve      Autonomous reasoning loop that
used to store exact answers    embedding lookups against      broad, relevant knowledge      interacts with systems via APIs
[Librarian's physical shelf    past query-response pairs      from external documents        [Librarian orders new books,
 storing reference cards]      [Librarian reusing exact       [Librarian searching catalog   updates catalog, emails patrons]
                               past answer from logbook]      for many books on a topic]

ROLE IN AN AI SYSTEM           ROLE IN AN AI SYSTEM           ROLE IN AN AI SYSTEM           ROLE IN AN AI SYSTEM
----------------------------   ----------------------------   ----------------------------   ----------------------------
Storage layer / Exact-match    Latency & cost optimization    Knowledge retrieval layer /    Execution & orchestration layer /
latency optimization           via high-precision embedding   Core "research" pipeline       State mutability engine
                               reuse (Binary Gate)

CORE FUNCTION                  CORE FUNCTION                  CORE FUNCTION                  CORE FUNCTION
----------------------------   ----------------------------   ----------------------------   ----------------------------
Store/retrieve cached answers  Embedding lookup against past  Embedding lookup against       Plan, execute, and self-correct
quickly via exact identifier   queries to verify REUSE.       documents to find CONTEXT.     using external deterministic tools
[Librarian handing card back]  [Librarian checking ledger]    [Librarian matching topics]    [Librarian calling publisher]

STATE MUTATION (READ/WRITE)    STATE MUTATION (READ/WRITE)    STATE MUTATION (READ/WRITE)    STATE MUTATION (READ/WRITE)
----------------------------   ----------------------------   ----------------------------   ----------------------------
Read-Only / Idempotent         Read-Only / Idempotent         Read-Only / Idempotent         Read/Write / Mutates State
Does not change external       Does not change external       Does not change external       Performs actions that change
system state.                  system state.                  system state.                  state (e.g., sending an email).

TOKEN COST & CONTEXT WINDOW    TOKEN COST & CONTEXT WINDOW    TOKEN COST & CONTEXT WINDOW    TOKEN COST & CONTEXT WINDOW
----------------------------   ----------------------------   ----------------------------   ----------------------------
Zero Token Cost                Low Token Cost                 High Token Cost                Maximum Token Cost
Bypasses LLM entirely;         Consumes tokens only for       Fills the LLM context window   Requires multiple generation
does not touch context window. creating the query embedding.  with document chunks.          cycles and API payload tokens.

EMBEDDING DEPENDENCY           EMBEDDING DEPENDENCY           EMBEDDING DEPENDENCY           EMBEDDING DEPENDENCY
----------------------------   ----------------------------   ----------------------------   ----------------------------
None                           Strict / Brittle               Strict / Broad                 None (Relies on API schemas)
Uses exact string or hash      Changing embedding models      Changing embedding models      Independent of embeddings;
matching.                      instantly invalidates cache.   requires full DB re-indexing.  driven by LLM reasoning.

EVALUATION METRIC              EVALUATION METRIC              EVALUATION METRIC              EVALUATION METRIC
----------------------------   ----------------------------   ----------------------------   ----------------------------
Hit Rate                       Precision                      Recall (NDCG, MAP)             Task Success Rate
Did the exact key exist?       Did we avoid false positives?  Did we find the right docs?    Did the API call succeed?

GOVERNANCE & BOUNDARIES        GOVERNANCE & BOUNDARIES        GOVERNANCE & BOUNDARIES        GOVERNANCE & BOUNDARIES
----------------------------   ----------------------------   ----------------------------   ----------------------------
Key Expiry (TTL)               Strict Admission Gates         Token Budgets                  Rate Limits (API)
[Librarian discards old        [Requires 0.95+ score to       [Librarian limits number       [Librarian caps number of
 reference cards]              prevent silent wrong answers]  of books to read at once]      external phone calls made]

MATCHING LOGIC                 MATCHING LOGIC                 MATCHING LOGIC                 MATCHING LOGIC
----------------------------   ----------------------------   ----------------------------   ----------------------------
Exact Match / O(1) Hashing     Embedding Similarity Search    Embedding Similarity Search    Dynamic Tool Selection via LLM
Requested key perfectly        ANN search requires extreme    ANN search returning Top-K     LLM evaluates intent to route
matches stored key             precision (>0.95)              closest matches (Top-K)        payload to specific API schemas

DATA PAYLOAD                   DATA PAYLOAD                   DATA PAYLOAD                   DATA PAYLOAD
----------------------------   ----------------------------   ----------------------------   ----------------------------
Strings, hashes, JSON objects  Current Query (Vector) vs.     Current Query (Vector) vs.     API requests, JSON payloads,
mapped to simple string keys   Past Queries (Vectors)         Doc Chunks (Vectors)           and code execution outputs

TOOLS COMMONLY USED            TOOLS COMMONLY USED            TOOLS COMMONLY USED            TOOLS COMMONLY USED
----------------------------   ----------------------------   ----------------------------   ----------------------------
Redis Server, Memcached,       GPTCache, LlamaIndex cache     Vector DBs (FAISS, Pinecone),  LangGraph, AutoGPT, API Gateways,
DynamoDB                       (Enforced as strict lookup)    Embedding models, LLMs         Tool/Function Calling LLMs

HOW IT WORKS (CASCADING)       HOW IT WORKS (CASCADING)       HOW IT WORKS (CASCADING)       HOW IT WORKS (CASCADING)
----------------------------   ----------------------------   ----------------------------   ----------------------------
User Query                     [CACHE MISS FROM LAYER 1]      [CACHE MISS FROM LAYER 2]      [INSUFFICIENT RAG CONTEXT]
  │                              │                              │                              │
  ▼                              ▼                              ▼                              ▼
Lookup exact string key        Generate Query Embedding       [REUSE Query Embedding]        Agent evaluates goal
  │                              │                              │                              │
  ▼                              ▼                              ▼                              ▼
Hash table lookup              Search PAST QUERY vectors      Search DOCUMENT vectors        Selects & invokes tool (API)
  │                              │                              │                              │
  ▼                              ▼                              ▼                              ▼
Exact match found?             Similarity > 0.95?             Top-K docs returned -> LLM     Evaluates response
  ├── YES: Return value          ├── YES: Return cached text    ├── CAN ANSWER: Return         ├── SUCCESS: Return
  └── NO: (Cache Miss) ───────>  └── NO: (Cache Miss) ───────>  └── NO: (Need action) ───────> └── FAIL: Acts again

LATENCY & COST PROFILE         LATENCY & COST PROFILE         LATENCY & COST PROFILE         LATENCY & COST PROFILE
----------------------------   ----------------------------   ----------------------------   ----------------------------
Ultra-Low Latency / Zero Cost  Medium Latency / Low Cost      High Latency / High Cost       Variable Latency / Highest Cost
Pure in-memory fetch (<1ms)    Calls embedding model + DB     Calls embedding model & LLM    Multi-step LLM calls & API waits

MAINTENANCE (FRESHNESS)        MAINTENANCE (FRESHNESS)        MAINTENANCE (FRESHNESS)        MAINTENANCE (FRESHNESS)
----------------------------   ----------------------------   ----------------------------   ----------------------------
LRU Eviction / Manual Clear    Deterministic Indexing         Periodic Vector Re-indexing    Tool Registry Updates
[Librarian throws away cards   [Ensure index is consistent    [Librarian reorganizes the     [Librarian checks if publishers
 for books no longer held]      to maintain replayability]     shelves for new arrivals]      changed their phone numbers]

PRIMARY FAILURE MODE           PRIMARY FAILURE MODE           PRIMARY FAILURE MODE           PRIMARY FAILURE MODE
----------------------------   ----------------------------   ----------------------------   ----------------------------
Cache Misses & Stale Data      False Positives (Catastrophic) Hallucination & Bad Context    Infinite Loops & Tool Failure
