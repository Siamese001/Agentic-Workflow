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
        |  [validated request]
        ▼
┌───────────────┐                                                                      ┌─────────────┐
│2. L1 INTERPRET│◄─────────────────────────────[reads]─────────────────────────────────┤ L4 ARCHIVE  │
│ • Parse Intent│                                                                      │ (Archivist) │
│ • Draft Plan  │                                                                      │ Read-only   │
│ • Validate    │                                                                      └──────┬──────┘
└───────┬───────┘                                                                             │
        │ [plan contract]                                                                     │
        ▼                                                                                     │
┌─────────────────────────────────┐                 ┌────────────────────────┐                │
│ 3. L0 ROUTING (Dispatcher)      │──[R2 Retrieve]─►│ C0 CONTEXT ENGINEERING │                │
│ Outputs:                        │                 │    / GROUNDING         │                │
│ • R1 Cache ─────[RET]───────────┼──┐              │ • Retrieve/Grnd 🟠     │                │
│ • R5 Fallback ──[RET]───────────┼──┤              └───────────┬────────────┘                │
│ • R2 Grounded Read (Single)     │  │                          │                             │
│ • R3/R4 Action/Workflow (Multi) │  │                          │ [evidence] 🟠               │
└───────┬─────────────────────────┘  │                          ▼                             │
        │                            │              ┌───────────┴────────────┐                │
        │ [route contract]           │              │ PROMPT ASSEMBLY        │◄───[state load]┘
        │                            │              │ (Sys•Ctx•Task)         │
        │                            │              └───────────┬────────────┘
        │                            │                          │
        │                            │                          │ [dispatch]
        │                            │                          │
        ├◄───────────────────────────┼──────────────────────────┘
        ▼                            │
┌───────┴────────────────────────┐   │          [!] R1/R5 skip L3/L2 and go straight to Exit Desk
│ L3 ORCHESTRATE (Manager)       │   │
│ • Step expansion/sequencing    │   │
│ • Multi-step dependency math   │   │
│ • Plan evolution (bounded)     │   │
└───────┬────────────────────────┘   │
        │                            │
        ▼                            ▼
┌───────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. L2 EXECUTE (Assistant) ◄── (handles current single step execution)                                           │
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
        ├◄────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        ├◄─────────────────────────────────────────────────────────┐
        ▼                                                          │
┌──────────────────────────────────┐                               │
│ 5. EXIT EVAL & CONTROL           ├─────[commit request]──────────┼────────────────────► ┌─────────────┐
│ - Final policy & safety review   │                               │                      │ UNIVERSAL   │
│ ◄── [ Receiving [RET] Short-     │                               │                      │ WRITE GATE  │
│       Circuits & Artifacts ]     │                               │                      └──────┬──────┘
└───────┬─┬─┬──────────────────────┘                               │                             │
        │ │ │                                                      │                             │ [commits]
        │ │ │                                                      │                             ▼
        │ │ └─[deny/reroute] ──► [ Reroute ]                       │                      ┌─────────────┐
        │ │                                                        │                      │ L4 ARCHIVE  │
        │ └─[escalate] ────────► ┌──────────────┐                  │                      │ (Writes)    │
        │  HIGH-RISK ACTIONS:    │ HUMAN REVIEW │                  │                      └─────────────┘
        │  pause for guardrails/ └──────┬───────┘                  │
        │  human approval before        │                          │
        │  irreversible writes          └─(resume)─────────────────┘
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