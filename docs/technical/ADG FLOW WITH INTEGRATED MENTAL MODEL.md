COMPRESSED VERSION
==================

                           STATIC VIEW                                   RUNTIME VIEW
                    (how books are organized)                     (how books are actually used)

CODEBASE (books)                                            SYSTEM EXECUTION (readers using books)
      │                                                                   │
      ▼                                                                   ▼
╔══════════════════════════════╗                               Runtime events / traces / telemetry
║           ADG                ║                                           │
║                              ║                                           ▼
║  Builder (catalog librarian) ║                                 Runtime analyzers / observers
║            │                 ║                                           │
║            ▼                 ║                                           ▼
║  Static Graph (catalog)      ║                                 Runtime findings / behavior reports
╚══════════════════════════════╝
             │
             ▼
Analyzers (rule librarians)
             │
             ▼
Violations (misfiled books)
             │
             ▼
Reports / CI (library compliance report)



ADG + RUNTIME FLOW WITH INTEGRATED MENTAL MODEL
===============================================

Goal
----
Show in one view:
1. What is INSIDE the ADG
2. What consumes the ADG catalog
3. Where runtime behavior fits
4. How static structure and runtime behavior differ



STATIC SIDE
===========

[1] CODEBASE
------------------------------------
All source files in the repository

Mental Model
• Books in the library
• Books reference other books
• Shelves represent architectural layers
• Archive represents state storage
      │
      ▼


╔════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                      ADG (Architecture Dependency Graph)                           ║
║                                                                                                    ║
║  [2] ADG BUILDER / SCANNER                                                                         ║
║  -----------------------------------------------------------------------------------------------   ║
║  Scans repository and extracts relationships                                                       ║
║                                                                                                    ║
║  Mental Model                                                                                      ║
║  • Cataloging librarian reads every book                                                           ║
║  • Records references between books                                                                ║
║  • Records which shelf each book belongs to                                                        ║
║  • Records which books cite external sources                                                       ║
║  • Records which books write to archive/state                                                      ║
║                                                                                                    ║
║                 │                                                                                  ║
║                 ▼                                                                                  ║
║                                                                                                    ║
║  [3] STATIC ADG                                                                                    ║
║  -----------------------------------------------------------------------------------------------   ║
║  Architecture Dependency Graph database                                                            ║
║                                                                                                    ║
║  Example catalog entries                                                                           ║
║  ModuleA ──imports──> ModuleB                                                                      ║
║  ModuleC ──calls──> OpenAI                                                                         ║
║  ModuleD ──writes──> L4_state                                                                      ║
║  ModuleE ──belongs_to──> Layer3                                                                    ║
║                                                                                                    ║
║  Mental Model                                                                                      ║
║  • Library catalog database                                                                        ║
║  • Stores relationships between books                                                              ║
║  • Contains architectural metadata                                                                 ║
║  • Shows how the library is organized                                                              ║
║  • Does NOT enforce rules                                                                          ║
║  • Does NOT show live reading behavior                                                             ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════╝
      │
      ▼


[4] STATIC ANALYZERS
------------------------------------
Programs that query the ADG

Examples
• layer_authority analyzer
• prompt_governance analyzer
• mutation_authority analyzer
• seam_enforcement analyzer

Mental Model
• Librarians reading the catalog
• Asking rule questions about the library
• Checking if books are on the correct shelf
• Checking if books cite restricted sections
• Checking if books bypass the reference desk
      │
      ▼


[5] STATIC VIOLATION DETECTION
------------------------------------
Rule violations discovered from structure

Examples
ModuleA ──calls──> OpenAI
Violation: bypassed seam

LearningModule ──writes──> filesystem
Violation: bypassed write gateway

Mental Model
• Librarian discovers catalog problems
• Book placed on wrong shelf
• Book bypassed reference desk
• Book wrote directly into archive
      │
      ▼


[6] STATIC REPORTS / CI / GOVERNANCE
------------------------------------
Architecture health reporting

Outputs
• violation reports
• severity ranking
• CI failures
• architecture drift monitoring

Mental Model
• Library compliance report
• Incident log
• Instructions to reorganize shelves




RUNTIME SIDE
============

[7] SYSTEM EXECUTION
------------------------------------
The software is actually running

Mental Model
• Readers moving through the library
• Readers taking books off shelves
• Readers using reference desk
• Readers entering archive areas
      │
      ▼


[8] RUNTIME EVENTS / TRACES / TELEMETRY
---------------------------------------
Observed execution behavior

Examples
trace_id=1234
module=agent_router
provider=openai
state_write=l4_state
prompt_hash=...

Mental Model
• Library activity log
• Which reader touched which book
• Which desk was used
• Which archive area was accessed
      │
      ▼


[9] RUNTIME ANALYZERS / OBSERVERS
---------------------------------
Programs that inspect runtime behavior

Examples
• seam bypass detector
• runtime policy hash verifier
• state mutation observer
• trace compliance checker

Mental Model
• Librarians watching how books are actually used
• Checking whether readers follow library procedures
• Checking whether restricted areas were entered properly
      │
      ▼


[10] RUNTIME FINDINGS / BEHAVIOR REPORTS
----------------------------------------
Behavior violations or confirmations discovered from execution

Examples
Observed:
AgentModule ──calls──> OpenAI directly

Expected:
AgentModule ──calls──> LLMSeam ──calls──> OpenAI

Finding:
Runtime seam bypass detected

Mental Model
• Reader skipped the reference desk
• Reader entered archive directly
• Reader used a restricted book path
      │
      ▼


[11] RUNTIME GOVERNANCE / OPERATIONS
------------------------------------
Operational reporting and enforcement

Outputs
• runtime incident reports
• drift detection
• trace compliance reports
• alerting / dashboards / audits

Mental Model
• Live library operations report
• Incident desk log
• Audit trail of actual reader behavior




STATIC vs RUNTIME
=================

STATIC ADG
----------
Shows how books are organized and related

Questions it answers
• Which book references which other book?
• Which shelf does this book belong to?
• Which module calls which provider?
• Which module writes which state?

Mental Model
• Library catalog


RUNTIME
-------
Shows how books are actually used while the library is open

Questions it answers
• Which module actually ran?
• Which provider was actually called?
• Which state was actually mutated?
• Was the correct seam actually used?

Mental Model
• Readers moving through the library
• Library activity log




HOW THEY WORK TOGETHER
======================

ADG provides EXPECTED structure
Runtime provides OBSERVED behavior

Mental Model
• Catalog says where a book should be
• Observation says what people actually did with it

Comparison example

Expected from ADG
AgentModule ──calls──> LLMSeam ──calls──> OpenAI

Observed at runtime
AgentModule ──calls──> OpenAI

Result
Runtime analyzer flags seam bypass




ONE-LINE MENTAL MODEL
=====================

ADG      = library catalog
Analyzers = librarians reading the catalog
Runtime   = readers actually using the library
Telemetry = library activity log
Reports   = compliance and incident notes
