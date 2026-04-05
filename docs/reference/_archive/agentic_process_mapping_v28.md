==============================================================================================================================
                            AGENTIC SYSTEM — PROCESS MAP (CANONICAL SEMANTICS & LOOP)
 PRIMARY RUNTIME PATH: L1 ───> L0 ───> [opt L3] ───> L2 | L0 routing (R3) invokes C0 context assembly
                            L5 = cross-cutting policy | UNIVERSAL WRITE GATE = writes to L4
==============================================================================================================================

[ L5 POLICY PLANE / Safety Officer ] ──(cross-cutting authority over [1], [2], [3], [4], [5], [6], EXIT, UNIVERSAL WRITE GATE)──

===========================================================================================================
[1] REQUEST INTAKE + ENVELOPE CHECK
===========================================================================================================
- The front door of the system where every request is initially received, checked for basic validity, and verified for access rights before any actual thinking or routing begins.
- The library security guard and front desk greeter who checks your library card, makes sure you aren't carrying any banned items, and confirms you are allowed inside before you ever speak to a librarian.

                                             │ [ External Trigger ]
                                             ▼
                   ┌───────────────────────────────────────────────────┐
                   │ U0 REQUEST SOURCES                                │
                   │ - User UI / Chat Interface                        │
                   │ - Application API Calls                           │
                   │ - Scheduled / Asynchronous System Events          │
                   └─────────────────────────┬─────────────────────────┘
                                             │
                                             ▼
                   ┌───────────────────────────────────────────────────┐
                   │ INGRESS / ENVELOPE CHECK                          │
                   │ - Auth / Identity verification                    │
                   │ - Quota and rate limit enforcement                │
                   │ - Malformed request / schema rejection            │
                   │ - (Optional) Pre-layer sanitization               │
                   │ invariant: No semantic routing or reasoning here  │
                   └─────────────────────────┬─────────────────────────┘
                                             │
                                             │ [ Validated Request ]
                                             ▼
                                    [ Dispatch to [2] ]
===========================================================================================================
[2] L1 REASONING + PLAN GENERATION
===========================================================================================================
- The core thinking engine that breaks down a complex user request into a step-by-step plan. It gathers necessary rules and background knowledge but never takes direct action itself.
- The senior reference librarian who listens to your complex research question, figures out exactly which sections of the library contain the answers, and writes down a step-by-step research plan on a notepad.

                                         │ [ Validated User Request / Goal ]
                                         ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ INTENT & CONTEXT ANALYSIS                                                    │
 │ - Parse primary objectives, soft constraints, and hard constraints           │
 │ - Extract relevant entities, parameters, and required output formats         │
 └───────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                                         ▼
                 ┌───────────────────────┴───────────────────────┐             ┌────────────────────┐
                 │ MEMORY & PRIORS FETCH (Librarian)             │<──[reads]───│ L4 ARCHIVE         │
                 │ - Retrieve task schemas and routing heuristics│             │ Read-only source   │
                 │ - Load safety bounds and compliance policies  │             │ - Guardrails       │
                 │ - Fetch few-shot examples or standard SOPs    │             │ - Standard Ops     │
                 └───────────────────────┬───────────────────────┘             └────────────────────┘
                                         │
                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L1 REASONING LOOP                                                                                  │
│                                        │                                                           │
│                                        ▼                                                           │
│                  ┌───────────────────────────────────────────┐                                     │
│           ┌─────>│ PLAN SYNTHESIS                            │                                     │
│           │      │ - Decompose goal into atomic sub-tasks    │                                     │
│           │      │ - Resolve task dependencies (Seq vs DAG)  │                                     │
│           │      │ - Map sub-tasks to proposed tool routes   │                                     │
│           │      └─────────────────────┬─────────────────────┘                                     │
│           │                            │                                                           │
│   [Refine / Rework]                    ▼                                                           │
│           │      ┌───────────────────────────────────────────┐ yes ┌───────────────────────────┐   │
│           │      │ PLAN VALIDATION & REFLECTION              ├───> │ APPROVED PLAN             │   │
│           └──────┤ - Self-correct: Meets user constraints?   │     │ Structurally sound,       │   │
│             no   │ - Policy check: Proposed actions safe?    │     │ bounded, and policy-safe  │   │
│                  │ - Logic check: Dependencies resolvable?   │     └───────────┬───────────────┘   │
│                  └───────────────────────────────────────────┘                 │                   │
└────────────────────────────────────────────────────────────────────────────────┼───────────────────┘
                                                                                 │
                                                                                 │ [ Formalized Plan ]
                                                                                 ▼
                                                                        [ Dispatch to [3] ]
