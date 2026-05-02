"""Async eval packet utilities.

Provides the in-process future-run packet queues used by L6 shadow evaluation.
This hardened version removes nondeterministic packet identifiers and validates
queue drain arguments defensively.
"""

from __future__ import annotations

import hashlib
import json
import logging
import queue
import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from agentic_core.L2_execution.utils.providers import (
    get_clock,
)  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency

if TYPE_CHECKING:
    from agentic_core.L2_execution.types.sealed_l2_artifact import (
        SealedL2Artifact,
    )  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency
    from agentic_core.L5_safety.types.exit_disposition_types import CurrentRunEvaluationResult

_log = logging.getLogger(__name__)
_QUEUE_MAXSIZE = 5000
_INGESTER_LOCK = threading.Lock()
_INGESTER: AsyncEvalIngester | None = None
_SHADOW_INGESTER_LOCK = threading.Lock()
_SHADOW_INGESTER: ShadowEvalIngester | None = None


@dataclass(frozen=True)
class AsyncEvalPacket:
    """Sealed, read-only normalized join of BUS T evidence metrics + exit outcome."""

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


@dataclass(frozen=True)
class HumanFeedbackRecord:
    """Human adjudication record for S2D calibration."""

    reviewer_id: str = ""
    verdict: str = ""
    notes: str = ""
    reviewed_at: float = 0.0


@dataclass(frozen=True)
class CommitReceipt:
    """Receipt from a UWG commit attempt."""

    commit_id: str = ""
    committed: bool = False
    ledger_index: int = 0
    commit_hash: str = ""
    committed_at: float = 0.0


@dataclass(frozen=True)
class ShadowEvalPacket:
    """Full shadow evaluation input packet for L6 async grading."""

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


class AsyncEvalIngester:
    """Thread-safe in-process queue for L6 shadow evaluation packets."""

    def __init__(self) -> None:
        self._queue: queue.Queue[AsyncEvalPacket] = queue.Queue(maxsize=_QUEUE_MAXSIZE)
        self._enqueue_count = 0
        self._drop_count = 0
        self._drain_count = 0
        self._lock = threading.Lock()

    def ingest(self, packet: AsyncEvalPacket) -> bool:
        try:
            self._queue.put_nowait(packet)
            with self._lock:
                self._enqueue_count += 1
            return True
        except queue.Full:
            with self._lock:
                self._drop_count += 1
            return False

    def drain(self, max_packets: int = 200) -> list[AsyncEvalPacket]:
        packets: list[AsyncEvalPacket] = []
        drain_limit = max(0, int(max_packets))
        for _ in range(drain_limit):
            try:
                packets.append(self._queue.get_nowait())
                with self._lock:
                    self._drain_count += 1
            except queue.Empty:
                break
        return packets

    def qsize(self) -> int:
        return self._queue.qsize()

    def status(self) -> dict[str, Any]:
        qs = self._queue.qsize()
        maxsize = self._queue.maxsize if self._queue.maxsize > 0 else _QUEUE_MAXSIZE
        with self._lock:
            enqueue_count = self._enqueue_count
            drop_count = self._drop_count
            drain_count = self._drain_count
        return {
            "qsize": qs,
            "maxsize": maxsize,
            "saturation_pct": round(100.0 * qs / maxsize, 1),
            "enqueue_count": enqueue_count,
            "drop_count": drop_count,
            "drain_count": drain_count,
        }


class ShadowEvalIngester:
    """Thread-safe in-process queue for ``ShadowEvalPacket`` instances."""

    def __init__(self) -> None:
        self._queue: queue.Queue[ShadowEvalPacket] = queue.Queue(maxsize=_QUEUE_MAXSIZE)
        self._enqueue_count = 0
        self._drop_count = 0
        self._drain_count = 0
        self._lock = threading.Lock()

    def enqueue(self, packet: ShadowEvalPacket) -> bool:
        try:
            self._queue.put_nowait(packet)
            with self._lock:
                self._enqueue_count += 1
            return True
        except queue.Full:
            with self._lock:
                self._drop_count += 1
            return False

    def drain(self, max_packets: int = 200) -> list[ShadowEvalPacket]:
        packets: list[ShadowEvalPacket] = []
        drain_limit = max(0, int(max_packets))
        for _ in range(drain_limit):
            try:
                packets.append(self._queue.get_nowait())
                with self._lock:
                    self._drain_count += 1
            except queue.Empty:
                break
        return packets

    def qsize(self) -> int:
        return self._queue.qsize()

    def status(self) -> dict[str, Any]:
        qs = self._queue.qsize()
        maxsize = self._queue.maxsize if self._queue.maxsize > 0 else _QUEUE_MAXSIZE
        with self._lock:
            enqueue_count = self._enqueue_count
            drop_count = self._drop_count
            drain_count = self._drain_count
        return {
            "qsize": qs,
            "maxsize": maxsize,
            "saturation_pct": round(100.0 * qs / maxsize, 1),
            "enqueue_count": enqueue_count,
            "drop_count": drop_count,
            "drain_count": drain_count,
        }


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return f"{prefix}-{hashlib.sha256(material.encode('utf-8')).hexdigest()[:16]}"


