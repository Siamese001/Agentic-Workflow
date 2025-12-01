"""
L1 Cognitive Planning - Registry Context Validation

Implements pure planning operations for validating registry context data
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

class ContextValidationType(str, Enum):
    """Supported context validation types with L5 safety validation"""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    BUSINESS_LOGIC = "business_logic"
    DATA_INTEGRITY = "data_integrity"


class ContextValidationLevel(str, Enum):
    """Context validation levels with L5 safety enforcement"""
    STRICT = "strict"
    STANDARD = "standard"
    LENIENT = "lenient"
    MINIMAL = "minimal"


class RegistryContextSafetyPolicy(BaseModel):
    """L5 Safety policy for registry context validation operations"""
    max_context_size: int = Field(default=524288, description="Maximum context size in bytes (512KB)")
    max_validation_depth: int = Field(default=8, description="Maximum validation nesting depth")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in ContextValidationType])
    allowed_validation_levels: List[str] = Field(default_factory=lambda: [t.value for t in ContextValidationLevel])
    require_context_integrity: bool = Field(default=True)
    prevent_context_injection: bool = Field(default=True)
    sanitize_context_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class RegistryContextSafetyValidator:
    """L5 Safety validator for registry context validation operations"""
    
    def __init__(self, policy: RegistryContextSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.RegistryContextSafetyValidator")
        
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
        self._privileged_contexts = [
            "system", "admin", "root", "kernel", "driver",
            "hardware", "bios", "firmware", "bootloader"
        ]
    
    def validate_context_input(self, context_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates context input against L5 safety policies"""
        try:
            # Check context size
            context_data = context_input.get("context", {})
            context_size = len(str(context_data).encode('utf-8'))
            
            if context_size > self.policy.max_context_size:
                error_msg = f"Context too large: {context_size} > {self.policy.max_context_size} bytes"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation type
            validation_type = context_input.get("validation_type", "")
            if validation_type not in self.policy.allowed_validation_types:
                error_msg = f"Prohibited validation type: {validation_type}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation level
            validation_level = context_input.get("validation_level", "")
            if validation_level not in self.policy.allowed_validation_levels:
                error_msg = f"Prohibited validation level: {validation_level}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation depth
            max_depth = self._calculate_context_depth(context_data)
            if max_depth > self.policy.max_validation_depth:
                error_msg = f"Context nesting too deep: {max_depth} > {self.policy.max_validation_depth}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(context_data).lower()
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
            
            # Check for privileged contexts
            for privileged in self._privileged_contexts:
                if privileged in content_str:
                    self.logger.warning(f"Privileged context detected: {privileged}")
                    # Additional validation would be required in production
            
            return True, None
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.error(f"Safety validation failed: {error_msg}")
            if self.policy.fail_closed:
                return False, error_msg
            return True, error_msg
    
    def _calculate_context_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of context structure"""
        if current_depth > self.policy.max_validation_depth:
            return current_depth
        
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_context_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_context_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth


# ============================================================================
# L1 COGNITIVE PLANNING INTERFACES
# ============================================================================

@dataclass
class ContextValidationRule:
    """Individual validation rule for registry context"""
    id: str
    validation_type: ContextValidationType
    validation_level: ContextValidationLevel
    context_path: str
    rule_definition: str
    criteria: Dict[str, Any]
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class RegistryContextValidationRequest:
    """Input request for registry context validation operations"""
    registry_context: Dict[str, Any]
    validation_rules: List[Dict[str, Any]]
    validation_type: ContextValidationType
    validation_level: ContextValidationLevel
    target_layer: str
    context: Dict[str, Any]
    validation_options: Dict[str, Any] = field(default_factory=dict)
    security_requirements: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class ContextValidationError:
    """Individual context validation error"""
    context_path: str
    rule_id: str
    validation_type: ContextValidationType
    error_category: str
    error_message: str
    actual_value: Any
    expected_value: Any
    severity: str


@dataclass
class ContextValidationResult:
    """Result of registry context validation"""
    is_valid: bool
    validation_errors: List[ContextValidationError]
    validation_warnings: List[ContextValidationError]
    compliance_score: float
    validation_summary: Dict[str, Any]
    security_flags: List[str]
    integrity_checks: Dict[str, bool]


@dataclass
class RegistryContextValidationResult:
    """Output result from registry context validation operations"""
    validation_result: ContextValidationResult
    validated_context: Dict[str, Any]
    validation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    context_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class RegistryContextValidatorInterface(ABC):
    """Abstract interface for registry context validation operations"""
    
    @abstractmethod
    async def validate_registry_context(self, request: RegistryContextValidationRequest) -> RegistryContextValidationResult:
        """Validate registry context against rules and criteria"""
        pass
    
    @abstractmethod
    async def validate_context_structure(self, context: Dict[str, Any], rules: List[ContextValidationRule]) -> List[ContextValidationError]:
        """Validate context structure and organization"""
        pass
    
    @abstractmethod
    async def validate_context_integrity(self, context: Dict[str, Any]) -> Dict[str, bool]:
        """Validate context data integrity and consistency"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class RegistryContextValidator(RegistryContextValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating registry context.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[RegistryContextSafetyPolicy] = None):
        self.safety_policy = safety_policy or RegistryContextSafetyPolicy()
        self.safety_validator = RegistryContextSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Context validation patterns and rules
        self._validation_patterns = {
            ContextValidationType.STRUCTURAL: {
                "required_sections": self._validate_required_sections,
                "section_types": self._validate_section_types,
                "field_presence": self._validate_field_presence,
                "array_constraints": self._validate_array_constraints
            },
            ContextValidationType.SEMANTIC: {
                "naming_conventions": self._validate_naming_conventions,
                "value_ranges": self._validate_value_ranges,
                "format_patterns": self._validate_format_patterns,
                "semantic_consistency": self._validate_semantic_consistency
            },
            ContextValidationType.SECURITY: {
                "access_controls": self._validate_access_controls,
                "encryption_status": self._validate_encryption_status,
                "audit_trail": self._validate_audit_trail,
                "security_headers": self._validate_security_headers
            },
            ContextValidationType.COMPLIANCE: {
                "regulatory_compliance": self._validate_regulatory_compliance,
                "policy_adherence": self._validate_policy_adherence,
                "documentation_completeness": self._validate_documentation_completeness,
                "version_compliance": self._validate_version_compliance
            },
            ContextValidationType.BUSINESS_LOGIC: {
                "workflow_compliance": self._validate_workflow_compliance,
                "business_rules": self._validate_business_rules,
                "state_transitions": self._validate_state_transitions,
                "dependency_validation": self._validate_dependency_validation
            },
            ContextValidationType.DATA_INTEGRITY: {
                "checksum_validation": self._validate_checksum_validation,
                "referential_integrity": self._validate_referential_integrity,
                "temporal_consistency": self._validate_temporal_consistency,
                "data_consistency": self._validate_data_consistency
            }
        }
        
        self.logger.info("RegistryContextValidator initialized with L5 safety policies")
    
    async def validate_registry_context(self, request: RegistryContextValidationRequest) -> RegistryContextValidationResult:
        """
        Validate registry context against rules and criteria.
        
        Args:
            request: Registry context validation request with context and validation rules
            
        Returns:
            RegistryContextValidationResult: Structured result with validation outcome and details
            
        Raises:
            ValidationError: If registry context validation fails
            SafetyError: If context violates safety policies
        """
        self.logger.info(f"Validating registry context for layer {request.target_layer} with {request.validation_type} validation")
        
        try:
            # L5 Safety validation
            context_input = {
                "context": request.registry_context,
                "validation_type": request.validation_type.value,
                "validation_level": request.validation_level.value
            }
            
            is_valid, error_msg = self.safety_validator.validate_context_input(context_input)
            if not is_valid:
                raise SafetyError(f"Registry context safety validation failed: {error_msg}")
            
            # Sanitize context if required
            sanitized_context = request.registry_context
            if self.safety_policy.sanitize_context_data:
                sanitized_context = await self._sanitize_context(request.registry_context)
            
            # Parse validation rules
            parsed_rules = await self._parse_validation_rules(request.validation_rules)
            
            # Validate context structure
            structure_errors = await self.validate_context_structure(sanitized_context, parsed_rules)
            
            # Validate context integrity
            integrity_checks = await self.validate_context_integrity(sanitized_context)
            
            # Separate errors and warnings based on severity
            validation_errors = [e for e in structure_errors if e.severity in ["error", "critical"]]
            validation_warnings = [e for e in structure_errors if e.severity in ["warning", "info"]]
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(sanitized_context, structure_errors)
            
            # Generate validation summary
            validation_summary = await self._generate_validation_summary(
                request.validation_type,
                request.validation_level,
                structure_errors
            )
            
            # Extract security flags
            security_flags = self._extract_security_flags(structure_errors)
            
            # Create validation result
            validation_result = ContextValidationResult(
                is_valid=len(validation_errors) == 0,
                validation_errors=validation_errors,
                validation_warnings=validation_warnings,
                compliance_score=compliance_score,
                validation_summary=validation_summary,
                security_flags=security_flags,
                integrity_checks=integrity_checks
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_context_risk_score(sanitized_context, structure_errors),
                "security_flags": security_flags
            }
            
            # Generate unique context ID
            context_id = self._generate_context_id(request, validation_result)
            
            result = RegistryContextValidationResult(
                validation_result=validation_result,
                validated_context=sanitized_context,
                validation_metadata={
                    "validation_type": request.validation_type.value,
                    "validation_level": request.validation_level.value,
                    "target_layer": request.target_layer,
                    "rules_applied": len(parsed_rules),
                    "integrity_checks": len(integrity_checks),
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                context_id=context_id
            )
            
            self.logger.info(f"Successfully validated registry context with compliance score {compliance_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate registry context: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def validate_context_structure(self, context: Dict[str, Any], rules: List[ContextValidationRule]) -> List[ContextValidationError]:
        """Validate context structure and organization"""
        errors = []
        
        for rule in rules:
            try:
                # Get validation function for rule type
                type_patterns = self._validation_patterns.get(rule.validation_type, {})
                validation_func = type_patterns.get(rule.rule_definition)
                
                if validation_func:
                    # Apply validation function
                    rule_errors = await validation_func(context, rule)
                    errors.extend(rule_errors)
                else:
                    # Unknown rule definition
                    error = ContextValidationError(
                        context_path=rule.context_path,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="unknown_rule",
                        error_message=f"Unknown validation rule definition: {rule.rule_definition}",
                        actual_value=None,
                        expected_value=None,
                        severity="warning"
                    )
                    errors.append(error)
                
            except Exception as e:
                self.logger.error(f"Failed to apply context validation rule {rule.id}: {str(e)}")
                error = ContextValidationError(
                    context_path=rule.context_path,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="rule_execution_error",
                    error_message=f"Rule execution failed: {str(e)}",
                    actual_value=str(e),
                    expected_value="success",
                    severity="error"
                )
                errors.append(error)
        
        return errors
    
    async def validate_context_integrity(self, context: Dict[str, Any]) -> Dict[str, bool]:
        """Validate context data integrity and consistency"""
        integrity_checks = {}
        
        try:
            # Check for required top-level sections
            integrity_checks["has_metadata"] = "metadata" in context
            integrity_checks["has_layer_info"] = "layer_info" in context
            integrity_checks["has_capabilities"] = "capabilities" in context
            
            # Check data consistency
            integrity_checks["consistent_timestamps"] = self._check_timestamp_consistency(context)
            integrity_checks["valid_references"] = self._check_reference_validity(context)
            integrity_checks["no_duplicate_keys"] = self._check_no_duplicate_keys(context)
            
            # Check structural integrity
            integrity_checks["valid_structure"] = self._check_valid_structure(context)
            integrity_checks["complete_data"] = self._check_data_completeness(context)
            
        except Exception as e:
            self.logger.error(f"Context integrity validation failed: {str(e)}")
            integrity_checks["integrity_check_failed"] = False
        
        return integrity_checks
    
    async def _parse_validation_rules(self, raw_rules: List[Dict[str, Any]]) -> List[ContextValidationRule]:
        """Parse raw validation rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = ContextValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    validation_type=ContextValidationType(raw_rule.get("validation_type", "structural")),
                    validation_level=ContextValidationLevel(raw_rule.get("validation_level", "standard")),
                    context_path=raw_rule.get("context_path", ""),
                    rule_definition=raw_rule.get("rule_definition", ""),
                    criteria=raw_rule.get("criteria", {}),
                    error_message=raw_rule.get("error_message", "Context validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse context validation rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = ContextValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    validation_type=ContextValidationType.STRUCTURAL,
                    validation_level=ContextValidationLevel.LENIENT,
                    context_path="",
                    rule_definition="required_sections",
                    criteria={},
                    error_message=f"Parsing failed: {str(e)}",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize context content for safety"""
        sanitized = context.copy()
        
        # Remove dangerous script content
        for key, value in sanitized.items():
            if isinstance(value, str):
                # Remove script tags and dangerous content
                sanitized[key] = value.replace("<script", "").replace("</script>", "")
            elif isinstance(value, dict):
                sanitized[key] = await self._sanitize_context(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    await self._sanitize_context(item) if isinstance(item, dict) else item
                    for item in value
                ]
        
        return sanitized
    
    # Structural validation implementations
    async def _validate_required_sections(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate required context sections"""
        errors = []
        required_sections = rule.criteria.get("required_sections", [])
        
        for section in required_sections:
            if section not in context:
                error = ContextValidationError(
                    context_path=section,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="missing_section",
                    error_message=f"Required section '{section}' is missing",
                    actual_value=None,
                    expected_value="present",
                    severity="error"
                )
                errors.append(error)
        
        return errors
    
    async def _validate_section_types(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate section data types"""
        errors = []
        section_types = rule.criteria.get("section_types", {})
        
        for section, expected_type in section_types.items():
            if section in context:
                value = context[section]
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
                    error = ContextValidationError(
                        context_path=section,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="type_mismatch",
                        error_message=f"Section '{section}' should be of type {expected_type}",
                        actual_value=type(value).__name__,
                        expected_value=expected_type,
                        severity="error"
                    )
                    errors.append(error)
        
        return errors
    
    async def _validate_field_presence(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate field presence in sections"""
        errors = []
        field_requirements = rule.criteria.get("field_requirements", {})
        
        for section, required_fields in field_requirements.items():
            if section in context and isinstance(context[section], dict):
                section_data = context[section]
                for field in required_fields:
                    if field not in section_data:
                        error = ContextValidationError(
                            context_path=f"{section}.{field}",
                            rule_id=rule.id,
                            validation_type=rule.validation_type,
                            error_category="missing_field",
                            error_message=f"Required field '{field}' missing in section '{section}'",
                            actual_value=None,
                            expected_value="present",
                            severity="error"
                        )
                        errors.append(error)
        
        return errors
    
    async def _validate_array_constraints(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate array field constraints"""
        errors = []
        array_constraints = rule.criteria.get("array_constraints", {})
        
        for field_path, constraints in array_constraints.items():
            value = self._get_nested_value(context, field_path)
            if isinstance(value, list):
                min_items = constraints.get("min_items")
                max_items = constraints.get("max_items")
                
                if min_items is not None and len(value) < min_items:
                    error = ContextValidationError(
                        context_path=field_path,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="array_constraint_violation",
                        error_message=f"Array '{field_path}' has {len(value)} items, minimum {min_items} required",
                        actual_value=len(value),
                        expected_value=f">={min_items}",
                        severity="error"
                    )
                    errors.append(error)
                
                if max_items is not None and len(value) > max_items:
                    error = ContextValidationError(
                        context_path=field_path,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="array_constraint_violation",
                        error_message=f"Array '{field_path}' has {len(value)} items, maximum {max_items} allowed",
                        actual_value=len(value),
                        expected_value=f"<={max_items}",
                        severity="error"
                    )
                    errors.append(error)
        
        return errors
    
    # Semantic validation implementations
    async def _validate_naming_conventions(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate naming conventions"""
        errors = []
        naming_rules = rule.criteria.get("naming_rules", {})
        
        for field_path, pattern in naming_rules.items():
            value = self._get_nested_value(context, field_path)
            if isinstance(value, str):
                import re
                if not re.match(pattern, value):
                    error = ContextValidationError(
                        context_path=field_path,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="naming_convention_violation",
                        error_message=f"Field '{field_path}' value '{value}' does not match naming pattern",
                        actual_value=value,
                        expected_value=pattern,
                        severity="warning"
                    )
                    errors.append(error)
        
        return errors
    
    async def _validate_value_ranges(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate value ranges"""
        errors = []
        range_rules = rule.criteria.get("range_rules", {})
        
        for field_path, range_spec in range_rules.items():
            value = self._get_nested_value(context, field_path)
            if isinstance(value, (int, float)):
                min_val = range_spec.get("min")
                max_val = range_spec.get("max")
                
                if min_val is not None and value < min_val:
                    error = ContextValidationError(
                        context_path=field_path,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="range_violation",
                        error_message=f"Field '{field_path}' value {value} is below minimum {min_val}",
                        actual_value=value,
                        expected_value=f">={min_val}",
                        severity="error"
                    )
                    errors.append(error)
                
                if max_val is not None and value > max_val:
                    error = ContextValidationError(
                        context_path=field_path,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="range_violation",
                        error_message=f"Field '{field_path}' value {value} is above maximum {max_val}",
                        actual_value=value,
                        expected_value=f"<={max_val}",
                        severity="error"
                    )
                    errors.append(error)
        
        return errors
    
    async def _validate_format_patterns(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate format patterns"""
        errors = []
        format_rules = rule.criteria.get("format_rules", {})
        
        for field_path, pattern in format_rules.items():
            value = self._get_nested_value(context, field_path)
            if isinstance(value, str):
                import re
                if not re.match(pattern, value):
                    error = ContextValidationError(
                        context_path=field_path,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="format_violation",
                        error_message=f"Field '{field_path}' value '{value}' does not match required format",
                        actual_value=value,
                        expected_value=pattern,
                        severity="error"
                    )
                    errors.append(error)
        
        return errors
    
    async def _validate_semantic_consistency(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate semantic consistency"""
        errors = []
        consistency_rules = rule.criteria.get("consistency_rules", [])
        
        for rule_spec in consistency_rules:
            field1 = rule_spec.get("field1")
            field2 = rule_spec.get("field2")
            relationship = rule_spec.get("relationship")
            
            value1 = self._get_nested_value(context, field1)
            value2 = self._get_nested_value(context, field2)
            
            if relationship == "equals" and value1 != value2:
                error = ContextValidationError(
                    context_path=f"{field1},{field2}",
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="semantic_inconsistency",
                    error_message=f"Fields '{field1}' and '{field2}' should be equal",
                    actual_value=f"{value1} != {value2}",
                    expected_value="equal",
                    severity="warning"
                )
                errors.append(error)
        
        return errors
    
    # Security validation implementations (simplified)
    async def _validate_access_controls(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate access controls"""
        # Simplified implementation
        return []
    
    async def _validate_encryption_status(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate encryption status"""
        # Simplified implementation
        return []
    
    async def _validate_audit_trail(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate audit trail"""
        # Simplified implementation
        return []
    
    async def _validate_security_headers(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate security headers"""
        # Simplified implementation
        return []
    
    # Compliance validation implementations (simplified)
    async def _validate_regulatory_compliance(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate regulatory compliance"""
        # Simplified implementation
        return []
    
    async def _validate_policy_adherence(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate policy adherence"""
        # Simplified implementation
        return []
    
    async def _validate_documentation_completeness(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate documentation completeness"""
        # Simplified implementation
        return []
    
    async def _validate_version_compliance(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate version compliance"""
        # Simplified implementation
        return []
    
    # Business logic validation implementations (simplified)
    async def _validate_workflow_compliance(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate workflow compliance"""
        # Simplified implementation
        return []
    
    async def _validate_business_rules(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate business rules"""
        # Simplified implementation
        return []
    
    async def _validate_state_transitions(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate state transitions"""
        # Simplified implementation
        return []
    
    async def _validate_dependency_validation(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate dependency validation"""
        # Simplified implementation
        return []
    
    # Data integrity validation implementations (simplified)
    async def _validate_checksum_validation(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate checksum validation"""
        # Simplified implementation
        return []
    
    async def _validate_referential_integrity(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate referential integrity"""
        # Simplified implementation
        return []
    
    async def _validate_temporal_consistency(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate temporal consistency"""
        # Simplified implementation
        return []
    
    async def _validate_data_consistency(self, context: Dict[str, Any], rule: ContextValidationRule) -> List[ContextValidationError]:
        """Validate data consistency"""
        # Simplified implementation
        return []
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """Get nested value from object using dot notation"""
        if not path:
            return obj
        
        parts = path.split(".")
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _check_timestamp_consistency(self, context: Dict[str, Any]) -> bool:
        """Check timestamp consistency across context"""
        # Simplified implementation
        return True
    
    def _check_reference_validity(self, context: Dict[str, Any]) -> bool:
        """Check reference validity"""
        # Simplified implementation
        return True
    
    def _check_no_duplicate_keys(self, context: Dict[str, Any]) -> bool:
        """Check for duplicate keys"""
        # Simplified implementation
        return True
    
    def _check_valid_structure(self, context: Dict[str, Any]) -> bool:
        """Check valid structure"""
        # Simplified implementation
        return isinstance(context, dict)
    
    def _check_data_completeness(self, context: Dict[str, Any]) -> bool:
        """Check data completeness"""
        # Simplified implementation
        return len(context) > 0
    
    def _calculate_compliance_score(self, context: Dict[str, Any], errors: List[ContextValidationError]) -> float:
        """Calculate compliance score based on validation results"""
        if not errors:
            return 1.0
        
        # Weight errors by severity
        total_penalty = 0
        for error in errors:
            if error.severity == "critical":
                total_penalty += 0.5
            elif error.severity == "error":
                total_penalty += 0.3
            elif error.severity == "warning":
                total_penalty += 0.1
            elif error.severity == "info":
                total_penalty += 0.05
        
        return max(0.0, 1.0 - total_penalty)
    
    async def _generate_validation_summary(
        self, 
        validation_type: ContextValidationType, 
        validation_level: ContextValidationLevel, 
        errors: List[ContextValidationError]
    ) -> Dict[str, Any]:
        """Generate validation summary"""
        error_categories = [error.error_category for error in errors]
        validation_types = [error.validation_type.value for error in errors]
        severity_counts = {}
        
        for error in errors:
            severity_counts[error.severity] = severity_counts.get(error.severity, 0) + 1
        
        return {
            "validation_type": validation_type.value,
            "validation_level": validation_level.value,
            "total_errors": len(errors),
            "error_categories": list(set(error_categories)),
            "validation_types": list(set(validation_types)),
            "severity_distribution": severity_counts,
            "most_common_error": max(error_categories) if error_categories else None
        }
    
    def _extract_security_flags(self, errors: List[ContextValidationError]) -> List[str]:
        """Extract security flags from validation errors"""
        security_flags = []
        
        for error in errors:
            if "security" in error.error_category.lower():
                security_flags.append("security_violation")
            elif "access" in error.error_category.lower():
                security_flags.append("access_control_issue")
            elif "injection" in error.error_category.lower():
                security_flags.append("injection_risk")
        
        return security_flags
    
    async def _estimate_validation_complexity(self, request: RegistryContextValidationRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.validation_rules) // 5
        
        # Add complexity for context size
        context_size = len(str(request.registry_context)) // 1000
        complexity_score += context_size
        
        # Add complexity for validation type
        if request.validation_type in [ContextValidationType.SECURITY, ContextValidationType.COMPLIANCE]:
            complexity_score += 2
        elif request.validation_type == ContextValidationType.BUSINESS_LOGIC:
            complexity_score += 3
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_context_risk_score(self, context: Dict[str, Any], errors: List[ContextValidationError]) -> float:
        """Calculate risk score for the context (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for critical errors
        critical_errors = sum(1 for e in errors if e.severity == "critical")
        if critical_errors > 0:
            risk_score += 0.4
        
        # Increase risk for security-related errors
        security_errors = sum(1 for e in errors if "security" in e.error_category)
        if security_errors > 0:
            risk_score += 0.3
        
        # Increase risk for large contexts
        context_size = len(str(context))
        if context_size > 50000:  # 50KB
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_context_id(self, request: RegistryContextValidationRequest, result: ContextValidationResult) -> str:
        """Generate unique context identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.target_layer}:{request.validation_type.value}:{result.compliance_score:.2f}:{timestamp}"
        return f"context_validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: RegistryContextValidationRequest, error: str) -> RegistryContextValidationResult:
        """Create safe fallback validation when main validation fails"""
        fallback_error = ContextValidationError(
            context_path="fallback_validation",
            rule_id="fallback_rule",
            validation_type=ContextValidationType.STRUCTURAL,
            error_category="validation_failed",
            error_message=f"Validation failed: {error}",
            actual_value="fallback",
            expected_value="success",
            severity="warning"
        )
        
        fallback_result = ContextValidationResult(
            is_valid=False,
            validation_errors=[fallback_error],
            validation_warnings=[],
            compliance_score=0.0,
            validation_summary={"fallback": True},
            security_flags=["fallback_mode"],
            integrity_checks={"fallback": False}
        )
        
        return RegistryContextValidationResult(
            validation_result=fallback_result,
            validated_context={"fallback": True, "error": error},
            validation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            context_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when context violates safety policies"""
    pass


class RegistryContextValidationError(Exception):
    """Raised for general registry context validation errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_registry_context_validator(safety_policy: Optional[RegistryContextSafetyPolicy] = None) -> RegistryContextValidator:
    """Factory function to create RegistryContextValidator with optional custom safety policy"""
    return RegistryContextValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_context_request(request: RegistryContextValidationRequest) -> tuple[bool, Optional[str]]:
    """Validate registry context request parameters"""
    try:
        if not isinstance(request.registry_context, dict):
            return False, "Registry context must be a dictionary"
        
        if not isinstance(request.validation_rules, list):
            return False, "Validation rules must be a list"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
