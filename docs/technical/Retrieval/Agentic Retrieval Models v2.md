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
| (Vector Score > 0.95) |               |  [Librarian reuses exact      |
|                       |               |   thinking safely]            |
+-----------------------+               +-------------------------------+
          | NO (Cache Miss)
          v
+-----------------------+      YES      +-------------------------------+
| Topic in the Stacks?  |-------------->|  LAYER 3: THE CATALOG         |
| (Search Vector DB)    |               |  [Librarian finds related     |
|                       |               |   ideas for synthesis]        |
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


1. REDIS (EXACT MATCH)         2. SEMANTIC CACHING            3. SEMANTIC RETRIEVAL (RAG)    4. AGENTIC ACTION (TOOL USE)
(Simplest: Literal Match)      (Intermediate: Safe Reuse)     (Complex: Broad Recall)        (Most Complex: Execute & Mutate)

MENTAL MODEL                   MENTAL MODEL                   MENTAL MODEL                   MENTAL MODEL
----------------------------   ----------------------------   ----------------------------   ----------------------------
Layer 1: Instant recall        Layer 2: Safely reuse exact    Layer 3: Generate new thinking Layer 4: Act on thinking
                               thinking (High Precision)      (High Recall)

WHAT IT IS                     WHAT IT IS                     WHAT IT IS                     WHAT IT IS
----------------------------   ----------------------------   ----------------------------   ----------------------------
Fast in-memory datastore       Binary decision system to      Retrieve broad, relevant       Autonomous reasoning loop that
used to store exact answers    reuse previously computed LLM  knowledge from external docs   interacts with systems via APIs
[Librarian's physical shelf    answers via a strict gate      for LLM synthesis              [Librarian orders new books,
 storing reference cards]      [Librarian reusing exact       [Librarian searching catalog   updates catalog, emails patrons]
                               past answer from logbook]      for many books on a topic]

ROLE IN AN AI SYSTEM           ROLE IN AN AI SYSTEM           ROLE IN AN AI SYSTEM           ROLE IN AN AI SYSTEM
----------------------------   ----------------------------   ----------------------------   ----------------------------
Storage layer / Exact-match    Latency & cost optimization    Knowledge retrieval layer /    Execution & orchestration layer /
latency optimization           for deterministic reuse        Core "research" pipeline       State mutability engine

CORE FUNCTION                  CORE FUNCTION                  CORE FUNCTION                  CORE FUNCTION
----------------------------   ----------------------------   ----------------------------   ----------------------------
Store/retrieve cached answers  Decide if previous result can  Find related information       Plan, execute, and self-correct
quickly via exact identifier   be safely reused without       using Top-K similarity         using external deterministic tools
[Librarian handing card back]  recomputing (REUSE/DO NOT)     [Librarian bringing many bks]  [Librarian calling publisher]

GOVERNANCE & BOUNDARIES        GOVERNANCE & BOUNDARIES        GOVERNANCE & BOUNDARIES        GOVERNANCE & BOUNDARIES
----------------------------   ----------------------------   ----------------------------   ----------------------------
Key Expiry (TTL)               Strict Admission Gates         Token Budgets                  Rate Limits (API)
[Librarian discards old        [Requires exact embedding      [Librarian limits number       [Librarian caps number of
 reference cards]              versioning & 1-result gate]    of books to read at once]      external phone calls made]

MATCHING LOGIC                 MATCHING LOGIC                 MATCHING LOGIC                 MATCHING LOGIC
----------------------------   ----------------------------   ----------------------------   ----------------------------
Exact Match / O(1) Hashing     Strict Similarity Threshold    Broad Similarity Search        Dynamic Tool Selection via LLM
Requested key perfectly        Needs very high score (0.97+). ANN search returning Top-K     LLM evaluates intent to route
matches stored key             Avoids ANN randomness to       closest matches (e.g., 0.6-0.9)payload to specific API schemas
                               maintain replayability.        for synthesis.

DATA PAYLOAD                   DATA PAYLOAD                   DATA PAYLOAD                   DATA PAYLOAD
----------------------------   ----------------------------   ----------------------------   ----------------------------
Strings, hashes, JSON objects  User queries (Vectors) mapped  Document chunks (Text),        API requests, JSON payloads,
mapped to simple string keys   to ONE exact LLM response      Metadata, Embeddings (Floats)  and code execution outputs
                               (or none)                      (Many documents returned)

TOOLS COMMONLY USED            TOOLS COMMONLY USED            TOOLS COMMONLY USED            TOOLS COMMONLY USED
----------------------------   ----------------------------   ----------------------------   ----------------------------
Redis Server, Memcached,       GPTCache, LangChain cache      Vector DBs (FAISS, Pinecone),  LangGraph, AutoGPT, API Gateways,
DynamoDB                       (Vector DB used strictly as a  Embedding models, LLMs         Tool/Function Calling LLMs
                               lookup table with guardrails)

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
Exact match found?             Similarity > 0.95 gate?        Top-K docs returned -> LLM     Evaluates response
  ├── YES: Return value          ├── YES: Return EXACT match    ├── CAN ANSWER: Return         ├── SUCCESS: Return
  └── NO: (Cache Miss) ───────>  └── NO: (Cache Miss) ───────>  └── NO: (Need action) ───────> └── FAIL: Acts again

LATENCY & COST PROFILE         LATENCY & COST PROFILE         LATENCY & COST PROFILE         LATENCY & COST PROFILE
----------------------------   ----------------------------   ----------------------------   ----------------------------
Ultra-Low Latency / Zero Cost  Medium Latency / Low Cost      High Latency / High Cost       Variable Latency / Highest Cost
Pure in-memory fetch (<1ms)    Calls embedding model + DB     Calls embedding model & LLM    Multi-step LLM calls & API waits

MAINTENANCE (FRESHNESS)        MAINTENANCE (FRESHNESS)        MAINTENANCE (FRESHNESS)        MAINTENANCE (FRESHNESS)
----------------------------   ----------------------------   ----------------------------   ----------------------------
LRU Eviction / Manual Clear    Deterministic Indexing         Periodic Vector Re-indexing    Tool Registry Updates
[Librarian throws away cards   [Librarian ensures past        [Librarian reorganizes the     [Librarian checks if publishers
 for books no longer held]      logbook entries remain strict] shelves for new arrivals]      changed their phone numbers]

PRIMARY FAILURE MODE           PRIMARY FAILURE MODE           PRIMARY FAILURE MODE           PRIMARY FAILURE MODE
----------------------------   ----------------------------   ----------------------------   ----------------------------
Cache Misses & Stale Data      False Positives (Catastrophic) Hallucination & Bad Context    Infinite Loops & Tool Failure
                               Slightly off similarity reuse  (Due to broad recall limits)
                               causes silent wrong answer.
