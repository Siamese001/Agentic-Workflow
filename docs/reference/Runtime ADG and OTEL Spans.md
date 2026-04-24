┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         RUNTIME ADG + OTEL + RAG + GRAPHDB BEST-PRACTICE OVERWRITE                         │
│                                                                                                            │
│  traceID      = one full agentic run                                                                        │
│  span         = one recorded runtime breadcrumb inside that run                                              │
│  ADG node     = meaningful runtime object: request, plan, route, evidence, step, tool, output, eval, commit │
│  ADG edge     = relationship: validates, routes_to, retrieves, invokes, emits, blocks, commits, learns_from │
│  graph rule   = every span carries trace_id + span_id + parent_span_id + run_id + layer + component         │
│  RAG rule     = every retrieval span carries query, index version, evidence IDs, support score, provenance  │
│  safety rule  = every mutation span remains proposal-only until Exit -> UWG -> L4 commit                    │
│  eval rule    = every completed run produces eval metrics, replay proof, and future-run-only learning data  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


[ USER REQUEST ]
      │
      │ creates / receives
      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TRACE ROOT / RUNTIME RUN                                                                                    │
│ span: runtime.trace_root                                                                                    │
│                                                                                                            │
│ required span attrs:                                                                                        │
│ - trace_id, span_id, parent_span_id=null                                                                    │
│ - run_id, request_id, session_id, tenant_id, caller_scope                                                   │
│ - input_envelope_hash, runtime_version, service.name, deployment.environment                                │
│                                                                                                            │
│ runtime ADG nodes:                                                                                          │
│ - RuntimeRun                                                                                                │
│ - UserRequest                                                                                               │
│                                                                                                            │
│ runtime ADG edges:                                                                                          │
│ - UserRequest started RuntimeRun                                                                            │
│ - RuntimeRun contains all child spans                                                                       │
│                                                                                                            │
│ coverage invariant:                                                                                         │
│ - if trace root is missing, the runtime ADG cannot prove the run existed as one correlated execution         │
└──────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                               │
                                               ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ INTAKE / U0                                                                                                │
│ Front door: validate, normalize, stamp trace root. No reasoning, no route, no retrieval, no mutation.       │
│                                                                                                            │
│ spans:                                                                                                     │
│ - U0.intake.validate                                                                                       │
│ - U0.intake.normalize                                                                                      │
│ - U0.intake.stamp_trace                                                                                    │
│                                                                                                            │
│ required span attrs:                                                                                        │
│ - request_id, trace_root, schema_status, auth_status, quota_status                                          │
│ - normalized_payload_hash, rejection_reason, caller_scope_baseline                                          │
│ - origin_trust=user_turn, ingress_channel, envelope_version                                                 │
│                                                                                                            │
│ runtime ADG nodes:                                                                                          │
│ - IntakeEnvelope                                                                                            │
│ - ValidatedRequest                                                                                          │
│                                                                                                            │
│ runtime ADG edges:                                                                                          │
│ - IntakeEnvelope validates UserRequest                                                                      │
│ - IntakeEnvelope emits ValidatedRequest                                                                     │
│                                                                                                            │
│ best-practice add:                                                                                          │
│ - stamp trace_id before any L1/L0 work so every downstream span has a single correlation root               │
└──────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                               │
                                               ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L1 REASONING / PLAN GENERATION                                                                              │
│ Understand the ask and create a bounded plan. No retrieval, no route authority, no tools, no durable write. │
│                                                                                                            │
│ spans:                                                                                                     │
│ - L1.intent.parse                                                                                          │
│ - L1.context.priors_load                                                                                    │
│ - L1.plan.draft                                                                                            │
│ - L1.plan.validate                                                                                         │
│                                                                                                            │
│ required span attrs:                                                                                        │
│ - intent_frame_hash, task_class, task_spec_hash, success_condition                                          │
│ - assumptions, unresolved_gaps, proposed_route, route_risk, confidence                                      │
│ - plan_contract_hash, grounding_required, output_contract_hash                                             │
│                                                                                                            │
│ runtime ADG nodes:                                                                                          │
│ - L1IntentFrame                                                                                             │
│ - L1PlanContract                                                                                            │
│                                                                                                            │
│ runtime ADG edges:                                                                                          │
│ - L1IntentFrame interprets ValidatedRequest                                                                 │
│ - L1PlanContract proposes_route to L0                                                                       │
│ - L1PlanContract emits PlanContract                                                                         │
│                                                                                                            │
│ best-practice add:                                                                                          │
│ - record proposed route separately from selected route so L0 remains the only routing authority             │
└──────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                               │
                                               ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L0 ROUTE DECISION                                                                                           │
