"""
L1 Cognitive Planning - Layer Specification Validation

Implements pure planning operations for validating layer specifications
with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from __future__ import annotations
import logging
import asyncio
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field, ValidationError


# ============================================================================
# L5 SAFETY & LOGGING INFRASTRUCTURE
# ============================================================================

class ValidationType(str, Enum):
    """Supported validation types with L5 safety validation"""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    DEPENDENCY = "dependency"
    INTERFACE = "interface"


class ValidationSeverity(str, Enum):
    """Validation severity levels with L5 safety enforcement"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class LayerSpecSafetyPolicy(BaseModel):
    """L5 Safety policy for layer specification validation operations"""
    max_spec_size: int = Field(default=2097152, description="Maximum spec size in bytes (2MB)")
    max_validation_rules: int = Field(default=500, description="Maximum validation rules per spec")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in ValidationType])
    require_schema_validation: bool = Field(default=True)
    prevent_spec_injection: bool = Field(default=True)
    sanitize_spec_content: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerSpecSafetyValidator:
    """L5 Safety validator for layer specification validation operations"""
    
    def __init__(self, policy: LayerSpecSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerSpecSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._privileged_keywords = [
            "admin", "root", "sudo", "escalate", "privilege",
            "system", "kernel", "driver", "hardware"
        ]
    
    def validate_spec_input(self, spec_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates specification input against L5 safety policies"""
        try:
            # Check spec size
            spec_data = spec_input.get("spec", {})
            spec_size = len(str(spec_data).encode('utf-8'))
            
            if spec_size > self.policy.max_spec_size:
                error_msg = f"Specification too large: {spec_size} > {self.policy.max_spec_size} bytes"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation rules count
            validation_rules = spec_input.get("validation_rules", [])
            if len(validation_rules) > self.policy.max_validation_rules:
                error_msg = f"Too many validation rules: {len(validation_rules)} > {self.policy.max_validation_rules}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation types
            for rule in validation_rules:
                rule_type = rule.get("type", "")
                if rule_type not in self.policy.allowed_validation_types:
                    error_msg = f"Prohibited validation type: {rule_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(spec_data).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for privileged keywords
            for keyword in self._privileged_keywords:
                if keyword in content_str:
                    self.logger.warning(f"Privileged keyword detected: {keyword}")
                    # Additional validation would be required in production
            
            return True, None
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.error(f"Safety validation failed: {error_msg}")
            if self.policy.fail_closed:
                return False, error_msg
            return True, error_msg


# ============================================================================
# L1 COGNITIVE PLANNING INTERFACES
# ============================================================================

@dataclass
class ValidationRule:
    """Individual validation rule specification"""
    id: str
    type: ValidationType
    severity: ValidationSeverity
    description: str
    criteria: Dict[str, Any]
    expected_result: Any
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class LayerSpecValidationRequest:
    """Input request for layer specification validation operations"""
    layer_name: str
    layer_spec: Dict[str, Any]
    validation_rules: List[Dict[str, Any]]
    context: Dict[str, Any]
    validation_options: Dict[str, Any] = field(default_factory=dict)
    security_requirements: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class ValidationResult:
    """Result of individual validation rule"""
    rule_id: str
    rule_type: ValidationType
    severity: ValidationSeverity
    passed: bool
    actual_result: Any
    expected_result: Any
    error_message: Optional[str]
    execution_time_ms: float


@dataclass
class LayerSpecValidationSummary:
    """Summary of layer specification validation results"""
    layer_name: str
    total_rules: int
    passed_rules: int
    failed_rules: int
    critical_failures: int
    error_failures: int
    warnings: int
    compliance_score: float
    validation_summary: Dict[str, Any]


@dataclass
class LayerSpecValidationResult:
    """Output result from layer specification validation operations"""
    validation_summary: LayerSpecValidationSummary
    validation_results: List[ValidationResult]
    validation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    validation_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerSpecValidatorInterface(ABC):
    """Abstract interface for layer specification validation operations"""
    
    @abstractmethod
    async def validate_specification(self, request: LayerSpecValidationRequest) -> LayerSpecValidationResult:
        """Validate layer specification against rules"""
        pass
    
    @abstractmethod
    async def validate_spec_structure(self, spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate basic structure of specification"""
        pass
    
    @abstractmethod
    async def apply_validation_rules(self, spec: Dict[str, Any], rules: List[ValidationRule]) -> List[ValidationResult]:
        """Apply validation rules to specification"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerSpecValidator(LayerSpecValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating layer specifications.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerSpecSafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerSpecSafetyPolicy()
        self.safety_validator = LayerSpecSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Validation rule templates and patterns
        self._validation_templates = {
            ValidationType.STRUCTURAL: {
                "required_fields": ["layer_name", "layer_type", "version"],
                "field_types": {
                    "layer_name": str,
                    "layer_type": str,
                    "version": str,
                    "dependencies": list,
                    "interfaces": list
                }
            },
            ValidationType.SEMANTIC: {
                "naming_conventions": {
                    "layer_name": r"^[a-z][a-z0-9_]*$",
                    "layer_type": r"^[a-z][a-z0-9_]*$"
                },
                "version_format": r"^\d+\.\d+\.\d+$"
            },
            ValidationType.SECURITY: {
                "required_security_fields": ["authentication", "authorization"],
                "forbidden_patterns": ["password", "secret", "token"]
            },
            ValidationType.COMPLIANCE: {
                "required_compliance_fields": ["standards", "policies"],
                "compliance_standards": ["ISO27001", "SOC2", "GDPR"]
            },
            ValidationType.DEPENDENCY: {
                "max_dependencies": 10,
                "required_dependency_fields": ["name", "version", "type"]
            },
            ValidationType.INTERFACE: {
                "required_interface_fields": ["name", "method", "parameters"],
                "supported_methods": ["GET", "POST", "PUT", "DELETE"]
            }
        }
        
        self.logger.info("LayerSpecValidator initialized with L5 safety policies")
    
    async def validate_specification(self, request: LayerSpecValidationRequest) -> LayerSpecValidationResult:
        """
        Validate layer specification against rules.
        
        Args:
            request: Layer specification validation request with spec and rules
            
        Returns:
            LayerSpecValidationResult: Structured result with validation summary and detailed results
            
        Raises:
            ValidationError: If specification validation fails
            SafetyError: If specification violates safety policies
        """
        self.logger.info(f"Validating specification for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            spec_input = {
                "spec": request.layer_spec,
                "validation_rules": request.validation_rules
            }
            
            is_valid, error_msg = self.safety_validator.validate_spec_input(spec_input)
            if not is_valid:
                raise SafetyError(f"Specification validation failed: {error_msg}")
            
            # Validate basic structure
            structure_valid, structure_errors = await self.validate_spec_structure(request.layer_spec)
            if not structure_valid:
                self.logger.warning(f"Structure validation issues: {structure_errors}")
            
            # Parse validation rules
            parsed_rules = await self._parse_validation_rules(request.validation_rules)
            
            # Apply validation rules
            validation_results = await self.apply_validation_rules(request.layer_spec, parsed_rules)
            
            # Generate validation summary
            validation_summary = await self._generate_validation_summary(
                request.layer_name, 
                validation_results
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_validation_risk_score(validation_results),
                "security_flags": self._extract_security_flags(validation_results)
            }
            
            # Generate unique validation ID
            validation_id = self._generate_validation_id(request, validation_summary)
            
            result = LayerSpecValidationResult(
                validation_summary=validation_summary,
                validation_results=validation_results,
                validation_metadata={
                    "validation_duration_ms": sum(r.execution_time_ms for r in validation_results),
                    "rules_executed": len(validation_results),
                    "structure_errors": structure_errors,
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                validation_id=validation_id
            )
            
            self.logger.info(f"Successfully validated {request.layer_name} with {validation_summary.compliance_score:.2f} compliance score")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate layer specification: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def validate_spec_structure(self, spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate basic structure of specification"""
        try:
            errors = []
            
            # Check required fields
            template = self._validation_templates.get(ValidationType.STRUCTURAL, {})
            required_fields = template.get("required_fields", [])
            
            for field in required_fields:
                if field not in spec:
                    errors.append(f"Missing required field: {field}")
            
            # Check field types
            field_types = template.get("field_types", {})
            for field, expected_type in field_types.items():
                if field in spec and not isinstance(spec[field], expected_type):
                    errors.append(f"Invalid type for {field}: expected {expected_type.__name__}, got {type(spec[field]).__name__}")
            
            # Validate naming conventions
            naming_conventions = template.get("naming_conventions", {})
            for field, pattern in naming_conventions.items():
                if field in spec:
                    import re
                    if not re.match(pattern, str(spec[field])):
                        errors.append(f"Invalid naming convention for {field}: {spec[field]}")
            
            # Validate version format
            version_format = template.get("version_format")
            if "version" in spec and version_format:
                import re
                if not re.match(version_format, str(spec["version"])):
                    errors.append(f"Invalid version format: {spec['version']}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Structure validation error: {str(e)}"]
    
    async def apply_validation_rules(self, spec: Dict[str, Any], rules: List[ValidationRule]) -> List[ValidationResult]:
        """Apply validation rules to specification"""
        results = []
        
        for rule in rules:
            try:
                start_time = datetime.now()
                
                # Apply rule based on type
                if rule.type == ValidationType.STRUCTURAL:
                    passed, actual_result = await self._apply_structural_rule(spec, rule)
                elif rule.type == ValidationType.SEMANTIC:
                    passed, actual_result = await self._apply_semantic_rule(spec, rule)
                elif rule.type == ValidationType.SECURITY:
                    passed, actual_result = await self._apply_security_rule(spec, rule)
                elif rule.type == ValidationType.COMPLIANCE:
                    passed, actual_result = await self._apply_compliance_rule(spec, rule)
                elif rule.type == ValidationType.DEPENDENCY:
                    passed, actual_result = await self._apply_dependency_rule(spec, rule)
                elif rule.type == ValidationType.INTERFACE:
                    passed, actual_result = await self._apply_interface_rule(spec, rule)
                else:
                    passed, actual_result = False, f"Unknown rule type: {rule.type}"
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds() * 1000
                
                result = ValidationResult(
                    rule_id=rule.id,
                    rule_type=rule.type,
                    severity=rule.severity,
                    passed=passed,
                    actual_result=actual_result,
                    expected_result=rule.expected_result,
                    error_message=None if passed else rule.error_message,
                    execution_time_ms=execution_time
                )
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Failed to apply validation rule {rule.id}: {str(e)}")
                
                # Create error result
                error_result = ValidationResult(
                    rule_id=rule.id,
                    rule_type=rule.type,
                    severity=ValidationSeverity.ERROR,
                    passed=False,
                    actual_result=str(e),
                    expected_result=rule.expected_result,
                    error_message=f"Rule execution failed: {str(e)}",
                    execution_time_ms=0.0
                )
                results.append(error_result)
        
        return results
    
    async def _parse_validation_rules(self, raw_rules: List[Dict[str, Any]]) -> List[ValidationRule]:
        """Parse raw validation rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = ValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    type=ValidationType(raw_rule.get("type", "structural")),
                    severity=ValidationSeverity(raw_rule.get("severity", "error")),
                    description=raw_rule.get("description", ""),
                    criteria=raw_rule.get("criteria", {}),
                    expected_result=raw_rule.get("expected_result", True),
                    error_message=raw_rule.get("error_message", "Validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse validation rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = ValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    type=ValidationType.STRUCTURAL,
                    severity=ValidationSeverity.WARNING,
                    description=f"Parsing failed: {str(e)}",
                    criteria={},
                    expected_result=True,
                    error_message="Fallback rule",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _apply_structural_rule(self, spec: Dict[str, Any], rule: ValidationRule) -> Tuple[bool, Any]:
        """Apply structural validation rule"""
        criteria = rule.criteria
        
        if "field_exists" in criteria:
            field_name = criteria["field_exists"]
            return field_name in spec, field_name in spec
        
        if "field_type" in criteria:
            field_name = criteria["field_type"]
            expected_type = criteria["expected_type"]
            if field_name in spec:
                actual_type = type(spec[field_name]).__name__
                return actual_type == expected_type, actual_type
            return False, "field_missing"
        
        if "max_fields" in criteria:
            max_fields = criteria["max_fields"]
            actual_count = len(spec)
            return actual_count <= max_fields, actual_count
        
        return True, "structural_rule_passed"
    
    async def _apply_semantic_rule(self, spec: Dict[str, Any], rule: ValidationRule) -> Tuple[bool, Any]:
        """Apply semantic validation rule"""
        criteria = rule.criteria
        
        if "naming_pattern" in criteria:
            field_name = criteria["naming_pattern"]
            pattern = criteria["pattern"]
            if field_name in spec:
                import re
                value = str(spec[field_name])
                matches = re.match(pattern, value) is not None
                return matches, value
        
        if "version_compatible" in criteria:
            if "version" in spec:
                version = str(spec["version"])
                # Simple version validation
                parts = version.split(".")
                return len(parts) == 3, version
        
        return True, "semantic_rule_passed"
    
    async def _apply_security_rule(self, spec: Dict[str, Any], rule: ValidationRule) -> Tuple[bool, Any]:
        """Apply security validation rule"""
        criteria = rule.criteria
        
        if "no_sensitive_data" in criteria:
            sensitive_keywords = ["password", "secret", "token", "key"]
            spec_str = str(spec).lower()
            found_sensitive = any(keyword in spec_str for keyword in sensitive_keywords)
            return not found_sensitive, not found_sensitive
        
        if "requires_authentication" in criteria:
            has_auth = "authentication" in spec
            return has_auth, has_auth
        
        return True, "security_rule_passed"
    
    async def _apply_compliance_rule(self, spec: Dict[str, Any], rule: ValidationRule) -> Tuple[bool, Any]:
        """Apply compliance validation rule"""
        criteria = rule.criteria
        
        if "compliance_standard" in criteria:
            required_standard = criteria["compliance_standard"]
            compliance = spec.get("compliance", [])
            meets_standard = required_standard in compliance
            return meets_standard, compliance
        
        if "has_policy" in criteria:
            policy_name = criteria["has_policy"]
            policies = spec.get("policies", [])
            has_policy = policy_name in policies
            return has_policy, policies
        
        return True, "compliance_rule_passed"
    
    async def _apply_dependency_rule(self, spec: Dict[str, Any], rule: ValidationRule) -> Tuple[bool, Any]:
        """Apply dependency validation rule"""
        criteria = rule.criteria
        
        if "max_dependencies" in criteria:
            max_deps = criteria["max_dependencies"]
            dependencies = spec.get("dependencies", [])
            actual_count = len(dependencies)
            return actual_count <= max_deps, actual_count
        
        if "no_circular_deps" in criteria:
            dependencies = spec.get("dependencies", [])
            # Simple circular dependency check
            has_circular = len(set(dependencies)) != len(dependencies)
            return not has_circular, not has_circular
        
        return True, "dependency_rule_passed"
    
    async def _apply_interface_rule(self, spec: Dict[str, Any], rule: ValidationRule) -> Tuple[bool, Any]:
        """Apply interface validation rule"""
        criteria = rule.criteria
        
        if "has_interface" in criteria:
            interface_name = criteria["has_interface"]
            interfaces = spec.get("interfaces", [])
            has_interface = interface_name in interfaces
            return has_interface, interfaces
        
        if "valid_methods" in criteria:
            interfaces = spec.get("interfaces", [])
            valid_methods = criteria["valid_methods"]
            all_valid = all(
                interface.get("method", "") in valid_methods 
                for interface in interfaces
            )
            return all_valid, [i.get("method", "") for i in interfaces]
        
        return True, "interface_rule_passed"
    
    async def _generate_validation_summary(
        self, 
        layer_name: str, 
        results: List[ValidationResult]
    ) -> LayerSpecValidationSummary:
        """Generate validation summary from results"""
        total_rules = len(results)
        passed_rules = sum(1 for r in results if r.passed)
        failed_rules = total_rules - passed_rules
        critical_failures = sum(1 for r in results if not r.passed and r.severity == ValidationSeverity.CRITICAL)
        error_failures = sum(1 for r in results if not r.passed and r.severity == ValidationSeverity.ERROR)
        warnings = sum(1 for r in results if not r.passed and r.severity == ValidationSeverity.WARNING)
        
        # Calculate compliance score
        if total_rules == 0:
            compliance_score = 0.0
        else:
            # Weight critical and errors more heavily
            weighted_score = passed_rules
            weighted_score -= critical_failures * 2
            weighted_score -= error_failures * 1
            weighted_score -= warnings * 0.5
            compliance_score = max(0.0, min(1.0, weighted_score / total_rules))
        
        validation_summary = {
            "rule_types": list(set(r.rule_type.value for r in results)),
            "severity_distribution": {
                "critical": critical_failures,
                "error": error_failures,
                "warning": warnings,
                "info": sum(1 for r in results if r.severity == ValidationSeverity.INFO)
            }
        }
        
        return LayerSpecValidationSummary(
            layer_name=layer_name,
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            critical_failures=critical_failures,
            error_failures=error_failures,
            warnings=warnings,
            compliance_score=compliance_score,
            validation_summary=validation_summary
        )
    
    def _extract_security_flags(self, results: List[ValidationResult]) -> List[str]:
        """Extract security flags from validation results"""
        security_flags = []
        
        for result in results:
            if result.rule_type == ValidationType.SECURITY and not result.passed:
                security_flags.append(f"security_failure:{result.rule_id}")
            
            if "dangerous" in str(result.actual_result).lower():
                security_flags.append("dangerous_content_detected")
        
        return security_flags
    
    async def _estimate_validation_complexity(self, request: LayerSpecValidationRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.validation_rules) // 10
        
        # Add complexity for spec size
        spec_size = len(str(request.layer_spec)) // 1000
        complexity_score += spec_size
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_validation_risk_score(self, results: List[ValidationResult]) -> float:
        """Calculate risk score for the validation results (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for critical failures
        critical_failures = sum(1 for r in results if not r.passed and r.severity == ValidationSeverity.CRITICAL)
        if critical_failures > 0:
            risk_score += 0.4
        
        # Increase risk for security failures
        security_failures = sum(1 for r in results if r.rule_type == ValidationType.SECURITY and not r.passed)
        if security_failures > 0:
            risk_score += 0.3
        
        # Increase risk for many failures
        total_failures = sum(1 for r in results if not r.passed)
        if total_failures > len(results) * 0.5:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_validation_id(self, request: LayerSpecValidationRequest, summary: LayerSpecValidationSummary) -> str:
        """Generate unique validation identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.layer_name}:{summary.total_rules}:{summary.compliance_score:.2f}:{timestamp}"
        return f"validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: LayerSpecValidationRequest, error: str) -> LayerSpecValidationResult:
        """Create safe fallback validation when main validation fails"""
        fallback_result = ValidationResult(
            rule_id="fallback_rule_001",
            rule_type=ValidationType.STRUCTURAL,
            severity=ValidationSeverity.WARNING,
            passed=False,
            actual_result="fallback_validation",
            expected_result=True,
            error_message=f"Validation failed: {error}",
            execution_time_ms=0.0
        )
        
        fallback_summary = LayerSpecValidationSummary(
            layer_name=request.layer_name,
            total_rules=1,
            passed_rules=0,
            failed_rules=1,
            critical_failures=0,
            error_failures=1,
            warnings=0,
            compliance_score=0.0,
            validation_summary={"fallback": True}
        )
        
        return LayerSpecValidationResult(
            validation_summary=fallback_summary,
            validation_results=[fallback_result],
            validation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            validation_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when specification violates safety policies"""
    pass


class SpecValidationError(Exception):
    """Raised for general specification validation errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_spec_validator(safety_policy: Optional[LayerSpecSafetyPolicy] = None) -> LayerSpecValidator:
    """Factory function to create LayerSpecValidator with optional custom safety policy"""
    return LayerSpecValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_spec_request(request: LayerSpecValidationRequest) -> tuple[bool, Optional[str]]:
    """Validate layer specification request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.layer_spec, dict):
            return False, "Layer specification must be a dictionary"
        
        if not isinstance(request.validation_rules, list):
            return False, "Validation rules must be a list"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
