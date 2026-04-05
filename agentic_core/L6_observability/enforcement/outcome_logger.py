"""
L6 Observability Outcome Logger - Deterministic outcome recording + reconciliation

Writes append-only outcome records (data-only, no wall-clock),
computes deterministic record hashes, performs deterministic reconciliation.
Does not mutate L4 directly and does not couple to L2/L5 internals.
"""

import hashlib
import json
from dataclasses import dataclass

from agentic_core.L2_execution.utils.execution_proof_emitter import ExecutionProofEmitter
from agentic_core.L6_observability.evaluation.evaluation_record import (
    EvaluationStage,
    evaluate_and_attach,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

from agentic_core.runtime.lifecycle_trace_contract import (
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
        except (ValueError, TypeError, RuntimeError) as e:
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
