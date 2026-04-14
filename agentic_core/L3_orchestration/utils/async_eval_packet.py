from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Any


@dataclass
class AsyncEvalPacket:
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
    run_scope: str = "CURRENT_RUN"

    def __post_init__(self) -> None:
        self.packet_id = str(self.packet_id or "")
        self.run_id = str(self.run_id or "")
        self.lane_id = str(self.lane_id or "")
        self.collection = str(self.collection or "")
        self.policy_hash = str(self.policy_hash or "")
        self.query_hash = str(self.query_hash or "")
        self.retrieval_id = str(self.retrieval_id or "")
        self.exit_disposition = str(self.exit_disposition or "")
        self.exit_trace_id = str(self.exit_trace_id or "")
        self.exit_reason = str(self.exit_reason or "")
        self.weak_support_disposition = str(self.weak_support_disposition or "")
        self.run_scope = str(self.run_scope or "CURRENT_RUN")
        self.citation_completeness = _safe_float(self.citation_completeness)
        self.support_coverage = _safe_float(self.support_coverage)
        self.provenance_completeness = _safe_float(self.provenance_completeness)
        self.exact_match_ratio = _safe_float(self.exact_match_ratio)
        self.grounded_replayable = bool(self.grounded_replayable)
        self.contradiction_present = bool(self.contradiction_present)
        self.sealed_at = _safe_float(self.sealed_at)


@dataclass
class ShadowEvalPacket:
    packet_id: str
    run_id: str
    sealed_at: float
    run_scope: str = "FUTURE_RUN"

    def __post_init__(self) -> None:
        self.packet_id = str(self.packet_id or "")
        self.run_id = str(self.run_id or "")
        self.sealed_at = _safe_float(self.sealed_at)
        self.run_scope = str(self.run_scope or "FUTURE_RUN")


class _PacketIngester:
    def __init__(self, max_queue: int = 10_000) -> None:
        self._queue: list[Any] = []
        self._lock = Lock()
        self._max_queue = max(1, int(max_queue))

    def ingest(self, packet: Any) -> None:
        with self._lock:
            self._queue.append(packet)
            overflow = len(self._queue) - self._max_queue
            if overflow > 0:
                del self._queue[:overflow]

    def qsize(self) -> int:
        with self._lock:
            return len(self._queue)

    def peek(self, max_packets: int | None = None) -> list[Any]:
        with self._lock:
            limit = len(self._queue) if max_packets is None else max(0, int(max_packets))
            return list(self._queue[:limit])

    def drain(self, max_packets: int | None = None) -> list[Any]:
        with self._lock:
            if max_packets is None:
                max_packets = len(self._queue)
            max_packets = max(0, int(max_packets))
            drained = self._queue[:max_packets]
            self._queue = self._queue[max_packets:]
            return drained

    def clear(self) -> None:
        with self._lock:
            self._queue.clear()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return default
    if value != value:
        return default
    return value


_async_ingester = _PacketIngester()
_shadow_ingester = _PacketIngester()


def get_async_eval_ingester() -> _PacketIngester:
    return _async_ingester


def get_shadow_eval_ingester() -> _PacketIngester:
    return _shadow_ingester


def reset_async_eval_ingester() -> None:
    global _async_ingester
    _async_ingester = _PacketIngester()


def reset_shadow_eval_ingester() -> None:
    global _shadow_ingester
    _shadow_ingester = _PacketIngester()


def enqueue_shadow_eval_packet(packet: ShadowEvalPacket) -> bool:
    if not isinstance(packet, ShadowEvalPacket):
        packet = ShadowEvalPacket(
            packet_id=getattr(packet, "packet_id", ""),
            run_id=getattr(packet, "run_id", ""),
            sealed_at=getattr(packet, "sealed_at", 0.0),
            run_scope=getattr(packet, "run_scope", "FUTURE_RUN"),
        )
    get_shadow_eval_ingester().ingest(packet)
    return True
