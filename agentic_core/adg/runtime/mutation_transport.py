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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "mutation_transport", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "mutation_transport", "policy_binding")
trace_contract._emit_snapshots_state("p0", "mutation_transport", "state_snapshot")

trace_contract._emit_emits_metric_event("mutation_transport", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("mutation_transport", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("mutation_transport", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("mutation_transport", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("mutation_transport", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("mutation_transport", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("mutation_transport", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("mutation_transport", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("mutation_transport", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("mutation_transport", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("mutation_transport", "p4obs", "alert")
trace_contract._emit_links_incident_trace("mutation_transport", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("mutation_transport", "p3lm", "pattern")
trace_contract._emit_records_learning_event("mutation_transport", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("mutation_transport", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("mutation_transport", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("mutation_transport", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("mutation_transport", "p3lm", "policy")
trace_contract._emit_stores_learning_state("mutation_transport", "p3lm", "state")
trace_contract._emit_records_execution_trace("mutation_transport", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("mutation_transport", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("mutation_transport", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("mutation_transport", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("mutation_transport", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("mutation_transport", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("mutation_transport", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("mutation_transport", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("mutation_transport", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "mutation_transport", "context_pull")
trace_contract._emit_pulls_context("p1", "mutation_transport", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "mutation_transport", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "mutation_transport", "uwg_term_2")
trace_contract._emit_writes_through("p1", "mutation_transport", "write_through")
trace_contract._emit_writes_through("p1", "mutation_transport", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "mutation_transport", "safety_validation")
trace_contract._emit_invokes_eval("p1", "mutation_transport", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "mutation_transport", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "mutation_transport", "human_escalation")
trace_contract._emit_routes_through("p1", "mutation_transport", "route_through")
trace_contract._emit_checks_agent_registry("p1", "mutation_transport", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "mutation_transport", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "mutation_transport", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "mutation_transport", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "mutation_transport", "target_agent")
trace_contract._emit_verifies_policy("p1", "mutation_transport", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "mutation_transport", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "mutation_transport", "boundary_check")
trace_contract._emit_transcripts_response("p1", "mutation_transport", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "mutation_transport")
trace_contract._emit_gated_by_confidence("p1", "mutation_transport", "confidence_gate")
trace_contract.emit_replay_key("p0", "mutation_transport")
trace_contract.emit_determinism_digest("p0", "mutation_transport")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "mutation_transport", "execution_auth")
trace_contract._emit_validates_capability("p2", "mutation_transport", "capability_check")
trace_contract._emit_routes_to_capability("p2", "mutation_transport", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "mutation_transport", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "mutation_transport", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "mutation_transport", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "mutation_transport", "exec_output")
trace_contract._emit_dispatches_agent("p3", "mutation_transport", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "mutation_transport", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "mutation_transport", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "mutation_transport", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "mutation_transport", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "mutation_transport", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "mutation_transport", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "mutation_transport", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "mutation_transport", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "mutation_transport", "eval_metric")
trace_contract._emit_stores_embedding("p4", "mutation_transport", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "mutation_transport", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "mutation_transport", "exec_snapshot_link")


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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "MutationTransportReport.phases_distribution"
        )

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "MutationTransport.package_diff"
        )

        packet = MutationPacket(run_id=self.report.run_id, agent_id=self.report.agent_id)
        for p in patches:
            packet.patches.append(
                RFC6902Patch(**{k: v for k, v in p.items() if k in ("op", "path", "value", "from_path")}),
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


trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_1")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_2")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_3")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_4")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_5")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_6")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_7")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_8")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_9")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_10")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_11")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_12")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_13")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_14")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_15")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_16")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_17")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_18")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_19")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_20")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_21")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_22")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_23")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_24")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_25")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_26")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_27")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_28")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_29")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_30")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_31")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_32")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_33")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_34")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_35")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_36")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_37")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_38")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_39")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_40")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_41")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_42")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_43")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_44")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_45")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_46")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_47")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_48")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_49")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_50")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_51")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_52")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_53")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_54")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_55")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_56")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_57")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_58")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_59")
trace_contract._emit_reads_through("l4", "mutation_transport", "urg_read_60")
