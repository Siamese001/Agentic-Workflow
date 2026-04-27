==============================================================================================================================
                            AGENTIC SYSTEM — PROCESS MAP (CANONICAL SEMANTICS & LOOP)
 PRIMARY RUNTIME PATH: L1 ───> L0 ───> [opt L3] ───> L2 | L0 routing (R3) invokes C0 context assembly
                            L5 = cross-cutting policy | UNIVERSAL WRITE GATE = writes to L4
==============================================================================================================================

[ L5 POLICY PLANE / Safety Officer ] ──(cross-cutting authority over [1], [2], [3], [4], [5], [6], EXIT, UNIVERSAL WRITE GATE)──

----------------------------------------------------------------------------------------------------------------------
 MODEL ARCHITECTURE & SIGNAL LEGEND

 🧠 ENCODER FAMILY = search / classify / compare / embed / rank
   🔵 intent_vec   = live ask / route query / step-specific search query
   🟠 fact_vec     = stored source chunk / indexed fact / retrieval target
   🟢 graph_sig    = lineage / dependency / ACL / citation / trace relationship

 ✍️ DECODER FAMILY = reason / plan / generate / call tools / judge output
   🔶 gen_text     = natural language, plan, judgment, answer, tool-call proposal
   🧾 judge_text   = evaluation rationale / rubric judgment / critique summary

 🧩 HYBRID STEP = encoder signal feeds decoder work
   🔵/🟠/🟢 -> 🔶 = retrieve/classify/compare first, then generate or judge

 🧱 CONTROL / NON-MODEL STEP = contract, gate, policy, state, or write-control logic
   📜 contract     = deterministic packet / schema / signed artifact
   🚦 gate         = runtime proceed/stop verdict
   🔐 cert         = L5 certification evidence
   🗄️ state        = L4 durable read/write surface
   ✒️ commit       = UWG durable write admission only
   🧪 proof        = 99 CI / release / replay / regression acceptance proof
----------------------------------------------------------------------------------------------------------------------

CRITICAL SEMANTIC RULES
----------------------------------------------------------------------------------------------------------------------
- Encoder vs decoder describes the model family, not the authority level.
- Blue vs orange describes runtime role, not model capability.
- The same encoder-family model can create both 🔵 intent_vec and 🟠 fact_vec.
- 🔵 intent_vec means "what this live run is asking for."
- 🟠 fact_vec means "what stored evidence or indexed source says."
- 🟢 graph_sig means "how sources, traces, ACLs, citations, entities, files, and dependencies connect."
- 🔵 matching 🟠 is not proof by itself.
- C0 must still verify ACL, freshness, lineage, sparse/BM25 exactness, metadata, contradiction, and support.
- Decoder output can reason, plan, generate, call tools, or judge, but generated text does not create authority.
- Authority comes from contracts, gates, policy, registry, capability, sandbox, L5 certification, Exit disposition, and UWG write admission.

===========================================================================================================
[1] REQUEST INTAKE + ENVELOPE CHECK                                      🧠 classify + 🧱 contract/gate
===========================================================================================================
- The front door of the system where every request is initially received, checked for basic validity, and verified for access rights before any actual thinking or routing begins.
- The library security guard and front desk greeter who checks your library card, screens the form, normalizes the slip, and stamps a bounded request packet that later staff are allowed to read.
- Intake may use 🧠 encoder-family classification for schema, source, identity, abuse, duplicate, or obvious injection triage.
- Intake is still primarily 🧱 control logic.
- It emits a 📜 ValidatedRequest or rejection packet.
- It does not semantically plan, route, retrieve, answer, execute, or mutate.

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
│  │ 🧠 classify source / auth baseline     │ │ 🧠 classify malformed / duplicate     │ │ 🧱 📜 emit ValidatedRequest           │  │
│  │ 🧱 bind caller / tenant / trace        │ │ 🧱 enforce quota / schema / limits    │ │ 🧱 stamp request_id / trace_root      │  │
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
│ 🧱 📜 contract output only                                                                                                          │
│ - validated_request                                                                                                                │
│ - request_id / session_id / trace_root                                                                                             │
│ - caller_scope_baseline / tenant bind / access baseline                                                                            │
│ - normalized payload                                                                                                               │
│ - origin labels / initial data-boundary labels                                                                                     │
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
[2] L1 REASONING + PLAN GENERATION                                  🧩 classify/priors -> 🔶 plan + 📜 contract
===========================================================================================================
- The senior reference librarian reads the stamped request slip, understands the actual goal, loads governing rules and priors, and writes the bounded plan that later routing may act on.
- L1 may think, decompose, compare options, critique its own draft, and self-correct, but it never retrieves evidence directly, never routes with authority, never executes tools, and never mutates durable state.
- Planner / Doer split: L1 is the planner role. Whether backed by a reasoning-class decoder or a fast model is a per-work-class calibration; L2 is the doer. L1 prompts stay simple and direct for reasoning models.
- Workflow vs agent discipline: Prefer predictable workflows: R1A / R1B / R3 / R4. Reserve multi-hop R3/R4 managed workflow for open-ended problems the plan cannot predetermine. Lowest viable agency always wins.
- 🧠 Encoder nuance: L1 may classify intent, task class, ambiguity, risk, or similarity to approved patterns with 🔵 intent_vec style signals.
- ✍️ Decoder nuance: L1 may draft and refine a 🔶 plan, but the plan is advisory until L0 emits the 📜 RouteContract.
- 🧱 Control nuance: L1 output is a 📜 L1PlanContract, not route authority.

                                                          │ [ goal ]
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ READING THE PATRON'S SLIP                                                                                       │
│ ┌────────────────────────────┐ ┌────────────────────────────┐ ┌──────────────────────────────────────────────┐ │
│ │ I1 GOAL + SUCCESS CONDITION│ │ I2 CONSTRAINTS + RULES     │ │ I3 DETAILS + WORK CLASS                     │ │
│ │ 🧠 classify intent 🔵      │ │ 🧠 classify constraints     │ │ 🧠 classify work class / risk               │ │
│ │ ✍️ summarize goal 🔶       │ │ 🧱 mark hard bounds         │ │ 🧱 mark budget / agency posture             │ │
│ │ - primary objective        │ │ - hard / soft constraints  │ │ - entities, numbers, deliverable, format    │ │
│ │ - requested end-state      │ │ - must / should / avoid    │ │ - summarize / compare / analyze / act       │ │
│ │ - answer / plan / artifact │ │ - scope / exclusions       │ │ - work class drives planner mode + budget   │ │
│ └──────────────┬─────────────┘ └──────────────┬─────────────┘ └──────────────────────┬───────────────────────┘ │
│             [parse]                        [bound]                                 [frame]                      │
│                └─────────────────────────────┴─────────────────────────────────────────┘                         │
│                                                          ▼                                                      │
│         [ clear intent frame = goal + constraints + details + output target + work class + success condition ] │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │ [ triage ]
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PLAN-SKIP TRIAGE                                                                                                │
│ 🧠 compare/classify complexity, cache eligibility, ambiguity, policy sensitivity                                 │
│ 🧱 choose minimal planning posture                                                                               │
│ rule: do not plan what does not need planning. A trivial, unambiguous, cache-eligible ask skips the thinking    │
│ desk and is handed directly to L0 as a DIRECT-mode plan stub. It is still a valid L1PlanContract, just minimal. │
│ escape: any of {ambiguous intent, multi-step decomposition, policy-sensitive, grounding_required}               │
│         → proceed into the full thinking desk below.                                                            │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │ [ context ]
                                                           ▼
