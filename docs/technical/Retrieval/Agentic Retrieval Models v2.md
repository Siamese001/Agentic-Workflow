1. REDIS (EXACT MATCH)         2. SEMANTIC CACHING            3. SEMANTIC RETRIEVAL (RAG)    4. AGENTIC ACTION (TOOL USE)
(Simplest: Literal Match)      (Intermediate: Meaning Match)  (Complex: Generate Answer)     (Most Complex: Execute & Mutate)

MENTAL MODEL                   MENTAL MODEL                   MENTAL MODEL                   MENTAL MODEL
----------------------------   ----------------------------   ----------------------------   ----------------------------
Layer 1: Instant recall        Layer 2: Reuse thinking        Layer 3: Generate new thinking Layer 4: Act on thinking

WHAT IT IS                     WHAT IT IS                     WHAT IT IS                     WHAT IT IS
----------------------------   ----------------------------   ----------------------------   ----------------------------
Fast in-memory datastore       Reuse previously computed LLM  Retrieve relevant knowledge    Autonomous reasoning loop that
used to store exact answers    answers for similar questions  from external documents        interacts with systems via APIs
[Librarian's physical shelf    [Librarian recognizing query   [Librarian searching catalog   [Librarian orders new books,
 storing reference cards]       already in the logbook]        by topic for relevant books]   updates catalog, emails patrons]

ROLE IN AN AI SYSTEM           ROLE IN AN AI SYSTEM           ROLE IN AN AI SYSTEM           ROLE IN AN AI SYSTEM
----------------------------   ----------------------------   ----------------------------   ----------------------------
Storage layer / Exact-match    Latency & cost optimization    Knowledge retrieval layer /    Execution & orchestration layer /
latency optimization           layer for high-volume queries  Core "research" pipeline       State mutability engine

CORE FUNCTION                  CORE FUNCTION                  CORE FUNCTION                  CORE FUNCTION
----------------------------   ----------------------------   ----------------------------   ----------------------------
Store/retrieve cached answers  Decide if previous result can  Find relevant documents        Plan, execute, and self-correct
quickly via exact identifier   be reused based on meaning     using similarity for queries   using external deterministic tools
[Librarian handing card back]  [Librarian checking ledger]    [Librarian matching topics]    [Librarian calling publisher]

MATCHING LOGIC                 MATCHING LOGIC                 MATCHING LOGIC                 MATCHING LOGIC
----------------------------   ----------------------------   ----------------------------   ----------------------------
Exact Match / O(1) Hashing     Strict Similarity Threshold    Broad Similarity Search        Dynamic Tool Selection via LLM
Requested key perfectly        ANN search requires high       ANN search returning Top-K     LLM evaluates intent to route
matches stored key             similarity score (e.g., >0.95) closest matches (e.g., HNSW)   payload to specific API schemas

DATA PAYLOAD                   DATA PAYLOAD                   DATA PAYLOAD                   DATA PAYLOAD
----------------------------   ----------------------------   ----------------------------   ----------------------------
Strings, hashes, JSON objects  User queries (Vectors) mapped  Document chunks (Text),        API requests, JSON payloads,
mapped to simple string keys   to LLM responses (Text)        Metadata, Embeddings (Floats)  and code execution outputs

TOOLS COMMONLY USED            TOOLS COMMONLY USED            TOOLS COMMONLY USED            TOOLS COMMONLY USED
----------------------------   ----------------------------   ----------------------------   ----------------------------
Redis Server, Memcached,       GPTCache, LangChain cache,     Vector DBs (FAISS, Pinecone),  LangGraph, AutoGPT, API Gateways,
DynamoDB                       LlamaIndex similarity cache    Embedding models, LLMs         Tool/Function Calling LLMs

HOW IT WORKS (CASCADING)       HOW IT WORKS (CASCADING)       HOW IT WORKS (CASCADING)       HOW IT WORKS (CASCADING)
----------------------------   ----------------------------   ----------------------------   ----------------------------
User Query                     [CACHE MISS FROM LAYER 1]      [CACHE MISS FROM LAYER 2]      [INSUFFICIENT RAG CONTEXT]
  │                              │                              │                              │
  ▼                              ▼                              ▼                              ▼
Lookup exact string key        Create query embedding         Create query embedding         Agent evaluates goal
  │                              │                              │                              │
  ▼                              ▼                              ▼                              ▼
Hash table lookup              Vector search against          Vector search against          Selects & invokes tool (API)
  │                              │                              │                              │
  ▼                              ▼                              ▼                              ▼
Exact match found?             Similarity > 0.95?             Top-K docs returned -> LLM     Evaluates response
  ├── YES: Return value          ├── YES: Return cached text    ├── CAN ANSWER: Return         ├── SUCCESS: Return
  └── NO: (Cache Miss) ───────>  └── NO: (Cache Miss) ───────>  └── NO: (Need action) ───────> └── FAIL: Acts again

LATENCY & COST PROFILE         LATENCY & COST PROFILE         LATENCY & COST PROFILE         LATENCY & COST PROFILE
----------------------------   ----------------------------   ----------------------------   ----------------------------
Ultra-Low Latency / Zero Cost  Medium Latency / Low Cost      High Latency / High Cost       Variable Latency / Highest Cost
Pure in-memory fetch (<1ms)    Calls embedding model + DB     Calls embedding model & LLM    Multi-step LLM calls & API waits

PRIMARY FAILURE MODE           PRIMARY FAILURE MODE           PRIMARY FAILURE MODE           PRIMARY FAILURE MODE
----------------------------   ----------------------------   ----------------------------   ----------------------------
Cache Misses & Stale Data      False Positives (Drift)        Hallucination & Bad Context    Infinite Loops & Tool Failure