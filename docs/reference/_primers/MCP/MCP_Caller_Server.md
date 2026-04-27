┌──────────────────────────────┐      Example caller files:
│ CALLER                       │<----- - deterministic script
│ MCP client runtime           │      - app runtime
│ in script/app/agent          │      - agent framework
│ (not this file)              │
└──────────────┬───────────────┘
               │ 1) "What can you do?"
               v
┌──────────────────────────────┐      File: tools/mcp/vector_db_server.py
│ MCP SERVER                   │<----- Symbol: mcp = create_mcp_server(...)
│ exposes tools                │      Tools registered here:
│ and resources                │      create_collection, add_documents,
│                              │      query_collection, semantic_search, etc.
└──────────────┬───────────────┘
               │ 2) "Here are my tools/resources"
               v
┌──────────────────────────────┐      Caller now knows available tools from:
│ CALLER                       │<----- tools/mcp/vector_db_server.py
│ now knows what exists        │
│ and their schemas            │
└──────────────┬───────────────┘
               │ 3) "Run this tool with these args"
               v
┌──────────────────────────────┐      File: tools/mcp/vector_db_server.py
│ MCP SERVER                   │<----- Thin MCP wrapper / adapter
│ validates + runs it          │      Then calls:
│                              │      from tools.retrieval.vector_service
│                              │      import get_vector_service
└──────────────┬───────────────┘
               │
               v
┌──────────────────────────────┐      File: tools/retrieval/vector_service.py
│ REAL VECTOR SERVICE          │<----- Symbol: get_vector_service()
│ actual retrieval logic       │      format_semantic_search(...)
│ lives here                   │      format_query_collection(...)
│                              │      format_add_documents(...)
└──────────────┬───────────────┘
               │
               v
┌──────────────────────────────┐      Backend files/modules referenced:
│ VECTOR BACKEND               │<----- tools.retrieval.vector_store
│ Chroma + embedder + config   │      tools.retrieval.vector_config
│ do the actual work           │      Chroma client / embedding model
└──────────────┬───────────────┘
               │ 4) "Here is the result"
               v
┌──────────────────────────────┐      Result formatted back through:
│ CALLER                       │<----- tools/mcp/vector_db_server.py
│ uses result next             │      as string output or translated error
└──────────────────────────────┘