========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: C0_Context_Engine
Canonical file: C0_Context_Engine_detailed.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: C0_Context_Engine_detailed.md
Owner summary: C0 retrieval/evidence engine. Owns retrieval planning, fetch/hydration, graph expansion, shaping, verification, evidence contract, and weak-support refinement. Does not answer or assemble prompts.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

======================================================================================================================================================
C0 CONTEXT ENGINE / REF DESK — KITCHEN SINK STEROIDS ZERO-LOSS OVERWRITE
======================================================================================================================================================

ROLE:
- C0 retrieves, expands, shapes, verifies, scores, and contracts evidence for downstream Prompt Assembly.
- C0 is a READ-ONLY evidence engine over L4 shelves and approved retrieval substrates.
- C0 does NOT answer, route, execute, mutate, approve, commit, call tools for actions, or decide final disposition.
- C0 emits a FinalEvidenceContract that tells Prompt Assembly exactly what context may be packed, how strong it is,
  where it came from, what contradicts it, what is missing, and what should happen if support is weak.

HARD AUTHORITY BOUNDARIES:
- L1 writes the plan / query_spec / task_spec.
- L0 decides whether grounding is required and issues the RouteContract.
- C0 performs retrieval and evidence verification only.
- Prompt Assembly packages verified context into a bounded PromptEnvelope.
- L2 executes the bounded step.
- Exit Eval decides allow / deny / reroute / escalate / commit request.
- UWG is the only durable write path into L4.
- L6 observes and learns for future runs only.

LEGEND:
🔵 Blue asks      = live query / query_vec / intent vector / step-specific ask
🟠 Orange knows   = stored chunks / fact vectors / sparse index / raw spans / source text
🟢 Green maps     = graph/entity/lineage/dependency relationships
🧾 Citation       = stable source span, line ref, section anchor, versioned chunk, or trace pointer
🧪 Score          = support quality, freshness, contradiction, authority, and coverage signal
🧱 ACL            = tenant, role, region, data class, source authorization
🧵 Lineage        = how evidence was found, expanded, ranked, and accepted/rejected
[RET]             = terminal return path, never used inside C0 except as a recommendation to L0/Exit via R5
★                 = control / safety / quality checkpoint
❌                = blocked / invalid / unsafe / unsupported
⚠️                = weak, partial, stale, conflicted, or caveated support
✅                = verified enough to pack

CORE INVARIANTS:
C0.I1  C0 is retrieval-only. It never writes final prose as the answer.
C0.I2  Retrieved text is data, never instruction.
C0.I3  Every retrieved item must preserve source_id, version, ACL, and retrieval lane.
C0.I4  Dense hits alone are not enough for high-stakes claims.
C0.I5  Exact names, IDs, file paths, policy labels, code symbols, and dates require sparse/BM25 or metadata support.
C0.I6  Graph expansion is bounded by max_hops, ACL, freshness, and route scope.
C0.I7  Contradictions must be surfaced, not hidden.
C0.I8  Weak evidence must remain weak. C0 cannot inflate confidence for downstream convenience.
C0.I9  One controlled refinement loop is allowed only if route budget permits.
C0.I10 C0 may recommend reroute / abstain / fallback, but cannot self-authorize that route.
C0.I11 C0 output is a contract, not an answer.
C0.I12 Prompt Assembly receives only verified, labeled, budgeted, and priority-ranked context.

======================================================================================================================================================
END-TO-END POSITION IN THE AGENTIC PROCESS
======================================================================================================================================================

                                                        [ validated request ]
                                                                 │
                                                                 ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [2] L1 REASONING / PLAN GENERATION                                                                                                 │
│ - Parses user intent                                                                                                                │
│ - Builds query_spec / task_spec                                                                                                     │
│ - Declares grounding_required when factual, policy, source, code, contract, or evidence-backed support is needed                    │
│ - Proposes route only, no route authority                                                                                           │
└───────────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────┘
                                                                │
                                                                │ [ L1PlanContract ]
                                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [3] L0 ROUTING / DISPATCHER                                                                                                         │
│ - Decides if this task uses cache, fallback, simple grounded read, single action, or managed workflow                                │
│ - Emits deterministic RouteContract                                                                                                 │
│ - For grounded routes, commands C0: "build evidence before L2 answers"                                                              │
└───────────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────┘
                                                                │
                                      ┌─────────────────────────┴──────────────────────────┐
                                      │                                                    │
                                      ▼                                                    ▼
                         [ R1 / R5 terminal path ]                           [ R3 / R3-R4 grounded path ]
                         exact cache / semantic cache / fallback              simple grounded read or grounded workflow step
                                      │                                                    │
                                      ▼                                                    ▼
                                  [RET]                                           ┌──────────────────────┐
                                      │                                            │ C0 CONTEXT ENGINE     │
                                      │                                            │ Ref Desk / Research   │
                                      │                                            └──────────┬───────────┘
                                      │                                                       │
                                      │                                                       ▼
                                      │                                            [ FinalEvidenceContract ]
                                      │                                                       │
                                      │                                                       ▼
                                      │                                            ┌──────────────────────┐
                                      │                                            │ PROMPT ASSEMBLY       │
                                      │                                            │ Packet Builder        │
                                      │                                            └──────────┬───────────┘
                                      │                                                       │
                                      │                                                       ▼
                                      │                                            [ bounded PromptEnvelope ]
                                      │                                                       │
                                      │                                                       ▼
                                      │                                            ┌──────────────────────┐
                                      │                                            │ L2 EXECUTE            │
                                      │                                            │ bounded step only     │
                                      │                                            └──────────┬───────────┘
                                      │                                                       │
                                      └─────────────────────────────┬─────────────────────────┘
                                                                    ▼
                                                        [ EXIT EVAL & CONTROL ]
                                                                    │
                                                                    ▼
                                                          [ response / reroute /
                                                            escalation / commit request ]

======================================================================================================================================================
C0 INPUT CONTRACT
======================================================================================================================================================

                                       ┌────────────────────────────────────────────────────────────┐
                                       │ L0 ROUTE CONTRACT                                          │
                                       ├────────────────────────────────────────────────────────────┤
                                       │ route_id: R3_GROUNDED | R3/R4_WORKFLOW_STEP                │
                                       │ grounding_required: true                                   │
                                       │ execution_form: SINGLE_STEP | MANAGED_WORKFLOW_STEP        │
                                       │ freshness_class: static | slow | current | latest           │
                                       │ support_target: quote | summary | clause | code | RCA       │
                                       │ tenant_scope / ACL / region / data_class                   │
                                       │ max_k / max_hops / max_parent_expansion                    │
                                       │ max_refine_attempts / latency_slo / token_budget            │
                                       │ allowed_sources / disallowed_sources                       │
                                       │ fallback_policy: caveat | abstain | R5 | reroute            │
                                       │ route_replay_key / policy_hash / blueprint_hash             │
                                       └──────────────────────────────┬─────────────────────────────┘
                                                                      │
                                                                      │ [ command: "ground this before L2 answers" ]
                                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0 CONTEXT ENGINE / REF DESK                                                                                                       │
