================================================================================================================================================================
                                  CHROMA ROUTER — HOW IT SHOULD WORK IN YOUR SYSTEM
                      [L0 = ROUTING AUTHORITY / Front Desk]   [C0 = TEMP CONTEXT DESK]   [L4 = STORED COLLECTIONS / Archive]
================================================================================================================================================================

[ USER QUERY ]
     |
     v
+-----------------------------+
| 🤖 L1 INTENT READ           |
| "What is this asking for?"  |
| - architecture?             |
| - best practice?            |
| - policy/safety?            |
| - retrieval/RAG?            |
| - MCP/tool contracts?       |
| - code/symbol lookup?       |
+-----------------------------+
     |
     v
+--------------------------------------------------------------------+
| 🚦 L0 ROUTER / FRONT DESK DISPATCHER                               |
| Routing authority only                                             |
| Decides DOMAIN KEY + PRIMARY COLLECTION + FALLBACK                 |
|                                                                    |
| architecture / policy / history / standards  -> curated_agent_docs |
| best_practice / orchestration / RAG         -> curated_agent_docs |
| MCP / FastMCP / tool_contracts              -> curated_agent_docs |
| code / implementation / symbol lookup       -> arch_docs          |
| external broad fallback only                -> ext_knowledge      |
+--------------------------------------------------------------------+
     |
     +-------------------------- primary route --------------------------+
     |                                                                  |
     v                                                                  v
+----------------------------------+                        +----------------------------------+
| 📚 curated_agent_docs            |                        | 📚 arch_docs                     |
| Canonical / high-signal          |                        | Broad internal repo coverage     |
| Best for architecture, policy,   |                        | Best for code-level identifiers, |
| best-practice, orchestration,    |                        | implementation details, symbols  |
| retrieval, MCP/tool contracts    |                        | and breadth-heavy lookups        |
+----------------------------------+                        +----------------------------------+
     |                                                                  |
     +-----------------------------------+------------------------------+
                                         |
                                         v
                           +-----------------------------------+
                           | 🔎 BUILD CHROMA QUERY             |
                           | query_texts=[user_query]          |
                           | n_results = K + oversample        |
                           | where = metadata prefilter        |
                           |                                   |
                           | examples:                         |
                           | - canonical=True                  |
                           | - topic_bucket in [...]           |
                           | - doc_family in [...]             |
                           | - exclude noisy families          |
                           +-----------------------------------+
                                         |
                                         v
                           +-----------------------------------+
                           | 🧠 CHROMA FIRST PASS              |
                           | returns top N candidate chunks    |
                           | by vector similarity              |
                           +-----------------------------------+
                                         |
                                         v
+==============================================================================================================================================================+
|                                                      LIVE-PATH POST-PROCESSING                                                                  |
+==============================================================================================================================================================+
| 1. AUTHORITY RERANK                                                                                                                             |
|    Boost stronger sources upward                                                                                                                |
|    Example: constitutional.md outranks weaker pattern docs for policy queries                                                                   |
|                                                                                                                                               |
| 2. COLLAPSE-GROUP DEDUP                                                                                                                         |
|    Prevent one source family from flooding top-K                                                                                                |
|    Example: max 2 chunks from MCP SDK / LangGraph / AutoGen group                                                                              |
|    This is now part of the live path for best_practice + tool_contracts style queries                                                          |
|                                                                                                                                               |
| 3. FINAL TRUNCATE TO K                                                                                                                          |
|    Keep the best, most diverse, most authoritative K chunks                                                                                     |
+==============================================================================================================================================================+
                                         |
                                         v
+--------------------------------------------------------------------+
| 🔍 C0 CONTEXT DESK / TEMP READING STACK                            |
| Read-only temporary assembly                                       |
| - stitch adjacent context if needed                                |
| - keep citations / chunk manifest                                  |
| - no routing authority                                              |
| - no write authority                                                |
+--------------------------------------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------+
| 🤖 L1 ANSWER CONSTRUCTION                                           |
| Uses only returned evidence                                         |
| - summarize                                                         |
| - explain                                                           |
| - answer                                                            |
+--------------------------------------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------+
| ❓ FALLBACK RULES                                                    |
| if curated_agent_docs unavailable or weak:                          |
|    1. for architecture/policy/history -> fallback to arch_docs      |
|    2. for broad external standards gaps -> fallback to ext_knowledge|
|    3. never default architecture straight to ext_knowledge          |
+--------------------------------------------------------------------+