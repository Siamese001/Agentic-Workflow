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
- The library security guard and front desk greeter who checks your library card, screens the form, normalizes the slip, and stamps a bounded request packet that later staff are allowed to read.

                                                                  [ arrive ]
                                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ U0 REQUEST SOURCES                                                                                                                 │
│ ┌────────────────────────────────┐ ┌────────────────────────────────┐ ┌────────────────────────────────┐ ┌───────────────────────┐ │
│ │ U1 USER / CHAT ENTRY           │ │ U2 APP / API ENTRY            │ │ U3 SCHEDULED / BATCH ENTRY    │ │ U4 CALLBACK / ALERT   │ │
│ │ - direct conversation          │ │ - service-to-service handoff  │ │ - recurring jobs              │ │ - async notices       │ │
│ │ - UI sessions                  │ │ - formal application calls    │ │ - mail-room style drop-offs   │ │ - webhook / signal    │ │
│ └───────────────┬────────────────┘ └───────────────┬────────────────┘ └───────────────┬────────────────┘ └───────────┬───────────┘ │
│                 │                                  │                                  │                            │               │
│             [source]                           [source]                           [source]                     [source]            │
│                 └──────────────────────────────────┴───────────────┬──────────────────┴────────────────────────────┘               │
│                                                                    │                                                               │
│                                                                [ queue ]                                                           │
│                                                                    ▼                                                               │
│                                   [ people, forms, callbacks, alerts, and batched letters waiting in line ]                       │
└────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                                 [ intake ]
                                                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ THE FRONT DESK / SECURITY CHECK                                                                                                    │
│ Rule: We do not answer, reason, retrieve, or route here. We only validate the envelope, normalize the slip, and stamp ingress.     │
│ invariant: No semantic routing, no L1 planning, no C0 retrieval, no external calls, no mutation authority.                         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────┐ ┌────────────────────────────────────────┐ ┌────────────────────────────────────────┐  │
│  │ E1 REAL REQUEST + ACCESS BASELINE      │ │ E2 ENVELOPE VALIDITY + LIMITS         │ │ E3 NORMALIZE + STAMP                  │  │
│  │ - accepted transport / form            │ │ - schema / required fields            │ │ - normalized payload                  │  │
│  │ - auth / identity / tenant bind        │ │ - quota / abuse / duplicate guard     │ │ - validated_request                   │  │
│  │ - region / caller scope baseline       │ │ - supported request shape only        │ │ - request_id / session_id / trace_root│  │
│  │ - request shell + trace_root started   │ │ - reject malformed or oversized asks  │ │ - safe packet for later staff         │  │
│  └───────────────────┬────────────────────┘ └───────────────────┬────────────────────┘ └───────────────────┬────────────────────┘  │
│                   [verify]                                     [validate]                                  [stamp]                   │
│                      └──────────────────────────────────────────────┬─────────────────────────────────────────┘                     │
│                                                                     ▼                                                              │
│                             [ a clean, stamped request packet with tracking number and bounded caller scope ]                      │
└─────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                                                      │
                                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ INGRESS OUTPUT CONTRACT                                                                                                            │
│ - validated_request                                                                                                                │
│ - request_id / session_id / trace_root                                                                                             │
│ - caller_scope_baseline / tenant bind / access baseline                                                                            │
│ - normalized payload                                                                                                               │
│ - rejection reason if denied                                                                                                       │
│ invariant: ingress stamps the slip but does not decide the route or answer the patron                                             │
└──────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                   │
                                                   ┌───────────────┴───────────────┐
                                          [ pass ] │                               │ [ fail ]
                                                   ▼                               ▼
                                     ┌───────────────────────────┐   ┌─────────────────────────────┐
                                     │ Send to Research Desk [2] │   │ Reject / Ask to Refill Form │
                                     └───────────────────────────┘   └─────────────────────────────┘

