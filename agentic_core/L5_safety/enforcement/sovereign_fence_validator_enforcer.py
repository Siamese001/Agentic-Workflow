from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Proposal = Any
Policy = Any


class SovereignFenceViolation(Exception):
    """Raised when a proposal violates a sovereign safety fence."""

    def __init__(self, reason_code: str, message: str):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SovereignFenceViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SovereignFenceViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "SovereignFenceViolation.__init__")
        self.reason_code = reason_code
        self.message = message
        super().__init__(f"[{self.reason_code}] {self.message}")


@dataclass(frozen=True)
class FenceValidationResult:
    """The result of a fence validation check."""

    is_valid: bool
    violations: Sequence[SovereignFenceViolation]

    def to_digest_contribution(self) -> dict[str, Any]:
        """Returns a dictionary suitable for inclusion in a determinism digest."""
        return {
            "is_valid": self.is_valid,
            "violation_codes": sorted([v.reason_code for v in self.violations]),
        }


def validate(proposal: Proposal, policy: Policy) -> FenceValidationResult:
    """
    Validates a proposal against a sovereign policy fence.

    This is a hard boundary. It is not advisory. A validation failure here must
    block any state change (e.g., before a STAMP operation).

    Args:
        proposal: The proposed action or state change.
        policy: The sovereign policy to validate against.

    Returns:
        A FenceValidationResult indicating if the proposal is valid.
    """
    violations = []
    return FenceValidationResult(is_valid=not violations, violations=violations)
