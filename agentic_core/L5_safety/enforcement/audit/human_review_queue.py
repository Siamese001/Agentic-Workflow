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
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
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
