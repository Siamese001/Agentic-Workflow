==============================================================================================================================
                            AGENTIC SYSTEM — PROCESS MAP (CANONICAL SEMANTICS & LOOP)
 PRIMARY RUNTIME PATH: L1 → L0 → [opt L3] → L2 | L1 may optionally prefetch context via C0 before L0 dispatch | L5 = cross-cutting policy | UWG = writes to L4
==============================================================================================================================

[ L5 POLICY PLANE / Safety Officer ] ──(cross-cutting authority over L1, L0, L2, Exit, UWG)──────────────────────────────────┐
         ┌──────────────────┐                                                                                                │
         │U0 REQUEST SOURCES│                                                                                                │
         │ (User/App/Event) │                                                                                                │
         └────────┬─────────┘                                                                                                │
                  ▼                                                                                                          │
         ┌──────────────────┐                                                                                                │
         │ INGRESS / CHECK  │ <── (optional pre-layer envelope validation, NOT L0)                                           │
         └────────┬─────────┘                                                                                                │
                  │                                                                                                          │
┌─────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│                 ▼                                                                      [CORE RUNTIME LOOP]               │ │
│ ┌───────────────┴──────────────────┐<──────────────────────────────────────────────────────────────────────────────────┐ │ │
│ │  L1 REASONING LOOP (Librarian)   │<───────────────────────────────────────────────────────────┐                      │ │ │
│ └───────────────┬──────────────────┘                                                            │                      │ │ │
│                 ├                    ┌────────────────────────────────┐             ┌───────────┴────────────┐         │ │ │
│                 ├──[context-opt]───> │ C0 CONTEXT ENGINE (Ref Desk)   │─[evidence]─>│     PROMPT ASSEMBLY    │         │ │ │
│                 │     R3 primarily   │ retrieve•curate•compress•ground│             │ (System•Context•Task)  │         │ │ │
│                 │                    │  L1-owned pre-dispatch context │             │  packages reasoning ctx │         │ │ │
│                 │                    └───────────────▲────────────────┘             └───────────▲────────────┘         │ │ │
│                 │                                    │                                          │                      │ │ │
│                 │                                    └───────── [reads] ────────────────────────┤                      │ │ │
│                 │ [plan]                                                                        │ [state load]         │ │ │
│                 ▼                                                                               │                      │ │ │
│ ┌──────────────────────────────────────────────────────────────────────────────┐      ┌───────────┴────────────┐         │ │ │
│ │ L0 ROUTING (Dispatcher)                                                      │      │       L4 STATE /       │         │ │ │
│ │------------------------------------------------------------------------------│      │       Archivist        │         │ │ │
│ │ R1A exact cache • R1Bsem cache     -> direct cache route | no pre-L0 C0 req │      └───────────▲────────────┘         │ │ │
│ │ R3 agentic RAG                     -> context-backed route | consumes C0 ctx │                 │                      │ │ │
│ │ R4 action • R5 fallback            -> direct dispatch route | no pre-L0 C0   │                 │                      │ │ │
│ └───────────────┬──────────────────────────────────────────────────────────────┘                 │                      │ │ │
│                 │                                                                               │ [writes]             │ │ │
│                 │ [dispatch]                                                                    │                      │ │ │
│                 ▼                                                                               │                      │ │ │
│ ┌──────────────────────────────────┐                                                            │                      │ │ │
│ │ L3 ORCHESTRATOR [opt] (Sec Head) │                                                            │                      │ │ │
│ └───────────────┬──────────────────┘                                                            │                      │ │ │
│                 ▼ [EXECUTE]                                                                     │                      │ │ │
│ ┌──────────────────────────────────┐                                                            │                      │ │ │
│ │  L2 EXECUTION (Execution Staff)  │                                                            │                      │ │ │
│ └───────────────┬──────────────────┘                                                            │                      │ │ │
│                 ▼ [L2 EXECUTION OUTPUT]                                                         │                      │ │ │
└─────────────────┼───────────────────────────────────────────────────────────────────────────────┼────────────────────────┘ │
                  │                                                                               │                            │
==================┼===============================================================================┼============================│
[5] POST-L2 CONTROL + EVALUATION                                                                  │                            │
==================┼===============================================================================┼============================│
                  ▼                                                                               │                            │
 ┌────────────────┴─────────────────┐                                                             │                            │
 │ LIVE EVALUATION SPINE            │                                                             │                            │
 │ current-run judgment             │                                                             │                            │
 │ - policy checks                  │                                                             │                            │
 │ - schema / sandbox validity      │                                                             │                            │
 │ - outcome checks                 │                                                             │                            │
 │ - trajectory checks              │                                                             │                            │
 │ - release-time regression checks │                                                             │                            │
 └────────────────┬─────────────────┘                                                             │                            │
                  │                                                                               │                            │
 ┌────────────────▼─────────────────┐<───[approve / deny / rework / reroute]────────┐           │                            │
 │ EXIT SPINE                       │                                               │           │                            │
 │ Checkout / disposition authority │             ┌─────────────────────────┐       │           │                            │
 │ - allow / finish                 ├──[ESCALATE]─> HITL                    │       │           │                            │
 │ - deny                           │             │ human review            │       │           │                            │
 │ - reroute / control              │             └────────────┬────────────┘       │           │                            │
 │ - escalate to HITL               │                          ▼                    │           │                            │
 │ - commit if needed               │             ┌─────────────────────────┐       │           │                            │
 └─┬──────────────┬───────────────┬─┘             │ HUMAN DISPOSITION       ├───────┘           │                            │
   │              │               │               └─────────────────────────┘                   │                            │
   ▼              ▼               ▼                                                             │                            │
[ALLOW /       [COMMIT ->      [DENY /                                                          │                            │
 FINISH]        UWG -> L4]      REROUTE]                                                        │                            │
                                                                                                │                            │
================================================================================================┼============================│
[6] SHADOW EVALUATION + FUTURE-RUN LEARNING                                                     │                            │
================================================================================================┼============================│
                  │                                                                             │                            │
                  ▼ [Runtime evidence + L4 artifacts]                                           │                            │
 ┌────────────────┴───────────────────────────┐                                                 │                            │
 │ SHADOW EVALUATION SPINE                    │                                                 │                            │
 │ Review / scoring / signalization           │                                                 │                            │
 │ - telemetry grading                        │                                                 │                            │
 │ - broader drift / replay / trend analysis  │                                                 │                            │
 │ - heavier regression/calibration analytics │                                                 │                            │
 └────────────────┬───────────────────────────┘                                                 │                            │
                  │                                                                             │                            │
         ┌────────┴────────┐                                                                    │                            │
         │                 │                                                                    │                            │
         ▼                 ▼                                                                    │                            │
    [L6 OBSERVE]     [BUS P / BUS T]                                                            │                            │
                           │                                                                    │                            │
                           ▼                                                                    │                            │
             ┌─────────────┴────────────────────┐                                               │                            │
             │ EVOLUTION / SYSTEM LEARNING LOOP │                                               │                            │
             │ future-runs only                 │                                               │                            │
             │ - RCA                            │                                               │                            │
             │ - proposal drafting              │                                               │                            │
             │ - approval                       │                                               │                            │
             │ - promotion to BUS U             │                                               │                            │
             └─────────────┬────────────────────┘                                               │                            │
                           │                                                                    │                            │
                           ▼                                                                    │                            │
               [BUS U FUTURE RUNS ONLY]                                                         │                            │
                                                                                                │                            │
────────────────────────────────────────────────────────────────────────────────────────────────┴────────────────────────────┘








