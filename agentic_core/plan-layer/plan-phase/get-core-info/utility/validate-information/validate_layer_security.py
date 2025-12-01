"""
L1 Cognitive Planning - Layer Security Validation

Implements pure planning operations for validating layer security
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

class SecurityValidationType(str, Enum):
    """Supported security validation types with L5 safety validation"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    INPUT_VALIDATION = "input_validation"
    OUTPUT_SANITIZATION = "output_sanitization"
    VULNERABILITY = "vulnerability"


class SecuritySeverity(str, Enum):
    """Security validation severity levels with L5 safety enforcement"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LayerSecuritySafetyPolicy(BaseModel):
    """L5 Safety policy for layer security validation operations"""
    max_security_rules: int = Field(default=100, description="Maximum security rules")
    max_validation_depth: int = Field(default=10, description="Maximum validation nesting depth")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in SecurityValidationType])
    allowed_severities: List[str] = Field(default_factory=lambda: [t.value for t in SecuritySeverity])
    require_security_validation: bool = Field(default=True)
    prevent_security_bypass: bool = Field(default=True)
    sanitize_security_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerSecuritySafetyValidator:
    """L5 Safety validator for layer security validation operations"""
    
    def __init__(self, policy: LayerSecuritySafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerSecuritySafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._security_patterns = [
            r"password", r"secret", r"token", r"key",
            r"credential", r"auth", r"certificate"
        ]
        self._injection_patterns = [
            r"\${", r"%{", r"{{", r"\[\[",  # Template injection
            r"union\s+select", r"drop\s+table",  # SQL injection
            r"<\?php", r"<%", r"@\s*import"  # Code injection
        ]
    
    def validate_security_input(self, security_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates security input against L5 safety policies"""
        try:
            # Check security rules count
            security_rules = security_input.get("security_rules", [])
            if len(security_rules) > self.policy.max_security_rules:
                error_msg = f"Too many security rules: {len(security_rules)} > {self.policy.max_security_rules}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation types
            for rule in security_rules:
                rule_type = rule.get("type", "")
                if rule_type not in self.policy.allowed_validation_types:
                    error_msg = f"Prohibited validation type: {rule_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check validation depth
            layer_spec = security_input.get("layer_spec", {})
            max_depth = self._calculate_validation_depth(layer_spec)
            if max_depth > self.policy.max_validation_depth:
                error_msg = f"Validation nesting too deep: {max_depth} > {self.policy.max_validation_depth}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(layer_spec).lower()
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
            
            # Check for security patterns (additional validation)
            for pattern in self._security_patterns:
                if pattern in content_str:
                    self.logger.warning(f"Security pattern detected: {pattern}")
                    # Additional validation would be required in production
            
            return True, None
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.error(f"Safety validation failed: {error_msg}")
            if self.policy.fail_closed:
                return False, error_msg
            return True, error_msg
    
    def _calculate_validation_depth(self, layer_spec: Dict[str, Any]) -> int:
        """Calculate maximum nesting depth of validation"""
        try:
            def get_depth(obj, current_depth=0):
                if current_depth > self.policy.max_validation_depth:
                    return current_depth
                
                if isinstance(obj, dict):
                    if not obj:
                        return current_depth + 1
                    
                    max_sub_depth = 0
                    for value in obj.values():
                        sub_depth = get_depth(value, current_depth + 1)
                        max_sub_depth = max(max_sub_depth, sub_depth)
                    return max_sub_depth
                elif isinstance(obj, list):
                    if not obj:
                        return current_depth + 1
                    
                    max_sub_depth = 0
                    for item in obj:
                        sub_depth = get_depth(item, current_depth + 1)
                        max_sub_depth = max(max_sub_depth, sub_depth)
                    return max_sub_depth
                else:
                    return current_depth + 1
            
            return get_depth(layer_spec)
            
        except Exception as e:
            self.logger.error(f"Validation depth calculation failed: {str(e)}")
            return 0


# ============================================================================
# L1 COGNITIVE PLANNING INTERFACES
# ============================================================================

@dataclass
class SecurityValidationRule:
    """Individual security validation rule specification"""
    id: str
    validation_type: SecurityValidationType
    severity: SecuritySeverity
    criteria: Dict[str, Any]
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class LayerSecurityValidationRequest:
    """Input request for layer security validation operations"""
    layer_name: str
    layer_spec: Dict[str, Any]
    security_rules: List[Dict[str, Any]]
    validation_options: Dict[str, Any]
    context: Dict[str, Any]
    security_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class SecurityValidationError:
    """Individual security validation error"""
    layer_id: str
    rule_id: str
    validation_type: SecurityValidationType
    error_category: str
    error_message: str
    actual_value: Any
    expected_value: Any
    severity: SecuritySeverity
    cve_reference: Optional[str]


@dataclass
class SecurityValidationResult:
    """Result of layer security validation"""
    is_secure: bool
    security_score: float
    validation_errors: List[SecurityValidationError]
    validation_warnings: List[SecurityValidationError]
    vulnerability_count: int
    security_summary: Dict[str, Any]
    security_flags: List[str]


