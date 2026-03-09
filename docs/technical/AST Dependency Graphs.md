==========================================================================================================
1) IMPORT GRAPH                     2) FUNCTION CALL GRAPH                3) CLASS INHERITANCE GRAPH
==========================================================================================================

app.py ─────────▶ service.py        main() ─────────▶ create_user()        BaseAgent
service.py ─────▶ repo.py           create_user() ───▶ save_user()             ▲
repo.py ────────▶ db.py             save_user() ─────▶ insert_row()             │
                                                                         ChildAgent
                                                                              ▲
                                                                              │
                                                                         MetricsAgent


Edges represent:                  Edges represent:                      Edges represent:
file/module imports               one function calling another          a class extending another class

AST nodes used:                   AST nodes used:                       AST nodes used:
Import / ImportFrom               Call() nodes                          ClassDef bases

Purpose:                          Purpose:                              Purpose:
map module dependencies           map execution flow                    map object hierarchy

Typical use:                      Typical use:                          Typical use:
• detect circular imports         • trace runtime paths                 • understand agent taxonomy
• enforce layer rules             • find dead code                      • enforce framework contracts
• measure blast radius            • debugging traces                    • detect misuse of base classes


==========================================================================================================
4) MODULE / COMPONENT GRAPH        5) SYMBOL / ATTRIBUTE GRAPH           6) OBJECT COMPOSITION GRAPH
==========================================================================================================

RoutingLayer ───▶ ExecutionLayer   service.py ───▶ settings.DB_URL       Agent
ExecutionLayer ─▶ SafetyLayer      repo.py ──────▶ models.User             │
RAGLayer ───────▶ EmbeddingLayer   agent.py ─────▶ validator.check()       ▼
                                                                      MemoryStore
                                                                          │
                                                                          ▼
                                                                      ToolRegistry


Edges represent:                  Edges represent:                      Edges represent:
subsystem using another           reference to a variable, class,       object containing or using
architectural component           attribute, or function                another object

AST nodes used:                   AST nodes used:                       AST nodes used:
module import aggregation         Attribute(), Name()                   Assign(), constructor calls

Purpose:                          Purpose:                              Purpose:
show architecture-level           trace precise symbol usage            show internal object structure
dependencies                      across the codebase                   inside classes

Typical use:                      Typical use:                          Typical use:
• layer governance                • config tracing                      • understand component wiring
• detect forbidden imports        • secret / env usage scanning         • detect tight coupling
• visualize system structure      • dependency auditing                 • architecture refactoring


==========================================================================================================
HOW AST PRODUCES THESE GRAPHS
==========================================================================================================

source code
     │
     ▼
AST parser
     │
     ▼
AST nodes extracted
     │
     ├── Import / ImportFrom
     ├── Call
     ├── ClassDef
     ├── Attribute
     └── Assignment / construction
     │
     ▼
edges created between nodes
     │
     ▼
dependency graphs
