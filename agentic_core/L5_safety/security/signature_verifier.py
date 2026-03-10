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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
        data = {
            "packet_hash": self.packet.compute_hash(),
            "sandbox_config": self.sandbox_config,
        }
        canonical = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class SignatureVerifier:
    """Central signature verifier with fail-closed semantics."""

    def __init__(self):
        self._trusted_signers: dict[str, str] = {
            # signer_id: public_key_hash (simplified for Phase 8)
            "system": "system_signer_hash",
            "agent": "agent_signer_hash",
            "gateway": "gateway_signer_hash",
        }

    def verify_instruction_packet(self, packet: InstructionPacket) -> VerificationContext:
        """
        Verify an instruction packet signature.

        Fail-closed: raises if verification fails.
        """
        if packet.signature is None:
            raise SignatureVerificationError("INSTRUCTION_PACKET_MISSING_SIGNATURE: Packet has no signature")

        if packet.signer_id is None:
            raise SignatureVerificationError("INSTRUCTION_PACKET_MISSING_SIGNER: Packet has no signer_id")

        # Verify signer is trusted
        if packet.signer_id not in self._trusted_signers:
            raise SignatureVerificationError(
                f"INSTRUCTION_PACKET_UNTRUSTED_SIGNER: signer_id={packet.signer_id}"
            )

        # Compute expected signature (simplified verification for Phase 8)
        packet_hash = packet.compute_hash()
        expected_signature = self._compute_signature(packet_hash, packet.signer_id)

        if packet.signature != expected_signature:
            raise SignatureVerificationError(
                f"INSTRUCTION_PACKET_INVALID_SIGNATURE: expected={expected_signature[:16]}..., "
                f"provided={packet.signature[:16]}..."
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
        # First verify the inner packet
        packet_context = self.verify_instruction_packet(envelope.packet)

        if envelope.envelope_signature is None:
            raise SignatureVerificationError("SANDBOX_ENVELOPE_MISSING_SIGNATURE: Envelope has no signature")

        # Verify envelope signature
        envelope_hash = envelope.compute_hash()
        expected_envelope_sig = self._compute_signature(envelope_hash, "system")

        if envelope.envelope_signature != expected_envelope_sig:
            raise SignatureVerificationError(
                f"SANDBOX_ENVELOPE_INVALID_SIGNATURE: expected={expected_envelope_sig[:16]}..., "
                f"provided={envelope.envelope_signature[:16]}..."
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
        # Simulate signature computation
        signer_key = self._trusted_signers.get(signer_id, "unknown")
        signature_data = f"{data_hash}:{signer_id}:{signer_key}"
        return hashlib.sha256(signature_data.encode("utf-8")).hexdigest()

    def add_trusted_signer(self, signer_id: str, public_key_hash: str) -> None:
        """Add a trusted signer (for testing purposes)."""
        self._trusted_signers[signer_id] = public_key_hash


# Global verifier instance
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


# Module initialization
logger.info("SignatureVerifier: Initialized with fail-closed semantics")
