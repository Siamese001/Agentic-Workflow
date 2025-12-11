"""Schema Safety Ethics Validator - Validates schemas for ethical compliance.

This module provides ethical validation for data schemas,
including bias detection in schema design, fairness checks, and ethical guidelines compliance.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Set
import logging
import re
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SchemaEthicalCategory(Enum):
    """Categories of ethical concerns in schemas."""
    BIAS_IN_FIELDS = "bias_in_fields"
    DISCRIMINATORY_LABELS = "discriminatory_labels"
    PRIVACY_VIOLATION = "privacy_violation"
    SENSITIVE_ATTRIBUTES = "sensitive_attributes"
    UNFAIR_CONSTRAINTS = "unfair_constraints"
    ETHICAL_VIOLATION = "ethical_violation"


class EthicalSeverity(Enum):
    """Severity levels for ethical violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SchemaEthicalRule:
    """Definition of a schema ethical rule."""
    id: str
    name: str
    category: SchemaEthicalCategory
    description: str
    check_pattern: Optional[str] = None
    check_function: Optional[str] = None
    severity: EthicalSeverity = EthicalSeverity.MEDIUM
    enabled: bool = True
    threshold: Optional[float] = None


@dataclass
class SchemaEthicalViolation:
    """Record of a schema ethical violation."""
    rule_id: str
    rule_name: str
    category: SchemaEthicalCategory
    severity: EthicalSeverity
    description: str
    field_name: Optional[str] = None
    detected_content: Optional[str] = None
    confidence: float = 0.0
    recommendation: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SchemaEthicsValidationResult:
    """Result of schema ethics validation."""
    ethical: bool
    violations: List[SchemaEthicalViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    ethical_score: float = 1.0
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaSafetyEthicsConfig:
    """Configuration for schema safety ethics validation."""
    enabled_categories: List[SchemaEthicalCategory] = field(default_factory=lambda: [
        SchemaEthicalCategory.BIAS_IN_FIELDS, SchemaEthicalCategory.PRIVACY_VIOLATION, SchemaEthicalCategory.SENSITIVE_ATTRIBUTES
    ])
    strict_mode: bool = False
    confidence_threshold: float = 0.7
    custom_rules: List[SchemaEthicalRule] = field(default_factory=list)
    protected_attributes: List[str] = field(default_factory=lambda: [
        "gender", "race", "ethnicity", "age", "religion", "disability", "sexual_orientation"
    ])
    sensitive_field_patterns: List[str] = field(default_factory=lambda: [
        r".*ssn.*", r".*social_security.*", r".*credit_card.*", r".*password.*", r".*secret.*"
    ])
    log_level: str = "INFO"


class SchemaSafetyEthicsValidator:
    """Main class for schema safety ethics validation."""

    def __init__(self, config: Optional[SchemaSafetyEthicsConfig] = None):
        self.config = config or SchemaSafetyEthicsConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._rules = []
        self._load_default_rules()

    def validate_schema_ethics(self, schema: Dict[str, Any]) -> SchemaEthicsValidationResult:
        """Validate schema for ethical compliance.
        
        Args:
            schema: Schema definition to validate
            
        Returns:
            SchemaEthicsValidationResult: Schema ethics validation results
        """
        self.logger.info("Validating schema for ethical compliance")
        
        violations = []
        warnings = []
        recommendations = []
        
        try:
            # Extract fields from schema
            fields = self._extract_fields(schema)
            
            # Check each enabled category
            for category in self.config.enabled_categories:
                category_rules = [r for r in self._rules if r.category == category and r.enabled]
                
                for rule in category_rules:
                    rule_violations = self._check_schema_rule(rule, schema, fields)
                    violations.extend(rule_violations)
            
            # Check custom rules
            for rule in self.config.custom_rules:
                if rule.enabled:
                    rule_violations = self._check_schema_rule(rule, schema, fields)
                    violations.extend(rule_violations)
            
            # Filter violations by confidence threshold
            high_confidence_violations = [v for v in violations if v.confidence >= self.config.confidence_threshold]
            low_confidence_violations = [v for v in violations if v.confidence < self.config.confidence_threshold]
            
            # Add low confidence violations as warnings
            for violation in low_confidence_violations:
                warnings.append(f"Low confidence: {violation.description}")
            
            # Collect recommendations
            recommendations = list(set(v.recommendation for v in high_confidence_violations if v.recommendation))
            
            # Calculate ethical score
            ethical_score = self._calculate_ethical_score(high_confidence_violations)
            
            # Determine if schema is ethical
            ethical = len(high_confidence_violations) == 0 or (not self.config.strict_mode and ethical_score >= 0.7)
            
            result = SchemaEthicsValidationResult(
                ethical=ethical,
                violations=high_confidence_violations,
                warnings=warnings,
                ethical_score=ethical_score,
                recommendations=recommendations,
                metadata={
                    "validated_at": datetime.utcnow().isoformat(),
                    "categories_checked": [c.value for c in self.config.enabled_categories],
                    "total_fields": len(fields),
                    "validator": "SchemaSafetyEthicsValidator"
                }
            )
            
            self.logger.info(
                f"Schema ethics validation completed: {'ethical' if ethical else 'unethical'} "
                f"(score: {ethical_score:.2f}, violations: {len(high_confidence_violations)})"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Schema ethics validation failed: {str(e)}")
            return SchemaEthicsValidationResult(
                ethical=False,
                violations=[SchemaEthicalViolation(
                    rule_id="system_error",
                    rule_name="System Error",
                    category=SchemaEthicalCategory.ETHICAL_VIOLATION,
                    severity=EthicalSeverity.HIGH,
                    description=f"Validation failed: {str(e)}",
                    confidence=1.0
                )],
                metadata={"error": str(e)}
            )

    def _extract_fields(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract field definitions from schema."""
        fields = []
        
        # Handle different schema formats
        if "properties" in schema:
            # JSON Schema format
            for field_name, field_def in schema["properties"].items():
                fields.append({
                    "name": field_name,
                    "type": field_def.get("type", "unknown"),
                    "description": field_def.get("description", ""),
                    "enum": field_def.get("enum", []),
                    "required": field_name in schema.get("required", [])
                })
        
        elif "fields" in schema:
            # Custom schema format
            for field_def in schema["fields"]:
                fields.append(field_def)
        
        elif isinstance(schema, dict):
            # Simple key-value format
            for key, value in schema.items():
                if isinstance(value, dict):
                    fields.append({
                        "name": key,
                        "type": value.get("type", "unknown"),
                        "description": value.get("description", ""),
                        "enum": value.get("enum", []),
                        "required": value.get("required", False)
                    })
        
        return fields

    def _check_schema_rule(self, rule: SchemaEthicalRule, schema: Dict[str, Any], fields: List[Dict[str, Any]]) -> List[SchemaEthicalViolation]:
        """Check a single schema ethical rule."""
        violations = []
        
        try:
            # Pattern-based check
            if rule.check_pattern:
                pattern = re.compile(rule.check_pattern, re.IGNORECASE)
                
                for field in fields:
                    # Check field name
                    if pattern.search(field["name"]):
                        violations.append(SchemaEthicalViolation(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            category=rule.category,
                            severity=rule.severity,
                            description=f"Field name '{field['name']}' matches ethical concern pattern",
                            field_name=field["name"],
                            detected_content=field["name"],
                            confidence=0.8,
                            recommendation=f"Consider renaming field '{field['name']}'"
                        ))
                    
                    # Check field description
                    if field.get("description") and pattern.search(field["description"]):
                        violations.append(SchemaEthicalViolation(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            category=rule.category,
                            severity=rule.severity,
                            description=f"Field description contains potentially biased language",
                            field_name=field["name"],
                            detected_content=field["description"][:100],
                            confidence=0.7,
                            recommendation=f"Review description for field '{field['name']}'"
                        ))
            
            # Function-based check
            if rule.check_function:
                check_method = getattr(self, f"_check_{rule.check_function}", None)
                if check_method:
                    function_violations = check_method(rule, schema, fields)
                    violations.extend(function_violations)
            
        except Exception as e:
            self.logger.warning(f"Rule check {rule.id} failed: {str(e)}")
        
        return violations

    def _calculate_ethical_score(self, violations: List[SchemaEthicalViolation]) -> float:
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
        """Load default schema ethical rules."""
        # Bias in fields rules
        self._rules.extend([
            SchemaEthicalRule(
                id="gender_bias_fields",
                name="Gender Bias in Fields",
                category=SchemaEthicalCategory.BIAS_IN_FIELDS,
                description="Detects gender-biased field names",
                check_pattern=r".*(male|female|gender_specific|sexist).*",
                severity=EthicalSeverity.MEDIUM
            ),
            SchemaEthicalRule(
                id="racial_bias_fields",
                name="Racial Bias in Fields",
                category=SchemaEthicalCategory.BIAS_IN_FIELDS,
                description="Detects racially biased field names",
                check_function="racial_bias_fields",
                severity=EthicalSeverity.HIGH
            )
        ])
        
        # Discriminatory labels rules
        self._rules.extend([
            SchemaEthicalRule(
                id="discriminatory_labels",
                name="Discriminatory Labels",
                category=SchemaEthicalCategory.DISCRIMINATORY_LABELS,
                description="Detects discriminatory labels in enum values",
                check_function="discriminatory_labels",
                severity=EthicalSeverity.HIGH
            )
        ])
        
        # Privacy violation rules
        self._rules.extend([
            SchemaEthicalRule(
                id="pii_fields",
                name="PII Fields",
                category=SchemaEthicalCategory.PRIVACY_VIOLATION,
                description="Detects potentially sensitive PII fields",
                check_function="pii_fields",
                severity=EthicalSeverity.HIGH
            )
        ])
        
        # Sensitive attributes rules
        self._rules.extend([
            SchemaEthicalRule(
                id="protected_attributes",
                name="Protected Attributes",
                category=SchemaEthicalCategory.SENSITIVE_ATTRIBUTES,
                description="Detects fields that might be protected attributes",
                check_function="protected_attributes",
                severity=EthicalSeverity.MEDIUM
            )
        ])

    # Schema ethical check methods
    def _check_racial_bias_fields(self, rule: SchemaEthicalRule, schema: Dict[str, Any], fields: List[Dict[str, Any]]) -> List[SchemaEthicalViolation]:
        """Check for racial bias in field names."""
        violations = []
        racial_terms = ["race", "ethnicity", "nationality", "color", "origin"]
        
        for field in fields:
            field_name_lower = field["name"].lower()
            for term in racial_terms:
                if term in field_name_lower:
                    # Check if field is used inappropriately
                    if any(word in field_name_lower for word in ["score", "rating", "grade", "class"]):
                        violations.append(SchemaEthicalViolation(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            category=rule.category,
                            severity=rule.severity,
                            description=f"Field '{field['name']}' may use racial attribute for scoring",
                            field_name=field["name"],
                            confidence=0.8,
                            recommendation="Avoid using racial attributes in scoring or classification"
                        ))
        
        return violations

    def _check_discriminatory_labels(self, rule: SchemaEthicalRule, schema: Dict[str, Any], fields: List[Dict[str, Any]]) -> List[SchemaEthicalViolation]:
        """Check for discriminatory labels in enum values."""
        violations = []
        discriminatory_terms = ["inferior", "superior", "bad", "good", "weak", "strong"]
        
        for field in fields:
            if field.get("enum"):
                for value in field["enum"]:
                    if any(term in str(value).lower() for term in discriminatory_terms):
                        violations.append(SchemaEthicalViolation(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            category=rule.category,
                            severity=rule.severity,
                            description=f"Enum value '{value}' in field '{field['name']}' is potentially discriminatory",
                            field_name=field["name"],
                            detected_content=str(value),
                            confidence=0.7,
                            recommendation="Use neutral terminology in enum values"
                        ))
        
        return violations

    def _check_pii_fields(self, rule: SchemaEthicalRule, schema: Dict[str, Any], fields: List[Dict[str, Any]]) -> List[SchemaEthicalViolation]:
        """Check for PII-related fields."""
        violations = []
        
        for field in fields:
            field_name_lower = field["name"].lower()
            
            # Check against sensitive patterns
            for pattern in self.config.sensitive_field_patterns:
                if re.match(pattern, field_name_lower):
                    violations.append(SchemaEthicalViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        description=f"Field '{field['name']}' may contain sensitive PII",
                        field_name=field["name"],
                        confidence=0.9,
                        recommendation="Ensure proper encryption and access controls for sensitive fields"
                    ))
        
        return violations

    def _check_protected_attributes(self, rule: SchemaEthicalRule, schema: Dict[str, Any], fields: List[Dict[str, Any]]) -> List[SchemaEthicalViolation]:
        """Check for protected attributes."""
        violations = []
        
        for field in fields:
            field_name_lower = field["name"].lower()
            
            for attribute in self.config.protected_attributes:
                if attribute in field_name_lower:
                    # Check if field is required
                    if field.get("required"):
                        violations.append(SchemaEthicalViolation(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            category=rule.category,
                            severity=rule.severity,
                            description=f"Protected attribute '{attribute}' is marked as required",
                            field_name=field["name"],
                            confidence=0.8,
                            recommendation=f"Consider making {attribute} field optional"
                        ))
        
        return violations

    def add_rule(self, rule: SchemaEthicalRule) -> None:
        """Add a custom schema ethical rule.
        
        Args:
            rule: Rule to add
        """
        self.logger.info(f"Adding schema ethical rule: {rule.id}")
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
def create_schema_safety_ethics_validator(
    enabled_categories: List[str] = None,
    strict_mode: bool = False,
    confidence_threshold: float = 0.7,
    **kwargs
) -> SchemaSafetyEthicsValidator:
    """Create a configured schema safety ethics validator."""
    config = SchemaSafetyEthicsConfig(
        enabled_categories=[SchemaEthicalCategory(c) for c in (enabled_categories or ["bias_in_fields", "privacy_violation", "sensitive_attributes"])],
        strict_mode=strict_mode,
        confidence_threshold=confidence_threshold,
        **kwargs
    )
    return SchemaSafetyEthicsValidator(config)


# Convenience function for direct usage
def validate_safety_ethics(
    schema: Dict[str, Any],
    categories: List[str] = None,
    strict_mode: bool = False,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Validate schema for ethical compliance.
    
    Args:
        schema: Schema definition to validate
        categories: List of ethical categories to check
        strict_mode: Whether to use strict validation
        config: Optional validator configuration
        
    Returns:
        Dict: Schema ethics validation results
    """
    # Create validator and execute
    validator_config = SchemaSafetyEthicsConfig(
        enabled_categories=[SchemaEthicalCategory(c) for c in (categories or ["bias_in_fields", "privacy_violation", "sensitive_attributes"])],
        strict_mode=strict_mode,
        **config or {}
    )
    validator = SchemaSafetyEthicsValidator(validator_config)
    result = validator.validate_schema_ethics(schema)
    
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
                "field_name": v.field_name,
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