===========================================================================================================
[2] L1 REASONING + PLAN GENERATION
===========================================================================================================
- The senior reference librarian reads the stamped request slip, understands the actual goal, loads governing rules and priors, and writes the bounded plan that later routing may act on.
- L1 may think, decompose, compare options, and self-correct, but it never retrieves evidence directly, never routes with authority, never executes tools, and never mutates durable state.

                                                          │ [ goal ]
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ READING THE PATRON'S SLIP                                                                                       │
│ ┌────────────────────────────┐ ┌────────────────────────────┐ ┌──────────────────────────────────────────────┐ │
│ │ I1 GOAL + SUCCESS CONDITION│ │ I2 CONSTRAINTS + RULES     │ │ I3 DETAILS + WORK CLASS                     │ │
│ │ - primary objective        │ │ - hard / soft constraints  │ │ - entities, numbers, deliverable, format    │ │
│ │ - requested end-state      │ │ - must / should / avoid    │ │ - summarize / compare / analyze / act       │ │
│ │ - answer / plan / artifact │ │ - scope / exclusions       │ │ - work class drives later plan shape        │ │
│ └──────────────┬─────────────┘ └──────────────┬─────────────┘ └──────────────────────┬───────────────────────┘ │
│             [parse]                        [bound]                                 [frame]                      │
│                └─────────────────────────────┴─────────────────────────────────────────┘                         │
│                                                          ▼                                                      │
│         [ clear intent frame = goal + constraints + details + output target + work class + success condition ]  │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │ [ context ]
                                                           ▼
┌──────────────────────────────────────────────────────────┴────────────────────────────────┐┌────────────────────┐
│ GATHERING RULES, EXAMPLES, AND PRIORS                                                     ││ L4 ARCHIVE         │
│ ┌──────────────────────────┐┌──────────────────────────┐┌───────────────────────────────┐ ││ Read-only source   │
│ │ M1 TASK SCHEMAS + ROUTES ││ M2 SAFETY / POLICY      ││ M3 EXAMPLES + APPROVED PATTERNS│ ││ - Guardrails       │
│ │ - task schemas           ││ - compliance bounds     ││ - prior good answers           │ ││ - standard ops     │
│ │ - output contracts       ││ - escalation thresholds ││ - SOPs / exemplars             │ ││ - prior examples   │
│ │ - route heuristics       ││ - disallowed actions    ││ - stopping rules / priors      │ ││ - approved plans   │
│ └────────────┬─────────────┘└────────────┬─────────────┘└───────────────┬───────────────┘ │└────────────────────┘
│           [load]                      [bound]                        [bundle]              │
│              └──────────────────────────┴──────────────────────────────┘                    │
│                                                          ▼                                 │
│                 [ plan bundle = schemas + policy + examples + priors + approved patterns + limits ]           │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │ [ reason ]
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ THE THINKING DESK (L1 REASONING LOOP)                                                                           │
│ invariant: internal non-linearity stays here only. L1 can draft, inspect, refine, simplify, clarify, or       │
│ abstain, but cannot execute.                                                                                     │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────┐ ┌────────────────────────────────┐ ┌──────────────────────────────────────┐ │
│ │ T1 INTERPRET THE REQUEST       │ │ T2 DRAFT THE PLAN             │ │ T3 VALIDATE / SIMPLIFY / CLARIFY    │ │
│ │ - contextual refinement of the │ │ - break goal into work units  │ │ - does it answer the real goal?     │ │
│ │   visible request before plan  │ │ - order dependencies          │ │ - is it safe and coherent?          │ │
│ │ - identify explicit unknowns   │ │ - propose route options only  │ │ - lowest viable agency?             │ │
│ │ - sharpen what matters most    │ │ - mark grounding / support    │ │ - clarify or abstain if needed      │ │
│ └──────────────┬─────────────────┘ └──────────────┬─────────────────┘ └──────────────────────┬───────────────┘ │
│             [interpret]                       [draft]                                     [check]               │
│                └────────────────────────────────┴─────────────────────────────────────────────┘                  │
│                                                          ▼                                                      │
│            [ pass -> approve plan | fail -> refine / simplify / clarify / abstain within L1 only ]             │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │ [ output ]
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L1 PLAN OUTPUT CONTRACT                                                                                         │
│ - proposed_route: R1 / R3 / R4 / R5                                                                            │
│ - query_spec / task_spec / route_risk / confidence                                                              │
│ - grounding_required / declared assumptions / unresolved gaps                                                   │
│ invariant: L1 produces the notepad plan only. It does not retrieve evidence, route with authority, or perform   │
│ the work.                                                                                                       │
└───────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                        │ [ handoff ]
                                                        ▼
                                         [ Send to Hallway Director [3] ]

===========================================================================================================
[3] ROUTE DECISION + SWITCHING
===========================================================================================================
[ PEDAGOGICAL LEGEND ]  🔵 Blue asks = query_vec / intent vector
                        🟠 Orange knows = raw_text_vector / contextual_text_vector
                        🟢 Green maps = knowledge_graph / entity_subgraph
                        [RET] = Terminal early exit; bypasses L3 and returns to Exit Control

