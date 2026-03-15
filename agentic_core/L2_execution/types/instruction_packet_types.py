"""
InstructionPacket -- HMAC-SHA256 signed L2 ingress artifact.

Canonical JSON (sort_keys=True, separators=(",",":"), ensure_ascii=True)
is used as the signing surface.  Signature comparison is constant-time.

Phase 1: Cryptographic Boundary Contracts (Item 39)
Phase 2: L5 Guardian Certification Extension
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from agentic_core.L0_routing.providers.clock_provider import ClockProvider as clock_provider
from agentic_core.L5_safety.enforcement.credential_guard import get_credential_guard as credential_guard

from agentic_core.L2_execution.enforcement.key_source import get_current_secret
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_applies_guardrail("p0", "instruction_packet_types", "p0_governance")
_emit_snapshots_state("p0", "instruction_packet_types", "state_snapshot")


def _canonical_bytes(data: dict[str, Any]) -> bytes:
    """Return deterministic UTF-8 bytes from *data* (sorted keys, no spaces)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


class SignatureVerificationError(ValueError):
    """Raised when HMAC signature verification fails."""


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
    l5_signature : str
        L5 guardian certification signature (HMAC-SHA256). Empty means uncertified.
    certification_timestamp : str
        ISO8601 timestamp when L5 certification was applied.
    expiration_timestamp : str
        ISO8601 timestamp when L5 certification expires.
    agent_registry_hash : str
        SHA256 hash of agent registry at time of certification.
    execution_profile_hash : str
        SHA256 hash of execution profile at time of certification.
    policy_hash : str
        SHA256 hash of policy configuration at time of certification.
    """

    instruction_id: str
    payload: str
    metadata: dict[str, Any] = field(default_factory=dict)
    signature: str = field(default="", init=False)
    l5_signature: str = field(default="", init=True)
    certification_timestamp: str = field(default="", init=True)
    expiration_timestamp: str = field(default="", init=True)
    agent_registry_hash: str = field(default="", init=True)
    execution_profile_hash: str = field(default="", init=True)
    policy_hash: str = field(default="", init=True)

    def __post_init__(self) -> None:
        """Enforce mandatory signing at construction."""
        if not self.signature:
            credential_guard.check(operation="credential_access", target="get_current_secret")
            get_credential_guard().check(operation="credential_access", target="get_current_secret")
            secret = get_current_secret()
            mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
            object.__setattr__(self, "signature", mac.hexdigest().lower())

    def _signable_dict(self) -> dict[str, Any]:
        """Return the dict that is signed by base signature (base fields only)."""
        return {"instruction_id": self.instruction_id, "metadata": self.metadata, "payload": self.payload}

    def _l5_signable_dict(self) -> dict[str, Any]:
        """Return the dict for L5 signature (excludes l5_signature to avoid circularity)."""
        return {
            "instruction_id": self.instruction_id,
            "metadata": self.metadata,
            "payload": self.payload,
            "certification_timestamp": self.certification_timestamp,
            "expiration_timestamp": self.expiration_timestamp,
            "agent_registry_hash": self.agent_registry_hash,
            "execution_profile_hash": self.execution_profile_hash,
            "policy_hash": self.policy_hash,
        }

    def canonical_bytes(self) -> bytes:
        """Deterministic bytes over the base signing surface."""
        return _canonical_bytes(self._signable_dict())

    def sign(self, secret: bytes) -> InstructionPacket:
        """Return a *new* InstructionPacket with HMAC-SHA256 signature set."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "InstructionPacket.sign")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:InstructionPacket.sign".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        new_packet = InstructionPacket.__new__(InstructionPacket)
        object.__setattr__(new_packet, "instruction_id", self.instruction_id)
        object.__setattr__(new_packet, "payload", self.payload)
        object.__setattr__(new_packet, "metadata", self.metadata)
        object.__setattr__(new_packet, "signature", mac.hexdigest().lower())
        object.__setattr__(new_packet, "l5_signature", self.l5_signature)
        object.__setattr__(new_packet, "certification_timestamp", self.certification_timestamp)
        object.__setattr__(new_packet, "expiration_timestamp", self.expiration_timestamp)
        object.__setattr__(new_packet, "agent_registry_hash", self.agent_registry_hash)
        object.__setattr__(new_packet, "execution_profile_hash", self.execution_profile_hash)
        object.__setattr__(new_packet, "policy_hash", self.policy_hash)
        return new_packet

    def certify_l5(
        self,
        l5_secret: bytes,
        agent_registry_hash: str,
        execution_profile_hash: str,
        policy_hash: str,
        expiration_hours: int = 24,
    ) -> InstructionPacket:
        """Return a *new* InstructionPacket with L5 certification applied.

        Args:
            l5_secret: L5 guardian signing secret
            agent_registry_hash: SHA256 of agent registry
            execution_profile_hash: SHA256 of execution profile
            policy_hash: SHA256 of policy configuration
            expiration_hours: Hours until certification expires

        Returns:
            New InstructionPacket with L5 certification fields populated
        """
        now = clock_provider.now(timezone.utc)
        expiration = now + timedelta(hours=expiration_hours)
        certified = InstructionPacket.__new__(InstructionPacket)
        object.__setattr__(certified, "instruction_id", self.instruction_id)
        object.__setattr__(certified, "payload", self.payload)
        object.__setattr__(certified, "metadata", self.metadata)
        object.__setattr__(certified, "signature", "")
        object.__setattr__(certified, "l5_signature", "")
        object.__setattr__(certified, "certification_timestamp", now.isoformat())
        object.__setattr__(certified, "expiration_timestamp", expiration.isoformat())
        object.__setattr__(certified, "agent_registry_hash", agent_registry_hash)
        object.__setattr__(certified, "execution_profile_hash", execution_profile_hash)
        object.__setattr__(certified, "policy_hash", policy_hash)
        object.__setattr__(certified, "signature", self.signature)
        l5_canonical_bytes = _canonical_bytes(certified._l5_signable_dict())
        l5_mac = hmac.new(l5_secret, l5_canonical_bytes, hashlib.sha256)
        object.__setattr__(certified, "l5_signature", l5_mac.hexdigest().lower())
        return certified

    def verify_l5_certification(self, l5_secret: bytes) -> None:
        """Verify L5 certification signature and expiration.

        Args:
            l5_secret: L5 guardian signing secret

        Raises:
            SignatureVerificationError: if L5 signature is invalid or expired
        """
        if not self.l5_signature:
            raise SignatureVerificationError("InstructionPacket has no L5 signature -- packet is uncertified")
        l5_canonical_bytes = _canonical_bytes(self._l5_signable_dict())
        mac = hmac.new(l5_secret, l5_canonical_bytes, hashlib.sha256)
        expected = mac.hexdigest().lower()
        if not hmac.compare_digest(self.l5_signature, expected):
            raise SignatureVerificationError(
                "InstructionPacket L5 signature mismatch -- certification tampered or wrong key"
            )
        if self.expiration_timestamp:
            try:
                expiration = datetime.fromisoformat(self.expiration_timestamp.replace("Z", "+00:00"))
                if clock_provider.now(timezone.utc) > expiration:
                    raise SignatureVerificationError("InstructionPacket L5 certification has expired")
            except ValueError as e:
                raise SignatureVerificationError(f"Invalid expiration timestamp format: {e}")
        else:
            raise SignatureVerificationError("InstructionPacket missing expiration timestamp")

    def verify(self, secret: bytes) -> None:
        """Raise SignatureVerificationError if signature is absent or wrong."""
        if not self.signature:
            raise SignatureVerificationError("InstructionPacket has no signature -- packet is unsigned")
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

    @property
    def is_l5_certified(self) -> bool:
        """True when L5 certification signature is present (not verified)."""
        return bool(self.l5_signature)
