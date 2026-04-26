========================================================================================================================
RUNTIME GATES REQUIREMENTS SPEC
Target: Agentic-Workflow / Windsurf Implementation
Purpose: Formalize best-in-class runtime gate mesh for live agentic execution
Scope: Current-run gates only, plus runtime regression/anomaly protection
Out of Scope: CI/CD promotion gates, shadow rollout, canary rollout, offline regression suites, judge calibration pipelines
========================================================================================================================

CORE DISTINCTION
------------------------------------------------------------------------------------------------------------------------
Runtime gates govern the CURRENT LIVE RUN.

They decide whether a specific:
- request
- route
- retrieval packet
- prompt packet
- tool call
- workflow step
- model invocation
- output
- escalation
- write proposal

is allowed to proceed right now.

CI/CD / promotion gates govern the NEXT SYSTEM VERSION.

They decide whether a candidate:
- prompt version
- model version
- policy version
- tool version
- routing version
- evaluator version
- memory/rubric/config version

can move through:
shadow -> canary -> staged rollout -> full rollout -> rollback.

Runtime regression protection is allowed in this spec only as LIVE ANOMALY CONTAINMENT:
"Is this current run behaving materially worse, stranger, slower, riskier, or less grounded than its expected class?"

========================================================================================================================
AUTHORITATIVE RUNTIME DECISIONS
========================================================================================================================

Every runtime gate MUST return one of the following bounded dispositions:

┌──────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────┐
│ DISPOSITION          │ MEANING                                                                                      │
├──────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ ALLOW                │ Continue current run unchanged                                                               │
│ DENY                 │ Stop current run or requested action                                                        │
│ CLARIFY              │ Ask user for missing critical information                                                   │
│ ABSTAIN              │ Return safe non-answer when support/scope is insufficient                                    │
│ REROUTE              │ Send back to L1/L0 for a new governed route decision                                         │
│ SHRINK_SCOPE         │ Reduce action/tool/data scope to safe bounded subset                                         │
│ RETRY                │ Retry same step within explicit max attempts and same policy snapshot                        │
│ HEAL                 │ Apply bounded deterministic repair or governed repair lane                                    │
│ ESCALATE_HITL        │ Freeze and materialize bounded packet for human review                                       │
│ QUARANTINE           │ Isolate unsafe/untrusted content so it cannot enter prompt/tool context                      │
│ REDACT               │ Remove secrets, PII, cross-tenant data, or unsafe spans                                      │
│ SAFE_FALLBACK        │ Return safest supported answer/path                                                         │
│ MARK_DEGRADED        │ Continue only with degraded/non-certified status and audit note                              │
│ COMMIT_REQUEST       │ Submit proposed durable mutation to UWG only                                                 │
│ BLOCK_COMMIT         │ Block durable write even if answer/action can finish                                         │
└──────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────┘

Hard invariant:
No runtime gate may silently bypass, mutate durable state, or expand its own authority.

========================================================================================================================
RUNTIME GATE MESH OVERVIEW
========================================================================================================================

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ LIVE REQUEST PATH                                                                                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ U0 / Intake                                                                                                          │
│   G01 Request ingress gate                                                                                           │
│   G02 Identity / tenant / session gate                                                                               │
│   G03 Intent / ambiguity gate                                                                                        │
│   G04 Initial safety / policy screen                                                                                 │
│                                                                                                                      │
│ L1 / Reasoning + Plan                                                                                                │
│   G03 Intent clarity gate                                                                                            │
│   G04 Policy-safe plan gate                                                                                          │
│   G05 Risk tier gate                                                                                                 │
│   G18 Plan / trajectory shape pre-check                                                                              │
│                                                                                                                      │
│ L0 / Route Decision                                                                                                  │
│   G07 Route selection gate                                                                                           │
│   G08 Grounding requirement gate                                                                                     │
│   G10 Cache / freshness / reuse gate                                                                                 │
│   G20 Cost tier / SLO gate                                                                                           │
│                                                                                                                      │
│ C0 / Retrieval + Prompt Assembly                                                                                     │
│   G08 Retrieval plan gate                                                                                            │
│   G09 Evidence quality gate                                                                                          │
│   G13 Retrieved/tool content trust gate                                                                              │
│   G17 ACL / tenant / privacy gate                                                                                    │
│   G10 Prompt packet authority-order gate                                                                             │
│                                                                                                                      │
│ L3 / Workflow Orchestration                                                                                          │
│   G18 Workflow trajectory gate                                                                                       │
│   G19 Loop / retry / thrash gate                                                                                     │
│   G20 Budget / latency / cost gate                                                                                   │
│   G25 Runtime regression / anomaly gate                                                                              │
│                                                                                                                      │
│ L2 / Execution                                                                                                       │
│   G11 Tool/model registry gate                                                                                       │
│   G12 Tool argument gate                                                                                             │
│   G14 External egress gate                                                                                           │
│   G15 Filesystem / shell / data access gate                                                                          │
│   G21 Output schema gate                                                                                             │
│   G24 Determinism / replay gate                                                                                      │
│                                                                                                                      │
│ Exit / L5 / UWG                                                                                                      │
│   G22 Output quality gate                                                                                            │
│   G23 Security / leakage gate                                                                                        │
│   G26 Exit disposition gate                                                                                          │
│   G27 Durable write sovereignty gate                                                                                 │
│   G28 Audit / trace completeness gate                                                                                │
│                                                                                                                      │
│ L6 / Shadow Evidence, Current-Run Signals, Future-Run Learning                                                       │
│   G25 Runtime anomaly evidence                                                                                        │
│   G29 Learning firewall                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

