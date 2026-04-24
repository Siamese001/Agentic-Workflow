==============================================================================================================================
[C2] 👁️ OBSERVABILITY, TELEMETRY & CONTROL SIGNALS
     Library Persona: 🕰️ Master Clock + 🎥 Tape Reviewer + 🔔 Bell Tower Keeper + 🧾 Trace Clerk
     Operational Span: U0 intake -> L1 -> L0/C0/PA/L3 -> L2 -> Exit/HITL/UWG -> L6 -> Metrics -> Meta-learning
     OTEL Role: one runtime crumb trail, one trace_id per accepted request, span every governed desk action
==============================================================================================================================

[!] SIMPLEST OBSERVABILITY PATTERN:
    trace_id = whole patron visit / case folder
    span_id  = one stamped desk action inside that visit
    parent_id = who handed work to whom
    attributes = replay, policy, route, tool/model, artifact, timing, result, and cost receipts

[!] HARD LAW:
    OTEL observes and correlates. OTEL does not route, retrieve, execute, approve, commit, or mutate.
    Live control decisions still belong to L5 / Exit. Durable writes still belong to UWG -> L4.

==============================================================================================================================
[ THE AGENTIC OTEL CRUMB TRAIL ]
==============================================================================================================================

   👤 apps ──► 🚪 U0 ──► 🧠 L1 ──► 🧭 L0 ──► [C0/PA or L3] ──► 🛠️ L2 ──► 🚪 EXIT ──► 👥 HITL ──► 🖋️ UWG/L4
                 │          │          │             │                │            │             │             │
                 └──────────┴──────────┴─────────────┴────────────────┴────────────┴─────────────┴─────────────┘
                                                       │
                                                       │ [same trace_id | child spans | replay lineage]
                                                       ▼
████████████████████████████████████████████████ RUNTIME BOUNDARY ████████████████████████████████████████████████
                                                       │
                                                       ▼
                         👁️ L6 SHADOW EVAL ──► 📊 METRICS ──► 🌙 META-LEARNING / RCA ──► 🖋️ UWG -> 🏛️ L4

