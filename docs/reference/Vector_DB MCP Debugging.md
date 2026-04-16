The cleanest way to isolate it is to split the system into five boxes — caller, MCP wrapper, embedding runtime, Chroma client, and Chroma store — because your rebuild succeeded and the apparent stall only showed up when the post-rebuild validation query hit repo_evidence, which means the failure zone is almost certainly query-path orchestration, not the repo_evidence rebuild itself.

                                                VECTOR_DB MCP / CHROMA UNIFIED DEBUG MAP                                                
┌──────────────────────────────────────────────────────────────────────┐ ┌──────────────────────────────────────────────────────────────────────┐
│  A. WINDSURF / CALLER                                                │ │ FASTEST BINARY-ISOLATION VIEW                                        │
│  ------------------------------------------------------------------  │ │ -------------------------------------------------------------------- │
│  Prompt / script / validation step                                   │ │                          WHERE IS THE HANG?                          │
│                                                                      │ │                                                                      │
│    "query repo_evidence for TS-20"                                   │ │                       ┌────────────────────────┐                       │
│           │                                                          │ │                       │ SAME QUERY, TWO PATHS  │                       │
│           ▼                                                          │ │                       └───────────┬────────────┘                       │
│    MCP tool invocation                                               │ │                                   │                                    │
│    args = {                                                          │ │                 ┌─────────────────┴─────────────────┐                  │
│      collection_name = "repo_evidence"                               │ │                 ▼                                   ▼                  │
│      query_text      = "normative requirements specification         │ │ ┌─────────────────────────────┐ ┌─────────────────────────────────┐  │
│                        for the agentic routing system"               │ │ │ PATH 1: MCP / query_texts   │ │ PATH 2: direct query_embeddings │  │
│      n_results       = 5                                             │ │ │ --------------------------- │ │ ------------------------------- │  │
│      include         = ["documents","metadatas","distances"]         │ │ │ caller -> MCP -> embed ->   │ │ embed separately ->             │  │
│    }                                                                 │ │ │ chroma -> response          │ │ PersistentClient -> query       │  │
└──────────────────────────────────────────────────────────────────────┘ │ └─────────────┬───────────────┘ └───────────────┬─────────────────┘  │
                                 │                                       │               │                                 │                    │
                                 │ MCP request                           │     if this hangs, but Path 2 works             │                    │
                                 ▼                                       │               │                                 │                    │
┌──────────────────────────────────────────────────────────────────────┐ │               ▼                                 ▼                    │
│  B. VECTOR_DB MCP SERVER                                             │ │ ┌─────────────────────────────┐ ┌─────────────────────────────────┐  │
│  ------------------------------------------------------------------  │ │ │ MCP wrapper / embed runtime │ │ Chroma query path itself works  │  │
│  Request handler / wrapper layer                                     │ │ │ is the likely problem       │ │ issue is NOT the ANN store      │  │
│                                                                      │ │ └─────────────────────────────┘ └─────────────────────────────────┘  │
│    parse args                                                        │ └──────────────────────────────────────────────────────────────────────┘
│    validate collection exists                                        │ ┌──────────────────────────────────────────────────────────────────────┐
│    choose path: query_texts OR query_embeddings                      │ │ WHAT THIS MEANS IN YOUR CASE                                         │
│    build response payload                                            │ │ -------------------------------------------------------------------- │
│                                                                      │ │ Your last run supports this split: the missing-file blocker was      │
│    POSSIBLE HANG ZONES HERE:                                         │ │ fixed, dry-run passed, rebuild completed, and only after that did    │
│      B1. request wrapper waits forever                               │ │ the validation query become the problem.                             │
│      B2. server process stale after rebuild                          │ │                                                                      │
│      B3. response serialization on documents/metadatas               │ │ REBUILD PATH                                                         │
│      B4. no timeout / no phase logging                               │ │   normative_requirements_spec.md added                               │
└──────────────────────────────────────────────────────────────────────┘ │       ->                                                             │
                                 │                                       │   ingest_repo_evidence dry-run passed                                │
                                 │ if query_text path                    │       ->                                                             │
                                 ▼                                       │   repo_evidence rebuilt                                              │
┌──────────────────────────────────────────────────────────────────────┐ │       ->                                                             │
│  C. EMBEDDING RUNTIME                                                │ │   2789 -> 3451 chunks                                                │
│  ------------------------------------------------------------------  │ │       ->                                                             │
│  BAAI/bge-m3                                                         │ │   validation query invoked                                           │
│                                                                      │ │       ->                                                             │
│    load model                                                        │ │   apparent hang                                                      │
│    tokenize query                                                    │ │                                                                      │
│    encode query text -> 1024-dim vector                              │ │ SO THE MOST LIKELY FAILURE BAND IS:                                  │
│                                                                      │ │                                                                      │
│    POSSIBLE HANG ZONES HERE:                                         │ │   [ MCP handler ]                                                    │
│      C1. model warmup / reload per request                           │ │        or                                                            │
│      C2. CUDA / CPU device transition                                │ │   [ embedding runtime for query_text ]                               │
│      C3. wrapper says "query" but real delay is embed step           │ │        or                                                            │
│                                                                      │ │   [ full-response serialization ]                                    │
│    DEBUG SPLIT:                                                      │ │                                                                      │
│      query_texts      = MCP wraps embed + query together             │ │ NOT:                                                                 │
│      query_embeddings = you embed first, then query Chroma directly  │ │                                                                      │
└──────────────────────────────────────────────────────────────────────┘ │   [ repo_evidence rebuild mechanics ]                                │
                                 │                                       │                                                                      │
                                 │ query_embeddings                      │ That sequencing is straight from your latest run.                    │
                                 ▼                                       └──────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────┐ ┌──────────────────────────────────────────────────────────────────────┐