========================================================================================================================
FORMAL RUNTIME GATE REQUIREMENTS
========================================================================================================================

┌──────┬──────────────────────────────────────┬──────────────────────┬───────────────────────────────────────────────┐
│ ID   │ GATE FAMILY                          │ PRIMARY LAYER         │ RUNTIME QUESTION                              │
├──────┼──────────────────────────────────────┼──────────────────────┼───────────────────────────────────────────────┤
│ G01  │ Request ingress gate                 │ U0 / Intake           │ Is this a valid, intelligible live request?  │
│ G02  │ Identity / tenant / session gate     │ U0 / L5               │ Who is asking and under what boundary?       │
│ G03  │ Intent / ambiguity gate              │ U0 / L1               │ Is the task clear enough to proceed?         │
│ G04  │ Safety / policy gate                 │ U0 / L1 / L5          │ Is the request or plan policy-compliant?     │
│ G05  │ Risk tier gate                       │ L1 / L0 / L5          │ Is autonomy allowed for this risk class?     │
│ G06  │ HITL approval gate                   │ L5 / Exit             │ Must a human approve before execution/write? │
│ G07  │ Route selection gate                 │ L0                   │ Which governed route is allowed?             │
│ G08  │ Retrieval / grounding gate           │ L0 / C0               │ Is grounding required and supportable?       │
│ G09  │ Evidence quality gate                │ C0                   │ Is evidence relevant, fresh, cited, safe?    │
│ G10  │ Prompt assembly gate                 │ PA                   │ Is the prompt packet bounded and ordered?    │
│ G11  │ Tool/model registry gate             │ L2 / C7               │ Is tool/model allowed for this route?        │
│ G12  │ Tool argument gate                   │ L2 / C7               │ Are args typed, scoped, and safe?            │
│ G13  │ Tool/retrieved output trust gate     │ C0 / PA / L2          │ Can returned content enter context safely?   │
│ G14  │ External egress gate                 │ L2 / C7               │ Is provider/network/API egress approved?     │
│ G15  │ Filesystem / shell / data gate       │ L2                   │ Is data access inside declared sandbox?      │
│ G16  │ Memory access gate                   │ L1 / C0 / L4 / L5     │ Can memory be read or proposed for update?   │
│ G17  │ Privacy / cross-context gate         │ All / L5              │ Is there tenant/session/user data bleed?     │
│ G18  │ Workflow trajectory gate             │ L3                   │ Is step order sane, bounded, and aligned?    │
│ G19  │ Loop / retry / thrash gate           │ L3 / L2               │ Is the agent spinning or retrying badly?     │
│ G20  │ Cost / latency / budget gate         │ L0 / L3 / L2          │ Is run within token/time/cost/SLO budget?    │
│ G21  │ Output schema gate                   │ L2 / Exit             │ Does output match required schema/format?    │
│ G22  │ Output quality gate                  │ Exit / L5             │ Is answer complete, grounded, useful?        │
│ G23  │ Security / leakage gate              │ U0 / C0 / L2 / Exit   │ Any injection, jailbreak, secret leakage?    │
│ G24  │ Determinism / replay gate            │ C1 / L2 / L6          │ Is run replay-certifiable enough?            │
│ G25  │ Runtime regression / anomaly gate    │ L3 / L6 / Exit        │ Is this run abnormal vs its expected class?  │
│ G26  │ Exit disposition gate                │ Exit / L5             │ Can sealed result leave current run?         │
│ G27  │ Durable write sovereignty gate       │ UWG / L4              │ Can proposed mutation become durable state?  │
│ G28  │ Audit / trace completeness gate      │ L6 / Exit             │ Is evidence complete enough for audit?       │
│ G29  │ Learning firewall gate               │ L6 / UWG              │ Is learning future-run-only and governed?    │
└──────┴──────────────────────────────────────┴──────────────────────┴───────────────────────────────────────────────┘

========================================================================================================================
G01 REQUEST INGRESS GATE
========================================================================================================================

Purpose:
- Prevent invalid, malformed, abusive, unintelligible, or out-of-scope requests from entering deeper runtime.

Required checks:
- MUST validate accepted transport and envelope shape.
- MUST assign request_id, session_id, trace_root.
- MUST enforce size, quota, and duplicate controls.
- MUST reject malformed request schemas before L1.
- MUST detect obvious unsafe or abusive input.
- MUST produce normalized validated_request or rejection reason.

Allowed decisions:
- ALLOW
- DENY
- CLARIFY
- SAFE_FALLBACK
- THROTTLE if implemented

Regression signals:
- ingress_reject_rate spike
- malformed_request_rate spike
- jailbreak_attempt_rate spike
- duplicate_request_rate spike
- quota_violation_rate spike

Stop condition:
- If no valid request envelope exists, downstream L1/L0/C0/L2 MUST NOT run.

========================================================================================================================
G02 IDENTITY / TENANT / SESSION GATE
========================================================================================================================

Purpose:
- Bind caller identity, tenant scope, session scope, region, and access baseline.

Required checks:
- MUST authenticate or classify caller identity.
- MUST bind tenant/session/region scope.
- MUST verify caller is allowed to access requested resource class.
- MUST prevent cross-tenant and cross-session bleed.
- MUST stamp caller_scope_baseline into the runtime envelope.

