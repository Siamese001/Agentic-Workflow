[ L1_PLAN_CONTRACT ]
                                                     │
                                                     ▼
========================================================================================================================================
[3] ROUTE DECISION + SWITCHING — v15
========================================================================================================================================

- The dispatcher takes the approved L1 plan and decides whether the request should short-circuit
  through exact reuse, bounded semantic reuse, grounded context assembly, external action dispatch,
  managed workflow orchestration, human-gated escalation, or safe fallback.
- L0 decides the path, but it does not itself retrieve, think deeply, execute tools, call models,
  mutate state, approve final egress, or promote learning.
- L0 emits exactly one deterministic RouteContract:
  route_id, confidence, reason_codes, freshness_class, cache_policy, execution_form, cost_tier,
  fallback_chain, slo, telemetry_keys, tenant_scope, sandbox_class, support_target, route_digest, and hmac_sig.
- L3 is OPTIONAL and is invoked only when the selected route must be expanded into managed steps.
- Terminal [RET] routes bypass L3 completely and go straight to Exit Eval & Control.
- Single-step routes bypass L3 and go straight to one bounded L2 execution step.
- Managed workflow routes enter L3 only when dependency order, branching, joins, retries, parallel-safe shards,
  iterative refinement, staged evidence assembly, stateful handoff, HITL pause/resume, or resumable workflow state
  are genuinely required.
- L0 is a dispatcher, not an executor. Downstream layers consume the RouteContract but do not re-decide the route.
- L0 makes the cheapest safe decision, not the fanciest possible decision.
- L0 prefers deterministic reuse when policy, freshness, and support obligations are satisfied.
- L0 prefers grounded read over ungrounded generation when factual, policy, document, code, legal, medical,
  financial, regulatory, or user-file claims are involved.
- L0 prefers single-step execution over L3 orchestration unless the contract genuinely changes across steps.
- L0 prefers abstain / clarify / safe partial over fabricated certainty when support is weak.
- L0 never creates a durable write. It can only route a proposed mutation toward Exit Eval and UWG.

========================================================================================================================================
PEDAGOGICAL LEGEND
========================================================================================================================================

🔵 Blue asks      = live query text / query_vec / intent vector / step ask / model-side intent representation
🟠 Orange knows   = raw text chunks / contextual chunk vectors / dense fact vectors / sparse BM25 terms / source spans
🟢 Green maps     = knowledge graph / entity subgraph / lineage graph / dependency graph / ADG / runtime graph
🟣 Purple governs = policy, ACL, capability, sandbox, HITL, registry, and egress controls
⚫ Black seals    = replay envelope, route_digest, hmac_sig, evidence seal, trace receipt, deterministic proof
[RET]             = terminal early exit; bypasses L3 and returns to Exit Eval & Control
[UWG]             = Universal Write Gateway, the only durable write path into L4
★                 = high-signal v15 detail added inside preserved v14 structure

========================================================================================================================================
MENTAL MODEL
========================================================================================================================================

L1 writes the notepad plan.
L0 decides which hallway the patron should go down.
C0 finds evidence only when the route requires grounding.
Prompt Assembly packs the bounded evidence/rules/task packet.
L3 manages multi-step work only when the hallway turns into a workflow.
L2 performs the current bounded step.
Exit Eval decides whether the sealed result may leave, reroute, escalate, or request commit.
UWG is the only clerk allowed to write durable truth into L4.
L6 watches, scores, and improves future runs only.