===========================================================================================================

 ┌──────────────────────────────────────────────┐                               ┌────────────────────────────────────┐
 │ L0 ROUTING (Dispatcher)                      │                               │ L4 STATE / ARCHIVE                 │
 │ - Ingress: approved L1 plan + 🔵 query_vec   │                               │ - Universal Persistence Boundary   │
 │ - Pre-filter: tenant / ACL / region bounds   │                               │ - Cache Stores (Exact/Sem.)        │
 │ - Enforce expiry / freshness requirements    │                               │ - Canonical raw chunks 🟠          │
 │ - Fast Fail: reject invalid scope early      │                               │ - Dense vector / sparse index 🟠   │
 │ - Score: cache / grounded / action /         │                               │ - Knowledge graph & entities 🟢    │
 │   workflow / support / freshness needs       │                               │ - Canonical source lineage         │
 │ - Emit route contract, not the work itself   │                               │ - Version manifests / schema       │
 └──────────────────────┬───────────────────────┘                               │ - No direct write path exists      │
                        │                                                       └──────────────────┬─────────────────┘
                        ▼                                                                          │
 ┌──────────────────────────────────────────────┐                                                  │
 │ L0 ROUTE DECISION SWITCH                     │                                                  │
 │ The dispatcher selects ONE path family:      │                                                  │
 │ terminal, single-step, or managed workflow.  │                                                  │
 └─┬────────────────────────────────────────────┘                                                  │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R1A EXACT CACHE                        │◄──────────────────────────────────────────────────┤
   │  │ - Perfect keyed reuse, zero infer      │                                                   │
   │  │ - Exact prior answer                   ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Short-circuit path                   │                                                   │
   │  │ - NO C0 NEEDED, NO L3 NEEDED           │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R1B SEMANTIC CACHE                     │◄──────────────────────────────────────────────────┤
   │  │ - Policy-approved similarity reuse     │                                                   │
   │  │ - Matches 🔵 ask vs 🔵 cached asks     ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Reuse-safe bounded task class        │                                                   │
   │  │ - NO C0 NEEDED, NO L3 NEEDED           │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R5 FALLBACK                            │                                                   │
   │  │ - Safest bounded outcome               │                                                   │
   │  │ - Abstain / clarify / safe default     ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Terminal safe route                  │                                                   │
   │  │ - NO C0 NEEDED, NO L3 NEEDED           │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R3 SIMPLE GROUNDED READ                │                                                   │
   │  │ - Factual / policy claims need backing │                                                   │
   │  │ - Strictly grounded answer only        │                                                   │
   │  │ - Single-pass grounding                │                                                   │
   │  │ - Bypasses L3, still needs one L2 step │                                                   │
   │  └───────────────────┬────────────────────┘                                                   │
   │                      ▼                                                                        │
   │  ┌────────────────────────────────────────┐                                                   │
   │  │ C0 CONTEXT ENGINE (Ref Desk)           │◄──────────────[ Read ]────────────────────────────┤
   │  │ - Scope source / freshness / ACL       │                                                   │
   │  │ - Match 🔵 ask against 🟠 evidence      │                                                   │
   │  │ - May traverse 🟢 graph relations       │                                                   │
   │  │ - Dedupe / rerank / verify support     │                                                   │
   │  └───────────────────┬────────────────────┘                                                   │
   │                      │ [Evidence Contract]                                                    │
   │                      ▼                                                                        │
   │  ┌────────────────────────────────────────┐                                                   │
   │  │ PROMPT ASSEMBLY                        │◄──────────────[ Load ]────────────────────────────┘
   │  │ - Load system template + schema        │
   │  │ - Slot grounded context 🟠             │
   │  │ - Budget / trim / reserve tokens       │
   │  │ - Emit bounded prompt packet           │
   │  │ - Packages only, does not retrieve     │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │       [ L2 Execute Single Grounded Step ]──────► [RET] ──► To 5. EXIT EVAL & CONTROL
   │
   │  ┌────────────────────────────────────────┐
   ├──► R4 SINGLE ACTION                       │
   │  │ - Dispatch one bounded external action │
   │  │ - Mutation-capable but tightly scoped  │
   │  │ - Direct single-step path to L2        │
   │  │ - NO C0 NEEDED, NO L3 NEEDED           │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │             [ L2 Execute Single Step ]─────────► [RET] ──► To 5. EXIT EVAL & CONTROL
   │
   │  ┌────────────────────────────────────────┐
   └──► R3/R4 MANAGED WORKFLOW                 │
      │ - Multi-hop grounded read or action    │
      │ - Dependency order / branching / joins │
      │ - Needs resumable workflow state       │
      │ - L3 orchestration required            │
      └───────────────────┬────────────────────┘
                          │
                          ▼
       ┌──────────────────────────────────────────────────────────────────────┐
       │ L3 ORCHESTRATE (Manager)                                             │
       │ - Ingress: approved route package from L0                            │
       │ - Expand route into managed executable steps                         │
       │ - Preserve route bounds, budget, and policy limits                   │
       └──────────────┬───────────────────────────────┬──────────────────────┘
                      │                               │
                      ▼                               ▼
       ┌──────────────────────────────────┐   ┌──────────────────────────────┐
       │ L3.1 STEP EXPANSION              │   │ L3.2 WORKFLOW STATE          │
       │ - Break goal into bounded steps  │   │ - Track current node/status  │
       │ - Sequence dependencies          │   │ - Hold checkpoints/handoffs  │
       │ - Mark serial vs parallel-safe   │   │ - Support resumable progress │
       └────────────────┬─────────────────┘   └───────────────┬──────────────┘
                        │                                     │
                        └──────────────────┬──────────────────┘
                                           ▼
       ┌──────────────────────────────────────────────────────────────────────┐
       │ L3.3 READINESS + HANDOFF                                             │
       │ - Select only steps whose prerequisites are satisfied                │
       │ - Carry forward needed 🔵 asks, 🟠 evidence, and 🟢 graph outputs     │
       │ - Hand the current bounded step to L2                                │
       │ - Accept returned status/artifacts and move the workflow forward     │
       └──────────────────────────────┬───────────────────────────────────────┘
                                      ▼
                           [ Return sealed work ──► To 5. EXIT EVAL & CONTROL ]