Allowed decisions:
- ALLOW
- DENY
- RESTRICT
- REDACT
- ESCALATE_HITL

Regression signals:
- cross_tenant_near_miss_count
- unauthorized_resource_attempt_rate
- session_scope_mismatch_count
- ACL_denial_rate spike

Stop condition:
- If tenant/session boundary cannot be established, request MUST fail closed.

========================================================================================================================
G03 INTENT / AMBIGUITY GATE
========================================================================================================================

Purpose:
- Ensure the system understands enough to act safely.

Required checks:
- MUST identify primary objective.
- MUST identify requested deliverable.
- MUST capture hard constraints, soft constraints, exclusions.
- MUST detect ambiguity in target, action, recipient, file, data source, time range, or write scope.
- MUST distinguish read-only, answer-only, external action, durable write, and workflow asks.

Allowed decisions:
- ALLOW
- CLARIFY
- ABSTAIN
- SAFE_FALLBACK
- SHRINK_SCOPE

Regression signals:
- clarification_rate spike
- wrong_intent_user_correction_rate
- task_reclassification_rate
- ambiguous_action_attempts

Stop condition:
- If ambiguity affects irreversible action, external egress, or durable write, system MUST clarify or escalate before action.

========================================================================================================================
G04 SAFETY / POLICY GATE
========================================================================================================================

Purpose:
- Enforce current policy across request, plan, route, execution, and exit.

Required checks:
- MUST load active policy_hash.
- MUST classify safety risk.
- MUST detect disallowed requests and unsafe transformations.
- MUST enforce policy before tool/model execution.
- MUST fail closed on policy mismatch.
- MUST bind compliance_hash to governed packet.

Allowed decisions:
- ALLOW
- DENY
- SAFE_FALLBACK
- SHRINK_SCOPE
- ESCALATE_HITL
- REROUTE

Regression signals:
- refusal_rate unexpected drop
- safety_classifier_low_confidence_rate
- policy_mismatch_count
- unsafe_request_pass_through_count

Stop condition:
- If policy_hash is missing or inconsistent, route/execution MUST NOT proceed.

========================================================================================================================
G05 RISK TIER GATE
========================================================================================================================

Purpose:
- Set autonomy level based on risk, reversibility, blast radius, and user explicitness.

Required checks:
- MUST classify read-only vs action vs write vs external egress.
- MUST classify reversible vs irreversible.
- MUST classify low/medium/high impact.
- MUST detect production, financial, legal, medical, security, privacy, or customer-facing consequences.
- MUST lower autonomy for high-impact or irreversible operations.

Allowed decisions:
- ALLOW
- SHRINK_SCOPE
- ESCALATE_HITL
- DENY
- SAFE_FALLBACK

Regression signals:
- high_risk_action_rate spike
- human_reversal_rate spike
- unapproved_mutation_attempt_count
- risk_tier_misclassification_count

Stop condition:
- High-impact irreversible action MUST NOT execute without explicit HITL or user confirmation gate.

========================================================================================================================
G06 HITL APPROVAL GATE
========================================================================================================================

Purpose:
- Pause live execution when human authorization is required.

Required checks:
- MUST freeze packet before human review.
- MUST materialize bounded evidence packet.
- MUST treat human input as data, not sovereign authority.
- MUST re-clear human-modified output through L5.
- MUST preserve audit trail of approve / modify / reject.

Allowed decisions:
- ESCALATE_HITL
- APPROVE_TO_CONTINUE
- MODIFY_THEN_RECLEAR
- REJECT
- RETURN_TO_L1
- BLOCK_COMMIT

Regression signals:
- HITL_approval_latency
- HITL_rejection_rate
- HITL_modify_rate
- repeated_HITL_same_reason_code

Stop condition:
- Human approval MUST NOT bypass L5 re-clearance or UWG write path.

========================================================================================================================
G07 ROUTE SELECTION GATE
========================================================================================================================

Purpose:
- Select the one governed runtime path.

Required checks:
- MUST consume L1 plan contract.
- MUST emit exactly one deterministic RouteContract.
- MUST not retrieve, execute, mutate, or approve output.
- MUST decide among cache, grounded read, single action, managed workflow, fallback.
- MUST attach route_id, confidence, reason_codes, freshness_class, cache_policy, execution_form, cost_tier, fallback_chain, SLO, tenant_scope, hmac_sig.
- MUST send terminal RET routes directly to Exit Control.

Allowed decisions:
- ROUTE_R1_EXACT_CACHE
- ROUTE_R1_SEMANTIC_CACHE
- ROUTE_R3_GROUNDED_READ
- ROUTE_R4_SINGLE_ACTION
- ROUTE_R3_R4_MANAGED_WORKFLOW
- ROUTE_R5_FALLBACK
- REROUTE
- DENY

Regression signals:
- route_distribution_shift
- unexpected_high_cost_route_rate
- cache_hit_rate_collapse
- wrong_route_user_correction_rate
- route_digest_mismatch

Stop condition:
- If RouteContract cannot be signed or replayed, downstream execution MUST NOT proceed.

========================================================================================================================
G08 RETRIEVAL / GROUNDING GATE
========================================================================================================================

Purpose:
- Determine whether grounded evidence is required and whether retrieval can safely support the task.

