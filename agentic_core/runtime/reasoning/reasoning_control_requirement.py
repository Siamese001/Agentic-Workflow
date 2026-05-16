"""ReasoningControlRequirement semantics — binds receipt state to consequences."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RequirementLevel(str, Enum):
    OPTIONAL = "OPTIONAL"
    REQUIRED = "REQUIRED"
    POLICY_REQUIRED = "POLICY_REQUIRED"
    QUALITY_REQUIRED = "QUALITY_REQUIRED"


class AllowedSurface(str, Enum):
    TRANSPORT = "TRANSPORT"
    PROMPT = "PROMPT"
    ORCHESTRATION = "ORCHESTRATION"
    POLICY = "POLICY"


class DowngradeDisposition(str, Enum):
    WARN = "WARN"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class ReceiptState(str, Enum):
    APPLIED = "APPLIED"
    DEGRADED = "DEGRADED"
    UNSUPPORTED = "UNSUPPORTED"
    IGNORED = "IGNORED"


@dataclass(frozen=True, slots=True)
class ReasoningControlRequirement:
    """Per-control governance metadata (declared upstream; resolver may narrow)."""

    control_name: str
    requested: bool
    requirement_level: RequirementLevel
    allowed_surfaces: frozenset[AllowedSurface]
    fallback_allowed: bool
    downgrade_disposition: DowngradeDisposition
    decisive_reason_when_not_applied: str


__all__ = [
    "AllowedSurface",
    "DowngradeDisposition",
    "ReasoningControlRequirement",
    "ReceiptState",
    "RequirementLevel",
]