┌──────────────────────────────────────────────────────────┴────────────────────────────────┐┌────────────────────┐
│ GATHERING RULES, EXAMPLES, AND PRIORS                                                     ││ L4 ARCHIVE         │
│ 🧩 read approved state first, then plan                                                    ││ 🗄️ read-only state │
│ ┌──────────────────────────┐┌──────────────────────────┐┌───────────────────────────────┐ ││ - Guardrails       │
│ │ M1 TASK SCHEMAS + ROUTES ││ M2 SAFETY / POLICY      ││ M3 EXAMPLES + APPROVED PATTERNS│ ││ - standard ops     │
│ │ 🧱 schema/route contract ││ 🔐 policy/cert refs     ││ 🧠 compare task to patterns    │ ││ - prior examples   │
│ │ - task schemas           ││ - compliance bounds     ││ 🟠 approved examples/facts     │ ││ - approved plans   │
│ │ - output contracts       ││ - escalation thresholds ││ - prior good answers           │ ││ - policy/registry  │
│ │ - route heuristics       ││ - disallowed actions    ││ - SOPs / exemplars             │ ││   read surfaces    │
│ │ - delimiter/XML schema   ││ - HITL thresholds       ││ - stopping rules / priors      │ ││                    │
│ │   for L1→L0 handoff      ││                         ││ - zero-shot first, few-shot if │ ││                    │
│ │                          ││                         ││   examples clearly align       │ ││                    │
│ └────────────┬─────────────┘└────────────┬─────────────┘└───────────────┬───────────────┘ │└────────────────────┘
│           [load]                      [bound]                        [bundle]              │
│              └──────────────────────────┴──────────────────────────────┘                    │
│                                                          ▼                                 │
│                 [ plan bundle = schemas + policy + examples + priors + approved patterns + limits ]            │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │ [ envelope ]
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PROMPT ENVELOPE FOR L1 PLANNING                                                                                 │
│ 🧱 prompt contract controls what the decoder sees                                                                │
│ ✍️ decoder may generate 🔶 plan material inside this boundary                                                     │
│ - SYSTEM / DEVELOPER msg = L5 policy + M1 schemas + M2 safety + M3 few-shot exemplars when used                 │
│ - USER msg               = validated_request intent frame I1 + I2 + I3                                          │
│ - Delimiters separate sections. Reasoning models: keep prompts simple. Non-reasoning models: explicit           │
│   scaffolding allowed.                                                                                          │
│ - Private scratchpad NEVER crosses L1 → L0. Only sanitized published_rationale appears in the output contract.  │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │ [ reason ]
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ THE THINKING DESK (L1 REASONING LOOP — planner mode + evaluator-optimizer)                                      │
│ ✍️ 🔶 gen_text produces plan drafts, decompositions, assumptions, and rationale                                  │
│ 🧾 judge_text may critique plan quality, safety, and agency posture                                              │
│ 🧱 only the published 📜 L1PlanContract crosses the boundary                                                     │
│ invariant: internal non-linearity stays here only. L1 can draft, inspect, refine, simplify, clarify,            │
│ re-draft, or abstain, but cannot execute.                                                                        │
│ planner mode ∈ { DIRECT, CHAIN_OF_THOUGHT, REACT, DECOMPOSED } — chosen from I3 work class and plan budget.     │
│ iteration budget: max_refinements, wall_clock_ms, token_cap. Hitting any cap forces an exit branch below.       │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────┐ ┌────────────────────────────────┐ ┌──────────────────────────────────────┐ │
│ │ T1 INTERPRET THE REQUEST       │ │ T2 DRAFT THE PLAN             │ │ T3 EVALUATE + SELF-CRITIQUE          │ │
│ │ 🧩 🔵 classify -> 🔶 interpret │ │ ✍️ 🔶 generate plan           │ │ ✍️ 🧾 judge_text critique            │ │
│ │ - contextual refinement of the │ │ - break goal into work units  │ │ - does it answer the real goal?      │ │
│ │   visible request before plan  │ │ - order dependencies          │ │ - is it safe and coherent?           │ │
│ │ - identify explicit unknowns   │ │ - propose route options only  │ │ - lowest viable agency?              │ │
│ │ - sharpen what matters most    │ │ - mark grounding / support    │ │ - per-step expected_ground_truth?    │ │
│ │ - fact-grade intent as         │ │ - declare expected evidence   │ │ - critic persona scores plan;        │ │
│ │   DIRECTLY_OBSERVED / DERIVED  │ │   each step will return       │ │   emits accept / refine / escalate   │ │
│ │   / UNRESOLVED                 │ │ - declare assumptions + gaps  │ │ - loop T2↔T3 up to budget cap        │ │
│ └──────────────┬─────────────────┘ └──────────────┬─────────────────┘ └──────────────────────┬───────────────┘ │
│             [interpret]                       [draft]                                     [evaluate]            │
│                └────────────────────────────────┴─────────────────────────────────────────────┘                │
│                                                          ▼                                                      │
│    T3 exit branches, mutually exclusive:                                                                      │
│       (a) ACCEPT      → plan approved, emit L1PlanContract                                                      │
│       (b) REFINE      → return to T2 if refinements_used < max_refinements                                     │
│       (c) CLARIFY     → request user clarification, distinct from abstain, blocks on human input                │
│       (d) BEST-EFFORT → budget exhausted but safe partial plan possible → emit with limitations, route R5       │
│       (e) ABSTAIN     → unsafe or under-specified → emit R5 safe-default, no user prompt                        │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │ [ output ]
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L1 PLAN OUTPUT CONTRACT (published, crosses L1 → L0)                                                            │
│ 🧱 📜 L1PlanContract only                                                                                        │
│ structured handoff; internal scratchpad is NOT included                                                         │
│ - proposed_route         : R1A | R1B | R3 | R4 | R5 | CLARIFY                                                   │
│ - reasoning_mode         : DIRECT | CHAIN_OF_THOUGHT | REACT | DECOMPOSED                                       │
│ - query_spec             : retrieval ask for C0 if grounding_required, later becomes 🔵 intent_vec              │
│ - task_spec              : per-step work units with expected_ground_truth                                       │
│ - route_risk             : cost / latency / safety / reversibility signature                                    │
│ - confidence_score       : ∈ [0.0, 1.0] — rubric-anchored; below HITL threshold ⇒ gate at [5] EXIT              │
│ - grounding_required     : bool — forces C0 retrieval path                                                      │
│ - declared_assumptions   : fact-graded DIRECTLY_OBSERVED | DERIVED | UNRESOLVED                                 │
│ - unresolved_gaps        : explicit list of what L1 could not resolve                                           │
│ - published_rationale    : sanitized 🔶 gen_text, redacted of private scratchpad                                │
│ - planner_telemetry      : refinements_used, wall_clock_ms, token_usage, critic_iterations                      │
│ invariant: L1 produces the notepad plan only. It does not retrieve evidence, route with authority, or perform   │
│ the work. Private scratchpad stays in L1; only the fields above cross the boundary.                             │
└───────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                        │ [ handoff ]
                                                        ▼
                                         [ Send to Hallway Director [3] ]

┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ REPLAN RE-ENTRY (from [5] EXIT EVAL & CONTROL)                                                                  │
│ 🧱 controlled re-entry only                                                                                      │
│ When L2/C0/L3 return evidence that invalidates a declared_assumption, the exit gate MAY route back to L1 with   │
│ a replan_request carrying: original plan_id, failed_assumption, observed_evidence, residual_budget.             │
│ L1 re-enters at T2 with the reduced budget and emits a successor L1PlanContract linked by plan_id.              │
│ Replan count is bounded; exceeding the cap escalates to BEST-EFFORT or ABSTAIN, not another replan.             │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

===========================================================================================================
[3] ROUTE DECISION + SWITCHING                                  🧩 score/classify -> 📜 RouteContract
===========================================================================================================
[ PEDAGOGICAL LEGEND ]  🔵 intent_vec = live route ask / query / step-specific search vector
                        🟠 fact_vec   = stored source chunk / indexed fact / retrieval target
                        🟢 graph_sig  = lineage / dependency / ACL / citation / trace relationship
                        🔶 gen_text   = plan, route explanation, workflow sequence, tool-call proposal
                        🧾 judge_text = rubric judgment / critique summary
                        [RET]        = Terminal early exit; bypasses L3 and returns to Exit Control

===========================================================================================================

 ┌──────────────────────────────────────────────┐                               ┌────────────────────────────────────┐
 │ L0 ROUTING (Dispatcher)                      │                               │ L4 STATE / ARCHIVE                 │
 │ 🧩 route scoring may use encoder + decoder  │                               │ 🗄️ durable read surface            │
 │ 🧱 📜 emits exactly one RouteContract        │                               │ - Universal Persistence Boundary   │
 │ - Ingress: approved L1 plan + 🔵 intent_vec │                               │ - Cache Stores Exact/Semantic      │
 │ - Pre-filter: tenant / ACL / region bounds  │                               │ - Canonical raw chunks 🟠          │
 │ - Enforce expiry / freshness requirements   │                               │ - Dense vector / sparse index 🟠   │
 │ - Fast Fail: reject invalid scope early     │                               │ - Knowledge graph & entities 🟢    │
 │ - Score: cache / grounded / action /        │                               │ - Canonical source lineage         │
 │   workflow / support / freshness needs      │                               │ - Version manifests / schema       │
 │ - Emit route contract, not the work itself  │                               │ - No direct write path exists      │
 └──────────────────────┬───────────────────────┘                               └──────────────────┬─────────────────┘
                        │                                                                          │
                        ▼                                                                          │
 ┌──────────────────────────────────────────────┐                                                  │
 │ L0 ROUTE DECISION SWITCH                     │                                                  │
 │ 🧩 🔵/🟠/🟢 may inform choice                 │                                                  │
 │ ✍️ 🔶 may generate route rationale           │                                                  │
 │ 🧱 only 📜 RouteContract has authority       │                                                  │
 │ The dispatcher selects ONE path family:      │                                                  │
 │ terminal, single-step, or managed workflow.  │                                                  │
 │ L0 may use encoder scores or decoder logic,  │                                                  │
 │ but only its sealed RouteContract has route  │                                                  │
 │ authority.                                  │                                                  │
 └─┬────────────────────────────────────────────┘                                                  │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R1A EXACT CACHE                        │◄──────────────────────────────────────────────────┤
   │  │ 🧱 deterministic key lookup            │                                                   │
   │  │ - Perfect keyed reuse, zero infer      │                                                   │
   │  │ - Exact prior answer                   ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Short-circuit path                   │                                                   │
   │  │ - NO C0 NEEDED, NO L3 NEEDED           │                                                   │
   │  │ - Must still pass Exit output checks   │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R1B SEMANTIC CACHE                     │◄──────────────────────────────────────────────────┤
   │  │ 🧠 compare 🔵 live ask to stored refs  │                                                   │
   │  │ - Policy-approved similarity reuse     │                                                   │
   │  │ - Matches 🔵 ask vs cached 🔵/🟠 refs   ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Reuse-safe bounded task class        │                                                   │
   │  │ - NO C0 NEEDED, NO L3 NEEDED           │                                                   │
   │  │ - Similarity is not truth; Exit checks │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R5 FALLBACK                            │                                                   │
   │  │ 🧱 safe terminal route                 │                                                   │
   │  │ - Safest bounded outcome               │                                                   │
   │  │ - Abstain / clarify / safe default     ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Terminal safe route                  │                                                   │
   │  │ - NO C0 NEEDED, NO L3 NEEDED           │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R3 SIMPLE GROUNDED READ                │                                                   │
   │  │ 🧩 retrieve/verify -> generate answer  │                                                   │
   │  │ - Factual / policy claims need backing │                                                   │
   │  │ - Strictly grounded answer only        │                                                   │
   │  │ - Single-pass grounding                │                                                   │
   │  │ - Bypasses L3, still needs one L2 step │                                                   │
   │  └───────────────────┬────────────────────┘                                                   │
   │                      ▼                                                                        │
   │  ┌────────────────────────────────────────┐                                                   │
   │  │ C0 CONTEXT ENGINE (Ref Desk)           │◄──────────────[ Read ]────────────────────────────┤
   │  │ 🧠 🔵 intent_vec MATCHES 🟠 fact_vec   │                                                   │
   │  │ 🧠 rank / compare / classify support   │                                                   │
   │  │ 🟢 graph_sig for lineage / ACL / deps  │                                                   │
   │  │ 🧱 emits 📜 FinalEvidenceContract      │                                                   │
   │  │ - Scope source / freshness / ACL       │                                                   │
   │  │ - Match 🔵 ask against 🟠 evidence     │                                                   │
   │  │ - May traverse 🟢 graph relations      │                                                   │
   │  │ - Use sparse/BM25 for exact terms      │                                                   │
   │  │ - Use metadata for names/IDs/dates     │                                                   │
   │  │ - Dedupe / rerank / verify support     │                                                   │
   │  │ - Surface contradictions and gaps      │                                                   │
   │  │ - Evidence only, never answer          │                                                   │
   │  └───────────────────┬────────────────────┘                                                   │
   │                      │ [Evidence Contract]                                                    │
   │                      ▼                                                                        │
   │  ┌────────────────────────────────────────┐                                                   │
   │  │ PROMPT ASSEMBLY                        │◄──────────────[ Load ]────────────────────────────┘
   │  │ 🧱 compose signed prompt contract       │
   │  │ 🧩 packages 🟠 evidence for decoder     │
   │  │ - Load system template + schema        │
   │  │ - Slot grounded context 🟠             │
   │  │ - Preserve source labels + fences      │
   │  │ - Budget / trim / reserve tokens       │
   │  │ - Emit bounded prompt packet           │
   │  │ - Packages only, does not retrieve     │
   │  │ - Does not call provider or execute    │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │       [ L2 Execute Single Grounded Step ]──────► [RET] ──► To 5. EXIT EVAL & CONTROL
   │
   │  ┌────────────────────────────────────────┐
   ├──► R4 SINGLE ACTION                       │
   │  │ 🧱 action route -> L2                  │
   │  │ ✍️ downstream tool-call proposal only  │
   │  │ - Dispatch one bounded external action │
   │  │ - Mutation-capable but tightly scoped  │
   │  │ - Direct single-step path to L2        │
   │  │ - NO C0 NEEDED unless args grounded    │
   │  │ - NO L3 NEEDED                         │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │             [ L2 Execute Single Step ]─────────► [RET] ──► To 5. EXIT EVAL & CONTROL
   │
   │  ┌────────────────────────────────────────┐
   └──► R3/R4 MANAGED WORKFLOW                 │
      │ 🧩 route -> orchestration -> execution │
      │ - Multi-hop grounded read or action    │
      │ - Dependency order / branching / joins │
      │ - Needs resumable workflow state       │
      │ - L3 orchestration required            │
      └───────────────────┬────────────────────┘
                          │
                          ▼
       ┌──────────────────────────────────────────────────────────────────────┐
       │ L3 ORCHESTRATE (Manager)                                             │
       │ ✍️ 🔶 sequence / package steps                                        │
       │ 🧱 📜 emit bounded step contracts                                    │
       │ - Ingress: approved route package from L0                            │
       │ - Expand route into managed executable steps                         │
       │ - Preserve route bounds, budget, and policy limits                   │
       │ - Does not re-decide route                                           │
       │ - Does not execute tools or models                                   │
       │ - Does not retrieve directly                                         │
       │ - Does not write L4                                                  │
       └──────────────┬───────────────────────────────┬──────────────────────┘
                      │                               │
                      ▼                               ▼
       ┌──────────────────────────────────┐   ┌──────────────────────────────┐
       │ L3.1 STEP EXPANSION              │   │ L3.2 WORKFLOW STATE          │
       │ ✍️ 🔶 decompose / sequence       │   │ 🧱 workflow control state    │
       │ - Break goal into bounded steps  │   │ - Track current node/status  │
       │ - Sequence dependencies          │   │ - Hold checkpoints/handoffs  │
       │ - Mark serial vs parallel-safe   │   │ - Support resumable progress │
       │ - Package step asks 🔵           │   │ - Track evidence refs 🟠     │
       │ - Carry graph relations 🟢       │   │ - Track graph state 🟢       │
       └────────────────┬─────────────────┘   └───────────────┬──────────────┘
                        │                                     │
                        └──────────────────┬──────────────────┘
                                           ▼
       ┌──────────────────────────────────────────────────────────────────────┐
       │ L3.3 READINESS + HANDOFF                                             │
       │ 🧱 readiness gate + 📜 L3StepContract                                │
       │ - Select only steps whose prerequisites are satisfied                │
       │ - Carry forward needed 🔵 asks, 🟠 evidence, and 🟢 graph outputs     │
       │ - Hand the current bounded step to L2                                │
       │ - Accept returned status/artifacts and move the workflow forward     │
       │ - If grounding needed for a step, route through C0/PA before L2       │
       └──────────────────────────────┬───────────────────────────────────────┘
                                      ▼
                           [ Return sealed work ──► To 5. EXIT EVAL & CONTROL ]