│ Deterministically select the path: exact cache, semantic cache, grounded read, action, workflow, fallback.  │
│                                                                                                            │
│ spans:                                                                                                     │
│ - L0.route.score                                                                                           │
│ - L0.cache.check                                                                                            │
│ - L0.route.select                                                                                          │
│ - L0.route.contract                                                                                        │
│                                                                                                            │
│ required span attrs:                                                                                        │
│ - selected_route, reason_codes, confidence, risk_tier, freshness_class                                      │
│ - cache_decision, cache_key_hash, semantic_similarity_score, support_required                               │
│ - execution_form=terminal|single_step|managed_workflow                                                      │
│ - route_contract_hash, route_bounds, policy_hash                                                            │
│                                                                                                            │
│ runtime ADG nodes:                                                                                          │
│ - RouteContract                                                                                             │
│ - RouteFamily                                                                                               │
│                                                                                                            │
│ runtime ADG edges:                                                                                          │
│ - RouteContract reads L1PlanContract                                                                        │
│ - RouteContract selects RouteFamily                                                                         │
│ - RouteContract emits DirectStepPacket or WorkflowRequest                                                   │
│                                                                                                            │
│ best-practice add:                                                                                          │
│ - route decision must be queryable by reason_code, not just final selected route                            │
└──────────────┬──────────────────────────────────────────────────────────────────────────────┬──────────────┘
               │                                                                              │
               │ direct / single-step route                                                   │ managed workflow route
               ▼                                                                              ▼

┌────────────────────────────────────────────────────────────────────┐       ┌────────────────────────────────────────────────────────────────────┐
│ DIRECT / SINGLE-STEP PATH                                           │       │ L3 ORCHESTRATION PATH                                             │
│ R1 exact cache, R1B semantic cache, R3 simple read, R4 action, R5.   │       │ Only when L0 selected managed multi-step R3/R4 workflow.            │
├────────────────────────────────────────────────────────────────────┤       ├────────────────────────────────────────────────────────────────────┤
│ spans:                                                             │       │ spans:                                                             │
│ - L0.direct.package                                                │       │ - L3.workflow.expand                                               │
│ - L0.ret.short_circuit       only R1/R5                             │       │ - L3.workflow.state                                                │
│ - L0.single_step.dispatch    only R3/R4                             │       │ - L3.step.ready_check                                              │
│                                                                    │       │ - L3.step.dispatch                                                 │
│ required span attrs:                                                │       │ - L3.step.merge_result                                             │
│ - direct_step_id, selected_route, no_l3_required=true               │       │                                                                    │
│ - packet_hash, terminal_return_reason                               │       │ required span attrs:                                                │
│                                                                    │       │ - workflow_id, dag_hash, node_ids, dependency_edges                 │
│ runtime ADG nodes:                                                  │       │ - branch_rules, join_rules, checkpoint_hash, current_step_id        │
│ - DirectStepPacket                                                  │       │ - ready_node_ids, blocked_node_ids, workflow_state_hash             │
│ - TerminalReturn                                                    │       │                                                                    │
│                                                                    │       │ runtime ADG nodes:                                                  │
│ runtime ADG edges:                                                  │       │ - WorkflowGraph                                                     │
│ - DirectStepPacket bypasses L3                                      │       │ - WorkflowStep                                                      │
│ - DirectStepPacket dispatches to L2 or Exit                         │       │ - StepDependency                                                    │
│                                                                    │       │                                                                    │
│ best-practice add:                                                  │       │ runtime ADG edges:                                                  │
│ - terminal routes still emit spans, otherwise cache/fallback paths   │       │ - WorkflowGraph expands RouteContract                               │
│   disappear from runtime ADG coverage                               │       │ - WorkflowStep depends_on WorkflowStep                              │
└──────────────────────────────┬─────────────────────────────────────┘       │ - WorkflowStep dispatches_to L2                                     │
                               │                                             │                                                                    │
                               │                                             │ best-practice add:                                                  │
                               │                                             │ - model L3 as graph topology: nodes, edges, readiness, joins,        │
                               │                                             │   checkpoints, and handoff contracts                                │
                               │                                             └──────────────────────────────┬─────────────────────────────────────┘
                               │                                                                            │
                               └────────────────────────────────────────────┬───────────────────────────────┘
                                                                            ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0 RETRIEVAL / CONTEXT ENGINE                                                                               │
