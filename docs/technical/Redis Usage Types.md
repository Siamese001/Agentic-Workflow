AGENTIC SYSTEM — REDIS USAGE TYPES
==================================


REDIS HOT CACHE (LOCAL)                                           REDIS MCP (TOOL INTERFACE)
================================================================================================


Agentic Runtime  (system automatically checking fast memory)      Agent  (LLM reasoning deciding to use a tool)
│                                                                 │
│ needs fast access to ADG / embeddings / retrieval results       │ agent decides Redis interaction is needed
▼                                                                 ▼
+--------------------------------------+                          +-----------------------------------+
| LOCAL REDIS SERVER                   |                          | MCP TOOL: redis                   |
|--------------------------------------|                          |-----------------------------------|
| key → value store                    | librarian index drawer   | get(key)                          | assistant retrieves book
| ADG fragments                        | dependency map binder    | set(key,value)                    | assistant places book on cart
| semantic cache                       | frequently used notes    | scan()                            | assistant searches cart
| RAG retrieval results                | research summary cards   | delete()                          | assistant removes book
| routing hints                        | librarian routing notes  | publish(channel,msg)              | assistant broadcasts msg
| TTL eviction                         | rotating book cart       |                                   |
+--------------------------------------+                          +-----------------------------------+



TECHNICAL ROLE                                                    TECHNICAL ROLE
in-memory runtime cache (automatic lookup)                        tool adapter allowing agent to access Redis
front desk cart checked before walking to archives                librarian assistant executing a requested task


TOKEN & CONTEXT IMPACT                                            TOKEN & CONTEXT IMPACT
Low Token Cost: Resolved before prompting                         High Token Cost: Results injected into context
Only final synthesized data consumes context window               Agent must "read" the raw JSON/text output



DATA FLOW                                                         CALL FLOW
runtime code executes lookup                                      agent reasoning decides to call tool
│                                                                 │
▼                                                                 ▼
check redis cache                                                 tool call issued
│                                                                 │
├── cache hit → return result instantly                           MCP tool registry routes request
│    (librarian finds book on desk cart)                          (circulation desk directs assistant)
│
└── cache miss → query FAISS / ADG / disk                         Redis MCP handler executes command
       (librarian walks to deep archive shelves)                  (assistant performs the action)
            │                                                          │
            ▼                                                          ▼
      write result back to redis                                  Redis server executes command
      (place book onto cart for next visitor)                     (book retrieved, stored, or published)
                                                                       │
                                                                       ▼
                                                                  result returned to agent



EXAMPLE KEYS                                                      EXAMPLE KEYS
rag:query_hash → top_k_documents                                  agent_memory:client:acme
cached RAG retrieval result (note card on cart)                   "client prefers Gemini"

adg:module:validator                                              workflow:run:123
dependency graph node cached                                      "step2_completed"

tool_result:repo_scan                                             analysis:task_445:step1
cached repository structure                                       "ADG anomaly detected"