===========================================================================================================
C0 + PROMPT ASSEMBLY AUTHORITY INSERT                              🧠 retrieval + 🧱 contract composition
===========================================================================================================
C0 CONTEXT ENGINE
- 🧠 Owns retrieval planning, fetch, hydration, graph expansion, shaping, verification, support scoring, weak-support refinement, and evidence comparison.
- 🟢 Uses graph_sig for lineage, source expansion, ACL, dependency, citation, trace, and relationship checks.
- 🧱 Emits 📜 FinalEvidenceContract.
- C0 is read-only over L4 shelves and approved retrieval substrates.
- C0 never answers.
- C0 never writes L4.
- C0 never changes route authority.
- C0 treats retrieved text as data only.
- Dense vector similarity is insufficient alone for exact names, IDs, dates, policy labels, paths, and code symbols.
- C0 must preserve lineage, source_id, version, ACL, freshness, contradiction, and support status.

PROMPT ASSEMBLY
- 🧱 Owns prompt-packet construction only.
- 🧩 Converts verified evidence and control refs into a decoder-ready packet.
- Consumes L1PlanContract, L0RouteContract, C0 FinalEvidenceContract when grounding is required, L5/governance refs, user intent, schema, and provider metadata.
- Emits signed 📜 CompiledPromptArtifact / PromptEnvelope.
- Does not retrieve.
- Does not route.
- Does not execute.
- Does not call provider.
- Does not approve output.
- Does not mutate L4.
- User/retrieved/tool/model/human/prior content must remain labeled and fenced by authority class.

