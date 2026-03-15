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
from agentic_core.L2_execution.types.instruction_packet_types import (
    InstructionPacket,
    SignatureVerificationError,
)
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_verifies_boundary,
)

_emit_snapshots_state("p0", "boundary_verifier", "state_snapshot")


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
            str(uuid.uuid4()), "L2BoundaryVerifier.verify_instruction_packet", "L2_EXECUTION"
        )
        _emit_applies_guardrail(
            str(uuid.uuid4()), "L2BoundaryVerifier.verify_instruction_packet", "L2_EXECUTION"
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "L2BoundaryVerifier.verify_instruction_packet"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:L2BoundaryVerifier.verify_instruction_packet".encode()
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
