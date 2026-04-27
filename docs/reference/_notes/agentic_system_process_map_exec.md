========================================================================================================================
                                      AGENTIC SYSTEM PROCESS MAP - EXECUTIVE SUMMARY
========================================================================================================================
 [!] SIMPLEST VIABLE PATTERN: deterministic workflow first -> single agent -> multi-agent only
 [i] AGENT CORE = model + tools + instructions + guardrails + evals
 [!] CHEAT RULE: L2 proposes -> Exit clears -> UWG commits -> L4 stores
 [!] CONTROL SPLIT: Runtime Gates decide live proceed/stop | Exit emits one X3 | L5 certifies evidence

 ----------------------------------------------------------------------------------------------------------------------
 MODEL ARCHITECTURE & SIGNAL LEGEND
 
 [ENCODER] Models (Embedding, Semantic Search, Classification)
   ► Produces 🔵 intent vector (live ask / step-specific search query)
   ► Produces 🟠 fact vector   (stored source / chunk embedded at index time)
   ► Produces 🟢 graph_sig     (lineage / dependency / ACL / citation relationships)

 [DECODER] Models (Generative Planning, Reasoning, Tool-Calling, Evaluation)
   ► Produces 🔶 gen_text      (natural language, plans, judgments, tool proposals)
 ----------------------------------------------------------------------------------------------------------------------
========================================================================================================================

[ L5 POLICY PLANE ] ────────────────────────────────────────────────────────────────────────────────────────────────────
 │ Certifies: authority | policy | registry | origin trust | capability | sandbox | egress | HITL | replay/audit
 │ Does NOT: route | retrieve | execute | emit final runtime disposition | write L4
 ▼

[ 00C RUNTIME GATES ] ──────────────────────────────────────────────────────────────────────────────────────────────────
 │ Emits GateVerdict. UNKNOWN is never PASS. Does not emit final X3 or write L4.
 ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. INTAKE CHECK                                                                     [ENCODER] Auth / Schema Classify │
│ U0 only ◄── (Auth, Quota, Malformed schema check. NO semantic routing)                                               │
└──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────┘
                                               │ [Validated Request]
                                               ▼
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██ ◄─────────────────────────────────────────────── R U N T I M E   B E G I N S ─────────────────────────────────────► ██
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
                                               │
┌──────────────────────────────────────────────┴──────────────────────────────────────────────┐        ┌───────────────┐
│ 2. L1 INTERPRET                                                  [ENCODER] 🔵 intent vector │───────►│ L4 ARCHIVE    │
│ • Parse Intent                                                       [DECODER] 🔶 gen_text  │        │ (Archivist)   │
│ • Draft Plan                                                                                │        │ Read-only     │
│ • Validate                                                                                  │◄───────│ planning      │
│ • Route hints                                                                               │        │ priors        │
└───────┬─────────────────────────────────────────────────────────────────────────────────────┘        └───────────────┘
        │ [plan contract]                                              
        ▼                                                              
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. L0 ROUTING (Dispatcher)                                                             [DECODER] 🔶 gen_text (Route) │
│ Outputs exactly one RouteContract                                                                                    │
│ ★ Gate: route/risk/HITL posture                                                                                      │
│                                                                                                                      │
│ • R1 Cache ──────────[RET]──┐                                                                                        │
│ • R5 Fallback ───────[RET]──┤                                                                                        │
│ • R2 Grounded Read (Single) │                                                                                        │
│ • R3/R4 Action/Workflow     │                                                                                        │
└───────┬─────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┘
        │ [route contract]    │ [R2 Retrieve]
        │                     ▼
        │             ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
        │             │ C0 CONTEXT ENGINEERING / GROUNDING                          [ENCODER] 🔵 intent vector MATCHES │
        │             │ ★ Gate: ACL/evidence                                                  🟠 fact vector           │
        │             │ • Retrieve/Grnd 🟠                                          [ENCODER] 🟢 graph_sig             │
        │             │ • Evidence only                                                                                │
        │             │ • Never answers                                                                                │
        │             └───────────┬────────────────────────────────────────────────────────────────────────────────────┘
        │                         │ [evidence contract] 🟠 fact vector
        │                         ▼
        │             ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
        │             │ PROMPT ASSEMBLY (Sys•Ctx•Task)                                           [DECODER] 🔶 gen_text │
        │             │ ◄─── [state load]                                                                              │
        │             │ ★ Gate: prompt boundary                                                                        │
        │             │ • Compose only                                                                                 │
        │             │ • No retrieve/execute                                                                          │
        │             └───────────┬────────────────────────────────────────────────────────────────────────────────────┘
        │                         │ [dispatch / compiled prompt artifact]
        ├◄────────────────────────┘
        ▼
