========================================================================================================================
                                      AGENTIC SYSTEM PROCESS MAP - EXECUTIVE SUMMARY
                                      ZERO-LOSS FULL OVERWRITE WITH SPINE SUBSTEPS
========================================================================================================================
 [!] SIMPLEST VIABLE PATTERN: deterministic workflow first -> single agent -> multi-agent only
 [i] AGENT CORE = model + tools + instructions + guardrails + evals
 [!] CHEAT RULE: L2 proposes -> Exit clears -> UWG commits -> L4 stores
 [!] CONTROL SPLIT: Runtime Gates decide live proceed/stop | Exit emits one X3 | L5 certifies evidence
 [!] WRITE LAW: only UWG writes durable state to L4
 [!] LEARNING LAW: L6 learns only after the current run boundary

 ----------------------------------------------------------------------------------------------------------------------
 MODEL ARCHITECTURE & SIGNAL LEGEND

 [ENCODER] Models / indexes / classifiers
   ► 🔵 intent_vec  = live ask, route intent, step-specific search query, task support target
   ► 🟠 fact_vec    = stored source chunk, indexed fact, cache embedding, citation-bearing evidence span
   ► 🟢 graph_sig   = lineage, dependency, ACL, citation, contradiction, supersession, workflow relation

 [DECODER] Models / planners / generators / judges
   ► 🔶 gen_text    = natural language, plan text, route reasoning, tool-call proposal, answer, evaluation judgment

 [CONTROL / EVIDENCE]
   ► ★ GateVerdict  = current-run proceed/stop verdict from 00C Runtime Gates
   ► 🧾 receipt     = replayable proof artifact
   ► [RET]          = terminal short-circuit packet sent to Exit
   ► [CONTRACT]     = mandatory handoff packet between spine stages
 ----------------------------------------------------------------------------------------------------------------------
========================================================================================================================


[ 00A / L5 POLICY + GOVERNANCE CERTIFICATION PLANE ] ──────────────────────────────────────────────────────────────────
 │ Cross-cutting evidence plane, not a sequential runtime step.
 │
 │ Certifies evidence for:
 │ authority | policy | registry | origin trust | instruction/data boundary | capability | sandbox | egress | HITL | replay/audit
 │
 │ Provides certification refs consumed by U0, L1, L0, C0, PA, L3, L2, Exit, UWG, L4, and L6.
 │
 │ Does NOT:
 │ route | retrieve | assemble prompts | execute | emit live GateVerdict | emit final X3 | write L4 | learn
 ▼


[ 00C / RUNTIME GATES CURRENT-RUN CONTROL MESH ] ─────────────────────────────────────────────────────────────────────
 │ Cross-cutting live control mesh, not a sequential runtime step.
 │
 │ Asks:
 │ "May this current live packet, route, retrieval packet, prompt packet, workflow step, tool call, model call,
 │  output, escalation, or write proposal proceed right now?"
 │
 │ Emits:
 │ GateVerdict with bounded recommendation. UNKNOWN is never PASS.
 │
 │ Does NOT:
 │ route | retrieve | assemble prompts | execute | emit final X3 | certify L5 evidence | write L4 | learn
 ▼


┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. U0 REQUEST INTAKE                                                            [ENCODER] auth/schema/origin classify │
│                                                                                                                      │
│ PURPOSE                                                                                                             │
│ "Is this inbound request structurally valid, attributable, bounded, quota-safe, traceable, and safe to hand to L1?"  │
│                                                                                                                      │
│ SUBSTEPS                                                                                                            │
│ U0.1 Transport / envelope / channel validation                                                                       │
│      - accept raw ingress envelope                                                                                   │
│      - validate channel, payload shape, size, malformed schema, duplicate request                                    │
│                                                                                                                      │
│ U0.2 Identity / tenant / session / quota baseline                                                                    │
│      - bind caller, tenant, session, quota, request_id, trace_root                                                   │
│                                                                                                                      │
│ U0.3 Schema normalization / idempotency                                                                              │
│      - normalize payload                                                                                            │
│      - compute request digest                                                                                        │
│      - preserve original payload lineage                                                                             │
│                                                                                                                      │
│ U0.4 Origin trust / injection triage / data labeling                                                                 │
│      - initial origin labels                                                                                         │
│      - obvious instruction smuggling triage                                                                          │
│      - user text marked as intent, not authority                                                                     │
│                                                                                                                      │
│ U0.5 ValidatedRequest / RejectedRequest handoff                                                                      │
│      - emit structurally admissible request or fail-closed rejection                                                 │
│                                                                                                                      │
│ SIGNALS                                                                                                             │
│ 🔵 intent_vec: not generated here. U0 does not perform semantic routing.                                             │
│ 🟠 fact_vec: not used here except static classification references.                                                   │
│ 🟢 graph_sig: not used here except trace_root lineage seed.                                                          │
│ 🔶 gen_text: not used here.                                                                                          │
│                                                                                                                      │
│ INPUT                                                                                                                │
│ raw request                                                                                                          │
│                                                                                                                      │
│ OUTPUT                                                                                                               │
│ [CONTRACT] ValidatedRequest or RejectedRequest                                                                       │
│ 🧾 intake_receipt | request_digest | origin_label_seed | trace_root                                                  │
│                                                                                                                      │
│ MAY                                                                                                                  │
│ validate envelope | stamp identity | normalize payload | label origin | emit L1 handoff                              │
│                                                                                                                      │
│ MUST NOT                                                                                                             │
│ reason | route | retrieve | assemble prompts | call models | call tools | execute | write L4                         │
│                                                                                                                      │
│ ★ Runtime Gates                                                                                                      │
│ G01 ingress | G02 identity | G03 intent triage | G04 safety precheck | G05 risk baseline                             │
└──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────┘
                                               │ [CONTRACT] ValidatedRequest
                                               ▼

