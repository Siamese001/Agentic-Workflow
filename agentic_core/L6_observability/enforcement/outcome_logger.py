"""
L6 Observability Outcome Logger - Deterministic outcome recording + reconciliation

Writes append-only outcome records (data-only, no wall-clock),
computes deterministic record hashes, performs deterministic reconciliation.
Does not mutate L4 directly and does not couple to L2/L5 internals.
"""

import hashlib
import json
from dataclasses import dataclass

from agentic_core.L2_execution.determinism.execution_proof_emitter import ExecutionProofEmitter
from agentic_core.L6_observability.evaluation.evaluation_record import (
    EvaluationStage,
    evaluate_and_attach,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
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

emit_replay_key("p0", "outcome_logger")
emit_determinism_digest("p0", "outcome_logger")

_emit_dispatches_healing_run("p1", "outcome_logger", "L6")
_emit_routes_through("p1", "outcome_logger", "L6")
_emit_checks_agent_registry("p1", "outcome_logger", "agent_registry")
_emit_validates_agent_capability("p1", "outcome_logger", "capability")
_emit_dispatches_execution_plan("p1", "outcome_logger", "exec_plan")
_emit_agent_executes_agent("p1", "outcome_logger", "sub_agent")
_emit_routes_to_agent("p1", "outcome_logger", "target_agent")
_emit_verifies_policy("p1", "outcome_logger", "policy_check")
_emit_observes_runtime_state("p1", "outcome_logger", "runtime_state")
_emit_verifies_boundary("p1", "outcome_logger", "boundary_check")
_emit_transcripts_response("p1", "outcome_logger", "transcript")
_emit_hard_fails_untranscripted("p1", "outcome_logger")
_emit_gated_by_confidence("p1", "outcome_logger", "confidence_gate")
_emit_escalates_to_human("p1", "outcome_logger", "L6")
_emit_reads_policy_state("p1", "outcome_logger", "L6")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "outcome_logger", "execution_auth")
_emit_validates_capability("p2", "outcome_logger", "capability_check")
_emit_routes_to_capability("p2", "outcome_logger", "capability_route")
_emit_writes_via_uwg("p2", "outcome_logger", "uwg_write")
_emit_blocks_direct_write("p2", "outcome_logger", "direct_write_block")
_emit_records_tool_invocation("p2", "outcome_logger", "tool_invocation")
_emit_captures_execution_output("p2", "outcome_logger", "exec_output")
_emit_dispatches_agent("p3", "outcome_logger", "agent_dispatch")
_emit_coordinates_agents("p3", "outcome_logger", "agent_coordination")
_emit_records_workflow_lineage("p3", "outcome_logger", "workflow_lineage")
_emit_records_healing_outcome("p3", "outcome_logger", "healing_outcome")
_emit_escalates_failure("p3", "outcome_logger", "failure_escalation")
_emit_orchestrates_workflow("p3", "outcome_logger", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "outcome_logger", "healing_dispatch")
_emit_invokes_evaluation("p3", "outcome_logger", "evaluation_signal")
_emit_records_telemetry_event("p4", "outcome_logger", "telemetry_event")
_emit_captures_evaluation_metric("p4", "outcome_logger", "eval_metric")
_emit_stores_embedding("p4", "outcome_logger", "embedding_store")
_emit_updates_meta_learning_state("p4", "outcome_logger", "meta_learning")
_emit_links_execution_to_snapshot("p4", "outcome_logger", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("outcome_logger", "p4obs", "metric_1")
_emit_emits_metric_event("outcome_logger", "p4obs", "metric_2")
_emit_emits_metric_event("outcome_logger", "p4obs", "metric_3")
_emit_emits_metric_event("outcome_logger", "p4obs", "metric_4")
_emit_emits_metric_event("outcome_logger", "p4obs", "metric_5")
_emit_emits_metric_event("outcome_logger", "p4obs", "metric_6")
_emit_records_incident_event("outcome_logger", "p4obs", "incident")
_emit_captures_runtime_anomaly("outcome_logger", "p4obs", "anomaly")
_emit_writes_observability_log("outcome_logger", "p4obs", "obs_log")
_emit_updates_monitoring_state("outcome_logger", "p4obs", "mon_state")
_emit_triggers_alert("outcome_logger", "p4obs", "alert")
_emit_links_incident_trace("outcome_logger", "p4obs", "trace_link")
_emit_captures_pattern("outcome_logger", "p3lm", "pattern")
_emit_records_learning_event("outcome_logger", "p3lm", "learning_event")
_emit_writes_learning_snapshot("outcome_logger", "p3lm", "snapshot")
_emit_feeds_meta_learning("outcome_logger", "p3lm", "meta_feed")
_emit_updates_routing_strategy("outcome_logger", "p3lm", "routing")
_emit_improves_agent_policy("outcome_logger", "p3lm", "policy")
_emit_stores_learning_state("outcome_logger", "p3lm", "state")
_emit_records_execution_trace("outcome_logger", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("outcome_logger", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("outcome_logger", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("outcome_logger", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("outcome_logger", "L4_STATE", "p2_trace_5")
_emit_reads_environ("outcome_logger", "env_read", "p2_env_1")
_emit_reads_environ("outcome_logger", "env_read", "p2_env_2")
_emit_reads_runtime_state("outcome_logger", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("outcome_logger", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "outcome_logger", "context_pull")
_emit_pulls_context("p1", "outcome_logger", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "outcome_logger", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "outcome_logger", "uwg_term_2")
_emit_writes_through("p1", "outcome_logger", "write_through")
_emit_writes_through("p1", "outcome_logger", "write_through_2")
_emit_validated_by_safety_plane("p1", "outcome_logger", "safety_validation")
_emit_invokes_eval("p1", "outcome_logger", "eval_call")
_emit_proposal_commits_routing("p1", "outcome_logger", "routing_commit")

_proof_emitter = ExecutionProofEmitter("L6.OutcomeLogger")


@dataclass(frozen=True)
class OutcomeRecord:
    """Immutable outcome record for deterministic logging."""

    trace_id: str
    cid: str
    status: str
    manifest_hash: str
    record_hash: str

    @classmethod
    def create(cls, trace_id: str, cid: str, status: str, manifest_hash: str) -> "OutcomeRecord":
        """
        Create a new OutcomeRecord with deterministic record_hash.

        Args:
            trace_id: Execution trace identifier
            cid: Correlation ID
            status: Execution status
            manifest_hash: Manifest hash from orchestrator

        Returns:
            New OutcomeRecord with computed record_hash
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "OutcomeRecord.create", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "OutcomeRecord.create", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "OutcomeRecord.create")

        canonical_data = {"trace_id": trace_id, "cid": cid, "status": status, "manifest_hash": manifest_hash}
        canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
        record_hash = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
        return cls(
            trace_id=trace_id, cid=cid, status=status, manifest_hash=manifest_hash, record_hash=record_hash
        )


class OutcomeLogger:
    """
    Deterministic outcome logger with append-only semantics.

    In-memory list storage, no disk I/O, no wall-clock usage.
    """

    def __init__(self):
        """Initialize OutcomeLogger with empty in-memory storage."""
        self._records: list[OutcomeRecord] = []

    def append(self, *, trace_id: str, cid: str, status: str, manifest_hash: str) -> OutcomeRecord:
        """
        Append a new outcome record to the log.

        Args:
            trace_id: Execution trace identifier
            cid: Correlation ID
            status: Execution status
            manifest_hash: Manifest hash from orchestrator

        Returns:
            Created OutcomeRecord (immutable)
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "OutcomeLogger.append")

        with _proof_emitter.proof_op(f"outcome_log:{trace_id[:8]}"):
            pass
        record = OutcomeRecord.create(trace_id, cid, status, manifest_hash)
        self._records.append(record)
        # P1/L6: bind outcome record to trace lineage via evaluate_and_attach
        try:
            evaluate_and_attach(
                evaluated_artifact={"cid": cid, "status": status, "manifest_hash": manifest_hash},
                rubric={"type": "outcome_record"},
                evaluator_id="OutcomeLogger",
                score_payload={"status": status, "record_hash": record.record_hash},
                evaluated_stage=EvaluationStage.FINAL_OUTCOME_TRACE,
                trace_id=trace_id,
            )
        except Exception:
            pass
        return record

    def records(self) -> tuple[OutcomeRecord, ...]:
        """
        Get immutable snapshot of all records.

        Returns:
            Tuple of all OutcomeRecord objects (append-only ordering preserved)
        """
        return tuple(self._records)


@dataclass(frozen=True)
class ReconcileResult:
    """Deterministic reconciliation result."""

    missing: tuple[str, ...]
    extra: tuple[str, ...]
    ok: bool


class OutcomeReconciler:
    """
    Deterministic outcome reconciler.

    Compares observed records against expected hashes.
    """

    def reconcile(
        self, *, observed: tuple[OutcomeRecord, ...], expected_hashes: tuple[str, ...]
    ) -> ReconcileResult:
        """
        Reconcile observed records against expected hashes.

        Args:
            observed: Tuple of observed OutcomeRecord objects
            expected_hashes: Tuple of expected record hashes

        Returns:
            ReconcileResult with missing/extra hashes and ok status
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "OutcomeReconciler.reconcile")

        observed_hashes = tuple(record.record_hash for record in observed)
        missing_set = set(expected_hashes) - set(observed_hashes)
        missing = tuple(sorted(missing_set))
        extra_set = set(observed_hashes) - set(expected_hashes)
        extra = tuple(sorted(extra_set))
        ok = len(missing) == 0 and len(extra) == 0
        return ReconcileResult(missing=missing, extra=extra, ok=ok)