========================================================================================================================================
TOP-LEVEL L0 + L4 CONTROL VIEW
========================================================================================================================================

 ┌──────────────────────────────────────────────┐                               ┌────────────────────────────────────────────┐
 │ L0 ROUTING / DISPATCHER                      │                               │ L4 STATE / ARCHIVE                         │
 │ The Front Desk Dispatcher                    │                               │ The Archivist / Durable Shelves            │
 ├──────────────────────────────────────────────┤                               ├────────────────────────────────────────────┤
 │ INGRESS                                      │                               │ READ SURFACES                              │
 │ - L1PlanContract                             │                               │ - Exact cache store                         │
 │ - task_spec / query_spec                     │                               │ - Semantic cache store                      │
 │ - proposed_route candidates                  │                               │ - Canonical raw chunks 🟠                  │
 │ - route_risk / confidence                    │                               │ - Dense fact vectors 🟠                    │
 │ - grounding_required                         │                               │ - Sparse / BM25 index 🟠                   │
 │ - action_intent / mutate_intent              │                               │ - Source lineage / citation anchors        │
 │ - declared assumptions / gaps                │                               │ - Knowledge graph / entities 🟢            │
 │ - 🔵 query_vec if already computed           │                               │ - ADG / code graph / dependency map 🟢     │
 │                                              │                               │ - Version manifests / schema registry      │
 │ PREFILTER                                    │                               │ - Prior approved examples / rubrics        │
 │ - tenant / ACL / region                      │                               │ - Policy snapshots and route baselines     │
 │ - source availability                        │                               │                                            │
 │ - model/tool registry eligibility 🟣          │                               │ WRITE LAW                                  │
 │ - capability class                           │                               │ - Universal Persistence Boundary           │
 │ - high-impact / irreversible intent          │                               │ - No direct write path from L0/L2/L3/HITL  │
 │ - freshness requirement                      │                               │ - Writes require UWG only                  │
 │ - support obligation                         │                               │ - Read surfaces feed C0 only               │
 │ - privacy / egress boundary                  │                               │ - Learning promotions require UWG          │
 │                                              │                               │                                            │
 │ SCORING                                      │                               │ CONTROL                                    │
 │ - exact-cacheable?                           │                               │ - Snapshot IDs                             │
 │ - semantic-cacheable?                        │                               │ - Policy hashes                            │
 │ - grounded-read needed?                      │                               │ - Evidence versions                        │
 │ - action dispatch needed?                    │                               │ - Cache expiry                             │
 │ - workflow / multi-hop needed?               │                               │ - Alias swaps after commit                 │
 │ - HITL needed?                               │                               │ - Retrieval cache invalidation             │
 │ - fallback safest?                           │                               │                                            │
 │ - parallel / iterative / high-stakes? ★      │                               │                                            │
 │ - compute difficulty / cost tier? ★          │                               │                                            │
 │                                              │                               │                                            │
 │ OUTPUT                                       │                               │                                            │
 │ - Emit RouteContract only                    │                               │                                            │
 │ - Emit RouteTelemetryEvent to L6             │                               │                                            │
 │ - Never perform the work itself              │                               │                                            │
 └──────────────────────┬───────────────────────┘                               └──────────────────┬─────────────────────────┘
                        │                                                                          │
                        │                                                                          │
                        └───────────────────────────────[ read handles only ]──────────────────────┘
                        │
                        ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ L0 ROUTE DECISION SWITCH                                                                                                  │
 │ The dispatcher selects ONE terminal, single-step, or managed-workflow path based on the deterministic route contract.      │
 ├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ COLD-START RULE                                                                                                           │
 │ - If confidence is weak and support is required, choose conservative R3 grounded read or R5 safe fallback.                 │
 │ - If the task asks for factual claims and evidence is unavailable, do not choose ungrounded generation.                    │
 │ - If user intent is underspecified but safe clarification can resolve it, select R5 clarify/abstain path.                  │
 │                                                                                                                            │
 │ FIXED DECISION ORDER                                                                                                      │
 │  0. Invalid envelope / scope fail / unsafe request                   -> R5 FALLBACK [RET]                                 │
 │  1. Exact reusable answer with valid freshness and policy             -> R1A EXACT CACHE [RET]                             │
 │  2. Reuse-safe semantic match with calibrated confidence              -> R1B SEMANTIC CACHE [RET]                          │
 │  3. High-risk / irreversible / ambiguous mutation                     -> HITL posture then Exit/UWG path                   │
 │  4. Low-risk reversible action, one bounded action                    -> R4 SINGLE ACTION -> L2                            │
 │  5. Factual / document / code / policy answer requiring support       -> R3 SIMPLE GROUNDED READ -> C0 -> PA -> L2         │
 │  6. Multi-hop read/action with dependencies or changing step contract -> R3/R4 MANAGED WORKFLOW -> L3 -> L2                │
 │  7. No safe/grounded/reusable path                                    -> R5 FALLBACK [RET]                                 │
 │                                                                                                                            │
 │ IMPORTANT DISAMBIGUATION                                                                                                  │
 │ - R3 simple grounded read does use C0 and L2, but not L3.                                                                   │
 │ - R4 single action uses L2, but not C0 unless action args require grounded lookup.                                          │
 │ - R3/R4 managed workflow uses L3 because the work needs step state, branching, joins, retries, or staged evidence.          │
 │ - R1A/R1B/R5 are terminal short-circuits and return directly to Exit Eval.                                                  │
 │ - HITL is not sovereign authority. Human input re-enters as data and must be re-cleared.                                   │
 └─┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
   │
   │
   │  ┌────────────────────────────────────────┐
   ├──► R1A EXACT CACHE                        │◄──────────────────────────────────────────────────┐
   │  │ The locked photocopy drawer             │                                                   │
   │  ├────────────────────────────────────────┤                                                   │
   │  │ PURPOSE                                │                                                   │
   │  │ - Perfect keyed reuse, zero inference   │                                                   │
   │  │ - Bypass deep pipeline entirely         │                                                   │
   │  │ - Exact prior answer, no C0 needed      │                                                   │
   │  │ - Terminal short-circuit route          ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - No L3 needed                          │                                                   │
   │  │                                        │                                                   │
   │  │ MATCH REQUIREMENTS                      │                                                   │
   │  │ - normalized_request_hash match         │                                                   │
   │  │ - tenant_scope match                    │                                                   │
   │  │ - policy_hash compatible                │                                                   │
   │  │ - source snapshot compatible            │                                                   │
   │  │ - output schema compatible              │                                                   │
   │  │ - freshness_class satisfied             │                                                   │
   │  │ - no changed safety policy              │                                                   │
   │  │                                        │                                                   │
   │  │ CONTRACT FIELDS                         │                                                   │
   │  │ - route_id = R1A_EXACT_CACHE            │                                                   │
   │  │ - cache_policy = EXACT_ONLY             │                                                   │
   │  │ - execution_form = TERMINAL_SHORTCIRCUIT│                                                   │
   │  │ - confidence = 1.0 or deterministic hit │                                                   │
   │  │ - fallback_chain empty on hit           │                                                   │
   │  │ - evidence_contract = prior sealed ref  │                                                   │
   │  │                                        │                                                   │
   │  │ GUARDS                                  │                                                   │
   │  │ - Do not use if freshness expired       │                                                   │
   │  │ - Do not use across tenant/policy drift │                                                   │
   │  │ - Do not use if answer had weak support │                                                   │
   │  │ - On miss: re-decide from scratch       │                                                   │
   │  │ - No "soft fallback" inside R1A         │                                                   │
   │  │                                        │                                                   │
   │  │ EXAMPLES                                │                                                   │
   │  │ - "What does ADR mean?"                │                                                   │
   │  │ - "What is golden path meaning?"       │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R1B SEMANTIC CACHE                     │◄──────────────────────────────────────────────────┤
   │  │ The familiar-question drawer            │                                                   │
   │  ├────────────────────────────────────────┤                                                   │
   │  │ PURPOSE                                │                                                   │
   │  │ - Policy-approved similarity reuse      │                                                   │
   │  │ - Bounded reuse for stable tasks        │                                                   │
   │  │ - Matches 🔵 live ask vs 🔵 cached ask  │                                                   │
   │  │ - No deep reading when reuse is safe    ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Terminal short-circuit route          │                                                   │
   │  │ - No C0 needed, no L3 needed            │                                                   │
   │  │                                        │                                                   │
   │  │ MATCH REQUIREMENTS                      │                                                   │
   │  │ - semantic similarity above threshold   │                                                   │
   │  │ - task class is reuse-safe              │                                                   │
   │  │ - answer style/schema compatible        │                                                   │
   │  │ - no factual freshness dependency       │                                                   │
   │  │ - no user-file/doc-specific obligation  │                                                   │
   │  │ - no action/mutation intent             │                                                   │
   │  │ - no personalization boundary conflict  │                                                   │
   │  │ - policy_hash compatible                │                                                   │
   │  │                                        │                                                   │
   │  │ HYBRID SCORING                          │                                                   │
   │  │ - 🔵 query_vec cosine similarity        │                                                   │
   │  │ - lexical overlap for named terms       │                                                   │
   │  │ - task-class compatibility              │                                                   │
   │  │ - output-contract compatibility         │                                                   │
   │  │ - risk penalty for stale/factual asks   │                                                   │
   │  │ - tenant/scope penalty                  │                                                   │
   │  │                                        │                                                   │
   │  │ CONTRACT FIELDS                         │                                                   │
   │  │ - route_id = R1B_SEMANTIC_CACHE         │                                                   │
   │  │ - cache_policy = SEMANTIC_OK            │                                                   │
   │  │ - execution_form = TERMINAL_SHORTCIRCUIT│                                                   │
   │  │ - confidence = calibrated sim score     │                                                   │
   │  │ - reason_codes include cache_hit_basis  │                                                   │
   │  │                                        │                                                   │
   │  │ GUARDS                                  │                                                   │
   │  │ - Semantic threshold must be calibrated │                                                   │
   │  │ - Bad cache entries amplify bad answers │                                                   │
   │  │ - Do not reuse for "latest/current"    │                                                   │
   │  │ - Do not reuse for legal/medical/fin    │                                                   │
   │  │   claims unless explicitly approved     │                                                   │
   │  │ - Do not reuse for attached-file Q&A    │                                                   │
   │  │ - Do not reuse across policy drift      │                                                   │
   │  │ - If uncertain, prefer R3 or R5         │                                                   │
   │  │                                        │                                                   │
   │  │ EXAMPLES                                │                                                   │
   │  │ - "Explain Jaccard again."             │                                                   │
   │  │ - "Remind me what semantic cache does."│                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐                                                   │
   ├──► R5 FALLBACK                            │                                                   │
   │  │ The safe "do not guess" desk            │                                                   │
   │  ├────────────────────────────────────────┤                                                   │
   │  │ PURPOSE                                │                                                   │
   │  │ - Safest bounded outcome                │                                                   │
   │  │ - Abstain, clarify, deny, or safe part  ├─► [RET] ──► To 5. EXIT EVAL & CONTROL             │
   │  │ - Ungrounded default when evidence weak │                                                   │
   │  │ - Terminal safe route                   │                                                   │
   │  │ - No C0 needed when issue is unsafe     │                                                   │
   │  │ - No L3 needed                          │                                                   │
   │  │                                        │                                                   │
   │  │ TRIGGERS                                │                                                   │
   │  │ - invalid scope                         │                                                   │
   │  │ - unsafe request                        │                                                   │
   │  │ - policy conflict                       │                                                   │
   │  │ - unclear recipient/action/scope        │                                                   │
   │  │ - missing critical artifact             │                                                   │
   │  │ - no evidence for grounded claim        │                                                   │
   │  │ - cache confidence below threshold      │                                                   │
   │  │ - tool/model unavailable with no safe   │                                                   │
   │  │   fallback                              │                                                   │
   │  │ - budget exhausted before safe answer   │                                                   │
   │  │                                        │                                                   │
   │  │ CONTRACT FIELDS                         │                                                   │
   │  │ - route_id = R5_FALLBACK                │                                                   │
   │  │ - execution_form = TERMINAL_SHORTCIRCUIT│                                                   │
   │  │ - fallback_chain terminal entry         │                                                   │
   │  │ - reason_codes mandatory                │                                                   │
   │  │ - safe_response_type = clarify/abstain/ │                                                   │
   │  │   refuse/safe_partial                   │                                                   │
   │  │                                        │                                                   │
   │  │ GUARDS                                  │                                                   │
   │  │ - Emits reason_code, never silent fail  │                                                   │
   │  │ - No vague tool execution               │                                                   │
   │  │ - No broad mutation                     │                                                   │
   │  │ - No hidden credential use              │                                                   │
   │  │ - No fabricated evidence                │                                                   │
   │  │ - No "best guess" for high-risk claims │                                                   │
   │  │                                        │                                                   │
   │  │ EXAMPLES                                │                                                   │
   │  │ - "Delete anything old."               │                                                   │
   │  │ - "Send this to everyone."             │                                                   │
   │  │ - "Use whatever credentials you find." │                                                   │
   │  │ - "Tell me what the document says"     │                                                   │
   │  │   when no document exists               │                                                   │
   │  └────────────────────────────────────────┘                                                   │
   │                                                                                               │
   │  ┌────────────────────────────────────────┐
   ├──► R3 SIMPLE GROUNDED READ                │
   │  │ The reference-desk answer path          │
   │  ├────────────────────────────────────────┤
   │  │ PURPOSE                                │
   │  │ - Factual/policy/code/doc claims require│
   │  │   backing                              │
   │  │ - Evidence class and support target     │
   │  │ - Strictly grounded answer only         │
   │  │ - Single-pass grounding, bypasses L3    │
   │  │ - Still requires one bounded L2 step    │
   │  │                                        │
   │  │ TRIGGERS                                │
   │  │ - user asks about an uploaded file      │
   │  │ - user asks what a source says          │
   │  │ - user asks current/law/policy/company  │
   │  │   facts that need freshness             │
   │  │ - user asks code/doc/repo specific Q&A  │
   │  │ - user asks for cited summary           │
   │  │ - user asks for grounded comparison     │
   │  │ - user asks "are you sure" / verify     │
   │  │                                        │
   │  │ CONTRACT FIELDS                         │
   │  │ - route_id = R3_SIMPLE_GROUNDED_READ    │
   │  │ - execution_form = SINGLE_STEP          │
   │  │ - cost_tier usually TIER_M              │
   │  │ - cache_policy = READ_THROUGH or NONE   │
   │  │ - support_target required               │
   │  │ - citation_mode bound                   │
   │  │ - fallback_chain: refine -> R5          │
   │  │                                        │
   │  │ GUARDS                                  │
   │  │ - C0 may refine once within budget      │
   │  │ - No durable write                      │
   │  │ - No action dispatch                    │
   │  │ - No hidden multi-step autonomy         │
   │  │ - Weak evidence becomes caveat/abstain  │
   │  │ - If decomposition grows beyond budget, │
   │  │   recommend workflow/reroute, but C0    │
   │  │   cannot self-authorize L3              │
   │  │                                        │
   │  │ EXAMPLES                                │
   │  │ - "What does C5 say about prompt        │
   │  │   assembly?"                           │
   │  │ - "Review this file and tell me where   │
   │  │   retrieval happens."                   │
   │  │ - "What does my lease say about pets?" │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
   │  │ C0 CONTEXT ENGINE / REF DESK                                                                              │◄────────────[ Read ]─────────────┐
   │  │ Retrieval, shaping, verification, and support scoring only.                                                │                               │
   │  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                               │
   │  │ C0.1 PLAN                                                                                                 │                               │
   │  │ - Inputs: L1 query_spec, L0 RouteContract, tenant_scope, ACL, region, freshness_class, support_target      │                               │
   │  │ - Decide allowed sources: docs/code/logs/tickets/tables/policy/prior artifacts                             │                               │
   │  │ - Decide retrieval modes: dense, sparse/BM25, graph, metadata, cache if allowed                            │                               │
   │  │ - Decide limits: max_k, max_parent_expansion, max_graph_hops, max_refine_attempts                          │                               │
   │  │ - Output RetrievalPlan                                                                                    │                               │
   │  │                                                                                                            │                               │
   │  │ C0.2 FETCH                                                                                                │                               │
   │  │ - Runtime query text -> encoder -> 🔵 query_vec                                                           │                               │
   │  │ - 🔵 query_vec searches 🟠 dense fact/context vectors                                                       │                               │
   │  │ - Exact terms search 🟠 sparse/BM25 index                                                                  │                               │
   │  │ - Metadata filters enforce tenant/time/author/version/region/type                                          │                               │
   │  │ - Hydrate source_id, file_path, section, timestamp, version, ACL                                            │                               │
   │  │ - Expand parent-child context around small hit spans                                                       │                               │
   │  │ - Output CandidateEvidencePool                                                                            │                               │
   │  │                                                                                                            │                               │
   │  │ C0.3 GRAPH                                                                                                │                               │
   │  │ - Candidate chunks -> entity extraction -> 🟢 bounded graph hops                                            │                               │
   │  │ - Follow parent doc, referenced module, owner, policy, schema, ADR, dependency, contradiction               │                               │
   │  │ - Enforce max_hops, ACL, freshness, relation type preservation                                              │                               │
   │  │ - No ACL escape through graph neighbors                                                                    │                               │
   │  │ - Output GraphExpandedEvidencePool                                                                         │                               │
   │  │                                                                                                            │                               │
   │  │ C0.4 SHAPE                                                                                                │                               │
   │  │ - Dedupe dense+sparse duplicate hits                                                                       │                               │
   │  │ - Rerank by support_target, authority, freshness, direct span, graph proximity, contradiction value         │                               │
   │  │ - Prune stale, weak-lineage, redundant, low relevance, ACL-risky payload                                    │                               │
   │  │ - Stratify MUST_USE / SUPPORTING / CONTRADICTS / BACKGROUND / EXCLUDED                                     │                               │
   │  │ - Preserve contradictions, do not hide conflicts                                                           │                               │
   │  │ - Output ShapedEvidenceSet                                                                                 │                               │
   │  │                                                                                                            │                               │
   │  │ C0.5 CONTRACT                                                                                             │                               │
   │  │ - Verify source_id resolves                                                                                │                               │
   │  │ - Verify cited span / line ref / section anchor resolves                                                   │                               │
   │  │ - Verify version matches snapshot                                                                          │                               │
   │  │ - Verify citation anchors are stable                                                                       │                               │
   │  │ - Score direct support, coverage, contradiction risk, stale-source risk, unsupported-inference risk         │                               │
   │  │ - Status = PASS / WEAK / CONFLICTED / EMPTY / BLOCKED                                                      │                               │
   │  │ - Output EvidenceContract                                                                                  │                               │
   │  │                                                                                                            │                               │
   │  │ C0.6 REFINE / BROADEN / DECOMPOSE                                                                          │                               │
   │  │ - Triggered only if support is weak and route budget allows                                                │                               │
   │  │ - Tactics: rewrite, broaden, narrow, decompose, graph_hop, abstain                                          │                               │
   │  │ - Exactly bounded second pass unless RouteContract permits more                                            │                               │
   │  │ - If still weak: recommend R5 fallback / abstain                                                           │                               │
   │  │ - If task grew workflow-sized: recommend reroute, do not self-authorize L3                                  │                               │
   │  │                                                                                                            │                               │
   │  │ OUTPUT FINAL EVIDENCE CONTRACT                                                                             │                               │
   │  │ - status / support_score / verified_chunks / cited_spans / source_ids                                      │                               │
   │  │ - evidence_classes / contradiction_flags / unresolved_gaps                                                 │                               │
   │  │ - freshness_report / ACL_report / lineage_manifest                                                         │                               │
   │  │ - prompt_budget_hint / recommended_disposition / budget_report                                             │                               │
   │  │                                                                                                            │                               │
   │  │ HARD LAW                                                                                                   │                               │
   │  │ - C0 retrieves only                                                                                        │                               │
   │  │ - C0 never answers                                                                                         │                               │
   │  │ - C0 never routes                                                                                          │                               │
   │  │ - C0 never executes                                                                                        │                               │
   │  │ - C0 never mutates durable state                                                                           │                               │
   │  └───────────────────┬────────────────────────────────────────────────────────────────────────────────────────┘                               │
   │                      │ [ Evidence Contract ]                                                                                                   │
   │                      ▼                                                                                                                        │
   │  ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐                               │
   │  │ PROMPT ASSEMBLY / PACKET BUILDER                                                                           │◄────────────[ Load ]─────────────┘
   │  │ Trusted composer only. No retrieval, no execution, no durable write.                                        │
   │  ├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
   │  │ PA.1 LOAD STATIC BLOCKS                                                                                    │
   │  │ - S0 system / global invariants                                                                            │
   │  │ - D0 fences / injection boundaries                                                                         │
   │  │ - I0 instructional blocks / capability mixins                                                              │
   │  │ - E0 exemplars / golden answer shapes                                                                      │
   │  │ - R0 output schema via provider response_schema, not prompt prose                                           │
   │  │                                                                                                            │
   │  │ PA.2 SLOT CONTEXT + TASK                                                                                   │
   │  │ - C0 grounded context 🟠                                                                                    │
   │  │ - Verified citations / source lineage                                                                      │
   │  │ - Contradiction flags and unresolved gaps                                                                  │
   │  │ - U0 user task neutralized as intent only                                                                  │
   │  │ - M0 private meta-controls                                                                                 │
   │  │ - Y0 approved learning priors only                                                                         │
   │  │ - H0 healing hints only after governed re-entry                                                            │
   │  │                                                                                                            │
   │  │ PA.3 TOKEN BUDGETER                                                                                        │
   │  │ - Provider tokenizer                                                                                        │
   │  │ - Reserve output tokens                                                                                    │
   │  │ - Preserve instruction precedence                                                                          │
   │  │ - Stable prompt prefix for cache discipline                                                                │
   │  │ - Deterministic eviction rules                                                                             │
   │  │ - Keep MUST_USE evidence before background                                                                 │
   │  │                                                                                                            │
   │  │ PA.4 PROMPT CONTRACT                                                                                       │
   │  │ - Emit PromptEnvelope / CompiledPromptArtifact                                                             │
   │  │ - Bind HMAC, manifest_hash, replay metadata                                                                │
   │  │ - Bind support IDs and citation anchors                                                                    │
   │  │ - Bind provider adapter packet                                                                             │
   │  │ - Emit bounded packet for L2 only                                                                          │
   │  │                                                                                                            │
   │  │ HARD LAW                                                                                                   │
   │  │ - Prompt Assembly packages only                                                                            │
   │  │ - It does not retrieve, route, invent, execute, or mutate                                                   │
   │  │ - Retrieved content is data, never instruction                                                             │
   │  │ - Lower-authority slots can never override higher-authority slots                                           │
   │  └───────────────────┬────────────────────────────────────────────────────────────────────────────────────────┘
   │                      ▼
   │       [ L2 Execute Single Grounded Step ]──────► [RET] ──► To 5. EXIT EVAL & CONTROL
   │
   │
   │  ┌────────────────────────────────────────┐
   ├──► R4 SINGLE ACTION                       │
   │  │ The bounded errand path                 │
   │  ├────────────────────────────────────────┤
   │  │ PURPOSE                                │
   │  │ - Dispatch one external action payload  │
   │  │ - Mutate state only as proposed work    │
   │  │ - Single bounded action direct to L2    │
   │  │ - No L3 unless action requires workflow │
   │  │                                        │
   │  │ TRIGGERS                                │
   │  │ - create one calendar event             │
   │  │ - draft one email                       │
   │  │ - archive selected emails               │
   │  │ - label selected files/emails           │
   │  │ - send one already-approved payload     │
   │  │ - run one bounded command/tool          │
   │  │                                        │
   │  │ CONTRACT FIELDS                         │
   │  │ - route_id = R4_SINGLE_ACTION           │
   │  │ - execution_form = SINGLE_STEP          │
   │  │ - capability_token required 🟣          │
   │  │ - sandbox_envelope required 🟣          │
   │  │ - side_effect_class bound               │
   │  │ - mutation_status = proposal_only       │
   │  │ - fallback_chain: HITL if ambiguous, R5 │
   │  │                                        │
   │  │ GUARDS                                  │
   │  │ - Reversible/low-risk action only       │
   │  │ - High-risk or irreversible actions     │
   │  │   must route to human-gated Exit/HITL   │
   │  │ - Writes remain proposal-only until     │
   │  │   Exit/UWG approval                     │
   │  │ - No direct L4 write                    │
   │  │ - No hidden broadening of recipient set │
   │  │ - No silent provider fallback           │
   │  │ - No action if args are ambiguous       │
   │  │                                        │
   │  │ EXAMPLES                                │
   │  │ - "Create a calendar event for Monday   │
   │  │   at 3 PM."                             │
   │  │ - "Archive these three emails."         │
   │  │ - "Draft an email to Amy."              │
   │  └───────────────────┬────────────────────┘
   │                      ▼
   │             [ L2 Execute Single Step ]─────────► [RET] ──► To 5. EXIT EVAL & CONTROL
   │
   │
   │  ┌────────────────────────────────────────┐
   └──► R3/R4 MANAGED WORKFLOW                 │
      │ The floor-supervisor path               │
      ├────────────────────────────────────────┤
      │ PURPOSE                                │
      │ - Multi-hop RAG or workflow action      │
      │ - Dependency order / branching / joins  │
      │ - Needs resumable workflow state        │
      │ - L3 orchestration required             │
      │                                        │
      │ TRIGGERS                                │
      │ - More than one dependent step          │
      │ - Step contract changes across steps    │
      │ - Evidence must be gathered in stages   │
      │ - Weak evidence requires targeted rerun │
      │ - Branches must be joined               │
      │ - Parallel shards are safe and useful   │
      │ - Tool result determines next action    │
      │ - HITL pause/resume may be needed       │
      │ - Long-running resumable workflow       │
      │ - Evaluator/optimizer loop is bounded   │
      │ - Confidence cascade across compute tier│
      │                                        │
      │ CONTRACT FIELDS                         │
      │ - route_id = R3R4_MANAGED_WORKFLOW      │
      │ - execution_form = MANAGED_WORKFLOW     │
      │ - workflow_blueprint_id                 │
      │ - max_nodes / max_depth / max_iterations│
      │ - branch_policy / join_policy           │
      │ - parallelism_policy                    │
      │ - checkpoint_policy                     │
      │ - fallback_chain                        │
      │ - HITL_pause_points                     │
      │ - route_slo and per-step slo slices     │
      │                                        │
      │ GUARDS                                  │
      │ - Use only when contract changes        │
      │   between steps                         │
      │ - Parallel fan-out happens inside L3,   │
      │   not as an L0 structural change        │
      │ - Evaluator/optimizer loops require     │
      │   max_iterations and measurable quality │
      │ - Confidence cascade is valid only when │
      │   executor capability is uncertain, not │
      │   when routing itself is uncertain      │
      │ - Preserve single-agent-first unless    │
      │   specialists improve isolation         │
      │ - No hidden retrieval outside C0        │
      │ - No hidden scope expansion             │
      │ - No open-ended autonomy                │
      │                                        │
      │ EXAMPLE                                 │
      │ - "Review 90 days of tickets, incident │
      │   logs, and churn notes; find top       │
      │   themes, pull evidence, rerun weak     │
      │   areas, rank causes, and draft         │
      │   remediation."                         │
      └───────────────────┬────────────────────┘
                          │
                          ▼