│ Present only for grounded routes. C0 retrieves and shapes evidence. It does not generate, route, or write.  │
│                                                                                                            │
│ spans:                                                                                                     │
│ - C0.retrieval.plan                                                                                        │
│ - C0.query.embed                                                                                            │
│ - C0.evidence.fetch_dense                                                                                   │
│ - C0.evidence.fetch_sparse                                                                                  │
│ - C0.graph.traverse                                                                                         │
│ - C0.evidence.rerank                                                                                        │
│ - C0.evidence.contract                                                                                      │
│                                                                                                            │
│ required span attrs:                                                                                        │
│ - query_vec_id, query_text_hash, source_scope, acl_scope, freshness_scope                                    │
│ - vector_store_id, index_version, embedding_model_id, retrieval_mode=dense|sparse|hybrid|graph              │
│ - top_k, similarity_threshold, bm25_enabled, reranker_model_id                                              │
│ - source_ids, chunk_ids, entity_ids, edge_ids, evidence_ids                                                  │
│ - rerank_scores, support_score, coverage_gaps, contradiction_flags                                          │
│ - contextual_chunk_header_hash, parent_document_id, citation_span_ids                                       │
│                                                                                                            │
│ runtime ADG nodes:                                                                                          │
│ - RetrievalQuery                                                                                            │
│ - EvidenceChunk                                                                                             │
│ - EntitySubgraph                                                                                            │
│ - EvidenceContract                                                                                          │
│                                                                                                            │
│ runtime ADG edges:                                                                                          │
│ - RetrievalQuery searches L4ReadShelf                                                                       │
│ - RetrievalQuery matches EvidenceChunk                                                                      │
│ - EntitySubgraph connects EvidenceChunk                                                                     │
│ - EvidenceContract emits verified evidence                                                                  │
│                                                                                                            │
│ best-practice add:                                                                                          │
│ - hybrid retrieval should expose dense vector, sparse/BM25, rerank, graph traversal, and provenance fields  │
│ - every answerable claim later must map back to evidence_ids and citation_span_ids                           │
└──────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                               │
                                               ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PROMPT ASSEMBLY                                                                                            │
│ Packages the bounded prompt. It does not retrieve new facts or invent policy.                              │
│                                                                                                            │
│ spans:                                                                                                     │
│ - PA.static_blocks.load                                                                                    │
│ - PA.context.slot                                                                                          │
│ - PA.token_budget                                                                                          │
│ - PA.prompt.contract                                                                                       │
│                                                                                                            │
│ required span attrs:                                                                                        │
│ - prompt_envelope_hash, system_template_hash, task_template_hash, output_schema_hash                        │
│ - evidence_ids, citation_span_ids, contradiction_flags, must_use_context_ids                                │
│ - token_budget_total, token_budget_used, trim_strategy, overflow_action                                     │
│ - hmac, replay_metadata, prompt_hash, prompt_version                                                        │
│                                                                                                            │
│ runtime ADG nodes:                                                                                          │
│ - PromptEnvelope                                                                                            │
│ - BoundedPromptPacket                                                                                       │
│                                                                                                            │
│ runtime ADG edges:                                                                                          │
│ - PromptEnvelope packages EvidenceContract                                                                  │
│ - PromptEnvelope emits BoundedPromptPacket                                                                  │
│ - BoundedPromptPacket dispatches_to L2                                                                      │
│                                                                                                            │
│ best-practice add:                                                                                          │
│ - prompt assembly should preserve instruction order, evidence provenance, and citation anchors              │
└──────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                               │
                                               ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L2 EXECUTION                                                                                                │
