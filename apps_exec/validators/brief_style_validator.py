"""
L5 Brief Validation + Style Gates — apps_exec.enterprise.

Validates brief content against style standards,
detects unsupported claims, and enforces quality thresholds.

Layer 5 Safety: Static analysis, policy enforcement, quality gates.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_verifies_policy,
)
from tqdm import tqdm

_log = logging.getLogger(__name__)


class ViolationSeverity(str, Enum):
    """Severity of validation violation."""

    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"


@dataclass(frozen=True)
class StyleViolation:
    """A style validation violation."""

    violation_id: str
    rule_id: str
    check_id: str
    severity: ViolationSeverity
    message: str
    suggestion: str


@dataclass
class BriefValidationResult:
    """Result of brief validation."""

    passed: bool
    violations: list[StyleViolation] = field(default_factory=list)
    style_metrics: dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    readability_score: float = 0.0
    evidence_score: float = 0.0


class StyleValidator:
    """L5 validator for brief style and quality."""

    # Buzzwords to detect
    BUZZWORDS: frozenset[str] = frozenset(
        {
            "game-changer",
            "synergy",
            "leverage",
            "holistic",
            "paradigm shift",
            "thought leader",
            "disruptive",
            "innovative",
            "cutting-edge",
            "world-class",
            "best-in-class",
            "next-generation",
            "state-of-the-art",
        }
    )

    # Unsupported claim patterns
    UNSUPPORTED_CLAIM_PATTERNS: list[re.Pattern] = [
        re.compile(r"\b(first\s+(?:and\s+only|ever))\b", re.IGNORECASE),
        re.compile(r"\b(unique\s+(?:in\s+(?:the\s+)?world|globally))\b", re.IGNORECASE),
        re.compile(r"\b(?:guaranteed|assured)\s+(?:to\s+)?(?:success|results?)\b", re.IGNORECASE),
        re.compile(r"\b(?:unprecedented|unmatched)\s+(?:in\s+(?:the\s+)?industry)\b", re.IGNORECASE),
    ]

    def __init__(self) -> None:
        self._violation_counter = 0

    def validate(
        self,
        brief_content: str,
        brief_metadata: dict[str, Any],
        target_audience: str,
    ) -> BriefValidationResult:
        """Validate brief content against style standards."""
        _emit_records_execution_trace("enterprise", "StyleValidator", "validate_start")

        violations: list[StyleViolation] = []

        # Check buzzword density
        buzzword_violations = self._check_buzzwords(brief_content)
        violations.extend(buzzword_violations)

        # Check for unsupported claims
        claim_violations = self._check_unsupported_claims(brief_content)
        violations.extend(claim_violations)

        # Check for empty sections
        empty_violations = self._check_empty_sections(brief_content)
        violations.extend(empty_violations)

        # Check evidence anchors
        evidence_result = self._check_evidence_anchors(brief_content)

        # Calculate style metrics
        style_metrics = self._calculate_style_metrics(brief_content)

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            violations,
            style_metrics,
            evidence_result,
        )

        # Determine pass/fail
        blocking_count = len([v for v in violations if v.severity == ViolationSeverity.BLOCKING])
        passed = blocking_count == 0 and quality_score >= 0.70

        _emit_applies_guardrail("enterprise", "StyleValidator", "validation_complete")

        return BriefValidationResult(
            passed=passed,
            violations=violations,
            style_metrics=style_metrics,
            quality_score=quality_score,
            readability_score=style_metrics.get("readability_score", 0.0),
            evidence_score=evidence_result.get("score", 0.0),
        )

    def _check_buzzwords(self, content: str) -> list[StyleViolation]:
        """Check for buzzword violations."""
        violations: list[StyleViolation] = []
        content_lower = content.lower()

        # Count buzzwords
        buzzword_count = 0
        for buzzword in self.BUZZWORDS:
            count = content_lower.count(buzzword.lower())
            buzzword_count += count

        # Calculate density (per 100 words)
        total_words = len(content.split())
        density = (buzzword_count / max(total_words, 1)) * 100

        # Check threshold
        if density > 5.0:
            self._violation_counter += 1
            violations.append(
                StyleViolation(
                    violation_id=f"V{self._violation_counter:03d}",
                    rule_id="STYLE_BUZZWORD_DENSITY",
                    check_id="buzzwords",
                    severity=ViolationSeverity.BLOCKING,
                    message=f"Buzzword density {density:.1f}% exceeds 5% threshold",
                    suggestion="Replace buzzwords with specific, concrete language",
                ),
            )
        elif buzzword_count > 0:
            self._violation_counter += 1
            violations.append(
                StyleViolation(
                    violation_id=f"V{self._violation_counter:03d}",
                    rule_id="STYLE_BUZZWORD_DENSITY",
                    check_id="buzzwords",
                    severity=ViolationSeverity.WARNING,
                    message=f"{buzzword_count} buzzwords detected",
                    suggestion="Consider replacing with more specific terms",
                ),
            )

        return violations

    def _check_unsupported_claims(self, content: str) -> list[StyleViolation]:
        """Check for unsupported absolute claims."""
        violations: list[StyleViolation] = []

        for pattern in tqdm(self.UNSUPPORTED_CLAIM_PATTERNS, desc="Processing", unit="item"):
            matches = pattern.findall(content)
            for match in tqdm(matches, desc="Processing", unit="item"):
                self._violation_counter += 1
                violations.append(
                    StyleViolation(
                        violation_id=f"V{self._violation_counter:03d}",
                        rule_id="STYLE_UNSUPPORTED_CLAIM",
                        check_id="absolute_claims",
                        severity=ViolationSeverity.BLOCKING,
                        message=f"Unsupported claim detected: '{match}'",
                        suggestion="Remove or provide concrete evidence for this claim",
                    ),
                )

        return violations

    def _check_empty_sections(self, content: str) -> list[StyleViolation]:
        """Check for sections with empty body."""
        violations: list[StyleViolation] = []

        # Parse sections (assumes markdown ## headers)
        sections = re.split(r"\n##\s+", content)

        for section in tqdm(sections[1:], desc="Processing", unit="item"):  # Skip preamble
            lines = section.strip().split("\n")
            if len(lines) < 2 or not lines[1].strip():
                self._violation_counter += 1
                section_title = lines[0][:30] if lines else "Unknown"
                violations.append(
                    StyleViolation(
                        violation_id=f"V{self._violation_counter:03d}",
                        rule_id="STYLE_EMPTY_BODY",
                        check_id=f"section_{section_title}",
                        severity=ViolationSeverity.BLOCKING,
                        message=f"Section '{section_title}' has empty body",
                        suggestion="Add substantive content to this section",
                    ),
                )

        return violations

    def _check_evidence_anchors(self, content: str) -> dict[str, Any]:
        """Check for evidence anchors in the content."""
        # Evidence patterns
        evidence_patterns = [
            r"\b(?:test coverage|benchmark|performance|latency|throughput)\b",
            r"\b(?:determinism|governance|audit|compliance)\b",
            r"\b(?:security|scalability|reliability)\b",
            r"\d+\s*(?:ms|milliseconds|seconds|req/s|rps|tps)",
            r"\d+\.?\d*%",
        ]

        evidence_count = 0
        for pattern in evidence_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            evidence_count += len(matches)

        # Calculate evidence score
        total_words = len(content.split())
        evidence_density = evidence_count / max(total_words / 100, 1)

        # Score: 1.0 if at least 5 evidence markers per 100 words
        score = min(1.0, evidence_density / 5.0)

        return {
            "count": evidence_count,
            "density": evidence_density,
            "score": score,
            "sufficient": score >= 0.6,
        }

    def _calculate_style_metrics(self, content: str) -> dict[str, Any]:
        """Calculate various style metrics."""
        words = content.split()
        sentences = re.split(r"[.!?]+", content)

        total_words = len(words)
        total_sentences = len([s for s in sentences if s.strip()])

        # Average sentence length
        avg_sentence_length = total_words / max(total_sentences, 1)

        # Readability (simple Flesch-inspired metric)
        # Higher is better (easier to read)
        # 100 = very easy, 0 = very difficult
        readability = max(0, 100 - (avg_sentence_length - 15) * 2)

        # Passive voice detection (simple heuristic)
        passive_indicators = ["was", "were", "been", "being", "is", "are"]
        passive_count = sum(1 for word in words if word.lower() in passive_indicators)
        passive_ratio = passive_count / max(total_words, 1)

        return {
            "total_words": total_words,
            "total_sentences": total_sentences,
            "avg_sentence_length": avg_sentence_length,
            "readability_score": readability / 100,  # Normalize to 0-1
            "passive_voice_ratio": passive_ratio,
        }

    def _calculate_quality_score(
        self,
        violations: list[StyleViolation],
        style_metrics: dict[str, Any],
        evidence_result: dict[str, Any],
    ) -> float:
        """Calculate overall quality score."""
        base_score = 1.0

        # Deduct for violations
        blocking = len([v for v in violations if v.severity == ViolationSeverity.BLOCKING])
        warnings = len([v for v in violations if v.severity == ViolationSeverity.WARNING])

        base_score -= blocking * 0.25
        base_score -= warnings * 0.05

        # Adjust for style metrics
        readability = style_metrics.get("readability_score", 0.5)
        base_score -= abs(0.7 - readability) * 0.1  # Penalize if not in 0.6-0.8 range

        passive_ratio = style_metrics.get("passive_voice_ratio", 0.0)
        if passive_ratio > 0.3:
            base_score -= 0.1

        # Boost for evidence
        evidence_score = evidence_result.get("score", 0.0)
        base_score += evidence_score * 0.1

        return max(0.0, min(1.0, base_score))


class QualityGate:
    """Enforces quality thresholds for brief generation."""

    def __init__(
        self,
        min_quality_score: float = 0.70,
        min_evidence_score: float = 0.60,
        max_buzzword_density: float = 0.05,
    ) -> None:
        self.min_quality_score = min_quality_score
        self.min_evidence_score = min_evidence_score
        self.max_buzzword_density = max_buzzword_density

    def evaluate(self, validation_result: BriefValidationResult) -> dict[str, Any]:
        """Evaluate brief against quality gates."""
        _emit_verifies_policy("enterprise", "QualityGate", "evaluate")

        gates_passed = True
        violations: list[str] = []

        # Quality score gate
        quality_score = validation_result.quality_score
        if quality_score < self.min_quality_score:
            gates_passed = False
            violations.append(
                f"Quality score {quality_score:.0%} below threshold {self.min_quality_score:.0%}",
            )

        # Evidence score gate
        evidence_score = validation_result.evidence_score
        if evidence_score < self.min_evidence_score:
            gates_passed = False
            violations.append(
                f"Evidence score {evidence_score:.0%} below threshold {self.min_evidence_score:.0%}",
            )

        # Buzzword density gate
        buzzword_density = validation_result.style_metrics.get("buzzword_density", 0.0)
        if buzzword_density > self.max_buzzword_density:
            gates_passed = False
            violations.append(
                f"Buzzword density {buzzword_density:.1%} exceeds maximum {self.max_buzzword_density:.0%}",
            )

        # Style violations gate
        blocking_violations = len(
            [v for v in validation_result.violations if v.severity == ViolationSeverity.BLOCKING]
        )
        if blocking_violations > 0:
            gates_passed = False
            violations.append(f"{blocking_violations} blocking style violations found")

        return {
            "gates_passed": gates_passed,
            "violations": violations,
            "violation_count": len(violations),
            "thresholds": {
                "min_quality": self.min_quality_score,
                "min_evidence": self.min_evidence_score,
                "max_buzzwords": self.max_buzzword_density,
            },
        }


class BriefValidationAgent:
    """Agent wrapper for brief validation."""

    def __init__(self) -> None:
        self.validator = StyleValidator()
        self.quality_gate = QualityGate()

    def validate_brief(
        self,
        brief_content: str,
        brief_metadata: dict[str, Any],
        target_audience: str,
    ) -> tuple[BriefValidationResult, dict[str, Any]]:
        """Validate a brief and evaluate against quality gates."""
        _emit_records_execution_trace("enterprise", "BriefValidationAgent", "validate_brief")

        # Run style validation
        validation = self.validator.validate(
            brief_content,
            brief_metadata,
            target_audience,
        )

        # Run quality gates
        gates = self.quality_gate.evaluate(validation)

        return validation, gates

    def validate_batch(
        self,
        briefs: list[tuple[str, dict[str, Any], str]],
    ) -> list[tuple[BriefValidationResult, dict[str, Any]]]:
        """Validate multiple briefs."""
        results: list[tuple[BriefValidationResult, dict[str, Any]]] = []

        for content, metadata, audience in briefs:
            result = self.validate_brief(content, metadata, audience)
            results.append(result)

        return results

    def get_validation_summary(
        self,
        results: list[tuple[BriefValidationResult, dict[str, Any]]],
    ) -> dict[str, Any]:
        """Generate summary across all validations."""
        validations = [r[0] for r in results]
        gates = [r[1] for r in results]

        total = len(validations)
        passed = sum(1 for v in validations if v.passed)
        gates_passed = sum(1 for g in gates if g["gates_passed"])

        avg_quality = sum(v.quality_score for v in validations) / max(total, 1)
        avg_evidence = sum(v.evidence_score for v in validations) / max(total, 1)

        # Aggregate violations
        all_violations: list[StyleViolation] = []
        for v in validations:
            all_violations.extend(v.violations)

        violation_counts: dict[str, int] = {}
        for v in all_violations:
            key = v.rule_id
            violation_counts[key] = violation_counts.get(key, 0) + 1

        return {
            "total_briefs": total,
            "passed_validation": passed,
            "passed_gates": gates_passed,
            "avg_quality_score": avg_quality,
            "avg_evidence_score": avg_evidence,
            "common_violations": violation_counts,
            "overall_pass_rate": passed / max(total, 1),
        }
