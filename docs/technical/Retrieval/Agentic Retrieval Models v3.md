# UNIFIED ARCHITECTURAL SPEC: AGENTIC RETRIEVAL & RAG PIPELINES

+======================================================================================================================================================+
|                                                               THE THREE PIPELINES                             |
+======================================================================================================================================================+
| [ PIPELINE A: TRAINING ]                                                                                                                             |
| Public / licensed corpora -> model training -> model weights                                                  |
| (No vector DB population)                                                                                     |
|                                                                                                                                                      |
| [ PIPELINE B: INGESTION / INDEXING ]                                                                                                                 |
| Your documents -> chunk -> embed -> vector DB                                                                 |
| (Builds retrieval substrate)                                                                                  |
|                                                                                                                                                      |
| [ PIPELINE C: INFERENCE / RUNTIME ]                                                                                                                  |
| User query -> exact cache -> semantic cache -> RAG -> agentic action                                          |
| (Consumes prebuilt stores; never creates chunks)                        |
+======================================================================================================================================================+

+======================================================================================================================================================+
| [ PIPELINE 1 (STAGE 0): INGESTION / INDEX BUILD (OFFLINE, PRE-RUNTIME) ]|
+======================================================================================================================================================+
| SOURCES: PDFs / Docs / SharePoint / DB / Web fetch                                                            |
|                                                                                                                                                      |
| DETAILED EXECUTION PIPELINE:                                                                                                                         |
| 1. DOCUMENT LOADER: read file / API / DB                                                                |
| 2. TEXT EXTRACTION: PDF parsing / OCR / Extract text                    |
| 3. CLEANING / NORMALIZATION: remove noise / normalize formatting                                        |
| 4. CHUNKING: split into smaller units (Example: A: "Client ABC experienced...")                         |
| 5. METADATA ATTACHMENT: doc_id, page, source                                                            |
| 6. TOKENIZATION & EMBEDDING: convert chunk → tokens → vector (e.g., [0.21, -0.33, 0.77, ...])           |
| 7. VECTOR DATABASE STORAGE: Stores {embedding vector + chunk text + metadata}     |
| 8. ORIGINAL DOC STORAGE: (S3 / Blob / Filesystem / DB)                                                  |
|                                                                                                                                                      |
| HARD RULE:                                                                                                                                           |
| No ingestion -> no chunks -> empty vector DB -> no RAG retrieval        |
+======================================================================================================================================================+

+-------------------------------------------------------------------------+----------------------------------------------------------------------------+
|                  EMBEDDINGS: TWO DIFFERENT STRUCTURES                   |                            SYSTEM INVARIANTS                               |
|                                  |                                     |
+-------------------------------------------------------------------------+----------------------------------------------------------------------------+
| A. LLM INTERNAL TOKEN EMBEDDING MATRIX                                  | NO MAGIC DATA INVARIANT:                                                   |
| - part of model weights                                                 | If a source was not trained into model weights and was not ingested        |
| - rows = vocabulary tokens                                              | into retrieval storage, the system cannot retrieve it.                     |
| - columns = hidden dimensions                                           |----------------------------------------------------------------------------|
| - used for model computation / generation                               | EMBEDDING CONSISTENCY RULE:                                                |
|                                                                         | The embedding model used to index chunks must match the embedding          |
| B. RAG CHUNK EMBEDDINGS                                                 | model used for query search. Changing the embedding model requires         |
| - one vector per chunk / passage                                        | re-embedding the corpus.                                                   |
| - generated by embedding model                                          |----------------------------------------------------------------------------|
| - stored externally in vector DB                                        | THE CORE TRUTH (PIPELINE SEPARATION):                                      |
| - used only for retrieval                                               | Ingestion Pipeline creates chunks/embeddings. Query Pipeline never         |
|                                                                         | creates chunks; only searches existing ones.                               |
| RULE: Vector DB does not store token rows from the LLM embedding        |                               |
| matrix. It stores final chunk-level vectors + text + metadata.          |                                                                            |
+-------------------------------------------------------------------------+----------------------------------------------------------------------------+

========================================================================================================================================================
PIPELINE 2: INFERENCE / QUERY TIME (INTEGRATED CASCADING AGENT)
========================================================================================================================================================

[ START: INBOUND USER QUERY ] -> "Why did denied claims increase for Client ABC?"
          |
          |
          v
+------------------------------------------------------------------------------------------------------------------------------------------------------+
| QUERY PRE-PROCESSING (SHARED)                                                                           |
| Action: Normalize Query (Case folding, punctuation) -> Tokenize -> Embed (Generate q_vector)                                                         |
+------------------------------------------------------------------------------------------------------------------------------------------------------+
          |
          |
          |
          v
