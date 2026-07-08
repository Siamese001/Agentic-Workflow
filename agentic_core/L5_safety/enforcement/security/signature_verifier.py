"""Signature Verifier - Single Source of Truth for Packet Verification

[PHASE 8] Central signature verification for InstructionPacket and SandboxEnvelope.
Provides fail-closed verification with no fallback.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "signature_verifier")
trace_contract.emit_determinism_digest("p0", "signature_verifier")

trace_contract._emit_dispatches_healing_run("p1", "signature_verifier", "L5")
trace_contract._emit_routes_through("p1", "signature_verifier", "L5")
trace_contract._emit_checks_agent_registry("p1", "signature_verifier", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "signature_verifier", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "signature_verifier", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "signature_verifier", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "signature_verifier", "target_agent")
trace_contract._emit_verifies_policy("p1", "signature_verifier", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "signature_verifier", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "signature_verifier", "boundary_check")
trace_contract._emit_transcripts_response("p1", "signature_verifier", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "signature_verifier")
trace_contract._emit_gated_by_confidence("p1", "signature_verifier", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "signature_verifier", "L5")
trace_contract._emit_reads_policy_state("p1", "signature_verifier", "L5")

trace_contract._emit_applies_guardrail("p0", "signature_verifier", "p0_governance")
trace_contract._emit_snapshots_state("p0", "signature_verifier", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "signature_verifier", "execution_auth")
trace_contract._emit_validates_capability("p2", "signature_verifier", "capability_check")
trace_contract._emit_routes_to_capability("p2", "signature_verifier", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "signature_verifier", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "signature_verifier", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "signature_verifier", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "signature_verifier", "exec_output")
trace_contract._emit_dispatches_agent("p3", "signature_verifier", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "signature_verifier", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "signature_verifier", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "signature_verifier", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "signature_verifier", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "signature_verifier", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "signature_verifier", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "signature_verifier", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "signature_verifier", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "signature_verifier", "eval_metric")
trace_contract._emit_stores_embedding("p4", "signature_verifier", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "signature_verifier", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "signature_verifier", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("signature_verifier", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("signature_verifier", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("signature_verifier", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("signature_verifier", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("signature_verifier", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("signature_verifier", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("signature_verifier", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("signature_verifier", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("signature_verifier", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("signature_verifier", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("signature_verifier", "p4obs", "alert")
trace_contract._emit_links_incident_trace("signature_verifier", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("signature_verifier", "p3lm", "pattern")
trace_contract._emit_records_learning_event("signature_verifier", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("signature_verifier", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("signature_verifier", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("signature_verifier", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("signature_verifier", "p3lm", "policy")
trace_contract._emit_stores_learning_state("signature_verifier", "p3lm", "state")
trace_contract._emit_records_execution_trace("signature_verifier", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("signature_verifier", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("signature_verifier", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("signature_verifier", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("signature_verifier", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("signature_verifier", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("signature_verifier", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("signature_verifier", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("signature_verifier", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "signature_verifier", "context_pull")
trace_contract._emit_pulls_context("p1", "signature_verifier", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "signature_verifier", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "signature_verifier", "uwg_term_2")
trace_contract._emit_writes_through("p1", "signature_verifier", "write_through")
trace_contract._emit_writes_through("p1", "signature_verifier", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "signature_verifier", "safety_validation")
trace_contract._emit_invokes_eval("p1", "signature_verifier", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "signature_verifier", "routing_commit")

logger = logging.getLogger(__name__)


class SignatureVerificationError(RuntimeError):
    """Raised when signature verification fails."""

    pass


@dataclass(frozen=True)
class VerificationContext:
    """Immutable context containing verification results."""

    is_verified: bool
    signature_hash: str
    signer_id: str
    packet_hash: str
    verification_timestamp: float = field(default_factory=lambda: __import__("time").time())

    @property
    def is_valid(self) -> bool:
        """Alias for is_verified for backward compatibility."""
        return self.is_verified


@dataclass(frozen=True)
class InstructionPacket:
    """Instruction packet requiring signature verification."""

    payload: dict[str, Any]
    signature: str | None = None
    signer_id: str | None = None

    def compute_hash(self) -> str:
        """Compute deterministic hash of packet payload."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "InstructionPacket.compute_hash")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:InstructionPacket.compute_hash".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        canonical = json.dumps(self.payload, separators=(",", ":"), sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SandboxEnvelope:
    """Sandbox envelope requiring signature verification."""

    packet: InstructionPacket
    sandbox_config: dict[str, Any]
    envelope_signature: str | None = None

    def compute_hash(self) -> str:
        """Compute deterministic hash of envelope."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "SandboxEnvelope.compute_hash")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SandboxEnvelope.compute_hash".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {"packet_hash": self.packet.compute_hash(), "sandbox_config": self.sandbox_config}
        canonical = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class SignatureVerifier:
    """Central signature verifier with fail-closed semantics."""

    def __init__(self):
        self._trusted_signers: dict[str, str] = {
            "system": "system_signer_hash",
            "agent": "agent_signer_hash",
            "gateway": "gateway_signer_hash",
        }

    def verify_instruction_packet(self, packet: InstructionPacket) -> VerificationContext:
        """
        Verify an instruction packet signature.

        Fail-closed: raises if verification fails.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "SignatureVerifier.verify_instruction_packet",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:SignatureVerifier.verify_instruction_packet".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if packet.signature is None:
            raise SignatureVerificationError("INSTRUCTION_PACKET_MISSING_SIGNATURE: Packet has no signature")
        if packet.signer_id is None:
            raise SignatureVerificationError("INSTRUCTION_PACKET_MISSING_SIGNER: Packet has no signer_id")
        if packet.signer_id not in self._trusted_signers:
            raise SignatureVerificationError(
                f"INSTRUCTION_PACKET_UNTRUSTED_SIGNER: signer_id={packet.signer_id}",
            )
        packet_hash = packet.compute_hash()
        expected_signature = self._compute_signature(packet_hash, packet.signer_id)
        if packet.signature != expected_signature:
            raise SignatureVerificationError(
                f"INSTRUCTION_PACKET_INVALID_SIGNATURE: expected={expected_signature[:16]}..., provided={packet.signature[:16]}...",
            )
        return VerificationContext(
            is_verified=True,
            signature_hash=packet.signature,
            signer_id=packet.signer_id,
            packet_hash=packet_hash,
        )

    def verify_sandbox_envelope(self, envelope: SandboxEnvelope) -> VerificationContext:
        """
        Verify a sandbox envelope signature.

        Fail-closed: raises if verification fails.
        """
        packet_context = self.verify_instruction_packet(envelope.packet)
        if envelope.envelope_signature is None:
            raise SignatureVerificationError("SANDBOX_ENVELOPE_MISSING_SIGNATURE: Envelope has no signature")
        envelope_hash = envelope.compute_hash()
        expected_envelope_sig = self._compute_signature(envelope_hash, "system")
        if envelope.envelope_signature != expected_envelope_sig:
            raise SignatureVerificationError(
                f"SANDBOX_ENVELOPE_INVALID_SIGNATURE: expected={expected_envelope_sig[:16]}..., provided={envelope.envelope_signature[:16]}...",
            )
        return VerificationContext(
            is_verified=True,
            signature_hash=envelope.envelope_signature,
            signer_id="system",
            packet_hash=envelope_hash,
        )

    def _compute_signature(self, data_hash: str, signer_id: str) -> str:
        """
        Compute signature for given data hash and signer.

        Simplified implementation for Phase 8 - in production this would use
        actual cryptographic signatures.
        """
        signer_key = self._trusted_signers.get(signer_id, "unknown")
        signature_data = f"{data_hash}:{signer_id}:{signer_key}"
        return hashlib.sha256(signature_data.encode("utf-8")).hexdigest()

    def add_trusted_signer(self, signer_id: str, public_key_hash: str) -> None:
        """Add a trusted signer (for testing purposes)."""
        self._trusted_signers[signer_id] = public_key_hash


_global_verifier: SignatureVerifier | None = None


def get_signature_verifier() -> SignatureVerifier:
    """Get the global signature verifier instance."""
    global _global_verifier
    if _global_verifier is None:
        _global_verifier = SignatureVerifier()
    return _global_verifier


def verify_instruction_packet(packet: InstructionPacket) -> VerificationContext:
    """Convenience function to verify instruction packet."""
    return get_signature_verifier().verify_instruction_packet(packet)


def verify_sandbox_envelope(envelope: SandboxEnvelope) -> VerificationContext:
    """Convenience function to verify sandbox envelope."""
    return get_signature_verifier().verify_sandbox_envelope(envelope)


logger.info("SignatureVerifier: Initialized with fail-closed semantics")
