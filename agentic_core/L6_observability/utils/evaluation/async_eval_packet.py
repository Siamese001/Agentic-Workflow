"""
agentic_core/L6_observability/utils/evaluation/async_eval_packet.py

Async eval packet — normalized BUS T + exit-gate join packet for L6 shadow evaluation.

The join seam: ``evaluate_and_emit()`` in ``evidence_eval_bridge.py`` has simultaneous
access to (gate_result, metrics, weak_support_disposition, run_id).
``ingest_eval_packet()`` captures all three at that callsite without durable writes or
live-run mutation.

Future-run only.  No L4 writes.  No UWG bypass.  No new packages.
"""

from __future__ import annotations

import queue
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, ClassVar

from agentic_core.L2_execution.utils.providers import get_clock

_QUEUE_MAXSIZE = 5000
_INGESTER_LOCK = threading.Lock()
_INGESTER: "AsyncEvalIngester | None" = None


@dataclass(frozen=True)
class AsyncEvalPacket:
    """Sealed, read-only normalized join of BUS T evidence metrics + exit outcome.

    Schema
    ------
    Correlation:
        packet_id           — UUID for this packet
        run_id              — execution run_id (correlation key, from execution_context)
        lane_id             — tool name / lane identifier (e.g. "action_node.act")
        policy_hash         — policy hash from exit gate

    Evidence quality signals (from EvidenceMetrics):
        citation_completeness, support_coverage, provenance_completeness,
        exact_match_ratio, grounded_replayable, contradiction_present,
        query_hash, retrieval_id, collection

    Exit gate outcome (from ExitGateResult):
        exit_disposition    — ExitDisposition.value string
        exit_trace_id       — ExitGateResult.trace_id
        exit_reason         — ExitGateResult.reason

    Weak-support governance:
        weak_support_disposition — WeakSupportDisposition.value string

    Replay / trace metadata:
        sealed_at           — monotonic tick at packet creation
    """

    packet_id: str
    run_id: str
    lane_id: str
    collection: str
    policy_hash: str

    citation_completeness: float
    support_coverage: float
    provenance_completeness: float
    exact_match_ratio: float
    grounded_replayable: bool
    contradiction_present: bool
    query_hash: str
    retrieval_id: str

    exit_disposition: str
    exit_trace_id: str
    exit_reason: str

    weak_support_disposition: str

    sealed_at: float


class AsyncEvalIngester:
    """Thread-safe in-process queue for L6 shadow evaluation packets.

    Non-blocking: ``ingest()`` drops the packet (non-fatal) if the queue is full.
    No durable writes.  No L4 access.  Future-run only.
    """

    def __init__(self) -> None:
        self._queue: queue.Queue[AsyncEvalPacket] = queue.Queue(maxsize=_QUEUE_MAXSIZE)

    def ingest(self, packet: AsyncEvalPacket) -> bool:
        """Non-blocking ingest.  Returns False if queue full (non-fatal drop)."""
        try:
            self._queue.put_nowait(packet)
            return True
        except queue.Full:
            return False

    def drain(self, max_packets: int = 200) -> list[AsyncEvalPacket]:
        """Drain up to *max_packets* for shadow grading (non-blocking)."""
        packets: list[AsyncEvalPacket] = []
        for _ in range(max_packets):
            try:
                packets.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return packets

    def qsize(self) -> int:
        return self._queue.qsize()


def get_async_eval_ingester() -> AsyncEvalIngester:
    """Return the process-level AsyncEvalIngester singleton."""
    global _INGESTER
    if _INGESTER is None:
        with _INGESTER_LOCK:
            if _INGESTER is None:
                _INGESTER = AsyncEvalIngester()
    return _INGESTER


def reset_async_eval_ingester() -> None:
    """Reset the singleton for test isolation."""
    global _INGESTER
    _INGESTER = None