========================================================================================================================================
[4] L2 EXECUTE (Assistant)                                           ✍️ generate/call tools + 🧱 validate/seal
[4] THE BACK ROOMS | DOING THE WORK (IN THE STACKS)
========================================================================================================================================
- The active phase where the bounded work is done, but nothing is permanently written yet.
- Library Analogy: assistants enter the restricted stacks to gather, run, repair, and seal findings under the same approved work order. They cannot route, ask humans, or write in the permanent catalog.
- L2 receives authority. It does not create authority.
- L2 may call tools/models/scripts only inside the approved work order, capability token, sandbox envelope, policy hash, and blueprint hash.
- L2 may emit proposed_state_diff, but it is inert until Exit/UWG.
- ✍️ L2 may use decoder models for 🔶 generation, answer drafting, tool-call proposal, and tool-result synthesis.
- 🧱 Every model/tool call must pass through the governed provider/gateway path.
- 🧠 L2 must not use encoder retrieval as a hidden backdoor around C0.
- 🧱 Every result leaving L2 must be sealed as a 📜 SealedL2Artifact.

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
│ - Every result leaving L2 must be sealed, replayable, lineage-bound, terminal-classified, and evidence-carrying                     │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E1. PREPARATION DESK                                                                                                                 │
│ [ Intake Counter ]                                                                                                                   │
│ 🧱 prepare execution room / 📜 bind packet                                                                                            │
│ - Accept the signed step packet / current-step contract                                                                              │
│ - Lock environment, tools, permissions, and execution budget                                                                         │
│ - Bind stable run identity and execution lineage                                                                                     │
│ - Freeze the governing blueprint/policy snapshot for this step                                                                       │
│ - Prepare the step so later healing works against the same approved frame                                                            │
│ - Attach replay key, attempt seed, prompt hash, input hash, policy hash, blueprint hash                                               │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     │
                                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E2. WORK ORDER CHECK                                                                                                                 │
