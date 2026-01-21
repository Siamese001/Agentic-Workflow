from __future__ import annotations

"""Constitutional AI System for Safety and Alignment.

Phase 1 - Pillar 9: Safety & Policy (Control Plane & Guardrails)
Migrated from archives/engines/legacy_engines/ConstitutionalAiSystem.py
"""

import logging
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

Logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of constitutional rules."""
    SAFETY = "safety"
    ETHICS = "ethics"
    PRIVACY = "privacy"
    BIAS = "bias"
    LEGAL = "legal"
    QUALITY = "quality"


class RuleSeverity(Enum):
    """Severity levels for rule violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationType(Enum):
    """Types of constitutional violations."""
    CONTENT = "content"
    STYLE = "style"
    STRUCTURE = "structure"
    CONTEXT = "context"


@dataclass
class ConstitutionalRule:
    """Individual constitutional rule."""
    rule_id: str
    RuleType: RuleType
    title: str
    description: str
    pattern: str
    Severity: RuleSeverity
    action: str
    replacement: str | None = None


@dataclass
class ViolationReport:
    """Report of constitutional Violation."""
    rule_id: str
    ViolationType: ViolationType
    Severity: RuleSeverity
    location: str
    content: str
    suggestion: str
    confidence: float


@dataclass
class ConstitutionalReviewResult:
    """Result of constitutional review."""
    is_compliant: bool
    violations: list[ViolationReport]
    compliance_score: float
    recommendations: list[str]
    reviewed_at: float