========================================================================================================================================
[4] L2 EXECUTE (Assistant)
[4] THE BACK ROOMS | DOING THE WORK (IN THE STACKS)
========================================================================================================================================
- The active phase where the bounded work is done, but nothing is permanently written yet.
- Library Analogy: assistants enter the restricted stacks to gather, run, repair, and seal findings under the same
  approved work order. They cannot route, ask humans, or write in the permanent catalog.

                  [ SINGLE-STEP ROUTES ]                                      [ MANAGED WORKFLOW ROUTES ]
        [ L0 direct bounded step packet ]                                  [ L3 current-step handoff ]
                              │                                                          │
                              └──────────────────────────────┬───────────────────────────┘
                                                             │ [ governed handoff ]
                                                             ▼
                                           ┌─────────────────┴─────────────────┐
                                           ▼                                   ▼
                                 ┌───────────────────┐               ┌───────────────────┐
                                 │ SIMPLE TASK       │               │ COMPLEX TASK      │
                                 │ one bounded step  │               │ current ready step│
                                 └─────────┬─────────┘               └─────────┬─────────┘
                                           │                                   │
                                           └─────────────────┬─────────────────┘
                                                             │ [ approved work order ]
                                                             ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L2 EXECUTION CORE                                                                                                                   │
│ Strict Rules: No routing | No human interaction | No durable commit authority                                                       │
│ - Work arrives already approved and bounded                                                                                          │
│ - Same governing snapshot must hold across validation, execution, and healing                                                       │
│ - L2 performs the current step only; it does not expand workflow scope                                                              │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E1. PREPARATION DESK                                                                                                                 │
│ [ Intake Counter ]                                                                                                                   │
│ - Accept the signed step packet / current-step contract                                                                              │
│ - Lock environment, tools, permissions, and execution budget                                                                         │
│ - Bind stable run identity and execution lineage                                                                                     │
│ - Freeze the governing blueprint/policy snapshot for this step                                                                       │
│ - Prepare the step so later healing works against the same approved frame                                                            │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     │
                                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E2. WORK ORDER CHECK                                                                                                                 │
│ [ Packet Inspection Desk ]                                                                                                           │
│ - Confirm the step packet is authentic and internally consistent                                                                     │
│ - Verify permissions, scope, and runtime budget                                                                                      │
│ - Validate shape of inputs and expected side-effect class                                                                            │
│ - Confirm the step can be executed as handed off, without rerouting                                                                  │
│                                                                                                                                    │
│ PASS -> stamp Approved to Start                                                                                                      │
│ FAIL -> sealed rejection before any work starts                                                                                      │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     │ [ Approved Work Order ]
                                         ┌───────────────────────────┴───────────────────────────┐
                                         │                                                       │
                                       pass                                                    fail
                                         │                                                       │
                                         ▼                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐   ┌───────────────────────────────────┐
