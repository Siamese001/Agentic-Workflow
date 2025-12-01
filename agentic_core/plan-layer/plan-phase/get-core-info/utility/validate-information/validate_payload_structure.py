"""
L1 Cognitive Planning - Payload Structure Validation

Implements pure planning operations for validating payload structures
with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from __future__ import annotations
import logging
import asyncio
import json
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field, ValidationError


# ============================================================================
# L5 SAFETY & LOGGING INFRASTRUCTURE
# ============================================================================

class ValidationScope(str, Enum):
    """Supported validation scopes with L5 safety validation"""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    BUSINESS = "business"


class ValidationLevel(str, Enum):
    """Validation levels with L5 safety enforcement"""
    STRICT = "strict"
    STANDARD = "standard"
    LENIENT = "lenient"
    MINIMAL = "minimal"


class PayloadStructureSafetyPolicy(BaseModel):
    """L5 Safety policy for payload structure validation operations"""
    max_payload_size: int = Field(default=1048576, description="Maximum payload size in bytes (1MB)")
    max_validation_depth: int = Field(default=10, description="Maximum validation nesting depth")
    allowed_scopes: List[str] = Field(default_factory=lambda: [t.value for t in ValidationScope])
    allowed_levels: List[str] = Field(default_factory=lambda: [t.value for t in ValidationLevel])
    require_schema_validation: bool = Field(default=True)
    prevent_payload_injection: bool = Field(default=True)
    sanitize_payload_content: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class PayloadStructureSafetyValidator:
    """L5 Safety validator for payload structure validation operations"""
    
    def __init__(self, policy: PayloadStructureSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.PayloadStructureSafetyValidator")
        
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
    
    def validate_payload_input(self, payload_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates payload input against L5 safety policies"""
        try:
            # Check payload size
            payload_data = payload_input.get("payload", {})
            payload_size = len(str(payload_data).encode('utf-8'))
            
            if payload_size > self.policy.max_payload_size:
                error_msg = f"Payload too large: {payload_size} > {self.policy.max_payload_size} bytes"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation scope
            validation_scope = payload_input.get("scope", "")
            if validation_scope not in self.policy.allowed_scopes:
                error_msg = f"Prohibited validation scope: {validation_scope}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation level
            validation_level = payload_input.get("level", "")
            if validation_level not in self.policy.allowed_levels:
                error_msg = f"Prohibited validation level: {validation_level}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation depth
            max_depth = self._calculate_payload_depth(payload_data)
            if max_depth > self.policy.max_validation_depth:
                error_msg = f"Payload nesting too deep: {max_depth} > {self.policy.max_validation_depth}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(payload_data).lower()
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
    
    def _calculate_payload_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of payload structure"""
        if current_depth > self.policy.max_validation_depth:
            return current_depth
        
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_payload_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_payload_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth


# ============================================================================
# L1 COGNITIVE PLANNING INTERFACES
# ============================================================================

@dataclass
class ValidationRule:
    """Individual validation rule for payload structure"""
    id: str
    scope: ValidationScope
    level: ValidationLevel
    field_path: str
    rule_type: str
    criteria: Dict[str, Any]
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class PayloadValidationRequest:
    """Input request for payload structure validation operations"""
    payload: Dict[str, Any]
    validation_schema: Optional[Dict[str, Any]]
    validation_rules: List[Dict[str, Any]]
    validation_scope: ValidationScope
    validation_level: ValidationLevel
    context: Dict[str, Any]
    validation_options: Dict[str, Any] = field(default_factory=dict)
    security_requirements: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class PayloadValidationError:
    """Individual payload validation error"""
    field_path: str
    rule_id: str
    error_type: str
    error_message: str
    actual_value: Any
    expected_value: Any
    severity: str


@dataclass
class PayloadValidationResult:
    """Result of payload structure validation"""
    is_valid: bool
    validation_errors: List[PayloadValidationError]
    validation_warnings: List[PayloadValidationError]
    compliance_score: float
    validation_summary: Dict[str, Any]
    security_flags: List[str]


@dataclass
class PayloadStructureValidationResult:
    """Output result from payload structure validation operations"""
    validation_result: PayloadValidationResult
    validated_payload: Dict[str, Any]
    validation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    validation_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class PayloadStructureValidatorInterface(ABC):
    """Abstract interface for payload structure validation operations"""
    
    @abstractmethod
    async def validate_payload_structure(self, request: PayloadValidationRequest) -> PayloadStructureValidationResult:
        """Validate payload structure against schema and rules"""
        pass
    
    @abstractmethod
    async def validate_against_schema(self, payload: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[PayloadValidationError]]:
        """Validate payload against JSON schema"""
        pass
    
    @abstractmethod
    async def apply_validation_rules(self, payload: Dict[str, Any], rules: List[ValidationRule]) -> List[PayloadValidationError]:
        """Apply custom validation rules to payload"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class PayloadStructureValidator(PayloadStructureValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating payload structures.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[PayloadStructureSafetyPolicy] = None):
        self.safety_policy = safety_policy or PayloadStructureSafetyPolicy()
        self.safety_validator = PayloadStructureSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Validation rule templates and patterns
        self._validation_patterns = {
            ValidationScope.STRUCTURAL: {
                "field_exists": lambda payload, field: self._field_exists(payload, field),
                "field_type": lambda payload, field, expected_type: self._field_type(payload, field, expected_type),
                "field_required": lambda payload, field: self._field_required(payload, field),
                "array_min_items": lambda payload, field, min_items: self._array_min_items(payload, field, min_items),
                "string_min_length": lambda payload, field, min_length: self._string_min_length(payload, field, min_length)
            },
            ValidationScope.SEMANTIC: {
                "naming_convention": lambda payload, field, pattern: self._naming_convention(payload, field, pattern),
                "email_format": lambda payload, field: self._email_format(payload, field),
                "url_format": lambda payload, field: self._url_format(payload, field),
                "version_format": lambda payload, field: self._version_format(payload, field)
            },
            ValidationScope.SECURITY: {
                "no_sensitive_data": lambda payload, field: self._no_sensitive_data(payload, field),
                "encrypted_field": lambda payload, field: self._encrypted_field(payload, field),
                "safe_characters": lambda payload, field: self._safe_characters(payload, field),
                "no_script_tags": lambda payload, field: self._no_script_tags(payload, field)
            },
            ValidationScope.COMPLIANCE: {
                "required_compliance_fields": lambda payload, fields: self._required_compliance_fields(payload, fields),
                "audit_trail_present": lambda payload: self._audit_trail_present(payload),
                "data_retention_policy": lambda payload, field: self._data_retention_policy(payload, field),
                "privacy_compliance": lambda payload, field: self._privacy_compliance(payload, field)
            },
            ValidationScope.BUSINESS: {
                "business_rules": lambda payload, rules: self._business_rules(payload, rules),
                "data_consistency": lambda payload, rules: self._data_consistency(payload, rules),
                "workflow_compliance": lambda payload, workflow: self._workflow_compliance(payload, workflow)
            }
        }
        
        self.logger.info("PayloadStructureValidator initialized with L5 safety policies")
    
    async def validate_payload_structure(self, request: PayloadValidationRequest) -> PayloadStructureValidationResult:
        """
        Validate payload structure against schema and rules.
        
        Args:
            request: Payload validation request with payload and validation criteria
            
        Returns:
            PayloadStructureValidationResult: Structured result with validation outcome and details
            
        Raises:
            ValidationError: If payload structure validation fails
            SafetyError: If payload violates safety policies
        """
        self.logger.info(f"Validating payload structure with {request.validation_scope} scope at {request.validation_level} level")
        
        try:
            # L5 Safety validation
            payload_input = {
                "payload": request.payload,
                "scope": request.validation_scope.value,
                "level": request.validation_level.value
            }
            
            is_valid, error_msg = self.safety_validator.validate_payload_input(payload_input)
            if not is_valid:
                raise SafetyError(f"Payload safety validation failed: {error_msg}")
            
            # Sanitize payload if required
            sanitized_payload = request.payload
            if self.safety_policy.sanitize_payload_content:
                sanitized_payload = await self._sanitize_payload(request.payload)
            
            # Parse validation rules
            parsed_rules = await self._parse_validation_rules(request.validation_rules)
            
            # Validate against schema if provided
            schema_errors = []
            if request.validation_schema:
                schema_valid, schema_errors = await self.validate_against_schema(
                    sanitized_payload, 
                    request.validation_schema
                )
                if not schema_valid:
                    self.logger.warning(f"Schema validation failed with {len(schema_errors)} errors")
            
            # Apply validation rules
            rule_errors = await self.apply_validation_rules(sanitized_payload, parsed_rules)
            
            # Combine all validation errors
            all_errors = schema_errors + rule_errors
            
            # Separate errors and warnings based on severity
            validation_errors = [e for e in all_errors if e.severity in ["error", "critical"]]
            validation_warnings = [e for e in all_errors if e.severity in ["warning", "info"]]
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(sanitized_payload, all_errors)
            
            # Generate validation summary
            validation_summary = await self._generate_validation_summary(
                request.validation_scope,
                request.validation_level,
                all_errors
            )
            
            # Extract security flags
            security_flags = self._extract_security_flags(all_errors)
            
            # Create validation result
            validation_result = PayloadValidationResult(
                is_valid=len(validation_errors) == 0,
                validation_errors=validation_errors,
                validation_warnings=validation_warnings,
                compliance_score=compliance_score,
                validation_summary=validation_summary,
                security_flags=security_flags
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_payload_risk_score(sanitized_payload, all_errors),
                "security_flags": security_flags
            }
            
            # Generate unique validation ID
            validation_id = self._generate_validation_id(request, validation_result)
            
            result = PayloadStructureValidationResult(
                validation_result=validation_result,
                validated_payload=sanitized_payload,
                validation_metadata={
                    "validation_scope": request.validation_scope.value,
                    "validation_level": request.validation_level.value,
                    "rules_applied": len(parsed_rules),
                    "schema_validated": request.validation_schema is not None,
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                validation_id=validation_id
            )
            
            self.logger.info(f"Successfully validated payload with compliance score {compliance_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate payload structure: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def validate_against_schema(self, payload: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[PayloadValidationError]]:
        """Validate payload against JSON schema"""
        try:
            errors = []
            
            # Basic JSON schema validation (simplified implementation)
            # In production, would use jsonschema library
            required_fields = schema.get("required", [])
            properties = schema.get("properties", {})
            
            # Check required fields
            for field in required_fields:
                if field not in payload:
                    error = PayloadValidationError(
                        field_path=field,
                        rule_id="schema_required",
                        error_type="missing_field",
                        error_message=f"Required field '{field}' is missing",
                        actual_value=None,
                        expected_value="present",
                        severity="error"
                    )
                    errors.append(error)
            
            # Check field types and constraints
            for field, field_schema in properties.items():
                if field in payload:
                    value = payload[field]
                    
                    # Type validation
                    expected_type = field_schema.get("type")
                    if expected_type:
                        if not self._validate_field_type(value, expected_type):
                            error = PayloadValidationError(
                                field_path=field,
                                rule_id="schema_type",
                                error_type="type_mismatch",
                                error_message=f"Field '{field}' should be of type {expected_type}",
                                actual_value=type(value).__name__,
                                expected_value=expected_type,
                                severity="error"
                            )
                            errors.append(error)
                    
                    # String constraints
                    if expected_type == "string":
                        min_length = field_schema.get("minLength")
                        if min_length and len(str(value)) < min_length:
                            error = PayloadValidationError(
                                field_path=field,
                                rule_id="schema_min_length",
                                error_type="constraint_violation",
                                error_message=f"Field '{field}' should be at least {min_length} characters",
                                actual_value=len(str(value)),
                                expected_value=f">={min_length}",
                                severity="error"
                            )
                            errors.append(error)
                        
                        pattern = field_schema.get("pattern")
                        if pattern:
                            import re
                            if not re.match(pattern, str(value)):
                                error = PayloadValidationError(
                                    field_path=field,
                                    rule_id="schema_pattern",
                                    error_type="pattern_mismatch",
                                    error_message=f"Field '{field}' does not match required pattern",
                                    actual_value=str(value),
                                    expected_value=pattern,
                                    severity="error"
                                )
                                errors.append(error)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            error = PayloadValidationError(
                field_path="schema_validation",
                rule_id="schema_error",
                error_type="validation_error",
                error_message=f"Schema validation failed: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity="critical"
            )
            return False, [error]
    
    async def apply_validation_rules(self, payload: Dict[str, Any], rules: List[ValidationRule]) -> List[PayloadValidationError]:
        """Apply custom validation rules to payload"""
        errors = []
        
        for rule in rules:
            try:
                # Get validation function for rule scope
                scope_patterns = self._validation_patterns.get(rule.scope, {})
                validation_func = scope_patterns.get(rule.rule_type)
                
                if validation_func:
                    # Apply validation function
                    criteria = rule.criteria
                    field_path = rule.field_path
                    
                    if rule.rule_type in ["field_exists", "field_type", "field_required"]:
                        is_valid = validation_func(payload, field_path, criteria.get("expected_type"))
                    elif rule.rule_type in ["naming_convention", "email_format", "url_format"]:
                        is_valid = validation_func(payload, field_path, criteria.get("pattern"))
                    elif rule.rule_type in ["no_sensitive_data", "encrypted_field", "safe_characters"]:
                        is_valid = validation_func(payload, field_path)
                    else:
                        # Generic validation with criteria
                        is_valid = validation_func(payload, criteria)
                    
                    if not is_valid:
                        error = PayloadValidationError(
                            field_path=field_path,
                            rule_id=rule.id,
                            error_type=rule.rule_type,
                            error_message=rule.error_message,
                            actual_value=self._get_field_value(payload, field_path),
                            expected_value=criteria.get("expected_value"),
                            severity="error"
                        )
                        errors.append(error)
                else:
                    # Unknown rule type
                    error = PayloadValidationError(
                        field_path=rule.field_path,
                        rule_id=rule.id,
                        error_type="unknown_rule",
                        error_message=f"Unknown validation rule type: {rule.rule_type}",
                        actual_value=None,
                        expected_value=None,
                        severity="warning"
                    )
                    errors.append(error)
                
            except Exception as e:
                self.logger.error(f"Failed to apply validation rule {rule.id}: {str(e)}")
                error = PayloadValidationError(
                    field_path=rule.field_path,
                    rule_id=rule.id,
                    error_type="rule_execution_error",
                    error_message=f"Rule execution failed: {str(e)}",
                    actual_value=str(e),
                    expected_value="success",
                    severity="error"
                )
                errors.append(error)
        
        return errors
    
    async def _parse_validation_rules(self, raw_rules: List[Dict[str, Any]]) -> List[ValidationRule]:
        """Parse raw validation rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = ValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    scope=ValidationScope(raw_rule.get("scope", "structural")),
                    level=ValidationLevel(raw_rule.get("level", "standard")),
                    field_path=raw_rule.get("field_path", ""),
                    rule_type=raw_rule.get("rule_type", ""),
                    criteria=raw_rule.get("criteria", {}),
                    error_message=raw_rule.get("error_message", "Validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse validation rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = ValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    scope=ValidationScope.STRUCTURAL,
                    level=ValidationLevel.LENIENT,
                    field_path="",
                    rule_type="field_exists",
                    criteria={},
                    error_message=f"Parsing failed: {str(e)}",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _sanitize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize payload content for safety"""
        sanitized = payload.copy()
        
        # Remove dangerous script content
        for key, value in sanitized.items():
            if isinstance(value, str):
                # Remove script tags
                sanitized[key] = value.replace("<script", "").replace("</script>", "")
        
        return sanitized
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type against expected type"""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True  # Unknown type, assume valid
    
    def _get_field_value(self, payload: Dict[str, Any], field_path: str) -> Any:
        """Get field value from payload using dot notation"""
        if not field_path:
            return payload
        
        parts = field_path.split(".")
        current = payload
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    # Validation function implementations
    def _field_exists(self, payload: Dict[str, Any], field_path: str) -> bool:
        return self._get_field_value(payload, field_path) is not None
    
    def _field_type(self, payload: Dict[str, Any], field_path: str, expected_type: str) -> bool:
        value = self._get_field_value(payload, field_path)
        return value is not None and self._validate_field_type(value, expected_type)
    
    def _field_required(self, payload: Dict[str, Any], field_path: str) -> bool:
        value = self._get_field_value(payload, field_path)
        return value is not None and value != ""
    
    def _array_min_items(self, payload: Dict[str, Any], field_path: str, min_items: int) -> bool:
        value = self._get_field_value(payload, field_path)
        return isinstance(value, list) and len(value) >= min_items
    
    def _string_min_length(self, payload: Dict[str, Any], field_path: str, min_length: int) -> bool:
        value = self._get_field_value(payload, field_path)
        return isinstance(value, str) and len(value) >= min_length
    
    def _naming_convention(self, payload: Dict[str, Any], field_path: str, pattern: str) -> bool:
        value = self._get_field_value(payload, field_path)
        if not isinstance(value, str):
            return False
        import re
        return re.match(pattern, value) is not None
    
    def _email_format(self, payload: Dict[str, Any], field_path: str) -> bool:
        value = self._get_field_value(payload, field_path)
        if not isinstance(value, str):
            return False
        import re
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_pattern, value) is not None
    
    def _url_format(self, payload: Dict[str, Any], field_path: str) -> bool:
        value = self._get_field_value(payload, field_path)
        if not isinstance(value, str):
            return False
        import re
        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return re.match(url_pattern, value) is not None
    
    def _version_format(self, payload: Dict[str, Any], field_path: str) -> bool:
        value = self._get_field_value(payload, field_path)
        if not isinstance(value, str):
            return False
        import re
        version_pattern = r"^\d+\.\d+\.\d+$"
        return re.match(version_pattern, value) is not None
    
    def _no_sensitive_data(self, payload: Dict[str, Any], field_path: str) -> bool:
        value = self._get_field_value(payload, field_path)
        if not isinstance(value, str):
            return True
        sensitive_keywords = ["password", "secret", "token", "key"]
        return not any(keyword in value.lower() for keyword in sensitive_keywords)
    
    def _encrypted_field(self, payload: Dict[str, Any], field_path: str) -> bool:
        # Simplified encryption check - would be more sophisticated in production
        value = self._get_field_value(payload, field_path)
        return isinstance(value, str) and len(value) > 20  # Assume long strings are encrypted
    
    def _safe_characters(self, payload: Dict[str, Any], field_path: str) -> bool:
        value = self._get_field_value(payload, field_path)
        if not isinstance(value, str):
            return True
        import re
        # Allow only alphanumeric, spaces, and basic punctuation
        safe_pattern = r"^[a-zA-Z0-9\s\-_.,!?()]+$"
        return re.match(safe_pattern, value) is not None
    
    def _no_script_tags(self, payload: Dict[str, Any], field_path: str) -> bool:
        value = self._get_field_value(payload, field_path)
        if not isinstance(value, str):
            return True
        return "<script" not in value.lower()
    
    def _required_compliance_fields(self, payload: Dict[str, Any], fields: List[str]) -> bool:
        return all(field in payload for field in fields)
    
    def _audit_trail_present(self, payload: Dict[str, Any]) -> bool:
        return "audit_trail" in payload or "timestamp" in payload
    
    def _data_retention_policy(self, payload: Dict[str, Any], field_path: str) -> bool:
        # Simplified check - would be more sophisticated in production
        return self._field_exists(payload, field_path)
    
    def _privacy_compliance(self, payload: Dict[str, Any], field_path: str) -> bool:
        # Simplified check - would be more sophisticated in production
        value = self._get_field_value(payload, field_path)
        return isinstance(value, dict) and "privacy_level" in value
    
    def _business_rules(self, payload: Dict[str, Any], rules: List[Dict[str, Any]]) -> bool:
        # Simplified business rules validation
        return True
    
    def _data_consistency(self, payload: Dict[str, Any], rules: List[Dict[str, Any]]) -> bool:
        # Simplified data consistency check
        return True
    
    def _workflow_compliance(self, payload: Dict[str, Any], workflow: str) -> bool:
        # Simplified workflow compliance check
        return "workflow" in payload
    
    def _calculate_compliance_score(self, payload: Dict[str, Any], errors: List[PayloadValidationError]) -> float:
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
        scope: ValidationScope, 
        level: ValidationLevel, 
        errors: List[PayloadValidationError]
    ) -> Dict[str, Any]:
        """Generate validation summary"""
        error_types = [error.error_type for error in errors]
        severity_counts = {}
        
        for error in errors:
            severity_counts[error.severity] = severity_counts.get(error.severity, 0) + 1
        
        return {
            "validation_scope": scope.value,
            "validation_level": level.value,
            "total_errors": len(errors),
            "error_types": list(set(error_types)),
            "severity_distribution": severity_counts,
            "most_common_error": max(error_types) if error_types else None
        }
    
    def _extract_security_flags(self, errors: List[PayloadValidationError]) -> List[str]:
        """Extract security flags from validation errors"""
        security_flags = []
        
        for error in errors:
            if "injection" in error.error_type.lower():
                security_flags.append("injection_risk")
            elif "script" in error.error_message.lower():
                security_flags.append("script_content")
            elif "sensitive" in error.error_type.lower():
                security_flags.append("sensitive_data")
        
        return security_flags
    
    async def _estimate_validation_complexity(self, request: PayloadValidationRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.validation_rules) // 5
        
        # Add complexity for schema validation
        if request.validation_schema:
            complexity_score += 2
        
        # Add complexity for payload size
        payload_size = len(str(request.payload)) // 1000
        complexity_score += payload_size
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_payload_risk_score(self, payload: Dict[str, Any], errors: List[PayloadValidationError]) -> float:
        """Calculate risk score for the payload (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for critical errors
        critical_errors = sum(1 for e in errors if e.severity == "critical")
        if critical_errors > 0:
            risk_score += 0.4
        
        # Increase risk for security-related errors
        security_errors = sum(1 for e in errors if "security" in e.error_type or "injection" in e.error_type)
        if security_errors > 0:
            risk_score += 0.3
        
        # Increase risk for large payloads
        payload_size = len(str(payload))
        if payload_size > 10000:  # 10KB
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_validation_id(self, request: PayloadValidationRequest, result: PayloadValidationResult) -> str:
        """Generate unique validation identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.validation_scope.value}:{request.validation_level.value}:{result.compliance_score:.2f}:{timestamp}"
        return f"payload_validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: PayloadValidationRequest, error: str) -> PayloadStructureValidationResult:
        """Create safe fallback validation when main validation fails"""
        fallback_error = PayloadValidationError(
            field_path="fallback_validation",
            rule_id="fallback_rule",
            error_type="validation_failed",
            error_message=f"Validation failed: {error}",
            actual_value="fallback",
            expected_value="success",
            severity="warning"
        )
        
        fallback_result = PayloadValidationResult(
            is_valid=False,
            validation_errors=[fallback_error],
            validation_warnings=[],
            compliance_score=0.0,
            validation_summary={"fallback": True},
            security_flags=["fallback_mode"]
        )
        
        return PayloadStructureValidationResult(
            validation_result=fallback_result,
            validated_payload={"fallback": True, "error": error},
            validation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            validation_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when payload violates safety policies"""
    
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


class PayloadValidationError(Exception):
    """Raised for general payload validation errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, operation: Optional[str] = None, payload_type: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code or "PAYLOAD_VALIDATION_ERROR"
        self.operation = operation
        self.payload_type = payload_type
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        op_info = f" in {self.operation}" if self.operation else ""
        type_info = f" for {self.payload_type}" if self.payload_type else ""
        return f"[{self.error_code}]{op_info}{type_info} {base_msg}"


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_payload_structure_validator(safety_policy: Optional[PayloadStructureSafetyPolicy] = None) -> PayloadStructureValidator:
    """Factory function to create PayloadStructureValidator with optional custom safety policy"""
    return PayloadStructureValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_payload_request(request: PayloadValidationRequest) -> tuple[bool, Optional[str]]:
    """Validate payload structure request parameters"""
    try:
        if not isinstance(request.payload, dict):
            return False, "Payload must be a dictionary"
        
        if not isinstance(request.validation_rules, list):
            return False, "Validation rules must be a list"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
