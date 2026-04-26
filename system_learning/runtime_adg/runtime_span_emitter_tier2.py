"""Tier 2 runtime span emit helpers — full 14-stage spec coverage.

Sister module to ``runtime_span_emitter`` (Tier 1: trace_root / step.seal /
exit.disposition). This module adds emit helpers for the remaining stages
defined in ``docs/reference/Runtime ADG and OTEL Spans.md``:

    Stage 02 — emit_intake (validate / normalize / stamp_trace)
    Stage 03 — emit_l1_reasoning (intent.parse / context.priors_load / plan.draft / plan.validate)
    Stage 04 — emit_l0_route (score / cache.check / select / contract)  [select also covered by Tier 1]
    Stage 05 — emit_direct_path (package / short_circuit / single_step.dispatch)
    Stage 06 — emit_l3_step (workflow.expand / step.ready_check / step.dispatch / step.merge_result)
    Stage 08 — emit_prompt_assembly (static_blocks.load / context.slot / token_budget / prompt.contract)
    Stage 11 — emit_response (response.emit / runtime.close_no_write)
    Stage 12 — emit_uwg_commit (verify_authority / validate_diff / append_ledger / archive.materialize)
    Stage 13 — emit_l6_eval (telemetry.ingest / outcome.evaluate / trajectory.evaluate / replay.verify / metrics.seal)
    Stage 14 — emit_meta_learning (signal.fuse / rca.create / pattern.extract / promotion.propose / promotion.commit)

L2 execution (Stage 09) already has rich producers via Tier 1 step.seal
+ heal_router_otel + consensus_otel; this module does not add a duplicate
helper for it. C0 retrieval (Stage 07) gets a thin universal helper here
so every spec stage that lacks a Tier 1 producer has at least one
default emitter — useful for tests, replay, and scaffolding.

Design rules (mirror ``runtime_span_emitter``):

  1. Fail-open: missing adapter / no `_completed_spans` -> debug log + return.
  2. Idempotent per call: caller decides emit timing.
  3. Deterministic attribute shape — consumed by ``RuntimeADGMaterializer``.
  4. No reach into ``agentic_core`` (this module sits below L6 in the layer
     stack). Span-name strings are duplicated here from
     ``agentic_core.L6_observability.semconv.runtime``; a unit test enforces
     they stay in sync.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Sequence

from system_learning.runtime_adg.runtime_span_emitter import _append_span

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Span name constants — MUST stay in sync with semconv.runtime.
# ---------------------------------------------------------------------------

# Stage 07 — C0 retrieval
SPAN_C0_RETRIEVAL_PLAN = "C0.retrieval.plan"
SPAN_C0_QUERY_EMBED = "C0.query.embed"
SPAN_C0_EVIDENCE_FETCH_DENSE = "C0.evidence.fetch_dense"
SPAN_C0_EVIDENCE_FETCH_SPARSE = "C0.evidence.fetch_sparse"
SPAN_C0_GRAPH_TRAVERSE = "C0.graph.traverse"
SPAN_C0_EVIDENCE_RERANK = "C0.evidence.rerank"
SPAN_C0_EVIDENCE_CONTRACT = "C0.evidence.contract"

# Stage 02 — intake / U0
SPAN_INTAKE_VALIDATE = "U0.intake.validate"
SPAN_INTAKE_NORMALIZE = "U0.intake.normalize"
SPAN_INTAKE_STAMP_TRACE = "U0.intake.stamp_trace"

# Stage 03 — L1 reasoning
SPAN_L1_INTENT_PARSE = "L1.intent.parse"
SPAN_L1_CONTEXT_PRIORS_LOAD = "L1.context.priors_load"
SPAN_L1_PLAN_DRAFT = "L1.plan.draft"
SPAN_L1_PLAN_VALIDATE = "L1.plan.validate"

# Stage 04 — L0 routing
SPAN_L0_ROUTE_SCORE = "L0.route.score"
SPAN_L0_CACHE_CHECK = "L0.cache.check"
SPAN_L0_ROUTE_SELECT = "L0.route.select"
SPAN_L0_ROUTE_CONTRACT = "L0.route.contract"

# Stage 05 — direct path
SPAN_L0_DIRECT_PACKAGE = "L0.direct.package"
SPAN_L0_RET_SHORT_CIRCUIT = "L0.ret.short_circuit"
SPAN_L0_SINGLE_STEP_DISPATCH = "L0.single_step.dispatch"

# Stage 06 — L3 orchestration
SPAN_L3_WORKFLOW_EXPAND = "L3.workflow.expand"
SPAN_L3_WORKFLOW_STATE = "L3.workflow.state"
SPAN_L3_STEP_READY_CHECK = "L3.step.ready_check"
SPAN_L3_STEP_DISPATCH = "L3.step.dispatch"
SPAN_L3_STEP_MERGE_RESULT = "L3.step.merge_result"

# Stage 08 — prompt assembly
SPAN_PA_STATIC_BLOCKS_LOAD = "PA.static_blocks.load"
SPAN_PA_CONTEXT_SLOT = "PA.context.slot"
SPAN_PA_TOKEN_BUDGET = "PA.token_budget"
SPAN_PA_PROMPT_CONTRACT = "PA.prompt.contract"

# Stage 11 — response
SPAN_RESPONSE_EMIT = "Response.emit"
SPAN_RUNTIME_CLOSE_NO_WRITE = "Runtime.close_no_write"

# Stage 12 — UWG/L4 commit
SPAN_UWG_COMMIT_VERIFY_AUTHORITY = "UWG.commit.verify_authority"
SPAN_UWG_COMMIT_VALIDATE_DIFF = "UWG.commit.validate_diff"
SPAN_UWG_COMMIT_APPEND_LEDGER = "UWG.commit.append_ledger"
SPAN_L4_ARCHIVE_MATERIALIZE = "L4.archive.materialize"

# Stage 13 — L6 eval
SPAN_L6_TELEMETRY_INGEST = "L6.telemetry.ingest"
SPAN_L6_OUTCOME_EVALUATE = "L6.outcome.evaluate"
SPAN_L6_TRAJECTORY_EVALUATE = "L6.trajectory.evaluate"
SPAN_L6_RETRIEVAL_EVALUATE = "L6.retrieval.evaluate"
SPAN_L6_REPLAY_VERIFY = "L6.replay.verify"
SPAN_L6_METRICS_SEAL = "L6.metrics.seal"

# Stage 14 — meta-learning
SPAN_METALEARNING_SIGNAL_FUSE = "MetaLearning.signal.fuse"
SPAN_METALEARNING_RCA_CREATE = "MetaLearning.rca.create"
SPAN_METALEARNING_PATTERN_EXTRACT = "MetaLearning.pattern.extract"
SPAN_METALEARNING_RULE_DRAFT = "MetaLearning.rule.draft"
SPAN_METALEARNING_SHADOW_REPLAY = "MetaLearning.shadow_replay"
SPAN_METALEARNING_PROMOTION_PROPOSE = "MetaLearning.promotion.propose"
SPAN_METALEARNING_PROMOTION_APPROVE_OR_REJECT = "MetaLearning.promotion.approve_or_reject"
SPAN_METALEARNING_PROMOTION_COMMIT = "MetaLearning.promotion.commit"


# Layer string constants
_LAYER_U0 = "U0_intake"
_LAYER_L0 = "L0_routing"
_LAYER_L1 = "L1_cognition"
_LAYER_L3 = "L3_orchestration"
_LAYER_L4 = "L4_state"
_LAYER_L5 = "L5_safety"
_LAYER_L6 = "L6_observability"
_LAYER_L7 = "L7_meta_learning"


def _now() -> float:
    return time.time()


# ===========================================================================
# Stage 02 — Intake / U0
# ===========================================================================


def emit_intake(
    adapter: Any,
    trace_id: str,
    request_id: str,
    *,
    schema_status: str = "ok",
    auth_status: str = "ok",
    quota_status: str = "ok",
    normalized_payload_hash: str | None = None,
    rejection_reason: str = "",
    parent_span_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    """Emit the U0 intake stamp_trace span (canonical intake marker).

    For finer granularity (validate / normalize emitted separately), call
    :func:`emit_intake_validate` and :func:`emit_intake_normalize` directly.
    """
    attrs: dict[str, Any] = {
        "request_id": request_id,
        "trace_id": trace_id,
        "schema_status": schema_status,
        "auth_status": auth_status,
        "quota_status": quota_status,
        "normalized_payload_hash": normalized_payload_hash or "",
        "rejection_reason": rejection_reason,
        "envelope_version": "v1",
        "parent_span_id": parent_span_id,
    }
    if metadata:
        attrs.update(metadata)
    _append_span(
        adapter,
        name=SPAN_INTAKE_STAMP_TRACE,
        kind="intake",
        layer=_LAYER_U0,
        component="U0Intake",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )


def emit_intake_validate(
    adapter: Any,
    trace_id: str,
    request_id: str,
    *,
    schema_status: str,
    auth_status: str,
    quota_status: str,
    rejection_reason: str = "",
    parent_span_id: str = "",
) -> None:
    attrs = {
        "request_id": request_id,
        "schema_status": schema_status,
        "auth_status": auth_status,
        "quota_status": quota_status,
        "rejection_reason": rejection_reason,
        "parent_span_id": parent_span_id,
    }
    _append_span(
        adapter,
        name=SPAN_INTAKE_VALIDATE,
        kind="validator",
        layer=_LAYER_U0,
        component="U0IntakeValidator",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )


def emit_intake_normalize(
    adapter: Any,
    trace_id: str,
    request_id: str,
    normalized_payload_hash: str,
    *,
    parent_span_id: str = "",
) -> None:
    attrs = {
        "request_id": request_id,
        "normalized_payload_hash": normalized_payload_hash,
        "envelope_version": "v1",
        "parent_span_id": parent_span_id,
    }
    _append_span(
        adapter,
        name=SPAN_INTAKE_NORMALIZE,
        kind="intake",
        layer=_LAYER_U0,
        component="U0IntakeNormalizer",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )


# ===========================================================================
# Stage 03 — L1 Reasoning
# ===========================================================================


def emit_l1_reasoning(
    adapter: Any,
    trace_id: str,
    *,
    intent_frame_hash: str,
    plan_contract_hash: str,
    proposed_route: str,
    task_class: str = "",
    confidence: float = 0.0,
    parent_span_id: str = "",
) -> None:
    """Emit the canonical L1 plan.draft span — anchors L1 stage in coverage."""
    attrs = {
        "intent_frame_hash": intent_frame_hash,
        "plan_contract_hash": plan_contract_hash,
        "proposed_route": proposed_route,
        "task_class": task_class,
        "confidence": confidence,
        "parent_span_id": parent_span_id,
    }
    _append_span(
        adapter,
        name=SPAN_L1_PLAN_DRAFT,
        kind="planner",
        layer=_LAYER_L1,
        component="L1Planner",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )


# ===========================================================================
# Stage 04 — L0 Route Decision
# ===========================================================================


def emit_l0_route_select(
    adapter: Any,
    trace_id: str,
    *,
    selected_route: str,
    reason_codes: Sequence[str] = (),
    route_contract_hash: str = "",
    cache_decision: str = "miss",
    execution_form: str = "single_step",
    confidence: float = 0.0,
    risk_tier: str = "low",
    parent_span_id: str = "",
) -> None:
    attrs = {
        "selected_route": selected_route,
        "reason_codes": list(reason_codes),
        "route_contract_hash": route_contract_hash,
        "cache_decision": cache_decision,
        "execution_form": execution_form,
        "confidence": confidence,
        "risk_tier": risk_tier,
        "parent_span_id": parent_span_id,
    }
    _append_span(
        adapter,
        name=SPAN_L0_ROUTE_SELECT,
        kind="router",
        layer=_LAYER_L0,
        component="L0Router",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )


# ===========================================================================
# Stage 05 — Direct Path
# ===========================================================================


def emit_direct_path(
    adapter: Any,
    trace_id: str,
    *,
    direct_step_id: str,
    selected_route: str,
    packet_hash: str,
    terminal_return_reason: str = "",
    parent_span_id: str = "",
) -> None:
    attrs = {
        "direct_step_id": direct_step_id,
        "selected_route": selected_route,
        "no_l3_required": True,
        "packet_hash": packet_hash,
        "terminal_return_reason": terminal_return_reason,
        "parent_span_id": parent_span_id,
    }
    _append_span(
        adapter,
        name=SPAN_L0_DIRECT_PACKAGE,
        kind="dispatcher",
        layer=_LAYER_L0,
        component="L0DirectDispatcher",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )


# ===========================================================================
# Stage 06 — L3 Orchestration
# ===========================================================================


def emit_l3_step(
    adapter: Any,
    trace_id: str,
    *,
    workflow_id: str,
    dag_hash: str,
    current_step_id: str,
    ready_node_ids: Sequence[str] = (),
    blocked_node_ids: Sequence[str] = (),
    workflow_state_hash: str = "",
    parent_span_id: str = "",
) -> None:
    """Emit the canonical L3 step.dispatch span — anchors L3 stage in coverage."""
    attrs = {
        "workflow_id": workflow_id,
        "dag_hash": dag_hash,
        "current_step_id": current_step_id,
        "ready_node_ids": list(ready_node_ids),
        "blocked_node_ids": list(blocked_node_ids),
        "workflow_state_hash": workflow_state_hash,
        "parent_span_id": parent_span_id,
    }
    _append_span(
        adapter,
        name=SPAN_L3_STEP_DISPATCH,
        kind="orchestrator",
        layer=_LAYER_L3,
        component="L3Orchestrator",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )


# ===========================================================================
# Stage 07 — C0 retrieval (universal scaffolding helper)
# ===========================================================================


def emit_c0_retrieval(
    adapter: Any,
    trace_id: str,
    *,
    retrieval_mode: str,
    evidence_ids: Sequence[str] = (),
    vector_store_id: str = "",
    index_version: str = "",
    query_vec_id: str = "",
    support_score: float = 0.0,
    parent_span_id: str = "",
) -> None:
    """Emit a default C0.evidence.contract span — Stage 07 universal helper.

    Production C0 retrieval is normally instrumented by ``rag.py`` producers
    which carry full GenAI semconv (operation.name, model_id, fetch latency,
    rerank scores). This helper is intentionally thin: it lets test and
    scaffolding code land a single Stage 07 span that satisfies the Tier 2
    contract (kind=retrieval, layer=L1, attrs include retrieval_mode +
    vector_store_id + index_version) without pulling in the full RAG stack.

    For real production traces, prefer the rag.py emitters which fan out into
    ``C0.retrieval.plan`` -> ``C0.query.embed`` -> ``C0.evidence.fetch_*``
    -> ``C0.evidence.rerank`` -> ``C0.evidence.contract``.
    """
    if retrieval_mode not in {"dense", "sparse", "hybrid", "graph"}:
        # Fail-open with debug log: invalid mode is a caller bug, not an
        # observability outage. Coerce to ``hybrid`` so downstream
        # validators still see a well-formed span.
        logger.debug(
            "emit_c0_retrieval: invalid retrieval_mode=%r, coercing to 'hybrid'",
            retrieval_mode,
        )
        retrieval_mode = "hybrid"
    attrs = {
        "retrieval_mode": retrieval_mode,
        "evidence_ids": list(evidence_ids),
        "vector_store_id": vector_store_id,
        "index_version": index_version,
        "query_vec_id": query_vec_id,
        "support_score": support_score,
        "parent_span_id": parent_span_id,
    }
    _append_span(
        adapter,
        name=SPAN_C0_EVIDENCE_CONTRACT,
        kind="retrieval",
        layer=_LAYER_L1,
        component="C0Retriever",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )


# ===========================================================================
# Stage 08 — Prompt Assembly
# ===========================================================================


def emit_prompt_assembly(
    adapter: Any,
    trace_id: str,
    *,
    prompt_envelope_hash: str,
    prompt_hash: str,
    system_template_hash: str,
    task_template_hash: str = "",
    output_schema_hash: str = "",
    evidence_ids: Sequence[str] = (),
    token_budget_total: int = 0,
    token_budget_used: int = 0,
    parent_span_id: str = "",
) -> None:
    """Emit the canonical PA prompt.contract span."""
    attrs = {
        "prompt_envelope_hash": prompt_envelope_hash,
        "prompt_hash": prompt_hash,
        "system_template_hash": system_template_hash,
        "task_template_hash": task_template_hash,
        "output_schema_hash": output_schema_hash,
        "evidence_ids": list(evidence_ids),
        "token_budget_total": token_budget_total,
        "token_budget_used": token_budget_used,
        "parent_span_id": parent_span_id,
    }
    _append_span(
        adapter,
        name=SPAN_PA_PROMPT_CONTRACT,
        kind="assembler",
        layer=_LAYER_L1,
        component="PromptAssembler",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )


# ===========================================================================
# Stage 11 — Response / No Write
# ===========================================================================


def emit_response(
    adapter: Any,
    trace_id: str,
    *,
    response_id: str | None = None,
    final_output_hash: str,
    no_write_marker: bool = True,
    caller_delivery_status: str = "delivered",
    parent_span_id: str = "",
) -> str:
    """Emit Response.emit and Runtime.close_no_write spans (paired).

    Returns the resolved ``response_id``.
    """
    rid = response_id or f"resp-{uuid.uuid4().hex[:12]}"
    base_attrs = {
        "response_id": rid,
        "final_output_hash": final_output_hash,
        "no_write_marker": no_write_marker,
        "caller_delivery_status": caller_delivery_status,
        "parent_span_id": parent_span_id,
    }
    now = _now()
    _append_span(
        adapter,
        name=SPAN_RESPONSE_EMIT,
        kind="response",
        layer=_LAYER_L0,
        component="ResponseEmitter",
        attributes=dict(base_attrs),
        started_at=now,
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )
    close_attrs = dict(base_attrs)
    close_attrs["runtime_closed"] = True
    _append_span(
        adapter,
        name=SPAN_RUNTIME_CLOSE_NO_WRITE,
        kind="response",
        layer=_LAYER_L0,
        component="RuntimeCloser",
        attributes=close_attrs,
        started_at=now + 0.001,
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )
    return rid


# ===========================================================================
# Stage 12 — UWG / L4 Commit
# ===========================================================================


def emit_uwg_commit(
    adapter: Any,
    trace_id: str,
    *,
    commit_request_id: str,
    mutation_type: str,
    proposed_diff_hash: str,
    before_hash: str,
    after_hash: str,
    ledger_hash: str,
    rollback_ref: str = "",
    commit_id: str | None = None,
    audit_receipt_id: str | None = None,
    parent_span_id: str = "",
) -> str:
    """Emit the canonical UWG.commit.append_ledger span."""
    cid = commit_id or f"commit-{uuid.uuid4().hex[:12]}"
    rid = audit_receipt_id or f"audit-{uuid.uuid4().hex[:12]}"
    attrs = {
        "commit_request_id": commit_request_id,
        "mutation_type": mutation_type,
        "proposed_diff_hash": proposed_diff_hash,
        "before_hash": before_hash,
        "after_hash": after_hash,
        "ledger_hash": ledger_hash,
        "rollback_ref": rollback_ref,
        "commit_id": cid,
        "audit_receipt_id": rid,
        "alias_swap_status": "complete",
        "parent_span_id": parent_span_id,
    }
    _append_span(
        adapter,
        name=SPAN_UWG_COMMIT_APPEND_LEDGER,
        kind="commit",
        layer=_LAYER_L4,
        component="UWGCommitter",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )
    return cid


# ===========================================================================
# Stage 13 — L6 Eval / Shadow Evaluation
# ===========================================================================


def emit_l6_eval(
    adapter: Any,
    trace_id: str,
    *,
    eval_bundle_id: str | None = None,
    replay_digest: str = "",
    task_completion_score: float = 0.0,
    groundedness_score: float = 0.0,
    citation_support_score: float = 0.0,
    answer_relevance_score: float = 0.0,
    trajectory_score: float = 0.0,
    determinism_status: str = "deterministic",
    grader_id: str = "",
    parent_span_id: str = "",
) -> str:
    """Emit the canonical L6.metrics.seal span."""
    bid = eval_bundle_id or f"eval-{uuid.uuid4().hex[:12]}"
    attrs = {
        "eval_bundle_id": bid,
        "replay_digest": replay_digest,
        "task_completion_score": task_completion_score,
        "groundedness_score": groundedness_score,
        "citation_support_score": citation_support_score,
        "answer_relevance_score": answer_relevance_score,
        "trajectory_score": trajectory_score,
        "determinism_status": determinism_status,
        "grader_id": grader_id,
        "parent_span_id": parent_span_id,
    }
    _append_span(
        adapter,
        name=SPAN_L6_METRICS_SEAL,
        kind="eval",
        layer=_LAYER_L6,
        component="L6Evaluator",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )
    return bid


# ===========================================================================
# Stage 14 — Meta-Learning / Promotion
# ===========================================================================


def emit_meta_learning(
    adapter: Any,
    trace_id: str,
    *,
    rca_id: str | None = None,
    incident_cluster_id: str = "",
    pattern_id: str = "",
    severity: str = "info",
    confidence_band: str = "medium",
    promotion_candidate_id: str | None = None,
    shadow_replay_result: str = "pending",
    regression_result: str = "pending",
    sme_signoff_status: str = "pending",
    future_run_only: bool = True,
    parent_span_id: str = "",
) -> str:
    """Emit the canonical MetaLearning.promotion.propose span."""
    rid = rca_id or f"rca-{uuid.uuid4().hex[:12]}"
    pcid = promotion_candidate_id or f"prom-{uuid.uuid4().hex[:12]}"
    attrs = {
        # Use both cases — `RCA_id` (doctrine) + `rca_id` (Pythonic alias).
        "RCA_id": rid,
        "rca_id": rid,
        "incident_cluster_id": incident_cluster_id,
        "pattern_id": pattern_id,
        "severity": severity,
        "confidence_band": confidence_band,
        "promotion_candidate_id": pcid,
        "shadow_replay_result": shadow_replay_result,
        "regression_result": regression_result,
        "SME_signoff_status": sme_signoff_status,
        "future_run_only": future_run_only,
        "parent_span_id": parent_span_id,
    }
    _append_span(
        adapter,
        name=SPAN_METALEARNING_PROMOTION_PROPOSE,
        kind="promotion",
        layer=_LAYER_L7,
        component="MetaLearningPromoter",
        attributes=attrs,
        started_at=_now(),
        duration_ms=0.0,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
    )
    return pcid


# ---------------------------------------------------------------------------
# Aggregate registry — used by tests to enumerate Tier 2 emit helpers.
# ---------------------------------------------------------------------------

TIER2_EMITTERS: dict[str, str] = {
    # stage_key -> default span name emitted by helper
    "stage_02_intake": SPAN_INTAKE_STAMP_TRACE,
    "stage_03_L1_reasoning": SPAN_L1_PLAN_DRAFT,
    "stage_04_L0_routing": SPAN_L0_ROUTE_SELECT,
    "stage_05_direct_path": SPAN_L0_DIRECT_PACKAGE,
    "stage_06_L3_orchestration": SPAN_L3_STEP_DISPATCH,
    "stage_07_C0_retrieval": SPAN_C0_EVIDENCE_CONTRACT,
    "stage_08_prompt_assembly": SPAN_PA_PROMPT_CONTRACT,
    "stage_11_response": SPAN_RESPONSE_EMIT,
    "stage_12_uwg_l4_commit": SPAN_UWG_COMMIT_APPEND_LEDGER,
    "stage_13_L6_eval": SPAN_L6_METRICS_SEAL,
    "stage_14_meta_learning": SPAN_METALEARNING_PROMOTION_PROPOSE,
}

ALL_TIER2_SPAN_NAMES: frozenset[str] = frozenset(
    {
        SPAN_C0_RETRIEVAL_PLAN,
        SPAN_C0_QUERY_EMBED,
        SPAN_C0_EVIDENCE_FETCH_DENSE,
        SPAN_C0_EVIDENCE_FETCH_SPARSE,
        SPAN_C0_GRAPH_TRAVERSE,
        SPAN_C0_EVIDENCE_RERANK,
        SPAN_C0_EVIDENCE_CONTRACT,
        SPAN_INTAKE_VALIDATE,
        SPAN_INTAKE_NORMALIZE,
        SPAN_INTAKE_STAMP_TRACE,
        SPAN_L1_INTENT_PARSE,
        SPAN_L1_CONTEXT_PRIORS_LOAD,
        SPAN_L1_PLAN_DRAFT,
        SPAN_L1_PLAN_VALIDATE,
        SPAN_L0_ROUTE_SCORE,
        SPAN_L0_CACHE_CHECK,
        SPAN_L0_ROUTE_SELECT,
        SPAN_L0_ROUTE_CONTRACT,
        SPAN_L0_DIRECT_PACKAGE,
        SPAN_L0_RET_SHORT_CIRCUIT,
        SPAN_L0_SINGLE_STEP_DISPATCH,
        SPAN_L3_WORKFLOW_EXPAND,
        SPAN_L3_WORKFLOW_STATE,
        SPAN_L3_STEP_READY_CHECK,
        SPAN_L3_STEP_DISPATCH,
        SPAN_L3_STEP_MERGE_RESULT,
        SPAN_PA_STATIC_BLOCKS_LOAD,
        SPAN_PA_CONTEXT_SLOT,
        SPAN_PA_TOKEN_BUDGET,
        SPAN_PA_PROMPT_CONTRACT,
        SPAN_RESPONSE_EMIT,
        SPAN_RUNTIME_CLOSE_NO_WRITE,
        SPAN_UWG_COMMIT_VERIFY_AUTHORITY,
        SPAN_UWG_COMMIT_VALIDATE_DIFF,
        SPAN_UWG_COMMIT_APPEND_LEDGER,
        SPAN_L4_ARCHIVE_MATERIALIZE,
        SPAN_L6_TELEMETRY_INGEST,
        SPAN_L6_OUTCOME_EVALUATE,
        SPAN_L6_TRAJECTORY_EVALUATE,
        SPAN_L6_RETRIEVAL_EVALUATE,
        SPAN_L6_REPLAY_VERIFY,
        SPAN_L6_METRICS_SEAL,
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


__all__ = [
    # Span name constants
    "SPAN_C0_RETRIEVAL_PLAN",
    "SPAN_C0_QUERY_EMBED",
    "SPAN_C0_EVIDENCE_FETCH_DENSE",
    "SPAN_C0_EVIDENCE_FETCH_SPARSE",
    "SPAN_C0_GRAPH_TRAVERSE",
    "SPAN_C0_EVIDENCE_RERANK",
    "SPAN_C0_EVIDENCE_CONTRACT",
    "SPAN_INTAKE_VALIDATE",
    "SPAN_INTAKE_NORMALIZE",
    "SPAN_INTAKE_STAMP_TRACE",
    "SPAN_L1_INTENT_PARSE",
    "SPAN_L1_CONTEXT_PRIORS_LOAD",
    "SPAN_L1_PLAN_DRAFT",
    "SPAN_L1_PLAN_VALIDATE",
    "SPAN_L0_ROUTE_SCORE",
    "SPAN_L0_CACHE_CHECK",
    "SPAN_L0_ROUTE_SELECT",
    "SPAN_L0_ROUTE_CONTRACT",
    "SPAN_L0_DIRECT_PACKAGE",
    "SPAN_L0_RET_SHORT_CIRCUIT",
    "SPAN_L0_SINGLE_STEP_DISPATCH",
    "SPAN_L3_WORKFLOW_EXPAND",
    "SPAN_L3_WORKFLOW_STATE",
    "SPAN_L3_STEP_READY_CHECK",
    "SPAN_L3_STEP_DISPATCH",
    "SPAN_L3_STEP_MERGE_RESULT",
    "SPAN_PA_STATIC_BLOCKS_LOAD",
    "SPAN_PA_CONTEXT_SLOT",
    "SPAN_PA_TOKEN_BUDGET",
    "SPAN_PA_PROMPT_CONTRACT",
    "SPAN_RESPONSE_EMIT",
    "SPAN_RUNTIME_CLOSE_NO_WRITE",
    "SPAN_UWG_COMMIT_VERIFY_AUTHORITY",
    "SPAN_UWG_COMMIT_VALIDATE_DIFF",
    "SPAN_UWG_COMMIT_APPEND_LEDGER",
    "SPAN_L4_ARCHIVE_MATERIALIZE",
    "SPAN_L6_TELEMETRY_INGEST",
    "SPAN_L6_OUTCOME_EVALUATE",
    "SPAN_L6_TRAJECTORY_EVALUATE",
    "SPAN_L6_RETRIEVAL_EVALUATE",
    "SPAN_L6_REPLAY_VERIFY",
    "SPAN_L6_METRICS_SEAL",
    "SPAN_METALEARNING_SIGNAL_FUSE",
    "SPAN_METALEARNING_RCA_CREATE",
    "SPAN_METALEARNING_PATTERN_EXTRACT",
    "SPAN_METALEARNING_RULE_DRAFT",
    "SPAN_METALEARNING_SHADOW_REPLAY",
    "SPAN_METALEARNING_PROMOTION_PROPOSE",
    "SPAN_METALEARNING_PROMOTION_APPROVE_OR_REJECT",
    "SPAN_METALEARNING_PROMOTION_COMMIT",
    # Aggregates
    "TIER2_EMITTERS",
    "ALL_TIER2_SPAN_NAMES",
    # Emit functions
    "emit_intake",
    "emit_intake_validate",
    "emit_intake_normalize",
    "emit_l1_reasoning",
    "emit_l0_route_select",
    "emit_direct_path",
    "emit_l3_step",
    "emit_c0_retrieval",
    "emit_prompt_assembly",
    "emit_response",
    "emit_uwg_commit",
    "emit_l6_eval",
    "emit_meta_learning",
]