========================================================================================================================================
L3 ORCHESTRATION CONTROL PLANE — THE MANAGING LIBRARIAN
========================================================================================================================================

       ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
       │ L3 ORCHESTRATION CONTROL PLANE                                                                              │
       │ The Managing Librarian. Expands one approved managed-workflow route into bounded executable steps.           │
       ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
       │ INGRESS                                                                                                      │
       │ - Approved RouteContract from L0                                                                             │
       │ - Workflow blueprint / action contracts                                                                      │
       │ - Evidence requirements / support targets                                                                    │
       │ - Capability and sandbox bounds 🟣                                                                           │
       │ - Policy hash / blueprint hash / snapshot IDs ⚫                                                              │
       │ - Cost tier / budget / timeout / fallback_chain                                                              │
       │                                                                                                              │
       │ AUTHORITY                                                                                                    │
       │ - Consumes RouteContract, does not re-decide L0 route                                                        │
       │ - Expands workflow shape within approved bounds                                                              │
       │ - Emits current bounded step contracts only                                                                  │
       │ - Holds workflow state and checkpoints                                                                       │
       │ - Cannot persist durable truth directly                                                                      │
       │ - Cannot approve final egress                                                                                │
       │ - Cannot bypass L2, Exit, HITL, or UWG                                                                       │
       │                                                                                                              │
       │ OUTPUT                                                                                                       │
       │ - StepContract to L2 for the current ready node                                                              │
       │ - Step readiness decisions                                                                                   │
       │ - Branch/join state                                                                                          │
       │ - Retry/fallback disposition                                                                                 │
       │ - Sealed workflow package to Exit when complete                                                              │
       │                                                                                                              │
       │   ┌──────────────────────────────┐       ┌───────────────────────────────┐                                  │
       │   │ L3.1 DAG / HTN / AST RUNNER  │◄─────►│ L3.2 STATE LEDGER             │                                  │
       │   │ - Build executable graph     │       │ - Workflow checkpoint state   │                                  │
       │   │ - Nodes, edges, dependencies │       │ - Node status tracking        │                                  │
       │   │ - Serial/parallel tags       │       │ - Attempt/retry counters      │                                  │
       │   │ - Branch/join rules          │       │ - Fallback depth tracking     │                                  │
       │   │ - Forward-only current run   │       │ - SLO remaining budget        │                                  │
       │   │ - Issues 🔵 step asks        │       │ - Resume tokens               │                                  │
       │   │ - No backward graph edges    │       │ - HITL pause packets          │                                  │
       │   └──────────────┬───────────────┘       └───────────────────────────────┘                                  │
       │                  │                                                                                           │
       │   ┌──────────────▼───────────────┐       ┌───────────────────────────────┐                                  │
       │   │ L3.3 CONTEXT BUS             │◄─────►│ L3.4 POLICY ENGINE            │                                  │
       │   │ - Carries 🟠 evidence refs   │       │ - Route bounds check 🟣       │                                  │
       │   │ - Carries 🟢 graph refs      │       │ - Capability/sandbox check    │                                  │
       │   │ - Stages partial artifacts   │       │ - Guardrail validation        │                                  │
       │   │ - Central merge area         │       │ - HITL trigger check          │                                  │
       │   │ - Evidence packet only       │       │ - No scope expansion          │                                  │
       │   │ - No hidden retrieval        │       │ - No memory bloat             │                                  │
       │   └──────────────┬───────────────┘       └───────────────────────────────┘                                  │
       │                  │                                                                                           │
       │   ┌──────────────▼───────────────┐       ┌───────────────────────────────┐                                  │
       │   │ L3.5 CONCURRENCY GOVERNOR    │◄─────►│ L3.6 QUALITY LOOP GOVERNOR    │                                  │
       │   │ - Fan-out only if independent│       │ - Evaluator/optimizer bounds  │                                  │
       │   │ - Join only after all ready  │       │ - Max iterations              │                                  │
       │   │ - Quorum/vote rules          │       │ - Quality threshold           │                                  │
       │   │ - Race prevention            │       │ - Stop on diminishing returns │                                  │
       │   │ - Resource ceilings          │       │ - Safe partial on exhaustion  │                                  │
       │   └──────────────┬───────────────┘       └───────────────────────────────┘                                  │
       │                  │                                                                                           │
       │   ┌──────────────▼───────────────┐       ┌───────────────────────────────┐                                  │
       │   │ L3.7 FALLBACK / CASCADE CTRL │◄─────►│ L3.8 TELEMETRY EMITTER        │                                  │
       │   │ - Ordered fallback_chain     │       │ - RouteTelemetry join keys    │                                  │
       │   │ - Provider/tool alternatives │       │ - Node start/end events       │                                  │
       │   │ - TIER_S -> TIER_M -> TIER_L │       │ - Attempt/fallback metrics    │                                  │
       │   │ - Circuit breaker behavior   │       │ - Reason codes                │                                  │
       │   │ - No silent fallback         │       │ - Replay receipts ⚫           │                                  │
       │   └──────────────────────────────┘       └───────────────────────────────┘                                  │
       └──────────────┬───────────────────────────────────────────────────────────────────────────────────────────────┘
                      │
                      ▼