│ E3. DOING THE WORK                                                                                                     │   │ REJECTED REQUEST FOLDER           │
│ [ The Study Carrel ]                                                                                                   │   │ - Reason for rejection            │
│ - Invoke the required tool/model/action                                                                                │   │ - No actual work was performed    │
│ - Run under bounded time, policy, and sandbox limits                                                                   │   │ - Sealed before execution         │
│ - Capture outputs, traces, and intermediate execution evidence                                                         │   └───────────────────┬───────────────┘
│ - Classify result as: SUCCESS / FIXABLE / COMPLETE FAILURE                                                             │
└────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────┘
                                                     │
                            ┌────────────────────────┼──────────────────────────┐
                            │                        │                          │
                            ▼                        ▼                          ▼
                       [ SUCCESS ]             [ FIXABLE ]              [ COMPLETE FAILURE ]
                            │                        │                          │
                            │                        ▼                          │
                            │     ┌────────────────────────────────────────────────────────────────────────────┐
                            │     │ E4. FIXING DESK                                                         │
                            │     │ [ Repair Bench ]                                                        │
                            │     │ - Identify what failed and why                                          │
                            │     │ - Apply only bounded, allowed repair actions                            │
                            │     │ - Keep the same governing snapshot and step lineage                     │
                            │     │ - Check retry limits so the step does not loop forever                  │
                            │     │ - If repaired, send back to E3                                          │
                            │     │ - If not repaired, mark NEEDS_HELP or terminal failure                  │
                            │     └───────────────────────────────┬────────────────────────────────────────┘
                            │                                     │
                            │                         ┌───────────┴───────────┐
                            │                         │                       │
                            │                      repaired              not repaired
                            │                         │                       │
                            │                         ▼                       ▼
                            │                  [ back to E3 ]         [ GIVE UP / NEED HELP ]
                            │                                                 │
                            └─────────────────────────────┬───────────────────┴─────────────────────────────┘
                                                          │
                                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E5. SEAL THE FINAL FOLDER                                                                                                            │
│ [ Records Folder Sealing ]                                                                                                           │
│ - Package the final output, notes, and execution evidence                                                                            │
│ - Attach traces, lineage, and validation history                                                                                     │
│ - Attach replay-oriented receipts and attempt counters                                                                               │
│ - Seal the step result as an L2 artifact for downstream control                                                                      │
│                                                                                                                                    │
│ Terminal classes: SUCCESS | FAILURE | NEEDS_HELP | REJECTED                                                                         │
│ Invariant: no durable commit here. L2 only emits sealed artifacts for downstream control.                                           │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     │ [ Sealed Folders / Step Results ]
                                                                     ▼
                                                           [ Send to Next Step [5] ]

========================================================================================================================================
[5] EXIT EVAL & CONTROL
[5] THE EXIT DESK | FINAL REVIEW BEFORE RESPONSE OR COMMIT
========================================================================================================================================
- The final runtime checkpoint that receives either a sealed L2 result or a terminal [RET] short-circuit from L0.
- Library Analogy: the head desk reviews the finished folder, decides whether it can leave safely, whether it needs human review,
  whether it must be sent back, or whether it may request real ink through the Master Clerk.

                                    [ Sealed L2 Artifacts ]                    [RET] Short-Circuit from L0
                                                  │                                      │
                                                  └──────────────────┬───────────────────┘
                                                                     │ [ runtime disposition input ]
                                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. EXIT EVAL & CONTROL                                                                                                               │
│ - Final runtime policy, safety, and quality review                                                                                   │
│ - Receives only sealed runtime outputs or terminal short-circuits                                                                    │
│ - Produces explicit disposition only: allow/finish, deny/reroute, escalate, or commit request                                       │
│                                                                                                                                    │
│ CURRENT-RUN EVALUATION                                                                                                               │
│ - Policy / baseline fit                                                                                                              │
│ - Answered the request in the required form                                                                                          │
│ - Safe to leave: integrity, isolation, mutation authorization                                                                        │
│ - Answer quality: groundedness, citation/support, completeness                                                                       │
└───────┬─┬─┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │ │ │
        │ │ └─[deny/reroute] ──► ┌────────────────────────────────┐
        │ │                      │ DENY / REROUTE                 │
        │ │                      │ - hard rule break or failed    │
        │ │                      │   runtime evaluation           │
        │ │                      │ - send back to safe path       │
        │ │                      └────────────────────────────────┘
        │ │
        │ └─[escalate] ────────► ┌─────────────────────────────────────────────────────┐
        │                        │ HUMAN REVIEW                                        │
        │                        │ - bounded packet: reason + evidence + runtime trace │
        │                        │ - decision: approve / modify / reject               │
        │                        │ - resumed path must re-enter governed flow           │
        │                        └───────┬─────────────────────────────────────────────┘
        │                                │
        │                                └─(resume/allow)──────────────────────────────────────┐
        │                                                                                       │
        ├───────[commit request]─────────────────────────────────────────────────────────────────┼────────────────────► ┌────────────────────────────────────────┐
        │                                                                                       │                      │ UNIVERSAL WRITE GATE (UWG)             │
        │                                                                                       │                      │ - sole durable commit authority        │
        │                                                                                       │                      │ - verifies authority, scope, and diff  │
        │                                                                                       │                      │ - commits approved mutation to L4      │
        │                                                                                       │                      └───────────────────┬────────────────────┘
        │                                                                                       │                                          │ [commits]
        │                                                                                       │                                          ▼
        │                                                                                       │                      ┌────────────────────────────────────────┐
        │                                                                                       │                      │ L4 ARCHIVE                             │
        │                                                                                       │                      │ (Durable Writes / Ledger)              │
        │                                                                                       │                      └────────────────────────────────────────┘
        │
        │ [allow/finish]
        ▼
