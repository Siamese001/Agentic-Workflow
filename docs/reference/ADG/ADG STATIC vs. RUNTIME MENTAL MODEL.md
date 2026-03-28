=========================================================================================================================
                                     ADG + RUNTIME FLOW WITH INTEGRATED MENTAL MODEL
                                        (Augmented with Graph DB & L6 Tracing)
=========================================================================================================================
Goal: Show in one view [1] What is INSIDE the ADG, [2] What consumes the ADG catalog,
      [3] Where runtime behavior fits, [4] How static structure and runtime behavior differ,
      [5] How a Graph DB augments the system, and [6] L6 Observability tracing requirements.

STATIC VIEW (The Expected Structure)                                RUNTIME VIEW (The Observed Behavior)
"How books are organized"                                           "How books are actually used"
====================================================                ====================================================

[1] CODEBASE                                                        [7] SYSTEM EXECUTION
----------------------------------------------------                ----------------------------------------------------
All source files in the repository.                                 The software is actually running (app doing work).
Mental Model:                                                       Mental Model:
• Books in the library, referencing other books                     • Readers moving through the library
• Shelves represent architectural layers                            • Readers taking books off shelves
• Archive represents state storage                                  • Readers entering archive areas
      │                                                                   │
      ▼                                                                   ▼
╔══════════════════════════════════════════════════╗                [8] RUNTIME EVENTS / TRACES / TELEMETRY
║ [2] ADG BUILDER / SCANNER                        ║                ----------------------------------------------------
║ Scans repository and extracts relationships.     ║                Observed execution behavior.
║ Mental Model: Cataloging librarian reads every   ║                Examples: trace_id=1234, module=agent_router,
║ book, records references, shelves, and archives. ║                provider=openai, state_write=l4_state
║     │                                            ║
║     ▼                                            ║                >> L6 OBSERVABILITY TRACING REQ: Must emit structured
║ [3] STATIC ADG                                   ║                traces capturing deep architectural context (e.g., L6
║ Architecture Dependency Graph database.          ║                zone entry/exits, state mutations) to enable precise
║ Examples:                                        ║                graph matching and path reconstruction.
║ ModuleA ──imports──> ModuleB                     ║
║ ModuleC ──calls──> OpenAI                        ║                Mental Model: Library activity log (Which reader
║ ModuleD ──writes──> L4_state                     ║                touched which book, which desk was used) + Readers
║                                                  ║                carrying GPS trackers recording exact L6 zones.
║ >> GRAPH DB AUGMENTATION: Stores structural ADG  ║                      │
║ as nodes/edges for deep path traversal queries.  ║                      ▼
║                                                  ║     THE BRIDGE   [9] RUNTIME ANALYZERS / OBSERVERS
║ Mental Model: Library catalog database. Shows    ║======(queries)======>----------------------------------------------
║ organization. Does NOT enforce rules/behavior.   ║      for rules   Programs that inspect runtime behavior.
║ (Graph DB = 3D interconnected map of all books). ║                  They cross-reference telemetry against the ADG!
╚══════════════════════════════════════════════════╝
      │                                                               >> GRAPH DB AUGMENTATION: Overlays L6 trace paths
      ▼                                                               directly onto the static graph to visualize runtime
[4] STATIC ANALYZERS                                                  drift, edge traversals, and execution hotspots.
----------------------------------------------------
Programs that query the ADG (e.g., layer_authority).                  Mental Model: Librarians watching the cameras
Mental Model: Librarians reading the catalog asking                   and comparing reader actions to the master catalog
rule questions (Are books on the right shelf?).                       (Graph DB = Glowing footprints mapped on the 3D map).
      │                                                                   │
      ▼                                                                   ▼
[5] STATIC VIOLATION DETECTION                                      [10] RUNTIME FINDINGS / BEHAVIOR REPORTS
----------------------------------------------------                ----------------------------------------------------
Rule violations discovered from structure.                          Behavior violations or confirmations discovered.
Example: ModuleA ─calls─> OpenAI (bypassed seam)                    Example Finding:
Mental Model: Librarian discovers catalog problems                  Expected (from ADG): Agent ─calls─> LLMSeam ─calls─> OpenAI
(misfiled books, bypassed desks).                                   Observed (from Telemetry): Agent ─calls─> OpenAI directly
      │                                                             Result: Runtime seam bypass detected.
      ▼                                                             Mental Model: Reader skipped the reference desk.
[6] STATIC REPORTS / CI / GOVERNANCE                                      │
----------------------------------------------------                      ▼
Architecture health reporting (CI failures, drift).                 [11] RUNTIME GOVERNANCE / OPERATIONS
Mental Model: Library compliance report, incident log.              ----------------------------------------------------
                                                                    Operational reporting and enforcement.
                                                                    Outputs: alerts, drift detection, audit trails.
                                                                    Mental Model: Live library operations report.

=========================================================================================================================
HOW THEY WORK TOGETHER
=========================================================================================================================
ADG provides EXPECTED structure (Catalog says where a book should be).
Runtime provides OBSERVED behavior (Observation says what people actually did with it).
Graph DB provides UNIFIED TOPOLOGY (Mapping static structure to dynamic telemetry).

ONE-LINE MENTAL MODEL:
ADG = Library Catalog │ Analyzers = Librarians reading catalog │ Runtime = Readers using library │ Telemetry = Log
Graph DB = 3D Map of Library & Footprints │ L6 Tracing = GPS Trackers on Readers
=========================================================================================================================