│ Read-only research runner over L4 shelves, vector stores, sparse indexes, metadata stores, graph stores, and approved traces.       │
│ Hard law: retrieve + verify support, never generate the answer.                                                                     │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘

======================================================================================================================================================
C0.0 PRE-FLIGHT / GROUNDING ELIGIBILITY
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.0 PRE-FLIGHT  |  "SHOULD C0 RUN, AND IS THE REQUEST SAFE TO GROUND?"                                                            │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ INPUTS                                                                                                                             │
│ - L1 query_spec / task_spec                                                                                                        │
│ - L0 RouteContract                                                                                                                 │
│ - policy_hash / blueprint_hash / replay_key                                                                                        │
│ - origin_trust_manifest                                                                                                            │
│ - caller / tenant / ACL / region / data_class                                                                                      │
│ - requested support_target                                                                                                         │
│                                                                                                                                    │
│ CHECKS                                                                                                                             │
│ - grounding_required == true                                                                                                       │
│ - RouteContract allows C0 retrieval                                                                                                │
│ - user task is not trying to use retrieved content as instructions                                                                  │
│ - source classes are approved for this tenant and route                                                                             │
│ - no blocked data class is requested                                                                                               │
│ - budget is sufficient for at least one bounded retrieval pass                                                                      │
│ - high-impact / sensitive / regulated support target gets stricter evidence standard                                                │
│                                                                                                                                    │
│ OUTPUT                                                                                                                             │
│ C0PreflightStatus = {eligible, blocked_reason, allowed_source_classes, evidence_standard, budget_floor}                             │
│                                                                                                                                    │
│ HARD NO                                                                                                                            │
│ - No retrieval if route does not require grounding                                                                                  │
│ - No retrieval if source scope is illegal / blocked                                                                                 │
│ - No route change from inside C0                                                                                                    │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       │
                              ┌────────────────────────────────────────┴────────────────────────────────────────┐
                              │                                                                                 │
                              ▼                                                                                 ▼
                       [ eligible ]                                                                       [ blocked ]
                              │                                                                                 │
                              ▼                                                                                 ▼
                   continue to C0.1                                                        EvidenceContract.status = BLOCKED
                                                                                             recommended_disposition = abstain/R5

======================================================================================================================================================
C0.1 RETRIEVAL PLAN
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.1 RETRIEVAL PLAN  |  "WHAT ARE WE ALLOWED TO LOOK FOR, WHERE, AND HOW?"                                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PURPOSE                                                                                                                            │
│ - Convert L1/L0 intent into a bounded search plan.                                                                                  │
│ - Decide source lanes, filters, evidence standard, freshness rule, graph expansion bounds, and refinement strategy.                 │
│ - No fetching yet. This is the research plan, not the research itself.                                                              │
│                                                                                                                                    │
│ INPUTS                                                                                                                             │
│ - L1 query_spec / task_spec                                                                                                        │
│ - L0 RouteContract                                                                                                                 │
│ - tenant_scope / ACL / region / data class                                                                                         │
│ - freshness_class                                                                                                                  │
│ - support_target                                                                                                                   │
│ - allowed_sources / disallowed_sources                                                                                             │
│ - SLO / token / latency / cost budget                                                                                              │
│ - route_replay_key / policy_hash / blueprint_hash                                                                                  │
│                                                                                                                                    │
│ SUPPORT TARGET TYPES                                                                                                               │
│ - EXACT_QUOTE: needs direct source span and stable citation anchor                                                                  │
│ - SOURCE_SUMMARY: needs multiple supporting spans and no hidden contradictions                                                      │
│ - POLICY_CLAUSE: needs exact policy version, date, and clause anchor                                                                │
│ - CODE_LOCATION: needs file path, symbol, line/span, and version                                                                    │
│ - INCIDENT_EVIDENCE: needs trace/log/ticket lineage and time bounds                                                                 │
│ - ROOT_CAUSE_RANKING: needs multiple sources, conflict handling, and ranked evidence                                                │
│ - COMPARISON: needs source parity across compared items                                                                             │
│ - CLAIM_CHECK: needs direct support or explicit caveat                                                                              │
│                                                                                                                                    │
│ SOURCE CLASS DECISIONS                                                                                                             │
│ - docs: design docs, specs, ADRs, READMEs, manuals                                                                                  │
│ - code: files, symbols, callsites, tests, configs                                                                                   │
│ - logs: traces, OTEL spans, run logs, error logs                                                                                    │
│ - tickets: issues, support tickets, customer feedback, incidents                                                                    │
│ - tables: CSVs, warehouses, metrics exports, eval reports                                                                           │
│ - policy: compliance docs, SOPs, governance rules                                                                                   │
│ - prior artifacts: sealed runs, eval bundles, RCA notes, promotion receipts                                                         │
│                                                                                                                                    │
│ RETRIEVAL MODE DECISIONS                                                                                                           │
│ - dense vector search: semantic recall and paraphrase match                                                                         │
│ - sparse/BM25 search: exact names, IDs, paths, policy labels, dates, symbols                                                        │
│ - metadata search: tenant, time, source type, author, version, region                                                               │
│ - graph traverse: entities, dependencies, lineage, ownership, contradictions                                                       │
│ - cache lookup: only when freshness and policy permit                                                                               │
│ - hybrid fusion: combine dense + sparse + graph + metadata signals                                                                  │
│                                                                                                                                    │
│ BOUNDS                                                                                                                             │
│ - max_k                                                                                                                            │
│ - max_parent_expansion                                                                                                             │
│ - max_child_expansion                                                                                                              │
│ - max_graph_hops                                                                                                                   │
│ - max_refine_attempts                                                                                                              │
│ - max_token_context                                                                                                                │
│ - max_source_classes                                                                                                               │
│ - max_latency_ms                                                                                                                   │
│ - max_cost_tier                                                                                                                    │
│                                                                                                                                    │
│ OUTPUT                                                                                                                             │
│ RetrievalPlan = {                                                                                                                  │
│   source_classes, allowed_sources, disallowed_sources, filters, retrieval_modes,                                                   │
│   support_target, freshness_rule, evidence_standard, graph_bounds,                                                                  │
│   dense_query_spec, sparse_query_spec, metadata_filters, cache_policy,                                                              │
│   budgets, weak_support_policy, replay_metadata                                                                                     │
│ }                                                                                                                                  │
│                                                                                                                                    │
│ HARD NO                                                                                                                            │
│ - No fetching yet                                                                                                                  │
│ - No answering                                                                                                                     │
│ - No route change                                                                                                                  │
│ - No source expansion beyond RouteContract                                                                                         │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       │ [ bounded search parameters ]
                                                                       ▼

