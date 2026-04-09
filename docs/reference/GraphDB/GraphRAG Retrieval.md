+--------------------------------------------------------------------------------+
|                             THE CLEAN RULES                                    |
|--------------------------------------------------------------------------------|
| * Truth lives strictly in SQLite                                               |
| * Traversal lives strictly in GraphDB                                          |
| * GraphRAG strictly uses the GraphDB projection                                |
| * Leverages the best of all three: truth, graph-native speed, & better context |
+--------------------------------------------------------------------------------+
                                       |
                                       | (Defines Architecture)
                                       v
+--------------------------------------------------------------------------------+
|                          LAYER 1: CANONICAL STORAGE                            |
|                                   SQLITE                                       |
|--------------------------------------------------------------------------------|
| * Acts as canonical ADG truth                                                  |
| * Functions as a deterministic artifact                                        |
| * Hosts CI / ratchets / baselines                                              |
| * Preserves absolute truth and determinism                                     |
| * Optimized for canonical storage and reporting (not traversal)                |
+--------------------------------------------------------------------------------+
                  |                                        |
                  | (One-Way Data Projection)              | (BYPASS ATTEMPT)
                  v                                        v
+-----------------------------------+    +---------------------------------------+
|    LAYER 2: TRAVERSAL SURFACE     |    |         [!] ANTI-PATTERN [!]          |
|        GRAPHDB PROJECTION         |    |      DIRECT GRAPHRAG -> SQLITE        |
|-----------------------------------|    |---------------------------------------|
| * Traversal-optimized surface     |    | * Forces retrieval to do graph work   |
| * Shortest path calculations      |    | * Hits storage unoptimized for graphs |
| * k-hop neighborhoods             |    | * Makes retrieval heavier             |
| * Blast radius analysis           |    | * Makes retrieval noisier             |
| * Snapshot topology diffs         |    | * Makes retrieval less explainable    |
| * Gives efficient graph traversal |    | * Violates the "Clean Rule"           |
+-----------------------------------+    +---------------------------------------+
                  |                                        |
                  | (Graph Traversal Results)              | (BLOCKED PATH)
                  v                                        X
+--------------------------------------------------------------------------------+
|                       LAYER 3: RETRIEVAL & ORCHESTRATION                       |
|                                    GRAPHRAG                                    |
|--------------------------------------------------------------------------------|
| * Retrieval/orchestration layer                                                |
| * Uses graph traversal results from GraphDB                                    |
| * Assembles the right graph context for the LLM                                |
| * Keeps retrieval lightweight and highly explainable                           |
+--------------------------------------------------------------------------------+
                                       |
                                       | (Enriched Context + User Query)
                                       v
+--------------------------------------------------------------------------------+
|                              LAYER 4: SYNTHESIS                                |
|                              LLM / AGENT ANSWER                                |
|--------------------------------------------------------------------------------|
| * Receives perfectly assembled graph context                                   |
| * Generates grounded, highly-contextualized final answer                       |
+--------------------------------------------------------------------------------+
                                       |
                                       | (Flowchart Dependency Tests)
                                       v
+--------------------------------------------------------------------------------+
|                        LAYER 5: TEST ON FLOWCHART                              |
|                          VALIDATION DEPENDENCIES                               |
|--------------------------------------------------------------------------------|
| * TEST: Confirm SQLite deterministic baselines hold in CI                      |
| * TEST: Verify GraphDB projection accuracy (topology diffs check out)          |
| * TEST: Ensure GraphRAG is exclusively calling GraphDB, zero direct SQLite IO  |
+--------------------------------------------------------------------------------+