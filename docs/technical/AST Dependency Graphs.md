```
================================================================================================================================================================================
AST GRAPH TAXONOMY — ZERO LOSS OVERWRITE (COMPACT)
================================================================================================================================================================================

1) IMPORT GRAPH                          2) FUNCTION CALL GRAPH                   3) CLASS INHERITANCE GRAPH
================================================================================================================================================================================
WHAT IT SHOWS                            WHAT IT SHOWS                            WHAT IT SHOWS
File / module dependency flow            Runtime call flow between functions      Parent-child class hierarchy

VISUAL FLOW                              VISUAL FLOW                              VISUAL FLOW
app.py ──▶ service.py                    main() ──▶ create_user()                 BaseAgent
   │                                        │                                      ▲
   └──▶ repo.py ──▶ db.py                   └──▶ save_user() ──▶ insert()          │
                                                                                ChildAgent
                                                                                   ▲
                                                                                   │
                                                                                MetricsAgent

EDGE MEANING                             EDGE MEANING                             EDGE MEANING
Module A imports Module B                Function A calls Function B             Class A extends Class B

PRIMARY AST SIGNALS                      PRIMARY AST SIGNALS                      PRIMARY AST SIGNALS
Import / ImportFrom                      Call()                                   ClassDef
                                                                                bases

PURPOSE                                  PURPOSE                                  PURPOSE
Map static module dependencies           Map execution behavior                   Map object model structure

TYPICAL USES                             TYPICAL USES                             TYPICAL USES
• Detect circular imports                • Trace runtime paths                    • Understand agent taxonomy
• Enforce layer rules                    • Find dead code                         • Enforce framework contracts
• Measure blast radius                   • Debug stack behavior                   • Detect misuse of base classes


4) MODULE / COMPONENT GRAPH              5) SYMBOL / ATTRIBUTE GRAPH              6) OBJECT COMPOSITION GRAPH
================================================================================================================================================================================
WHAT IT SHOWS                            WHAT IT SHOWS                            WHAT IT SHOWS
Subsystem dependency flow                Exact symbol / attribute references      Objects containing or wiring other objects

VISUAL FLOW                              VISUAL FLOW                              VISUAL FLOW
RoutingLayer ──▶ ExecutionLayer          service.py ──▶ settings.DB_URL           Agent
     │                 │                 repo.py ──▶ models.User                   │
     ▼                 ▼                 agent.py ──▶ validator.check()            ├──▶ MemoryStore
RAGLayer ──▶ EmbeddingLayer                                                      │
                                                                                └──▶ ToolRegistry

EDGE MEANING                             EDGE MEANING                             EDGE MEANING
Component A depends on B                 Code references variable / class / fn   Object owns or instantiates another object

PRIMARY AST SIGNALS                      PRIMARY AST SIGNALS                      PRIMARY AST SIGNALS
Import aggregation                       Attribute()                              Assign()
Module grouping                          Name()                                   AnnAssign()
                                                                                constructor Call()

PURPOSE                                  PURPOSE                                  PURPOSE
Show architecture dependencies           Trace precise usage points               Show internal object wiring

TYPICAL USES                             TYPICAL USES                             TYPICAL USES
• Layer governance                       • Config tracing                         • Understand component wiring
• Detect forbidden imports               • Secret / env usage scanning            • Detect tight coupling
• Visualize system structure             • Dependency auditing                    • Architecture refactoring


================================================================================================================================================================================
HOW AST PRODUCES THESE GRAPHS
================================================================================================================================================================================
[ Source Code Files ]
        │
        ▼
[ AST Parser ]
        │
        ▼
[ AST Nodes Extracted ]
        │
        ├─ Import / ImportFrom      → builds IMPORT GRAPH
        ├─ Call()                   → builds FUNCTION CALL GRAPH
        ├─ ClassDef + bases         → builds CLASS INHERITANCE GRAPH
        ├─ Name() / Attribute()     → builds SYMBOL / ATTRIBUTE GRAPH
        ├─ Assign() + constructor   → builds OBJECT COMPOSITION GRAPH
        └─ module grouping          → builds MODULE / COMPONENT GRAPH
        │
        ▼
[ Edge Extraction Rules ]
        │
        ▼
[ Graph Nodes + Edges ]
        │
        ▼
[ Dependency Graph Family ]


================================================================================================================================================================================
QUICK DISTINCTION
================================================================================================================================================================================
IMPORT GRAPH              = file/module dependencies
FUNCTION CALL GRAPH       = runtime execution flow
CLASS INHERITANCE GRAPH   = class hierarchy
MODULE GRAPH              = subsystem dependencies
SYMBOL GRAPH              = exact variable / attribute references
OBJECT COMPOSITION GRAPH  = object containment / wiring


================================================================================================================================================================================
MENTAL MODEL
================================================================================================================================================================================
STATIC STRUCTURE AXIS
Import Graph
Class Inheritance Graph
Module / Component Graph
Symbol / Attribute Graph
Object Composition Graph

DYNAMIC EXECUTION AXIS
Function Call Graph

AST → syntax tree of code
Graphs → different projections extracted from that tree
```
