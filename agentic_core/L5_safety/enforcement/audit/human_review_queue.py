"""Gate C5: HumanReviewQueue — stub for human-enqueued AI verdicts.

Verdicts with confidence < 0.7 are placed here and blocked from routing
until a human reviewer approves or rejects them.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

logger = logging.getLogger(__name__)


@dataclass
class PendingVerdict:
    """A verdict awaiting human review."""

    verdict_id: str
    component: str
    trace_id: str
    confidence: float
    verdict: str
    input_hash: str
    reviewed: bool = False
    approved: bool = False
    reviewer_notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class HumanReviewQueue:
    """Thread-safe queue for AI verdicts requiring human review.

    Verdicts are blocked from routing until `approve()` or `reject()` is called.
    """

    def __init__(self) -> None:
        self._queue: dict[str, PendingVerdict] = {}
        self._lock = threading.Lock()

    def enqueue(self, verdict: PendingVerdict) -> None:
        """Add a verdict to the review queue."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "HumanReviewQueue.enqueue")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HumanReviewQueue.enqueue".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        with self._lock:
            self._queue[verdict.verdict_id] = verdict
        logger.info(
            "HumanReviewQueue: enqueued verdict_id=%s component=%s confidence=%.2f",
            verdict.verdict_id,
            verdict.component,
            verdict.confidence,
        )

    def approve(self, verdict_id: str, reviewer_notes: str = "") -> bool:
        """Mark a verdict as approved. Returns True if found."""
        with self._lock:
            v = self._queue.get(verdict_id)
            if v is None:
                return False
            v.reviewed = True
            v.approved = True
            v.reviewer_notes = reviewer_notes
        logger.info("HumanReviewQueue: approved verdict_id=%s", verdict_id)
        return True

    def reject(self, verdict_id: str, reviewer_notes: str = "") -> bool:
        """Mark a verdict as rejected. Returns True if found."""
        with self._lock:
            v = self._queue.get(verdict_id)
            if v is None:
                return False
            v.reviewed = True
            v.approved = False
            v.reviewer_notes = reviewer_notes
        logger.info("HumanReviewQueue: rejected verdict_id=%s", verdict_id)
        return True

    def is_approved(self, verdict_id: str) -> bool:
        """Return True only if the verdict has been reviewed and approved."""
        with self._lock:
            v = self._queue.get(verdict_id)
            return v is not None and v.reviewed and v.approved

    def is_blocked(self, verdict_id: str) -> bool:
        """Return True if the verdict exists and has not yet been reviewed."""
        with self._lock:
            v = self._queue.get(verdict_id)
            return v is not None and (not v.reviewed)

    def pending_count(self) -> int:
        """Return number of unreviewed verdicts."""
        with self._lock:
            return sum(1 for v in self._queue.values() if not v.reviewed)

    def all_pending(self) -> list[PendingVerdict]:
        """Return all unreviewed verdicts."""
        with self._lock:
            return [v for v in self._queue.values() if not v.reviewed]

    def size(self) -> int:
        with self._lock:
            return len(self._queue)


_GLOBAL_REVIEW_QUEUE: HumanReviewQueue | None = None


def get_review_queue() -> HumanReviewQueue:
    """Return the module-level singleton review queue."""
    global _GLOBAL_REVIEW_QUEUE
    if _GLOBAL_REVIEW_QUEUE is None:
        _GLOBAL_REVIEW_QUEUE = HumanReviewQueue()
    return _GLOBAL_REVIEW_QUEUE


__all__ = ["HumanReviewQueue", "PendingVerdict", "get_review_queue"]