│ Executes the current bounded step only. Tool/model/action runs here. No durable commit authority.           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ span: L2.step.prepare                                                                                       │
│ required span attrs:                                                                                        │
│ - step_id, parent_step_id, blueprint_hash, policy_hash, idempotency_key, replay_key                          │
│ - capability_token_hash, sandbox_scope, fs_scope, net_scope, tool_allowlist, model_allowlist                 │
│ runtime ADG node: ExecutionStep                                                                             │
│ runtime ADG edges: ExecutionStep receives StepPacket | ExecutionStep binds ReplayEnvelope                    │
│                                                                                                            │
│ span: L2.step.validate                                                                                      │
│ required span attrs:                                                                                        │
│ - validation_packet_id, input_schema_status, side_effect_class, sandbox_status, budget_scope                 │
│ - mutation_intent_detected, write_auth=false_inside_L2                                                       │
│ runtime ADG node: ValidationPacket                                                                          │
│ runtime ADG edges: ValidationPacket validates ExecutionStep | blocks/allows ExecutionAttempt                 │
│                                                                                                            │
│ span: L2.model.invoke                                                                                       │
│ required span attrs:                                                                                        │
│ - model_id, provider, decoding_config_hash, prompt_hash, prompt_tokens, output_tokens                        │
│ - latency_ms, stop_reason, response_id, model_output_hash                                                   │
│ runtime ADG node: ModelInvocation                                                                           │
│ runtime ADG edges: ModelInvocation consumes PromptEnvelope | emits ModelOutput                               │
│                                                                                                            │
│ span: L2.tool.invoke                                                                                        │
│ required span attrs:                                                                                        │
│ - tool_name, tool_version, args_hash, return_code, stdout_hash, stderr_hash                                  │
│ - side_effect_class, latency_ms, timeout_status, circuit_breaker_status                                      │
│ runtime ADG node: ToolInvocation                                                                            │
│ runtime ADG edges: ToolInvocation invokes Tool | consumes ToolArgs | emits ToolResult                        │
│                                                                                                            │
│ span: L2.heal.attempt                                                                                       │
│ required span attrs:                                                                                        │
│ - error_code, reason_code, retry_count, repair_count, healing_tier, parent_attempt_id                        │
│ - oscillation_guard_status, terminal_repair_status                                                          │
│ runtime ADG node: HealingAttempt                                                                            │
│ runtime ADG edges: HealingAttempt repairs FailedAttempt | retries ExecutionAttempt                           │
│                                                                                                            │
│ span: L2.step.seal                                                                                          │
│ required span attrs:                                                                                        │
│ - terminal_class, output_artifact_ids, evidence_ids, lineage_hash, replay_key, output_hash                   │
│ - state_diff_hash, proposed_mutation_hash, attempt_count, validation_counters                                │
│ runtime ADG node: SealedL2Artifact                                                                          │
│ runtime ADG edges: SealedL2Artifact seals ExecutionResult | emits ExitEvalInput                              │
│                                                                                                            │
│ best-practice add:                                                                                          │
│ - tool lifecycle must be visible as model/tool/application handoff, not hidden in one generic execute span   │
│ - mutation intent can be recorded, but L2 must never become the durable writer                               │
└──────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                               │
                                               ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ EXIT EVAL / CURRENT-RUN CONTROL                                                                             │
│ Receives sealed L2 artifacts or terminal L0 returns. Decides allow, deny, reroute, escalate, commit request.│
│                                                                                                            │
│ spans:                                                                                                     │
│ - Exit.eval.policy                                                                                         │
│ - Exit.eval.quality                                                                                        │
│ - Exit.eval.safety                                                                                         │
│ - Exit.eval.mutation_auth                                                                                  │
│ - Exit.disposition                                                                                         │
│                                                                                                            │
│ required span attrs:                                                                                        │
│ - exit_disposition=allow|deny|reroute|escalate|commit_request                                               │
│ - policy_hash, compliance_hash, groundedness_check, citation_support_check                                  │
│ - schema_check, safety_check, mutation_auth_result, reason_codes                                            │
│ - hitl_required, hitl_packet_id, hitl_decision, final_output_hash                                           │
│                                                                                                            │
│ runtime ADG nodes:                                                                                          │
│ - ExitDisposition                                                                                           │
│ - RuntimeOutcome                                                                                            │
│ - HITLPacket optional                                                                                       │
│                                                                                                            │
│ runtime ADG edges:                                                                                          │
│ - ExitDisposition evaluates SealedL2Artifact                                                                │
│ - ExitDisposition allows/denies/reroutes/escalates RuntimeOutcome                                           │
│ - ExitDisposition requests_commit through UWG only                                                          │
│                                                                                                            │
│ best-practice add:                                                                                          │
│ - eval should be both policy-grade and answer-grade, not just "did the tool return successfully?"           │
└──────────────────────┬──────────────────────────────────────────────────────────────────────┬──────────────┘
                       │                                                                      │
                       │ allow / finish, no durable write                                     │ commit request
                       ▼                                                                      ▼

