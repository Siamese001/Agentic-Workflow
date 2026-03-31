#################################################################################################################################
#                                     ADG TEST SUITE ARCHITECTURE & RCA CHEAT SHEET (SQLITE-BACKED)                             #
#################################################################################################################################
# CORE PRINCIPLE: Treat the test suite as a directed graph. Use SQLite evidence to isolate the smallest shared "bad node".     #
#################################################################################################################################

1. STRUCTURAL WEIGHT: EDGE COUNT RANKING            2. BOOTSTRAP OVERHEAD: CONFTEST CHAINS
------------------------------------------          ------------------------------------------
[ ADG ON TEST FILES ]                               [ SHARED FIXTURE PIPELINE ]
┌────────────────────────────────────────┐          ┌──────────────┐
│             test_target.py             │          │ test_file.py │
├───────────────────┬────────────────────┤          └──────┬───────┘
│     EDGES OUT     │      EDGES IN      │                 │ imports / fixture resolution
│ (Imports, Calls,  │ (Imported by,      │                 v
│ Fixtures, Reads)  │  Helpers used by)  │          ┌──────────────┐
└──────────┬────────┴──────────┬─────────┘          │ conftest.py  │
           │                   │                    └──────┬───────┘
           └─────────┬─────────┘                           │
           count(incident edges)                           ├─────────> helper_a.py (Runtime Bootstrap)
                     v                                     ├─────────> fixture_factory.py (Env/Mocks)
┌────────────────────────────────────────┐                 └─────────> lifecycle_trace_contract (Tracing)
│         TOP STRUCTURAL HOTSPOTS        │
│ 1. test_x.py [412] - Dense Setup       │          [ THE MEASUREMENT ]
│ 2. test_y.py [365] - Helper Fanout     │          Long chains = Higher "Bootstrap Tax".
│ 3. test_z.py [344] - Fixture Heavy     │          ADG isolates if the failure is in the TEST logic
└────────────────────────────────────────┘          or the SHARED STACK inherited via conftest.

---------------------------------------------------------------------------------------------------------------------------------

3. COUPLING SPREAD: CONTRACT MAP                    4. THE ADG-BACKED RCA PIPELINE
------------------------------------------          ------------------------------------------
"Who pulls lifecycle_trace_contract?"               [ SYMPTOM ] ──────> [ FIXTURE CRASH / RUNTIME ISSUE ]
                                                                                  │
DIR: tests/unit        [###] (3)                                                  v
DIR: tests/integration [#########] (9)              ┌───────────────────────────────────────────────────────────┐
DIR: tests/guardian    [#######] (7)                │ ADG SQLITE EVIDENCE GATHERING                             │
DIR: tests/e2e         [##] (2)                     │ - Trace provenance (source_file, line, symbol)            │
                                                    │ - Calculate Fan-in/Fan-out of failing nodes               │
[ INSIGHT ]                                         └──────────┬────────────────────────────────────────────────┘
DIRECT IMPORTS   = Obvious Dependency                          │
TRANSITIVE PROOF = Hidden Bootstrap Tax                        v
ADG reveals the "tax" by traversing imports         ┌───────────────────────────────────────────────────────────┐
to find the lifecycle_trace_contract origin.        │ BUILD ANALYTIC VIEWS                                      │
                                                    │ 1. Hotspot Rank | 2. Conftest Chain | 3. Contract Map     │
                                                    └──────────┬────────────────────────────────────────────────┘
                                                               │
                                                               v
                                                    ┌───────────────────────────────────────────────────────────┐
                                                    │ ROOT CAUSE ISOLATION                                      │
                                                    │ "Single shared node" vs "Many unrelated local failures"   │
                                                    └──────────┬────────────────────────────────────────────────┘
                                                               │
                                                               v
                                                    ┌───────────────────────────────────────────────────────────┐
                                                    │ RCA OUTPUT: failure_category, root_cause, blast_radius,   │
                                                    │ and the SMALLEST SAFE FIX SURFACE.                        │
                                                    └───────────────────────────────────────────────────────────┘

#################################################################################################################################
#   EDGE COUNT = Weight  |  IMPORT CHAIN = Path  |  FANIN = Dependant Count  |  FANOUT = Resource Drag  |  RCA = Shared Node   #
#################################################################################################################################