┌──────────────────────────────────────────────────┐
│ RESPONSE / OUTCOME                               │◄───────────────────────────────────────────────────────────────────────────────────┘
│ - return runtime answer or terminal disposition  │
│ - no durable write occurs here                   │
└───────────────────────┬──────────────────────────┘
                        │
                        ▼
            [ RETURN TO CALLER (U0) ]

                        │
                        │                             [ ASYNC RUNTIME DATA EXHAUST ]
                        └───────(Gathered from all layers: Traces, Artifacts, Outcomes, reason codes, commit status)
                                                   │
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██ ◄──────────────────────────────────────────────────────────── R U N T I M E   B O U N D A R Y ─────────────────────────────────────► ██
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
                                                   │
                                        [ SEND TO SHADOW LEARNING [6] ]
                                                   │
 6. L6 SHADOW EVALUATION -> FUTURE-RUN LEARNING (The Night Shift / Board Meeting)
 [!] EVAL MUST PRECEDE LEARNING: firewalled evaluation must complete before any future-run promotion
 [i] CONSTRAINTS: No Live Patron Impact | Future Visits Only | Floor Staff Propose Only | UWG = Sole Ink Path
                                                   ▼
 ┌───────────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐   ┌───────────────────────────┐
 │ 6A. INGEST                │──►│ 6B. EVALUATE             │──►│ 6C. RCA/SYNTH             │──►│ 6D. PROMOTE / UPDATE      │
 │                           │   │                           │   │                           │   │                           │
 │ - Map telemetry, traces,  │   │ - Grade outcomes,         │   │ - Aggregate graded        │   │ - Run gated review on     │
 │   exits, artifacts,       │   │   groundedness, and       │   │   signals into incident   │   │   proposed changes        │
 │   and HITL packets        │   │   citation support        │   │   patterns and severity   │   │ - Approve or reject       │
 │ - Normalize evidence and  │   │ - Grade trajectories:     │   │ - Perform RCA and drift   │   │   promotion candidates    │
 │   preserve lineage /      │   │   tool order, retries,    │   │   investigation           │   │ - Route approved updates  │
 │   replay linkage          │   │   budget, execution shape │   │ - Draft prompt / policy / │   │   through UWG to L4       │
 │ - Observer posture only:  │   │ - Detect regressions in   │   │   rubric / config changes │   │ - Publish committed       │
 │   evidence reads only,    │   │   exact match, schema,    │   │   as proposals only       │   │   next-run updates onto   │
 │   no live mutation        │   │   API, and guardrails     │   │ - No promotion yet, only  │   │   rollout surfaces        │
 │                           │   │ - Human calibration tunes  │   │   candidate update sets   │   │ - No current-run mutation │
 │                           │   │   grading, not runtime     │   │                           │   │                           │
 └───────────────────────────┘   └───────────────────────────┘   └───────────────────────────┘   └─────────────┬─────────────┘
                                                                                                               │
                                                                                                               ▼
         [ FUTURE RUNTIME SURFACES UPDATED: BUS U pushes Prompts, Policies, Baselines, Rubrics, and Approved Reason Priors ]
         [ INVARIANT: learning signals inform next-run behavior only. They do not mutate or rescue the completed run. ]

==============================================================================================================================
[4.1] L2 MODULE BREAKOUT — EXECUTION COMPONENT MAP
==============================================================================================================================
Canonical mapping of L2 execution modules to process map phases E1-E5.
Generated: 2026-04-03 | ADG Source: adg_indexed_04032026_1923.sqlite

