====================================================================================================================
AST SCAN                                             | ADG (AST DEPENDENCY GRAPH)
====================================================================================================================
Purpose                                             | Purpose
Analyze structure of ONE file                       | Model relationships across ENTIRE repo
ANALOGY: Inspect one building blueprint             | ANALOGY: City infrastructure map
                                                    |
--------------------------------------------------------------------------------------------------------------------
Scope                                               | Scope
Single file                                         | Whole codebase
ANALOGY: Room-by-room inspection                    | ANALOGY: Google Maps view of the whole city
                                                    |
--------------------------------------------------------------------------------------------------------------------
Input                                               | Input
Source file → parsed into syntax tree               | All files → AST scans aggregated
ANALOGY: Architect drawing one building             | ANALOGY: Urban planner collecting all blueprints
                                                    |
--------------------------------------------------------------------------------------------------------------------
Output                                              | Output
Tree structure                                      | Graph structure
                                                    |
Example                                             | Example
                                                    |
Module                                              | nodes:
 └─Function add()                                   |   files
    └─Return a+b                                    |   classes
ANALOGY: Family tree of code                        |   functions
                                                    | edges:
                                                    |   imports
                                                    |   calls
                                                    |   inheritance
                                                    |
                                                    | ANALOGY: Road network between buildings
--------------------------------------------------------------------------------------------------------------------
Questions it answers                                | Questions it answers
"What exists in this file?"                         | "How does the system connect?"
                                                    |
ANALOGY:                                            | ANALOGY:
What rooms exist in the building?                   | Which roads connect all buildings?
                                                    |
--------------------------------------------------------------------------------------------------------------------
Typical Uses                                        | Typical Uses
                                                    |
Linting                                             | Refactoring safety
Security scans                                      | Test impact analysis
Pattern detection                                   | Agentic code navigation
Code metrics                                        | Dependency visualization
                                                    |
ANALOGY: Building inspection                        | ANALOGY: Traffic control system
--------------------------------------------------------------------------------------------------------------------
Example                                             | Example
                                                    |
AST scan sees:                                      | ADG sees:
                                                    |
file_a.py                                           | test_user.py
  └ import service                                  |      │
                                                    |      ▼
                                                    | create_user()
                                                    |      │
                                                    |      ▼
                                                    | db.insert()
                                                    |
ANALOGY:                                            | ANALOGY:
Blueprint shows a staircase                         | City map shows highway chain
====================================================================================================================