│ [ Packet Inspection Desk ]                                                                                                           │
│ 🧱 🚦 validation gate before execution                                                                                                │
│ - Confirm the step packet is authentic and internally consistent                                                                     │
│ - Verify permissions, scope, runtime budget, capability token, and sandbox envelope                                                   │
│ - Validate shape of inputs and expected side-effect class                                                                            │
│ - Confirm the step can be executed as handed off, without rerouting                                                                  │
│ - Fail before execution on missing authority, missing sandbox, stale policy, blocked ACL, or route mismatch                          │
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
│ [ The Study Carrel ]                                                                                                   │   │ 🧱 sealed failure contract        │
│ ✍️ 🔶 model/tool output, answer draft, tool proposal, synthesis                                                         │   │ - Reason for rejection            │
│ 🧱 bounded sandbox and trace capture                                                                                    │   │ - No actual work was performed    │
│ - Invoke the required tool/model/action                                                                                │   │ - Sealed before execution         │
│ - Run under bounded time, policy, and sandbox limits                                                                   │   └───────────────────┬───────────────┘
│ - Capture outputs, traces, and intermediate execution evidence                                                         │
│ - Use only packet-provided prompt/tool/model/action parameters                                                         │
│ - No hidden parameters, no opportunistic tools, no unapproved retrieval, no authority expansion                         │
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
                            │     │ 🧩 classify failure -> 🔶 repair proposal -> 🧱 same-authority gate       │
                            │     │ - Identify what failed and why                                          │
                            │     │ - Apply only bounded, allowed repair actions                            │
                            │     │ - Keep the same governing snapshot and step lineage                     │
                            │     │ - Check retry limits so the step does not loop forever                  │
                            │     │ - If repaired, send back to E3                                          │
                            │     │ - If not repaired, mark NEEDS_HELP or terminal failure                  │
                            │     │                                                                          │
                            │     │ HEAL SPLIT                                                              │
                            │     │ - Heal repository = approved repair menu for this agent/tool/route       │
                            │     │ - Heal function = live same-authority repair governor for this failure   │
                            │     │ - Cannot heal missing authority, blocked ACL, policy conflict, route     │
                            │     │   mismatch, stale policy, sandbox gap, or HITL need                     │
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
│ 🧱 📜 SealedL2Artifact                                                                                                                │
│ - Package the final output, notes, and execution evidence                                                                            │
│ - Attach traces, lineage, validation history, retry history, repair counters, and terminal classification                            │
│ - Attach replay-oriented receipts and attempt counters                                                                               │
│ - Attach proposed_state_diff only when mutation intent exists                                                                        │
│ - Seal the step result as an L2 artifact for downstream control                                                                      │
│                                                                                                                                    │
│ Terminal classes: SUCCESS | FAILURE | NEEDS_HELP | REJECTED                                                                         │
│ Invariant: no durable commit here. L2 only emits sealed artifacts for downstream control.                                           │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     │ [ Sealed Folders / Step Results ]
                                                                     ▼
                                                           [ Send to Next Step [5] ]

========================================================================================================================================
[5] EXIT EVAL & CONTROL                                           🧩 evaluate -> 🧾 judge_text -> 🧱 X3 disposition
[5] THE EXIT DESK | FINAL REVIEW BEFORE RESPONSE OR COMMIT
========================================================================================================================================
- The final runtime checkpoint that receives either a sealed L2 result, sealed workflow package, re-cleared HITL packet, or terminal [RET] short-circuit from L0.
- Library Analogy: the head desk reviews the finished folder, decides whether it can leave safely, whether it needs human review, whether it must be sent back, or whether it may request real ink through the Master Clerk.
- Exit owns current-run checkout and exactly one X3 disposition.
- Exit does not execute tools.
- Exit does not retrieve evidence.
- Exit does not mutate L4.
- Exit does not let L6 learning rescue the current run.
- 🧠 Exit may use classifiers, semantic comparisons, schema checks, and trace comparisons.
- ✍️ Exit may use 🧾 judge_text for rubric rationale.
- 🧱 Only the X1/X2/X3 gate contract creates final current-run disposition.

                                    [ Sealed L2 Artifacts ]                    [RET] Short-Circuit from L0
                                                  │                                      │
                                                  └──────────────────┬───────────────────┘
                                                                     │ [ runtime disposition input ]
                                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. EXIT EVAL & CONTROL                                                                                                               │
