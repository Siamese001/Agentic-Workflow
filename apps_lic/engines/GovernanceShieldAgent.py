"""Governance Shield Agent - Risk Maturity and Safety Protocol Generation.

This agent audits content for "Naive Claims" and generates mature, risk-aware
language for senior AI leadership positions. It creates safety protocols that
address security, privacy, and evaluation frameworks.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from apps_lic.shared.core.agent_base import LICAgentBase
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin

logger = logging.getLogger(__name__)


@dataclass
class GovernanceShieldAgent(SubatomicTestingMixin, LICAgentBase):
    """Sovereign Governance Shield - Audits and upgrades content for risk maturity."""

    # Sovereign Configuration
    risk_thresholds: dict[str, float] = field(
        default_factory=lambda: {"max_confidence_score": 0.95, "min_safety_level": 0.8}
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

        # Naive claim patterns to detect and replace
        self.naive_patterns = {
            "absolute_accuracy": [
                r"100% accurate",
                r"perfect accuracy",
                r"zero errors",
                r"flawless performance",
                r"always correct",
            ],
            "hallucination_claims": [
                r"zero hallucinations",
                r"hallucination[- ]free",
                r"no hallucinations",
                r"eliminated hallucinations",
                r"completely factual",
            ],
            "privacy_violations": [
                r"used user data",
                r"trained on customer data",
                r"leverages personal information",
                r"processes private data",
            ],
            "security_claims": [
                r"completely secure",
                r"unhackable",
                r"impenetrable",
                r"100% secure",
            ],
        }

        # Senior replacements for naive claims
        self.senior_replacements = {
            "absolute_accuracy": [
                "high-precision (>99%) with human fallback",
                "99.5%+ accuracy with confidence scoring",
                "enterprise-grade accuracy with validation",
            ],
            "hallucination_claims": [
                "minimized hallucination rates via citation-based RAG",
                "reduced hallucination risk through fact-checking pipelines",
                "hallucination mitigation with source attribution",
            ],
            "privacy_violations": [
                "leveraged anonymized telemetry for model fine-tuning",
                "utilized privacy-preserving synthetic data",
                "employed differential privacy techniques for training",
            ],
            "security_claims": [
                "enterprise-grade security with defense-in-depth",
                "multi-layered security architecture",
                "comprehensive security controls and monitoring",
            ],
        }

        # Industry-specific compliance requirements
        self.compliance_requirements = {
            "healthcare": ["HIPAA", "HITECH", "FDA 21 CFR Part 11"],
            "finance": ["SOC 2 Type II", "PCI DSS", "GLBA", "FINRA"],
            "legal": ["ABA Model Rules", "Data Protection Act", "Bar Compliance"],
            "cybersecurity": ["NIST CSF", "ISO 27001", "CMMC"],
            "general": ["GDPR", "CCPA", "SOX"],
        }

        logger.info("Initialized GovernanceShieldAgent")

    def sanitize_claims(self, content: str) -> str:
        """Sanitize naive claims with mature, risk-aware language.

        Args:
            content: Content to sanitize

        Returns:
            Sanitized content
        """
        try:
            sanitized = content

            # Check for zero tolerance violations
            if "zero hallucinations" in sanitized.lower():
                logger.warning(
                    "CRITICAL: 'Zero hallucinations' claim detected - immediate disqualifier"
                )
                sanitized = self._critical_fix_zero_hallucinations(sanitized)

            # Apply pattern replacements
            for category, patterns in self.naive_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, sanitized, re.IGNORECASE)
                    if matches:
                        # Replace with senior language
                        replacements = self.senior_replacements[category]
                        replacement = replacements[0]  # Use first replacement

                        # Replace all occurrences
                        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
                        logger.debug(f"Replaced {category} claim with: {replacement}")

            # Additional privacy fixes
            sanitized = self._fix_privacy_language(sanitized)

            return sanitized

        except Exception as e:
            logger.error(f"Error sanitizing claims: {str(e)}")
            return content

    def generate_safety_protocol(self, risk_profile: RiskProfile) -> SafetyProtocol:
        """Generate safety protocol based on risk profile.

        Args:
            risk_profile: Risk profile for target company

        Returns:
            Comprehensive safety protocol
        """
        try:
            if risk_profile.is_high_risk:
                return self._generate_high_risk_protocol(risk_profile)
            else:
                return self._generate_standard_protocol(risk_profile)

        except Exception as e:
            logger.error(f"Error generating safety protocol: {str(e)}")
            return SafetyProtocol(
                validation_strategy="Comprehensive testing before deployment",
                data_privacy_approach="Privacy by design principles",
                human_in_the_loop_policy="Human review for critical decisions",
            )

    def audit_outreach(self, email_draft: str) -> str:
        """Audit final email draft for compliance.

        Args:
            email_draft: Email content to audit

        Returns:
            Audited email content
        """
        try:
            # Run full sanitization
            audited = self.sanitize_claims(email_draft)

            # Add compliance disclaimer if needed
            if any(term in audited.lower() for term in ["hipaa", "phi", "health data"]):
                audited += "\n\n[Note: All healthcare applications maintain HIPAA compliance through on-prem deployment or BAA-compliant APIs.]"

            return audited

        except Exception as e:
            logger.error(f"Error auditing outreach: {str(e)}")
            return email_draft

    def scan_risk_level(self, industry: str, job_description: str) -> RiskProfile:
        """Scan industry and JD to determine risk level.

        Args:
            industry: Target company industry
            job_description: Job description text

        Returns:
            Risk profile with sensitivity and requirements
        """
        try:
            industry_lower = industry.lower()
            jd_lower = job_description.lower()

            # Determine base sensitivity
            if industry_lower in ["healthcare", "health", "medical", "pharma"]:
                sensitivity = IndustrySensitivity.HIGH
                compliance = self.compliance_requirements["healthcare"]
                data_types = ["PHI", "Patient Data", "Medical Records"]
            elif industry_lower in ["finance", "banking", "fintech", "insurance"]:
                sensitivity = IndustrySensitivity.HIGH
                compliance = self.compliance_requirements["finance"]
                data_types = ["PII", "Financial Data", "Transaction Records"]
            elif industry_lower in ["legal", "law", "compliance"]:
                sensitivity = IndustrySensitivity.HIGH
                compliance = self.compliance_requirements["legal"]
                data_types = ["Attorney-Client Privilege", "Legal Documents"]
            elif industry_lower in ["cybersecurity", "security", "infosec"]:
                sensitivity = IndustrySensitivity.HIGH
                compliance = self.compliance_requirements["cybersecurity"]
                data_types = ["Security Logs", "Incident Data", "Threat Intelligence"]
            else:
                sensitivity = IndustrySensitivity.MEDIUM
                compliance = self.compliance_requirements["general"]
                data_types = ["User Data", "Analytics Data"]

            # Boost sensitivity if JD mentions compliance
            if any(
                term in jd_lower for term in ["compliance", "regulatory", "audit", "sox", "hipaa"]
            ):
                if sensitivity == IndustrySensitivity.MEDIUM:
                    sensitivity = IndustrySensitivity.HIGH
                    logger.info("Boosted to HIGH sensitivity due to JD compliance keywords")

            # Extract additional compliance keywords from JD
            additional_compliance = []
            for framework in ["GDPR", "CCPA", "SOC 2", "ISO 27001", "NIST", "CMMC"]:
                if framework.lower() in jd_lower:
                    additional_compliance.append(framework)

            compliance.extend(additional_compliance)

            return RiskProfile(
                industry_sensitivity=sensitivity,
                compliance_keywords=list(set(compliance)),  # Remove duplicates
                data_sensitivity=data_types,
            )

        except Exception as e:
            logger.error(f"Error scanning risk level: {str(e)}")
            return RiskProfile(
                industry_sensitivity=IndustrySensitivity.MEDIUM,
                compliance_keywords=["GDPR"],
                data_sensitivity=["User Data"],
            )

    def _critical_fix_zero_hallucinations(self, content: str) -> str:
        """Critical fix for zero hallucination claims.

        Args:
            content: Content with critical violation

        Returns:
            Fixed content
        """
        # Immediate replacement for zero tolerance violation
        content = re.sub(
            r"zero hallucinations",
            "minimized hallucinations through rigorous validation",
            content,
            flags=re.IGNORECASE,
        )

        content = re.sub(
            r"hallucination[- ]free", "hallucination-mitigated", content, flags=re.IGNORECASE
        )

        return content

    def _fix_privacy_language(self, content: str) -> str:
        """Fix privacy-related language issues.

        Args:
            content: Content to fix

        Returns:
            Fixed content
        """
        # Replace problematic privacy language
        privacy_fixes = {
            r"user data without consent": "anonymized user data with consent",
            r"personal information": "anonymized identifiers",
            r"private data": "privacy-protected data",
            r"customer data": "customer-approved analytics",
        }

        for pattern, replacement in privacy_fixes.items():
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        return content

    def _generate_high_risk_protocol(self, risk_profile: RiskProfile) -> SafetyProtocol:
        """Generate protocol for high-risk industries.

        Args:
            risk_profile: High-risk profile

        Returns:
            Comprehensive safety protocol
        """
        frameworks = risk_profile.compliance_keywords

        # Check for HIPAA requirement
        if "HIPAA" in frameworks:
            privacy = "On-prem deployment or BAA-compliant APIs with PII redaction (Presidio)"
        else:
            privacy = "End-to-end encryption with data minimization and anonymization"

        return SafetyProtocol(
            validation_strategy="Automated eval pipeline (Ragas) + human expert review before production",
            data_privacy_approach=privacy,
            human_in_the_loop_policy="Mandatory human oversight for all high-stakes decisions with audit trails",
            compliance_frameworks=frameworks,
        )

    def _generate_standard_protocol(self, risk_profile: RiskProfile) -> SafetyProtocol:
        """Generate protocol for standard risk industries.

        Args:
            risk_profile: Standard risk profile

        Returns:
            Standard safety protocol
        """
        return SafetyProtocol(
            validation_strategy="Comprehensive testing including bias, fairness, and performance metrics",
            data_privacy_approach="Privacy by design with differential privacy techniques",
            human_in_the_loop_policy="Human review for edge cases and sensitive applications",
            compliance_frameworks=risk_profile.compliance_keywords,
        )


# Factory function for easy instantiation
def create_governance_shield_agent() -> GovernanceShieldAgent:
    """Create a GovernanceShieldAgent instance.

    Returns:
        Configured GovernanceShieldAgent
    """
    return GovernanceShieldAgent()


# Convenience function for quick sanitization
def sanitize_content(content: str) -> str:
    """Quickly sanitize content for risk maturity.

    Args:
        content: Content to sanitize

    Returns:
        Sanitized content
    """
    agent = create_governance_shield_agent()
    return agent.sanitize_claims(content)
