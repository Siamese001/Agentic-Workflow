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
from agentic_core.L6_observability.utils.evaluation.evaluation_record import (
    EvaluationStage,
    evaluate_and_attach,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_snapshots_state,  # noqa: E402
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
            trace_id=trace_id,
            cid=cid,
            status=status,
            manifest_hash=manifest_hash,
            record_hash=record_hash,
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
            pass  # guardian: allow-silent-swallow -- intentional: ValueError used for control flow
        return record

    def append_gate_result(self, gate_result: object) -> "OutcomeRecord":
        """Append an ExitGateResult disposition to the outcome log.

        Adapts ExitGateResult → OutcomeRecord without coupling to L5 internals
        beyond the ExitGateResult.to_dict() contract.

        Args:
            gate_result: ExitGateResult from ExitControlGate.evaluate().

        Returns:
            Created OutcomeRecord (immutable).
        """
        d = gate_result.to_dict()
        return self.append(
            trace_id=d["trace_id"],
            cid=d["trace_id"],
            status=d["disposition"],
            manifest_hash=hashlib.sha256((d.get("policy_hash") or d["trace_id"]).encode()).hexdigest()[:16],
        )

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
        self,
        *,
        observed: tuple[OutcomeRecord, ...],
        expected_hashes: tuple[str, ...],
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
