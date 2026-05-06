========================================================================================================================
                                      AGENTIC SYSTEM PROCESS MAP - EXECUTIVE SUMMARY
========================================================================================================================
 [!] SIMPLEST VIABLE PATTERN: deterministic workflow first -> single agent -> multi-agent only
 [i] AGENT CORE = model + tools + instructions + guardrails + evals
 [!] CHEAT RULE: L2 proposes -> Exit clears -> UWG commits -> L4 stores
 [!] CONTROL SPLIT: Runtime Gates decide live proceed/stop | Exit emits one X3 | L5 certifies authority
 [!]                | L7 taps every stage (cross-cutting, parallel) and seals bundle post-run (non-blocking)

 ----------------------------------------------------------------------------------------------------------------------
 MODEL ARCHITECTURE & SIGNAL LEGEND
 
 [ENCODER] Models (Embedding, Semantic Search, Classification)
   ► Produces 🔵 intent vector (live ask / step-specific search query)
   ► Produces 🟠 fact vector   (stored source / chunk embedded at index time)
   ► Produces 🟢 graph_sig     (lineage / dependency / ACL / citation relationships)

 [DECODER] Models (Generative Planning, Reasoning, Tool-Calling, Evaluation)
   ► Produces 🔶 gen_text      (natural language, plans, judgments, tool proposals)

 [00D] EVAL PRIMITIVES (LLM-as-Judge, Deterministic Validators, Schema Checkers)
   ► Emits scorecard / critique / judge evidence
   ► Primary placement: 05 Exit | Light use: 00C, L2 | Post-run: 06 L6
   ► Does NOT route, execute, approve by itself, or write to L4

 [00E] AUDIT PRIMITIVES (OTEL spans, evidence assertions, hash-chain, signer)
   ► Produces 🟣 audit_trace (spans → merkle root → signature)
   ► Tap: every stage, parallel | Seal: stage 07 L7, post-run
   ► Does NOT route, judge, approve, write L4, or gate runtime
 ----------------------------------------------------------------------------------------------------------------------
========================================================================================================================

[ L5 POLICY PLANE ] ────────────────────────────────────────────────────────────────────────────────────────────────────
 │ Certifies: authority | policy | registry | origin trust | capability | sandbox | egress | HITL | replay/audit
 │ Does NOT: route | retrieve | execute | emit final runtime disposition | write L4
 ▼

[ L7 AUDITABILITY PLANE ] ◄── CROSS-CUTTING (taps every stage in parallel; seal is stage 07) ─────────────────────
 │ Tap (live):  spans at U0 | L1 | L0 | C0 | PA | L2 | Exit | UWG | L4-commit | L6   — parallel, non-blocking
 │ Seal (post): tap stream → evidence_assertions.jsonl → *.json + *.sha256 + *.merkle.json + *.signature.json
 │ Trust:       DEVELOPMENT_PROOF → INTEGRITY_PROOF → SIGNED_OFF | compiler is sole status authority | canary required
 │ Does NOT:    route | retrieve | execute | judge | approve | write L4 | gate runtime | emit X3 | rescue run
 ▼

[ 00C RUNTIME GATES ] ──────────────────────────────────────────────────────────────────────────────────────────────────
 │ Emits GateVerdict. UNKNOWN is never PASS. Does not emit final X3 or write L4.
 │ • May invoke 00D judge for live gate evidence, but gates emit GateVerdict, not final X3
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
│                                                                                                                      │
│ • Optional local critique (00D) before E5 Seal, same-authority only, no approval power                               │
└───────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │ [sealed artifacts / proposed_state_diff if any]
        ▼
┌───────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. EXIT EVAL & CONTROL                                                          [DECODER] 🔶 gen_text (Output Grade) │
│                                                                         [ENCODER] 🔵 intent vector vs 🟠 fact vector │
│ ★ LLM-AS-JUDGE PRIMARY LIVE USE (00D)                                             (Semantic Safety Checks)           │
│   • Scores candidate against rubric, evidence, schema, safety, false-confidence, citation integrity                  │
│   • Emits judge scorecard as X1 evidence; X3 owns final disposition                                                  │
│   • Does not retrieve, execute, route, approve by itself, or write L4                                                │
│                                                                                                                      │
│ - Final policy & safety review                                                                                       │
│ - X1 checks sealed result (incorporates Judge Scorecard)                                                             │
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
│ - May reuse judge (00D) for post-run grading, RCA, calibration, and future-run proposals only                        │
│ - RCA / drift / calibration                                                                                          │
│ - Future-run proposals                                                                                               │
│ - Sends promotion request to UWG                                                                                     │
│ - No current-run rescue                                                                                              │
│ - No direct L4 write                                                                                                 │
└───────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │ [span tree + RCA + X3 + UWG commit log]
        ▼
┌───────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 7. L7 SEAL (compile bundle)                                                              [00E] 🟣 audit_trace          │
│                                                                                                                      │
│ - Closes tap stream (live since U0); compiles → hashes → signs                                                       │
│ - Inputs:  tap stream + L6 RCA + Exit X3 + UWG commit log                                                            │
│ - Outputs: evidence_assertions.jsonl → *.json + *.sha256 + *.merkle.json + *.signature.json                          │
│ - ★ Hostile verifier: compiler is sole status authority; prose "certified" claims invalid without bundle             │
│ - ★ Mutation-rejection canary required per bundle                                                                    │
│ - Trust ladder: DEVELOPMENT_PROOF → INTEGRITY_PROOF → SIGNED_OFF                                                      │
│ - No rescue / No L4 write / No reroute · Failure → bundle DEGRADED, runtime already done                              │
│ - L7 ≠ L5 (authority to act, pre/intra-run) · L7 ≠ L6 (learns from exhaust, proposes future runs)                    │
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
- L7: prior bundles for diff/regression, signer key registry, mutation canary registry

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
- L7: signer identity / bundle-schema authority / trust-level transitions

L7 AUDIT TAP POINTS:
- U0:   request envelope hash, origin label
- L1:   plan contract hash, intent vector fingerprint
- L0:   RouteContract id, gate verdicts
- C0:   evidence contract hash, ACL decisions, citation set
- PA:   compiled prompt artifact hash, slot ordering
- L2:   tool-call args/results, heal attempts, proposed_state_diff
- Exit: judge scorecard, X1/X2/X3 verdicts, HITL escalations
- UWG:  commit-request → commit-result with policy-replay-audit match
- L6:   RCA, drift signals, promotion requests
========================================================================================================================