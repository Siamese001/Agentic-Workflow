"""Safety Ethics Validator - Validates content and operations for ethical compliance.

This module provides ethical validation for AI operations,
including bias detection, fairness checks, and ethical guidelines compliance.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Set
import logging
import re
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EthicalCategory(Enum):
    """Categories of ethical concerns."""
    BIAS = "bias"
    FAIRNESS = "fairness"
    PRIVACY = "privacy"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    SAFETY = "safety"
    CONSENT = "consent"
    DISCRIMINATION = "discrimination"


class EthicalSeverity(Enum):
    """Severity levels for ethical violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EthicalRule:
    """Definition of an ethical rule."""
    id: str
    name: str
    category: EthicalCategory
    description: str
    check_pattern: Optional[str] = None
    check_function: Optional[str] = None
    severity: EthicalSeverity = EthicalSeverity.MEDIUM
    enabled: bool = True
    threshold: Optional[float] = None


@dataclass
class EthicalViolation:
    """Record of an ethical violation."""
    rule_id: str
    rule_name: str
    category: EthicalCategory
    severity: EthicalSeverity
    description: str
    detected_content: Optional[str] = None
    confidence: float = 0.0
    recommendation: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EthicsValidationResult:
    """Result of ethics validation."""
    ethical: bool
    violations: List[EthicalViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    ethical_score: float = 1.0
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyEthicsConfig:
    """Configuration for safety ethics validation."""
    enabled_categories: List[EthicalCategory] = field(default_factory=lambda: [
        EthicalCategory.BIAS, EthicalCategory.FAIRNESS, EthicalCategory.PRIVACY
    ])
    strict_mode: bool = False
    confidence_threshold: float = 0.7
    custom_rules: List[EthicalRule] = field(default_factory=list)
    protected_attributes: List[str] = field(default_factory=lambda: [
        "gender", "race", "age", "religion", "disability", "sexual_orientation"
    ])
    log_level: str = "INFO"


class SafetyEthicsValidator:
    """Main class for safety ethics validation."""

    def __init__(self, config: Optional[SafetyEthicsConfig] = None):
        self.config = config or SafetyEthicsConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._rules = []
        self._load_default_rules()

    def validate_ethics(self, content: str, context: Optional[Dict[str, Any]] = None) -> EthicsValidationResult:
        """Validate content for ethical compliance.
        
        Args:
            content: Content to validate
            context: Optional context information
            
        Returns:
            EthicsValidationResult: Ethics validation results
        """
        self.logger.info("Validating content for ethical compliance")
        
        violations = []
        warnings = []
        recommendations = []
        
        try:
            # Check each enabled category
            for category in self.config.enabled_categories:
                category_rules = [r for r in self._rules if r.category == category and r.enabled]
                
                for rule in category_rules:
                    violation = self._check_ethical_rule(rule, content, context)
                    
                    if violation and violation.confidence >= self.config.confidence_threshold:
                        violations.append(violation)
                        if violation.recommendation:
                            recommendations.append(violation.recommendation)
                    elif violation:
                        warnings.append(f"Low confidence: {violation.description}")
            
            # Check custom rules
            for rule in self.config.custom_rules:
                if rule.enabled:
                    violation = self._check_ethical_rule(rule, content, context)
                    if violation and violation.confidence >= self.config.confidence_threshold:
                        violations.append(violation)
            
            # Calculate ethical score
            ethical_score = self._calculate_ethical_score(violations)
            
            # Determine if content is ethical
            ethical = len(violations) == 0 or (not self.config.strict_mode and ethical_score >= 0.7)
            
            result = EthicsValidationResult(
                ethical=ethical,
                violations=violations,
                warnings=warnings,
                ethical_score=ethical_score,
                recommendations=recommendations,
                metadata={
                    "validated_at": datetime.utcnow().isoformat(),
                    "categories_checked": [c.value for c in self.config.enabled_categories],
                    "content_length": len(content),
                    "validator": "SafetyEthicsValidator"
                }
            )
            
            self.logger.info(
                f"Ethics validation completed: {'ethical' if ethical else 'unethical'} "
                f"(score: {ethical_score:.2f}, violations: {len(violations)})"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ethics validation failed: {str(e)}")
            return EthicsValidationResult(
                ethical=False,
                violations=[EthicalViolation(
                    rule_id="system_error",
                    rule_name="System Error",
                    category=EthicalCategory.SAFETY,
                    severity=EthicalSeverity.HIGH,
                    description=f"Validation failed: {str(e)}",
                    confidence=1.0
                )],
                metadata={"error": str(e)}
            )

    def _check_ethical_rule(self, rule: EthicalRule, content: str, context: Optional[Dict[str, Any]]) -> Optional[EthicalViolation]:
        """Check a single ethical rule."""
        try:
            # Pattern-based check
            if rule.check_pattern:
                matches = re.findall(rule.check_pattern, content, re.IGNORECASE)
                if matches:
                    return EthicalViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        description=f"Potential {rule.category.value} issue detected",
                        detected_content=str(matches[:3]),
                        confidence=0.8,
                        recommendation=f"Review content for {rule.category.value} concerns"
                    )
            
            # Function-based check
            if rule.check_function:
                check_method = getattr(self, f"_check_{rule.check_function}", None)
                if check_method:
                    return check_method(rule, content, context)
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Rule check {rule.id} failed: {str(e)}")
            return None

    def _calculate_ethical_score(self, violations: List[EthicalViolation]) -> float:
        """Calculate overall ethical score."""
        if not violations:
            return 1.0
        
        # Weight violations by severity
        severity_weights = {
            EthicalSeverity.LOW: 0.1,
            EthicalSeverity.MEDIUM: 0.3,
            EthicalSeverity.HIGH: 0.5,
            EthicalSeverity.CRITICAL: 1.0
        }
        
        total_penalty = sum(severity_weights.get(v.severity, 0.3) for v in violations)
        score = max(0.0, 1.0 - total_penalty)
        
        return round(score, 2)

    def _load_default_rules(self) -> None:
        """Load default ethical rules."""
        # Bias rules
        self._rules.extend([
            EthicalRule(
                id="gender_bias",
                name="Gender Bias Detection",
                category=EthicalCategory.BIAS,
                description="Detects gender-based bias in content",
                check_pattern=r'\b(men|women|he|she|him|her)\s+(are|is|should|must|always|never)\s+\w+',
                severity=EthicalSeverity.MEDIUM
            ),
            EthicalRule(
                id="racial_bias",
                name="Racial Bias Detection",
                category=EthicalCategory.BIAS,
                description="Detects racial bias in content",
                check_function="racial_bias",
                severity=EthicalSeverity.HIGH
            ),
            EthicalRule(
                id="age_bias",
                name="Age Bias Detection",
                category=EthicalCategory.BIAS,
                description="Detects age-related bias",
                check_pattern=r'\b(young|old|elderly|millennial|boomer)\s+(people|persons|individuals)\s+\w+',
                severity=EthicalSeverity.MEDIUM
            )
        ])
        
        # Fairness rules
        self._rules.extend([
            EthicalRule(
                id="equal_opportunity",
                name="Equal Opportunity Language",
                category=EthicalCategory.FAIRNESS,
                description="Ensures equal opportunity language",
                check_function="equal_opportunity",
                severity=EthicalSeverity.MEDIUM
            ),
            EthicalRule(
                id="stereotyping",
                name="Stereotyping Detection",
                category=EthicalCategory.FAIRNESS,
                description="Detects harmful stereotypes",
                check_function="stereotyping",
                severity=EthicalSeverity.HIGH
            )
        ])
        
        # Privacy rules
        self._rules.extend([
            EthicalRule(
                id="pii_exposure",
                name="PII Exposure",
                category=EthicalCategory.PRIVACY,
                description="Detects potential PII exposure",
                check_pattern=r'\b(\d{3}-\d{2}-\d{4}|\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})\b',
                severity=EthicalSeverity.HIGH
            ),
            EthicalRule(
                id="privacy_consent",
                name="Privacy Consent",
                category=EthicalCategory.PRIVACY,
                description="Checks for privacy consent mentions",
                check_function="privacy_consent",
                severity=EthicalSeverity.MEDIUM
            )
        ])

    # Ethical check methods
    def _check_racial_bias(self, rule: EthicalRule, content: str, context: Optional[Dict[str, Any]]) -> Optional[EthicalViolation]:
        """Check for racial bias."""
        racial_terms = ["race", "ethnicity", "nationality", "culture"]
        content_lower = content.lower()
        
        for term in racial_terms:
            if term in content_lower:
                # Look for problematic patterns
                if any(word in content_lower for word in ["inferior", "superior", "better", "worse"]):
                    return EthicalViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        description="Potential racial bias detected",
                        detected_content=term,
                        confidence=0.7,
                        recommendation="Review content for racial bias"
                    )
        
        return None

    def _check_equal_opportunity(self, rule: EthicalRule, content: str, context: Optional[Dict[str, Any]]) -> Optional[EthicalViolation]:
        """Check for equal opportunity language."""
        discriminatory_terms = ["only men", "only women", "no disabilities", "age limit"]
        content_lower = content.lower()
        
        for term in discriminatory_terms:
            if term in content_lower:
                return EthicalViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    description="Discriminatory language detected",
                    detected_content=term,
                    confidence=0.8,
                    recommendation="Use inclusive language"
                )
        
        return None

    def _check_stereotyping(self, rule: EthicalRule, content: str, context: Optional[Dict[str, Any]]) -> Optional[EthicalViolation]:
        """Check for harmful stereotypes."""
        stereotype_patterns = [
            r"all\s+(\w+)\s+are",
            r"(\w+)\s+can't\s+(\w+)",
            r"(\w+)\s+always\s+(\w+)",
            r"typical\s+(\w+)"
        ]
        
        for pattern in stereotype_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                return EthicalViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    description="Potential stereotyping detected",
                    detected_content=str(matches[:3]),
                    confidence=0.6,
                    recommendation="Avoid stereotypes and generalizations"
                )
        
        return None

    def _check_privacy_consent(self, rule: EthicalRule, content: str, context: Optional[Dict[str, Any]]) -> Optional[EthicalViolation]:
        """Check for privacy consent mentions."""
        privacy_terms = ["personal data", "private information", "sensitive data"]
        consent_terms = ["consent", "permission", "agreement", "authorization"]
        
        content_lower = content.lower()
        has_privacy = any(term in content_lower for term in privacy_terms)
        has_consent = any(term in content_lower for term in consent_terms)
        
        if has_privacy and not has_consent:
            return EthicalViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                category=rule.category,
                severity=rule.severity,
                description="Privacy data mentioned without consent",
                detected_content="privacy data without consent",
                confidence=0.7,
                recommendation="Include consent information when handling private data"
            )
        
        return None

    def add_rule(self, rule: EthicalRule) -> None:
        """Add a custom ethical rule.
        
        Args:
            rule: Rule to add
        """
        self.logger.info(f"Adding ethical rule: {rule.id}")
        self.config.custom_rules.append(rule)

    def get_ethics_summary(self) -> Dict[str, Any]:
        """Get summary of ethics configuration.
        
        Returns:
            Dict: Ethics configuration summary
        """
        return {
            "enabled_categories": [c.value for c in self.config.enabled_categories],
            "total_rules": len(self._rules) + len(self.config.custom_rules),
            "strict_mode": self.config.strict_mode,
            "confidence_threshold": self.config.confidence_threshold,
            "protected_attributes": self.config.protected_attributes
        }