Required checks:
- MUST scope source, freshness, ACL, tenant, support target.
- MUST choose retrieval modes: dense, sparse/BM25, graph, metadata, cache if allowed.
- MUST reject blocked sources.
- MUST enforce max_k, max_graph_hops, max_refine_attempts.
- MUST never answer, route, execute, or mutate from C0.

Allowed decisions:
- RETRIEVE
- REFINE_RETRIEVAL
- BROADEN
- NARROW
- DECOMPOSE
- ABSTAIN
- REROUTE_RECOMMENDATION_ONLY

Regression signals:
- retrieval_empty_rate
- weak_support_rate
- ACL_block_rate
- stale_source_rate
- max_refine_exceeded_count

Stop condition:
- If factual/policy claim requires evidence and evidence is empty/blocked, system MUST abstain, caveat, or fallback.

========================================================================================================================
G09 EVIDENCE QUALITY GATE
========================================================================================================================

Purpose:
- Verify that evidence is strong enough to support an answer or action.

Required checks:
- MUST verify source_id resolves.
- MUST verify cited spans/line refs/anchors.
- MUST verify version/snapshot.
- MUST preserve source lineage.
- MUST flag contradictions.
- MUST score direct support, coverage, freshness, authority, contradiction risk, unsupported inference risk.
- MUST produce EvidenceContract.

Allowed decisions:
- PASS
- WEAK_WITH_CAVEATS
- CONFLICTED
- EMPTY
- BLOCKED
- ABSTAIN
- REFINE_ONCE

Regression signals:
- citation_support_rate_drop
- unsupported_inference_rate
- contradiction_hidden_rate
- evidence_contract_failure_rate
- Recall@K / MRR degradation

Stop condition:
- No answer may present unsupported evidence as certain.

========================================================================================================================
G10 PROMPT ASSEMBLY GATE
========================================================================================================================

Purpose:
- Ensure prompt packet is bounded, authority-ordered, replayable, and injection-resistant.

Required checks:
- MUST preserve slot authority order.
- MUST treat U0 as task intent only.
- MUST treat retrieved/tool content as data, not instruction.
- MUST bind output schema through provider response schema where possible.
- MUST bind tool schemas through provider tool field where possible.
- MUST apply deterministic token budgeting.
- MUST emit signed CompiledPromptArtifact with HMAC, manifest_hash, replay metadata.

Canonical slot order:
S0 -> D0 -> I0 -> E0 -> C0 -> M0 -> U0 -> H0
R0 bound through API response_schema / response_format, not prose.

Allowed decisions:
- EMIT
- REBUILD
- REJECT
- SHRINK_CONTEXT
- QUARANTINE_CONTEXT
- REQUEST_RETRIEVAL_REFINEMENT

Regression signals:
- prompt_budget_overflow_rate
- prompt_injection_near_miss_count
- schema_binding_missing_rate
- prompt_manifest_mismatch_count
- deterministic_prompt_diff_count

Stop condition:
- If lower-authority content can override higher-authority instructions, prompt MUST NOT dispatch.

========================================================================================================================
G11 TOOL / MODEL REGISTRY GATE
========================================================================================================================

Purpose:
- Ensure only approved tools/models/providers are invoked.

Required checks:
- MUST verify tool/model identity.
- MUST verify allowed_models / allowed_tools.
- MUST verify provider mapping.
- MUST block silent fallback.
- MUST validate registry digest integrity.
- MUST check capability roster.

Allowed decisions:
- ALLOW
- BLOCK
- SUBSTITUTE_APPROVED
- REROUTE
- ESCALATE_HITL

Regression signals:
- unknown_tool_attempt_count
- silent_fallback_attempt_count
- provider_drift_count
- registry_digest_mismatch_count
- tool_availability_failure_rate

Stop condition:
- Tool/model not on approved roster MUST NOT be invoked.

========================================================================================================================
G12 TOOL ARGUMENT GATE
========================================================================================================================

Purpose:
- Validate runtime tool arguments before invocation.

Required checks:
- MUST validate argument schema.
- MUST validate target was user-specified or policy-authorized.
- MUST validate path/resource/recipient/amount/time range.
- MUST enforce least privilege.
- MUST reject broad wildcards for risky actions.
- MUST bind idempotency key for mutating actions.

Allowed decisions:
- ALLOW
- SHRINK_SCOPE
- REJECT
- CLARIFY
- ESCALATE_HITL

Regression signals:
- tool_arg_validation_failure_rate
- broad_scope_arg_attempt_count
- inferred_target_action_rate
- idempotency_key_missing_count

Stop condition:
- Dangerous or mutating tool calls with ambiguous target MUST NOT execute.

========================================================================================================================
G13 TOOL / RETRIEVED OUTPUT TRUST GATE
========================================================================================================================

Purpose:
- Prevent untrusted content from hijacking model context or execution.

Required checks:
- MUST classify origin: user_turn, retrieved, tool_output, human_review, system, policy.
- MUST scan retrieved/tool output for embedded instructions.
- MUST detect jailbreaks, hidden text, coercive instructions, data exfiltration attempts.
- MUST strip/quarantine unsafe spans.
- MUST prevent quarantined content from entering prompt documents/context.

Allowed decisions:
- PASS_AS_DATA
- STRIP
- QUARANTINE
- REJECT
- REROUTE
- SAFE_FALLBACK

Regression signals:
- tool_output_injection_rate
- quarantine_rate_spike
- unsafe_content_pass_through_count
- connector_poisoning_count

Stop condition:
- Untrusted content MUST NOT be treated as instruction.