████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██ ◄─────────────────────────────────────────────── R U N T I M E   B E G I N S ─────────────────────────────────────► ██
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
                                               │
                                               ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────┐        ┌───────────────┐
│ 2. L1 REASONING + PLAN GENERATION                                    [ENCODER] 🔵 intent_vec │───────►│ L4 READ       │
│                                                                     [DECODER] 🔶 gen_text    │        │ planning      │
│ PURPOSE                                                                                      │◄───────│ priors only   │
│ "What is the user trying to accomplish, what is ambiguous, and what bounded plan should L0    │        └───────────────┘
│  consider without giving L1 route authority?"                                                 │
│                                                                                              │
│ SUBSTEPS                                                                                     │
│ L1.1 Intent frame and ambiguity register                                                      │
│      - parse goal, deliverable, constraints, assumptions, missing inputs                      │
│      - separate user intent from policy or authority claims                                   │
│      - produce ambiguity register                                                            │
│                                                                                              │
│ L1.2 Planning priors and rule bundle                                                          │
│      - read approved L4 planning references only                                              │
│      - load approved examples, rubrics, planning rules, policy refs                           │
│      - no final evidence retrieval                                                           │
│                                                                                              │
│ L1.3 Contextual refinement loop                                                               │
│      - planning-only refinement                                                              │
│      - improve task decomposition and support expectations                                    │
│      - no hidden current-run mutation                                                        │
│                                                                                              │
│ L1.4 Draft plan and route hints                                                               │
│      - work units                                                                            │
│      - dependency sketch                                                                      │
│      - grounding need marker                                                                  │
│      - action need marker                                                                     │
│      - HITL hint                                                                              │
│      - route hints only, not route decision                                                   │
│                                                                                              │
│ L1.5 Plan validation and self-repair                                                          │
│      - plan consistency audit                                                                 │
│      - lowest viable agency check                                                            │
│      - bounded repair of the plan only                                                        │
│                                                                                              │
│ L1.6 L1PlanContract handoff                                                                   │
│      - freeze plan                                                                            │
│      - emit digest, telemetry keys, non-authority assertion                                   │
│                                                                                              │
│ SIGNALS                                                                                      │
│ 🔵 intent_vec: used to represent the live user ask and planning support target.                │
│ 🟠 fact_vec: not used for final evidence. May reference approved L4 planning examples only.    │
│ 🟢 graph_sig: optional dependency sketch only, not retrieval graph expansion.                  │
│ 🔶 gen_text: used to draft and validate the plan contract.                                    │
│                                                                                              │
│ INPUT                                                                                         │
│ [CONTRACT] ValidatedRequest                                                                   │
│                                                                                              │
│ OUTPUT                                                                                        │
│ [CONTRACT] L1PlanContract                                                                     │
│ 🧾 plan_digest | ambiguity_register | support_expectation | action_expectation | route_hints   │
│                                                                                              │
│ MAY                                                                                           │
│ interpret intent | frame ambiguity | read approved planning priors | recommend bounded plan    │
│                                                                                              │
│ MUST NOT                                                                                      │
│ route with authority | retrieve final evidence | assemble prompts | execute | approve egress   │
│ write L4 | learn into current run                                                             │
│                                                                                              │
│ ★ Runtime Gates                                                                               │
│ intent clarity | authority separation | planning budget | L4 planning-prior read eligibility   │
└───────┬──────────────────────────────────────────────────────────────────────────────────────┘
        │ [CONTRACT] L1PlanContract
        ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. L0 ROUTE DECISION                                                                 [DECODER] 🔶 route decision text │
