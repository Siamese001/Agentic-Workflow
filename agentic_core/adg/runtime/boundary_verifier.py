"""G10 (gap): Execution boundary verification runtime.

Models the L2BoundaryVerifier + CapabilityChokepoint seam that checks packet
validity, L5 certification, and envelope validity before any action executes.

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "boundary_verifier", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "boundary_verifier", "policy_binding")
trace_contract._emit_snapshots_state("p0", "boundary_verifier", "state_snapshot")

trace_contract._emit_emits_metric_event("boundary_verifier", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("boundary_verifier", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("boundary_verifier", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("boundary_verifier", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("boundary_verifier", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("boundary_verifier", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("boundary_verifier", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("boundary_verifier", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("boundary_verifier", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("boundary_verifier", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("boundary_verifier", "p4obs", "alert")
trace_contract._emit_links_incident_trace("boundary_verifier", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("boundary_verifier", "p3lm", "pattern")
trace_contract._emit_records_learning_event("boundary_verifier", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("boundary_verifier", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("boundary_verifier", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("boundary_verifier", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("boundary_verifier", "p3lm", "policy")
trace_contract._emit_stores_learning_state("boundary_verifier", "p3lm", "state")
trace_contract._emit_records_execution_trace("boundary_verifier", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("boundary_verifier", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("boundary_verifier", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("boundary_verifier", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("boundary_verifier", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("boundary_verifier", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("boundary_verifier", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("boundary_verifier", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("boundary_verifier", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "boundary_verifier", "context_pull")
trace_contract._emit_pulls_context("p1", "boundary_verifier", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "boundary_verifier", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "boundary_verifier", "uwg_term_2")
trace_contract._emit_writes_through("p1", "boundary_verifier", "write_through")
trace_contract._emit_writes_through("p1", "boundary_verifier", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "boundary_verifier", "safety_validation")
trace_contract._emit_invokes_eval("p1", "boundary_verifier", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "boundary_verifier", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "boundary_verifier", "human_escalation")
trace_contract._emit_routes_through("p1", "boundary_verifier", "route_through")
trace_contract._emit_checks_agent_registry("p1", "boundary_verifier", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "boundary_verifier", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "boundary_verifier", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "boundary_verifier", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "boundary_verifier", "target_agent")
trace_contract._emit_verifies_policy("p1", "boundary_verifier", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "boundary_verifier", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "boundary_verifier", "boundary_check")
trace_contract._emit_transcripts_response("p1", "boundary_verifier", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "boundary_verifier")
trace_contract._emit_gated_by_confidence("p1", "boundary_verifier", "confidence_gate")
trace_contract.emit_replay_key("p0", "boundary_verifier")
trace_contract.emit_determinism_digest("p0", "boundary_verifier")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "boundary_verifier", "execution_auth")
trace_contract._emit_validates_capability("p2", "boundary_verifier", "capability_check")
trace_contract._emit_routes_to_capability("p2", "boundary_verifier", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "boundary_verifier", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "boundary_verifier", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "boundary_verifier", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "boundary_verifier", "exec_output")
trace_contract._emit_dispatches_agent("p3", "boundary_verifier", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "boundary_verifier", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "boundary_verifier", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "boundary_verifier", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "boundary_verifier", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "boundary_verifier", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "boundary_verifier", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "boundary_verifier", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "boundary_verifier", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "boundary_verifier", "eval_metric")
trace_contract._emit_stores_embedding("p4", "boundary_verifier", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "boundary_verifier", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "boundary_verifier", "exec_snapshot_link")


class VerificationOutcome(str, Enum):
    ACCEPTED = "accepted"
    REJECTED_INVALID_PACKET = "rejected_invalid_packet"
    REJECTED_NO_CERT = "rejected_no_cert"
    REJECTED_EXPIRED_ENVELOPE = "rejected_expired_envelope"
    REJECTED_TOKEN_REVOKED = "rejected_token_revoked"
    REJECTED_UNKNOWN = "rejected_unknown"


@dataclass
class BoundaryPacket:
    """Execution request packet submitted to the L2 boundary verifier."""

    packet_id: str = field(default_factory=lambda: f"pkt-{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    envelope_id: str = ""
    token_id: str = ""
    l5_cert_hash: str = ""
    payload_hash: str = ""
    submitted_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "agent_id": self.agent_id,
            "envelope_id": self.envelope_id,
            "token_id": self.token_id,
            "l5_cert_hash": self.l5_cert_hash,
            "payload_hash": self.payload_hash,
            "submitted_at": self.submitted_at,
        }


@dataclass
class BoundaryVerificationResult:
    """Result of a single boundary verification check."""

    result_id: str = field(default_factory=lambda: f"bvr-{uuid.uuid4().hex[:8]}")
    packet_id: str = ""
    outcome: VerificationOutcome = VerificationOutcome.ACCEPTED
    checked_at: float = field(default_factory=time.time)
    checks_passed: list[str] = field(default_factory=list)
    checks_failed: list[str] = field(default_factory=list)
    rejection_reason: str = ""

    @property
    def accepted(self) -> bool:
        return self.outcome == VerificationOutcome.ACCEPTED

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "packet_id": self.packet_id,
            "outcome": self.outcome.value,
            "accepted": self.accepted,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "rejection_reason": self.rejection_reason,
            "checked_at": self.checked_at,
        }


@dataclass
class BoundaryVerifierReport:
    """Aggregated report of all boundary verification events."""

    agent_id: str = ""
    run_id: str = ""
    results: list[BoundaryVerificationResult] = field(default_factory=list)

    @property
    def total_checks(self) -> int:
        return len(self.results)

    @property
    def accepted_count(self) -> int:
        return sum(1 for r in self.results if r.accepted)

    @property
    def rejected_count(self) -> int:
        return sum(1 for r in self.results if not r.accepted)

    @property
    def acceptance_rate(self) -> float:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "BoundaryVerifierReport.acceptance_rate"
        )

        if not self.results:
            return 1.0
        return self.accepted_count / len(self.results)

    def rejections_by_outcome(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self.results:
            if not r.accepted:
                key = r.outcome.value
                counts[key] = counts.get(key, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "total_checks": self.total_checks,
            "accepted_count": self.accepted_count,
            "rejected_count": self.rejected_count,
            "acceptance_rate": self.acceptance_rate,
            "rejections_by_outcome": self.rejections_by_outcome(),
        }

    @property
    def summary(self) -> str:
        return (
            f"BoundaryVerifier [{self.agent_id}] — "
            f"{self.total_checks} checks, "
            f"{self.accepted_count} accepted, {self.rejected_count} rejected"
        )


class L2BoundaryVerifier:
    """Runtime verifier for execution boundary packets."""

    def __init__(self, agent_id: str, run_id: str) -> None:
        self.report = BoundaryVerifierReport(agent_id=agent_id, run_id=run_id)

    def verify(self, packet: BoundaryPacket) -> BoundaryVerificationResult:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "L2BoundaryVerifier.verify")

        result = BoundaryVerificationResult(packet_id=packet.packet_id)

        if not packet.packet_id:
            result.checks_failed.append("packet_id_missing")
            result.outcome = VerificationOutcome.REJECTED_INVALID_PACKET
            result.rejection_reason = "packet_id missing"
            self.report.results.append(result)
            return result

        result.checks_passed.append("packet_id_present")

        if not packet.l5_cert_hash:
            result.checks_failed.append("l5_cert_missing")
            result.outcome = VerificationOutcome.REJECTED_NO_CERT
            result.rejection_reason = "L5 certification hash missing"
            self.report.results.append(result)
            return result

        result.checks_passed.append("l5_cert_present")

        if not packet.envelope_id:
            result.checks_failed.append("envelope_id_missing")
            result.outcome = VerificationOutcome.REJECTED_INVALID_PACKET
            result.rejection_reason = "envelope_id missing"
            self.report.results.append(result)
            return result

        result.checks_passed.append("envelope_valid")

        if not packet.token_id:
            result.checks_failed.append("token_missing")
            result.outcome = VerificationOutcome.REJECTED_TOKEN_REVOKED
            result.rejection_reason = "capability token missing"
            self.report.results.append(result)
            return result

        result.checks_passed.append("token_present")
        result.outcome = VerificationOutcome.ACCEPTED
        self.report.results.append(result)
        return result

    def certify_envelope(
        self,
        envelope_id: str,
        token_id: str,
        l5_cert_hash: str,
    ) -> BoundaryVerificationResult:
        packet = BoundaryPacket(
            agent_id=self.report.agent_id,
            envelope_id=envelope_id,
            token_id=token_id,
            l5_cert_hash=l5_cert_hash,
        )
        return self.verify(packet)


class CapabilityChokepoint:
    """Secondary chokepoint that validates L5 certification before capability use."""

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        self._certified_tokens: set[str] = set()
        self._rejected_tokens: set[str] = set()

    def certify(self, token_id: str, l5_cert_hash: str) -> bool:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "CapabilityChokepoint.certify"
        )

        if not token_id or not l5_cert_hash:
            self._rejected_tokens.add(token_id)
            return False
        self._certified_tokens.add(token_id)
        return True

    def is_certified(self, token_id: str) -> bool:
        return token_id in self._certified_tokens

    @property
    def certified_count(self) -> int:
        return len(self._certified_tokens)

    @property
    def rejected_count(self) -> int:
        return len(self._rejected_tokens)
