MENTAL MODEL — DEPENDENCY GRAPH vs GRAPH DATABASE

CATEGORY            DEPENDENCY GRAPH                                   GRAPH DATABASE
------------------------------------------------------------------------------------------------------------
Purpose             Analyze structure of code                          Store and query relationships

What nodes are      Files / modules / classes                          Real entities (users, docs,
                                                                        systems, agents)

What edges mean     Code dependency                                    Relationship between entities
                    (imports / calls)                                  (knows, uses, owns, etc.)

Example nodes       main.py                                            (Amit)
                    agent.py                                           (Agentic Platform)
                    memory.py                                          (Embedding Model)

Example edges       agent.py → memory.py                               (Amit) ─WORKS_WITH→ (Platform)
                    memory.py → vector_store.py                        (Platform) ─USES→ (Embedding)

Flowchart           main.py                                            (Amit)
                    │                                                   │
                    ▼                                                   ▼
                    agent.py                                ─WORKS_WITH→ (Agentic Platform)
                    │                                                   │
                    ▼                                                   ▼
                    memory.py                                  ─USES→ (Embedding Model)
                    │
                    ▼
                    vector_store.py

Typical tools       dependency analyzers                               Neo4j, TigerGraph,
                    static analysis                                    Amazon Neptune

Typical uses        • refactoring safely                               • knowledge graphs
                    • architecture diagrams                            • recommendation engines
                    • blast radius analysis                            • fraud detection
                    • import analysis                                  • relationship queries

Key idea            Map of "who needs who" in code                     Database designed for
                                                                        relationship queries
