=========================================================================================================
                                 THE ADG MENTAL MODEL & ARCHITECTURE
=========================================================================================================
BOTTOM LINE: SQLite ADG stores the exact graph, Redis ADG serves graph answers quickly, 
             and ChromaDB translates messy human language into likely graph targets.
=========================================================================================================

┌─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
│           SQLITE ADG            │            REDIS ADG            │            CHROMADB             │
│          (Exact Truth)          │      (Fast Graph Serving)       │ (Fuzzy Language-to-Graph Bridge)│
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ [INTENT]                        │ [INTENT]                        │ [INTENT]                        │
│ "What is actually true in the   │ "Give me the nearby graph       │ "The user said something vague. │
│  graph?"                        │  fast."                         │  What graph thing do they       │
│                                 │                                 │  probably mean?"                │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ [ACTOR]                         │ [ACTOR]                         │ [ACTOR]                         │
│  Analyst / System               │  Runtime / App                  │  Natural Language Query         │
│        │                        │        │                        │        │                        │
│        ▼                        │        ▼                        │        ▼                        │
│ ┌───────────────┐               │ ┌───────────────┐               │ ┌───────────────────────────┐   │
│ │ SQLite ADG    │               │ │ Redis ADG     │               │ │ Chroma Embeddings/Search  │   │
│ │ Canonical DB  │               │ │ Hot Graph     │               │ │ Semantic Similarity       │   │
│ └──────┬────────┘               │ └──────┬────────┘               │ └──────────┬────────────────┘   │
│        │                        │        │                        │            │                    │
│        ▼                        │        ▼                        │            ▼                    │
│ [CAPABILITIES]                  │ [CAPABILITIES]                  │ [CAPABILITIES]                  │
│ • Exact joins                   │ • Neighbor lookup               │ • Likely node/module candidates │
│ • Reachability verification     │ • Adjacency expansion           │ • Concept matching              │
│ • Rule violations               │ • Cached graph answers          │ • "Sounds like..." mapping      │
│ • Diff generation               │ • Low-latency serving           │                                 │
│ • Deterministic evidence        │                                 │                                 │
│        │                        │        │                        │            │                    │
│        ▼                        │        ▼                        │            ▼                    │
│ [THE DIRECTIVE]                 │ [THE DIRECTIVE]                 │ [THE DIRECTIVE]                 │
│ "Prove it."                     │ "Serve it now."                 │ "Map words to graph territory." │
└─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘

=========================================================================================================
                                     FULL SYSTEM INTEGRATION FLOW
=========================================================================================================

                                       [ USER ASKS QUESTION ]
                                                 │
                                                 ▼
                                      "Find the thing I mean"
                                                 │
                                                 ▼
                               ┌───────────────────────────────────┐
                               │             CHROMADB              │
                               │ Fuzzy language -> graph territory │
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                               (Candidate Nodes / Modules / Symbols)
                                                 │
                                  ┌──────────────┴──────────────┐
                                  │                             │
                                  ▼                             ▼
                        ┌───────────────────┐         ┌───────────────────┐
                        │     REDIS ADG     │         │    SQLITE ADG     │
                        │ Fast expansion    │         │ Exact verification│
                        │ Nearby nodes      │         │ True edges/paths  │
                        │ Hot-path serve    │         │ Violations/proof  │
                        └─────────┬─────────┘         └─────────┬─────────┘
                                  │                             │
                                  └──────────────┬──────────────┘
                                                 ▼
                                  [ FAST ANSWER BACKED BY TRUTH ]

=========================================================================================================
                                       ONE-LINE MEMORY HOOK
=========================================================================================================
  • SQLite ADG = "What IS true?"
  • Redis ADG  = "What is NEARBY, fast?"
  • ChromaDB   = "What did the user PROBABLY mean?"

=========================================================================================================
                                   EXAMPLE: "WHERE DOES X LIVE?"
=========================================================================================================

[ USER QUERY ] "Where does healing retry logic live?"
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CHROMADB                                                                │
│ Semantic Match: "healing retry logic" -> heal loop, retry, recovery     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ▼
                     [ Likely Graph Targets Returned ]
                     • healing_tier_router
                     • healing_tier_dispatcher
                     • l2_evaluate_and_heal
                                     │
                  ┌──────────────────┴──────────────────┐
                  ▼                                     ▼
┌───────────────────────────────────┐ ┌───────────────────────────────────┐
│ REDIS ADG                         │ │ SQLITE ADG                        │
│ Expand callers, neighbors, hops   │ │ Confirm exact modules/functions   │
└─────────────────┬─────────────────┘ └─────────────────┬─────────────────┘
                  └──────────────────┬──────────────────┘
                                     ▼
                    [ ANSWER WITH EXACT GRAPH EVIDENCE ]