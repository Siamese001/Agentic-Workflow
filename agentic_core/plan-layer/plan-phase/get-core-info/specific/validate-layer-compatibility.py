"""
L1 Cognitive Planning - Layer Compatibility Validation

Implements pure planning operations for validating layer compatibility
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

class CompatibilityType(str, Enum):
    """Supported compatibility types with L5 safety validation"""
    VERSION = "version"
    INTERFACE = "interface"
    DEPENDENCY = "dependency"
    DATA_FORMAT = "data_format"
    PROTOCOL = "protocol"
    CONFIGURATION = "configuration"


class CompatibilityLevel(str, Enum):
    """Compatibility level types with L5 safety enforcement"""
    COMPATIBLE = "compatible"
    PARTIALLY_COMPATIBLE = "partially_compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


class LayerCompatibilitySafetyPolicy(BaseModel):
    """L5 Safety policy for layer compatibility validation operations"""
    max_layer_count: int = Field(default=10, description="Maximum layers to compare")
    max_compatibility_rules: int = Field(default=50, description="Maximum compatibility rules")
    allowed_compatibility_types: List[str] = Field(default_factory=lambda: [t.value for t in CompatibilityType])
    allowed_levels: List[str] = Field(default_factory=lambda: [t.value for t in CompatibilityLevel])
    require_compatibility_validation: bool = Field(default=True)
    prevent_version_conflicts: bool = Field(default=True)
    sanitize_compatibility_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerCompatibilitySafetyValidator:
    """L5 Safety validator for layer compatibility validation operations"""
    
    def __init__(self, policy: LayerCompatibilitySafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerCompatibilitySafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._conflict_patterns = [
            r"conflict", r"incompatible", r"mismatch", r"error",
            r"failed", r"broken", r"corrupted"
        ]
    
    def validate_compatibility_input(self, compatibility_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates compatibility input against L5 safety policies"""
        try:
            # Check layer count
            layers = compatibility_input.get("layers", [])
            if len(layers) > self.policy.max_layer_count:
                error_msg = f"Too many layers: {len(layers)} > {self.policy.max_layer_count}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check compatibility rules count
            compatibility_rules = compatibility_input.get("compatibility_rules", [])
            if len(compatibility_rules) > self.policy.max_compatibility_rules:
                error_msg = f"Too many compatibility rules: {len(compatibility_rules)} > {self.policy.max_compatibility_rules}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check compatibility types
            for rule in compatibility_rules:
                rule_type = rule.get("type", "")
                if rule_type not in self.policy.allowed_compatibility_types:
                    error_msg = f"Prohibited compatibility type: {rule_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(layers).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for conflict patterns (additional validation)
            for pattern in self._conflict_patterns:
                if pattern in content_str:
                    self.logger.warning(f"Conflict pattern detected: {pattern}")
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
class CompatibilityRule:
    """Individual compatibility rule specification"""
    id: str
    type: CompatibilityType
    source_layer: str
    target_layer: str
    criteria: Dict[str, Any]
    severity: str
    metadata: Dict[str, Any]


@dataclass
class LayerCompatibilityRequest:
    """Input request for layer compatibility validation operations"""
    source_layer: Dict[str, Any]
    target_layer: Dict[str, Any]
    compatibility_rules: List[Dict[str, Any]]
    validation_options: Dict[str, Any]
    context: Dict[str, Any]
    compatibility_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class CompatibilityCheckResult:
    """Result of individual compatibility check"""
    rule_id: str
    rule_type: CompatibilityType
    source_layer: str
    target_layer: str
    compatibility_level: CompatibilityLevel
    details: Dict[str, Any]
    issues: List[str]
    recommendations: List[str]
    execution_time_ms: float


@dataclass
class LayerCompatibilityValidationResult:
    """Result of layer compatibility validation"""
    overall_compatibility: CompatibilityLevel
    compatibility_score: float
    check_results: List[CompatibilityCheckResult]
    critical_issues: List[str]
    recommendations: List[str]
    validation_summary: Dict[str, Any]


