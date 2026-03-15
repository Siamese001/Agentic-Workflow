"""
SandboxEnvelope -- HMAC-SHA256 signed L2 tool-invocation wrapper.

Carries an InstructionPacket (or raw payload) plus tool invocation metadata.
Signature must be verified before any side-effect is permitted.

Phase 1: Cryptographic Boundary Contracts (Item 40)
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from dataclasses import dataclass as _dc
from typing import Any

from agentic_core.L2_execution.enforcement.key_source import get_current_secret
from agentic_core.L2_execution.types.instruction_packet_types import (
    SignatureVerificationError,
    _canonical_bytes,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

# ---------------------------------------------------------------------------
# ToolBudget
# ---------------------------------------------------------------------------


@_dc(frozen=True)
class ToolBudget:
    """OS-level resource caps per tool invocation (spec contract [2])."""

    compute_ms: int = 5_000  # wall-clock cap; enforced by BudgetEnforcer
    memory_mb: int = 256
    stdout_bytes: int = 65_536  # 64 KiB

    def __post_init__(self) -> None:
        if self.compute_ms <= 0 or self.memory_mb <= 0 or self.stdout_bytes <= 0:
            raise ValueError("All ToolBudget caps must be positive")


DEFAULT_TOOL_BUDGET = ToolBudget()


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
    budget : ToolBudget
        OS-level resource caps for this invocation (spec contract [2]).
    signature : str
        Lowercase hex HMAC-SHA256.  Empty string means unsigned.
    """

    envelope_id: str
    tool_name: str
    tool_args: dict[str, Any] = field(default_factory=dict)
    instruction_packet_id: str = ""
    invocation_metadata: dict[str, Any] = field(default_factory=dict)
    budget: ToolBudget = field(default_factory=ToolBudget)
    signature: str = field(default="", init=False)

    def __post_init__(self) -> None:
        """Enforce mandatory signing at construction."""
        if not self.signature:
            # Auto-sign with injected secret
            secret = get_current_secret()
            mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
            # Use object.__setattr__ since dataclass is frozen
            object.__setattr__(self, "signature", mac.hexdigest().lower())

    # ------------------------------------------------------------------
    # Signing surface
    # ------------------------------------------------------------------

    def _signable_dict(self) -> dict[str, Any]:
        return {
            "budget": {
                "compute_ms": self.budget.compute_ms,
                "memory_mb": self.budget.memory_mb,
                "stdout_bytes": self.budget.stdout_bytes,
            },
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

    def sign(self, secret: bytes) -> SandboxEnvelope:
        """Return a *new* SandboxEnvelope with HMAC-SHA256 signature set."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "SandboxEnvelope.sign")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:SandboxEnvelope.sign".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        mac = hmac.new(secret, self.canonical_bytes(), hashlib.sha256)
        new_env = SandboxEnvelope.__new__(SandboxEnvelope)
        object.__setattr__(new_env, "envelope_id", self.envelope_id)
        object.__setattr__(new_env, "tool_name", self.tool_name)
        object.__setattr__(new_env, "tool_args", self.tool_args)
        object.__setattr__(new_env, "instruction_packet_id", self.instruction_packet_id)
        object.__setattr__(new_env, "invocation_metadata", self.invocation_metadata)
        object.__setattr__(new_env, "budget", self.budget)
        object.__setattr__(new_env, "signature", mac.hexdigest().lower())
        return new_env

    def verify(self, secret: bytes) -> None:
        """Raise SignatureVerificationError if signature is absent or wrong.

        Must be called before any tool execution, write, or network call.
        """
        if not self.signature:
            raise SignatureVerificationError("SandboxEnvelope has no signature -- envelope is unsigned")
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
