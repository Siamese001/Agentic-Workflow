"""
L5 Research Validation + Source Gates — apps_research.enterprise.

Validates research artifacts against quality standards,
verifies source coverage, and enforces claim-type labeling.

Layer 5 Safety: Static analysis, policy enforcement, source verification.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_verifies_policy,
)

_log = logging.getLogger(__name__)


class ViolationSeverity(str, Enum):
    """Severity of validation violation."""

    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"


@dataclass(frozen=True)
class ValidationViolation:
    """A validation violation."""

    violation_id: str
    rule_id: str
    check_id: str
    severity: ViolationSeverity
    message: str
    suggestion: str


@dataclass
class ResearchValidationResult:
    """Result of research validation."""

    passed: bool
    violations: list[ValidationViolation] = field(default_factory=list)
    source_metrics: dict[str, Any] = field(default_factory=dict)
    claim_metrics: dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    source_coverage: float = 0.0


class ResearchValidator:
    """L5 validator for research artifacts."""

    # Required claim type labels
    CLAIM_TYPE_LABELS: frozenset[str] = frozenset({
        "[DIRECT_EVIDENCE]",
        "[INTERPRETATION]",
        "[ANALYST_INFERENCE]",
        "[ASSUMPTION]",
    })

    # Source register required fields
    REQUIRED_SOURCE_FIELDS: frozenset[str] = frozenset({
        "source_id",
        "title",
        "claim_type",
        "confidence",
    })

    def __init__(self) -> None:
        self._violation_counter = 0

    def validate(
        self,
        research_content: str,
        source_register: list[dict[str, Any]],
        required_sections: list[str],
    ) -> ResearchValidationResult:
        """Validate research artifact against standards."""
        _emit_records_execution_trace("enterprise", "ResearchValidator", "validate_start")

        violations: list[ValidationViolation] = []

        # Check source register presence
        source_violations = self._check_source_register(source_register)
        violations.extend(source_violations)

        # Check required sections
        section_violations = self._check_required_sections(research_content, required_sections)
        violations.extend(section_violations)

        # Check claim type labels
        claim_violations = self._check_claim_types(research_content)
        violations.extend(claim_violations)

        # Check for empty sections
        empty_violations = self._check_empty_sections(research_content)
        violations.extend(empty_violations)

        # Calculate source metrics
        source_metrics = self._calculate_source_metrics(source_register)

        # Calculate claim metrics
        claim_metrics = self._calculate_claim_metrics(research_content)

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            violations, source_metrics, claim_metrics
        )

        # Calculate source coverage
        source_coverage = source_metrics.get("valid_sources_ratio", 0.0)

        # Determine pass/fail
        blocking_count = len([v for v in violations if v.severity == ViolationSeverity.BLOCKING])
        passed = blocking_count == 0 and quality_score >= 0.70

        _emit_applies_guardrail("enterprise", "ResearchValidator", "validation_complete")

        return ResearchValidationResult(
            passed=passed,
            violations=violations,
            source_metrics=source_metrics,
            claim_metrics=claim_metrics,
            quality_score=quality_score,
            source_coverage=source_coverage,
        )

    def _check_source_register(
        self,
        source_register: list[dict[str, Any]],
    ) -> list[ValidationViolation]:
        """Check source register completeness."""
        violations: list[ValidationViolation] = []

        # Check for empty source register
        if not source_register:
            self._violation_counter += 1
            violations.append(
                ValidationViolation(
                    violation_id=f"V{self._violation_counter:03d}",
                    rule_id="RES_NO_SOURCE_REGISTER",
                    check_id="source_count",
                    severity=ViolationSeverity.BLOCKING,
                    message="Source register is empty",
                    suggestion="Add at least one source with proper claim typing",
                )
            )
            return violations

        # Check each source entry
        for idx, source in enumerate(source_register):
            missing_fields = self.REQUIRED_SOURCE_FIELDS - set(source.keys())
            if missing_fields:
                self._violation_counter += 1
                violations.append(
                    ValidationViolation(
                        violation_id=f"V{self._violation_counter:03d}",
                        rule_id="RES_INCOMPLETE_SOURCE",
                        check_id=f"source_{idx}",
                        severity=ViolationSeverity.BLOCKING,
                        message=f"Source {idx} missing fields: {', '.join(missing_fields)}",
                        suggestion=f"Add missing fields: {', '.join(missing_fields)}",
                    )
                )

        return violations

    def _check_required_sections(
        self,
        content: str,
        required_sections: list[str],
    ) -> list[ValidationViolation]:
        """Check for required sections."""
        violations: list[ValidationViolation] = []

        for section in required_sections:
            # Look for section header
            section_pattern = rf"##\s+{re.escape(section.replace('_', ' '))}"
            if not re.search(section_pattern, content, re.IGNORECASE):
                self._violation_counter += 1
                violations.append(
                    ValidationViolation(
                        violation_id=f"V{self._violation_counter:03d}",
                        rule_id="RES_MISSING_SECTION",
                        check_id=section,
                        severity=ViolationSeverity.BLOCKING,
                        message=f"Required section '{section}' not found",
                        suggestion=f"Add section header: ## {section.replace('_', ' ').title()}",
                    )
                )

        return violations

    def _check_claim_types(self, content: str) -> list[ValidationViolation]:
        """Check for claim type labels in content."""
        violations: list[ValidationViolation] = []

        # Count claim type labels
        claim_count = 0
        for label in self.CLAIM_TYPE_LABELS:
            claim_count += content.count(label)

        # Check if any claim types are present
        if claim_count == 0:
            self._violation_counter += 1
            violations.append(
                ValidationViolation(
                    violation_id=f"V{self._violation_counter:03d}",
                    rule_id="RES_NO_CLAIM_TYPES",
                    check_id="claim_labels",
                    severity=ViolationSeverity.BLOCKING,
                    message="No claim type labels found in content",
                    suggestion="Add claim type labels: [DIRECT_EVIDENCE], [INTERPRETATION], [ANALYST_INFERENCE], [ASSUMPTION]",
                )
            )

        return violations

    def _check_empty_sections(self, content: str) -> list[ValidationViolation]:
        """Check for sections with empty body."""
        violations: list[ValidationViolation] = []

        # Parse sections (assumes markdown ## headers)
        sections = re.split(r"\n##\s+", content)

        for section in sections[1:]:  # Skip preamble
            lines = section.strip().split("\n")
            if len(lines) < 2 or not lines[1].strip():
                self._violation_counter += 1
                section_title = lines[0][:30] if lines else "Unknown"
                violations.append(
                    ValidationViolation(
                        violation_id=f"V{self._violation_counter:03d}",
                        rule_id="RES_EMPTY_SECTION",
                        check_id=f"section_{section_title}",
                        severity=ViolationSeverity.BLOCKING,
                        message=f"Section '{section_title}' has empty body",
                        suggestion="Add substantive content to this section",
                    )
                )

        return violations

    def _calculate_source_metrics(
        self,
        source_register: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Calculate source metrics."""
        if not source_register:
            return {
                "total_sources": 0,
                "valid_sources": 0,
                "valid_sources_ratio": 0.0,
                "avg_confidence": 0.0,
                "claim_type_distribution": {},
            }

        total = len(source_register)

        # Count valid sources (have all required fields)
        valid = sum(1 for s in source_register if self.REQUIRED_SOURCE_FIELDS <= set(s.keys()))

        # Average confidence
        confidences = [s.get("confidence", 0.0) for s in source_register]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Claim type distribution
        claim_types: dict[str, int] = {}
        for s in source_register:
            ct = s.get("claim_type", "unknown")
            claim_types[ct] = claim_types.get(ct, 0) + 1

        return {
            "total_sources": total,
            "valid_sources": valid,
            "valid_sources_ratio": valid / max(total, 1),
            "avg_confidence": avg_confidence,
            "claim_type_distribution": claim_types,
        }

    def _calculate_claim_metrics(self, content: str) -> dict[str, Any]:
        """Calculate claim type metrics."""
        claim_counts: dict[str, int] = {}

        for label in self.CLAIM_TYPE_LABELS:
            count = content.count(label)
            key = label.strip("[]").lower()
            claim_counts[key] = count

        total_claims = sum(claim_counts.values())

        # Calculate distribution
        distribution = {
            k: v / max(total_claims, 1)
            for k, v in claim_counts.items()
        }

        return {
            "total_claims": total_claims,
            "claim_counts": claim_counts,
            "distribution": distribution,
            "has_direct_evidence": claim_counts.get("direct_evidence", 0) > 0,
            "evidence_ratio": claim_counts.get("direct_evidence", 0) / max(total_claims, 1),
        }

    def _calculate_quality_score(
        self,
        violations: list[ValidationViolation],
        source_metrics: dict[str, Any],
        claim_metrics: dict[str, Any],
    ) -> float:
        """Calculate overall quality score."""
        base_score = 1.0

        # Deduct for violations
        blocking = len([v for v in violations if v.severity == ViolationSeverity.BLOCKING])
        warnings = len([v for v in violations if v.severity == ViolationSeverity.WARNING])

        base_score -= blocking * 0.25
        base_score -= warnings * 0.05

        # Boost for sources
        valid_ratio = source_metrics.get("valid_sources_ratio", 0.0)
        base_score += valid_ratio * 0.1

        # Boost for direct evidence
        evidence_ratio = claim_metrics.get("evidence_ratio", 0.0)
        base_score += evidence_ratio * 0.1

        # Penalty for low claim diversity
        distribution = claim_metrics.get("distribution", {})
        if len([v for v in distribution.values() if v > 0]) < 2:
            base_score -= 0.1

        return max(0.0, min(1.0, base_score))