==============================================================================================================================
[0] TRACE ENVELOPE REQUIREMENTS
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TRACE ENVELOPE                                                                                                            │
│ - One accepted runtime request MUST have exactly one canonical trace_id.                                                    │
│ - trace_root starts at U0 after the request is accepted and stamped.                                                       │
│ - Same trace_id propagates through U0, L1, L0, C0, PA, L3 if invoked, L2, Exit, HITL, UWG/L4, and L6.                      │
│ - Short-circuit routes still trace. R1/R5 [RET] skip deeper work, not observability.                                       │
│ - A missing trace_id is a telemetry defect. A changed trace_id inside one runtime is a lineage break.                      │
│ - L6 may read trace data only. L6 never mutates the current run.                                                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED TRACE BAGGAGE / COMMON ATTRIBUTES                                                                                │
│ identity   : trace_id, span_id, parent_span_id, request_id, session_id, run_id, tenant_id, actor_type                      │
│ governance : policy_hash, compliance_hash, capability_token_id, sandbox_envelope_id, origin_trust_class                    │
│ replay     : replay_key, blueprint_hash, snapshot_id, idempotency_key, deterministic_seed_ref, lineage_hash                │
│ routing    : layer, process_box, route_family, route_contract_id, reason_code, confidence, risk_tier                       │
│ execution  : model_id/tool_id/provider_id, input_digest, output_digest, artifact_ids, attempt_count, retry_count           │
│ timing     : start_time, end_time, duration_ms, queue_ms, timeout_ms, clock_source, clock_drift_flag                       │
│ quality    : support_score, citation_precision, groundedness_score, schema_valid, abstain_fit, eval_verdict               │
│ cost       : tokens_in, tokens_out, tool_cost, provider_cost, cache_hit, latency_class                                      │
│ result     : status, terminal_class, error_code, anomaly_flags, disposition, commit_status                                 │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[1] U0 REQUEST INTAKE + ENVELOPE CHECK  [trace_root begins here]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ U0 OBSERVABILITY BOX                                                                                                       │
│ - Starts trace_root only after request acceptance.                                                                          │
│ - Binds request_id / session_id / caller_scope / tenant / initial policy posture.                                           │
│ - Stamps the clean request packet with trace context before L1 sees it.                                                     │
│ - Does not perform semantic routing, retrieval, execution, or mutation.                                                     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED U0 SPANS                                                                                                          │
│ trace_root -> auth_check -> quota_check -> schema_check -> normalize_request -> stamp_ingress                              │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED ATTRIBUTES                                                                                                        │
│ request_id | session_id | trace_id | caller_scope | tenant_id | ingress_source | auth_status | quota_status | schema_status │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DEFECT SIGNALS                                                                                                             │
│ - Accepted request without trace_root.                                                                                      │
│ - Request passed to L1 without request_id/session_id/trace_id.                                                              │
│ - Rejection without reason_code.                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[2] L1 REASONING + PLAN GENERATION  [trace interprets, but does not execute]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L1 OBSERVABILITY BOX                                                                                                       │
│ - Records how the request was interpreted and how the plan contract was formed.                                             │
│ - Captures assumptions, missing-info markers, plan confidence, and proposed route options.                                  │
│ - Keeps internal reasoning non-authoritative: L1 proposes only.                                                             │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED L1 SPANS                                                                                                          │
│ parse_intent -> load_policy_priors -> load_examples -> draft_plan -> validate_plan -> emit_plan_contract                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED ATTRIBUTES                                                                                                        │
│ plan_id | task_spec | query_spec | proposed_route | grounding_required | confidence | route_risk | assumptions | gaps      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DEFECT SIGNALS                                                                                                             │
│ - Plan contract emitted without parent trace from U0.                                                                       │
│ - Proposed route missing reason_code or confidence.                                                                         │
│ - L1 span shows tool/model execution beyond planning scope.                                                                 │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[3] L0 ROUTE DECISION + SWITCHING  [route contract, not the work]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L0 OBSERVABILITY BOX                                                                                                       │
│ - Records deterministic route scoring and selected route family.                                                            │
│ - Captures cache probes, freshness checks, ACL checks, support requirement, and [RET] short-circuit reasons.                │
│ - Emits route_contract_id for downstream C0/PA/L3/L2/Exit spans.                                                            │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED L0 SPANS                                                                                                          │
│ prefilter_scope -> cache_probe_exact -> cache_probe_semantic -> route_score -> route_decision -> emit_route_contract        │
│ optional: ret_short_circuit for R1A / R1B / R5 terminal paths                                                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED ATTRIBUTES                                                                                                        │
│ route_family | route_contract_id | reason_code | confidence | risk_tier | cache_hit | freshness_class | acl_status         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DEFECT SIGNALS                                                                                                             │
│ - Route decision without L1 parent span.                                                                                    │
│ - R1/R5 [RET] path without Exit span.                                                                                       │
│ - Selected C0/L3 path without route_contract_id.                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[3A] C0 RETRIEVAL + PROMPT ASSEMBLY  [only when L0 selects grounding]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0 / PA OBSERVABILITY BOX                                                                                                  │
│ - C0 records retrieval planning, evidence fetch, graph traversal, rerank, evidence shaping, and support gaps.               │
│ - Prompt Assembly records static block load, context slotting, token budgeting, and prompt envelope signing.                │
│ - C0 retrieves only. PA packages only. Neither invents facts, routes, executes, or mutates.                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED C0 SPANS                                                                                                          │
│ retrieval_plan -> evidence_fetch_dense_sparse -> graph_traverse -> dedupe_rerank -> evidence_contract                      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED PA SPANS                                                                                                          │
│ load_static_blocks -> slot_context_task -> budget_tokens -> sign_prompt_envelope -> dispatch_packet                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED ATTRIBUTES                                                                                                        │
│ source_ids | cited_spans | evidence_contract_id | support_score | gaps | prompt_hash | token_budget | snapshot_id          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DEFECT SIGNALS                                                                                                             │
│ - Answer later claims grounded support but no C0 evidence spans exist.                                                      │
│ - Cited source_id not present in evidence_contract span.                                                                    │
│ - PromptEnvelope signed without evidence_contract_id for grounded route.                                                    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[3B] L3 ORCHESTRATION  [only when L0 selects managed workflow]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L3 OBSERVABILITY BOX                                                                                                       │
│ - Records workflow expansion, DAG/step graph construction, readiness checks, node dispatch, node merge, and completion.     │
│ - Tracks forward-only orchestration flow for current run; feedback loops happen after L2/Exit/L6, not as backward DAG edges.│
│ - Carries route bounds, budgets, policy posture, and current-step contracts to L2.                                          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED L3 SPANS                                                                                                          │
│ classify_execution_shape -> dag_build -> readiness_check -> node_dispatch -> step_result_merge -> workflow_exit_package    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED ATTRIBUTES                                                                                                        │
│ workflow_id | node_id | dependency_ids | step_contract_id | route_contract_id | branch_result | checkpoint_id | budget      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DEFECT SIGNALS                                                                                                             │
│ - Multi-step workflow without workflow_id.                                                                                  │
│ - L2 executes a managed step without L3 parent span.                                                                        │
│ - Span fanout exceeds route budget or declared workflow shape.                                                              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[4] L2 EXECUTE  [highest-density span zone]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L2 OBSERVABILITY BOX                                                                                                       │
│ - Records every bounded execution step under the same trace_id, replay envelope, policy_hash, and snapshot manifest.        │
│ - Every tool/model/cache/vector/graph/network/MCP/provider call is a child span under E3.                                  │
│ - Every retry/heal attempt is a child span under E4 with reason_code and attempt counters.                                  │
│ - L2 emits sealed artifacts only. No durable commit occurs here.                                                            │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED L2 SPANS                                                                                                          │
│ E1 prep_env -> bind_budget -> bind_replay -> bind_lineage                                                                  │
│ E2 validate_packet -> validate_caps -> validate_schema -> approve_or_reject                                                 │
│ E3 invoke_model/tool/cache/vector/graph/MCP/provider -> capture_output -> classify_result                                  │
│ E4 classify_failure -> local_repair -> retry_or_escalate_artifact                                                          │
│ E5 package_payload -> attach_traces_lineage -> attach_replay_receipts -> seal_artifact                                     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED ATTRIBUTES                                                                                                        │
│ step_contract_id | replay_key | blueprint_hash | policy_hash | capability_token_id | sandbox_envelope_id | tool_id        │
│ model_id | provider_id | input_digest | output_digest | stdout_digest | stderr_digest | attempt_count | retry_count      │
│ repair_count | error_code | terminal_class | artifact_id | lineage_hash | duration_ms | tokens_in/out | provider_cost    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DEFECT SIGNALS                                                                                                             │
│ - Tool/model invocation without child span.                                                                                 │
│ - Retry/heal event without attempt_count, repair_count, reason_code, or parent_packet_id.                                  │
│ - Artifact or state diff exists without corresponding execution span.                                                       │
│ - Mutation span appears outside UWG path.                                                                                   │
│ - Policy_hash diverges from replay envelope.                                                                                │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[5] EXIT EVAL & CONTROL  [live disposition from sealed evidence]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ EXIT OBSERVABILITY BOX                                                                                                     │
│ - Receives sealed L2 artifacts or [RET] short-circuit from L0.                                                              │
│ - Records current-run policy, safety, quality, groundedness, schema, and mutation authorization checks.                     │
│ - Emits exactly one explicit disposition path: allow_finish, deny_reroute, escalate, or commit_request.                     │
│ - Live control signals can ring the bell here. Telemetry alone never silently changes the answer.                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED EXIT SPANS                                                                                                        │
│ receive_runtime_input -> policy_eval -> quality_eval -> safety_eval -> disposition                                         │
│ disposition child: allow_finish | deny_reroute | escalate | commit_request                                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED ATTRIBUTES                                                                                                        │
│ disposition | eval_verdict | support_score | citation_precision | groundedness_score | schema_valid | mutation_auth_status  │
│ terminal_class | artifact_ids | reason_code | risk_tier | commit_request_id                                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DEFECT SIGNALS                                                                                                             │
│ - Runtime ends without Exit disposition span.                                                                               │
│ - Allow/finish with failed policy or schema span.                                                                            │
│ - Commit request without artifact lineage and mutation authorization.                                                       │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[5A] HITL + UWG/L4  [human review and real ink remain governed]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HITL OBSERVABILITY BOX                                                                                                     │
│ - Records freeze, bounded packet materialization, review verdict, and L5 re-clearance.                                      │
│ - Human input is recorded as data, not authority.                                                                            │
│ - Any modified diff must re-enter governed clearance before allow or commit.                                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED HITL SPANS                                                                                                        │
│ freeze_state -> materialize_review_packet -> human_review -> re_clearance -> resume_or_reject                              │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED ATTRIBUTES                                                                                                        │
│ review_packet_id | reviewer_role | verdict | diff_id | reason_code | re_clearance_status | frozen_auth_state              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ UWG / L4 OBSERVABILITY BOX                                                                                                 │
│ - Records the only real write path: verify authority, check scope/diff, claim lock, commit, chain append, refresh surfaces. │
│ - Any ghost write attempt outside UWG is a sovereignty violation.                                                           │
│ - Commit receipts become durable L4 telemetry and future replay evidence.                                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED UWG / L4 SPANS                                                                                                    │
│ verify_authority -> check_catalog_scope_diff -> claim_write_lock -> commit_chain_append -> refresh_read_surfaces           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED ATTRIBUTES                                                                                                        │
│ commit_request_id | commit_id | ledger_hash | lock_id | diff_id | rbacs_status | scope_status | chain_hash | refresh_status │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DEFECT SIGNALS                                                                                                             │
│ - Commit status exists without UWG verification spans.                                                                      │
│ - Durable L4 mutation without commit_chain_append span.                                                                     │
│ - Overlapping write spans without serialized lock evidence.                                                                 │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

