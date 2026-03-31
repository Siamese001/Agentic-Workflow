+---------------------------------------------------------------------------------------+
|                              The Library (Target Codebase)                            |
+---------------------------------------------------------------------------------------+
                                            |
+===========================================v===========================================+
|                      PHASE 1: THE CATALOGING (ADG) ERROR ZONES                        |
|                     (The limits of Macro-Topology & Telemetry)                        |
+=======================================================================================+
                                            |
               +----------------------------+----------------------------+
               |                                                         |
+--------------v---------------+                          +--------------v---------------+
|  ADG SCENARIO A: The Noise   |                          |  ADG SCENARIO B: The Blind   |
| (Reads structural topology)  |                          |  (Misses dynamic execution)  |
+------------------------------+                          +------------------------------+
| ADG sees static `import`     |                          | ADG sees zero explicit calls |
| statements but zero executed |                          | because test execution is    |
| test pathways.               |                          | driven by fixtures/mocks.    |
|                              |                          |                              |
| Flags: "Needs Enhancement"   |                          | Flags: "Isolated/No Tests"   |
+--------------+---------------+                          +--------------+---------------+
               |                                                         |
+--------------v---------------+                          +--------------v---------------+
|     < FALSE POSITIVE >       |                          |     < FALSE NEGATIVE >       |
| e.g., __init__.py markers or |                          | e.g., test_heal_telemetry.py |
| dead-code static imports.    |                          | fully written, dynamic test. |
| (The 220 structural files).  |                          | (The actual behavioral files)|
+--------------+---------------+                          +--------------+---------------+
               |                                                         |
               +----------------------------+----------------------------+
                                            |
                                (Batch of Suspect Files)
                                            |
+===========================================v===========================================+
|                PHASE 2: L5 RECONCILIATION & AST EXECUTION (The Cure)                  |
+=======================================================================================+
                                            |
               +----------------------------v----------------------------+
               | System Bus routes suspects to Execution Persona (AST)   |
               | Strict Authority Boundary: AST physically reads source. |
               +----------------------------+----------------------------+
                                            |
               +----------------------------+----------------------------+
               |                                                         |
+--------------v---------------+                          +--------------v---------------+
|  CURING THE FALSE POSITIVE   |                          |  CURING THE FALSE NEGATIVE   |
+------------------------------+                          +------------------------------+
| AST dynamically filters out  |                          | AST parsing ignores dynamic  |
| structural files & counts    |                          | execution illusions & proves |
| the internal `FunctionDefs`. |                          | the logic exists on disk.    |
|                              |                          |                              |
| Result: 0 test methods found.|                          | Result: >0 test methods.     |
+--------------+---------------+                          +--------------+---------------+
               |                                                         |
+--------------v---------------+                          +--------------v---------------+
|  UWG MUTATION (Discard/Trim) |                          |    UWG MUTATION (Override)   |
| "AST proves no logic exists. |                          | "AST proves logic exists.    |
| Discard ADG structural noise |                          | Override ADG blind spot; mark|
| from the enhancement queue." |                          | as true Behavioral Test."    |
+--------------+---------------+                          +--------------+---------------+
               |                                                         |
               +----------------------------+----------------------------+
                                            |
+===========================================v===========================================+
|                           PHASE 3: DETERMINISTIC TRUTH                                |
+---------------------------------------------------------------------------------------+
|                                Verified C0 Context                                    |
|                      (The True Target Files for Enhancement)                          |
+---------------------------------------------------------------------------------------+