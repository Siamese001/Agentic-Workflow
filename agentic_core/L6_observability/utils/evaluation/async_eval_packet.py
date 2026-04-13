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

import logging
import queue
import threading
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from agentic_core.L2_execution.types.sealed_l2_artifact import SealedL2Artifact
    from agentic_core.L5_safety.types.exit_disposition_types import CurrentRunEvaluationResult

from agentic_core.L2_execution.utils.providers import get_clock

_QUEUE_MAXSIZE = 5000
_INGESTER_LOCK = threading.Lock()
_INGESTER: AsyncEvalIngester | None = None

_SHADOW_INGESTER_LOCK = threading.Lock()
_SHADOW_INGESTER: ShadowEvalIngester | None = None


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
    Drops are logged at WARNING level and counted in ``status()``.
    No durable writes.  No L4 access.  Future-run only.
    """

    def __init__(self) -> None:
        self._queue: queue.Queue[AsyncEvalPacket] = queue.Queue(maxsize=_QUEUE_MAXSIZE)
        self._enqueue_count: int = 0
        self._drop_count: int = 0
        self._drain_count: int = 0

    def ingest(self, packet: AsyncEvalPacket) -> bool:
        """Non-blocking ingest.  Returns False if queue full (non-fatal drop)."""
        try:
            self._queue.put_nowait(packet)
            self._enqueue_count += 1
            return True
        except queue.Full:
            self._drop_count += 1
            return False

    def drain(self, max_packets: int = 200) -> list[AsyncEvalPacket]:
        """Drain up to *max_packets* for shadow grading (non-blocking)."""
        packets: list[AsyncEvalPacket] = []
        for _ in range(max_packets):
            try:
                packets.append(self._queue.get_nowait())
                self._drain_count += 1
            except queue.Empty:
                break
        return packets

    def qsize(self) -> int:
        return self._queue.qsize()

    def status(self) -> dict:
        """Return a snapshot of queue health metrics.

        Keys:
            qsize:           Current number of items in queue.
            maxsize:         Maximum queue capacity.
            saturation_pct:  qsize / maxsize * 100 (float, 0–100).
            enqueue_count:   Cumulative successful enqueues since creation.
            drop_count:      Cumulative drops due to queue full since creation.
            drain_count:     Cumulative items drained since creation.
        """
        qs = self._queue.qsize()
        maxsize = self._queue.maxsize if self._queue.maxsize > 0 else _QUEUE_MAXSIZE
        return {
            "qsize": qs,
            "maxsize": maxsize,
            "saturation_pct": round(100.0 * qs / maxsize, 1),
            "enqueue_count": self._enqueue_count,
            "drop_count": self._drop_count,
            "drain_count": self._drain_count,
        }


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
    _async_ingester = get_async_eval_ingester()
    enqueued = _async_ingester.ingest(packet)
    if not enqueued:
        _log.warning(
            "[AsyncEvalIngester] Drop: queue full (maxsize=%d). run_id=%s lane=%s",
            _async_ingester._queue.maxsize,
            run_id,
            lane_id,
        )
    return packet


# ---------------------------------------------------------------------------
# ShadowEvalIngester — canonical future-run queue for ShadowEvalPackets
# ---------------------------------------------------------------------------


class ShadowEvalIngester:
    """Thread-safe in-process queue for ShadowEvalPackets (canonical future-run path).

    Drainable by L6ShadowEvalPipeline.run_shadow_packet_cycle().
    Drops are logged at WARNING level and counted in ``status()``.
    No durable writes.  No L4 access.  Future-run only.
    """

    def __init__(self) -> None:
        self._queue: queue.Queue[ShadowEvalPacket] = queue.Queue(maxsize=_QUEUE_MAXSIZE)
        self._enqueue_count: int = 0
        self._drop_count: int = 0
        self._drain_count: int = 0

    def enqueue(self, packet: ShadowEvalPacket) -> bool:
        """Non-blocking enqueue.  Returns False if queue full (non-fatal drop)."""
        try:
            self._queue.put_nowait(packet)
            self._enqueue_count += 1
            return True
        except queue.Full:
            self._drop_count += 1
            return False

    def drain(self, max_packets: int = 200) -> list[ShadowEvalPacket]:
        """Drain up to *max_packets* for shadow pipeline processing (non-blocking)."""
        packets: list = []
        for _ in range(max_packets):
            try:
                packets.append(self._queue.get_nowait())
                self._drain_count += 1
            except queue.Empty:
                break
        return packets

    def qsize(self) -> int:
        return self._queue.qsize()

    def status(self) -> dict:
        """Return a snapshot of queue health metrics.

        Keys:
            qsize:           Current number of items in queue.
            maxsize:         Maximum queue capacity.
            saturation_pct:  qsize / maxsize * 100 (float, 0–100).
            enqueue_count:   Cumulative successful enqueues since creation.
            drop_count:      Cumulative drops due to queue full since creation.
            drain_count:     Cumulative items drained since creation.
        """
        qs = self._queue.qsize()
        maxsize = self._queue.maxsize if self._queue.maxsize > 0 else _QUEUE_MAXSIZE
        return {
            "qsize": qs,
            "maxsize": maxsize,
            "saturation_pct": round(100.0 * qs / maxsize, 1),
            "enqueue_count": self._enqueue_count,
            "drop_count": self._drop_count,
            "drain_count": self._drain_count,
        }


def get_shadow_eval_ingester() -> ShadowEvalIngester:
    """Return the process-level ShadowEvalIngester singleton."""
    global _SHADOW_INGESTER
    if _SHADOW_INGESTER is None:
        with _SHADOW_INGESTER_LOCK:
            if _SHADOW_INGESTER is None:
                _SHADOW_INGESTER = ShadowEvalIngester()
    return _SHADOW_INGESTER


def reset_shadow_eval_ingester() -> None:
    """Reset the singleton for test isolation."""
    global _SHADOW_INGESTER
    _SHADOW_INGESTER = None


def enqueue_shadow_eval_packet(packet: ShadowEvalPacket) -> bool:
    """Enqueue a ShadowEvalPacket for async L6 shadow pipeline processing.

    The canonical CURRENT_RUN→FUTURE_RUN handoff point called from
    ``evaluate_and_emit()`` after the current-run boundary is crossed.
    Non-blocking — drops silently if queue full (non-fatal).

    Args:
        packet: ShadowEvalPacket from build_shadow_eval_packet().

    Returns:
        True if enqueued; False if dropped (queue full).
    """
    _shadow_ingester = get_shadow_eval_ingester()
    enqueued = _shadow_ingester.enqueue(packet)
    if not enqueued:
        _log.warning(
            "[ShadowEvalIngester] Drop: queue full (maxsize=%d). packet_id=%s",
            _shadow_ingester._queue.maxsize,
            getattr(packet, "packet_id", "?"),
        )
    return enqueued


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
    Consumed by: L6ShadowEvalPipeline.run_shadow_packet_cycle() — future-run only.

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


# ---------------------------------------------------------------------------
# ShadowEvalPacket builder — async intake from current-run closure
# ---------------------------------------------------------------------------


def build_shadow_eval_packet(
    artifact: SealedL2Artifact,
    eval_result: CurrentRunEvaluationResult,
    *,
    hitl_packet: dict[str, Any] | None = None,
    commit_receipts: tuple[CommitReceipt, ...] = (),
    human_feedback: tuple[HumanFeedbackRecord, ...] = (),
    extra_telemetry: dict[str, Any] | None = None,
) -> ShadowEvalPacket:
    """Build a ShadowEvalPacket from a completed current-run closure.

    Called AFTER the current-run boundary has been crossed and all dispositions
    are final.  No live mutation.  Future-run only.

    Args:
        artifact:        Sealed L2 artifact from current run.
        eval_result:     CurrentRunEvaluationResult from ExitControlGate.evaluate_sealed().
        hitl_packet:     Optional HITL packet dict if HITL was triggered this run.
        commit_receipts: Optional commit receipts if a UWG commit occurred.
        human_feedback:  Optional human feedback records.
        extra_telemetry: Optional extra telemetry signals to merge.

    Returns:
        ShadowEvalPacket — sealed, future-run scoped, ready for L6ShadowEvalPipeline.
    """
    # Scope invariant: both inputs must be from a completed CURRENT_RUN boundary.
    if getattr(artifact, "run_scope", None) != "CURRENT_RUN":
        raise ValueError(
            f"build_shadow_eval_packet: artifact must have run_scope='CURRENT_RUN', "
            f"got {getattr(artifact, 'run_scope', None)!r}"
        )
    if getattr(eval_result, "run_scope", None) != "CURRENT_RUN":
        raise ValueError(
            f"build_shadow_eval_packet: eval_result must have run_scope='CURRENT_RUN', "
            f"got {getattr(eval_result, 'run_scope', None)!r}"
        )
    q = eval_result.quality_checks
    r = eval_result.rubric_scores
    ic = eval_result.integrity_checks
    vc = artifact.validation_counters
    rm = artifact.replay_metadata

    telemetry: dict[str, Any] = {
        # Outcome signals from CurrentRunEvaluationResult
        "groundedness_score": q.groundedness_score,
        "support_coverage": q.support_coverage,
        "relevance_score": q.relevance_score,
        "abstain_correct": q.abstain_correct,
        "escalation_correct": q.escalation_correct,
        "answer_fit": q.answer_fit,
        # Rubric signals
        "rules_compliance_score": r.rules_compliance_score,
        "policy_adherence_score": r.policy_adherence_score,
        "schema_completion_score": r.schema_completion_score,
        "confidence_score": eval_result.confidence_score,
        # Integrity signals
        "safety_clear": ic.safety_clear,
        "policy_pass": ic.policy_pass,
        "mutation_authorized": ic.mutation_authorized,
        "env_integrity": ic.env_integrity,
        "replay_env_complete": ic.replay_env_complete,
        # Artifact signals
        "terminal_classification": artifact.terminal_classification.value,
        "replay_completeness": rm.replay_completeness,
        "policy_checks_passed": vc.policy_checks_passed,
        "policy_checks_failed": vc.policy_checks_failed,
        "schema_checks_passed": vc.schema_checks_passed,
        "schema_checks_failed": vc.schema_checks_failed,
        "mutation_auth_checks_failed": vc.mutation_auth_checks_failed,
        "has_commit_payload": artifact.has_commit_payload,
        "policy_hash": eval_result.policy_hash or "",
        "compliance_hash": eval_result.compliance_hash or "",
    }
    if hitl_packet:
        telemetry["hitl_packet"] = hitl_packet
    if extra_telemetry:
        telemetry.update(extra_telemetry)

    exec_traces = (dict(artifact.exec_trace),) if artifact.exec_trace else ()

    _lineage: list[str] = []
    if eval_result.trace_id:
        _lineage.append(eval_result.trace_id)
    if artifact.trace_id and artifact.trace_id != eval_result.trace_id:
        _lineage.append(artifact.trace_id)

    _baseline: list[str] = []
    if eval_result.policy_hash:
        _baseline.append(eval_result.policy_hash)
    if eval_result.compliance_hash:
        _baseline.append(eval_result.compliance_hash)

    return ShadowEvalPacket(
        packet_id=f"sep-{uuid.uuid4().hex[:16]}",
        run_id=eval_result.eval_id,
        exit_disposition=eval_result.disposition.value,
        exit_trace_id=eval_result.trace_id,
        exit_reason=eval_result.disposition_reason,
        exec_traces=exec_traces,
        telemetry=telemetry,
        human_feedback=human_feedback,
        commit_receipts=commit_receipts,
        lineage_ids=tuple(_lineage),
        baseline_ids=tuple(_baseline),
        sealed_at=get_clock().now_epoch(),
    )


__all__ = [
    "AsyncEvalPacket",
    "AsyncEvalIngester",
    "get_async_eval_ingester",
    "reset_async_eval_ingester",
    "ingest_eval_packet",
    "ShadowEvalIngester",
    "get_shadow_eval_ingester",
    "reset_shadow_eval_ingester",
    "enqueue_shadow_eval_packet",
    "HumanFeedbackRecord",
    "CommitReceipt",
    "ShadowEvalPacket",
    "build_shadow_eval_packet",
]
