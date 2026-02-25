"""
L2 Boundary Verifier -- fail-closed signature enforcement at L2 ingress.

All InstructionPacket and SandboxEnvelope objects MUST pass verify()
before any tool execution, write, or network call is permitted.

Phase 1: Cryptographic Boundary Contracts (Item 39/40 -- L2 wiring)
"""

from __future__ import annotations

from agentic_core.L2_execution.enforcement.key_source import get_current_secret
from agentic_core.L2_execution.types.instruction_packet import (
    InstructionPacket,
    SignatureVerificationError,
)
from agentic_core.L2_execution.types.sandbox_envelope import SandboxEnvelope


class L2BoundaryVerifier:
    """Fail-closed verification gate for L2 ingress artifacts.

    Usage
    -----
    verifier = L2BoundaryVerifier()
    verifier.verify_instruction_packet(packet)    # raises if invalid
    verifier.verify_sandbox_envelope(envelope)  # raises if invalid
    """

    def __init__(self) -> None:
        # No constructor args - uses injected key source
        pass

    def verify_instruction_packet(self, packet: InstructionPacket) -> None:
        """Verify InstructionPacket signature.  Raises SignatureVerificationError on failure."""
        if not isinstance(packet, InstructionPacket):
            raise TypeError(f"Expected InstructionPacket, got {type(packet).__name__}")
        secret = get_current_secret()
        packet.verify(secret)

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

    def is_envelope_valid(self, envelope: SandboxEnvelope) -> bool:
        """Return True if envelope passes verification, False otherwise (no exception)."""
        try:
            self.verify_sandbox_envelope(envelope)
            return True
        except (SignatureVerificationError, TypeError):
            return False
