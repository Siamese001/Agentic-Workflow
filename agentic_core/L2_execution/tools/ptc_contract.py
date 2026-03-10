"""
PTC (Prompt-to-Code) Runtime Contract Enforcement.

Enforces at runtime:
- stdout-only contract: PTC output must not produce implicit file writes
- deterministic redaction: minimal deterministic redactor strips secrets
- strict byte caps: output exceeding cap is hard-rejected (fail-closed)
- no bypass of write gateway

Phase 1: Cryptographic Boundary Contracts (Item 41 -- PTC enforcement)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L2_execution.types.instruction_packet_types import (
    SignatureVerificationError,
)
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Hard byte cap for PTC stdout output (fail-closed above this).
PTC_STDOUT_BYTE_CAP: int = 65_536  # 64 KiB

# Minimal deterministic secret-redaction patterns.
# Patterns are applied in declaration order (deterministic).
_REDACTION_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[^\s,;\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(secret\s*[:=]\s*)[^\s,;\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(password\s*[:=]\s*)[^\s,;\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(token\s*[:=]\s*)[^\s,;\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9\-._~+/]+=*"), r"\1[REDACTED]"),
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class PTCContractViolation(RuntimeError):
    """Raised when a PTC runtime contract is violated."""


class PTCBytesCapExceeded(PTCContractViolation):
    """Raised when PTC output exceeds the hard byte cap."""


class PTCUnsignedEnvelopeError(PTCContractViolation):
    """Raised when PTC execution is attempted with an unsigned envelope."""


# ---------------------------------------------------------------------------
# Redactor
# ---------------------------------------------------------------------------


def redact_output(text: str) -> str:
    """Apply deterministic redaction to *text*.

    Patterns are applied in fixed declaration order for determinism.
    Returns the redacted string.
    """
    for pattern, replacement in _REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


# ---------------------------------------------------------------------------
# PTC Contract Enforcer
# ---------------------------------------------------------------------------


@dataclass
class PTCContractEnforcer:
    """Enforces PTC runtime contracts before and after tool execution.

    Usage
    -----
    enforcer = PTCContractEnforcer(secret=b"shared-secret")
    enforcer.pre_execute(envelope)           # raises if envelope not valid
    safe_output = enforcer.post_execute(raw_output)  # redact + cap check
    """

    secret: bytes
    byte_cap: int = PTC_STDOUT_BYTE_CAP
    _violation_count: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.secret:
            raise ValueError("PTCContractEnforcer: secret must be non-empty bytes")
        if self.byte_cap <= 0:
            raise ValueError("PTCContractEnforcer: byte_cap must be positive")

    # ------------------------------------------------------------------
    # Pre-execution gate (fail-closed)
    # ------------------------------------------------------------------

    def pre_execute(self, envelope: SandboxEnvelope) -> None:
        """Verify envelope signature before any side-effect.

        Raises PTCUnsignedEnvelopeError or SignatureVerificationError on failure.
        """
        if not isinstance(envelope, SandboxEnvelope):
            raise TypeError(
                f"PTCContractEnforcer.pre_execute: expected SandboxEnvelope, "
                f"got {type(envelope).__name__}"
            )
        if not envelope.is_signed:
            self._violation_count += 1
            raise PTCUnsignedEnvelopeError(
                f"PTC contract violation: SandboxEnvelope '{envelope.envelope_id}' "
                f"is unsigned -- execution refused"
            )
        try:
            envelope.verify(self.secret)
        except SignatureVerificationError as exc:
            self._violation_count += 1
            raise PTCContractViolation(
                f"PTC contract violation: envelope signature invalid -- {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Post-execution gate (redact + cap)
    # ------------------------------------------------------------------

    def post_execute(self, raw_output: str) -> str:
        """Redact secrets and enforce byte cap on PTC stdout output.

        Raises PTCBytesCapExceeded if the redacted output exceeds byte_cap.
        Returns the safe, redacted output string.
        """
        if not isinstance(raw_output, str):
            raise TypeError(
                f"PTCContractEnforcer.post_execute: expected str, "
                f"got {type(raw_output).__name__}"
            )
        redacted = redact_output(raw_output)
        encoded_len = len(redacted.encode("utf-8"))
        if encoded_len > self.byte_cap:
            self._violation_count += 1
            raise PTCBytesCapExceeded(
                f"PTC contract violation: output {encoded_len} bytes exceeds "
                f"cap {self.byte_cap} bytes -- output rejected"
            )
        return redacted

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def violation_count(self) -> int:
        """Total number of contract violations detected by this enforcer."""
        return self._violation_count
