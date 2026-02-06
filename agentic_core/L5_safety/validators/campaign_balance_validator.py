"""
Campaign Balance Deterministic Layer

Moved from CampaignBalanceAgent - 100% deterministic logic extracted.
This module contains pure deterministic campaign balance validation.

Deterministic Operations:
- Ratio calculations
- Required field validation
- Threshold comparisons
- Balance rule processing
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BalanceResult:
    """Result of campaign balance validation."""

    passed: bool
    issues: list[str]
    ratio: float | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class CampaignBalanceValidator:
    """
    Pure deterministic campaign balance validation.

    All logic is 100% deterministic - no external dependencies or LLM calls.
    """

    def __init__(self, thresholds: dict[str, Any] | None = None) -> None:
        """
        Initialize with balance validation thresholds.

        Args:
            thresholds: Configuration for balance validation
        """
        self.thresholds = thresholds or {
            "max_leads_per_message": 100,
            "min_leads_per_message": 1,
        }

    def validate_campaign_balance(
        self, campaign: dict[str, Any], leads: list[Any], messages: list[Any]
    ) -> BalanceResult:
        """
        Validate campaign balance using purely deterministic logic.

        Args:
            campaign: Campaign data dictionary
            leads: List of lead objects
            messages: List of message objects

        Returns:
            BalanceResult with deterministic findings
        """
        issues: list[str] = []

        # Calculate lead-to-message ratio (deterministic arithmetic)
        ratio = self._calculate_lead_message_ratio(leads, messages)
        if ratio is not None:
            # Validate ratio against thresholds (deterministic comparison)
            ratio_issues = self._validate_ratio(ratio)
            issues.extend(ratio_issues)

        # Validate required campaign fields (deterministic existence checks)
        field_issues = self._validate_required_fields(campaign)
        issues.extend(field_issues)

        return BalanceResult(
            passed=len(issues) == 0,
            issues=issues,
            ratio=ratio,
            metadata={"validation_type": "deterministic"},
        )

    def _calculate_lead_message_ratio(self, leads: list[Any], messages: list[Any]) -> float | None:
        """
        Calculate lead-to-message ratio using deterministic arithmetic.

        Moved to Deterministic: Pure mathematical calculation
        """
        if not messages:
            return None

        lead_count = len(leads)
        message_count = len(messages)

        # Deterministic ratio calculation
        return lead_count / message_count

    def _validate_ratio(self, ratio: float) -> list[str]:
        """
        Validate ratio against deterministic thresholds.

        Moved to Deterministic: Pure comparison logic
        """
        issues: list[str] = []

        max_ratio = self.thresholds["max_leads_per_message"]
        min_ratio = self.thresholds["min_leads_per_message"]

        # Deterministic threshold comparisons
        if ratio > max_ratio:
            issues.append("Too many leads per message template")
        elif ratio < min_ratio:
            issues.append("More templates than leads")

        return issues

    def _validate_required_fields(self, campaign: dict[str, Any]) -> list[str]:
        """
        Validate required campaign fields using deterministic checks.

        Moved to Deterministic: Pure existence validation
        """
        issues: list[str] = []

        # Deterministic field existence checks
        if not campaign.get("name"):
            issues.append("Campaign missing name")

        if not campaign.get("goal"):
            issues.append("Campaign missing goal")

        return issues

    def calculate_balance_score(
        self, campaign: dict[str, Any], leads: list[Any], messages: list[Any]
    ) -> float:
        """
        Calculate overall balance score using deterministic algorithm.

        Returns:
            Float between 0.0 and 1.0 representing balance quality
        """
        score = 1.0

        # Deduct points for missing required fields
        if not campaign.get("name"):
            score -= 0.3

        if not campaign.get("goal"):
            score -= 0.3

        # Deduct points for ratio issues
        ratio = self._calculate_lead_message_ratio(leads, messages)
        if ratio is not None:
            max_ratio = self.thresholds["max_leads_per_message"]
            min_ratio = self.thresholds["min_leads_per_message"]

            if ratio > max_ratio:
                # Penalize based on how far over the limit
                excess_ratio = ratio - max_ratio
                score -= min(0.4, excess_ratio / max_ratio * 0.4)
            elif ratio < min_ratio:
                # Penalize based on how far under the minimum
                deficit_ratio = min_ratio - ratio
                score -= min(0.4, deficit_ratio / min_ratio * 0.4)

        return max(0.0, score)

    def suggest_improvements(
        self, campaign: dict[str, Any], leads: list[Any], messages: list[Any]
    ) -> list[str]:
        """
        Generate deterministic improvement suggestions.

        Returns:
            List of actionable improvement suggestions
        """
        suggestions: list[str] = []

        # Check for missing fields
        if not campaign.get("name"):
            suggestions.append("Add a descriptive campaign name")

        if not campaign.get("goal"):
            suggestions.append("Define a clear campaign goal")

        # Check ratio issues
        ratio = self._calculate_lead_message_ratio(leads, messages)
        if ratio is not None:
            max_ratio = self.thresholds["max_leads_per_message"]
            min_ratio = self.thresholds["min_leads_per_message"]

            if ratio > max_ratio:
                needed_messages = len(leads) // max_ratio + 1
                suggestions.append(f"Create {needed_messages - len(messages)} more message templates")

            elif ratio < min_ratio:
                needed_leads = len(messages) * min_ratio
                suggestions.append(f"Add {needed_leads - len(leads)} more leads or remove templates")

        return suggestions
