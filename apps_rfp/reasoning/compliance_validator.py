"""
L5 Compliance Validation + Claims Verification — apps_rfp.enterprise.

Validates proposal content against compliance requirements,
verifies claims have evidence, and ensures regulatory alignment.

Layer 5 Safety: Static analysis, policy enforcement, hallucination gates.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_records_execution_trace,
    _emit_applies_guardrail,
    _emit_validates_agent_capability,
    _emit_verifies_policy,
)

_log = logging.getLogger(__name__)


class ViolationSeverity(str, Enum):
    """Severity of compliance violation."""

    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"


@dataclass(frozen=True)
class ComplianceViolation:
    """A compliance violation or concern."""

    violation_id: str
    rule_id: str
    section_id: str
    severity: ViolationSeverity
    message: str
    suggestion: str


@dataclass(frozen=True)
class ClaimVerification:
    """Verification status of a specific claim."""

    claim_id: str
    claim_text: str
    section_id: str
    has_evidence: bool
    evidence_refs: list[str]
    confidence: str  # high, medium, low, unsupported
    recommendation: str


@dataclass
class ComplianceValidationResult:
    """Result of compliance validation."""

    passed: bool
    violations: list[ComplianceViolation] = field(default_factory=list)
    claim_verifications: list[ClaimVerification] = field(default_factory=list)
    regulatory_gaps: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    quality_score: float = 0.0


class ComplianceRule:
    """A compliance validation rule."""

    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        severity: ViolationSeverity,
        check_fn: callable,
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.severity = severity
        self.check_fn = check_fn


class ComplianceValidator:
    """L5 validator for proposal compliance."""

    # Regulatory requirements by industry
    REGULATORY_REQUIREMENTS: dict[str, list[str]] = {
        "financial_services": [
            "data_retention_policy",
            "audit_trail_completeness",
            "sox_compliance",
            "gdpr_data_protection",
            "model_explainability",
        ],
        "healthcare": [
            "hipaa_phi_protection",
            "fda_21cfr11_validation",
            "clinical_data_integrity",
            "audit_access_controls",
        ],
        "government": [
            "fedramp_authorization",
            "fisma_compliance",
            "data_sovereignty",
            "supply_chain_security",
        ],
        "technology": [
            "data_privacy",
            "security_baseline",
        ],
    }

    # Unsupportable claims that trigger warnings
    UNSUPPORTABLE_PATTERNS: list[tuple[str, str]] = [
        (r"\bguaranteed\b", "Absolute guarantee claim"),
        (r"\b100%\s+(?:accurate|reliable|secure)", "100% claim without qualification"),
        (r"\bzero\s+risk\b", "Zero risk claim"),
        (r"\balways\s+(?:works|secure|compliant)\b", "Unqualified absolute claim"),
        (r"\bnever\s+fails?\b", "Never fails claim"),
        (r"\bunhackable\b", "Unhackable claim"),
        (r"\bbulletproof\b", "Bulletproof claim"),
    ]

    def __init__(self) -> None:
        self.rules = self._initialize_rules()

    def validate(
        self,
        proposal_sections: list[dict[str, Any]],
        industry: str,
        rfp_requirements: list[dict[str, Any]],
    ) -> ComplianceValidationResult:
        """Validate proposal against compliance rules."""
        _emit_records_execution_trace("enterprise", "ComplianceValidator", "validate_start")

        violations: list[ComplianceViolation] = []
        claim_verifications: list[ClaimVerification] = []

        # Check each rule against proposal
        for rule in self.rules:
            rule_violations = rule.check_fn(proposal_sections, industry, rfp_requirements)
            violations.extend(rule_violations)

        # Verify claims have evidence
        for section in proposal_sections:
            section_claims = self._extract_claims(section)
            for claim in section_claims:
                verification = self._verify_claim(claim, section)
                claim_verifications.append(verification)

        # Check regulatory gaps
        regulatory_gaps = self._identify_regulatory_gaps(proposal_sections, industry)

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            violations, claim_verifications, regulatory_gaps
        )

        # Determine pass/fail
        blocking_count = len([v for v in violations if v.severity == ViolationSeverity.BLOCKING])
        passed = blocking_count == 0 and len(regulatory_gaps) == 0

        _emit_applies_guardrail("enterprise", "ComplianceValidator", "validation_complete")

        return ComplianceValidationResult(
            passed=passed,
            violations=violations,
            claim_verifications=claim_verifications,
            regulatory_gaps=regulatory_gaps,
            risk_flags=self._extract_risk_flags(violations, regulatory_gaps),
            quality_score=quality_score,
        )

    def _initialize_rules(self) -> list[ComplianceRule]:
        """Initialize all compliance validation rules."""
        return [
            ComplianceRule(
                rule_id="R001",
                name="Unsupported Claims",
                description="Detect claims that cannot be supportable",
                severity=ViolationSeverity.WARNING,
                check_fn=self._check_unsupported_claims,
            ),
            ComplianceRule(
                rule_id="R002",
                name="Missing Evidence",
                description="Verify key claims have evidence references",
                severity=ViolationSeverity.WARNING,
                check_fn=self._check_missing_evidence,
            ),
            ComplianceRule(
                rule_id="R003",
                name="Regulatory Alignment",
                description="Check alignment with industry regulatory requirements",
                severity=ViolationSeverity.BLOCKING,
                check_fn=self._check_regulatory_alignment,
            ),
            ComplianceRule(
                rule_id="R004",
                name="Required Sections",
                description="Verify all required sections are present",
                severity=ViolationSeverity.BLOCKING,
                check_fn=self._check_required_sections,
            ),
            ComplianceRule(
                rule_id="R005",
                name="Security Claims",
                description="Validate security-related claims have proper backing",
                severity=ViolationSeverity.WARNING,
                check_fn=self._check_security_claims,
            ),
        ]

    def _check_unsupported_claims(
        self,
        sections: list[dict[str, Any]],
        industry: str,
        rfp_requirements: list[dict[str, Any]],
    ) -> list[ComplianceViolation]:
        """Check for unsupported absolute claims."""
        violations: list[ComplianceViolation] = []

        for section in sections:
            body = section.get("body", "")
            section_id = section.get("section_id", "unknown")

            for pattern, description in self.UNSUPPORTABLE_PATTERNS:
                if re.search(pattern, body, re.IGNORECASE):
                    violations.append(
                        ComplianceViolation(
                            violation_id=f"V{len(violations)+1:03d}",
                            rule_id="R001",
                            section_id=section_id,
                            severity=ViolationSeverity.WARNING,
                            message=f"Potentially unsupportable claim: {description}",
                            suggestion="Quantify with specific metrics or add qualifying language",
                        )
                    )

        return violations

    def _check_missing_evidence(
        self,
        sections: list[dict[str, Any]],
        industry: str,
        rfp_requirements: list[dict[str, Any]],
    ) -> list[ComplianceViolation]:
        """Check for claims without evidence."""
        violations: list[ComplianceViolation] = []

        for section in sections:
            body = section.get("body", "")
            section_id = section.get("section_id", "")
            evidence_cited = section.get("evidence_cited", [])

            # Check for numeric claims without evidence
            numeric_claims = re.findall(r"\b(\d+%|\$[\d,]+|\d+\s+(?:hours|days|weeks|months))\b", body)

            if numeric_claims and not evidence_cited:
                violations.append(
                    ComplianceViolation(
                        violation_id=f"V{len(violations)+1:03d}",
                        rule_id="R002",
                        section_id=section_id,
                        severity=ViolationSeverity.WARNING,
                        message=f"Numeric claims ({len(numeric_claims)} found) without evidence citations",
                        suggestion="Add evidence anchors or source references for quantified claims",
                    )
                )

        return violations

    def _check_regulatory_alignment(
        self,
        sections: list[dict[str, Any]],
        industry: str,
        rfp_requirements: list[dict[str, Any]],
    ) -> list[ComplianceViolation]:
        """Check alignment with regulatory requirements."""
        violations: list[ComplianceViolation] = []

        requirements = self.REGULATORY_REQUIREMENTS.get(industry, [])
        if not requirements:
            return violations

        # Combine all section text
        all_text = " ".join(s.get("body", "") for s in sections).lower()

        # Check for required regulatory mentions
        for req in requirements:
            req_display = req.replace("_", " ").title()
            keywords = req.replace("_", " ").split()

            # Check if any keyword is mentioned
            if not any(kw in all_text for kw in keywords):
                violations.append(
                    ComplianceViolation(
                        violation_id=f"V{len(violations)+1:03d}",
                        rule_id="R003",
                        section_id="proposal",
                        severity=ViolationSeverity.BLOCKING,
                        message=f"Missing regulatory alignment: {req_display}",
                        suggestion=f"Add section addressing {req_display} compliance requirements",
                    )
                )

        return violations

    def _check_required_sections(
        self,
        sections: list[dict[str, Any]],
        industry: str,
        rfp_requirements: list[dict[str, Any]],
    ) -> list[ComplianceViolation]:
        """Check that all required sections are present."""
        violations: list[ComplianceViolation] = []

        required = {
            "executive_summary",
            "technical_approach",
            "implementation_roadmap",
            "risk_and_governance",
            "value_case",
        }

        present = {s.get("section_id", "").lower().replace("-", "_") for s in sections}

        for req in required:
            if not any(req in p for p in present):
                violations.append(
                    ComplianceViolation(
                        violation_id=f"V{len(violations)+1:03d}",
                        rule_id="R004",
                        section_id="proposal",
                        severity=ViolationSeverity.BLOCKING,
                        message=f"Required section missing: {req}",
                        suggestion=f"Add {req} section to proposal",
                    )
                )

        return violations

    def _check_security_claims(
        self,
        sections: list[dict[str, Any]],
        industry: str,
        rfp_requirements: list[dict[str, Any]],
    ) -> list[ComplianceViolation]:
        """Validate security-related claims."""
        violations: list[ComplianceViolation] = []

        security_keywords = [
            "encryption", "secure", "authentication", "authorization",
            "vulnerability", "penetration test", "soc2", "iso27001",
        ]

        for section in sections:
            body = section.get("body", "")
            section_id = section.get("section_id", "")

            # Check for security claims without specifics
            for keyword in security_keywords:
                if keyword in body.lower():
                    # Check if there's specific backing
                    if not re.search(rf"{keyword}.*(?:using|via|with|specific|standard)", body, re.IGNORECASE):
                        violations.append(
                            ComplianceViolation(
                                violation_id=f"V{len(violations)+1:03d}",
                                rule_id="R005",
                                section_id=section_id,
                                severity=ViolationSeverity.WARNING,
                                message=f"Security claim '{keyword}' without specific backing",
                                suggestion="Add specific implementation details or standards references",
                            )
                        )
                    break  # One violation per section is enough

        return violations

    def _extract_claims(self, section: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract claims from a section."""
        body = section.get("body", "")
        claims: list[dict[str, Any]] = []

        # Pattern: sentences with numbers or strong verbs
        sentences = re.split(r'[.!?]+', body)

        for idx, sent in enumerate(sentences):
            sent = sent.strip()
            if len(sent) > 20:
                # Check if it's a claim (has metrics, outcomes, or strong assertions)
                if any(pattern in sent.lower() for pattern in [
                    "will", "delivers", "achieves", "reduces", "improves",
                    "guarantees", "ensures", "provides", "%", "$", "percent"
                ]):
                    claims.append({
                        "claim_id": f"C{idx+1:03d}",
                        "text": sent,
                        "section_id": section.get("section_id", "unknown"),
                    })

        return claims

    def _verify_claim(self, claim: dict[str, Any], section: dict[str, Any]) -> ClaimVerification:
        """Verify a claim has supporting evidence."""
        claim_text = claim["text"]
        evidence_refs = section.get("evidence_cited", [])

        # Determine confidence based on evidence and claim type
        has_evidence = len(evidence_refs) > 0

        # Check for quantified claims (need stronger evidence)
        is_quantified = bool(re.search(r'\d+%|\$[\d,]+|\d+\s+(?:hours|days|weeks)', claim_text))

        if has_evidence and is_quantified:
            confidence = "medium"  # Quantified claims need extra scrutiny
        elif has_evidence:
            confidence = "high"
        elif is_quantified:
            confidence = "unsupported"  # Quantified without evidence = problem
        else:
            confidence = "low"

        recommendation = {
            "high": "Claim is well-supported",
            "medium": "Add additional evidence for quantified metrics",
            "low": "Consider adding evidence reference",
            "unsupported": "REQUIRED: Add evidence for quantified claim",
        }.get(confidence, "Review claim support")

        return ClaimVerification(
            claim_id=claim["claim_id"],
            claim_text=claim_text[:100] + "..." if len(claim_text) > 100 else claim_text,
            section_id=claim["section_id"],
            has_evidence=has_evidence,
            evidence_refs=evidence_refs,
            confidence=confidence,
            recommendation=recommendation,
        )

    def _identify_regulatory_gaps(
        self,
        sections: list[dict[str, Any]],
        industry: str,
    ) -> list[str]:
        """Identify missing regulatory coverage."""
        gaps: list[str] = []

        requirements = self.REGULATORY_REQUIREMENTS.get(industry, [])
        all_text = " ".join(s.get("body", "") for s in sections).lower()

        for req in requirements:
            keywords = req.replace("_", " ").split()
            if not any(kw in all_text for kw in keywords):
                gaps.append(req)

        return gaps

    def _calculate_quality_score(
        self,
        violations: list[ComplianceViolation],
        claim_verifications: list[ClaimVerification],
        regulatory_gaps: list[str],
    ) -> float:
        """Calculate overall quality score."""
        base_score = 1.0

        # Deduct for violations
        blocking = len([v for v in violations if v.severity == ViolationSeverity.BLOCKING])
        warnings = len([v for v in violations if v.severity == ViolationSeverity.WARNING])

        base_score -= blocking * 0.25
        base_score -= warnings * 0.05

        # Deduct for unsupported claims
        unsupported = len([c for c in claim_verifications if c.confidence == "unsupported"])
        base_score -= unsupported * 0.1

        # Deduct for regulatory gaps
        base_score -= len(regulatory_gaps) * 0.15

        return max(0.0, base_score)

    def _extract_risk_flags(
        self,
        violations: list[ComplianceViolation],
        regulatory_gaps: list[str],
    ) -> list[str]:
        """Extract risk flags from validation results."""
        flags: list[str] = []

        if any(v.severity == ViolationSeverity.BLOCKING for v in violations):
            flags.append("blocking_violations_present")

        if regulatory_gaps:
            flags.append("regulatory_gaps_identified")

        unsupported_claims = len([v for v in violations if v.rule_id == "R001"])
        if unsupported_claims > 2:
            flags.append("multiple_unsupported_claims")

        return flags


