==============================================================================================================================
                            AGENTIC SYSTEM — PROCESS MAP (CANONICAL SEMANTICS & LOOP)
 PRIMARY RUNTIME PATH: L1 ───> L0 ───> [opt L3] ───> L2 | L0 routing (R3) invokes C0 context assembly
                            L5 = cross-cutting policy | UWG = writes to L4
==============================================================================================================================

[ L5 POLICY PLANE / Safety Officer ] ──(cross-cutting authority over [1], [2], [3], [4], [5], [6], EXIT, UWG)──────────────

==============================================================================================================================
[1] REQUEST INTAKE + ENVELOPE CHECK
==============================================================================================================================
         ┌──────────────────────────────────────┐
         │ U0 REQUEST SOURCES (User/App/Event)  │
         └──────────────────┬───────────────────┘
                            ▼
         ┌──────────────────────────────────────┐
         │           INGRESS / CHECK            │ <─── optional pre-layer envelope validation, NOT L0
         └──────────────────┬───────────────────┘
                            │ [dispatch to [2]]
                            ▼

==============================================================================================================================
[2] L1 REASONING
==============================================================================================================================
 ┌────────────────────────────────────┐
 │ L1 REASONING LOOP (Librarian)      │<─────────────────────────────────────────────────────────────────────────────┐
 └───────────────┬────────────────────┘                                                                              │
                 │ [plan]                                                                                            │
                 │ [dispatch to [3]]                                                                                 │
                 ▼                                                                                                   │
                                                                                                                     │
==============================================================================================================================
[3] ROUTE DECISION + SWITCHING
==============================================================================================================================
 ┌────────────────────────────────────┐                                                                              │
 │ L0 ROUTING (Dispatcher)            │                                                                              │
 │ plan enters route authority        │                                                                              │
 └───────────────┬────────────────────┘                                                                              │
                 ▼                                                                                                   │
 ┌──────────────────────────────────────────────┐ yes ┌──────────────────────────────┐                               │
 │ D1: exact cache key hit under policy?        ├───> │ R1A EXACT CACHE              ├───> [RETURN]                  │
 │ query + scope + freshness + version          │     │ cache / short-circuit        │                               │
 └───────────────┬──────────────────────────────┘     └──────────────────────────────┘                               │
              no ▼                                                                                                   │
 ┌──────────────────────────────────────────────┐ yes ┌──────────────────────────────┐                               │
 │ D2: semantic cache valid enough under policy?├───> │ R1B SEM CACHE                ├───> [RETURN]                  │
 │ similarity + ACL + freshness pass            │     │ cache / short-circuit        │                               │
 └───────────────┬──────────────────────────────┘     └──────────────────────────────┘                               │
              no ▼                                                                                                   │
 ┌──────────────────────────────────────────────┐ yes ┌────────────────────────────────┐                             │
 │ D3: does this request need grounded context? ├───> │ R3 AGENTIC RAG                 │                             │
 │ retrieval / context infusion required?       │     │ returns grounded context only, │                             │
 └───────────────┬──────────────────────────────┘     │ no execution authority         │                             │
              no ▼                                    └──────────────┬─────────────────┘                             │
 ┌──────────────────────────────────────────────┐                    │                                               │
 │ D4: does this request need external action?  │                    ▼                                     ┌─────────┴─────────┐
 │ tool / workflow / side-effect required?      │     ┌────────────────────────────────┐               │L4 STATE/Archivist │
 └───────┬───────────────────────┬──────────────┘     │ C0 CONTEXT ENGINE (Ref Desk)   │──[reads]────> │read for C0 & PA   │
     yes │                    no │                    │ retrieves and grounds only     │               └─────────┬─────────┘
         ▼                       ▼                    │ never routes or executes       │                         │
 ┌──────────────────────┐ ┌──────────────────────┐    └──────────────┬─────────────────┘                         │
 │ R4 ACTION            │ │ R5 FALLBACK          │                   │ [evidence]                                │
 │ direct dispatch      │ │ direct dispatch      │                   ▼                                           │
 └───────┬──────────────┘ └──────┬───────────────┘     ┌────────────────────────────────┐                        │
         └───────────────┬───────┘                     │ PROMPT ASSEMBLY                │<─────[state load]──────┘
                         │                             │ packages grounded context for  │
                         └───────────────────────┬─────┤ active run / does not retrieve │
                                                 │     └─────────────┬──────────────────┘
                                                 │ [dispatch to [4]]
                                                 ▼

