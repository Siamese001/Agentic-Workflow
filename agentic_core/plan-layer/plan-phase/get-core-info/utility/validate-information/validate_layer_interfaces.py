"""
L1 Cognitive Planning - Layer Interfaces Validation

Implements pure planning operations for validating layer interfaces
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

class InterfaceValidationType(str, Enum):
    """Supported interface validation types with L5 safety validation"""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"
    PROTOCOL = "protocol"
    DOCUMENTATION = "documentation"


class ValidationSeverity(str, Enum):
    """Validation severity levels with L5 safety enforcement"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class LayerInterfacesSafetyPolicy(BaseModel):
    """L5 Safety policy for layer interfaces validation operations"""
    max_interface_count: int = Field(default=50, description="Maximum interfaces per layer")
    max_parameter_count: int = Field(default=20, description="Maximum parameters per interface")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in InterfaceValidationType])
    allowed_severities: List[str] = Field(default_factory=lambda: [t.value for t in ValidationSeverity])
    require_interface_validation: bool = Field(default=True)
    prevent_interface_injection: bool = Field(default=True)
    sanitize_interface_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerInterfacesSafetyValidator:
    """L5 Safety validator for layer interfaces validation operations"""
    
    def __init__(self, policy: LayerInterfacesSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerInterfacesSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._injection_patterns = [
            r"\${", r"%{", r"{{", r"\[\[",  # Template injection
            r"union\s+select", r"drop\s+table",  # SQL injection
            r"<\?php", r"<%", r"@\s*import"  # Code injection
        ]
    
    def validate_interfaces_input(self, interfaces_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates interfaces input against L5 safety policies"""
        try:
            # Check interface count
            interfaces = interfaces_input.get("interfaces", [])
            if len(interfaces) > self.policy.max_interface_count:
                error_msg = f"Too many interfaces: {len(interfaces)} > {self.policy.max_interface_count}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check parameter counts
            for interface in interfaces:
                parameters = interface.get("parameters", [])
                if len(parameters) > self.policy.max_parameter_count:
                    error_msg = f"Too many parameters: {len(parameters)} > {self.policy.max_parameter_count}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check validation types
            validation_rules = interfaces_input.get("validation_rules", [])
            for rule in validation_rules:
                rule_type = rule.get("type", "")
                if rule_type not in self.policy.allowed_validation_types:
                    error_msg = f"Prohibited validation type: {rule_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(interfaces).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for injection patterns
            for pattern in self._injection_patterns:
                if pattern in content_str:
                    error_msg = f"Injection pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
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
class InterfaceValidationRule:
    """Individual interface validation rule specification"""
    id: str
    validation_type: InterfaceValidationType
    severity: ValidationSeverity
    criteria: Dict[str, Any]
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class LayerInterfacesValidationRequest:
    """Input request for layer interfaces validation operations"""
    layer_name: str
    interfaces: List[Dict[str, Any]]
    validation_rules: List[Dict[str, Any]]
    validation_options: Dict[str, Any]
    context: Dict[str, Any]
    interface_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class InterfaceValidationError:
    """Individual interface validation error"""
    interface_id: str
    rule_id: str
    validation_type: InterfaceValidationType
    error_category: str
    error_message: str
    actual_value: Any
    expected_value: Any
    severity: ValidationSeverity


@dataclass
class InterfacesValidationResult:
    """Result of layer interfaces validation"""
    is_valid: bool
    validation_errors: List[InterfaceValidationError]
    validation_warnings: List[InterfaceValidationError]
    interface_summary: Dict[str, Any]
    validation_summary: Dict[str, Any]
    security_flags: List[str]


@dataclass
class LayerInterfacesValidationResult:
    """Output result from layer interfaces validation operations"""
    validation_result: InterfacesValidationResult
    validated_interfaces: List[Dict[str, Any]]
    validation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    interfaces_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerInterfacesValidatorInterface(ABC):
    """Abstract interface for layer interfaces validation operations"""
    
    @abstractmethod
    async def validate_interfaces(self, request: LayerInterfacesValidationRequest) -> LayerInterfacesValidationResult:
        """Validate layer interfaces against rules and criteria"""
        pass
    
    @abstractmethod
    async def validate_interface_structure(self, interfaces: List[Dict[str, Any]]) -> List[InterfaceValidationError]:
        """Validate interface structure and organization"""
        pass
    
    @abstractmethod
    async def validate_interface_compatibility(self, interfaces: List[Dict[str, Any]]) -> List[InterfaceValidationError]:
        """Validate interface compatibility and consistency"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerInterfacesValidator(LayerInterfacesValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating layer interfaces.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerInterfacesSafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerInterfacesSafetyPolicy()
        self.safety_validator = LayerInterfacesSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Interface validation patterns and rules
        self._validation_patterns = {
            InterfaceValidationType.STRUCTURAL: {
                "required_fields": self._validate_required_fields,
                "field_types": self._validate_field_types,
                "interface_format": self._validate_interface_format
            },
            InterfaceValidationType.SEMANTIC: {
                "naming_conventions": self._validate_naming_conventions,
                "parameter_consistency": self._validate_parameter_consistency,
                "documentation_completeness": self._validate_documentation_completeness
            },
            InterfaceValidationType.SECURITY: {
                "authentication_required": self._validate_authentication_required,
                "authorization_policies": self._validate_authorization_policies,
                "input_validation": self._validate_input_validation
            },
            InterfaceValidationType.COMPATIBILITY: {
                "version_compatibility": self._validate_version_compatibility,
                "backward_compatibility": self._validate_backward_compatibility,
                "api_compatibility": self._validate_api_compatibility
            },
            InterfaceValidationType.PROTOCOL: {
                "protocol_standards": self._validate_protocol_standards,
                "endpoint_validation": self._validate_endpoint_validation,
                "method_validation": self._validate_method_validation
            },
            InterfaceValidationType.DOCUMENTATION: {
                "documentation_presence": self._validate_documentation_presence,
                "documentation_quality": self._validate_documentation_quality,
                "example_completeness": self._validate_example_completeness
            }
        }
        
        self.logger.info("LayerInterfacesValidator initialized with L5 safety policies")
    
    async def validate_interfaces(self, request: LayerInterfacesValidationRequest) -> LayerInterfacesValidationResult:
        """
        Validate layer interfaces against rules and criteria.
        
        Args:
            request: Layer interfaces validation request with interfaces and validation rules
            
        Returns:
            LayerInterfacesValidationResult: Structured result with validation outcome and details
            
        Raises:
            ValidationError: If interfaces validation fails
            SafetyError: If interfaces violate safety policies
        """
        self.logger.info(f"Validating interfaces for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            interfaces_input = {
                "interfaces": request.interfaces,
                "validation_rules": request.validation_rules
            }
            
            is_valid, error_msg = self.safety_validator.validate_interfaces_input(interfaces_input)
            if not is_valid:
                raise SafetyError(f"Interfaces safety validation failed: {error_msg}")
            
            # Sanitize interfaces if required
            sanitized_interfaces = request.interfaces
            if self.safety_policy.sanitize_interface_data:
                sanitized_interfaces = await self._sanitize_interfaces(request.interfaces)
            
            # Parse validation rules
            parsed_rules = await self._parse_validation_rules(request.validation_rules)
            
            # Execute validation rules
            validation_errors = []
            for rule in parsed_rules:
                rule_errors = await self._execute_validation_rule(sanitized_interfaces, rule)
                validation_errors.extend(rule_errors)
            
            # Validate interface structure
            structure_errors = await self.validate_interface_structure(sanitized_interfaces)
            validation_errors.extend(structure_errors)
            
            # Validate interface compatibility
            compatibility_errors = await self.validate_interface_compatibility(sanitized_interfaces)
            validation_errors.extend(compatibility_errors)
            
            # Separate errors and warnings based on severity
            error_list = [e for e in validation_errors if e.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]]
            warning_list = [e for e in validation_errors if e.severity in [ValidationSeverity.WARNING, ValidationSeverity.INFO]]
            
            # Determine overall validity
            is_interfaces_valid = len(error_list) == 0
            
            # Generate interface summary
            interface_summary = await self._generate_interface_summary(sanitized_interfaces)
            
            # Generate validation summary
            validation_summary = await self._generate_validation_summary(
                request.layer_name,
                validation_errors
            )
            
            # Extract security flags
            security_flags = self._extract_security_flags(validation_errors)
            
            # Create validation result
            validation_result = InterfacesValidationResult(
                is_valid=is_interfaces_valid,
                validation_errors=error_list,
                validation_warnings=warning_list,
                interface_summary=interface_summary,
                validation_summary=validation_summary,
                security_flags=security_flags
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_interfaces_risk_score(validation_result),
                "security_flags": security_flags
            }
            
            # Generate unique interfaces ID
            interfaces_id = self._generate_interfaces_id(request, validation_result)
            
            result = LayerInterfacesValidationResult(
                validation_result=validation_result,
                validated_interfaces=sanitized_interfaces,
                validation_metadata={
                    "layer_name": request.layer_name,
                    "rules_applied": len(parsed_rules),
                    "total_interfaces": len(sanitized_interfaces),
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                interfaces_id=interfaces_id
            )
            
            self.logger.info(f"Successfully validated interfaces for {request.layer_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate layer interfaces: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def validate_interface_structure(self, interfaces: List[Dict[str, Any]]) -> List[InterfaceValidationError]:
        """Validate interface structure and organization"""
        errors = []
        
        try:
            # Check for duplicate interface names
            interface_names = [iface.get("name", "") for iface in interfaces]
            if len(interface_names) != len(set(interface_names)):
                duplicates = [name for name in interface_names if interface_names.count(name) > 1]
                error = InterfaceValidationError(
                    interface_id="multiple",
                    rule_id="structure_validation",
                    validation_type=InterfaceValidationType.STRUCTURAL,
                    error_category="duplicate_names",
                    error_message=f"Duplicate interface names: {duplicates}",
                    actual_value=duplicates,
                    expected_value="unique names",
                    severity=ValidationSeverity.ERROR
                )
                errors.append(error)
            
            # Check for duplicate interface IDs
            interface_ids = [iface.get("id", "") for iface in interfaces]
            if len(interface_ids) != len(set(interface_ids)):
                duplicates = [i_id for i_id in interface_ids if interface_ids.count(i_id) > 1]
                error = InterfaceValidationError(
                    interface_id="multiple",
                    rule_id="structure_validation",
                    validation_type=InterfaceValidationType.STRUCTURAL,
                    error_category="duplicate_ids",
                    error_message=f"Duplicate interface IDs: {duplicates}",
                    actual_value=duplicates,
                    expected_value="unique IDs",
                    severity=ValidationSeverity.ERROR
                )
                errors.append(error)
            
            # Validate each interface structure
            for iface in interfaces:
                interface_id = iface.get("id", "unknown")
                
                # Check required fields
                required_fields = ["id", "name", "type", "direction"]
                for field in required_fields:
                    if field not in iface or iface[field] is None:
                        error = InterfaceValidationError(
                            interface_id=interface_id,
                            rule_id="structure_validation",
                            validation_type=InterfaceValidationType.STRUCTURAL,
                            error_category="missing_field",
                            error_message=f"Required field '{field}' is missing",
                            actual_value=None,
                            expected_value="present",
                            severity=ValidationSeverity.ERROR
                        )
                        errors.append(error)
                
                # Validate parameters structure
                parameters = iface.get("parameters", [])
                if not isinstance(parameters, list):
                    error = InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id="structure_validation",
                        validation_type=InterfaceValidationType.STRUCTURAL,
                        error_category="invalid_parameters",
                        error_message="Parameters must be a list",
                        actual_value=type(parameters).__name__,
                        expected_value="list",
                        severity=ValidationSeverity.ERROR
                    )
                    errors.append(error)
        
        except Exception as e:
            self.logger.error(f"Interface structure validation failed: {str(e)}")
            error = InterfaceValidationError(
                interface_id="structure_validation",
                rule_id="structure_validation_error",
                validation_type=InterfaceValidationType.STRUCTURAL,
                error_category="validation_error",
                error_message=f"Structure validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=ValidationSeverity.ERROR
            )
            errors.append(error)
        
        return errors
    
    async def validate_interface_compatibility(self, interfaces: List[Dict[str, Any]]) -> List[InterfaceValidationError]:
        """Validate interface compatibility and consistency"""
        errors = []
        
        try:
            # Group interfaces by type for compatibility checks
            interfaces_by_type = {}
            for iface in interfaces:
                iface_type = iface.get("type", "")
                if iface_type not in interfaces_by_type:
                    interfaces_by_type[iface_type] = []
                interfaces_by_type[iface_type].append(iface)
            
            # Check API interfaces for endpoint consistency
            api_interfaces = interfaces_by_type.get("api", [])
            for api_iface in api_interfaces:
                interface_id = api_iface.get("id", "unknown")
                endpoint = api_iface.get("endpoint", "")
                
                if not endpoint:
                    error = InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id="compatibility_validation",
                        validation_type=InterfaceValidationType.COMPATIBILITY,
                        error_category="missing_endpoint",
                        error_message="API interface missing endpoint",
                        actual_value=endpoint,
                        expected_value="non-empty endpoint",
                        severity=ValidationSeverity.ERROR
                    )
                    errors.append(error)
            
            # Check service interfaces for protocol consistency
            service_interfaces = interfaces_by_type.get("service", [])
            for service_iface in service_interfaces:
                interface_id = service_iface.get("id", "unknown")
                protocol = service_iface.get("protocol", "")
                
                if not protocol:
                    error = InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id="compatibility_validation",
                        validation_type=InterfaceValidationType.COMPATIBILITY,
                        error_category="missing_protocol",
                        error_message="Service interface missing protocol",
                        actual_value=protocol,
                        expected_value="non-empty protocol",
                        severity=ValidationSeverity.ERROR
                    )
                    errors.append(error)
            
            # Check parameter consistency across similar interfaces
            for iface_type, type_interfaces in interfaces_by_type.items():
                if len(type_interfaces) > 1:
                    # Check for similar parameter patterns
                    param_patterns = []
                    for iface in type_interfaces:
                        param_names = [p.get("name", "") for p in iface.get("parameters", [])]
                        param_patterns.append(tuple(sorted(param_names)))
                    
                    # Flag interfaces with very different parameter patterns
                    unique_patterns = set(param_patterns)
                    if len(unique_patterns) > len(type_interfaces) * 0.5:
                        error = InterfaceValidationError(
                            interface_id="type_analysis",
                            rule_id="compatibility_validation",
                            validation_type=InterfaceValidationType.COMPATIBILITY,
                            error_category="inconsistent_parameters",
                            error_message=f"Inconsistent parameter patterns in {iface_type} interfaces",
                            actual_value=len(unique_patterns),
                            expected_value="consistent patterns",
                            severity=ValidationSeverity.WARNING
                        )
                        errors.append(error)
        
        except Exception as e:
            self.logger.error(f"Interface compatibility validation failed: {str(e)}")
            error = InterfaceValidationError(
                interface_id="compatibility_validation",
                rule_id="compatibility_validation_error",
                validation_type=InterfaceValidationType.COMPATIBILITY,
                error_category="validation_error",
                error_message=f"Compatibility validation error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=ValidationSeverity.ERROR
            )
            errors.append(error)
        
        return errors
    
    async def _parse_validation_rules(self, raw_rules: List[Dict[str, Any]]) -> List[InterfaceValidationRule]:
        """Parse raw validation rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = InterfaceValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    validation_type=InterfaceValidationType(raw_rule.get("validation_type", "structural")),
                    severity=ValidationSeverity(raw_rule.get("severity", "error")),
                    criteria=raw_rule.get("criteria", {}),
                    error_message=raw_rule.get("error_message", "Interface validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse validation rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = InterfaceValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    validation_type=InterfaceValidationType.STRUCTURAL,
                    severity=ValidationSeverity.WARNING,
                    criteria={},
                    error_message=f"Parsing failed: {str(e)}",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _execute_validation_rule(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Execute individual validation rule"""
        errors = []
        
        try:
            # Get validation function for rule type
            type_patterns = self._validation_patterns.get(rule.validation_type, {})
            validation_func = type_patterns.get(rule.criteria.get("validation_function", ""))
            
            if validation_func:
                # Apply validation function
                rule_errors = await validation_func(interfaces, rule)
                errors.extend(rule_errors)
            else:
                # Unknown validation function
                error = InterfaceValidationError(
                    interface_id="multiple",
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="unknown_validation",
                    error_message=f"Unknown validation function: {rule.criteria.get('validation_function')}",
                    actual_value=None,
                    expected_value=None,
                    severity=ValidationSeverity.WARNING
                )
                errors.append(error)
                
        except Exception as e:
            self.logger.error(f"Failed to execute validation rule {rule.id}: {str(e)}")
            error = InterfaceValidationError(
                interface_id="multiple",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="rule_execution_error",
                error_message=f"Rule execution failed: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=ValidationSeverity.ERROR
            )
            errors.append(error)
        
        return errors
    
    async def _sanitize_interfaces(self, interfaces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sanitize interface content for safety"""
        sanitized = []
        
        for iface in interfaces:
            sanitized_iface = iface.copy()
            
            # Remove dangerous content from string fields
            for key, value in sanitized_iface.items():
                if isinstance(value, str):
                    # Remove script tags and dangerous content
                    sanitized_value = value.replace("<script", "").replace("</script>", "")
                    sanitized_iface[key] = sanitized_value
                elif isinstance(value, list):
                    # Sanitize list items
                    sanitized_list = []
                    for item in value:
                        if isinstance(item, str):
                            sanitized_item = item.replace("<script", "").replace("</script>", "")
                            sanitized_list.append(sanitized_item)
                        elif isinstance(item, dict):
                            sanitized_item = await self._sanitize_interface_dict(item)
                            sanitized_list.append(sanitized_item)
                        else:
                            sanitized_list.append(item)
                    sanitized_iface[key] = sanitized_list
                elif isinstance(value, dict):
                    sanitized_iface[key] = await self._sanitize_interface_dict(value)
            
            sanitized.append(sanitized_iface)
        
        return sanitized
    
    async def _sanitize_interface_dict(self, interface_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize interface dictionary content"""
        sanitized = {}
        
        for key, value in interface_dict.items():
            if isinstance(value, str):
                sanitized_value = value.replace("<script", "").replace("</script>", "")
                sanitized[key] = sanitized_value
            elif isinstance(value, dict):
                sanitized[key] = await self._sanitize_interface_dict(value)
            elif isinstance(value, list):
                sanitized_list = []
                for item in value:
                    if isinstance(item, str):
                        sanitized_item = item.replace("<script", "").replace("</script>", "")
                        sanitized_list.append(sanitized_item)
                    elif isinstance(item, dict):
                        sanitized_item = await self._sanitize_interface_dict(item)
                        sanitized_list.append(sanitized_item)
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
            else:
                sanitized[key] = value
        
        return sanitized
    
    # Validation function implementations
    async def _validate_required_fields(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate required fields in interfaces"""
        errors = []
        required_fields = rule.criteria.get("required_fields", ["id", "name", "type"])
        
        for iface in interfaces:
            interface_id = iface.get("id", "unknown")
            for field in required_fields:
                if field not in iface or iface[field] is None:
                    error = InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="missing_field",
                        error_message=f"Required field '{field}' is missing",
                        actual_value=None,
                        expected_value="present",
                        severity=rule.severity
                    )
                    errors.append(error)
        
        return errors
    
    async def _validate_field_types(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate field types in interfaces"""
        errors = []
        field_types = rule.criteria.get("field_types", {})
        
        for iface in interfaces:
            interface_id = iface.get("id", "unknown")
            for field, expected_type in field_types.items():
                if field in iface:
                    value = iface[field]
                    type_mapping = {
                        "string": str,
                        "integer": int,
                        "number": (int, float),
                        "boolean": bool,
                        "array": list,
                        "object": dict
                    }
                    
                    expected_python_type = type_mapping.get(expected_type)
                    if expected_python_type and not isinstance(value, expected_python_type):
                        error = InterfaceValidationError(
                            interface_id=interface_id,
                            rule_id=rule.id,
                            validation_type=rule.validation_type,
                            error_category="type_mismatch",
                            error_message=f"Field '{field}' should be of type {expected_type}",
                            actual_value=type(value).__name__,
                            expected_value=expected_type,
                            severity=rule.severity
                        )
                        errors.append(error)
        
        return errors
    
    async def _validate_interface_format(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate interface format"""
        errors = []
        
        for iface in interfaces:
            interface_id = iface.get("id", "unknown")
            
            # Check ID format
            iface_id_value = iface.get("id", "")
            if not iface_id_value or not isinstance(iface_id_value, str):
                error = InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="invalid_format",
                    error_message="Interface ID must be a non-empty string",
                    actual_value=iface_id_value,
                    expected_value="non-empty string",
                    severity=rule.severity
                )
                errors.append(error)
        
        return errors
    
    async def _validate_naming_conventions(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate naming conventions"""
        errors = []
        naming_pattern = rule.criteria.get("naming_pattern", r"^[a-z][a-z0-9_]*$")
        
        for iface in interfaces:
            interface_id = iface.get("id", "unknown")
            name = iface.get("name", "")
            
            import re
            if not re.match(naming_pattern, name):
                error = InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="naming_convention_violation",
                    error_message=f"Interface name '{name}' does not match naming pattern",
                    actual_value=name,
                    expected_value=naming_pattern,
                    severity=rule.severity
                )
                errors.append(error)
        
        return errors
    
    async def _validate_parameter_consistency(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate parameter consistency"""
        errors = []
        
        # Check if interfaces list is provided
        if not interfaces:
            errors.append(InterfaceValidationError(
                interface_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_interfaces_provided",
                error_message="No interfaces provided for parameter consistency validation",
                actual_value=None,
                expected_value="list of interfaces",
                severity="error"
            ))
            return errors
        
        # Validate parameter consistency across interfaces
        interface_params = {}
        
        for interface in interfaces:
            if not isinstance(interface, dict):
                errors.append(InterfaceValidationError(
                    interface_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_interface_format",
                    error_message="Interface must be a dictionary",
                    actual_value=interface,
                    expected_value="interface dictionary",
                    severity="error"
                ))
                continue
            
            interface_id = interface.get("id", "unknown")
            parameters = interface.get("parameters", [])
            
            # Check parameter consistency
            for param in parameters:
                if not isinstance(param, dict):
                    errors.append(InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="invalid_parameter_format",
                        error_message=f"Parameter must be a dictionary in interface {interface_id}",
                        actual_value=param,
                        expected_value="parameter dictionary",
                        severity="error"
                    ))
                    continue
                
                param_name = param.get("name", "")
                param_type = param.get("type", "")
                param_required = param.get("required", False)
                
                if param_name:
                    if param_name not in interface_params:
                        interface_params[param_name] = {
                            "types": set(),
                            "required_values": set(),
                            "interfaces": []
                        }
                    
                    interface_params[param_name]["types"].add(param_type)
                    interface_params[param_name]["required_values"].add(param_required)
                    interface_params[param_name]["interfaces"].append(interface_id)
        
        # Check for inconsistent parameter types across interfaces
        for param_name, param_info in interface_params.items():
            if len(param_info["types"]) > 1:
                errors.append(InterfaceValidationError(
                    interface_id="multiple",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="inconsistent_parameter_types",
                    error_message=f"Parameter '{param_name}' has inconsistent types across interfaces: {param_info['types']}",
                    actual_value=list(param_info["types"]),
                    expected_value="consistent type across all interfaces",
                    severity="warning"
                ))
            
            if len(param_info["required_values"]) > 1:
                errors.append(InterfaceValidationError(
                    interface_id="multiple",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="inconsistent_parameter_requirements",
                    error_message=f"Parameter '{param_name}' has inconsistent required status across interfaces: {param_info['required_values']}",
                    actual_value=list(param_info["required_values"]),
                    expected_value="consistent required status across all interfaces",
                    severity="warning"
                ))
        
        return errors
    
    async def _validate_documentation_completeness(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate documentation completeness"""
        errors = []
        
        for iface in interfaces:
            interface_id = iface.get("id", "unknown")
            description = iface.get("description", "")
            
            if not description or len(description.strip()) < 10:
                error = InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="incomplete_documentation",
                    error_message="Interface description is too short or missing",
                    actual_value=len(description) if description else 0,
                    expected_value=">= 10 characters",
                    severity=ValidationSeverity.WARNING
                )
                errors.append(error)
        
        return errors
    
    async def _validate_authentication_required(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate authentication requirements"""
        errors = []
        require_auth = rule.criteria.get("require_authentication", False)
        
        if require_auth:
            for iface in interfaces:
                interface_id = iface.get("id", "unknown")
                auth = iface.get("authentication", {})
                
                if not auth:
                    error = InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="missing_authentication",
                        error_message="Interface requires authentication but none specified",
                        actual_value=auth,
                        expected_value="authentication configuration",
                        severity=ValidationSeverity.ERROR
                    )
                    errors.append(error)
        
        return errors
    
    async def _validate_authorization_policies(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate authorization policies"""
        errors = []
        
        # Check if interfaces list is provided
        if not interfaces:
            errors.append(InterfaceValidationError(
                interface_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_interfaces_provided",
                error_message="No interfaces provided for authorization policy validation",
                actual_value=None,
                expected_value="list of interfaces",
                severity="error"
            ))
            return errors
        
        # Validate authorization policies across interfaces
        for interface in interfaces:
            if not isinstance(interface, dict):
                errors.append(InterfaceValidationError(
                    interface_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_interface_format",
                    error_message="Interface must be a dictionary",
                    actual_value=interface,
                    expected_value="interface dictionary",
                    severity="error"
                ))
                continue
            
            interface_id = interface.get("id", "unknown")
            authorization = interface.get("authorization", {})
            
            # Check if authorization is configured for sensitive operations
            operations = interface.get("operations", [])
            sensitive_operations = ["delete", "update", "create", "admin"]
            
            for operation in operations:
                if isinstance(operation, dict):
                    op_name = operation.get("name", "")
                    if op_name.lower() in sensitive_operations:
                        op_auth = operation.get("authorization", {})
                        if not op_auth:
                            errors.append(InterfaceValidationError(
                                interface_id=interface_id,
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="missing_authorization_for_sensitive_operation",
                                error_message=f"Sensitive operation '{op_name}' missing authorization policy",
                                actual_value=op_auth,
                                expected_value="authorization configuration",
                                severity="error"
                            ))
                        else:
                            # Validate authorization policy structure
                            if "roles" not in op_auth and "permissions" not in op_auth:
                                errors.append(InterfaceValidationError(
                                    interface_id=interface_id,
                                    rule_id=rule.rule_id,
                                    validation_type=rule.validation_type,
                                    error_category="incomplete_authorization_policy",
                                    error_message=f"Authorization policy for '{op_name}' must specify roles or permissions",
                                    actual_value=op_auth,
                                    expected_value="include roles or permissions",
                                    severity="warning"
                                ))
            
            # Check for role-based access control
            if authorization:
                roles = authorization.get("roles", [])
                if not roles:
                    errors.append(InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="no_roles_defined",
                        error_message="Authorization policy should define at least one role",
                        actual_value=roles,
                        expected_value="list of roles",
                        severity="warning"
                    ))
                else:
                    # Validate role definitions
                    for role in roles:
                        if isinstance(role, dict):
                            if "name" not in role:
                                errors.append(InterfaceValidationError(
                                    interface_id=interface_id,
                                    rule_id=rule.rule_id,
                                    validation_type=rule.validation_type,
                                    error_category="role_without_name",
                                    error_message="Role definition must include a name",
                                    actual_value=role,
                                    expected_value="include name field",
                                    severity="error"
                                ))
                            
                            if "permissions" not in role:
                                errors.append(InterfaceValidationError(
                                    interface_id=interface_id,
                                    rule_id=rule.rule_id,
                                    validation_type=rule.validation_type,
                                    error_category="role_without_permissions",
                                    error_message=f"Role '{role.get('name', 'unnamed')}' must define permissions",
                                    actual_value=role,
                                    expected_value="include permissions field",
                                    severity="warning"
                                ))
        
        return errors
    
    async def _validate_input_validation(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate input validation"""
        errors = []
        
        for iface in interfaces:
            interface_id = iface.get("id", "unknown")
            parameters = iface.get("parameters", [])
            
            for param in parameters:
                param_name = param.get("name", "")
                validation_rules = param.get("validation_rules", {})
                
                if not validation_rules:
                    error = InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="missing_input_validation",
                        error_message=f"Parameter '{param_name}' missing validation rules",
                        actual_value=validation_rules,
                        expected_value="validation rules",
                        severity=ValidationSeverity.WARNING
                    )
                    errors.append(error)
        
        return errors
    
    async def _validate_version_compatibility(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate version compatibility"""
        errors = []
        
        # Check if interfaces list is provided
        if not interfaces:
            errors.append(InterfaceValidationError(
                interface_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_interfaces_provided",
                error_message="No interfaces provided for version compatibility validation",
                actual_value=None,
                expected_value="list of interfaces",
                severity="error"
            ))
            return errors
        
        # Validate version compatibility across interfaces
        interface_versions = {}
        
        for interface in interfaces:
            if not isinstance(interface, dict):
                errors.append(InterfaceValidationError(
                    interface_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_interface_format",
                    error_message="Interface must be a dictionary",
                    actual_value=interface,
                    expected_value="interface dictionary",
                    severity="error"
                ))
                continue
            
            interface_id = interface.get("id", "unknown")
            version = interface.get("version", "")
            
            if not version:
                errors.append(InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_version",
                    error_message="Interface version is missing",
                    actual_value=version,
                    expected_value="semantic version (e.g., 1.0.0)",
                    severity="warning"
                ))
            else:
                # Validate semantic version format
                import re
                semver_pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9\-\.]+)?(\+[a-zA-Z0-9\-\.]+)?$'
                if not re.match(semver_pattern, version):
                    errors.append(InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="invalid_version_format",
                        error_message=f"Interface version '{version}' is not in semantic version format",
                        actual_value=version,
                        expected_value="semantic version (e.g., 1.0.0)",
                        severity="warning"
                    ))
                
                # Track versions for compatibility checking
                if interface_id not in interface_versions:
                    interface_versions[interface_id] = []
                interface_versions[interface_id].append(version)
        
        # Check for version conflicts
        for interface_id, versions in interface_versions.items():
            if len(set(versions)) > 1:
                errors.append(InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="version_conflict",
                    error_message=f"Interface '{interface_id}' has conflicting versions: {set(versions)}",
                    actual_value=versions,
                    expected_value="consistent version across all instances",
                    severity="error"
                ))
        
        # Validate version dependencies
        for interface in interfaces:
            interface_id = interface.get("id", "unknown")
            dependencies = interface.get("dependencies", [])
            
            for dependency in dependencies:
                if isinstance(dependency, dict):
                    dep_name = dependency.get("name", "")
                    dep_version_constraint = dependency.get("version_constraint", "")
                    
                    if dep_version_constraint:
                        # Basic validation of version constraint format
                        valid_operators = ["==", "!=", ">=", "<=", ">", "<", "~=", "^"]
                        has_valid_operator = any(op in dep_version_constraint for op in valid_operators)
                        
                        if not has_valid_operator and not re.match(semver_pattern, dep_version_constraint):
                            errors.append(InterfaceValidationError(
                                interface_id=interface_id,
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="invalid_version_constraint",
                                error_message=f"Invalid version constraint for dependency '{dep_name}': {dep_version_constraint}",
                                actual_value=dep_version_constraint,
                                expected_value="valid version constraint (e.g., >=1.0.0, ^2.3.0)",
                                severity="warning"
                            ))
        
        return errors
    
    async def _validate_backward_compatibility(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate backward compatibility"""
        errors = []
        
        # Check if interfaces list is provided
        if not interfaces:
            errors.append(InterfaceValidationError(
                interface_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_interfaces_provided",
                error_message="No interfaces provided for backward compatibility validation",
                actual_value=None,
                expected_value="list of interfaces",
                severity="error"
            ))
            return errors
        
        # Group interfaces by name to check version compatibility
        interface_groups = {}
        
        for interface in interfaces:
            if not isinstance(interface, dict):
                errors.append(InterfaceValidationError(
                    interface_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_interface_format",
                    error_message="Interface must be a dictionary",
                    actual_value=interface,
                    expected_value="interface dictionary",
                    severity="error"
                ))
                continue
            
            interface_id = interface.get("id", "unknown")
            interface_name = interface.get("name", interface_id)
            version = interface.get("version", "")
            
            if interface_name not in interface_groups:
                interface_groups[interface_name] = []
            interface_groups[interface_name].append(interface)
        
        # Check backward compatibility for each interface group
        for interface_name, group_interfaces in interface_groups.items():
            if len(group_interfaces) > 1:
                # Sort interfaces by version (assuming semantic versioning)
                sorted_interfaces = sorted(group_interfaces, key=lambda x: x.get("version", "0.0.0"))
                
                for i in range(1, len(sorted_interfaces)):
                    current = sorted_interfaces[i]
                    previous = sorted_interfaces[i-1]
                    
                    current_id = current.get("id", "unknown")
                    current_version = current.get("version", "")
                    previous_version = previous.get("version", "")
                    
                    # Check for breaking changes in parameters
                    current_params = {p.get("name"): p for p in current.get("parameters", [])}
                    previous_params = {p.get("name"): p for p in previous.get("parameters", [])}
                    
                    # Check for removed required parameters (breaking change)
                    for param_name, param in previous_params.items():
                        if param.get("required", False) and param_name not in current_params:
                            errors.append(InterfaceValidationError(
                                interface_id=current_id,
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="breaking_change_removed_required_parameter",
                                error_message=f"Version {current_version} removed required parameter '{param_name}' that existed in {previous_version}",
                                actual_value=None,
                                expected_value=f"keep parameter '{param_name}' for backward compatibility",
                                severity="error"
                            ))
                    
                    # Check for type changes in existing parameters (breaking change)
                    for param_name, param in current_params.items():
                        if param_name in previous_params:
                            current_type = param.get("type", "")
                            previous_type = previous_params[param_name].get("type", "")
                            
                            if current_type != previous_type:
                                errors.append(InterfaceValidationError(
                                    interface_id=current_id,
                                    rule_id=rule.rule_id,
                                    validation_type=rule.validation_type,
                                    error_category="breaking_change_parameter_type",
                                    error_message=f"Version {current_version} changed type of parameter '{param_name}' from {previous_type} to {current_type}",
                                    actual_value=current_type,
                                    expected_value=previous_type,
                                    severity="error"
                                ))
                    
                    # Check for operations changes
                    current_operations = {op.get("name"): op for op in current.get("operations", [])}
                    previous_operations = {op.get("name"): op for op in previous.get("operations", [])}
                    
                    # Check for removed operations (breaking change)
                    for op_name in previous_operations:
                        if op_name not in current_operations:
                            errors.append(InterfaceValidationError(
                                interface_id=current_id,
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="breaking_change_removed_operation",
                                error_message=f"Version {current_version} removed operation '{op_name}' that existed in {previous_version}",
                                actual_value=None,
                                expected_value=f"keep operation '{op_name}' for backward compatibility",
                                severity="warning"
                            ))
        
        return errors
    
    async def _validate_api_compatibility(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate API compatibility"""
        errors = []
        
        # Check if interfaces list is provided
        if not interfaces:
            errors.append(InterfaceValidationError(
                interface_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_interfaces_provided",
                error_message="No interfaces provided for API compatibility validation",
                actual_value=None,
                expected_value="list of interfaces",
                severity="error"
            ))
            return errors
        
        # Validate API compatibility across interfaces
        for interface in interfaces:
            if not isinstance(interface, dict):
                errors.append(InterfaceValidationError(
                    interface_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_interface_format",
                    error_message="Interface must be a dictionary",
                    actual_value=interface,
                    expected_value="interface dictionary",
                    severity="error"
                ))
                continue
            
            interface_id = interface.get("id", "unknown")
            api_spec = interface.get("api_spec", {})
            
            if not api_spec:
                errors.append(InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_api_spec",
                    error_message="API specification is missing",
                    actual_value=api_spec,
                    expected_value="API specification",
                    severity="warning"
                ))
                continue
            
            # Validate API specification format
            api_format = api_spec.get("format", "")
            supported_formats = ["openapi3", "openapi2", "swagger", "raml"]
            if api_format not in supported_formats:
                errors.append(InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="unsupported_api_format",
                    error_message=f"Unsupported API format: {api_format}",
                    actual_value=api_format,
                    expected_value="one of: " + ", ".join(supported_formats),
                    severity="warning"
                ))
            
            # Validate endpoint consistency
            endpoints = api_spec.get("endpoints", [])
            if not endpoints:
                errors.append(InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="no_endpoints_defined",
                    error_message="No endpoints defined in API specification",
                    actual_value=endpoints,
                    expected_value="list of endpoints",
                    severity="warning"
                ))
            else:
                # Check for duplicate endpoints
                endpoint_paths = []
                for endpoint in endpoints:
                    if isinstance(endpoint, dict):
                        path = endpoint.get("path", "")
                        method = endpoint.get("method", "")
                        
                        if path and method:
                            endpoint_key = f"{method.upper()} {path}"
                            if endpoint_key in endpoint_paths:
                                errors.append(InterfaceValidationError(
                                    interface_id=interface_id,
                                    rule_id=rule.rule_id,
                                    validation_type=rule.validation_type,
                                    error_category="duplicate_endpoint",
                                    error_message=f"Duplicate endpoint defined: {endpoint_key}",
                                    actual_value=endpoint_key,
                                    expected_value="unique endpoints",
                                    severity="error"
                                ))
                            else:
                                endpoint_paths.append(endpoint_key)
                
                # Validate response formats
                for endpoint in endpoints:
                    if isinstance(endpoint, dict):
                        endpoint_path = endpoint.get("path", "")
                        endpoint_method = endpoint.get("method", "")
                        responses = endpoint.get("responses", {})
                        
                        if not responses:
                            errors.append(InterfaceValidationError(
                                interface_id=interface_id,
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="endpoint_no_responses",
                                error_message=f"Endpoint {endpoint_method} {endpoint_path} has no response definitions",
                                actual_value=responses,
                                expected_value="response definitions",
                                severity="warning"
                            ))
                        else:
                            # Check for consistent response formats
                            response_formats = set()
                            for status_code, response in responses.items():
                                if isinstance(response, dict):
                                    response_format = response.get("format", "json")
                                    response_formats.add(response_format)
                            
                            if len(response_formats) > 1:
                                errors.append(InterfaceValidationError(
                                    interface_id=interface_id,
                                    rule_id=rule.rule_id,
                                    validation_type=rule.validation_type,
                                    error_category="inconsistent_response_formats",
                                    error_message=f"Endpoint {endpoint_method} {endpoint_path} has inconsistent response formats: {response_formats}",
                                    actual_value=list(response_formats),
                                    expected_value="consistent response format",
                                    severity="warning"
                                ))
        
        return errors
    
    async def _validate_protocol_standards(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate protocol standards"""
        errors = []
        allowed_protocols = rule.criteria.get("allowed_protocols", ["http", "https", "grpc"])
        
        for iface in interfaces:
            interface_id = iface.get("id", "unknown")
            protocol = iface.get("protocol", "")
            
            if protocol and protocol not in allowed_protocols:
                error = InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="invalid_protocol",
                    error_message=f"Protocol '{protocol}' not in allowed protocols",
                    actual_value=protocol,
                    expected_value=f"one of {allowed_protocols}",
                    severity=ValidationSeverity.ERROR
                )
                errors.append(error)
        
        return errors
    
    async def _validate_endpoint_validation(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate endpoint validation"""
        errors = []
        
        # Check if interfaces list is provided
        if not interfaces:
            errors.append(InterfaceValidationError(
                interface_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_interfaces_provided",
                error_message="No interfaces provided for endpoint validation",
                actual_value=None,
                expected_value="list of interfaces",
                severity="error"
            ))
            return errors
        
        # Validate endpoint configurations across interfaces
        for interface in interfaces:
            if not isinstance(interface, dict):
                errors.append(InterfaceValidationError(
                    interface_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_interface_format",
                    error_message="Interface must be a dictionary",
                    actual_value=interface,
                    expected_value="interface dictionary",
                    severity="error"
                ))
                continue
            
            interface_id = interface.get("id", "unknown")
            endpoints = interface.get("endpoints", [])
            
            if not endpoints:
                errors.append(InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="no_endpoints_defined",
                    error_message="No endpoints defined for interface",
                    actual_value=endpoints,
                    expected_value="list of endpoints",
                    severity="warning"
                ))
                continue
            
            # Validate each endpoint
            for endpoint in endpoints:
                if not isinstance(endpoint, dict):
                    errors.append(InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="invalid_endpoint_format",
                        error_message="Endpoint must be a dictionary",
                        actual_value=endpoint,
                        expected_value="endpoint dictionary",
                        severity="error"
                    ))
                    continue
                
                # Check required endpoint fields
                path = endpoint.get("path", "")
                method = endpoint.get("method", "")
                
                if not path:
                    errors.append(InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="endpoint_path_missing",
                        error_message="Endpoint path is required",
                        actual_value=path,
                        expected_value="endpoint path (e.g., /api/users)",
                        severity="error"
                    ))
                
                if not method:
                    errors.append(InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="endpoint_method_missing",
                        error_message="Endpoint method is required",
                        actual_value=method,
                        expected_value="HTTP method (GET, POST, PUT, DELETE)",
                        severity="error"
                    ))
                else:
                    # Validate HTTP method
                    valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
                    if method.upper() not in valid_methods:
                        errors.append(InterfaceValidationError(
                            interface_id=interface_id,
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="invalid_http_method",
                            error_message=f"Invalid HTTP method: {method}",
                            actual_value=method,
                            expected_value="one of: " + ", ".join(valid_methods),
                            severity="error"
                        ))
                
                # Validate path format
                if path and not path.startswith("/"):
                    errors.append(InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="invalid_path_format",
                        error_message=f"Endpoint path must start with '/': {path}",
                        actual_value=path,
                        expected_value="path starting with '/'",
                        severity="warning"
                    ))
                
                # Check for parameter validation in endpoints
                parameters = endpoint.get("parameters", [])
                for param in parameters:
                    if isinstance(param, dict):
                        param_name = param.get("name", "")
                        param_type = param.get("type", "")
                        
                        if not param_name:
                            errors.append(InterfaceValidationError(
                                interface_id=interface_id,
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="endpoint_parameter_name_missing",
                                error_message="Endpoint parameter name is required",
                                actual_value=param_name,
                                expected_value="parameter name",
                                severity="error"
                            ))
                        
                        if not param_type:
                            errors.append(InterfaceValidationError(
                                interface_id=interface_id,
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="endpoint_parameter_type_missing",
                                error_message=f"Parameter '{param_name}' type is required",
                                actual_value=param_type,
                                expected_value="parameter type",
                                severity="warning"
                            ))
        
        return errors
    
    async def _validate_method_validation(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate method validation"""
        errors = []
        allowed_methods = rule.criteria.get("allowed_methods", ["GET", "POST", "PUT", "DELETE"])
        
        for iface in interfaces:
            interface_id = iface.get("id", "unknown")
            method = iface.get("method", "")
            
            if method and method not in allowed_methods:
                error = InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="invalid_method",
                    error_message=f"Method '{method}' not in allowed methods",
                    actual_value=method,
                    expected_value=f"one of {allowed_methods}",
                    severity=ValidationSeverity.ERROR
                )
                errors.append(error)
        
        return errors
    
    async def _validate_documentation_presence(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate documentation presence"""
        errors = []
        
        for iface in interfaces:
            interface_id = iface.get("id", "unknown")
            documentation = iface.get("documentation", {})
            
            if not documentation:
                error = InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="missing_documentation",
                    error_message="Interface missing documentation",
                    actual_value=documentation,
                    expected_value="documentation object",
                    severity=ValidationSeverity.WARNING
                )
                errors.append(error)
        
        return errors
    
    async def _validate_documentation_quality(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate documentation quality"""
        errors = []
        
        # Check if interfaces list is provided
        if not interfaces:
            errors.append(InterfaceValidationError(
                interface_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_interfaces_provided",
                error_message="No interfaces provided for documentation quality validation",
                actual_value=None,
                expected_value="list of interfaces",
                severity="error"
            ))
            return errors
        
        # Validate documentation quality across interfaces
        for interface in interfaces:
            if not isinstance(interface, dict):
                errors.append(InterfaceValidationError(
                    interface_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_interface_format",
                    error_message="Interface must be a dictionary",
                    actual_value=interface,
                    expected_value="interface dictionary",
                    severity="error"
                ))
                continue
            
            interface_id = interface.get("id", "unknown")
            description = interface.get("description", "")
            
            # Check description length and quality
            if not description:
                errors.append(InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_description",
                    error_message="Interface description is missing",
                    actual_value=description,
                    expected_value="interface description",
                    severity="warning"
                ))
            elif len(description.strip()) < 20:
                errors.append(InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_description_length",
                    error_message="Interface description is too short",
                    actual_value=len(description),
                    expected_value=">= 20 characters",
                    severity="warning"
                ))
            elif not any(keyword in description.lower() for keyword in ["api", "interface", "service", "endpoint", "method"]):
                errors.append(InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="poor_description_quality",
                    error_message="Interface description lacks relevant keywords",
                    actual_value=description,
                    expected_value="description with API/interface keywords",
                    severity="warning"
                ))
            
            # Check for parameter documentation
            parameters = interface.get("parameters", [])
            for param in parameters:
                if isinstance(param, dict):
                    param_name = param.get("name", "")
                    param_description = param.get("description", "")
                    
                    if param_name and not param_description:
                        errors.append(InterfaceValidationError(
                            interface_id=interface_id,
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="missing_parameter_documentation",
                            error_message=f"Parameter '{param_name}' lacks description",
                            actual_value=param_description,
                            expected_value="parameter description",
                            severity="warning"
                        ))
            
            # Check for examples
            examples = interface.get("examples", [])
            if not examples:
                errors.append(InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_examples",
                    error_message="Interface lacks usage examples",
                    actual_value=examples,
                    expected_value="usage examples",
                    severity="warning"
                ))
        
        return errors
    
    async def _validate_example_completeness(
        self, 
        interfaces: List[Dict[str, Any]], 
        rule: InterfaceValidationRule
    ) -> List[InterfaceValidationError]:
        """Validate example completeness"""
        errors = []
        
        # Check if interfaces list is provided
        if not interfaces:
            errors.append(InterfaceValidationError(
                interface_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_interfaces_provided",
                error_message="No interfaces provided for example completeness validation",
                actual_value=None,
                expected_value="list of interfaces",
                severity="error"
            ))
            return errors
        
        # Validate example completeness across interfaces
        for interface in interfaces:
            if not isinstance(interface, dict):
                errors.append(InterfaceValidationError(
                    interface_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_interface_format",
                    error_message="Interface must be a dictionary",
                    actual_value=interface,
                    expected_value="interface dictionary",
                    severity="error"
                ))
                continue
            
            interface_id = interface.get("id", "unknown")
            examples = interface.get("examples", [])
            
            if not examples:
                errors.append(InterfaceValidationError(
                    interface_id=interface_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="no_examples_provided",
                    error_message="No examples provided for interface",
                    actual_value=examples,
                    expected_value="list of examples",
                    severity="warning"
                ))
                continue
            
            # Validate each example
            for i, example in enumerate(examples):
                if not isinstance(example, dict):
                    errors.append(InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="invalid_example_format",
                        error_message=f"Example {i} must be a dictionary",
                        actual_value=example,
                        expected_value="example dictionary",
                        severity="error"
                    ))
                    continue
                
                # Check for required example fields
                if "request" not in example:
                    errors.append(InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="example_request_missing",
                        error_message=f"Example {i} missing request field",
                        actual_value=example,
                        expected_value="include request field",
                        severity="warning"
                    ))
                
                if "response" not in example:
                    errors.append(InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="example_response_missing",
                        error_message=f"Example {i} missing response field",
                        actual_value=example,
                        expected_value="include response field",
                        severity="warning"
                    ))
                
                # Check for example description
                description = example.get("description", "")
                if not description or len(description.strip()) < 10:
                    errors.append(InterfaceValidationError(
                        interface_id=interface_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="example_description_missing",
                        error_message=f"Example {i} description is missing or too short",
                        actual_value=description,
                        expected_value=">= 10 characters",
                        severity="warning"
                    ))
                
                # Validate request structure
                request = example.get("request", {})
                if isinstance(request, dict):
                    if "method" not in request:
                        errors.append(InterfaceValidationError(
                            interface_id=interface_id,
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="example_request_method_missing",
                            error_message=f"Example {i} request missing HTTP method",
                            actual_value=request,
                            expected_value="include HTTP method",
                            severity="warning"
                        ))
                    
                    if "url" not in request:
                        errors.append(InterfaceValidationError(
                            interface_id=interface_id,
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="example_request_url_missing",
                            error_message=f"Example {i} request missing URL",
                            actual_value=request,
                            expected_value="include request URL",
                            severity="warning"
                        ))
        
        return errors
    
    async def _generate_interface_summary(self, interfaces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate interface summary"""
        interface_types = {}
        total_parameters = 0
        directions = {}
        
        for iface in interfaces:
            iface_type = iface.get("type", "unknown")
            interface_types[iface_type] = interface_types.get(iface_type, 0) + 1
            
            parameters = iface.get("parameters", [])
            total_parameters += len(parameters)
            
            direction = iface.get("direction", "unknown")
            directions[direction] = directions.get(direction, 0) + 1
        
        return {
            "total_interfaces": len(interfaces),
            "interface_types": interface_types,
            "total_parameters": total_parameters,
            "average_parameters_per_interface": total_parameters / len(interfaces) if interfaces else 0,
            "directions": directions
        }
    
    async def _generate_validation_summary(
        self, 
        layer_name: str,
        errors: List[InterfaceValidationError]
    ) -> Dict[str, Any]:
        """Generate validation summary"""
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
            "most_common_error": max(error_categories) if error_categories else None
        }
    
    def _extract_security_flags(self, errors: List[InterfaceValidationError]) -> List[str]:
        """Extract security flags from validation errors"""
        security_flags = []
        
        for error in errors:
            if error.validation_type == InterfaceValidationType.SECURITY:
                security_flags.append("security_validation_failed")
            elif "authentication" in error.error_category:
                security_flags.append("authentication_issue")
            elif "authorization" in error.error_category:
                security_flags.append("authorization_issue")
        
        return security_flags
    
    async def _estimate_validation_complexity(self, request: LayerInterfacesValidationRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.interfaces) // 3
        
        # Add complexity for validation rules
        complexity_score += len(request.validation_rules) // 2
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_interfaces_risk_score(self, validation_result: InterfacesValidationResult) -> float:
        """Calculate risk score for the interfaces (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for validation errors
        if validation_result.validation_errors:
            risk_score += 0.3
        
        # Increase risk for security validation failures
        security_errors = [e for e in validation_result.validation_errors if e.validation_type == InterfaceValidationType.SECURITY]
        if security_errors:
            risk_score += 0.4
        
        # Increase risk for many interfaces
        total_interfaces = validation_result.interface_summary.get("total_interfaces", 0)
        if total_interfaces > 20:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_interfaces_id(self, request: LayerInterfacesValidationRequest, result: InterfacesValidationResult) -> str:
        """Generate unique interfaces identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.layer_name}:{len(result.validation_errors)}:{result.interface_summary.get('total_interfaces', 0)}:{timestamp}"
        return f"interfaces_validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: LayerInterfacesValidationRequest, error: str) -> LayerInterfacesValidationResult:
        """Create safe fallback validation when main validation fails"""
        fallback_error = InterfaceValidationError(
            interface_id="fallback",
            rule_id="fallback_rule",
            validation_type=InterfaceValidationType.STRUCTURAL,
            error_category="validation_failed",
            error_message=f"Validation failed: {error}",
            actual_value="fallback",
            expected_value="success",
            severity=ValidationSeverity.WARNING
        )
        
        fallback_result = InterfacesValidationResult(
            is_valid=False,
            validation_errors=[fallback_error],
            validation_warnings=[],
            interface_summary={"fallback": True},
            validation_summary={"fallback": True},
            security_flags=["fallback_mode"]
        )
        
        return LayerInterfacesValidationResult(
            validation_result=fallback_result,
            validated_interfaces=[],
            validation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            interfaces_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when interfaces violate safety policies"""
    pass


class LayerInterfacesValidationError(Exception):
    """Raised for general layer interfaces validation errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_interfaces_validator(safety_policy: Optional[LayerInterfacesSafetyPolicy] = None) -> LayerInterfacesValidator:
    """Factory function to create LayerInterfacesValidator with optional custom safety policy"""
    return LayerInterfacesValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_interfaces_request(request: LayerInterfacesValidationRequest) -> tuple[bool, Optional[str]]:
    """Validate layer interfaces request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.interfaces, list):
            return False, "Interfaces must be a list"
        
        if not isinstance(request.validation_rules, list):
            return False, "Validation rules must be a list"
        
        if not isinstance(request.validation_options, dict):
            return False, "Validation options must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
