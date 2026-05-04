====================================================================================================
                        AGENTIC SYSTEM — UNIFIED LIBRARIAN PERSONA MAP
                             LLM-AS-JUDGE EXACT PLACEMENT & FLOW
====================================================================================================

┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [ U0 INTAKE ] (Greeter)                                                                          │
│ Normalizes request | Captures origin | No answer | No execution                                  │
└─────────────────────────────────┬────────────────────────────────────────────────────────────────┘
                                  │ raw intent
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [ L0 ROUTE ] (Dispatcher)                                                                        │
│ Emits RouteContract | e.g., Grounded Read | No retrieval | No execution                          │
└─────────────────────────────────┬────────────────────────────────────────────────────────────────┘
                                  │ route contract
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [ C0 EVIDENCE ] (Reference Desk)                                                                 │
│ Shapes evidence packet | Retrieves cited spans | No answer | No execution                        │
└─────────────────────────────────┬────────────────────────────────────────────────────────────────┘
                                  │ evidence packet
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [ PA PROMPT ] (Assembler)                                                                        │
│ Binds evidence + task + rubric + constraints | No retrieval | No execution                       │
└─────────────────────────────────┬────────────────────────────────────────────────────────────────┘
                                  │ prompt packet
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [ L2 EXECUTE ] (Research Assistant) ◄────────────────────── [ EVIDENCE / FACTS ]                 │
│ Generates draft | Executes tools | Proposes diffs           (Warranty Policy)                    │
└─────────────────────────────────┬────────────────────────────────────────────────────────────────┘
                                  │ candidate output
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [ EXIT EVAL ] (Head Librarian)      ◄────────────────────── [ RUBRIC / RULES ]                   │
│ ★ LLM-AS-JUDGE RUNS HERE ★                                  (Grounding, Schema)                  │
│ Evaluates candidate against rubric | Checks completeness, safety, correctness, false confidence  │
└─────────────────────────────────┬────────────────────────────────────────────────────────────────┘
                                  │ emit verdict
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [ X3 DISPOSITION ] (Security Checkpoint)                                                         │
│ Evaluates judge scorecard | Owns final routing decision | Emits exactly one action               │
└─┬─────────────────┬─────────────────┬─────────────────┬──────────────────────────────────────────┘
  │ release answer  │ bounded repair  │ block fallback  │ human review
  ▼                 ▼                 ▼                 ▼
[ACCEPT]          [REVISE]          [REJECT]          [ESCALATE]
  │                 │                 │                 │
  └─────────────────┴────────┬────────┴─────────────────┘
                             │ commit request
                             ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [ UWG / L4 ] (Archivist)                                                                         │
│ Durable write ONLY if authorized | Stores audit trail, trace ID, disposition | No direct L2 write│
└─────────────────────────────────┬────────────────────────────────────────────────────────────────┘
                                  │ post run
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [ L6 SHADOW ] (Analysts)                                                                         │
│ Post-run eval | Future-run learning | RCA | No current-run mutation | No direct L4 write         │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

====================================================================================================
  JUDGE BOUNDARIES (Head Librarian)         │  JUDGE EVAL DIMENSIONS
--------------------------------------------├-------------------------------------------------------
  CAN DO:                                   │  [Groundedness] Maps to evidence?
  • Evaluate candidate & compare to facts   │  [Correctness] Logic / fact pattern right?
  • Score against rubric & output schema    │  [Completeness] Answered the required task?
  • Detect false confidence & violations    │  [Schema] Matches required output format?
  • Recommend revise/reject/escalate        │  [Safety] Within authority and constraints?
                                            │  [False Confidence] Overclaiming beyond evidence?
  CANNOT DO:                                │  [Citation Integrity] Spans support the claim?
  • Retrieve new evidence or execute tools  │  [Repairability] Can bounded fix make it acceptable?
  • Override X3 Gate or mutate current run  │
  • Write to L4 or invent missing facts     │  MEMORY HOOK: Judge asks "Is it grounded & safe?"
====================================================================================================