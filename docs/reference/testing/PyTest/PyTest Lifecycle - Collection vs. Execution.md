=================================================================================================
                            PYTEST EXECUTION DECISION TREE & LIFECYCLE
                     (Fully Integrated Librarian Governance & Agentic Routing)
=================================================================================================

+-----------------------------------------------------------------------------------------------+
| 1. INITIALIZATION & CONFIGURATION (C0 / Meta-Learning Roles)                                  |
| Loads global configurations, plugins, and root directory constraints.                         |
| Reads `pytest.ini`, `pyproject.toml`, and root `conftest.py`.                                 |
+---------------------------------------+-------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------------------+
| 2. DISCOVERY & COLLECTION (Retrieval Personas)                                                |
| Scans the directory tree recursively to build the test suite manifest.                        |
| MUST survive module imports to parse Abstract Syntax Trees (AST).                             |
+---------------------------------------+-------------------------------------------------------+
                                        |
      [Decision: Import test module to inspect contents]
       |
       ├─► [ PATH A: THE PATHOLOGY - FATAL EARLY EXIT ] ❌
       |    │
       |    ├─ import test_module_A.py
       |    │   └─ top-level import broken_app_code ────> [!] SyntaxError
       |    │
       |    ├─ import test_module_B.py
       |    │   └─ top-level import BATCH_SIZE ─────────> [!] ImportError (e.g., ModuleNotFound)
       |    │
       |    └─> 🛑 SESSION CRASH (Retrieval Persona Fatal Exception)
       |         │
       |         └─► [ L5 GOVERNANCE ROUTING: CATEGORY 1 TRIAGE (Structural/Import Error) ]
       |              │
       |              ├─ Check 1.1: Should this module exist in the architecture?
       |              │  │
       |              │  ├─ YES → Missing module that should exist
       |              │  │        ├─ Code: Create the module  |  Test: None
       |              │  │        ├─ Repair Class: production_bug_fix
       |              │  │        └─ Analogy: Catalog entry exists, but book was not placed on shelf
       |              │  │
       |              │  └─ NO ─> Check 1.2: Is the import path wrong?
       |              │           │
       |              │           ├─ YES → Wrong import path
       |              │           │        ├─ Code: Correct the import path  |  Test: None
       |              │           │        ├─ Repair Class: stale_reference_fix
       |              │           │        └─ Analogy: Librarian searched the wrong aisle
       |              │           │
       |              │           └─ NO → Unintended structural dependency
       |              │                   ├─ Code: Remove invalid import/reference
       |              │                   ├─ Test: Ensure tests don't force invalid structure
       |              │                   ├─ Status: BLOCKED - Anti-pattern detected
       |              │                   └─ Analogy: Adding a fake book so the catalog check passes
       |
       └─► [ PATH B: TARGET STATE - DELAYED IMPORTS ] ✅ 
            │                                                                    
            ├─ import test_module_A.py (Clean: No top-level app imports)         
            ├─ import test_module_B.py (Clean: No top-level app imports)         
            │                                                                    
            v                                                                    
      [File parsed successfully -> Apply standard AST filtering rules]           
       |                                                                         
       +--> Matches `test_*.py`? -> Is Class? -> Is Function? -> ADD TO QUEUE    
                                        |                                        
                                        v                                        
+-----------------------------------------------------------------------------------------------+
| 3. FIXTURE RESOLUTION (System Bus / ADG Personas)                                             |
| Resolves dependency injection. Prepares required state, mocks, and connections.               |
+---------------------------------------+-------------------------------------------------------+
                                        |                                        
                                        v                                        
+-----------------------------------------------------------------------------------------------+
| 4. TEST EXECUTION (Execution / Tooling Personas)                                              |
| Runs individual tests with Single Mutation Authority (isolated state).                        |
+---------------------------------------+-------------------------------------------------------+
                                        |                                        
                 [Decision Tree: Execution Result & Failures]                    
                  |                                                              
                  +--> Run test_A()                                              
                  |     └─ inside test: import broken_code ──────> ❌ (Routes to CAT 1 TRIAGE above)
                  |                                                  
                  +--> Run test_B()                                              
                  |     └─ logic assertion fails: assert 1 == 2 ─> ❌ [!] AssertionError / ValueError
                  |                                                 │
                  |      ┌──────────────────────────────────────────┘
                  |      │
                  |      └─► [ L5 GOVERNANCE ROUTING: CATEGORY 2 TRIAGE (Assertion/Logic Error) ]
                  |           │
                  |           ├─ Check 2.1: Is an error supposed to happen here?
                  |           │  │
                  |           │  ├─ YES → Expected error path
                  |           │  │        ├─ Code: Ensure correct error is raised  |  Test: Verify type
                  |           │  │        ├─ Repair Class: production_bug_fix
                  |           │  │        └─ Analogy: System intentionally blocks restricted book
                  |           │  │
                  |           │  └─ NO ─> Check 2.2: Is the test too strict about wording?
                  |           │           │
                  |           │           ├─ YES → Brittle error regex
                  |           │           │        ├─ Test: Relax regex (ONLY if semantics preserved)
                  |           │           │        ├─ Repair Class: broken_test_fix
                  |           │           │        ├─ FORBIDDEN: Weakening assertion strictness
                  |           │           │        ├─ VALID: `match="must be positive"` (from "positive int")
                  |           │           │        ├─ INVALID: `pytest.raises(Exception)` (from ValueError)
                  |           │           │        └─ Analogy: Inspector demanding exact wording of warning sign
                  |           │           │
                  |           │           └─ NO ─> Check 2.3: Did the architecture contract legitimately change?
                  |           │                    │
                  |           │                    ├─ YES → Architecture contract changed
                  |           │                    │        ├─ Code: Implement new behavior if missing
                  |           │                    │        ├─ Test: Update tests to match new contract
                  |           │                    │        ├─ Repair Class: policy_regression_fix / bug_fix
                  |           │                    │        └─ Analogy: Library updated rules, checklist is old
                  |           │                    │
                  |           │                    └─ NO → Logic failure / Unintended behavior shift
                  |           │                             ├─ Code: Fix broken logic to satisfy contract
                  |           │                             ├─ Test: Leave as-is (correctly caught regression)
                  |           │                             ├─ Repair Class: production_bug_fix
                  |           │                             └─ Analogy: Pages glued together; fix book, not catalog
                  |                                                  
                  +--> Run test_C() ─────────────────────────────> ✅ (Mark: PASSED)   
                  |                                                              
                  +--> [Is the test marked `@pytest.mark.skip`?]─> ⏭️ (Mark: SKIPPED)  
                  |                                                              
                  +--> [Did the test fail, but marked `xfail`?] ─> ⚠️ (Mark: XFAIL)    
                                        |                                        
                                        v                                        
+-----------------------------------------------------------------------------------------------+
| 5. TEARDOWN (L5 Governance / HITL Governance)                                                 |
| Enforces strict cleanup. Executes `yield` continuations in fixtures to close DBs,             |
| network calls, and reset environmental mutations.                                             |
+---------------------------------------+-------------------------------------------------------+
                                        |                                        
                                        v                                        
+-----------------------------------------------------------------------------------------------+
| 6. REPORTING (Determinism / Replay Roles)                                                     |
| Aggregates all test receipts, stdout/stderr captures, and coverage data into                  |
| a final, fully auditable terminal output or XML/JSON artifact.                                |
+-----------------------------------------------------------------------------------------------+