+-----------------------+      YES      +--------------------------------------------------------------------------------------------------------------+
| Exact Call Number?    |-------------->| LAYER 1: EXACT CACHE (THE INDEX CARD)                                                                        |
| (O(1) Hash Lookup)    |               | [Librarian pulls exact card for instant recall]                       |
+-----------------------+               | Def: Exact normalized key match; no embeddings required.              |
          |                             | Attr: Zero Token Cost | Read-Only | O(1) Match                        |
          | NO (Cache Miss)             | Tools: Redis Server, Memcached, DynamoDB                              |
          |                             | Action: Return Exact Match Instantly                            |
          v                             +--------------------------------------------------------------------------------------------------------------+
          |
          |
+-----------------------+      YES      +-------------------------------------------+       +----------------------------------------------------------+
| Familiar Request?     |-------------->| LAYER 2: SEMANTIC CACHE (THE LOGBOOK)     |       | LAYER 2 RECORD & USE CASE CALLOUT     |
| (Vector Score > 0.95) |               | [Librarian safely reuses exact thinking]  |------>| RECORD: {query_text, query_embedding,                    |
+-----------------------+               | Def: Query embedding similarity; reuse.   |       |          cached_response, metadata: {...}}               |
          |                             | Attr: Low Token Cost | Read-Only | >0.95  |       |----------------------------------------------------------|
          | NO (Cache Miss)             | Tools: GPTCache, LlamaIndex cache         |       | USE CASE: High-precision shortcut. Avoids LLM cost by    |
          |                             | Action: Vector Search vs Cache -> Return  |       | returning a previously computed answer for frequent,     |
          v                             +-------------------------------------------+       | identical-intent queries. NOT for document storage.      |
          |                                                                                 +----------------------------------------------------------+
          |
+-----------------------+      YES      +-------------------------------------------+       +----------------------------------------------------------+
| Topic in the Stacks?  |-------------->| LAYER 3: SEMANTIC RAG (THE CATALOG)       |       | LAYER 3 RECORD & USE CASE CALLOUT     |
| (Search Vector DB)    |               | [Librarian searches catalog & generates]  |------>| RECORD: {chunk_id, doc_id, chunk_text,                   |
+-----------------------+               | Attr: High Token Cost | Broad Recall      |       |          embedding_vector, metadata: {...}}              |
          |                             | Tools: Vector DBs, Embedding models       |       |----------------------------------------------------------|
          | NO (Insufficient Context)   | Action: Vector Search vs DB -> Score &    |       | USE CASE: Broad knowledge retrieval. Finds relevant      |
          |                             |         Rank -> Top-K -> Assemble Context |       | chunks of external documents to ground the LLM's new     |
          v                             +-------------------------------------------+       | answer. This is the core "research" / context phase.     |
          |                                                                                 +----------------------------------------------------------+
          |
+-----------------------+      YES      +--------------------------------------------------------------------------------------------------------------+
| External Action?      |-------------->| LAYER 4: AGENTIC ACTION (THE SPECIAL ORDER)                                                                  |
| (API / DB Mutation)   |               | [Librarian orders new books, updates catalog, calls pub]              |
+-----------------------+               | Attr: Maximum Token Cost | MUTATES STATE (W/R)                        |
          |                             | Tools: LangGraph, AutoGPT, Tool/Function Calling LLMs                 |
          | NO                          | Action: Trigger API -> Send Context/Payload to LLM              |
          |                             +--------------------------------------------------------------------------------------------------------------+
          v
          |
          |
+-----------------------+
| FALLBACK: GENERIC LLM |
| (Parametric Memory)   |
| [Librarian answers    |
|  from pure memory]    |
| Action: LLM Tokenize  |
| -> Generate -> Output |
+-----------------------+



========================================================================================================================================================
DETAILED LAYER ANALYSIS MATRIX (WIDESCREEN COMPARISON)
========================================================================================================================================================

FEATURE                      1. L1: EXACT CACHE (REDIS KV)  2. L2: SEMANTIC CACHE          3. SEMANTIC RETRIEVAL (RAG)    4. AGENTIC ACTION (TOOL USE)
                             (Simplest: Literal Match)      (Intermediate: Safe Reuse)     (Complex: Broad Recall)        (Most Complex: Mutate)
---------------------------- ----------------------------   ----------------------------   ----------------------------   ------------------------------
MENTAL MODEL                 Layer 1: Instant recall        Layer 2: Safely reuse exact    Layer 3: Generate new thinking Layer 4: Act on thinking
                                                            thinking (High Precision)      (High Recall)