========================================================================================================================================
A. EXECUTION SHAPE CLASSIFICATION
========================================================================================================================================

           ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
           │ A. EXECUTION SHAPE CLASSIFICATION                                                                            │
           ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
           │ QUESTION                                                                                                     │
           │ - Does the selected route expand to one bounded step or to a managed multi-step workflow?                    │
           │                                                                                                              │
           │ TESTS                                                                                                        │
           │ - Is there more than one 🔵 ask across the route?                                                            │
           │ - Is there more than one 🟠 evidence packet required?                                                        │
           │ - Is there more than one 🟢 graph traversal / dependency stage?                                               │
           │ - Does any step depend on the output of a prior step?                                                        │
           │ - Does the task require branch selection after observing a result?                                           │
           │ - Does the task require join/merge of parallel outputs?                                                      │
           │ - Does the task require retry/repair with bounded iteration?                                                 │
           │ - Does the task require HITL pause/resume?                                                                   │
           │ - Does the task require resumable checkpoints?                                                               │
           │ - Does the action contract change between steps?                                                            │
           │                                                                                                              │
           │ DECISION RULES                                                                                               │
           │ - Prefer single-agent / single-step if it satisfies the contract                                             │
           │ - Do not split just because you can                                                                          │
           │ - Managed workflow only when the step contract changes between steps                                         │
           │ - Parallel fan-out is valid only for independent shards or voting/guardrail review                           │
           │ - Evaluator/optimizer loop is valid only when quality can be scored and iteration is bounded                 │
           │ - Confidence cascade is valid only when compute tier is uncertain, not when route identity is uncertain      │
           │ - If route identity itself is uncertain, return to L0/Exit reroute, do not improvise inside L3               │
           │                                                                                                              │
           │ OUTPUT                                                                                                       │
           │ - A1 Direct Step Package, or A2 Multi-Step Workflow / DAG                                                     │
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘
                             [ one bounded step ] ▼                                                       [ managed workflow ] ▼

           ┌────────────────────────────────────────┐                      ┌────────────────────────────────────────────┐
           │ A1. DIRECT STEP PACKAGE                │                      │ A2. MULTI-STEP WORKFLOW / DAG              │
           ├────────────────────────────────────────┤                      ├────────────────────────────────────────────┤
           │ - Emit one step contract for L2         │                      │ - Build nodes, edges, and branch rules      │
           │ - Encode dependency order if trivial    │                      │ - Mark parallel-safe vs serial-only paths   │
           │ - May contain one 🔵 ask or one action  │                      │ - Assign where 🔵 asks enter the DAG        │
           │ - May carry one 🟠 evidence packet      │                      │ - Assign where 🟠 evidence is required      │
           │ - May carry one 🟢 graph payload        │                      │ - Assign where 🟢 graph traversals happen   │
           │ - Send immediately to L2                │                      │ - Encode retry, join, timeout, SLO budget   │
           │ - Use when R3/R4 single-step suffices   │                      │ - Encode fallbacks and HITL pause points    │
           │ - No L3 expansion after packaging       │                      │ - Encode max loop/cascade depth             │
           │ - No open-ended autonomy                │                      │ - Encode checkpoint/resume semantics        │
           │ - Still sealed through Exit             │                      │ - Encode evidence merge and contradiction   │
           └──────────────────────┬─────────────────┘                      └──────────────────────┬─────────────────────┘
                                  │                                                               │
                                  └───────────────────────────────────────┬───────────────────────┘
                                                                          │
                                                                          ▼
