from __future__ import annotations

"""
Constitutional Governance Guardrail - Consolidated Constitutional AI

Merges:
- ConstitutionalReviewer
- constitutional_ai
- constitutional_overseer

Composable Rules:
- constitutional_review: Constitutional principle checks
- governance: Governance rule enforcement
- oversight: Oversight and audit trails
"""


import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConstitutionalPrinciple(Enum):
    """Core constitutional principles."""

    HELPFULNESS = "helpfulness"
    HARMLESSNESS = "harmlessness"
    HONESTY = "honesty"
    TRANSPARENCY = "transparency"
    PRIVACY = "privacy"
    FAIRNESS = "fairness"
    ACCOUNTABILITY = "accountability"


@dataclass
class PrincipleViolation:
    """Violation of a constitutional principle."""

    principle: ConstitutionalPrinciple
    severity: str  # "minor", "moderate", "severe"
    description: str
    suggested_revision: str | None = None


@dataclass
class GovernanceResult:
    """Result of governance check."""

    compliant: bool
    violations: list[PrincipleViolation] = field(default_factory=list)
    audit_id: str | None = None
    review_notes: str = ""


class ConstitutionalGovernanceGuardrail:
    """
    Consolidated Constitutional Governance Guardrail.

    Provides unified constitutional AI with:
    - Constitutional principle enforcement
    - Governance rule checking
    - Oversight and audit trails
    """

    def __init__(self):
        """Initialize constitutional governance guardrail."""
        self.enabled_rules: list[str] = [
            "constitutional_review",
            "governance",
            "oversight",
        ]

        # Constitutional principles with detection patterns
        self.principle_checks = {
            ConstitutionalPrinciple.HARMLESSNESS: {
                "negative_patterns": [
                    "harm",
                    "hurt",
                    "damage",
                    "destroy",
                    "kill",
                    "attack",
                    "exploit",
                    "abuse",
                ],
                "weight": 1.0,
            },
            ConstitutionalPrinciple.HONESTY: {
                "negative_patterns": ["lie", "deceive", "mislead", "fake", "pretend to be"],
                "weight": 0.9,
            },
            ConstitutionalPrinciple.PRIVACY: {
                "negative_patterns": ["personal data", "private information", "ssn", "password"],
                "weight": 0.8,
            },
            ConstitutionalPrinciple.FAIRNESS: {
                "negative_patterns": ["discriminate", "bias against", "unfair"],
                "weight": 0.8,
            },
        }

        # Audit log
        self.audit_log: list[dict[str, Any]] = []
        self.audit_counter = 0

        # Statistics
        self.reviews_performed = 0
        self.violations_found = 0
        self.revisions_suggested = 0

    async def review(self, content: str, context: dict[str, Any] | None = None) -> GovernanceResult:
        """
        Review content for constitutional compliance.

        Args:
            content: Content to review
            context: Optional context

        Returns:
            GovernanceResult
        """
        self.reviews_performed += 1
        violations = []

        # Apply constitutional review
        if "constitutional_review" in self.enabled_rules:
            violations.extend(self._check_principles(content))

        # Apply governance rules
        if "governance" in self.enabled_rules:
            violations.extend(self._check_governance(content, context))

        # Create audit trail
        audit_id = None
        if "oversight" in self.enabled_rules:
            audit_id = self._create_audit(content, violations)

        self.violations_found += len(violations)

        return GovernanceResult(
            compliant=len(violations) == 0,
            violations=violations,
            audit_id=audit_id,
            review_notes=self._generate_notes(violations),
        )

    def _check_principles(self, content: str) -> list[PrincipleViolation]:
        """Check content against constitutional principles."""
        violations = []
        content_lower = content.lower()

        for principle, config in self.principle_checks.items():
            for pattern in config["negative_patterns"]:
                if pattern in content_lower:
                    violations.append(
                        PrincipleViolation(
                            principle=principle,
                            severity="moderate",
                            description=f"Potential violation of {principle.value}: contains '{pattern}'",
                            suggested_revision=f"Consider removing or rephrasing content containing '{pattern}'",
                        )
                    )
                    self.revisions_suggested += 1
                    break  # One violation per principle

        return violations

    def _check_governance(self, content: str, context: dict[str, Any] | None) -> list[PrincipleViolation]:
        """Check governance rules."""
        violations = []

        # Check content length governance
        if len(content) > 10000:
            violations.append(
                PrincipleViolation(
                    principle=ConstitutionalPrinciple.TRANSPARENCY,
                    severity="minor",
                    description="Content exceeds governance length limit",
                )
            )

        return violations

    def _create_audit(self, content: str, violations: list[PrincipleViolation]) -> str:
        """Create audit trail entry."""
        self.audit_counter += 1
        audit_id = f"audit_{self.audit_counter}_{int(time.time())}"

        self.audit_log.append(
            {
                "audit_id": audit_id,
                "timestamp": time.time(),
                "content_length": len(content),
                "violation_count": len(violations),
                "violations": [
                    {
                        "principle": v.principle.value,
                        "severity": v.severity,
                        "description": v.description,
                    }
                    for v in violations
                ],
            }
        )

        return audit_id

    def _generate_notes(self, violations: list[PrincipleViolation]) -> str:
        """Generate review notes."""
        if not violations:
            return "Content is compliant with constitutional principles."

        notes = []
        for v in violations:
            notes.append(f"- {v.principle.value}: {v.description}")

        return "\n".join(notes)

    def revise_content(self, content: str, violations: list[PrincipleViolation]) -> str:
        """
        Suggest revised content based on violations.

        Args:
            content: Original content
            violations: List of violations

        Returns:
            Revised content suggestion
        """
        # Simple revision - add disclaimer
        if violations:
            return f"[REVISED] {content}\n\n[Note: Content was flagged for potential issues with: {', '.join(v.principle.value for v in violations)}]"
        return content

    def get_audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent audit log entries."""
        return self.audit_log[-limit:]

    def get_statistics(self) -> dict[str, Any]:
        """Get governance statistics."""
        return {
            "reviews_performed": self.reviews_performed,
            "violations_found": self.violations_found,
            "revisions_suggested": self.revisions_suggested,
            "audit_log_size": len(self.audit_log),
            "compliance_rate": (
                (self.reviews_performed - self.violations_found) / self.reviews_performed * 100
            )
            if self.reviews_performed > 0
            else 100,
        }