===========================================================================================================
[3] ROUTE DECISION + SWITCHING
===========================================================================================================
- The traffic controller that looks at the plan and decides exactly where each step needs to go—whether that's fetching a quick cached answer, pulling grounded context, or sending it off for external tool execution.
- The dispatch clerk at the main desk who looks at the senior librarian's notepad and routes the requests: sending a runner to the archives, pointing you to the quick-reference encyclopedia, or requesting an inter-library loan.

 ┌────────────────────────────────────┐
 │ L0 ROUTING (Dispatcher)            │
 │ Plan enters route authority        │
 └───────────────┬────────────────────┘
                 ▼
 ┌──────────────────────────────────────┐ yes ┌──────────────────────────────┐
 │ D1: Exact cache key hit by policy?   ├───> │ R1A EXACT CACHE              ├───> [ RETURN ]
 └───────────────┬──────────────────────┘     │ Short-circuit execution      │
              no ▼                            └──────────────────────────────┘
 ┌──────────────────────────────────────┐ yes ┌──────────────────────────────┐
 │ D2: Semantic cache valid by policy?  ├───> │ R1B SEMANTIC CACHE           ├───> [ RETURN ]
 └───────────────┬──────────────────────┘     │ Short-circuit execution      │
              no ▼                            └──────────────────────────────┘
 ┌──────────────────────────────────────┐ yes ┌────────────────────────────────┐
 │ D3: Requires grounded context?       ├───> │ R3 AGENTIC RAG                 │
 └───────────────┬──────────────────────┘     │ Returns context only           │
              no ▼                            └──────────────┬─────────────────┘
 ┌──────────────────────────────────────┐                    │
 │ D4: Requires external action?        │                    ▼                            ┌────────────────────┐
 └───────┬───────────────────────┬──────┘     ┌────────────────────────────────┐          │ L4 STATE / ARCHIVE │
     yes │                    no │            │ C0 CONTEXT ENGINE (Ref Desk)   │─[reads]─>│ Read-only for      │
         ▼                       ▼            │ Retrieves and grounds only     │          │ context & prompt   │
 ┌───────────────────┐ ┌───────────────────┐  │ Never routes or executes       │          └─────────┬──────────┘
 │ R4 ACTION         │ │ R5 FALLBACK       │  └──────────────┬─────────────────┘                    │
 │ Dispatch to       │ │ Dispatch to safe, │                 │ [Evidence]                           │
 │ external tool     │ │ ungrounded default│                 ▼                                      │
 └───────┬───────────┘ └──────┬────────────┘  ┌────────────────────────────────┐                    │
         │                    │               │ PROMPT ASSEMBLY                │<───[state load]────┘
         │                    │               │ Packages grounded context      │
         │                    │               │ Does not retrieve              │
         │                    │               └──────────────┬─────────────────┘
         │                    │                              │
         └────────────────────┴───────────────┬──────────────┘
                                              │
                                              ▼
                                     [ Dispatch to [4] ]