========================================================================================================================================
B. STEP GRAPH / READINESS CONTROL
========================================================================================================================================

           ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
           │ B. STEP GRAPH / READINESS CONTROL                                                                            │◄─────┐
           ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤      │
           │ READY NODE SELECTION                                                                                         │      │
           │ - Pick only nodes whose dependencies are satisfied                                                            │      │
           │ - Respect policy, budget, timeout, concurrency, and checkpoint constraints                                    │      │
           │ - Hold blocked nodes until prerequisites, required 🟠 support, and route conditions are satisfied             │      │
           │ - Preserve forward-only L3 flow: no backward edges in the orchestration graph for the current run             │      │
           │                                                                                                              │      │
           │ DEPENDENCY TYPES                                                                                             │      │
           │ - Data dependency: prior artifact required                                                                    │      │
           │ - Evidence dependency: verified C0 contract required                                                          │      │
           │ - Policy dependency: clearance or HITL result required                                                        │      │
           │ - Tool dependency: capability token required                                                                  │      │
           │ - Graph dependency: 🟢 entity/dependency map required                                                         │      │
           │ - Join dependency: all branch outputs required                                                                │      │
           │                                                                                                              │      │
           │ BUDGET / SLO CONTROL                                                                                         │      │
           │ - Do not spawn a node if remaining budget is exhausted                                                        │      │
           │ - Slice SLO by step criticality                                                                               │      │
           │ - Reserve budget for Exit Eval and safe fallback                                                              │      │
           │ - Trigger safe partial on timeout/SLO breach                                                                  │      │
           │                                                                                                              │      │
           │ FALLBACK CONTROL                                                                                              │      │
           │ - Enforce fallback_chain in order                                                                             │      │
           │ - Provider outage, tool failure, timeout, SLO breach, or failed step uses ordered alternatives                 │      │
           │ - No silent fallback                                                                                          │      │
           │ - Track fallback_depth, attempt_count, reason_codes                                                           │      │
           │                                                                                                              │      │
           │ LOOP GUARD                                                                                                    │      │
           │ - Repeated unproductive spans trigger safe route or human review                                              │      │
           │ - Max repair attempts enforced                                                                                │      │
           │ - Max evaluator/optimizer iterations enforced                                                                 │      │
           │ - Oscillation detection emits reason_code                                                                     │      │
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘      │
                                          ▼                                                                                      │

           ┌────────────────────────────────────────────────────────────┐
           │ STEP CONTRACT TO L2                                        │
           ├────────────────────────────────────────────────────────────┤
           │ IDENTITY                                                   │
           │ - workflow_id / node_id / attempt_id                       │
           │ - parent_route_id / route_digest                           │
           │ - policy_hash / blueprint_hash / snapshot_id ⚫             │
           │ - idempotency_key                                          │
           │                                                            │
           │ WORK ORDER                                                 │
           │ - Current node only                                        │
           │ - Bounded autonomy                                         │
           │ - Tool / model / action spec                               │
           │ - Inputs may include 🔵 query intent                       │
           │ - Inputs may include 🟠 grounded evidence                  │
           │ - Inputs may include 🟢 graph payload                      │
           │ - Expected artifact / support target                       │
           │ - Output schema / validation target                        │
           │                                                            │
           │ CONTROL                                                    │
           │ - capability_token 🟣                                      │
           │ - sandbox_envelope 🟣                                      │
           │ - cost_tier and provider lane                              │
           │ - timeout / circuit breaker                                │
           │ - retry policy                                             │
           │ - fallback permission                                      │
           │ - no durable commit authority                              │
           │                                                            │
           │ OBSERVABILITY                                              │
           │ - telemetry_keys                                           │
           │ - trace_root / span_parent                                 │
           │ - expected receipts                                        │
           │ - slo slice                                                │
           │ - reason_code namespace                                    │
           └──────────────────────┬─────────────────────────────────────┘
                                  │
                                  ▼
                       [ Dispatch to [4] L2_EXECUTE ]
                                  │
                                  ▼

           ┌────────────────────────────────────────────────────────────┐
           │ STEP RESULT RETURN                                         │
           ├────────────────────────────────────────────────────────────┤
           │ PAYLOAD                                                    │
           │ - status, outputs, artifacts, errors                       │
           │ - final answer candidate or intermediate artifact           │
           │ - state diff proposal, if any                              │
           │ - evidence notes, if any                                   │
           │                                                            │
           │ ROUTING SIGNALS TO L3                                      │
           │ - may return new 🟠 evidence refs                          │
           │ - may return updated 🟢 graph state                         │
           │ - may return next 🔵 ask candidates                         │
           │ - retry signal                                             │
           │ - branch result                                            │
           │ - handoff signal                                           │
           │ - needs_help / HITL pause signal                           │
           │                                                            │
           │ OUTCOME CLASS                                              │
           │ - SUCCESS                                                  │
           │ - DEGRADED                                                 │
           │ - SOFT_REPAIRABLE                                          │
           │ - FAILED_TERMINAL                                          │
           │ - NEEDS_HELP                                               │
           │ - REJECTED                                                 │
           │                                                            │
           │ TELEMETRY                                                  │
           │ - observed latency                                         │
           │ - tokens / cost                                            │
           │ - quality signal                                           │
           │ - fallback_depth                                           │
           │ - exact reason_code                                        │
           │ - best-partial artifact on timeout/SLO breach              │
           │ - replay receipt ⚫                                        │
           │                                                            │
           │ HARD LAW                                                   │
           │ - Never mutates durable L4 directly                        │
           └──────────────────────┬─────────────────────────────────────┘
                                  ▼