========================================================================================================================
G14 EXTERNAL EGRESS GATE
========================================================================================================================

Purpose:
- Govern calls outside the local runtime boundary.

Required checks:
- MUST verify provider/API/network target is approved.
- MUST verify exact data leaving the system.
- MUST enforce no silent provider fallback.
- MUST apply privacy/security redaction before egress.
- MUST record invocation receipt.

Allowed decisions:
- ALLOW
- DENY
- REDACT_AND_ALLOW
- ESCALATE_HITL
- BLOCK_COMMIT

Regression signals:
- unexpected_network_call_count
- external_egress_denial_rate
- secret_redaction_count
- provider_fallback_attempt_count

Stop condition:
- External egress without approved provider mapping MUST fail closed.

========================================================================================================================
G15 FILESYSTEM / SHELL / DATA ACCESS GATE
========================================================================================================================

Purpose:
- Bound runtime filesystem, shell, and data access.

Required checks:
- MUST enforce fs_scope.
- MUST enforce syscall/shell/network scope.
- MUST block destructive commands unless explicitly authorized.
- MUST block credential exploration.
- MUST block out-of-scope path traversal.
- MUST distinguish read vs write vs delete.

Allowed decisions:
- ALLOW
- DENY
- SANDBOX
- SHRINK_SCOPE
- ESCALATE_HITL

Regression signals:
- out_of_scope_path_attempt_count
- blocked_shell_command_rate
- credential_access_attempt_count
- destructive_command_attempt_count

Stop condition:
- Shell/filesystem access outside sandbox envelope MUST NOT execute.

========================================================================================================================
G16 MEMORY ACCESS GATE
========================================================================================================================

Purpose:
- Control read/write access to memory and durable state.

Required checks:
- MUST distinguish memory read vs proposed memory update.
- MUST verify relevance and tenant/session scope.
- MUST block sensitive or irrelevant memory bleed.
- MUST require UWG for durable memory writes.
- MUST support no-memory mode where required.

Allowed decisions:
- READ_ALLOW
- READ_DENY
- REDACT
- PROPOSE_UPDATE
- BLOCK_UPDATE
- ESCALATE_HITL

Regression signals:
- irrelevant_memory_reference_rate
- cross_context_memory_near_miss_count
- memory_write_rejection_rate
- sensitive_memory_trigger_count

Stop condition:
- L1/L2/L6 MUST NOT directly mutate durable memory.

========================================================================================================================
G17 PRIVACY / CROSS-CONTEXT GATE
========================================================================================================================

Purpose:
- Prevent user, tenant, session, connector, or task data bleed.

Required checks:
- MUST enforce tenant ACL at every retrieval and graph hop.
- MUST prevent session-to-session bleed.
- MUST detect PII/secrets in output.
- MUST prevent unrelated private context from influencing answer.
- MUST validate connector permission freshness.

Allowed decisions:
- ALLOW
- REDACT
- DENY
- ISOLATE
- REQUIRE_PERMISSION
- FORCE_TENANT_SCOPED_RETRIEVAL

Regression signals:
- redaction_event_rate
- cross_context_near_miss_count
- connector_permission_error_rate
- tenant_acl_violation_count

Stop condition:
- Cross-tenant or cross-session leakage MUST block output.

========================================================================================================================
G18 WORKFLOW TRAJECTORY GATE
========================================================================================================================

Purpose:
- Control multi-step workflow behavior.

Required checks:
- MUST verify current node dependencies are satisfied.
- MUST enforce forward-only DAG/step flow for current run.
- MUST prevent hidden scope expansion.
- MUST verify handoff conditions.
- MUST verify parallel branches are independent.
- MUST preserve route bounds from L0.
- MUST emit bounded step contract only.

Allowed decisions:
- CONTINUE
- HOLD_NODE
- RETRY
- REROUTE
- ESCALATE_HITL
- RETURN_BEST_PARTIAL
- FAIL_WORKFLOW

Regression signals:
- unexpected_trajectory_class
- handoff_failure_rate
- branch_explosion_count
- scope_expansion_attempt_count
- dependency_violation_count

Stop condition:
- L3 MUST NOT re-decide L0 route or persist durable truth.

========================================================================================================================
G19 LOOP / RETRY / THRASH GATE
========================================================================================================================

Purpose:
- Stop unproductive agent loops.

Required checks:
- MUST track attempt_count.
- MUST track repeated same error.
- MUST track retry_count per step and per workflow.
- MUST detect oscillation.
- MUST detect repeated retrieval/tool/model calls with no new signal.
- MUST enforce max_iterations and max_retry thresholds.

Allowed decisions:
- RETRY
- HEAL
- STOP
- REROUTE
- ESCALATE_HITL
- RETURN_BEST_PARTIAL

Regression signals:
- retry_thrash_rate
- repeated_error_code_rate
- max_iteration_hit_rate
- no_new_signal_loop_count
- oscillation_detected_count

Stop condition:
- Repeated unproductive retries MUST terminate or escalate.

========================================================================================================================
G20 COST / LATENCY / BUDGET GATE
========================================================================================================================

Purpose:
- Prevent runaway runtime cost, latency, and resource consumption.

Required checks:
- MUST enforce SLO.
- MUST enforce max tokens.
- MUST enforce max tool calls.
- MUST enforce max model calls.
- MUST enforce max graph hops.
- MUST enforce max branch fan-out.
- MUST track provider latency and timeout.
- MUST emit budget_report.