# Factory function for easy instantiation
def create_safety_ethics_validator(
    enabled_categories: List[str] = None,
    strict_mode: bool = False,
    confidence_threshold: float = 0.7,
    **kwargs
) -> SafetyEthicsValidator:
    """Create a configured safety ethics validator."""
    config = SafetyEthicsConfig(
        enabled_categories=[EthicalCategory(c) for c in (enabled_categories or ["bias", "fairness", "privacy"])],
        strict_mode=strict_mode,
        confidence_threshold=confidence_threshold,
        **kwargs
    )
    return SafetyEthicsValidator(config)


# Convenience function for direct usage
def validate_safety_ethics(
    content: str,
    categories: List[str] = None,
    strict_mode: bool = False,
    context: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Validate content for ethical compliance.
    
    Args:
        content: Content to validate
        categories: List of ethical categories to check
        strict_mode: Whether to use strict validation
        context: Optional context information
        config: Optional validator configuration
        
    Returns:
        Dict: Ethics validation results
    """
    # Create validator and execute
    validator_config = SafetyEthicsConfig(
        enabled_categories=[EthicalCategory(c) for c in (categories or ["bias", "fairness", "privacy"])],
        strict_mode=strict_mode,
        **config or {}
    )
    validator = SafetyEthicsValidator(validator_config)
    result = validator.validate_ethics(content, context)
    
    # Convert result to dict for JSON serialization
    return {
        "ethical": result.ethical,
        "violations": [
            {
                "rule_id": v.rule_id,
                "rule_name": v.rule_name,
                "category": v.category.value,
                "severity": v.severity.value,
                "description": v.description,
                "detected_content": v.detected_content,
                "confidence": v.confidence,
                "recommendation": v.recommendation,
                "timestamp": v.timestamp.isoformat()
            }
            for v in result.violations
        ],
        "warnings": result.warnings,
        "ethical_score": result.ethical_score,
        "recommendations": result.recommendations,
        "metadata": result.metadata
    }
