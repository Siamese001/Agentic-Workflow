1. REDIS (EXACT MATCH)            2. SEMANTIC CACHING               3. TRADITIONAL RAG (ONE-SHOT)     4. AGENTIC RAG (ITERATIVE)
(Simplest: Literal Match)         (Intermediate: Meaning Match)     (Complex: Generate Answer)        (Most Complex: Solve Problem)

MENTAL MODEL                      MENTAL MODEL                      MENTAL MODEL                      MENTAL MODEL
-------------------------------   -------------------------------   -------------------------------   -------------------------------
Layer 1: Instant recall (exact)   Layer 2: Reuse thinking (similar) Layer 3: Generate (novel)         Layer 4: Autonomous research

WHAT IT IS                        WHAT IT IS                        WHAT IT IS                        WHAT IT IS
-------------------------------   -------------------------------   -------------------------------   -------------------------------
Fast in-memory datastore          Reuse previously computed LLM     Retrieve relevant knowledge       Iterative system that plans,
used to store exact answers.      answers for similar questions.    from external documents.          retrieves, and self-corrects.
[Librarian's physical shelving    [Librarian recognizing a query    [Librarian searching catalog      [Librarian given a thesis topic
 system storing reference cards]   already in the logbook]           by topic for relevant books]      who iteratively reads & adjusts]

CORE FUNCTION                     CORE FUNCTION                     CORE FUNCTION                     CORE FUNCTION
-------------------------------   -------------------------------   -------------------------------   -------------------------------
Store/retrieve cached answers     Decide if previous result can     Find relevant documents           Multi-step reasoning and dynamic
quickly via exact identifier.     be reused based on meaning.       using similarity for new queries. tool execution for complex needs.

MATCHING LOGIC                    MATCHING LOGIC                    MATCHING LOGIC                    MATCHING LOGIC
-------------------------------   -------------------------------   -------------------------------   -------------------------------
Exact Match / O(1) Hashing        Strict Similarity Threshold       Broad Similarity Search           Goal-Oriented Routing
Requested key must perfectly      ANN search requires a very high   ANN search returning Top-K        LLM dynamically formulates
match stored key (byte for byte). similarity score (e.g., >0.95).   closest matches (e.g., HNSW).     queries based on missing context.

DATA PAYLOAD                      DATA PAYLOAD                      DATA PAYLOAD                      DATA PAYLOAD
-------------------------------   -------------------------------   -------------------------------   -------------------------------
Strings, hashes, JSON objects     Previous queries (Vectors)        Document chunks (Text), Metadata, Thought-Action-Observation loops,
mapped to simple string keys.     mapped to LLM responses (Text).   and Vector Embeddings (Floats).   dynamically fetched JSON context.

TOOLS COMMONLY USED               TOOLS COMMONLY USED               TOOLS COMMONLY USED               TOOLS COMMONLY USED
-------------------------------   -------------------------------   -------------------------------   -------------------------------
Redis Server, Memcached,          GPTCache, LangChain cache,        Vector DBs (FAISS, Pinecone),     L1 Cognitive Engine, L4 Gateway,
DynamoDB                          LlamaIndex similarity cache       Embedding models, LLMs            Tool Calling, LangGraph

HOW IT WORKS + EXECUTION FLOW     HOW IT WORKS + EXECUTION FLOW     HOW IT WORKS + EXECUTION FLOW     HOW IT WORKS + EXECUTION FLOW
-------------------------------   -------------------------------   -------------------------------   -------------------------------
User Query                        User Query                        User Query                        User Query
  │                                 │                                 │                                 │
  ▼                                 ▼                                 ▼                                 ▼
Lookup exact string key           Create query embedding            Create query embedding            L1 Agent formulates plan
in memory                         (embedding model)                 (embedding model)                   │
  │                                 │                                 │                                 ▼
  ▼                                 ▼                                 ▼                               Calls L4 Gateway tools
Hash table lookup                 Vector search against             Vector search against               │
(O(1) execution)                  cached query vectors              document vectors                    ▼
  │                                 │                                 │                               Evaluates retrieved data
  ▼                                 ▼                                 ▼                                 │<--(If insufficient, loop back)
If exact match -> return          If match >95% found ->            Top-K relevant documents            ▼
value immediately                 return cached text                returned                          Synthesizes final answer
  │                                 │                                 │                                 │
  ▼                                 ▼                                 ▼                                 ▼
[Librarian grabs exact            [Librarian photocopies            LLM reads documents               [Librarian writes fully
 reference card]                   the old essay]                    to produce answer                 researched thesis]

ROLE IN AN AI SYSTEM              ROLE IN AN AI SYSTEM              ROLE IN AN AI SYSTEM              ROLE IN AN AI SYSTEM
-------------------------------   -------------------------------   -------------------------------   -------------------------------
Storage layer / Exact-match       Latency & cost optimization       Knowledge retrieval layer /       Cognitive engine for multi-hop
latency optimization              layer for high-volume queries     Core "research" pipeline          or highly ambiguous user intents.

LATENCY & COST PROFILE            LATENCY & COST PROFILE            LATENCY & COST PROFILE            LATENCY & COST PROFILE
-------------------------------   -------------------------------   -------------------------------   -------------------------------
Ultra-Low Latency / Zero Cost     Medium Latency / Low Cost         High Latency / High Cost          Extreme Latency / Extreme Cost
Pure in-memory fetch (<1ms)       Calls embedding model + DB        Calls embedding model, DB,        Multiple LLM calls, recursive
No embedding or LLM costs         Saves expensive LLM costs         and waits for LLM (1-5+ sec)      loops, high token burn (10-30s).

PRIMARY FAILURE MODE              PRIMARY FAILURE MODE              PRIMARY FAILURE MODE              PRIMARY FAILURE MODE
-------------------------------   -------------------------------   -------------------------------   -------------------------------
Cache Misses & Stale Data         False Positives (Drift)           Hallucination & Poor Retrieval    Infinite Loops & Tool Drift
Memory fills up, or main          Assumes nuanced query is          Irrelevant docs retrieved,        Agent gets stuck reasoning or
data changes without update       identical to past generic one     LLM uses bad context              hallucinates tool parameters.

THE UPGRADE OPPORTUNITY           THE UPGRADE OPPORTUNITY           THE UPGRADE OPPORTUNITY           THE UPGRADE OPPORTUNITY
-------------------------------   -------------------------------   -------------------------------   -------------------------------
Maintain exact-match baseline,    Make Layer 2 first-class.         Do NOT replace RAG. Integrate it  Transition from linear generation
but bind to unified telemetry     Implement governed policy and     with unified telemetry and state  to a self-correcting L1/L4 loop
and state lineage.                embedding lifecycle management.   lineage.                          with strict observability (L6).