Allowed decisions:
- CONTINUE
- DEGRADE_MODEL_TIER
- REDUCE_K
- STOP_ITERATION
- TIMEOUT
- RETURN_BEST_PARTIAL
- REROUTE_PROVIDER

Regression signals:
- p95_latency_spike
- p99_latency_spike
- cost_per_task_spike
- tokens_per_task_spike
- tool_calls_per_task_spike
- cache_hit_collapse

Stop condition:
- Exhausted budget MUST prevent additional autonomous steps.

========================================================================================================================
G21 OUTPUT SCHEMA GATE
========================================================================================================================

Purpose:
- Ensure generated output conforms to required schema and format.

Required checks:
- MUST validate structured output schema.
- MUST validate required fields.
- MUST validate type constraints.
- MUST validate citation anchors where required.
- MUST attempt bounded repair only if allowed.
- MUST fail closed if schema is required and cannot be repaired.

Allowed decisions:
- ALLOW
- REPAIR
- REJECT
- REROUTE
- SAFE_FALLBACK

Regression signals:
- schema_failure_rate
- schema_repair_rate
- invalid_json_rate
- missing_required_field_rate
- citation_anchor_missing_rate

Stop condition:
- Required schema failure MUST block exit unless safe fallback is permitted.

========================================================================================================================
G22 OUTPUT QUALITY GATE
========================================================================================================================

Purpose:
- Decide whether answer quality is acceptable before response leaves.

Required checks:
- MUST check answer completeness.
- MUST check task fit.
- MUST check groundedness and faithfulness.
- MUST check citation support.
- MUST check uncertainty/caveat correctness.
- MUST check hallucination/overclaim risk.
- MUST check user format requirements.

Allowed decisions:
- ALLOW
- REVISE
- ABSTAIN
- REROUTE
- ESCALATE_HITL
- SAFE_FALLBACK

Regression signals:
- task_completion_drop
- groundedness_drop
- citation_precision_drop
- user_correction_rate
- output_repair_rate
- hallucination_flag_rate

Stop condition:
- Unsupported high-confidence claims MUST NOT exit.

========================================================================================================================
G23 SECURITY / LEAKAGE GATE
========================================================================================================================

Purpose:
- Detect adversarial behavior and sensitive-data leakage across ingress, context, tools, and output.

Required checks:
- MUST detect prompt injection.
- MUST detect indirect prompt injection.
- MUST detect jailbreaks.
- MUST detect system/developer prompt leakage attempts.
- MUST detect secrets, credentials, tokens, and PII.
- MUST detect data exfiltration attempts.
- MUST detect safety-check bypass attempts.

Allowed decisions:
- DENY
- QUARANTINE
- REDACT
- SAFE_COMPLETE
- ESCALATE_HITL
- DISABLE_TOOL_OR_CONNECTOR

Regression signals:
- injection_detect_rate
- injection_false_negative_rate
- leakage_near_miss_count
- credential_access_attempt_count
- safety_bypass_attempt_count

Stop condition:
- Secret/system prompt leakage risk MUST block output or egress.

========================================================================================================================
G24 DETERMINISM / REPLAY GATE
========================================================================================================================

Purpose:
- Certify the run is replayable enough for audit and trust.

Required checks:
- MUST bind replay_key.
- MUST bind policy_hash.
- MUST bind blueprint_hash.
- MUST bind snapshot identifiers.
- MUST prevent wall-clock dependence inside guarded run.
- MUST prevent raw entropy and uuid4 where unstable.
- MUST prevent mixed-state reads.
- MUST prevent silent provider fallback.
- MUST seal final determinism digest.

Allowed decisions:
- CERTIFY
- MARK_DEGRADED
- BLOCK_COMMIT
- RERUN_UNDER_FREEZE
- ESCALATE
- NON_REPLAYABLE

Regression signals:
- replay_digest_mismatch
- policy_hash_mismatch
- snapshot_mismatch
- non_deterministic_route_count
- missing_replay_key_count

Stop condition:
- Durable commit MUST be blocked if replay certification is required and invalid.

========================================================================================================================
G25 RUNTIME REGRESSION / ANOMALY GATE
========================================================================================================================

Purpose:
- Protect current run when live behavior deviates materially from expected task-class baseline.

Important distinction:
- CI/CD regression protection decides whether candidate version ships.
- Runtime regression protection decides whether this live run should continue, downgrade, reroute, pause, or escalate.

Required checks:
- MUST compare current run behavior to expected route/task class baseline where available.
- MUST detect abnormal tool count.
- MUST detect abnormal token/cost/latency.
- MUST detect abnormal retrieval weakness.
- MUST detect abnormal retry/thrash.
- MUST detect abnormal route class.
- MUST detect judge/scorer disagreement where live judge is allowed.
- MUST detect unusual shell/network/file action.
- MUST detect provider schema drift.

Allowed decisions:
- CONTINUE
- MARK_DEGRADED
- DOWNGRADE_AUTONOMY
- SHRINK_SCOPE
- REROUTE
- FORCE_HITL
- RETURN_BEST_PARTIAL
- ABSTAIN
- OPEN_INCIDENT

Regression signals:
- route_distribution_shift
- cost_latency_anomaly
- tool_count_anomaly
- retry_anomaly
- support_score_anomaly
- safety_confidence_anomaly
- schema_drift_anomaly
- HITL_modify_spike
- user_correction_spike

Stop condition:
- Severe anomaly in high-risk action MUST pause or escalate before action/egress/write.

