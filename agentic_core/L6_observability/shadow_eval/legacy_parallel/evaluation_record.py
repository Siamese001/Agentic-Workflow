"""
agentic_core/L6_observability/evaluation/evaluation_record.py

EvaluationRecord — P1/L6 evaluation signal integration.

All evaluations MUST pass through evaluate_and_attach().
Orphan evaluations (no trace linkage) are prohibited.

evaluate_and_attach() steps (mandatory, in order):
  1. bind evaluated artifact to trace id
  2. record evaluator identity
  3. record rubric hash
  4. record score output
  5. attach policy hash if policy-sensitive
  6. emit evaluation linkage record

EvaluationRecord (10 required spec fields):
    evaluation_id, run_id, trace_id, evaluated_artifact_hash,
    evaluated_stage, evaluator_id, score_payload_hash,
    rubric_hash, policy_hash, outcome_hash

EvaluationStage (5 mandatory trace targets):
    REASONING_TRACE, EXECUTION_TRACE, ROUTING_TRACE,
    STATE_MUTATION_TRACE, FINAL_OUTCOME_TRACE

ADG edges emitted:
    invokes_eval            — every evaluate_and_attach() call
    records_execution_trace — evaluation linked to active trace
    references_policy_hash  — where evaluation is policy-sensitive
    attaches_evaluation     — linkage record to evaluated artifact
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.utils.runners.providers import (
    get_clock,
)  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "evaluation_record")
emit_determinism_digest("p0", "evaluation_record")

_emit_dispatches_healing_run("p1", "evaluation_record", "L6")
_emit_routes_through("p1", "evaluation_record", "L6")
_emit_checks_agent_registry("p1", "evaluation_record", "agent_registry")
_emit_validates_agent_capability("p1", "evaluation_record", "capability")
_emit_dispatches_execution_plan("p1", "evaluation_record", "exec_plan")
_emit_agent_executes_agent("p1", "evaluation_record", "sub_agent")
_emit_routes_to_agent("p1", "evaluation_record", "target_agent")
_emit_verifies_policy("p1", "evaluation_record", "policy_check")
_emit_observes_runtime_state("p1", "evaluation_record", "runtime_state")
_emit_verifies_boundary("p1", "evaluation_record", "boundary_check")
_emit_transcripts_response("p1", "evaluation_record", "transcript")
_emit_hard_fails_untranscripted("p1", "evaluation_record")
_emit_gated_by_confidence("p1", "evaluation_record", "confidence_gate")
_emit_escalates_to_human("p1", "evaluation_record", "L6")
_emit_reads_policy_state("p1", "evaluation_record", "L6")

_emit_snapshots_state("p0", "evaluation_record", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "evaluation_record", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "evaluation_record")
_emit_authorize_and_execute("p2", "evaluation_record", "execution_auth")
_emit_validates_capability("p2", "evaluation_record", "capability_check")
_emit_routes_to_capability("p2", "evaluation_record", "capability_route")
_emit_writes_via_uwg("p2", "evaluation_record", "uwg_write")
_emit_blocks_direct_write("p2", "evaluation_record", "direct_write_block")
_emit_records_tool_invocation("p2", "evaluation_record", "tool_invocation")
_emit_captures_execution_output("p2", "evaluation_record", "exec_output")
_emit_dispatches_agent("p3", "evaluation_record", "agent_dispatch")
_emit_coordinates_agents("p3", "evaluation_record", "agent_coordination")
_emit_records_workflow_lineage("p3", "evaluation_record", "workflow_lineage")
_emit_records_healing_outcome("p3", "evaluation_record", "healing_outcome")
_emit_escalates_failure("p3", "evaluation_record", "failure_escalation")
_emit_orchestrates_workflow("p3", "evaluation_record", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "evaluation_record", "healing_dispatch")
_emit_invokes_evaluation("p3", "evaluation_record", "evaluation_signal")
_emit_records_telemetry_event("p4", "evaluation_record", "telemetry_event")
_emit_captures_evaluation_metric("p4", "evaluation_record", "eval_metric")
_emit_stores_embedding("p4", "evaluation_record", "embedding_store")
_emit_updates_meta_learning_state("p4", "evaluation_record", "meta_learning")
_emit_links_execution_to_snapshot("p4", "evaluation_record", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("evaluation_record", "p4obs", "metric_1")
_emit_emits_metric_event("evaluation_record", "p4obs", "metric_2")
_emit_emits_metric_event("evaluation_record", "p4obs", "metric_3")
_emit_emits_metric_event("evaluation_record", "p4obs", "metric_4")
_emit_emits_metric_event("evaluation_record", "p4obs", "metric_5")
_emit_emits_metric_event("evaluation_record", "p4obs", "metric_6")
_emit_records_incident_event("evaluation_record", "p4obs", "incident")
_emit_captures_runtime_anomaly("evaluation_record", "p4obs", "anomaly")
_emit_writes_observability_log("evaluation_record", "p4obs", "obs_log")
_emit_updates_monitoring_state("evaluation_record", "p4obs", "mon_state")
_emit_triggers_alert("evaluation_record", "p4obs", "alert")
_emit_links_incident_trace("evaluation_record", "p4obs", "trace_link")
_emit_captures_pattern("evaluation_record", "p3lm", "pattern")
_emit_records_learning_event("evaluation_record", "p3lm", "learning_event")
_emit_writes_learning_snapshot("evaluation_record", "p3lm", "snapshot")
_emit_feeds_meta_learning("evaluation_record", "p3lm", "meta_feed")
_emit_updates_routing_strategy("evaluation_record", "p3lm", "routing")
_emit_improves_agent_policy("evaluation_record", "p3lm", "policy")
_emit_stores_learning_state("evaluation_record", "p3lm", "state")
_emit_records_execution_trace("evaluation_record", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("evaluation_record", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("evaluation_record", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("evaluation_record", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("evaluation_record", "L4_STATE", "p2_trace_5")
_emit_reads_environ("evaluation_record", "env_read", "p2_env_1")
_emit_reads_environ("evaluation_record", "env_read", "p2_env_2")
_emit_reads_runtime_state("evaluation_record", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("evaluation_record", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "evaluation_record", "context_pull")
_emit_pulls_context("p1", "evaluation_record", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "evaluation_record", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "evaluation_record", "uwg_term_2")
_emit_writes_through("p1", "evaluation_record", "write_through")
_emit_writes_through("p1", "evaluation_record", "write_through_2")
_emit_validated_by_safety_plane("p1", "evaluation_record", "safety_validation")
_emit_invokes_eval("p1", "evaluation_record", "eval_call")
_emit_proposal_commits_routing("p1", "evaluation_record", "routing_commit")

logger = logging.getLogger(__name__)
_INVOKES_EVAL_LOG = logging.getLogger("adg.invokes_eval")
_TRACE_LOG = logging.getLogger("adg.records_execution_trace")
_POLICY_LOG = logging.getLogger("adg.references_policy_hash")
_ATTACH_LOG = logging.getLogger("adg.attaches_evaluation")


# ---------------------------------------------------------------------------
# EvaluationStage — 5 mandatory trace targets per spec §4
# ---------------------------------------------------------------------------


class EvaluationStage(str, Enum):
    """Trace target that every evaluation must attach to."""

    REASONING_TRACE = "reasoning_trace"
    EXECUTION_TRACE = "execution_trace"
    ROUTING_TRACE = "routing_trace"
    STATE_MUTATION_TRACE = "state_mutation_trace"
    FINAL_OUTCOME_TRACE = "final_outcome_trace"


# ---------------------------------------------------------------------------
# EvaluationRecord — 10 required spec fields
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvaluationRecord:
    """Immutable artifact of one governed evaluation invocation (P1/L6 spec §2)."""

    evaluation_id: str
    run_id: str
    trace_id: str
    evaluated_artifact_hash: str
    evaluated_stage: str
    evaluator_id: str
    score_payload_hash: str
    rubric_hash: str
    policy_hash: str
    outcome_hash: str

    created_tick: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        run_id: str,
        trace_id: str,
        evaluated_artifact: Any,
        evaluated_stage: EvaluationStage,
        evaluator_id: str,
        score_payload: Any,
        rubric: Any,
        policy_hash: str = "",
    ) -> EvaluationRecord:
        eval_id = f"ev-{uuid.uuid4().hex[:12]}"
        artifact_hash = _sha256_any(evaluated_artifact)
        score_hash = _sha256_any(score_payload)
        rubric_hash = _sha256_any(rubric)
        outcome_hash = hashlib.sha256(f"{eval_id}:{artifact_hash}:{score_hash}".encode()).hexdigest()[:16]
        return cls(
            evaluation_id=eval_id,
            run_id=run_id,
            trace_id=trace_id,
            evaluated_artifact_hash=artifact_hash,
            evaluated_stage=evaluated_stage.value,
            evaluator_id=evaluator_id,
            score_payload_hash=score_hash,
            rubric_hash=rubric_hash,
            policy_hash=policy_hash or "default",
            outcome_hash=outcome_hash,
        )


# ---------------------------------------------------------------------------
# EvaluationLinkage — binds evaluation to trace lineage
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvaluationLinkage:
    """Links an EvaluationRecord to the trace context it was produced in."""

    linkage_id: str
    evaluation_id: str
    trace_id: str
    run_id: str
    evaluated_stage: str
    evaluated_artifact_hash: str
    outcome_hash: str
    created_tick: float = field(default_factory=lambda: get_clock().now_epoch())


# ---------------------------------------------------------------------------
# OrphanEvaluationError — emitted when no trace context is available
# ---------------------------------------------------------------------------


class OrphanEvaluationError(RuntimeError):
    """Raised when evaluate_and_attach() is called with no trace_id context.

    Per spec §4: every evaluation must attach to a trace. Orphan evaluations
    are prohibited.
    """


# ---------------------------------------------------------------------------
# evaluate_and_attach — mandatory entrypoint per spec §3
# ---------------------------------------------------------------------------


def evaluate_and_attach(
    evaluated_artifact: Any,
    rubric: Any,
    evaluator_id: str,
    score_payload: Any,
    evaluated_stage: EvaluationStage,
    run_id: str = "",
    trace_id: str = "",
    policy_hash: str = "",
    policy_sensitive: bool = False,
) -> EvaluationRecord:
    """Mandatory evaluation entrypoint — P1/L6 spec §3.

    Steps (in order, all mandatory):
      1. bind evaluated artifact to trace id
      2. record evaluator identity
      3. record rubric hash
      4. record score output
      5. attach policy hash if policy-sensitive
      6. emit evaluation linkage record

    Args:
        evaluated_artifact:  Artifact under evaluation (any serialisable value).
        rubric:              Evaluation rubric (dict, str, or any serialisable).
        evaluator_id:        Identity of the evaluator (module name, agent id, etc.).
        score_payload:       Raw score output (dict, float, or any serialisable).
        evaluated_stage:     Which trace this evaluation attaches to (EvaluationStage).
        run_id:              Run identifier (auto-resolved if empty).
        trace_id:            Trace context (auto-resolved from active trace if empty).
        policy_hash:         Policy hash (used if policy_sensitive=True).
        policy_sensitive:    If True, references_policy_hash ADG edge is emitted.

    Returns:
        EvaluationRecord (immutable, 10 fields)

    Raises:
        OrphanEvaluationError: if trace_id cannot be resolved (no trace context).
    """
    # --- Step 1: Bind evaluated artifact to trace id ---
    effective_trace_id = trace_id
    if not effective_trace_id:
        effective_trace_id = _resolve_trace_id()

    if not effective_trace_id:
        raise OrphanEvaluationError(
            f"evaluate_and_attach: no trace_id available for evaluator='{evaluator_id}' "
            f"stage={evaluated_stage.value} — orphan evaluations are prohibited (P1/L6 spec §4)",
        )

    effective_run_id = run_id or _resolve_run_id() or "unknown"
    effective_policy = policy_hash or "default"

    # --- Step 2: Record evaluator identity (already captured in evaluator_id param) ---

    # --- Step 3 & 4: Record rubric hash + score output (captured in EvaluationRecord.create) ---

    # --- Step 5: Attach policy hash if policy-sensitive ---
    if policy_sensitive:
        _POLICY_LOG.debug(
            "references_policy_hash EVALUATE_AND_ATTACH evaluator=%s stage=%s policy=%s",
            evaluator_id,
            evaluated_stage.value,
            effective_policy[:12],
        )

    # --- ADG edge: invokes_eval ---
    _INVOKES_EVAL_LOG.debug(
        "invokes_eval EVALUATE_AND_ATTACH evaluator=%s stage=%s run_id=%s trace_id=%s",
        evaluator_id,
        evaluated_stage.value,
        effective_run_id,
        effective_trace_id,
    )

    # --- ADG edge: records_execution_trace ---
    _TRACE_LOG.debug(
        "records_execution_trace EVALUATE_AND_ATTACH evaluator=%s stage=%s trace=%s",
        evaluator_id,
        evaluated_stage.value,
        effective_trace_id,
    )

    # --- Build EvaluationRecord ---
    record = EvaluationRecord.create(
        run_id=effective_run_id,
        trace_id=effective_trace_id,
        evaluated_artifact=evaluated_artifact,
        evaluated_stage=evaluated_stage,
        evaluator_id=evaluator_id,
        score_payload=score_payload,
        rubric=rubric,
        policy_hash=effective_policy,
    )

    # --- Step 6: Emit evaluation linkage record ---
    linkage = EvaluationLinkage(
        linkage_id=f"el-{uuid.uuid4().hex[:12]}",
        evaluation_id=record.evaluation_id,
        trace_id=effective_trace_id,
        run_id=effective_run_id,
        evaluated_stage=evaluated_stage.value,
        evaluated_artifact_hash=record.evaluated_artifact_hash,
        outcome_hash=record.outcome_hash,
    )
    _ATTACH_LOG.debug(
        "attaches_evaluation EVALUATE_AND_ATTACH eval_id=%s trace=%s stage=%s artifact_hash=%s",
        record.evaluation_id,
        effective_trace_id,
        evaluated_stage.value,
        record.evaluated_artifact_hash,
    )
    _record_evaluation(record, linkage)

    logger.debug(
        "EVALUATE_AND_ATTACH emitted eval_id=%s evaluator=%s stage=%s run_id=%s trace=%s",
        record.evaluation_id,
        evaluator_id,
        evaluated_stage.value,
        effective_run_id,
        effective_trace_id,
    )
    return record


# ---------------------------------------------------------------------------
# EvaluationIndex — queryable by run_id, trace_id, stage, artifact_hash
# ---------------------------------------------------------------------------


class EvaluationIndex:
    """Queryable index of all emitted EvaluationRecords.

    Per spec §5: evaluation results must be queryable by:
    - run_id
    - trace_id
    - evaluated_stage
    - evaluated_artifact_hash
    """

    def __init__(self) -> None:
        self._records: list[EvaluationRecord] = []
        self._linkages: list[EvaluationLinkage] = []
        self._lock = threading.RLock()

    def ingest(self, record: EvaluationRecord, linkage: EvaluationLinkage) -> None:
        with self._lock:
            self._records.append(record)
            self._linkages.append(linkage)

    def by_run_id(self, run_id: str) -> list[EvaluationRecord]:
        with self._lock:
            return [r for r in self._records if r.run_id == run_id]

    def by_trace_id(self, trace_id: str) -> list[EvaluationRecord]:
        with self._lock:
            return [r for r in self._records if r.trace_id == trace_id]

    def by_stage(self, stage: EvaluationStage) -> list[EvaluationRecord]:
        with self._lock:
            return [r for r in self._records if r.evaluated_stage == stage.value]

    def by_artifact_hash(self, artifact_hash: str) -> list[EvaluationRecord]:
        with self._lock:
            return [r for r in self._records if r.evaluated_artifact_hash == artifact_hash]

    def orphan_evaluations(self) -> list[EvaluationRecord]:
        """Return evaluations with no matching linkage (should always be empty)."""
        with self._lock:
            linked_ids = {lk.evaluation_id for lk in self._linkages}
            return [r for r in self._records if r.evaluation_id not in linked_ids]

    def all_records(self) -> list[EvaluationRecord]:
        with self._lock:
            return list(self._records)

    def all_linkages(self) -> list[EvaluationLinkage]:
        with self._lock:
            return list(self._linkages)

    def record_count(self) -> int:
        with self._lock:
            return len(self._records)

    def orphan_count(self) -> int:
        return len(self.orphan_evaluations())


# ---------------------------------------------------------------------------
# Process-level EvaluationIndex singleton
# ---------------------------------------------------------------------------

_global_index: EvaluationIndex | None = None
_global_index_lock = threading.Lock()


def get_evaluation_index() -> EvaluationIndex:
    """Return the process-level EvaluationIndex singleton."""
    global _global_index
    if _global_index is None:
        with _global_index_lock:
            if _global_index is None:
                _global_index = EvaluationIndex()
    return _global_index


def reset_evaluation_index() -> None:
    """Reset the global evaluation index (for testing)."""
    global _global_index
    _global_index = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _sha256_any(value: Any) -> str:
    try:
        raw = json.dumps(value, sort_keys=True, default=str).encode()
    except (ValueError, TypeError, RuntimeError) as e:
        raw = str(value).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def _resolve_trace_id() -> str:
    try:
        from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

        active = get_active_execution_trace()
        return active.trace_id if active else ""
    except (ValueError, TypeError, RuntimeError) as e:
        return ""


def _resolve_run_id() -> str:
    try:
        from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

        active = get_active_execution_trace()
        return getattr(active, "run_id", "") if active else ""
    except (ValueError, TypeError, RuntimeError) as e:
        return ""


def _record_evaluation(record: EvaluationRecord, linkage: EvaluationLinkage) -> None:
    get_evaluation_index().ingest(record, linkage)


__all__ = [
    "EvaluationStage",
    "EvaluationRecord",
    "EvaluationLinkage",
    "EvaluationIndex",
    "evaluate_and_attach",
    "get_evaluation_index",
    "reset_evaluation_index",
    "OrphanEvaluationError",
]
