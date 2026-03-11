AST vs ADG (Simple Side-by-Side)

┌──────────────────────────────────────────────┬─────────────────────────────────────────────────────┐
│ AST (Abstract Syntax Tree)                   │ ADG (AST Dependency Graph)                          │
├──────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
│ Shows structure of ONE file                  │ Shows relationships across MANY files               │
│                                              │                                                     │
│ Python code                                  │ Entire repository                                   │
│                                              │                                                     │
│ def add(a,b):                                │ add() used by:                                      │
│     return a+b                               │   service.py                                        │
│                                              │   api.py                                            │
│                                              │   tests/test_add.py                                 │
├──────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
│ ASCII Structure                              │ ASCII Dependency Map                                │
│                                              │                                                     │
│ FunctionDef                                  │  service.py                                         │
│  ├─ arguments                                │       │                                             │
│  └─ return                                   │       ▼                                             │
│       └─ BinOp (+)                           │      add()                                          │
│                                              │       ▲                                             │
│                                              │       │                                             │
│                                              │   test_add.py                                       │
├──────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
│ What it answers                              │ What it answers                                     │
│                                              │                                                     │
│ "What is inside this code?"                  │ "What code depends on this?"                        │
│ "What variables/functions exist?"             │ "What breaks if I change this?"                     │
│ "How is the syntax structured?"               │ "What tests cover this function?"                   │
├──────────────────────────────────────────────┼─────────────────────────────────────────────────────┤
│ Analogy                                      │ Analogy                                             │
│                                              │                                                     │
│ Blueprint of ONE room in a house             │ City map showing roads between buildings            │
│                                              │                                                     │
│ Or                                           │ Or                                                  │
│                                              │                                                     │
│ Sentence grammar tree                        │ Social network graph                                │
│                                              │                                                     │
│ "subject → verb → object"                    │ "who talks to who"                                  │
└──────────────────────────────────────────────┴─────────────────────────────────────────────────────┘