========================================================================================================================================
C. GRAPH STATE UPDATE / HANDOFF MERGE
========================================================================================================================================

           ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
           │ C. GRAPH STATE UPDATE / HANDOFF MERGE                                                                        │
           ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
           │ NODE STATE                                                                                                   │
           │ - Mark node done / failed / retry / paused / skipped                                                         │
           │ - Update attempt_count and fallback_depth                                                                    │
           │ - Attach reason_codes                                                                                        │
           │ - Attach receipts and trace refs                                                                             │
           │                                                                                                              │
           │ DEPENDENCY UNLOCK                                                                                            │
           │ - Unlock dependents when prerequisites are satisfied                                                          │
           │ - Hold dependents when required 🟠 support is weak                                                            │
           │ - Hold dependents when policy/HITL clearance is missing                                                       │
           │ - Trigger allowed repair only inside same blueprint/policy snapshot                                           │
           │                                                                                                              │
           │ EVIDENCE / GRAPH MERGE                                                                                       │
           │ - Rejoin branches                                                                                            │
           │ - Merge returned 🟠 support and 🟢 graph outcomes into next-step readiness                                    │
           │ - Carry forward next eligible 🔵 asks without turning L3 into an open loop                                    │
           │ - Preserve lineage from all merged branches                                                                  │
           │ - Preserve contradiction flags                                                                               │
           │                                                                                                              │
           │ PARALLEL FAN-OUT                                                                                             │
           │ - Aggregate section shards                                                                                   │
           │ - Aggregate voting/guardrail reviews                                                                          │
           │ - Require deterministic join order                                                                            │
           │ - If one shard fails, apply branch policy: retry, degrade, safe partial, or escalate                           │
           │                                                                                                              │
           │ EVALUATOR / OPTIMIZER                                                                                        │
           │ - Stop at quality threshold                                                                                   │
           │ - Stop at max_iterations                                                                                      │
           │ - Stop at exhausted budget                                                                                    │
           │ - Stop on oscillation                                                                                         │
           │ - Preserve best prior artifact                                                                                │
           │                                                                                                              │
           │ CONFIDENCE CASCADE                                                                                            │
           │ - Escalate TIER_S -> TIER_M -> TIER_L only when executor confidence requires it                               │
           │ - Do not cascade just to search for a preferred answer                                                        │
           │ - Do not cascade if policy blocks the task                                                                    │
           │                                                                                                              │
           │ HITL PAUSE                                                                                                    │
           │ - Freeze packet                                                                                               │
           │ - Materialize bounded evidence                                                                                │
           │ - Human review output returns as untrusted data                                                               │
           │ - Resume only through governed re-clearance                                                                   │
           │                                                                                                              │
           │ HARD LAW                                                                                                      │
           │ - Failed repair stays inside same blueprint/policy snapshot                                                   │
           │ - No hidden scope growth                                                                                      │
           │ - No hidden durable write                                                                                     │
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘      │
                                          ▼                                                                                      │