WHAT IT IS                   Fast in-memory datastore       Binary decision system using   Vector search to retrieve      Autonomous reasoning loop that
                             used to store exact answers    embedding lookups against      broad, relevant knowledge      interacts with systems via API
                             [Librarian's physical shelf    past query-response pairs      from external documents        [Librarian orders new books,
                              storing reference cards]      [Librarian reusing exact       [Librarian searching catalog    updates catalog, emails]
                                                             past answer from logbook]      for many books on a topic]

ROLE IN AN AI SYSTEM         Storage layer / Exact-match    Latency & cost optimization    Knowledge retrieval layer /    Execution & orchestration /
                             latency optimization           via high-precision embedding   Core "research" pipeline       State mutability engine
                                                            reuse (Binary Gate)

CORE FUNCTION                Store/retrieve cached answers  Embedding lookup against past  Embedding lookup against       Plan, execute, & self-correct
                             quickly via exact identifier   queries to verify REUSE.       documents to find CONTEXT.     using deterministic tools
                             [Librarian handing card back]  [Librarian checking ledger]    [Librarian matching topics]    [Librarian calling publisher]

STATE MUTATION (READ/WRITE)  Read-Only / Idempotent         Read-Only / Idempotent         Read-Only / Idempotent         Read/Write / Mutates State
                             Does not change external       Does not change external       Does not change external       Performs actions that change
                             system state.                  system state.                  system state.                  state (e.g., sending email).

TOKEN COST & CONTEXT WINDOW  Zero Token Cost                Low Token Cost                 High Token Cost                Maximum Token Cost
                             Bypasses LLM entirely;         Consumes tokens only for       Fills the LLM context window   Requires multiple generation
                             does not touch context window. creating the query embedding.  with document chunks.          cycles & API payload tokens.

EMBEDDING DEPENDENCY         None                           Strict / Brittle               Strict / Broad                 None (Relies on API schemas)
                             Uses exact string or hash      Changing embedding models      Changing embedding models      Independent of embeddings;
                             matching.                      instantly invalidates cache.   requires full DB re-indexing.  driven by LLM reasoning.

EVALUATION METRIC            Hit Rate                       Precision                      Recall (NDCG, MAP)             Task Success Rate
                             Did the exact key exist?       Did we avoid false positives?  Did we find the right docs?    Did the API call succeed?

GOVERNANCE & BOUNDARIES      Key Expiry (TTL)               Strict Admission Gates         Token Budgets                  Rate Limits (API)
                             [Librarian discards old        [Requires 0.95+ score to       [Librarian limits number       [Librarian caps number of
                              reference cards]               prevent silent wrong answers]  of books to read at once]      external phone calls made]

MATCHING LOGIC               Exact Match / O(1) Hashing     Embedding Similarity Search    Embedding Similarity Search    Dynamic Tool Selection via LLM
                             Requested key perfectly        ANN search requires extreme    ANN search returning Top-K     LLM evaluates intent to route
                             matches stored key             precision (>0.95)              closest matches (Top-K)        payload to specific schemas

DATA PAYLOAD                 Strings, hashes, JSON objects  Current Query (Vector) vs.     Current Query (Vector) vs.     API requests, JSON payloads,
                             mapped to simple string keys   Past Queries (Vectors)         Doc Chunks (Vectors)           and code execution outputs

TOOLS COMMONLY USED          Redis Server, Memcached,       GPTCache, LlamaIndex cache     Vector DBs (FAISS, Pinecone),  LangGraph, AutoGPT, API GWs,
                             DynamoDB                       (Enforced as strict lookup)    Embedding models, LLMs         Tool/Function Calling LLMs

LATENCY & COST PROFILE       Ultra-Low Latency / Zero Cost  Medium Latency / Low Cost      High Latency / High Cost       Variable Latency / High Cost
                             Pure in-memory fetch (<1ms)    Calls embedding model + DB     Calls embedding model & LLM    Multi-step LLM calls & APIs

MAINTENANCE (FRESHNESS)      LRU Eviction / Manual Clear    Deterministic Indexing         Periodic Vector Re-indexing    Tool Registry Updates
                             [Librarian throws away cards   [Ensure index is consistent    [Librarian reorganizes the     [Librarian checks if pubs
                              for books no longer held]      to maintain replayability]     shelves for new arrivals]      changed phone numbers]

PRIMARY FAILURE MODE         Cache Misses & Stale Data      False Positives (Catastroph.)  Hallucination & Bad Context    Infinite Loops & Tool Failure