class ClaimsVerifier:
    """Verifies that proposal claims can be substantiated."""

    def __init__(self) -> None:
        self._evidence_registry: dict[str, list[str]] = {}

    def register_evidence(self, claim_pattern: str, evidence_sources: list[str]) -> None:
        """Register evidence sources for claim patterns."""
        self._evidence_registry[claim_pattern] = evidence_sources

    def verify_claim_against_sources(
        self,
        claim: str,
        available_sources: list[str],
    ) -> dict[str, Any]:
        """Verify a claim against available evidence sources."""
        _emit_verifies_policy("enterprise", "ClaimsVerifier", "verify_claim")

        # Check for direct matches
        direct_matches = [s for s in available_sources if any(word in s.lower() for word in claim.lower().split()[:5])]

        # Check for pattern matches in registry
        pattern_matches: list[str] = []
        for pattern, sources in self._evidence_registry.items():
            if re.search(pattern, claim, re.IGNORECASE):
                pattern_matches.extend(sources)

        all_matches = list(set(direct_matches + pattern_matches))

        return {
            "claim": claim[:100],
            "verified": len(all_matches) > 0,
            "evidence_sources": all_matches[:5],  # Top 5
            "verification_confidence": "high" if len(all_matches) >= 2 else "medium" if all_matches else "low",
        }

    def batch_verify(
        self,
        claims: list[str],
        available_sources: list[str],
    ) -> list[dict[str, Any]]:
        """Verify multiple claims."""
        _emit_validates_agent_capability("enterprise", "ClaimsVerifier", "batch_verify")

        return [self.verify_claim_against_sources(claim, available_sources) for claim in claims]
