=============================================================================================
                  PYTEST LIFECYCLE: COLLECTION VS. EXECUTION PATHOLOGY
=============================================================================================

  ▶ pytest
     │
     ▼
  [ PHASE 1: COLLECTION ] 
     │
     ├─► [ PATH A: CURRENT STATE - FATAL EARLY EXIT ] ❌
     │    │
     │    ├─ import test_module_A.py
     │    │   └─ top-level import broken_app_code ───────┐ 
     │    │                                              ▼
     │    │                                    [!] SyntaxError / IndentationError
     │    │
     │    ├─ import test_module_B.py
     │    │   └─ top-level import BATCH_SIZE ────────────┐
     │    │                                              ▼
     │    │                                    [!] ImportError: missing API contract
     │    ▼
     │  [ SESSION CRASH ] 
     │    │
     │    └─> 🛑 FATAL: Collection aborted. 
     │        Tests never reach execution. 
     │        CI pipeline blocked. Granular reporting lost.
     │
     │
     └─► [ PATH B: TARGET STATE - ISOLATED TEST FAILURES ] ✅
          │
          ├─ import test_module_A.py (Clean: No top-level app imports)
          ├─ import test_module_B.py (Clean: No top-level app imports)
          │
          ▼
       [ PHASE 2: EXECUTION ]
          │
          ├─ Run test_A() 
          │   └─ inside test: import broken_app_code ────> ❌ Test A Fails (Honest visibility)
          │
          ├─ Run test_B()
          │   └─ inside test: import BATCH_SIZE ─────────> ❌ Test B Fails (Honest visibility)
          │
          ├─ Run test_C() ───────────────────────────────> ✅ Test C Passes
          │
          ▼
       [ GRACEFUL FINISH ] 
          │
          └─> 📊 SUCCESS: Full suite executes. 
              Granular pass/fail/skip report generated. CI pipeline unblocked.

=============================================================================================