======================================================================================================================================================
C0.2 EVIDENCE FETCH
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.2 EVIDENCE FETCH  |  "FIND CANDIDATE SUPPORT WITHOUT TRUSTING IT YET"                                                          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PURPOSE                                                                                                                            │
│ - Execute the planned retrieval lanes.                                                                                              │
│ - Gather candidate evidence with lane provenance and metadata.                                                                      │
│ - Preserve enough surrounding context for later verification.                                                                       │
│                                                                                                                                    │
│ LIVE QUERY PATH                                                                                                                    │
│                                                                                                                                    │
│   user/query text                                                                                                                  │
│        │                                                                                                                           │
│        ▼                                                                                                                           │
│   encoder model                                                                                                                    │
│        │                                                                                                                           │
│        ▼                                                                                                                           │
│   🔵 query_vec / intent vector                                                                                                      │
│                                                                                                                                    │
│ SEARCH LANES                                                                                                                       │
│                                                                                                                                    │
│   🔵 query_vec ───────────────► 🟠 dense fact/context vectors        = semantic recall / paraphrase match                         │
│   exact query terms ─────────► 🟠 sparse/BM25 index                 = names, IDs, symbols, filenames, policy labels               │
│   metadata filters ──────────► 🟠 source metadata                   = tenant, time, author, version, region, source type          │
│   cache if permitted ────────► 🟠 reusable prior context            = only if freshness + policy allow                            │
│   trace query if permitted ──► 🟠 runtime spans/logs                = exact run / trace / incident evidence                       │
│   code index if permitted ───► 🟠 file/symbol index                 = definitions, imports, callsites, configs                    │
│                                                                                                                                    │
│ DENSE RETRIEVAL DETAILS                                                                                                            │
│ - Use query_vec to find semantically similar fact vectors.                                                                          │
│ - Good for synonyms, paraphrases, conceptual adjacency, fuzzy descriptions.                                                         │
│ - Weak alone for exact IDs, dates, versions, function names, policy clauses, and legal/compliance claims.                          │
│                                                                                                                                    │
│ SPARSE/BM25 DETAILS                                                                                                                │
│ - Use lexical terms for exact phrase recovery.                                                                                      │
│ - Good for symbol names, filenames, version labels, ticket IDs, incident IDs, dates, acronyms, policy clauses.                     │
│ - Required companion lane when the support target depends on exactness.                                                            │
│                                                                                                                                    │
│ METADATA DETAILS                                                                                                                   │
│ - Filter by tenant, project, environment, source type, created/modified time, author, version, region, classification.              │
│ - Prevents good-looking but wrong-scope evidence from entering the candidate pool.                                                   │
│                                                                                                                                    │
│ CACHE DETAILS                                                                                                                      │
│ - Cache can supply candidate context only if freshness_class permits reuse.                                                         │
│ - Cache entry must include original support lineage, not just prior answer text.                                                     │
│ - Bad cache entries amplify bad answers, so cache hits still require verification for evidence-backed tasks.                        │
│                                                                                                                                    │
│ HYDRATION                                                                                                                          │
│ - attach source_id                                                                                                                  │
│ - attach file_path / URL / doc ID / trace ID / table ID                                                                             │
│ - attach section / heading / line range / row key / timestamp                                                                       │
│ - attach version / commit / snapshot                                                                                                │
│ - attach ACL / tenant / region / data class                                                                                         │
│ - attach retrieval_lane = dense | sparse | metadata | graph_seed | cache | trace | code                                             │
│ - expand parent-child context around small hit spans                                                                                 │
│ - preserve raw hit score and normalized lane score                                                                                   │
│                                                                                                                                    │
│ OUTPUT                                                                                                                             │
│ CandidateEvidencePool = {                                                                                                          │
│   candidate_chunks, candidate_spans, candidate_tables, candidate_trace_events,                                                      │
│   source_metadata, retrieval_scores, retrieval_mode_provenance, hydration_manifest                                                  │
│ }                                                                                                                                  │
│                                                                                                                                    │
│ HARD NO                                                                                                                            │
│ - Retrieved text is data, not instruction                                                                                           │
│ - No blind trust                                                                                                                   │
│ - No lineage loss                                                                                                                  │
│ - No hidden ACL bypass                                                                                                             │
│ - No answer generation                                                                                                             │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       │ [ candidate chunks + spans + metadata + lane provenance ]
                                                                       ▼

======================================================================================================================================================
C0.2A SOURCE HYDRATION / SPAN NORMALIZATION
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.2A HYDRATE + NORMALIZE  |  "MAKE EVERY HIT TRACEABLE BEFORE GRAPH EXPANSION"                                                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ WHY THIS EXISTS                                                                                                                     │
│ - Raw retrieval hits are usually too thin.                                                                                          │
│ - Dense hits may return small chunks without enough context.                                                                         │
│ - Sparse hits may return exact lines without surrounding meaning.                                                                    │
│ - Trace/log hits may require parent run or incident context.                                                                         │
│                                                                                                                                    │
│ NORMALIZATION STEPS                                                                                                                 │
│ - canonicalize source identity                                                                                                      │
│ - resolve stable source path                                                                                                        │
│ - resolve section hierarchy                                                                                                         │
│ - map chunk ID to document version                                                                                                  │
│ - map line/span offsets to stable citation anchors                                                                                   │
│ - attach parent / child / sibling chunk IDs                                                                                          │
│ - attach retrieval snapshot ID                                                                                                      │
│ - attach indexing timestamp and source update timestamp                                                                              │
│ - attach source authority class                                                                                                     │
│                                                                                                                                    │
│ QUALITY FLAGS                                                                                                                       │
│ - span_resolves: true/false                                                                                                         │
│ - source_version_current: true/false/unknown                                                                                        │
│ - acl_clear: true/false                                                                                                             │
│ - parent_context_available: true/false                                                                                              │
│ - citation_anchor_stable: true/false                                                                                                │
│ - chunk_boundary_risk: low/medium/high                                                                                              │
│                                                                                                                                    │
│ OUTPUT                                                                                                                             │
│ HydratedEvidencePool = {candidate_pool + resolved_source_metadata + citation_anchor_candidates + hydration_flags}                   │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼

