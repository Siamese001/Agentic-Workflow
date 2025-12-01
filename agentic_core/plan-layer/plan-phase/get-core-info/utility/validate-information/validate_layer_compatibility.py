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

class CompatibilityValidationType(str, Enum):
    """Supported compatibility validation types with L5 safety validation"""
    VERSION = "version"
    INTERFACE = "interface"
    DEPENDENCY = "dependency"
    PROTOCOL = "protocol"
    DATA_FORMAT = "data_format"
    CONFIGURATION = "configuration"


class CompatibilitySeverity(str, Enum):
    """Compatibility validation severity levels with L5 safety enforcement"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class LayerCompatibilitySafetyPolicy(BaseModel):
    """L5 Safety policy for layer compatibility validation operations"""
    max_layer_count: int = Field(default=10, description="Maximum layers to compare")
    max_compatibility_rules: int = Field(default=50, description="Maximum compatibility rules")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in CompatibilityValidationType])
    allowed_severities: List[str] = Field(default_factory=lambda: [t.value for t in CompatibilitySeverity])
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
            
            # Check validation types
            for rule in compatibility_rules:
                rule_type = rule.get("type", "")
                if rule_type not in self.policy.allowed_validation_types:
                    error_msg = f"Prohibited validation type: {rule_type}"
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
class CompatibilityValidationRule:
    """Individual compatibility validation rule specification"""
    id: str
    validation_type: CompatibilityValidationType
    severity: CompatibilitySeverity
    criteria: Dict[str, Any]
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class LayerCompatibilityValidationRequest:
    """Input request for layer compatibility validation operations"""
    source_layer: Dict[str, Any]
    target_layer: Dict[str, Any]
    compatibility_rules: List[Dict[str, Any]]
    validation_options: Dict[str, Any]
    context: Dict[str, Any]
    compatibility_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class CompatibilityValidationError:
    """Individual compatibility validation error"""
    layer_pair: str
    rule_id: str
    validation_type: CompatibilityValidationType
    error_category: str
    error_message: str
    actual_value: Any
    expected_value: Any
    severity: CompatibilitySeverity


@dataclass
class CompatibilityValidationResult:
    """Result of layer compatibility validation"""
    is_compatible: bool
    compatibility_score: float
    validation_errors: List[CompatibilityValidationError]
    validation_warnings: List[CompatibilityValidationError]
    compatibility_matrix: Dict[str, str]
    validation_summary: Dict[str, Any]
    security_flags: List[str]


@dataclass
class LayerCompatibilityValidationResult:
    """Output result from layer compatibility validation operations"""
    validation_result: CompatibilityValidationResult
    compatibility_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    compatibility_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerCompatibilityValidatorInterface(ABC):
    """Abstract interface for layer compatibility validation operations"""
    
    @abstractmethod
    async def validate_compatibility(self, request: LayerCompatibilityValidationRequest) -> LayerCompatibilityValidationResult:
        """Validate compatibility between layers"""
        pass
    
    @abstractmethod
    async def check_version_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> List[CompatibilityValidationError]:
        """Check version compatibility between layers"""
        pass
    
    @abstractmethod
    async def check_interface_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> List[CompatibilityValidationError]:
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
        self._validation_patterns = {
            CompatibilityValidationType.VERSION: {
                "semantic_versioning": self._validate_semantic_versioning,
                "version_constraints": self._validate_version_constraints,
                "breaking_changes": self._validate_breaking_changes
            },
            CompatibilityValidationType.INTERFACE: {
                "api_compatibility": self._validate_api_compatibility,
                "parameter_compatibility": self._validate_parameter_compatibility,
                "return_type_compatibility": self._validate_return_type_compatibility
            },
            CompatibilityValidationType.DEPENDENCY: {
                "dependency_versions": self._validate_dependency_versions,
                "dependency_conflicts": self._validate_dependency_conflicts,
                "transitive_dependencies": self._validate_transitive_dependencies
            },
            CompatibilityValidationType.PROTOCOL: {
                "protocol_versions": self._validate_protocol_versions,
                "protocol_features": self._validate_protocol_features,
                "protocol_security": self._validate_protocol_security
            },
            CompatibilityValidationType.DATA_FORMAT: {
                "schema_compatibility": self._validate_schema_compatibility,
                "data_type_compatibility": self._validate_data_type_compatibility,
                "format_compatibility": self._validate_format_compatibility
            },
            CompatibilityValidationType.CONFIGURATION: {
                "config_schema": self._validate_config_schema,
                "config_defaults": self._validate_config_defaults,
                "config_compatibility": self._validate_config_compatibility
            }
        }
        
        self.logger.info("LayerCompatibilityValidator initialized with L5 safety policies")
    
    async def validate_compatibility(self, request: LayerCompatibilityValidationRequest) -> LayerCompatibilityValidationResult:
        """
        Validate compatibility between layers.
        
        Args:
            request: Layer compatibility validation request with source and target layers
            
        Returns:
            LayerCompatibilityValidationResult: Structured result with compatibility validation outcome and details
            
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
            
            # Sanitize compatibility data if required
            sanitized_source = request.source_layer
            sanitized_target = request.target_layer
            if self.safety_policy.sanitize_compatibility_data:
                sanitized_source = await self._sanitize_layer_data(request.source_layer)
                sanitized_target = await self._sanitize_layer_data(request.target_layer)
            
            # Parse compatibility rules
            parsed_rules = await self._parse_compatibility_rules(request.compatibility_rules)
            
            # Execute compatibility validation rules
            validation_errors = []
            for rule in parsed_rules:
                rule_errors = await self._execute_compatibility_rule(sanitized_source, sanitized_target, rule)
                validation_errors.extend(rule_errors)
            
            # Check version compatibility
            version_errors = await self.check_version_compatibility(sanitized_source, sanitized_target)
            validation_errors.extend(version_errors)
            
            # Check interface compatibility
            interface_errors = await self.check_interface_compatibility(sanitized_source, sanitized_target)
            validation_errors.extend(interface_errors)
            
            # Separate errors and warnings based on severity
            error_list = [e for e in validation_errors if e.severity in [CompatibilitySeverity.CRITICAL, CompatibilitySeverity.ERROR]]
            warning_list = [e for e in validation_errors if e.severity in [CompatibilitySeverity.WARNING, CompatibilitySeverity.INFO]]
            
            # Determine overall compatibility
            is_layers_compatible = len(error_list) == 0
            
            # Calculate compatibility score
            compatibility_score = self._calculate_compatibility_score(validation_errors)
            
            # Generate compatibility matrix
            compatibility_matrix = await self._generate_compatibility_matrix(
                sanitized_source, 
                sanitized_target, 
                validation_errors
            )
            
            # Generate validation summary
            validation_summary = await self._generate_validation_summary(
                source_name,
                target_name,
                validation_errors
            )
            
            # Extract security flags
            security_flags = self._extract_security_flags(validation_errors)
            
            # Create validation result
            validation_result = CompatibilityValidationResult(
                is_compatible=is_layers_compatible,
                compatibility_score=compatibility_score,
                validation_errors=error_list,
                validation_warnings=warning_list,
                compatibility_matrix=compatibility_matrix,
                validation_summary=validation_summary,
                security_flags=security_flags
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_compatibility_risk_score(validation_result),
                "security_flags": security_flags
            }
            
            # Generate unique compatibility ID
            compatibility_id = self._generate_compatibility_id(request, validation_result)
            
            result = LayerCompatibilityValidationResult(
                validation_result=validation_result,
                compatibility_metadata={
                    "source_layer": source_name,
                    "target_layer": target_name,
                    "rules_applied": len(parsed_rules),
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
    
    async def check_version_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> List[CompatibilityValidationError]:
        """Check version compatibility between layers"""
        errors = []
        
        try:
            source_version = source.get("version", "1.0.0")
            target_version = target.get("version", "1.0.0")
            layer_pair = f"{source.get('name', 'source')}:{target.get('name', 'target')}"
            
            # Simple semantic versioning check
            source_parts = source_version.split(".")
            target_parts = target_version.split(".")
            
            # Major version check
            if len(source_parts) >= 1 and len(target_parts) >= 1:
                if source_parts[0] != target_parts[0]:
                    error = CompatibilityValidationError(
                        layer_pair=layer_pair,
                        rule_id="version_compatibility",
                        validation_type=CompatibilityValidationType.VERSION,
                        error_category="major_version_mismatch",
                        error_message=f"Major version mismatch: {source_parts[0]} vs {target_parts[0]}",
                        actual_value=source_version,
                        expected_value=target_version,
                        severity=CompatibilitySeverity.CRITICAL
                    )
                    errors.append(error)
            
            # Minor version check
            if len(source_parts) >= 2 and len(target_parts) >= 2:
                if int(source_parts[1]) > int(target_parts[1]):
                    error = CompatibilityValidationError(
                        layer_pair=layer_pair,
                        rule_id="version_compatibility",
                        validation_type=CompatibilityValidationType.VERSION,
                        error_category="minor_version_newer",
                        error_message=f"Source minor version newer: {source_parts[1]} vs {target_parts[1]}",
                        actual_value=source_version,
                        expected_value=target_version,
                        severity=CompatibilitySeverity.WARNING
                    )
                    errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Version compatibility check failed: {str(e)}")
            layer_pair = f"{source.get('name', 'source')}:{target.get('name', 'target')}"
            error = CompatibilityValidationError(
                layer_pair=layer_pair,
                rule_id="version_compatibility_error",
                validation_type=CompatibilityValidationType.VERSION,
                error_category="validation_error",
                error_message=f"Version compatibility check error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=CompatibilitySeverity.ERROR
            )
            errors.append(error)
        
        return errors
    
    async def check_interface_compatibility(self, source: Dict[str, Any], target: Dict[str, Any]) -> List[CompatibilityValidationError]:
        """Check interface compatibility between layers"""
        errors = []
        
        try:
            source_interfaces = source.get("interfaces", [])
            target_interfaces = target.get("interfaces", [])
            layer_pair = f"{source.get('name', 'source')}:{target.get('name', 'target')}"
            
            # Check for missing interfaces
            source_interface_names = {iface.get("name") for iface in source_interfaces}
            target_interface_names = {iface.get("name") for iface in target_interfaces}
            
            missing_in_target = source_interface_names - target_interface_names
            if missing_in_target:
                error = CompatibilityValidationError(
                    layer_pair=layer_pair,
                    rule_id="interface_compatibility",
                    validation_type=CompatibilityValidationType.INTERFACE,
                    error_category="missing_interfaces",
                    error_message=f"Missing interfaces in target: {missing_in_target}",
                    actual_value=list(target_interface_names),
                    expected_value=list(source_interface_names),
                    severity=CompatibilitySeverity.ERROR
                )
                errors.append(error)
            
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
                        error = CompatibilityValidationError(
                            layer_pair=layer_pair,
                            rule_id="interface_compatibility",
                            validation_type=CompatibilityValidationType.INTERFACE,
                            error_category="missing_parameters",
                            error_message=f"Missing parameters in {source_iface.get('name')}: {missing_params}",
                            actual_value=list(target_param_names),
                            expected_value=list(source_param_names),
                            severity=CompatibilitySeverity.WARNING
                        )
                        errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Interface compatibility check failed: {str(e)}")
            layer_pair = f"{source.get('name', 'source')}:{target.get('name', 'target')}"
            error = CompatibilityValidationError(
                layer_pair=layer_pair,
                rule_id="interface_compatibility_error",
                validation_type=CompatibilityValidationType.INTERFACE,
                error_category="validation_error",
                error_message=f"Interface compatibility check error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=CompatibilitySeverity.ERROR
            )
            errors.append(error)
        
        return errors
    
    async def _parse_compatibility_rules(self, raw_rules: List[Dict[str, Any]]) -> List[CompatibilityValidationRule]:
        """Parse raw compatibility rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = CompatibilityValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    validation_type=CompatibilityValidationType(raw_rule.get("validation_type", "version")),
                    severity=CompatibilitySeverity(raw_rule.get("severity", "error")),
                    criteria=raw_rule.get("criteria", {}),
                    error_message=raw_rule.get("error_message", "Compatibility validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse compatibility rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = CompatibilityValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    validation_type=CompatibilityValidationType.VERSION,
                    severity=CompatibilitySeverity.WARNING,
                    criteria={},
                    error_message=f"Parsing failed: {str(e)}",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _execute_compatibility_rule(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Execute individual compatibility validation rule"""
        errors = []
        layer_pair = f"{source_layer.get('name', 'source')}:{target_layer.get('name', 'target')}"
        
        try:
            # Get validation function for rule type
            type_patterns = self._validation_patterns.get(rule.validation_type, {})
            validation_func = type_patterns.get(rule.criteria.get("validation_function", ""))
            
            if validation_func:
                # Apply validation function
                rule_errors = await validation_func(source_layer, target_layer, rule)
                errors.extend(rule_errors)
            else:
                # Unknown validation function
                error = CompatibilityValidationError(
                    layer_pair=layer_pair,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="unknown_validation",
                    error_message=f"Unknown validation function: {rule.criteria.get('validation_function')}",
                    actual_value=None,
                    expected_value=None,
                    severity=CompatibilitySeverity.WARNING
                )
                errors.append(error)
                
        except Exception as e:
            self.logger.error(f"Failed to execute compatibility rule {rule.id}: {str(e)}")
            error = CompatibilityValidationError(
                layer_pair=layer_pair,
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="rule_execution_error",
                error_message=f"Rule execution failed: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=CompatibilitySeverity.ERROR
            )
            errors.append(error)
        
        return errors
    
    async def _sanitize_layer_data(self, layer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize layer data for safety"""
        sanitized = layer_data.copy()
        
        # Remove dangerous content from string fields
        for key, value in sanitized.items():
            if isinstance(value, str):
                # Remove script tags and dangerous content
                sanitized_value = value.replace("<script", "").replace("</script>", "")
                sanitized[key] = sanitized_value
            elif isinstance(value, list):
                # Sanitize list items
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        sanitized_item = item.replace("<script", "").replace("</script>", "")
                        sanitized_list.append(sanitized_item)
                    elif isinstance(item, dict):
                        sanitized_item = await self._sanitize_layer_data(item)
                        sanitized_list.append(sanitized_item)
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
            elif isinstance(value, dict):
                sanitized[key] = await self._sanitize_layer_data(value)
        
        return sanitized
    
    # Validation function implementations
    async def _validate_semantic_versioning(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate semantic versioning compatibility"""
        errors = []
        layer_pair = f"{source_layer.get('name', 'source')}:{target_layer.get('name', 'target')}"
        
        source_version = source_layer.get("version", "")
        target_version = target_layer.get("version", "")
        
        if not self._is_valid_semver(source_version):
            error = CompatibilityValidationError(
                layer_pair=layer_pair,
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="invalid_semver",
                error_message=f"Invalid semantic version: {source_version}",
                actual_value=source_version,
                expected_value="semantic version (x.y.z)",
                severity=rule.severity
            )
            errors.append(error)
        
        if not self._is_valid_semver(target_version):
            error = CompatibilityValidationError(
                layer_pair=layer_pair,
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="invalid_semver",
                error_message=f"Invalid semantic version: {target_version}",
                actual_value=target_version,
                expected_value="semantic version (x.y.z)",
                severity=rule.severity
            )
            errors.append(error)
        
        return errors
    
    async def _validate_version_constraints(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate version constraints"""
        # Simplified implementation
        return []
    
    async def _validate_breaking_changes(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate breaking changes"""
        # Simplified implementation
        return []
    
    async def _validate_api_compatibility(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate API compatibility"""
        # Simplified implementation
        return []
    
    async def _validate_parameter_compatibility(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate parameter compatibility"""
        # Simplified implementation
        return []
    
    async def _validate_return_type_compatibility(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate return type compatibility"""
        # Simplified implementation
        return []
    
    async def _validate_dependency_versions(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate dependency versions"""
        # Simplified implementation
        return []
    
    async def _validate_dependency_conflicts(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate dependency conflicts"""
        # Simplified implementation
        return []
    
    async def _validate_transitive_dependencies(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate transitive dependencies"""
        # Simplified implementation
        return []
    
    async def _validate_protocol_versions(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate protocol versions"""
        # Simplified implementation
        return []
    
    async def _validate_protocol_features(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate protocol features"""
        # Simplified implementation
        return []
    
    async def _validate_protocol_security(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate protocol security"""
        # Simplified implementation
        return []
    
    async def _validate_schema_compatibility(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate schema compatibility"""
        # Simplified implementation
        return []
    
    async def _validate_data_type_compatibility(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate data type compatibility"""
        # Simplified implementation
        return []
    
    async def _validate_format_compatibility(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate format compatibility"""
        # Simplified implementation
        return []
    
    async def _validate_config_schema(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate configuration schema"""
        # Simplified implementation
        return []
    
    async def _validate_config_defaults(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate configuration defaults"""
        # Simplified implementation
        return []
    
    async def _validate_config_compatibility(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        rule: CompatibilityValidationRule
    ) -> List[CompatibilityValidationError]:
        """Validate configuration compatibility"""
        # Simplified implementation
        return []
    
    def _is_valid_semver(self, version: str) -> bool:
        """Check if version follows semantic versioning"""
        if not version:
            return False
        
        import re
        semver_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9\-]+)?(\+[a-zA-Z0-9\-]+)?$"
        return re.match(semver_pattern, version) is not None
    
    def _calculate_compatibility_score(self, errors: List[CompatibilityValidationError]) -> float:
        """Calculate compatibility score based on validation errors"""
        if not errors:
            return 1.0
        
        # Weight errors by severity
        severity_weights = {
            CompatibilitySeverity.CRITICAL: 0.0,
            CompatibilitySeverity.ERROR: 0.3,
            CompatibilitySeverity.WARNING: 0.7,
            CompatibilitySeverity.INFO: 0.9
        }
        
        total_weight = sum(severity_weights[error.severity] for error in errors)
        average_score = total_weight / len(errors)
        
        return round(average_score, 2)
    
    async def _generate_compatibility_matrix(
        self, 
        source_layer: Dict[str, Any], 
        target_layer: Dict[str, Any], 
        errors: List[CompatibilityValidationError]
    ) -> Dict[str, str]:
        """Generate compatibility matrix"""
        source_name = source_layer.get("name", "source")
        target_name = target_layer.get("name", "target")
        
        matrix = {
            f"{source_name}:{target_name}": "incompatible" if errors else "compatible"
        }
        
        # Add detailed compatibility by type
        error_types = [error.validation_type.value for error in errors]
        for error_type in set(error_types):
            type_errors = [e for e in errors if e.validation_type.value == error_type]
            if type_errors:
                matrix[f"{source_name}:{target_name}:{error_type}"] = "incompatible"
            else:
                matrix[f"{source_name}:{target_name}:{error_type}"] = "compatible"
        
        return matrix
    
    async def _generate_validation_summary(
        self, 
        source_name: str,
        target_name: str,
        errors: List[CompatibilityValidationError]
    ) -> Dict[str, Any]:
        """Generate validation summary"""
        error_types = [error.validation_type.value for error in errors]
        error_categories = [error.error_category for error in errors]
        severity_counts = {}
        
        for error in errors:
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "source_layer": source_name,
            "target_layer": target_name,
            "total_errors": len(errors),
            "error_types": list(set(error_types)),
            "error_categories": list(set(error_categories)),
            "severity_distribution": severity_counts,
            "most_common_error": max(error_categories) if error_categories else None
        }
    
    def _extract_security_flags(self, errors: List[CompatibilityValidationError]) -> List[str]:
        """Extract security flags from validation errors"""
        security_flags = []
        
        for error in errors:
            if error.validation_type == CompatibilityValidationType.PROTOCOL:
                security_flags.append("protocol_compatibility_issue")
            elif "security" in error.error_category:
                security_flags.append("security_compatibility_issue")
            elif error.severity == CompatibilitySeverity.CRITICAL:
                security_flags.append("critical_compatibility_issue")
        
        return security_flags
    
    async def _estimate_validation_complexity(self, request: LayerCompatibilityValidationRequest) -> str:
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
    
    def _calculate_compatibility_risk_score(self, validation_result: CompatibilityValidationResult) -> float:
        """Calculate risk score for the compatibility validation (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for compatibility errors
        if validation_result.validation_errors:
            risk_score += 0.4
        
        # Increase risk for critical issues
        critical_errors = [e for e in validation_result.validation_errors if e.severity == CompatibilitySeverity.CRITICAL]
        if critical_errors:
            risk_score += 0.5
        
        # Increase risk for low compatibility score
        if validation_result.compatibility_score < 0.5:
            risk_score += 0.3
        
        return min(risk_score, 1.0)
    
    def _generate_compatibility_id(self, request: LayerCompatibilityValidationRequest, result: CompatibilityValidationResult) -> str:
        """Generate unique compatibility identifier"""
        timestamp = datetime.now().isoformat()
        source_name = request.source_layer.get("name", "unknown")
        target_name = request.target_layer.get("name", "unknown")
        content = f"{source_name}:{target_name}:{result.compatibility_score:.2f}:{timestamp}"
        return f"compat_validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: LayerCompatibilityValidationRequest, error: str) -> LayerCompatibilityValidationResult:
        """Create safe fallback validation when main validation fails"""
        layer_pair = f"{request.source_layer.get('name', 'source')}:{request.target_layer.get('name', 'target')}"
        
        fallback_error = CompatibilityValidationError(
            layer_pair=layer_pair,
            rule_id="fallback_rule",
            validation_type=CompatibilityValidationType.VERSION,
            error_category="validation_failed",
            error_message=f"Compatibility validation failed: {error}",
            actual_value="fallback",
            expected_value="success",
            severity=CompatibilitySeverity.WARNING
        )
        
        fallback_result = CompatibilityValidationResult(
            is_compatible=False,
            compatibility_score=0.0,
            validation_errors=[fallback_error],
            validation_warnings=[],
            compatibility_matrix={"fallback": "incompatible"},
            validation_summary={"fallback": True},
            security_flags=["fallback_mode"]
        )
        
        return LayerCompatibilityValidationResult(
            validation_result=fallback_result,
            compatibility_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            compatibility_id=f"fallback_{hash(error) % 100000:06d}"
        )


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

def validate_compatibility_request(request: LayerCompatibilityValidationRequest) -> tuple[bool, Optional[str]]:
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
