"""
L1 Cognitive Planning - Layer Scalability Validation

Implements pure planning operations for validating layer scalability
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

class ScalabilityValidationType(str, Enum):
    """Supported scalability validation types with L5 safety validation"""
    HORIZONTAL_SCALING = "horizontal_scaling"
    VERTICAL_SCALING = "vertical_scaling"
    AUTO_SCALING = "auto_scaling"
    LOAD_BALANCING = "load_balancing"
    RESOURCE_ALLOCATION = "resource_allocation"
    PERFORMANCE_SCALING = "performance_scaling"


class ScalabilitySeverity(str, Enum):
    """Scalability validation severity levels with L5 safety enforcement"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LayerScalabilitySafetyPolicy(BaseModel):
    """L5 Safety policy for layer scalability validation operations"""
    max_scalability_rules: int = Field(default=50, description="Maximum scalability rules")
    max_validation_metrics: int = Field(default=100, description="Maximum validation metrics")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in ScalabilityValidationType])
    allowed_severities: List[str] = Field(default_factory=lambda: [t.value for t in ScalabilitySeverity])
    require_scalability_validation: bool = Field(default=True)
    prevent_scalability_bottlenecks: bool = Field(default=True)
    sanitize_scalability_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerScalabilitySafetyValidator:
    """L5 Safety validator for layer scalability validation operations"""
    
    def __init__(self, policy: LayerScalabilitySafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerScalabilitySafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._scalability_patterns = [
            r"scale", r"elastic", r"cluster", r"node",
            r"instance", r"replica", r"shard", r"partition"
        ]
    
    def validate_scalability_input(self, scalability_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates scalability input against L5 safety policies"""
        try:
            # Check scalability rules count
            scalability_rules = scalability_input.get("scalability_rules", [])
            if len(scalability_rules) > self.policy.max_scalability_rules:
                error_msg = f"Too many scalability rules: {len(scalability_rules)} > {self.policy.max_scalability_rules}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation types
            for rule in scalability_rules:
                rule_type = rule.get("type", "")
                if rule_type not in self.policy.allowed_validation_types:
                    error_msg = f"Prohibited validation type: {rule_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check metrics count
            scalability_metrics = scalability_input.get("scalability_metrics", {})
            metric_count = len(scalability_metrics)
            if metric_count > self.policy.max_validation_metrics:
                error_msg = f"Too many scalability metrics: {metric_count} > {self.policy.max_validation_metrics}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(scalability_input).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for scalability patterns (additional validation)
            for pattern in self._scalability_patterns:
                if pattern in content_str:
                    self.logger.warning(f"Scalability pattern detected: {pattern}")
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
class ScalabilityValidationRule:
    """Individual scalability validation rule specification"""
    id: str
    validation_type: ScalabilityValidationType
    severity: ScalabilitySeverity
    criteria: Dict[str, Any]
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class LayerScalabilityValidationRequest:
    """Input request for layer scalability validation operations"""
    layer_name: str
    layer_spec: Dict[str, Any]
    scalability_metrics: Dict[str, Any]
    scalability_rules: List[Dict[str, Any]]
    validation_options: Dict[str, Any]
    context: Dict[str, Any]
    scalability_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class ScalabilityValidationError:
    """Individual scalability validation error"""
    layer_id: str
    rule_id: str
    validation_type: ScalabilityValidationType
    error_category: str
    error_message: str
    actual_value: Any
    expected_value: Any
    severity: ScalabilitySeverity
    scalability_impact: str


@dataclass
class ScalabilityValidationResult:
    """Result of layer scalability validation"""
    is_scalable: bool
    scalability_score: float
    validation_errors: List[ScalabilityValidationError]
    validation_warnings: List[ScalabilityValidationError]
    scalability_summary: Dict[str, Any]
    scalability_recommendations: List[str]
    scalability_flags: List[str]


@dataclass
class LayerScalabilityValidationResult:
    """Output result from layer scalability validation operations"""
    validation_result: ScalabilityValidationResult
    validated_layer: Dict[str, Any]
    validation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    scalability_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerScalabilityValidatorInterface(ABC):
    """Abstract interface for layer scalability validation operations"""
    
    @abstractmethod
    async def validate_scalability(self, request: LayerScalabilityValidationRequest) -> LayerScalabilityValidationResult:
        """Validate layer scalability against rules and criteria"""
        pass
    
    @abstractmethod
    async def check_horizontal_scalability(self, metrics: Dict[str, Any]) -> List[ScalabilityValidationError]:
        """Check horizontal scalability metrics"""
        pass
    
    @abstractmethod
    async def check_vertical_scalability(self, metrics: Dict[str, Any]) -> List[ScalabilityValidationError]:
        """Check vertical scalability metrics"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerScalabilityValidator(LayerScalabilityValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating layer scalability.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerScalabilitySafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerScalabilitySafetyPolicy()
        self.safety_validator = LayerScalabilitySafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Scalability validation patterns and rules
        self._validation_patterns = {
            ScalabilityValidationType.HORIZONTAL_SCALING: {
                "instance_scaling": self._validate_instance_scaling,
                "load_distribution": self._validate_load_distribution,
                "cluster_configuration": self._validate_cluster_configuration
            },
            ScalabilityValidationType.VERTICAL_SCALING: {
                "resource_scaling": self._validate_resource_scaling,
                "performance_scaling": self._validate_performance_scaling,
                "capacity_limits": self._validate_capacity_limits
            },
            ScalabilityValidationType.AUTO_SCALING: {
                "auto_scaling_policies": self._validate_auto_scaling_policies,
                "scaling_triggers": self._validate_scaling_triggers,
                "scaling_limits": self._validate_scaling_limits
            },
            ScalabilityValidationType.LOAD_BALANCING: {
                "load_balancer_config": self._validate_load_balancer_config,
                "traffic_distribution": self._validate_traffic_distribution,
                "health_checks": self._validate_health_checks
            },
            ScalabilityValidationType.RESOURCE_ALLOCATION: {
                "resource_efficiency": self._validate_resource_efficiency,
                "resource_utilization": self._validate_resource_utilization,
                "resource_limits": self._validate_resource_limits
            },
            ScalabilityValidationType.PERFORMANCE_SCALING: {
                "throughput_scaling": self._validate_throughput_scaling,
                "latency_scaling": self._validate_latency_scaling,
                "performance_degradation": self._validate_performance_degradation
            }
        }
        
        self.logger.info("LayerScalabilityValidator initialized with L5 safety policies")
    
    async def validate_scalability(self, request: LayerScalabilityValidationRequest) -> LayerScalabilityValidationResult:
        """
        Validate layer scalability against rules and criteria.
        
        Args:
            request: Layer scalability validation request with layer specification and scalability metrics
            
        Returns:
            LayerScalabilityValidationResult: Structured result with scalability validation outcome and details
            
        Raises:
            ValidationError: If scalability validation fails
            SafetyError: If scalability validation violates safety policies
        """
        self.logger.info(f"Validating scalability for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            scalability_input = {
                "scalability_rules": request.scalability_rules,
                "scalability_metrics": request.scalability_metrics
            }
            
            is_valid, error_msg = self.safety_validator.validate_scalability_input(scalability_input)
            if not is_valid:
                raise SafetyError(f"Scalability safety validation failed: {error_msg}")
            
            # Sanitize scalability data if required
            sanitized_metrics = request.scalability_metrics
            if self.safety_policy.sanitize_scalability_data:
                sanitized_metrics = await self._sanitize_scalability_data(request.scalability_metrics)
            
            # Parse scalability rules
            parsed_rules = await self._parse_scalability_rules(request.scalability_rules)
            
            # Execute scalability validation rules
            validation_errors = []
            for rule in parsed_rules:
                rule_errors = await self._execute_scalability_rule(sanitized_metrics, rule)
                validation_errors.extend(rule_errors)
            
            # Check horizontal scalability
            horizontal_errors = await self.check_horizontal_scalability(sanitized_metrics)
            validation_errors.extend(horizontal_errors)
            
            # Check vertical scalability
            vertical_errors = await self.check_vertical_scalability(sanitized_metrics)
            validation_errors.extend(vertical_errors)
            
            # Separate errors and warnings based on severity
            error_list = [e for e in validation_errors if e.severity in [ScalabilitySeverity.CRITICAL, ScalabilitySeverity.HIGH]]
            warning_list = [e for e in validation_errors if e.severity in [ScalabilitySeverity.MEDIUM, ScalabilitySeverity.LOW]]
            
            # Determine overall scalability
            is_scalable = len(error_list) == 0
            
            # Calculate scalability score
            scalability_score = self._calculate_scalability_score(validation_errors)
            
            # Generate scalability summary
            scalability_summary = await self._generate_scalability_summary(
                request.layer_name,
                sanitized_metrics,
                validation_errors
            )
            
            # Generate scalability recommendations
            scalability_recommendations = await self._generate_scalability_recommendations(validation_errors)
            
            # Extract scalability flags
            scalability_flags = self._extract_scalability_flags(validation_errors)
            
            # Create validation result
            validation_result = ScalabilityValidationResult(
                is_scalable=is_scalable,
                scalability_score=scalability_score,
                validation_errors=error_list,
                validation_warnings=warning_list,
                scalability_summary=scalability_summary,
                scalability_recommendations=scalability_recommendations,
                scalability_flags=scalability_flags
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_scalability_risk_score(validation_result),
                "scalability_flags": scalability_flags
            }
            
            # Generate unique scalability ID
            scalability_id = self._generate_scalability_id(request, validation_result)
            
            result = LayerScalabilityValidationResult(
                validation_result=validation_result,
                validated_layer=request.layer_spec,
                validation_metadata={
                    "layer_name": request.layer_name,
                    "rules_applied": len(parsed_rules),
                    "metrics_validated": len(sanitized_metrics),
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                scalability_id=scalability_id
            )
            
            self.logger.info(f"Successfully validated scalability for {request.layer_name} with score {scalability_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate layer scalability: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def check_horizontal_scalability(self, metrics: Dict[str, Any]) -> List[ScalabilityValidationError]:
        """Check horizontal scalability metrics"""
        errors = []
        
        try:
            # Check minimum instances
            min_instances = metrics.get("min_instances", 1)
            required_min_instances = metrics.get("required_min_instances", 2)
            
            if min_instances < required_min_instances:
                error = ScalabilityValidationError(
                    layer_id="scalability_check",
                    rule_id="horizontal_scaling_validation",
                    validation_type=ScalabilityValidationType.HORIZONTAL_SCALING,
                    error_category="insufficient_instances",
                    error_message=f"Minimum instances {min_instances} below required {required_min_instances}",
                    actual_value=min_instances,
                    expected_value=f">={required_min_instances}",
                    severity=ScalabilitySeverity.HIGH,
                    scalability_impact="horizontal_scaling"
                )
                errors.append(error)
            
            # Check maximum instances
            max_instances = metrics.get("max_instances", 0)
            required_max_instances = metrics.get("required_max_instances", 10)
            
            if max_instances < required_max_instances:
                error = ScalabilityValidationError(
                    layer_id="scalability_check",
                    rule_id="horizontal_scaling_validation",
                    validation_type=ScalabilityValidationType.HORIZONTAL_SCALING,
                    error_category="limited_max_instances",
                    error_message=f"Maximum instances {max_instances} below required {required_max_instances}",
                    actual_value=max_instances,
                    expected_value=f">={required_max_instances}",
                    severity=ScalabilitySeverity.MEDIUM,
                    scalability_impact="scaling_capacity"
                )
                errors.append(error)
            
            # Check load balancer configuration
            load_balancer_configured = metrics.get("load_balancer_configured", False)
            if not load_balancer_configured:
                error = ScalabilityValidationError(
                    layer_id="scalability_check",
                    rule_id="horizontal_scaling_validation",
                    validation_type=ScalabilityValidationType.HORIZONTAL_SCALING,
                    error_category="missing_load_balancer",
                    error_message="Load balancer not configured for horizontal scaling",
                    actual_value=load_balancer_configured,
                    expected_value=True,
                    severity=ScalabilitySeverity.HIGH,
                    scalability_impact="load_distribution"
                )
                errors.append(error)
            
            # Check instance distribution
            instance_distribution = metrics.get("instance_distribution", {})
            if not instance_distribution:
                error = ScalabilityValidationError(
                    layer_id="scalability_check",
                    rule_id="horizontal_scaling_validation",
                    validation_type=ScalabilityValidationType.HORIZONTAL_SCALING,
                    error_category="missing_instance_distribution",
                    error_message="Instance distribution not configured",
                    actual_value=instance_distribution,
                    expected_value="distribution configuration",
                    severity=ScalabilitySeverity.MEDIUM,
                    scalability_impact="distribution_strategy"
                )
                errors.append(error)
            
            # Check scaling policies
            scaling_policies = metrics.get("horizontal_scaling_policies", [])
            if not scaling_policies:
                error = ScalabilityValidationError(
                    layer_id="scalability_check",
                    rule_id="horizontal_scaling_validation",
                    validation_type=ScalabilityValidationType.HORIZONTAL_SCALING,
                    error_category="missing_scaling_policies",
                    error_message="Horizontal scaling policies not configured",
                    actual_value=scaling_policies,
                    expected_value="list of scaling policies",
                    severity=ScalabilitySeverity.MEDIUM,
                    scalability_impact="auto_scaling"
                )
                errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Horizontal scalability check failed: {str(e)}")
            error = ScalabilityValidationError(
                layer_id="scalability_check",
                rule_id="horizontal_scaling_error",
                validation_type=ScalabilityValidationType.HORIZONTAL_SCALING,
                error_category="validation_error",
                error_message=f"Horizontal scaling validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=ScalabilitySeverity.HIGH,
                scalability_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def check_vertical_scalability(self, metrics: Dict[str, Any]) -> List[ScalabilityValidationError]:
        """Check vertical scalability metrics"""
        errors = []
        
        try:
            # Check CPU scaling capability
            cpu_scaling_enabled = metrics.get("cpu_scaling_enabled", False)
            if not cpu_scaling_enabled:
                error = ScalabilityValidationError(
                    layer_id="scalability_check",
                    rule_id="vertical_scaling_validation",
                    validation_type=ScalabilityValidationType.VERTICAL_SCALING,
                    error_category="cpu_scaling_disabled",
                    error_message="CPU scaling not enabled",
                    actual_value=cpu_scaling_enabled,
                    expected_value=True,
                    severity=ScalabilitySeverity.MEDIUM,
                    scalability_impact="vertical_scaling"
                )
                errors.append(error)
            
            # Check memory scaling capability
            memory_scaling_enabled = metrics.get("memory_scaling_enabled", False)
            if not memory_scaling_enabled:
                error = ScalabilityValidationError(
                    layer_id="scalability_check",
                    rule_id="vertical_scaling_validation",
                    validation_type=ScalabilityValidationType.VERTICAL_SCALING,
                    error_category="memory_scaling_disabled",
                    error_message="Memory scaling not enabled",
                    actual_value=memory_scaling_enabled,
                    expected_value=True,
                    severity=ScalabilitySeverity.MEDIUM,
                    scalability_impact="vertical_scaling"
                )
                errors.append(error)
            
            # Check storage scaling capability
            storage_scaling_enabled = metrics.get("storage_scaling_enabled", False)
            if not storage_scaling_enabled:
                error = ScalabilityValidationError(
                    layer_id="scalability_check",
                    rule_id="vertical_scaling_validation",
                    validation_type=ScalabilityValidationType.VERTICAL_SCALING,
                    error_category="storage_scaling_disabled",
                    error_message="Storage scaling not enabled",
                    actual_value=storage_scaling_enabled,
                    expected_value=True,
                    severity=ScalabilitySeverity.LOW,
                    scalability_impact="storage_capacity"
                )
                errors.append(error)
            
            # Check resource limits
            resource_limits = metrics.get("resource_limits", {})
            if not resource_limits:
                error = ScalabilityValidationError(
                    layer_id="scalability_check",
                    rule_id="vertical_scaling_validation",
                    validation_type=ScalabilityValidationType.VERTICAL_SCALING,
                    error_category="missing_resource_limits",
                    error_message="Resource limits not configured",
                    actual_value=resource_limits,
                    expected_value="resource limits configuration",
                    severity=ScalabilitySeverity.MEDIUM,
                    scalability_impact="resource_management"
                )
                errors.append(error)
            
            # Check scaling performance impact
            scaling_performance_impact = metrics.get("scaling_performance_impact", "high")
            if scaling_performance_impact == "high":
                error = ScalabilityValidationError(
                    layer_id="scalability_check",
                    rule_id="vertical_scaling_validation",
                    validation_type=ScalabilityValidationType.VERTICAL_SCALING,
                    error_category="high_scaling_impact",
                    error_message="Vertical scaling has high performance impact",
                    actual_value=scaling_performance_impact,
                    expected_value="low or medium",
                    severity=ScalabilitySeverity.MEDIUM,
                    scalability_impact="performance"
                )
                errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Vertical scalability check failed: {str(e)}")
            error = ScalabilityValidationError(
                layer_id="scalability_check",
                rule_id="vertical_scaling_error",
                validation_type=ScalabilityValidationType.VERTICAL_SCALING,
                error_category="validation_error",
                error_message=f"Vertical scaling validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=ScalabilitySeverity.HIGH,
                scalability_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def _parse_scalability_rules(self, raw_rules: List[Dict[str, Any]]) -> List[ScalabilityValidationRule]:
        """Parse raw scalability rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = ScalabilityValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    validation_type=ScalabilityValidationType(raw_rule.get("validation_type", "horizontal_scaling")),
                    severity=ScalabilitySeverity(raw_rule.get("severity", "medium")),
                    criteria=raw_rule.get("criteria", {}),
                    error_message=raw_rule.get("error_message", "Scalability validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse scalability rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = ScalabilityValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    validation_type=ScalabilityValidationType.HORIZONTAL_SCALING,
                    severity=ScalabilitySeverity.MEDIUM,
                    criteria={},
                    error_message=f"Parsing failed: {str(e)}",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _execute_scalability_rule(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Execute individual scalability validation rule"""
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
                error = ScalabilityValidationError(
                    layer_id="scalability_check",
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="unknown_validation",
                    error_message=f"Unknown validation function: {rule.criteria.get('validation_function')}",
                    actual_value=None,
                    expected_value=None,
                    severity=ScalabilitySeverity.MEDIUM,
                    scalability_impact="validation"
                )
                errors.append(error)
                
        except Exception as e:
            self.logger.error(f"Failed to execute scalability rule {rule.id}: {str(e)}")
            error = ScalabilityValidationError(
                layer_id="scalability_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="rule_execution_error",
                error_message=f"Rule execution failed: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=ScalabilitySeverity.HIGH,
                scalability_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def _sanitize_scalability_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize scalability data for safety"""
        sanitized = metrics.copy()
        
        # Remove dangerous content from string fields
        for key, value in sanitized.items():
            if isinstance(value, str):
                # Remove script tags and dangerous content
                sanitized_value = value.replace("<script", "").replace("</script>", "")
                sanitized[key] = sanitized_value
            elif isinstance(value, dict):
                sanitized[key] = await self._sanitize_scalability_data(value)
            elif isinstance(value, list):
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        sanitized_item = item.replace("<script", "").replace("</script>", "")
                        sanitized_list.append(sanitized_item)
                    elif isinstance(item, dict):
                        sanitized_item = await self._sanitize_scalability_data(item)
                        sanitized_list.append(sanitized_item)
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
        
        return sanitized
    
    # Validation function implementations
    async def _validate_instance_scaling(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate instance scaling"""
        errors = []
        
        min_instances = rule.criteria.get("min_instances", 2)
        actual_min_instances = metrics.get("min_instances", 0)
        
        if actual_min_instances < min_instances:
            error = ScalabilityValidationError(
                layer_id="scalability_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="insufficient_instance_scaling",
                error_message=f"Instance scaling {actual_min_instances} below minimum {min_instances}",
                actual_value=actual_min_instances,
                expected_value=f">={min_instances}",
                severity=rule.severity,
                scalability_impact="horizontal_scaling"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_load_distribution(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate load distribution"""
        # Simplified implementation
        return []
    
    async def _validate_cluster_configuration(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate cluster configuration"""
        # Simplified implementation
        return []
    
    async def _validate_resource_scaling(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate resource scaling"""
        errors = []
        
        cpu_scaling = rule.criteria.get("cpu_scaling", True)
        actual_cpu_scaling = metrics.get("cpu_scaling_enabled", False)
        
        if cpu_scaling and not actual_cpu_scaling:
            error = ScalabilityValidationError(
                layer_id="scalability_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="cpu_scaling_required",
                error_message="CPU scaling is required but not enabled",
                actual_value=actual_cpu_scaling,
                expected_value=True,
                severity=rule.severity,
                scalability_impact="vertical_scaling"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_performance_scaling(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate performance scaling"""
        # Simplified implementation
        return []
    
    async def _validate_capacity_limits(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate capacity limits"""
        # Simplified implementation
        return []
    
    async def _validate_auto_scaling_policies(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate auto scaling policies"""
        # Simplified implementation
        return []
    
    async def _validate_scaling_triggers(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate scaling triggers"""
        # Simplified implementation
        return []
    
    async def _validate_scaling_limits(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate scaling limits"""
        # Simplified implementation
        return []
    
    async def _validate_load_balancer_config(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate load balancer configuration"""
        # Simplified implementation
        return []
    
    async def _validate_traffic_distribution(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate traffic distribution"""
        # Simplified implementation
        return []
    
    async def _validate_health_checks(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate health checks"""
        # Simplified implementation
        return []
    
    async def _validate_resource_efficiency(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate resource efficiency"""
        # Simplified implementation
        return []
    
    async def _validate_resource_utilization(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate resource utilization"""
        # Simplified implementation
        return []
    
    async def _validate_resource_limits(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate resource limits"""
        # Simplified implementation
        return []
    
    async def _validate_throughput_scaling(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate throughput scaling"""
        # Simplified implementation
        return []
    
    async def _validate_latency_scaling(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate latency scaling"""
        # Simplified implementation
        return []
    
    async def _validate_performance_degradation(
        self, 
        metrics: Dict[str, Any], 
        rule: ScalabilityValidationRule
    ) -> List[ScalabilityValidationError]:
        """Validate performance degradation"""
        # Simplified implementation
        return []
    
    def _calculate_scalability_score(self, errors: List[ScalabilityValidationError]) -> float:
        """Calculate scalability score based on validation errors"""
        if not errors:
            return 1.0
        
        # Weight errors by severity
        severity_weights = {
            ScalabilitySeverity.CRITICAL: 0.0,
            ScalabilitySeverity.HIGH: 0.3,
            ScalabilitySeverity.MEDIUM: 0.6,
            ScalabilitySeverity.LOW: 0.8
        }
        
        total_weight = sum(severity_weights[error.severity] for error in errors)
        average_score = total_weight / len(errors)
        
        return round(average_score, 2)
    
    async def _generate_scalability_summary(
        self, 
        layer_name: str,
        metrics: Dict[str, Any],
        errors: List[ScalabilityValidationError]
    ) -> Dict[str, Any]:
        """Generate scalability summary"""
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
                "min_instances": metrics.get("min_instances", 0),
                "max_instances": metrics.get("max_instances", 0),
                "load_balancer_configured": metrics.get("load_balancer_configured", False),
                "cpu_scaling_enabled": metrics.get("cpu_scaling_enabled", False),
                "memory_scaling_enabled": metrics.get("memory_scaling_enabled", False)
            }
        }
    
    async def _generate_scalability_recommendations(self, errors: List[ScalabilityValidationError]) -> List[str]:
        """Generate scalability recommendations based on errors"""
        recommendations = []
        
        error_categories = [error.error_category for error in errors]
        
        if "insufficient_instances" in error_categories:
            recommendations.append("Increase minimum instance count for better availability")
            recommendations.append("Configure auto-scaling policies for dynamic scaling")
        
        if "missing_load_balancer" in error_categories:
            recommendations.append("Configure load balancer for horizontal scaling")
            recommendations.append("Implement health checks for load balancer")
        
        if "cpu_scaling_disabled" in error_categories:
            recommendations.append("Enable CPU scaling for vertical scalability")
            recommendations.append("Configure resource limits and scaling policies")
        
        if "memory_scaling_disabled" in error_categories:
            recommendations.append("Enable memory scaling for better resource utilization")
            recommendations.append("Monitor memory usage and configure scaling triggers")
        
        if "missing_scaling_policies" in error_categories:
            recommendations.append("Define scaling policies based on metrics")
            recommendations.append("Configure scaling triggers and limits")
        
        if "high_scaling_impact" in error_categories:
            recommendations.append("Optimize scaling process to reduce performance impact")
            recommendations.append("Consider horizontal scaling over vertical scaling")
        
        if not recommendations:
            recommendations.append("Scalability configuration is within acceptable limits")
        
        return recommendations
    
    def _extract_scalability_flags(self, errors: List[ScalabilityValidationError]) -> List[str]:
        """Extract scalability flags from validation errors"""
        scalability_flags = []
        
        for error in errors:
            if error.validation_type == ScalabilityValidationType.HORIZONTAL_SCALING:
                scalability_flags.append("horizontal_scaling_issue")
            elif error.validation_type == ScalabilityValidationType.VERTICAL_SCALING:
                scalability_flags.append("vertical_scaling_issue")
            elif error.validation_type == ScalabilityValidationType.AUTO_SCALING:
                scalability_flags.append("auto_scaling_issue")
            elif error.validation_type == ScalabilityValidationType.LOAD_BALANCING:
                scalability_flags.append("load_balancing_issue")
            elif error.severity == ScalabilitySeverity.CRITICAL:
                scalability_flags.append("critical_scalability_issue")
        
        return scalability_flags
    
    async def _estimate_validation_complexity(self, request: LayerScalabilityValidationRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.scalability_rules) // 2
        
        # Add complexity for metrics
        complexity_score += len(request.scalability_metrics) // 5
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_scalability_risk_score(self, validation_result: ScalabilityValidationResult) -> float:
        """Calculate risk score for the scalability validation (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for scalability errors
        if validation_result.validation_errors:
            risk_score += 0.3
        
        # Increase risk for critical issues
        critical_errors = [e for e in validation_result.validation_errors if e.severity == ScalabilitySeverity.CRITICAL]
        if critical_errors:
            risk_score += 0.5
        
        # Increase risk for low scalability score
        if validation_result.scalability_score < 0.5:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_scalability_id(self, request: LayerScalabilityValidationRequest, result: ScalabilityValidationResult) -> str:
        """Generate unique scalability identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.layer_name}:{result.scalability_score:.2f}:{len(result.validation_errors)}:{timestamp}"
        return f"scalability_validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: LayerScalabilityValidationRequest, error: str) -> LayerScalabilityValidationResult:
        """Create safe fallback validation when main validation fails"""
        layer_name = request.layer_spec.get("name", "unknown")
        
        fallback_error = ScalabilityValidationError(
            layer_id=layer_name,
            rule_id="fallback_rule",
            validation_type=ScalabilityValidationType.HORIZONTAL_SCALING,
            error_category="validation_failed",
            error_message=f"Scalability validation failed: {error}",
            actual_value="fallback",
            expected_value="success",
            severity=ScalabilitySeverity.MEDIUM,
            scalability_impact="validation"
        )
        
        fallback_result = ScalabilityValidationResult(
            is_scalable=False,
            scalability_score=0.0,
            validation_errors=[fallback_error],
            validation_warnings=[],
            scalability_summary={"fallback": True},
            scalability_recommendations=["Fix scalability validation system"],
            scalability_flags=["fallback_mode"]
        )
        
        return LayerScalabilityValidationResult(
            validation_result=fallback_result,
            validated_layer=request.layer_spec,
            validation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            scalability_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when scalability validation violates safety policies"""
    
    def __init__(self, message: str, policy_violation: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.policy_violation = policy_violation
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.policy_violation:
            return f"[SAFETY_VIOLATION: {self.policy_violation}] {base_msg}"
        return f"[SAFETY_ERROR] {base_msg}"


class LayerScalabilityValidationError(Exception):
    """Raised for general layer scalability validation errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, operation: Optional[str] = None, scalability_metric: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code or "LAYER_SCALABILITY_VALIDATION_ERROR"
        self.operation = operation
        self.scalability_metric = scalability_metric
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        op_info = f" in {self.operation}" if self.operation else ""
        metric_info = f" for {self.scalability_metric}" if self.scalability_metric else ""
        return f"[{self.error_code}]{op_info}{metric_info} {base_msg}"


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_scalability_validator(safety_policy: Optional[LayerScalabilitySafetyPolicy] = None) -> LayerScalabilityValidator:
    """Factory function to create LayerScalabilityValidator with optional custom safety policy"""
    return LayerScalabilityValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_scalability_request(request: LayerScalabilityValidationRequest) -> tuple[bool, Optional[str]]:
    """Validate layer scalability request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.layer_spec, dict):
            return False, "Layer specification must be a dictionary"
        
        if not isinstance(request.scalability_metrics, dict):
            return False, "Scalability metrics must be a dictionary"
        
        if not isinstance(request.scalability_rules, list):
            return False, "Scalability rules must be a list"
        
        if not isinstance(request.validation_options, dict):
            return False, "Validation options must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