████████████████████████████████████████████████ RUNTIME BOUNDARY ████████████████████████████████████████████████

==============================================================================================================================
[6] L6 SHADOW EVALUATION  [observer only, future-run learning only]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L6 READ SURFACES                                                                                                           │
│ - Sealed Execution Trace: every tool/model interaction and state change proposal.                                           │
│ - OTEL Span Graph: trace_id, parent/child spans, timings, attributes, statuses, and error lineage.                         │
│ - Exit Dispositions: allow, deny, escalate, commit request, and final response outcome.                                    │
│ - L4 Telemetry Shelf: historical baselines, prior run logs, commit receipts, and promotion receipts.                       │
│ - Replay Receipts: replay_key, policy_hash, snapshot_id, deterministic digest, artifact lineage.                           │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L6 VERIFY SPINE                                                                                                           │
│ does not execute | does not route | does not commit | generates signals only                                               │
├──────────────────────────────┬──────────────────────────────┬──────────────────────────────┬──────────────────────────────┤
│ 1. TIME AUDIT                │ 2. ISOLATION CHECK           │ 3. DRIFT / ANOMALY DETECT    │ 4. PACKET SEAL               │
│ - Verify stamps              │ - Verify seeds               │ - Budget usage               │ - Normalize metrics          │
│ - Order and latency          │ - Check sandbox isolation    │ - Retry thrash / spikes      │ - Seal exec environment      │
│ - Span duration              │ - Replay strictness          │ - Span fanout anomaly        │ - Final provenance           │
│ - Clock drift detect         │ - Trace continuity           │ - Hidden action detection    │ - Evidence lineage           │
└──────────────┬───────────────┴──────────────┬───────────────┴──────────────┬───────────────┴──────────────┬───────────────┘
               │                              │                              │                              │
               └──────────────────────────────┴──────────────┬───────────────┴──────────────────────────────┘
                                                              ▼
                                                [ L6EvidenceBundle ]
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ REQUIRED L6 SPANS                                                                                                          │
│ ingest_trace -> normalize_evidence -> evaluate_outcome -> evaluate_trajectory -> detect_regression -> rca_synthesis        │
│ -> promotion_candidate_packet                                                                                              │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED ATTRIBUTES                                                                                                        │
│ eval_bundle_id | trace_id | span_graph_id | replay_key | determinism_status | anomaly_flags | drift_flags | RCA_id        │
│ outcome_scores | trajectory_scores | support_rate | citation_precision | abstain_fit | retry_thrash | latency_by_layer   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ OUTPUTS                                                                                                                    │
│ - BUS D / BUS E: live safety bell only when current-run control must deny, re-enter, or escalate.                          │
│ - BUS T: async trace and telemetry payload for metrics, RCA, replay, trends, and future-run learning.                      │
│ - L6EvidenceBundle: sealed, replay-linked evidence for after-hours evaluation.                                             │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[7] METRICS BOX  [normalize trace exhaust into measurable signals]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ METRICS OBSERVABILITY BOX                                                                                                  │
│ - Converts OTEL spans and sealed artifacts into normalized system metrics.                                                  │
│ - Separates live control metrics from async improvement metrics.                                                            │
│ - Metrics can inform Exit or future learning, but cannot bypass L5/UWG authority.                                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED METRIC FAMILIES                                                                                                   │
│ reliability : success_rate, terminal_failure_rate, rejected_before_execution_rate, replay_pass_rate                         │
│ latency     : duration_by_layer, queue_ms, provider_latency, retrieval_latency, exit_eval_latency, p50/p95/p99             │
│ cost        : tokens_in/out, provider_cost, tool_cost, cache_savings, cost_by_route                                         │
│ retrieval   : Recall@K, MRR, support_rate, citation_precision, evidence_gap_rate, rerank_delta                             │
│ trajectory  : tool_order_fit, retry_count, repair_count, thrash_rate, span_fanout, workflow_node_completion                 │
│ safety      : policy_denial_rate, injection_detect_rate, sandbox_breach_rate, HITL_rate, ghost_write_attempts              │
│ governance  : commit_request_rate, UWG_commit_success_rate, ledger_append_latency, policy_hash_mismatch_rate               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED METRIC KEYS                                                                                                       │
│ trace_id | route_family | layer | process_box | policy_hash | model_id | tool_id | provider_id | tenant_id | time_bucket    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DEFECT SIGNALS                                                                                                             │
│ - Metric emitted without trace/span lineage.                                                                                │
│ - Metric aggregates live and future-run signals without label separation.                                                   │
│ - Cost or latency metric missing route_family/model/tool/provider dimension.                                                │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[8] META-LEARNING / RCA / FUTURE-RUN PROMOTION  [observe -> seal -> propose -> approve -> update]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ META-LEARNING OBSERVABILITY BOX                                                                                            │
│ - Consumes L6EvidenceBundle, metrics, traces, exits, artifacts, and HITL packets after the runtime boundary.                │
│ - Performs RCA, drift clustering, rubric/policy/prompt/config proposal drafting, and shadow replay.                         │
│ - Produces proposals only until approved through gauntlet and committed by UWG -> L4.                                       │
│ - Learning signals inform future runs only. They do not mutate or rescue the completed run.                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED META-LEARNING SPANS                                                                                                │
│ archive_freeze -> case_file_compile -> investigation -> rca_packet -> rule_drafting -> shadow_replay_gauntlet              │
│ -> approve_or_reject -> knowledge_extraction -> promotion_packet -> uwg_l4_commit_if_approved                              │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED ATTRIBUTES                                                                                                        │
│ case_file_id | incident_id | RCA_id | drift_cluster_id | proposed_rule_id | rollback_plan_id | gauntlet_status             │
│ SME_signoff | promotion_packet_id | update_surface | commit_id | rollout_receipt_id                                         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ DEFECT SIGNALS                                                                                                             │
│ - Promotion proposal not linked to trace_id / case_file_id / RCA_id.                                                        │
│ - Future-run update without shadow replay and regression evidence.                                                          │
│ - Learning path writes directly to L4 without UWG commit span.                                                              │
│ - Current-run behavior changes because of meta-learning before runtime boundary.                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[ TRACE SHAPE: ONE REQUEST, MANY SPANS ]
==============================================================================================================================

