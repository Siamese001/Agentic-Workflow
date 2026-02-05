"""
Governance Shield Deterministic Layer

Extracted deterministic logic from GovernanceShieldAgent.
This module contains pure deterministic governance and risk validation.

Deterministic Operations:
- Risk level scanning (rule-based classification)
- Privacy language detection (keyword matching)
- Protocol generation (template-based)
- Basic governance rule validation
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class GovernanceResult:
    """Result of governance validation with deterministic scoring."""

    passed: bool
    issues: list[str]
    risk_level: str
    score: float | None = None
    protocol: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class GovernanceShieldDeterministic:
    """
    Pure deterministic governance and risk validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize with governance validation configuration.

        Args:
            config: Configuration dictionary containing governance rules
        """
        self.risk_keywords = config.get(
            "risk_keywords",
            {
                "high": ["guarantee", "always", "never", "promise", "commitment"],
                "medium": ["likely", "probably", "usually", "typically"],
                "low": ["may", "might", "could", "possibly", "potential"],
            },
        )
        self.privacy_patterns = config.get(
            "privacy_patterns",
            [
                r"\b(ssn|social security)\b",
                r"\b(credit card|cc number)\b",
                r"\b(password|pwd)\b",
                r"\b(private|confidential|secret)\b",
            ],
        )
        self.forbidden_patterns = config.get(
            "forbidden_patterns",
            [
                r"\b(money back|refund guaranteed)\b",
                r"\b(risk free|no risk)\b",
                r"\b(100%|perfect|always)\b",
            ],
        )
        self.protocol_templates = config.get(
            "protocol_templates",
            {
                "high": "HIGH_RISK_PROTOCOL: Immediate review required. Content: {content}",
                "medium": "MEDIUM_RISK_PROTOCOL: Manager review recommended. Content: {content}",
                "low": "LOW_RISK_PROTOCOL: Standard validation passed. Content: {content}",
            },
        )

    def scan_risk_level(self, content: str) -> GovernanceResult:
        """
        Scan content for risk level using deterministic keyword matching.

        Moved to Deterministic: Pure keyword-based risk classification
        """
        issues: list[str] = []
        risk_scores = {"high": 0, "medium": 0, "low": 0}

        content_lower = content.lower()

        # Count risk keywords (deterministic keyword matching)
        for level, keywords in self.risk_keywords.items():
            for keyword in keywords:
                matches = len(re.findall(rf"\b{re.escape(keyword)}\b", content_lower))
                risk_scores[level] += matches

        # Determine risk level (deterministic scoring logic)
        total_score = risk_scores["high"] * 3 + risk_scores["medium"] * 2 + risk_scores["low"] * 1

        if risk_scores["high"] >= 2 or total_score >= 5:
            risk_level = "high"
            issues.append(f"High risk detected: {risk_scores['high']} high-risk keywords")
        elif risk_scores["medium"] >= 3 or total_score >= 3:
            risk_level = "medium"
            issues.append(f"Medium risk detected: {risk_scores['medium']} medium-risk keywords")
        else:
            risk_level = "low"

        # Calculate risk score
        max_possible_score = sum(len(keywords) for keywords in self.risk_keywords.values())
        score = 1.0 - (total_score / max_possible_score) if max_possible_score > 0 else 1.0

        return GovernanceResult(
            passed=risk_level != "high",
            issues=issues,
            risk_level=risk_level,
            score=max(0.0, score),
            metadata={"validation_type": "deterministic", "risk_scores": risk_scores},
        )

    def detect_privacy_language(self, content: str) -> GovernanceResult:
        """
        Detect privacy-sensitive language using deterministic patterns.

        Moved to Deterministic: Pure regex pattern matching
        """
        issues: list[str] = []
        privacy_matches = []

        # Check privacy patterns (deterministic regex matching)
        for pattern in self.privacy_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            privacy_matches.extend(matches)

        if privacy_matches:
            issues.append(f"Privacy-sensitive language detected: {len(privacy_matches)} instances")
            issues.extend([f"- {match}" for match in set(privacy_matches)])

        # Calculate privacy risk score
        score = 1.0 - (len(privacy_matches) * 0.2)
        score = max(0.0, score)

        risk_level = "high" if len(privacy_matches) >= 3 else "medium" if privacy_matches else "low"

        return GovernanceResult(
            passed=len(privacy_matches) == 0,
            issues=issues,
            risk_level=risk_level,
            score=score,
            metadata={"validation_type": "deterministic", "privacy_matches": privacy_matches},
        )

    def check_forbidden_patterns(self, content: str) -> GovernanceResult:
        """
        Check for forbidden patterns using deterministic regex.

        Moved to Deterministic: Pure forbidden pattern detection
        """
        issues: list[str] = []
        forbidden_matches = []

        # Check forbidden patterns (deterministic regex matching)
        for pattern in self.forbidden_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            forbidden_matches.extend(matches)

        if forbidden_matches:
            issues.append(f"Forbidden patterns detected: {len(forbidden_matches)} instances")
            issues.extend([f"- {match}" for match in set(forbidden_matches)])

        # Calculate compliance score
        score = 1.0 - (len(forbidden_matches) * 0.3)
        score = max(0.0, score)

        risk_level = "high" if forbidden_matches else "low"

        return GovernanceResult(
            passed=len(forbidden_matches) == 0,
            issues=issues,
            risk_level=risk_level,
            score=score,
            metadata={"validation_type": "deterministic", "forbidden_matches": forbidden_matches},
        )

    def generate_safety_protocol(self, risk_level: str, content: str) -> GovernanceResult:
        """
        Generate safety protocol using deterministic templates.

        Moved to Deterministic: Pure template-based protocol generation
        """
        template = self.protocol_templates.get(risk_level, self.protocol_templates["low"])
        protocol = template.format(content=content[:200] + "..." if len(content) > 200 else content)

        return GovernanceResult(
            passed=True,
            issues=[],
            risk_level=risk_level,
            protocol=protocol,
            metadata={"validation_type": "deterministic", "protocol_type": "template"},
        )

    def audit_content_compliance(self, content: str) -> GovernanceResult:
        """
        Perform comprehensive content audit using deterministic rules.

        Combines all deterministic validation methods.
        """
        all_issues = []
        risk_levels = []
        scores = []

        # Risk level scan
        risk_result = self.scan_risk_level(content)
        all_issues.extend(risk_result.issues)
        risk_levels.append(risk_result.risk_level)
        if risk_result.score is not None:
            scores.append(risk_result.score)

        # Privacy language detection
        privacy_result = self.detect_privacy_language(content)
        all_issues.extend(privacy_result.issues)
        risk_levels.append(privacy_result.risk_level)
        if privacy_result.score is not None:
            scores.append(privacy_result.score)

        # Forbidden pattern check
        forbidden_result = self.check_forbidden_patterns(content)
        all_issues.extend(forbidden_result.issues)
        risk_levels.append(forbidden_result.risk_level)
        if forbidden_result.score is not None:
            scores.append(forbidden_result.score)

        # Determine overall risk level (deterministic logic)
        overall_risk = (
            "high" if "high" in risk_levels else "medium" if "medium" in risk_levels else "low"
        )

        # Calculate overall score
        overall_score = sum(scores) / len(scores) if scores else 1.0

        # Generate safety protocol
        protocol_result = self.generate_safety_protocol(overall_risk, content)

        return GovernanceResult(
            passed=overall_risk != "high" and len(all_issues) == 0,
            issues=all_issues,
            risk_level=overall_risk,
            score=overall_score,
            protocol=protocol_result.protocol,
            metadata={
                "validation_type": "deterministic",
                "component_risks": risk_levels,
                "total_issues": len(all_issues),
            },
        )

    def sanitize_claims(self, content: str) -> GovernanceResult:
        """
        Sanitize claims using deterministic rule-based logic.

        Moved to Deterministic: Pure claim sanitization rules
        """
        sanitized_content = content
        sanitizations = []

        # Replace absolute claims (deterministic replacement)
        absolute_patterns = {
            r"\balways\b": "typically",
            r"\bnever\b": "rarely",
            r"\bguaranteed\b": "expected",
            r"\b100%\b": "high",
            r"\bperfect\b": "excellent",
        }

        for pattern, replacement in absolute_patterns.items():
            matches = len(re.findall(pattern, sanitized_content, re.IGNORECASE))
            if matches > 0:
                sanitized_content = re.sub(
                    pattern, replacement, sanitized_content, flags=re.IGNORECASE
                )
                sanitizations.append(
                    f"Replaced {matches} instances of '{pattern}' with '{replacement}'"
                )

        # Calculate sanitization score
        score = 1.0 - (len(sanitizations) * 0.1)
        score = max(0.0, score)

        return GovernanceResult(
            passed=len(sanitizations) == 0,
            issues=sanitizations,
            risk_level="low",
            score=score,
            metadata={"validation_type": "deterministic", "sanitizations": sanitizations},
        )