======================================================================================================================================================
C0.3 GRAPH TRAVERSE
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.3 GRAPH TRAVERSE  |  "FOLLOW THE CARD CATALOG WITHOUT ESCAPING SCOPE"                                                          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PURPOSE                                                                                                                            │
│ - Use graph relationships to add context, definitions, owners, dependencies, contradictions, and lineage.                           │
│ - Improve evidence quality without turning retrieval into unbounded exploration.                                                    │
│                                                                                                                                    │
│ START                                                                                                                              │
│ Candidate chunks / spans / rows / traces                                                                                            │
│        │                                                                                                                           │
│        ▼                                                                                                                           │
│ entity extraction / symbol extraction / source anchor mapping                                                                       │
│                                                                                                                                    │
│ 🟢 BOUNDED GRAPH HOPS                                                                                                               │
│                                                                                                                                    │
│   candidate span ──► parent document / section                                                                                      │
│                  ├─► referenced file / module / class / function                                                                    │
│                  ├─► owner / author / service / component                                                                           │
│                  ├─► policy / ADR / schema / glossary                                                                               │
│                  ├─► upstream dependency                                                                                            │
│                  ├─► downstream dependency                                                                                          │
│                  ├─► incident / trace / ticket cluster                                                                              │
│                  ├─► prior sealed run / eval bundle                                                                                 │
│                  ├─► contradiction or alternate source                                                                               │
│                  └─► source lineage / version lineage                                                                               │
│                                                                                                                                    │
│ GRAPH RELATION TYPES                                                                                                                │
│ - defines                                                                                                                           │
│ - references                                                                                                                        │
│ - imports                                                                                                                           │
│ - calls                                                                                                                             │
│ - owns                                                                                                                              │
│ - depends_on                                                                                                                        │
│ - supersedes                                                                                                                        │
│ - contradicts                                                                                                                       │
│ - duplicates                                                                                                                        │
│ - implements                                                                                                                        │
│ - governed_by                                                                                                                       │
│ - derived_from                                                                                                                      │
│ - observed_in                                                                                                                       │
│ - remediated_by                                                                                                                     │
│                                                                                                                                    │
│ CONTROL                                                                                                                            │
│ - max_hops enforced                                                                                                                │
│ - ACL enforced at every hop                                                                                                         │
│ - freshness enforced after expansion                                                                                                │
│ - relation type preserved                                                                                                           │
│ - source class preserved                                                                                                            │
│ - graph traversal must remain tied to support_target                                                                                │
│ - no open-ended browsing of graph                                                                                                   │
│                                                                                                                                    │
│ GRAPH EXPANSION ACCEPTANCE RULES                                                                                                    │
│ - accept if it directly clarifies candidate evidence                                                                                 │
│ - accept if it provides authoritative definition or version context                                                                  │
│ - accept if it reveals contradiction or caveat                                                                                       │
│ - accept if it provides source lineage                                                                                               │
│ - reject if it is merely interesting but not support-relevant                                                                        │
│ - reject if ACL / tenant / region / freshness fails                                                                                  │
│                                                                                                                                    │
│ OUTPUT                                                                                                                             │
│ GraphExpandedEvidencePool = {                                                                                                      │
│   original_candidates, graph_neighbors, entity_map, relation_map, lineage_edges,                                                     │
│   conflict_candidates, dependency_context, source_authority_context                                                                  │
│ }                                                                                                                                  │
│                                                                                                                                    │
│ HARD NO                                                                                                                            │
│ - No ACL escape through graph neighbors                                                                                             │
│ - No durable memory promotion                                                                                                       │
│ - No unbounded graph walk                                                                                                           │
│ - No self-routing into workflow                                                                                                     │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       │ [ graph-expanded evidence pool ]
                                                                       ▼

======================================================================================================================================================
C0.4 SHAPE / RERANK / STRATIFY
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.4 SHAPE  |  "CLEAN, RANK, COMPRESS, AND STRUCTURE THE EVIDENCE PILE"                                                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PURPOSE                                                                                                                            │
│ - Turn a noisy candidate pool into a compact, ranked, source-safe evidence set.                                                     │
│ - Preserve the best support, contradictions, and caveats.                                                                           │
│ - Remove weak, redundant, stale, out-of-scope, or unsafe evidence.                                                                  │
│                                                                                                                                    │
│ DEDUPE                                                                                                                             │
│ - collapse duplicate chunks                                                                                                         │
│ - merge dense + sparse duplicate hits                                                                                               │
│ - merge parent/child duplicates                                                                                                     │
│ - keep strongest citation span                                                                                                      │
│ - preserve retrieval lane provenance even when deduping                                                                             │
│ - mark near-duplicates as duplicate_of                                                                                              │
│                                                                                                                                    │
│ RERANK SIGNALS                                                                                                                     │
│ - relevance to support_target                                                                                                       │
│ - directness of support                                                                                                             │
│ - source authority                                                                                                                  │
│ - freshness match                                                                                                                   │
│ - citation anchor stability                                                                                                         │
│ - graph proximity                                                                                                                   │
│ - exact lexical support                                                                                                             │
│ - dense semantic support                                                                                                            │
│ - metadata fit                                                                                                                      │
│ - contradiction value                                                                                                               │
│ - source diversity                                                                                                                  │
│ - coverage contribution                                                                                                             │
│ - risk of quote distortion                                                                                                          │
│ - ACL cleanliness                                                                                                                   │
│                                                                                                                                    │
│ PRUNE                                                                                                                              │
│ - remove stale sources unless needed as historical evidence                                                                          │
│ - remove weak-lineage material                                                                                                      │
│ - remove low relevance material                                                                                                     │
│ - remove ACL-risky material                                                                                                         │
│ - remove redundant payload                                                                                                          │
│ - remove instruction-like retrieved content from prompt-eligible context unless neutralized                                         │
│ - preserve enough surrounding context to avoid quote distortion                                                                      │
│                                                                                                                                    │
│ STRATIFY                                                                                                                           │
│   MUST_USE      = required to answer safely                                                                                         │
│   SUPPORTING    = helpful evidence but not sufficient alone                                                                          │
│   CONTRADICTS   = credible conflict, caveat, disagreement, version mismatch                                                         │
│   BACKGROUND    = optional explanatory context                                                                                       │
│   DEFINITIONS   = glossary / acronym / concept anchors                                                                               │
│   LINEAGE       = source/version/dependency provenance                                                                                │
│   EXCLUDED      = removed with reason                                                                                                │
│                                                                                                                                    │
│ COMPRESSION                                                                                                                        │
│ - preserve citation-bearing spans first                                                                                              │
│ - compress background before must-use evidence                                                                                       │
│ - keep exact quoted text when exact quote is required                                                                                │
│ - keep source diversity when claims depend on multiple sources                                                                       │
│ - keep contradiction snippets even if uncomfortable                                                                                  │
│ - discard decorative or repeated language                                                                                            │
│                                                                                                                                    │
│ OUTPUT                                                                                                                             │
│ ShapedEvidenceSet = {                                                                                                               │
│   ranked_evidence, must_use, supporting, contradicts, background, definitions, lineage,                                              │
│   excluded_with_reasons, compression_manifest, token_estimate                                                                        │
│ }                                                                                                                                  │
│                                                                                                                                    │
│ HARD NO                                                                                                                            │
│ - Do not hide contradictions                                                                                                        │
│ - Do not pad with weak evidence                                                                                                     │
│ - Do not optimize for fake confidence                                                                                               │
│ - Do not discard lineage                                                                                                            │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       │ [ ranked + stratified evidence ]
                                                                       ▼