trace_id = T-accepted-request
│
├─ U0.trace_root
│  ├─ U0.auth_check
│  ├─ U0.quota_check
│  └─ U0.stamp_ingress
│
├─ L1.parse_intent
│  ├─ L1.load_policy_priors
│  ├─ L1.draft_plan
│  └─ L1.emit_plan_contract
│
├─ L0.route_decision
│  ├─ L0.cache_probe_exact / semantic
│  ├─ L0.ret_short_circuit                  [R1/R5]
│  ├─ C0.evidence_fetch -> PA.sign_prompt   [R3 simple grounded read]
│  └─ L3.dag_build -> L3.node_dispatch      [managed workflow]
│
├─ L2.execute_current_step
│  ├─ E1.prep_env
│  ├─ E2.validate_packet
│  ├─ E3.invoke_tool/model/cache/MCP
│  ├─ E4.heal_retry
│  └─ E5.seal_artifact
│
├─ Exit.disposition
│  ├─ allow_finish
│  ├─ deny_reroute
│  ├─ escalate -> HITL.review -> L5.reclear
│  └─ commit_request -> UWG.verify -> UWG.commit_chain -> L4.receipt
│
└─ L6.ingest_trace
   ├─ Metrics.normalize
   ├─ RCA.synthesize
   └─ MetaLearning.promotion_candidate -> UWG/L4 if approved