========================================================================================================================================
D. COMPLETION / EXIT PACKAGE
========================================================================================================================================

           ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐      │
           │ D. COMPLETION / EXIT PACKAGE                                                                                 │      │
           ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤      │
           │ COMPLETION TEST                                                                                              │      │
           │ - Are all required nodes sealed?                                                                             │      │
           │ - Are all mandatory branches resolved?                                                                       │      │
           │ - Are all required joins complete?                                                                           │      │
           │ - Are all required 🟠 support obligations satisfied?                                                         │      │
           │ - Are contradictions explicitly labeled?                                                                     │      │
           │ - Are unresolved gaps carried forward?                                                                       │      │
           │ - Are route-level success conditions satisfied?                                                              │      │
           │ - Is any mutation merely proposed and not committed?                                                         │      │
           │                                                                                                              │      │
           │ IF COMPLETE                                                                                                  │      │
           │ - Emit one sealed workflow package upward for Exit Eval & Control                                            │      │
           │ - Attach RouteTelemetryEvent + RouteOutcomeEvent join keys                                                   │      │
           │ - Attach confidence, reason_codes, fallback_depth, SLO usage, and cost tier                                  │      │
           │ - Attach evidence lineage, citations, replay receipts, and policy_hash                                       │      │
           │ - Attach final artifact and best partials if degraded                                                        │      │
           │ - Attach mutation proposal only if write requested                                                           │      │
           │                                                                                                              │      │
           │ IF NOT COMPLETE                                                                                              │      │
           │ - Return to B for next ready node                                                                            ├──────┘ no
           │ - Or emit safe partial / abstain / HITL pause / failure disposition                                           │
           │                                                                                                              │
           │ WEAK SUPPORT RULE                                                                                            │
           │ - If required support is weak, emit safe partial / caveat / abstain disposition                               │
           │ - Never fabricate certainty                                                                                  │
           │                                                                                                              │
           │ WRITE RULE                                                                                                   │
           │ - If any mutation is requested, emit commit request only                                                      │
           │ - UWG remains the sole durable write path                                                                     │
           │                                                                                                              │
           │ LEARNING RULE                                                                                                │
           │ - Learning signal is exhaust only                                                                            │
           │ - L6 may tune future runs but never mutates this completed run                                                │
           └──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘
                                       yes ▼
                             [ Return sealed work ──► To 5. EXIT EVAL & CONTROL ]

========================================================================================================================================
ROUTE CONTRACT SCHEMA — v15
========================================================================================================================================

RouteContract {
  route_id:
    R1A_EXACT_CACHE |
    R1B_SEMANTIC_CACHE |
    R3_SIMPLE_GROUNDED_READ |
    R4_SINGLE_ACTION |
    R3R4_MANAGED_WORKFLOW |
    R5_FALLBACK,

  execution_form:
    TERMINAL_SHORTCIRCUIT |
    SINGLE_STEP |
    MANAGED_WORKFLOW,

  confidence:
    calibrated numeric score plus reasoned class:
    EXACT | HIGH | MEDIUM | LOW | UNSAFE | INSUFFICIENT_SUPPORT,

  reason_codes:
    [
      SCOPE_FAIL,
      POLICY_BLOCK,
      EXACT_CACHE_HIT,
      SEMANTIC_CACHE_HIT,
      CACHE_EXPIRED,
      GROUNDING_REQUIRED,
      SUPPORT_WEAK,
      ACTION_LOW_RISK,
      ACTION_HIGH_RISK,
      HITL_REQUIRED,
      MULTI_STEP_REQUIRED,
      DEPENDENCY_BRANCHING_REQUIRED,
      GRAPH_REQUIRED,
      FRESHNESS_REQUIRED,
      ACL_BLOCKED,
      TOOL_UNAVAILABLE,
      PROVIDER_OUTAGE,
      SLO_RISK,
      FALLBACK_SELECTED
    ],

  freshness_class:
    STATIC |
    SLOW_CHANGING |
    RECENT |
    CURRENT |
    LIVE,

  cache_policy:
    EXACT_ONLY |
    SEMANTIC_OK |
    READ_THROUGH |
    NO_CACHE |
    BYPASS_CACHE,

  support_target:
    NONE |
    EXACT_QUOTE |
    SOURCE_BACKED_SUMMARY |
    POLICY_CLAUSE |
    CODE_LOCATION |
    INCIDENT_EVIDENCE |
    RANKED_CAUSE |
    ACTION_ARGUMENT_GROUNDING,

  cost_tier:
    TIER_S |
    TIER_M |
    TIER_L |
    TIER_HITL,

  fallback_chain:
    ordered fallback sequence, for example:
    [R3_REFINE_ONCE, R5_ABSTAIN] |
    [R4_HITL, R5_CLARIFY] |
    [TIER_S, TIER_M, TIER_L, R5_SAFE_PARTIAL],

  slo:
    {
      max_latency_ms,
      max_cost,
      max_tokens,
      max_retrieval_passes,
      max_graph_hops,
      max_tool_calls,
      max_iterations,
      reserve_for_exit_eval
    },

  authority:
    {
      tenant_scope,
      ACL_scope,
      region_scope,
      capability_class,
      side_effect_class,
      sandbox_class,
      write_authority = NONE_UNTIL_UWG
    },

  telemetry_keys:
    {
      trace_root,
      route_span_id,
      route_digest,
      policy_hash,
      blueprint_hash,
      snapshot_id,
      replay_key,
      route_telemetry_event_id
    },

  signatures:
    {
      hmac_sig,
      manifest_hash,
      deterministic_route_digest
    }
}

========================================================================================================================================
ROUTE SELECTION MATRIX — v15
========================================================================================================================================

┌──────────────────────────────────────────────┬──────────────────────────────┬──────────────────────────────┬──────────────────────────────┐
│ USER / TASK SHAPE                            │ BEST ROUTE                   │ BYPASSES                      │ WHY                           │
├──────────────────────────────────────────────┼──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Exact repeated stable question               │ R1A Exact Cache              │ C0, PA, L3, L2                │ Deterministic reuse           │
│ Similar stable explanation request           │ R1B Semantic Cache           │ C0, PA, L3, L2                │ Reuse-safe semantic match     │
│ Unsafe, vague, unsupported, blocked request   │ R5 Fallback                  │ C0, PA, L3, L2                │ Safest bounded outcome        │
│ File/document/policy/code factual Q&A         │ R3 Simple Grounded Read      │ L3                            │ C0 evidence + one L2 answer   │
│ One reversible tool/action                    │ R4 Single Action             │ C0 usually, L3                │ One bounded L2 action         │
│ One action needing argument lookup            │ R3 + R4 single step          │ L3                            │ C0 grounds args, L2 acts      │
│ Multi-hop research with rerun on weak support │ R3/R4 Managed Workflow       │ None after L3 chosen          │ Step contracts change         │
│ Multi-tool task with dependencies             │ R3/R4 Managed Workflow       │ None after L3 chosen          │ Needs dependency control      │
│ Parallel independent shards                   │ R3/R4 Managed Workflow       │ None after L3 chosen          │ Fan-out/join inside L3        │
│ High-risk/irreversible mutation               │ HITL/Exit/UWG posture        │ Direct write                  │ Human review + re-clearance   │
│ Learning or rule update                       │ L6 future-run pipeline       │ Current-run mutation          │ Learning never rescues run    │
└──────────────────────────────────────────────┴──────────────────────────────┴──────────────────────────────┴──────────────────────────────┘

