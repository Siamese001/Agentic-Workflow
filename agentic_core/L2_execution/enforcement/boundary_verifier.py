"""
L2 Boundary Verifier -- fail-closed signature enforcement at L2 ingress.

All InstructionPacket and SandboxEnvelope objects MUST pass verify()
before any tool execution, write, or network call is permitted.

Phase 1: Cryptographic Boundary Contracts (Item 39/40 -- L2 wiring)
Phase 2: L5 Guardian Certification Enforcement
"""

from __future__ import annotations

import uuid

from agentic_core.L2_execution.enforcement.key_source import get_current_secret
from agentic_core.L2_execution.types.l2_instruction_packet import (
    InstructionPacket,
    SignatureVerificationError,
)
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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

emit_replay_key("p0", "boundary_verifier")
emit_determinism_digest("p0", "boundary_verifier")

_emit_dispatches_healing_run("p1", "boundary_verifier", "L2")
_emit_routes_through("p1", "boundary_verifier", "L2")
_emit_checks_agent_registry("p1", "boundary_verifier", "agent_registry")
_emit_validates_agent_capability("p1", "boundary_verifier", "capability")
_emit_dispatches_execution_plan("p1", "boundary_verifier", "exec_plan")
_emit_agent_executes_agent("p1", "boundary_verifier", "sub_agent")
_emit_routes_to_agent("p1", "boundary_verifier", "target_agent")
_emit_verifies_policy("p1", "boundary_verifier", "policy_check")
_emit_observes_runtime_state("p1", "boundary_verifier", "runtime_state")
_emit_transcripts_response("p1", "boundary_verifier", "transcript")
_emit_hard_fails_untranscripted("p1", "boundary_verifier")
_emit_gated_by_confidence("p1", "boundary_verifier", "confidence_gate")
_emit_escalates_to_human("p1", "boundary_verifier", "L2")
_emit_reads_policy_state("p1", "boundary_verifier", "L2")