class SourceGate:
    """Enforces source coverage thresholds."""

    def __init__(
        self,
        min_sources: int = 1,
        min_confidence: float = 0.70,
        require_direct_evidence: bool = True,
    ) -> None:
        self.min_sources = min_sources
        self.min_confidence = min_confidence
        self.require_direct_evidence = require_direct_evidence

    def evaluate(self, validation_result: ResearchValidationResult) -> dict[str, Any]:
        """Evaluate research against source gates."""
        _emit_verifies_policy("enterprise", "SourceGate", "evaluate")

        gates_passed = True
        violations: list[str] = []

        # Source count gate
        total_sources = validation_result.source_metrics.get("total_sources", 0)
        if total_sources < self.min_sources:
            gates_passed = False
            violations.append(
                f"Source count {total_sources} below threshold {self.min_sources}"
            )

        # Confidence gate
        avg_confidence = validation_result.source_metrics.get("avg_confidence", 0.0)
        if avg_confidence < self.min_confidence:
            gates_passed = False
            violations.append(
                f"Avg confidence {avg_confidence:.0%} below threshold {self.min_confidence:.0%}"
            )

        # Direct evidence gate
        if self.require_direct_evidence:
            has_evidence = validation_result.claim_metrics.get("has_direct_evidence", False)
            if not has_evidence:
                gates_passed = False
                violations.append("No direct evidence claims found")

        # Quality score gate
        if validation_result.quality_score < 0.70:
            gates_passed = False
            violations.append(
                f"Quality score {validation_result.quality_score:.0%} below threshold 70%"
            )

        return {
            "gates_passed": gates_passed,
            "violations": violations,
            "violation_count": len(violations),
            "thresholds": {
                "min_sources": self.min_sources,
                "min_confidence": self.min_confidence,
                "require_evidence": self.require_direct_evidence,
            },
        }