│  D. CHROMA CLIENT LAYER                                              │ │ MINIMAL PROBE SEQUENCE                                               │
│  ------------------------------------------------------------------  │ │ -------------------------------------------------------------------- │
│  chromadb.PersistentClient(path="data/cache/chromadb")               │ │ STEP 1                                                               │
│                                                                      │ │   get_collection("repo_evidence").count()                            │
│    client.get_collection("repo_evidence")                            │ │     |                                                                │
│    collection.query(...)                                             │ │     |-- hangs  -> client/server/store issue                          │
│                                                                      │ │     |                                                                │
│    POSSIBLE HANG ZONES HERE:                                         │ │     |-- works  -> continue                                           │
│      D1. stale client after rebuild                                  │ │                                                                      │
│      D2. wrapper using query_texts instead of query_embeddings       │ │ STEP 2                                                               │
│      D3. large include payload slows return                          │ │   embed query only                                                   │
│                                                                      │ │     |                                                                │
│    DEBUG ORDER:                                                      │ │     |-- hangs  -> embedding runtime / model lifecycle issue          │
│      1. get_collection + count                                       │ │     |                                                                │
│      2. query_embeddings + distances only                            │ │     |-- works  -> continue                                           │
│      3. add metadatas                                                │ │                                                                      │
│      4. add documents                                                │ │ STEP 3                                                               │
└──────────────────────────────────────────────────────────────────────┘ │   query_embeddings + include=["distances"]                           │
                                 │                                       │     |                                                                │
                                 │ ANN lookup                            │     |-- hangs  -> direct Chroma query issue                          │
                                 ▼                                       │     |                                                                │
┌──────────────────────────────────────────────────────────────────────┐ │     |-- works  -> continue                                           │
│  E. CHROMA STORE                                                     │ │                                                                      │
│  ------------------------------------------------------------------  │ │ STEP 4                                                               │
│  Persistent store: data/cache/chromadb                               │ │   query_embeddings + include=["distances","metadatas"]               │
│                                                                      │ │     |                                                                │
│    collection: repo_evidence                                         │ │     |-- hangs  -> metadata payload / wrapper issue                   │
│    post-rebuild size: 3451 chunks                                    │ │     |                                                                │
│                                                                      │ │     |-- works  -> continue                                           │
│    WHAT IS ALREADY KNOWN:                                            │ │                                                                      │
│      - repo_evidence dry-run passed                                  │ │ STEP 5                                                               │
│      - rebuild completed cleanly                                     │ │   query_embeddings + include=["distances","metadatas","documents"]   │
│      - collection grew 2789 -> 3451                                  │ │     |                                                                │
│                                                                      │ │     |-- hangs  -> document payload / serialization issue             │
│    THIS MAKES A PURE INDEX-CORRUPTION THEORY LESS LIKELY THAN:       │ │     |                                                                │
│      - embed/runtime stall                                           │ │     |-- works  -> MCP wrapper around query_texts is the problem      │
│      - wrapper/server stall                                          │ └──────────────────────────────────────────────────────────────────────┘
│      - payload serialization stall                                   │ ┌──────────────────────────────────────────────────────────────────────┐
└──────────────────────────────────────────────────────────────────────┘ │ ONE-BOX VERSION FOR SCREENSHOT/DEBUG NOTES                           │
                                                                         │ -------------------------------------------------------------------- │
                                                                         │ CALLER                                                               │
                                                                         │   -> vector_db MCP request                                           │
                                                                         │      -> query handler                                                │
                                                                         │         -> embed query text (bge-m3)                                 │
                                                                         │            -> chromadb PersistentClient                              │
                                                                         │               -> get_collection("repo_evidence")                     │
                                                                         │                  -> ANN query                                        │
                                                                         │                     -> assemble metadatas/documents/distances        │
                                                                         │                        -> return MCP response                        │
                                                                         │                                                                      │
                                                                         │ IF HANG:                                                             │
                                                                         │   1. count()?                                                        │
                                                                         │   2. embed only?                                                     │
                                                                         │   3. query_embeddings + distances only?                              │
                                                                         │   4. add metadatas?                                                  │
                                                                         │   5. add documents?                                                  │
                                                                         └──────────────────────────────────────────────────────────────────────┘