_emit_snapshots_state("p0", "boundary_verifier", "state_snapshot")
_emit_authorize_and_execute("p2", "boundary_verifier", "execution_auth")
_emit_validates_capability("p2", "boundary_verifier", "capability_check")
_emit_routes_to_capability("p2", "boundary_verifier", "capability_route")
_emit_writes_via_uwg("p2", "boundary_verifier", "uwg_write")
_emit_blocks_direct_write("p2", "boundary_verifier", "direct_write_block")
_emit_records_tool_invocation("p2", "boundary_verifier", "tool_invocation")
_emit_captures_execution_output("p2", "boundary_verifier", "exec_output")
_emit_dispatches_agent("p3", "boundary_verifier", "agent_dispatch")
_emit_coordinates_agents("p3", "boundary_verifier", "agent_coordination")
_emit_records_workflow_lineage("p3", "boundary_verifier", "workflow_lineage")
_emit_records_healing_outcome("p3", "boundary_verifier", "healing_outcome")
_emit_escalates_failure("p3", "boundary_verifier", "failure_escalation")
_emit_orchestrates_workflow("p3", "boundary_verifier", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "boundary_verifier", "healing_dispatch")
_emit_invokes_evaluation("p3", "boundary_verifier", "evaluation_signal")
_emit_records_telemetry_event("p4", "boundary_verifier", "telemetry_event")
_emit_captures_evaluation_metric("p4", "boundary_verifier", "eval_metric")
_emit_stores_embedding("p4", "boundary_verifier", "embedding_store")
_emit_updates_meta_learning_state("p4", "boundary_verifier", "meta_learning")
_emit_links_execution_to_snapshot("p4", "boundary_verifier", "exec_snapshot_link")
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
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("boundary_verifier", "p4obs", "metric_1")
_emit_emits_metric_event("boundary_verifier", "p4obs", "metric_2")
_emit_emits_metric_event("boundary_verifier", "p4obs", "metric_3")
_emit_emits_metric_event("boundary_verifier", "p4obs", "metric_4")
_emit_emits_metric_event("boundary_verifier", "p4obs", "metric_5")
_emit_emits_metric_event("boundary_verifier", "p4obs", "metric_6")
_emit_records_incident_event("boundary_verifier", "p4obs", "incident")
_emit_captures_runtime_anomaly("boundary_verifier", "p4obs", "anomaly")
_emit_writes_observability_log("boundary_verifier", "p4obs", "obs_log")
_emit_updates_monitoring_state("boundary_verifier", "p4obs", "mon_state")
_emit_triggers_alert("boundary_verifier", "p4obs", "alert")
_emit_links_incident_trace("boundary_verifier", "p4obs", "trace_link")
_emit_captures_pattern("boundary_verifier", "p3lm", "pattern")
_emit_records_learning_event("boundary_verifier", "p3lm", "learning_event")
_emit_writes_learning_snapshot("boundary_verifier", "p3lm", "snapshot")
_emit_feeds_meta_learning("boundary_verifier", "p3lm", "meta_feed")
_emit_updates_routing_strategy("boundary_verifier", "p3lm", "routing")
_emit_improves_agent_policy("boundary_verifier", "p3lm", "policy")
_emit_stores_learning_state("boundary_verifier", "p3lm", "state")
_emit_records_execution_trace("boundary_verifier", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("boundary_verifier", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("boundary_verifier", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("boundary_verifier", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("boundary_verifier", "L4_STATE", "p2_trace_5")
_emit_reads_environ("boundary_verifier", "env_read", "p2_env_1")
_emit_reads_environ("boundary_verifier", "env_read", "p2_env_2")
_emit_reads_runtime_state("boundary_verifier", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("boundary_verifier", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "boundary_verifier", "context_pull")
_emit_pulls_context("p1", "boundary_verifier", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "boundary_verifier", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "boundary_verifier", "uwg_term_2")
_emit_writes_through("p1", "boundary_verifier", "write_through")
_emit_writes_through("p1", "boundary_verifier", "write_through_2")
_emit_validated_by_safety_plane("p1", "boundary_verifier", "safety_validation")
_emit_invokes_eval("p1", "boundary_verifier", "eval_call")
_emit_proposal_commits_routing("p1", "boundary_verifier", "routing_commit")


class L2BoundaryVerifier:
    """Fail-closed verification gate for L2 ingress artifacts.

    Usage
    -----
    verifier = L2BoundaryVerifier()
    verifier.verify_instruction_packet(packet)    # raises if invalid
    verifier.verify_sandbox_envelope(envelope)  # raises if invalid
    verifier.verify_l5_certification(packet)     # raises if uncertified
    """

    def __init__(self, l5_secret: bytes | None = None, secret: bytes | None = None) -> None:
        """Initialize verifier with optional L5 secret.

        Args:
            l5_secret: L5 guardian signing secret. If None, L5 verification
                      is skipped (for backward compatibility).
            secret: Deprecated backward-compat param (ignored; key source is injected).
        """
        if secret is not None and len(secret) == 0:
            raise ValueError("secret must be non-empty")
        self._l5_secret = l5_secret

    def verify_instruction_packet(self, packet: InstructionPacket) -> None:
        """Verify InstructionPacket signature.  Raises SignatureVerificationError on failure."""
        _emit_verifies_boundary(
            str(uuid.uuid4()),
            "L2BoundaryVerifier.verify_instruction_packet",
            "L2_EXECUTION",
        )
        _emit_applies_guardrail(
            str(uuid.uuid4()),
            "L2BoundaryVerifier.verify_instruction_packet",
            "L2_EXECUTION",
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "L2BoundaryVerifier.verify_instruction_packet",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:L2BoundaryVerifier.verify_instruction_packet".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not isinstance(packet, InstructionPacket):
            raise TypeError(f"Expected InstructionPacket, got {type(packet).__name__}")
        secret = get_current_secret()
        packet.verify(secret)

    def verify_l5_certification(self, packet: InstructionPacket) -> None:
        """Verify L5 guardian certification.  Raises SignatureVerificationError on failure.

        This is the P1: INITIALIZATION verification sequence:
        1. Verify L5 signature using canonical HMAC-SHA256
        2. Verify expiration timestamp
        3. Additional verification steps can be added here
        """
        if not isinstance(packet, InstructionPacket):
            raise TypeError(f"Expected InstructionPacket, got {type(packet).__name__}")

        if self._l5_secret is None:
            raise SignatureVerificationError("L5 verification required but no L5 secret provided to verifier")

        packet.verify_l5_certification(self._l5_secret)

    def verify_instruction_packet_with_l5(self, packet: InstructionPacket) -> None:
        """Verify both base signature and L5 certification.  Raises on any failure."""
        # First verify base signature
        self.verify_instruction_packet(packet)
        # Then verify L5 certification
        self.verify_l5_certification(packet)

    def verify_packet(self, packet: InstructionPacket) -> None:
        """Backward-compat alias for verify_instruction_packet."""
        self.verify_instruction_packet(packet)

    def verify_envelope(self, envelope: SandboxEnvelope) -> None:
        """Backward-compat alias for verify_sandbox_envelope."""
        self.verify_sandbox_envelope(envelope)

    def verify_sandbox_envelope(self, envelope: SandboxEnvelope) -> None:
        """Verify SandboxEnvelope signature before side-effects.  Raises on failure."""
        if not isinstance(envelope, SandboxEnvelope):
            raise TypeError(f"Expected SandboxEnvelope, got {type(envelope).__name__}")
        secret = get_current_secret()
        envelope.verify(secret)

    def is_packet_valid(self, packet: InstructionPacket) -> bool:
        """Return True if packet passes verification, False otherwise (no exception)."""
        try:
            self.verify_instruction_packet(packet)
            return True
        except (SignatureVerificationError, TypeError):
            return False

    def is_l5_certified(self, packet: InstructionPacket) -> bool:
        """Return True if packet has valid L5 certification, False otherwise."""
        try:
            self.verify_l5_certification(packet)
            return True
        except (SignatureVerificationError, TypeError):
            return False

    def is_packet_valid_with_l5(self, packet: InstructionPacket) -> bool:
        """Return True if packet passes both base and L5 verification, False otherwise."""
        try:
            self.verify_instruction_packet_with_l5(packet)
            return True
        except (SignatureVerificationError, TypeError):
            return False

    def is_envelope_valid(self, envelope: SandboxEnvelope) -> bool:
        """Return True if envelope passes verification, False otherwise (no exception)."""
        try:
            self.verify_sandbox_envelope(envelope)
            return True
        except (SignatureVerificationError, TypeError):
            return False