class ResearchValidationAgent:
    """Agent wrapper for research validation."""

    def __init__(self) -> None:
        self.validator = ResearchValidator()
        self.source_gate = SourceGate()

    def validate_research(
        self,
        research_content: str,
        source_register: list[dict[str, Any]],
        required_sections: list[str],
    ) -> tuple[ResearchValidationResult, dict[str, Any]]:
        """Validate research and evaluate against gates."""
        _emit_records_execution_trace("enterprise", "ResearchValidationAgent", "validate_research")

        # Run validation
        validation = self.validator.validate(
            research_content, source_register, required_sections
        )

        # Run gates
        gates = self.source_gate.evaluate(validation)

        return validation, gates

    def validate_batch(
        self,
        research_items: list[tuple[str, list[dict[str, Any]], list[str]]],
    ) -> list[tuple[ResearchValidationResult, dict[str, Any]]]:
        """Validate multiple research artifacts."""
        results: list[tuple[ResearchValidationResult, dict[str, Any]]] = []

        for content, sources, sections in research_items:
            result = self.validate_research(content, sources, sections)
            results.append(result)

        return results

    def get_validation_summary(
        self,
        results: list[tuple[ResearchValidationResult, dict[str, Any]]],
    ) -> dict[str, Any]:
        """Generate summary across all validations."""
        validations = [r[0] for r in results]
        gates = [r[1] for r in results]

        total = len(validations)
        passed = sum(1 for v in validations if v.passed)
        gates_passed = sum(1 for g in gates if g["gates_passed"])

        avg_quality = sum(v.quality_score for v in validations) / max(total, 1)
        avg_coverage = sum(v.source_coverage for v in validations) / max(total, 1)

        # Aggregate violations
        all_violations: list[ValidationViolation] = []
        for v in validations:
            all_violations.extend(v.violations)

        violation_counts: dict[str, int] = {}
        for v in all_violations:
            key = v.rule_id
            violation_counts[key] = violation_counts.get(key, 0) + 1

        return {
            "total_research": total,
            "passed_validation": passed,
            "passed_gates": gates_passed,
            "avg_quality_score": avg_quality,
            "avg_source_coverage": avg_coverage,
            "common_violations": violation_counts,
            "overall_pass_rate": passed / max(total, 1),
        }
