[ L1_PLAN_CONTRACT ]
                                                     │
                                                     ▼
========================================================================================================================================
[3] ROUTE DECISION + SWITCHING — v14
========================================================================================================================================

- The dispatcher takes the approved L1 plan and decides whether the request should short-circuit
  through exact reuse, bounded semantic reuse, grounded context assembly, external action
  dispatch, managed workflow orchestration, human-gated escalation, or safe fallback.
- L0 decides the path, but it does not itself retrieve, think deeply, execute tools, call models,
  mutate state, or approve final egress.
- L0 emits exactly one deterministic RouteContract:
  route_id, confidence, reason_codes, freshness_class, cache_policy, execution_form, cost_tier,
  fallback_chain, slo, telemetry_keys, tenant_scope, and hmac_sig.
- L3 is OPTIONAL and is invoked only when the selected route must be expanded into managed steps.
- Terminal [RET] routes bypass L3 completely and go straight to Exit Eval & Control.
- Single-step routes bypass L3 and go straight to one bounded L2 execution step.
- Managed workflow routes enter L3 only when dependency order, branching, joins, retries, parallel-safe
  shards, iterative refinement, or resumable state are genuinely required.
- L0 is a dispatcher, not an executor. Downstream layers consume the RouteContract but do not re-decide
  the route.


