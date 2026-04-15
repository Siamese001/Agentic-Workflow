===================================================================================================================
                                  AGENTIC SYSTEM PROCESS MAP - EXECUTIVE SUMMARY
===================================================================================================================
 [!] SIMPLEST VIABLE PATTERN: deterministic workflow first -> single agent -> multi-agent only
 [i] AGENT CORE = model + tools + instructions + guardrails + evals
===================================================================================================================

[ L5 POLICY PLANE ] ──(Cross-cutting authority over all phases, exits, & Write Gate)───────────────────────────────
        │
        ▼
┌───────────────┐
│1. INTAKE CHECK│ ◄── (Auth, Quota, Malformed schema check. NO semantic routing)
└───────┬───────┘
        │ [Validated Request]
        │
        ▼
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██ ◄───────────────────────────────────── R U N T I M E   B E G I N S ─────────────────────────────────────────► ██
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████
        │
        ▼
┌───────────────┐                                                                      ┌─────────────┐
│2. L1 INTERPRET│◄─────────────────────────────[reads]─────────────────────────────────┤ L4 ARCHIVE  │
│ • Parse Intent│                                                                      │ (Archivist) │
│ • Draft Plan  │                                                                      │ Read-only   │
│ • Validate    │                                                                      └──────┬──────┘
└───────┬───────┘                                                                             │
        │                                                                                     │
        │ [plan]                                                                              │
        ▼                                                                                     │
┌─────────────────────────────────┐                 ┌────────────────────────┐                │
│ 3. L0 ROUTING                   │──[R2 Retrieve]─►│ C0 CONTEXT ENGINEERING │                │
│ Outputs:                        │                 │    / GROUNDING         │                │
│ • R1 Cache                      │                 │ • Retrieve/Grnd        │                │
│ • R2 Retrieve via C0            │                 └───────────┬────────────┘                │
│ • R3 Action / workflow          │                             │                             │
│ • R4 Direct model answer        │                             │ [evidence]                  │
│ • R5 Deny / escalate / fallback │                             ▼                             │
└───────┬─────────────────────────┘                 ┌───────────┴────────────┐                │
        │                                           │ PROMPT ASSEMBLY        │◄───[state load]┘
        │                                           │ (Sys•Ctx•Task)         │
        │                                           └───────────┬────────────┘
        │                                                       │
        │                                                       │ [dispatch]
        │                                                       │
        ├◄──────────────────────────────────────────────────────┘
        ▼
┌───────┴──────────┐
│ L3 ORCHESTRATE   │
│ • Manage Steps   │
│ • Coordinate Agt │
│ • Plan Evolution │
└───────┬──────────┘
        │
        ▼
┌───────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. L2 EXECUTE ◄── (handles current single step execution)                                                       │
│ * BOUNDED AUTONOMY: tool feedback each step | exit conditions | max turns                                       │
│  ┌────────┐   ┌─────────┐   ┌─────────┐   ┌────────┐   ┌────────┐                                               │
│  │E1: Prep│──►│E2: Valid│──►│E3: Exec │──►│E4: Heal│──►│E5: Seal│                                               │
│  └────────┘   └─────────┘   └─▲───────┘   └─┬──────┘   └────────┘                                               │
│                               │ [retry]     │                                                                   │
│                               └─────────────┘                                                                   │
└───────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        │ [sealed artifacts]
        │
        ├◄─────────────────────────────────────────────────────┐
        ▼                                                      │
┌───────────────┐                                              │
│ 5. EXIT EVAL  ├───────[commit request]───────────────────────┼────────────────────► ┌─────────────┐
│ & CONTROL     │                                              │                      │ UNIVERSAL   │
└───────┬─┬─┬───┘                                              │                      │ WRITE GATE  │
        │ │ │                                                  │                      └──────┬──────┘
        │ │ │                                                  │                             │
        │ │ └─[deny/reroute] ──► [ Reroute ]                   │                             │ [commits]
        │ │                                                    │                             ▼
        │ └─[escalate] ────────► ┌──────────────┐              │                      ┌─────────────┐
        │  HIGH-RISK ACTIONS:    │ HUMAN REVIEW │              │                      │ L4 ARCHIVE  │
        │  pause for guardrails/ └──────┬───────┘              │                      │ (Writes)    │
        │  human approval before        │                      │                      └─────────────┘
        │  irreversible writes          └─(resume)─────────────┘
        │
        │ [allow/finish]
        ▼
┌─────────────────┐
│ RESPONSE/OUTCOME│
└─────────────────┘
        │
        │                             [ ASYNC RUNTIME DATA EXHAUST ]
        └───────(Gathered from all layers: Traces, Artifacts, Outcomes)
                                                   │
███████████████████████████████████████████████████▼███████████████████████████████████████████████████████████████
██ ◄─────────────────────────────────────── R U N T I M E   B O U N D A R Y ───────────────────────────────────► ██
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████
                                                   │
 6. L6 SHADOW EVALUATION -> FUTURE-RUN LEARNING
                                                   ▼
 ┌────────────────┐   ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
 │ 6A. INGEST     │──►│ 6B. EVALUATE   │──►│ 6C. RCA/SYNTH  │──►│ 6D. PROMOTE /  │
 │ Map telemetry, │   │ Grade outcomes │   │ Root cause &   │   │ UPDATE         │
 │ traces, exits, │   │ trajectories,  │   │ and drift      │   │ UWG -> L4 ->   │
 │ artifacts      │   │ and drift      │   │ generation     │   │ Update Bus     │
 └────────────────┘   └────────────────┘   └────────────────┘   └────────┬───────┘
                                                                         │
                                                                         ▼
             [ FUTURE RUNTIME SURFACES UPDATED: Prompts, Policies, Baselines upgraded ]
===================================================================================================================