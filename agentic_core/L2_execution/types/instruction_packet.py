"""
InstructionPacket -- HMAC-SHA256 signed L2 ingress artifact.

Canonical JSON (sort_keys=True, separators=(",",":"), ensure_ascii=True)
is used as the signing surface.  Signature comparison is constant-time.

Phase 1: Cryptographic Boundary Contracts (Item 39)
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field, replace
from typing import Any


# ---------------------------------------------------------------------------
# Canonicalization helper
# ---------------------------------------------------------------------------


def _canonical_bytes(data: dict[str, Any]) -> bytes:
    """Return deterministic UTF-8 bytes from *data* (sorted keys, no spaces)."""
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class SignatureVerificationError(ValueError):
    """Raised when HMAC signature verification fails."""


# ---------------------------------------------------------------------------
# InstructionPacket
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InstructionPacket:
    """Signed instruction artifact for L2 ingress.

    Fields
    ------
    instruction_id : str
        Stable, deterministic identifier for this instruction.
    payload : str
        The instruction text / command payload.
    metadata : dict[str, Any]
        Arbitrary key/value context (must be JSON-serialisable).
    signature : str
        Lowercase hex HMAC-SHA256.  Empty string means unsigned.
    """

    instruction_id: str
    payload: str
    metadata: dict[str, Any] = field(default_factory=dict)
    signature: str = ""

    # ------------------------------------------------------------------
    # Signing surface
    # ------------------------------------------------------------------

    def _signable_dict(self) -> dict[str, Any]:
        """Return the dict that is signed (excludes signature field)."""
        return {
            "instruction_id": self.instruction_id,
            "metadata": self.metadata,
            "payload": self.payload,
        }

    def canonical_bytes(self) -> bytes:
        """Deterministic bytes over the signable surface."""
        return _canonical_bytes(self._signable_dict())

    # ------------------------------------------------------------------
    # sign / verify
    # ------------------------------------------------------------------

    def sign(self, secret: bytes) -> "InstructionPacket":
        """Return a *new* InstructionPacket with HMAC-SHA256 signature set."""
        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        return replace(self, signature=mac.hexdigest().lower())

    def verify(self, secret: bytes) -> None:
        """Raise SignatureVerificationError if signature is absent or wrong."""
        if not self.signature:
            raise SignatureVerificationError(
                "InstructionPacket has no signature -- packet is unsigned"
            )
        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        expected = mac.hexdigest().lower()
        if not hmac.compare_digest(self.signature, expected):
            raise SignatureVerificationError(
                "InstructionPacket signature mismatch -- packet tampered or wrong key"
            )

    @property
    def is_signed(self) -> bool:
        """True when a signature string is present (not verified)."""
        return bool(self.signature)