@dataclass
class LayerSecurityValidationResult:
    """Output result from layer security validation operations"""
    validation_result: SecurityValidationResult
    validated_layer: Dict[str, Any]
    validation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    security_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerSecurityValidatorInterface(ABC):
    """Abstract interface for layer security validation operations"""
    
    @abstractmethod
    async def validate_security(self, request: LayerSecurityValidationRequest) -> LayerSecurityValidationResult:
        """Validate layer security against rules and criteria"""
        pass
    
    @abstractmethod
    async def check_authentication_security(self, layer_spec: Dict[str, Any]) -> List[SecurityValidationError]:
        """Check authentication security configurations"""
        pass
    
    @abstractmethod
    async def check_authorization_security(self, layer_spec: Dict[str, Any]) -> List[SecurityValidationError]:
        """Check authorization security configurations"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerSecurityValidator(LayerSecurityValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating layer security.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerSecuritySafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerSecuritySafetyPolicy()
        self.safety_validator = LayerSecuritySafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Security validation patterns and rules
        self._validation_patterns = {
            SecurityValidationType.AUTHENTICATION: {
                "auth_required": self._validate_auth_required,
                "auth_strength": self._validate_auth_strength,
                "auth_protocols": self._validate_auth_protocols
            },
            SecurityValidationType.AUTHORIZATION: {
                "rbac_configured": self._validate_rbac_configured,
                "permission_granularity": self._validate_permission_granularity,
                "access_control": self._validate_access_control
            },
            SecurityValidationType.ENCRYPTION: {
                "data_encryption": self._validate_data_encryption,
                "transmission_encryption": self._validate_transmission_encryption,
                "key_management": self._validate_key_management
            },
            SecurityValidationType.INPUT_VALIDATION: {
                "input_sanitization": self._validate_input_sanitization,
                "parameter_validation": self._validate_parameter_validation,
                "type_validation": self._validate_type_validation
            },
            SecurityValidationType.OUTPUT_SANITIZATION: {
                "output_encoding": self._validate_output_encoding,
                "content_filtering": self._validate_content_filtering,
                "response_sanitization": self._validate_response_sanitization
            },
            SecurityValidationType.VULNERABILITY: {
                "known_vulnerabilities": self._validate_known_vulnerabilities,
                "dependency_vulnerabilities": self._validate_dependency_vulnerabilities,
                "security_patches": self._validate_security_patches
            }
        }
        
        self.logger.info("LayerSecurityValidator initialized with L5 safety policies")
    
    async def validate_security(self, request: LayerSecurityValidationRequest) -> LayerSecurityValidationResult:
        """
        Validate layer security against rules and criteria.
        
        Args:
            request: Layer security validation request with layer specification and security rules
            
        Returns:
            LayerSecurityValidationResult: Structured result with security validation outcome and details
            
        Raises:
            ValidationError: If security validation fails
            SafetyError: If security validation violates safety policies
        """
        self.logger.info(f"Validating security for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            security_input = {
                "layer_spec": request.layer_spec,
                "security_rules": request.security_rules
            }
            
            is_valid, error_msg = self.safety_validator.validate_security_input(security_input)
            if not is_valid:
                raise SafetyError(f"Security safety validation failed: {error_msg}")
            
            # Sanitize security data if required
            sanitized_layer = request.layer_spec
            if self.safety_policy.sanitize_security_data:
                sanitized_layer = await self._sanitize_security_data(request.layer_spec)
            
            # Parse security rules
            parsed_rules = await self._parse_security_rules(request.security_rules)
            
            # Execute security validation rules
            validation_errors = []
            for rule in parsed_rules:
                rule_errors = await self._execute_security_rule(sanitized_layer, rule)
                validation_errors.extend(rule_errors)
            
            # Check authentication security
            auth_errors = await self.check_authentication_security(sanitized_layer)
            validation_errors.extend(auth_errors)
            
            # Check authorization security
            authz_errors = await self.check_authorization_security(sanitized_layer)
            validation_errors.extend(authz_errors)
            
            # Separate errors and warnings based on severity
            error_list = [e for e in validation_errors if e.severity in [SecuritySeverity.CRITICAL, SecuritySeverity.HIGH]]
            warning_list = [e for e in validation_errors if e.severity in [SecuritySeverity.MEDIUM, SecuritySeverity.LOW]]
            
            # Determine overall security
            is_layer_secure = len(error_list) == 0
            
            # Calculate security score
            security_score = self._calculate_security_score(validation_errors)
            
            # Count vulnerabilities
            vulnerability_count = len([e for e in validation_errors if e.validation_type == SecurityValidationType.VULNERABILITY])
            
            # Generate security summary
            security_summary = await self._generate_security_summary(
                request.layer_name,
                validation_errors
            )
            
            # Extract security flags
            security_flags = self._extract_security_flags(validation_errors)
            
            # Create validation result
            validation_result = SecurityValidationResult(
                is_secure=is_layer_secure,
                security_score=security_score,
                validation_errors=error_list,
                validation_warnings=warning_list,
                vulnerability_count=vulnerability_count,
                security_summary=security_summary,
                security_flags=security_flags
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_security_risk_score(validation_result),
                "security_flags": security_flags
            }
            
            # Generate unique security ID
            security_id = self._generate_security_id(request, validation_result)
            
            result = LayerSecurityValidationResult(
                validation_result=validation_result,
                validated_layer=sanitized_layer,
                validation_metadata={
                    "layer_name": request.layer_name,
                    "rules_applied": len(parsed_rules),
                    "vulnerabilities_found": vulnerability_count,
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                security_id=security_id
            )
            
            self.logger.info(f"Successfully validated security for {request.layer_name} with score {security_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate layer security: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def check_authentication_security(self, layer_spec: Dict[str, Any]) -> List[SecurityValidationError]:
        """Check authentication security configurations"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        try:
            # Check if authentication is configured
            auth_config = layer_spec.get("authentication", {})
            if not auth_config:
                error = SecurityValidationError(
                    layer_id=layer_name,
                    rule_id="auth_security",
                    validation_type=SecurityValidationType.AUTHENTICATION,
                    error_category="missing_authentication",
                    error_message="Layer missing authentication configuration",
                    actual_value=auth_config,
                    expected_value="authentication configuration",
                    severity=SecuritySeverity.HIGH,
                    cve_reference=None
                )
                errors.append(error)
                return errors
            
            # Check authentication methods
            auth_methods = auth_config.get("methods", [])
            if not auth_methods:
                error = SecurityValidationError(
                    layer_id=layer_name,
                    rule_id="auth_security",
                    validation_type=SecurityValidationType.AUTHENTICATION,
                    error_category="missing_auth_methods",
                    error_message="No authentication methods specified",
                    actual_value=auth_methods,
                    expected_value="list of authentication methods",
                    severity=SecuritySeverity.HIGH,
                    cve_reference=None
                )
                errors.append(error)
            
            # Check for weak authentication methods
            weak_methods = ["basic", "none", "anonymous"]
            for method in auth_methods:
                if method.lower() in weak_methods:
                    error = SecurityValidationError(
                        layer_id=layer_name,
                        rule_id="auth_security",
                        validation_type=SecurityValidationType.AUTHENTICATION,
                        error_category="weak_auth_method",
                        error_message=f"Weak authentication method: {method}",
                        actual_value=method,
                        expected_value="strong authentication method",
                        severity=SecuritySeverity.MEDIUM,
                        cve_reference=None
                    )
                    errors.append(error)
            
            # Check session management
            session_config = auth_config.get("session", {})
            if session_config:
                timeout = session_config.get("timeout", 0)
                if timeout > 3600:  # More than 1 hour
                    error = SecurityValidationError(
                        layer_id=layer_name,
                        rule_id="auth_security",
                        validation_type=SecurityValidationType.AUTHENTICATION,
                        error_category="excessive_session_timeout",
                        error_message=f"Session timeout too long: {timeout} seconds",
                        actual_value=timeout,
                        expected_value="<= 3600 seconds",
                        severity=SecuritySeverity.MEDIUM,
                        cve_reference=None
                    )
                    errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Authentication security check failed: {str(e)}")
            error = SecurityValidationError(
                layer_id=layer_name,
                rule_id="auth_security_error",
                validation_type=SecurityValidationType.AUTHENTICATION,
                error_category="validation_error",
                error_message=f"Authentication security check error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=SecuritySeverity.HIGH,
                cve_reference=None
            )
            errors.append(error)
        
        return errors
    
    async def check_authorization_security(self, layer_spec: Dict[str, Any]) -> List[SecurityValidationError]:
        """Check authorization security configurations"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        try:
            # Check if authorization is configured
            authz_config = layer_spec.get("authorization", {})
            if not authz_config:
                error = SecurityValidationError(
                    layer_id=layer_name,
                    rule_id="authz_security",
                    validation_type=SecurityValidationType.AUTHORIZATION,
                    error_category="missing_authorization",
                    error_message="Layer missing authorization configuration",
                    actual_value=authz_config,
                    expected_value="authorization configuration",
                    severity=SecuritySeverity.HIGH,
                    cve_reference=None
                )
                errors.append(error)
                return errors
            
            # Check authorization model
            authz_model = authz_config.get("model", "")
            if not authz_model:
                error = SecurityValidationError(
                    layer_id=layer_name,
                    rule_id="authz_security",
                    validation_type=SecurityValidationType.AUTHORIZATION,
                    error_category="missing_authz_model",
                    error_message="No authorization model specified",
                    actual_value=authz_model,
                    expected_value="authorization model (RBAC, ABAC, etc.)",
                    severity=SecuritySeverity.HIGH,
                    cve_reference=None
                )
                errors.append(error)
            
            # Check role definitions
            if authz_model.lower() == "rbac":
                roles = authz_config.get("roles", [])
                if not roles:
                    error = SecurityValidationError(
                        layer_id=layer_name,
                        rule_id="authz_security",
                        validation_type=SecurityValidationType.AUTHORIZATION,
                        error_category="missing_roles",
                        error_message="RBAC model missing role definitions",
                        actual_value=roles,
                        expected_value="list of roles",
                        severity=SecuritySeverity.HIGH,
                        cve_reference=None
                    )
                    errors.append(error)
                
                # Check for overly permissive roles
                for role in roles:
                    permissions = role.get("permissions", [])
                    if "*" in permissions or "all" in [p.lower() for p in permissions]:
                        error = SecurityValidationError(
                            layer_id=layer_name,
                            rule_id="authz_security",
                            validation_type=SecurityValidationType.AUTHORIZATION,
                            error_category="overly_permissive_role",
                            error_message=f"Overly permissive role: {role.get('name', 'unknown')}",
                            actual_value=permissions,
                            expected_value="specific permissions",
                            severity=SecuritySeverity.HIGH,
                            cve_reference=None
                        )
                        errors.append(error)
            
            # Check permission granularity
            permissions = authz_config.get("permissions", [])
            if permissions:
                coarse_permissions = [p for p in permissions if len(p.split(":")) < 2]
                if len(coarse_permissions) > len(permissions) * 0.5:
                    error = SecurityValidationError(
                        layer_id=layer_name,
                        rule_id="authz_security",
                        validation_type=SecurityValidationType.AUTHORIZATION,
                        error_category="coarse_permissions",
                        error_message="Too many coarse-grained permissions",
                        actual_value=len(coarse_permissions),
                        expected_value=f"<={len(permissions) * 0.5}",
                        severity=SecuritySeverity.MEDIUM,
                        cve_reference=None
                    )
                    errors.append(error)
            
        except Exception as e:
            self.logger.error(f"Authorization security check failed: {str(e)}")
            error = SecurityValidationError(
                layer_id=layer_name,
                rule_id="authz_security_error",
                validation_type=SecurityValidationType.AUTHORIZATION,
                error_category="validation_error",
                error_message=f"Authorization security check error: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=SecuritySeverity.HIGH,
                cve_reference=None
            )
            errors.append(error)
        
        return errors
    
    async def _parse_security_rules(self, raw_rules: List[Dict[str, Any]]) -> List[SecurityValidationRule]:
        """Parse raw security rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = SecurityValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    validation_type=SecurityValidationType(raw_rule.get("validation_type", "authentication")),
                    severity=SecuritySeverity(raw_rule.get("severity", "medium")),
                    criteria=raw_rule.get("criteria", {}),
                    error_message=raw_rule.get("error_message", "Security validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse security rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = SecurityValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    validation_type=SecurityValidationType.AUTHENTICATION,
                    severity=SecuritySeverity.MEDIUM,
                    criteria={},
                    error_message=f"Parsing failed: {str(e)}",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _execute_security_rule(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Execute individual security validation rule"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        try:
            # Get validation function for rule type
            type_patterns = self._validation_patterns.get(rule.validation_type, {})
            validation_func = type_patterns.get(rule.criteria.get("validation_function", ""))
            
            if validation_func:
                # Apply validation function
                rule_errors = await validation_func(layer_spec, rule)
                errors.extend(rule_errors)
            else:
                # Unknown validation function
                error = SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="unknown_validation",
                    error_message=f"Unknown validation function: {rule.criteria.get('validation_function')}",
                    actual_value=None,
                    expected_value=None,
                    severity=SecuritySeverity.MEDIUM,
                    cve_reference=None
                )
                errors.append(error)
                
        except Exception as e:
            self.logger.error(f"Failed to execute security rule {rule.id}: {str(e)}")
            error = SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="rule_execution_error",
                error_message=f"Rule execution failed: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=SecuritySeverity.HIGH,
                cve_reference=None
            )
            errors.append(error)
        
        return errors
    
    async def _sanitize_security_data(self, layer_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize security data for safety"""
        sanitized = layer_spec.copy()
        
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
                        sanitized_item = await self._sanitize_security_data(item)
                        sanitized_list.append(sanitized_item)
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
            elif isinstance(value, dict):
                sanitized[key] = await self._sanitize_security_data(value)
        
        return sanitized
    
    # Validation function implementations
    async def _validate_auth_required(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate authentication is required"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        auth_config = layer_spec.get("authentication", {})
        if not auth_config:
            error = SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="authentication_required",
                error_message="Authentication is required but not configured",
                actual_value=auth_config,
                expected_value="authentication configuration",
                severity=rule.severity,
                cve_reference=None
            )
            errors.append(error)
        
        return errors
    
    async def _validate_auth_strength(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate authentication strength"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        auth_config = layer_spec.get("authentication", {})
        auth_methods = auth_config.get("methods", [])
        
        strong_methods = ["oauth2", "jwt", "saml", "ldap"]
        has_strong_auth = any(method.lower() in strong_methods for method in auth_methods)
        
        if not has_strong_auth:
            error = SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="weak_authentication",
                error_message="Authentication methods are not strong enough",
                actual_value=auth_methods,
                expected_value=f"one of {strong_methods}",
                severity=rule.severity,
                cve_reference=None
            )
            errors.append(error)
        
        return errors
    
    async def _validate_auth_protocols(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate authentication protocols"""
        errors = []
        
        # Check if authentication is configured
        if "authentication" not in layer_spec:
            errors.append(SecurityValidationError(
                field="authentication",
                message="Authentication configuration not defined",
                severity="error",
                rule_id=rule.rule_id
            ))
            return errors
        
        auth = layer_spec["authentication"]
        
        # Validate authentication methods
        if "methods" not in auth:
            errors.append(SecurityValidationError(
                field="authentication.methods",
                message="Authentication methods not specified",
                severity="error",
                rule_id=rule.rule_id
            ))
        else:
            methods = auth["methods"]
            if not isinstance(methods, list) or len(methods) == 0:
                errors.append(SecurityValidationError(
                    field="authentication.methods",
                    message="At least one authentication method must be specified",
                    severity="error",
                    rule_id=rule.rule_id
                ))
            else:
                # Validate each authentication method
                valid_methods = ["oauth2", "jwt", "basic", "api_key", "certificate"]
                for method in methods:
                    if method not in valid_methods:
                        errors.append(SecurityValidationError(
                            field="authentication.methods",
                            message=f"Unsupported authentication method: {method}",
                            severity="warning",
                            rule_id=rule.rule_id
                        ))
        
        # Validate session management
        if "session_management" in auth:
            session = auth["session_management"]
            if session.get("timeout_minutes", 0) < 15:
                errors.append(SecurityValidationError(
                    field="authentication.session_management.timeout_minutes",
                    message="Session timeout should be at least 15 minutes",
                    severity="warning",
                    rule_id=rule.rule_id
                ))
            
            if not session.get("secure_cookies", False):
                errors.append(SecurityValidationError(
                    field="authentication.session_management.secure_cookies",
                    message="Secure cookies should be enabled",
                    severity="warning",
                    rule_id=rule.rule_id
                ))
        
        return errors
    
    async def _validate_rbac_configured(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate RBAC is configured"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        authz_config = layer_spec.get("authorization", {})
        authz_model = authz_config.get("model", "")
        
        if authz_model.lower() == "rbac":
            roles = authz_config.get("roles", [])
            if not roles:
                error = SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="rbac_not_configured",
                    error_message="RBAC model specified but no roles configured",
                    actual_value=roles,
                    expected_value="list of roles",
                    severity=rule.severity,
                    cve_reference=None
                )
                errors.append(error)
        
        return errors
    
    async def _validate_permission_granularity(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate permission granularity"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if authorization is configured
        authz_config = layer_spec.get("authorization", {})
        if not authz_config:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="authorization_not_configured",
                error_message="Authorization configuration not defined",
                actual_value=None,
                expected_value="authorization configuration",
                severity="warning",
                cve_reference=None
            ))
            return errors
        
        # Validate permission structure
        permissions = authz_config.get("permissions", [])
        if not permissions:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="permissions_not_defined",
                error_message="No permissions defined in authorization configuration",
                actual_value=permissions,
                expected_value="list of permissions",
                severity="error",
                cve_reference=None
            ))
        else:
            # Check permission granularity
            coarse_permissions = 0
            for perm in permissions:
                if isinstance(perm, str):
                    # String permissions are too coarse
                    coarse_permissions += 1
                elif isinstance(perm, dict):
                    # Check if permission has proper granularity
                    if "resource" not in perm or "action" not in perm:
                        coarse_permissions += 1
            
            if coarse_permissions > len(permissions) * 0.5:  # More than 50% are coarse
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_permission_granularity",
                    error_message=f"Too many coarse-grained permissions: {coarse_permissions}/{len(permissions)}",
                    actual_value=f"{coarse_permissions} coarse permissions",
                    expected_value="fine-grained resource-action permissions",
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate role-permission mapping
        roles = authz_config.get("roles", [])
        if roles:
            for role in roles:
                if isinstance(role, dict):
                    role_perms = role.get("permissions", [])
                    if not role_perms:
                        errors.append(SecurityValidationError(
                            layer_id=layer_name,
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="role_without_permissions",
                            error_message=f"Role '{role.get('name', 'unnamed')}' has no permissions defined",
                            actual_value=role_perms,
                            expected_value="list of permissions",
                            severity="warning",
                            cve_reference=None
                        ))
        
        return errors
    
    async def _validate_access_control(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate access control"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if access control is configured
        access_control = layer_spec.get("access_control", {})
        if not access_control:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="access_control_not_configured",
                error_message="Access control configuration not defined",
                actual_value=None,
                expected_value="access control configuration",
                severity="error",
                cve_reference=None
            ))
            return errors
        
        # Validate access control mechanisms
        mechanisms = access_control.get("mechanisms", [])
        if not mechanisms:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_access_control_mechanisms",
                error_message="No access control mechanisms specified",
                actual_value=mechanisms,
                expected_value="list of access control mechanisms",
                severity="error",
                cve_reference=None
            ))
        else:
            # Validate each mechanism
            valid_mechanisms = ["firewall", "network_acl", "api_gateway", "service_mesh", "iam"]
            for mechanism in mechanisms:
                if mechanism not in valid_mechanisms:
                    errors.append(SecurityValidationError(
                        layer_id=layer_name,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="unsupported_access_control_mechanism",
                        error_message=f"Unsupported access control mechanism: {mechanism}",
                        actual_value=mechanism,
                        expected_value="supported mechanism",
                        severity="warning",
                        cve_reference=None
                    ))
        
        # Validate network access rules
        network_rules = access_control.get("network_rules", {})
        if network_rules:
            # Check for default deny policy
            if not network_rules.get("default_deny", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="no_default_deny_policy",
                    error_message="Network access control should have default deny policy",
                    actual_value=network_rules.get("default_deny"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
            
            # Validate IP restrictions
            allowed_ips = network_rules.get("allowed_ips", [])
            if allowed_ips and len(allowed_ips) > 1000:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="excessive_allowed_ips",
                    error_message=f"Too many allowed IPs: {len(allowed_ips)} - consider using CIDR ranges",
                    actual_value=len(allowed_ips),
                    expected_value="< 1000 IPs or CIDR ranges",
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate API access control
        api_access = access_control.get("api_access", {})
        if api_access:
            if not api_access.get("rate_limiting", {}).get("enabled", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="no_api_rate_limiting",
                    error_message="API access control should have rate limiting enabled",
                    actual_value=api_access.get("rate_limiting"),
                    expected_value="enabled rate limiting",
                    severity="warning",
                    cve_reference=None
                ))
        
        return errors
    
    async def _validate_data_encryption(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate data encryption"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        encryption_config = layer_spec.get("encryption", {})
        if not encryption_config:
            error = SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="missing_encryption",
                error_message="Data encryption not configured",
                actual_value=encryption_config,
                expected_value="encryption configuration",
                severity=rule.severity,
                cve_reference=None
            )
            errors.append(error)
        
        return errors
    
    async def _validate_transmission_encryption(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate transmission encryption"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if transmission encryption is configured
        transmission = layer_spec.get("transmission", {})
        if not transmission:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="transmission_not_configured",
                error_message="Transmission security configuration not defined",
                actual_value=None,
                expected_value="transmission configuration",
                severity="error",
                cve_reference=None
            ))
            return errors
        
        # Validate TLS configuration
        tls_config = transmission.get("tls", {})
        if not tls_config.get("enabled", False):
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="tls_not_enabled",
                error_message="TLS should be enabled for transmission encryption",
                actual_value=tls_config.get("enabled"),
                expected_value=True,
                severity="error",
                cve_reference=None
            ))
        else:
            # Validate TLS version
            tls_version = tls_config.get("version", "")
            if tls_version not in ["1.2", "1.3"]:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="weak_tls_version",
                    error_message=f"TLS version {tls_version} is not recommended - use TLS 1.2 or 1.3",
                    actual_value=tls_version,
                    expected_value="1.2 or 1.3",
                    severity="warning",
                    cve_reference=None
                ))
            
            # Validate cipher suites
            cipher_suites = tls_config.get("cipher_suites", [])
            weak_ciphers = ["RC4", "DES", "3DES", "MD5"]
            for cipher in cipher_suites:
                if any(weak in cipher.upper() for weak in weak_ciphers):
                    errors.append(SecurityValidationError(
                        layer_id=layer_name,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="weak_cipher_suite",
                        error_message=f"Weak cipher suite detected: {cipher}",
                        actual_value=cipher,
                        expected_value="strong cipher suites only",
                        severity="error",
                        cve_reference=None
                    ))
        
        # Validate certificate configuration
        cert_config = transmission.get("certificate", {})
        if tls_config.get("enabled", False) and not cert_config:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="certificate_not_configured",
                error_message="Certificate configuration required when TLS is enabled",
                actual_value=cert_config,
                expected_value="certificate configuration",
                severity="error",
                cve_reference=None
            ))
        elif cert_config:
            # Check certificate expiry
            if "expires_at" in cert_config:
                from datetime import datetime
                try:
                    expiry_date = datetime.fromisoformat(cert_config["expires_at"].replace('Z', '+00:00'))
                    if expiry_date < datetime.now():
                        errors.append(SecurityValidationError(
                            layer_id=layer_name,
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="certificate_expired",
                            error_message="Certificate has expired",
                            actual_value=cert_config["expires_at"],
                            expected_value="future date",
                            severity="error",
                            cve_reference=None
                        ))
                except ValueError:
                    errors.append(SecurityValidationError(
                        layer_id=layer_name,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="invalid_certificate_date",
                        error_message="Certificate expiry date format is invalid",
                        actual_value=cert_config["expires_at"],
                        expected_value="ISO 8601 date",
                        severity="warning",
                        cve_reference=None
                    ))
        
        return errors
    
    async def _validate_key_management(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate key management"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if key management is configured
        key_mgmt = layer_spec.get("key_management", {})
        if not key_mgmt:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="key_management_not_configured",
                error_message="Key management configuration not defined",
                actual_value=None,
                expected_value="key management configuration",
                severity="error",
                cve_reference=None
            ))
            return errors
        
        # Validate key storage
        key_storage = key_mgmt.get("storage", {})
        if not key_storage:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="key_storage_not_configured",
                error_message="Key storage configuration not defined",
                actual_value=key_storage,
                expected_value="key storage configuration",
                severity="error",
                cve_reference=None
            ))
        else:
            # Validate key storage type
            storage_type = key_storage.get("type", "")
            secure_storage_types = ["hsm", "cloud_kms", "vault", "encrypted_file"]
            if storage_type not in secure_storage_types:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insecure_key_storage",
                    error_message=f"Insecure key storage type: {storage_type}",
                    actual_value=storage_type,
                    expected_value="secure storage type (HSM, KMS, Vault)",
                    severity="error",
                    cve_reference=None
                ))
        
        # Validate key rotation policy
        rotation = key_mgmt.get("rotation", {})
        if not rotation.get("enabled", False):
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="key_rotation_not_enabled",
                error_message="Key rotation should be enabled",
                actual_value=rotation.get("enabled"),
                expected_value=True,
                severity="warning",
                cve_reference=None
            ))
        else:
            # Check rotation interval
            rotation_days = rotation.get("interval_days", 0)
            if rotation_days == 0:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_rotation_interval",
                    error_message="Key rotation interval must be greater than 0",
                    actual_value=rotation_days,
                    expected_value="> 0 days",
                    severity="error",
                    cve_reference=None
                ))
            elif rotation_days > 365:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="excessive_rotation_interval",
                    error_message="Key rotation interval should not exceed 365 days",
                    actual_value=rotation_days,
                    expected_value="<= 365 days",
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate key generation
        key_gen = key_mgmt.get("generation", {})
        if key_gen:
            # Check key strength
            key_size = key_gen.get("key_size", 0)
            if key_size < 2048:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="weak_key_size",
                    error_message=f"Key size {key_size} is too weak - use at least 2048 bits",
                    actual_value=key_size,
                    expected_value=">= 2048 bits",
                    severity="error",
                    cve_reference=None
                ))
            
            # Check algorithm
            algorithm = key_gen.get("algorithm", "")
            secure_algorithms = ["RSA-2048", "RSA-4096", "AES-256", "ECDSA-P256"]
            if algorithm not in secure_algorithms:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="weak_key_algorithm",
                    error_message=f"Weak key algorithm: {algorithm}",
                    actual_value=algorithm,
                    expected_value="secure algorithm (RSA-2048+, AES-256, ECDSA)",
                    severity="warning",
                    cve_reference=None
                ))
        
        return errors
    
    async def _validate_input_sanitization(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate input sanitization"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        input_config = layer_spec.get("input_validation", {})
        if not input_config:
            error = SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="missing_input_validation",
                error_message="Input validation not configured",
                actual_value=input_config,
                expected_value="input validation configuration",
                severity=rule.severity,
                cve_reference=None
            )
            errors.append(error)
        
        return errors
    
    async def _validate_parameter_validation(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate parameter validation"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if parameter validation is configured
        param_config = layer_spec.get("parameter_validation", {})
        if not param_config:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="parameter_validation_not_configured",
                error_message="Parameter validation configuration not defined",
                actual_value=None,
                expected_value="parameter validation configuration",
                severity="warning",
                cve_reference=None
            ))
            return errors
        
        # Validate parameter types
        param_types = param_config.get("types", {})
        if param_types:
            for param_name, param_type in param_types.items():
                if param_type not in ["string", "integer", "float", "boolean", "array", "object"]:
                    errors.append(SecurityValidationError(
                        layer_id=layer_name,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="invalid_parameter_type",
                        error_message=f"Invalid parameter type for {param_name}: {param_type}",
                        actual_value=param_type,
                        expected_value="valid parameter type",
                        severity="warning",
                        cve_reference=None
                    ))
        
        # Validate parameter constraints
        constraints = param_config.get("constraints", {})
        if constraints:
            for param_name, constraint in constraints.items():
                if isinstance(constraint, dict):
                    # Check for reasonable constraint values
                    if "max_length" in constraint:
                        max_len = constraint["max_length"]
                        if max_len <= 0 or max_len > 1000000:  # 1MB limit
                            errors.append(SecurityValidationError(
                                layer_id=layer_name,
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="unreasonable_max_length",
                                error_message=f"Unreasonable max_length for {param_name}: {max_len}",
                                actual_value=max_len,
                                expected_value="0 < max_length <= 1000000",
                                severity="warning",
                                cve_reference=None
                            ))
                    
                    if "min_value" in constraint and "max_value" in constraint:
                        if constraint["min_value"] > constraint["max_value"]:
                            errors.append(SecurityValidationError(
                                layer_id=layer_name,
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="invalid_value_range",
                                error_message=f"Invalid value range for {param_name}: min > max",
                                actual_value=f"min={constraint['min_value']}, max={constraint['max_value']}",
                                expected_value="min <= max",
                                severity="error",
                                cve_reference=None
                            ))
        
        # Validate sanitization rules
        sanitization = param_config.get("sanitization", {})
        if sanitization:
            required_sanitizers = ["xss", "sql_injection", "html_escape"]
            configured_sanitizers = sanitization.get("enabled", [])
            
            for sanitizer in required_sanitizers:
                if sanitizer not in configured_sanitizers:
                    errors.append(SecurityValidationError(
                        layer_id=layer_name,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="missing_sanitizer",
                        error_message=f"Missing critical sanitizer: {sanitizer}",
                        actual_value=configured_sanitizers,
                        expected_value=f"include {sanitizer}",
                        severity="warning",
                        cve_reference=None
                    ))
        
        return errors
    
    async def _validate_type_validation(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate type validation"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if type validation is configured
        type_config = layer_spec.get("type_validation", {})
        if not type_config:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="type_validation_not_configured",
                error_message="Type validation configuration not defined",
                actual_value=None,
                expected_value="type validation configuration",
                severity="warning",
                cve_reference=None
            ))
            return errors
        
        # Validate strict type checking
        strict_types = type_config.get("strict_types", False)
        if not strict_types:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="strict_types_not_enabled",
                error_message="Strict type checking should be enabled for security",
                actual_value=strict_types,
                expected_value=True,
                severity="warning",
                cve_reference=None
            ))
        
        # Validate type casting rules
        casting_rules = type_config.get("casting", {})
        if casting_rules:
            # Check for unsafe casting
            unsafe_casts = casting_rules.get("allow_unsafe", False)
            if unsafe_casts:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="unsafe_type_casting",
                    error_message="Unsafe type casting should not be allowed",
                    actual_value=unsafe_casts,
                    expected_value=False,
                    severity="error",
                    cve_reference=None
                ))
            
            # Validate allowed conversions
            allowed_conversions = casting_rules.get("allowed_conversions", [])
            dangerous_conversions = ["string_to_code", "array_to_object", "json_to_function"]
            for conversion in allowed_conversions:
                if conversion in dangerous_conversions:
                    errors.append(SecurityValidationError(
                        layer_id=layer_name,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="dangerous_type_conversion",
                        error_message=f"Dangerous type conversion allowed: {conversion}",
                        actual_value=conversion,
                        expected_value="safe conversions only",
                        severity="error",
                        cve_reference=None
                    ))
        
        # Validate schema validation
        schema_validation = type_config.get("schema_validation", {})
        if schema_validation:
            if not schema_validation.get("enabled", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="schema_validation_not_enabled",
                    error_message="Schema validation should be enabled",
                    actual_value=schema_validation.get("enabled"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
        
        return errors
    
    async def _validate_output_encoding(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate output encoding"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if output encoding is configured
        output_config = layer_spec.get("output_encoding", {})
        if not output_config:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="output_encoding_not_configured",
                error_message="Output encoding configuration not defined",
                actual_value=None,
                expected_value="output encoding configuration",
                severity="error",
                cve_reference=None
            ))
            return errors
        
        # Validate HTML encoding
        html_encoding = output_config.get("html", {})
        if html_encoding:
            if not html_encoding.get("auto_escape", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="html_auto_escape_not_enabled",
                    error_message="HTML auto-escape should be enabled to prevent XSS",
                    actual_value=html_encoding.get("auto_escape"),
                    expected_value=True,
                    severity="error",
                    cve_reference=None
                ))
            
            # Check for unsafe HTML contexts
            unsafe_contexts = html_encoding.get("unsafe_contexts", [])
            if unsafe_contexts:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="unsafe_html_contexts",
                    error_message=f"Unsafe HTML contexts configured: {unsafe_contexts}",
                    actual_value=unsafe_contexts,
                    expected_value="no unsafe contexts",
                    severity="error",
                    cve_reference=None
                ))
        
        # Validate JSON encoding
        json_encoding = output_config.get("json", {})
        if json_encoding:
            if not json_encoding.get("secure_serialization", True):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insecure_json_serialization",
                    error_message="JSON serialization should be secure",
                    actual_value=json_encoding.get("secure_serialization"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate URL encoding
        url_encoding = output_config.get("url", {})
        if url_encoding:
            if not url_encoding.get("encode_all_parameters", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="url_parameters_not_encoded",
                    error_message="All URL parameters should be encoded",
                    actual_value=url_encoding.get("encode_all_parameters"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate Content Security Policy
        csp_config = output_config.get("csp", {})
        if not csp_config.get("enabled", False):
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="csp_not_enabled",
                error_message="Content Security Policy should be enabled",
                actual_value=csp_config.get("enabled"),
                expected_value=True,
                severity="warning",
                cve_reference=None
            ))
        
        return errors
    
    async def _validate_content_filtering(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate content filtering"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if content filtering is configured
        content_config = layer_spec.get("content_filtering", {})
        if not content_config:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="content_filtering_not_configured",
                error_message="Content filtering configuration not defined",
                actual_value=None,
                expected_value="content filtering configuration",
                severity="warning",
                cve_reference=None
            ))
            return errors
        
        # Validate input content filtering
        input_filtering = content_config.get("input", {})
        if input_filtering:
            # Check for malicious content detection
            if not input_filtering.get("malware_detection", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="malware_detection_not_enabled",
                    error_message="Malware detection should be enabled for input content",
                    actual_value=input_filtering.get("malware_detection"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
            
            # Validate file upload restrictions
            file_uploads = input_filtering.get("file_uploads", {})
            if file_uploads:
                if not file_uploads.get("scan_uploads", True):
                    errors.append(SecurityValidationError(
                        layer_id=layer_name,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="file_scanning_not_enabled",
                        error_message="File upload scanning should be enabled",
                        actual_value=file_uploads.get("scan_uploads"),
                        expected_value=True,
                        severity="error",
                        cve_reference=None
                    ))
                
                # Check file size limits
                max_file_size = file_uploads.get("max_file_size", 0)
                if max_file_size == 0 or max_file_size > 100 * 1024 * 1024:  # 100MB limit
                    errors.append(SecurityValidationError(
                        layer_id=layer_name,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="excessive_file_size_limit",
                        error_message=f"File size limit too large or not set: {max_file_size} bytes",
                        actual_value=max_file_size,
                        expected_value="0 < max_file_size <= 100MB",
                        severity="warning",
                        cve_reference=None
                    ))
                
                # Validate allowed file types
                allowed_types = file_uploads.get("allowed_types", [])
                dangerous_types = [".exe", ".bat", ".cmd", ".scr", ".vbs", ".js"]
                for dangerous_type in dangerous_types:
                    if dangerous_type in allowed_types:
                        errors.append(SecurityValidationError(
                            layer_id=layer_name,
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="dangerous_file_type_allowed",
                            error_message=f"Dangerous file type allowed: {dangerous_type}",
                            actual_value=allowed_types,
                            expected_value=f"exclude {dangerous_type}",
                            severity="error",
                            cve_reference=None
                        ))
        
        # Validate output content filtering
        output_filtering = content_config.get("output", {})
        if output_filtering:
            # Check for data leakage prevention
            if not output_filtering.get("data_leakage_prevention", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="data_leakage_prevention_not_enabled",
                    error_message="Data leakage prevention should be enabled for output",
                    actual_value=output_filtering.get("data_leakage_prevention"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
            
            # Validate sensitive data filtering
            sensitive_patterns = output_filtering.get("sensitive_patterns", [])
            required_patterns = ["ssn", "credit_card", "api_key", "password"]
            for pattern in required_patterns:
                if pattern not in sensitive_patterns:
                    errors.append(SecurityValidationError(
                        layer_id=layer_name,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="missing_sensitive_pattern_filter",
                        error_message=f"Missing sensitive data pattern filter: {pattern}",
                        actual_value=sensitive_patterns,
                        expected_value=f"include {pattern}",
                        severity="warning",
                        cve_reference=None
                    ))
        
        return errors
    
    async def _validate_response_sanitization(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate response sanitization"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if response sanitization is configured
        response_config = layer_spec.get("response_sanitization", {})
        if not response_config:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="response_sanitization_not_configured",
                error_message="Response sanitization configuration not defined",
                actual_value=None,
                expected_value="response sanitization configuration",
                severity="warning",
                cve_reference=None
            ))
            return errors
        
        # Validate response headers sanitization
        headers_sanitization = response_config.get("headers", {})
        if headers_sanitization:
            if not headers_sanitization.get("remove_sensitive_headers", True):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="sensitive_headers_not_removed",
                    error_message="Sensitive headers should be removed from responses",
                    actual_value=headers_sanitization.get("remove_sensitive_headers"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
            
            # Check for security headers
            security_headers = headers_sanitization.get("security_headers", {})
            required_headers = ["X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection"]
            for header in required_headers:
                if not security_headers.get(header, False):
                    errors.append(SecurityValidationError(
                        layer_id=layer_name,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="missing_security_header",
                        error_message=f"Missing security header: {header}",
                        actual_value=security_headers.get(header),
                        expected_value=True,
                        severity="warning",
                        cve_reference=None
                    ))
        
        # Validate response body sanitization
        body_sanitization = response_config.get("body", {})
        if body_sanitization:
            # Check for error message sanitization
            if not body_sanitization.get("sanitize_error_messages", True):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="error_messages_not_sanitized",
                    error_message="Error messages should be sanitized to prevent information leakage",
                    actual_value=body_sanitization.get("sanitize_error_messages"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
            
            # Validate stack trace handling
            stack_trace_config = body_sanitization.get("stack_traces", {})
            if stack_trace_config.get("include_in_response", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="stack_traces_in_response",
                    error_message="Stack traces should not be included in responses",
                    actual_value=stack_trace_config.get("include_in_response"),
                    expected_value=False,
                    severity="error",
                    cve_reference=None
                ))
            
            # Check for debug information
            if body_sanitization.get("include_debug_info", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="debug_info_in_response",
                    error_message="Debug information should not be included in production responses",
                    actual_value=body_sanitization.get("include_debug_info"),
                    expected_value=False,
                    severity="error",
                    cve_reference=None
                ))
        
        # Validate response filtering
        response_filtering = response_config.get("filtering", {})
        if response_filtering:
            # Check for data filtering
            if not response_filtering.get("filter_sensitive_data", True):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="sensitive_data_not_filtered",
                    error_message="Sensitive data should be filtered from responses",
                    actual_value=response_filtering.get("filter_sensitive_data"),
                    expected_value=True,
                    severity="error",
                    cve_reference=None
                ))
            
            # Validate field filtering
            field_filters = response_filtering.get("field_filters", [])
            critical_fields = ["password", "token", "secret", "key"]
            for field in critical_fields:
                if field not in field_filters:
                    errors.append(SecurityValidationError(
                        layer_id=layer_name,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="missing_field_filter",
                        error_message=f"Missing critical field filter: {field}",
                        actual_value=field_filters,
                        expected_value=f"include {field}",
                        severity="warning",
                        cve_reference=None
                    ))
        
        return errors
    
    async def _validate_known_vulnerabilities(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate known vulnerabilities"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if vulnerability scanning is configured
        vuln_config = layer_spec.get("vulnerability_scanning", {})
        if not vuln_config:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="vulnerability_scanning_not_configured",
                error_message="Vulnerability scanning configuration not defined",
                actual_value=None,
                expected_value="vulnerability scanning configuration",
                severity="warning",
                cve_reference=None
            ))
            return errors
        
        # Validate dependency scanning
        dependency_scan = vuln_config.get("dependencies", {})
        if dependency_scan:
            if not dependency_scan.get("enabled", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="dependency_scanning_not_enabled",
                    error_message="Dependency vulnerability scanning should be enabled",
                    actual_value=dependency_scan.get("enabled"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
            
            # Check scan frequency
            scan_frequency = dependency_scan.get("scan_frequency", "")
            if scan_frequency not in ["daily", "weekly", "on_commit"]:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_scan_frequency",
                    error_message=f"Insufficient scan frequency: {scan_frequency}",
                    actual_value=scan_frequency,
                    expected_value="daily, weekly, or on_commit",
                    severity="warning",
                    cve_reference=None
                ))
            
            # Validate vulnerability threshold
            severity_threshold = dependency_scan.get("severity_threshold", "")
            allowed_thresholds = ["low", "medium", "high", "critical"]
            if severity_threshold not in allowed_thresholds:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_severity_threshold",
                    error_message=f"Invalid severity threshold: {severity_threshold}",
                    actual_value=severity_threshold,
                    expected_value="one of: low, medium, high, critical",
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate runtime scanning
        runtime_scan = vuln_config.get("runtime", {})
        if runtime_scan:
            if not runtime_scan.get("enabled", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="runtime_scanning_not_enabled",
                    error_message="Runtime vulnerability scanning should be enabled",
                    actual_value=runtime_scan.get("enabled"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
            
            # Check for real-time protection
            if not runtime_scan.get("real_time_protection", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="real_time_protection_not_enabled",
                    error_message="Real-time vulnerability protection should be enabled",
                    actual_value=runtime_scan.get("real_time_protection"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate CVE database updates
        cve_updates = vuln_config.get("cve_database", {})
        if cve_updates:
            update_frequency = cve_updates.get("update_frequency", "")
            if update_frequency not in ["hourly", "daily"]:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_cve_update_frequency",
                    error_message=f"CVE database update frequency too low: {update_frequency}",
                    actual_value=update_frequency,
                    expected_value="hourly or daily",
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate known vulnerable components
        known_vulnerable = vuln_config.get("known_vulnerable_components", [])
        critical_vulnerable_libs = ["log4j", "openssl-1.1.1", "struts2", "spring-framework<5.3.0"]
        for vulnerable_lib in known_vulnerable_libs:
            if vulnerable_lib in known_vulnerable:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="known_vulnerable_component_present",
                    error_message=f"Known vulnerable component present: {vulnerable_lib}",
                    actual_value=known_vulnerable,
                    expected_value=f"remove {vulnerable_lib}",
                    severity="error",
                    cve_reference=None
                ))
        
        return errors
    
    async def _validate_dependency_vulnerabilities(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate dependency vulnerabilities"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if dependencies are defined
        dependencies = layer_spec.get("dependencies", [])
        if not dependencies:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="dependencies_not_defined",
                error_message="Dependencies not defined for vulnerability scanning",
                actual_value=dependencies,
                expected_value="list of dependencies",
                severity="warning",
                cve_reference=None
            ))
            return errors
        
        # Validate each dependency
        for i, dep in enumerate(dependencies):
            if not isinstance(dep, dict):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_dependency_format",
                    error_message=f"Dependency {i} must be a dictionary",
                    actual_value=dep,
                    expected_value="dependency dictionary",
                    severity="error",
                    cve_reference=None
                ))
                continue
            
            # Check for required dependency fields
            if "name" not in dep:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="dependency_name_missing",
                    error_message=f"Dependency {i} missing required field: name",
                    actual_value=dep,
                    expected_value="include name field",
                    severity="error",
                    cve_reference=None
                ))
            
            if "version" not in dep:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="dependency_version_missing",
                    error_message=f"Dependency {i} missing required field: version",
                    actual_value=dep,
                    expected_value="include version field",
                    severity="warning",
                    cve_reference=None
                ))
            
            # Check for known vulnerable versions
            dep_name = dep.get("name", "")
            dep_version = dep.get("version", "")
            
            # Known vulnerable dependency patterns
            vulnerable_patterns = {
                "log4j": ["2.0", "2.1", "2.2", "2.3"],
                "openssl": ["1.0.0", "1.0.1", "1.0.2", "1.1.0"],
                "struts2": ["2.0", "2.1", "2.2", "2.3"],
                "spring": ["4.0", "4.1", "4.2", "4.3"]
            }
            
            for vuln_lib, vuln_versions in vulnerable_patterns.items():
                if vuln_lib in dep_name.lower():
                    for vuln_version in vuln_versions:
                        if vuln_version in dep_version:
                            errors.append(SecurityValidationError(
                                layer_id=layer_name,
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="vulnerable_dependency_version",
                                error_message=f"Dependency {dep_name} has vulnerable version: {dep_version}",
                                actual_value=dep_version,
                                expected_value=f"upgrade {dep_name} to secure version",
                                severity="error",
                                cve_reference=None
                            ))
            
            # Check for unpinned versions (security risk)
            if dep_version and any(char in dep_version for char in [">", "<", "^", "~", "*"]):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="unpinned_dependency_version",
                    error_message=f"Dependency {dep_name} uses unpinned version: {dep_version}",
                    actual_value=dep_version,
                    expected_value="use pinned version (e.g., 1.2.3)",
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate dependency scanning configuration
        dep_scan_config = layer_spec.get("dependency_scanning", {})
        if dep_scan_config:
            if not dep_scan_config.get("enabled", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="dependency_scanning_disabled",
                    error_message="Dependency scanning should be enabled",
                    actual_value=dep_scan_config.get("enabled"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
        
        return errors
    
    async def _validate_security_patches(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate security patches"""
        errors = []
        layer_name = layer_spec.get("name", "unknown")
        
        # Check if patch management is configured
        patch_config = layer_spec.get("patch_management", {})
        if not patch_config:
            errors.append(SecurityValidationError(
                layer_id=layer_name,
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="patch_management_not_configured",
                error_message="Patch management configuration not defined",
                actual_value=None,
                expected_value="patch management configuration",
                severity="warning",
                cve_reference=None
            ))
            return errors
        
        # Validate patch policy
        patch_policy = patch_config.get("policy", {})
        if patch_policy:
            # Check for automatic patching
            if not patch_policy.get("auto_patch_critical", True):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="auto_patch_critical_disabled",
                    error_message="Automatic patching of critical vulnerabilities should be enabled",
                    actual_value=patch_policy.get("auto_patch_critical"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
            
            # Validate patch window
            patch_window = patch_policy.get("patch_window_days", 0)
            if patch_window == 0:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="patch_window_not_defined",
                    error_message="Patch window must be greater than 0 days",
                    actual_value=patch_window,
                    expected_value="> 0 days",
                    severity="error",
                    cve_reference=None
                ))
            elif patch_window > 30:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="excessive_patch_window",
                    error_message=f"Patch window too long: {patch_window} days - should be ≤ 30 days",
                    actual_value=patch_window,
                    expected_value="≤ 30 days",
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate patch monitoring
        patch_monitoring = patch_config.get("monitoring", {})
        if patch_monitoring:
            if not patch_monitoring.get("enabled", False):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="patch_monitoring_disabled",
                    error_message="Patch monitoring should be enabled",
                    actual_value=patch_monitoring.get("enabled"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
            
            # Check monitoring frequency
            monitoring_frequency = patch_monitoring.get("frequency", "")
            if monitoring_frequency not in ["hourly", "daily", "weekly"]:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="insufficient_monitoring_frequency",
                    error_message=f"Insufficient monitoring frequency: {monitoring_frequency}",
                    actual_value=monitoring_frequency,
                    expected_value="hourly, daily, or weekly",
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate patch history
        patch_history = patch_config.get("history", [])
        if patch_history:
            # Check for recent patches
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=90)
            recent_patches = 0
            
            for patch in patch_history:
                if isinstance(patch, dict) and "applied_date" in patch:
                    try:
                        patch_date = datetime.fromisoformat(patch["applied_date"].replace('Z', '+00:00'))
                        if patch_date >= cutoff_date:
                            recent_patches += 1
                    except ValueError:
                        errors.append(SecurityValidationError(
                            layer_id=layer_name,
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="invalid_patch_date_format",
                            error_message="Patch date format is invalid",
                            actual_value=patch["applied_date"],
                            expected_value="ISO 8601 date",
                            severity="warning",
                            cve_reference=None
                        ))
            
            if recent_patches == 0:
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="no_recent_patches",
                    error_message="No security patches applied in the last 90 days",
                    actual_value=recent_patches,
                    expected_value="> 0 recent patches",
                    severity="warning",
                    cve_reference=None
                ))
        
        # Validate patch testing
        patch_testing = patch_config.get("testing", {})
        if patch_testing:
            if not patch_testing.get("required", True):
                errors.append(SecurityValidationError(
                    layer_id=layer_name,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="patch_testing_not_required",
                    error_message="Patch testing should be required before deployment",
                    actual_value=patch_testing.get("required"),
                    expected_value=True,
                    severity="warning",
                    cve_reference=None
                ))
        
        return errors
    
    def _calculate_security_score(self, errors: List[SecurityValidationError]) -> float:
        """Calculate security score based on validation errors"""
        if not errors:
            return 1.0
        
        # Weight errors by severity
        severity_weights = {
            SecuritySeverity.CRITICAL: 0.0,
            SecuritySeverity.HIGH: 0.2,
            SecuritySeverity.MEDIUM: 0.5,
            SecuritySeverity.LOW: 0.8
        }
        
        total_weight = sum(severity_weights[error.severity] for error in errors)
        average_score = total_weight / len(errors)
        
        return round(average_score, 2)
    
    async def _generate_security_summary(
        self, 
        layer_name: str,
        errors: List[SecurityValidationError]
    ) -> Dict[str, Any]:
        """Generate security summary"""
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
            "most_critical_error": max(error_categories) if error_categories else None
        }
    
    def _extract_security_flags(self, errors: List[SecurityValidationError]) -> List[str]:
        """Extract security flags from validation errors"""
        security_flags = []
        
        for error in errors:
            if error.validation_type == SecurityValidationType.VULNERABILITY:
                security_flags.append("vulnerability_found")
            elif error.validation_type == SecurityValidationType.AUTHENTICATION:
                security_flags.append("authentication_issue")
            elif error.validation_type == SecurityValidationType.AUTHORIZATION:
                security_flags.append("authorization_issue")
            elif error.severity == SecuritySeverity.CRITICAL:
                security_flags.append("critical_security_issue")
        
        return security_flags
    
    async def _estimate_validation_complexity(self, request: LayerSecurityValidationRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.security_rules) // 3
        
        # Add complexity for layer size
        layer_size = len(str(request.layer_spec)) // 1000
        complexity_score += layer_size
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_security_risk_score(self, validation_result: SecurityValidationResult) -> float:
        """Calculate risk score for the security validation (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for security errors
        if validation_result.validation_errors:
            risk_score += 0.4
        
        # Increase risk for critical issues
        critical_errors = [e for e in validation_result.validation_errors if e.severity == SecuritySeverity.CRITICAL]
        if critical_errors:
            risk_score += 0.5
        
        # Increase risk for vulnerabilities
        if validation_result.vulnerability_count > 0:
            risk_score += 0.3
        
        # Increase risk for low security score
        if validation_result.security_score < 0.5:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_security_id(self, request: LayerSecurityValidationRequest, result: SecurityValidationResult) -> str:
        """Generate unique security identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.layer_name}:{result.security_score:.2f}:{result.vulnerability_count}:{timestamp}"
        return f"security_validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: LayerSecurityValidationRequest, error: str) -> LayerSecurityValidationResult:
        """Create safe fallback validation when main validation fails"""
        layer_name = request.layer_spec.get("name", "unknown")
        
        fallback_error = SecurityValidationError(
            layer_id=layer_name,
            rule_id="fallback_rule",
            validation_type=SecurityValidationType.AUTHENTICATION,
            error_category="validation_failed",
            error_message=f"Security validation failed: {error}",
            actual_value="fallback",
            expected_value="success",
            severity=SecuritySeverity.MEDIUM,
            cve_reference=None
        )
        
        fallback_result = SecurityValidationResult(
            is_secure=False,
            security_score=0.0,
            validation_errors=[fallback_error],
            validation_warnings=[],
            vulnerability_count=0,
            security_summary={"fallback": True},
            security_flags=["fallback_mode"]
        )
        
        return LayerSecurityValidationResult(
            validation_result=fallback_result,
            validated_layer=request.layer_spec,
            validation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            security_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when security validation violates safety policies"""
    pass


class LayerSecurityValidationError(Exception):
    """Raised for general layer security validation errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_security_validator(safety_policy: Optional[LayerSecuritySafetyPolicy] = None) -> LayerSecurityValidator:
    """Factory function to create LayerSecurityValidator with optional custom safety policy"""
    return LayerSecurityValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_security_request(request: LayerSecurityValidationRequest) -> tuple[bool, Optional[str]]:
    """Validate layer security request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.layer_spec, dict):
            return False, "Layer specification must be a dictionary"
        
        if not isinstance(request.security_rules, list):
            return False, "Security rules must be a list"
        
        if not isinstance(request.validation_options, dict):
            return False, "Validation options must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