----------------------------------------------------------------------------------------------------------------------------
[4.1.1] Phase E1 — PRE-COMMIT / PREP DESK (L2.1 INIT)
----------------------------------------------------------------------------------------------------------------------------
MODULE                                           │ FUNCTION                        │ CONTRACT METHOD
─────────────────────────────────────────────────┼─────────────────────────────────┼─────────────────────────────
L2ExecutionAgent (base)                          │ Phase orchestration             │ run_l2_phases()
L2EmbeddingSovereignAgent                        │ Embedding context setup         │ l2_init()
L2RedisSovereignAgent                            │ Redis connection init           │ l2_init()
L2SovereignMCPGatewayAgent                      │ MCP tool binding                │ l2_init()
L2StructuredEngineAgent                          │ Intent validation               │ l2_init()
L2SubAtomicRegistryAgent                         │ Registry lookup                 │ l2_init()
ToolIntentExecutor                               │ Sandbox validation              │ l2_init()

Responsibilities:
- Environment/capabilities/budget locking
- Idempotency key binding  
- Blueprint hash binding for healing replay
- Sandbox state validation (for mutating ops)

----------------------------------------------------------------------------------------------------------------------------
[4.1.2] Phase E2 — VALIDATE / WORK ORDER CHECK (L2.1 INIT cont.)
----------------------------------------------------------------------------------------------------------------------------
MODULE                                           │ FUNCTION                        │ CONTRACT METHOD
─────────────────────────────────────────────────┼─────────────────────────────────┼─────────────────────────────
ToolIntentExecutor                               │ Intent + sandbox validation     │ l2_init() → validation
SovereignLLMGateway                              │ Capability token validation     │ authorize_and_execute()
UniversalWriteGateway                            │ Write permission check          │ MutationRecord validation

Validation Gates:
- Integrity & Signature Chain
- Cap Scope & Env Budget
- Schema & Side-Effect Class
- Mutation Type Sanity

FAIL here = Request rejected before any work starts (sealed rejection)

----------------------------------------------------------------------------------------------------------------------------
[4.1.3] Phase E3 — EXECUTE / DOING THE WORK (L2.2 EXECUTE)
----------------------------------------------------------------------------------------------------------------------------
MODULE                                           │ FUNCTION                        │ CONTRACT METHOD
─────────────────────────────────────────────────┼─────────────────────────────────┼─────────────────────────────
L2EmbeddingSovereignAgent                        │ Generate embeddings             │ l2_execute()
L2RedisSovereignAgent                            │ Cache operations                │ l2_execute()
L2SovereignMCPGatewayAgent                       │ MCP tool invocation             │ l2_execute()
L2StructuredEngineAgent                          │ Process structured intents      │ l2_execute()
L2SubAtomicRegistryAgent                         │ Registry operations             │ l2_execute()
ToolIntentExecutor                               │ Tool invocation with sandbox    │ l2_execute()
EmbeddingSovereignAgent (legacy)                 │ Async embedding generation      │ get_embedding()
RedisSovereignAgent (legacy)                     │ Redis get/set/delete            │ cache operations

Execution Model:
- Bounded invocation with timeout/circuit breaker
- Isolated execution (sandbox for mutating ops)
- Execution telemetry emission
- Result classification: SUCCESS | SOFT_REPAIRABLE | FAIL_TERMINAL

----------------------------------------------------------------------------------------------------------------------------
[4.1.4] Phase E4 — HEAL LOOP / FIXING MISTAKES (L2.3 EVALUATE_HEAL)
----------------------------------------------------------------------------------------------------------------------------
MODULE                                           │ FUNCTION                        │ CONTRACT METHOD
─────────────────────────────────────────────────┼─────────────────────────────────┼─────────────────────────────
L2ExecutionAgent (base)                          │ Phase result evaluation         │ should_attempt_heal()
L2EmbeddingSovereignAgent                        │ Provider fallback (bge→gemini)  │ l2_evaluate_and_heal()
L2RedisSovereignAgent                            │ Retry with reconnection         │ l2_evaluate_and_heal()
L2SovereignMCPGatewayAgent                       │ Tool retry / fallback           │ l2_evaluate_and_heal()
L2StructuredEngineAgent                          │ Intent reprocessing             │ l2_evaluate_and_heal()
L2SubAtomicRegistryAgent                         │ Registry retry                  │ l2_evaluate_and_heal()
ToolIntentExecutor                               │ Retry with recovery             │ l2_evaluate_and_heal()
healing_tier_router.py                           │ Tier-based routing              │ route_by_confidence()
healing_tier_dispatcher.py                       │ Healing dispatch                │ dispatch_healing()

