[ L1_PLAN_CONTRACT ]
                                                     │
                                                     ▼
========================================================================================================================================
[3] ROUTE DECISION + SWITCHING
========================================================================================================================================

- The dispatcher takes the approved L1 plan and decides whether the request should short-circuit
  through exact reuse, bounded semantic reuse, grounded context assembly, external action
  dispatch, or safe fallback.
- L0 decides the path, but it does not itself do retrieval, think deeply, or perform the work.
- L0 emits a deterministic route contract: selected route, confidence, reason codes, freshness class,
  cache policy, and execution form.
- L3 is OPTIONAL and is invoked only when the selected route must be expanded into managed steps.


[ PEDAGOGICAL LEGEND ]  🔵 Blue asks = query_vec / intent vector
                        🟠 Orange knows = raw_text_vector / contextual_text_vector
                        🟢 Green maps = knowledge_graph / entity_subgraph
                        [RET] = Terminal early exit; completely bypasses L3 to hit Exit Control

 ┌──────────────────────────────────────────────┐                               ┌────────────────────────────────────┐
 │ L0 ROUTING (Dispatcher)                      │                               │ L4 STATE / ARCHIVE                 │
 │ - Ingress: L1Plan + 🔵 query_vec             │                               │ - Universal Persistence Boundary   │
 │ - Pre-filter: tenant / ACL / region bounds   │                               │ - Cache Stores (Exact/Sem.)        │
 │ - Enforce expiry / freshness requirements    │                               │ - Canonical raw chunks 🟠          │
 │ - Fast Fail: Reject invalid scope early      │                               │ - Dense vector / sparse index 🟠   │
 │ - Score: cacheable / grounded / action /     │                               │ - Knowledge graph & entities 🟢    │
 │   multi-hop / freshness / support needs      │                               │ - Canonical source lineage         │
 │ - Emit route contract, not the work itself   │                               │ - Version manifests / schema       │
 └──────────────────────┬───────────────────────┘                               │ - No direct write path exists      │
                        │                                                       └──────────────────┬─────────────────┘
                        ▼                                                                          │
 ┌──────────────────────────────────────────────┐                                                  │
 │ L0 ROUTE DECISION SWITCH                     │                                                  │
 │ The dispatcher selects ONE terminal or       │                                                  │
 │ orchestrated path based on the contract.     │                                                  │
 └─┬────────────────────────────────────────────┘                                                  │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R1A EXACT CACHE                        │◄──────────────────────────────────────────────────┤
   │  │ - Perfect keyed reuse, zero infer.     │                                                   │
   │  │ - Bypass deep pipeline entirely        ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Exact prior answer (NO C0 NEEDED)    │                                                   │
   │  │ - NO L3 NEEDED                         │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R1B SEMANTIC CACHE                     │◄──────────────────────────────────────────────────┤
   │  │ - Policy-approved sim, bounded reuse   │                                                   │
   │  │ - Matches 🔵 ask vs 🔵 cached ask      │                                                   │
   │  │ - Reuse-safe tasks, no deep reading    ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Short-circuit exec (NO C0 NEEDED)    │                                                   │
   │  │ - Terminal short-circuit route         │                                                   │
   │  │ - NO L3 NEEDED                         │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R5 FALLBACK                            │                                                   │
   │  │ - Safest bound outcome                 │                                                   │
   │  │ - Abstain/clarify                      ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Ungrounded default                   │                                                   │
   │  │ - Terminal safe route                  │                                                   │
   │  │ - NO C0 NEEDED, NO L3 NEEDED           │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R3 SIMPLE GROUNDED READ                │                                                   │
   │  │ - Factual/policy claims require backing│                                                   │
   │  │ - Evidence class & support target      │                                                   │
   │  │ - Strictly grounded answer only        │                                                   │
   │  │ - Single-pass grounding, bypasses L3   │                                                   │
   │  │ - Still requires one bounded L2 step   │                                                   │
   │  └───────────────────┬────────────────────┘                                                   │
   │                      ▼                                                                        │
   │  ┌────────────────────────────────────────┐                                                   │
   │  │ C0 CONTEXT ENGINE (Ref Desk)           │◄──────────────[ Read ]────────────────────────────┤
   │  │ - C0.1 Plan: scope, freshness, ACL     │                                                   │
   │  │ - C0.2 Fetch: 🔵 query vs 🟠 ctx_vec   │                                                   │
   │  │ - C0.3 Graph: traverse entities 🟢     │                                                   │
   │  │ - C0.4 Shape: dedupe, rerank, prune    │                                                   │
   │  │ - C0.5 Contract: verify spans, score   │                                                   │
   │  │ - C0.6 If weak: rewrite / broaden /    │                                                   │
   │  │   decompose within route budget        │                                                   │
   │  └───────────────────┬────────────────────┘                                                   │
   │                      │ [Evidence Contract]                                                    │
   │                      ▼                                                                        │
   │  ┌────────────────────────────────────────┐                                                   │
   │  │ PROMPT ASSEMBLY                        │◄──────────────[ Load ]────────────────────────────┘
   │  │ - PA.1 Load: system template, schema   │
   │  │ - PA.2 Slot: context 🟠, contradict    │
   │  │ - PA.3 Budget: trim/reserve tokens     │
   │  │ - PA.4 Emit: PromptEnvelope, HMAC      │
   │  │ - Packages grounded packet only        │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │       [ L2 Execute Single Grounded Step ]──────► [RET] ──► To 5. EXIT EVAL & CONTROL
   │
   │  ┌────────────────────────────────────────┐
   ├──► R4 SINGLE ACTION                       │
   │  │ - Dispatch external action payload     │
   │  │ - Mutate state, bounded autonomy       │
   │  │ - Single bounded action direct to L2   │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │             [ L2 Execute Single Step ]─────────► [RET] ──► To 5. EXIT EVAL & CONTROL
   │
   │  ┌────────────────────────────────────────┐
   └──► R3/R4 MANAGED WORKFLOW                 │
      │ - Multi-hop RAG or workflow action     │
      │ - Dependency order / branching / joins │
      │ - Needs resumable workflow state       │
      │ - L3 Orchestration required            │
      └───────────────────┬────────────────────┘
                          │
                          ▼
       ┌──────────────────────────────────────────────────────────────────────┐
       │ L3 ORCHESTRATION CONTROL PLANE (The Managing Librarian)              │
       │ - Ingress: approved route package from L0 + action contracts         │
       │                                                                      │
       │   ┌──────────────────────────┐      ┌───────────────────────────┐    │
       │   │ L3.1 DAG / AST RUNNER    │◄────►│ L3.2 STATE LEDGER         │    │
       │   │ - Graph dependency math  │      │ - Durable checkpoints     │    │
       │   │ - Forward-only eval      │      │ - Resumable handoffs      │    │
       │   │ - Issues 🔵 step asks    │      │ - Step status tracking    │    │
       │   └──────────┬───────────────┘      └───────────────────────────┘    │
       │              │                                                       │
       │   ┌──────────▼───────────────┐      ┌───────────────────────────┐    │
       │   │ L3.3 CONTEXT BUS         │◄────►│ L3.4 POLICY ENGINE        │    │
       │   │ - Passes 🟠 references   │      │ - Route bounds check      │    │
       │   │ - Coordinates 🟢 maps    │      │ - Prevents memory bloat    │    │
       │   │ - Central staging area   │      │ - Guardrail validation    │    │
       │   └──────────┬───────────────┘      └───────────────────────────┘    │
       └──────────────┼───────────────────────────────────────────────────────┘
                      │
                      ▼
           ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
           │ A. EXECUTION SHAPE CLASSIFICATION                                                                          │
           │ - Decide whether the route expands to one bounded step or to a managed multi-step workflow                │
           │ - Confirm whether there is any real need for dependency tracking, branching, joins, or resumable state   │
           │ - Test whether more than one 🔵 ask, more than one 🟠 evidence packet, or more than one 🟢 graph step is  │
           │   required across the route                                                                                │
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘
                             [ one bounded step ] ▼                                                       [ managed workflow ] ▼
           ┌────────────────────────────────────────┐                      ┌────────────────────────────────────────────┐
           │ A1. DIRECT STEP PACKAGE               │                      │ A2. MULTI-STEP WORKFLOW / DAG              │
           │ - Emit one step contract for L2       │                      │ - Build nodes, edges, branch rules         │
           │ - Encode dependency order and join rules   │
           │ - May contain one 🔵 ask or one action│                      │ - Mark parallel-safe vs serial-only paths  │
           │ - Send immediately to execution       │                      │ - Assign where 🔵 asks, 🟠 evidence, and   │
           └──────────────────────┬─────────────────┘                      │   🟢 graph steps enter the DAG             │
                                  │                                        └──────────────────────┬─────────────────────┘
                                  │                                                               │
                                  └───────────────────────────────────────┬───────────────────────┘
                                                                          │
                                                                          ▼
           ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
           │ B. STEP GRAPH / READINESS CONTROL                                                                           │◄─────┐
           │ - Pick only nodes whose dependencies are satisfied                                                          │      │
           │ - Respect policy, budget, timeout, concurrency, and checkpoint constraints                                  │      │
           │ - Hold blocked nodes until prerequisites, required 🟠 support, and route conditions are satisfied           │      │
           │ - Preserve forward-only L3 flow: no backward edges in the orchestration graph for the current run          │      │
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘      │
                                          ▼                                                                                      │
           ┌────────────────────────────────────────────────────────────┐                                                        │
           │ STEP CONTRACT TO L2                                        │                                                        │
           │ - Current node only, bounded autonomy                      │                                                        │
           │ - Tool / model / action spec                               │                                                        │
           │ - Inputs may include 🔵 query intent,                      │                                                        │
           │   🟠 grounded evidence, 🟢 graph payload                   │                                                        │
           │ - Expected artifact / support target                       │                                                        │
           └──────────────────────┬─────────────────────────────────────┘                                                        │
                                  │                                                                                              │
                                  ▼                                                                                              │
                       [ Dispatch to [4] L2_EXECUTE ]                                                                            │
                                  │                                                                                              │
                                  ▼                                                                                              │
           ┌────────────────────────────────────────────────────────────┐                                                        │
           │ STEP RESULT RETURN                                         │                                                        │
           │ - Status, outputs, artifacts, errors                       │                                                        │
           │ - May return new 🟠 evidence, updated 🟢 graph state, or   │                                                        │
           │   next 🔵 ask candidates                                   │                                                        │
           │ - Retry signal / branch result / handoff                   │                                                        │
           └──────────────────────┬─────────────────────────────────────┘                                                        │
                                  ▼                                                                                              │
           ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐      │
           │ C. GRAPH STATE UPDATE / HANDOFF MERGE                                                                      │      │
           │ - Mark node done / failed / retry                                                                           │      │
           │ - Unlock dependents or trigger allowed repair / reroute path                                               │      │
           │ - Rejoin branches and merge returned 🟠 support and 🟢 graph outcomes into next-step readiness             │      │
           │ - Carry forward next eligible 🔵 asks without turning L3 into an open loop                                 │      │
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘      │
                                          ▼                                                                                      │
           ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐      │
           │ D. COMPLETION / EXIT PACKAGE                                                                                │      │
           │ - Test whether all required nodes are sealed                                                                 │      │
           │ - Verify all required 🟠 support obligations and route-level success conditions are satisfied                │      │
           │ - Emit one sealed workflow package upward for the control layer, or return to B for the next ready node     ├──────┘ no
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘
                                       yes ▼
                             [ Return sealed work ──► To 5. EXIT EVAL & CONTROL ]