│                                                                                                                      │
│ PURPOSE                                                                                                             │
│ "Which one deterministic route should this request take?"                                                           │
│                                                                                                                      │
│ SUBSTEPS                                                                                                            │
│ L0.1 Route input preflight                                                                                           │
│      - consume L1PlanContract                                                                                        │
│      - bind policy_hash, blueprint_hash, registry_digest_set, trace_root                                             │
│      - normalize route-ready facts                                                                                   │
│                                                                                                                      │
│ L0.2 Deterministic route selection                                                                                   │
│      - fixed route order                                                                                             │
│      - cheapest safe route wins                                                                                      │
│      - no opportunistic model/tool execution                                                                         │
│                                                                                                                      │
│ L0.3 Cache / fallback / HITL posture                                                                                 │
│      - check R1A exact cache eligibility                                                                              │
│      - check R1B semantic cache eligibility with 🔵 request intent vs 🟠 cache embedding compatibility                 │
│      - check R5 fallback posture                                                                                     │
│      - mark HITL posture as guard annotation only                                                                     │
│                                                                                                                      │
│ L0.4 Grounded and action handoff shaping                                                                             │
│      - R3 simple grounded read handoff                                                                               │
│      - R4 single bounded action handoff                                                                              │
│      - R3+R4 action-argument grounding shape                                                                         │
│                                                                                                                      │
│ L0.5 Managed workflow eligibility                                                                                    │
│      - if dependencies, joins, resumability, staged evidence, or bounded quality loops are required                   │
│      - execution_form = MANAGED_WORKFLOW                                                                             │
│      - otherwise execution_form = SINGLE_STEP or TERMINAL_SHORTCIRCUIT                                               │
│                                                                                                                      │
│ L0.6 RouteContract emission                                                                                          │
│      - exactly one RouteContract                                                                                     │
│      - route_digest, manifest_hash, hmac_sig, replay-bound route invariants                                          │
│                                                                                                                      │
│ SIGNALS                                                                                                             │
│ 🔵 intent_vec: route intent and cache query comparison.                                                               │
│ 🟠 fact_vec: cache entries and route-support references only.                                                         │
│ 🟢 graph_sig: workflow dependency hint only, not graph retrieval.                                                     │
│ 🔶 gen_text: route explanation or route selection rationale, if decoder-assisted.                                     │
│                                                                                                                      │
│ OUTPUT ROUTE BRANCHES                                                                                                │
│                                                                                                                      │
│   R1A_EXACT_CACHE          ───────────────► [RET exact cache packet] ───────────────► Exit                            │
│   R1B_SEMANTIC_CACHE       ───────────────► [RET semantic cache packet] ───────────► Exit                            │
│   R5_FALLBACK              ───────────────► [RET fallback / abstain packet] ───────► Exit                            │
│                                                                                                                      │
│   R3_SIMPLE_GROUNDED_READ  ───────────────► C0 Context Engine ─► PA ─► L2 ─────────► Exit                            │
│   R4_SINGLE_ACTION         ───────────────► L2, with C0/PA only if route requires ─► Exit                            │
│   R3R4_MANAGED_WORKFLOW    ───────────────► L3 Orchestration ─► L2 step loop ──────► Exit                            │
│                                                                                                                      │
│ INPUT                                                                                                                │
│ [CONTRACT] L1PlanContract                                                                                            │
│                                                                                                                      │
│ OUTPUT                                                                                                               │
│ [CONTRACT] RouteContract or [RET] terminal packet                                                                    │
│ 🧾 route_digest | route_telemetry | route_replay_receipt                                                             │
│                                                                                                                      │
│ MAY                                                                                                                  │
│ select one route | choose execution_form | attach HITL posture | hand off to C0, L2, L3, or Exit                     │
│                                                                                                                      │
│ MUST NOT                                                                                                             │
│ retrieve | assemble prompts | execute | call tools | call models | mutate state | approve output | write L4 | learn   │
│                                                                                                                      │
│ ★ Runtime Gates                                                                                                      │
│ G07 route authority | route determinism | cache compatibility | risk/HITL posture                                    │
└───────┬─────────────────────────────┬─────────────────────────────┬──────────────────────────────────────────────────┘
        │                             │                             │
        │ [RET terminal packet]        │ [R3 grounding required]      │ [R4 single action or R3R4 workflow]
        │                             │                             │
        ▼                             ▼                             ▼

