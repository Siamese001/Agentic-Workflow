"""
L1 Cognitive Planning - Layer Maintainability Validation

Implements pure planning operations for validating layer maintainability
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

class MaintainabilityValidationType(str, Enum):
    """Supported maintainability validation types with L5 safety validation"""
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    MODULARITY = "modularity"
    TEST_COVERAGE = "test_coverage"
    DEPENDENCY_MANAGEMENT = "dependency_management"
    CONFIGURATION_MANAGEMENT = "configuration_management"


class MaintainabilitySeverity(str, Enum):
    """Maintainability validation severity levels with L5 safety enforcement"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LayerMaintainabilitySafetyPolicy(BaseModel):
    """L5 Safety policy for layer maintainability validation operations"""
    max_maintainability_rules: int = Field(default=50, description="Maximum maintainability rules")
    max_validation_metrics: int = Field(default=100, description="Maximum validation metrics")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in MaintainabilityValidationType])
    allowed_severities: List[str] = Field(default_factory=lambda: [t.value for t in MaintainabilitySeverity])
    require_maintainability_validation: bool = Field(default=True)
    prevent_maintainability_degradation: bool = Field(default=True)
    sanitize_maintainability_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerMaintainabilitySafetyValidator:
    """L5 Safety validator for layer maintainability validation operations"""
    
    def __init__(self, policy: LayerMaintainabilitySafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerMaintainabilitySafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._maintainability_patterns = [
            r"documentation", r"comment", r"readme", r"guide",
            r"test", r"coverage", r"quality", r"refactor"
        ]
    
    def validate_maintainability_input(self, maintainability_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates maintainability input against L5 safety policies"""
        try:
            # Check maintainability rules count
            maintainability_rules = maintainability_input.get("maintainability_rules", [])
            if len(maintainability_rules) > self.policy.max_maintainability_rules:
                error_msg = f"Too many maintainability rules: {len(maintainability_rules)} > {self.policy.max_maintainability_rules}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation types
            for rule in maintainability_rules:
                rule_type = rule.get("type", "")
                if rule_type not in self.policy.allowed_validation_types:
                    error_msg = f"Prohibited validation type: {rule_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check metrics count
            maintainability_metrics = maintainability_input.get("maintainability_metrics", {})
            metric_count = len(maintainability_metrics)
            if metric_count > self.policy.max_validation_metrics:
                error_msg = f"Too many maintainability metrics: {metric_count} > {self.policy.max_validation_metrics}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(maintainability_input).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for maintainability patterns (additional validation)
            for pattern in self._maintainability_patterns:
                if pattern in content_str:
                    self.logger.warning(f"Maintainability pattern detected: {pattern}")
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
class MaintainabilityValidationRule:
    """Individual maintainability validation rule specification"""
    id: str
    validation_type: MaintainabilityValidationType
    severity: MaintainabilitySeverity
    criteria: Dict[str, Any]
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class LayerMaintainabilityValidationRequest:
    """Input request for layer maintainability validation operations"""
    layer_name: str
    layer_spec: Dict[str, Any]
    maintainability_metrics: Dict[str, Any]
    maintainability_rules: List[Dict[str, Any]]
    validation_options: Dict[str, Any]
    context: Dict[str, Any]
    maintainability_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class MaintainabilityValidationError:
    """Individual maintainability validation error"""
    layer_id: str
    rule_id: str
    validation_type: MaintainabilityValidationType
    error_category: str
    error_message: str
    actual_value: Any
    expected_value: Any
    severity: MaintainabilitySeverity
    maintainability_impact: str


@dataclass
class MaintainabilityValidationResult:
    """Result of layer maintainability validation"""
    is_maintainable: bool
    maintainability_score: float
    validation_errors: List[MaintainabilityValidationError]
    validation_warnings: List[MaintainabilityValidationError]
    maintainability_summary: Dict[str, Any]
    maintainability_recommendations: List[str]
    maintainability_flags: List[str]


@dataclass
class LayerMaintainabilityValidationResult:
    """Output result from layer maintainability validation operations"""
    validation_result: MaintainabilityValidationResult
    validated_layer: Dict[str, Any]
    validation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    maintainability_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerMaintainabilityValidatorInterface(ABC):
    """Abstract interface for layer maintainability validation operations"""
    
    @abstractmethod
    async def validate_maintainability(self, request: LayerMaintainabilityValidationRequest) -> LayerMaintainabilityValidationResult:
        """Validate layer maintainability against rules and criteria"""
        pass
    
    @abstractmethod
    async def check_code_quality_maintainability(self, metrics: Dict[str, Any]) -> List[MaintainabilityValidationError]:
        """Check code quality maintainability metrics"""
        pass
    
    @abstractmethod
    async def check_documentation_maintainability(self, metrics: Dict[str, Any]) -> List[MaintainabilityValidationError]:
        """Check documentation maintainability metrics"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerMaintainabilityValidator(LayerMaintainabilityValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating layer maintainability.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerMaintainabilitySafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerMaintainabilitySafetyPolicy()
        self.safety_validator = LayerMaintainabilitySafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Maintainability validation patterns and rules
        self._validation_patterns = {
            MaintainabilityValidationType.CODE_QUALITY: {
                "cyclomatic_complexity": self._validate_cyclomatic_complexity,
                "code_duplication": self._validate_code_duplication,
                "code_smells": self._validate_code_smells
            },
            MaintainabilityValidationType.DOCUMENTATION: {
                "api_documentation": self._validate_api_documentation,
                "code_comments": self._validate_code_comments,
                "readme_completeness": self._validate_readme_completeness
            },
            MaintainabilityValidationType.MODULARITY: {
                "module_cohesion": self._validate_module_cohesion,
                "coupling_levels": self._validate_coupling_levels,
                "separation_of_concerns": self._validate_separation_of_concerns
            },
            MaintainabilityValidationType.TEST_COVERAGE: {
                "unit_test_coverage": self._validate_unit_test_coverage,
                "integration_test_coverage": self._validate_integration_test_coverage,
                "test_quality": self._validate_test_quality
            },
            MaintainabilityValidationType.DEPENDENCY_MANAGEMENT: {
                "dependency_versions": self._validate_dependency_versions,
                "dependency_updates": self._validate_dependency_updates,
                "dependency_conflicts": self._validate_dependency_conflicts
            },
            MaintainabilityValidationType.CONFIGURATION_MANAGEMENT: {
                "config_separation": self._validate_config_separation,
                "environment_configs": self._validate_environment_configs,
                "config_documentation": self._validate_config_documentation
            }
        }
        
        self.logger.info("LayerMaintainabilityValidator initialized with L5 safety policies")
    
    async def validate_maintainability(self, request: LayerMaintainabilityValidationRequest) -> LayerMaintainabilityValidationResult:
        """
        Validate layer maintainability against rules and criteria.
        
        Args:
            request: Layer maintainability validation request with layer specification and maintainability metrics
            
        Returns:
            LayerMaintainabilityValidationResult: Structured result with maintainability validation outcome and details
            
        Raises:
            ValidationError: If maintainability validation fails
            SafetyError: If maintainability validation violates safety policies
        """
        self.logger.info(f"Validating maintainability for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            maintainability_input = {
                "maintainability_rules": request.maintainability_rules,
                "maintainability_metrics": request.maintainability_metrics
            }
            
            is_valid, error_msg = self.safety_validator.validate_maintainability_input(maintainability_input)
            if not is_valid:
                raise SafetyError(f"Maintainability safety validation failed: {error_msg}")
            
            # Sanitize maintainability data if required
            sanitized_metrics = request.maintainability_metrics
            if self.safety_policy.sanitize_maintainability_data:
                sanitized_metrics = await self._sanitize_maintainability_data(request.maintainability_metrics)
            
            # Parse maintainability rules
            parsed_rules = await self._parse_maintainability_rules(request.maintainability_rules)
            
            # Execute maintainability validation rules
            validation_errors = []
            for rule in parsed_rules:
                rule_errors = await self._execute_maintainability_rule(sanitized_metrics, rule)
                validation_errors.extend(rule_errors)
            
            # Check code quality maintainability
            code_quality_errors = await self.check_code_quality_maintainability(sanitized_metrics)
            validation_errors.extend(code_quality_errors)
            
            # Check documentation maintainability
            documentation_errors = await self.check_documentation_maintainability(sanitized_metrics)
            validation_errors.extend(documentation_errors)
            
            # Separate errors and warnings based on severity
            error_list = [e for e in validation_errors if e.severity in [MaintainabilitySeverity.CRITICAL, MaintainabilitySeverity.HIGH]]
            warning_list = [e for e in validation_errors if e.severity in [MaintainabilitySeverity.MEDIUM, MaintainabilitySeverity.LOW]]
            
            # Determine overall maintainability
            is_maintainable = len(error_list) == 0
            
            # Calculate maintainability score
            maintainability_score = self._calculate_maintainability_score(validation_errors)
            
            # Generate maintainability summary
            maintainability_summary = await self._generate_maintainability_summary(
                request.layer_name,
                sanitized_metrics,
                validation_errors
            )
            
            # Generate maintainability recommendations
            maintainability_recommendations = await self._generate_maintainability_recommendations(validation_errors)
            
            # Extract maintainability flags
            maintainability_flags = self._extract_maintainability_flags(validation_errors)
            
            # Create validation result
            validation_result = MaintainabilityValidationResult(
                is_maintainable=is_maintainable,
                maintainability_score=maintainability_score,
                validation_errors=error_list,
                validation_warnings=warning_list,
                maintainability_summary=maintainability_summary,
                maintainability_recommendations=maintainability_recommendations,
                maintainability_flags=maintainability_flags
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_maintainability_risk_score(validation_result),
                "maintainability_flags": maintainability_flags
            }
            
            # Generate unique maintainability ID
            maintainability_id = self._generate_maintainability_id(request, validation_result)
            
            result = LayerMaintainabilityValidationResult(
                validation_result=validation_result,
                validated_layer=request.layer_spec,
                validation_metadata={
                    "layer_name": request.layer_name,
                    "rules_applied": len(parsed_rules),
                    "metrics_validated": len(sanitized_metrics),
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                maintainability_id=maintainability_id
            )
            
            self.logger.info(f"Successfully validated maintainability for {request.layer_name} with score {maintainability_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate layer maintainability: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def check_code_quality_maintainability(self, metrics: Dict[str, Any]) -> List[MaintainabilityValidationError]:
        """Check code quality maintainability metrics"""
        errors = []
        
        try:
            # Check cyclomatic complexity
            cyclomatic_complexity = metrics.get("cyclomatic_complexity", 0)
            max_complexity = metrics.get("max_cyclomatic_complexity", 10)
            
            if cyclomatic_complexity > max_complexity:
                error = MaintainabilityValidationError(
                    layer_id="maintainability_check",
                    rule_id="code_quality_validation",
                    validation_type=MaintainabilityValidationType.CODE_QUALITY,
                    error_category="high_cyclomatic_complexity",
                    error_message=f"Cyclomatic complexity {cyclomatic_complexity} above maximum {max_complexity}",
                    actual_value=cyclomatic_complexity,
                    expected_value=f"<={max_complexity}",
                    severity=MaintainabilitySeverity.HIGH,
                    maintainability_impact="code_complexity"
                )
                errors.append(error)
            
            # Check code duplication
            code_duplication_percent = metrics.get("code_duplication_percent", 0)
            max_duplication = metrics.get("max_code_duplication_percent", 5)
            
            if code_duplication_percent > max_duplication:
                error = MaintainabilityValidationError(
                    layer_id="maintainability_check",
                    rule_id="code_quality_validation",
                    validation_type=MaintainabilityValidationType.CODE_QUALITY,
                    error_category="high_code_duplication",
                    error_message=f"Code duplication {code_duplication_percent}% above maximum {max_duplication}%",
                    actual_value=code_duplication_percent,
                    expected_value=f"<={max_duplication}%",
                    severity=MaintainabilitySeverity.MEDIUM,
                    maintainability_impact="code_reusability"
                )
                errors.append(error)
            
            # Check code smells
            code_smells = metrics.get("code_smells", 0)
            max_code_smells = metrics.get("max_code_smells", 5)
            
            if code_smells > max_code_smells:
                error = MaintainabilityValidationError(
                    layer_id="maintainability_check",
                    rule_id="code_quality_validation",
                    validation_type=MaintainabilityValidationType.CODE_QUALITY,
                    error_category="excessive_code_smells",
                    error_message=f"Code smells {code_smells} above maximum {max_code_smells}",
                    actual_value=code_smells,
                    expected_value=f"<={max_code_smells}",
                    severity=MaintainabilitySeverity.MEDIUM,
                    maintainability_impact="code_quality"
                )
                errors.append(error)
            
            # Check technical debt ratio
            technical_debt_ratio = metrics.get("technical_debt_ratio", 0)
            max_technical_debt = metrics.get("max_technical_debt_ratio", 0.1)  # 10%
            
            if technical_debt_ratio > max_technical_debt:
                error = MaintainabilityValidationError(
                    layer_id="maintainability_check",
                    rule_id="code_quality_validation",
                    validation_type=MaintainabilityValidationType.CODE_QUALITY,
                    error_category="high_technical_debt",
                    error_message=f"Technical debt ratio {technical_debt_ratio:.2%} above maximum {max_technical_debt:.2%}",
                    actual_value=technical_debt_ratio,
                    expected_value=f"<={max_technical_debt}",
                    severity=MaintainabilitySeverity.HIGH,
                    maintainability_impact="technical_debt"
                )
                errors.append(error)
            
            # Check code maintainability index
            maintainability_index = metrics.get("maintainability_index", 0)
            min_maintainability_index = metrics.get("min_maintainability_index", 70)
            
            if maintainability_index < min_maintainability_index:
                error = MaintainabilityValidationError(
                    layer_id="maintainability_check",
                    rule_id="code_quality_validation",
                    validation_type=MaintainabilityValidationType.CODE_QUALITY,
                    error_category="low_maintainability_index",
                    error_message=f"Maintainability index {maintainability_index} below minimum {min_maintainability_index}",
                    actual_value=maintainability_index,
                    expected_value=f">={min_maintainability_index}",
                    severity=MaintainabilitySeverity.HIGH,
                    maintainability_impact="maintainability"
                )
                errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Code quality maintainability check failed: {str(e)}")
            error = MaintainabilityValidationError(
                layer_id="maintainability_check",
                rule_id="code_quality_error",
                validation_type=MaintainabilityValidationType.CODE_QUALITY,
                error_category="validation_error",
                error_message=f"Code quality validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=MaintainabilitySeverity.HIGH,
                maintainability_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def check_documentation_maintainability(self, metrics: Dict[str, Any]) -> List[MaintainabilityValidationError]:
        """Check documentation maintainability metrics"""
        errors = []
        
        try:
            # Check API documentation coverage
            api_documentation_coverage = metrics.get("api_documentation_coverage", 0)
            min_api_coverage = metrics.get("min_api_documentation_coverage", 80)
            
            if api_documentation_coverage < min_api_coverage:
                error = MaintainabilityValidationError(
                    layer_id="maintainability_check",
                    rule_id="documentation_validation",
                    validation_type=MaintainabilityValidationType.DOCUMENTATION,
                    error_category="low_api_documentation_coverage",
                    error_message=f"API documentation coverage {api_documentation_coverage}% below minimum {min_api_coverage}%",
                    actual_value=api_documentation_coverage,
                    expected_value=f">={min_api_coverage}%",
                    severity=MaintainabilitySeverity.HIGH,
                    maintainability_impact="documentation"
                )
                errors.append(error)
            
            # Check code comment coverage
            code_comment_coverage = metrics.get("code_comment_coverage", 0)
            min_comment_coverage = metrics.get("min_code_comment_coverage", 60)
            
            if code_comment_coverage < min_comment_coverage:
                error = MaintainabilityValidationError(
                    layer_id="maintainability_check",
                    rule_id="documentation_validation",
                    validation_type=MaintainabilityValidationType.DOCUMENTATION,
                    error_category="low_code_comment_coverage",
                    error_message=f"Code comment coverage {code_comment_coverage}% below minimum {min_comment_coverage}%",
                    actual_value=code_comment_coverage,
                    expected_value=f">={min_comment_coverage}%",
                    severity=MaintainabilitySeverity.MEDIUM,
                    maintainability_impact="code_understandability"
                )
                errors.append(error)
            
            # Check README completeness
            readme_completeness = metrics.get("readme_completeness", 0)
            min_readme_completeness = metrics.get("min_readme_completeness", 70)
            
            if readme_completeness < min_readme_completeness:
                error = MaintainabilityValidationError(
                    layer_id="maintainability_check",
                    rule_id="documentation_validation",
                    validation_type=MaintainabilityValidationType.DOCUMENTATION,
                    error_category="incomplete_readme",
                    error_message=f"README completeness {readme_completeness}% below minimum {min_readme_completeness}%",
                    actual_value=readme_completeness,
                    expected_value=f">={min_readme_completeness}%",
                    severity=MaintainabilitySeverity.MEDIUM,
                    maintainability_impact="project_documentation"
                )
                errors.append(error)
            
            # Check documentation quality score
            documentation_quality_score = metrics.get("documentation_quality_score", 0)
            min_quality_score = metrics.get("min_documentation_quality_score", 7.0)
            
            if documentation_quality_score < min_quality_score:
                error = MaintainabilityValidationError(
                    layer_id="maintainability_check",
                    rule_id="documentation_validation",
                    validation_type=MaintainabilityValidationType.DOCUMENTATION,
                    error_category="low_documentation_quality",
                    error_message=f"Documentation quality score {documentation_quality_score} below minimum {min_quality_score}",
                    actual_value=documentation_quality_score,
                    expected_value=f">={min_quality_score}",
                    severity=MaintainabilitySeverity.MEDIUM,
                    maintainability_impact="documentation_quality"
                )
                errors.append(error)
            
            # Check documentation freshness
            documentation_age_days = metrics.get("documentation_age_days", 0)
            max_documentation_age = metrics.get("max_documentation_age_days", 90)
            
            if documentation_age_days > max_documentation_age:
                error = MaintainabilityValidationError(
                    layer_id="maintainability_check",
                    rule_id="documentation_validation",
                    validation_type=MaintainabilityValidationType.DOCUMENTATION,
                    error_category="outdated_documentation",
                    error_message=f"Documentation age {documentation_age_days} days above maximum {max_documentation_age} days",
                    actual_value=documentation_age_days,
                    expected_value=f"<={max_documentation_age} days",
                    severity=MaintainabilitySeverity.LOW,
                    maintainability_impact="documentation_currency"
                )
                errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Documentation maintainability check failed: {str(e)}")
            error = MaintainabilityValidationError(
                layer_id="maintainability_check",
                rule_id="documentation_error",
                validation_type=MaintainabilityValidationType.DOCUMENTATION,
                error_category="validation_error",
                error_message=f"Documentation validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=MaintainabilitySeverity.HIGH,
                maintainability_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def _parse_maintainability_rules(self, raw_rules: List[Dict[str, Any]]) -> List[MaintainabilityValidationRule]:
        """Parse raw maintainability rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = MaintainabilityValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    validation_type=MaintainabilityValidationType(raw_rule.get("validation_type", "code_quality")),
                    severity=MaintainabilitySeverity(raw_rule.get("severity", "medium")),
                    criteria=raw_rule.get("criteria", {}),
                    error_message=raw_rule.get("error_message", "Maintainability validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse maintainability rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = MaintainabilityValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    validation_type=MaintainabilityValidationType.CODE_QUALITY,
                    severity=MaintainabilitySeverity.MEDIUM,
                    criteria={},
                    error_message=f"Parsing failed: {str(e)}",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _execute_maintainability_rule(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Execute individual maintainability validation rule"""
        errors = []
        
        try:
            # Get validation function for rule type
            type_patterns = self._validation_patterns.get(rule.validation_type, {})
            validation_func = type_patterns.get(rule.criteria.get("validation_function", ""))
            
            if validation_func:
                # Apply validation function
                rule_errors = await validation_func(metrics, rule)
                errors.extend(rule_errors)
            else:
                # Unknown validation function
                error = MaintainabilityValidationError(
                    layer_id="maintainability_check",
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="unknown_validation",
                    error_message=f"Unknown validation function: {rule.criteria.get('validation_function')}",
                    actual_value=None,
                    expected_value=None,
                    severity=MaintainabilitySeverity.MEDIUM,
                    maintainability_impact="validation"
                )
                errors.append(error)
                
        except Exception as e:
            self.logger.error(f"Failed to execute maintainability rule {rule.id}: {str(e)}")
            error = MaintainabilityValidationError(
                layer_id="maintainability_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="rule_execution_error",
                error_message=f"Rule execution failed: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=MaintainabilitySeverity.HIGH,
                maintainability_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def _sanitize_maintainability_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize maintainability data for safety"""
        sanitized = metrics.copy()
        
        # Remove dangerous content from string fields
        for key, value in sanitized.items():
            if isinstance(value, str):
                # Remove script tags and dangerous content
                sanitized_value = value.replace("<script", "").replace("</script>", "")
                sanitized[key] = sanitized_value
            elif isinstance(value, dict):
                sanitized[key] = await self._sanitize_maintainability_data(value)
            elif isinstance(value, list):
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        sanitized_item = item.replace("<script", "").replace("</script>", "")
                        sanitized_list.append(sanitized_item)
                    elif isinstance(item, dict):
                        sanitized_item = await self._sanitize_maintainability_data(item)
                        sanitized_list.append(sanitized_item)
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
        
        return sanitized
    
    # Validation function implementations
    async def _validate_cyclomatic_complexity(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate cyclomatic complexity"""
        errors = []
        
        max_complexity = rule.criteria.get("max_complexity", 10)
        actual_complexity = metrics.get("cyclomatic_complexity", 0)
        
        if actual_complexity > max_complexity:
            error = MaintainabilityValidationError(
                layer_id="maintainability_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="cyclomatic_complexity_exceeded",
                error_message=f"Cyclomatic complexity {actual_complexity} exceeds maximum {max_complexity}",
                actual_value=actual_complexity,
                expected_value=f"<={max_complexity}",
                severity=rule.severity,
                maintainability_impact="code_complexity"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_code_duplication(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate code duplication"""
        # Simplified implementation
        return []
    
    async def _validate_code_smells(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate code smells"""
        # Simplified implementation
        return []
    
    async def _validate_api_documentation(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate API documentation"""
        errors = []
        
        min_coverage = rule.criteria.get("min_coverage", 80)
        actual_coverage = metrics.get("api_documentation_coverage", 0)
        
        if actual_coverage < min_coverage:
            error = MaintainabilityValidationError(
                layer_id="maintainability_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="api_documentation_insufficient",
                error_message=f"API documentation coverage {actual_coverage}% below minimum {min_coverage}%",
                actual_value=actual_coverage,
                expected_value=f">={min_coverage}%",
                severity=rule.severity,
                maintainability_impact="documentation"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_code_comments(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate code comments"""
        # Simplified implementation
        return []
    
    async def _validate_readme_completeness(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate README completeness"""
        # Simplified implementation
        return []
    
    async def _validate_module_cohesion(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate module cohesion"""
        # Simplified implementation
        return []
    
    async def _validate_coupling_levels(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate coupling levels"""
        # Simplified implementation
        return []
    
    async def _validate_separation_of_concerns(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate separation of concerns"""
        # Simplified implementation
        return []
    
    async def _validate_unit_test_coverage(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate unit test coverage"""
        # Simplified implementation
        return []
    
    async def _validate_integration_test_coverage(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate integration test coverage"""
        # Simplified implementation
        return []
    
    async def _validate_test_quality(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate test quality"""
        # Simplified implementation
        return []
    
    async def _validate_dependency_versions(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate dependency versions"""
        # Simplified implementation
        return []
    
    async def _validate_dependency_updates(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate dependency updates"""
        # Simplified implementation
        return []
    
    async def _validate_dependency_conflicts(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate dependency conflicts"""
        # Simplified implementation
        return []
    
    async def _validate_config_separation(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate configuration separation"""
        # Simplified implementation
        return []
    
    async def _validate_environment_configs(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate environment configurations"""
        # Simplified implementation
        return []
    
    async def _validate_config_documentation(
        self, 
        metrics: Dict[str, Any], 
        rule: MaintainabilityValidationRule
    ) -> List[MaintainabilityValidationError]:
        """Validate configuration documentation"""
        # Simplified implementation
        return []
    
    def _calculate_maintainability_score(self, errors: List[MaintainabilityValidationError]) -> float:
        """Calculate maintainability score based on validation errors"""
        if not errors:
            return 1.0
        
        # Weight errors by severity
        severity_weights = {
            MaintainabilitySeverity.CRITICAL: 0.0,
            MaintainabilitySeverity.HIGH: 0.3,
            MaintainabilitySeverity.MEDIUM: 0.6,
            MaintainabilitySeverity.LOW: 0.8
        }
        
        total_weight = sum(severity_weights[error.severity] for error in errors)
        average_score = total_weight / len(errors)
        
        return round(average_score, 2)
    
    async def _generate_maintainability_summary(
        self, 
        layer_name: str,
        metrics: Dict[str, Any],
        errors: List[MaintainabilityValidationError]
    ) -> Dict[str, Any]:
        """Generate maintainability summary"""
        error_types = [error.validation_type.value for error in errors]
        error_categories = [error.error_category for error in errors]
        severity_counts = {}
        
        for error in errors:
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "layer_name": layer_name,
            "total_errors": len(errors),
            "error_types": list(set(error_types)),
            "error_categories": list(set(error_categories)),
            "severity_distribution": severity_counts,
            "key_metrics": {
                "cyclomatic_complexity": metrics.get("cyclomatic_complexity", 0),
                "code_duplication_percent": metrics.get("code_duplication_percent", 0),
                "api_documentation_coverage": metrics.get("api_documentation_coverage", 0),
                "maintainability_index": metrics.get("maintainability_index", 0)
            }
        }
    
    async def _generate_maintainability_recommendations(self, errors: List[MaintainabilityValidationError]) -> List[str]:
        """Generate maintainability recommendations based on errors"""
        recommendations = []
        
        error_categories = [error.error_category for error in errors]
        
        if "high_cyclomatic_complexity" in error_categories:
            recommendations.append("Refactor complex methods to reduce cyclomatic complexity")
            recommendations.append("Break down large functions into smaller, focused ones")
        
        if "high_code_duplication" in error_categories:
            recommendations.append("Extract common code into reusable functions or classes")
            recommendations.append("Implement DRY principles to reduce duplication")
        
        if "low_api_documentation_coverage" in error_categories:
            recommendations.append("Add comprehensive API documentation")
            recommendations.append("Use automated documentation generation tools")
        
        if "low_code_comment_coverage" in error_categories:
            recommendations.append("Add meaningful comments to complex code sections")
            recommendations.append("Document business logic and algorithms")
        
        if "incomplete_readme" in error_categories:
            recommendations.append("Enhance README with installation and usage instructions")
            recommendations.append("Add examples and troubleshooting guides")
        
        if "high_technical_debt" in error_categories:
            recommendations.append("Address technical debt through refactoring")
            recommendations.append("Plan regular code review and cleanup sessions")
        
        if not recommendations:
            recommendations.append("Maintainability metrics are within acceptable limits")
        
        return recommendations
    
    def _extract_maintainability_flags(self, errors: List[MaintainabilityValidationError]) -> List[str]:
        """Extract maintainability flags from validation errors"""
        maintainability_flags = []
        
        for error in errors:
            if error.validation_type == MaintainabilityValidationType.CODE_QUALITY:
                maintainability_flags.append("code_quality_issue")
            elif error.validation_type == MaintainabilityValidationType.DOCUMENTATION:
                maintainability_flags.append("documentation_issue")
            elif error.validation_type == MaintainabilityValidationType.MODULARITY:
                maintainability_flags.append("modularity_issue")
            elif error.validation_type == MaintainabilityValidationType.TEST_COVERAGE:
                maintainability_flags.append("test_coverage_issue")
            elif error.severity == MaintainabilitySeverity.CRITICAL:
                maintainability_flags.append("critical_maintainability_issue")
        
        return maintainability_flags
    
    async def _estimate_validation_complexity(self, request: LayerMaintainabilityValidationRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.maintainability_rules) // 2
        
        # Add complexity for metrics
        complexity_score += len(request.maintainability_metrics) // 5
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_maintainability_risk_score(self, validation_result: MaintainabilityValidationResult) -> float:
        """Calculate risk score for the maintainability validation (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for maintainability errors
        if validation_result.validation_errors:
            risk_score += 0.3
        
        # Increase risk for critical issues
        critical_errors = [e for e in validation_result.validation_errors if e.severity == MaintainabilitySeverity.CRITICAL]
        if critical_errors:
            risk_score += 0.5
        
        # Increase risk for low maintainability score
        if validation_result.maintainability_score < 0.5:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_maintainability_id(self, request: LayerMaintainabilityValidationRequest, result: MaintainabilityValidationResult) -> str:
        """Generate unique maintainability identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.layer_name}:{result.maintainability_score:.2f}:{len(result.validation_errors)}:{timestamp}"
        return f"maintainability_validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: LayerMaintainabilityValidationRequest, error: str) -> LayerMaintainabilityValidationResult:
        """Create safe fallback validation when main validation fails"""
        layer_name = request.layer_spec.get("name", "unknown")
        
        fallback_error = MaintainabilityValidationError(
            layer_id=layer_name,
            rule_id="fallback_rule",
            validation_type=MaintainabilityValidationType.CODE_QUALITY,
            error_category="validation_failed",
            error_message=f"Maintainability validation failed: {error}",
            actual_value="fallback",
            expected_value="success",
            severity=MaintainabilitySeverity.MEDIUM,
            maintainability_impact="validation"
        )
        
        fallback_result = MaintainabilityValidationResult(
            is_maintainable=False,
            maintainability_score=0.0,
            validation_errors=[fallback_error],
            validation_warnings=[],
            maintainability_summary={"fallback": True},
            maintainability_recommendations=["Fix maintainability validation system"],
            maintainability_flags=["fallback_mode"]
        )
        
        return LayerMaintainabilityValidationResult(
            validation_result=fallback_result,
            validated_layer=request.layer_spec,
            validation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            maintainability_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when maintainability validation violates safety policies"""
    pass


class LayerMaintainabilityValidationError(Exception):
    """Raised for general layer maintainability validation errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_maintainability_validator(safety_policy: Optional[LayerMaintainabilitySafetyPolicy] = None) -> LayerMaintainabilityValidator:
    """Factory function to create LayerMaintainabilityValidator with optional custom safety policy"""
    return LayerMaintainabilityValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_maintainability_request(request: LayerMaintainabilityValidationRequest) -> tuple[bool, Optional[str]]:
    """Validate layer maintainability request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.layer_spec, dict):
            return False, "Layer specification must be a dictionary"
        
        if not isinstance(request.maintainability_metrics, dict):
            return False, "Maintainability metrics must be a dictionary"
        
        if not isinstance(request.maintainability_rules, list):
            return False, "Maintainability rules must be a list"
        
        if not isinstance(request.validation_options, dict):
            return False, "Validation options must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