┌────────────────────────────────────────────────────────────────────┐       ┌────────────────────────────────────────────────────────────────────┐
│ RESPONSE / NO WRITE                                                 │       │ UWG / L4 COMMIT                                                     │
│ Runtime answer leaves. No durable mutation.                         │       │ Only if Exit issued commit request.                                 │
├────────────────────────────────────────────────────────────────────┤       ├────────────────────────────────────────────────────────────────────┤
│ spans:                                                             │       │ spans:                                                             │
│ - Response.emit                                                    │       │ - UWG.commit.verify_authority                                      │
│ - Runtime.close_no_write                                           │       │ - UWG.commit.validate_diff                                         │
│                                                                    │       │ - UWG.commit.append_ledger                                         │
│ required span attrs:                                                │       │ - L4.archive.materialize                                           │
│ - response_id, final_output_hash, no_write_marker=true              │       │                                                                    │
│ - caller_delivery_status, runtime_closed=true                       │       │ required span attrs:                                                │
│                                                                    │       │ - commit_request_id, mutation_type, proposed_diff_hash              │
│ runtime ADG nodes:                                                  │       │ - before_hash, after_hash, ledger_hash, rollback_ref                │
│ - RuntimeResponse                                                   │       │ - commit_id, alias_swap_status, audit_receipt_id                    │
│                                                                    │       │ - write_lock_id, serialized_queue_position                          │
│ runtime ADG edges:                                                  │       │                                                                    │
│ - RuntimeResponse returns_to Caller                                 │       │ runtime ADG nodes:                                                  │
│ - RuntimeResponse closes RuntimeRun                                 │       │ - L4Commit                                                          │
│                                                                    │       │ - LedgerAppend                                                      │
│ best-practice add:                                                  │       │                                                                    │
│ - explicitly record no_write_marker so "allowed response" is not    │       │ runtime ADG edges:                                                  │
│   confused with committed state mutation                            │       │ - L4Commit commits_to L4Archive                                     │
└──────────────────────────────┬─────────────────────────────────────┘       │ - LedgerAppend appends LedgerChain                                  │
                               │                                             │ - L4Commit refreshes ReadSurfaces                                   │
                               │                                             │                                                                    │
                               │                                             │ best-practice add:                                                  │
                               │                                             │ - commit spans must prove authority, diff, before/after state,       │
                               │                                             │   rollback, and ledger append                                       │
                               │                                             └──────────────────────────────┬─────────────────────────────────────┘
                               │                                                                            │
                               └────────────────────────────────────────────┬───────────────────────────────┘
                                                                            ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L6 EVAL METRICS / SHADOW EVALUATION                                                                         │
│ After runtime boundary. Observer only. No live mutation.                                                     │
│                                                                                                            │
│ spans:                                                                                                     │
│ - L6.telemetry.ingest                                                                                       │
│ - L6.outcome.evaluate                                                                                       │
│ - L6.trajectory.evaluate                                                                                    │
│ - L6.retrieval.evaluate                                                                                     │
│ - L6.replay.verify                                                                                          │
│ - L6.metrics.seal                                                                                           │
│                                                                                                            │
│ required span attrs:                                                                                        │
│ - task_completion_score, groundedness_score, citation_support_score, answer_relevance_score                 │
│ - retrieval_precision, retrieval_recall_proxy, support_rate, contradiction_rate                             │
│ - trajectory_score, tool_order_score, retry_thrash, budget_adherence_score                                  │
│ - latency_ms, token_cost, tool_cost, drift_flags, anomaly_flags                                             │
│ - replay_digest, determinism_status, eval_bundle_id, grader_id, human_calibration_status                    │
│                                                                                                            │
│ runtime ADG nodes:                                                                                          │
│ - L6EvidenceBundle                                                                                          │
│ - EvalSignalBundle                                                                                          │
│ - ReplayVerification                                                                                        │
│                                                                                                            │
│ runtime ADG edges:                                                                                          │
│ - L6EvidenceBundle observes RuntimeRun                                                                      │
│ - EvalSignalBundle grades RuntimeOutcome                                                                    │
│ - ReplayVerification verifies SealedL2Artifact                                                              │
│                                                                                                            │
│ best-practice add:                                                                                          │
│ - eval metrics should grade outcome, retrieval support, trajectory, safety, replayability, and cost          │
│ - model graders should be calibrated with human review before being treated as authoritative                 │
└──────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┘
                                               │
                                               ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ META-LEARNING / FUTURE-RUN PROMOTION                                                                        │