===========================================================================================================
[4] LIVE TASK DISPATCH & EXECUTION (The Library Stacks)
===========================================================================================================
- The active phase where work is done, but nothing is permanently saved yet.
- Library Analogy: Assistants enter the restricted stacks to gather info, fix minor mistakes, 
  and seal findings for review. They cannot write in the permanent catalog themselves.

                                                 │ [ Handed down from Front Desk ]
                                                 ▼
                           ┌─────────────────────┴─────────────────────┐
                           ▼                                           ▼
                 ┌───────────────────┐                       ┌───────────────────┐
                 │ SIMPLE TASK       │                       │ COMPLEX TASK      │
                 │ Go find one       │                       │ Multi-step        │
                 │ specific book     │                       │ research project  │
                 └─────────┬─────────┘                       └─────────┬─────────┘
                           │                                           │
                           └─────────────────────┬─────────────────────┘
                                                 │ [ Approved Work Order ]
                                                 ▼

        ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ TASK EXECUTION CORE (Library Assistants)                                                            │
        │ Strict Rules: No human help | No permanent updates | Must use exact same rulebook for everything    │
        └──────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                       ▼

        ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ E1. PREPARATION DESK                                                                                │
        │ [ Intake Counter ]                                                                                  │
        │ - Lock in available time, tools, and permissions                                                    │
        │ - Attach a unique tracking ticket to avoid duplicate work                                           │
        │ - Lock in the specific rulebook version to be used                                                  │
        └──────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                       │
                                                       ▼
        ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ E2. WORK ORDER CHECK                                                                                │
        │ [ Packet Inspection Desk ]                                                                          │
        │ - Verify the work order is authentic and makes sense                                                │
        │ - Check assistant permissions and available time limits                                             │
        │ - Stamp as "Approved to Start" if valid                                                             │
        │                                                                                                     │
        │ FAIL here = Request rejected before any work starts                                                 │
        └──────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                       │ [ Approved Work Order ]
                                         ┌─────────────┴─────────────┐
                                         │                           │
                                       pass                        fail
                                         │                           │
                                         ▼                           ▼
        ┌────────────────────────────────────────────────┐   ┌───────────────────────────────────┐
        │ E3. DOING THE WORK                             │   │ REJECTED REQUEST FOLDER           │
        │ [ The Study Carrel ]                           │   │ - Reason for rejection            │
        │ - Start the clock and track attempts           │   │ - No actual work was performed    │
        │ - Use tools to find information                │   └───────────────────┬───────────────┘
        │ - Record notes, scratchpad, and answers        │                       │
        │ - Grade result:                                │                       │
        │   • SUCCESS (Got the info)                     │                       │
        │   • FIXABLE (Made a small error)               │                       │
        │   • COMPLETE FAILURE (Hit a dead end)          │                       │
        └───────────────────────┬────────────────────────┘                       │
                                │                                                │
            ┌───────────────────┼───────────────────────┐                        │
            │                   │                       │                        │
            ▼                   ▼                       ▼                        │
       [ SUCCESS ]         [ FIXABLE ]         [ COMPLETE FAILURE ]              │
            │                   │                       │                        │
            │                   ▼                       │                        │
            │    ┌────────────────────────────────────────────────────────────┐  │
            │    │ E4. FIXING DESK                                            │  │
            │    │ [ Repair Bench ]                                           │  │
            │    │ - Note exactly what went wrong                             │  │
            │    │ - Check rules to avoid endless loops                       │  │
            │    │ - Apply a strictly allowed fix                             │  │
            │    │ - Log the repair and try again                             │  │
            │    └───────────────────────┬────────────────────────────────────┘  │
            │                            │                                       │
            │                ┌───────────┴───────────┐                           │
            │                │                       │                           │
            │             repaired              not repaired                     │
            │                │                       │                           │
            │                ▼                       ▼                           │
            │         [ back to E3 ]         [ GIVE UP / ASK BOSS ]              │
            │                                           │                        │
            └───────────────────────────────┬───────────┴────────────────────────┘
                                            │
                                            ▼
        ┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ E5. SEAL THE FINAL FOLDER                                                                           │
        │ [ Records Folder Sealing ]                                                                          │
        │ - Package the final answers, notes, and proof of work                                               │
        │ - Propose updates (do NOT change the main catalog yet)                                              │
        │ - Seal folder securely                                                                              │
        │                                                                                                     │
        │ Terminal folders: SUCCESS | FAILURE | NEEDS HELP | REJECTED                                         │
        └──────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                       │ [ Sealed Folders ]
                                                       ▼
                                             [ Send to Next Step [5] ]

===========================================================================================================
[5] LIVE RUNTIME EXIT CONTROL + CURRENT-RUN EVALUATION
===========================================================================================================
- The final quality assurance checkpoint that reviews the completed work to ensure it's safe, accurate, and fully answers the prompt before delivering it to the user and requesting a permanent record be saved.
- The head librarian who reviews the compiled folder of research before handing it to you, ensuring it directly answers your question and follows all library policies, then signs off to have a copy filed in the permanent records.

                                             │ [ Sealed L2 Artifacts ]
                                             ▼
                   ┌───────────────────────────────────────────────────┐
                   │ CURRENT-RUN EVALUATION & EXIT CONTROL             │
                   │ - Evaluate outputs against policies and baselines │
                   │ - Determine runtime disposition                   │
                   └─────────────────────────┬─────────────────────────┘
                                             │
                     ┌───────────────────────┼───────────────────────┐
                     ▼                       ▼                       ▼
           ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
           │ DENY / REROUTE    │   │ ESCALATE (HITL)   │   │ COMMIT REQUEST    │
           │ Reject or rework  │   │ Human review gate │   │ Request L4 update │
           └───────────────────┘   └───────────────────┘   └─────────┬─────────┘
                                                                     │
                                                                     ▼
                                                            ┌──────────────────────┐
                                                            │ UNIVERSAL WRITE GATE │
                                                            │ -> L4 ARCHIVE        │
                                                            │ Durable Commit       │
                                                            └──────────┬───────────┘
                                                                       │
                                                                       ▼
                                                                [ Run Complete ]
                                                                       │
                                                                       ▼
