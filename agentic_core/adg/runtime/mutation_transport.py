"""G13 (gap): Mutation transport / commit protocol runtime.

Models the rich mutation pipeline beyond the UWG gateway:
  vsock-only egress → deny-by-default intent validation → blast-radius check
  → RFC 6902 diff packaging → signed ExecutionTrace → 2-phase commit → distribution.

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class CommitPhase(str, Enum):
    PENDING = "pending"
    DIFF_PACKAGED = "diff_packaged"
    BLAST_RADIUS_CHECKED = "blast_radius_checked"
    SIGNED = "signed"
    PHASE1_PREPARED = "phase1_prepared"
    PHASE2_COMMITTED = "phase2_committed"
    DISTRIBUTED = "distributed"
    ABORTED = "aborted"


@dataclass
class RFC6902Patch:
    """An RFC 6902 JSON Patch operation."""

    op: str = "replace"
    path: str = ""
    value: Any = None
    from_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"op": self.op, "path": self.path}
        if self.value is not None:
            d["value"] = self.value
        if self.from_path:
            d["from"] = self.from_path
        return d


@dataclass
class MutationPacket:
    """A fully packaged mutation ready for 2-phase commit."""

    packet_id: str = field(default_factory=lambda: f"mp-{uuid.uuid4().hex[:12]}")
    run_id: str = ""
    agent_id: str = ""
    patches: list[RFC6902Patch] = field(default_factory=list)
    diff_hash: str = ""
    trace_signature: str = ""
    blast_radius_score: float = 0.0
    blast_radius_approved: bool = False
    phase: CommitPhase = CommitPhase.PENDING
    created_at: float = field(default_factory=time.time)
    committed_at: float = 0.0
    distributed_at: float = 0.0
    abort_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "patch_count": len(self.patches),
            "diff_hash": self.diff_hash,
            "trace_signature": self.trace_signature,
            "blast_radius_score": self.blast_radius_score,
            "blast_radius_approved": self.blast_radius_approved,
            "phase": self.phase.value,
            "created_at": self.created_at,
            "committed_at": self.committed_at,
            "distributed_at": self.distributed_at,
            "abort_reason": self.abort_reason,
        }


@dataclass
class MutationTransportReport:
    """Aggregated report for mutation transport / commit operations in one session."""

    agent_id: str = ""
    run_id: str = ""
    packets: list[MutationPacket] = field(default_factory=list)

    @property
    def committed_count(self) -> int:
        return sum(1 for p in self.packets if p.phase == CommitPhase.PHASE2_COMMITTED)

    @property
    def distributed_count(self) -> int:
        return sum(1 for p in self.packets if p.phase == CommitPhase.DISTRIBUTED)

    @property
    def aborted_count(self) -> int:
        return sum(1 for p in self.packets if p.phase == CommitPhase.ABORTED)

    @property
    def total_packets(self) -> int:
        return len(self.packets)

    def phases_distribution(self) -> dict[str, int]:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MutationTransportReport.phases_distribution")

        counts: dict[str, int] = {}
        for p in self.packets:
            key = p.phase.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_packets": self.total_packets,
            "committed_count": self.committed_count,
            "distributed_count": self.distributed_count,
            "aborted_count": self.aborted_count,
            "phases_distribution": self.phases_distribution(),
        }

    @property
    def summary(self) -> str:
        return (
            f"MutationTransport [{self.agent_id}] — "
            f"{self.total_packets} packets: "
            f"{self.committed_count} committed, "
            f"{self.distributed_count} distributed, "
            f"{self.aborted_count} aborted"
        )


class MutationTransport:
    """Runtime transport pipeline for the full mutation commit protocol."""

    _BLAST_RADIUS_THRESHOLD = 0.8

    def __init__(self, agent_id: str, run_id: str) -> None:
        self.report = MutationTransportReport(agent_id=agent_id, run_id=run_id)

    def package_diff(self, patches: list[dict[str, Any]]) -> MutationPacket:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MutationTransport.package_diff")

        packet = MutationPacket(run_id=self.report.run_id, agent_id=self.report.agent_id)
        for p in patches:
            packet.patches.append(
                RFC6902Patch(**{k: v for k, v in p.items() if k in ("op", "path", "value", "from_path")})
            )
        payload = str([p.to_dict() for p in packet.patches])
        packet.diff_hash = hashlib.sha256(payload.encode()).hexdigest()
        packet.phase = CommitPhase.DIFF_PACKAGED
        self.report.packets.append(packet)
        return packet

    def build_rfc6902_patch(self, patches: list[dict[str, Any]]) -> MutationPacket:
        return self.package_diff(patches)

    def validate_blast_radius(self, packet: MutationPacket, score: float) -> bool:
        packet.blast_radius_score = score
        packet.blast_radius_approved = score <= self._BLAST_RADIUS_THRESHOLD
        packet.phase = CommitPhase.BLAST_RADIUS_CHECKED
        return packet.blast_radius_approved

    def check_blast_radius(self, packet: MutationPacket, score: float) -> bool:
        return self.validate_blast_radius(packet, score)

    def sign_execution_trace(self, packet: MutationPacket, trace_payload: str = "") -> str:
        raw = f"{packet.packet_id}:{packet.diff_hash}:{trace_payload}"
        packet.trace_signature = hashlib.sha256(raw.encode()).hexdigest()
        packet.phase = CommitPhase.SIGNED
        return packet.trace_signature

    def commit_mutation(self, packet: MutationPacket) -> bool:
        if not packet.blast_radius_approved:
            packet.phase = CommitPhase.ABORTED
            packet.abort_reason = "blast_radius_exceeded"
            return False
        if not packet.trace_signature:
            packet.phase = CommitPhase.ABORTED
            packet.abort_reason = "unsigned_packet"
            return False
        packet.phase = CommitPhase.PHASE2_COMMITTED
        packet.committed_at = time.time()
        return True

    def distribute_mutation(self, packet: MutationPacket) -> None:
        if packet.phase == CommitPhase.PHASE2_COMMITTED:
            packet.phase = CommitPhase.DISTRIBUTED
            packet.distributed_at = time.time()
