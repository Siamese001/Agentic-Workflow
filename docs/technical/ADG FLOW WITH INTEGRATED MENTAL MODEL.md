ADG FLOW WITH INTEGRATED MENTAL MODEL
=====================================


[1] CODEBASE
---------------------------
All source files in the repository
(modules, symbols, layers, calls)

Mental Model
• Books in the library
• Each book contains knowledge
• Books reference other books


        │
        ▼


[2] ADG BUILDER / SCANNER
---------------------------
Scans repository and extracts relationships

Mental Model
• Cataloging librarian reads every book
• Records who references whom
• Records which shelf each book belongs to
• Records which books cite external sources


        │
        ▼


[3] STATIC ADG
---------------------------
Architecture Dependency Graph database

Example entries

ModuleA ──imports──> ModuleB
ModuleC ──calls──> OpenAI
ModuleD ──writes──> L4_state
ModuleE ──belongs_to──> Layer3

Mental Model
• Library catalog database
• Stores metadata about books
• Contains relationships between books
• Does NOT enforce any rules


        │
        │
        │  ADG remains static
        │
        ▼


[4] ANALYZERS
---------------------------
Programs that query the ADG

Examples
• layer_authority analyzer
• prompt_governance analyzer
• mutation_authority analyzer
• seam_enforcement analyzer

Mental Model
• Librarians reading the catalog
• Asking questions about library rules
• Checking if books are filed correctly
• Checking if books cite restricted material


        │
        ▼


[5] VIOLATION DETECTION
---------------------------
Rule violations discovered

Examples

ModuleA ──calls──> OpenAI
Violation: bypassed seam

LearningModule ──writes──> filesystem
Violation: bypassed write gateway

Mental Model
• Librarian finds problems
• Book placed on wrong shelf
• Book bypassed reference desk
• Book wrote directly into archive


        │
        ▼


[6] REPORTS / CI / GOVERNANCE
---------------------------
Architecture health reports

Outputs
• violation reports
• severity rankings
• CI failures
• architecture drift tracking

Mental Model
• Library compliance report
• Incident log for catalog issues
• Instructions to reorganize shelves



COMPRESSED VERSION
==================

CODEBASE (books)
     │
     ▼
ADG BUILDER (cataloging librarian)
     │
     ▼
STATIC ADG (library catalog)
     │
     ▼
ANALYZERS (rule-checking librarians)
     │
     ▼
VIOLATIONS (misfiled books)
     │
     ▼
REPORTS / CI (library compliance report)