class ConstitutionalAISystem:
    """Constitutional AI System for Safety and Alignment.

    Provides rule-based validation, ethical guidelines,
    and content compliance checking.
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize Constitutional AI system.

        Args:
            enable_logging: Enable logging of violations
        """
        self.enable_logging = enable_logging
        self.rules: dict[str, ConstitutionalRule] = {}
        self.rule_patterns: dict[RuleType, list[ConstitutionalRule]] = {
            rt: [] for rt in RuleType
        }
        self._load_default_rules()

    def add_rule(self, rule: ConstitutionalRule) -> None:
        """Add a constitutional rule.

        Args:
            rule: Rule to add
        """
        self.rules[rule.rule_id] = rule
        self.rule_patterns[rule.RuleType].append(rule)

        if self.enable_logging:
            Logger.debug(f"Added constitutional rule: {rule.rule_id}")

    def remove_rule(self, rule_id: str) -> None:
        """Remove a constitutional rule.

        Args:
            rule_id: ID of rule to remove
        """
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            self.rule_patterns[rule.RuleType].remove(rule)
            del self.rules[rule_id]

            if self.enable_logging:
                Logger.debug(f"Removed constitutional rule: {rule_id}")

    def review_content(
        self,
        content: str,
        context: dict[str, any] | None = None,
    ) -> ConstitutionalReviewResult:
        """Review content against constitutional rules.

        Args:
            content: Content to review
            context: Optional context for evaluation

        Returns:
            ConstitutionalReviewResult with violations and recommendations
        """
        if not content:
            return ConstitutionalReviewResult(
                is_compliant=True,
                violations=[],
                compliance_score=1.0,
                recommendations=[],
                reviewed_at=time.time(),
            )

        violations = self._check_compliance(content, context)

        is_compliant = len(violations) == 0
        compliance_score = self._calculate_compliance_score(violations)
        recommendations = self._generate_recommendations(violations)

        if self.enable_logging and violations:
            Logger.warning(
                "constitutional_violations",
                extra={
                    "violation_count": len(violations),
                    "compliance_score": compliance_score,
                    "critical_count": sum(
                        1 for v in violations
                        if v.Severity == RuleSeverity.CRITICAL
                    ),
                }
            )

        return ConstitutionalReviewResult(
            is_compliant=is_compliant,
            violations=violations,
            compliance_score=compliance_score,
            recommendations=recommendations,
            reviewed_at=time.time(),
        )

    def _check_compliance(
        self,
        content: str,
        context: dict[str, any] | None = None,
    ) -> list[ViolationReport]:
        """Check content against all rules.

        Args:
            content: Content to check
            context: Optional context

        Returns:
            List of violations
        """
        violations = []

        for rule in self.rules.values():
            rule_violations = self._check_rule(content, rule, context)
            violations.extend(rule_violations)

        severity_order = {
            RuleSeverity.CRITICAL: 0,
            RuleSeverity.HIGH: 1,
            RuleSeverity.MEDIUM: 2,
            RuleSeverity.LOW: 3,
        }

        violations.sort(key=lambda v: severity_order.get(v.Severity, 4))

        return violations

    def _check_rule(
        self,
        content: str,
        rule: ConstitutionalRule,
        context: dict[str, any] | None = None,
    ) -> list[ViolationReport]:
        """Check content against a specific rule.

        Args:
            content: Content to check
            rule: Rule to apply
            context: Optional context

        Returns:
            List of violations for this rule
        """
        violations = []

        try:
            matches = re.finditer(rule.pattern, content, re.IGNORECASE)

            for match in matches:
                Violation = ViolationReport(
                    rule_id=rule.rule_id,
                    ViolationType=ViolationType.CONTENT,
                    Severity=rule.Severity,
                    location=f"Position {match.Span()}",
                    content=match.group(),
                    suggestion=rule.replacement or f"Remove or rephrase: {match.group()}",
                    confidence=0.9,
                )
                violations.append(Violation)

        except re.error as e:
            if self.enable_logging:
                Logger.error(
                    f"Invalid regex pattern in rule {rule.rule_id}: {e}"
                )

        return violations

    def _calculate_compliance_score(self, violations: list[ViolationReport]) -> float:
        """Calculate compliance score based on violations.

        Args:
            violations: List of violations

        Returns:
            Compliance score (0.0-1.0)
        """
        if not violations:
            return 1.0

        severity_weights = {
            RuleSeverity.CRITICAL: 1.0,
            RuleSeverity.HIGH: 0.7,
            RuleSeverity.MEDIUM: 0.4,
            RuleSeverity.LOW: 0.2,
        }

        total_penalty = sum(
            severity_weights.get(v.Severity, 0.5) for v in violations
        )

        score = max(0.0, 1.0 - (total_penalty / 10.0))

        return round(score, 2)

    def _generate_recommendations(
        self,
        violations: list[ViolationReport],
    ) -> list[str]:
        """Generate recommendations based on violations.

        Args:
            violations: List of violations

        Returns:
            List of recommendations
        """
        if not violations:
            return ["Content is compliant with all constitutional rules"]

        recommendations = []

        violation_by_type = defaultdict(list)
        for v in violations:
            violation_by_type[v.Severity].append(v)

        if RuleSeverity.CRITICAL in violation_by_type:
            recommendations.append(
                f"CRITICAL: Address {len(violation_by_type[RuleSeverity.CRITICAL])} "
                "critical violations immediately"
            )

        if RuleSeverity.HIGH in violation_by_type:
            recommendations.append(
                f"HIGH: Review {len(violation_by_type[RuleSeverity.HIGH])} "
                "high-Severity violations"
            )

        unique_rules = {v.rule_id for v in violations}
        if len(unique_rules) <= 3:
            for rule_id in unique_rules:
                rule = self.rules.get(rule_id)
                if rule:
                    recommendations.append(f"Review rule: {rule.title}")

        return recommendations

    def _load_default_rules(self) -> None:
        """Load default constitutional rules."""
        default_rules = [
            ConstitutionalRule(
                rule_id="safety_001",
                RuleType=RuleType.SAFETY,
                title="No harmful content",
                description="Prevent harmful or dangerous content",
                pattern=r'\b(kill|harm|attack|destroy)\b',
                Severity=RuleSeverity.CRITICAL,
                action="block",
            ),
            ConstitutionalRule(
                rule_id="privacy_001",
                RuleType=RuleType.PRIVACY,
                title="No PII exposure",
                description="Prevent exposure of personal information",
                pattern=r'\b\d{3}-\d{2}-\d{4}\b',
                Severity=RuleSeverity.HIGH,
                action="block",
            ),
            ConstitutionalRule(
                rule_id="ethics_001",
                RuleType=RuleType.ETHICS,
                title="No deceptive content",
                description="Prevent misleading or deceptive content",
                pattern=r'\b(fake|fraud|scam|trick)\b',
                Severity=RuleSeverity.MEDIUM,
                action="warn",
            ),
        ]

        for rule in default_rules:
            self.add_rule(rule)


def review_content(content: str, context: dict[str, any] | None = None) -> ConstitutionalReviewResult:
    """Convenience function to review content.

    Args:
        content: Content to review
        context: Optional context

    Returns:
        ConstitutionalReviewResult
    """
    system = ConstitutionalAISystem()
    return system.review_content(content, context)