def get_async_eval_ingester() -> AsyncEvalIngester:
    """Return the process-level ``AsyncEvalIngester`` singleton."""
    global _INGESTER
    if _INGESTER is None:
        with _INGESTER_LOCK:
            if _INGESTER is None:
                _INGESTER = AsyncEvalIngester()
    return _INGESTER


def reset_async_eval_ingester() -> None:
    """Reset the singleton for test isolation."""
    global _INGESTER
    with _INGESTER_LOCK:
        _INGESTER = None


def ingest_eval_packet(
    run_id: str,
    lane_id: str,
    gate_result: Any,
    metrics: Any,
    weak_support_disposition: Any,
) -> AsyncEvalPacket:
    """Build and enqueue a sealed ``AsyncEvalPacket`` for L6 shadow evaluation."""
    gate_dict = gate_result.to_dict() if hasattr(gate_result, "to_dict") else {}
    packet_payload = {
        "run_id": run_id or "",
        "lane_id": lane_id or "",
        "collection": getattr(metrics, "collection", "") or "",
        "policy_hash": gate_dict.get("policy_hash") or "",
        "query_hash": getattr(metrics, "query_hash", "") or "",
        "retrieval_id": getattr(metrics, "retrieval_id", "") or "",
        "exit_trace_id": gate_dict.get("trace_id", "") or "",
        "weak_support_disposition": getattr(weak_support_disposition, "value", str(weak_support_disposition)),
    }
    packet = AsyncEvalPacket(
        packet_id=_stable_id("ap", packet_payload),
        run_id=packet_payload["run_id"],
        lane_id=packet_payload["lane_id"],
        collection=packet_payload["collection"],
        policy_hash=packet_payload["policy_hash"],
        citation_completeness=float(getattr(metrics, "citation_completeness", 0.0)),
        support_coverage=float(getattr(metrics, "support_coverage", 0.0)),
        provenance_completeness=float(getattr(metrics, "provenance_completeness", 0.0)),
        exact_match_ratio=float(getattr(metrics, "exact_match_ratio", 0.0)),
        grounded_replayable=bool(getattr(metrics, "grounded_replayable", False)),
        contradiction_present=bool(getattr(metrics, "contradiction_present", False)),
        query_hash=packet_payload["query_hash"],
        retrieval_id=packet_payload["retrieval_id"],
        exit_disposition=gate_dict.get("disposition", "") or "",
        exit_trace_id=packet_payload["exit_trace_id"],
        exit_reason=gate_dict.get("reason", "") or "",
        weak_support_disposition=packet_payload["weak_support_disposition"],
        sealed_at=float(get_clock().now_epoch()),
    )
    async_ingester = get_async_eval_ingester()
    if not async_ingester.ingest(packet):
        _log.warning(
            "[AsyncEvalIngester] Drop: queue full (maxsize=%d). run_id=%s lane=%s",
            async_ingester._queue.maxsize,
            run_id,
            lane_id,
        )
    return packet


def get_shadow_eval_ingester() -> ShadowEvalIngester:
    """Return the process-level ``ShadowEvalIngester`` singleton."""
    global _SHADOW_INGESTER
    if _SHADOW_INGESTER is None:
        with _SHADOW_INGESTER_LOCK:
            if _SHADOW_INGESTER is None:
                _SHADOW_INGESTER = ShadowEvalIngester()
    return _SHADOW_INGESTER


def reset_shadow_eval_ingester() -> None:
    """Reset the singleton for test isolation."""
    global _SHADOW_INGESTER
    with _SHADOW_INGESTER_LOCK:
        _SHADOW_INGESTER = None


def enqueue_shadow_eval_packet(packet: ShadowEvalPacket) -> bool:
    """Enqueue a ``ShadowEvalPacket`` for async L6 shadow pipeline processing."""
    shadow_ingester = get_shadow_eval_ingester()
    enqueued = shadow_ingester.enqueue(packet)
    if not enqueued:
        _log.warning(
            "[ShadowEvalIngester] Drop: queue full (maxsize=%d). packet_id=%s",
            shadow_ingester._queue.maxsize,
            getattr(packet, "packet_id", "?"),
        )
    return enqueued