┌──────────────────────────────┐      ┌──────────────────────────────────────────────────────────────────────────────┐
│ [RET] TERMINAL SHORT-CIRCUIT │      │ 3C. C0 CONTEXT ENGINEERING / GROUNDING                                       │
│                              │      │                                 [ENCODER] 🔵 intent_vec vs 🟠 fact_vec         │
│ exact cache                  │      │                                 [ENCODER] 🟢 graph_sig when graph enabled     │
│ semantic cache               │      │                                                                              │
│ fallback / abstain           │      │ PURPOSE                                                                      │
│                              │      │ "What evidence is allowed, relevant, fresh, cited, contradiction-aware,      │
│ Goes directly to Exit.        │      │  and strong enough to pack?"                                                 │
│                              │      │                                                                              │
│ No C0, PA, L3, or L2 unless   │      │ SUBSTEPS                                                                     │
│ Exit reroutes.               │      │ C0.0 Preflight                                                               │
└──────────────┬───────────────┘      │      - route grants grounding                                                │
               │                      │      - support target                                                        │
               │                      │      - ACL, source scope, freshness, origin trust, budget                    │
               │                      │                                                                              │
               │                      │ C0.1 Retrieval plan                                                          │
               │                      │      - 🔵 dense query_vec / intent vector                                     │
               │                      │      - 🟠 sparse/BM25, metadata, cache, source classes                        │
               │                      │      - 🟢 graph_seed if route permits graph expansion                         │
               │                      │                                                                              │
               │                      │ C0.2 Evidence fetch                                                          │
               │                      │      - 🔵 query searches dense index                                          │
               │                      │      - 🟠 fact vectors return nearest-neighbor candidates                     │
               │                      │      - 🟠 BM25 and metadata filters return lexical/structured candidates       │
               │                      │      - hydrate source_id, version, span, ACL, lineage, citation anchors       │
               │                      │                                                                              │
               │                      │ C0.3 Graph RAG, if enabled                                                    │
               │                      │      - 🟢 lineage, owners, dependencies, contradictions, supersession          │
               │                      │      - graph expansion is bounded by route and ACL                            │
               │                      │                                                                              │
               │                      │ C0.4 Shape / rerank / stratify                                                │
               │                      │      - 🔵 relevance to live intent/support target                              │
               │                      │      - 🟠 dense score, BM25 score, metadata fit, freshness                     │
               │                      │      - 🟢 graph proximity, lineage strength, contradiction relation            │
               │                      │      - strata: MUST_USE, SUPPORTING, CONTRADICTS, BACKGROUND, EXCLUDED        │
               │                      │                                                                              │
               │                      │ C0.5 FinalEvidenceContract                                                    │
               │                      │      - verify citations, freshness, authority, ACL, contradiction status       │
               │                      │      - status: PASS, WEAK_WITH_CAVEATS, CONFLICTED, EMPTY, BLOCKED            │
               │                      │                                                                              │
               │                      │ C0.6 Weak support refinement, if budget permits                               │
               │                      │      - broaden, decompose, or retry once                                      │
               │                      │      - no answer and no route change                                          │
               │                      │                                                                              │
               │                      │ INPUT                                                                        │
               │                      │ [CONTRACT] RouteContract with grounding_required = true                       │
               │                      │                                                                              │
               │                      │ OUTPUT                                                                       │
               │                      │ [CONTRACT] FinalEvidenceContract                                             │
               │                      │ 🧾 evidence_receipt | citation_map | contradiction_report | support_status    │
               │                      │                                                                              │
               │                      │ MAY                                                                          │
               │                      │ retrieve | hydrate | score | stratify | verify evidence                       │
               │                      │                                                                              │
               │                      │ MUST NOT                                                                     │
               │                      │ answer | route | assemble prompts | execute | write L4 | inflate support       │
               │                      │                                                                              │
               │                      │ ★ Runtime Gates                                                              │
               │                      │ G08 retrieval legality | G09 evidence quality | ACL | freshness              │
               │                      └──────────────┬───────────────────────────────────────────────────────────────┘
               │                                     │ [CONTRACT] FinalEvidenceContract
               │                                     ▼
               │                      ┌──────────────────────────────────────────────────────────────────────────────┐
               │                      │ 3D. PROMPT ASSEMBLY                                                         │
               │                      │                                   [DECODER] 🔶 provider-ready packet         │
               │                      │                                   [ENCODER] 🟠 C0 evidence refs as data       │
               │                      │                                                                            │
               │                      │ PURPOSE                                                                    │
               │                      │ "Can governed inputs be packed into authority-ordered prompt slots without  │
               │                      │  lower-authority content becoming instructions?"                           │
               │                      │                                                                            │
               │                      │ SUBSTEPS                                                                   │
               │                      │ PA.0 Boundary check                                                         │
               │                      │      - L1 exists                                                            │
               │                      │      - L0 exists                                                            │
               │                      │      - C0 exists when grounding_required = true                              │
               │                      │      - provider lane, response schema, policy_hash, replay_key bound         │
               │                      │                                                                            │
               │                      │ PA.1 Load / resolve Prompt BOM                                              │
               │                      │      - S0 system                                                            │
               │                      │      - D0 fences                                                            │
               │                      │      - I0 instructions                                                       │
               │                      │      - E0 approved examples                                                  │
               │                      │      - C0 verified evidence refs 🟠                                           │
               │                      │      - M0 provider-safe controls                                             │
               │                      │      - U0 neutralized user task                                              │
               │                      │      - H0 bounded repair hints                                               │
               │                      │      - R0 response schema                                                    │
               │                      │                                                                            │
               │                      │ PA.2 Slot composition                                                       │
               │                      │      - canonical order: S0 -> D0 -> I0 -> E0 -> C0 -> M0 -> U0 -> H0         │
               │                      │      - R0 bound as schema, not loose prose                                   │
               │                      │                                                                            │
               │                      │ PA.3 Airlock / security pass                                                │
               │                      │      - user text remains intent                                              │
               │                      │      - retrieved text remains evidence data 🟠                                │
               │                      │      - tool and human text remain data until cleared                         │
               │                      │      - no instruction smuggling                                              │
               │                      │                                                                            │
               │                      │ PA.4 Validate slot contract                                                 │
               │                      │      - authority order                                                       │
               │                      │      - citations and lineage preserved                                       │
               │                      │      - schema and tool bindings intact                                       │
               │                      │      - C0 support status not inflated                                        │
               │                      │                                                                            │
               │                      │ PA.5 Token budget / determinism                                             │
               │                      │      - preserve S0, D0, I0, R0, must-use C0 evidence first                   │
               │                      │      - deterministic trim only optional payloads                             │
               │                      │                                                                            │
               │                      │ PA.6 Provider-aware rendering                                               │
               │                      │      - map slots to provider fields without semantic drift                    │
               │                      │      - same canonical slots, provider-specific render                         │
               │                      │                                                                            │
               │                      │ PA.7 Sign compiled prompt artifact                                          │
               │                      │      - prompt_hash                                                           │
               │                      │      - component_hash_map                                                    │
               │                      │      - provider render manifest                                              │
               │                      │      - replay manifest                                                       │
               │                      │                                                                            │
               │                      │ SIGNALS                                                                    │
               │                      │ 🔵 intent_vec: user task support target carried from L1/L0, not recomputed.   │
               │                      │ 🟠 fact_vec: verified evidence enters C0 slot as data only.                   │
               │                      │ 🟢 graph_sig: lineage/citation/contradiction refs carried as data only.       │
               │                      │ 🔶 gen_text: provider-ready prompt rendering, not final answer.              │
               │                      │                                                                            │
               │                      │ INPUT                                                                      │
               │                      │ L1PlanContract | RouteContract | FinalEvidenceContract | L5 refs | schema   │
               │                      │                                                                            │
               │                      │ OUTPUT                                                                     │
               │                      │ [CONTRACT] PromptEnvelope / CompiledPromptArtifact                          │
               │                      │ 🧾 prompt_hash | slot_lineage_map | assembly_security_receipt                │
               │                      │                                                                            │
               │                      │ MAY                                                                        │
               │                      │ compose | render | hash | sign | package                                    │
               │                      │                                                                            │
               │                      │ MUST NOT                                                                   │
               │                      │ retrieve | route | execute | approve L2 execution | write L4                 │
               │                      │                                                                            │
               │                      │ ★ Runtime Gates                                                            │
               │                      │ G10 prompt boundary | instruction/data boundary | provider rendering         │
               │                      └──────────────┬───────────────────────────────────────────────────────────────┘
               │                                     │ [CONTRACT] CompiledPromptArtifact
               │                                     ▼
               │
               │
               ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 3B. L3 ORCHESTRATION, OPTIONAL                                                       [DECODER] 🔶 workflow sequence │