======================================================================================================================================================
C0.4A CONTRADICTION / GAP HANDLING
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.4A CONTRADICTION + GAP SCAN  |  "WHAT WOULD MAKE THE DOWNSTREAM ANSWER WRONG?"                                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CONTRADICTION TYPES                                                                                                                │
│ - version contradiction: newer source supersedes older source                                                                        │
│ - source contradiction: two authoritative sources disagree                                                                           │
│ - scope contradiction: evidence applies to wrong tenant / product / region                                                          │
│ - time contradiction: evidence applies to old policy / old release / old incident window                                            │
│ - semantic contradiction: similar words refer to different concepts                                                                  │
│ - code contradiction: docs say one thing, implementation says another                                                               │
│ - runtime contradiction: design says expected behavior, traces show different behavior                                               │
│ - policy contradiction: action is technically possible but prohibited                                                               │
│                                                                                                                                    │
│ GAP TYPES                                                                                                                          │
│ - missing direct support                                                                                                            │
│ - missing exact quote                                                                                                               │
│ - missing current version                                                                                                           │
│ - missing owner / authority                                                                                                         │
│ - missing source diversity                                                                                                          │
│ - missing code/test/runtime validation                                                                                              │
│ - missing citation anchor                                                                                                           │
│ - missing time range                                                                                                                │
│ - missing tenant/ACL proof                                                                                                          │
│                                                                                                                                    │
│ OUTPUT                                                                                                                             │
│ ConflictGapReport = {contradiction_flags, unresolved_gaps, likely_failure_modes, recommended_refine_tactic}                         │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼

======================================================================================================================================================
C0.5 EVIDENCE CONTRACT
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.5 EVIDENCE CONTRACT  |  "VERIFY SPANS AND SCORE WHETHER SUPPORT IS GOOD ENOUGH"                                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PURPOSE                                                                                                                            │
│ - Convert shaped evidence into a strict downstream contract.                                                                         │
│ - Verify that the evidence is citeable, current enough, authorized, and strong enough for the support target.                        │
│                                                                                                                                    │
│ VERIFY                                                                                                                             │
│ - source_id resolves                                                                                                                │
│ - cited span resolves                                                                                                               │
│ - line ref / section anchor resolves                                                                                                │
│ - document version matches retrieval snapshot                                                                                       │
│ - citation anchor is stable                                                                                                         │
│ - source is ACL-cleared                                                                                                             │
│ - source is within tenant / region / data class                                                                                     │
│ - retrieved content is classified as data, not instruction                                                                          │
│ - graph lineage is bounded and valid                                                                                                │
│ - cache source includes original evidence lineage if used                                                                            │
│                                                                                                                                    │
│ SCORE DIMENSIONS                                                                                                                   │
│ - direct_support_score                                                                                                              │
│ - coverage_score                                                                                                                    │
│ - source_authority_score                                                                                                            │
│ - freshness_score                                                                                                                   │
│ - contradiction_risk                                                                                                                │
│ - unsupported_inference_risk                                                                                                        │
│ - citation_stability_score                                                                                                          │
│ - lineage_quality_score                                                                                                             │
│ - source_diversity_score                                                                                                            │
│ - exactness_score                                                                                                                   │
│ - ACL_confidence                                                                                                                    │
│                                                                                                                                    │
│ SUPPORT STATUS                                                                                                                     │
│   PASS              = enough direct support                                                                                         │
│   WEAK              = partial support, refinement may help                                                                           │
│   WEAK_WITH_CAVEATS = usable only if downstream answer explicitly caveats                                                           │
│   CONFLICTED        = credible sources disagree                                                                                      │
│   EMPTY             = no usable evidence                                                                                            │
│   BLOCKED           = source/policy/ACL prevents use                                                                                 │
│                                                                                                                                    │
│ SCORING INTUITION                                                                                                                  │
│ - PASS requires direct evidence for the core claim, not just thematic similarity.                                                    │
│ - WEAK may support partial answer or caveated response.                                                                              │
│ - CONFLICTED requires downstream answer to acknowledge disagreement or avoid conclusion.                                             │
│ - EMPTY requires abstain or clarify.                                                                                                │
│ - BLOCKED requires policy-safe refusal / fallback.                                                                                  │
│                                                                                                                                    │
│ OUTPUT                                                                                                                             │
│ EvidenceContract = {                                                                                                                │
│   status, support_score, score_breakdown, verified_chunks, cited_spans, source_ids,                                                  │
│   contradiction_flags, unresolved_gaps, lineage, freshness_report, ACL_report,                                                       │
│   prompt_budget_hint, recommended_disposition                                                                                        │
│ }                                                                                                                                  │
│                                                                                                                                    │
│ HARD NO                                                                                                                            │
│ - No vibes-based answering                                                                                                          │
│ - No overstating weak support                                                                                                       │
│ - No hiding unresolved gaps                                                                                                         │
│ - No fabricated citation anchors                                                                                                    │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       │
                         ┌─────────────────────────────────────────────┴──────────────────────────────────────────────┐
                         │                                                                                            │
                         │ status = PASS / usable                                                                     │ status = WEAK / CONFLICTED / EMPTY / BLOCKED
                         ▼                                                                                            ▼

======================================================================================================================================================
PASS PATH VS REFINE PATH
======================================================================================================================================================

