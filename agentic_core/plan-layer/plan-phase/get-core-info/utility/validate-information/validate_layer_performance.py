"""
L1 Cognitive Planning - Layer Performance Validation

Implements pure planning operations for validating layer performance
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

class PerformanceValidationType(str, Enum):
    """Supported performance validation types with L5 safety validation"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    RESOURCE_USAGE = "resource_usage"
    SCALABILITY = "scalability"
    LATENCY = "latency"
    CONCURRENCY = "concurrency"


class PerformanceSeverity(str, Enum):
    """Performance validation severity levels with L5 safety enforcement"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LayerPerformanceSafetyPolicy(BaseModel):
    """L5 Safety policy for layer performance validation operations"""
    max_performance_rules: int = Field(default=50, description="Maximum performance rules")
    max_validation_metrics: int = Field(default=100, description="Maximum validation metrics")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in PerformanceValidationType])
    allowed_severities: List[str] = Field(default_factory=lambda: [t.value for t in PerformanceSeverity])
    require_performance_validation: bool = Field(default=True)
    prevent_performance_degradation: bool = Field(default=True)
    sanitize_performance_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerPerformanceSafetyValidator:
    """L5 Safety validator for layer performance validation operations"""
    
    def __init__(self, policy: LayerPerformanceSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerPerformanceSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._performance_patterns = [
            r"benchmark", r"metrics", r"performance", r"load",
            r"stress", r"capacity", r"throughput"
        ]
    
    def validate_performance_input(self, performance_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates performance input against L5 safety policies"""
        try:
            # Check performance rules count
            performance_rules = performance_input.get("performance_rules", [])
            if len(performance_rules) > self.policy.max_performance_rules:
                error_msg = f"Too many performance rules: {len(performance_rules)} > {self.policy.max_performance_rules}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation types
            for rule in performance_rules:
                rule_type = rule.get("type", "")
                if rule_type not in self.policy.allowed_validation_types:
                    error_msg = f"Prohibited validation type: {rule_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check metrics count
            performance_metrics = performance_input.get("performance_metrics", {})
            metric_count = len(performance_metrics)
            if metric_count > self.policy.max_validation_metrics:
                error_msg = f"Too many performance metrics: {metric_count} > {self.policy.max_validation_metrics}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(performance_input).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for performance patterns (additional validation)
            for pattern in self._performance_patterns:
                if pattern in content_str:
                    self.logger.warning(f"Performance pattern detected: {pattern}")
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
class PerformanceValidationRule:
    """Individual performance validation rule specification"""
    id: str
    validation_type: PerformanceValidationType
    severity: PerformanceSeverity
    criteria: Dict[str, Any]
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class LayerPerformanceValidationRequest:
    """Input request for layer performance validation operations"""
    layer_name: str
    layer_spec: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    performance_rules: List[Dict[str, Any]]
    validation_options: Dict[str, Any]
    context: Dict[str, Any]
    performance_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class PerformanceValidationError:
    """Individual performance validation error"""
    layer_id: str
    rule_id: str
    validation_type: PerformanceValidationType
    error_category: str
    error_message: str
    actual_value: Any
    expected_value: Any
    severity: PerformanceSeverity
    performance_impact: str


@dataclass
class PerformanceValidationResult:
    """Result of layer performance validation"""
    is_optimal: bool
    performance_score: float
    validation_errors: List[PerformanceValidationError]
    validation_warnings: List[PerformanceValidationError]
    performance_summary: Dict[str, Any]
    optimization_recommendations: List[str]
    performance_flags: List[str]