│                                                                                      [ENCODER] 🟢 dependency graph   │
│ PURPOSE                                                                                                             │
│ "If L0 selected MANAGED_WORKFLOW, how is the approved route expanded into bounded executable steps?"                 │
│                                                                                                                      │
│ RUNS ONLY WHEN                                                                                                       │
│ RouteContract.execution_form = MANAGED_WORKFLOW                                                                      │
│                                                                                                                      │
│ SUBSTEPS                                                                                                            │
│ L3.1 Managed workflow eligibility and DAG                                                                            │
│      - consume already-selected RouteContract                                                                         │
│      - classify execution shape                                                                                      │
│      - build bounded DAG / HTN / AST runner                                                                           │
│      - 🟢 dependency graph, branch/join state, checkpoint structure                                                   │
│                                                                                                                      │
│ L3.2 Step readiness state ledger and context bus                                                                      │
│      - ready-node selection                                                                                          │
│      - workflow ledger                                                                                                │
│      - checkpoint refs                                                                                                │
│      - carry C0 evidence refs and graph refs as data only                                                             │
│                                                                                                                      │
│ L3.3 L3ToL2StepContract handoff                                                                                      │
│      - package current bounded step                                                                                  │
│      - bind route_id, workflow_id, node_id, capability, sandbox, policy, blueprint, replay                            │
│      - mark whether step is PTC-capable, but do not execute PTC                                                       │
│                                                                                                                      │
│ L3.4 Concurrency / quality / fallback / completion                                                                    │
│      - fan-out and join only where approved                                                                           │
│      - bounded quality loops                                                                                         │
│      - fallback controller                                                                                            │
│      - completion and sealed workflow package                                                                         │
│                                                                                                                      │
│ SIGNALS                                                                                                             │
│ 🔵 intent_vec: carried support target only.                                                                           │
│ 🟠 fact_vec: evidence refs carried only if supplied by C0.                                                            │
│ 🟢 graph_sig: workflow dependency and join structure.                                                                 │
│ 🔶 gen_text: sequence explanation or workflow packaging, if decoder-assisted.                                         │
│                                                                                                                      │
│ INPUT                                                                                                                │
│ [CONTRACT] RouteContract with MANAGED_WORKFLOW                                                                        │
│                                                                                                                      │
│ OUTPUT                                                                                                               │
│ [CONTRACT] L3ToL2StepContract for current ready node                                                                  │
│ 🧾 workflow_ledger | checkpoint_ref | branch_join_state | step_handoff_receipt                                        │
│                                                                                                                      │
│ MAY                                                                                                                  │
│ sequence | checkpoint | resume | package bounded steps | merge sealed step artifacts                                  │
│                                                                                                                      │
│ MUST NOT                                                                                                             │
│ re-route | retrieve directly | assemble prompts | execute tools/models/PTC | approve output | write L4 | learn        │
│                                                                                                                      │
│ ★ Runtime Gates                                                                                                      │
│ G18 workflow trajectory | G19 loop/retry/thrash | workflow budget                                                     │
└───────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
            │ [CONTRACT] current bounded step
            ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. L2 EXECUTE                                                                       [DECODER] 🔶 model/tool/action    │