┌───────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L3 ORCHESTRATE (Manager)                                                                [DECODER] 🔶 gen_text (Seq.) │
│ • Step expansion/sequencing                                                                                          │
│ • Multi-step dependency math                                                                                         │
│ • Plan evolution (bounded)          [!] R1/R5 skip L3/L2 and go                                                      │
│ • No route re-decision                  straight to Exit Desk                                                        │
│ • No execution / L4 write                                                                                            │
└───────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. L2 EXECUTE (Assistant) ◄── (handles current single step execution)              [DECODER] 🔶 gen_text (Tool Call) │
│                                                                                                                      │
│ * BOUNDED AUTONOMY: tool feedback each step | exit conditions | max turns                                            │
│ * MUTATION LAW: may emit proposed_state_diff only; cannot write L4                                                   │
│ * ★ Gate: tool/model args | sandbox | side effects | retry/heal budget                                               │
│                                                                                                                      │
│  ┌────────┐   ┌─────────┐   ┌─────────┐   ┌────────┐   ┌────────┐                                                    │
│  │E1: Prep│──►│E2: Valid│──►│E3: Exec │──►│E4: Heal│──►│E5: Seal│                                                    │
│  └────────┘   └─────────┘   └─▲───────┘   └─┬──────┘   └────────┘                                                    │
│                               │ [retry]     │                                                                        │
│                               └─────────────┘                                                                        │
│                                                                                                                      │
│  E4 HEAL SPLIT:                                                                                                      │
│  - Heal repository = approved repair menu for this agent/tool/route                                                  │
│  - Heal function = live same-authority repair governor for this failure                                              │
│  - Cannot heal missing authority, blocked ACL, policy conflict, route mismatch, stale policy, or HITL need           │
└───────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │ [sealed artifacts / proposed_state_diff if any]
        ▼
┌───────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. EXIT EVAL & CONTROL                                                          [DECODER] 🔶 gen_text (Output Grade) │
│                                                                         [ENCODER] 🔵 intent vector vs 🟠 fact vector │
│ - Final policy & safety review                                                    (Semantic Safety Checks)           │
│ - X1 checks sealed result                                                                                            │
│ - X2 aggregates verdicts                                                                                             │
│ - X3 emits exactly one outcome                                                                                       │
│ - ★ Gate: output/replay/write                                                                                        │
│ ◄── [ Receiving [RET] Short-Circuits & Artifacts ]                                                                   │
│                                                                                                                      │
│ X3 outcomes:                             [commit request only]                                                       │
│ • DENY / REROUTE ──────────────┐         (Atomic commit)                                                             │
│ • ESCALATE_HITL ───────────┐   │              │                                                                      │
│ • COMMIT_REQUEST_TO_UWG ───┼───┼──────────────┼────► ┌─────────────────────────────────────────────────────────────┐ │
│ • ALLOW / FINISH           │   │              │      │ UNIVERSAL WRITE GATE (UWG)                                  │ │
│ • SAFE_ABSTAIN             │   │              │      │ ★ Gate: no bypass                                           │ │
└────────────────────────────┼───┼──────────────┼────► └──────┬──────────────────────────────────────────────────────┘ │
                             │   │              │             │                                                        │
   ┌───────────────────────┐ │   │              │             ▼                                                        │
   │ HUMAN REVIEW          │◄┘   │              │      ┌─────────────────────────────────────────────────────────────┐ │
   │ HIGH-RISK ACTIONS:    │     │              │      │ L4 ARCHIVE (Writes)                                         │ │
   │ pause for guardrails/ │     └► [ Reroute ] │      │ durable truth                                               │ │
   │ human approval before │                    │      └─────────────────────────────────────────────────────────────┘ │
   │ irreversible writes   │                    │                                                                      │
   └───────────────────────┘                    │                                                                      │
        ┌───────────────────────────────────────┘                                                                      │
        │                                                                                                              │
        ▼                                                                                                              │
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██ ◄─────────────────────────────────────────────── R U N T I M E   E N D S ─────────────────────────────────────────► ██
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
        │                                                                                                              │
        │ [runtime exhaust after current-run boundary]                                                                 │
        ▼                                                                                                              │
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 6. L6 SHADOW LEARNING                                                                    [DECODER] 🔶 gen_text (RCA) │
│                                                                                  [ENCODER] 🟢 graph_sig (Clustering) │
│ - Completed-run eval only                                                                                            │
│ - RCA / drift / calibration                                                                                          │
│ - Future-run proposals                                                                                               │
│ - Sends promotion request to UWG                                                                                     │
│ - No current-run rescue                                                                                              │
│ - No direct L4 write                                                                                                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

========================================================================================================================
LEAN HOTSPOTS
========================================================================================================================

L4 READ HOTSPOTS:
- L1: planning priors / approved examples
- L0: cache, route policy, blueprint, registry
- C0: retrieval surfaces, indexes, graph projections, citations, ACL, freshness
- PA: prompt BOM, schema, allowed examples
- L2: tool/model/connector/sandbox registry snapshots
- Exit: policy thresholds, grader profiles, proposed mutation metadata
- L6: completed-run exhaust, eval records, traces

L5 CERT HOTSPOTS:
- U0: origin labels / boundary triage
- L1: user intent vs authority separation
- L0: route authority / side-effect posture
- C0: source authority / ACL / retrieved text as data only
- PA: slot authority ordering / instruction-data airlock
- L2: capability token / sandbox envelope / same-authority heal
- Exit: safe-to-leave / HITL / egress / replay / audit
- UWG: policy-replay-audit match before commit
- L6: governance regression after runtime only
========================================================================================================================