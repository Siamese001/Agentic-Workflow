"""RAG Compliance Checker - Checks RAG operations for compliance with policies and standards.

This module provides compliance checking for RAG operations,
ensuring adherence to organizational policies and best practices.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ComplianceCategory(Enum):
    """Categories of compliance checks."""
    DATA_QUALITY = "data_quality"
    PRIVACY = "privacy"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ETHICS = "ethics"
    GOVERNANCE = "governance"


class ComplianceLevel(Enum):
    """Compliance levels."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    EXEMPT = "exempt"


@dataclass
class CompliancePolicy:
    """Definition of a compliance policy."""
    id: str
    name: str
    category: ComplianceCategory
    description: str
    check_function: str
    severity: str = "medium"
    enabled: bool = True
    threshold: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceIssue:
    """Record of a compliance issue."""
    policy_id: str
    policy_name: str
    category: ComplianceCategory
    severity: str
    description: str
    actual_value: Optional[Any] = None
    expected_value: Optional[Any] = None
    recommendation: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceReport:
    """Report of compliance check results."""
    operation_id: str
    overall_compliance: ComplianceLevel
    compliance_score: float
    issues: List[ComplianceIssue] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    exempt_policies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGComplianceConfig:
    """Configuration for RAG compliance checking."""
    enabled_categories: List[ComplianceCategory] = field(default_factory=lambda: [
        ComplianceCategory.DATA_QUALITY, ComplianceCategory.SECURITY, ComplianceCategory.PRIVACY
    ])
    strict_mode: bool = False
    auto_exempt_low_risk: bool = True
    score_threshold: float = 0.8
    custom_policies: List[CompliancePolicy] = field(default_factory=list)
    exemption_list: List[str] = field(default_factory=list)
    log_level: str = "INFO"