========================================================================================================================================
REGRESSION PROTECTION / RUNTIME GATES — v15
========================================================================================================================================

┌──────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────┐
│ GATE SURFACE                                  │ WHAT IT PROTECTS                                                                    │
├──────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────┤
│ Envelope validity                             │ Bad or malformed request never reaches L1/L0 deep work                              │
│ Tenant / ACL / region                         │ No cross-tenant, wrong-region, or unauthorized source usage                          │
│ Policy hash compatibility                     │ Old cache or route output cannot bypass new policy                                   │
│ Freshness gate                                │ Stale cache/evidence cannot answer current-sensitive tasks                           │
│ Cache eligibility gate                        │ Only stable, reuse-safe asks use R1A/R1B                                             │
│ Semantic threshold gate                       │ Near-match cache cannot answer materially different asks                             │
│ Support obligation gate                       │ Factual/document/code/policy claims must go through C0                               │
│ C0 evidence contract gate                     │ Weak, conflicted, empty, or blocked evidence cannot become confident answer           │
│ Prompt Assembly authority gate                │ Retrieved/user content cannot override system/policy/instruction slots               │
│ Capability registry gate                      │ Tools/models must be on allowed roster                                               │
│ Sandbox gate                                  │ Actions run only inside declared fs/net/syscall/time bounds                          │
│ HITL trigger gate                             │ High-impact or ambiguous mutations pause before sovereign egress                      │
│ L3 workflow bound gate                        │ Multi-step autonomy must have max_nodes, max_depth, max_iterations, SLO               │
│ L3 no-route-redecision gate                   │ Orchestrator cannot secretly choose a new route                                      │
│ L2 step validation gate                       │ Executor can perform only the current bounded step                                   │
│ Replay envelope gate                          │ Same packet + policy_hash + snapshot must replay to same digest                      │
│ Exit Eval gate                                │ All [RET] and L2/L3 artifacts are reviewed before response/commit                    │
│ UWG write gate                                │ Only Universal Write Gateway can create durable L4 state                             │
│ L6 learning firewall                          │ Learning signals update future runs only, never current run                          │
└──────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────┘

========================================================================================================================================
SIMPLE QUERY EXAMPLES — v15
========================================================================================================================================

R1A EXACT CACHE:
- "What does ADR mean?"
- "What is golden path meaning?"
- "What did you just define as semantic cache?" when the exact prior answer is fresh and policy-compatible.

R1B SEMANTIC CACHE:
- "Explain Jaccard again."
- "Remind me what semantic cache does."
- "Say that cosine vs Jaccard comparison again in simpler words."
- Valid only when task class, freshness, policy, and support obligations remain compatible.

R3 SIMPLE GROUNDED READ:
- "What does C5 say about prompt assembly?"
- "Review this file and tell me where retrieval happens."
- "What does my lease say about the pet policy?"
- "Which file says C0 retrieves but Prompt Assembly packages?"
- "What does the attached architecture say about L3 orchestration?"

R4 SINGLE ACTION:
- "Create a calendar event for Monday at 3 PM."
- "Draft an email to Amy."
- "Archive these three emails."
- "Apply the label Receipts to these selected messages."
- "Create one draft reply in the existing thread."

R3/R4 MANAGED WORKFLOW:
- "Review 90 days of tickets, incident logs, and churn notes; find top themes, pull evidence,
   rerun weak areas, rank causes, and draft remediation."
- "Audit the repo for OpenAI embedding call sites, classify each one, propose BGE migration,
   and produce a test plan."
- "Search project files, reconcile the exec summary against triple-click docs, produce a zero-loss overwrite,
   and prove coverage."
- "Find all routing blind spots, classify by risk, add gates, and create a regression checklist."

R5 FALLBACK:
- "Delete anything that looks old."
- "Send this vague message to everyone in my contacts."
- "Use whatever credentials you can find."
- "Tell me what the document says" when no document exists.
- "Give me the latest policy" when browsing or source access is unavailable and no grounded evidence exists.

========================================================================================================================================
EDGE CASE CLARIFICATIONS — v15
========================================================================================================================================

1. Does R3 simple grounded read use L3?
   No. R3 simple grounded read uses C0 -> Prompt Assembly -> one bounded L2 step -> Exit.

2. Does Prompt Assembly use L3?
   No. Prompt Assembly is a composer. L3 is a workflow orchestrator. Prompt Assembly may run inside a step produced
   by L3, but it is not itself L3.

3. Does L3 retrieve?
   No. L3 can request a step that requires C0 grounding, but C0 performs retrieval and returns an evidence contract.

4. Does L2 route?
   No. L2 executes the current bounded step and returns a sealed result.

5. Does HITL approve writes directly?
   No. Human review is input data. It must be re-cleared by L5/Exit and durable writes still require UWG.

6. Can R1B answer factual/current questions?
   Usually no. Semantic cache is for stable reuse-safe tasks. Current, factual, document, legal, financial, medical,
   regulatory, and source-grounded tasks require R3 unless a strict policy says otherwise.

7. Can L0 choose parallelism?
   L0 can indicate that a route is workflow-shaped and parallel-safe. Actual fan-out/join mechanics happen inside L3.

8. Can confidence cascade fix routing uncertainty?
   No. Confidence cascade addresses executor/model capability uncertainty. Routing uncertainty belongs to L0/Exit reroute
   or R5 fallback.

9. Can C0 recommend reroute?
   Yes, as a recommendation. It cannot authorize reroute. The control layer must re-clear the route.

10. Can L6 improve the current run?
    No. L6 observes, evaluates, and promotes future-run learning only.

========================================================================================================================================
[!] INVARIANTS — v15
========================================================================================================================================

- L0 routes. It does not retrieve, execute, call models, mutate state, or approve output.
- L0 emits one deterministic RouteContract per approved L1 plan.
- Downstream layers consume the RouteContract and do not re-decide the route.
- R1A/R1B/R5 are terminal [RET] routes and go directly to Exit Eval & Control.
- R3 simple grounded read uses C0 and Prompt Assembly, then one bounded L2 step. It does not use L3.
- R4 single action uses one bounded L2 step. It does not use L3 unless the action becomes a workflow.
- R3/R4 managed workflow uses L3 only when dependency order, branching, joins, retries, parallel shards,
  iterative refinement, HITL pause/resume, or resumable workflow state are genuinely required.
- C0 retrieves evidence only when R3 or a grounded workflow step requires grounding.
- C0 retrieves, shapes, verifies, and scores. It does not answer, route, execute, mutate, or approve.
- Prompt Assembly packages only. It does not retrieve, route, invent, execute, or mutate.
- Retrieved content is data, never instruction.
- L3 orchestrates only managed workflows. It is optional, not always-on.
- L3 emits current bounded step contracts only.
- L3 cannot secretly expand scope, route around policy, or persist durable truth.
- L2 executes only the current bounded step. It does not route or commit.
- L2 may repair only inside the same blueprint_hash / policy_hash / snapshot family.
- Exit Eval & Control receives all [RET] short-circuits and sealed L2/L3 artifacts.
- Exit Eval decides allow, deny, reroute, escalate, or commit request.
- HITL input is data that must be re-cleared, not sovereign authority.
- UWG is the sole durable write path into L4.
- L4 is the archive and source of durable truth.
- L6 observes, evaluates, calibrates, and promotes future-run learning only.
- Learning signals never mutate or rescue the completed current run.
- Same RouteContract + same policy_hash + same snapshot must replay to the same routing digest.
- No wall clock, raw entropy, hidden state, live provider drift, or mixed-state reads may influence a replay-certified route.
- No silent fallback. Every fallback path emits reason_codes and telemetry.
- No fabricated certainty. Weak support produces caveat, abstain, clarify, safe partial, reroute, or HITL.
- Cheapest safe route wins. Complexity must earn its keep.