███████████████████████████████████████████████████████████████████████████████████████████████████████████
██                                                                                                       ██
██ ◄─────────────────────────── R U N T I M E   B O U N D A R Y   R E A C H E D ───────────────────────► ██
██                                                                                                       ██
███████████████████████████████████████████████████████████████████████████████████████████████████████████
                                                                       │
                                                                       ▼
                                         [ Runtime Evidence & Committed L4 Artifacts ]
                                                                       │
                                                                       ▼
===========================================================================================================
[6] SHADOW EVALUATION + FUTURE-RUN LEARNING
===========================================================================================================
- An asynchronous, background process that reviews past interactions to identify mistakes, improve future performance, and update the system's core instructions and rules.
- The library board of directors meeting after hours to review the day's visitor logs and complaint box, using those insights to rewrite the employee handbook and reorganize the catalog system for tomorrow.

        ┌──────────────────────────────────────────────────────────────────────────────┐
        │ SHADOW EVALUATION & L6 OBSERVABILITY                                         │
        │ - Ingest telemetry, traces, and exit outcomes                                │
        │ - Grade performance, detect system drift, and map failure clusters           │
        └──────────────────────────────┬───────────────────────────────────────────────┘
                                       │
                                       ▼
                       ┌──────────────────────────────────────────────┐
                       │ EVOLUTION & SYSTEM LEARNING LOOP             │
                       │ - Root Cause Analysis (RCA) intake           │
                       │ - Synthesize rule, prompt, and config drafts │
                       └───────────────┬──────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
          ┌───────────────────┐                 ┌────────────────────┐
          │ REJECT / HOLD     │                 │ APPROVED PROMOTION │
          │ (No Action)       │                 └─────────┬──────────┘
          └───────────────────┘                           │
                                                          ▼
                                                ┌──────────────────────┐
                                                │ UNIVERSAL WRITE GATE │
                                                │ Sole Write Gate      │
                                                └──────────┬───────────┘
                                                           │
                                                           ▼
                                                ┌────────────────────┐
                                                │ L4 ARCHIVE         │
                                                │ Source of Truth    │
                                                └─────────┬──────────┘
                                                          │
                                                          ▼
                                                ┌────────────────────┐
                                                │ UPDATE BUS         │
                                                │ Rollout Publisher  │
                                                └─────────┬──────────┘
                                                          │
                                                          ▼
          ┌───────────────────────────────────────────────────────────────────────────────┐
          │ FUTURE RUNTIME SURFACES UPDATED                                               │
          │ (Prompts, Policies, Baselines, and Logic upgraded for subsequent runs only)   │
          └───────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[ LEGEND ] LAYER DEFINITIONS (L0 - L6)
==============================================================================================================================
 LAYER │ PERSONA                  │ CORE FUNCTION / MEANING                                                                   
───────┼──────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────
 L0    │ Dispatcher               │ Route authority; determines execution path (cache, RAG, action, fallback).                
 L1    │ Librarian                │ Reasoning loop; formulates execution plans and dispatches to routing.                     
 L2    │ Execution Staff          │ Tool and action execution; interfaces with external systems to produce output.            
 L3    │ Orchestrator (Sec Head)  │ Optional multi-step orchestration; manages complex L2 execution chains.                   
 L4    │ Archivist                │ Authoritative state; durable writes via UNIVERSAL WRITE GATE only. Broad read, strict write authority.     
 L5    │ Safety Officer           │ Cross-cutting policy plane; enforces guardrails across all runtime/exit points.           
 L6    │ Observer                 │ Shadow evaluation; monitors telemetry for future-run system learning and RCA.             
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────