========================================================================================================================
G26 EXIT DISPOSITION GATE
========================================================================================================================

Purpose:
- Make final live decision for sealed runtime artifacts or RET short-circuits.

Required checks:
- MUST receive sealed L2/L3 artifacts or RET short-circuit.
- MUST validate policy, schema, support, safety, sandbox, mutation authorization.
- MUST produce explicit disposition.
- MUST not silently allow unknown state.
- MUST route commit requests to UWG only.
- MUST support deny/reroute/escalate/allow/commit request.

Allowed decisions:
- ALLOW
- DENY
- REROUTE
- ESCALATE_HITL
- COMMIT_REQUEST
- SAFE_FALLBACK
- ABSTAIN

Regression signals:
- exit_denial_rate
- reroute_rate
- escalate_rate
- output_repair_rate
- commit_request_rejection_rate

Stop condition:
- No sealed result may leave runtime without explicit exit disposition.

========================================================================================================================
G27 DURABLE WRITE SOVEREIGNTY GATE
========================================================================================================================

Purpose:
- Ensure all real mutations go through Universal Write Gateway only.

Required checks:
- MUST distinguish answer-only vs proposed mutation.
- MUST verify signature, compliance_hash, policy_hash.
- MUST verify capability token authorizes write.
- MUST verify RBAC, blast radius, diff, rollback where applicable.
- MUST claim write lock.
- MUST append durable ledger/hash-chain audit record.
- MUST refresh read surfaces after commit.

Allowed decisions:
- NO_WRITE
- COMMIT
- REJECT_WRITE
- REQUIRE_HITL
- LOCK_SUBSTRATE
- ROLLBACK_IF_SUPPORTED

Regression signals:
- ghost_write_attempt_count
- write_rejection_rate
- rollback_rate
- write_lock_conflict_rate
- out_of_scope_diff_count

Stop condition:
- No direct L2, L3, HITL, or L6 durable write is allowed.

========================================================================================================================
G28 AUDIT / TRACE COMPLETENESS GATE
========================================================================================================================

Purpose:
- Ensure runtime decisions are traceable and reviewable.

Required checks:
- MUST capture trace_root.
- MUST capture route contract and reason codes.
- MUST capture tool/model invocations.
- MUST capture evidence contracts.
- MUST capture step outputs and errors.
- MUST capture exit disposition.
- MUST capture HITL decisions.
- MUST capture commit receipts when write occurs.
- MUST seal replay/audit bundle where required.

Allowed decisions:
- ALLOW
- MARK_DEGRADED
- BLOCK_EXIT
- BLOCK_COMMIT
- ESCALATE
- NON_REPLAYABLE

Regression signals:
- missing_span_rate
- trace_join_failure_rate
- evidence_bundle_missing_rate
- invocation_record_missing_rate
- audit_hash_mismatch

Stop condition:
- If audit-grade trace is required and missing, commit MUST be blocked and exit may be blocked based on policy.

========================================================================================================================
G29 LEARNING FIREWALL GATE
========================================================================================================================

Purpose:
- Prevent L6 learning, shadow evaluation, or meta-learning from mutating current run.

Required checks:
- MUST classify L6 outputs as future-run signals only.
- MUST prevent current-run rescue via learning loop.
- MUST route proposed updates through gauntlet and UWG.
- MUST block direct L6 writes to L4.
- MUST preserve separation between runtime evidence and promoted policy/rubric/config changes.

Allowed decisions:
- ARCHIVE
- PROPOSE_UPDATE
- HOLD_FOR_REVIEW
- REJECT_PROMOTION
- UWG_COMMIT_AFTER_APPROVAL
- BLOCK_LIVE_MUTATION

Regression signals:
- live_learning_mutation_attempt_count
- unapproved_promotion_attempt_count
- shadow_eval_to_runtime_bleed_count
- rubric_drift_without_receipt_count

Stop condition:
- Learning signals MUST NOT mutate or rescue completed current run.

========================================================================================================================
RUNTIME REGRESSION PROTECTION REQUIREMENTS
========================================================================================================================

Runtime regression protection MUST be implemented as live anomaly containment.

It MUST NOT replace CI/CD regression suites.
It MUST NOT promote new rules.
It MUST NOT silently change model/prompt/policy behavior in the current run.
It MAY downgrade, pause, reroute, shrink scope, escalate, or abstain.

┌─────────────────────────────┬──────────────────────────────────────┬──────────────────────────────────────┐
│ LIVE REGRESSION SIGNAL       │ EXAMPLE                              │ ALLOWED CURRENT-RUN RESPONSE          │
├─────────────────────────────┼──────────────────────────────────────┼──────────────────────────────────────┤
│ route anomaly                │ simple read routes to costly workflow│ reroute / mark degraded               │
│ retrieval anomaly            │ support score below baseline         │ refine once / caveat / abstain        │
│ cost anomaly                 │ tokens 3x task-class baseline        │ stop / reduce K / lower autonomy      │
│ latency anomaly              │ SLO breach                           │ timeout / return best partial         │
│ tool anomaly                 │ unusual shell/network/file tool      │ shrink scope / HITL / deny            │
│ retry anomaly                │ repeated same error                  │ stop retry / heal / escalate          │
│ output anomaly               │ repeated schema repair               │ block exit / reroute                  │
│ policy anomaly               │ policy hash mismatch                 │ deny / freeze / reroute               │
│ safety anomaly               │ low classifier confidence            │ safe fallback / HITL                  │
│ privacy anomaly              │ cross-context near miss              │ redact / block / isolate              │
│ replay anomaly               │ digest mismatch                      │ non-replayable / block commit         │
│ judge anomaly                │ judge disagreement spike             │ HITL / mark degraded                  │
└─────────────────────────────┴──────────────────────────────────────┴──────────────────────────────────────┘

