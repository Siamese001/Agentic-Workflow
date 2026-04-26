"""PA.7 Final Emit — output state codes.

Implements the eight :class:`DispatchDisposition` codes from the spec
(``PASS`` plus seven ``BLOCKED_*``) with a deterministic
:class:`DispatchOutcome` value.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DispatchDisposition(str, Enum):
    """Final emit state for a CompiledPromptArtifact (spec §PA.7)."""

    PASS = "PASS"
    BLOCKED_POLICY = "BLOCKED_POLICY"
    BLOCKED_CONTEXT = "BLOCKED_CONTEXT"
    BLOCKED_SCHEMA = "BLOCKED_SCHEMA"
    BLOCKED_BUDGET = "BLOCKED_BUDGET"
    BLOCKED_REPLAY = "BLOCKED_REPLAY"
    BLOCKED_TOOL = "BLOCKED_TOOL"
    BLOCKED_HITL = "BLOCKED_HITL"


class DispatchBlockReason(str, Enum):
    """Canonical reason codes for each BLOCKED_* disposition.

    Strings remain stable across versions for telemetry / replay matching.
    """

    POLICY_HASH_MISMATCH = "policy_hash_mismatch"
    POLICY_FENCE_VIOLATION = "policy_fence_violation"
    EVIDENCE_REQUIRED_MISSING = "evidence_required_missing"
    EVIDENCE_BLOCKED = "evidence_blocked"
    EVIDENCE_CONFLICTED_NOT_PRESERVED = "evidence_conflicted_not_preserved"
    SCHEMA_INVALID = "schema_invalid"
    SCHEMA_PROVIDER_UNSUPPORTED = "schema_provider_unsupported"
    BUDGET_OVERFLOW = "budget_overflow"
    BUDGET_REFINE_REQUIRED = "budget_refine_required"
    REPLAY_HASH_MISMATCH = "replay_hash_mismatch"
    REPLAY_METADATA_MISSING = "replay_metadata_missing"
    TOOL_REGISTRY_MISMATCH = "tool_registry_mismatch"
    TOOL_CAPABILITY_MISMATCH = "tool_capability_mismatch"
    HITL_REVIEW_REQUIRED = "hitl_review_required"

    @staticmethod
    def expected_disposition(reason: DispatchBlockReason) -> DispatchDisposition:
        """Map a reason code back to its canonical block disposition."""
        if reason in {
            DispatchBlockReason.POLICY_HASH_MISMATCH,
            DispatchBlockReason.POLICY_FENCE_VIOLATION,
        }:
            return DispatchDisposition.BLOCKED_POLICY
        if reason in {
            DispatchBlockReason.EVIDENCE_REQUIRED_MISSING,
            DispatchBlockReason.EVIDENCE_BLOCKED,
            DispatchBlockReason.EVIDENCE_CONFLICTED_NOT_PRESERVED,
        }:
            return DispatchDisposition.BLOCKED_CONTEXT
        if reason in {
            DispatchBlockReason.SCHEMA_INVALID,
            DispatchBlockReason.SCHEMA_PROVIDER_UNSUPPORTED,
        }:
            return DispatchDisposition.BLOCKED_SCHEMA
        if reason in {
            DispatchBlockReason.BUDGET_OVERFLOW,
            DispatchBlockReason.BUDGET_REFINE_REQUIRED,
        }:
            return DispatchDisposition.BLOCKED_BUDGET
        if reason in {
            DispatchBlockReason.REPLAY_HASH_MISMATCH,
            DispatchBlockReason.REPLAY_METADATA_MISSING,
        }:
            return DispatchDisposition.BLOCKED_REPLAY
        if reason in {
            DispatchBlockReason.TOOL_REGISTRY_MISMATCH,
            DispatchBlockReason.TOOL_CAPABILITY_MISMATCH,
        }:
            return DispatchDisposition.BLOCKED_TOOL
        if reason is DispatchBlockReason.HITL_REVIEW_REQUIRED:
            return DispatchDisposition.BLOCKED_HITL
        raise ValueError(f"unmapped DispatchBlockReason: {reason}")


@dataclass(frozen=True)
class DispatchOutcome:
    """Final dispatch decision for a CompiledPromptArtifact.

    Attributes
    ----------
    disposition
        One of the eight :class:`DispatchDisposition` values.
    block_reason
        Canonical reason code when ``disposition`` is any ``BLOCKED_*``;
        ``None`` for PASS.
    detail
        Free-text message for telemetry / operator triage.
    dispatch_allowed
        True iff disposition is PASS.
    """

    disposition: DispatchDisposition
    block_reason: DispatchBlockReason | None = None
    detail: str = ""
    dispatch_allowed: bool = False

    def __post_init__(self) -> None:
        if self.disposition is DispatchDisposition.PASS:
            if self.block_reason is not None:
                raise ValueError("DispatchOutcome.PASS must not carry a block_reason")
            object.__setattr__(self, "dispatch_allowed", True)
        else:
            if self.block_reason is None:
                raise ValueError(f"DispatchOutcome.{self.disposition.value} requires a block_reason")
            expected = DispatchBlockReason.expected_disposition(self.block_reason)
            if expected is not self.disposition:
                raise ValueError(
                    f"block_reason {self.block_reason.value} does not match "
                    f"disposition {self.disposition.value} (expected {expected.value})",
                )
            object.__setattr__(self, "dispatch_allowed", False)


def build_dispatch_outcome(
    *,
    disposition: DispatchDisposition,
    block_reason: DispatchBlockReason | None = None,
    detail: str = "",
) -> DispatchOutcome:
    """Construct a :class:`DispatchOutcome` with consistency checks."""
    return DispatchOutcome(
        disposition=disposition,
        block_reason=block_reason,
        detail=detail,
    )


__all__ = [
    "DispatchBlockReason",
    "DispatchDisposition",
    "DispatchOutcome",
    "build_dispatch_outcome",
]
