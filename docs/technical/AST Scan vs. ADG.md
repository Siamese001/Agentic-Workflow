====================================================================================================================
AST SCAN                                                  | ADG (AST DEPENDENCY GRAPH)
====================================================================================================================

PURPOSE                                                   | PURPOSE
Analyze structure of ONE file                             | Model relationships across ENTIRE repository
ANALOGY: Inspect one building blueprint                   | ANALOGY: City infrastructure map
                                                           |
--------------------------------------------------------------------------------------------------------------------
SCOPE                                                     | SCOPE
Single file                                               | Whole codebase
ANALOGY: Room-by-room inspection                          | ANALOGY: Google Maps view of the whole city
                                                           |
--------------------------------------------------------------------------------------------------------------------
INPUT                                                     | INPUT
Source file → parsed into syntax tree                     | All files → AST scans aggregated into dependency graph
ANALOGY: Architect drawing one building                   | ANALOGY: Urban planner collecting all blueprints
                                                           |
--------------------------------------------------------------------------------------------------------------------
OUTPUT                                                    | OUTPUT
Tree structure                                            | Graph structure
                                                           |
Example                                                   | Example
                                                           |
Module                                                    | nodes:
 └─ Function add()                                        |   files
    └─ Return a + b                                       |   classes
ANALOGY: Family tree of code                              |   functions
                                                           |
                                                           | edges:
                                                           |   imports
                                                           |   function calls
                                                           |   inheritance
                                                           |   type references
                                                           |
                                                           | ANALOGY: Road network connecting buildings
--------------------------------------------------------------------------------------------------------------------
QUESTIONS IT ANSWERS                                      | QUESTIONS IT ANSWERS
"What exists inside this file?"                           | "How does the system connect?"
                                                           |
ANALOGY:                                                  | ANALOGY:
What rooms exist in the building?                         | Which roads connect all buildings?
                                                           |
--------------------------------------------------------------------------------------------------------------------
VISIBILITY LEVEL                                          | VISIBILITY LEVEL
Local structural view                                     | Global architectural view
ANALOGY: Standing inside a single building                | ANALOGY: Satellite map of an entire city
--------------------------------------------------------------------------------------------------------------------
TYPICAL USES                                              | TYPICAL USES
Linting                                                   | Refactoring safety
Security scans                                            | Test impact analysis
Pattern detection                                         | Dependency analysis
Code metrics                                              | Architecture visualization
                                                           | Agentic code navigation
                                                           |
ANALOGY: Building inspection                              | ANALOGY: Traffic control system
--------------------------------------------------------------------------------------------------------------------
RUNTIME ROLE                                              | RUNTIME ROLE
Usually static analysis only                              | Used by orchestration / tooling / agents
ANALOGY: Pre-construction inspection                      | ANALOGY: City traffic system directing vehicles
--------------------------------------------------------------------------------------------------------------------
EXAMPLE VIEW                                              | EXAMPLE VIEW

AST scan sees:                                            | ADG sees:

file_a.py                                                 | test_user.py
  └ import service                                        |      │
                                                           |      ▼
                                                           | create_user()
                                                           |      │
                                                           |      ▼
                                                           | db.insert()

ANALOGY:                                                  | ANALOGY:
Blueprint shows a staircase                               | City map shows the highway chain connecting buildings

====================================================================================================================
KEY DISTINCTION
====================================================================================================================

AST Scan:
• analyzes code structure within a single file
• produces a syntax tree
• used for linting, validation, and local inspection

ADG:
• aggregates AST results across the entire repository
• produces a dependency graph of system relationships
• enables refactoring intelligence, test impact analysis, and agentic code navigation

ANALOGY SUMMARY

AST Scan = Inspecting one building blueprint
ADG       = Mapping the entire city road network
====================================================================================================================