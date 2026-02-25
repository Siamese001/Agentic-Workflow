"""
SandboxEnvelope -- HMAC-SHA256 signed L2 tool-invocation wrapper.

Carries an InstructionPacket (or raw payload) plus tool invocation metadata.
Signature must be verified before any side-effect is permitted.

Phase 1: Cryptographic Boundary Contracts (Item 40)
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field, replace
from typing import Any

from agentic_core.L2_execution.types.instruction_packet import (
    SignatureVerificationError,
    _canonical_bytes,
)


# ---------------------------------------------------------------------------
# SandboxEnvelope
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SandboxEnvelope:
    """Signed wrapper for L2 tool invocations.

    Fields
    ------
    envelope_id : str
        Deterministic identifier for this envelope (e.g. instruction_id + tool).
    tool_name : str
        Name of the tool being invoked.
    tool_args : dict[str, Any]
        Arguments passed to the tool (must be JSON-serialisable).
    instruction_packet_id : str
        ``instruction_id`` of the parent InstructionPacket being executed.
    invocation_metadata : dict[str, Any]
        Additional L2 metadata (agent, tick, etc.).
    signature : str
        Lowercase hex HMAC-SHA256.  Empty string means unsigned.
    """

    envelope_id: str
    tool_name: str
    tool_args: dict[str, Any] = field(default_factory=dict)
    instruction_packet_id: str = ""
    invocation_metadata: dict[str, Any] = field(default_factory=dict)
    signature: str = ""

    # ------------------------------------------------------------------
    # Signing surface
    # ------------------------------------------------------------------

    def _signable_dict(self) -> dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "instruction_packet_id": self.instruction_packet_id,
            "invocation_metadata": self.invocation_metadata,
            "tool_args": self.tool_args,
            "tool_name": self.tool_name,
        }

    def canonical_bytes(self) -> bytes:
        """Deterministic bytes over the signable surface."""
        return _canonical_bytes(self._signable_dict())

    # ------------------------------------------------------------------
    # sign / verify
    # ------------------------------------------------------------------

    def sign(self, secret: bytes) -> "SandboxEnvelope":
        """Return a *new* SandboxEnvelope with HMAC-SHA256 signature set."""
        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        return replace(self, signature=mac.hexdigest().lower())

    def verify(self, secret: bytes) -> None:
        """Raise SignatureVerificationError if signature is absent or wrong.

        Must be called before any tool execution, write, or network call.
        """
        if not self.signature:
            raise SignatureVerificationError(
                "SandboxEnvelope has no signature -- envelope is unsigned"
            )
        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        expected = mac.hexdigest().lower()
        if not hmac.compare_digest(self.signature, expected):
            raise SignatureVerificationError(
                "SandboxEnvelope signature mismatch -- envelope tampered or wrong key"
            )

    @property
    def is_signed(self) -> bool:
        """True when a signature string is present (not verified)."""
        return bool(self.signature)