│                                                                                                                       │
│ PURPOSE                                                                                                               │
│ "Perform exactly the current bounded packet, repair only safe local defects, and seal the result."                    │
│                                                                                                                       │
│ ENTRY SHAPES                                                                                                          │
│ - SINGLE_STEP from L0                                                                                                 │
│ - current L3 step from managed workflow                                                                               │
│ - model packet from Prompt Assembly                                                                                   │
│ - action/tool packet from RouteContract or L3ToL2StepContract                                                         │
│                                                                                                                       │
│ CORE EXECUTION                                                                                                        │
│                                                                                                                       │
│  ┌────────┐   ┌─────────┐   ┌────────────────────────────────────────┐   ┌────────┐   ┌────────┐                     │
│  │E1 Prep │──►│E2 Valid │──►│E3 Exec, optional PTC inside this box    │──►│E4 Heal │──►│E5 Seal │                     │
│  └────────┘   └─────────┘   └────────────────────▲───────────────────┘   └───┬────┘   └────────┘                     │
│                                                  │                           │                                         │
│                                                  └──────── retry ◄──────────┘                                         │
│                                                                                                                       │
│ E1 PREP - frozen execution room                                                                                      │
│ - receive signed packet                                                                                               │
│ - bind route, step, capability_token, sandbox_envelope, policy_hash, blueprint_hash                                    │
│ - freeze registry, provider lane, filesystem, network, secrets, locale, budget                                         │
│ - bind replay_key, attempt_seed, snapshot_manifest, idempotency                                                       │
│ - assert no direct write path to L4                                                                                    │
│ - emit frozen_execution_context                                                                                       │
│                                                                                                                       │
│ E2 VALID - work order check                                                                                           │
│ - validate signature chain                                                                                            │
│ - validate capability scope                                                                                           │
│ - validate sandbox envelope                                                                                           │
│ - validate schema shape, side-effect class, budget, safety sanity                                                     │
│ - validate executability without humans, reroute, or replanning                                                       │
│ - fail closed as sealed_rejection_packet before execution when required                                                │
│                                                                                                                       │
│ E3 EXEC - one bounded attempt, optional PTC mode lives here                                                            │
│ - open attempt with trace_id, span_id, attempt_seed, counters                                                          │
│ - build invocation from sealed packet only                                                                             │
│ - run exactly one approved execution lane                                                                              │
│                                                                                                                       │
│   E3 lanes:                                                                                                           │
│   - READ_ANALYSIS lane                                                                                                │
│     uses 🔶 gen_text for bounded analysis over supplied packet or evidence refs                                        │
│                                                                                                                       │
│   - MODEL lane                                                                                                        │
│     uses 🔶 gen_text from approved provider through governed gateway                                                   │
│     uses 🟠 C0 evidence only when supplied through PromptEnvelope                                                       │
│                                                                                                                       │
│   - TOOL lane                                                                                                         │
│     executes one approved tool call with sealed args                                                                   │
│                                                                                                                       │
│   - ACTION lane                                                                                                       │
│     performs one approved side-effect-bounded action                                                                   │
│                                                                                                                       │
│   - ARTIFACT lane                                                                                                     │
│     creates or transforms bounded artifact output                                                                      │
│                                                                                                                       │
│   - OPTIONAL PTC sandbox lane                                                                                         │
│     Programmatic Tool Calling is an E3 execution mode, not a separate spine stage.                                     │
│     PTC may execute model-driven tool sequences only inside the frozen L2 room.                                        │
│     PTC uses the same capability_token, sandbox_envelope, policy_hash, blueprint_hash, replay_key, and budget.         │
│     PTC denies ambient tools, hidden parameters, unapproved retrieval, authority expansion, and direct L4 writes.       │
│     PTC emits deterministic invocation logs and cross-tool coordination receipts.                                      │
│                                                                                                                       │
│ - capture telemetry: latency, tokens, cost, compute, memory, stdout/stderr, return code, errors                       │
│ - capture output: payload, raw tool result, structured model output, generated files, artifacts                        │
│ - capture proposed_state_diff only, never durable state                                                                │
│ - classify result: SUCCESS | DEGRADED_SUCCESS | SOFT_REPAIRABLE | FAIL_TERMINAL | NEEDS_HELP | REJECTED               │
│                                                                                                                       │
│ E4 HEAL - same-authority repair governor                                                                               │
│ - localize failure                                                                                                     │
│ - allowed repairs: JSON/schema repair, output reformat, transient retry, checkpoint resume, deterministic trim         │
│ - disallowed repairs: missing authority, blocked ACL, policy conflict, route mismatch, stale policy, HITL need         │
│ - preserve same policy_hash, blueprint_hash, capability, sandbox, prompt_hash, replay_key, source snapshot             │
│ - enforce oscillation guard and repair budget                                                                          │
│                                                                                                                       │
│ E5 SEAL - sealed artifact and dispatch                                                                                 │
│ - package payload, evidence, traces, replay, counters, hashes, artifacts                                               │
│ - package proposed_state_diff as inert mutation candidate only                                                         │
│ - stamp terminal_class and decisive reason                                                                             │
│ - assert no durable commit occurred                                                                                    │
│ - dispatch to Exit or back to L3 merge if managed workflow has more nodes                                              │
│                                                                                                                       │
│ SIGNALS                                                                                                              │
│ 🔵 intent_vec: carried from L1/L0 for task alignment only.                                                             │
│ 🟠 fact_vec: evidence refs may be consumed if supplied by C0/PA, never newly retrieved unless explicitly authorized.   │
│ 🟢 graph_sig: workflow/citation lineage carried for traceability only.                                                 │
│ 🔶 gen_text: model/tool-call proposal, answer generation, local critique, or E3 execution output.                     │
│                                                                                                                       │
│ INPUT                                                                                                                 │
│ RouteContract or L3ToL2StepContract | PromptEnvelope if model execution required | C0 refs if grounded                 │
│                                                                                                                       │
│ OUTPUT                                                                                                                │
│ [CONTRACT] SealedL2Artifact or sealed workflow step artifact                                                           │
│ 🧾 prep_receipt | validation_receipt | attempt_receipt | optional_ptc_receipt | heal_receipt | seal_receipt            │
│                                                                                                                       │
│ MAY                                                                                                                   │
│ execute bounded work | call approved model/tool/action | run optional PTC sandbox | emit proposed_state_diff           │
│                                                                                                                       │
│ MUST NOT                                                                                                              │
│ choose route | expand workflow | retrieve opportunistically | ask humans directly | approve egress | commit L4 | learn  │
│                                                                                                                       │
│ ★ Runtime Gates                                                                                                       │
│ G11 tool/model registry | G12 args | G13 tool/retrieved output trust | G15 sandbox | G19 retry | G20 budget            │
└───────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
            │
            ├──────── if managed workflow still has ready nodes ───────► L3 merge and next L3ToL2StepContract
            │
            │ [CONTRACT] SealedL2Artifact or sealed workflow package
            ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. EXIT EVALUATION + CONTROL                                            [DECODER] 🔶 output grade / disposition      │