│ 🧩 🔵/🟠/🟢 -> 🧾 judge_text where evaluation requires semantic or grounded comparison                                                  │
│ 🧱 🚦 X1 gates -> X2 aggregation -> 📜 X3 disposition                                                                                 │
│ - Final runtime policy, safety, authority, quality, evidence, replay, and observability review                                      │
│ - Receives only sealed runtime outputs or terminal short-circuits                                                                    │
│ - Produces exactly one X3 disposition                                                                                                │
│                                                                                                                                    │
│ X1 CURRENT-RUN CHECKOUT GATES                                                                                                        │
│ X1A Today's Rules       - policy manifest, threshold profile, grader roster                                                         │
│ X1B Answered It         - task completion, format, instruction-follow                                                               │
│ X1C Safe to Leave       - sandbox, mutation authority, side effect, egress                                                          │
│ X1D Answer Good         - groundedness, faithfulness, citations, support                                                            │
│ X1E Trajectory OK       - process quality, tool choice, retry, handoff                                                              │
│ X1F Story Adds Up       - internal consistency and cross-step coherence                                                             │
│ X1G Replay Eligible     - replay guard, idempotency, manifest integrity                                                             │
│ X1H Observable          - OTEL span tree, counters, audit trail completeness                                                        │
│ X1I Consistency         - pass^k / variance / drift where activated                                                                 │
│ X1J Write Eligibility   - pre-UWG readiness when mutation requested                                                                 │
│                                                                                                                                    │
│ Gate result enum: PASS | FAIL | WARN | UNKNOWN | NOT_APPLICABLE                                                                     │
│ Runtime law: UNKNOWN is never PASS. NOT_APPLICABLE requires reason.                                                                 │
│                                                                                                                                    │
│ X2 AGGREGATION                                                                                                                       │
│ - combines X1 verdicts under policy weights and thresholds                                                                          │
│ - computes aggregate severity, confidence, unknown_fraction, and recommendation                                                     │
│                                                                                                                                    │
│ X3 DISPOSITION, exactly one                                                                                                          │
│ - X3A DENY / REROUTE                                                                                                                 │
│ - X3B ESCALATE_HITL                                                                                                                  │
│ - X3C COMMIT_REQUEST_TO_UWG                                                                                                          │
│ - X3D ALLOW / FINISH                                                                                                                 │
│ - X3E SAFE_ABSTAIN                                                                                                                   │
│                                                                                                                                    │
│ CURRENT-RUN EVALUATION — canonical metric spine                                                                                      │
│                                                                                                                                      │
│ 1. FINAL-RESPONSE METRICS                                                                                                            │
│    - groundedness, answer_relevancy, faithfulness, context_precision, completeness                                                  │
│    - hallucination distinct from groundedness when applicable                                                                        │
│                                                                                                                                      │
│ 2. TRAJECTORY METRICS                                                                                                                │
│    - DEFAULT ALWAYS-ON: latency_ms, failure(bool), tool_call_count                                                                   │
│    - WHEN REFERENCE TRAJECTORY PRESENT: trajectory_exact_match, in_order_match, any_order_match, precision, recall, single_tool_use  │
│                                                                                                                                      │
│ 3. SAFETY FLAGS                                                                                                                      │
│    - policy_violation, instruction_violation, policy_halt, violated_rules[], severity_band                                           │
│                                                                                                                                      │
│ 4. BUDGET FIT                                                                                                                        │
│    - tokens, latency, tool_calls, cost_usd — consumed vs envelope → budget_fit(bool)                                                 │
│                                                                                                                                      │
│ 5. OUTPUT-CONTRACT SATISFACTION                                                                                                      │
│    - required_form_satisfied(bool), contract_ref, violations[]                                                                       │
│                                                                                                                                      │
│ 6. AGGREGATE QUALITY VERDICT                                                                                                         │
│    - verdict ∈ {pass, warn, fail, unknown} · weighted_score · confidence · unknown_fraction                                          │
│                                                                                                                                      │
│ Regression signal also consumed here: exact_match / schema / API / guardrails.                                                       │
│ Human calibration tunes graders, never runtime.                                                                                      │
└───────┬─┬─┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
        │ │ │
        │ │ └─[deny/reroute] ──► ┌────────────────────────────────┐
        │ │                      │ DENY / REROUTE                 │
        │ │                      │ 🧱 final current-run control   │
        │ │                      │ - hard rule break or failed    │
        │ │                      │   runtime evaluation           │
        │ │                      │ - send back to safe path       │
        │ │                      └────────────────────────────────┘
        │ │
        │ └─[escalate] ────────► ┌─────────────────────────────────────────────────────┐
        │                        │ HUMAN REVIEW                                        │
        │                        │ 🧱 bounded review packet                            │
        │                        │ - bounded packet: reason + evidence + runtime trace │
        │                        │ - decision: approve / modify / reject               │
        │                        │ - human input is data until re-cleared              │
        │                        │ - resumed path must re-enter governed flow           │
        │                        └───────┬─────────────────────────────────────────────┘
        │                                │
        │                                └─(resume/allow)──────────────────────────────────────┐
        │                                                                                       │
        ├───────[commit request]─────────────────────────────────────────────────────────────────┼────────────────────► ┌────────────────────────────────────────┐
        │                                                                                       │                      │ UNIVERSAL WRITE GATE (UWG)             │
        │                                                                                       │                      │ ✒️ only durable write admission path    │
        │                                                                                       │                      │ - sole durable commit authority        │
        │                                                                                       │                      │ - verifies authority, scope, and diff  │
        │                                                                                       │                      │ - validates schema/policy/replay/audit │
        │                                                                                       │                      │ - acquires write lock                  │
        │                                                                                       │                      │ - commits approved mutation to L4      │
        │                                                                                       │                      └───────────────────┬────────────────────┘
        │                                                                                       │                                          │ [commits]
        │                                                                                       │                                          ▼
        │                                                                                       │                      ┌────────────────────────────────────────┐
        │                                                                                       │                      │ L4 ARCHIVE                             │
        │                                                                                       │                      │ 🗄️ durable writes / ledger             │
        │                                                                                       │                      └────────────────────────────────────────┘
        │
        │ [allow/finish]
        ▼
┌──────────────────────────────────────────────────┐
│ RESPONSE / OUTCOME                               │◄───────────────────────────────────────────────────────────────────────────────────┘
│ 🧱 final returned outcome                        │
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
 │ 🧱 read sealed exhaust    │   │ 🧩 signals -> 🧾 judge    │   │ ✍️ 🔶 RCA/proposals       │   │ ✒️ UWG-only promotion     │
 │                           │   │                           │   │                           │   │                           │
 │ - Map telemetry, traces,  │   │ - Grade outcomes,         │   │ - Aggregate graded        │   │ - Run gated review on     │
 │   exits, artifacts,       │   │   groundedness, and       │   │   signals into incident   │   │   proposed changes        │
 │   HITL packets, and       │   │   citation support        │   │   patterns and severity   │   │ - Approve or reject       │
 │   UWG receipts            │   │ - Grade trajectories:     │   │ - Perform RCA and drift   │   │   promotion candidates    │
 │ - Normalize evidence and  │   │   tool order, retries,    │   │   investigation           │   │ - Route approved updates  │
 │   preserve lineage /      │   │   budget, execution shape │   │ - Draft prompt / policy / │   │   through UWG to L4       │
 │   replay linkage          │   │ - Detect regressions in   │   │   rubric / config changes │   │ - Publish committed       │
 │ - Observer posture only:  │   │   exact match, schema,    │   │   as proposals only       │   │   next-run updates onto   │
 │   evidence reads only,    │   │   API, and guardrails     │   │ - No promotion yet, only  │   │   rollout surfaces        │
 │   no live mutation        │   │ - Human calibration tunes │   │   candidate update sets   │   │ - No current-run mutation │
 │                           │   │   grading, not runtime    │   │                           │   │                           │
 └───────────────────────────┘   └───────────────────────────┘   └───────────────────────────┘   └─────────────┬─────────────┘
                                                                                                               │
                                                                                                               ▼
         [ FUTURE RUNTIME SURFACES UPDATED: BUS U pushes Prompts, Policies, Baselines, Rubrics, and Approved Reason Priors ]
         [ INVARIANT: learning signals inform next-run behavior only. They do not mutate or rescue the completed run. ]

========================================================================================================================================
CROSS-CUTTING RUNTIME GATES VS EXIT CRITERIA                         🧱 🚦 vs 🧱 X3 vs 🔐 cert
========================================================================================================================================

00C RUNTIME GATES
- 🧱 🚦 gate logic.
- Ask: "Can this current live step, packet, tool call, output, escalation, or write proposal proceed right now?"
- Emit GateVerdict.
- Run across U0, L1, L0, C0, PA, L3, L2, Exit, UWG/L4, and L6 firewall points.
- Own G01-G29 live gate law.
- May recommend bounded runtime dispositions.
- Do not emit final X3.
- Do not certify L5 evidence as their own output.
- Do not write L4.