Healing Tiers:
- LOCAL_AGENT: In-agent retry (handled by l2_evaluate_and_heal)
- COORDINATED: Multi-agent healing (via healing_tier_router)
- ESCALATED: Human-in-the-loop or abort

----------------------------------------------------------------------------------------------------------------------------
[4.1.5] Phase E5 — SEAL OUTPUT / FINAL FOLDER (L2.4 SYNTHESIZE)
----------------------------------------------------------------------------------------------------------------------------
MODULE                                           │ FUNCTION                        │ CONTRACT METHOD
─────────────────────────────────────────────────┼─────────────────────────────────┼─────────────────────────────
L2EmbeddingSovereignAgent                        │ Embedding result packaging      │ l2_synthesize()
L2RedisSovereignAgent                            │ Operation result packaging      │ l2_synthesize()
L2SovereignMCPGatewayAgent                      │ Tool result packaging           │ l2_synthesize()
L2StructuredEngineAgent                          │ Intent result packaging         │ l2_synthesize()
L2SubAtomicRegistryAgent                         │ Registry result packaging       │ l2_synthesize()
ToolIntentExecutor                               │ ToolResult creation             │ l2_synthesize()

Sealing Requirements:
- Final answer / artifact attachment
- Traces / ancestry / lineage
- Replay keys / validation counters
- Terminal class: SUCCESS | FAILURE | NEEDS_HELP | REJECTED
- NO durable commit (L2 only emits sealed artifacts)

----------------------------------------------------------------------------------------------------------------------------
[4.1.6] L2 Execution Contract Compliance Matrix
----------------------------------------------------------------------------------------------------------------------------
AGENT/WRAPPER                    │ l2_init │ l2_execute │ l2_evaluate_and_heal │ l2_synthesize │ STATUS
───────────────────────────────────┼─────────┼────────────┼──────────────────────┼───────────────┼──────────
L2EmbeddingSovereignAgent        │    ✓    │     ✓      │          ✓           │       ✓       │ COMPLIANT
L2RedisSovereignAgent            │    ✓    │     ✓      │          ✓           │       ✓       │ COMPLIANT
L2SovereignMCPGatewayAgent        │    ✓    │     ✓      │          ✓           │       ✓       │ COMPLIANT
L2StructuredEngineAgent           │    ✓    │     ✓      │          ✓           │       ✓       │ COMPLIANT
L2SubAtomicRegistryAgent          │    ✓    │     ✓      │          ✓           │       ✓       │ COMPLIANT
ToolIntentExecutor                │    ✓    │     ✓      │          ✓           │       ✓       │ COMPLIANT
EmbeddingSovereignAgent (legacy)   │    ✗    │     ✗      │          ✗           │       ✗       │ LEGACY
RedisSovereignAgent (legacy)       │    ✗    │     ✗      │          ✗           │       ✗       │ LEGACY
SovereignMCPGateway (legacy)       │    ✗    │     ✗      │          ✗           │       ✗       │ LEGACY
StructuredEngineAgent (legacy)    │    ✗    │     ✗      │          ✗           │       ✗       │ LEGACY
SubAtomicRegistryAgent (legacy)    │    ✗    │     ✗      │          ✗           │       ✗       │ LEGACY
ToolsmithAgent (deprecated)        │    N/A  │    N/A     │         N/A          │      N/A      │ DEPRECATED

Migration Path: Legacy agents → L2 Wrappers → Full L2ExecutionAgent inheritance

==============================================================================================================================
[ LEGEND ] LAYER DEFINITIONS (L0 - L6)
==============================================================================================================================
 LAYER │ PERSONA                  │ CORE FUNCTION / MEANING                                                                   
───────┼──────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────
 L0    │ Dispatcher               │ Route authority; determines execution path (cache, RAG, action, fallback).                
 L1    │ Librarian                │ Reasoning loop; formulates execution plans and dispatches to routing.                     
 L2    │ Assistant                │ Tool and action execution; interfaces with external systems to produce output.            
 L3    │ Manager                  │ Optional multi-step orchestration; manages complex L2 execution chains.                   
 L4    │ Archivist                │ Authoritative state; durable writes via UNIVERSAL WRITE GATE only. Broad read, strict write authority.     
 L5    │ Safety Officer           │ Cross-cutting policy plane; enforces guardrails across all runtime/exit points.           
 L6    │ Observer                 │ Shadow evaluation; monitors telemetry for future-run system learning and RCA.             
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────