│                                                                         [ENCODER] 🔵 intent_vec vs 🟠 fact_vec        │
│                                                                         [ENCODER] 🟢 lineage/replay/audit graph       │
│ PURPOSE                                                                                                              │
│ "Can this sealed result leave, be denied, be rerouted, be escalated, safely abstained, or request a durable commit?" │
│                                                                                                                       │
│ INPUT SOURCES                                                                                                         │
│ - [RET] exact cache packet from L0                                                                                    │
│ - [RET] semantic cache packet from L0 with 🔵 request intent vs 🟠 cache/evidence compatibility                         │
│ - [RET] fallback / abstain packet from L0                                                                             │
│ - SealedL2Artifact from single-step execution                                                                          │
│ - sealed workflow package from L3/L2 loop                                                                              │
│ - re-cleared HITL packet                                                                                              │
│                                                                                                                       │
│ SUBSTEPS                                                                                                             │
│ 5.1 Input normalization and ExitReviewPacket                                                                          │
│      - classify source type                                                                                            │
│      - normalize lineage without flattening it                                                                         │
│      - bind run_id, request_id, trace_root, policy_hash, blueprint_hash, replay_key                                    │
│      - attach C0, PA, L2, L3, L5, 00C, and telemetry refs as available                                                │
│                                                                                                                       │
│ 5.2 X1A-X1F current-run checkout checks                                                                               │
│      - X1A Today's Rules: policy manifest, threshold, grader roster                                                    │
│      - X1B Answered It: task completion, format, instruction following                                                 │
│      - X1C Safe to Leave: sandbox, mutation authority, side effect, egress                                             │
│      - X1D Answer Good: groundedness, faithfulness, citation, support using 🔵 intent vs 🟠 evidence                    │
│      - X1E Trajectory OK: process quality, tool choice, retry, handoff                                                 │
│      - X1F Story Adds Up: internal consistency, cross-step coherence                                                   │
│                                                                                                                       │
│ 5.3 X1G-X1I replay / observability / consistency                                                                       │
│      - X1G Replay Eligible: replay guard and idempotency                                                               │
│      - X1H Observable: OTEL span tree and counter completeness                                                         │
│      - X1I Consistency Across Runs: pass^k, variance, drift if activated                                               │
│                                                                                                                       │
│ 5.4 X1J write eligibility and UWG handoff                                                                              │
│      - proposed_state_diff completeness                                                                                │
│      - CommitRequest candidate readiness                                                                               │
│      - no direct write bypass                                                                                          │
│                                                                                                                       │
│ 5.5 X2 aggregation and X3 disposition                                                                                  │
│      - aggregate X1 verdicts under policy weights                                                                      │
│      - UNKNOWN is never treated as PASS                                                                                │
│      - emit exactly one X3 outcome                                                                                     │
│                                                                                                                       │
│ 5.6 HITL freeze / review / re-clearance                                                                                │
│      - freeze risky work                                                                                               │
│      - human input remains data                                                                                        │
│      - L5 re-clearance required before re-entry                                                                        │
│                                                                                                                       │
│ 5.7 Return response and runtime exhaust                                                                                │
│      - user-visible response or safe bounded non-answer                                                                 │
│      - sealed runtime exhaust bundle                                                                                   │
│      - L6 handoff only after current-run boundary                                                                      │
│                                                                                                                       │
│ X3 DISPOSITION PATHS                                                                                                  │
│                                                                                                                       │
│   X3A DENY / REROUTE              ─────► bounded denial or route re-entry packet                                      │
│   X3B ESCALATE_HITL               ─────► freeze packet -> human review -> L5 re-clearance -> Exit re-entry             │
│   X3C COMMIT_REQUEST_TO_UWG       ─────► UWG durable write validation                                                  │
│   X3D ALLOW / FINISH              ─────► user-visible final response                                                   │
│   X3E SAFE_ABSTAIN                ─────► safe bounded abstain response                                                 │
│                                                                                                                       │
│ SIGNALS                                                                                                              │
│ 🔵 intent_vec: task completion and support target comparison.                                                          │
│ 🟠 fact_vec: evidence, citations, cache records, source spans, support facts.                                          │
│ 🟢 graph_sig: lineage, replay, contradiction, workflow, audit, dependency consistency.                                 │
│ 🔶 gen_text: grader rationale, user-visible response, disposition explanation when needed.                            │
│                                                                                                                       │
│ INPUT                                                                                                                 │
│ [RET] packet | SealedL2Artifact | sealed workflow package | re-cleared HITL packet                                     │
│                                                                                                                       │
│ OUTPUT                                                                                                                │
│ [CONTRACT] ExitDispositionReceipt with exactly one X3                                                                  │
│ optional [CONTRACT] CommitRequest to UWG                                                                               │
│ [CONTRACT] RuntimeExhaustBundle after runtime boundary                                                                 │
│                                                                                                                       │
│ MAY                                                                                                                   │
│ allow finish | deny | reroute | escalate HITL | safe abstain | request UWG commit                                      │
│                                                                                                                       │
│ MUST NOT                                                                                                              │
│ execute | retrieve | assemble prompts | mutate L4 | let L6 rescue current run                                          │
│                                                                                                                       │
│ ★ Runtime Gates                                                                                                       │
│ G21 output schema | G22 quality | G23 leakage | G24 replay | G26 Exit eligibility | G27 write sovereignty             │
└───────────┬───────────────────────────────┬───────────────────────────────┬─────────────────────────────────────────┘
            │                               │                               │
            │ X3D ALLOW / FINISH            │ X3A / X3B / X3E                │ X3C COMMIT_REQUEST_TO_UWG
            ▼                               ▼                               ▼