EXIT EVAL
- 🧩 may evaluate with encoder and decoder judge signals.
- 🧱 emits exactly one X3 disposition.
- Ask: "Can this sealed run result leave, reroute, escalate, abstain, or request durable commit?"
- Aggregates X1 checks through X2.
- Emits exactly one X3 disposition.
- Does not execute.
- Does not retrieve.
- Does not write L4.

L5 GOVERNANCE
- 🔐 cert evidence.
- Ask: "Is the packet certified under valid policy, authority, registry, origin-trust, capability, sandbox, egress, HITL, replay, and audit evidence?"
- Emits certification evidence, receipts, gap reports, manifests, hashes, and status language.
- Does not emit live runtime dispositions.
- Does not decide final X3.
- Does not write L4.

L4/UWG
- 🗄️ state and ✒️ commit control.
- Ask: "What durable system-of-record state exists, and may this cleared mutation be admitted?"
- L4 owns durable records and read surfaces.
- UWG owns the only durable write path.
- No layer writes around UWG.

L6
- 🧪/🧾 completed-run evaluation feeding future-run proposals.
- Ask: "What can completed-run evidence teach future runs after the runtime boundary?"
- Cannot mutate current run.
- Cannot directly write L4.
- Must pass approved promotion through UWG.

========================================================================================================================================
99 END-TO-END PROOF HARNESS                                             🧪 proof
========================================================================================================================================
- 🧪 99 does not own runtime behavior.
- 🧪 99 proves that the runtime behavior actually happened.
- A run is not proven because the final answer looks right.
- A run is proven only when contracts, traces, gate receipts, replay evidence, no-bypass evidence, and artifact manifests line up.

Minimum proof bundle:
- scenario_id
- request_id
- run_id
- trace_root
- policy_hash
- blueprint_hash
- replay_key
- RouteContract or terminal route packet
- FinalEvidenceContract when grounding is required
- PromptEnvelope or CompiledPromptArtifact when model execution is required
- sealed L2 artifact or terminal RET packet
- ExitReviewPacket
- X1 gate/check verdict bundle consumed by Exit
- X3 disposition receipt
- CommitRequest and UWG receipt if durable mutation is requested
- RuntimeExhaustBundle handoff to L6 after boundary
- OTEL span tree export
- replay comparison receipt
- no-bypass assertion receipt
- artifact manifest and deterministic digest


==============================================================================================================================
[ LEGEND ] LAYER DEFINITIONS (L0 - L6)
==============================================================================================================================
 LAYER │ PERSONA                  │ CORE FUNCTION / MEANING
───────┼──────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────
 U0    │ Front Desk / Guard       │ 🧠 classify + 🧱 validate envelope, identity, schema, quota, origin labels, trace root.
 L0    │ Dispatcher               │ 🧩 route scoring + 🧱 exactly one deterministic RouteContract.
 L1    │ Librarian                │ 🧩 intent/priors -> ✍️ 🔶 plan + 🧱 L1PlanContract.
 L2    │ Assistant                │ ✍️ generate/call tools + 🧱 validate, heal locally, seal artifacts.
 L3    │ Manager                  │ ✍️ sequence workflow + 🧱 bounded step contracts, no execution.
 L4    │ Archivist                │ 🗄️ authoritative durable state; broad read, UWG-only write.
 L5    │ Safety Officer           │ 🔐 cross-cutting governance certification evidence.
 L6    │ Observer                 │ 🧾 completed-run evaluation and ✍️ future-run proposals only.
 00C   │ Runtime Gate Mesh        │ 🚦 live GateVerdict law; proceed/stop checks, UNKNOWN is never PASS.
 99    │ Proof Harness            │ 🧪 cross-layer acceptance proof, OTEL, replay, no-bypass, route coverage.
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

==============================================================================================================================
[ LEGEND ] ARTIFACT / CONTRACT DEFINITIONS
==============================================================================================================================
 ARTIFACT / CONTRACT             │ OWNER │ MEANING
─────────────────────────────────┼───────┼────────────────────────────────────────────────────────────────────────────────────
 ValidatedRequest                │ U0    │ 📜 clean stamped ingress packet for L1.
 L1PlanContract                  │ L1    │ 📜 advisory plan, query_spec, task_spec, assumptions, route hints.
 RouteContract                   │ L0    │ 📜 deterministic route authority. Exactly one per routed run.
 FinalEvidenceContract           │ C0    │ 📜 verified evidence packet with support, lineage, gaps, contradictions.
 CompiledPromptArtifact          │ PA    │ 📜 signed provider-ready prompt packet. Compose-only artifact.
 L3StepContract                  │ L3    │ 📜 current managed-workflow step package.
 SealedL2Artifact                │ L2    │ 📜 sealed execution result with traces, counters, terminal class.
 ProposedStateDiff               │ L2    │ 📜 inert mutation proposal. Not durable until Exit/UWG.
 ExitReviewPacket                │ Exit  │ 📜 normalized packet for X1/X2/X3 checkout.
 X3DispositionReceipt            │ Exit  │ 📜 exactly one final current-run disposition.
 CommitRequest                   │ Exit  │ 📜 request to UWG for durable mutation after Exit clears.
 UWGCommitReceipt                │ UWG   │ ✒️ durable write admission proof.
 RuntimeExhaustBundle            │ Exit  │ 📜 completed-run evidence bundle sent to L6.
 LearningProposal                │ L6    │ 📜 future-run proposal only. Must pass gauntlet and UWG to become durable.
 OTELSpanTree                    │ 99    │ 🧪 observability proof of actual runtime path.
 ReplayComparisonReceipt         │ 99    │ 🧪 deterministic replay proof where required.
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

==============================================================================================================================
END OF AGENTIC SYSTEM — PROCESS MAP v34
==============================================================================================================================