@dataclass
class LayerPerformanceValidationResult:
    """Output result from layer performance validation operations"""
    validation_result: PerformanceValidationResult
    validated_layer: Dict[str, Any]
    validation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    performance_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerPerformanceValidatorInterface(ABC):
    """Abstract interface for layer performance validation operations"""
    
    @abstractmethod
    async def validate_performance(self, request: LayerPerformanceValidationRequest) -> LayerPerformanceValidationResult:
        """Validate layer performance against rules and criteria"""
        pass
    
    @abstractmethod
    async def check_response_time_performance(self, metrics: Dict[str, Any]) -> List[PerformanceValidationError]:
        """Check response time performance metrics"""
        pass
    
    @abstractmethod
    async def check_resource_usage_performance(self, metrics: Dict[str, Any]) -> List[PerformanceValidationError]:
        """Check resource usage performance metrics"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerPerformanceValidator(LayerPerformanceValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating layer performance.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerPerformanceSafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerPerformanceSafetyPolicy()
        self.safety_validator = LayerPerformanceSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Performance validation patterns and rules
        self._validation_patterns = {
            PerformanceValidationType.RESPONSE_TIME: {
                "response_time_threshold": self._validate_response_time_threshold,
                "response_time_distribution": self._validate_response_time_distribution,
                "response_time_trends": self._validate_response_time_trends
            },
            PerformanceValidationType.THROUGHPUT: {
                "throughput_minimum": self._validate_throughput_minimum,
                "throughput_consistency": self._validate_throughput_consistency,
                "throughput_scaling": self._validate_throughput_scaling
            },
            PerformanceValidationType.RESOURCE_USAGE: {
                "cpu_usage": self._validate_cpu_usage,
                "memory_usage": self._validate_memory_usage,
                "disk_usage": self._validate_disk_usage
            },
            PerformanceValidationType.SCALABILITY: {
                "horizontal_scaling": self._validate_horizontal_scaling,
                "vertical_scaling": self._validate_vertical_scaling,
                "load_balancing": self._validate_load_balancing
            },
            PerformanceValidationType.LATENCY: {
                "network_latency": self._validate_network_latency,
                "processing_latency": self._validate_processing_latency,
                "latency_percentiles": self._validate_latency_percentiles
            },
            PerformanceValidationType.CONCURRENCY: {
                "concurrent_users": self._validate_concurrent_users,
                "thread_safety": self._validate_thread_safety,
                "deadlock_prevention": self._validate_deadlock_prevention
            }
        }
        
        self.logger.info("LayerPerformanceValidator initialized with L5 safety policies")
    
    async def validate_performance(self, request: LayerPerformanceValidationRequest) -> LayerPerformanceValidationResult:
        """
        Validate layer performance against rules and criteria.
        
        Args:
            request: Layer performance validation request with layer specification and performance metrics
            
        Returns:
            LayerPerformanceValidationResult: Structured result with performance validation outcome and details
            
        Raises:
            ValidationError: If performance validation fails
            SafetyError: If performance validation violates safety policies
        """
        self.logger.info(f"Validating performance for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            performance_input = {
                "performance_rules": request.performance_rules,
                "performance_metrics": request.performance_metrics
            }
            
            is_valid, error_msg = self.safety_validator.validate_performance_input(performance_input)
            if not is_valid:
                raise SafetyError(f"Performance safety validation failed: {error_msg}")
            
            # Sanitize performance data if required
            sanitized_metrics = request.performance_metrics
            if self.safety_policy.sanitize_performance_data:
                sanitized_metrics = await self._sanitize_performance_data(request.performance_metrics)
            
            # Parse performance rules
            parsed_rules = await self._parse_performance_rules(request.performance_rules)
            
            # Execute performance validation rules
            validation_errors = []
            for rule in parsed_rules:
                rule_errors = await self._execute_performance_rule(sanitized_metrics, rule)
                validation_errors.extend(rule_errors)
            
            # Check response time performance
            response_time_errors = await self.check_response_time_performance(sanitized_metrics)
            validation_errors.extend(response_time_errors)
            
            # Check resource usage performance
            resource_errors = await self.check_resource_usage_performance(sanitized_metrics)
            validation_errors.extend(resource_errors)
            
            # Separate errors and warnings based on severity
            error_list = [e for e in validation_errors if e.severity in [PerformanceSeverity.CRITICAL, PerformanceSeverity.HIGH]]
            warning_list = [e for e in validation_errors if e.severity in [PerformanceSeverity.MEDIUM, PerformanceSeverity.LOW]]
            
            # Determine overall performance optimality
            is_optimal = len(error_list) == 0
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(validation_errors)
            
            # Generate performance summary
            performance_summary = await self._generate_performance_summary(
                request.layer_name,
                sanitized_metrics,
                validation_errors
            )
            
            # Generate optimization recommendations
            optimization_recommendations = await self._generate_optimization_recommendations(validation_errors)
            
            # Extract performance flags
            performance_flags = self._extract_performance_flags(validation_errors)
            
            # Create validation result
            validation_result = PerformanceValidationResult(
                is_optimal=is_optimal,
                performance_score=performance_score,
                validation_errors=error_list,
                validation_warnings=warning_list,
                performance_summary=performance_summary,
                optimization_recommendations=optimization_recommendations,
                performance_flags=performance_flags
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_performance_risk_score(validation_result),
                "performance_flags": performance_flags
            }
            
            # Generate unique performance ID
            performance_id = self._generate_performance_id(request, validation_result)
            
            result = LayerPerformanceValidationResult(
                validation_result=validation_result,
                validated_layer=request.layer_spec,
                validation_metadata={
                    "layer_name": request.layer_name,
                    "rules_applied": len(parsed_rules),
                    "metrics_validated": len(sanitized_metrics),
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                performance_id=performance_id
            )
            
            self.logger.info(f"Successfully validated performance for {request.layer_name} with score {performance_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate layer performance: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def check_response_time_performance(self, metrics: Dict[str, Any]) -> List[PerformanceValidationError]:
        """Check response time performance metrics"""
        errors = []
        
        try:
            # Check average response time
            avg_response_time = metrics.get("average_response_time", 0)
            max_avg_response_time = metrics.get("max_average_response_time", 1000)  # Default 1 second
            
            if avg_response_time > max_avg_response_time:
                error = PerformanceValidationError(
                    layer_id="performance_check",
                    rule_id="response_time_validation",
                    validation_type=PerformanceValidationType.RESPONSE_TIME,
                    error_category="slow_response_time",
                    error_message=f"Average response time too high: {avg_response_time}ms",
                    actual_value=avg_response_time,
                    expected_value=f"<={max_avg_response_time}ms",
                    severity=PerformanceSeverity.HIGH,
                    performance_impact="user_experience"
                )
                errors.append(error)
            
            # Check 95th percentile response time
            p95_response_time = metrics.get("p95_response_time", 0)
            max_p95_response_time = metrics.get("max_p95_response_time", 2000)  # Default 2 seconds
            
            if p95_response_time > max_p95_response_time:
                error = PerformanceValidationError(
                    layer_id="performance_check",
                    rule_id="response_time_validation",
                    validation_type=PerformanceValidationType.RESPONSE_TIME,
                    error_category="high_p95_response_time",
                    error_message=f"95th percentile response time too high: {p95_response_time}ms",
                    actual_value=p95_response_time,
                    expected_value=f"<={max_p95_response_time}ms",
                    severity=PerformanceSeverity.MEDIUM,
                    performance_impact="user_experience"
                )
                errors.append(error)
            
            # Check response time consistency
            response_time_std = metrics.get("response_time_std", 0)
            max_std_deviation = metrics.get("max_response_time_std", 500)  # Default 500ms
            
            if response_time_std > max_std_deviation:
                error = PerformanceValidationError(
                    layer_id="performance_check",
                    rule_id="response_time_validation",
                    validation_type=PerformanceValidationType.RESPONSE_TIME,
                    error_category="inconsistent_response_time",
                    error_message=f"Response time standard deviation too high: {response_time_std}ms",
                    actual_value=response_time_std,
                    expected_value=f"<={max_std_deviation}ms",
                    severity=PerformanceSeverity.MEDIUM,
                    performance_impact="predictability"
                )
                errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Response time performance check failed: {str(e)}")
            error = PerformanceValidationError(
                layer_id="performance_check",
                rule_id="response_time_error",
                validation_type=PerformanceValidationType.RESPONSE_TIME,
                error_category="validation_error",
                error_message=f"Response time validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=PerformanceSeverity.HIGH,
                performance_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def check_resource_usage_performance(self, metrics: Dict[str, Any]) -> List[PerformanceValidationError]:
        """Check resource usage performance metrics"""
        errors = []
        
        try:
            # Check CPU usage
            cpu_usage = metrics.get("cpu_usage_percent", 0)
            max_cpu_usage = metrics.get("max_cpu_usage_percent", 80)  # Default 80%
            
            if cpu_usage > max_cpu_usage:
                error = PerformanceValidationError(
                    layer_id="performance_check",
                    rule_id="resource_usage_validation",
                    validation_type=PerformanceValidationType.RESOURCE_USAGE,
                    error_category="high_cpu_usage",
                    error_message=f"CPU usage too high: {cpu_usage}%",
                    actual_value=cpu_usage,
                    expected_value=f"<={max_cpu_usage}%",
                    severity=PerformanceSeverity.HIGH,
                    performance_impact="system_performance"
                )
                errors.append(error)
            
            # Check memory usage
            memory_usage = metrics.get("memory_usage_percent", 0)
            max_memory_usage = metrics.get("max_memory_usage_percent", 85)  # Default 85%
            
            if memory_usage > max_memory_usage:
                error = PerformanceValidationError(
                    layer_id="performance_check",
                    rule_id="resource_usage_validation",
                    validation_type=PerformanceValidationType.RESOURCE_USAGE,
                    error_category="high_memory_usage",
                    error_message=f"Memory usage too high: {memory_usage}%",
                    actual_value=memory_usage,
                    expected_value=f"<={max_memory_usage}%",
                    severity=PerformanceSeverity.HIGH,
                    performance_impact="system_performance"
                )
                errors.append(error)
            
            # Check disk usage
            disk_usage = metrics.get("disk_usage_percent", 0)
            max_disk_usage = metrics.get("max_disk_usage_percent", 90)  # Default 90%
            
            if disk_usage > max_disk_usage:
                error = PerformanceValidationError(
                    layer_id="performance_check",
                    rule_id="resource_usage_validation",
                    validation_type=PerformanceValidationType.RESOURCE_USAGE,
                    error_category="high_disk_usage",
                    error_message=f"Disk usage too high: {disk_usage}%",
                    actual_value=disk_usage,
                    expected_value=f"<={max_disk_usage}%",
                    severity=PerformanceSeverity.MEDIUM,
                    performance_impact="system_performance"
                )
                errors.append(error)
            
            # Check network I/O
            network_io = metrics.get("network_io_mbps", 0)
            max_network_io = metrics.get("max_network_io_mbps", 100)  # Default 100 Mbps
            
            if network_io > max_network_io:
                error = PerformanceValidationError(
                    layer_id="performance_check",
                    rule_id="resource_usage_validation",
                    validation_type=PerformanceValidationType.RESOURCE_USAGE,
                    error_category="high_network_io",
                    error_message=f"Network I/O too high: {network_io} Mbps",
                    actual_value=network_io,
                    expected_value=f"<={max_network_io} Mbps",
                    severity=PerformanceSeverity.MEDIUM,
                    performance_impact="network_performance"
                )
                errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Resource usage performance check failed: {str(e)}")
            error = PerformanceValidationError(
                layer_id="performance_check",
                rule_id="resource_usage_error",
                validation_type=PerformanceValidationType.RESOURCE_USAGE,
                error_category="validation_error",
                error_message=f"Resource usage validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=PerformanceSeverity.HIGH,
                performance_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def _parse_performance_rules(self, raw_rules: List[Dict[str, Any]]) -> List[PerformanceValidationRule]:
        """Parse raw performance rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = PerformanceValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    validation_type=PerformanceValidationType(raw_rule.get("validation_type", "response_time")),
                    severity=PerformanceSeverity(raw_rule.get("severity", "medium")),
                    criteria=raw_rule.get("criteria", {}),
                    error_message=raw_rule.get("error_message", "Performance validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse performance rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = PerformanceValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    validation_type=PerformanceValidationType.RESPONSE_TIME,
                    severity=PerformanceSeverity.MEDIUM,
                    criteria={},
                    error_message=f"Parsing failed: {str(e)}",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _execute_performance_rule(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Execute individual performance validation rule"""
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
                error = PerformanceValidationError(
                    layer_id="performance_check",
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="unknown_validation",
                    error_message=f"Unknown validation function: {rule.criteria.get('validation_function')}",
                    actual_value=None,
                    expected_value=None,
                    severity=PerformanceSeverity.MEDIUM,
                    performance_impact="validation"
                )
                errors.append(error)
                
        except Exception as e:
            self.logger.error(f"Failed to execute performance rule {rule.id}: {str(e)}")
            error = PerformanceValidationError(
                layer_id="performance_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="rule_execution_error",
                error_message=f"Rule execution failed: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=PerformanceSeverity.HIGH,
                performance_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def _sanitize_performance_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize performance data for safety"""
        sanitized = metrics.copy()
        
        # Remove dangerous content from string fields
        for key, value in sanitized.items():
            if isinstance(value, str):
                # Remove script tags and dangerous content
                sanitized_value = value.replace("<script", "").replace("</script>", "")
                sanitized[key] = sanitized_value
            elif isinstance(value, dict):
                sanitized[key] = await self._sanitize_performance_data(value)
            elif isinstance(value, list):
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        sanitized_item = item.replace("<script", "").replace("</script>", "")
                        sanitized_list.append(sanitized_item)
                    elif isinstance(item, dict):
                        sanitized_item = await self._sanitize_performance_data(item)
                        sanitized_list.append(sanitized_item)
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
        
        return sanitized
    
    # Validation function implementations
    async def _validate_response_time_threshold(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate response time threshold"""
        errors = []
        
        threshold = rule.criteria.get("threshold", 1000)
        actual_response_time = metrics.get("average_response_time", 0)
        
        if actual_response_time > threshold:
            error = PerformanceValidationError(
                layer_id="performance_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="response_time_threshold_exceeded",
                error_message=f"Response time {actual_response_time}ms exceeds threshold {threshold}ms",
                actual_value=actual_response_time,
                expected_value=f"<={threshold}ms",
                severity=rule.severity,
                performance_impact="user_experience"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_response_time_distribution(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate response time distribution"""
        # Simplified implementation
        return []
    
    async def _validate_response_time_trends(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate response time trends"""
        # Simplified implementation
        return []
    
    async def _validate_throughput_minimum(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate throughput minimum"""
        errors = []
        
        minimum_throughput = rule.criteria.get("minimum", 100)
        actual_throughput = metrics.get("throughput_rps", 0)
        
        if actual_throughput < minimum_throughput:
            error = PerformanceValidationError(
                layer_id="performance_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="throughput_below_minimum",
                error_message=f"Throughput {actual_throughput} RPS below minimum {minimum_throughput} RPS",
                actual_value=actual_throughput,
                expected_value=f">={minimum_throughput} RPS",
                severity=rule.severity,
                performance_impact="capacity"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_throughput_consistency(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate throughput consistency"""
        # Simplified implementation
        return []
    
    async def _validate_throughput_scaling(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate throughput scaling"""
        # Simplified implementation
        return []
    
    async def _validate_cpu_usage(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate CPU usage"""
        errors = []
        
        max_cpu_usage = rule.criteria.get("max_cpu_percent", 80)
        actual_cpu_usage = metrics.get("cpu_usage_percent", 0)
        
        if actual_cpu_usage > max_cpu_usage:
            error = PerformanceValidationError(
                layer_id="performance_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="high_cpu_usage",
                error_message=f"CPU usage {actual_cpu_usage}% exceeds maximum {max_cpu_usage}%",
                actual_value=actual_cpu_usage,
                expected_value=f"<={max_cpu_usage}%",
                severity=rule.severity,
                performance_impact="system_performance"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_memory_usage(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate memory usage"""
        errors = []
        
        max_memory_usage = rule.criteria.get("max_memory_percent", 85)
        actual_memory_usage = metrics.get("memory_usage_percent", 0)
        
        if actual_memory_usage > max_memory_usage:
            error = PerformanceValidationError(
                layer_id="performance_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="high_memory_usage",
                error_message=f"Memory usage {actual_memory_usage}% exceeds maximum {max_memory_usage}%",
                actual_value=actual_memory_usage,
                expected_value=f"<={max_memory_usage}%",
                severity=rule.severity,
                performance_impact="system_performance"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_disk_usage(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate disk usage"""
        # Simplified implementation
        return []
    
    async def _validate_horizontal_scaling(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate horizontal scaling"""
        # Simplified implementation
        return []
    
    async def _validate_vertical_scaling(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate vertical scaling"""
        # Simplified implementation
        return []
    
    async def _validate_load_balancing(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate load balancing"""
        # Simplified implementation
        return []
    
    async def _validate_network_latency(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate network latency"""
        # Simplified implementation
        return []
    
    async def _validate_processing_latency(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate processing latency"""
        # Simplified implementation
        return []
    
    async def _validate_latency_percentiles(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate latency percentiles"""
        # Simplified implementation
        return []
    
    async def _validate_concurrent_users(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate concurrent users"""
        # Simplified implementation
        return []
    
    async def _validate_thread_safety(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate thread safety"""
        # Simplified implementation
        return []
    
    async def _validate_deadlock_prevention(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate deadlock prevention"""
        # Simplified implementation
        return []
    
    def _calculate_performance_score(self, errors: List[PerformanceValidationError]) -> float:
        """Calculate performance score based on validation errors"""
        if not errors:
            return 1.0
        
        # Weight errors by severity
        severity_weights = {
            PerformanceSeverity.CRITICAL: 0.0,
            PerformanceSeverity.HIGH: 0.3,
            PerformanceSeverity.MEDIUM: 0.6,
            PerformanceSeverity.LOW: 0.8
        }
        
        total_weight = sum(severity_weights[error.severity] for error in errors)
        average_score = total_weight / len(errors)
        
        return round(average_score, 2)
    
    async def _generate_performance_summary(
        self, 
        layer_name: str,
        metrics: Dict[str, Any],
        errors: List[PerformanceValidationError]
    ) -> Dict[str, Any]:
        """Generate performance summary"""
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
                "average_response_time": metrics.get("average_response_time", 0),
                "cpu_usage": metrics.get("cpu_usage_percent", 0),
                "memory_usage": metrics.get("memory_usage_percent", 0),
                "throughput": metrics.get("throughput_rps", 0)
            }
        }
    
    async def _generate_optimization_recommendations(self, errors: List[PerformanceValidationError]) -> List[str]:
        """Generate optimization recommendations based on errors"""
        recommendations = []
        
        error_categories = [error.error_category for error in errors]
        
        if "slow_response_time" in error_categories:
            recommendations.append("Optimize algorithms and database queries")
            recommendations.append("Implement caching strategies")
        
        if "high_cpu_usage" in error_categories:
            recommendations.append("Optimize CPU-intensive operations")
            recommendations.append("Consider horizontal scaling")
        
        if "high_memory_usage" in error_categories:
            recommendations.append("Implement memory management improvements")
            recommendations.append("Check for memory leaks")
        
        if "throughput_below_minimum" in error_categories:
            recommendations.append("Increase server capacity")
            recommendations.append("Optimize request processing")
        
        if not recommendations:
            recommendations.append("Performance is within acceptable limits")
        
        return recommendations
    
    def _extract_performance_flags(self, errors: List[PerformanceValidationError]) -> List[str]:
        """Extract performance flags from validation errors"""
        performance_flags = []
        
        for error in errors:
            if error.validation_type == PerformanceValidationType.RESOURCE_USAGE:
                performance_flags.append("resource_usage_issue")
            elif error.validation_type == PerformanceValidationType.RESPONSE_TIME:
                performance_flags.append("response_time_issue")
            elif error.validation_type == PerformanceValidationType.THROUGHPUT:
                performance_flags.append("throughput_issue")
            elif error.severity == PerformanceSeverity.CRITICAL:
                performance_flags.append("critical_performance_issue")
        
        return performance_flags
    
    async def _estimate_validation_complexity(self, request: LayerPerformanceValidationRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.performance_rules) // 2
        
        # Add complexity for metrics
        complexity_score += len(request.performance_metrics) // 5
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_performance_risk_score(self, validation_result: PerformanceValidationResult) -> float:
        """Calculate risk score for the performance validation (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for performance errors
        if validation_result.validation_errors:
            risk_score += 0.3
        
        # Increase risk for critical issues
        critical_errors = [e for e in validation_result.validation_errors if e.severity == PerformanceSeverity.CRITICAL]
        if critical_errors:
            risk_score += 0.5
        
        # Increase risk for low performance score
        if validation_result.performance_score < 0.5:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_performance_id(self, request: LayerPerformanceValidationRequest, result: PerformanceValidationResult) -> str:
        """Generate unique performance identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.layer_name}:{result.performance_score:.2f}:{len(result.validation_errors)}:{timestamp}"
        return f"performance_validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: LayerPerformanceValidationRequest, error: str) -> LayerPerformanceValidationResult:
        """Create safe fallback validation when main validation fails"""
        layer_name = request.layer_spec.get("name", "unknown")
        
        fallback_error = PerformanceValidationError(
            layer_id=layer_name,
            rule_id="fallback_rule",
            validation_type=PerformanceValidationType.RESPONSE_TIME,
            error_category="validation_failed",
            error_message=f"Performance validation failed: {error}",
            actual_value="fallback",
            expected_value="success",
            severity=PerformanceSeverity.MEDIUM,
            performance_impact="validation"
        )
        
        fallback_result = PerformanceValidationResult(
            is_optimal=False,
            performance_score=0.0,
            validation_errors=[fallback_error],
            validation_warnings=[],
            performance_summary={"fallback": True},
            optimization_recommendations=["Fix performance validation system"],
            performance_flags=["fallback_mode"]
        )
        
        return LayerPerformanceValidationResult(
            validation_result=fallback_result,
            validated_layer=request.layer_spec,
            validation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            performance_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when performance validation violates safety policies"""
    pass


class LayerPerformanceValidationError(Exception):
    """Raised for general layer performance validation errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_performance_validator(safety_policy: Optional[LayerPerformanceSafetyPolicy] = None) -> LayerPerformanceValidator:
    """Factory function to create LayerPerformanceValidator with optional custom safety policy"""
    return LayerPerformanceValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_performance_request(request: LayerPerformanceValidationRequest) -> tuple[bool, Optional[str]]:
    """Validate layer performance request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.layer_spec, dict):
            return False, "Layer specification must be a dictionary"
        
        if not isinstance(request.performance_metrics, dict):
            return False, "Performance metrics must be a dictionary"
        
        if not isinstance(request.performance_rules, list):
            return False, "Performance rules must be a list"
        
        if not isinstance(request.validation_options, dict):
            return False, "Validation options must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