class RAGComplianceChecker:
    """Main class for RAG compliance checking."""

    def __init__(self, config: Optional[RAGComplianceConfig] = None):
        self.config = config or RAGComplianceConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._policies = []
        self._load_default_policies()

    def check_compliance(self, operation: Dict[str, Any]) -> ComplianceReport:
        """Check RAG operation for compliance.
        
        Args:
            operation: RAG operation to check
            
        Returns:
            ComplianceReport: Compliance check report
        """
        self.logger.info(f"Checking compliance for operation: {operation.get('id', 'unknown')}")
        
        issues = []
        passed_checks = []
        exempt_policies = []
        
        try:
            operation_id = operation.get("id", "unknown")
            
            # Check each enabled category
            for category in self.config.enabled_categories:
                category_policies = [p for p in self._policies if p.category == category and p.enabled]
                
                for policy in category_policies:
                    # Check if policy is exempt
                    if policy.id in self.config.exemption_list:
                        exempt_policies.append(policy.id)
                        continue
                    
                    # Run compliance check
                    issue = self._check_policy(policy, operation)
                    
                    if issue:
                        issues.append(issue)
                    else:
                        passed_checks.append(policy.id)
            
            # Check custom policies
            for policy in self.config.custom_policies:
                if policy.enabled and policy.id not in self.config.exemption_list:
                    issue = self._check_policy(policy, operation)
                    if issue:
                        issues.append(issue)
                    else:
                        passed_checks.append(policy.id)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(issues, passed_checks, exempt_policies)
            
            # Determine overall compliance
            overall_compliance = self._determine_compliance_level(compliance_score, issues)
            
            report = ComplianceReport(
                operation_id=operation_id,
                overall_compliance=overall_compliance,
                compliance_score=compliance_score,
                issues=issues,
                passed_checks=passed_checks,
                exempt_policies=exempt_policies,
                metadata={
                    "checked_at": datetime.utcnow().isoformat(),
                    "categories_checked": [c.value for c in self.config.enabled_categories],
                    "total_policies": len(self._policies) + len(self.config.custom_policies),
                    "checker": "RAGComplianceChecker"
                }
            )
            
            self.logger.info(
                f"Compliance check completed: {overall_compliance.value} "
                f"(score: {compliance_score:.2f}, issues: {len(issues)})"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {str(e)}")
            return ComplianceReport(
                operation_id=operation.get("id", "unknown"),
                overall_compliance=ComplianceLevel.NON_COMPLIANT,
                compliance_score=0.0,
                issues=[ComplianceIssue(
                    policy_id="system_error",
                    policy_name="System Error",
                    category=ComplianceCategory.GOVERNANCE,
                    severity="critical",
                    description=f"Compliance check failed: {str(e)}"
                )],
                metadata={"error": str(e)}
            )

    def _check_policy(self, policy: CompliancePolicy, operation: Dict[str, Any]) -> Optional[ComplianceIssue]:
        """Check a single compliance policy."""
        check_method = getattr(self, f"_check_{policy.check_function}", None)
        
        if check_method:
            try:
                return check_method(operation, policy)
            except Exception as e:
                self.logger.warning(f"Policy check {policy.id} failed: {str(e)}")
                return ComplianceIssue(
                    policy_id=policy.id,
                    policy_name=policy.name,
                    category=policy.category,
                    severity="medium",
                    description=f"Policy check failed: {str(e)}"
                )
        
        return None

    def _calculate_compliance_score(self, issues: List[ComplianceIssue], passed: List[str], exempt: List[str]) -> float:
        """Calculate overall compliance score."""
        total_checks = len(issues) + len(passed) + len(exempt)
        
        if total_checks == 0:
            return 1.0
        
        # Weight issues by severity
        severity_weights = {"low": 0.1, "medium": 0.3, "high": 0.5, "critical": 1.0}
        penalty = sum(severity_weights.get(issue.severity, 0.3) for issue in issues)
        
        # Calculate score
        score = (len(passed) + len(exempt)) / total_checks
        score = max(0.0, score - penalty)
        
        return round(score, 2)

    def _determine_compliance_level(self, score: float, issues: List[ComplianceIssue]) -> ComplianceLevel:
        """Determine overall compliance level."""
        # Check for critical issues
        if any(issue.severity == "critical" for issue in issues):
            return ComplianceLevel.NON_COMPLIANT
        
        # Check score threshold
        if score >= self.config.score_threshold:
            return ComplianceLevel.COMPLIANT
        elif score >= 0.6:
            return ComplianceLevel.PARTIALLY_COMPLIANT
        else:
            return ComplianceLevel.NON_COMPLIANT

    def _load_default_policies(self) -> None:
        """Load default compliance policies."""
        # Data quality policies
        self._policies.extend([
            CompliancePolicy(
                id="data_freshness",
                name="Data Freshness Check",
                category=ComplianceCategory.DATA_QUALITY,
                description="Data must be fresh and up-to-date",
                check_function="data_freshness",
                severity="medium",
                threshold=30  # days
            ),
            CompliancePolicy(
                id="data_completeness",
                name="Data Completeness Check",
                category=ComplianceCategory.DATA_QUALITY,
                description="Required fields must be present",
                check_function="data_completeness",
                severity="high"
            ),
            CompliancePolicy(
                id="source_reliability",
                name="Source Reliability Check",
                category=ComplianceCategory.DATA_QUALITY,
                description="Sources must be reliable and verified",
                check_function="source_reliability",
                severity="medium"
            )
        ])
        
        # Security policies
        self._policies.extend([
            CompliancePolicy(
                id="authentication",
                name="Authentication Required",
                category=ComplianceCategory.SECURITY,
                description="Operations must be authenticated",
                check_function="authentication",
                severity="critical"
            ),
            CompliancePolicy(
                id="authorization",
                name="Authorization Check",
                category=ComplianceCategory.SECURITY,
                description="User must be authorized for operation",
                check_function="authorization",
                severity="high"
            ),
            CompliancePolicy(
                id="data_encryption",
                name="Data Encryption",
                category=ComplianceCategory.SECURITY,
                description="Sensitive data must be encrypted",
                check_function="data_encryption",
                severity="high"
            )
        ])
        
        # Privacy policies
        self._policies.extend([
            CompliancePolicy(
                id="pii_protection",
                name="PII Protection",
                category=ComplianceCategory.PRIVACY,
                description="PII must be protected or anonymized",
                check_function="pii_protection",
                severity="high"
            ),
            CompliancePolicy(
                id="consent_management",
                name="Consent Management",
                category=ComplianceCategory.PRIVACY,
                description="User consent must be obtained and recorded",
                check_function="consent_management",
                severity="medium"
            )
        ])

    # Policy check methods
    def _check_data_freshness(self, operation: Dict[str, Any], policy: CompliancePolicy) -> Optional[ComplianceIssue]:
        """Check data freshness."""
        data_age_days = operation.get("data_age_days", 0)
        
        if data_age_days > policy.threshold:
            return ComplianceIssue(
                policy_id=policy.id,
                policy_name=policy.name,
                category=policy.category,
                severity=policy.severity,
                description=f"Data is {data_age_days} days old, exceeds threshold of {policy.threshold} days",
                actual_value=data_age_days,
                expected_value=f"< {policy.threshold} days",
                recommendation="Refresh data or use more recent sources"
            )
        return None

    def _check_data_completeness(self, operation: Dict[str, Any], policy: CompliancePolicy) -> Optional[ComplianceIssue]:
        """Check data completeness."""
        required_fields = ["id", "content", "timestamp"]
        missing_fields = [f for f in required_fields if f not in operation]
        
        if missing_fields:
            return ComplianceIssue(
                policy_id=policy.id,
                policy_name=policy.name,
                category=policy.category,
                severity=policy.severity,
                description=f"Missing required fields: {', '.join(missing_fields)}",
                actual_value=f"Missing: {missing_fields}",
                expected_value=f"All fields: {required_fields}",
                recommendation="Add missing required fields"
            )
        return None

    def _check_source_reliability(self, operation: Dict[str, Any], policy: CompliancePolicy) -> Optional[ComplianceIssue]:
        """Check source reliability."""
        source_score = operation.get("source_reliability_score", 1.0)
        
        if source_score < 0.7:
            return ComplianceIssue(
                policy_id=policy.id,
                policy_name=policy.name,
                category=policy.category,
                severity=policy.severity,
                description=f"Source reliability score {source_score} is below threshold",
                actual_value=source_score,
                expected_value=">= 0.7",
                recommendation="Use more reliable sources or verify existing ones"
            )
        return None

    def _check_authentication(self, operation: Dict[str, Any], policy: CompliancePolicy) -> Optional[ComplianceIssue]:
        """Check authentication."""
        if not operation.get("authenticated", False):
            return ComplianceIssue(
                policy_id=policy.id,
                policy_name=policy.name,
                category=policy.category,
                severity=policy.severity,
                description="Operation is not authenticated",
                actual_value="False",
                expected_value="True",
                recommendation="Implement proper authentication"
            )
        return None

    def _check_authorization(self, operation: Dict[str, Any], policy: CompliancePolicy) -> Optional[ComplianceIssue]:
        """Check authorization."""
        if not operation.get("authorized", False):
            return ComplianceIssue(
                policy_id=policy.id,
                policy_name=policy.name,
                category=policy.category,
                severity=policy.severity,
                description="Operation is not authorized",
                actual_value="False",
                expected_value="True",
                recommendation="Check user permissions"
            )
        return None

    def _check_data_encryption(self, operation: Dict[str, Any], policy: CompliancePolicy) -> Optional[ComplianceIssue]:
        """Check data encryption."""
        has_sensitive_data = operation.get("has_sensitive_data", False)
        is_encrypted = operation.get("encrypted", False)
        
        if has_sensitive_data and not is_encrypted:
            return ComplianceIssue(
                policy_id=policy.id,
                policy_name=policy.name,
                category=policy.category,
                severity=policy.severity,
                description="Sensitive data is not encrypted",
                actual_value="False",
                expected_value="True",
                recommendation="Enable encryption for sensitive data"
            )
        return None

    def _check_pii_protection(self, operation: Dict[str, Any], policy: CompliancePolicy) -> Optional[ComplianceIssue]:
        """Check PII protection."""
        has_pii = operation.get("contains_pii", False)
        pii_protected = operation.get("pii_protected", False)
        
        if has_pii and not pii_protected:
            return ComplianceIssue(
                policy_id=policy.id,
                policy_name=policy.name,
                category=policy.category,
                severity=policy.severity,
                description="PII detected but not protected",
                actual_value="False",
                expected_value="True",
                recommendation="Implement PII protection or anonymization"
            )
        return None

    def _check_consent_management(self, operation: Dict[str, Any], policy: CompliancePolicy) -> Optional[ComplianceIssue]:
        """Check consent management."""
        if not operation.get("user_consent", False):
            return ComplianceIssue(
                policy_id=policy.id,
                policy_name=policy.name,
                category=policy.category,
                severity=policy.severity,
                description="User consent not recorded",
                actual_value="False",
                expected_value="True",
                recommendation="Obtain and record user consent"
            )
        return None

    def add_policy(self, policy: CompliancePolicy) -> None:
        """Add a custom compliance policy.
        
        Args:
            policy: Policy to add
        """
        self.logger.info(f"Adding compliance policy: {policy.id}")
        self._policies.append(policy)

    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get summary of compliance configuration.
        
        Returns:
            Dict: Compliance configuration summary
        """
        return {
            "enabled_categories": [c.value for c in self.config.enabled_categories],
            "total_policies": len(self._policies) + len(self.config.custom_policies),
            "strict_mode": self.config.strict_mode,
            "score_threshold": self.config.score_threshold,
            "exempt_policies": len(self.config.exemption_list)
        }


# Factory function for easy instantiation
def create_rag_compliance_checker(
    enabled_categories: List[str] = None,
    strict_mode: bool = False,
    score_threshold: float = 0.8,
    **kwargs
) -> RAGComplianceChecker:
    """Create a configured RAG compliance checker."""
    config = RAGComplianceConfig(
        enabled_categories=[ComplianceCategory(c) for c in (enabled_categories or ["data_quality", "security", "privacy"])],
        strict_mode=strict_mode,
        score_threshold=score_threshold,
        **kwargs
    )
    return RAGComplianceChecker(config)


# Convenience function for direct usage
def check_rag_compliance(
    operation: Dict[str, Any],
    categories: List[str] = None,
    strict_mode: bool = False,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Check RAG operation for compliance.
    
    Args:
        operation: RAG operation to check
        categories: List of compliance categories to check
        strict_mode: Whether to use strict mode
        config: Optional checker configuration
        
    Returns:
        Dict: Compliance check report
    """
    # Create checker and execute
    checker_config = RAGComplianceConfig(
        enabled_categories=[ComplianceCategory(c) for c in (categories or ["data_quality", "security", "privacy"])],
        strict_mode=strict_mode,
        **config or {}
    )
    checker = RAGComplianceChecker(checker_config)
    report = checker.check_compliance(operation)
    
    # Convert report to dict for JSON serialization
    return {
        "operation_id": report.operation_id,
        "overall_compliance": report.overall_compliance.value,
        "compliance_score": report.compliance_score,
        "issues": [
            {
                "policy_id": i.policy_id,
                "policy_name": i.policy_name,
                "category": i.category.value,
                "severity": i.severity,
                "description": i.description,
                "actual_value": i.actual_value,
                "expected_value": i.expected_value,
                "recommendation": i.recommendation,
                "timestamp": i.timestamp.isoformat()
            }
            for i in report.issues
        ],
        "passed_checks": report.passed_checks,
        "exempt_policies": report.exempt_policies,
        "metadata": report.metadata
    }
