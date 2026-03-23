1. REDIS (EXACT MATCH / KV CACHE)         2. SEMANTIC CACHING                       3. SEMANTIC RETRIEVAL (RAG)
(Simplest: Literal Match)                 (Intermediate: Meaning Match)             (Most Complex: Generate Answer)

MENTAL MODEL                              MENTAL MODEL                              MENTAL MODEL
-------------------------------           -------------------------------           -------------------------------
Layer 1: Instant recall (exact)           Layer 2: Reuse thinking (similar)         Layer 3: Generate new thinking (novel)

WHAT IT IS                                WHAT IT IS                                WHAT IT IS
-------------------------------           -------------------------------           -------------------------------
Fast in-memory datastore                  Reuse previously computed LLM             Retrieve relevant knowledge
used to store exact answers               answers for similar questions             from external documents
[Librarian's physical shelving            [Librarian recognizing a question         [Librarian searching catalog
 system storing reference cards]           already in the logbook]                   by topic for relevant books]

CORE FUNCTION                             CORE FUNCTION                             CORE FUNCTION
-------------------------------           -------------------------------           -------------------------------
Store/retrieve cached answers             Decide if previous result can             Find relevant documents
quickly via exact identifier              be reused based on meaning                using similarity for new queries
[Librarian pulling a card                 [Librarian checking the ledger            [Librarian matching topic
 and handing it back instantly]            to see if solved before]                  keywords to select books]

MATCHING LOGIC                            MATCHING LOGIC                            MATCHING LOGIC
-------------------------------           -------------------------------           -------------------------------
Exact Match / O(1) Hashing                Strict Similarity Threshold               Broad Similarity Search
Requested key must perfectly              ANN search requires a very high           ANN search returning Top-K
match stored key (byte for byte)          similarity score (e.g., >0.95)            closest matches (e.g., HNSW)

DATA PAYLOAD                              DATA PAYLOAD                              DATA PAYLOAD
-------------------------------           -------------------------------           -------------------------------
Strings, hashes, JSON objects             Previous user queries (Vectors)           Document chunks (Text), Metadata,
mapped to simple string keys              mapped to LLM responses (Text)            and Vector Embeddings (Floats)

TOOLS COMMONLY USED                       TOOLS COMMONLY USED                       TOOLS COMMONLY USED
-------------------------------           -------------------------------           -------------------------------
Redis Server, Memcached,                  GPTCache, LangChain cache,                Vector DBs (FAISS, Pinecone),
DynamoDB                                  LlamaIndex similarity cache               Embedding models, LLMs

HOW IT WORKS + EXECUTION FLOW             HOW IT WORKS + EXECUTION FLOW             HOW IT WORKS + EXECUTION FLOW
-------------------------------           -------------------------------           -------------------------------
User Query                                User Query                                User Query
  │                                         │                                         │
  ▼                                         ▼                                         ▼
Lookup exact string key                   Create query embedding                    Create query embedding
in memory                                 (embedding model)                         (embedding model)
  │                                         │                                         │
  ▼                                         ▼                                         ▼
Hash table lookup                         Vector search against                     Vector search against
(O(1) execution)                          cached query vectors                      document vectors
  │                                         │                                         │
  ▼                                         ▼                                         ▼
If exact match -> return                  If match >95% found ->                    Top-K relevant documents
value immediately                         return cached text                        returned
  │                                         │                                         │
  ▼                                         ▼                                         ▼
[Librarian grabs exact                    [Librarian photocopies                    LLM reads documents
 reference card]                           the old essay]                           to produce answer
                                                                                      │
                                                                                      ▼
                                                                                    [Librarian reads books
                                                                                     and writes new essay]

ROLE IN AN AI SYSTEM                      ROLE IN AN AI SYSTEM                      ROLE IN AN AI SYSTEM
-------------------------------           -------------------------------           -------------------------------
Storage layer / Exact-match               Latency & cost optimization               Knowledge retrieval layer /
latency optimization                      layer for high-volume queries             Core "research" pipeline

LATENCY & COST PROFILE                    LATENCY & COST PROFILE                    LATENCY & COST PROFILE
-------------------------------           -------------------------------           -------------------------------
Ultra-Low Latency / Zero Cost             Medium Latency / Low Cost                 High Latency / High Cost
Pure in-memory fetch (<1ms)               Calls embedding model + DB                Calls embedding model, DB,
No embedding or LLM costs                 Saves expensive LLM costs                 and waits for LLM (1-5+ sec)

PRIMARY FAILURE MODE                      PRIMARY FAILURE MODE                      PRIMARY FAILURE MODE
-------------------------------           -------------------------------           -------------------------------
Cache Misses & Stale Data                 False Positives (Drift)                   Hallucination & Poor Retrieval
Memory fills up, or main                  Assumes nuanced query is                  Irrelevant docs retrieved,
data changes without update               identical to past generic one             LLM uses bad context

THE UPGRADE OPPORTUNITY                   THE UPGRADE OPPORTUNITY                   THE UPGRADE OPPORTUNITY
-------------------------------           -------------------------------           -------------------------------
Maintain exact-match baseline,            Make Layer 2 first-class. Operationalize  Do NOT replace RAG. Integrate it
but bind to unified telemetry             with governed policy, admission gates,    with the unified embedding system,
and state lineage.                        and embedding lifecycle management.       cache admission, and telemetry.