==============================================================================================================================
[ FAILURE / GAP DETECTION RULES ]
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TELEMETRY DEFECTS                                                                                                          │
│ - Missing trace_id after accepted U0 request.                                                                                │
│ - New trace_id created mid-run without explicit external callback boundary.                                                  │
│ - Broken parent_span_id chain across L0 -> C0/PA/L3/L2 -> Exit.                                                             │
│ - Tool/model invocation without child span.                                                                                 │
│ - Retry/heal event without attempt_count or parent_packet_id.                                                               │
│ - Exit disposition missing or ambiguous.                                                                                    │
│ - Commit request without UWG verification/commit spans.                                                                     │
│ - L6 evidence bundle missing replay_key, policy_hash, or span graph.                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ANOMALY SIGNALS                                                                                                            │
│ - Latency spike by layer, route, provider, or tool.                                                                         │
│ - Retry thrash: repeated E4 heal loops for same reason_code.                                                                │
│ - Span fanout exceeds route budget or declared workflow shape.                                                              │
│ - Hidden action: artifact or state diff exists without corresponding span.                                                  │
│ - Ghost write attempt: mutation span appears outside UWG commit path.                                                       │
│ - Policy mismatch: span policy_hash diverges from replay envelope policy_hash.                                              │
│ - Evidence gap: answer cites unsupported source_ids or missing retrieval spans.                                             │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[ OTEL + REPLAY BINDING ]
==============================================================================================================================

   Replay proves:  same input + same envelope + same policy_hash + same read snapshot -> same replay digest
   OTEL proves:    what happened, in what order, under what parent, with what timing, cost, status, and artifacts

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ BINDING REQUIREMENTS                                                                                                       │
│ - replay_key must appear on all spans after replay envelope creation.                                                       │
│ - policy_hash must appear on all governed runtime spans.                                                                    │
│ - snapshot_id must appear on all state-read, retrieval, prompt assembly, and execution spans.                               │
│ - artifact_id must link sealed L2 outputs, Exit evidence, L6 evidence bundles, and any UWG commit receipts.                 │
│ - deterministic replay failures must reference the exact span_id and reason_code that broke replayability.                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==============================================================================================================================
[!] LIVE SIDE: Observe -> Detect -> Ring Bell -> Exit Gate decides the current run.
[!] FUTURE SIDE: Observe -> Seal Evidence -> Learning Loop -> Approved Promotion updates the manual for tomorrow.
[!] OTEL LAW: Trace the whole visit, span every desk action, preserve parent/child lineage, and never mutate from telemetry alone.
==============================================================================================================================