│ Future-run only. Learning proposes updates. Approved updates must pass gauntlet and UWG/L4 before use.      │
│                                                                                                            │
│ spans:                                                                                                     │
│ - MetaLearning.signal.fuse                                                                                  │
│ - MetaLearning.rca.create                                                                                   │
│ - MetaLearning.pattern.extract                                                                              │
│ - MetaLearning.rule.draft                                                                                   │
│ - MetaLearning.shadow_replay                                                                                │
│ - MetaLearning.promotion.propose                                                                            │
│ - MetaLearning.promotion.approve_or_reject                                                                  │
│ - MetaLearning.promotion.commit        only after approval through UWG                                      │
│                                                                                                            │
│ required span attrs:                                                                                        │
│ - RCA_id, incident_cluster_id, pattern_id, severity, confidence_band                                        │
│ - proposed_rule_update_hash, proposed_prompt_update_hash, proposed_policy_update_hash                       │
│ - promotion_candidate_id, shadow_replay_result, regression_result, SME_signoff_status                       │
│ - approved_update_id, future_run_only=true, rollback_plan_hash                                              │
│                                                                                                            │
│ runtime ADG nodes:                                                                                          │
│ - IncidentCluster                                                                                           │
│ - RCARecord                                                                                                 │
│ - PromotionCandidate                                                                                        │
│ - ApprovedLearningUpdate                                                                                    │
│                                                                                                            │
│ runtime ADG edges:                                                                                          │
│ - RCARecord learns_from EvalSignalBundle                                                                    │
│ - PromotionCandidate proposes UpdateCandidate                                                               │
│ - ApprovedLearningUpdate promotes_via UWG/L4                                                                │
│                                                                                                            │
│ best-practice add:                                                                                          │
│ - never let eval or learning mutate the completed run                                                       │
│ - learning updates must be replay-tested, regression-tested, approved, committed, and rollout-receipted      │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


────────────────────────────────────────────────────────────────────────────────────────────────────────────
RUNTIME ADG COVERAGE DIAGNOSTIC
────────────────────────────────────────────────────────────────────────────────────────────────────────────

EXPECTED FROM RUN REGISTRY / L4 / REPLAY
      │
      ▼
┌────────────────────────────────────┐
│ expected traceIDs                  │
│ T-001, T-002, T-003, ...           │
└──────────────┬─────────────────────┘
               │ compare
               ▼
┌────────────────────────────────────┐
│ actual OTEL traceIDs               │
│ traces found in exported spans     │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ COVERAGE CHECK                                                                                             │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ traceID missing entirely        -> run had no telemetry                                                     │
│ Intake span missing             -> run shell exists but trace root was not emitted                           │
│ L1 span missing                 -> intent/plan is invisible                                                  │
│ L0 span missing                 -> route decision cannot be audited                                           │
│ L3 span missing                 -> managed workflow cannot reconstruct dependency graph                       │
│ C0 span missing                 -> grounded answer cannot prove retrieval, hybrid search, rerank, graph path  │
│ PA span missing                 -> prompt cannot prove which evidence and instructions were packaged          │
│ L2 model/tool span missing      -> actual model/tool execution is invisible                                  │
│ L2 seal span missing            -> output lacks replay, lineage, and artifact proof                           │
│ Exit span missing               -> no authoritative allow/deny/escalate/commit disposition                    │
│ UWG/L4 span missing             -> commit cannot be tied to ledger proof                                      │
│ L6 span missing                 -> no eval metrics, retrieval grade, replay verification, or cost view        │
│ Meta-learning span missing      -> future-run learning has no RCA, promotion, or rollback lineage             │
│ spans have different traceIDs   -> trace propagation is broken                                                │
│ parent_id missing/broken        -> runtime ADG tree cannot reconstruct execution path                         │
│ missing evidence IDs            -> RAG cannot prove groundedness                                              │
│ missing graph entity/edge IDs   -> GraphRAG cannot prove relationship path                                    │
│ missing policy/replay hashes    -> governance and determinism cannot be certified                             │
│ all required spans present      -> runtime ADG coverage is probably healthy                                   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