==============================================================================================================================
[4] RUNTIME DISPATCH + Execution
==============================================================================================================================
                                                 │ [dispatch from L0]
                                                 ├───>[simple execution]───────────────────────┐
                                                 │                                             │
                                                 ▼ [multi-step required]                       │
                                  ┌────────────────────────────────┐                           │
                                  │ L3 ORCHESTRATOR [opt] (Sec Head│                           │
                                  │ multi-step coordination only   │                           │
                                  └──────────────┬─────────────────┘                           │
                                                 │ [EXECUTE]                                   │
                                                 ▼                                             ▼
                                  ┌──────────────────────────────────────────────────────────────┐
                                  │  L2 EXECUTION (Execution Staff)                              │
                                  └──────────────┬───────────────────────────────────────────────┘
                                                 │ [L2 EXECUTION OUTPUT]
                                                 │ [dispatch to [5]]
                                                 ▼

==============================================================================================================================
[5] LIVE POST-L2 CONTROL + EVALUATION
==============================================================================================================================
                                                 ┌────────────────────────────────┐
                                                 │ LIVE EVALUATION SPINE          │
                                                 │ current-run judgment           │
                                                 │ - policy checks                │
                                                 │ - schema / sandbox validity    │
                                                 │ - outcome checks               │
                                                 │ - trajectory checks            │
                                                 │ - release-time regression chks │
                                                 └───────────────┬────────────────┘
                                                                 │
 ┌───────────────────────────────────────────────────────────────┴──┐<───[approve / deny / rework / reroute]───┐
 │ EXIT SPINE                                                       │                                          │
 │ Checkout / disposition authority                                 │           ┌──────────────────────────┐   │
 │ - allow / finish (no state mutation implied)          [ESCALATE]─┼───>       │ HITL                     │   │
 │ - deny                                                           │           │ human review             │   │
 │ - reroute / control                                              │           └────────────┬─────────────┘   │
 │ - escalate to HITL                                               │                        │                 │
 │ - COMMIT -> UWG only                                             │                        ▼                 │
 └─┬──────────────────────┬──────────────────────┬──────────────────┘           ┌──────────────────────────┐   │
   │                      │                      │                              │ HUMAN DISPOSITION        ├───┘
   ▼                      ▼                      ▼                              └────────────┬─────────────┘
[ALLOW /               [COMMIT ───>           [DENY /                                        │
 FINISH]                UWG ───> L4]           REROUTE] <────────────────────────────────────┘
   │                      │                      │
   └──────────────────────┼──────────────────────┘
                          │
                          │ [run complete ───> dispatch async to [6]]
                          ▼

==============================================================================================================================
[6] SHADOW EVALUATION + FUTURE-RUN LEARNING
==============================================================================================================================
                          │ [Runtime evidence + L4 artifacts]
                          ▼
                          ┌────────────────────────────────┐
                          │ SHADOW EVALUATION SPINE        │
                          │ future-run influence only,     │
                          │ never current-run mutation     │
                          │ - telemetry grading            │
                          │ - broader drift/replay/trend   │
                          │ - heavier regression/calibrat. │
                          └──────────────┬─────────────────┘
                  ┌──────────────────────┴──────────────────────┐
                  ▼                                             ▼
             [L6 OBSERVE]                        [PRODUCTION BUS / TESTING BUS]
                                                                │
                                                                ▼
                                                 ┌──────────────┴─────────────────────────────────┐
                                                 │ EVOLUTION / SYSTEM LEARNING LOOP               │
                                                 │ invariant: no current-run mutation             │
                                                 │ learning/promotion via approved rollout paths  │
                                                 │ to affect future runs only                     │
                                                 └──────────────┬─────────────────────────────────┘
                                                                ▼
                                            [USER ACCEPTANCE TESTING BUS FUTURE RUNS ONLY]

==============================================================================================================================
[ LEGEND ] LAYER DEFINITIONS (L0 - L6)
==============================================================================================================================
 LAYER │ PERSONA                  │ CORE FUNCTION / MEANING                                                                   
───────┼──────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────
 L0    │ Dispatcher               │ Route authority; determines execution path (cache, RAG, action, fallback).                
 L1    │ Librarian                │ Reasoning loop; formulates execution plans and dispatches to routing.                     
 L2    │ Execution Staff          │ Tool and action execution; interfaces with external systems to produce output.            
 L3    │ Orchestrator (Sec Head)  │ Optional multi-step orchestration; manages complex L2 execution chains.                   
 L4    │ Archivist                │ State and memory management; universal read/write surface for system state.               
 L5    │ Safety Officer           │ Cross-cutting policy plane; enforces guardrails across all runtime/exit points.           
 L6    │ Observer                 │ Shadow evaluation; monitors telemetry for future-run system learning and RCA.             
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────