========================================================================================================================
CI/CD VS RUNTIME REGRESSION PLACEMENT
========================================================================================================================

┌──────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┐
│ CI/CD REGRESSION PROTECTION                          │ RUNTIME REGRESSION PROTECTION                                │
├──────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ Happens before or around release                     │ Happens inside a live request/run                            │
│ Tests candidate version                              │ Tests current behavior against expected task-class baseline  │
│ Uses offline evals, replay suites, golden sets       │ Uses telemetry, trace, live scores, thresholds               │
│ Decides shadow/canary/rollout/rollback               │ Decides continue/downgrade/reroute/escalate/abstain          │
│ Promotes future version                              │ Protects current run                                         │
│ Can update prompts/policies after approval           │ Cannot mutate current run policy                             │
│ Owned by release/eval pipeline                       │ Owned by runtime control plane                               │
└──────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘

Rule:
CI/CD regression gates protect the next release.
Runtime regression gates protect the current run.
Trace/replay evidence makes both provable.

========================================================================================================================
IMPLEMENTATION ACCEPTANCE CRITERIA
========================================================================================================================

A Windsurf implementation is acceptable only if:

[1] Every live request receives:
    - request_id
    - session_id
    - trace_root
    - caller_scope_baseline
    - policy_hash
    - route contract or rejection reason

[2] Every L0 route emits:
    - route_id
    - confidence
    - reason_codes
    - freshness_class
    - cache_policy
    - execution_form
    - cost_tier
    - fallback_chain
    - slo
    - telemetry_keys
    - tenant_scope
    - hmac_sig

[3] Every C0 retrieval emits:
    - RetrievalPlan
    - CandidateEvidencePool
    - ShapedEvidenceSet
    - EvidenceContract
    - support_score
    - cited_spans
    - source_ids
    - contradiction_flags
    - unresolved_gaps
    - lineage_manifest

[4] Every Prompt Assembly emits:
    - CompiledPromptArtifact
    - slot manifest
    - authority order proof
    - prompt_budget_report
    - HMAC
    - manifest_hash
    - replay metadata

[5] Every L2 step emits:
    - input step contract
    - capability_token
    - sandbox envelope
    - tool/model invocation records
    - stdout/stderr/return codes where applicable
    - output artifact
    - status
    - error_code if failed
    - attempt_count
    - replay receipts

[6] Every L3 managed workflow emits:
    - DAG/step graph
    - readiness state
    - dependency status
    - retry/loop counters
    - fallback_depth
    - branch merge records
    - workflow completion package

[7] Every Exit decision emits:
    - disposition
    - reason_codes
    - policy result
    - safety result
    - schema result
    - groundedness/support result
    - mutation authorization result
    - commit request if needed

[8] Every UWG write emits:
    - write authorization proof
    - RBAC/scope result
    - before/after diff
    - write lock record
    - ledger/hash-chain append
    - commit receipt
    - cache/read-surface refresh receipt

[9] Every runtime anomaly gate emits:
    - task_class
    - expected baseline
    - observed value
    - deviation
    - severity
    - live disposition
    - whether incident/RCA was opened

[10] L6 learning emits:
    - evidence bundle
    - RCA packet if applicable
    - proposed update only
    - no current-run mutation proof
    - UWG receipt only if future-run update was approved

========================================================================================================================
STOP CONDITIONS
========================================================================================================================

The system MUST stop, deny, reroute, or escalate when any of the following occurs:

- Missing request envelope
- Missing identity/tenant boundary
- Missing or mismatched policy_hash
- Ambiguous target for mutating action
- Tool/model not on approved roster
- Tool args too broad or unsafe
- External egress not approved
- Sandbox scope missing
- Evidence required but unavailable/blocked
- Prompt assembly authority order violation
- Prompt injection or tool-output injection not safely neutralized
- Cross-context data bleed risk
- Secret/system/developer prompt leakage risk
- Loop/thrash threshold exceeded
- Budget/SLO exhausted
- Required schema cannot be repaired
- Output unsupported by cited evidence
- Replay certification failure for commit-required run
- Audit bundle missing for audit-required action
- Any durable write path bypasses UWG
- L6 learning attempts to mutate current run

========================================================================================================================
NON-GOALS / EXCLUSIONS
========================================================================================================================

This runtime gate spec MUST NOT implement:

- shadow-to-canary promotion logic
- offline regression suite execution
- judge calibration promotion
- rollout percentage control
- automatic prompt/policy updates inside current run
- model retraining
- durable memory mutation outside UWG
- hidden fallback provider substitution
- unbounded agent loops
- direct human edits to durable state
- silent repair without audit trail

========================================================================================================================
COMPACT SUMMARY
========================================================================================================================

┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Runtime gates protect the current run.                                                           │
│ Promotion gates protect the next release.                                                         │
│ Regression exists in both places, but with different authority.                                   │
│ Runtime regression = live anomaly containment.                                                    │
│ CI/CD regression = release qualification.                                                         │
│ Audit/replay makes both provable.                                                                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
========================================================================================================================