┌──────────────────────────────────────────────────────────────────────────────────┐          ┌──────────────────────────────────────────────────────────────────────────────┐
│ READY FOR PROMPT ASSEMBLY                                                       │          │ C0.6 REFINE / BROADEN / DECOMPOSE                                           │
├──────────────────────────────────────────────────────────────────────────────────┤          │ "ONE CONTROLLED SECOND PASS IF SUPPORT IS WEAK"                             │
│ ✅ direct support exists                                                        │          ├──────────────────────────────────────────────────────────────────────────────┤
│ ✅ cited spans verified                                                         │          │ DIAGNOSE                                                                     │
│ ✅ source IDs resolve                                                           │          │ - wrong terms                                                                 │
│ ✅ ACL cleared                                                                  │          │ - query too narrow                                                            │
│ ✅ freshness acceptable                                                         │          │ - query too broad                                                             │
│ ✅ contradictions/gaps explicitly labeled                                       │          │ - stale sources                                                               │
│ ✅ prompt packing priority is clear                                             │          │ - missing graph neighbor                                                      │
│                                                                                 │          │ - source class omitted                                                        │
│ OUTPUT                                                                          │          │ - exact phrase missing                                                        │
│ - FinalEvidenceContract proceeds to Prompt Assembly                             │          │ - contradiction                                                               │
│ - downstream answer may still need caveats if status is WEAK_WITH_CAVEATS       │          │ - ACL blocked                                                                 │
└──────────────────────────────────────┬───────────────────────────────────────────┘          │ - support target too compound                                                 │
                                       │                                                      │                                                                                │
                                       │                                                      │ CHOOSE ONE TACTIC                                                             │
                                       │                                                      │   REWRITE   = same intent, better words                                       │
                                       │                                                      │   BROADEN   = widen synonyms/source class within ACL                          │
                                       │                                                      │   NARROW    = add exact entity/file/time filter                               │
                                       │                                                      │   DECOMPOSE = split compound support target                                   │
                                       │                                                      │   GRAPH_HOP = one bounded 🟢 relation hop                                      │
                                       │                                                      │   HYBRIDIZE = add sparse if dense-only failed                                  │
                                       │                                                      │   FRESHEN   = force current-version filter                                     │
                                       │                                                      │   ABSTAIN   = cannot safely recover support                                   │
                                       │                                                      │                                                                                │
                                       │                                                      │ GUARDS                                                                         │
                                       │                                                      │ - no infinite loop                                                            │
                                       │                                                      │ - no source escape                                                            │
                                       │                                                      │ - no budget overrun                                                           │
                                       │                                                      │ - no route rewrite by C0                                                      │
                                       │                                                      │ - no unsupported source class addition                                         │
                                       │                                                      │ - no weakening ACL to improve recall                                           │
                                       │                                                      │ - if task became workflow-sized, recommend reroute but do not self-authorize   │
                                       │                                                      └──────────────────────────────────────┬───────────────────────────────────────┘
                                       │                                                                             │
                                       │                                                                             ▼
                                       │                                                              [ bounded second retrieval pass ]
                                       │                                                                             │
                                       │                                                                             ▼
                                       │                                                              [ re-score through C0.4 + C0.5 ]
                                       │                                                                             │
                                       │                                  ┌──────────────────────────────────────────┴──────────────────────────────────────────┐
                                       │                                  │                                                                                     │
                                       │                                  ▼                                                                                     ▼
                                       │                    [ PASS / WEAK_WITH_CAVEATS ]                                                       [ EMPTY / BLOCKED / unsafe ]
                                       │                                  │                                                                                     │
                                       └──────────────────────────────────┴───────────────────────────────────────┐                                             │
                                                                                                                  │                                             ▼
                                                                                                                  │                                [ recommend R5 fallback / abstain ]
                                                                                                                  │
                                                                                                                  ▼

======================================================================================================================================================
C0.6 CONTROLLED REFINEMENT LOOP
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0.6 REFINE LOOP  |  "FIX THE SEARCH, NOT THE FACTS"                                                                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ENTRY CONDITIONS                                                                                                                    │
│ - EvidenceContract.status in {WEAK, CONFLICTED, EMPTY}                                                                              │
│ - RouteContract permits refine attempt                                                                                              │
│ - budget remaining                                                                                                                  │
│ - source scope still valid                                                                                                          │
│ - support target still unchanged                                                                                                    │
│                                                                                                                                    │
│ ALLOWED REFINEMENTS                                                                                                                 │
│ - rewrite query terms                                                                                                               │
│ - add exact sparse terms                                                                                                            │
│ - add metadata filter                                                                                                               │
│ - broaden synonyms within same allowed source class                                                                                  │
│ - narrow by entity / file / date / version                                                                                           │
│ - decompose compound target into sub-targets                                                                                         │
│ - perform one bounded graph hop                                                                                                     │
│ - switch fusion weights between dense/sparse/metadata                                                                                │
│                                                                                                                                    │
│ DISALLOWED REFINEMENTS                                                                                                              │
│ - changing the user task                                                                                                            │
│ - changing the route                                                                                                                │
│ - expanding tenant / ACL / region                                                                                                   │
│ - ignoring contradictions                                                                                                           │
│ - inventing source authority                                                                                                        │
│ - turning a read task into an action task                                                                                            │
│ - modifying durable memory                                                                                                          │
│                                                                                                                                    │
│ EXIT CONDITIONS                                                                                                                     │
│ - PASS                                                                                                                              │
│ - WEAK_WITH_CAVEATS                                                                                                                 │
│ - CONFLICTED                                                                                                                        │
│ - EMPTY                                                                                                                             │
│ - BLOCKED                                                                                                                           │
│ - budget_exhausted                                                                                                                  │
│ - unsafe_to_continue                                                                                                                │
│                                                                                                                                    │
│ OUTPUT                                                                                                                             │
│ RefinedEvidenceContract = EvidenceContract + {refine_attempts, refine_tactic, refine_delta, remaining_gaps}                         │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼

======================================================================================================================================================
FINAL C0 EVIDENCE CONTRACT
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FINAL C0 EVIDENCE CONTRACT                                                                                                         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ status:                                                                                                                            │
│   PASS | WEAK_WITH_CAVEATS | CONFLICTED | EMPTY | BLOCKED                                                                          │
│                                                                                                                                    │
│ support_score:                                                                                                                     │
│   0.00 - 1.00                                                                                                                      │
│                                                                                                                                    │
│ score_breakdown:                                                                                                                   │
│   direct_support_score                                                                                                             │
│   coverage_score                                                                                                                   │
│   source_authority_score                                                                                                           │
│   freshness_score                                                                                                                  │
│   citation_stability_score                                                                                                         │
│   lineage_quality_score                                                                                                            │
│   exactness_score                                                                                                                  │
│   contradiction_risk                                                                                                               │
│   unsupported_inference_risk                                                                                                       │
│                                                                                                                                    │
│ verified_chunks:                                                                                                                   │
│   stable chunk IDs / row IDs / trace IDs / code spans                                                                               │
│                                                                                                                                    │
│ cited_spans:                                                                                                                       │
│   exact spans / line refs / section anchors / timestamps / table rows                                                               │
│                                                                                                                                    │
│ source_ids:                                                                                                                        │
│   doc IDs / file paths / version IDs / commit IDs / trace IDs / ticket IDs                                                          │
│                                                                                                                                    │
│ evidence_classes:                                                                                                                  │
│   MUST_USE / SUPPORTING / CONTRADICTS / BACKGROUND / DEFINITIONS / LINEAGE / EXCLUDED                                               │
│                                                                                                                                    │
│ contradiction_flags:                                                                                                               │
│   explicit conflicts, supersession issues, stale/new mismatch, docs-vs-code mismatch, policy-vs-runtime mismatch                    │
│                                                                                                                                    │
│ unresolved_gaps:                                                                                                                   │
│   missing support items, missing current version, missing exact span, missing source class, missing validation                       │
│                                                                                                                                    │
│ freshness_report:                                                                                                                  │
│   source age vs freshness_class, version currency, stale-source risk                                                                 │
│                                                                                                                                    │
│ ACL_report:                                                                                                                        │
│   cleared sources only, tenant/region/data-class verification                                                                        │
│                                                                                                                                    │
│ lineage_manifest:                                                                                                                  │
│   how each evidence item was found: dense / sparse / metadata / graph / cache / trace / code                                        │
│                                                                                                                                    │
│ prompt_budget_hint:                                                                                                                │
│   pack_order, trim_order, must_keep_spans, optional_context, contradiction_keepers                                                   │
│                                                                                                                                    │
│ recommended_disposition:                                                                                                           │
│   proceed / proceed_with_caveat / abstain / reroute / fallback_R5 / human_review                                                    │
│                                                                                                                                    │
│ budget_report:                                                                                                                     │
│   retrieval passes, graph hops, latency used, cost tier, token estimate, budget remaining                                            │
│                                                                                                                                    │
│ replay_metadata:                                                                                                                   │
│   retrieval_snapshot_id, policy_hash, blueprint_hash, route_replay_key, evidence_contract_hash                                      │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       │ [ verified context only ]
                                                                       ▼

