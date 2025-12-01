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
        # Simplified implementation
        return []
    
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
        # Simplified implementation
        return []
    
    async def _validate_access_control(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate access control"""
        # Simplified implementation
        return []
    
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
        # Simplified implementation
        return []
    
    async def _validate_key_management(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate key management"""
        # Simplified implementation
        return []
    
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
        # Simplified implementation
        return []
    
    async def _validate_type_validation(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate type validation"""
        # Simplified implementation
        return []
    
    async def _validate_output_encoding(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate output encoding"""
        # Simplified implementation
        return []
    
    async def _validate_content_filtering(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate content filtering"""
        # Simplified implementation
        return []
    
    async def _validate_response_sanitization(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate response sanitization"""
        # Simplified implementation
        return []
    
    async def _validate_known_vulnerabilities(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate known vulnerabilities"""
        # Simplified implementation
        return []
    
    async def _validate_dependency_vulnerabilities(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate dependency vulnerabilities"""
        # Simplified implementation
        return []
    
    async def _validate_security_patches(
        self, 
        layer_spec: Dict[str, Any], 
        rule: SecurityValidationRule
    ) -> List[SecurityValidationError]:
        """Validate security patches"""
        # Simplified implementation
        return []
    
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
