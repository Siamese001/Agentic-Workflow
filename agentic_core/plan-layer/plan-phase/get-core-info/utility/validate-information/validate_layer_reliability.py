"""
L1 Cognitive Planning - Layer Reliability Validation

Implements pure planning operations for validating layer reliability
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

class ReliabilityValidationType(str, Enum):
    """Supported reliability validation types with L5 safety validation"""
    AVAILABILITY = "availability"
    ERROR_RATE = "error_rate"
    FAULT_TOLERANCE = "fault_tolerance"
    RECOVERY_TIME = "recovery_time"
    CONSISTENCY = "consistency"
    DURABILITY = "durability"


class ReliabilitySeverity(str, Enum):
    """Reliability validation severity levels with L5 safety enforcement"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LayerReliabilitySafetyPolicy(BaseModel):
    """L5 Safety policy for layer reliability validation operations"""
    max_reliability_rules: int = Field(default=50, description="Maximum reliability rules")
    max_validation_metrics: int = Field(default=100, description="Maximum validation metrics")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in ReliabilityValidationType])
    allowed_severities: List[str] = Field(default_factory=lambda: [t.value for t in ReliabilitySeverity])
    require_reliability_validation: bool = Field(default=True)
    prevent_reliability_degradation: bool = Field(default=True)
    sanitize_reliability_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerReliabilitySafetyValidator:
    """L5 Safety validator for layer reliability validation operations"""
    
    def __init__(self, policy: LayerReliabilitySafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerReliabilitySafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._reliability_patterns = [
            r"uptime", r"downtime", r"sla", r"slo",
            r"failure", r"recovery", r"backup", r"redundancy"
        ]
    
    def validate_reliability_input(self, reliability_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates reliability input against L5 safety policies"""
        try:
            # Check reliability rules count
            reliability_rules = reliability_input.get("reliability_rules", [])
            if len(reliability_rules) > self.policy.max_reliability_rules:
                error_msg = f"Too many reliability rules: {len(reliability_rules)} > {self.policy.max_reliability_rules}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation types
            for rule in reliability_rules:
                rule_type = rule.get("type", "")
                if rule_type not in self.policy.allowed_validation_types:
                    error_msg = f"Prohibited validation type: {rule_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check metrics count
            reliability_metrics = reliability_input.get("reliability_metrics", {})
            metric_count = len(reliability_metrics)
            if metric_count > self.policy.max_validation_metrics:
                error_msg = f"Too many reliability metrics: {metric_count} > {self.policy.max_validation_metrics}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(reliability_input).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for reliability patterns (additional validation)
            for pattern in self._reliability_patterns:
                if pattern in content_str:
                    self.logger.warning(f"Reliability pattern detected: {pattern}")
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
class ReliabilityValidationRule:
    """Individual reliability validation rule specification"""
    id: str
    validation_type: ReliabilityValidationType
    severity: ReliabilitySeverity
    criteria: Dict[str, Any]
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class LayerReliabilityValidationRequest:
    """Input request for layer reliability validation operations"""
    layer_name: str
    layer_spec: Dict[str, Any]
    reliability_metrics: Dict[str, Any]
    reliability_rules: List[Dict[str, Any]]
    validation_options: Dict[str, Any]
    context: Dict[str, Any]
    reliability_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class ReliabilityValidationError:
    """Individual reliability validation error"""
    layer_id: str
    rule_id: str
    validation_type: ReliabilityValidationType
    error_category: str
    error_message: str
    actual_value: Any
    expected_value: Any
    severity: ReliabilitySeverity
    reliability_impact: str


@dataclass
class ReliabilityValidationResult:
    """Result of layer reliability validation"""
    is_reliable: bool
    reliability_score: float
    validation_errors: List[ReliabilityValidationError]
    validation_warnings: List[ReliabilityValidationError]
    reliability_summary: Dict[str, Any]
    reliability_recommendations: List[str]
    reliability_flags: List[str]


@dataclass
class LayerReliabilityValidationResult:
    """Output result from layer reliability validation operations"""
    validation_result: ReliabilityValidationResult
    validated_layer: Dict[str, Any]
    validation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    reliability_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerReliabilityValidatorInterface(ABC):
    """Abstract interface for layer reliability validation operations"""
    
    @abstractmethod
    async def validate_reliability(self, request: LayerReliabilityValidationRequest) -> LayerReliabilityValidationResult:
        """Validate layer reliability against rules and criteria"""
        pass
    
    @abstractmethod
    async def check_availability_reliability(self, metrics: Dict[str, Any]) -> List[ReliabilityValidationError]:
        """Check availability reliability metrics"""
        pass
    
    @abstractmethod
    async def check_error_rate_reliability(self, metrics: Dict[str, Any]) -> List[ReliabilityValidationError]:
        """Check error rate reliability metrics"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerReliabilityValidator(LayerReliabilityValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating layer reliability.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerReliabilitySafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerReliabilitySafetyPolicy()
        self.safety_validator = LayerReliabilitySafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Reliability validation patterns and rules
        self._validation_patterns = {
            ReliabilityValidationType.AVAILABILITY: {
                "uptime_threshold": self._validate_uptime_threshold,
                "availability_sla": self._validate_availability_sla,
                "downtime_limits": self._validate_downtime_limits
            },
            ReliabilityValidationType.ERROR_RATE: {
                "error_rate_threshold": self._validate_error_rate_threshold,
                "error_distribution": self._validate_error_distribution,
                "error_trends": self._validate_error_trends
            },
            ReliabilityValidationType.FAULT_TOLERANCE: {
                "redundancy_configured": self._validate_redundancy_configured,
                "failover_mechanisms": self._validate_failover_mechanisms,
                "circuit_breakers": self._validate_circuit_breakers
            },
            ReliabilityValidationType.RECOVERY_TIME: {
                "mttr_threshold": self._validate_mttr_threshold,
                "recovery_procedures": self._validate_recovery_procedures,
                "backup_restoration": self._validate_backup_restoration
            },
            ReliabilityValidationType.CONSISTENCY: {
                "data_consistency": self._validate_data_consistency,
                "state_consistency": self._validate_state_consistency,
                "transaction_integrity": self._validate_transaction_integrity
            },
            ReliabilityValidationType.DURABILITY: {
                "data_persistence": self._validate_data_persistence,
                "backup_frequency": self._validate_backup_frequency,
                "data_replication": self._validate_data_replication
            }
        }
        
        self.logger.info("LayerReliabilityValidator initialized with L5 safety policies")
    
    async def validate_reliability(self, request: LayerReliabilityValidationRequest) -> LayerReliabilityValidationResult:
        """
        Validate layer reliability against rules and criteria.
        
        Args:
            request: Layer reliability validation request with layer specification and reliability metrics
            
        Returns:
            LayerReliabilityValidationResult: Structured result with reliability validation outcome and details
            
        Raises:
            ValidationError: If reliability validation fails
            SafetyError: If reliability validation violates safety policies
        """
        self.logger.info(f"Validating reliability for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            reliability_input = {
                "reliability_rules": request.reliability_rules,
                "reliability_metrics": request.reliability_metrics
            }
            
            is_valid, error_msg = self.safety_validator.validate_reliability_input(reliability_input)
            if not is_valid:
                raise SafetyError(f"Reliability safety validation failed: {error_msg}")
            
            # Sanitize reliability data if required
            sanitized_metrics = request.reliability_metrics
            if self.safety_policy.sanitize_reliability_data:
                sanitized_metrics = await self._sanitize_reliability_data(request.reliability_metrics)
            
            # Parse reliability rules
            parsed_rules = await self._parse_reliability_rules(request.reliability_rules)
            
            # Execute reliability validation rules
            validation_errors = []
            for rule in parsed_rules:
                rule_errors = await self._execute_reliability_rule(sanitized_metrics, rule)
                validation_errors.extend(rule_errors)
            
            # Check availability reliability
            availability_errors = await self.check_availability_reliability(sanitized_metrics)
            validation_errors.extend(availability_errors)
            
            # Check error rate reliability
            error_rate_errors = await self.check_error_rate_reliability(sanitized_metrics)
            validation_errors.extend(error_rate_errors)
            
            # Separate errors and warnings based on severity
            error_list = [e for e in validation_errors if e.severity in [ReliabilitySeverity.CRITICAL, ReliabilitySeverity.HIGH]]
            warning_list = [e for e in validation_errors if e.severity in [ReliabilitySeverity.MEDIUM, ReliabilitySeverity.LOW]]
            
            # Determine overall reliability
            is_reliable = len(error_list) == 0
            
            # Calculate reliability score
            reliability_score = self._calculate_reliability_score(validation_errors)
            
            # Generate reliability summary
            reliability_summary = await self._generate_reliability_summary(
                request.layer_name,
                sanitized_metrics,
                validation_errors
            )
            
            # Generate reliability recommendations
            reliability_recommendations = await self._generate_reliability_recommendations(validation_errors)
            
            # Extract reliability flags
            reliability_flags = self._extract_reliability_flags(validation_errors)
            
            # Create validation result
            validation_result = ReliabilityValidationResult(
                is_reliable=is_reliable,
                reliability_score=reliability_score,
                validation_errors=error_list,
                validation_warnings=warning_list,
                reliability_summary=reliability_summary,
                reliability_recommendations=reliability_recommendations,
                reliability_flags=reliability_flags
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_reliability_risk_score(validation_result),
                "reliability_flags": reliability_flags
            }
            
            # Generate unique reliability ID
            reliability_id = self._generate_reliability_id(request, validation_result)
            
            result = LayerReliabilityValidationResult(
                validation_result=validation_result,
                validated_layer=request.layer_spec,
                validation_metadata={
                    "layer_name": request.layer_name,
                    "rules_applied": len(parsed_rules),
                    "metrics_validated": len(sanitized_metrics),
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                reliability_id=reliability_id
            )
            
            self.logger.info(f"Successfully validated reliability for {request.layer_name} with score {reliability_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate layer reliability: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def check_availability_reliability(self, metrics: Dict[str, Any]) -> List[ReliabilityValidationError]:
        """Check availability reliability metrics"""
        errors = []
        
        try:
            # Check uptime percentage
            uptime_percent = metrics.get("uptime_percent", 0)
            min_uptime_percent = metrics.get("min_uptime_percent", 99.9)  # Default 99.9%
            
            if uptime_percent < min_uptime_percent:
                error = ReliabilityValidationError(
                    layer_id="reliability_check",
                    rule_id="availability_validation",
                    validation_type=ReliabilityValidationType.AVAILABILITY,
                    error_category="low_uptime",
                    error_message=f"Uptime {uptime_percent}% below minimum {min_uptime_percent}%",
                    actual_value=uptime_percent,
                    expected_value=f">={min_uptime_percent}%",
                    severity=ReliabilitySeverity.HIGH,
                    reliability_impact="service_availability"
                )
                errors.append(error)
            
            # Check downtime incidents
            downtime_incidents = metrics.get("downtime_incidents", 0)
            max_downtime_incidents = metrics.get("max_downtime_incidents", 5)  # Default 5 incidents
            
            if downtime_incidents > max_downtime_incidents:
                error = ReliabilityValidationError(
                    layer_id="reliability_check",
                    rule_id="availability_validation",
                    validation_type=ReliabilityValidationType.AVAILABILITY,
                    error_category="excessive_downtime_incidents",
                    error_message=f"Too many downtime incidents: {downtime_incidents}",
                    actual_value=downtime_incidents,
                    expected_value=f"<={max_downtime_incidents}",
                    severity=ReliabilitySeverity.MEDIUM,
                    reliability_impact="service_stability"
                )
                errors.append(error)
            
            # Check availability SLA compliance
            sla_target = metrics.get("availability_sla_target", 99.9)
            actual_availability = metrics.get("actual_availability", 0)
            
            if actual_availability < sla_target:
                error = ReliabilityValidationError(
                    layer_id="reliability_check",
                    rule_id="availability_validation",
                    validation_type=ReliabilityValidationType.AVAILABILITY,
                    error_category="sla_non_compliance",
                    error_message=f"Availability {actual_availability}% below SLA target {sla_target}%",
                    actual_value=actual_availability,
                    expected_value=f">={sla_target}%",
                    severity=ReliabilitySeverity.CRITICAL,
                    reliability_impact="sla_compliance"
                )
                errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Availability reliability check failed: {str(e)}")
            error = ReliabilityValidationError(
                layer_id="reliability_check",
                rule_id="availability_error",
                validation_type=ReliabilityValidationType.AVAILABILITY,
                error_category="validation_error",
                error_message=f"Availability validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=ReliabilitySeverity.HIGH,
                reliability_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def check_error_rate_reliability(self, metrics: Dict[str, Any]) -> List[ReliabilityValidationError]:
        """Check error rate reliability metrics"""
        errors = []
        
        try:
            # Check error rate percentage
            error_rate_percent = metrics.get("error_rate_percent", 0)
            max_error_rate_percent = metrics.get("max_error_rate_percent", 1.0)  # Default 1%
            
            if error_rate_percent > max_error_rate_percent:
                error = ReliabilityValidationError(
                    layer_id="reliability_check",
                    rule_id="error_rate_validation",
                    validation_type=ReliabilityValidationType.ERROR_RATE,
                    error_category="high_error_rate",
                    error_message=f"Error rate {error_rate_percent}% above maximum {max_error_rate_percent}%",
                    actual_value=error_rate_percent,
                    expected_value=f"<={max_error_rate_percent}%",
                    severity=ReliabilitySeverity.HIGH,
                    reliability_impact="service_quality"
                )
                errors.append(error)
            
            # Check critical errors
            critical_errors = metrics.get("critical_errors", 0)
            max_critical_errors = metrics.get("max_critical_errors", 0)  # Default 0 critical errors
            
            if critical_errors > max_critical_errors:
                error = ReliabilityValidationError(
                    layer_id="reliability_check",
                    rule_id="error_rate_validation",
                    validation_type=ReliabilityValidationType.ERROR_RATE,
                    error_category="critical_errors_present",
                    error_message=f"Critical errors detected: {critical_errors}",
                    actual_value=critical_errors,
                    expected_value=f"<={max_critical_errors}",
                    severity=ReliabilitySeverity.CRITICAL,
                    reliability_impact="service_stability"
                )
                errors.append(error)
            
            # Check error trends
            error_trend = metrics.get("error_trend", "stable")
            if error_trend == "increasing":
                error = ReliabilityValidationError(
                    layer_id="reliability_check",
                    rule_id="error_rate_validation",
                    validation_type=ReliabilityValidationType.ERROR_RATE,
                    error_category="increasing_error_trend",
                    error_message="Error rate is trending upward",
                    actual_value=error_trend,
                    expected_value="stable or decreasing",
                    severity=ReliabilitySeverity.MEDIUM,
                    reliability_impact="service_degradation"
                )
                errors.append(error)
            
            # Check timeout errors
            timeout_errors = metrics.get("timeout_errors", 0)
            max_timeout_errors = metrics.get("max_timeout_errors", 10)  # Default 10 timeout errors
            
            if timeout_errors > max_timeout_errors:
                error = ReliabilityValidationError(
                    layer_id="reliability_check",
                    rule_id="error_rate_validation",
                    validation_type=ReliabilityValidationType.ERROR_RATE,
                    error_category="excessive_timeout_errors",
                    error_message=f"Too many timeout errors: {timeout_errors}",
                    actual_value=timeout_errors,
                    expected_value=f"<={max_timeout_errors}",
                    severity=ReliabilitySeverity.MEDIUM,
                    reliability_impact="performance"
                )
                errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Error rate reliability check failed: {str(e)}")
            error = ReliabilityValidationError(
                layer_id="reliability_check",
                rule_id="error_rate_error",
                validation_type=ReliabilityValidationType.ERROR_RATE,
                error_category="validation_error",
                error_message=f"Error rate validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=ReliabilitySeverity.HIGH,
                reliability_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def _parse_reliability_rules(self, raw_rules: List[Dict[str, Any]]) -> List[ReliabilityValidationRule]:
        """Parse raw reliability rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = ReliabilityValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    validation_type=ReliabilityValidationType(raw_rule.get("validation_type", "availability")),
                    severity=ReliabilitySeverity(raw_rule.get("severity", "medium")),
                    criteria=raw_rule.get("criteria", {}),
                    error_message=raw_rule.get("error_message", "Reliability validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse reliability rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = ReliabilityValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    validation_type=ReliabilityValidationType.AVAILABILITY,
                    severity=ReliabilitySeverity.MEDIUM,
                    criteria={},
                    error_message=f"Parsing failed: {str(e)}",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _execute_reliability_rule(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Execute individual reliability validation rule"""
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
                error = ReliabilityValidationError(
                    layer_id="reliability_check",
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="unknown_validation",
                    error_message=f"Unknown validation function: {rule.criteria.get('validation_function')}",
                    actual_value=None,
                    expected_value=None,
                    severity=ReliabilitySeverity.MEDIUM,
                    reliability_impact="validation"
                )
                errors.append(error)
                
        except Exception as e:
            self.logger.error(f"Failed to execute reliability rule {rule.id}: {str(e)}")
            error = ReliabilityValidationError(
                layer_id="reliability_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="rule_execution_error",
                error_message=f"Rule execution failed: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=ReliabilitySeverity.HIGH,
                reliability_impact="validation"
            )
            errors.append(error)
        
        return errors
    
    async def _sanitize_reliability_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize reliability data for safety"""
        sanitized = metrics.copy()
        
        # Remove dangerous content from string fields
        for key, value in sanitized.items():
            if isinstance(value, str):
                # Remove script tags and dangerous content
                sanitized_value = value.replace("<script", "").replace("</script>", "")
                sanitized[key] = sanitized_value
            elif isinstance(value, dict):
                sanitized[key] = await self._sanitize_reliability_data(value)
            elif isinstance(value, list):
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        sanitized_item = item.replace("<script", "").replace("</script>", "")
                        sanitized_list.append(sanitized_item)
                    elif isinstance(item, dict):
                        sanitized_item = await self._sanitize_reliability_data(item)
                        sanitized_list.append(sanitized_item)
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
        
        return sanitized
    
    # Validation function implementations
    async def _validate_uptime_threshold(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate uptime threshold"""
        errors = []
        
        threshold = rule.criteria.get("threshold", 99.9)
        actual_uptime = metrics.get("uptime_percent", 0)
        
        if actual_uptime < threshold:
            error = ReliabilityValidationError(
                layer_id="reliability_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="uptime_threshold_violation",
                error_message=f"Uptime {actual_uptime}% below threshold {threshold}%",
                actual_value=actual_uptime,
                expected_value=f">={threshold}%",
                severity=rule.severity,
                reliability_impact="service_availability"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_availability_sla(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate availability SLA"""
        errors = []
        
        sla_target = rule.criteria.get("sla_target", 99.9)
        actual_availability = metrics.get("actual_availability", 0)
        
        if actual_availability < sla_target:
            error = ReliabilityValidationError(
                layer_id="reliability_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="sla_non_compliance",
                error_message=f"Availability {actual_availability}% below SLA target {sla_target}%",
                actual_value=actual_availability,
                expected_value=f">={sla_target}%",
                severity=rule.severity,
                reliability_impact="sla_compliance"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_downtime_limits(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate downtime limits"""
        # Simplified implementation
        return []
    
    async def _validate_error_rate_threshold(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate error rate threshold"""
        errors = []
        
        threshold = rule.criteria.get("threshold", 1.0)
        actual_error_rate = metrics.get("error_rate_percent", 0)
        
        if actual_error_rate > threshold:
            error = ReliabilityValidationError(
                layer_id="reliability_check",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="error_rate_threshold_exceeded",
                error_message=f"Error rate {actual_error_rate}% exceeds threshold {threshold}%",
                actual_value=actual_error_rate,
                expected_value=f"<={threshold}%",
                severity=rule.severity,
                reliability_impact="service_quality"
            )
            errors.append(error)
        
        return errors
    
    async def _validate_error_distribution(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate error distribution"""
        # Simplified implementation
        return []
    
    async def _validate_error_trends(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate error trends"""
        # Simplified implementation
        return []
    
    async def _validate_redundancy_configured(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate redundancy configured"""
        # Simplified implementation
        return []
    
    async def _validate_failover_mechanisms(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate failover mechanisms"""
        # Simplified implementation
        return []
    
    async def _validate_circuit_breakers(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate circuit breakers"""
        # Simplified implementation
        return []
    
    async def _validate_mttr_threshold(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate MTTR threshold"""
        # Simplified implementation
        return []
    
    async def _validate_recovery_procedures(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate recovery procedures"""
        # Simplified implementation
        return []
    
    async def _validate_backup_restoration(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate backup restoration"""
        # Simplified implementation
        return []
    
    async def _validate_data_consistency(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate data consistency"""
        # Simplified implementation
        return []
    
    async def _validate_state_consistency(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate state consistency"""
        # Simplified implementation
        return []
    
    async def _validate_transaction_integrity(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate transaction integrity"""
        # Simplified implementation
        return []
    
    async def _validate_data_persistence(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate data persistence"""
        # Simplified implementation
        return []
    
    async def _validate_backup_frequency(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate backup frequency"""
        # Simplified implementation
        return []
    
    async def _validate_data_replication(
        self, 
        metrics: Dict[str, Any], 
        rule: ReliabilityValidationRule
    ) -> List[ReliabilityValidationError]:
        """Validate data replication"""
        # Simplified implementation
        return []
    
    def _calculate_reliability_score(self, errors: List[ReliabilityValidationError]) -> float:
        """Calculate reliability score based on validation errors"""
        if not errors:
            return 1.0
        
        # Weight errors by severity
        severity_weights = {
            ReliabilitySeverity.CRITICAL: 0.0,
            ReliabilitySeverity.HIGH: 0.2,
            ReliabilitySeverity.MEDIUM: 0.5,
            ReliabilitySeverity.LOW: 0.8
        }
        
        total_weight = sum(severity_weights[error.severity] for error in errors)
        average_score = total_weight / len(errors)
        
        return round(average_score, 2)
    
    async def _generate_reliability_summary(
        self, 
        layer_name: str,
        metrics: Dict[str, Any],
        errors: List[ReliabilityValidationError]
    ) -> Dict[str, Any]:
        """Generate reliability summary"""
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
                "uptime_percent": metrics.get("uptime_percent", 0),
                "error_rate_percent": metrics.get("error_rate_percent", 0),
                "availability_sla_target": metrics.get("availability_sla_target", 0),
                "actual_availability": metrics.get("actual_availability", 0)
            }
        }
    
    async def _generate_reliability_recommendations(self, errors: List[ReliabilityValidationError]) -> List[str]:
        """Generate reliability recommendations based on errors"""
        recommendations = []
        
        error_categories = [error.error_category for error in errors]
        
        if "low_uptime" in error_categories:
            recommendations.append("Improve system monitoring and alerting")
            recommendations.append("Implement automatic failover mechanisms")
        
        if "high_error_rate" in error_categories:
            recommendations.append("Investigate root causes of errors")
            recommendations.append("Implement better error handling and retry logic")
        
        if "critical_errors_present" in error_categories:
            recommendations.append("Address critical errors immediately")
            recommendations.append("Review system architecture for single points of failure")
        
        if "increasing_error_trend" in error_categories:
            recommendations.append("Analyze error trends and implement preventive measures")
            recommendations.append("Consider load balancing and scaling strategies")
        
        if "sla_non_compliance" in error_categories:
            recommendations.append("Review and adjust SLA targets")
            recommendations.append("Implement redundancy and backup systems")
        
        if not recommendations:
            recommendations.append("Reliability metrics are within acceptable limits")
        
        return recommendations
    
    def _extract_reliability_flags(self, errors: List[ReliabilityValidationError]) -> List[str]:
        """Extract reliability flags from validation errors"""
        reliability_flags = []
        
        for error in errors:
            if error.validation_type == ReliabilityValidationType.AVAILABILITY:
                reliability_flags.append("availability_issue")
            elif error.validation_type == ReliabilityValidationType.ERROR_RATE:
                reliability_flags.append("error_rate_issue")
            elif error.validation_type == ReliabilityValidationType.FAULT_TOLERANCE:
                reliability_flags.append("fault_tolerance_issue")
            elif error.severity == ReliabilitySeverity.CRITICAL:
                reliability_flags.append("critical_reliability_issue")
        
        return reliability_flags
    
    async def _estimate_validation_complexity(self, request: LayerReliabilityValidationRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.reliability_rules) // 2
        
        # Add complexity for metrics
        complexity_score += len(request.reliability_metrics) // 5
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_reliability_risk_score(self, validation_result: ReliabilityValidationResult) -> float:
        """Calculate risk score for the reliability validation (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for reliability errors
        if validation_result.validation_errors:
            risk_score += 0.4
        
        # Increase risk for critical issues
        critical_errors = [e for e in validation_result.validation_errors if e.severity == ReliabilitySeverity.CRITICAL]
        if critical_errors:
            risk_score += 0.5
        
        # Increase risk for low reliability score
        if validation_result.reliability_score < 0.5:
            risk_score += 0.3
        
        return min(risk_score, 1.0)
    
    def _generate_reliability_id(self, request: LayerReliabilityValidationRequest, result: ReliabilityValidationResult) -> str:
        """Generate unique reliability identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.layer_name}:{result.reliability_score:.2f}:{len(result.validation_errors)}:{timestamp}"
        return f"reliability_validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: LayerReliabilityValidationRequest, error: str) -> LayerReliabilityValidationResult:
        """Create safe fallback validation when main validation fails"""
        layer_name = request.layer_spec.get("name", "unknown")
        
        fallback_error = ReliabilityValidationError(
            layer_id=layer_name,
            rule_id="fallback_rule",
            validation_type=ReliabilityValidationType.AVAILABILITY,
            error_category="validation_failed",
            error_message=f"Reliability validation failed: {error}",
            actual_value="fallback",
            expected_value="success",
            severity=ReliabilitySeverity.MEDIUM,
            reliability_impact="validation"
        )
        
        fallback_result = ReliabilityValidationResult(
            is_reliable=False,
            reliability_score=0.0,
            validation_errors=[fallback_error],
            validation_warnings=[],
            reliability_summary={"fallback": True},
            reliability_recommendations=["Fix reliability validation system"],
            reliability_flags=["fallback_mode"]
        )
        
        return LayerReliabilityValidationResult(
            validation_result=fallback_result,
            validated_layer=request.layer_spec,
            validation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            reliability_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when reliability validation violates safety policies"""
    pass


class LayerReliabilityValidationError(Exception):
    """Raised for general layer reliability validation errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_reliability_validator(safety_policy: Optional[LayerReliabilitySafetyPolicy] = None) -> LayerReliabilityValidator:
    """Factory function to create LayerReliabilityValidator with optional custom safety policy"""
    return LayerReliabilityValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_reliability_request(request: LayerReliabilityValidationRequest) -> tuple[bool, Optional[str]]:
    """Validate layer reliability request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.layer_spec, dict):
            return False, "Layer specification must be a dictionary"
        
        if not isinstance(request.reliability_metrics, dict):
            return False, "Reliability metrics must be a dictionary"
        
        if not isinstance(request.reliability_rules, list):
            return False, "Reliability rules must be a list"
        
        if not isinstance(request.validation_options, dict):
            return False, "Validation options must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
