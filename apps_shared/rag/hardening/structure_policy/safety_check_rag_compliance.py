"""Safety-Enhanced RAG Compliance Checker - Checks RAG operations for compliance with safety policies.

This module provides comprehensive compliance checking for RAG operations,
including policy validation, security checks, and regulatory compliance.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Set
import logging
import re
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ComplianceType(Enum):
    """Types of compliance checks."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    CCPA = "ccpa"
    SECURITY = "security"
    PRIVACY = "privacy"
    ETHICS = "ethics"
    QUALITY = "quality"


class ComplianceStatus(Enum):
    """Compliance status levels."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNKNOWN = "unknown"
    VIOLATION = "violation"


@dataclass
class ComplianceRule:
    """Definition of a compliance rule."""
    id: str
    name: str
    compliance_type: ComplianceType
    description: str
    check_function: str  # Name of check function
    severity: str = "medium"
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceViolation:
    """Record of a compliance violation."""
    rule_id: str
    rule_name: str
    compliance_type: ComplianceType
    severity: str
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    remediation: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceCheckResult:
    """Result of compliance checking."""
    overall_status: ComplianceStatus
    compliance_scores: Dict[str, float] = field(default_factory=dict)
    violations: List[ComplianceViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyRAGComplianceConfig:
    """Configuration for safety RAG compliance checking."""
    enabled_compliance_types: List[ComplianceType] = field(default_factory=lambda: [
        ComplianceType.SECURITY, ComplianceType.PRIVACY, ComplianceType.ETHICS
    ])
    strict_mode: bool = False
    auto_remediation: bool = False
    violation_threshold: float = 0.5
    log_violations: bool = True
    custom_rules: List[ComplianceRule] = field(default_factory=list)
    exempt_operations: Set[str] = field(default_factory=set)
    log_level: str = "INFO"


class SafetyRAGComplianceChecker:
    """Main class for safety-enhanced RAG compliance checking."""

    def __init__(self, config: Optional[SafetyRAGComplianceConfig] = None):
        self.config = config or SafetyRAGComplianceConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._rules = []
        self._load_default_rules()

    def check_compliance(self, operation: Dict[str, Any]) -> ComplianceCheckResult:
        """Check RAG operation for compliance.
        
        Args:
            operation: RAG operation to check
            
        Returns:
            ComplianceCheckResult: Compliance check results
        """
        self.logger.info(f"Checking compliance for operation: {operation.get('type', 'unknown')}")
        
        violations = []
        warnings = []
        recommendations = []
        compliance_scores = {}
        
        try:
            # Skip exempt operations
            if operation.get('id') in self.config.exempt_operations:
                return ComplianceCheckResult(
                    overall_status=ComplianceStatus.COMPLIANT,
                    metadata={"exempt": True}
                )
            
            # Check each enabled compliance type
            for compliance_type in self.config.enabled_compliance_types:
                type_score, type_violations = self._check_compliance_type(operation, compliance_type)
                compliance_scores[compliance_type.value] = type_score
                violations.extend(type_violations)
            
            # Check custom rules
            for rule in self.config.custom_rules:
                if rule.enabled:
                    violation = self._check_custom_rule(rule, operation)
                    if violation:
                        violations.append(violation)
            
            # Calculate overall status
            overall_status = self._calculate_overall_status(compliance_scores, violations)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(violations)
            
            result = ComplianceCheckResult(
                overall_status=overall_status,
                compliance_scores=compliance_scores,
                violations=violations,
                warnings=warnings,
                recommendations=recommendations,
                metadata={
                    "checked_at": datetime.utcnow().isoformat(),
                    "operation_type": operation.get("type"),
                    "rules_checked": len(self._rules) + len(self.config.custom_rules),
                    "checker": "SafetyRAGComplianceChecker"
                }
            )
            
            # Log violations if enabled
            if self.config.log_violations and violations:
                self._log_compliance_violations(operation, violations)
            
            self.logger.info(
                f"Compliance check completed: {overall_status.value} "
                f"(score: {sum(compliance_scores.values())/len(compliance_scores):.2f})"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {str(e)}")
            return ComplianceCheckResult(
                overall_status=ComplianceStatus.UNKNOWN,
                violations=[ComplianceViolation(
                    rule_id="system_error",
                    rule_name="System Error",
                    compliance_type=ComplianceType.SECURITY,
                    severity="high",
                    description=f"Compliance check failed: {str(e)}"
                )],
                metadata={"error": str(e)}
            )

    def _check_compliance_type(self, operation: Dict[str, Any], compliance_type: ComplianceType) -> Tuple[float, List[ComplianceViolation]]:
        """Check compliance for a specific type."""
        violations = []
        score = 1.0
        
        # Get rules for this compliance type
        type_rules = [r for r in self._rules if r.compliance_type == compliance_type]
        
        for rule in type_rules:
            if not rule.enabled:
                continue
            
            # Run compliance check
            check_method = getattr(self, f"_check_{rule.check_function}", None)
            if check_method:
                violation = check_method(operation, rule)
                if violation:
                    violations.append(violation)
                    score -= 0.1  # Deduct points for violations
        
        # Ensure score is within bounds
        score = max(0.0, min(1.0, score))
        
        return score, violations

    def _check_custom_rule(self, rule: ComplianceRule, operation: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check a custom compliance rule."""
        # Simulate custom rule checking
        if rule.check_function in operation:
            return ComplianceViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                compliance_type=rule.compliance_type,
                severity=rule.severity,
                description=f"Custom rule violation: {rule.description}",
                evidence={"operation": operation.get("id")}
            )
        return None

    def _calculate_overall_status(self, scores: Dict[str, float], violations: List[ComplianceViolation]) -> ComplianceStatus:
        """Calculate overall compliance status."""
        if not scores:
            return ComplianceStatus.UNKNOWN
        
        avg_score = sum(scores.values()) / len(scores)
        
        # Check for critical violations
        critical_violations = [v for v in violations if v.severity == "critical"]
        if critical_violations:
            return ComplianceStatus.VIOLATION
        
        # Determine status based on score
        if avg_score >= 0.9:
            return ComplianceStatus.COMPLIANT
        elif avg_score >= 0.7:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            return ComplianceStatus.NON_COMPLIANT

    def _generate_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate recommendations based on violations."""
        recommendations = []
        
        # Group violations by type
        violation_types = {}
        for violation in violations:
            comp_type = violation.compliance_type.value
            if comp_type not in violation_types:
                violation_types[comp_type] = []
            violation_types[comp_type].append(violation)
        
        # Generate recommendations for each type
        for comp_type, type_violations in violation_types.items():
            if comp_type == "privacy":
                recommendations.append("Review data handling practices and implement privacy controls")
            elif comp_type == "security":
                recommendations.append("Strengthen security measures and implement access controls")
            elif comp_type == "ethics":
                recommendations.append("Review ethical guidelines and implement bias detection")
            elif comp_type == "gdpr":
                recommendations.append("Ensure GDPR compliance through proper data consent and handling")
            elif comp_type == "hipaa":
                recommendations.append("Implement HIPAA-compliant data protection and audit trails")
        
        return recommendations

    def _load_default_rules(self) -> None:
        """Load default compliance rules."""
        # Security compliance rules
        self._rules.extend([
            ComplianceRule(
                id="auth_required",
                name="Authentication Required",
                compliance_type=ComplianceType.SECURITY,
                description="Operations must be authenticated",
                check_function="authentication",
                severity="high"
            ),
            ComplianceRule(
                id="data_encryption",
                name="Data Encryption",
                compliance_type=ComplianceType.SECURITY,
                description="Sensitive data must be encrypted",
                check_function="encryption",
                severity="high"
            ),
            ComplianceRule(
                id="access_control",
                name="Access Control",
                compliance_type=ComplianceType.SECURITY,
                description="Access must be properly controlled",
                check_function="access_control",
                severity="medium"
            )
        ])
        
        # Privacy compliance rules
        self._rules.extend([
            ComplianceRule(
                id="pii_protection",
                name="PII Protection",
                compliance_type=ComplianceType.PRIVACY,
                description="PII must be protected",
                check_function="pii_protection",
                severity="high"
            ),
            ComplianceRule(
                id="data_minimization",
                name="Data Minimization",
                compliance_type=ComplianceType.PRIVACY,
                description="Only collect necessary data",
                check_function="data_minimization",
                severity="medium"
            )
        ])
        
        # Ethics compliance rules
        self._rules.extend([
            ComplianceRule(
                id="bias_detection",
                name="Bias Detection",
                compliance_type=ComplianceType.ETHICS,
                description="Check for biased content",
                check_function="bias_detection",
                severity="medium"
            ),
            ComplianceRule(
                id="transparency",
                name="Transparency",
                compliance_type=ComplianceType.ETHICS,
                description="Operations must be transparent",
                check_function="transparency",
                severity="low"
            )
        ])

    # Compliance check methods
    def _check_authentication(self, operation: Dict[str, Any], rule: ComplianceRule) -> Optional[ComplianceViolation]:
        """Check authentication compliance."""
        if not operation.get("authenticated", False):
            return ComplianceViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                compliance_type=rule.compliance_type,
                severity=rule.severity,
                description="Operation not authenticated",
                remediation="Implement proper authentication"
            )
        return None

    def _check_encryption(self, operation: Dict[str, Any], rule: ComplianceRule) -> Optional[ComplianceViolation]:
        """Check encryption compliance."""
        if "sensitive_data" in operation and not operation.get("encrypted", False):
            return ComplianceViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                compliance_type=rule.compliance_type,
                severity=rule.severity,
                description="Sensitive data not encrypted",
                remediation="Enable encryption for sensitive data"
            )
        return None

    def _check_access_control(self, operation: Dict[str, Any], rule: ComplianceRule) -> Optional[ComplianceViolation]:
        """Check access control compliance."""
        if not operation.get("access_level"):
            return ComplianceViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                compliance_type=rule.compliance_type,
                severity=rule.severity,
                description="No access control defined",
                remediation="Define appropriate access levels"
            )
        return None

    def _check_pii_protection(self, operation: Dict[str, Any], rule: ComplianceRule) -> Optional[ComplianceViolation]:
        """Check PII protection compliance."""
        content = operation.get("content", "") + operation.get("query", "")
        
        # Simple PII detection
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, content):
            return ComplianceViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                compliance_type=rule.compliance_type,
                severity=rule.severity,
                description="PII detected in content",
                remediation="Remove or redact PII from content"
            )
        return None

    def _check_data_minimization(self, operation: Dict[str, Any], rule: ComplianceRule) -> Optional[ComplianceViolation]:
        """Check data minimization compliance."""
        if operation.get("data_collected", 0) > operation.get("data_needed", 0):
            return ComplianceViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                compliance_type=rule.compliance_type,
                severity=rule.severity,
                description="Excess data collected",
                remediation="Collect only necessary data"
            )
        return None

    def _check_bias_detection(self, operation: Dict[str, Any], rule: ComplianceRule) -> Optional[ComplianceViolation]:
        """Check bias detection compliance."""
        content = operation.get("content", "").lower()
        biased_terms = ["gender", "race", "age", "religion"]
        
        if any(term in content for term in biased_terms):
            return ComplianceViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                compliance_type=rule.compliance_type,
                severity=rule.severity,
                description="Potentially biased content detected",
                remediation="Review and mitigate bias in content"
            )
        return None

    def _check_transparency(self, operation: Dict[str, Any], rule: ComplianceRule) -> Optional[ComplianceViolation]:
        """Check transparency compliance."""
        if not operation.get("source_explained", False):
            return ComplianceViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                compliance_type=rule.compliance_type,
                severity=rule.severity,
                description="Source not explained",
                remediation="Provide transparency about data sources"
            )
        return None

    def _log_compliance_violations(self, operation: Dict[str, Any], violations: List[ComplianceViolation]) -> None:
        """Log compliance violations."""
        for violation in violations:
            log_entry = {
                "timestamp": violation.timestamp.isoformat(),
                "operation_id": operation.get("id"),
                "rule_id": violation.rule_id,
                "compliance_type": violation.compliance_type.value,
                "severity": violation.severity,
                "description": violation.description
            }
            self.logger.warning(f"Compliance violation: {log_entry}")

    def add_compliance_rule(self, rule: ComplianceRule) -> None:
        """Add a custom compliance rule.
        
        Args:
            rule: Compliance rule to add
        """
        self.logger.info(f"Adding compliance rule: {rule.id}")
        self.config.custom_rules.append(rule)

    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get summary of compliance configuration.
        
        Returns:
            Dict: Compliance configuration summary
        """
        return {
            "enabled_compliance_types": [t.value for t in self.config.enabled_compliance_types],
            "total_rules": len(self._rules) + len(self.config.custom_rules),
            "strict_mode": self.config.strict_mode,
            "auto_remediation": self.config.auto_remediation,
            "exempt_operations": len(self.config.exempt_operations)
        }


