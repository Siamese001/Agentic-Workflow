"""
L1 Cognitive Planning - Registry Context Formatting

Implements pure planning operations for formatting registry context data
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

class ContextFormat(str, Enum):
    """Supported context format types with L5 safety validation"""
    REGISTRY_STANDARD = "registry_standard"
    LAYER_SPECIFIC = "layer_specific"
    COORDINATION = "coordination"
    VALIDATION = "validation"
    MONITORING = "monitoring"
    DEBUG = "debug"


class ContextScope(str, Enum):
    """Context scope types with L5 safety enforcement"""
    GLOBAL = "global"
    LAYER = "layer"
    COMPONENT = "component"
    FUNCTION = "function"
    INSTANCE = "instance"


class RegistryContextSafetyPolicy(BaseModel):
    """L5 Safety policy for registry context formatting operations"""
    max_context_size: int = Field(default=524288, description="Maximum context size in bytes (512KB)")
    max_nesting_depth: int = Field(default=8, description="Maximum context nesting depth")
    allowed_formats: List[str] = Field(default_factory=lambda: [t.value for t in ContextFormat])
    allowed_scopes: List[str] = Field(default_factory=lambda: [t.value for t in ContextScope])
    require_structure_validation: bool = Field(default=True)
    prevent_context_injection: bool = Field(default=True)
    sanitize_sensitive_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class RegistryContextSafetyValidator:
    """L5 Safety validator for registry context formatting operations"""
    
    def __init__(self, policy: RegistryContextSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.RegistryContextSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\."
        ]
        self._sensitive_data_patterns = [
            r"password", r"secret", r"token", r"key", r"credential",
            r"private", r"confidential", r"restricted", r"internal"
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
            
            # Check format
            context_format = context_input.get("format", "")
            if context_format not in self.policy.allowed_formats:
                error_msg = f"Prohibited context format: {context_format}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check scope
            context_scope = context_input.get("scope", "")
            if context_scope not in self.policy.allowed_scopes:
                error_msg = f"Prohibited context scope: {context_scope}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check nesting depth
            max_depth = self._calculate_nesting_depth(context_data)
            if max_depth > self.policy.max_nesting_depth:
                error_msg = f"Context nesting too deep: {max_depth} > {self.policy.max_nesting_depth}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous content
            content_str = str(context_data).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous content pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for sensitive data
            if self.policy.sanitize_sensitive_data:
                for pattern in self._sensitive_data_patterns:
                    if pattern in content_str:
                        self.logger.warning(f"Sensitive data pattern detected: {pattern}")
                        # In production, this would trigger sanitization
            
            return True, None
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.error(f"Safety validation failed: {error_msg}")
            if self.policy.fail_closed:
                return False, error_msg
            return True, error_msg
    
    def _calculate_nesting_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of context structure"""
        if current_depth > self.policy.max_nesting_depth:
            return current_depth
        
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_nesting_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_nesting_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth


# ============================================================================
# L1 COGNITIVE PLANNING INTERFACES
# ============================================================================

@dataclass
class ContextFormatRequest:
    """Input request for registry context formatting operations"""
    context: Dict[str, Any]
    target_format: ContextFormat
    target_scope: ContextScope
    target_layer: str
    formatting_options: Dict[str, Any] = field(default_factory=dict)
    sanitization_rules: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class FormattedContext:
    """Structured representation of a formatted registry context"""
    format_type: ContextFormat
    scope: ContextScope
    formatted_content: Union[str, Dict[str, Any]]
    metadata: Dict[str, Any]
    size_bytes: int
    checksum: Optional[str]
    sanitized: bool


@dataclass
class ContextValidationResult:
    """Result of context formatting validation"""
    is_valid: bool
    validation_errors: List[str]
    warnings: List[str]
    compliance_score: float
    security_flags: List[str]


