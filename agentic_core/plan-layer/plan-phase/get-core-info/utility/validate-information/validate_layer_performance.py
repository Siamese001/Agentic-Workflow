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
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="response_time_distribution",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for response time distribution validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get response time metrics
        response_times = metrics.get("response_times", [])
        percentiles = metrics.get("percentiles", {})
        
        if not response_times:
            errors.append(PerformanceValidationError(
                metric_name="response_times",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="missing_response_times",
                error_message="Response times data is missing",
                actual_value=response_times,
                expected_value="list of response times",
                severity="error"
            ))
            return errors
        
        # Validate response time distribution characteristics
        if len(response_times) < 10:
            errors.append(PerformanceValidationError(
                metric_name="response_times",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="insufficient_sample_size",
                error_message=f"Insufficient response time samples: {len(response_times)} (minimum 10 required)",
                actual_value=len(response_times),
                expected_value=">= 10",
                severity="warning"
            ))
        
        # Calculate basic statistics
        import statistics
        try:
            mean_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
            
            # Check if mean response time exceeds threshold
            max_mean_threshold = rule.criteria.get("max_mean_response_time", 1000)  # ms
            if mean_response_time > max_mean_threshold:
                errors.append(PerformanceValidationError(
                    metric_name="mean_response_time",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="mean_response_time_exceeded",
                    error_message=f"Mean response time {mean_response_time:.2f}ms exceeds threshold {max_mean_threshold}ms",
                    actual_value=mean_response_time,
                    expected_value=f"<= {max_mean_threshold}",
                    severity="error"
                ))
            
            # Check for high standard deviation (indicating inconsistent performance)
            max_std_dev_threshold = rule.criteria.get("max_std_deviation", 500)  # ms
            if std_dev > max_std_dev_threshold:
                errors.append(PerformanceValidationError(
                    metric_name="response_time_std_deviation",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_response_time_variance",
                    error_message=f"Response time standard deviation {std_dev:.2f}ms exceeds threshold {max_std_dev_threshold}ms",
                    actual_value=std_dev,
                    expected_value=f"<= {max_std_dev_threshold}",
                    severity="warning"
                ))
            
            # Validate percentiles if provided
            if percentiles:
                p50 = percentiles.get("p50", median_response_time)
                p95 = percentiles.get("p95")
                p99 = percentiles.get("p99")
                
                if p95 and p95 > rule.criteria.get("max_p95_response_time", 2000):
                    errors.append(PerformanceValidationError(
                        metric_name="p95_response_time",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="p95_response_time_exceeded",
                        error_message=f"95th percentile response time {p95:.2f}ms exceeds threshold",
                        actual_value=p95,
                        expected_value=f"<= {rule.criteria.get('max_p95_response_time', 2000)}",
                        severity="error"
                    ))
                
                if p99 and p99 > rule.criteria.get("max_p99_response_time", 5000):
                    errors.append(PerformanceValidationError(
                        metric_name="p99_response_time",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="p99_response_time_exceeded",
                        error_message=f"99th percentile response time {p99:.2f}ms exceeds threshold",
                        actual_value=p99,
                        expected_value=f"<= {rule.criteria.get('max_p99_response_time', 5000)}",
                        severity="warning"
                    ))
            
            # Check for outliers (response times > 3 standard deviations from mean)
            outliers = [rt for rt in response_times if abs(rt - mean_response_time) > 3 * std_dev]
            outlier_percentage = len(outliers) / len(response_times) * 100
            
            if outlier_percentage > rule.criteria.get("max_outlier_percentage", 5):
                errors.append(PerformanceValidationError(
                    metric_name="response_time_outliers",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="excessive_outliers",
                    error_message=f"Response time outliers represent {outlier_percentage:.2f}% of requests (threshold: {rule.criteria.get('max_outlier_percentage', 5)}%)",
                    actual_value=outlier_percentage,
                    expected_value=f"<= {rule.criteria.get('max_outlier_percentage', 5)}",
                    severity="warning"
                ))
                
        except statistics.StatisticsError as e:
            errors.append(PerformanceValidationError(
                metric_name="response_time_statistics",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="statistics_calculation_error",
                error_message=f"Error calculating response time statistics: {str(e)}",
                actual_value=str(e),
                expected_value="valid statistics",
                severity="error"
            ))
        
        return errors
    
    async def _validate_response_time_trends(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate response time trends"""
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="response_time_trends",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for response time trends validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get time series data
        time_series_data = metrics.get("time_series", [])
        trend_analysis = metrics.get("trend_analysis", {})
        
        if not time_series_data:
            errors.append(PerformanceValidationError(
                metric_name="time_series_data",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="missing_time_series_data",
                error_message="Time series data for response time trends is missing",
                actual_value=time_series_data,
                expected_value="list of time series data points",
                severity="error"
            ))
            return errors
        
        # Validate time series data quality
        if len(time_series_data) < 5:
            errors.append(PerformanceValidationError(
                metric_name="time_series_data",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="insufficient_time_series_data",
                error_message=f"Insufficient time series data points: {len(time_series_data)} (minimum 5 required for trend analysis)",
                actual_value=len(time_series_data),
                expected_value=">= 5",
                severity="warning"
            ))
        
        # Analyze response time trends
        try:
            # Extract response times from time series data
            response_times_over_time = []
            timestamps = []
            
            for data_point in time_series_data:
                if isinstance(data_point, dict):
                    response_times_over_time.append(data_point.get("response_time", 0))
                    timestamps.append(data_point.get("timestamp", ""))
            
            if len(response_times_over_time) < 2:
                errors.append(PerformanceValidationError(
                    metric_name="time_series_data",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_data_for_trend",
                    error_message="Need at least 2 data points for trend analysis",
                    actual_value=len(response_times_over_time),
                    expected_value=">= 2",
                    severity="error"
                ))
                return errors
            
            # Calculate trend using simple linear regression
            import statistics
            n = len(response_times_over_time)
            x_values = list(range(n))  # Time indices
            y_values = response_times_over_time
            
            # Calculate slope (trend)
            x_mean = statistics.mean(x_values)
            y_mean = statistics.mean(y_values)
            
            numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator
            
            # Check for degrading performance (positive slope indicates increasing response times)
            max_degradation_rate = rule.criteria.get("max_degradation_rate", 10)  # ms per time unit
            if slope > max_degradation_rate:
                errors.append(PerformanceValidationError(
                    metric_name="response_time_degradation",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="performance_degradation_detected",
                    error_message=f"Response time is degrading at {slope:.2f}ms per time unit (threshold: {max_degradation_rate}ms)",
                    actual_value=slope,
                    expected_value=f"<= {max_degradation_rate}",
                    severity="error"
                ))
            elif slope > max_degradation_rate / 2:
                errors.append(PerformanceValidationError(
                    metric_name="response_time_degradation",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="performance_degradation_warning",
                    error_message=f"Response time shows slight degradation trend: {slope:.2f}ms per time unit",
                    actual_value=slope,
                    expected_value=f"<= {max_degradation_rate / 2}",
                    severity="warning"
                ))
            
            # Check for performance volatility
            if len(y_values) > 1:
                volatility = statistics.stdev(y_values) / statistics.mean(y_values) * 100 if statistics.mean(y_values) > 0 else 0
                max_volatility = rule.criteria.get("max_volatility", 20)  # percentage
                
                if volatility > max_volatility:
                    errors.append(PerformanceValidationError(
                        metric_name="response_time_volatility",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_performance_volatility",
                        error_message=f"Response time volatility is {volatility:.2f}% (threshold: {max_volatility}%)",
                        actual_value=volatility,
                        expected_value=f"<= {max_volatility}",
                        severity="warning"
                    ))
            
            # Validate trend analysis if provided
            if trend_analysis:
                trend_direction = trend_analysis.get("direction", "")
                trend_strength = trend_analysis.get("strength", 0)
                
                if trend_direction == "degrading" and trend_strength > rule.criteria.get("max_trend_strength", 0.7):
                    errors.append(PerformanceValidationError(
                        metric_name="trend_analysis",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="strong_degrading_trend",
                        error_message=f"Strong degrading trend detected with strength {trend_strength:.2f}",
                        actual_value=trend_strength,
                        expected_value=f"<= {rule.criteria.get('max_trend_strength', 0.7)}",
                        severity="error"
                    ))
                
                # Check for trend consistency
                trend_consistency = trend_analysis.get("consistency", 0)
                if trend_consistency < rule.criteria.get("min_trend_consistency", 0.5):
                    errors.append(PerformanceValidationError(
                        metric_name="trend_consistency",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="inconsistent_trend",
                        error_message=f"Trend analysis consistency is low: {trend_consistency:.2f}",
                        actual_value=trend_consistency,
                        expected_value=f">= {rule.criteria.get('min_trend_consistency', 0.5)}",
                        severity="warning"
                    ))
            
        except (statistics.StatisticsError, ValueError, ZeroDivisionError) as e:
            errors.append(PerformanceValidationError(
                metric_name="trend_calculation_error",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="trend_calculation_error",
                error_message=f"Error calculating response time trends: {str(e)}",
                actual_value=str(e),
                expected_value="valid trend calculation",
                severity="error"
            ))
        
        return errors
    
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
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="throughput_consistency",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for throughput consistency validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get throughput time series data
        throughput_series = metrics.get("throughput_series", [])
        current_throughput = metrics.get("throughput_rps", 0)
        
        if not throughput_series:
            errors.append(PerformanceValidationError(
                metric_name="throughput_series",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="missing_throughput_series",
                error_message="Throughput time series data is missing for consistency validation",
                actual_value=throughput_series,
                expected_value="list of throughput measurements over time",
                severity="error"
            ))
            return errors
        
        # Validate throughput series data quality
        if len(throughput_series) < 5:
            errors.append(PerformanceValidationError(
                metric_name="throughput_series",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="insufficient_throughput_data",
                error_message=f"Insufficient throughput data points: {len(throughput_series)} (minimum 5 required for consistency analysis)",
                actual_value=len(throughput_series),
                expected_value=">= 5",
                severity="warning"
            ))
        
        try:
            import statistics
            
            # Extract throughput values from series
            throughput_values = []
            for data_point in throughput_series:
                if isinstance(data_point, dict):
                    throughput_values.append(data_point.get("throughput", 0))
                elif isinstance(data_point, (int, float)):
                    throughput_values.append(data_point)
            
            if len(throughput_values) < 2:
                errors.append(PerformanceValidationError(
                    metric_name="throughput_series",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_data_for_consistency",
                    error_message="Need at least 2 throughput measurements for consistency analysis",
                    actual_value=len(throughput_values),
                    expected_value=">= 2",
                    severity="error"
                ))
                return errors
            
            # Calculate throughput statistics
            mean_throughput = statistics.mean(throughput_values)
            std_dev = statistics.stdev(throughput_values) if len(throughput_values) > 1 else 0
            
            # Calculate coefficient of variation (CV) for consistency
            cv = (std_dev / mean_throughput * 100) if mean_throughput > 0 else 0
            
            # Check for throughput consistency (lower CV is better)
            max_cv_threshold = rule.criteria.get("max_coefficient_of_variation", 15)  # percentage
            if cv > max_cv_threshold:
                errors.append(PerformanceValidationError(
                    metric_name="throughput_consistency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="inconsistent_throughput",
                    error_message=f"Throughput coefficient of variation {cv:.2f}% exceeds threshold {max_cv_threshold}%",
                    actual_value=cv,
                    expected_value=f"<= {max_cv_threshold}%",
                    severity="warning"
                ))
            
            # Check for significant throughput drops
            if len(throughput_values) > 1:
                max_throughput = max(throughput_values)
                min_throughput = min(throughput_values)
                
                if max_throughput > 0:
                    throughput_drop_percentage = ((max_throughput - min_throughput) / max_throughput) * 100
                    max_drop_threshold = rule.criteria.get("max_throughput_drop", 25)  # percentage
                    
                    if throughput_drop_percentage > max_drop_threshold:
                        errors.append(PerformanceValidationError(
                            metric_name="throughput_drop",
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="significant_throughput_drop",
                            error_message=f"Throughput drop of {throughput_drop_percentage:.2f}% detected (max: {max_throughput:.2f}, min: {min_throughput:.2f})",
                            actual_value=throughput_drop_percentage,
                            expected_value=f"<= {max_drop_threshold}%",
                            severity="error"
                        ))
            
            # Check for throughput stability over recent periods
            if len(throughput_values) >= 3:
                recent_values = throughput_values[-3:]  # Last 3 measurements
                recent_mean = statistics.mean(recent_values)
                overall_mean = mean_throughput
                
                if overall_mean > 0:
                    recent_deviation = abs(recent_mean - overall_mean) / overall_mean * 100
                    max_recent_deviation = rule.criteria.get("max_recent_deviation", 20)  # percentage
                    
                    if recent_deviation > max_recent_deviation:
                        errors.append(PerformanceValidationError(
                            metric_name="recent_throughput_deviation",
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="unstable_recent_throughput",
                            error_message=f"Recent throughput deviation {recent_deviation:.2f}% indicates instability",
                            actual_value=recent_deviation,
                            expected_value=f"<= {max_recent_deviation}%",
                            severity="warning"
                        ))
            
            # Validate throughput against baseline if provided
            baseline_throughput = metrics.get("baseline_throughput")
            if baseline_throughput and baseline_throughput > 0:
                current_vs_baseline = (current_throughput / baseline_throughput) * 100
                min_baseline_percentage = rule.criteria.get("min_baseline_percentage", 80)  # percentage
                
                if current_vs_baseline < min_baseline_percentage:
                    errors.append(PerformanceValidationError(
                        metric_name="throughput_vs_baseline",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="below_baseline_throughput",
                        error_message=f"Current throughput {current_throughput:.2f} RPS is {current_vs_baseline:.2f}% of baseline {baseline_throughput:.2f} RPS",
                        actual_value=current_vs_baseline,
                        expected_value=f">= {min_baseline_percentage}%",
                        severity="warning"
                    ))
            
        except (statistics.StatisticsError, ValueError, ZeroDivisionError) as e:
            errors.append(PerformanceValidationError(
                metric_name="throughput_consistency_calculation",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="consistency_calculation_error",
                error_message=f"Error calculating throughput consistency: {str(e)}",
                actual_value=str(e),
                expected_value="valid consistency calculation",
                severity="error"
            ))
        
        return errors
    
    async def _validate_throughput_scaling(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate throughput scaling"""
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="throughput_scaling",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for throughput scaling validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get scaling metrics
        scaling_data = metrics.get("scaling_data", {})
        load_levels = scaling_data.get("load_levels", [])
        throughput_at_load = scaling_data.get("throughput_at_load", {})
        scaling_efficiency = scaling_data.get("scaling_efficiency", 0)
        
        if not load_levels or not throughput_at_load:
            errors.append(PerformanceValidationError(
                metric_name="scaling_data",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="missing_scaling_data",
                error_message="Scaling data is missing for throughput scaling validation",
                actual_value=scaling_data,
                expected_value="scaling data with load levels and throughput measurements",
                severity="error"
            ))
            return errors
        
        try:
            # Validate scaling behavior across different load levels
            load_throughput_pairs = []
            for load_level in load_levels:
                throughput = throughput_at_load.get(str(load_level), 0)
                load_throughput_pairs.append((load_level, throughput))
            
            if len(load_throughput_pairs) < 2:
                errors.append(PerformanceValidationError(
                    metric_name="scaling_data",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_scaling_data",
                    error_message="Need at least 2 load levels for scaling analysis",
                    actual_value=len(load_throughput_pairs),
                    expected_value=">= 2",
                    severity="error"
                ))
                return errors
            
            # Sort by load level
            load_throughput_pairs.sort(key=lambda x: x[0])
            
            # Calculate scaling efficiency
            if scaling_efficiency == 0:
                # Calculate scaling efficiency if not provided
                first_load, first_throughput = load_throughput_pairs[0]
                last_load, last_throughput = load_throughput_pairs[-1]
                
                if first_load > 0 and first_throughput > 0:
                    load_ratio = last_load / first_load
                    throughput_ratio = last_throughput / first_throughput
                    scaling_efficiency = (throughput_ratio / load_ratio) * 100
            
            # Check scaling efficiency threshold
            min_efficiency_threshold = rule.criteria.get("min_scaling_efficiency", 70)  # percentage
            if scaling_efficiency < min_efficiency_threshold:
                errors.append(PerformanceValidationError(
                    metric_name="scaling_efficiency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="poor_scaling_efficiency",
                    error_message=f"Throughput scaling efficiency {scaling_efficiency:.2f}% below threshold {min_efficiency_threshold}%",
                    actual_value=scaling_efficiency,
                    expected_value=f">= {min_efficiency_threshold}%",
                    severity="error"
                ))
            
            # Check for linear scaling behavior
            import statistics
            loads = [pair[0] for pair in load_throughput_pairs]
            throughputs = [pair[1] for pair in load_throughput_pairs]
            
            # Calculate correlation coefficient for linearity
            if len(loads) > 1:
                n = len(loads)
                load_mean = statistics.mean(loads)
                throughput_mean = statistics.mean(throughputs)
                
                numerator = sum((loads[i] - load_mean) * (throughputs[i] - throughput_mean) for i in range(n))
                load_std_sum = sum((loads[i] - load_mean) ** 2 for i in range(n))
                throughput_std_sum = sum((throughputs[i] - throughput_mean) ** 2 for i in range(n))
                
                if load_std_sum > 0 and throughput_std_sum > 0:
                    correlation = numerator / (load_std_sum ** 0.5 * throughput_std_sum ** 0.5)
                    
                    # Check for linear scaling (correlation close to 1)
                    min_correlation_threshold = rule.criteria.get("min_linear_correlation", 0.9)
                    if correlation < min_correlation_threshold:
                        errors.append(PerformanceValidationError(
                            metric_name="linear_scaling",
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="non_linear_scaling",
                            error_message=f"Throughput scaling correlation {correlation:.3f} indicates non-linear behavior",
                            actual_value=correlation,
                            expected_value=f">= {min_correlation_threshold}",
                            severity="warning"
                        ))
            
            # Check for scaling bottlenecks
            if len(load_throughput_pairs) >= 3:
                # Look for plateau in throughput (indicating bottleneck)
                throughputs_sorted = sorted(throughputs)
                max_throughput = max(throughputs)
                
                # Check if throughput growth slows down significantly at higher loads
                throughput_growth_rates = []
                for i in range(1, len(load_throughput_pairs)):
                    prev_load, prev_throughput = load_throughput_pairs[i-1]
                    curr_load, curr_throughput = load_throughput_pairs[i]
                    
                    if prev_load > 0:
                        load_growth = (curr_load - prev_load) / prev_load
                        throughput_growth = (curr_throughput - prev_throughput) / prev_throughput if prev_throughput > 0 else 0
                        
                        if load_growth > 0:
                            growth_rate = throughput_growth / load_growth
                            throughput_growth_rates.append(growth_rate)
                
                if throughput_growth_rates:
                    avg_growth_rate = statistics.mean(throughput_growth_rates)
                    min_growth_rate = rule.criteria.get("min_growth_rate", 0.5)
                    
                    if avg_growth_rate < min_growth_rate:
                        errors.append(PerformanceValidationError(
                            metric_name="scaling_bottleneck",
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="scaling_bottleneck_detected",
                            error_message=f"Average throughput growth rate {avg_growth_rate:.3f} indicates scaling bottleneck",
                            actual_value=avg_growth_rate,
                            expected_value=f">= {min_growth_rate}",
                            severity="warning"
                        ))
            
            # Validate peak throughput capacity
            peak_throughput = max(throughputs) if throughputs else 0
            expected_peak_throughput = rule.criteria.get("expected_peak_throughput", 0)
            
            if expected_peak_throughput > 0 and peak_throughput < expected_peak_throughput:
                errors.append(PerformanceValidationError(
                    metric_name="peak_throughput",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="below_peak_throughput",
                    error_message=f"Peak throughput {peak_throughput:.2f} RPS below expected {expected_peak_throughput:.2f} RPS",
                    actual_value=peak_throughput,
                    expected_value=f">= {expected_peak_throughput}",
                    severity="warning"
                ))
            
        except (statistics.StatisticsError, ValueError, ZeroDivisionError) as e:
            errors.append(PerformanceValidationError(
                metric_name="scaling_calculation_error",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="scaling_calculation_error",
                error_message=f"Error calculating throughput scaling: {str(e)}",
                actual_value=str(e),
                expected_value="valid scaling calculation",
                severity="error"
            ))
        
        return errors
    
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
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="disk_usage",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for disk usage validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get disk usage metrics
        disk_usage_percent = metrics.get("disk_usage_percent", 0)
        disk_usage_gb = metrics.get("disk_usage_gb", 0)
        total_disk_gb = metrics.get("total_disk_gb", 0)
        disk_io_metrics = metrics.get("disk_io", {})
        
        # Validate disk usage percentage
        max_disk_usage = rule.criteria.get("max_disk_percent", 85)
        if disk_usage_percent > max_disk_usage:
            errors.append(PerformanceValidationError(
                metric_name="disk_usage_percent",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="high_disk_usage",
                error_message=f"Disk usage {disk_usage_percent}% exceeds maximum {max_disk_usage}%",
                actual_value=disk_usage_percent,
                expected_value=f"<={max_disk_usage}%",
                severity="error"
            ))
        elif disk_usage_percent > max_disk_usage - 10:  # Warning threshold
            errors.append(PerformanceValidationError(
                metric_name="disk_usage_percent",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="disk_usage_warning",
                error_message=f"Disk usage {disk_usage_percent}% approaching maximum {max_disk_usage}%",
                actual_value=disk_usage_percent,
                expected_value=f"<={max_disk_usage - 10}%",
                severity="warning"
            ))
        
        # Validate absolute disk usage if total is provided
        if total_disk_gb > 0:
            max_absolute_usage = rule.criteria.get("max_disk_gb", total_disk_gb * 0.85)
            if disk_usage_gb > max_absolute_usage:
                errors.append(PerformanceValidationError(
                    metric_name="disk_usage_gb",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_absolute_disk_usage",
                    error_message=f"Disk usage {disk_usage_gb:.2f}GB exceeds maximum {max_absolute_usage:.2f}GB",
                    actual_value=disk_usage_gb,
                    expected_value=f"<={max_absolute_usage:.2f}GB",
                    severity="error"
                ))
        
        # Validate disk I/O metrics if provided
        if disk_io_metrics:
            # Check disk read/write rates
            read_rate = disk_io_metrics.get("read_rate_mb_s", 0)
            write_rate = disk_io_metrics.get("write_rate_mb_s", 0)
            iops = disk_io_metrics.get("iops", 0)
            
            # Check for unusually high I/O that might indicate performance issues
            max_read_rate = rule.criteria.get("max_read_rate_mb_s", 100)
            max_write_rate = rule.criteria.get("max_write_rate_mb_s", 100)
            
            if read_rate > max_read_rate:
                errors.append(PerformanceValidationError(
                    metric_name="disk_read_rate",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_disk_read_rate",
                    error_message=f"Disk read rate {read_rate:.2f}MB/s exceeds threshold {max_read_rate}MB/s",
                    actual_value=read_rate,
                    expected_value=f"<={max_read_rate}MB/s",
                    severity="warning"
                ))
            
            if write_rate > max_write_rate:
                errors.append(PerformanceValidationError(
                    metric_name="disk_write_rate",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_disk_write_rate",
                    error_message=f"Disk write rate {write_rate:.2f}MB/s exceeds threshold {max_write_rate}MB/s",
                    actual_value=write_rate,
                    expected_value=f"<={max_write_rate}MB/s",
                    severity="warning"
                ))
            
            # Check IOPS utilization
            max_iops = rule.criteria.get("max_iops", 1000)
            if iops > max_iops:
                errors.append(PerformanceValidationError(
                    metric_name="disk_iops",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_disk_iops",
                    error_message=f"Disk IOPS {iops} exceeds threshold {max_iops}",
                    actual_value=iops,
                    expected_value=f"<={max_iops}",
                    severity="warning"
                ))
            
            # Check disk latency
            read_latency = disk_io_metrics.get("read_latency_ms", 0)
            write_latency = disk_io_metrics.get("write_latency_ms", 0)
            
            max_read_latency = rule.criteria.get("max_read_latency_ms", 10)
            max_write_latency = rule.criteria.get("max_write_latency_ms", 15)
            
            if read_latency > max_read_latency:
                errors.append(PerformanceValidationError(
                    metric_name="disk_read_latency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_disk_read_latency",
                    error_message=f"Disk read latency {read_latency:.2f}ms exceeds threshold {max_read_latency}ms",
                    actual_value=read_latency,
                    expected_value=f"<={max_read_latency}ms",
                    severity="error"
                ))
            
            if write_latency > max_write_latency:
                errors.append(PerformanceValidationError(
                    metric_name="disk_write_latency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_disk_write_latency",
                    error_message=f"Disk write latency {write_latency:.2f}ms exceeds threshold {max_write_latency}ms",
                    actual_value=write_latency,
                    expected_value=f"<={max_write_latency}ms",
                    severity="error"
                ))
        
        # Check for disk space growth trends if historical data is available
        disk_history = metrics.get("disk_usage_history", [])
        if len(disk_history) >= 3:
            # Calculate growth rate
            recent_usage = disk_history[-1] if isinstance(disk_history[-1], (int, float)) else disk_history[-1].get("usage_percent", 0)
            oldest_usage = disk_history[0] if isinstance(disk_history[0], (int, float)) else disk_history[0].get("usage_percent", 0)
            
            if oldest_usage > 0:
                growth_rate = ((recent_usage - oldest_usage) / oldest_usage) * 100
                max_growth_rate = rule.criteria.get("max_growth_rate_percent", 20)  # percentage over the period
                
                if growth_rate > max_growth_rate:
                    errors.append(PerformanceValidationError(
                        metric_name="disk_growth_rate",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_disk_growth_rate",
                        error_message=f"Disk usage growth rate {growth_rate:.2f}% exceeds threshold {max_growth_rate}%",
                        actual_value=growth_rate,
                        expected_value=f"<={max_growth_rate}%",
                        severity="warning"
                    ))
        
        return errors
    
    async def _validate_horizontal_scaling(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate horizontal scaling"""
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="horizontal_scaling",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for horizontal scaling validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get horizontal scaling metrics
        scaling_metrics = metrics.get("horizontal_scaling", {})
        current_instances = scaling_metrics.get("current_instances", 0)
        max_instances = scaling_metrics.get("max_instances", 0)
        min_instances = scaling_metrics.get("min_instances", 0)
        scaling_events = scaling_metrics.get("scaling_events", [])
        scaling_policies = scaling_metrics.get("scaling_policies", {})
        
        # Validate instance count configuration
        if current_instances == 0:
            errors.append(PerformanceValidationError(
                metric_name="current_instances",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_running_instances",
                error_message="No running instances detected",
                actual_value=current_instances,
                expected_value=">= 1",
                severity="error"
            ))
        
        if max_instances == 0:
            errors.append(PerformanceValidationError(
                metric_name="max_instances",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_max_instances_configured",
                error_message="Maximum instances not configured",
                actual_value=max_instances,
                expected_value=">= 1",
                severity="warning"
            ))
        
        if min_instances == 0:
            errors.append(PerformanceValidationError(
                metric_name="min_instances",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_min_instances_configured",
                error_message="Minimum instances not configured",
                actual_value=min_instances,
                expected_value=">= 1",
                severity="warning"
            ))
        
        # Validate instance count ranges
        if max_instances > 0 and min_instances > 0:
            if min_instances >= max_instances:
                errors.append(PerformanceValidationError(
                    metric_name="instance_range",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_instance_range",
                    error_message=f"Minimum instances ({min_instances}) must be less than maximum instances ({max_instances})",
                    actual_value=f"min: {min_instances}, max: {max_instances}",
                    expected_value="min < max",
                    severity="error"
                ))
            
            if current_instances > max_instances:
                errors.append(PerformanceValidationError(
                    metric_name="current_instances",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="exceeds_max_instances",
                    error_message=f"Current instances ({current_instances}) exceeds maximum ({max_instances})",
                    actual_value=current_instances,
                    expected_value=f"<= {max_instances}",
                    severity="error"
                ))
            
            if current_instances < min_instances:
                errors.append(PerformanceValidationError(
                    metric_name="current_instances",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="below_min_instances",
                    error_message=f"Current instances ({current_instances}) below minimum ({min_instances})",
                    actual_value=current_instances,
                    expected_value=f">= {min_instances}",
                    severity="error"
                ))
        
        # Validate scaling policies if provided
        if scaling_policies:
            # Check scale-out policy
            scale_out_policy = scaling_policies.get("scale_out", {})
            if scale_out_policy:
                scale_out_threshold = scale_out_policy.get("cpu_threshold", 0)
                scale_out_cooldown = scale_out_policy.get("cooldown_seconds", 0)
                
                if scale_out_threshold == 0:
                    errors.append(PerformanceValidationError(
                        metric_name="scale_out_cpu_threshold",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="missing_scale_out_threshold",
                        error_message="Scale-out CPU threshold not configured",
                        actual_value=scale_out_threshold,
                        expected_value="> 0",
                        severity="warning"
                    ))
                
                if scale_out_cooldown == 0:
                    errors.append(PerformanceValidationError(
                        metric_name="scale_out_cooldown",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="missing_scale_out_cooldown",
                        error_message="Scale-out cooldown not configured",
                        actual_value=scale_out_cooldown,
                        expected_value="> 0",
                        severity="warning"
                    ))
            
            # Check scale-in policy
            scale_in_policy = scaling_policies.get("scale_in", {})
            if scale_in_policy:
                scale_in_threshold = scale_in_policy.get("cpu_threshold", 0)
                scale_in_cooldown = scale_in_policy.get("cooldown_seconds", 0)
                
                if scale_in_threshold == 0:
                    errors.append(PerformanceValidationError(
                        metric_name="scale_in_cpu_threshold",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="missing_scale_in_threshold",
                        error_message="Scale-in CPU threshold not configured",
                        actual_value=scale_in_threshold,
                        expected_value="> 0",
                        severity="warning"
                    ))
                
                if scale_in_cooldown == 0:
                    errors.append(PerformanceValidationError(
                        metric_name="scale_in_cooldown",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="missing_scale_in_cooldown",
                        error_message="Scale-in cooldown not configured",
                        actual_value=scale_in_cooldown,
                        expected_value="> 0",
                        severity="warning"
                    ))
        
        # Validate scaling events if provided
        if scaling_events:
            # Check for excessive scaling events (indicates instability)
            recent_events = [event for event in scaling_events 
                           if self._is_recent_event(event, hours=24)]
            
            max_events_per_day = rule.criteria.get("max_scaling_events_per_day", 10)
            if len(recent_events) > max_events_per_day:
                errors.append(PerformanceValidationError(
                    metric_name="scaling_frequency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="excessive_scaling_events",
                    error_message=f"Too many scaling events in last 24 hours: {len(recent_events)} (threshold: {max_events_per_day})",
                    actual_value=len(recent_events),
                    expected_value=f"<= {max_events_per_day}",
                    severity="warning"
                ))
            
            # Check for failed scaling events
            failed_events = [event for event in scaling_events 
                           if event.get("status") == "failed"]
            
            if failed_events:
                errors.append(PerformanceValidationError(
                    metric_name="scaling_failures",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="scaling_failures_detected",
                    error_message=f"Scaling failures detected: {len(failed_events)} events",
                    actual_value=len(failed_events),
                    expected_value=0,
                    severity="error"
                ))
            
            # Check scaling latency
            successful_events = [event for event in scaling_events 
                               if event.get("status") == "success" and "duration_seconds" in event]
            
            if successful_events:
                import statistics
                scaling_latencies = [event["duration_seconds"] for event in successful_events]
                avg_scaling_latency = statistics.mean(scaling_latencies)
                
                max_scaling_latency = rule.criteria.get("max_scaling_latency_seconds", 300)  # 5 minutes
                if avg_scaling_latency > max_scaling_latency:
                    errors.append(PerformanceValidationError(
                        metric_name="scaling_latency",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_scaling_latency",
                        error_message=f"Average scaling latency {avg_scaling_latency:.2f}s exceeds threshold {max_scaling_latency}s",
                        actual_value=avg_scaling_latency,
                        expected_value=f"<= {max_scaling_latency}s",
                        severity="warning"
                    ))
        
        # Validate scaling efficiency
        scaling_efficiency = scaling_metrics.get("scaling_efficiency", 0)
        min_efficiency = rule.criteria.get("min_scaling_efficiency", 70)  # percentage
        
        if scaling_efficiency > 0 and scaling_efficiency < min_efficiency:
            errors.append(PerformanceValidationError(
                metric_name="scaling_efficiency",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="poor_scaling_efficiency",
                error_message=f"Horizontal scaling efficiency {scaling_efficiency:.2f}% below threshold {min_efficiency}%",
                actual_value=scaling_efficiency,
                expected_value=f">= {min_efficiency}%",
                severity="warning"
            ))
        
        return errors
    
    def _is_recent_event(self, event: Dict[str, Any], hours: int = 24) -> bool:
        """Helper method to check if an event is recent"""
        try:
            from datetime import datetime, timedelta
            event_time = event.get("timestamp")
            if isinstance(event_time, str):
                event_time = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
            elif isinstance(event_time, (int, float)):
                event_time = datetime.fromtimestamp(event_time)
            else:
                return False
            
            return datetime.now(event_time.tzinfo) - event_time < timedelta(hours=hours)
        except (ValueError, TypeError, AttributeError):
            return False
    
    async def _validate_vertical_scaling(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate vertical scaling"""
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="vertical_scaling",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for vertical scaling validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get vertical scaling metrics
        scaling_metrics = metrics.get("vertical_scaling", {})
        current_resources = scaling_metrics.get("current_resources", {})
        max_resources = scaling_metrics.get("max_resources", {})
        min_resources = scaling_metrics.get("min_resources", {})
        scaling_events = scaling_metrics.get("scaling_events", [])
        resource_utilization = scaling_metrics.get("resource_utilization", {})
        
        # Validate CPU vertical scaling
        current_cpu = current_resources.get("cpu_cores", 0)
        max_cpu = max_resources.get("cpu_cores", 0)
        min_cpu = min_resources.get("cpu_cores", 0)
        
        if current_cpu == 0:
            errors.append(PerformanceValidationError(
                metric_name="current_cpu_cores",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_cpu_allocated",
                error_message="No CPU cores allocated",
                actual_value=current_cpu,
                expected_value=">= 1",
                severity="error"
            ))
        
        if max_cpu == 0:
            errors.append(PerformanceValidationError(
                metric_name="max_cpu_cores",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_max_cpu_configured",
                error_message="Maximum CPU cores not configured for vertical scaling",
                actual_value=max_cpu,
                expected_value=">= 1",
                severity="warning"
            ))
        
        if max_cpu > 0 and current_cpu > max_cpu:
            errors.append(PerformanceValidationError(
                metric_name="current_cpu_cores",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="exceeds_max_cpu",
                error_message=f"Current CPU cores ({current_cpu}) exceeds maximum ({max_cpu})",
                actual_value=current_cpu,
                expected_value=f"<= {max_cpu}",
                severity="error"
            ))
        
        # Validate memory vertical scaling
        current_memory = current_resources.get("memory_gb", 0)
        max_memory = max_resources.get("memory_gb", 0)
        min_memory = min_resources.get("memory_gb", 0)
        
        if current_memory == 0:
            errors.append(PerformanceValidationError(
                metric_name="current_memory_gb",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_memory_allocated",
                error_message="No memory allocated",
                actual_value=current_memory,
                expected_value=">= 1",
                severity="error"
            ))
        
        if max_memory == 0:
            errors.append(PerformanceValidationError(
                metric_name="max_memory_gb",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_max_memory_configured",
                error_message="Maximum memory not configured for vertical scaling",
                actual_value=max_memory,
                expected_value=">= 1",
                severity="warning"
            ))
        
        if max_memory > 0 and current_memory > max_memory:
            errors.append(PerformanceValidationError(
                metric_name="current_memory_gb",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="exceeds_max_memory",
                error_message=f"Current memory ({current_memory}GB) exceeds maximum ({max_memory}GB)",
                actual_value=current_memory,
                expected_value=f"<= {max_memory}",
                severity="error"
            ))
        
        # Validate resource ranges
        if max_cpu > 0 and min_cpu > 0:
            if min_cpu >= max_cpu:
                errors.append(PerformanceValidationError(
                    metric_name="cpu_range",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_cpu_range",
                    error_message=f"Minimum CPU cores ({min_cpu}) must be less than maximum ({max_cpu})",
                    actual_value=f"min: {min_cpu}, max: {max_cpu}",
                    expected_value="min < max",
                    severity="error"
                ))
        
        if max_memory > 0 and min_memory > 0:
            if min_memory >= max_memory:
                errors.append(PerformanceValidationError(
                    metric_name="memory_range",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_memory_range",
                    error_message=f"Minimum memory ({min_memory}GB) must be less than maximum ({max_memory}GB)",
                    actual_value=f"min: {min_memory}, max: {max_memory}",
                    expected_value="min < max",
                    severity="error"
                ))
        
        # Validate resource utilization for scaling decisions
        if resource_utilization:
            cpu_utilization = resource_utilization.get("cpu_percent", 0)
            memory_utilization = resource_utilization.get("memory_percent", 0)
            
            # Check if resources are underutilized (potential for scale-down)
            min_cpu_utilization = rule.criteria.get("min_cpu_utilization_percent", 20)
            min_memory_utilization = rule.criteria.get("min_memory_utilization_percent", 30)
            
            if cpu_utilization < min_cpu_utilization and current_cpu > min_cpu:
                errors.append(PerformanceValidationError(
                    metric_name="cpu_underutilization",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="cpu_underutilized",
                    error_message=f"CPU utilization {cpu_utilization}% below threshold {min_cpu_utilization}% with {current_cpu} cores allocated",
                    actual_value=cpu_utilization,
                    expected_value=f">= {min_cpu_utilization}%",
                    severity="warning"
                ))
            
            if memory_utilization < min_memory_utilization and current_memory > min_memory:
                errors.append(PerformanceValidationError(
                    metric_name="memory_underutilization",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="memory_underutilized",
                    error_message=f"Memory utilization {memory_utilization}% below threshold {min_memory_utilization}% with {current_memory}GB allocated",
                    actual_value=memory_utilization,
                    expected_value=f">= {min_memory_utilization}%",
                    severity="warning"
                ))
        
        # Validate scaling events if provided
        if scaling_events:
            # Check for excessive vertical scaling events
            recent_events = [event for event in scaling_events 
                           if self._is_recent_event(event, hours=24)]
            
            max_events_per_day = rule.criteria.get("max_vertical_scaling_events_per_day", 5)
            if len(recent_events) > max_events_per_day:
                errors.append(PerformanceValidationError(
                    metric_name="vertical_scaling_frequency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="excessive_vertical_scaling",
                    error_message=f"Too many vertical scaling events in last 24 hours: {len(recent_events)} (threshold: {max_events_per_day})",
                    actual_value=len(recent_events),
                    expected_value=f"<= {max_events_per_day}",
                    severity="error"
                ))
            
            # Check for failed scaling events
            failed_events = [event for event in scaling_events 
                           if event.get("status") == "failed"]
            
            if failed_events:
                errors.append(PerformanceValidationError(
                    metric_name="vertical_scaling_failures",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="vertical_scaling_failures_detected",
                    error_message=f"Vertical scaling failures detected: {len(failed_events)} events",
                    actual_value=len(failed_events),
                    expected_value=0,
                    severity="error"
                ))
            
            # Check scaling direction balance
            scale_up_events = [event for event in scaling_events 
                             if event.get("direction") == "up"]
            scale_down_events = [event for event in scaling_events 
                               if event.get("direction") == "down"]
            
            if len(scale_up_events) > len(scale_down_events) * 3:
                errors.append(PerformanceValidationError(
                    metric_name="scaling_direction_imbalance",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="excessive_scale_up_events",
                    error_message=f"Scale-up events ({len(scale_up_events)}) significantly outnumber scale-down events ({len(scale_down_events)})",
                    actual_value=f"up: {len(scale_up_events)}, down: {len(scale_down_events)}",
                    expected_value="balanced scaling",
                    severity="warning"
                ))
        
        # Validate scaling efficiency
        scaling_efficiency = scaling_metrics.get("scaling_efficiency", 0)
        min_efficiency = rule.criteria.get("min_vertical_scaling_efficiency", 75)  # percentage
        
        if scaling_efficiency > 0 and scaling_efficiency < min_efficiency:
            errors.append(PerformanceValidationError(
                metric_name="vertical_scaling_efficiency",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="poor_vertical_scaling_efficiency",
                error_message=f"Vertical scaling efficiency {scaling_efficiency:.2f}% below threshold {min_efficiency}%",
                actual_value=scaling_efficiency,
                expected_value=f">= {min_efficiency}%",
                severity="warning"
            ))
        
        # Check for resource hot-plug capability if configured
        hot_plug_config = scaling_metrics.get("hot_plug_config", {})
        if hot_plug_config:
            cpu_hot_plug = hot_plug_config.get("cpu_enabled", False)
            memory_hot_plug = hot_plug_config.get("memory_enabled", False)
            
            if not cpu_hot_plug and max_cpu > min_cpu:
                errors.append(PerformanceValidationError(
                    metric_name="cpu_hot_plug",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="cpu_hot_plug_disabled",
                    error_message="CPU hot-plug disabled but vertical scaling range configured",
                    actual_value=cpu_hot_plug,
                    expected_value=True,
                    severity="warning"
                ))
            
            if not memory_hot_plug and max_memory > min_memory:
                errors.append(PerformanceValidationError(
                    metric_name="memory_hot_plug",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="memory_hot_plug_disabled",
                    error_message="Memory hot-plug disabled but vertical scaling range configured",
                    actual_value=memory_hot_plug,
                    expected_value=True,
                    severity="warning"
                ))
        
        return errors
    
    async def _validate_load_balancing(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate load balancing"""
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="load_balancing",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for load balancing validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get load balancing metrics
        lb_metrics = metrics.get("load_balancing", {})
        algorithm = lb_metrics.get("algorithm", "")
        backend_instances = lb_metrics.get("backend_instances", [])
        health_checks = lb_metrics.get("health_checks", {})
        distribution_metrics = lb_metrics.get("distribution", {})
        
        # Validate load balancer configuration
        if not algorithm:
            errors.append(PerformanceValidationError(
                metric_name="load_balancing_algorithm",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="missing_load_balancing_algorithm",
                error_message="Load balancing algorithm not configured",
                actual_value=algorithm,
                expected_value="valid algorithm (round_robin, least_connections, ip_hash, etc.)",
                severity="error"
            ))
        
        # Validate backend instances
        if not backend_instances:
            errors.append(PerformanceValidationError(
                metric_name="backend_instances",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_backend_instances",
                error_message="No backend instances configured for load balancing",
                actual_value=len(backend_instances),
                expected_value=">= 1",
                severity="error"
            ))
            return errors
        
        # Check minimum number of backend instances
        min_instances = rule.criteria.get("min_backend_instances", 2)
        if len(backend_instances) < min_instances:
            errors.append(PerformanceValidationError(
                metric_name="backend_instances_count",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="insufficient_backend_instances",
                error_message=f"Insufficient backend instances: {len(backend_instances)} (minimum: {min_instances})",
                actual_value=len(backend_instances),
                expected_value=f">= {min_instances}",
                severity="warning"
            ))
        
        # Validate backend instance health
        healthy_instances = [inst for inst in backend_instances if inst.get("healthy", False)]
        unhealthy_instances = [inst for inst in backend_instances if not inst.get("healthy", False)]
        
        if len(healthy_instances) == 0:
            errors.append(PerformanceValidationError(
                metric_name="healthy_backend_instances",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_healthy_instances",
                error_message="No healthy backend instances available",
                actual_value=len(healthy_instances),
                expected_value=">= 1",
                severity="error"
            ))
        elif len(healthy_instances) < len(backend_instances) * 0.5:  # Less than 50% healthy
            errors.append(PerformanceValidationError(
                metric_name="healthy_instance_ratio",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="low_healthy_instance_ratio",
                error_message=f"Low healthy instance ratio: {len(healthy_instances)}/{len(backend_instances)}",
                actual_value=len(healthy_instances),
                expected_value=f">= {len(backend_instances) // 2}",
                severity="error"
            ))
        
        # Validate health check configuration
        if health_checks:
            health_check_enabled = health_checks.get("enabled", False)
            health_check_interval = health_checks.get("interval_seconds", 0)
            health_check_timeout = health_checks.get("timeout_seconds", 0)
            
            if not health_check_enabled:
                errors.append(PerformanceValidationError(
                    metric_name="health_check_enabled",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="health_checks_disabled",
                    error_message="Health checks are disabled for load balancer",
                    actual_value=health_check_enabled,
                    expected_value=True,
                    severity="warning"
                ))
            
            if health_check_interval == 0:
                errors.append(PerformanceValidationError(
                    metric_name="health_check_interval",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_health_check_interval",
                    error_message="Health check interval not configured",
                    actual_value=health_check_interval,
                    expected_value="> 0",
                    severity="warning"
                ))
            
            if health_check_timeout == 0:
                errors.append(PerformanceValidationError(
                    metric_name="health_check_timeout",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_health_check_timeout",
                    error_message="Health check timeout not configured",
                    actual_value=health_check_timeout,
                    expected_value="> 0",
                    severity="warning"
                ))
            
            # Check if timeout is reasonable compared to interval
            if health_check_interval > 0 and health_check_timeout > 0:
                if health_check_timeout >= health_check_interval:
                    errors.append(PerformanceValidationError(
                        metric_name="health_check_timing",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="health_check_timeout_too_high",
                        error_message=f"Health check timeout ({health_check_timeout}s) should be less than interval ({health_check_interval}s)",
                        actual_value=health_check_timeout,
                        expected_value=f"< {health_check_interval}",
                        severity="warning"
                    ))
        
        # Validate load distribution if provided
        if distribution_metrics:
            # Check request distribution across instances
            request_counts = distribution_metrics.get("request_counts", {})
            total_requests = sum(request_counts.values()) if request_counts else 0
            
            if total_requests > 0:
                # Calculate distribution balance (coefficient of variation)
                import statistics
                counts = list(request_counts.values())
                mean_requests = statistics.mean(counts)
                std_dev = statistics.stdev(counts) if len(counts) > 1 else 0
                
                cv = (std_dev / mean_requests * 100) if mean_requests > 0 else 0
                max_cv_threshold = rule.criteria.get("max_distribution_cv", 25)  # percentage
                
                if cv > max_cv_threshold:
                    errors.append(PerformanceValidationError(
                        metric_name="load_distribution_balance",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="unbalanced_load_distribution",
                        error_message=f"Load distribution coefficient of variation {cv:.2f}% exceeds threshold {max_cv_threshold}%",
                        actual_value=cv,
                        expected_value=f"<= {max_cv_threshold}%",
                        severity="warning"
                    ))
            
            # Check response time distribution across instances
            response_times = distribution_metrics.get("response_times", {})
            if response_times:
                avg_response_times = []
                for instance_id, times in response_times.items():
                    if times:
                        avg_response_times.append(statistics.mean(times))
                
                if avg_response_times:
                    max_response_time = max(avg_response_times)
                    min_response_time = min(avg_response_times)
                    
                    if max_response_time > 0:
                        response_time_variance = ((max_response_time - min_response_time) / max_response_time) * 100
                        max_variance_threshold = rule.criteria.get("max_response_time_variance", 50)  # percentage
                        
                        if response_time_variance > max_variance_threshold:
                            errors.append(PerformanceValidationError(
                                metric_name="response_time_distribution",
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="uneven_response_time_distribution",
                                error_message=f"Response time variance {response_time_variance:.2f}% across instances exceeds threshold",
                                actual_value=response_time_variance,
                                expected_value=f"<= {max_variance_threshold}%",
                                severity="warning"
                            ))
        
        # Validate session persistence if configured
        session_persistence = lb_metrics.get("session_persistence", {})
        if session_persistence:
            persistence_enabled = session_persistence.get("enabled", False)
            persistence_type = session_persistence.get("type", "")
            
            if persistence_enabled and not persistence_type:
                errors.append(PerformanceValidationError(
                    metric_name="session_persistence_type",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_session_persistence_type",
                    error_message="Session persistence enabled but type not specified",
                    actual_value=persistence_type,
                    expected_value="valid persistence type (cookie, ip_hash, etc.)",
                    severity="warning"
                ))
        
        # Check for failover configuration
        failover_config = lb_metrics.get("failover", {})
        if failover_config:
            failover_enabled = failover_config.get("enabled", False)
            failover_threshold = failover_config.get("failure_threshold", 0)
            
            if failover_enabled and failover_threshold == 0:
                errors.append(PerformanceValidationError(
                    metric_name="failover_threshold",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_failover_threshold",
                    error_message="Failover enabled but failure threshold not configured",
                    actual_value=failover_threshold,
                    expected_value="> 0",
                    severity="warning"
                ))
        
        return errors
    
    async def _validate_network_latency(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate network latency"""
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="network_latency",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for network latency validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get network latency metrics
        latency_metrics = metrics.get("network_latency", {})
        current_latency = latency_metrics.get("current_latency_ms", 0)
        latency_history = latency_metrics.get("latency_history_ms", [])
        latency_percentiles = latency_metrics.get("percentiles", {})
        connection_metrics = latency_metrics.get("connections", {})
        
        # Validate current network latency
        max_latency_threshold = rule.criteria.get("max_latency_ms", 100)
        if current_latency > max_latency_threshold:
            errors.append(PerformanceValidationError(
                metric_name="current_network_latency",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="high_network_latency",
                error_message=f"Current network latency {current_latency:.2f}ms exceeds threshold {max_latency_threshold}ms",
                actual_value=current_latency,
                expected_value=f"<= {max_latency_threshold}ms",
                severity="error"
            ))
        elif current_latency > max_latency_threshold * 0.8:  # Warning threshold
            errors.append(PerformanceValidationError(
                metric_name="current_network_latency",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="elevated_network_latency",
                error_message=f"Network latency {current_latency:.2f}ms approaching threshold {max_latency_threshold}ms",
                actual_value=current_latency,
                expected_value=f"<= {max_latency_threshold * 0.8}ms",
                severity="warning"
            ))
        
        # Validate latency history if provided
        if latency_history:
            if len(latency_history) < 5:
                errors.append(PerformanceValidationError(
                    metric_name="latency_history",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_latency_history",
                    error_message=f"Insufficient latency history data: {len(latency_history)} samples (minimum 5 required)",
                    actual_value=len(latency_history),
                    expected_value=">= 5",
                    severity="warning"
                ))
            
            # Calculate latency statistics
            import statistics
            try:
                avg_latency = statistics.mean(latency_history)
                std_dev = statistics.stdev(latency_history) if len(latency_history) > 1 else 0
                
                # Check average latency threshold
                max_avg_latency = rule.criteria.get("max_avg_latency_ms", 80)
                if avg_latency > max_avg_latency:
                    errors.append(PerformanceValidationError(
                        metric_name="avg_network_latency",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_avg_latency",
                        error_message=f"Average network latency {avg_latency:.2f}ms exceeds threshold {max_avg_latency}ms",
                        actual_value=avg_latency,
                        expected_value=f"<= {max_avg_latency}ms",
                        severity="error"
                    ))
                
                # Check latency consistency (lower standard deviation is better)
                max_std_dev = rule.criteria.get("max_latency_std_dev_ms", 20)
                if std_dev > max_std_dev:
                    errors.append(PerformanceValidationError(
                        metric_name="latency_consistency",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="inconsistent_latency",
                        error_message=f"Network latency standard deviation {std_dev:.2f}ms exceeds threshold {max_std_dev}ms",
                        actual_value=std_dev,
                        expected_value=f"<= {max_std_dev}ms",
                        severity="warning"
                    ))
                
                # Check for latency trends
                if len(latency_history) >= 3:
                    recent_avg = statistics.mean(latency_history[-3:])
                    older_avg = statistics.mean(latency_history[:3])
                    
                    if older_avg > 0:
                        latency_growth = ((recent_avg - older_avg) / older_avg) * 100
                        max_growth_threshold = rule.criteria.get("max_latency_growth_percent", 15)
                        
                        if latency_growth > max_growth_threshold:
                            errors.append(PerformanceValidationError(
                                metric_name="latency_trend",
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="increasing_latency_trend",
                                error_message=f"Network latency increasing by {latency_growth:.2f}% over time",
                                actual_value=latency_growth,
                                expected_value=f"<= {max_growth_threshold}%",
                                severity="warning"
                            ))
                
            except statistics.StatisticsError as e:
                errors.append(PerformanceValidationError(
                    metric_name="latency_statistics",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="latency_statistics_error",
                    error_message=f"Error calculating latency statistics: {str(e)}",
                    actual_value=str(e),
                    expected_value="valid statistics",
                    severity="error"
                ))
        
        # Validate latency percentiles if provided
        if latency_percentiles:
            p50 = latency_percentiles.get("p50", 0)
            p95 = latency_percentiles.get("p95", 0)
            p99 = latency_percentiles.get("p99", 0)
            
            # Check 95th percentile latency
            max_p95_latency = rule.criteria.get("max_p95_latency_ms", 150)
            if p95 > max_p95_latency:
                errors.append(PerformanceValidationError(
                    metric_name="p95_network_latency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_p95_latency",
                    error_message=f"95th percentile network latency {p95:.2f}ms exceeds threshold {max_p95_latency}ms",
                    actual_value=p95,
                    expected_value=f"<= {max_p95_latency}ms",
                    severity="error"
                ))
            
            # Check 99th percentile latency
            max_p99_latency = rule.criteria.get("max_p99_latency_ms", 200)
            if p99 > max_p99_latency:
                errors.append(PerformanceValidationError(
                    metric_name="p99_network_latency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_p99_latency",
                    error_message=f"99th percentile network latency {p99:.2f}ms exceeds threshold {max_p99_latency}ms",
                    actual_value=p99,
                    expected_value=f"<= {max_p99_latency}ms",
                    severity="warning"
                ))
        
        # Validate connection metrics if provided
        if connection_metrics:
            active_connections = connection_metrics.get("active_connections", 0)
            max_connections = connection_metrics.get("max_connections", 0)
            connection_errors = connection_metrics.get("connection_errors", 0)
            
            # Check connection error rate
            total_connections = connection_metrics.get("total_connections", 1)
            if total_connections > 0:
                error_rate = (connection_errors / total_connections) * 100
                max_error_rate = rule.criteria.get("max_connection_error_rate", 1)  # percentage
                
                if error_rate > max_error_rate:
                    errors.append(PerformanceValidationError(
                        metric_name="connection_error_rate",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_connection_error_rate",
                        error_message=f"Connection error rate {error_rate:.2f}% exceeds threshold {max_error_rate}%",
                        actual_value=error_rate,
                        expected_value=f"<= {max_error_rate}%",
                        severity="error"
                    ))
            
            # Check connection pool utilization
            if max_connections > 0:
                utilization = (active_connections / max_connections) * 100
                max_utilization = rule.criteria.get("max_connection_utilization", 80)  # percentage
                
                if utilization > max_utilization:
                    errors.append(PerformanceValidationError(
                        metric_name="connection_pool_utilization",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_connection_utilization",
                        error_message=f"Connection pool utilization {utilization:.2f}% exceeds threshold {max_utilization}%",
                        actual_value=utilization,
                        expected_value=f"<= {max_utilization}%",
                        severity="warning"
                    ))
        
        # Check for network latency SLA compliance if configured
        sla_config = latency_metrics.get("sla", {})
        if sla_config:
            sla_target = sla_config.get("target_latency_ms", 0)
            sla_compliance = sla_config.get("compliance_percentage", 0)
            
            if sla_target > 0 and sla_compliance > 0:
                min_sla_compliance = rule.criteria.get("min_sla_compliance", 95)  # percentage
                
                if sla_compliance < min_sla_compliance:
                    errors.append(PerformanceValidationError(
                        metric_name="sla_compliance",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="sla_compliance_failure",
                        error_message=f"Network latency SLA compliance {sla_compliance:.2f}% below target {min_sla_compliance}% for {sla_target}ms target",
                        actual_value=sla_compliance,
                        expected_value=f">= {min_sla_compliance}%",
                        severity="error"
                    ))
        
        return errors
    
    async def _validate_processing_latency(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate processing latency"""
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="processing_latency",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for processing latency validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get processing latency metrics
        processing_metrics = metrics.get("processing_latency", {})
        current_processing_time = processing_metrics.get("current_processing_time_ms", 0)
        processing_history = processing_metrics.get("processing_history_ms", [])
        queue_metrics = processing_metrics.get("queue", {})
        worker_metrics = processing_metrics.get("workers", {})
        
        # Validate current processing time
        max_processing_time = rule.criteria.get("max_processing_time_ms", 200)
        if current_processing_time > max_processing_time:
            errors.append(PerformanceValidationError(
                metric_name="current_processing_latency",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="high_processing_latency",
                error_message=f"Current processing time {current_processing_time:.2f}ms exceeds threshold {max_processing_time}ms",
                actual_value=current_processing_time,
                expected_value=f"<= {max_processing_time}ms",
                severity="error"
            ))
        elif current_processing_time > max_processing_time * 0.8:  # Warning threshold
            errors.append(PerformanceValidationError(
                metric_name="current_processing_latency",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="elevated_processing_latency",
                error_message=f"Processing time {current_processing_time:.2f}ms approaching threshold {max_processing_time}ms",
                actual_value=current_processing_time,
                expected_value=f"<= {max_processing_time * 0.8}ms",
                severity="warning"
            ))
        
        # Validate processing history if provided
        if processing_history:
            if len(processing_history) < 5:
                errors.append(PerformanceValidationError(
                    metric_name="processing_history",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_processing_history",
                    error_message=f"Insufficient processing history data: {len(processing_history)} samples (minimum 5 required)",
                    actual_value=len(processing_history),
                    expected_value=">= 5",
                    severity="warning"
                ))
            
            # Calculate processing statistics
            import statistics
            try:
                avg_processing_time = statistics.mean(processing_history)
                std_dev = statistics.stdev(processing_history) if len(processing_history) > 1 else 0
                
                # Check average processing time threshold
                max_avg_processing_time = rule.criteria.get("max_avg_processing_time_ms", 150)
                if avg_processing_time > max_avg_processing_time:
                    errors.append(PerformanceValidationError(
                        metric_name="avg_processing_latency",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_avg_processing_time",
                        error_message=f"Average processing time {avg_processing_time:.2f}ms exceeds threshold {max_avg_processing_time}ms",
                        actual_value=avg_processing_time,
                        expected_value=f"<= {max_avg_processing_time}ms",
                        severity="error"
                    ))
                
                # Check processing consistency
                max_processing_std_dev = rule.criteria.get("max_processing_std_dev_ms", 30)
                if std_dev > max_processing_std_dev:
                    errors.append(PerformanceValidationError(
                        metric_name="processing_consistency",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="inconsistent_processing_time",
                        error_message=f"Processing time standard deviation {std_dev:.2f}ms exceeds threshold {max_processing_std_dev}ms",
                        actual_value=std_dev,
                        expected_value=f"<= {max_processing_std_dev}ms",
                        severity="warning"
                    ))
                
                # Check for processing bottlenecks (increasing trend)
                if len(processing_history) >= 3:
                    recent_avg = statistics.mean(processing_history[-3:])
                    older_avg = statistics.mean(processing_history[:3])
                    
                    if older_avg > 0:
                        processing_growth = ((recent_avg - older_avg) / older_avg) * 100
                        max_growth_threshold = rule.criteria.get("max_processing_growth_percent", 20)
                        
                        if processing_growth > max_growth_threshold:
                            errors.append(PerformanceValidationError(
                                metric_name="processing_trend",
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="increasing_processing_time",
                                error_message=f"Processing time increasing by {processing_growth:.2f}% over time",
                                actual_value=processing_growth,
                                expected_value=f"<= {max_growth_threshold}%",
                                severity="warning"
                            ))
                
            except statistics.StatisticsError as e:
                errors.append(PerformanceValidationError(
                    metric_name="processing_statistics",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="processing_statistics_error",
                    error_message=f"Error calculating processing statistics: {str(e)}",
                    actual_value=str(e),
                    expected_value="valid statistics",
                    severity="error"
                ))
        
        # Validate queue metrics if provided
        if queue_metrics:
            queue_size = queue_metrics.get("current_size", 0)
            max_queue_size = queue_metrics.get("max_size", 0)
            queue_wait_time = queue_metrics.get("avg_wait_time_ms", 0)
            
            # Check queue size
            max_allowed_queue_size = rule.criteria.get("max_queue_size", 100)
            if queue_size > max_allowed_queue_size:
                errors.append(PerformanceValidationError(
                    metric_name="queue_size",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="large_queue_size",
                    error_message=f"Queue size {queue_size} exceeds threshold {max_allowed_queue_size}",
                    actual_value=queue_size,
                    expected_value=f"<= {max_allowed_queue_size}",
                    severity="warning"
                ))
            
            # Check queue utilization
            if max_queue_size > 0:
                queue_utilization = (queue_size / max_queue_size) * 100
                max_queue_utilization = rule.criteria.get("max_queue_utilization", 80)  # percentage
                
                if queue_utilization > max_queue_utilization:
                    errors.append(PerformanceValidationError(
                        metric_name="queue_utilization",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_queue_utilization",
                        error_message=f"Queue utilization {queue_utilization:.2f}% exceeds threshold {max_queue_utilization}%",
                        actual_value=queue_utilization,
                        expected_value=f"<= {max_queue_utilization}%",
                        severity="error"
                    ))
            
            # Check queue wait time
            max_queue_wait_time = rule.criteria.get("max_queue_wait_time_ms", 50)
            if queue_wait_time > max_queue_wait_time:
                errors.append(PerformanceValidationError(
                    metric_name="queue_wait_time",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_queue_wait_time",
                    error_message=f"Average queue wait time {queue_wait_time:.2f}ms exceeds threshold {max_queue_wait_time}ms",
                    actual_value=queue_wait_time,
                    expected_value=f"<= {max_queue_wait_time}ms",
                    severity="warning"
                ))
        
        # Validate worker metrics if provided
        if worker_metrics:
            active_workers = worker_metrics.get("active_workers", 0)
            total_workers = worker_metrics.get("total_workers", 0)
            worker_utilization = worker_metrics.get("utilization_percent", 0)
            
            # Check worker availability
            min_active_workers = rule.criteria.get("min_active_workers", 1)
            if active_workers < min_active_workers:
                errors.append(PerformanceValidationError(
                    metric_name="active_workers",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_active_workers",
                    error_message=f"Active workers {active_workers} below minimum {min_active_workers}",
                    actual_value=active_workers,
                    expected_value=f">= {min_active_workers}",
                    severity="error"
                ))
            
            # Check worker utilization
            max_worker_utilization = rule.criteria.get("max_worker_utilization", 85)  # percentage
            if worker_utilization > max_worker_utilization:
                errors.append(PerformanceValidationError(
                    metric_name="worker_utilization",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_worker_utilization",
                    error_message=f"Worker utilization {worker_utilization:.2f}% exceeds threshold {max_worker_utilization}%",
                    actual_value=worker_utilization,
                    expected_value=f"<= {max_worker_utilization}%",
                    severity="warning"
                ))
            
            # Check for worker saturation
            if total_workers > 0:
                saturation_ratio = active_workers / total_workers
                max_saturation_ratio = rule.criteria.get("max_worker_saturation", 0.9)
                
                if saturation_ratio > max_saturation_ratio:
                    errors.append(PerformanceValidationError(
                        metric_name="worker_saturation",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="worker_saturation",
                        error_message=f"Worker saturation ratio {saturation_ratio:.2f} exceeds threshold {max_saturation_ratio}",
                        actual_value=saturation_ratio,
                        expected_value=f"<= {max_saturation_ratio}",
                        severity="error"
                    ))
        
        # Check for processing pipeline bottlenecks if configured
        pipeline_metrics = processing_metrics.get("pipeline", {})
        if pipeline_metrics:
            pipeline_stages = pipeline_metrics.get("stages", [])
            bottleneck_stage = pipeline_metrics.get("bottleneck_stage", "")
            
            if pipeline_stages:
                # Check if any stage is taking significantly longer than others
                stage_times = [stage.get("processing_time_ms", 0) for stage in pipeline_stages]
                if stage_times:
                    max_stage_time = max(stage_times)
                    avg_stage_time = statistics.mean(stage_times)
                    
                    if avg_stage_time > 0:
                        bottleneck_ratio = max_stage_time / avg_stage_time
                        max_bottleneck_ratio = rule.criteria.get("max_bottleneck_ratio", 3.0)
                        
                        if bottleneck_ratio > max_bottleneck_ratio:
                            errors.append(PerformanceValidationError(
                                metric_name="pipeline_bottleneck",
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="pipeline_bottleneck_detected",
                                error_message=f"Pipeline bottleneck detected: stage ratio {bottleneck_ratio:.2f} exceeds threshold",
                                actual_value=bottleneck_ratio,
                                expected_value=f"<= {max_bottleneck_ratio}",
                                severity="warning"
                            ))
        
        return errors
    
    async def _validate_latency_percentiles(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate latency percentiles"""
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="latency_percentiles",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for latency percentiles validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get latency percentile metrics
        percentile_metrics = metrics.get("latency_percentiles", {})
        percentiles = percentile_metrics.get("values", {})
        sample_size = percentile_metrics.get("sample_size", 0)
        calculation_time = percentile_metrics.get("calculation_time_ms", 0)
        
        # Validate sample size
        min_sample_size = rule.criteria.get("min_sample_size", 100)
        if sample_size < min_sample_size:
            errors.append(PerformanceValidationError(
                metric_name="percentile_sample_size",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="insufficient_sample_size",
                error_message=f"Sample size {sample_size} insufficient for percentile calculation (minimum: {min_sample_size})",
                actual_value=sample_size,
                expected_value=f">= {min_sample_size}",
                severity="warning"
            ))
        
        # Validate required percentiles
        required_percentiles = rule.criteria.get("required_percentiles", [50, 90, 95, 99])
        missing_percentiles = []
        
        for p in required_percentiles:
            if f"p{p}" not in percentiles:
                missing_percentiles.append(f"p{p}")
        
        if missing_percentiles:
            errors.append(PerformanceValidationError(
                metric_name="required_percentiles",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="missing_required_percentiles",
                error_message=f"Missing required percentiles: {', '.join(missing_percentiles)}",
                actual_value=list(percentiles.keys()),
                expected_value=required_percentiles,
                severity="error"
            ))
        
        # Validate percentile values if provided
        if percentiles:
            # Check 50th percentile (median)
            p50 = percentiles.get("p50", 0)
            max_p50 = rule.criteria.get("max_p50_ms", 50)
            if p50 > max_p50:
                errors.append(PerformanceValidationError(
                    metric_name="p50_latency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_p50_latency",
                    error_message=f"50th percentile latency {p50:.2f}ms exceeds threshold {max_p50}ms",
                    actual_value=p50,
                    expected_value=f"<= {max_p50}ms",
                    severity="error"
                ))
            
            # Check 90th percentile
            p90 = percentiles.get("p90", 0)
            max_p90 = rule.criteria.get("max_p90_ms", 100)
            if p90 > max_p90:
                errors.append(PerformanceValidationError(
                    metric_name="p90_latency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_p90_latency",
                    error_message=f"90th percentile latency {p90:.2f}ms exceeds threshold {max_p90}ms",
                    actual_value=p90,
                    expected_value=f"<= {max_p90}ms",
                    severity="error"
                ))
            
            # Check 95th percentile
            p95 = percentiles.get("p95", 0)
            max_p95 = rule.criteria.get("max_p95_ms", 150)
            if p95 > max_p95:
                errors.append(PerformanceValidationError(
                    metric_name="p95_latency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_p95_latency",
                    error_message=f"95th percentile latency {p95:.2f}ms exceeds threshold {max_p95}ms",
                    actual_value=p95,
                    expected_value=f"<= {max_p95}ms",
                    severity="error"
                ))
            
            # Check 99th percentile
            p99 = percentiles.get("p99", 0)
            max_p99 = rule.criteria.get("max_p99_ms", 250)
            if p99 > max_p99:
                errors.append(PerformanceValidationError(
                    metric_name="p99_latency",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_p99_latency",
                    error_message=f"99th percentile latency {p99:.2f}ms exceeds threshold {max_p99}ms",
                    actual_value=p99,
                    expected_value=f"<= {max_p99}ms",
                    severity="warning"
                ))
            
            # Check 99.9th percentile if available
            p999 = percentiles.get("p99_9", 0)
            if p999 > 0:
                max_p999 = rule.criteria.get("max_p99_9_ms", 500)
                if p999 > max_p999:
                    errors.append(PerformanceValidationError(
                        metric_name="p99_9_latency",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_p99_9_latency",
                        error_message=f"99.9th percentile latency {p999:.2f}ms exceeds threshold {max_p999}ms",
                        actual_value=p999,
                        expected_value=f"<= {max_p999}ms",
                        severity="warning"
                    ))
        
        # Validate percentile distribution consistency
        if all(p in percentiles for p in ["p50", "p90", "p95", "p99"]):
            p50 = percentiles["p50"]
            p90 = percentiles["p90"]
            p95 = percentiles["p95"]
            p99 = percentiles["p99"]
            
            # Check if percentiles are in ascending order
            if not (p50 <= p90 <= p95 <= p99):
                errors.append(PerformanceValidationError(
                    metric_name="percentile_order",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_percentile_order",
                    error_message="Percentiles are not in ascending order: p50={}, p90={}, p95={}, p99={}".format(p50, p90, p95, p99),
                    actual_value=[p50, p90, p95, p99],
                    expected_value="ascending order",
                    severity="error"
                ))
            
            # Check for reasonable percentile ratios
            if p50 > 0:
                p90_p50_ratio = p90 / p50
                p95_p50_ratio = p95 / p50
                p99_p50_ratio = p99 / p50
                
                max_p90_p50_ratio = rule.criteria.get("max_p90_p50_ratio", 3.0)
                max_p95_p50_ratio = rule.criteria.get("max_p95_p50_ratio", 4.0)
                max_p99_p50_ratio = rule.criteria.get("max_p99_p50_ratio", 6.0)
                
                if p90_p50_ratio > max_p90_p50_ratio:
                    errors.append(PerformanceValidationError(
                        metric_name="p90_p50_ratio",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="excessive_p90_p50_ratio",
                        error_message=f"P90/P50 ratio {p90_p50_ratio:.2f} exceeds threshold {max_p90_p50_ratio}",
                        actual_value=p90_p50_ratio,
                        expected_value=f"<= {max_p90_p50_ratio}",
                        severity="warning"
                    ))
                
                if p95_p50_ratio > max_p95_p50_ratio:
                    errors.append(PerformanceValidationError(
                        metric_name="p95_p50_ratio",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="excessive_p95_p50_ratio",
                        error_message=f"P95/P50 ratio {p95_p50_ratio:.2f} exceeds threshold {max_p95_p50_ratio}",
                        actual_value=p95_p50_ratio,
                        expected_value=f"<= {max_p95_p50_ratio}",
                        severity="warning"
                    ))
                
                if p99_p50_ratio > max_p99_p50_ratio:
                    errors.append(PerformanceValidationError(
                        metric_name="p99_p50_ratio",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="excessive_p99_p50_ratio",
                        error_message=f"P99/P50 ratio {p99_p50_ratio:.2f} exceeds threshold {max_p99_p50_ratio}",
                        actual_value=p99_p50_ratio,
                        expected_value=f"<= {max_p99_p50_ratio}",
                        severity="warning"
                    ))
        
        # Validate calculation performance
        max_calculation_time = rule.criteria.get("max_calculation_time_ms", 100)
        if calculation_time > max_calculation_time:
            errors.append(PerformanceValidationError(
                metric_name="percentile_calculation_time",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="slow_percentile_calculation",
                error_message=f"Percentile calculation time {calculation_time:.2f}ms exceeds threshold {max_calculation_time}ms",
                actual_value=calculation_time,
                expected_value=f"<= {max_calculation_time}ms",
                severity="warning"
            ))
        
        # Check for percentile SLA compliance if configured
        sla_config = percentile_metrics.get("sla", {})
        if sla_config:
            sla_percentiles = sla_config.get("percentiles", {})
            sla_targets = sla_config.get("targets", {})
            
            for percentile, target in sla_targets.items():
                actual_value = percentiles.get(percentile, 0)
                if actual_value > target:
                    errors.append(PerformanceValidationError(
                        metric_name=f"sla_{percentile}",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="sla_percentile_violation",
                        error_message=f"SLA violation: {percentile} latency {actual_value:.2f}ms exceeds target {target}ms",
                        actual_value=actual_value,
                        expected_value=f"<= {target}ms",
                        severity="error"
                    ))
        
        return errors
    
    async def _validate_concurrent_users(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate concurrent users"""
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="concurrent_users",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for concurrent users validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get concurrent user metrics
        user_metrics = metrics.get("concurrent_users", {})
        current_users = user_metrics.get("current_count", 0)
        peak_users = user_metrics.get("peak_count", 0)
        max_capacity = user_metrics.get("max_capacity", 0)
        user_history = user_metrics.get("history", [])
        session_metrics = user_metrics.get("sessions", {})
        
        # Validate current concurrent users
        if current_users == 0:
            errors.append(PerformanceValidationError(
                metric_name="current_concurrent_users",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_active_users",
                error_message="No concurrent users detected",
                actual_value=current_users,
                expected_value=">= 1",
                severity="warning"
            ))
        
        # Validate capacity configuration
        if max_capacity == 0:
            errors.append(PerformanceValidationError(
                metric_name="max_user_capacity",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_capacity_configured",
                error_message="Maximum user capacity not configured",
                actual_value=max_capacity,
                expected_value="> 0",
                severity="error"
            ))
        else:
            # Check if current users exceed capacity
            if current_users > max_capacity:
                errors.append(PerformanceValidationError(
                    metric_name="current_vs_capacity",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="capacity_exceeded",
                    error_message=f"Current concurrent users {current_users} exceeds maximum capacity {max_capacity}",
                    actual_value=current_users,
                    expected_value=f"<= {max_capacity}",
                    severity="error"
                ))
            
            # Check capacity utilization
            utilization = (current_users / max_capacity) * 100
            max_utilization = rule.criteria.get("max_user_utilization", 85)  # percentage
            
            if utilization > max_utilization:
                errors.append(PerformanceValidationError(
                    metric_name="user_capacity_utilization",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_capacity_utilization",
                    error_message=f"User capacity utilization {utilization:.2f}% exceeds threshold {max_utilization}%",
                    actual_value=utilization,
                    expected_value=f"<= {max_utilization}%",
                    severity="warning"
                ))
        
        # Validate peak users if provided
        if peak_users > 0:
            if peak_users > max_capacity:
                errors.append(PerformanceValidationError(
                    metric_name="peak_vs_capacity",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="peak_exceeds_capacity",
                    error_message=f"Peak concurrent users {peak_users} exceeds maximum capacity {max_capacity}",
                    actual_value=peak_users,
                    expected_value=f"<= {max_capacity}",
                    severity="error"
                ))
            
            # Check peak-to-current ratio
            if current_users > 0:
                peak_ratio = peak_users / current_users
                max_peak_ratio = rule.criteria.get("max_peak_to_current_ratio", 2.0)
                
                if peak_ratio > max_peak_ratio:
                    errors.append(PerformanceValidationError(
                        metric_name="peak_to_current_ratio",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="excessive_peak_ratio",
                        error_message=f"Peak-to-current user ratio {peak_ratio:.2f} indicates potential load spikes",
                        actual_value=peak_ratio,
                        expected_value=f"<= {max_peak_ratio}",
                        severity="warning"
                    ))
        
        # Validate user history if provided
        if user_history:
            if len(user_history) < 5:
                errors.append(PerformanceValidationError(
                    metric_name="user_history",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_user_history",
                    error_message=f"Insufficient user history data: {len(user_history)} samples (minimum 5 required)",
                    actual_value=len(user_history),
                    expected_value=">= 5",
                    severity="warning"
                ))
            
            # Calculate user statistics
            import statistics
            try:
                avg_users = statistics.mean(user_history)
                std_dev = statistics.stdev(user_history) if len(user_history) > 1 else 0
                
                # Check average users threshold
                min_avg_users = rule.criteria.get("min_avg_concurrent_users", 1)
                if avg_users < min_avg_users:
                    errors.append(PerformanceValidationError(
                        metric_name="avg_concurrent_users",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="low_avg_concurrent_users",
                        error_message=f"Average concurrent users {avg_users:.2f} below minimum {min_avg_users}",
                        actual_value=avg_users,
                        expected_value=f">= {min_avg_users}",
                        severity="warning"
                    ))
                
                # Check user count consistency
                max_user_std_dev = rule.criteria.get("max_user_std_dev", 50)
                if std_dev > max_user_std_dev:
                    errors.append(PerformanceValidationError(
                        metric_name="user_count_consistency",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="inconsistent_user_count",
                        error_message=f"User count standard deviation {std_dev:.2f} exceeds threshold {max_user_std_dev}",
                        actual_value=std_dev,
                        expected_value=f"<= {max_user_std_dev}",
                        severity="warning"
                    ))
                
                # Check for user growth trends
                if len(user_history) >= 3:
                    recent_avg = statistics.mean(user_history[-3:])
                    older_avg = statistics.mean(user_history[:3])
                    
                    if older_avg > 0:
                        user_growth = ((recent_avg - older_avg) / older_avg) * 100
                        max_growth_threshold = rule.criteria.get("max_user_growth_percent", 25)
                        
                        if user_growth > max_growth_threshold:
                            errors.append(PerformanceValidationError(
                                metric_name="user_growth_trend",
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="rapid_user_growth",
                                error_message=f"Concurrent users growing by {user_growth:.2f}% over time",
                                actual_value=user_growth,
                                expected_value=f"<= {max_growth_threshold}%",
                                severity="warning"
                            ))
                
            except statistics.StatisticsError as e:
                errors.append(PerformanceValidationError(
                    metric_name="user_statistics",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="user_statistics_error",
                    error_message=f"Error calculating user statistics: {str(e)}",
                    actual_value=str(e),
                    expected_value="valid statistics",
                    severity="error"
                ))
        
        # Validate session metrics if provided
        if session_metrics:
            active_sessions = session_metrics.get("active_sessions", 0)
            session_duration_avg = session_metrics.get("avg_duration_minutes", 0)
            session_timeout_rate = session_metrics.get("timeout_rate_percent", 0)
            
            # Check session consistency
            if active_sessions != current_users:
                max_session_discrepancy = rule.criteria.get("max_session_discrepancy", 5)
                discrepancy = abs(active_sessions - current_users)
                
                if discrepancy > max_session_discrepancy:
                    errors.append(PerformanceValidationError(
                        metric_name="session_user_consistency",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="session_user_discrepancy",
                        error_message=f"Session count ({active_sessions}) differs from user count ({current_users}) by {discrepancy}",
                        actual_value=discrepancy,
                        expected_value=f"<= {max_session_discrepancy}",
                        severity="warning"
                    ))
            
            # Check session duration
            max_session_duration = rule.criteria.get("max_session_duration_minutes", 60)
            if session_duration_avg > max_session_duration:
                errors.append(PerformanceValidationError(
                    metric_name="session_duration",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="long_session_duration",
                    error_message=f"Average session duration {session_duration_avg:.2f} minutes exceeds threshold {max_session_duration}",
                    actual_value=session_duration_avg,
                    expected_value=f"<= {max_session_duration}",
                    severity="warning"
                ))
            
            # Check session timeout rate
            max_timeout_rate = rule.criteria.get("max_session_timeout_rate", 5)  # percentage
            if session_timeout_rate > max_timeout_rate:
                errors.append(PerformanceValidationError(
                    metric_name="session_timeout_rate",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_session_timeout_rate",
                    error_message=f"Session timeout rate {session_timeout_rate:.2f}% exceeds threshold {max_timeout_rate}%",
                    actual_value=session_timeout_rate,
                    expected_value=f"<= {max_timeout_rate}%",
                    severity="warning"
                ))
        
        # Check for user capacity planning if configured
        capacity_planning = user_metrics.get("capacity_planning", {})
        if capacity_planning:
            projected_growth = capacity_planning.get("projected_growth_percent", 0)
            recommended_capacity = capacity_planning.get("recommended_capacity", 0)
            
            if recommended_capacity > 0 and max_capacity > 0:
                if recommended_capacity > max_capacity:
                    capacity_gap = recommended_capacity - max_capacity
                    errors.append(PerformanceValidationError(
                        metric_name="capacity_planning_gap",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="capacity_planning_gap",
                        error_message=f"Recommended capacity {recommended_capacity} exceeds current capacity {max_capacity} by {capacity_gap}",
                        actual_value=capacity_gap,
                        expected_value=0,
                        severity="warning"
                    ))
            
            if projected_growth > 0:
                max_projected_growth = rule.criteria.get("max_projected_growth_percent", 50)
                if projected_growth > max_projected_growth:
                    errors.append(PerformanceValidationError(
                        metric_name="projected_growth",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_projected_growth",
                        error_message=f"Projected user growth {projected_growth:.2f}% exceeds threshold {max_projected_growth}%",
                        actual_value=projected_growth,
                        expected_value=f"<= {max_projected_growth}%",
                        severity="warning"
                    ))
        
        return errors
    
    async def _validate_thread_safety(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate thread safety"""
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="thread_safety",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for thread safety validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get thread safety metrics
        thread_metrics = metrics.get("thread_safety", {})
        concurrent_threads = thread_metrics.get("concurrent_threads", 0)
        thread_contentions = thread_metrics.get("contentions", 0)
        deadlocks = thread_metrics.get("deadlocks", 0)
        race_conditions = thread_metrics.get("race_conditions", 0)
        lock_metrics = thread_metrics.get("locks", {})
        thread_pool_metrics = thread_metrics.get("thread_pool", {})
        
        # Validate concurrent threads
        max_concurrent_threads = rule.criteria.get("max_concurrent_threads", 100)
        if concurrent_threads > max_concurrent_threads:
            errors.append(PerformanceValidationError(
                metric_name="concurrent_threads",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="excessive_concurrent_threads",
                error_message=f"Concurrent threads {concurrent_threads} exceeds threshold {max_concurrent_threads}",
                actual_value=concurrent_threads,
                expected_value=f"<= {max_concurrent_threads}",
                severity="warning"
            ))
        
        # Validate thread contentions
        max_contentions = rule.criteria.get("max_thread_contentions", 10)
        if thread_contentions > max_contentions:
            errors.append(PerformanceValidationError(
                metric_name="thread_contentions",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="high_thread_contentions",
                error_message=f"Thread contentions {thread_contentions} exceeds threshold {max_contentions}",
                actual_value=thread_contentions,
                expected_value=f"<= {max_contentions}",
                severity="error"
            ))
        
        # Validate deadlocks (should be zero)
        if deadlocks > 0:
            errors.append(PerformanceValidationError(
                metric_name="deadlocks",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="deadlocks_detected",
                error_message=f"Deadlocks detected: {deadlocks} occurrences",
                actual_value=deadlocks,
                expected_value=0,
                severity="error"
            ))
        
        # Validate race conditions (should be zero)
        if race_conditions > 0:
            errors.append(PerformanceValidationError(
                metric_name="race_conditions",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="race_conditions_detected",
                error_message=f"Race conditions detected: {race_conditions} occurrences",
                actual_value=race_conditions,
                expected_value=0,
                severity="error"
            ))
        
        # Validate lock metrics if provided
        if lock_metrics:
            lock_wait_time = lock_metrics.get("avg_wait_time_ms", 0)
            lock_holders = lock_metrics.get("active_locks", 0)
            lock_contentions = lock_metrics.get("contention_rate", 0)
            
            # Check lock wait time
            max_lock_wait_time = rule.criteria.get("max_lock_wait_time_ms", 10)
            if lock_wait_time > max_lock_wait_time:
                errors.append(PerformanceValidationError(
                    metric_name="lock_wait_time",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_lock_wait_time",
                    error_message=f"Average lock wait time {lock_wait_time:.2f}ms exceeds threshold {max_lock_wait_time}ms",
                    actual_value=lock_wait_time,
                    expected_value=f"<= {max_lock_wait_time}ms",
                    severity="warning"
                ))
            
            # Check number of active locks
            max_active_locks = rule.criteria.get("max_active_locks", 50)
            if lock_holders > max_active_locks:
                errors.append(PerformanceValidationError(
                    metric_name="active_locks",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="excessive_active_locks",
                    error_message=f"Active locks {lock_holders} exceeds threshold {max_active_locks}",
                    actual_value=lock_holders,
                    expected_value=f"<= {max_active_locks}",
                    severity="warning"
                ))
            
            # Check lock contention rate
            max_contention_rate = rule.criteria.get("max_lock_contention_rate", 0.1)  # 10%
            if lock_contentions > max_contention_rate:
                errors.append(PerformanceValidationError(
                    metric_name="lock_contention_rate",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="high_lock_contention_rate",
                    error_message=f"Lock contention rate {lock_contentions:.2f} exceeds threshold {max_contention_rate}",
                    actual_value=lock_contentions,
                    expected_value=f"<= {max_contention_rate}",
                    severity="warning"
                ))
        
        # Validate thread pool metrics if provided
        if thread_pool_metrics:
            pool_size = thread_pool_metrics.get("pool_size", 0)
            active_threads = thread_pool_metrics.get("active_threads", 0)
            queue_size = thread_pool_metrics.get("queue_size", 0)
            rejected_tasks = thread_pool_metrics.get("rejected_tasks", 0)
            
            # Check thread pool utilization
            if pool_size > 0:
                utilization = (active_threads / pool_size) * 100
                max_pool_utilization = rule.criteria.get("max_thread_pool_utilization", 80)  # percentage
                
                if utilization > max_pool_utilization:
                    errors.append(PerformanceValidationError(
                        metric_name="thread_pool_utilization",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_thread_pool_utilization",
                        error_message=f"Thread pool utilization {utilization:.2f}% exceeds threshold {max_pool_utilization}%",
                        actual_value=utilization,
                        expected_value=f"<= {max_pool_utilization}%",
                        severity="warning"
                    ))
            
            # Check queue size
            max_queue_size = rule.criteria.get("max_thread_pool_queue_size", 100)
            if queue_size > max_queue_size:
                errors.append(PerformanceValidationError(
                    metric_name="thread_pool_queue_size",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="large_thread_pool_queue",
                    error_message=f"Thread pool queue size {queue_size} exceeds threshold {max_queue_size}",
                    actual_value=queue_size,
                    expected_value=f"<= {max_queue_size}",
                    severity="warning"
                ))
            
            # Check rejected tasks (should be zero or minimal)
            max_rejected_tasks = rule.criteria.get("max_rejected_tasks", 5)
            if rejected_tasks > max_rejected_tasks:
                errors.append(PerformanceValidationError(
                    metric_name="rejected_tasks",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="excessive_rejected_tasks",
                    error_message=f"Rejected tasks {rejected_tasks} exceeds threshold {max_rejected_tasks}",
                    actual_value=rejected_tasks,
                    expected_value=f"<= {max_rejected_tasks}",
                    severity="error"
                ))
        
        # Check for thread safety violations history if provided
        violations_history = thread_metrics.get("violations_history", [])
        if violations_history:
            # Count recent violations
            recent_violations = [v for v in violations_history 
                               if self._is_recent_violation(v, hours=24)]
            
            max_violations_per_day = rule.criteria.get("max_violations_per_day", 5)
            if len(recent_violations) > max_violations_per_day:
                errors.append(PerformanceValidationError(
                    metric_name="thread_safety_violations",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="excessive_thread_safety_violations",
                    error_message=f"Thread safety violations in last 24 hours: {len(recent_violations)} (threshold: {max_violations_per_day})",
                    actual_value=len(recent_violations),
                    expected_value=f"<= {max_violations_per_day}",
                    severity="error"
                ))
            
            # Check violation types
            violation_types = {}
            for violation in recent_violations:
                vtype = violation.get("type", "unknown")
                violation_types[vtype] = violation_types.get(vtype, 0) + 1
            
            critical_types = ["deadlock", "race_condition", "data_corruption"]
            for vtype in critical_types:
                if vtype in violation_types:
                    errors.append(PerformanceValidationError(
                        metric_name=f"critical_violation_{vtype}",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="critical_thread_safety_violation",
                        error_message=f"Critical thread safety violation detected: {vtype} ({violation_types[vtype]} occurrences)",
                        actual_value=violation_types[vtype],
                        expected_value=0,
                        severity="error"
                    ))
        
        # Validate thread safety testing coverage if provided
        testing_metrics = thread_metrics.get("testing", {})
        if testing_metrics:
            coverage_percentage = testing_metrics.get("coverage_percentage", 0)
            concurrent_tests = testing_metrics.get("concurrent_tests", 0)
            
            # Check test coverage
            min_coverage = rule.criteria.get("min_thread_safety_coverage", 80)  # percentage
            if coverage_percentage < min_coverage:
                errors.append(PerformanceValidationError(
                    metric_name="thread_safety_test_coverage",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_thread_safety_coverage",
                    error_message=f"Thread safety test coverage {coverage_percentage:.2f}% below minimum {min_coverage}%",
                    actual_value=coverage_percentage,
                    expected_value=f">= {min_coverage}%",
                    severity="warning"
                ))
            
            # Check concurrent test count
            min_concurrent_tests = rule.criteria.get("min_concurrent_tests", 10)
            if concurrent_tests < min_concurrent_tests:
                errors.append(PerformanceValidationError(
                    metric_name="concurrent_thread_tests",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_concurrent_tests",
                    error_message=f"Concurrent thread tests {concurrent_tests} below minimum {min_concurrent_tests}",
                    actual_value=concurrent_tests,
                    expected_value=f">= {min_concurrent_tests}",
                    severity="warning"
                ))
        
        return errors
    
    def _is_recent_violation(self, violation: Dict[str, Any], hours: int = 24) -> bool:
        """Helper method to check if a violation is recent"""
        try:
            from datetime import datetime, timedelta
            violation_time = violation.get("timestamp")
            if isinstance(violation_time, str):
                violation_time = datetime.fromisoformat(violation_time.replace('Z', '+00:00'))
            elif isinstance(violation_time, (int, float)):
                violation_time = datetime.fromtimestamp(violation_time)
            else:
                return False
            
            return datetime.now(violation_time.tzinfo) - violation_time < timedelta(hours=hours)
        except (ValueError, TypeError, AttributeError):
            return False
    
    async def _validate_deadlock_prevention(
        self, 
        metrics: Dict[str, Any], 
        rule: PerformanceValidationRule
    ) -> List[PerformanceValidationError]:
        """Validate deadlock prevention"""
        errors = []
        
        # Check if metrics are provided
        if not metrics:
            errors.append(PerformanceValidationError(
                metric_name="deadlock_prevention",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_metrics_provided",
                error_message="No metrics provided for deadlock prevention validation",
                actual_value=None,
                expected_value="metrics dictionary",
                severity="error"
            ))
            return errors
        
        # Get deadlock prevention metrics
        deadlock_metrics = metrics.get("deadlock_prevention", {})
        deadlock_detection = deadlock_metrics.get("detection", {})
        prevention_mechanisms = deadlock_metrics.get("prevention_mechanisms", {})
        lock_ordering = deadlock_metrics.get("lock_ordering", {})
        timeout_config = deadlock_metrics.get("timeouts", {})
        monitoring = deadlock_metrics.get("monitoring", {})
        
        # Validate deadlock detection configuration
        if deadlock_detection:
            detection_enabled = deadlock_detection.get("enabled", False)
            detection_interval = deadlock_detection.get("interval_seconds", 0)
            
            if not detection_enabled:
                errors.append(PerformanceValidationError(
                    metric_name="deadlock_detection_enabled",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="deadlock_detection_disabled",
                    error_message="Deadlock detection is disabled",
                    actual_value=detection_enabled,
                    expected_value=True,
                    severity="warning"
                ))
            
            if detection_enabled and detection_interval == 0:
                errors.append(PerformanceValidationError(
                    metric_name="deadlock_detection_interval",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_detection_interval",
                    error_message="Deadlock detection interval not configured",
                    actual_value=detection_interval,
                    expected_value="> 0",
                    severity="error"
                ))
            
            # Check detection interval is reasonable
            max_detection_interval = rule.criteria.get("max_deadlock_detection_interval", 60)  # seconds
            if detection_interval > max_detection_interval:
                errors.append(PerformanceValidationError(
                    metric_name="deadlock_detection_interval",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="excessive_detection_interval",
                    error_message=f"Deadlock detection interval {detection_interval}s exceeds threshold {max_detection_interval}s",
                    actual_value=detection_interval,
                    expected_value=f"<= {max_detection_interval}s",
                    severity="warning"
                ))
        
        # Validate prevention mechanisms
        if prevention_mechanisms:
            mechanisms_enabled = prevention_mechanisms.get("enabled_mechanisms", [])
            required_mechanisms = rule.criteria.get("required_prevention_mechanisms", ["lock_timeout", "lock_ordering"])
            
            missing_mechanisms = [m for m in required_mechanisms if m not in mechanisms_enabled]
            if missing_mechanisms:
                errors.append(PerformanceValidationError(
                    metric_name="prevention_mechanisms",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_prevention_mechanisms",
                    error_message=f"Missing required deadlock prevention mechanisms: {', '.join(missing_mechanisms)}",
                    actual_value=mechanisms_enabled,
                    expected_value=required_mechanisms,
                    severity="error"
                ))
            
            # Check if sufficient mechanisms are enabled
            min_mechanisms = rule.criteria.get("min_prevention_mechanisms", 2)
            if len(mechanisms_enabled) < min_mechanisms:
                errors.append(PerformanceValidationError(
                    metric_name="prevention_mechanisms_count",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_prevention_mechanisms",
                    error_message=f"Insufficient deadlock prevention mechanisms: {len(mechanisms_enabled)} (minimum: {min_mechanisms})",
                    actual_value=len(mechanisms_enabled),
                    expected_value=f">= {min_mechanisms}",
                    severity="warning"
                ))
        
        # Validate lock ordering configuration
        if lock_ordering:
            ordering_enabled = lock_ordering.get("enabled", False)
            lock_hierarchy = lock_ordering.get("hierarchy", {})
            
            if not ordering_enabled:
                errors.append(PerformanceValidationError(
                    metric_name="lock_ordering_enabled",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="lock_ordering_disabled",
                    error_message="Lock ordering is disabled (important for deadlock prevention)",
                    actual_value=ordering_enabled,
                    expected_value=True,
                    severity="warning"
                ))
            
            if ordering_enabled and not lock_hierarchy:
                errors.append(PerformanceValidationError(
                    metric_name="lock_hierarchy",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_lock_hierarchy",
                    error_message="Lock ordering enabled but no lock hierarchy defined",
                    actual_value=lock_hierarchy,
                    expected_value="non-empty hierarchy",
                    severity="error"
                ))
            
            # Check for circular dependencies in lock hierarchy
            if lock_hierarchy:
                has_circular_deps = self._check_circular_dependencies(lock_hierarchy)
                if has_circular_deps:
                    errors.append(PerformanceValidationError(
                        metric_name="lock_hierarchy_circular_deps",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="circular_lock_dependencies",
                        error_message="Circular dependencies detected in lock hierarchy",
                        actual_value="circular dependencies present",
                        expected_value="no circular dependencies",
                        severity="error"
                    ))
        
        # Validate timeout configuration
        if timeout_config:
            lock_timeout = timeout_config.get("lock_timeout_ms", 0)
            transaction_timeout = timeout_config.get("transaction_timeout_ms", 0)
            
            # Check lock timeout
            if lock_timeout == 0:
                errors.append(PerformanceValidationError(
                    metric_name="lock_timeout",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="no_lock_timeout",
                    error_message="Lock timeout not configured (essential for deadlock prevention)",
                    actual_value=lock_timeout,
                    expected_value="> 0",
                    severity="error"
                ))
            else:
                max_lock_timeout = rule.criteria.get("max_lock_timeout_ms", 30000)  # 30 seconds
                if lock_timeout > max_lock_timeout:
                    errors.append(PerformanceValidationError(
                        metric_name="lock_timeout",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="excessive_lock_timeout",
                        error_message=f"Lock timeout {lock_timeout}ms exceeds threshold {max_lock_timeout}ms",
                        actual_value=lock_timeout,
                        expected_value=f"<= {max_lock_timeout}ms",
                        severity="warning"
                    ))
            
            # Check transaction timeout
            if transaction_timeout == 0:
                errors.append(PerformanceValidationError(
                    metric_name="transaction_timeout",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="no_transaction_timeout",
                    error_message="Transaction timeout not configured",
                    actual_value=transaction_timeout,
                    expected_value="> 0",
                    severity="warning"
                ))
            
            # Check timeout relationship
            if lock_timeout > 0 and transaction_timeout > 0:
                if transaction_timeout <= lock_timeout:
                    errors.append(PerformanceValidationError(
                        metric_name="timeout_relationship",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="invalid_timeout_relationship",
                        error_message=f"Transaction timeout ({transaction_timeout}ms) should be greater than lock timeout ({lock_timeout}ms)",
                        actual_value=f"transaction: {transaction_timeout}ms, lock: {lock_timeout}ms",
                        expected_value="transaction_timeout > lock_timeout",
                        severity="error"
                    ))
        
        # Validate monitoring configuration
        if monitoring:
            monitoring_enabled = monitoring.get("enabled", False)
            alert_threshold = monitoring.get("deadlock_alert_threshold", 0)
            monitoring_interval = monitoring.get("monitoring_interval_seconds", 0)
            
            if not monitoring_enabled:
                errors.append(PerformanceValidationError(
                    metric_name="deadlock_monitoring_enabled",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="deadlock_monitoring_disabled",
                    error_message="Deadlock monitoring is disabled",
                    actual_value=monitoring_enabled,
                    expected_value=True,
                    severity="warning"
                ))
            
            if monitoring_enabled and alert_threshold == 0:
                errors.append(PerformanceValidationError(
                    metric_name="deadlock_alert_threshold",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="no_alert_threshold",
                    error_message="Deadlock alert threshold not configured",
                    actual_value=alert_threshold,
                    expected_value="> 0",
                    severity="warning"
                ))
            
            if monitoring_enabled and monitoring_interval == 0:
                errors.append(PerformanceValidationError(
                    metric_name="deadlock_monitoring_interval",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="no_monitoring_interval",
                    error_message="Deadlock monitoring interval not configured",
                    actual_value=monitoring_interval,
                    expected_value="> 0",
                    severity="warning"
                ))
        
        # Check for recent deadlocks if history is provided
        deadlock_history = deadlock_metrics.get("deadlock_history", [])
        if deadlock_history:
            recent_deadlocks = [d for d in deadlock_history 
                              if self._is_recent_deadlock(d, hours=24)]
            
            max_deadlocks_per_day = rule.criteria.get("max_deadlocks_per_day", 0)  # Should be zero
            if len(recent_deadlocks) > max_deadlocks_per_day:
                errors.append(PerformanceValidationError(
                    metric_name="recent_deadlocks",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="recent_deadlocks_detected",
                    error_message=f"Deadlocks detected in last 24 hours: {len(recent_deadlocks)} (should be zero)",
                    actual_value=len(recent_deadlocks),
                    expected_value=0,
                    severity="error"
                ))
        
        # Validate deadlock testing if provided
        testing_metrics = deadlock_metrics.get("testing", {})
        if testing_metrics:
            deadlock_tests = testing_metrics.get("deadlock_tests", 0)
            concurrency_tests = testing_metrics.get("concurrency_tests", 0)
            
            # Check deadlock test coverage
            min_deadlock_tests = rule.criteria.get("min_deadlock_tests", 5)
            if deadlock_tests < min_deadlock_tests:
                errors.append(PerformanceValidationError(
                    metric_name="deadlock_test_coverage",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_deadlock_tests",
                    error_message=f"Deadlock tests {deadlock_tests} below minimum {min_deadlock_tests}",
                    actual_value=deadlock_tests,
                    expected_value=f">= {min_deadlock_tests}",
                    severity="warning"
                ))
            
            # Check concurrency test coverage
            min_concurrency_tests = rule.criteria.get("min_concurrency_tests", 10)
            if concurrency_tests < min_concurrency_tests:
                errors.append(PerformanceValidationError(
                    metric_name="concurrency_test_coverage",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_concurrency_tests",
                    error_message=f"Concurrency tests {concurrency_tests} below minimum {min_concurrency_tests}",
                    actual_value=concurrency_tests,
                    expected_value=f">= {min_concurrency_tests}",
                    severity="warning"
                ))
        
        return errors
    
    def _check_circular_dependencies(self, lock_hierarchy: Dict[str, Any]) -> bool:
        """Helper method to check for circular dependencies in lock hierarchy"""
        try:
            visited = set()
            recursion_stack = set()
            
            def has_cycle(lock_name: str) -> bool:
                if lock_name in recursion_stack:
                    return True
                if lock_name in visited:
                    return False
                
                visited.add(lock_name)
                recursion_stack.add(lock_name)
                
                dependencies = lock_hierarchy.get(lock_name, [])
                for dep in dependencies:
                    if has_cycle(dep):
                        return True
                
                recursion_stack.remove(lock_name)
                return False
            
            for lock_name in lock_hierarchy:
                if has_cycle(lock_name):
                    return True
            
            return False
        except (TypeError, AttributeError):
            return True  # Assume circular dependency if structure is invalid
    
    def _is_recent_deadlock(self, deadlock: Dict[str, Any], hours: int = 24) -> bool:
        """Helper method to check if a deadlock is recent"""
        try:
            from datetime import datetime, timedelta
            deadlock_time = deadlock.get("timestamp")
            if isinstance(deadlock_time, str):
                deadlock_time = datetime.fromisoformat(deadlock_time.replace('Z', '+00:00'))
            elif isinstance(deadlock_time, (int, float)):
                deadlock_time = datetime.fromtimestamp(deadlock_time)
            else:
                return False
            
            return datetime.now(deadlock_time.tzinfo) - deadlock_time < timedelta(hours=hours)
        except (ValueError, TypeError, AttributeError):
            return False
    
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