┌──────────────────────────────┐   ┌──────────────────────────────────┐   ┌───────────────────────────────────────────┐
│ USER RESPONSE RETURN          │   │ DENY / REROUTE / HITL / ABSTAIN  │   │ UWG UNIVERSAL WRITE GATE                  │
│                               │   │                                  │   │                                           │
│ final visible answer/artifact │   │ bounded current-run outcome       │   │ PURPOSE                                   │
│ or safe bounded response      │   │ no durable write unless UWG path   │   │ "Is this CommitRequest allowed to mutate │
│                               │   │                                  │   │  durable L4 state?"                       │
└──────────────┬───────────────┘   └──────────────┬───────────────────┘   │                                           │
               │                                  │                       │ SUBSTEPS                                  │
               │                                  │                       │ UWG.1 Validate CommitRequest              │
               │                                  │                       │ UWG.2 Validate StateDiff                  │
               │                                  │                       │ UWG.3 Check schema, policy, replay, audit │
               │                                  │                       │ UWG.4 Acquire write lock                  │
               │                                  │                       │ UWG.5 Atomic commit or blocked receipt    │
               │                                  │                       │ UWG.6 Refresh read surfaces               │
               │                                  │                       │ UWG.7 Append audit ledger                 │
               │                                  │                       │                                           │
               │                                  │                       │ SIGNALS                                   │
               │                                  │                       │ 🔵 intent_vec: not used for write truth.   │
               │                                  │                       │ 🟠 fact_vec: committed refs and state diff.│
               │                                  │                       │ 🟢 graph_sig: audit, lineage, dependency. │
               │                                  │                       │ 🔶 gen_text: not used for write authority. │
               │                                  │                       │                                           │
               │                                  │                       │ MAY                                       │
               │                                  │                       │ commit durable state after validation      │
               │                                  │                       │                                           │
               │                                  │                       │ MUST NOT                                  │
               │                                  │                       │ execute PTC/tools | route | retrieve      │
               │                                  │                       │ approve final answer | learn              │
               │                                  │                       │                                           │
               │                                  │                       │ ★ Runtime Gate                            │
               │                                  │                       │ G27 durable-write sovereignty              │
               │                                  │                       └──────────────┬────────────────────────────┘
               │                                  │                                      │
               │                                  │                                      ▼
               │                                  │                       ┌───────────────────────────────────────────┐
               │                                  │                       │ L4 ARCHIVE                                │
               │                                  │                       │ durable truth and versioned read surfaces │
               │                                  │                       │                                           │
               │                                  │                       │ Stores after UWG only:                    │
               │                                  │                       │ policy | blueprint | registry | memory    │
               │                                  │                       │ cache | retrieval surfaces | replay       │
               │                                  │                       │ audit | committed state                    │
               │                                  │                       └──────────────┬────────────────────────────┘
               │                                  │                                      │
               └──────────────────┬───────────────┴──────────────────────────────────────┘
                                  │ [CONTRACT] RuntimeExhaustBundle after current-run boundary
                                  ▼

████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██ ◄────────────────────────────────────────────── C U R R E N T   R U N   B O U N D A R Y ─────────────────────────► ██
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
                                  │
                                  ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 6. L6 SHADOW EVALUATION + SYSTEM LEARNING                              [DECODER] 🔶 RCA / proposal / eval judgment   │
│                                                                        [ENCODER] 🟢 pattern / drift / lineage graph   │
│                                                                        [ENCODER] 🟠 eval records and historical facts │
│ PURPOSE                                                                                                              │
│ "What can be learned for future runs after this run is complete?"                                                    │
│                                                                                                                       │
│ SUBSTEPS                                                                                                             │
│ L6.1 Runtime exhaust ingest and normalization                                                                         │
│      - consume sealed RuntimeExhaustBundle                                                                            │
│      - normalize stage map, artifact inventory, trace refs, evidence refs                                             │
│                                                                                                                       │
│ L6.2 Observer law isolation and eval readiness                                                                        │
│      - prove L6 did not mutate current run                                                                             │
│      - verify stage boundary                                                                                           │
│      - produce eval readiness receipt                                                                                  │
│                                                                                                                       │
│ L6.3 Outcome / trajectory / governance evaluation                                                                     │
│      - evaluate outcome quality                                                                                        │
│      - evaluate trajectory and tool choices                                                                            │
│      - evaluate governance regression                                                                                  │
│                                                                                                                       │
│ L6.4 Human calibration and eval record seal                                                                           │
│      - calibration records                                                                                             │
│      - judge reliability signals                                                                                       │
│      - sealed completed eval records                                                                                   │
│                                                                                                                       │
│ L6.5 Signal fusion / RCA / pattern synthesis                                                                          │
│      - 🟢 cluster failures, drift, repeated tool defects, repeated judge disagreement                                   │
│      - 🟠 use completed-run facts and eval records                                                                      │
│      - 🔶 produce RCA summary and pattern record                                                                        │
│                                                                                                                       │
│ L6.6 Proposal drafting and admission gate                                                                             │
│      - draft future-run proposal                                                                                       │
│      - proposed prompt/rubric/policy/cache/memory/index change remains inert                                           │
│      - proposal must be complete before gauntlet                                                                        │
│                                                                                                                       │
│ L6.7 Gauntlet / approval / UWG promotion                                                                               │
│      - replay proof                                                                                                    │
│      - regression proof                                                                                                │
│      - safety proof                                                                                                    │
│      - approved promotion request goes to UWG, never direct L4                                                         │
│      - activation only at future run_start                                                                             │
│                                                                                                                       │
│ SIGNALS                                                                                                              │
│ 🔵 intent_vec: used only for evaluation comparisons against original task, not live reroute.                           │
│ 🟠 fact_vec: completed-run artifacts, eval records, historical patterns, calibration records.                          │
│ 🟢 graph_sig: RCA clusters, lineage graph, drift graph, dependency and failure relationships.                          │
│ 🔶 gen_text: eval summaries, RCA, proposal text, calibration notes.                                                    │
│                                                                                                                       │
│ INPUT                                                                                                                 │
│ [CONTRACT] RuntimeExhaustBundle after current-run boundary                                                             │
│                                                                                                                       │
│ OUTPUT                                                                                                                │
│ CompletedEvalRecord | RCAPacket | ProposalPacket | optional UWG promotion request                                     │
│ 🧾 observer_law_receipt | eval_record_seal | gauntlet_receipt | future_run_activation_receipt                         │
│                                                                                                                       │
│ MAY                                                                                                                   │
│ evaluate completed run | calibrate graders | detect drift | draft future-run proposals | request UWG promotion         │
│                                                                                                                       │
│ MUST NOT                                                                                                              │
│ mutate current run | emit current-run X3 | rescue current run | directly write L4 | silently patch prompts/policy      │
│                                                                                                                       │
│ ★ Runtime Gates                                                                                                       │
│ G28 audit completeness | G29 learning firewall                                                                        │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

========================================================================================================================
END
========================================================================================================================