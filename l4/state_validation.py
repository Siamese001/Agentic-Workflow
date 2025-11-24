"""State Validation for L4 Security

Adds validation and sanitization to prevent state injection attacks
and ensure safe state writes in the L4 manager.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, is_dataclass
from enum import Enum
import logging

from .types import StateValidationError, StateOperation

logger = logging.getLogger(__name__)


class ValidationLevel(str, Enum):
    """Levels of state validation."""
    
    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"
    PARANOID = "paranoid"


@dataclass
class ValidationRule:
    """Rule for validating state data."""
    
    name: str
    pattern: Optional[str] = None
    max_length: Optional[int] = None
    allowed_types: Optional[List[type]] = None
    forbidden_keys: Optional[List[str]] = None
    required_keys: Optional[List[str]] = None
    custom_validator: Optional[callable] = None


class StateValidator:
    """Validates state data to prevent injection attacks."""
    
    # Basic validation rules
    BASIC_RULES = [
        ValidationRule(
            name="no_command_injection",
            pattern=r'(?i)(exec|eval|system|subprocess|os\.system)',
            max_length=10000
        ),
        ValidationRule(
            name="no_file_operations",
            pattern=r'(?i)(open|read|write|delete|remove)\s*\(',
        ),
        ValidationRule(
            name="no_network_requests",
            pattern=r'(?i)(requests\.|urllib|http|https|ftp)',
        ),
    ]
    
    # Strict validation rules
    STRICT_RULES = BASIC_RULES + [
        ValidationRule(
            name="no_base64_content",
            pattern=r'[A-Za-z0-9+/]{40,}={0,2}',
        ),
        ValidationRule(
            name="no_nested_json_attacks",
            pattern=r'\{[^{}]*\{[^{}]*\{',
        ),
        ValidationRule(
            name="no_script_tags",
            pattern=r'(?i)<script[^>]*>.*?</script>',
        ),
    ]
    
    # Paranoid validation rules
    PARANOID_RULES = STRICT_RULES + [
        ValidationRule(
            name="no_code_blocks",
            pattern=r'```[a-zA-Z]*\n.*```',
        ),
        ValidationRule(
            name="no_shell_commands",
            pattern=r'[;&|`$()]',
        ),
        ValidationRule(
            name="no_import_statements",
            pattern=r'(?i)import\s+\w+|from\s+\w+\s+import',
        ),
    ]
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STRICT):
        """Initialize state validator with security level."""
        self.validation_level = validation_level
        self.rules = self._get_rules_for_level(validation_level)
    
    def _get_rules_for_level(self, level: ValidationLevel) -> List[ValidationRule]:
        """Get validation rules for the specified level."""
        if level == ValidationLevel.NONE:
            return []
        elif level == ValidationLevel.BASIC:
            return self.BASIC_RULES
        elif level == ValidationLevel.STRICT:
            return self.STRICT_RULES
        elif level == ValidationLevel.PARANOID:
            return self.PARANOID_RULES
        else:
            return self.BASIC_RULES
    
    def validate_state_write(self, key: str, value: Any) -> None:
        """
        Validate a state write operation to prevent injection attacks.
        
        Args:
            key: State key being written
            value: Value being written
            
        Raises:
            StateValidationError: If validation fails
        """
        # Check key validation
        self._validate_key(key)
        
        # Check value validation
        self._validate_value(key, value)
        
        # Check for suspicious patterns
        self._check_patterns(key, value)
        
        # Check dataclass constraints if applicable
        if is_dataclass(value):
            self._validate_dataclass(key, value)
    
    def _validate_key(self, key: str) -> None:
        """Validate state key for injection attempts."""
        # Check for forbidden characters in keys
        forbidden_chars = [';', '&', '|', '`', '$', '(', ')']
        for char in forbidden_chars:
            if char in key:
                raise StateValidationError(
                    f"Forbidden character '{char}' in state key: {key}"
                )
        
        # Check for suspicious key patterns
        suspicious_patterns = [
            r'(?i)(command|exec|eval|system)',
            r'(?i)(inject|malicious|attack)',
            r'\.\.',  # Path traversal
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, key):
                raise StateValidationError(
                    f"Suspicious pattern in state key: {key}"
                )
    
    def _validate_value(self, key: str, value: Any) -> None:
        """Validate state value for type and size constraints."""
        # Check value size
        if isinstance(value, str):
            max_length = 50000  # Default max length
            for rule in self.rules:
                if rule.max_length and len(value) > rule.max_length:
                    raise StateValidationError(
                        f"Value too long for key '{key}': {len(value)} > {rule.max_length}"
                    )
        
        # Check for allowed types
        allowed_types = [str, int, float, bool, list, dict, type(None)]
        if not any(isinstance(value, t) for t in allowed_types):
            raise StateValidationError(
                f"Invalid type for key '{key}': {type(value).__name__}"
            )
        
        # Recursively validate collections
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                self.validate_state_write(f"{key}.{sub_key}", sub_value)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                self.validate_state_write(f"{key}[{i}]", item)
    
    def _check_patterns(self, key: str, value: Any) -> None:
        """Check value against security patterns."""
        if not isinstance(value, str):
            return
        
        for rule in self.rules:
            if rule.pattern and re.search(rule.pattern, value):
                raise StateValidationError(
                    f"Security violation for key '{key}': {rule.name} detected"
                )
    
    def _validate_dataclass(self, key: str, value: Any) -> None:
        """Validate dataclass fields for security."""
        if not is_dataclass(value):
            return
        
        for field_name, field_value in value.__dict__.items():
            try:
                self.validate_state_write(f"{key}.{field_name}", field_value)
            except StateValidationError as e:
                raise StateValidationError(
                    f"Dataclass validation failed for {key}.{field_name}: {str(e)}"
                )
    
    def sanitize_input(self, value: Any) -> Any:
        """
        Sanitize input value to remove potentially harmful content.
        
        Args:
            value: Value to sanitize
            
        Returns:
            Sanitized value
        """
        if not isinstance(value, str):
            return value
        
        # Remove potentially harmful patterns
        sanitized = value
        
        # Remove script tags
        sanitized = re.sub(r'(?i)<script[^>]*>.*?</script>', '', sanitized, flags=re.DOTALL)
        
        # Remove code blocks
        sanitized = re.sub(r'```[a-zA-Z]*\n.*?```', '', sanitized, flags=re.DOTALL)
        
        # Remove shell command patterns
        sanitized = re.sub(r'[;&|`$()]', '', sanitized)
        
        # Limit length
        max_length = 50000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "...[truncated]"
        
        return sanitized


@dataclass
class SecureStateManagerConfig:
    """Configuration for secure state manager."""
    
    validation_level: ValidationLevel = ValidationLevel.STRICT
    enable_sanitization: bool = True
    audit_log_writes: bool = True
    max_state_size: int = 1000000  # 1MB default


def create_state_validator(config: SecureStateManagerConfig) -> StateValidator:
    """Create a state validator with the given configuration."""
    return StateValidator(config.validation_level)


__all__ = [
    'ValidationLevel',
    'ValidationRule',
    'StateValidator', 
    'SecureStateManagerConfig',
    'create_state_validator',
]



