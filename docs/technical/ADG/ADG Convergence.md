AGENTIC SYSTEM LAYERS (L0–L6) — FULL LIBRARY ANALOGY OF ADG GAPS
==============================================================================================================================

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L0 ROUTING LAYER                                                                                                          │
│ System entry routing / dispatch                                                                                           │
│                                                                                                                           │
│ Technical                                                                                                                 │
│ ---------                                                                                                                 │
│ request_router / gateway / dispatch_agent                                                                                 │
│                                                                                                                           │
│ Library Analogy                                                                                                           │
│ ---------------                                                                                                           │
│ Visitor enters library → Front Desk Librarian decides where request should go                                            │
│                                                                                                                           │
│ Visitor                                                                                                                   │
│   │                                                                                                                       │
│   ▼                                                                                                                       │
│ Front Desk Librarian                                                                                                      │
│   │                                                                                                                       │
│   ├──────────────► Research Desk                                                                                          │
│   │                                                                                                                       │
│   ├──────────────► Archives Desk                                                                                          │
│   │                                                                                                                       │
│   └──────────────► Circulation Desk                                                                                       │
│                                                                                                                           │
│ GAP WHEN MISSING                                                                                                          │
│ librarian has no routing notes → does not know which desk handles which request                                          │
│                                                                                                                           │
│ Missing ADG Relations                                                                                                     │
│ dispatches_to / routes_to / agent_executes_agent                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L1 COGNITION LAYER                                                                                                        │
│ Context retrieval and reasoning                                                                                           │
│                                                                                                                           │
│ Technical                                                                                                                 │
│ ---------                                                                                                                 │
│ embedding retrieval / semantic search / context assembly                                                                  │
│                                                                                                                           │
│ Library Analogy                                                                                                           │
│ ---------------                                                                                                           │
│ Research librarian interprets the question and searches the catalog                                                      │
│                                                                                                                           │
│ Visitor Question                                                                                                          │
│        │                                                                                                                  │
│        ▼                                                                                                                  │
│ Research Librarian                                                                                                        │
│        │                                                                                                                  │
│        ▼                                                                                                                  │
│ Library Card Catalog                                                                                                      │
│        │                                                                                                                  │
│        ▼                                                                                                                  │
│ Relevant Books / References                                                                                               │
│                                                                                                                           │
│ GAP WHEN MISSING                                                                                                          │
│ librarian understands the question but cannot find which books relate                                                    │
│                                                                                                                           │
│ Missing ADG Relations                                                                                                     │
│ pulls_context / retrieves_embeddings / semantic_lookup                                                                    │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L2 EXECUTION LAYER                                                                                                        │
│ Tools and services performing work                                                                                        │
│                                                                                                                           │
│ Technical                                                                                                                 │
│ ---------                                                                                                                 │
│ programmatic tool calling / services / tool adapters                                                                      │
│                                                                                                                           │
│ Library Analogy                                                                                                           │
│ ---------------                                                                                                           │
│ Library staff who actually perform tasks                                                                                  │
│                                                                                                                           │
│ Research Desk                                                                                                             │
│       │                                                                                                                   │
│       ▼                                                                                                                   │
│ Task Request: "Copy page 42 from book"                                                                                    │
│       │                                                                                                                   │
│       ▼                                                                                                                   │
│ Photocopy Clerk                                                                                                           │
│       │                                                                                                                   │
│       ▼                                                                                                                   │
│ Printed Copy Delivered                                                                                                    │
│                                                                                                                           │
│ GAP WHEN MISSING                                                                                                          │
│ librarian knows what to do but not which staff member performs it                                                         │
│                                                                                                                           │
│ Missing ADG Relations                                                                                                     │
│ calls / executes_tool / invokes_service                                                                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L3 ORCHESTRATION LAYER                                                                                                    │
│ Multi-agent coordination                                                                                                  │
│                                                                                                                           │
│ Technical                                                                                                                 │
│ ---------                                                                                                                 │
│ orchestrators / planners / workflow agents                                                                                │
│                                                                                                                           │
│ Library Analogy                                                                                                           │
│ ---------------                                                                                                           │
│ Head Librarian coordinating multiple desks                                                                                │
│                                                                                                                           │
│ Head Librarian                                                                                                            │
│     │                                                                                                                     │
│     ├────────► Research Librarian                                                                                         │
│     │                                                                                                                     │
│     ├────────► Archive Retrieval Staff                                                                                    │
│     │                                                                                                                     │
│     └────────► Copy Center                                                                                                │
│                                                                                                                           │
│ GAP WHEN MISSING                                                                                                          │
│ librarians work independently without coordination                                                                        │
│                                                                                                                           │
│ Missing ADG Relations                                                                                                     │
│ orchestrates / coordinates / manages_agents                                                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L4 STATE LAYER                                                                                                            │
│ Persistent system memory                                                                                                  │
│                                                                                                                           │
│ Technical                                                                                                                 │
│ ---------                                                                                                                 │
│ databases / vector stores / file storage                                                                                  │
│                                                                                                                           │
│ Library Analogy                                                                                                           │
│ ---------------                                                                                                           │
│ Library archives where books are stored                                                                                   │
│                                                                                                                           │
│ Archive Vault                                                                                                             │
│     │                                                                                                                     │
│     ▼                                                                                                                     │
│ Shelves of Books                                                                                                          │
│     │                                                                                                                     │
│     ▼                                                                                                                     │
│ Retrieval by librarians                                                                                                   │
│                                                                                                                           │
│ GAP WHEN MISSING                                                                                                          │
│ librarian does not know where books are stored or recorded                                                                │
│                                                                                                                           │
│ Missing ADG Relations                                                                                                     │
│ reads_from / reads_through / writes_to                                                                                    │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L5 SAFETY LAYER                                                                                                           │
│ Guardrails and policy enforcement                                                                                         │
│                                                                                                                           │
│ Technical                                                                                                                 │
│ ---------                                                                                                                 │
│ safety validators / policy engines                                                                                        │
│                                                                                                                           │
│ Library Analogy                                                                                                           │
│ ---------------                                                                                                           │
│ Library rules enforcement                                                                                                 │
│                                                                                                                           │
│ Library Rules                                                                                                             │
│   • rare books cannot leave archive                                                                                       │
│   • photocopy limits                                                                                                      │
│   • access restrictions                                                                                                   │
│                                                                                                                           │
│ Librarian enforcing rules before fulfilling request                                                                       │
│                                                                                                                           │
│ GAP WHEN MISSING                                                                                                          │
│ staff may perform unsafe or unauthorized actions                                                                          │
│                                                                                                                           │
│ Missing ADG Relations                                                                                                     │
│ applies_guardrail / validates_action                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L6 OBSERVABILITY LAYER                                                                                                    │
│ Logging, tracing, determinism                                                                                            │
│                                                                                                                           │
│ Technical                                                                                                                 │
│ ---------                                                                                                                 │
│ execution traces / telemetry / replay logs                                                                                │
│                                                                                                                           │
│ Library Analogy                                                                                                           │
│ ---------------                                                                                                           │
│ Library audit ledger recording everything that happened                                                                   │
│                                                                                                                           │
│ Library Ledger                                                                                                            │
│     │                                                                                                                     │
│     ▼                                                                                                                     │
│ "Visitor requested book A"                                                                                                │
│ "Research librarian searched catalog"                                                                                     │
│ "Archive staff retrieved book"                                                                                            │
│ "Copy center produced pages"                                                                                              │
│                                                                                                                           │
│ GAP WHEN MISSING                                                                                                          │
│ no record of what happened inside the library                                                                             │
│                                                                                                                           │
│ Missing ADG Relations                                                                                                     │
│ records_execution_trace / emits_determinism_digest                                                                        │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


==============================================================================================================================
WHY CONVERGENCE FAILS
==============================================================================================================================

ADG convergence fails when the library catalog is incomplete.

Example failure:

Visitor request
      │
      ▼
Front desk routes request
      │
      ▼
Research librarian searches catalog
      │
      ▼
Finds reference
      │
      ▼
Needs archive retrieval
      │
      ▼
BUT catalog does not show which staff retrieves archives

The library cannot complete the workflow because the operational knowledge is missing.

In ADG terms this appears as:

missing relations
changing counts across rebuilds
non-deterministic graph structure

Convergence occurs when every action in the library has a corresponding catalog entry describing how it connects to the rest of the system.
==============================================================================================================================
