"""
L1 Cognitive Planning - Layer Completeness Validation

Implements pure planning operations for validating layer completeness
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

class CompletenessValidationType(str, Enum):
    """Supported completeness validation types with L5 safety validation"""
    FUNCTIONAL_COMPLETENESS = "functional_completeness"
    INTERFACE_COMPLETENESS = "interface_completeness"
    DOCUMENTATION_COMPLETENESS = "documentation_completeness"
    TEST_COMPLETENESS = "test_completeness"
    CONFIGURATION_COMPLETENESS = "configuration_completeness"
    DEPLOYMENT_COMPLETENESS = "deployment_completeness"


class CompletenessSeverity(str, Enum):
    """Completeness validation severity levels with L5 safety enforcement"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LayerCompletenessSafetyPolicy(BaseModel):
    """L5 Safety policy for layer completeness validation operations"""
    max_completeness_rules: int = Field(default=50, description="Maximum completeness rules")
    max_validation_metrics: int = Field(default=100, description="Maximum validation metrics")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in CompletenessValidationType])
    allowed_severities: List[str] = Field(default_factory=lambda: [t.value for t in CompletenessSeverity])
    require_completeness_validation: bool = Field(default=True)
    prevent_incomplete_deployment: bool = Field(default=True)
    sanitize_completeness_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerCompletenessSafetyValidator:
    """L5 Safety validator for layer completeness validation operations"""
    
    def __init__(self, policy: LayerCompletenessSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerCompletenessSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._completeness_patterns = [
            r"complete", r"missing", r"partial", r"full",
            r"coverage", r"gaps", r"requirements", r"specifications"
        ]
    
    def validate_completeness_input(self, completeness_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates completeness input against L5 safety policies"""
        try:
            # Check completeness rules count
            completeness_rules = completeness_input.get("completeness_rules", [])
            if len(completeness_rules) > self.policy.max_completeness_rules:
                error_msg = f"Too many completeness rules: {len(completeness_rules)} > {self.policy.max_completeness_rules}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation types
            for rule in completeness_rules:
                rule_type = rule.get("type", "")
                if rule_type not in self.policy.allowed_validation_types:
                    error_msg = f"Prohibited validation type: {rule_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check metrics count
            completeness_metrics = completeness_input.get("completeness_metrics", {})
            metric_count = len(completeness_metrics)
            if metric_count > self.policy.max_validation_metrics:
                error_msg = f"Too many completeness metrics: {metric_count} > {self.policy.max_validation_metrics}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(completeness_input).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for completeness patterns (additional validation)
            for pattern in self._completeness_patterns:
                if pattern in content_str:
                    self.logger.warning(f"Completeness pattern detected: {pattern}")
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
class CompletenessValidationRule:
    """Individual completeness validation rule specification"""
    id: str
    validation_type: CompletenessValidationType
    severity: CompletenessSeverity
    criteria: Dict[str, Any]
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class LayerCompletenessValidationRequest:
    """Input request for layer completeness validation operations"""
    layer_name: str
    layer_spec: Dict[str, Any]
    completeness_metrics: Dict[str, Any]
    completeness_rules: List[Dict[str, Any]]
    validation_options: Dict[str, Any]
    context: Dict[str, Any]
    completeness_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class CompletenessValidationError:
    """Individual completeness validation error"""
    layer_id: str
    rule_id: str
    validation_type: CompletenessValidationType
    error_category: str
    error_message: str
    actual_value: Any
    expected_value: Any
    severity: CompletenessSeverity
    completeness_impact: str


@dataclass
class CompletenessValidationResult:
    """Result of layer completeness validation"""
    is_complete: bool
    completeness_score: float
    validation_errors: List[CompletenessValidationError]
    validation_warnings: List[CompletenessValidationError]
    completeness_summary: Dict[str, Any]
    completeness_recommendations: List[str]
    completeness_flags: List[str]


@dataclass
class LayerCompletenessValidationResult:
    """Output result from layer completeness validation operations"""
    validation_result: CompletenessValidationResult
    validated_layer: Dict[str, Any]
    validation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    completeness_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerCompletenessValidatorInterface(ABC):
    """Abstract interface for layer completeness validation operations"""
    
    @abstractmethod
    async def validate_completeness(self, request: LayerCompletenessValidationRequest) -> LayerCompletenessValidationResult:
        """Validate layer completeness against rules and criteria"""
        pass
    
    @abstractmethod
    async def check_functional_completeness(self, metrics: Dict[str, Any]) -> List[CompletenessValidationError]:
        """Check functional completeness metrics"""
        pass
    
    @abstractmethod
    async def check_interface_completeness(self, metrics: Dict[str, Any]) -> List[CompletenessValidationError]:
        """Check interface completeness metrics"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerCompletenessValidator(LayerCompletenessValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating layer completeness.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerCompletenessSafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerCompletenessSafetyPolicy()
        self.safety_validator = LayerCompletenessSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Completeness validation patterns and rules
        self._validation_patterns = {
            CompletenessValidationType.FUNCTIONAL_COMPLETENESS: {
                "requirement_coverage": self._validate_requirement_coverage,
                "feature_implementation": self._validate_feature_implementation,
                "business_logic_completeness": self._validate_business_logic_completeness
            },
            CompletenessValidationType.INTERFACE_COMPLETENESS: {
                "api_completeness": self._validate_api_completeness,
                "endpoint_coverage": self._validate_endpoint_coverage,
                "data_contract_completeness": self._validate_data_contract_completeness
            },
            CompletenessValidationType.DOCUMENTATION_COMPLETENESS: {
                "api_documentation": self._validate_api_documentation,
                "user_guide_completeness": self._validate_user_guide_completeness,
                "technical_documentation": self._validate_technical_documentation
            },
            CompletenessValidationType.TEST_COMPLETENESS: {
                "unit_test_coverage": self._validate_unit_test_coverage,
                "integration_test_coverage": self._validate_integration_test_coverage,
                "acceptance_test_coverage": self._validate_acceptance_test_coverage
            },
            CompletenessValidationType.CONFIGURATION_COMPLETENESS: {
                "environment_config": self._validate_environment_config,
                "deployment_config": self._validate_deployment_config,
                "security_config": self._validate_security_config
            },
            CompletenessValidationType.DEPLOYMENT_COMPLETENESS: {
                "deployment_scripts": self._validate_deployment_scripts,
                "infrastructure_completeness": self._validate_infrastructure_completeness,
                "monitoring_setup": self._validate_monitoring_setup
            }
        }
        
        self.logger.info("LayerCompletenessValidator initialized with L5 safety policies")
    
    async def validate_completeness(self, request: LayerCompletenessValidationRequest) -> LayerCompletenessValidationResult:
        """
        Validate layer completeness against rules and criteria.
        
        Args:
            request: Layer completeness validation request with layer specification and completeness metrics
            
        Returns:
            LayerCompletenessValidationResult: Structured result with completeness validation outcome and details
            
        Raises:
            ValidationError: If completeness validation fails
            SafetyError: If completeness validation violates safety policies
        """
        self.logger.info(f"Validating completeness for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            completeness_input = {
                "completeness_rules": request.completeness_rules,
                "completeness_metrics": request.completeness_metrics
            }
            
            is_valid, error_msg = self.safety_validator.validate_completeness_input(completeness_input)
            if not is_valid:
                raise SafetyError(f"Completeness safety validation failed: {error_msg}")
            
            # Sanitize completeness data if required
            sanitized_metrics = request.completeness_metrics
            if self.safety_policy.sanitize_completeness_data:
                sanitized_metrics = await self._sanitize_completeness_data(request.completeness_metrics)
            
            # Parse completeness rules
            parsed_rules = await self._parse_completeness_rules(request.completeness_rules)
            
            # Execute completeness validation rules
            validation_errors = []
            for rule in parsed_rules:
                rule_errors = await self._execute_completeness_rule(sanitized_metrics, rule)
                validation_errors.extend(rule_errors)
            
            # Check functional completeness
            functional_errors = await self.check_functional_completeness(sanitized_metrics)
            validation_errors.extend(functional_errors)
            
            # Check interface completeness
            interface_errors = await self.check_interface_completeness(sanitized_metrics)
            validation_errors.extend(interface_errors)
            
            # Separate errors and warnings based on severity
            error_list = [e for e in validation_errors if e.severity in [CompletenessSeverity.CRITICAL, CompletenessSeverity.HIGH]]
            warning_list = [e for e in validation_errors if e.severity in [CompletenessSeverity.MEDIUM, CompletenessSeverity.LOW]]
            
            # Determine overall completeness
            is_complete = len(error_list) == 0
            
            # Calculate completeness score
            completeness_score = self._calculate_completeness_score(validation_errors)
            
            # Generate completeness summary
            completeness_summary = await self._generate_completeness_summary(
                request.layer_name,
                sanitized_metrics,
                validation_errors
            )
            
            # Generate completeness recommendations
            completeness_recommendations = await self._generate_completeness_recommendations(validation_errors)
            
            # Extract completeness flags
            completeness_flags = self._extract_completeness_flags(validation_errors)
            
            # Create validation result
            validation_result = CompletenessValidationResult(
                is_complete=is_complete,
                completeness_score=completeness_score,
                validation_errors=error_list,
                validation_warnings=warning_list,
                completeness_summary=completeness_summary,
                completeness_recommendations=completeness_recommendations,
                completeness_flags=completeness_flags
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_completeness_risk_score(validation_result),
                "completeness_flags": completeness_flags
            }
            
            # Generate unique completeness ID
            completeness_id = self._generate_completeness_id(request, validation_result)
            
            result = LayerCompletenessValidationResult(
                validation_result=validation_result,
                validated_layer=request.layer_spec,
                validation_metadata={
                    "layer_name": request.layer_name,
                    "rules_applied": len(parsed_rules),
                    "metrics_validated": len(sanitized_metrics),
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                completeness_id=completeness_id
            )
            
            self.logger.info(f"Successfully validated completeness for {request.layer_name} with score {completeness_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate layer completeness: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def check_functional_completeness(self, metrics: Dict[str, Any]) -> List[CompletenessValidationError]:
        """Check functional completeness metrics"""
        errors = []
        
        try:
            # Check requirement coverage
            requirement_coverage = metrics.get("requirement_coverage", 0)
            min_requirement_coverage = metrics.get("min_requirement_coverage", 95)
            
            if requirement_coverage < min_requirement_coverage:
                error = CompletenessValidationError(
                    layer_id="completeness_check",
                    rule_id="functional_completeness_validation",
                    validation_type=CompletenessValidationType.FUNCTIONAL_COMPLETENESS,
                    error_category="insufficient_requirement_coverage",
                    error_message=f"Requirement coverage {requirement_coverage}% below minimum {min_requirement_coverage}%",
                    actual_value=requirement_coverage,
                    expected_value=f">={min_requirement_coverage}%",
                    severity=CompletenessSeverity.CRITICAL,
                    completeness_impact="functional_completeness"
                )
                errors.append(error)
            
            # Check feature implementation
            implemented_features = metrics.get("implemented_features", 0)
            total_features = metrics.get("total_features", 0)
            
            if total_features > 0:
                feature_completion_rate = (implemented_features / total_features) * 100
                min_feature_completion = metrics.get("min_feature_completion", 90)
                
                if feature_completion_rate < min_feature_completion:
                    error = CompletenessValidationError(
                        layer_id="completeness_check",
                        rule_id="functional_completeness_validation",
                        validation_type=CompletenessValidationType.FUNCTIONAL_COMPLETENESS,
                        error_category="incomplete_feature_implementation",
                        error_message=f"Feature completion {feature_completion_rate:.1f}% below minimum {min_feature_completion}%",
                        actual_value=feature_completion_rate,
                        expected_value=f">={min_feature_completion}%",
                        severity=CompletenessSeverity.HIGH,
                        completeness_impact="feature_completeness"
                    )
                    errors.append(error)
            
            # Check business logic completeness
            business_logic_coverage = metrics.get("business_logic_coverage", 0)
            min_business_logic_coverage = metrics.get("min_business_logic_coverage", 85)
            
            if business_logic_coverage < min_business_logic_coverage:
                error = CompletenessValidationError(
                    layer_id="completeness_check",
                    rule_id="functional_completeness_validation",
                    validation_type=CompletenessValidationType.FUNCTIONAL_COMPLETENESS,
                    error_category="incomplete_business_logic",
                    error_message=f"Business logic coverage {business_logic_coverage}% below minimum {min_business_logic_coverage}%",
                    actual_value=business_logic_coverage,
                    expected_value=f">={min_business_logic_coverage}%",
                    severity=CompletenessSeverity.HIGH,
                    completeness_impact="business_logic_completeness"
                )
                errors.append(error)
            
            # Check edge case handling
            edge_case_coverage = metrics.get("edge_case_coverage", 0)
            min_edge_case_coverage = metrics.get("min_edge_case_coverage", 70)
            
            if edge_case_coverage < min_edge_case_coverage:
                error = CompletenessValidationError(
                    layer_id="completeness_check",
                    rule_id="functional_completeness_validation",
                    validation_type=CompletenessValidationType.FUNCTIONAL_COMPLETENESS,
                    error_category="insufficient_edge_case_handling",
                    error_message=f"Edge case coverage {edge_case_coverage}% below minimum {min_edge_case_coverage}%",
                    actual_value=edge_case_coverage,
                    expected_value=f">={min_edge_case_coverage}%",
                    severity=CompletenessSeverity.MEDIUM,
                    completeness_impact="robustness"
                )
                errors.append(error)
            
            # Check error handling completeness
            error_handling_coverage = metrics.get("error_handling_coverage", 0)
            min_error_handling_coverage = metrics.get("min_error_handling_coverage", 80)
            
            if error_handling_coverage < min_error_handling_coverage:
                error = CompletenessValidationError(
                    layer_id="completeness_check",
                    rule_id="functional_completeness_validation",
                    validation_type=CompletenessValidationType.FUNCTIONAL_COMPLETENESS,
                    error_category="incomplete_error_handling",
                    error_message=f"Error handling coverage {error_handling_coverage}% below minimum {min_error_handling_coverage}%",
                    actual_value=error_handling_coverage,
                    expected_value=f">={min_error_handling_coverage}%",
                    severity=CompletenessSeverity.HIGH,
                    completeness_impact="error_handling_completeness"
                )
                errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Functional completeness check failed: {str(e)}")
            error = CompletenessValidationError(
                layer_id="completeness_check",
                rule_id="functional_completeness_error",
                validation_type=CompletenessValidationType.FUNCTIONAL_COMPLETENESS,
                error_category="validation_error",
                error_message=f"Functional completeness validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=CompletenessSeverity.HIGH,
                completeness_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def check_interface_completeness(self, metrics: Dict[str, Any]) -> List[CompletenessValidationError]:
        """Check interface completeness metrics"""
        errors = []
        
        try:
            # Check API completeness
            api_completeness = metrics.get("api_completeness", 0)
            min_api_completeness = metrics.get("min_api_completeness", 90)
            
            if api_completeness < min_api_completeness:
                error = CompletenessValidationError(
                    layer_id="completeness_check",
                    rule_id="interface_completeness_validation",
                    validation_type=CompletenessValidationType.INTERFACE_COMPLETENESS,
                    error_category="incomplete_api",
                    error_message=f"API completeness {api_completeness}% below minimum {min_api_completeness}%",
                    actual_value=api_completeness,
                    expected_value=f">={min_api_completeness}%",
                    severity=CompletenessSeverity.HIGH,
                    completeness_impact="api_completeness"
                )
                errors.append(error)
            
            # Check endpoint coverage
            implemented_endpoints = metrics.get("implemented_endpoints", 0)
            total_endpoints = metrics.get("total_endpoints", 0)
            
            if total_endpoints > 0:
                endpoint_completion_rate = (implemented_endpoints / total_endpoints) * 100
                min_endpoint_completion = metrics.get("min_endpoint_completion", 95)
                
                if endpoint_completion_rate < min_endpoint_completion:
                    error = CompletenessValidationError(
                        layer_id="completeness_check",
                        rule_id="interface_completeness_validation",
                        validation_type=CompletenessValidationType.INTERFACE_COMPLETENESS,
                        error_category="incomplete_endpoint_implementation",
                        error_message=f"Endpoint completion {endpoint_completion_rate:.1f}% below minimum {min_endpoint_completion}%",
                        actual_value=endpoint_completion_rate,
                        expected_value=f">={min_endpoint_completion}%",
                        severity=CompletenessSeverity.HIGH,
                        completeness_impact="endpoint_completeness"
                    )
                    errors.append(error)
            
            # Check data contract completeness
            data_contract_completeness = metrics.get("data_contract_completeness", 0)
            min_data_contract_completeness = metrics.get("min_data_contract_completeness", 85)
            
            if data_contract_completeness < min_data_contract_completeness:
                error = CompletenessValidationError(
                    layer_id="completeness_check",
                    rule_id="interface_completeness_validation",
                    validation_type=CompletenessValidationType.INTERFACE_COMPLETENESS,
                    error_category="incomplete_data_contracts",
                    error_message=f"Data contract completeness {data_contract_completeness}% below minimum {min_data_contract_completeness}%",
                    actual_value=data_contract_completeness,
                    expected_value=f">={min_data_contract_completeness}%",
                    severity=CompletenessSeverity.MEDIUM,
                    completeness_impact="data_contract_completeness"
                )
                errors.append(error)
            
            # Check interface documentation
            interface_documentation_coverage = metrics.get("interface_documentation_coverage", 0)
            min_interface_documentation = metrics.get("min_interface_documentation", 80)
            
            if interface_documentation_coverage < min_interface_documentation:
                error = CompletenessValidationError(
                    layer_id="completeness_check",
                    rule_id="interface_completeness_validation",
                    validation_type=CompletenessValidationType.INTERFACE_COMPLETENESS,
                    error_category="incomplete_interface_documentation",
                    error_message=f"Interface documentation coverage {interface_documentation_coverage}% below minimum {min_interface_documentation}%",
                    actual_value=interface_documentation_coverage,
                    expected_value=f">={min_interface_documentation}%",
                    severity=CompletenessSeverity.MEDIUM,
                    completeness_impact="interface_documentation"
                )
                errors.append(error)
            
            # Check version compatibility
            version_completeness = metrics.get("version_completeness", 0)
            min_version_completeness = metrics.get("min_version_completeness", 75)
            
            if version_completeness < min_version_completeness:
                error = CompletenessValidationError(
                    layer_id="completeness_check",
                    rule_id="interface_completeness_validation",
                    validation_type=CompletenessValidationType.INTERFACE_COMPLETENESS,
                    error_category="incomplete_version_support",
                    error_message=f"Version completeness {version_completeness}% below minimum {min_version_completeness}%",
                    actual_value=version_completeness,
                    expected_value=f">={min_version_completeness}%",
                    severity=CompletenessSeverity.MEDIUM,
                    completeness_impact="version_compatibility"
                )
                errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Interface completeness check failed: {str(e)}")
            error = CompletenessValidationError(
                layer_id="completeness_check",
                rule_id="interface_completeness_error",
                validation_type=CompletenessValidationType.INTERFACE_COMPLETENESS,
                error_category="validation_error",
                error_message=f"Interface completeness validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=CompletenessSeverity.HIGH,
                completeness_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def _parse_completeness_rules(self, raw_rules: List[Dict[str, Any]]) -> List[CompletenessValidationRule]:
        """Parse raw completeness rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = CompletenessValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    validation_type=CompletenessValidationType(raw_rule.get("validation_type", "functional_completeness")),
                    severity=CompletenessSeverity(raw_rule.get("severity", "medium")),
                    criteria=raw_rule.get("criteria", {}),
                    error_message=raw_rule.get("error_message", "Completeness validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse completeness rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = CompletenessValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    validation_type=CompletenessValidationType.FUNCTIONAL_COMPLETENESS,
                    severity=CompletenessSeverity.MEDIUM,
                    criteria={},
                    error_message=f"Parsing failed: {str(e)}",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _execute_completeness_rule(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Execute individual completeness validation rule"""
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
                error = CompletenessValidationError(
                    layer_id="completeness_check",
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="unknown_validation",
                    error_message=f"Unknown validation function: {rule.criteria.get('validation_function')}",
                    actual_value=None,
                    expected_value=None,
                    severity=CompletenessSeverity.MEDIUM,
                    completeness_impact="validation"
                )
                errors.append(error)
                
        except Exception as e:
            self.logger.error(f"Failed to execute completeness rule {rule.id}: {str(e)}")
            error = CompletenessValidationError(
                layer_id="completeness_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="rule_execution_error",
                error_message=f"Rule execution failed: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=CompletenessSeverity.HIGH,
                completeness_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def _sanitize_completeness_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize completeness data for safety"""
        sanitized = metrics.copy()
        
        # Remove dangerous content from string fields
        for key, value in sanitized.items():
            if isinstance(value, str):
                # Remove script tags and dangerous content
                sanitized_value = value.replace("<script", "").replace("</script>", "")
                sanitized[key] = sanitized_value
            elif isinstance(value, dict):
                sanitized[key] = await self._sanitize_completeness_data(value)
            elif isinstance(value, list):
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        sanitized_item = item.replace("<script", "").replace("</script>", "")
                        sanitized_list.append(sanitized_item)
                    elif isinstance(item, dict):
                        sanitized_item = await self._sanitize_completeness_data(item)
                        sanitized_list.append(sanitized_item)
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
        
        return sanitized
    
    # Validation function implementations
    async def _validate_requirement_coverage(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate requirement coverage"""
        errors = []
        
        min_coverage = rule.criteria.get("min_coverage", 95)
        actual_coverage = metrics.get("requirement_coverage", 0)
        
        if actual_coverage < min_coverage:
            error = CompletenessValidationError(
                layer_id="completeness_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="requirement_coverage_insufficient",
                error_message=f"Requirement coverage {actual_coverage}% below minimum {min_coverage}%",
                actual_value=actual_coverage,
                expected_value=f">={min_coverage}%",
                severity=rule.severity,
                completeness_impact="functional_completeness"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_feature_implementation(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate feature implementation"""
        # Simplified implementation
        return []
    
    async def _validate_business_logic_completeness(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate business logic completeness"""
        # Simplified implementation
        return []
    
    async def _validate_api_completeness(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate API completeness"""
        errors = []
        
        min_completeness = rule.criteria.get("min_completeness", 90)
        actual_completeness = metrics.get("api_completeness", 0)
        
        if actual_completeness < min_completeness:
            error = CompletenessValidationError(
                layer_id="completeness_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="api_completeness_insufficient",
                error_message=f"API completeness {actual_completeness}% below minimum {min_completeness}%",
                actual_value=actual_completeness,
                expected_value=f">={min_completeness}%",
                severity=rule.severity,
                completeness_impact="interface_completeness"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_endpoint_coverage(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate endpoint coverage"""
        # Simplified implementation
        return []
    
    async def _validate_data_contract_completeness(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate data contract completeness"""
        # Simplified implementation
        return []
    
    async def _validate_api_documentation(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate API documentation"""
        # Simplified implementation
        return []
    
    async def _validate_user_guide_completeness(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate user guide completeness"""
        # Simplified implementation
        return []
    
    async def _validate_technical_documentation(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate technical documentation"""
        # Simplified implementation
        return []
    
    async def _validate_unit_test_coverage(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate unit test coverage"""
        # Simplified implementation
        return []
    
    async def _validate_integration_test_coverage(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate integration test coverage"""
        # Simplified implementation
        return []
    
    async def _validate_acceptance_test_coverage(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate acceptance test coverage"""
        # Simplified implementation
        return []
    
    async def _validate_environment_config(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate environment configuration"""
        # Simplified implementation
        return []
    
    async def _validate_deployment_config(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate deployment configuration"""
        # Simplified implementation
        return []
    
    async def _validate_security_config(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate security configuration"""
        # Simplified implementation
        return []
    
    async def _validate_deployment_scripts(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate deployment scripts"""
        # Simplified implementation
        return []
    
    async def _validate_infrastructure_completeness(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate infrastructure completeness"""
        # Simplified implementation
        return []
    
    async def _validate_monitoring_setup(
        self, 
        metrics: Dict[str, Any], 
        rule: CompletenessValidationRule
    ) -> List[CompletenessValidationError]:
        """Validate monitoring setup"""
        # Simplified implementation
        return []
    
    def _calculate_completeness_score(self, errors: List[CompletenessValidationError]) -> float:
        """Calculate completeness score based on validation errors"""
        if not errors:
            return 1.0
        
        # Weight errors by severity
        severity_weights = {
            CompletenessSeverity.CRITICAL: 0.0,
            CompletenessSeverity.HIGH: 0.2,
            CompletenessSeverity.MEDIUM: 0.5,
            CompletenessSeverity.LOW: 0.8
        }
        
        total_weight = sum(severity_weights[error.severity] for error in errors)
        average_score = total_weight / len(errors)
        
        return round(average_score, 2)
    
    async def _generate_completeness_summary(
        self, 
        layer_name: str,
        metrics: Dict[str, Any],
        errors: List[CompletenessValidationError]
    ) -> Dict[str, Any]:
        """Generate completeness summary"""
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
                "requirement_coverage": metrics.get("requirement_coverage", 0),
                "api_completeness": metrics.get("api_completeness", 0),
                "implemented_features": metrics.get("implemented_features", 0),
                "total_features": metrics.get("total_features", 0)
            }
        }
    
    async def _generate_completeness_recommendations(self, errors: List[CompletenessValidationError]) -> List[str]:
        """Generate completeness recommendations based on errors"""
        recommendations = []
        
        error_categories = [error.error_category for error in errors]
        
        if "insufficient_requirement_coverage" in error_categories:
            recommendations.append("Implement missing requirements to achieve full coverage")
            recommendations.append("Review and update requirement traceability matrix")
        
        if "incomplete_feature_implementation" in error_categories:
            recommendations.append("Complete implementation of all planned features")
            recommendations.append("Prioritize missing critical features")
        
        if "incomplete_api" in error_categories:
            recommendations.append("Complete API implementation and documentation")
            recommendations.append("Ensure all endpoints are properly implemented")
        
        if "incomplete_data_contracts" in error_categories:
            recommendations.append("Define and implement complete data contracts")
            recommendations.append("Add comprehensive data validation")
        
        if "incomplete_error_handling" in error_categories:
            recommendations.append("Implement comprehensive error handling")
            recommendations.append("Add proper exception handling and logging")
        
        if "insufficient_edge_case_handling" in error_categories:
            recommendations.append("Identify and handle edge cases")
            recommendations.append("Add comprehensive input validation")
        
        if not recommendations:
            recommendations.append("Layer completeness is within acceptable limits")
        
        return recommendations
    
    def _extract_completeness_flags(self, errors: List[CompletenessValidationError]) -> List[str]:
        """Extract completeness flags from validation errors"""
        completeness_flags = []
        
        for error in errors:
            if error.validation_type == CompletenessValidationType.FUNCTIONAL_COMPLETENESS:
                completeness_flags.append("functional_completeness_issue")
            elif error.validation_type == CompletenessValidationType.INTERFACE_COMPLETENESS:
                completeness_flags.append("interface_completeness_issue")
            elif error.validation_type == CompletenessValidationType.DOCUMENTATION_COMPLETENESS:
                completeness_flags.append("documentation_completeness_issue")
            elif error.validation_type == CompletenessValidationType.TEST_COMPLETENESS:
                completeness_flags.append("test_completeness_issue")
            elif error.severity == CompletenessSeverity.CRITICAL:
                completeness_flags.append("critical_completeness_issue")
        
        return completeness_flags
    
    async def _estimate_validation_complexity(self, request: LayerCompletenessValidationRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.completeness_rules) // 2
        
        # Add complexity for metrics
        complexity_score += len(request.completeness_metrics) // 5
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_completeness_risk_score(self, validation_result: CompletenessValidationResult) -> float:
        """Calculate risk score for the completeness validation (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for completeness errors
        if validation_result.validation_errors:
            risk_score += 0.4
        
        # Increase risk for critical issues
        critical_errors = [e for e in validation_result.validation_errors if e.severity == CompletenessSeverity.CRITICAL]
        if critical_errors:
            risk_score += 0.5
        
        # Increase risk for low completeness score
        if validation_result.completeness_score < 0.5:
            risk_score += 0.3
        
        return min(risk_score, 1.0)
    
    def _generate_completeness_id(self, request: LayerCompletenessValidationRequest, result: CompletenessValidationResult) -> str:
        """Generate unique completeness identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.layer_name}:{result.completeness_score:.2f}:{len(result.validation_errors)}:{timestamp}"
        return f"completeness_validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: LayerCompletenessValidationRequest, error: str) -> LayerCompletenessValidationResult:
        """Create safe fallback validation when main validation fails"""
        layer_name = request.layer_spec.get("name", "unknown")
        
        fallback_error = CompletenessValidationError(
            layer_id=layer_name,
            rule_id="fallback_rule",
            validation_type=CompletenessValidationType.FUNCTIONAL_COMPLETENESS,
            error_category="validation_failed",
            error_message=f"Completeness validation failed: {error}",
            actual_value="fallback",
            expected_value="success",
            severity=CompletenessSeverity.MEDIUM,
            completeness_impact="validation"
        )
        
        fallback_result = CompletenessValidationResult(
            is_complete=False,
            completeness_score=0.0,
            validation_errors=[fallback_error],
            validation_warnings=[],
            completeness_summary={"fallback": True},
            completeness_recommendations=["Fix completeness validation system"],
            completeness_flags=["fallback_mode"]
        )
        
        return LayerCompletenessValidationResult(
            validation_result=fallback_result,
            validated_layer=request.layer_spec,
            validation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            completeness_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when completeness validation violates safety policies"""
    pass


class LayerCompletenessValidationError(Exception):
    """Raised for general layer completeness validation errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_completeness_validator(safety_policy: Optional[LayerCompletenessSafetyPolicy] = None) -> LayerCompletenessValidator:
    """Factory function to create LayerCompletenessValidator with optional custom safety policy"""
    return LayerCompletenessValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_completeness_request(request: LayerCompletenessValidationRequest) -> tuple[bool, Optional[str]]:
    """Validate layer completeness request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.layer_spec, dict):
            return False, "Layer specification must be a dictionary"
        
        if not isinstance(request.completeness_metrics, dict):
            return False, "Completeness metrics must be a dictionary"
        
        if not isinstance(request.completeness_rules, list):
            return False, "Completeness rules must be a list"
        
        if not isinstance(request.validation_options, dict):
            return False, "Validation options must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