def build_shadow_eval_packet(
    artifact: SealedL2Artifact,
    eval_result: CurrentRunEvaluationResult,
    *,
    hitl_packet: dict[str, Any] | None = None,
    commit_receipts: tuple[CommitReceipt, ...] = (),
    human_feedback: tuple[HumanFeedbackRecord, ...] = (),
    extra_telemetry: dict[str, Any] | None = None,
) -> ShadowEvalPacket:
    """Build a ``ShadowEvalPacket`` from a completed current-run closure."""
    if getattr(artifact, "run_scope", None) != "CURRENT_RUN":
        raise ValueError(
            "build_shadow_eval_packet: artifact must have run_scope='CURRENT_RUN', "
            f"got {getattr(artifact, 'run_scope', None)!r}"
        )
    if getattr(eval_result, "run_scope", None) != "CURRENT_RUN":
        raise ValueError(
            "build_shadow_eval_packet: eval_result must have run_scope='CURRENT_RUN', "
            f"got {getattr(eval_result, 'run_scope', None)!r}"
        )

    quality_checks = eval_result.quality_checks
    rubric_scores = eval_result.rubric_scores
    integrity_checks = eval_result.integrity_checks
    validation_counters = artifact.validation_counters
    replay_metadata = artifact.replay_metadata

    telemetry: dict[str, Any] = {
        "groundedness_score": quality_checks.groundedness_score,
        "support_coverage": quality_checks.support_coverage,
        "relevance_score": quality_checks.relevance_score,
        "abstain_correct": quality_checks.abstain_correct,
        "escalation_correct": quality_checks.escalation_correct,
        "answer_fit": quality_checks.answer_fit,
        "rules_compliance_score": rubric_scores.rules_compliance_score,
        "policy_adherence_score": rubric_scores.policy_adherence_score,
        "schema_completion_score": rubric_scores.schema_completion_score,
        "confidence_score": eval_result.confidence_score,
        "safety_clear": integrity_checks.safety_clear,
        "policy_pass": integrity_checks.policy_pass,
        "mutation_authorized": integrity_checks.mutation_authorized,
        "env_integrity": integrity_checks.env_integrity,
        "replay_env_complete": integrity_checks.replay_env_complete,
        "terminal_classification": artifact.terminal_classification.value,
        "replay_completeness": replay_metadata.replay_completeness,
        "policy_checks_passed": validation_counters.policy_checks_passed,
        "policy_checks_failed": validation_counters.policy_checks_failed,
        "schema_checks_passed": validation_counters.schema_checks_passed,
        "schema_checks_failed": validation_counters.schema_checks_failed,
        "mutation_auth_checks_failed": validation_counters.mutation_auth_checks_failed,
        "has_commit_payload": artifact.has_commit_payload,
        "policy_hash": eval_result.policy_hash or "",
        "compliance_hash": eval_result.compliance_hash or "",
    }
    if hitl_packet:
        telemetry["hitl_packet"] = dict(hitl_packet)
    if extra_telemetry:
        telemetry.update(dict(extra_telemetry))

    exec_traces = (dict(artifact.exec_trace),) if getattr(artifact, "exec_trace", None) else ()

    lineage: list[str] = []
    if eval_result.trace_id:
        lineage.append(eval_result.trace_id)
    if artifact.trace_id and artifact.trace_id != eval_result.trace_id:
        lineage.append(artifact.trace_id)

    baselines: list[str] = []
    if eval_result.policy_hash:
        baselines.append(eval_result.policy_hash)
    if eval_result.compliance_hash:
        baselines.append(eval_result.compliance_hash)

    packet_payload = {
        "run_id": eval_result.eval_id,
        "trace_id": eval_result.trace_id,
        "disposition": eval_result.disposition.value,
        "reason": eval_result.disposition_reason,
        "lineage_ids": lineage,
        "baseline_ids": baselines,
    }

    return ShadowEvalPacket(
        packet_id=_stable_id("sep", packet_payload),
        run_id=eval_result.eval_id,
        exit_disposition=eval_result.disposition.value,
        exit_trace_id=eval_result.trace_id,
        exit_reason=eval_result.disposition_reason,
        exec_traces=exec_traces,
        telemetry=telemetry,
        human_feedback=human_feedback,
        commit_receipts=commit_receipts,
        lineage_ids=tuple(lineage),
        baseline_ids=tuple(baselines),
        sealed_at=float(get_clock().now_epoch()),
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