[ PEDAGOGICAL LEGEND ]  🔵 Blue asks = query_vec / intent vector
                        🟠 Orange knows = raw_text_vector / contextual_text_vector
                        🟢 Green maps = knowledge_graph / entity_subgraph
                        [RET] = Terminal early exit; completely bypasses L3 to hit Exit Control
                        ★ = v14 high-signal addition inside preserved v11 structure

 ┌──────────────────────────────────────────────┐                               ┌────────────────────────────────────┐
 │ L0 ROUTING (Dispatcher)                      │                               │ L4 STATE / ARCHIVE                 │
 │ - Ingress: L1Plan + 🔵 query_vec             │                               │ - Universal Persistence Boundary   │
 │ - Pre-filter: tenant / ACL / region bounds   │                               │ - Cache Stores (Exact/Sem.)        │
 │ - Enforce expiry / freshness requirements    │                               │ - Canonical raw chunks 🟠          │
 │ - Fast Fail: Reject invalid scope early      │                               │ - Dense vector / sparse index 🟠   │
 │ - Score: cacheable / grounded / action /     │                               │ - Knowledge graph & entities 🟢    │
 │   multi-hop / freshness / support needs      │                               │ - Canonical source lineage         │
 │ - Score: parallel / iterative / high-stakes  │ ★                             │ - Version manifests / schema       │
 │ - Apply calibrated thresholds, not vibes     │ ★                             │ - No direct write path exists      │
 │ - Select cost_tier: TIER_S / TIER_M / TIER_L │ ★                             │ - Writes require UWG, never L0/L2  │ ★
 │ - Attach fallback_chain + route SLO          │ ★                             │ - Read surfaces feed C0 only       │ ★
 │ - Emit route contract, not the work itself   │                               └──────────────────┬─────────────────┘
 │ - Emit RouteTelemetryEvent to L6             │ ★                                                │
 └──────────────────────┬───────────────────────┘                                                  │
                        │                                                                          │
                        ▼                                                                          │
 ┌──────────────────────────────────────────────┐                                                  │
 │ L0 ROUTE DECISION SWITCH                     │                                                  │
 │ The dispatcher selects ONE terminal or       │                                                  │
 │ orchestrated path based on the contract.     │                                                  │
 │ Cold-start rule: if confidence is weak,      │ ★                                                │
 │ choose conservative R3 grounded or R5 safe.  │ ★                                                │
 │ First match wins by fixed decision order:    │ ★                                                │
 │ scope fail -> cache -> HITL/high-risk ->     │ ★                                                │
 │ action -> grounded -> workflow -> fallback.  │ ★                                                │
 └─┬────────────────────────────────────────────┘                                                  │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R1A EXACT CACHE                        │◄──────────────────────────────────────────────────┤
   │  │ - Perfect keyed reuse, zero infer.     │                                                   │
   │  │ - Bypass deep pipeline entirely        ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Exact prior answer (NO C0 NEEDED)    │                                                   │
   │  │ - NO L3 NEEDED                         │                                                   │
   │  │ - Requires freshness_class satisfied   │ ★                                                │
   │  │ - cache_policy = EXACT_ONLY            │ ★                                                │
   │  │ - execution_form = TERMINAL_SHORTCIR.  │ ★                                                │
   │  │ - fallback_chain empty on hit          │ ★                                                │
   │  │ - On miss: re-decide, do not "fallback"│ ★                                                │
   │  │ - Example: "What does ADR mean?"       │ ★                                                │
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
   │  │ - Hybrid fusion + policy gates required│ ★                                                │
   │  │ - Semantic threshold must be calibrated│ ★                                                │
   │  │ - Bad cache entries amplify bad answers│ ★                                                │
   │  │ - Valid only for stable/reuse-safe asks│ ★                                                │
   │  │ - cache_policy = SEMANTIC_OK           │ ★                                                │
   │  │ - Example: "Explain Jaccard again."   │ ★                                                │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R5 FALLBACK                            │                                                   │
   │  │ - Safest bound outcome                 │                                                   │
   │  │ - Abstain/clarify                      ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Ungrounded default                   │                                                   │
   │  │ - Terminal safe route                  │                                                   │
   │  │ - NO C0 NEEDED, NO L3 NEEDED           │                                                   │
   │  │ - Always final entry in fallback_chain │ ★                                                │
   │  │ - Used for scope fail / unsafe action  │ ★                                                │
   │  │ - Used for weak support or no evidence │ ★                                                │
   │  │ - Used when confidence below threshold │ ★                                                │
   │  │ - Emits reason_code, not silent failure│ ★                                                │
   │  │ - Example: "Delete anything old."      │ ★                                                │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R3 SIMPLE GROUNDED READ                │                                                   │
   │  │ - Factual/policy claims require backing│                                                   │
   │  │ - Evidence class & support target      │                                                   │
   │  │ - Strictly grounded answer only        │                                                   │
   │  │ - Single-pass grounding, bypasses L3   │                                                   │
   │  │ - Still requires one bounded L2 step   │                                                   │
   │  │ - execution_form = SINGLE_STEP         │ ★                                                │
   │  │ - cost_tier usually TIER_M             │ ★                                                │
   │  │ - fallback_chain: workflow -> R5       │ ★                                                │
   │  │ - C0 may refine once within budget     │ ★                                                │
   │  │ - No durable write, no action dispatch │ ★                                                │
   │  │ - Example: "What does C5 say about     │ ★
   │  │   prompt assembly?"                    │ ★
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
   │  │ - Preserves citations/source lineage   │ ★                                                │
   │  │ - Flags contradiction and gaps         │ ★                                                │
   │  │ - If support remains weak: abstain/R5  │ ★                                                │
   │  │ - C0 retrieves only, never answers     │ ★                                                │
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
   │  │ - Does not retrieve or invent facts    │ ★
   │  │ - Binds replay metadata + support IDs  │ ★
   │  │ - Preserves instruction precedence     │ ★
   │  │ - Emits bounded packet for L2 only     │ ★
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │       [ L2 Execute Single Grounded Step ]──────► [RET] ──► To 5. EXIT EVAL & CONTROL
   │
   │  ┌────────────────────────────────────────┐
   ├──► R4 SINGLE ACTION                       │
   │  │ - Dispatch external action payload     │
   │  │ - Mutate state, bounded autonomy       │
   │  │ - Single bounded action direct to L2   │
   │  │ - execution_form = SINGLE_STEP         │ ★
   │  │ - capability_token + sandbox required  │ ★
   │  │ - Reversible/low-risk action only      │ ★
   │  │ - If high-risk or irreversible, route  │ ★
   │  │   to human-gated exit/HITL first       │ ★
   │  │ - Writes remain proposal-only until    │ ★
   │  │   Exit/UWG approval                    │ ★
   │  │ - fallback_chain: HITL if ambiguous,   │ ★
   │  │   then R5                              │ ★
   │  │ - Example: "Create a calendar event    │ ★
   │  │   for Monday at 3 PM."                 │ ★
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
      │ - execution_form = MANAGED_WORKFLOW    │ ★
      │ - Use only when contract changes       │ ★
      │   between steps                        │ ★
      │ - Can include parallel fan-out inside  │ ★
      │   workflow, not as L0 structural change│ ★
      │ - Can include evaluator/optimizer loop │ ★
      │   with max iterations and SLO guard    │ ★
      │ - Can include confidence cascade       │ ★
      │   TIER_S -> TIER_M -> TIER_L when      │ ★
      │   capability difficulty is uncertain   │ ★
      │ - Must preserve single-agent-first     │ ★
      │   unless specialists improve isolation │ ★
      │ - Example: "Review 90 days of tickets, │ ★
      │   find churn themes, pull evidence,    │ ★
      │   rerun weak areas, rank causes, and   │ ★
      │   draft remediation."                  │ ★
      └───────────────────┬────────────────────┘
                          │
                          ▼
       ┌──────────────────────────────────────────────────────────────────────┐
       │ L3 ORCHESTRATION CONTROL PLANE (The Managing Librarian)              │
       │ - Ingress: approved route package from L0 + action contracts         │
       │ - Consumes RouteContract, does not re-decide L0 route                │ ★
       │ - Enforces route bounds, budget, timeout, cost_tier, fallback_chain  │ ★
       │ - Holds workflow state, but cannot persist durable truth directly    │ ★
       │ - Emits current bounded step contracts only                          │ ★
       │                                                                      │
       │   ┌──────────────────────────┐      ┌───────────────────────────┐    │
       │   │ L3.1 DAG / AST RUNNER    │◄────►│ L3.2 STATE LEDGER         │    │
       │   │ - Graph dependency math  │      │ - Durable checkpoints     │    │
       │   │ - Forward-only eval      │      │ - Resumable handoffs      │    │
       │   │ - Issues 🔵 step asks    │      │ - Step status tracking    │    │
       │   │ - Serial/parallel tags ★ │      │ - fallback depth track ★  │    │
       │   │ - No backward edges ★    │      │ - SLO remaining budget ★  │    │
       │   └──────────┬───────────────┘      └───────────────────────────┘    │
       │              │                                                       │
       │   ┌──────────▼───────────────┐      ┌───────────────────────────┐    │
       │   │ L3.3 CONTEXT BUS         │◄────►│ L3.4 POLICY ENGINE        │    │
       │   │ - Passes 🟠 references   │      │ - Route bounds check      │    │
       │   │ - Coordinates 🟢 maps    │      │ - Prevents memory bloat    │    │
       │   │ - Central staging area   │      │ - Guardrail validation    │    │
       │   │ - Evidence packet only ★ │      │ - HITL trigger check ★    │    │
       │   │ - No hidden retrieval ★  │      │ - No scope expansion ★    │    │
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
           │ - Prefer single-agent / single-step if it satisfies the contract; do not split just because you can       │ ★
           │ - Choose managed workflow only when the step contract changes between steps                               │ ★
           │ - Parallel fan-out is valid only for independent shards or voting/guardrail review                        │ ★
           │ - Evaluator/optimizer loop is valid only when quality can be scored and iteration is bounded              │ ★
           │ - Confidence cascade is valid only when compute tier is uncertain, not when routing itself is uncertain   │ ★
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘
                             [ one bounded step ] ▼                                                       [ managed workflow ] ▼
           ┌────────────────────────────────────────┐                      ┌────────────────────────────────────────────┐
           │ A1. DIRECT STEP PACKAGE               │                      │ A2. MULTI-STEP WORKFLOW / DAG              │
           │ - Emit one step contract for L2       │                      │ - Build nodes, edges, branch rules         │
           │ - Encode dependency order and join rules   │                 │ - Mark parallel-safe vs serial-only paths  │
           │ - May contain one 🔵 ask or one action│                      │ - Assign where 🔵 asks, 🟠 evidence, and   │
           │ - Send immediately to execution       │                      │   🟢 graph steps enter the DAG             │
           │ - Use when R3/R4 single-step suffices │ ★                    │ - Encode retry, join, timeout, SLO budget  │ ★
           │ - No L3 expansion after packaging     │ ★                    │ - Encode fallbacks and HITL pause points   │ ★
           │ - No open-ended autonomy              │ ★                    │ - Encode max loop/cascade depth            │ ★
           └──────────────────────┬─────────────────┘                      └──────────────────────┬─────────────────────┘
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
           │ - Enforce SLO: do not spawn a node if remaining budget is already exhausted                                │ ★    │
           │ - Enforce fallback_chain: provider outage, timeout, SLO breach, or failed step uses ordered alternatives   │ ★    │
           │ - Enforce loop guard: repeated unproductive spans trigger safe route or human review in later routing      │ ★    │
           │ - Track fallback_depth, attempt_count, and reason_codes for L6 calibration                                 │ ★    │
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘      │
                                          ▼                                                                                      │
           ┌────────────────────────────────────────────────────────────┐                                                        │
           │ STEP CONTRACT TO L2                                        │                                                        │
           │ - Current node only, bounded autonomy                      │                                                        │
           │ - Tool / model / action spec                               │                                                        │
           │ - Inputs may include 🔵 query intent,                      │                                                        │
           │   🟠 grounded evidence, 🟢 graph payload                   │                                                        │
           │ - Expected artifact / support target                       │                                                        │
           │ - Includes capability_token + sandbox envelope             │ ★                                                      │
           │ - Includes cost_tier and provider lane if needed           │ ★                                                      │
           │ - Includes replay metadata, policy_hash, blueprint_hash    │ ★                                                      │
           │ - Includes slo slice and timeout/circuit breaker           │ ★                                                      │
           │ - Includes no durable commit authority                     │ ★                                                      │
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
           │ - Emits outcome_status: SUCCESS / DEGRADED / FAILED        │ ★                                                      │
           │ - Emits observed latency, tokens, cost, and quality signal │ ★                                                      │
           │ - Emits fallback_depth and exact reason_code               │ ★                                                      │
           │ - Emits best-partial artifact on timeout/SLO breach        │ ★                                                      │
           │ - Never mutates durable L4 directly                        │ ★                                                      │
           └──────────────────────┬─────────────────────────────────────┘                                                        │
                                  ▼                                                                                              │
           ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐      │
           │ C. GRAPH STATE UPDATE / HANDOFF MERGE                                                                      │      │
           │ - Mark node done / failed / retry                                                                           │      │
           │ - Unlock dependents or trigger allowed repair / reroute path                                               │      │
           │ - Rejoin branches and merge returned 🟠 support and 🟢 graph outcomes into next-step readiness             │      │
           │ - Carry forward next eligible 🔵 asks without turning L3 into an open loop                                 │      │
           │ - For parallel fan-out: aggregate section shards or voting results before downstream merge                 │ ★    │
           │ - For evaluator/optimizer: stop at quality threshold, max_iterations, or exhausted budget                  │ ★    │
           │ - For cascade: escalate TIER_S -> TIER_M -> TIER_L only when executor confidence requires it               │ ★    │
           │ - For HITL pause: freeze packet, materialize bounded evidence, resume only through governed re-clearance   │ ★    │
           │ - Failed repair stays inside same blueprint/policy snapshot; no hidden scope growth                        │ ★    │
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘      │
                                          ▼                                                                                      │
           ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐      │
           │ D. COMPLETION / EXIT PACKAGE                                                                                │      │
           │ - Test whether all required nodes are sealed                                                                 │      │
           │ - Verify all required 🟠 support obligations and route-level success conditions are satisfied                │      │
           │ - Emit one sealed workflow package upward for the control layer, or return to B for the next ready node     ├──────┘ no
           │ - Attach RouteTelemetryEvent + RouteOutcomeEvent join keys                                                  │ ★
           │ - Attach confidence, reason_codes, fallback_depth, SLO usage, and cost tier                                 │ ★
           │ - Attach evidence lineage, citations, replay receipts, and policy_hash                                      │ ★
           │ - If any required support is weak: emit safe partial / abstain disposition, not fabricated certainty        │ ★
           │ - If any mutation is requested: emit commit request only; UWG remains the sole durable write path           │ ★
           │ - Learning signal is exhaust only; L6 may tune future runs but never mutates this completed run             │ ★
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘
                                       yes ▼
                             [ Return sealed work ──► To 5. EXIT EVAL & CONTROL ]



