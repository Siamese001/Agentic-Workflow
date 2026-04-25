"""Runtime OpenTelemetry semantic-convention constants — SSOT.

This module is the single source of truth for span names, attribute keys,
runtime ADG node types, and runtime ADG edge types defined in:

    docs/reference/OTEL/Runtime ADG and OTEL Spans.md

The doctrine document defines 13 stages (trace_root, U0 intake, L1 reasoning,
L0 routing, direct path, L3 orchestration, C0 retrieval, prompt assembly,
L2 execution, Exit eval, Response, UWG/L4 commit, L6 eval, Meta-learning).
Every span name, attribute key, ADG node type, and ADG edge type from that
document MUST appear here as a typed `Final[str]` constant. CI gate
``check_runtime_adg_coverage`` validates the linkage.

Companion modules
-----------------
- ``rag.py``                       — C0 retrieval-stage GenAI semconv (ADR-062).
- ``system_learning.runtime_adg.span_contracts`` — Tier 2 multi-signal contract
  validator that consumes these constants.
- ``system_learning.runtime_adg.runtime_span_emitter`` — fail-open emit helpers
  that produce spans consistent with these constants.

Naming conventions
------------------
- Span names follow the doctrine document verbatim (e.g. ``L0.route.select``,
  ``UWG.commit.append_ledger``, ``MetaLearning.promotion.commit``).
- Attribute keys are bare strings (``trace_id``, ``input_envelope_hash``).
  Stages prefix attributes only when collision risk exists across stages.
- Runtime ADG node types are TitleCase (``RuntimeRun``, ``L4Commit``).
- Runtime ADG edge types use ``snake_case`` verbs (``validates``, ``commits_to``).

This module is import-safe and has no runtime side effects.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Layer constants — match `agentic_core` package layer prefixes.
# ---------------------------------------------------------------------------

LAYER_U0: Final[str] = "U0_intake"
LAYER_L0: Final[str] = "L0_routing"
LAYER_L1: Final[str] = "L1_cognition"
LAYER_L2: Final[str] = "L2_execution"
LAYER_L3: Final[str] = "L3_orchestration"
LAYER_L4: Final[str] = "L4_state"
LAYER_L5: Final[str] = "L5_safety"
LAYER_L6: Final[str] = "L6_observability"
LAYER_L7: Final[str] = "L7_meta_learning"

ALL_LAYERS: Final[frozenset[str]] = frozenset(
    {
        LAYER_U0,
        LAYER_L0,
        LAYER_L1,
        LAYER_L2,
        LAYER_L3,
        LAYER_L4,
        LAYER_L5,
        LAYER_L6,
        LAYER_L7,
    }
)


# ===========================================================================
# Stage 1 — TRACE ROOT / RUNTIME RUN
# Doctrine §"TRACE ROOT / RUNTIME RUN" (lines 19–38)
# ===========================================================================

SPAN_TRACE_ROOT: Final[str] = "runtime.trace_root"

# Attributes (every trace root)
ATTR_TRACE_ID: Final[str] = "trace_id"
ATTR_SPAN_ID: Final[str] = "span_id"
ATTR_PARENT_SPAN_ID: Final[str] = "parent_span_id"
ATTR_RUN_ID: Final[str] = "run_id"
ATTR_REQUEST_ID: Final[str] = "request_id"
ATTR_SESSION_ID: Final[str] = "session_id"
ATTR_TENANT_ID: Final[str] = "tenant_id"
ATTR_CALLER_SCOPE: Final[str] = "caller_scope"
ATTR_INPUT_ENVELOPE_HASH: Final[str] = "input_envelope_hash"
ATTR_RUNTIME_VERSION: Final[str] = "runtime_version"
ATTR_SERVICE_NAME: Final[str] = "service.name"
ATTR_DEPLOYMENT_ENV: Final[str] = "deployment.environment"

# Runtime ADG node types
NODE_RUNTIME_RUN: Final[str] = "RuntimeRun"
NODE_USER_REQUEST: Final[str] = "UserRequest"

# Runtime ADG edge types
EDGE_STARTED: Final[str] = "started"
EDGE_CONTAINS: Final[str] = "contains"


# ===========================================================================
# Stage 2 — INTAKE / U0
# Doctrine §"INTAKE / U0" (lines 41–65)
# ===========================================================================

SPAN_INTAKE_VALIDATE: Final[str] = "U0.intake.validate"
SPAN_INTAKE_NORMALIZE: Final[str] = "U0.intake.normalize"
SPAN_INTAKE_STAMP_TRACE: Final[str] = "U0.intake.stamp_trace"

# Attributes
ATTR_SCHEMA_STATUS: Final[str] = "schema_status"
ATTR_AUTH_STATUS: Final[str] = "auth_status"
ATTR_QUOTA_STATUS: Final[str] = "quota_status"
ATTR_NORMALIZED_PAYLOAD_HASH: Final[str] = "normalized_payload_hash"
ATTR_REJECTION_REASON: Final[str] = "rejection_reason"
ATTR_CALLER_SCOPE_BASELINE: Final[str] = "caller_scope_baseline"
ATTR_ORIGIN_TRUST: Final[str] = "origin_trust"
ATTR_INGRESS_CHANNEL: Final[str] = "ingress_channel"
ATTR_ENVELOPE_VERSION: Final[str] = "envelope_version"

# Runtime ADG node types
NODE_INTAKE_ENVELOPE: Final[str] = "IntakeEnvelope"
NODE_VALIDATED_REQUEST: Final[str] = "ValidatedRequest"

# Runtime ADG edge types
EDGE_VALIDATES: Final[str] = "validates"
EDGE_EMITS: Final[str] = "emits"


# ===========================================================================
# Stage 3 — L1 REASONING / PLAN GENERATION
# Doctrine §"L1 REASONING / PLAN GENERATION" (lines 68–94)
# ===========================================================================

SPAN_L1_INTENT_PARSE: Final[str] = "L1.intent.parse"
SPAN_L1_CONTEXT_PRIORS_LOAD: Final[str] = "L1.context.priors_load"
SPAN_L1_PLAN_DRAFT: Final[str] = "L1.plan.draft"
SPAN_L1_PLAN_VALIDATE: Final[str] = "L1.plan.validate"

# Attributes
ATTR_INTENT_FRAME_HASH: Final[str] = "intent_frame_hash"
ATTR_TASK_CLASS: Final[str] = "task_class"
ATTR_TASK_SPEC_HASH: Final[str] = "task_spec_hash"
ATTR_SUCCESS_CONDITION: Final[str] = "success_condition"
ATTR_ASSUMPTIONS: Final[str] = "assumptions"
ATTR_UNRESOLVED_GAPS: Final[str] = "unresolved_gaps"
ATTR_PROPOSED_ROUTE: Final[str] = "proposed_route"
ATTR_ROUTE_RISK: Final[str] = "route_risk"
ATTR_CONFIDENCE: Final[str] = "confidence"
ATTR_PLAN_CONTRACT_HASH: Final[str] = "plan_contract_hash"
ATTR_GROUNDING_REQUIRED: Final[str] = "grounding_required"
ATTR_OUTPUT_CONTRACT_HASH: Final[str] = "output_contract_hash"

# Runtime ADG node types
NODE_L1_INTENT_FRAME: Final[str] = "L1IntentFrame"
NODE_L1_PLAN_CONTRACT: Final[str] = "L1PlanContract"

# Runtime ADG edge types
EDGE_INTERPRETS: Final[str] = "interprets"
EDGE_PROPOSES_ROUTE: Final[str] = "proposes_route"


# ===========================================================================
# Stage 4 — L0 ROUTE DECISION
# Doctrine §"L0 ROUTE DECISION" (lines 97–124)
# ===========================================================================

SPAN_L0_ROUTE_SCORE: Final[str] = "L0.route.score"
SPAN_L0_CACHE_CHECK: Final[str] = "L0.cache.check"
SPAN_L0_ROUTE_SELECT: Final[str] = "L0.route.select"
SPAN_L0_ROUTE_CONTRACT: Final[str] = "L0.route.contract"

# Attributes
ATTR_SELECTED_ROUTE: Final[str] = "selected_route"
ATTR_REASON_CODES: Final[str] = "reason_codes"
ATTR_RISK_TIER: Final[str] = "risk_tier"
ATTR_FRESHNESS_CLASS: Final[str] = "freshness_class"
ATTR_CACHE_DECISION: Final[str] = "cache_decision"
ATTR_CACHE_KEY_HASH: Final[str] = "cache_key_hash"
ATTR_SEMANTIC_SIMILARITY_SCORE: Final[str] = "semantic_similarity_score"
ATTR_SUPPORT_REQUIRED: Final[str] = "support_required"
ATTR_EXECUTION_FORM: Final[str] = "execution_form"
ATTR_ROUTE_CONTRACT_HASH: Final[str] = "route_contract_hash"
ATTR_ROUTE_BOUNDS: Final[str] = "route_bounds"
ATTR_POLICY_HASH: Final[str] = "policy_hash"

# Execution form enum-likes
EXECUTION_FORM_TERMINAL: Final[str] = "terminal"
EXECUTION_FORM_SINGLE_STEP: Final[str] = "single_step"
EXECUTION_FORM_MANAGED_WORKFLOW: Final[str] = "managed_workflow"

VALID_EXECUTION_FORMS: Final[frozenset[str]] = frozenset(
    {EXECUTION_FORM_TERMINAL, EXECUTION_FORM_SINGLE_STEP, EXECUTION_FORM_MANAGED_WORKFLOW}
)

# Runtime ADG node types
NODE_ROUTE_CONTRACT: Final[str] = "RouteContract"
NODE_ROUTE_FAMILY: Final[str] = "RouteFamily"

# Runtime ADG edge types
EDGE_READS: Final[str] = "reads"
EDGE_SELECTS: Final[str] = "selects"


# ===========================================================================
# Stage 5 — DIRECT / SINGLE-STEP PATH
# Doctrine §"DIRECT / SINGLE-STEP PATH" (lines 129–158)
# ===========================================================================

SPAN_L0_DIRECT_PACKAGE: Final[str] = "L0.direct.package"
SPAN_L0_RET_SHORT_CIRCUIT: Final[str] = "L0.ret.short_circuit"
SPAN_L0_SINGLE_STEP_DISPATCH: Final[str] = "L0.single_step.dispatch"

# Attributes
ATTR_DIRECT_STEP_ID: Final[str] = "direct_step_id"
ATTR_NO_L3_REQUIRED: Final[str] = "no_l3_required"
ATTR_PACKET_HASH: Final[str] = "packet_hash"
ATTR_TERMINAL_RETURN_REASON: Final[str] = "terminal_return_reason"

# Runtime ADG node types
NODE_DIRECT_STEP_PACKET: Final[str] = "DirectStepPacket"
NODE_TERMINAL_RETURN: Final[str] = "TerminalReturn"

# Runtime ADG edge types
EDGE_BYPASSES: Final[str] = "bypasses"
EDGE_DISPATCHES_TO: Final[str] = "dispatches_to"


# ===========================================================================
# Stage 6 — L3 ORCHESTRATION PATH
# Doctrine §"L3 ORCHESTRATION PATH" (lines 130–158, right column)
# ===========================================================================

SPAN_L3_WORKFLOW_EXPAND: Final[str] = "L3.workflow.expand"
SPAN_L3_WORKFLOW_STATE: Final[str] = "L3.workflow.state"
SPAN_L3_STEP_READY_CHECK: Final[str] = "L3.step.ready_check"
SPAN_L3_STEP_DISPATCH: Final[str] = "L3.step.dispatch"
SPAN_L3_STEP_MERGE_RESULT: Final[str] = "L3.step.merge_result"

# Attributes
ATTR_WORKFLOW_ID: Final[str] = "workflow_id"
ATTR_DAG_HASH: Final[str] = "dag_hash"
ATTR_NODE_IDS: Final[str] = "node_ids"
ATTR_DEPENDENCY_EDGES: Final[str] = "dependency_edges"
ATTR_BRANCH_RULES: Final[str] = "branch_rules"
ATTR_JOIN_RULES: Final[str] = "join_rules"
ATTR_CHECKPOINT_HASH: Final[str] = "checkpoint_hash"
ATTR_CURRENT_STEP_ID: Final[str] = "current_step_id"
ATTR_READY_NODE_IDS: Final[str] = "ready_node_ids"
ATTR_BLOCKED_NODE_IDS: Final[str] = "blocked_node_ids"
ATTR_WORKFLOW_STATE_HASH: Final[str] = "workflow_state_hash"

# Runtime ADG node types
NODE_WORKFLOW_GRAPH: Final[str] = "WorkflowGraph"
NODE_WORKFLOW_STEP: Final[str] = "WorkflowStep"
NODE_STEP_DEPENDENCY: Final[str] = "StepDependency"

# Runtime ADG edge types
EDGE_EXPANDS: Final[str] = "expands"
EDGE_DEPENDS_ON: Final[str] = "depends_on"


# ===========================================================================
# Stage 7 — C0 RETRIEVAL / CONTEXT ENGINE
# Doctrine §"C0 RETRIEVAL / CONTEXT ENGINE" (lines 163–199)
#
# C0 has its own dedicated semconv module (rag.py / ADR-062). This block
# defines only the high-level orchestration spans/nodes/edges that the
# doctrine document calls out, NOT the per-stage retrieval primitives
# already covered by rag.py (SPAN_QUERY, SPAN_EMBED, SPAN_RERANK, etc.).
# ===========================================================================

SPAN_C0_RETRIEVAL_PLAN: Final[str] = "C0.retrieval.plan"
SPAN_C0_QUERY_EMBED: Final[str] = "C0.query.embed"
SPAN_C0_EVIDENCE_FETCH_DENSE: Final[str] = "C0.evidence.fetch_dense"
SPAN_C0_EVIDENCE_FETCH_SPARSE: Final[str] = "C0.evidence.fetch_sparse"
SPAN_C0_GRAPH_TRAVERSE: Final[str] = "C0.graph.traverse"
SPAN_C0_EVIDENCE_RERANK: Final[str] = "C0.evidence.rerank"
SPAN_C0_EVIDENCE_CONTRACT: Final[str] = "C0.evidence.contract"

# Attributes (high-level — see rag.py for low-level GenAI semconv)
ATTR_QUERY_VEC_ID: Final[str] = "query_vec_id"
ATTR_QUERY_TEXT_HASH: Final[str] = "query_text_hash"
ATTR_SOURCE_SCOPE: Final[str] = "source_scope"
ATTR_ACL_SCOPE: Final[str] = "acl_scope"
ATTR_FRESHNESS_SCOPE: Final[str] = "freshness_scope"
ATTR_VECTOR_STORE_ID: Final[str] = "vector_store_id"
ATTR_INDEX_VERSION: Final[str] = "index_version"
ATTR_EMBEDDING_MODEL_ID: Final[str] = "embedding_model_id"
ATTR_RETRIEVAL_MODE: Final[str] = "retrieval_mode"
ATTR_TOP_K: Final[str] = "top_k"
ATTR_SIMILARITY_THRESHOLD: Final[str] = "similarity_threshold"
ATTR_BM25_ENABLED: Final[str] = "bm25_enabled"
ATTR_RERANKER_MODEL_ID: Final[str] = "reranker_model_id"
ATTR_SOURCE_IDS: Final[str] = "source_ids"
ATTR_CHUNK_IDS: Final[str] = "chunk_ids"
ATTR_ENTITY_IDS: Final[str] = "entity_ids"
ATTR_EDGE_IDS: Final[str] = "edge_ids"
ATTR_EVIDENCE_IDS: Final[str] = "evidence_ids"
ATTR_RERANK_SCORES: Final[str] = "rerank_scores"
ATTR_SUPPORT_SCORE: Final[str] = "support_score"
ATTR_COVERAGE_GAPS: Final[str] = "coverage_gaps"
ATTR_CONTRADICTION_FLAGS: Final[str] = "contradiction_flags"
ATTR_CONTEXTUAL_CHUNK_HEADER_HASH: Final[str] = "contextual_chunk_header_hash"
ATTR_PARENT_DOCUMENT_ID: Final[str] = "parent_document_id"
ATTR_CITATION_SPAN_IDS: Final[str] = "citation_span_ids"

# Retrieval mode enum-likes
RETRIEVAL_MODE_DENSE: Final[str] = "dense"
RETRIEVAL_MODE_SPARSE: Final[str] = "sparse"
RETRIEVAL_MODE_HYBRID: Final[str] = "hybrid"
RETRIEVAL_MODE_GRAPH: Final[str] = "graph"

VALID_RETRIEVAL_MODES: Final[frozenset[str]] = frozenset(
    {RETRIEVAL_MODE_DENSE, RETRIEVAL_MODE_SPARSE, RETRIEVAL_MODE_HYBRID, RETRIEVAL_MODE_GRAPH}
)

# Runtime ADG node types
NODE_RETRIEVAL_QUERY: Final[str] = "RetrievalQuery"
NODE_EVIDENCE_CHUNK: Final[str] = "EvidenceChunk"
NODE_ENTITY_SUBGRAPH: Final[str] = "EntitySubgraph"
NODE_EVIDENCE_CONTRACT: Final[str] = "EvidenceContract"

# Runtime ADG edge types
EDGE_SEARCHES: Final[str] = "searches"
EDGE_MATCHES: Final[str] = "matches"
EDGE_CONNECTS: Final[str] = "connects"


# ===========================================================================
# Stage 8 — PROMPT ASSEMBLY
# Doctrine §"PROMPT ASSEMBLY" (lines 202–229)
# ===========================================================================

SPAN_PA_STATIC_BLOCKS_LOAD: Final[str] = "PA.static_blocks.load"
SPAN_PA_CONTEXT_SLOT: Final[str] = "PA.context.slot"
SPAN_PA_TOKEN_BUDGET: Final[str] = "PA.token_budget"
SPAN_PA_PROMPT_CONTRACT: Final[str] = "PA.prompt.contract"

# Attributes
ATTR_PROMPT_ENVELOPE_HASH: Final[str] = "prompt_envelope_hash"
ATTR_SYSTEM_TEMPLATE_HASH: Final[str] = "system_template_hash"
ATTR_TASK_TEMPLATE_HASH: Final[str] = "task_template_hash"
ATTR_OUTPUT_SCHEMA_HASH: Final[str] = "output_schema_hash"
ATTR_MUST_USE_CONTEXT_IDS: Final[str] = "must_use_context_ids"
ATTR_TOKEN_BUDGET_TOTAL: Final[str] = "token_budget_total"
ATTR_TOKEN_BUDGET_USED: Final[str] = "token_budget_used"
ATTR_TRIM_STRATEGY: Final[str] = "trim_strategy"
ATTR_OVERFLOW_ACTION: Final[str] = "overflow_action"
ATTR_HMAC: Final[str] = "hmac"
ATTR_REPLAY_METADATA: Final[str] = "replay_metadata"
ATTR_PROMPT_HASH: Final[str] = "prompt_hash"
ATTR_PROMPT_VERSION: Final[str] = "prompt_version"

# Runtime ADG node types
NODE_PROMPT_ENVELOPE: Final[str] = "PromptEnvelope"
NODE_BOUNDED_PROMPT_PACKET: Final[str] = "BoundedPromptPacket"

# Runtime ADG edge types
EDGE_PACKAGES: Final[str] = "packages"


# ===========================================================================
# Stage 9 — L2 EXECUTION
# Doctrine §"L2 EXECUTION" (lines 233–282)
# ===========================================================================

SPAN_L2_STEP_PREPARE: Final[str] = "L2.step.prepare"
SPAN_L2_STEP_VALIDATE: Final[str] = "L2.step.validate"
SPAN_L2_MODEL_INVOKE: Final[str] = "L2.model.invoke"
SPAN_L2_TOOL_INVOKE: Final[str] = "L2.tool.invoke"
SPAN_L2_HEAL_ATTEMPT: Final[str] = "L2.heal.attempt"
SPAN_L2_STEP_SEAL: Final[str] = "L2.step.seal"

# Attributes — prepare
ATTR_STEP_ID: Final[str] = "step_id"
ATTR_PARENT_STEP_ID: Final[str] = "parent_step_id"
ATTR_BLUEPRINT_HASH: Final[str] = "blueprint_hash"
ATTR_IDEMPOTENCY_KEY: Final[str] = "idempotency_key"
ATTR_REPLAY_KEY: Final[str] = "replay_key"
ATTR_CAPABILITY_TOKEN_HASH: Final[str] = "capability_token_hash"
ATTR_SANDBOX_SCOPE: Final[str] = "sandbox_scope"
ATTR_FS_SCOPE: Final[str] = "fs_scope"
ATTR_NET_SCOPE: Final[str] = "net_scope"
ATTR_TOOL_ALLOWLIST: Final[str] = "tool_allowlist"
ATTR_MODEL_ALLOWLIST: Final[str] = "model_allowlist"

# Attributes — validate
ATTR_VALIDATION_PACKET_ID: Final[str] = "validation_packet_id"
ATTR_INPUT_SCHEMA_STATUS: Final[str] = "input_schema_status"
ATTR_SIDE_EFFECT_CLASS: Final[str] = "side_effect_class"
ATTR_SANDBOX_STATUS: Final[str] = "sandbox_status"
ATTR_BUDGET_SCOPE: Final[str] = "budget_scope"
ATTR_MUTATION_INTENT_DETECTED: Final[str] = "mutation_intent_detected"
ATTR_WRITE_AUTH: Final[str] = "write_auth"

# Attributes — model invoke
ATTR_MODEL_ID: Final[str] = "model_id"
ATTR_PROVIDER: Final[str] = "provider"
ATTR_DECODING_CONFIG_HASH: Final[str] = "decoding_config_hash"
ATTR_PROMPT_TOKENS: Final[str] = "prompt_tokens"
ATTR_OUTPUT_TOKENS: Final[str] = "output_tokens"
ATTR_LATENCY_MS: Final[str] = "latency_ms"
ATTR_STOP_REASON: Final[str] = "stop_reason"
ATTR_RESPONSE_ID: Final[str] = "response_id"
ATTR_MODEL_OUTPUT_HASH: Final[str] = "model_output_hash"

# Attributes — tool invoke
ATTR_TOOL_NAME: Final[str] = "tool_name"
ATTR_TOOL_VERSION: Final[str] = "tool_version"
ATTR_ARGS_HASH: Final[str] = "args_hash"
ATTR_RETURN_CODE: Final[str] = "return_code"
ATTR_STDOUT_HASH: Final[str] = "stdout_hash"
ATTR_STDERR_HASH: Final[str] = "stderr_hash"
ATTR_TIMEOUT_STATUS: Final[str] = "timeout_status"
ATTR_CIRCUIT_BREAKER_STATUS: Final[str] = "circuit_breaker_status"

# Attributes — heal attempt
ATTR_ERROR_CODE: Final[str] = "error_code"
ATTR_REASON_CODE: Final[str] = "reason_code"
ATTR_RETRY_COUNT: Final[str] = "retry_count"
ATTR_REPAIR_COUNT: Final[str] = "repair_count"
ATTR_HEALING_TIER: Final[str] = "healing_tier"
ATTR_PARENT_ATTEMPT_ID: Final[str] = "parent_attempt_id"
ATTR_OSCILLATION_GUARD_STATUS: Final[str] = "oscillation_guard_status"
ATTR_TERMINAL_REPAIR_STATUS: Final[str] = "terminal_repair_status"

# Attributes — seal
ATTR_TERMINAL_CLASS: Final[str] = "terminal_class"
ATTR_OUTPUT_ARTIFACT_IDS: Final[str] = "output_artifact_ids"
ATTR_LINEAGE_HASH: Final[str] = "lineage_hash"
ATTR_OUTPUT_HASH: Final[str] = "output_hash"
ATTR_STATE_DIFF_HASH: Final[str] = "state_diff_hash"
ATTR_PROPOSED_MUTATION_HASH: Final[str] = "proposed_mutation_hash"
ATTR_ATTEMPT_COUNT: Final[str] = "attempt_count"
ATTR_VALIDATION_COUNTERS: Final[str] = "validation_counters"

# Runtime ADG node types
NODE_EXECUTION_STEP: Final[str] = "ExecutionStep"
NODE_VALIDATION_PACKET: Final[str] = "ValidationPacket"
NODE_MODEL_INVOCATION: Final[str] = "ModelInvocation"
NODE_TOOL_INVOCATION: Final[str] = "ToolInvocation"
NODE_HEALING_ATTEMPT: Final[str] = "HealingAttempt"
NODE_SEALED_L2_ARTIFACT: Final[str] = "SealedL2Artifact"

# Runtime ADG edge types
EDGE_RECEIVES: Final[str] = "receives"
EDGE_BINDS: Final[str] = "binds"
EDGE_BLOCKS: Final[str] = "blocks"
EDGE_ALLOWS: Final[str] = "allows"
EDGE_CONSUMES: Final[str] = "consumes"
EDGE_INVOKES: Final[str] = "invokes"
EDGE_REPAIRS: Final[str] = "repairs"
EDGE_RETRIES: Final[str] = "retries"
EDGE_SEALS: Final[str] = "seals"


# ===========================================================================
# Stage 10 — EXIT EVAL / CURRENT-RUN CONTROL
# Doctrine §"EXIT EVAL / CURRENT-RUN CONTROL" (lines 286–315)
# ===========================================================================

SPAN_EXIT_EVAL_POLICY: Final[str] = "Exit.eval.policy"
SPAN_EXIT_EVAL_QUALITY: Final[str] = "Exit.eval.quality"
SPAN_EXIT_EVAL_SAFETY: Final[str] = "Exit.eval.safety"
SPAN_EXIT_EVAL_MUTATION_AUTH: Final[str] = "Exit.eval.mutation_auth"
SPAN_EXIT_DISPOSITION: Final[str] = "Exit.disposition"

# Attributes
ATTR_EXIT_DISPOSITION: Final[str] = "exit_disposition"
ATTR_COMPLIANCE_HASH: Final[str] = "compliance_hash"
ATTR_GROUNDEDNESS_CHECK: Final[str] = "groundedness_check"
ATTR_CITATION_SUPPORT_CHECK: Final[str] = "citation_support_check"
ATTR_SCHEMA_CHECK: Final[str] = "schema_check"
ATTR_SAFETY_CHECK: Final[str] = "safety_check"
ATTR_MUTATION_AUTH_RESULT: Final[str] = "mutation_auth_result"
ATTR_HITL_REQUIRED: Final[str] = "hitl_required"
ATTR_HITL_PACKET_ID: Final[str] = "hitl_packet_id"
ATTR_HITL_DECISION: Final[str] = "hitl_decision"
ATTR_FINAL_OUTPUT_HASH: Final[str] = "final_output_hash"

# Disposition enum-likes
DISPOSITION_ALLOW: Final[str] = "allow"
DISPOSITION_DENY: Final[str] = "deny"
DISPOSITION_REROUTE: Final[str] = "reroute"
DISPOSITION_ESCALATE: Final[str] = "escalate"
DISPOSITION_COMMIT_REQUEST: Final[str] = "commit_request"

VALID_DISPOSITIONS: Final[frozenset[str]] = frozenset(
    {
        DISPOSITION_ALLOW,
        DISPOSITION_DENY,
        DISPOSITION_REROUTE,
        DISPOSITION_ESCALATE,
        DISPOSITION_COMMIT_REQUEST,
    }
)

# Runtime ADG node types
NODE_EXIT_DISPOSITION: Final[str] = "ExitDisposition"
NODE_RUNTIME_OUTCOME: Final[str] = "RuntimeOutcome"
NODE_HITL_PACKET: Final[str] = "HITLPacket"

# Runtime ADG edge types
EDGE_EVALUATES: Final[str] = "evaluates"
EDGE_DENIES: Final[str] = "denies"
EDGE_REROUTES: Final[str] = "reroutes"
EDGE_ESCALATES: Final[str] = "escalates"
EDGE_REQUESTS_COMMIT: Final[str] = "requests_commit"


# ===========================================================================
# Stage 11 — RESPONSE / NO WRITE
# Doctrine §"RESPONSE / NO WRITE" (lines 320–342)
# ===========================================================================

SPAN_RESPONSE_EMIT: Final[str] = "Response.emit"
SPAN_RUNTIME_CLOSE_NO_WRITE: Final[str] = "Runtime.close_no_write"

# Attributes
ATTR_NO_WRITE_MARKER: Final[str] = "no_write_marker"
ATTR_CALLER_DELIVERY_STATUS: Final[str] = "caller_delivery_status"
ATTR_RUNTIME_CLOSED: Final[str] = "runtime_closed"

# Runtime ADG node types
NODE_RUNTIME_RESPONSE: Final[str] = "RuntimeResponse"

# Runtime ADG edge types
EDGE_RETURNS_TO: Final[str] = "returns_to"
EDGE_CLOSES: Final[str] = "closes"


# ===========================================================================
# Stage 12 — UWG / L4 COMMIT
# Doctrine §"UWG / L4 COMMIT" (lines 321–348)
# ===========================================================================

SPAN_UWG_COMMIT_VERIFY_AUTHORITY: Final[str] = "UWG.commit.verify_authority"
SPAN_UWG_COMMIT_VALIDATE_DIFF: Final[str] = "UWG.commit.validate_diff"
SPAN_UWG_COMMIT_APPEND_LEDGER: Final[str] = "UWG.commit.append_ledger"
SPAN_L4_ARCHIVE_MATERIALIZE: Final[str] = "L4.archive.materialize"

# Attributes
ATTR_COMMIT_REQUEST_ID: Final[str] = "commit_request_id"
ATTR_MUTATION_TYPE: Final[str] = "mutation_type"
ATTR_PROPOSED_DIFF_HASH: Final[str] = "proposed_diff_hash"
ATTR_BEFORE_HASH: Final[str] = "before_hash"
ATTR_AFTER_HASH: Final[str] = "after_hash"
ATTR_LEDGER_HASH: Final[str] = "ledger_hash"
ATTR_ROLLBACK_REF: Final[str] = "rollback_ref"
ATTR_COMMIT_ID: Final[str] = "commit_id"
ATTR_ALIAS_SWAP_STATUS: Final[str] = "alias_swap_status"
ATTR_AUDIT_RECEIPT_ID: Final[str] = "audit_receipt_id"
ATTR_WRITE_LOCK_ID: Final[str] = "write_lock_id"
ATTR_SERIALIZED_QUEUE_POSITION: Final[str] = "serialized_queue_position"

# Runtime ADG node types
NODE_L4_COMMIT: Final[str] = "L4Commit"
NODE_LEDGER_APPEND: Final[str] = "LedgerAppend"

# Runtime ADG edge types
EDGE_COMMITS_TO: Final[str] = "commits_to"
EDGE_APPENDS: Final[str] = "appends"
EDGE_REFRESHES: Final[str] = "refreshes"


# ===========================================================================
# Stage 13 — L6 EVAL METRICS / SHADOW EVALUATION
# Doctrine §"L6 EVAL METRICS / SHADOW EVALUATION" (lines 353–385)
# ===========================================================================

SPAN_L6_TELEMETRY_INGEST: Final[str] = "L6.telemetry.ingest"
SPAN_L6_OUTCOME_EVALUATE: Final[str] = "L6.outcome.evaluate"
SPAN_L6_TRAJECTORY_EVALUATE: Final[str] = "L6.trajectory.evaluate"
SPAN_L6_RETRIEVAL_EVALUATE: Final[str] = "L6.retrieval.evaluate"
SPAN_L6_REPLAY_VERIFY: Final[str] = "L6.replay.verify"
SPAN_L6_METRICS_SEAL: Final[str] = "L6.metrics.seal"

# Attributes
ATTR_TASK_COMPLETION_SCORE: Final[str] = "task_completion_score"
ATTR_GROUNDEDNESS_SCORE: Final[str] = "groundedness_score"
ATTR_CITATION_SUPPORT_SCORE: Final[str] = "citation_support_score"
ATTR_ANSWER_RELEVANCE_SCORE: Final[str] = "answer_relevance_score"
ATTR_RETRIEVAL_PRECISION: Final[str] = "retrieval_precision"
ATTR_RETRIEVAL_RECALL_PROXY: Final[str] = "retrieval_recall_proxy"
ATTR_SUPPORT_RATE: Final[str] = "support_rate"
ATTR_CONTRADICTION_RATE: Final[str] = "contradiction_rate"
ATTR_TRAJECTORY_SCORE: Final[str] = "trajectory_score"
ATTR_TOOL_ORDER_SCORE: Final[str] = "tool_order_score"
ATTR_RETRY_THRASH: Final[str] = "retry_thrash"
ATTR_BUDGET_ADHERENCE_SCORE: Final[str] = "budget_adherence_score"
ATTR_TOKEN_COST: Final[str] = "token_cost"
ATTR_TOOL_COST: Final[str] = "tool_cost"
ATTR_DRIFT_FLAGS: Final[str] = "drift_flags"
ATTR_ANOMALY_FLAGS: Final[str] = "anomaly_flags"
ATTR_REPLAY_DIGEST: Final[str] = "replay_digest"
ATTR_DETERMINISM_STATUS: Final[str] = "determinism_status"
ATTR_EVAL_BUNDLE_ID: Final[str] = "eval_bundle_id"
ATTR_GRADER_ID: Final[str] = "grader_id"
ATTR_HUMAN_CALIBRATION_STATUS: Final[str] = "human_calibration_status"

# Runtime ADG node types
NODE_L6_EVIDENCE_BUNDLE: Final[str] = "L6EvidenceBundle"
NODE_EVAL_SIGNAL_BUNDLE: Final[str] = "EvalSignalBundle"
NODE_REPLAY_VERIFICATION: Final[str] = "ReplayVerification"

# Runtime ADG edge types
EDGE_OBSERVES: Final[str] = "observes"
EDGE_GRADES: Final[str] = "grades"
EDGE_VERIFIES: Final[str] = "verifies"


# ===========================================================================
# Stage 14 — META-LEARNING / FUTURE-RUN PROMOTION
# Doctrine §"META-LEARNING / FUTURE-RUN PROMOTION" (lines 389–423)
# ===========================================================================

SPAN_METALEARNING_SIGNAL_FUSE: Final[str] = "MetaLearning.signal.fuse"
SPAN_METALEARNING_RCA_CREATE: Final[str] = "MetaLearning.rca.create"
SPAN_METALEARNING_PATTERN_EXTRACT: Final[str] = "MetaLearning.pattern.extract"
SPAN_METALEARNING_RULE_DRAFT: Final[str] = "MetaLearning.rule.draft"
SPAN_METALEARNING_SHADOW_REPLAY: Final[str] = "MetaLearning.shadow_replay"
SPAN_METALEARNING_PROMOTION_PROPOSE: Final[str] = "MetaLearning.promotion.propose"
SPAN_METALEARNING_PROMOTION_APPROVE_OR_REJECT: Final[str] = "MetaLearning.promotion.approve_or_reject"
SPAN_METALEARNING_PROMOTION_COMMIT: Final[str] = "MetaLearning.promotion.commit"

# Attributes
ATTR_RCA_ID: Final[str] = "RCA_id"
ATTR_INCIDENT_CLUSTER_ID: Final[str] = "incident_cluster_id"
ATTR_PATTERN_ID: Final[str] = "pattern_id"
ATTR_SEVERITY: Final[str] = "severity"
ATTR_CONFIDENCE_BAND: Final[str] = "confidence_band"
ATTR_PROPOSED_RULE_UPDATE_HASH: Final[str] = "proposed_rule_update_hash"
ATTR_PROPOSED_PROMPT_UPDATE_HASH: Final[str] = "proposed_prompt_update_hash"
ATTR_PROPOSED_POLICY_UPDATE_HASH: Final[str] = "proposed_policy_update_hash"
ATTR_PROMOTION_CANDIDATE_ID: Final[str] = "promotion_candidate_id"
ATTR_SHADOW_REPLAY_RESULT: Final[str] = "shadow_replay_result"
ATTR_REGRESSION_RESULT: Final[str] = "regression_result"
ATTR_SME_SIGNOFF_STATUS: Final[str] = "SME_signoff_status"
ATTR_APPROVED_UPDATE_ID: Final[str] = "approved_update_id"
ATTR_FUTURE_RUN_ONLY: Final[str] = "future_run_only"
ATTR_ROLLBACK_PLAN_HASH: Final[str] = "rollback_plan_hash"

# Runtime ADG node types
NODE_INCIDENT_CLUSTER: Final[str] = "IncidentCluster"
NODE_RCA_RECORD: Final[str] = "RCARecord"
NODE_PROMOTION_CANDIDATE: Final[str] = "PromotionCandidate"
NODE_APPROVED_LEARNING_UPDATE: Final[str] = "ApprovedLearningUpdate"

# Runtime ADG edge types
EDGE_LEARNS_FROM: Final[str] = "learns_from"
EDGE_PROPOSES: Final[str] = "proposes"
EDGE_PROMOTES_VIA: Final[str] = "promotes_via"


# ---------------------------------------------------------------------------
# Aggregate registries — used by tests and the coverage CI gate.
# ---------------------------------------------------------------------------

ALL_SPAN_NAMES: Final[frozenset[str]] = frozenset(
    {
        # Stage 1 — trace root
        SPAN_TRACE_ROOT,
        # Stage 2 — U0 intake
        SPAN_INTAKE_VALIDATE,
        SPAN_INTAKE_NORMALIZE,
        SPAN_INTAKE_STAMP_TRACE,
        # Stage 3 — L1 reasoning
        SPAN_L1_INTENT_PARSE,
        SPAN_L1_CONTEXT_PRIORS_LOAD,
        SPAN_L1_PLAN_DRAFT,
        SPAN_L1_PLAN_VALIDATE,
        # Stage 4 — L0 route
        SPAN_L0_ROUTE_SCORE,
        SPAN_L0_CACHE_CHECK,
        SPAN_L0_ROUTE_SELECT,
        SPAN_L0_ROUTE_CONTRACT,
        # Stage 5 — direct path
        SPAN_L0_DIRECT_PACKAGE,
        SPAN_L0_RET_SHORT_CIRCUIT,
        SPAN_L0_SINGLE_STEP_DISPATCH,
        # Stage 6 — L3 orchestration
        SPAN_L3_WORKFLOW_EXPAND,
        SPAN_L3_WORKFLOW_STATE,
        SPAN_L3_STEP_READY_CHECK,
        SPAN_L3_STEP_DISPATCH,
        SPAN_L3_STEP_MERGE_RESULT,
        # Stage 7 — C0 retrieval
        SPAN_C0_RETRIEVAL_PLAN,
        SPAN_C0_QUERY_EMBED,
        SPAN_C0_EVIDENCE_FETCH_DENSE,
        SPAN_C0_EVIDENCE_FETCH_SPARSE,
        SPAN_C0_GRAPH_TRAVERSE,
        SPAN_C0_EVIDENCE_RERANK,
        SPAN_C0_EVIDENCE_CONTRACT,
        # Stage 8 — prompt assembly
        SPAN_PA_STATIC_BLOCKS_LOAD,
        SPAN_PA_CONTEXT_SLOT,
        SPAN_PA_TOKEN_BUDGET,
        SPAN_PA_PROMPT_CONTRACT,
        # Stage 9 — L2 execution
        SPAN_L2_STEP_PREPARE,
        SPAN_L2_STEP_VALIDATE,
        SPAN_L2_MODEL_INVOKE,
        SPAN_L2_TOOL_INVOKE,
        SPAN_L2_HEAL_ATTEMPT,
        SPAN_L2_STEP_SEAL,
        # Stage 10 — exit eval
        SPAN_EXIT_EVAL_POLICY,
        SPAN_EXIT_EVAL_QUALITY,
        SPAN_EXIT_EVAL_SAFETY,
        SPAN_EXIT_EVAL_MUTATION_AUTH,
        SPAN_EXIT_DISPOSITION,
        # Stage 11 — response
        SPAN_RESPONSE_EMIT,
        SPAN_RUNTIME_CLOSE_NO_WRITE,
        # Stage 12 — UWG/L4 commit
        SPAN_UWG_COMMIT_VERIFY_AUTHORITY,
        SPAN_UWG_COMMIT_VALIDATE_DIFF,
        SPAN_UWG_COMMIT_APPEND_LEDGER,
        SPAN_L4_ARCHIVE_MATERIALIZE,
        # Stage 13 — L6 eval
        SPAN_L6_TELEMETRY_INGEST,
        SPAN_L6_OUTCOME_EVALUATE,
        SPAN_L6_TRAJECTORY_EVALUATE,
        SPAN_L6_RETRIEVAL_EVALUATE,
        SPAN_L6_REPLAY_VERIFY,
        SPAN_L6_METRICS_SEAL,
        # Stage 14 — meta-learning
        SPAN_METALEARNING_SIGNAL_FUSE,
        SPAN_METALEARNING_RCA_CREATE,
        SPAN_METALEARNING_PATTERN_EXTRACT,
        SPAN_METALEARNING_RULE_DRAFT,
        SPAN_METALEARNING_SHADOW_REPLAY,
        SPAN_METALEARNING_PROMOTION_PROPOSE,
        SPAN_METALEARNING_PROMOTION_APPROVE_OR_REJECT,
        SPAN_METALEARNING_PROMOTION_COMMIT,
    }
)


# Mapping: stage number (1..14) -> (stage label, span set, signature attrs).
# Used by the Tier 2 contract and CI gate to drive structural validation.
STAGE_SPANS: Final[dict[int, tuple[str, frozenset[str], frozenset[str]]]] = {
    1: (
        "trace_root",
        frozenset({SPAN_TRACE_ROOT}),
        frozenset({ATTR_TRACE_ID, ATTR_RUN_ID, ATTR_INPUT_ENVELOPE_HASH}),
    ),
    2: (
        "intake",
        frozenset({SPAN_INTAKE_VALIDATE, SPAN_INTAKE_NORMALIZE, SPAN_INTAKE_STAMP_TRACE}),
        frozenset({ATTR_REQUEST_ID, ATTR_SCHEMA_STATUS, ATTR_AUTH_STATUS}),
    ),
    3: (
        "L1_reasoning",
        frozenset(
            {
                SPAN_L1_INTENT_PARSE,
                SPAN_L1_CONTEXT_PRIORS_LOAD,
                SPAN_L1_PLAN_DRAFT,
                SPAN_L1_PLAN_VALIDATE,
            }
        ),
        frozenset({ATTR_INTENT_FRAME_HASH, ATTR_PLAN_CONTRACT_HASH, ATTR_PROPOSED_ROUTE}),
    ),
    4: (
        "L0_routing",
        frozenset(
            {
                SPAN_L0_ROUTE_SCORE,
                SPAN_L0_CACHE_CHECK,
                SPAN_L0_ROUTE_SELECT,
                SPAN_L0_ROUTE_CONTRACT,
            }
        ),
        frozenset({ATTR_SELECTED_ROUTE, ATTR_REASON_CODES, ATTR_ROUTE_CONTRACT_HASH}),
    ),
    5: (
        "direct_path",
        frozenset(
            {SPAN_L0_DIRECT_PACKAGE, SPAN_L0_RET_SHORT_CIRCUIT, SPAN_L0_SINGLE_STEP_DISPATCH}
        ),
        frozenset({ATTR_DIRECT_STEP_ID, ATTR_PACKET_HASH}),
    ),
    6: (
        "L3_orchestration",
        frozenset(
            {
                SPAN_L3_WORKFLOW_EXPAND,
                SPAN_L3_WORKFLOW_STATE,
                SPAN_L3_STEP_READY_CHECK,
                SPAN_L3_STEP_DISPATCH,
                SPAN_L3_STEP_MERGE_RESULT,
            }
        ),
        frozenset({ATTR_WORKFLOW_ID, ATTR_DAG_HASH}),
    ),
    7: (
        "C0_retrieval",
        frozenset(
            {
                SPAN_C0_RETRIEVAL_PLAN,
                SPAN_C0_QUERY_EMBED,
                SPAN_C0_EVIDENCE_FETCH_DENSE,
                SPAN_C0_EVIDENCE_FETCH_SPARSE,
                SPAN_C0_GRAPH_TRAVERSE,
                SPAN_C0_EVIDENCE_RERANK,
                SPAN_C0_EVIDENCE_CONTRACT,
            }
        ),
        frozenset({ATTR_EVIDENCE_IDS, ATTR_RETRIEVAL_MODE}),
    ),
    8: (
        "prompt_assembly",
        frozenset(
            {
                SPAN_PA_STATIC_BLOCKS_LOAD,
                SPAN_PA_CONTEXT_SLOT,
                SPAN_PA_TOKEN_BUDGET,
                SPAN_PA_PROMPT_CONTRACT,
            }
        ),
        frozenset({ATTR_PROMPT_ENVELOPE_HASH, ATTR_PROMPT_HASH}),
    ),
    9: (
        "L2_execution",
        frozenset(
            {
                SPAN_L2_STEP_PREPARE,
                SPAN_L2_STEP_VALIDATE,
                SPAN_L2_MODEL_INVOKE,
                SPAN_L2_TOOL_INVOKE,
                SPAN_L2_HEAL_ATTEMPT,
                SPAN_L2_STEP_SEAL,
            }
        ),
        frozenset({ATTR_STEP_ID, ATTR_OUTPUT_HASH}),
    ),
    10: (
        "exit_eval",
        frozenset(
            {
                SPAN_EXIT_EVAL_POLICY,
                SPAN_EXIT_EVAL_QUALITY,
                SPAN_EXIT_EVAL_SAFETY,
                SPAN_EXIT_EVAL_MUTATION_AUTH,
                SPAN_EXIT_DISPOSITION,
            }
        ),
        frozenset({ATTR_EXIT_DISPOSITION, ATTR_POLICY_HASH}),
    ),
    11: (
        "response",
        frozenset({SPAN_RESPONSE_EMIT, SPAN_RUNTIME_CLOSE_NO_WRITE}),
        frozenset({ATTR_NO_WRITE_MARKER, ATTR_FINAL_OUTPUT_HASH}),
    ),
    12: (
        "uwg_l4_commit",
        frozenset(
            {
                SPAN_UWG_COMMIT_VERIFY_AUTHORITY,
                SPAN_UWG_COMMIT_VALIDATE_DIFF,
                SPAN_UWG_COMMIT_APPEND_LEDGER,
                SPAN_L4_ARCHIVE_MATERIALIZE,
            }
        ),
        frozenset({ATTR_COMMIT_ID, ATTR_LEDGER_HASH}),
    ),
    13: (
        "L6_eval",
        frozenset(
            {
                SPAN_L6_TELEMETRY_INGEST,
                SPAN_L6_OUTCOME_EVALUATE,
                SPAN_L6_TRAJECTORY_EVALUATE,
                SPAN_L6_RETRIEVAL_EVALUATE,
                SPAN_L6_REPLAY_VERIFY,
                SPAN_L6_METRICS_SEAL,
            }
        ),
        frozenset({ATTR_EVAL_BUNDLE_ID, ATTR_REPLAY_DIGEST}),
    ),
    14: (
        "meta_learning",
        frozenset(
            {
                SPAN_METALEARNING_SIGNAL_FUSE,
                SPAN_METALEARNING_RCA_CREATE,
                SPAN_METALEARNING_PATTERN_EXTRACT,
                SPAN_METALEARNING_RULE_DRAFT,
                SPAN_METALEARNING_SHADOW_REPLAY,
                SPAN_METALEARNING_PROMOTION_PROPOSE,
                SPAN_METALEARNING_PROMOTION_APPROVE_OR_REJECT,
                SPAN_METALEARNING_PROMOTION_COMMIT,
            }
        ),
        frozenset({ATTR_RCA_ID, ATTR_PROMOTION_CANDIDATE_ID}),
    ),
}


ALL_NODE_TYPES: Final[frozenset[str]] = frozenset(
    {
        NODE_RUNTIME_RUN,
        NODE_USER_REQUEST,
        NODE_INTAKE_ENVELOPE,
        NODE_VALIDATED_REQUEST,
        NODE_L1_INTENT_FRAME,
        NODE_L1_PLAN_CONTRACT,
        NODE_ROUTE_CONTRACT,
        NODE_ROUTE_FAMILY,
        NODE_DIRECT_STEP_PACKET,
        NODE_TERMINAL_RETURN,
        NODE_WORKFLOW_GRAPH,
        NODE_WORKFLOW_STEP,
        NODE_STEP_DEPENDENCY,
        NODE_RETRIEVAL_QUERY,
        NODE_EVIDENCE_CHUNK,
        NODE_ENTITY_SUBGRAPH,
        NODE_EVIDENCE_CONTRACT,
        NODE_PROMPT_ENVELOPE,
        NODE_BOUNDED_PROMPT_PACKET,
        NODE_EXECUTION_STEP,
        NODE_VALIDATION_PACKET,
        NODE_MODEL_INVOCATION,
        NODE_TOOL_INVOCATION,
        NODE_HEALING_ATTEMPT,
        NODE_SEALED_L2_ARTIFACT,
        NODE_EXIT_DISPOSITION,
        NODE_RUNTIME_OUTCOME,
        NODE_HITL_PACKET,
        NODE_RUNTIME_RESPONSE,
        NODE_L4_COMMIT,
        NODE_LEDGER_APPEND,
        NODE_L6_EVIDENCE_BUNDLE,
        NODE_EVAL_SIGNAL_BUNDLE,
        NODE_REPLAY_VERIFICATION,
        NODE_INCIDENT_CLUSTER,
        NODE_RCA_RECORD,
        NODE_PROMOTION_CANDIDATE,
        NODE_APPROVED_LEARNING_UPDATE,
    }
)


ALL_EDGE_TYPES: Final[frozenset[str]] = frozenset(
    {
        EDGE_STARTED,
        EDGE_CONTAINS,
        EDGE_VALIDATES,
        EDGE_EMITS,
        EDGE_INTERPRETS,
        EDGE_PROPOSES_ROUTE,
        EDGE_READS,
        EDGE_SELECTS,
        EDGE_BYPASSES,
        EDGE_DISPATCHES_TO,
        EDGE_EXPANDS,
        EDGE_DEPENDS_ON,
        EDGE_SEARCHES,
        EDGE_MATCHES,
        EDGE_CONNECTS,
        EDGE_PACKAGES,
        EDGE_RECEIVES,
        EDGE_BINDS,
        EDGE_BLOCKS,
        EDGE_ALLOWS,
        EDGE_CONSUMES,
        EDGE_INVOKES,
        EDGE_REPAIRS,
        EDGE_RETRIES,
        EDGE_SEALS,
        EDGE_EVALUATES,
        EDGE_DENIES,
        EDGE_REROUTES,
        EDGE_ESCALATES,
        EDGE_REQUESTS_COMMIT,
        EDGE_RETURNS_TO,
        EDGE_CLOSES,
        EDGE_COMMITS_TO,
        EDGE_APPENDS,
        EDGE_REFRESHES,
        EDGE_OBSERVES,
        EDGE_GRADES,
        EDGE_VERIFIES,
        EDGE_LEARNS_FROM,
        EDGE_PROPOSES,
        EDGE_PROMOTES_VIA,
    }
)


def stage_for_span(span_name: str) -> int | None:
    """Return the 1..14 stage number for ``span_name``, or None if unknown."""
    for stage_num, (_label, spans, _attrs) in STAGE_SPANS.items():
        if span_name in spans:
            return stage_num
    return None


def attrs_for_stage(stage: int) -> frozenset[str]:
    """Return the signature-attribute set for ``stage`` (1..14)."""
    entry = STAGE_SPANS.get(stage)
    if entry is None:
        return frozenset()
    return entry[2]


def label_for_stage(stage: int) -> str:
    """Return the canonical label for ``stage`` (1..14)."""
    entry = STAGE_SPANS.get(stage)
    if entry is None:
        return ""
    return entry[0]


__all__ = [
    # Layer constants
    "LAYER_U0",
    "LAYER_L0",
    "LAYER_L1",
    "LAYER_L2",
    "LAYER_L3",
    "LAYER_L4",
    "LAYER_L5",
    "LAYER_L6",
    "LAYER_L7",
    "ALL_LAYERS",
    # Stage 1
    "SPAN_TRACE_ROOT",
    "ATTR_TRACE_ID",
    "ATTR_SPAN_ID",
    "ATTR_PARENT_SPAN_ID",
    "ATTR_RUN_ID",
    "ATTR_REQUEST_ID",
    "ATTR_SESSION_ID",
    "ATTR_TENANT_ID",
    "ATTR_CALLER_SCOPE",
    "ATTR_INPUT_ENVELOPE_HASH",
    "ATTR_RUNTIME_VERSION",
    "ATTR_SERVICE_NAME",
    "ATTR_DEPLOYMENT_ENV",
    "NODE_RUNTIME_RUN",
    "NODE_USER_REQUEST",
    "EDGE_STARTED",
    "EDGE_CONTAINS",
    # Stage 2
    "SPAN_INTAKE_VALIDATE",
    "SPAN_INTAKE_NORMALIZE",
    "SPAN_INTAKE_STAMP_TRACE",
    "ATTR_SCHEMA_STATUS",
    "ATTR_AUTH_STATUS",
    "ATTR_QUOTA_STATUS",
    "ATTR_NORMALIZED_PAYLOAD_HASH",
    "ATTR_REJECTION_REASON",
    "ATTR_CALLER_SCOPE_BASELINE",
    "ATTR_ORIGIN_TRUST",
    "ATTR_INGRESS_CHANNEL",
    "ATTR_ENVELOPE_VERSION",
    "NODE_INTAKE_ENVELOPE",
    "NODE_VALIDATED_REQUEST",
    "EDGE_VALIDATES",
    "EDGE_EMITS",
    # Stage 3
    "SPAN_L1_INTENT_PARSE",
    "SPAN_L1_CONTEXT_PRIORS_LOAD",
    "SPAN_L1_PLAN_DRAFT",
    "SPAN_L1_PLAN_VALIDATE",
    "ATTR_INTENT_FRAME_HASH",
    "ATTR_TASK_CLASS",
    "ATTR_TASK_SPEC_HASH",
    "ATTR_SUCCESS_CONDITION",
    "ATTR_ASSUMPTIONS",
    "ATTR_UNRESOLVED_GAPS",
    "ATTR_PROPOSED_ROUTE",
    "ATTR_ROUTE_RISK",
    "ATTR_CONFIDENCE",
    "ATTR_PLAN_CONTRACT_HASH",
    "ATTR_GROUNDING_REQUIRED",
    "ATTR_OUTPUT_CONTRACT_HASH",
    "NODE_L1_INTENT_FRAME",
    "NODE_L1_PLAN_CONTRACT",
    "EDGE_INTERPRETS",
    "EDGE_PROPOSES_ROUTE",
    # Stage 4
    "SPAN_L0_ROUTE_SCORE",
    "SPAN_L0_CACHE_CHECK",
    "SPAN_L0_ROUTE_SELECT",
    "SPAN_L0_ROUTE_CONTRACT",
    "ATTR_SELECTED_ROUTE",
    "ATTR_REASON_CODES",
    "ATTR_RISK_TIER",
    "ATTR_FRESHNESS_CLASS",
    "ATTR_CACHE_DECISION",
    "ATTR_CACHE_KEY_HASH",
    "ATTR_SEMANTIC_SIMILARITY_SCORE",
    "ATTR_SUPPORT_REQUIRED",
    "ATTR_EXECUTION_FORM",
    "ATTR_ROUTE_CONTRACT_HASH",
    "ATTR_ROUTE_BOUNDS",
    "ATTR_POLICY_HASH",
    "EXECUTION_FORM_TERMINAL",
    "EXECUTION_FORM_SINGLE_STEP",
    "EXECUTION_FORM_MANAGED_WORKFLOW",
    "VALID_EXECUTION_FORMS",
    "NODE_ROUTE_CONTRACT",
    "NODE_ROUTE_FAMILY",
    "EDGE_READS",
    "EDGE_SELECTS",
    # Stage 5
    "SPAN_L0_DIRECT_PACKAGE",
    "SPAN_L0_RET_SHORT_CIRCUIT",
    "SPAN_L0_SINGLE_STEP_DISPATCH",
    "ATTR_DIRECT_STEP_ID",
    "ATTR_NO_L3_REQUIRED",
    "ATTR_PACKET_HASH",
    "ATTR_TERMINAL_RETURN_REASON",
    "NODE_DIRECT_STEP_PACKET",
    "NODE_TERMINAL_RETURN",
    "EDGE_BYPASSES",
    "EDGE_DISPATCHES_TO",
    # Stage 6
    "SPAN_L3_WORKFLOW_EXPAND",
    "SPAN_L3_WORKFLOW_STATE",
    "SPAN_L3_STEP_READY_CHECK",
    "SPAN_L3_STEP_DISPATCH",
    "SPAN_L3_STEP_MERGE_RESULT",
    "ATTR_WORKFLOW_ID",
    "ATTR_DAG_HASH",
    "ATTR_NODE_IDS",
    "ATTR_DEPENDENCY_EDGES",
    "ATTR_BRANCH_RULES",
    "ATTR_JOIN_RULES",
    "ATTR_CHECKPOINT_HASH",
    "ATTR_CURRENT_STEP_ID",
    "ATTR_READY_NODE_IDS",
    "ATTR_BLOCKED_NODE_IDS",
    "ATTR_WORKFLOW_STATE_HASH",
    "NODE_WORKFLOW_GRAPH",
    "NODE_WORKFLOW_STEP",
    "NODE_STEP_DEPENDENCY",
    "EDGE_EXPANDS",
    "EDGE_DEPENDS_ON",
    # Stage 7
    "SPAN_C0_RETRIEVAL_PLAN",
    "SPAN_C0_QUERY_EMBED",
    "SPAN_C0_EVIDENCE_FETCH_DENSE",
    "SPAN_C0_EVIDENCE_FETCH_SPARSE",
    "SPAN_C0_GRAPH_TRAVERSE",
    "SPAN_C0_EVIDENCE_RERANK",
    "SPAN_C0_EVIDENCE_CONTRACT",
    "ATTR_QUERY_VEC_ID",
    "ATTR_QUERY_TEXT_HASH",
    "ATTR_SOURCE_SCOPE",
    "ATTR_ACL_SCOPE",
    "ATTR_FRESHNESS_SCOPE",
    "ATTR_VECTOR_STORE_ID",
    "ATTR_INDEX_VERSION",
    "ATTR_EMBEDDING_MODEL_ID",
    "ATTR_RETRIEVAL_MODE",
    "ATTR_TOP_K",
    "ATTR_SIMILARITY_THRESHOLD",
    "ATTR_BM25_ENABLED",
    "ATTR_RERANKER_MODEL_ID",
    "ATTR_SOURCE_IDS",
    "ATTR_CHUNK_IDS",
    "ATTR_ENTITY_IDS",
    "ATTR_EDGE_IDS",
    "ATTR_EVIDENCE_IDS",
    "ATTR_RERANK_SCORES",
    "ATTR_SUPPORT_SCORE",
    "ATTR_COVERAGE_GAPS",
    "ATTR_CONTRADICTION_FLAGS",
    "ATTR_CONTEXTUAL_CHUNK_HEADER_HASH",
    "ATTR_PARENT_DOCUMENT_ID",
    "ATTR_CITATION_SPAN_IDS",
    "RETRIEVAL_MODE_DENSE",
    "RETRIEVAL_MODE_SPARSE",
    "RETRIEVAL_MODE_HYBRID",
    "RETRIEVAL_MODE_GRAPH",
    "VALID_RETRIEVAL_MODES",
    "NODE_RETRIEVAL_QUERY",
    "NODE_EVIDENCE_CHUNK",
    "NODE_ENTITY_SUBGRAPH",
    "NODE_EVIDENCE_CONTRACT",
    "EDGE_SEARCHES",
    "EDGE_MATCHES",
    "EDGE_CONNECTS",
    # Stage 8
    "SPAN_PA_STATIC_BLOCKS_LOAD",
    "SPAN_PA_CONTEXT_SLOT",
    "SPAN_PA_TOKEN_BUDGET",
    "SPAN_PA_PROMPT_CONTRACT",
    "ATTR_PROMPT_ENVELOPE_HASH",
    "ATTR_SYSTEM_TEMPLATE_HASH",
    "ATTR_TASK_TEMPLATE_HASH",
    "ATTR_OUTPUT_SCHEMA_HASH",
    "ATTR_MUST_USE_CONTEXT_IDS",
    "ATTR_TOKEN_BUDGET_TOTAL",
    "ATTR_TOKEN_BUDGET_USED",
    "ATTR_TRIM_STRATEGY",
    "ATTR_OVERFLOW_ACTION",
    "ATTR_HMAC",
    "ATTR_REPLAY_METADATA",
    "ATTR_PROMPT_HASH",
    "ATTR_PROMPT_VERSION",
    "NODE_PROMPT_ENVELOPE",
    "NODE_BOUNDED_PROMPT_PACKET",
    "EDGE_PACKAGES",
    # Stage 9
    "SPAN_L2_STEP_PREPARE",
    "SPAN_L2_STEP_VALIDATE",
    "SPAN_L2_MODEL_INVOKE",
    "SPAN_L2_TOOL_INVOKE",
    "SPAN_L2_HEAL_ATTEMPT",
    "SPAN_L2_STEP_SEAL",
    "ATTR_STEP_ID",
    "ATTR_PARENT_STEP_ID",
    "ATTR_BLUEPRINT_HASH",
    "ATTR_IDEMPOTENCY_KEY",
    "ATTR_REPLAY_KEY",
    "ATTR_CAPABILITY_TOKEN_HASH",
    "ATTR_SANDBOX_SCOPE",
    "ATTR_FS_SCOPE",
    "ATTR_NET_SCOPE",
    "ATTR_TOOL_ALLOWLIST",
    "ATTR_MODEL_ALLOWLIST",
    "ATTR_VALIDATION_PACKET_ID",
    "ATTR_INPUT_SCHEMA_STATUS",
    "ATTR_SIDE_EFFECT_CLASS",
    "ATTR_SANDBOX_STATUS",
    "ATTR_BUDGET_SCOPE",
    "ATTR_MUTATION_INTENT_DETECTED",
    "ATTR_WRITE_AUTH",
    "ATTR_MODEL_ID",
    "ATTR_PROVIDER",
    "ATTR_DECODING_CONFIG_HASH",
    "ATTR_PROMPT_TOKENS",
    "ATTR_OUTPUT_TOKENS",
    "ATTR_LATENCY_MS",
    "ATTR_STOP_REASON",
    "ATTR_RESPONSE_ID",
    "ATTR_MODEL_OUTPUT_HASH",
    "ATTR_TOOL_NAME",
    "ATTR_TOOL_VERSION",
    "ATTR_ARGS_HASH",
    "ATTR_RETURN_CODE",
    "ATTR_STDOUT_HASH",
    "ATTR_STDERR_HASH",
    "ATTR_TIMEOUT_STATUS",
    "ATTR_CIRCUIT_BREAKER_STATUS",
    "ATTR_ERROR_CODE",
    "ATTR_REASON_CODE",
    "ATTR_RETRY_COUNT",
    "ATTR_REPAIR_COUNT",
    "ATTR_HEALING_TIER",
    "ATTR_PARENT_ATTEMPT_ID",
    "ATTR_OSCILLATION_GUARD_STATUS",
    "ATTR_TERMINAL_REPAIR_STATUS",
    "ATTR_TERMINAL_CLASS",
    "ATTR_OUTPUT_ARTIFACT_IDS",
    "ATTR_LINEAGE_HASH",
    "ATTR_OUTPUT_HASH",
    "ATTR_STATE_DIFF_HASH",
    "ATTR_PROPOSED_MUTATION_HASH",
    "ATTR_ATTEMPT_COUNT",
    "ATTR_VALIDATION_COUNTERS",
    "NODE_EXECUTION_STEP",
    "NODE_VALIDATION_PACKET",
    "NODE_MODEL_INVOCATION",
    "NODE_TOOL_INVOCATION",
    "NODE_HEALING_ATTEMPT",
    "NODE_SEALED_L2_ARTIFACT",
    "EDGE_RECEIVES",
    "EDGE_BINDS",
    "EDGE_BLOCKS",
    "EDGE_ALLOWS",
    "EDGE_CONSUMES",
    "EDGE_INVOKES",
    "EDGE_REPAIRS",
    "EDGE_RETRIES",
    "EDGE_SEALS",
    # Stage 10
    "SPAN_EXIT_EVAL_POLICY",
    "SPAN_EXIT_EVAL_QUALITY",
    "SPAN_EXIT_EVAL_SAFETY",
    "SPAN_EXIT_EVAL_MUTATION_AUTH",
    "SPAN_EXIT_DISPOSITION",
    "ATTR_EXIT_DISPOSITION",
    "ATTR_COMPLIANCE_HASH",
    "ATTR_GROUNDEDNESS_CHECK",
    "ATTR_CITATION_SUPPORT_CHECK",
    "ATTR_SCHEMA_CHECK",
    "ATTR_SAFETY_CHECK",
    "ATTR_MUTATION_AUTH_RESULT",
    "ATTR_HITL_REQUIRED",
    "ATTR_HITL_PACKET_ID",
    "ATTR_HITL_DECISION",
    "ATTR_FINAL_OUTPUT_HASH",
    "DISPOSITION_ALLOW",
    "DISPOSITION_DENY",
    "DISPOSITION_REROUTE",
    "DISPOSITION_ESCALATE",
    "DISPOSITION_COMMIT_REQUEST",
    "VALID_DISPOSITIONS",
    "NODE_EXIT_DISPOSITION",
    "NODE_RUNTIME_OUTCOME",
    "NODE_HITL_PACKET",
    "EDGE_EVALUATES",
    "EDGE_DENIES",
    "EDGE_REROUTES",
    "EDGE_ESCALATES",
    "EDGE_REQUESTS_COMMIT",
    # Stage 11
    "SPAN_RESPONSE_EMIT",
    "SPAN_RUNTIME_CLOSE_NO_WRITE",
    "ATTR_NO_WRITE_MARKER",
    "ATTR_CALLER_DELIVERY_STATUS",
    "ATTR_RUNTIME_CLOSED",
    "NODE_RUNTIME_RESPONSE",
    "EDGE_RETURNS_TO",
    "EDGE_CLOSES",
    # Stage 12
    "SPAN_UWG_COMMIT_VERIFY_AUTHORITY",
    "SPAN_UWG_COMMIT_VALIDATE_DIFF",
    "SPAN_UWG_COMMIT_APPEND_LEDGER",
    "SPAN_L4_ARCHIVE_MATERIALIZE",
    "ATTR_COMMIT_REQUEST_ID",
    "ATTR_MUTATION_TYPE",
    "ATTR_PROPOSED_DIFF_HASH",
    "ATTR_BEFORE_HASH",
    "ATTR_AFTER_HASH",
    "ATTR_LEDGER_HASH",
    "ATTR_ROLLBACK_REF",
    "ATTR_COMMIT_ID",
    "ATTR_ALIAS_SWAP_STATUS",
    "ATTR_AUDIT_RECEIPT_ID",
    "ATTR_WRITE_LOCK_ID",
    "ATTR_SERIALIZED_QUEUE_POSITION",
    "NODE_L4_COMMIT",
    "NODE_LEDGER_APPEND",
    "EDGE_COMMITS_TO",
    "EDGE_APPENDS",
    "EDGE_REFRESHES",
    # Stage 13
    "SPAN_L6_TELEMETRY_INGEST",
    "SPAN_L6_OUTCOME_EVALUATE",
    "SPAN_L6_TRAJECTORY_EVALUATE",
    "SPAN_L6_RETRIEVAL_EVALUATE",
    "SPAN_L6_REPLAY_VERIFY",
    "SPAN_L6_METRICS_SEAL",
    "ATTR_TASK_COMPLETION_SCORE",
    "ATTR_GROUNDEDNESS_SCORE",
    "ATTR_CITATION_SUPPORT_SCORE",
    "ATTR_ANSWER_RELEVANCE_SCORE",
    "ATTR_RETRIEVAL_PRECISION",
    "ATTR_RETRIEVAL_RECALL_PROXY",
    "ATTR_SUPPORT_RATE",
    "ATTR_CONTRADICTION_RATE",
    "ATTR_TRAJECTORY_SCORE",
    "ATTR_TOOL_ORDER_SCORE",
    "ATTR_RETRY_THRASH",
    "ATTR_BUDGET_ADHERENCE_SCORE",
    "ATTR_TOKEN_COST",
    "ATTR_TOOL_COST",
    "ATTR_DRIFT_FLAGS",
    "ATTR_ANOMALY_FLAGS",
    "ATTR_REPLAY_DIGEST",
    "ATTR_DETERMINISM_STATUS",
    "ATTR_EVAL_BUNDLE_ID",
    "ATTR_GRADER_ID",
    "ATTR_HUMAN_CALIBRATION_STATUS",
    "NODE_L6_EVIDENCE_BUNDLE",
    "NODE_EVAL_SIGNAL_BUNDLE",
    "NODE_REPLAY_VERIFICATION",
    "EDGE_OBSERVES",
    "EDGE_GRADES",
    "EDGE_VERIFIES",
    # Stage 14
    "SPAN_METALEARNING_SIGNAL_FUSE",
    "SPAN_METALEARNING_RCA_CREATE",
    "SPAN_METALEARNING_PATTERN_EXTRACT",
    "SPAN_METALEARNING_RULE_DRAFT",
    "SPAN_METALEARNING_SHADOW_REPLAY",
    "SPAN_METALEARNING_PROMOTION_PROPOSE",
    "SPAN_METALEARNING_PROMOTION_APPROVE_OR_REJECT",
    "SPAN_METALEARNING_PROMOTION_COMMIT",
    "ATTR_RCA_ID",
    "ATTR_INCIDENT_CLUSTER_ID",
    "ATTR_PATTERN_ID",
    "ATTR_SEVERITY",
    "ATTR_CONFIDENCE_BAND",
    "ATTR_PROPOSED_RULE_UPDATE_HASH",
    "ATTR_PROPOSED_PROMPT_UPDATE_HASH",
    "ATTR_PROPOSED_POLICY_UPDATE_HASH",
    "ATTR_PROMOTION_CANDIDATE_ID",
    "ATTR_SHADOW_REPLAY_RESULT",
    "ATTR_REGRESSION_RESULT",
    "ATTR_SME_SIGNOFF_STATUS",
    "ATTR_APPROVED_UPDATE_ID",
    "ATTR_FUTURE_RUN_ONLY",
    "ATTR_ROLLBACK_PLAN_HASH",
    "NODE_INCIDENT_CLUSTER",
    "NODE_RCA_RECORD",
    "NODE_PROMOTION_CANDIDATE",
    "NODE_APPROVED_LEARNING_UPDATE",
    "EDGE_LEARNS_FROM",
    "EDGE_PROPOSES",
    "EDGE_PROMOTES_VIA",
    # Aggregates
    "ALL_SPAN_NAMES",
    "ALL_NODE_TYPES",
    "ALL_EDGE_TYPES",
    "STAGE_SPANS",
    # Helpers
    "stage_for_span",
    "attrs_for_stage",
    "label_for_stage",
]
