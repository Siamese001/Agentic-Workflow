"""apps_rg prerequisite gate — historical research briefing validator."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

__all__ = [
    "BriefingValidationResult",
    "BriefingCheck",
    "HistoricalBriefingValidator",
    "check_briefing_prerequisite",
]

_REQUIRES_RESEARCH_STATUSES = frozenset({
    "missing",
    "stale",
    "incomplete",
    "scope_mismatch",
})


class BriefingValidationResult(str, Enum):
    """Possible outcomes of briefing prerequisite validation."""

    VALID = "valid"
    MISSING = "missing"
    STALE = "stale"
    POLICY_MISMATCH = "policy_mismatch"
    BLUEPRINT_MISMATCH = "blueprint_mismatch"
    SCOPE_MISMATCH = "scope_mismatch"
    INCOMPLETE = "incomplete"


@dataclass
class BriefingCheck:
    """Result of a briefing prerequisite check."""

    result: BriefingValidationResult
    briefing: Optional[dict[str, Any]]
    reason: str = ""
    freshness_hours: Optional[float] = None

    @property
    def is_valid(self) -> bool:
        return self.result == BriefingValidationResult.VALID

    @property
    def requires_apps_research(self) -> bool:
        return self.result.value in _REQUIRES_RESEARCH_STATUSES


class HistoricalBriefingValidator:
    """Validates that a company research briefing meets prerequisite policy.

    Parameters
    ----------
    max_freshness_hours:
        Briefings older than this (in hours) are considered stale.
    required_sections:
        Section keys that must be present in a non-stale briefing.
    """

    DEFAULT_MAX_FRESHNESS_HOURS: float = 168.0  # 7 days
    DEFAULT_REQUIRED_SECTIONS: frozenset[str] = frozenset({
        "company_overview",
        "role_context",
    })

    def __init__(
        self,
        *,
        max_freshness_hours: float = DEFAULT_MAX_FRESHNESS_HOURS,
        required_sections: Optional[frozenset[str]] = None,
        policy_hash: str = "",
    ) -> None:
        self.max_freshness_hours = max_freshness_hours
        self.required_sections = required_sections or self.DEFAULT_REQUIRED_SECTIONS
        self.policy_hash = policy_hash

    def validate(
        self,
        briefing: Optional[dict[str, Any]],
        *,
        target_company: str = "",
        target_role: str = "",
    ) -> BriefingCheck:
        """Validate a briefing dict and return a BriefingCheck."""
        if briefing is None:
            return BriefingCheck(
                result=BriefingValidationResult.MISSING,
                briefing=None,
                reason="No briefing provided",
            )

        # Policy hash check
        if self.policy_hash:
            bp_hash = briefing.get("policy_hash", "")
            if bp_hash and bp_hash != self.policy_hash:
                return BriefingCheck(
                    result=BriefingValidationResult.POLICY_MISMATCH,
                    briefing=briefing,
                    reason=f"Policy hash mismatch: expected {self.policy_hash!r}, got {bp_hash!r}",
                )

        # Blueprint/company mismatch
        if target_company:
            brief_company = briefing.get("company", "") or briefing.get("target_company", "")
            if brief_company and brief_company.lower() != target_company.lower():
                return BriefingCheck(
                    result=BriefingValidationResult.BLUEPRINT_MISMATCH,
                    briefing=briefing,
                    reason=f"Briefing company {brief_company!r} != target {target_company!r}",
                )

        # Freshness check
        import datetime
        generated_at = briefing.get("generated_at") or briefing.get("created_at")
        freshness_hours: Optional[float] = None
        if generated_at:
            try:
                if isinstance(generated_at, str):
                    ts = datetime.datetime.fromisoformat(
                        generated_at.replace("Z", "+00:00")
                    )
                else:
                    ts = generated_at
                now = datetime.datetime.now(datetime.timezone.utc)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=datetime.timezone.utc)
                age_hours = (now - ts).total_seconds() / 3600
                freshness_hours = age_hours
                if age_hours > self.max_freshness_hours:
                    return BriefingCheck(
                        result=BriefingValidationResult.STALE,
                        briefing=briefing,
                        reason=f"Briefing is {age_hours:.1f}h old (limit: {self.max_freshness_hours}h)",
                        freshness_hours=age_hours,
                    )
            except Exception:
                pass

        # Required sections
        missing = self.required_sections - set(briefing.keys())
        if missing:
            return BriefingCheck(
                result=BriefingValidationResult.INCOMPLETE,
                briefing=briefing,
                reason=f"Missing required sections: {sorted(missing)}",
                freshness_hours=freshness_hours,
            )

        return BriefingCheck(
            result=BriefingValidationResult.VALID,
            briefing=briefing,
            reason="Briefing is valid",
            freshness_hours=freshness_hours,
        )


def check_briefing_prerequisite(
    briefing: Optional[dict[str, Any]],
    *,
    target_company: str = "",
    target_role: str = "",
    max_freshness_hours: float = HistoricalBriefingValidator.DEFAULT_MAX_FRESHNESS_HOURS,
) -> BriefingCheck:
    """Convenience wrapper — validates a briefing with default policy."""
    validator = HistoricalBriefingValidator(max_freshness_hours=max_freshness_hours)
    return validator.validate(
        briefing,
        target_company=target_company,
        target_role=target_role,
    )