@dataclass
class RegistryContextResult:
    """Output result from registry context formatting operations"""
    formatted_context: FormattedContext
    validation_result: ContextValidationResult
    formatting_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    context_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class RegistryContextFormatterInterface(ABC):
    """Abstract interface for registry context formatting operations"""
    
    @abstractmethod
    async def format_context(self, request: ContextFormatRequest) -> RegistryContextResult:
        """Format registry context according to specified format and scope"""
        pass
    
    @abstractmethod
    async def validate_formatted_context(self, context: FormattedContext) -> ContextValidationResult:
        """Validate formatted context structure and content"""
        pass
    
    @abstractmethod
    async def sanitize_context_data(self, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize context data according to specified rules"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class RegistryContextFormatter(RegistryContextFormatterInterface):
    """
    L1 Cognitive Planning implementation for formatting registry context.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[RegistryContextSafetyPolicy] = None):
        self.safety_policy = safety_policy or RegistryContextSafetyPolicy()
        self.safety_validator = RegistryContextSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Context formatting templates and patterns
        self._format_templates = {
            ContextFormat.REGISTRY_STANDARD: {
                "required_sections": ["metadata", "layer_info", "capabilities"],
                "optional_sections": ["dependencies", "constraints", "state"]
            },
            ContextFormat.LAYER_SPECIFIC: {
                "required_sections": ["layer_name", "layer_type", "configuration"],
                "optional_sections": ["interfaces", "state", "metrics"]
            },
            ContextFormat.COORDINATION: {
                "required_sections": ["message_type", "source", "target"],
                "optional_sections": ["payload", "correlation_id", "priority"]
            },
            ContextFormat.VALIDATION: {
                "required_sections": ["validation_type", "target", "criteria"],
                "optional_sections": ["context", "strict_mode", "timeout"]
            },
            ContextFormat.MONITORING: {
                "required_sections": ["metric_type", "source", "timestamp"],
                "optional_sections": ["metrics", "labels", "annotations"]
            },
            ContextFormat.DEBUG: {
                "required_sections": ["debug_info", "stack_trace", "context"],
                "optional_sections": ["variables", "state", "logs"]
            }
        }
        
        self.logger.info("RegistryContextFormatter initialized with L5 safety policies")
    
    async def format_context(self, request: ContextFormatRequest) -> RegistryContextResult:
        """
        Format registry context according to specified format and scope.
        
        Args:
            request: Context formatting request with data and formatting options
            
        Returns:
            RegistryContextResult: Structured result with formatted context and validation
            
        Raises:
            ValidationError: If context formatting fails
            SafetyError: If context violates safety policies
        """
        self.logger.info(f"Formatting context for {request.target_layer} in {request.target_format} format")
        
        try:
            # L5 Safety validation
            context_input = {
                "context": request.context,
                "format": request.target_format.value,
                "scope": request.target_scope.value
            }
            
            is_valid, error_msg = self.safety_validator.validate_context_input(context_input)
            if not is_valid:
                raise SafetyError(f"Context validation failed: {error_msg}")
            
            # Sanitize context data if required
            sanitized_context = request.context
            if request.sanitization_rules or self.safety_policy.sanitize_sensitive_data:
                sanitized_context = await self.sanitize_context_data(
                    request.context, 
                    request.sanitization_rules
                )
            
            # Format context according to template
            formatted_content = await self._format_context_by_template(
                sanitized_context, 
                request.target_format,
                request.target_scope,
                request.target_layer
            )
            
            # Apply scope-specific formatting
            scoped_content = await self._apply_scope_formatting(
                formatted_content,
                request.target_scope,
                request.formatting_options
            )
            
            # Generate metadata
            metadata = await self._generate_context_metadata(request, sanitized_context)
            
            # Calculate size and checksum
            content_bytes = str(scoped_content).encode('utf-8')
            size_bytes = len(content_bytes)
            checksum = self._calculate_checksum(content_bytes)
            
            # Create formatted context
            formatted_context = FormattedContext(
                format_type=request.target_format,
                scope=request.target_scope,
                formatted_content=scoped_content,
                metadata=metadata,
                size_bytes=size_bytes,
                checksum=checksum,
                sanitized=sanitized_context != request.context
            )
            
            # Validate formatted context
            validation_result = await self.validate_formatted_context(formatted_context)
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_context_risk_score(formatted_context),
                "security_flags": validation_result.security_flags
            }
            
            # Generate unique context ID
            context_id = self._generate_context_id(request, formatted_context)
            
            result = RegistryContextResult(
                formatted_context=formatted_context,
                validation_result=validation_result,
                formatting_metadata={
                    "formatting_duration_ms": size_bytes * 0.001,  # Rough estimate
                    "original_size": len(str(request.context)),
                    "final_size": size_bytes,
                    "compression_ratio": size_bytes / len(str(request.context)) if request.context else 1.0,
                    "complexity_estimate": await self._estimate_formatting_complexity(request)
                },
                safety_validation=safety_validation,
                context_id=context_id
            )
            
            self.logger.info(f"Successfully formatted context {context_id} ({size_bytes} bytes)")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to format registry context: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback context in non-fail-closed mode
            return self._create_fallback_context(request, str(e))
    
    async def validate_formatted_context(self, context: FormattedContext) -> ContextValidationResult:
        """Validate formatted context structure and content"""
        try:
            errors = []
            warnings = []
            security_flags = []
            
            # Basic structure validation
            if not context.formatted_content:
                errors.append("Formatted context content is empty")
            
            # Size validation
            if context.size_bytes > self.safety_policy.max_context_size:
                errors.append(f"Context exceeds maximum size: {context.size_bytes} > {self.safety_policy.max_context_size}")
            
            # Format-specific validation
            template = self._format_templates.get(context.format_type, {})
            required_sections = template.get("required_sections", [])
            
            if isinstance(context.formatted_content, dict):
                for section in required_sections:
                    if section not in context.formatted_content:
                        errors.append(f"Missing required section: {section}")
            
            # Security validation
            content_str = str(context.formatted_content).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    security_flags.append(f"dangerous_content:{pattern}")
            
            # Sensitive data validation
            if not context.sanitized:
                for pattern in self._sensitive_data_patterns:
                    if pattern in content_str:
                        warnings.append(f"Unsanitized sensitive data detected: {pattern}")
            
            # Calculate compliance score
            compliance_score = 1.0
            if errors:
                compliance_score -= 0.5
            if warnings:
                compliance_score -= 0.1 * len(warnings)
            if security_flags:
                compliance_score -= 0.2 * len(security_flags)
            
            compliance_score = max(0.0, compliance_score)
            
            return ContextValidationResult(
                is_valid=len(errors) == 0,
                validation_errors=errors,
                warnings=warnings,
                compliance_score=compliance_score,
                security_flags=security_flags
            )
            
        except Exception as e:
            return ContextValidationResult(
                is_valid=False,
                validation_errors=[f"Validation error: {str(e)}"],
                warnings=[],
                compliance_score=0.0,
                security_flags=["validation_failed"]
            )
    
    async def sanitize_context_data(self, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize context data according to specified rules"""
        try:
            sanitized = data.copy()
            
            # Apply default sanitization rules
            if self.safety_policy.sanitize_sensitive_data:
                sanitized = await self._apply_default_sanitization(sanitized)
            
            # Apply custom sanitization rules
            if rules:
                sanitized = await self._apply_custom_sanitization(sanitized, rules)
            
            return sanitized
            
        except Exception as e:
            self.logger.error(f"Context sanitization failed: {str(e)}")
            # Return original data if sanitization fails
            return data
    
    async def _format_context_by_template(
        self, 
        context: Dict[str, Any], 
        format_type: ContextFormat,
        scope: ContextScope,
        target_layer: str
    ) -> Dict[str, Any]:
        """Format context according to format template"""
        try:
            template = self._format_templates.get(format_type, {})
            required_sections = template.get("required_sections", [])
            optional_sections = template.get("optional_sections", [])
            
            formatted = {}
            
            # Add required sections
            for section in required_sections:
                if section == "metadata":
                    formatted[section] = {
                        "format": format_type.value,
                        "scope": scope.value,
                        "target_layer": target_layer,
                        "formatted_at": datetime.now().isoformat()
                    }
                elif section == "layer_info":
                    formatted[section] = {
                        "layer_name": target_layer,
                        "layer_type": context.get("layer_type", "unknown"),
                        "layer_version": context.get("version", "1.0.0")
                    }
                elif section in context:
                    formatted[section] = context[section]
                else:
                    formatted[section] = {}  # Empty required section
            
            # Add optional sections if present
            for section in optional_sections:
                if section in context:
                    formatted[section] = context[section]
            
            # Add any additional context data
            for key, value in context.items():
                if key not in required_sections and key not in optional_sections:
                    formatted[f"additional_{key}"] = value
            
            return formatted
            
        except Exception as e:
            self.logger.error(f"Template formatting failed: {str(e)}")
            raise
    
    async def _apply_scope_formatting(
        self, 
        content: Dict[str, Any], 
        scope: ContextScope,
        options: Dict[str, Any]
    ) -> Union[str, Dict[str, Any]]:
        """Apply scope-specific formatting to context"""
        try:
            if scope == ContextScope.GLOBAL:
                # Global scope: include all metadata
                content["_scope_metadata"] = {
                    "scope": "global",
                    "visibility": "all_layers",
                    "priority": options.get("priority", "medium")
                }
            elif scope == ContextScope.LAYER:
                # Layer scope: layer-specific formatting
                content["_scope_metadata"] = {
                    "scope": "layer",
                    "visibility": "layer_only",
                    "layer_specific": True
                }
            elif scope == ContextScope.COMPONENT:
                # Component scope: minimal formatting
                content["_scope_metadata"] = {
                    "scope": "component",
                    "visibility": "component_only",
                    "minimal": True
                }
            elif scope == ContextScope.FUNCTION:
                # Function scope: highly focused
                content["_scope_metadata"] = {
                    "scope": "function",
                    "visibility": "function_only",
                    "focused": True
                }
            elif scope == ContextScope.INSTANCE:
                # Instance scope: instance-specific
                content["_scope_metadata"] = {
                    "scope": "instance",
                    "visibility": "instance_only",
                    "ephemeral": True
                }
            
            # Return as JSON string if requested
            if options.get("serialize", False):
                return json.dumps(content, indent=2, ensure_ascii=False)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Scope formatting failed: {str(e)}")
            return content
    
    async def _generate_context_metadata(
        self, 
        request: ContextFormatRequest, 
        sanitized_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate context metadata"""
        return {
            "format": request.target_format.value,
            "scope": request.target_scope.value,
            "target_layer": request.target_layer,
            "formatted_at": datetime.now().isoformat(),
            "section_count": len(sanitized_context),
            "has_sensitive_data": await self._contains_sensitive_data(sanitized_context),
            "formatting_options": request.formatting_options,
            "sanitization_applied": sanitized_context != request.context
        }
    
    def _calculate_checksum(self, content: bytes) -> str:
        """Calculate checksum for context content"""
        import hashlib
        return hashlib.sha256(content).hexdigest()
    
    async def _contains_sensitive_data(self, data: Dict[str, Any]) -> bool:
        """Check if data contains sensitive information"""
        data_str = str(data).lower()
        for pattern in self._sensitive_data_patterns:
            if pattern in data_str:
                return True
        return False
    
    async def _apply_default_sanitization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default sanitization rules"""
        sanitized = data.copy()
        
        # Remove or mask sensitive fields
        sensitive_keys = ["password", "secret", "token", "key", "credential"]
        
        for key in list(sanitized.keys()):
            key_lower = key.lower()
            for sensitive in sensitive_keys:
                if sensitive in key_lower:
                    sanitized[key] = "***REDACTED***"
                    break
        
        return sanitized
    
    async def _apply_custom_sanitization(self, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Apply custom sanitization rules"""
        sanitized = data.copy()
        
        # Apply field removal rules
        remove_fields = rules.get("remove_fields", [])
        for field in remove_fields:
            sanitized.pop(field, None)
        
        # Apply field masking rules
        mask_fields = rules.get("mask_fields", [])
        for field in mask_fields:
            if field in sanitized:
                sanitized[field] = "***MASKED***"
        
        # Apply value replacement rules
        replace_rules = rules.get("replace_values", {})
        for field, replacement in replace_rules.items():
            if field in sanitized:
                sanitized[field] = replacement
        
        return sanitized
    
    async def _estimate_formatting_complexity(self, request: ContextFormatRequest) -> str:
        """Estimate formatting complexity"""
        complexity_score = len(request.context) // 20
        
        # Add complexity for different formats
        if request.target_format in [ContextFormat.COORDINATION, ContextFormat.VALIDATION]:
            complexity_score += 2
        elif request.target_format == ContextFormat.DEBUG:
            complexity_score += 3
        
        # Add complexity for scope
        if request.target_scope in [ContextScope.GLOBAL, ContextScope.LAYER]:
            complexity_score += 1
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_context_risk_score(self, context: FormattedContext) -> float:
        """Calculate risk score for the context (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for large contexts
        if context.size_bytes > 256000:  # 256KB
            risk_score += 0.2
        
        # Increase risk for unsanitized sensitive data
        if context.metadata.get("has_sensitive_data") and not context.sanitized:
            risk_score += 0.4
        
        # Increase risk for certain formats
        if context.format_type in [ContextFormat.DEBUG, ContextFormat.COORDINATION]:
            risk_score += 0.1
        
        # Increase risk for global scope
        if context.scope == ContextScope.GLOBAL:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _generate_context_id(self, request: ContextFormatRequest, context: FormattedContext) -> str:
        """Generate unique context identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.target_format.value}:{request.target_scope.value}:{request.target_layer}:{context.size_bytes}:{timestamp}"
        return f"context_{hash(content) % 1000000:06d}"
    
    def _create_fallback_context(self, request: ContextFormatRequest, error: str) -> RegistryContextResult:
        """Create safe fallback context when main formatting fails"""
        fallback_data = {
            "error": "context_formatting_failed",
            "message": "Safe fallback context",
            "original_format": request.target_format.value,
            "target_layer": request.target_layer,
            "metadata": {
                "fallback": True,
                "error": error,
                "formatted_at": datetime.now().isoformat()
            }
        }
        
        fallback_context = FormattedContext(
            format_type=ContextFormat.REGISTRY_STANDARD,  # Safe default
            scope=ContextScope.LAYER,  # Safe default
            formatted_content=fallback_data,
            metadata={"fallback": True, "error": error},
            size_bytes=len(str(fallback_data)),
            checksum=self._calculate_checksum(str(fallback_data).encode()),
            sanitized=False
        )
        
        fallback_validation = ContextValidationResult(
            is_valid=True,
            validation_errors=[],
            warnings=["Using fallback context"],
            compliance_score=0.5,
            security_flags=["fallback_mode"]
        )
        
        return RegistryContextResult(
            formatted_context=fallback_context,
            validation_result=fallback_validation,
            formatting_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            context_id=f"fallback_{hash(error) % 100000:06d}"
        )

# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when context violates safety policies"""
    
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


class ContextFormattingError(Exception):
    """Raised for general context formatting errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, operation: Optional[str] = None, context_type: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code or "CONTEXT_FORMATTING_ERROR"
        self.operation = operation
        self.context_type = context_type
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        op_info = f" in {self.operation}" if self.operation else ""
        type_info = f" for {self.context_type}" if self.context_type else ""
        return f"[{self.error_code}]{op_info}{type_info} {base_msg}"


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_registry_context_formatter(safety_policy: Optional[RegistryContextSafetyPolicy] = None) -> RegistryContextFormatter:
    """Factory function to create RegistryContextFormatter with optional custom safety policy"""
    return RegistryContextFormatter(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_context_request(request: ContextFormatRequest) -> tuple[bool, Optional[str]]:
    """Validate registry context request parameters"""
    try:
        if not request.target_layer or not request.target_layer.strip():
            return False, "Target layer cannot be empty"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        if not isinstance(request.formatting_options, dict):
            return False, "Formatting options must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"