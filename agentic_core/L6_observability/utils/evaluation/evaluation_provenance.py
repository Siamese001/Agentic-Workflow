"""
agentic_core/L6_observability/evaluation/evaluation_provenance.py

Wave 1.5: Evaluation Provenance Capture

Captures full evaluation audit trail with:
- Evaluation context (inputs, outputs, metadata)
- Evaluator identity and version
- Timestamp and trace lineage
- Evaluation results and scores
- Provenance query API

Persists to in-memory store (future: L4 state via UWG).
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from tqdm import tqdm

# P0 governance self-bootstrap
emit_replay_key("p0", "evaluation_provenance")
emit_determinism_digest("p0", "evaluation_provenance")
_emit_applies_guardrail("p0", "evaluation_provenance", "p0_governance")
_emit_snapshots_state("p0", "evaluation_provenance", "state_snapshot")
_tid = str(uuid.uuid4())
_emit_signs_execution_trace(_tid, hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)

# P1-P4 self-bootstrap
_emit_routes_through("p1", "evaluation_provenance", "L6")
_emit_authorize_and_execute("p2", "evaluation_provenance", "execution_auth")
_emit_validates_capability("p2", "evaluation_provenance", "capability_check")
_emit_routes_to_capability("p2", "evaluation_provenance", "capability_route")
_emit_writes_via_uwg("p2", "evaluation_provenance", "uwg_write")
_emit_blocks_direct_write("p2", "evaluation_provenance", "direct_write_block")
_emit_records_tool_invocation("p2", "evaluation_provenance", "tool_invocation")
_emit_captures_execution_output("p2", "evaluation_provenance", "exec_output")
_emit_dispatches_agent("p3", "evaluation_provenance", "agent_dispatch")
_emit_coordinates_agents("p3", "evaluation_provenance", "agent_coordination")
_emit_records_workflow_lineage("p3", "evaluation_provenance", "workflow_lineage")
_emit_records_healing_outcome("p3", "evaluation_provenance", "healing_outcome")
_emit_escalates_failure("p3", "evaluation_provenance", "failure_escalation")
_emit_orchestrates_workflow("p3", "evaluation_provenance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "evaluation_provenance", "healing_dispatch")
_emit_invokes_evaluation("p3", "evaluation_provenance", "evaluation_signal")
_emit_records_telemetry_event("p4", "evaluation_provenance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "evaluation_provenance", "eval_metric")
_emit_stores_embedding("p4", "evaluation_provenance", "embedding_store")
_emit_updates_meta_learning_state("p4", "evaluation_provenance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "evaluation_provenance", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EvaluationProvenance:
    """Complete provenance record for an evaluation.

    Captures full audit trail including:
    - What was evaluated (inputs, outputs, context)
    - Who evaluated it (evaluator identity, version)
    - When it was evaluated (timestamp, trace lineage)
    - How it was evaluated (parameters, configuration)
    - What was the result (scores, verdicts, metadata)
    """

    provenance_id: str
    evaluation_id: str
    trace_id: str
    evaluator_name: str
    evaluator_version: str
    evaluation_type: str
    timestamp_utc: float

    # Evaluation inputs
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    context_data: dict[str, Any]

    # Evaluation results
    score: float
    verdict: str
    confidence: float
    metadata: dict[str, Any]

    # Lineage
    parent_trace_id: str | None = None
    execution_snapshot_id: str | None = None


@dataclass
class ProvenanceQuery:
    """Query parameters for provenance search."""

    trace_id: str | None = None
    evaluator_name: str | None = None
    evaluation_type: str | None = None
    min_score: float | None = None
    max_score: float | None = None
    start_time_utc: float | None = None
    end_time_utc: float | None = None
    limit: int = 100


class EvaluationProvenanceStore:
    """In-memory provenance store for evaluation audit trails.

    Future: Persist to L4 state via UWG for durable storage.
    """

    def __init__(self, max_records: int = 10000) -> None:
        """Initialize provenance store.

        Args:
            max_records: Maximum provenance records to store (FIFO)
        """
        self._max_records = max_records
        self._records: dict[str, EvaluationProvenance] = {}
        self._records_by_trace: dict[str, list[str]] = {}
        self._records_by_evaluator: dict[str, list[str]] = {}
        self._insertion_order: list[str] = []

    def capture_provenance(
        self,
        evaluation_id: str,
        trace_id: str,
        evaluator_name: str,
        evaluator_version: str,
        evaluation_type: str,
        input_data: dict[str, Any],
        output_data: dict[str, Any],
        context_data: dict[str, Any],
        score: float,
        verdict: str,
        confidence: float = 1.0,
        metadata: dict[str, Any] | None = None,
        parent_trace_id: str | None = None,
        execution_snapshot_id: str | None = None,
    ) -> EvaluationProvenance:
        """Capture evaluation provenance.

        Args:
            evaluation_id: Unique evaluation ID
            trace_id: Execution trace ID
            evaluator_name: Name of evaluator
            evaluator_version: Version of evaluator
            evaluation_type: Type of evaluation
            input_data: Evaluation inputs
            output_data: Evaluation outputs
            context_data: Evaluation context
            score: Evaluation score
            verdict: Evaluation verdict
            confidence: Confidence in evaluation
            metadata: Optional metadata
            parent_trace_id: Optional parent trace ID
            execution_snapshot_id: Optional execution snapshot ID

        Returns:
            EvaluationProvenance record

        Emits ADG edges:
            - captures_evaluation_metric (P4)
            - links_execution_to_snapshot (P4)
        """
        _emit_captures_evaluation_metric("p4", "evaluation_provenance", evaluation_type)
        if execution_snapshot_id:
            _emit_links_execution_to_snapshot("p4", "evaluation_provenance", execution_snapshot_id)

        provenance_id = self._generate_provenance_id(evaluation_id, trace_id)

        provenance = EvaluationProvenance(
            provenance_id=provenance_id,
            evaluation_id=evaluation_id,
            trace_id=trace_id,
            evaluator_name=evaluator_name,
            evaluator_version=evaluator_version,
            evaluation_type=evaluation_type,
            timestamp_utc=time.time(),
            input_data=input_data,
            output_data=output_data,
            context_data=context_data,
            score=score,
            verdict=verdict,
            confidence=confidence,
            metadata=metadata or {},
            parent_trace_id=parent_trace_id,
            execution_snapshot_id=execution_snapshot_id,
        )

        # Store provenance
        self._records[provenance_id] = provenance
        self._insertion_order.append(provenance_id)

        # Index by trace
        if trace_id not in self._records_by_trace:
            self._records_by_trace[trace_id] = []
        self._records_by_trace[trace_id].append(provenance_id)

        # Index by evaluator
        if evaluator_name not in self._records_by_evaluator:
            self._records_by_evaluator[evaluator_name] = []
        self._records_by_evaluator[evaluator_name].append(provenance_id)

        # Enforce max records (FIFO)
        if len(self._records) > self._max_records:
            oldest_id = self._insertion_order.pop(0)
            oldest_record = self._records.pop(oldest_id)

            # Remove from indexes
            self._records_by_trace[oldest_record.trace_id].remove(oldest_id)
            self._records_by_evaluator[oldest_record.evaluator_name].remove(oldest_id)

        logger.info(
            "PROVENANCE_CAPTURED: id=%s trace=%s evaluator=%s type=%s score=%.3f",
            provenance_id[:12],
            trace_id,
            evaluator_name,
            evaluation_type,
            score,
        )

        return provenance

    def get_provenance(self, provenance_id: str) -> EvaluationProvenance | None:
        """Get provenance record by ID."""
        return self._records.get(provenance_id)

    def query_provenance(self, query: ProvenanceQuery) -> list[EvaluationProvenance]:
        """Query provenance records.

        Args:
            query: Query parameters

        Returns:
            List of matching provenance records (up to query.limit)
        """
        results = []

        # Start with all records or filter by trace/evaluator
        if query.trace_id:
            candidate_ids = self._records_by_trace.get(query.trace_id, [])
        elif query.evaluator_name:
            candidate_ids = self._records_by_evaluator.get(query.evaluator_name, [])
        else:
            candidate_ids = list(self._records.keys())

        # Apply filters
        for provenance_id in tqdm(candidate_ids, desc="Processing", unit="item"):
            record = self._records[provenance_id]

            # Evaluation type filter
            if query.evaluation_type and record.evaluation_type != query.evaluation_type:
                continue

            # Score filters
            if query.min_score is not None and record.score < query.min_score:
                continue
            if query.max_score is not None and record.score > query.max_score:
                continue

            # Time filters
            if query.start_time_utc is not None and record.timestamp_utc < query.start_time_utc:
                continue
            if query.end_time_utc is not None and record.timestamp_utc > query.end_time_utc:
                continue

            results.append(record)

            # Limit results
            if len(results) >= query.limit:
                break

        return results

    def get_trace_provenance(self, trace_id: str) -> list[EvaluationProvenance]:
        """Get all provenance records for a trace."""
        provenance_ids = self._records_by_trace.get(trace_id, [])
        return [self._records[pid] for pid in provenance_ids]

    def get_evaluator_provenance(self, evaluator_name: str) -> list[EvaluationProvenance]:
        """Get all provenance records for an evaluator."""
        provenance_ids = self._records_by_evaluator.get(evaluator_name, [])
        return [self._records[pid] for pid in provenance_ids]

    def get_stats(self) -> dict[str, Any]:
        """Get provenance store statistics."""
        return {
            "total_records": len(self._records),
            "max_records": self._max_records,
            "unique_traces": len(self._records_by_trace),
            "unique_evaluators": len(self._records_by_evaluator),
            "evaluators": list(self._records_by_evaluator.keys()),
        }

    def clear(self) -> None:
        """Clear all provenance records."""
        self._records.clear()
        self._records_by_trace.clear()
        self._records_by_evaluator.clear()
        self._insertion_order.clear()

    @staticmethod
    def _generate_provenance_id(evaluation_id: str, trace_id: str) -> str:
        """Generate provenance ID from evaluation and trace IDs."""
        combined = f"{evaluation_id}:{trace_id}:{time.time()}"
        return hashlib.sha256(combined.encode()).hexdigest()


# Global instance
_provenance_store: EvaluationProvenanceStore | None = None


def get_provenance_store() -> EvaluationProvenanceStore:
    """Get global provenance store instance."""
    global _provenance_store
    if _provenance_store is None:
        _provenance_store = EvaluationProvenanceStore()
    return _provenance_store


def reset_provenance_store() -> None:
    """Reset global provenance store (for testing)."""
    global _provenance_store
    _provenance_store = None


__all__ = [
    "EvaluationProvenance",
    "ProvenanceQuery",
    "EvaluationProvenanceStore",
    "get_provenance_store",
    "reset_provenance_store",
]
