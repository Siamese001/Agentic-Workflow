"""
Lead Quality Validator - Deterministic Lead Quality Validation

Zero-Ambiguity Standard: Renamed from lead_quality_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_maintenance/deterministic to L5_safety/validators.

Deterministic Operations:
- Required field validation (existence checks)
- Contact information validation (field presence)
- Email domain validation (pattern matching)
- Spam indicator detection (keyword matching)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LeadQualityResult:
    """Result of lead quality validation."""

    passed: bool
    issues: list[str]
    score: float | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class LeadQualityValidator:
    """
    Pure deterministic lead quality validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """
        Initialize with lead quality validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        """
        config = config or {}
        self.required_fields = config.get("required_fields", ["company"])
        self.contact_fields = config.get("contact_fields", ["contact_name", "email"])
        self.suspicious_domains = config.get(
            "suspicious_domains",
            [".xyz", ".top", ".click", ".link", ".work", ".date"],
        )
        self.spam_indicators = config.get(
            "spam_indicators",
            ["test@", "noreply@", "donotreply@", "spam@"],
        )

    def validate_lead_quality(self, leads: list[dict[str, Any]]) -> LeadQualityResult:
        """
        Validate lead quality using purely deterministic logic.

        Args:
            leads: List of lead dictionaries

        Returns:
            LeadQualityResult with deterministic findings
        """
        if not leads:
            return LeadQualityResult(
                passed=True,
                issues=[],
                score=1.0,
                metadata={"validation_type": "deterministic", "lead_count": 0},
            )

        issues: list[str] = []

        for i, lead in enumerate(leads):
            # Check required fields (deterministic existence checks)
            field_issues = self._check_required_fields(lead, i)
            issues.extend(field_issues)

            # Check contact information (deterministic field presence)
            contact_issues = self._check_contact_info(lead, i)
            issues.extend(contact_issues)

            # Check email domain (deterministic pattern matching)
            email_issues = self._check_email_domain(lead, i)
            issues.extend(email_issues)

            # Check spam indicators (deterministic keyword matching)
            spam_issues = self._check_spam_indicators(lead, i)
            issues.extend(spam_issues)

        # Calculate quality score
        score = self._calculate_quality_score(issues, len(leads))

        return LeadQualityResult(
            passed=len(issues) == 0,
            issues=issues,
            score=score,
            metadata={"validation_type": "deterministic", "lead_count": len(leads)},
        )

    def _check_required_fields(self, lead: dict[str, Any], lead_index: int) -> list[str]:
        """
        Check required fields using deterministic existence checks.

        Moved to Deterministic: Pure field existence validation
        """
        issues: list[str] = []

        for field in self.required_fields:
            if not lead.get(field):
                issues.append(f"Lead {lead_index}: Missing {field}")

        return issues

    def _check_contact_info(self, lead: dict[str, Any], lead_index: int) -> list[str]:
        """
        Check contact information using deterministic field presence.

        Moved to Deterministic: Pure field presence validation
        """
        issues: list[str] = []

        # At least one contact field must be present
        has_contact = any(lead.get(field) for field in self.contact_fields)
        if not has_contact:
            issues.append(f"Lead {lead_index}: Missing contact info")

        return issues

    def _check_email_domain(self, lead: dict[str, Any], lead_index: int) -> list[str]:
        """
        Check email domain using deterministic pattern matching.

        Moved to Deterministic: Pure domain validation
        """
        issues: list[str] = []

        email = lead.get("email", "")
        if email:
            for domain in self.suspicious_domains:
                if email.endswith(domain):
                    issues.append(f"Lead {lead_index}: Suspicious email domain")
                    break

        return issues

    def _check_spam_indicators(self, lead: dict[str, Any], lead_index: int) -> list[str]:
        """
        Check spam indicators using deterministic keyword matching.

        Moved to Deterministic: Pure keyword matching
        """
        issues: list[str] = []

        email = lead.get("email", "").lower()
        if email:
            for indicator in self.spam_indicators:
                if indicator in email:
                    issues.append(f"Lead {lead_index}: Spam indicator in email")
                    break

        return issues

    def _calculate_quality_score(self, issues: list[str], lead_count: int) -> float:
        """
        Calculate quality score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        """
        if lead_count == 0:
            return 1.0

        # Base score starts at 1.0
        base_score = 1.0

        # Deduct points for each issue relative to lead count
        issue_penalty = (len(issues) / lead_count) * 0.5
        base_score -= issue_penalty

        return max(0.0, min(1.0, base_score))

    def validate_single_lead(self, lead: dict[str, Any]) -> LeadQualityResult:
        """
        Validate a single lead for quality issues.

        Convenience method for single lead validation.
        """
        return self.validate_lead_quality([lead])

    def get_lead_completeness(self, lead: dict[str, Any]) -> float:
        """
        Calculate lead completeness score.

        Moved to Deterministic: Pure completeness calculation
        """
        all_fields = self.required_fields + self.contact_fields
        present_fields = sum(1 for field in all_fields if lead.get(field))
        return present_fields / len(all_fields) if all_fields else 1.0

    def analyze_lead_risk(self, lead: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze lead risk using deterministic rules.

        Returns detailed risk analysis for a lead.
        """
        email = lead.get("email", "")

        # Check for suspicious domain
        has_suspicious_domain = any(email.endswith(d) for d in self.suspicious_domains)

        # Check for spam indicators
        has_spam_indicator = any(ind in email.lower() for ind in self.spam_indicators)

        # Calculate completeness
        completeness = self.get_lead_completeness(lead)

        # Calculate risk score
        risk_score = 0
        if has_suspicious_domain:
            risk_score += 3
        if has_spam_indicator:
            risk_score += 5
        if completeness < 0.5:
            risk_score += 2

        risk_level = "low" if risk_score == 0 else "medium" if risk_score < 5 else "high"

        return {
            "has_suspicious_domain": has_suspicious_domain,
            "has_spam_indicator": has_spam_indicator,
            "completeness": completeness,
            "risk_score": risk_score,
            "risk_level": risk_level,
        }