# Factory function for easy instantiation
def create_safety_rag_compliance_checker(
    enabled_compliance_types: List[str] = None,
    strict_mode: bool = False,
    auto_remediation: bool = False,
    **kwargs
) -> SafetyRAGComplianceChecker:
    """Create a configured safety RAG compliance checker."""
    config = SafetyRAGComplianceConfig(
        enabled_compliance_types=[ComplianceType(t) for t in (enabled_compliance_types or ["security", "privacy", "ethics"])],
        strict_mode=strict_mode,
        auto_remediation=auto_remediation,
        **kwargs
    )
    return SafetyRAGComplianceChecker(config)


# Convenience function for direct usage
def check_rag_compliance(
    operation: Dict[str, Any],
    compliance_types: List[str] = None,
    strict_mode: bool = False,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Check RAG operation for compliance.
    
    Args:
        operation: RAG operation to check
        compliance_types: List of compliance types to check
        strict_mode: Whether to use strict mode
        config: Optional checker configuration
        
    Returns:
        Dict: Compliance check results
    """
    # Create checker and execute
    checker_config = SafetyRAGComplianceConfig(
        enabled_compliance_types=[ComplianceType(t) for t in (compliance_types or ["security", "privacy", "ethics"])],
        strict_mode=strict_mode,
        **config or {}
    )
    checker = SafetyRAGComplianceChecker(checker_config)
    result = checker.check_compliance(operation)
    
    # Convert result to dict for JSON serialization
    return {
        "overall_status": result.overall_status.value,
        "compliance_scores": result.compliance_scores,
        "violations": [
            {
                "rule_id": v.rule_id,
                "rule_name": v.rule_name,
                "compliance_type": v.compliance_type.value,
                "severity": v.severity,
                "description": v.description,
                "evidence": v.evidence,
                "remediation": v.remediation,
                "timestamp": v.timestamp.isoformat()
            }
            for v in result.violations
        ],
        "warnings": result.warnings,
        "recommendations": result.recommendations,
        "metadata": result.metadata
    }