========================================================================================================================================
SIMPLE QUERY EXAMPLES — v14
========================================================================================================================================

R1A EXACT CACHE:
- "What does ADR mean?"
- "What is golden path meaning?"

R1B SEMANTIC CACHE:
- "Explain Jaccard again."
- "Remind me what semantic cache does."

R3 SIMPLE GROUNDED READ:
- "What does C5 say about prompt assembly?"
- "Review this file and tell me where retrieval happens."
- "What does my lease say about the pet policy?"

R4 SINGLE ACTION:
- "Create a calendar event for Monday at 3 PM."
- "Draft an email to Amy."
- "Archive these three emails."

R3/R4 MANAGED WORKFLOW:
- "Review 90 days of tickets, incident logs, and churn notes; find top themes, pull evidence,
   rerun weak areas, rank causes, and draft remediation."
- "Audit the repo for OpenAI embedding call sites, classify each one, propose BGE migration,
   and produce a test plan."

R5 FALLBACK:
- "Delete anything that looks old."
- "Send this vague message to everyone in my contacts."
- "Use whatever credentials you can find."
- "Tell me what the document says" when no document exists.


========================================================================================================================================
[!] INVARIANTS
========================================================================================================================================

- L0 routes. It does not retrieve, execute, call models, mutate state, or approve output.
- C0 retrieves evidence only when R3/R3R4 requires grounding.
- Prompt Assembly packages only. It does not retrieve or invent.
- L3 orchestrates only managed workflows. It is optional, not always-on.
- L2 executes only the current bounded step. It does not route or commit.
- Exit Eval & Control receives all [RET] short-circuits and sealed L2/L3 artifacts.
- HITL input is data that must be re-cleared, not sovereign authority.
- UWG is the sole durable write path into L4.
- L6 observes, evaluates, calibrates, and promotes future-run learning only.
- Learning signals never mutate or rescue the completed current run.
- Same RouteContract + same policy_hash + same snapshot must replay to the same routing digest.