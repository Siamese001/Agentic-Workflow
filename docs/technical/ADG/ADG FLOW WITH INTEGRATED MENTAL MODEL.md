=========================================================================================================================
                                     ADG + RUNTIME FLOW WITH INTEGRATED MENTAL MODEL
=========================================================================================================================
Goal: Show in one view [1] What is INSIDE the ADG, [2] What consumes the ADG catalog,
      [3] Where runtime behavior fits, and [4] How static structure and runtime behavior differ.

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
║     │                                            ║                Mental Model: Library activity log (Which reader
║     ▼                                            ║                touched which book, which desk was used)
║ [3] STATIC ADG                                   ║                      │
║ Architecture Dependency Graph database.          ║                      ▼
║ Examples:                                        ║     THE BRIDGE   [9] RUNTIME ANALYZERS / OBSERVERS
║ ModuleA ──imports──> ModuleB                     ║======(queries)======>----------------------------------------------
║ ModuleC ──calls──> OpenAI                        ║      for rules   Programs that inspect runtime behavior.
║ ModuleD ──writes──> L4_state                     ║                  They cross-reference telemetry against the ADG!
║ Mental Model: Library catalog database. Shows    ║                  Mental Model: Librarians watching the cameras
║ organization. Does NOT enforce rules/behavior.   ║                  and comparing reader actions to the master catalog
╚══════════════════════════════════════════════════╝                  to check if procedures are followed.
      │                                                                   │
      ▼                                                                   ▼
[4] STATIC ANALYZERS                                                [10] RUNTIME FINDINGS / BEHAVIOR REPORTS
----------------------------------------------------                ----------------------------------------------------
Programs that query the ADG (e.g., layer_authority).                Behavior violations or confirmations discovered.
Mental Model: Librarians reading the catalog asking                 Example Finding:
rule questions (Are books on the right shelf?).                     Expected (from ADG): Agent ─calls─> LLMSeam ─calls─> OpenAI
      │                                                             Observed (from Telemetry): Agent ─calls─> OpenAI directly
      ▼                                                             Result: Runtime seam bypass detected.
[5] STATIC VIOLATION DETECTION                                      Mental Model: Reader skipped the reference desk.
----------------------------------------------------                      │
Rule violations discovered from structure.                                ▼
Example: ModuleA ─calls─> OpenAI (bypassed seam)                    [11] RUNTIME GOVERNANCE / OPERATIONS
Mental Model: Librarian discovers catalog problems                  ----------------------------------------------------
(misfiled books, bypassed desks).                                   Operational reporting and enforcement.
      │                                                             Outputs: alerts, drift detection, audit trails.
      ▼                                                             Mental Model: Live library operations report.
[6] STATIC REPORTS / CI / GOVERNANCE
----------------------------------------------------
Architecture health reporting (CI failures, drift).
Mental Model: Library compliance report, incident log.

=========================================================================================================================
HOW THEY WORK TOGETHER
=========================================================================================================================
ADG provides EXPECTED structure (Catalog says where a book should be).
Runtime provides OBSERVED behavior (Observation says what people actually did with it).

ONE-LINE MENTAL MODEL:
ADG = Library Catalog │ Analyzers = Librarians reading catalog │ Runtime = Readers using library │ Telemetry = Log
=========================================================================================================================