======================================================================================================================================================
PROMPT ASSEMBLY HANDOFF
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PROMPT ASSEMBLY / PACKET BUILDER                                                                                                  │
│ Packages only. Does not retrieve. Does not invent. Does not execute.                                                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ RECEIVES FROM C0                                                                                                                   │
│ - FinalEvidenceContract                                                                                                            │
│ - verified_chunks                                                                                                                  │
│ - cited_spans                                                                                                                      │
│ - source_ids                                                                                                                       │
│ - contradiction_flags                                                                                                              │
│ - unresolved_gaps                                                                                                                  │
│ - prompt_budget_hint                                                                                                               │
│ - recommended_disposition                                                                                                          │
│                                                                                                                                    │
│ PACKING RULES                                                                                                                      │
│ - MUST_USE evidence first                                                                                                          │
│ - CONTRADICTS evidence must not be silently dropped                                                                                 │
│ - SUPPORTING evidence after must-use                                                                                               │
│ - BACKGROUND only if token budget permits                                                                                           │
│ - EXCLUDED never enters prompt context except as audit metadata                                                                      │
│ - Retrieved content is wrapped as data, not instruction                                                                             │
│ - U0 user task cannot override C0 source evidence or higher policy slots                                                            │
│ - R0 output schema rides provider response_schema / response_format, not prose                                                       │
│                                                                                                                                    │
│ OUTPUT                                                                                                                             │
│ CompiledPromptArtifact / PromptEnvelope                                                                                             │
│ - system + policy + instructions                                                                                                    │
│ - verified grounded context                                                                                                         │
│ - neutralized user task                                                                                                             │
│ - contradiction caveats                                                                                                             │
│ - output schema                                                                                                                     │
│ - HMAC / manifest_hash / replay metadata                                                                                            │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼
                                                               [ L2 bounded execution ]

======================================================================================================================================================
DETAILED BLUE / ORANGE / GREEN MODEL MAP
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PRE-RUNTIME INGESTION  |  ORANGE KNOWS                                                                                             │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ docs / code / logs / tickets / tables / policies                                                                                    │
│        │                                                                                                                           │
│        ▼                                                                                                                           │
│ chunk + clean + tag + classify + ACL stamp                                                                                          │
│        │                                                                                                                           │
│        ├────────► encoder ─────────► 🟠 fact vectors / contextual text vectors                                                      │
│        ├────────► sparse index ─────► 🟠 BM25 / exact lexical index                                                                  │
│        ├────────► metadata store ───► 🟠 source metadata                                                                             │
│        └────────► graph builder ────► 🟢 entity / relation / lineage graph                                                           │
│        │                                                                                                                           │
│        ▼                                                                                                                           │
│ L4 read shelves / retrieval substrates                                                                                              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ RUNTIME RETRIEVAL  |  BLUE ASKS AGAINST ORANGE KNOWS AND GREEN MAPS                                                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ live user task / L1 query_spec / L0 RouteContract                                                                                    │
│        │                                                                                                                           │
│        ▼                                                                                                                           │
│ encoder                                                                                                                            │
│        │                                                                                                                           │
│        ▼                                                                                                                           │
│ 🔵 query_vec / intent vector                                                                                                        │
│        │                                                                                                                           │
│        ├────────► compare to 🟠 fact vectors                                                                                         │
│        ├────────► combine with 🟠 sparse/BM25 terms                                                                                  │
│        ├────────► filter by 🟠 metadata                                                                                              │
│        └────────► expand through 🟢 graph relationships                                                                               │
│        │                                                                                                                           │
│        ▼                                                                                                                           │
│ CandidateEvidencePool -> GraphExpandedEvidencePool -> ShapedEvidenceSet -> EvidenceContract                                         │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DOWNSTREAM GENERATION  |  C0 DOES NOT GENERATE                                                                                      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FinalEvidenceContract                                                                                                               │
│        │                                                                                                                           │
│        ▼                                                                                                                           │
│ Prompt Assembly packs context                                                                                                       │
│        │                                                                                                                           │
│        ▼                                                                                                                           │
│ L2 model/tool execution                                                                                                             │
│        │                                                                                                                           │
│        ▼                                                                                                                           │
│ Exit Eval verifies output before response / commit                                                                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

======================================================================================================================================================
QUALITY GATES INSIDE C0
======================================================================================================================================================

┌───────────────┬──────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┐
│ GATE          │ QUESTION                                             │ FAIL BEHAVIOR                                                 │
├───────────────┼──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ C0.G0 Scope   │ Is C0 allowed to retrieve for this route?             │ BLOCKED / recommend R5 or reroute                              │
│ C0.G1 ACL     │ Is every source tenant/region/data-class cleared?     │ Exclude source or BLOCKED                                      │
│ C0.G2 Fresh   │ Is evidence current enough for freshness_class?       │ Mark stale, search newer, caveat, or reject                    │
│ C0.G3 Exact   │ Are exact claims backed by sparse/metadata support?   │ WEAK unless exact lane confirms                                │
│ C0.G4 Dense   │ Are semantic hits directly relevant?                  │ Prune weak hits                                                 │
│ C0.G5 Graph   │ Are graph hops bounded and support-relevant?          │ Stop traversal / exclude neighbor                              │
│ C0.G6 Cite    │ Do spans resolve to stable anchors?                   │ Exclude or downgrade                                           │
│ C0.G7 Conflict│ Are contradictions surfaced?                          │ Add CONTRADICTS or mark CONFLICTED                             │
│ C0.G8 Cover   │ Does evidence cover the full support target?          │ WEAK / decompose / refine                                      │
│ C0.G9 Budget  │ Can context fit without losing must-use evidence?     │ Emit prompt_budget_hint / trim optional context                │
│ C0.G10 Inject │ Is retrieved text safely classified as data?          │ Quarantine / strip / reject instruction-like payload           │
└───────────────┴──────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘

======================================================================================================================================================
FAILURE MODES C0 MUST PREVENT
======================================================================================================================================================

┌─────────────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FAILURE MODE                        │ PREVENTION                                                                                     │
├─────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Dense-only hallucination             │ Require direct support and sparse/metadata confirmation for exact claims                                 │
│ Wrong tenant evidence                │ ACL + tenant filters at plan, fetch, graph hop, and verification stages                                  │
│ Stale policy answer                  │ freshness_class check + version verification                                                           │
│ Quote distortion                     │ parent expansion + stable cited span verification                                                       │
│ Hidden contradiction                 │ contradiction scan + CONTRADICTS evidence class                                                        │
│ Graph scope creep                    │ max_hops + relation filter + ACL at every hop                                                          │
│ Cache poisoning                      │ cache lineage verification + freshness and policy gates                                                 │
│ Prompt injection via retrieved text  │ origin-trust labeling + data-only wrapping + quarantine of instruction-like payload                      │
│ Fake confidence                      │ score breakdown + unresolved gaps + WEAK_WITH_CAVEATS status                                            │
│ Lost lineage                         │ retrieval_mode_provenance + lineage_manifest                                                           │
│ Overstuffed context                  │ priority packing + deterministic trim order                                                            │
│ Unsupported synthesis                │ distinguish direct support from downstream inference risk                                               │
│ Docs-vs-code mismatch                │ surface conflict, do not silently prefer convenient source                                              │
│ Runtime-vs-design mismatch           │ include trace/log evidence as contradiction or validation source when allowed                            │
└─────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────┘

======================================================================================================================================================
CONCRETE EXAMPLE FLOW
======================================================================================================================================================

USER ASK:
"What does C5 say about prompt assembly, and is C0 allowed to answer directly?"

L1:
- task_spec = answer question about C5 / C0 / prompt assembly
- query_spec = prompt assembly responsibilities, C0 responsibilities, boundaries
- grounding_required = true

L0:
- route_id = R3_SIMPLE_GROUNDED_READ
- support_target = source-backed summary
- allowed_sources = project docs
- max_refine_attempts = 1
- freshness_class = static/project-current

C0.1 PLAN:
- search docs for "C5 prompt assembly", "C0 retrieves only", "Prompt Assembly packages only"
- dense + sparse + metadata lanes
- graph hop to related C0 Context Engine and Prompt Assembly doc

C0.2 FETCH:
- dense finds conceptual prompt assembly material
- sparse finds exact "Prompt Assembly packages only" and "C0 retrieves only"
- metadata confirms project docs and current uploaded files

C0.3 GRAPH:
- link C5 to C0 Context Engine and Prompt Assembly compact view
- identify boundary: C0 retrieves, PA packages, L2 executes

C0.4 SHAPE:
- MUST_USE:
  - C5 mandate
  - C0 role boundary
  - Prompt Assembly handoff
- SUPPORTING:
  - L0 route notes
- CONTRADICTS:
  - none found
- EXCLUDED:
  - unrelated transformer refinement docs

C0.5 CONTRACT:
- status = PASS
- support_score = high
- recommendation = proceed

PROMPT ASSEMBLY:
- packs verified snippets and citation anchors
- marks retrieved docs as data
- sends bounded packet to L2

L2:
- answers from evidence

EXIT:
- checks groundedness and citation support

======================================================================================================================================================
C0 OUTPUT SCHEMA
======================================================================================================================================================

FinalEvidenceContract:
  contract_id: string
  route_id: string
  route_replay_key: string
  policy_hash: string
  blueprint_hash: string

  status:
    enum:
      - PASS
      - WEAK_WITH_CAVEATS
      - CONFLICTED
      - EMPTY
      - BLOCKED

  support_score: float

  score_breakdown:
    direct_support_score: float
    coverage_score: float
    source_authority_score: float
    freshness_score: float
    citation_stability_score: float
    lineage_quality_score: float
    exactness_score: float
    contradiction_risk: float
    unsupported_inference_risk: float

  evidence:
    must_use:
      - evidence_id
      - source_id
      - source_type
      - span_ref
      - quote_or_summary
      - retrieval_lane
      - authority_score
      - freshness_status
      - acl_status
      - token_cost
    supporting:
      - evidence_id
      - source_id
      - span_ref
      - reason
    contradicts:
      - evidence_id
      - source_id
      - span_ref
      - conflict_type
      - conflict_summary
    background:
      - evidence_id
      - source_id
      - span_ref
      - reason
    definitions:
      - term
      - source_id
      - span_ref
    lineage:
      - evidence_id
      - found_by
      - expanded_by
      - rerank_reason
    excluded:
      - evidence_id
      - exclusion_reason

  freshness_report:
    freshness_class: string
    newest_source_age: string
    stale_sources: list
    version_mismatches: list

  acl_report:
    tenant_scope: string
    cleared_sources: list
    blocked_sources_count: int
    data_classes_seen: list

  contradiction_flags:
    - type
    - source_a
    - source_b
    - severity
    - required_downstream_behavior

  unresolved_gaps:
    - gap_type
    - severity
    - impact_on_answer
    - suggested_next_step

  prompt_budget_hint:
    pack_order: list
    must_keep_evidence_ids: list
    trim_first_evidence_ids: list
    max_context_tokens: int
    estimated_context_tokens: int

  recommended_disposition:
    enum:
      - proceed
      - proceed_with_caveat
      - abstain
      - fallback_R5
      - reroute
      - human_review

  budget_report:
    retrieval_passes: int
    graph_hops_used: int
    latency_ms: int
    cost_tier_used: string
    budget_remaining: string

  replay_metadata:
    retrieval_snapshot_id: string
    evidence_contract_hash: string
    source_manifest_hash: string

======================================================================================================================================================
ONE-LINE MENTAL MODEL
======================================================================================================================================================

L0 says "ground this" -> C0 finds and verifies the evidence -> Prompt Assembly packs only verified context -> L2 answers or acts under guard -> Exit decides whether the result can leave.

======================================================================================================================================================
FINAL INVARIANT
======================================================================================================================================================

C0 is the reference desk, not the author, not the dispatcher, not the executor, not the judge, and not the clerk with the pen.

Its only job is to make downstream generation safer by turning messy shelves into a verified, scored, citeable, contradiction-aware
FinalEvidenceContract.
======================================================================================================================================================