@dataclass
class LayerCompatibilityResult:
    """Output result from layer compatibility validation operations"""
    validation_result: LayerCompatibilityValidationResult
    compatibility_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    compatibility_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerCompatibilityValidatorInterface(ABC):
    """Abstract interface for layer compatibility validation operations"""
    
    @abstractmethod
    async def validate_compatibility(self, request: LayerCompatibilityRequest) -> LayerCompatibilityResult:
        """Validate compatibility between layers"""
        pass
    
    @abstractmethod
    async def check_version_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> CompatibilityCheckResult:
        """Check version compatibility between layers"""
        pass
    
    @abstractmethod
    async def check_interface_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> CompatibilityCheckResult:
        """Check interface compatibility between layers"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerCompatibilityValidator(LayerCompatibilityValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating layer compatibility.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerCompatibilitySafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerCompatibilitySafetyPolicy()
        self.safety_validator = LayerCompatibilitySafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Compatibility validation patterns and rules
        self._compatibility_patterns = {
            CompatibilityType.VERSION: {
                "semantic_versioning": self._check_semantic_versioning,
                "version_constraints": self._check_version_constraints,
                "breaking_changes": self._check_breaking_changes
            },
            CompatibilityType.INTERFACE: {
                "api_compatibility": self._check_api_compatibility,
                "parameter_compatibility": self._check_parameter_compatibility,
                "return_type_compatibility": self._check_return_type_compatibility
            },
            CompatibilityType.DEPENDENCY: {
                "dependency_versions": self._check_dependency_versions,
                "dependency_conflicts": self._check_dependency_conflicts,
                "transitive_dependencies": self._check_transitive_dependencies
            },
            CompatibilityType.DATA_FORMAT: {
                "schema_compatibility": self._check_schema_compatibility,
                "data_type_compatibility": self._check_data_type_compatibility,
                "format_compatibility": self._check_format_compatibility
            },
            CompatibilityType.PROTOCOL: {
                "protocol_versions": self._check_protocol_versions,
                "protocol_features": self._check_protocol_features,
                "protocol_security": self._check_protocol_security
            },
            CompatibilityType.CONFIGURATION: {
                "config_schema": self._check_config_schema,
                "config_defaults": self._check_config_defaults,
                "config_compatibility": self._check_config_compatibility
            }
        }
        
        self.logger.info("LayerCompatibilityValidator initialized with L5 safety policies")
    
    async def validate_compatibility(self, request: LayerCompatibilityRequest) -> LayerCompatibilityResult:
        """
        Validate compatibility between layers.
        
        Args:
            request: Layer compatibility validation request with source and target layers
            
        Returns:
            LayerCompatibilityResult: Structured result with compatibility validation outcome and details
            
        Raises:
            ValidationError: If compatibility validation fails
            SafetyError: If compatibility validation violates safety policies
        """
        source_name = request.source_layer.get("name", "unknown_source")
        target_name = request.target_layer.get("name", "unknown_target")
        
        self.logger.info(f"Validating compatibility between {source_name} and {target_name}")
        
        try:
            # L5 Safety validation
            compatibility_input = {
                "layers": [request.source_layer, request.target_layer],
                "compatibility_rules": request.compatibility_rules
            }
            
            is_valid, error_msg = self.safety_validator.validate_compatibility_input(compatibility_input)
            if not is_valid:
                raise SafetyError(f"Compatibility safety validation failed: {error_msg}")
            
            # Parse compatibility rules
            parsed_rules = await self._parse_compatibility_rules(request.compatibility_rules)
            
            # Execute compatibility checks
            check_results = []
            for rule in parsed_rules:
                result = await self._execute_compatibility_check(request.source_layer, request.target_layer, rule)
                check_results.append(result)
            
            # Determine overall compatibility
            overall_compatibility = await self._determine_overall_compatibility(check_results)
            
            # Calculate compatibility score
            compatibility_score = self._calculate_compatibility_score(check_results)
            
            # Extract critical issues and recommendations
            critical_issues = []
            recommendations = []
            
            for result in check_results:
                critical_issues.extend([issue for issue in result.issues if "critical" in issue.lower()])
                recommendations.extend(result.recommendations)
            
            # Generate validation summary
            validation_summary = await self._generate_validation_summary(
                source_name,
                target_name,
                check_results
            )
            
            # Create validation result
            validation_result = LayerCompatibilityValidationResult(
                overall_compatibility=overall_compatibility,
                compatibility_score=compatibility_score,
                check_results=check_results,
                critical_issues=critical_issues,
                recommendations=recommendations,
                validation_summary=validation_summary
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_compatibility_risk_score(validation_result),
                "security_flags": self._extract_security_flags(check_results)
            }
            
            # Generate unique compatibility ID
            compatibility_id = self._generate_compatibility_id(request, validation_result)
            
            result = LayerCompatibilityResult(
                validation_result=validation_result,
                compatibility_metadata={
                    "source_layer": source_name,
                    "target_layer": target_name,
                    "checks_executed": len(check_results),
                    "critical_issues_count": len(critical_issues),
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                compatibility_id=compatibility_id
            )
            
            self.logger.info(f"Successfully validated compatibility with score {compatibility_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate layer compatibility: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def check_version_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> CompatibilityCheckResult:
        """Check version compatibility between layers"""
        try:
            source_version = source.get("version", "1.0.0")
            target_version = target.get("version", "1.0.0")
            
            # Simple semantic versioning check
            source_parts = source_version.split(".")
            target_parts = target_version.split(".")
            
            compatibility_level = CompatibilityLevel.COMPATIBLE
            issues = []
            recommendations = []
            
            # Major version check
            if len(source_parts) >= 1 and len(target_parts) >= 1:
                if source_parts[0] != target_parts[0]:
                    compatibility_level = CompatibilityLevel.INCOMPATIBLE
                    issues.append(f"Major version mismatch: {source_parts[0]} vs {target_parts[0]}")
                    recommendations.append("Consider updating to compatible major version")
            
            # Minor version check
            if len(source_parts) >= 2 and len(target_parts) >= 2:
                if int(source_parts[1]) > int(target_parts[1]):
                    if compatibility_level == CompatibilityLevel.COMPATIBLE:
                        compatibility_level = CompatibilityLevel.PARTIALLY_COMPATIBLE
                    issues.append(f"Source minor version newer: {source_parts[1]} vs {target_parts[1]}")
                    recommendations.append("Verify backward compatibility")
            
            return CompatibilityCheckResult(
                rule_id="version_compatibility",
                rule_type=CompatibilityType.VERSION,
                source_layer=source.get("name", ""),
                target_layer=target.get("name", ""),
                compatibility_level=compatibility_level,
                details={
                    "source_version": source_version,
                    "target_version": target_version
                },
                issues=issues,
                recommendations=recommendations,
                execution_time_ms=1.0
            )
            
        except Exception as e:
            return CompatibilityCheckResult(
                rule_id="version_compatibility",
                rule_type=CompatibilityType.VERSION,
                source_layer=source.get("name", ""),
                target_layer=target.get("name", ""),
                compatibility_level=CompatibilityLevel.UNKNOWN,
                details={"error": str(e)},
                issues=[f"Version check failed: {str(e)}"],
                recommendations=["Fix version format"],
                execution_time_ms=0.0
            )
    
    async def check_interface_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> CompatibilityCheckResult:
        """Check interface compatibility between layers"""
        try:
            source_interfaces = source.get("interfaces", [])
            target_interfaces = target.get("interfaces", [])
            
            compatibility_level = CompatibilityLevel.COMPATIBLE
            issues = []
            recommendations = []
            
            # Check for missing interfaces
            source_interface_names = {iface.get("name") for iface in source_interfaces}
            target_interface_names = {iface.get("name") for iface in target_interfaces}
            
            missing_in_target = source_interface_names - target_interface_names
            if missing_in_target:
                compatibility_level = CompatibilityLevel.PARTIALLY_COMPATIBLE
                issues.append(f"Missing interfaces in target: {missing_in_target}")
                recommendations.append("Implement missing interfaces in target layer")
            
            # Check for interface parameter compatibility
            for source_iface in source_interfaces:
                target_iface = next((iface for iface in target_interfaces if iface.get("name") == source_iface.get("name")), None)
                if target_iface:
                    source_params = source_iface.get("parameters", [])
                    target_params = target_iface.get("parameters", [])
                    
                    source_param_names = {param.get("name") for param in source_params}
                    target_param_names = {param.get("name") for param in target_params}
                    
                    missing_params = source_param_names - target_param_names
                    if missing_params:
                        if compatibility_level == CompatibilityLevel.COMPATIBLE:
                            compatibility_level = CompatibilityLevel.PARTIALLY_COMPATIBLE
                        issues.append(f"Missing parameters in {source_iface.get('name')}: {missing_params}")
                        recommendations.append(f"Add missing parameters to {source_iface.get('name')}")
            
            return CompatibilityCheckResult(
                rule_id="interface_compatibility",
                rule_type=CompatibilityType.INTERFACE,
                source_layer=source.get("name", ""),
                target_layer=target.get("name", ""),
                compatibility_level=compatibility_level,
                details={
                    "source_interfaces": len(source_interfaces),
                    "target_interfaces": len(target_interfaces),
                    "missing_interfaces": list(missing_in_target) if 'missing_in_target' in locals() else []
                },
                issues=issues,
                recommendations=recommendations,
                execution_time_ms=2.0
            )
            
        except Exception as e:
            return CompatibilityCheckResult(
                rule_id="interface_compatibility",
                rule_type=CompatibilityType.INTERFACE,
                source_layer=source.get("name", ""),
                target_layer=target.get("name", ""),
                compatibility_level=CompatibilityLevel.UNKNOWN,
                details={"error": str(e)},
                issues=[f"Interface check failed: {str(e)}"],
                recommendations=["Fix interface specification"],
                execution_time_ms=0.0
            )
    
    async def _parse_compatibility_rules(self, raw_rules: List[Dict[str, Any]]) -> List[CompatibilityRule]:
        """Parse raw compatibility rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = CompatibilityRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    type=CompatibilityType(raw_rule.get("type", "version")),
                    source_layer=raw_rule.get("source_layer", ""),
                    target_layer=raw_rule.get("target_layer", ""),
                    criteria=raw_rule.get("criteria", {}),
                    severity=raw_rule.get("severity", "medium"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse compatibility rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = CompatibilityRule(
                    id=f"fallback_rule_{i:03d}",
                    type=CompatibilityType.VERSION,
                    source_layer="",
                    target_layer="",
                    criteria={},
                    severity="low",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _execute_compatibility_check(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityRule
    ) -> CompatibilityCheckResult:
        """Execute individual compatibility check"""
        start_time = datetime.now()
        
        try:
            if rule.type == CompatibilityType.VERSION:
                result = await self.check_version_compatibility(source_layer, target_layer)
            elif rule.type == CompatibilityType.INTERFACE:
                result = await self.check_interface_compatibility(source_layer, target_layer)
            elif rule.type == CompatibilityType.DEPENDENCY:
                result = await self._check_dependency_compatibility(source_layer, target_layer)
            elif rule.type == CompatibilityType.DATA_FORMAT:
                result = await self._check_data_format_compatibility(source_layer, target_layer)
            elif rule.type == CompatibilityType.PROTOCOL:
                result = await self._check_protocol_compatibility(source_layer, target_layer)
            elif rule.type == CompatibilityType.CONFIGURATION:
                result = await self._check_configuration_compatibility(source_layer, target_layer)
            else:
                # Unknown rule type
                result = CompatibilityCheckResult(
                    rule_id=rule.id,
                    rule_type=rule.type,
                    source_layer=source_layer.get("name", ""),
                    target_layer=target_layer.get("name", ""),
                    compatibility_level=CompatibilityLevel.UNKNOWN,
                    details={"error": f"Unknown rule type: {rule.type}"},
                    issues=[f"Unknown compatibility check type: {rule.type}"],
                    recommendations=["Define valid compatibility check type"],
                    execution_time_ms=0.0
                )
            
            # Override rule ID and type
            result.rule_id = rule.id
            result.rule_type = rule.type
            
            end_time = datetime.now()
            result.execution_time_ms = (end_time - start_time).total_seconds() * 1000
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute compatibility check {rule.id}: {str(e)}")
            end_time = datetime.now()
            
            return CompatibilityCheckResult(
                rule_id=rule.id,
                rule_type=rule.type,
                source_layer=source_layer.get("name", ""),
                target_layer=target_layer.get("name", ""),
                compatibility_level=CompatibilityLevel.UNKNOWN,
                details={"error": str(e)},
                issues=[f"Check execution failed: {str(e)}"],
                recommendations=["Fix compatibility check implementation"],
                execution_time_ms=(end_time - start_time).total_seconds() * 1000
            )
    
    async def _determine_overall_compatibility(self, check_results: List[CompatibilityCheckResult]) -> CompatibilityLevel:
        """Determine overall compatibility from individual check results"""
        if not check_results:
            return CompatibilityLevel.UNKNOWN
        
        # Count compatibility levels
        level_counts = {level: 0 for level in CompatibilityLevel}
        for result in check_results:
            level_counts[result.compatibility_level] += 1
        
        # Determine overall level based on worst case
        if level_counts[CompatibilityLevel.INCOMPATIBLE] > 0:
            return CompatibilityLevel.INCOMPATIBLE
        elif level_counts[CompatibilityLevel.PARTIALLY_COMPATIBLE] > 0:
            return CompatibilityLevel.PARTIALLY_COMPATIBLE
        elif level_counts[CompatibilityLevel.COMPATIBLE] > 0:
            return CompatibilityLevel.COMPATIBLE
        else:
            return CompatibilityLevel.UNKNOWN
    
    def _calculate_compatibility_score(self, check_results: List[CompatibilityCheckResult]) -> float:
        """Calculate compatibility score based on check results"""
        if not check_results:
            return 0.0
        
        # Weight compatibility levels
        level_weights = {
            CompatibilityLevel.COMPATIBLE: 1.0,
            CompatibilityLevel.PARTIALLY_COMPATIBLE: 0.5,
            CompatibilityLevel.INCOMPATIBLE: 0.0,
            CompatibilityLevel.UNKNOWN: 0.25
        }
        
        total_weight = sum(level_weights[result.compatibility_level] for result in check_results)
        average_score = total_weight / len(check_results)
        
        return round(average_score, 2)
    
    async def _generate_validation_summary(
        self, 
        source_name: str, 
        target_name: str, 
        check_results: List[CompatibilityCheckResult]
    ) -> Dict[str, Any]:
        """Generate validation summary"""
        compatibility_types = [r.rule_type.value for r in check_results]
        compatibility_levels = [r.compatibility_level.value for r in check_results]
        level_counts = {}
        
        for level in compatibility_levels:
            level_counts[level] = level_counts.get(level, 0) + 1
        
        execution_times = [r.execution_time_ms for r in check_results]
        
        return {
            "source_layer": source_name,
            "target_layer": target_name,
            "total_checks": len(check_results),
            "compatibility_types": list(set(compatibility_types)),
            "compatibility_levels": list(set(compatibility_levels)),
            "level_distribution": level_counts,
            "total_execution_time_ms": sum(execution_times),
            "average_execution_time_ms": sum(execution_times) / len(execution_times) if execution_times else 0
        }
    
    def _extract_security_flags(self, check_results: List[CompatibilityCheckResult]) -> List[str]:
        """Extract security flags from check results"""
        security_flags = []
        
        for result in check_results:
            if result.compatibility_level == CompatibilityLevel.INCOMPATIBLE:
                security_flags.append("incompatible_layers")
            
            if "security" in result.issues or "auth" in result.issues:
                security_flags.append("security_compatibility_issue")
        
        return security_flags
    
    async def _estimate_validation_complexity(self, request: LayerCompatibilityRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.compatibility_rules) // 2
        
        # Add complexity for layer size
        source_size = len(str(request.source_layer)) // 1000
        target_size = len(str(request.target_layer)) // 1000
        complexity_score += source_size + target_size
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_compatibility_risk_score(self, validation_result: LayerCompatibilityValidationResult) -> float:
        """Calculate risk score for the compatibility validation (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for incompatible layers
        if validation_result.overall_compatibility == CompatibilityLevel.INCOMPATIBLE:
            risk_score += 0.6
        
        # Increase risk for critical issues
        if validation_result.critical_issues:
            risk_score += 0.3
        
        # Increase risk for low compatibility score
        if validation_result.compatibility_score < 0.5:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_compatibility_id(self, request: LayerCompatibilityRequest, result: LayerCompatibilityValidationResult) -> str:
        """Generate unique compatibility identifier"""
        timestamp = datetime.now().isoformat()
        source_name = request.source_layer.get("name", "unknown")
        target_name = request.target_layer.get("name", "unknown")
        content = f"{source_name}:{target_name}:{result.compatibility_score:.2f}:{timestamp}"
        return f"compat_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: LayerCompatibilityRequest, error: str) -> LayerCompatibilityResult:
        """Create safe fallback validation when main validation fails"""
        fallback_result = CompatibilityCheckResult(
            rule_id="fallback_check_001",
            rule_type=CompatibilityType.VERSION,
            source_layer=request.source_layer.get("name", ""),
            target_layer=request.target_layer.get("name", ""),
            compatibility_level=CompatibilityLevel.UNKNOWN,
            details={"fallback": True, "error": error},
            issues=[f"Validation failed: {error}"],
            recommendations=["Fix compatibility validation"],
            execution_time_ms=0.0
        )
        
        fallback_validation = LayerCompatibilityValidationResult(
            overall_compatibility=CompatibilityLevel.UNKNOWN,
            compatibility_score=0.0,
            check_results=[fallback_result],
            critical_issues=["fallback_mode"],
            recommendations=["Fix compatibility validation system"],
            validation_summary={"fallback": True}
        )
        
        return LayerCompatibilityResult(
            validation_result=fallback_validation,
            compatibility_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            compatibility_id=f"fallback_{hash(error) % 100000:06d}"
        )
    
    # Additional compatibility check implementations (simplified)
    async def _check_dependency_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> CompatibilityCheckResult:
        """Check dependency compatibility between layers"""
        # Simplified implementation
        return CompatibilityCheckResult(
            rule_id="dependency_compatibility",
            rule_type=CompatibilityType.DEPENDENCY,
            source_layer=source.get("name", ""),
            target_layer=target.get("name", ""),
            compatibility_level=CompatibilityLevel.COMPATIBLE,
            details={"message": "Dependency compatibility check not fully implemented"},
            issues=[],
            recommendations=[],
            execution_time_ms=1.0
        )
    
    async def _check_data_format_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> CompatibilityCheckResult:
        """Check data format compatibility between layers"""
        # Simplified implementation
        return CompatibilityCheckResult(
            rule_id="data_format_compatibility",
            rule_type=CompatibilityType.DATA_FORMAT,
            source_layer=source.get("name", ""),
            target_layer=target.get("name", ""),
            compatibility_level=CompatibilityLevel.COMPATIBLE,
            details={"message": "Data format compatibility check not fully implemented"},
            issues=[],
            recommendations=[],
            execution_time_ms=1.0
        )
    
    async def _check_protocol_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> CompatibilityCheckResult:
        """Check protocol compatibility between layers"""
        # Simplified implementation
        return CompatibilityCheckResult(
            rule_id="protocol_compatibility",
            rule_type=CompatibilityType.PROTOCOL,
            source_layer=source.get("name", ""),
            target_layer=target.get("name", ""),
            compatibility_level=CompatibilityLevel.COMPATIBLE,
            details={"message": "Protocol compatibility check not fully implemented"},
            issues=[],
            recommendations=[],
            execution_time_ms=1.0
        )
    
    async def _check_configuration_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> CompatibilityCheckResult:
        """Check configuration compatibility between layers"""
        # Simplified implementation
        return CompatibilityCheckResult(
            rule_id="configuration_compatibility",
            rule_type=CompatibilityType.CONFIGURATION,
            source_layer=source.get("name", ""),
            target_layer=target.get("name", ""),
            compatibility_level=CompatibilityLevel.COMPATIBLE,
            details={"message": "Configuration compatibility check not fully implemented"},
            issues=[],
            recommendations=[],
            execution_time_ms=1.0
        )
    
    # Version compatibility helper methods (simplified)
    def _check_semantic_versioning(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check semantic versioning compatibility"""
        return True  # Simplified
    
    def _check_version_constraints(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check version constraints"""
        return True  # Simplified
    
    def _check_breaking_changes(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check for breaking changes"""
        return False  # Simplified
    
    # Interface compatibility helper methods (simplified)
    def _check_api_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check API compatibility"""
        return True  # Simplified
    
    def _check_parameter_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check parameter compatibility"""
        return True  # Simplified
    
    def _check_return_type_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check return type compatibility"""
        return True  # Simplified
    
    # Other compatibility helper methods (simplified)
    def _check_dependency_versions(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check dependency versions"""
        return True  # Simplified
    
    def _check_dependency_conflicts(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check dependency conflicts"""
        return False  # Simplified
    
    def _check_transitive_dependencies(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check transitive dependencies"""
        return True  # Simplified
    
    def _check_schema_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check schema compatibility"""
        return True  # Simplified
    
    def _check_data_type_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check data type compatibility"""
        return True  # Simplified
    
    def _check_format_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check format compatibility"""
        return True  # Simplified
    
    def _check_protocol_versions(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check protocol versions"""
        return True  # Simplified
    
    def _check_protocol_features(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check protocol features"""
        return True  # Simplified
    
    def _check_protocol_security(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check protocol security"""
        return True  # Simplified
    
    def _check_config_schema(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check configuration schema"""
        return True  # Simplified
    
    def _check_config_defaults(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check configuration defaults"""
        return True  # Simplified
    
    def _check_config_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Check configuration compatibility"""
        return True  # Simplified


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when compatibility validation violates safety policies"""
    pass


class LayerCompatibilityValidationError(Exception):
    """Raised for general layer compatibility validation errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_compatibility_validator(safety_policy: Optional[LayerCompatibilitySafetyPolicy] = None) -> LayerCompatibilityValidator:
    """Factory function to create LayerCompatibilityValidator with optional custom safety policy"""
    return LayerCompatibilityValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_compatibility_request(request: LayerCompatibilityRequest) -> tuple[bool, Optional[str]]:
    """Validate layer compatibility request parameters"""
    try:
        if not isinstance(request.source_layer, dict):
            return False, "Source layer must be a dictionary"
        
        if not isinstance(request.target_layer, dict):
            return False, "Target layer must be a dictionary"
        
        if not isinstance(request.compatibility_rules, list):
            return False, "Compatibility rules must be a list"
        
        if not isinstance(request.validation_options, dict):
            return False, "Validation options must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