def ingest_eval_packet(
    run_id: str,
    lane_id: str,
    gate_result: Any,
    metrics: Any,
    weak_support_disposition: Any,
) -> AsyncEvalPacket:
    """Build a sealed AsyncEvalPacket and enqueue it for L6 shadow evaluation.

    This is the **real BUS T + exit + artifact join seam**: called from
    ``evaluate_and_emit()`` in ``evidence_eval_bridge.py`` immediately after all
    three artifacts are available at the same callsite.

    Args:
        run_id:                    Execution run_id (natural correlation key).
        lane_id:                   Tool name / lane identifier.
        gate_result:               ExitGateResult from run_live_exit_gate().
        metrics:                   EvidenceMetrics from emit_bundle_telemetry().
        weak_support_disposition:  WeakSupportDisposition from classify_evidence_support().

    Returns:
        AsyncEvalPacket — sealed, read-only, already enqueued.
    """
    gate_dict = gate_result.to_dict() if hasattr(gate_result, "to_dict") else {}

    packet = AsyncEvalPacket(
        packet_id=f"ap-{uuid.uuid4().hex[:16]}",
        run_id=run_id or "",
        lane_id=lane_id or "",
        collection=getattr(metrics, "collection", "") or "",
        policy_hash=gate_dict.get("policy_hash") or "",
        citation_completeness=float(getattr(metrics, "citation_completeness", 0.0)),
        support_coverage=float(getattr(metrics, "support_coverage", 0.0)),
        provenance_completeness=float(getattr(metrics, "provenance_completeness", 0.0)),
        exact_match_ratio=float(getattr(metrics, "exact_match_ratio", 0.0)),
        grounded_replayable=bool(getattr(metrics, "grounded_replayable", False)),
        contradiction_present=bool(getattr(metrics, "contradiction_present", False)),
        query_hash=getattr(metrics, "query_hash", "") or "",
        retrieval_id=getattr(metrics, "retrieval_id", "") or "",
        exit_disposition=gate_dict.get("disposition", ""),
        exit_trace_id=gate_dict.get("trace_id", ""),
        exit_reason=gate_dict.get("reason", ""),
        weak_support_disposition=getattr(weak_support_disposition, "value", str(weak_support_disposition)),
        sealed_at=get_clock().now_epoch(),
    )
    get_async_eval_ingester().ingest(packet)
    return packet


# ---------------------------------------------------------------------------
# ShadowEvalPacket and supporting sub-types
# ---------------------------------------------------------------------------
# Maps to: [6] S1 OBSERVABILITY — S1C REVIEW BUNDLE
# Full async shadow eval input; broader than AsyncEvalPacket.
# Produced by: Exit control closure after current-run boundary is crossed.
# Consumed by: L6ShadowEvalPipeline (future-run only; no live mutation).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HumanFeedbackRecord:
    """Human adjudication record for S2D calibration.

    Captures a single reviewer verdict on a shadow eval result.
    reviewer_id — opaque identifier for the human reviewer.
    verdict     — 'correct' | 'incorrect' | 'partial'.
    reviewed_at — monotonic epoch tick of the review.
    """

    reviewer_id: str = ""
    verdict: str = ""
    notes: str = ""
    reviewed_at: float = 0.0


@dataclass(frozen=True)
class CommitReceipt:
    """Receipt from a UWG commit attempt (if any commit occurred this run).

    committed    — True only if the durable ledger write succeeded.
    ledger_index — Index in the hash-chain ledger (0 = not committed).
    commit_hash  — SHA-256 hash of the committed record.
    """

    commit_id: str = ""
    committed: bool = False
    ledger_index: int = 0
    commit_hash: str = ""
    committed_at: float = 0.0


@dataclass(frozen=True)
class ShadowEvalPacket:
    """Full shadow evaluation input packet for L6 async grading (S1 REVIEW BUNDLE).

    Maps to: docs/reference/06_Shadow_Evaluation_System_Learning.md — S1C REVIEW BUNDLE
    Produced by: Exit control closure after current-run boundary is crossed.
    Consumed by: L6ShadowEvalPipeline.run_cycle() — future-run only.

    Layer authority: L6 (Observability — read-only, no mutations)
    No business logic.  No persistence.  No live-run mutation.

    Relationship to AsyncEvalPacket
    --------------------------------
    AsyncEvalPacket  — narrow BUS T join seam (evidence metrics + exit outcome)
                       for RAG-lane runs; created inline at evaluate_and_emit().
    ShadowEvalPacket — full S1 review bundle; broader scope; includes human
                       feedback, commit receipts, lineage, and baseline anchors
                       for the async multi-dimensional learning pipeline.

    Architectural invariant
    -----------------------
    run_scope = 'FUTURE_RUN' (ClassVar).  This packet must never influence the
    already-completed current run.  It is created only AFTER the current-run
    boundary has been crossed and all dispositions are final.
    """

    run_scope: ClassVar[str] = "FUTURE_RUN"

    packet_id: str
    run_id: str

    exit_disposition: str = ""
    exit_trace_id: str = ""
    exit_reason: str = ""

    exec_traces: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    telemetry: dict[str, Any] = field(default_factory=dict)

    human_feedback: tuple[HumanFeedbackRecord, ...] = field(default_factory=tuple)
    commit_receipts: tuple[CommitReceipt, ...] = field(default_factory=tuple)

    lineage_ids: tuple[str, ...] = field(default_factory=tuple)
    baseline_ids: tuple[str, ...] = field(default_factory=tuple)

    sealed_at: float = 0.0


__all__ = [
    "AsyncEvalPacket",
    "AsyncEvalIngester",
    "get_async_eval_ingester",
    "reset_async_eval_ingester",
    "ingest_eval_packet",
    "HumanFeedbackRecord",
    "CommitReceipt",
    "ShadowEvalPacket",
]
