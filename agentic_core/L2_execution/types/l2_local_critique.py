"""L2 Verify-Then-Execute / Local Critique Contract (spec 04.10).

Optional bounded L2-owned verification sub-loop for high-risk model/tool/script
attempts. Does not expand scope, plan, fetch evidence, change route, ask humans
directly, commit durable writes, or judge final user-facing quality.

Source spec: docs/reference/04_L2_Execute/04.10_L2_Verify_Then_Execute_Local_Critique.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CritiqueType(str, Enum):
    PRE_INVOCATION = "pre_invocation"
    POST_INVOCATION = "post_invocation"
    SCHEMA_SANITY = "schema_sanity"
    TOOL_ARGS_SANITY = "tool_args_sanity"
    SCRIPT_SAFETY_SANITY = "script_safety_sanity"
    ARTIFACT_SANITY = "artifact_sanity"


class CritiqueResult(str, Enum):
    PASS = "PASS"
    FAIL_LOCAL = "FAIL_LOCAL"
    WARN_LOCAL = "WARN_LOCAL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


# Default loop bound per spec 04.10 LOOP BOUNDS.
DEFAULT_MAX_LOCAL_CRITIQUE_PASSES = 1


@dataclass(frozen=True)
class LocalCritiqueInput:
    """Input to a single local-critique pass."""

    approved_work_order_ref: str
    invocation_candidate_ref: str
    capability_token_ref: str
    sandbox_envelope_ref: str
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    risk_tier: str
    verification_budget: int
    allowed_checks: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for required in (
            "approved_work_order_ref",
            "invocation_candidate_ref",
            "capability_token_ref",
            "sandbox_envelope_ref",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
        ):
            if not getattr(self, required):
                raise ValueError(f"LocalCritiqueInput.{required} required")
        if self.verification_budget <= 0:
            raise ValueError("verification_budget must be positive")


@dataclass(frozen=True)
class LocalCritiqueReceipt:
    """Single-pass critique receipt; replayable by deterministic_digest."""

    critique_receipt_id: str
    critique_type: CritiqueType
    result: CritiqueResult
    deterministic_digest: str
    adjustment_allowed: bool = False
    suggested_local_adjustment: Optional[str] = None
    reason_codes: tuple[str, ...] = ()
    # Spec 04.10 DISALLOWED checks — assertions stamped on every receipt.
    no_route_change_assertion: bool = True
    no_new_evidence_assertion: bool = True
    no_policy_override_assertion: bool = True

    def __post_init__(self) -> None:
        if not self.critique_receipt_id:
            raise ValueError("critique_receipt_id required")
        if not self.deterministic_digest:
            raise ValueError("deterministic_digest required")
        for assertion in (
            "no_route_change_assertion",
            "no_new_evidence_assertion",
            "no_policy_override_assertion",
        ):
            if not getattr(self, assertion):
                raise ValueError(
                    f"LocalCritiqueReceipt.{assertion} must be True (spec 04.10)"
                )
        if self.suggested_local_adjustment and not self.adjustment_allowed:
            raise ValueError(
                "suggested_local_adjustment provided but adjustment_allowed=False"
            )


__all__ = [
    "CritiqueResult",
    "CritiqueType",
    "DEFAULT_MAX_LOCAL_CRITIQUE_PASSES",
    "LocalCritiqueInput",
    "LocalCritiqueReceipt",
]
