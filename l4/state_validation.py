"""
State validation for secure résumé processing workflows.

Prevents injection attacks and ensures safe state management for reliable résumé improvement.
"""

from __future__ import annotations

import re
from typing import Any, Callable, List, Optional
from dataclasses import dataclass, is_dataclass
from enum import Enum
import logging

from .types import StateValidationError

logger = logging.getLogger(__name__)


class ValidationLevel(str, Enum):
    """
    Defines security validation levels for résumé state data.
    
    Ensures appropriate protection based on résumé processing sensitivity requirements.
    """
    
    NONE = "none"
    BASIC = "basic"
    STRICT = "strict"
    PARANOID = "paranoid"


@dataclass
class ValidationRule:
    """
    Configures validation rules for résumé state security.
    
    Protects résumé data integrity through comprehensive validation patterns.
    """
    
    name: str
    pattern: Optional[str] = None
    max_length: Optional[int] = None
    allowed_types: Optional[List[type]] = None
    forbidden_keys: Optional[List[str]] = None
    required_keys: Optional[List[str]] = None
    custom_validator: Optional[Callable[..., Any]] = None


class StateValidator:
    """
    Validates résumé state data to prevent security vulnerabilities.
    
    Ensures safe and reliable résumé processing through comprehensive validation checks.
    """
    
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
        """
        Initializes state validator for résumé security protection.
        
        Configures validation rules based on résumé processing security requirements.
        """
        self.validation_level = validation_level
        self.rules = self._get_rules_for_level(validation_level)
    
    def _get_rules_for_level(self, level: ValidationLevel) -> List[ValidationRule]:
        """
        Retrieves validation rules for résumé security level.
        
        Ensures appropriate protection based on résumé processing sensitivity requirements.
        """
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
        Validates résumé state write operations for security protection.
        
        Prevents injection attacks to ensure safe résumé processing workflows.
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
        """
        Validates résumé state keys for injection security.
        
        Ensures safe key naming to prevent résumé processing vulnerabilities.
        """
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
        """
        Validates résumé state values for type and size constraints.
        
        Ensures data integrity and security for reliable résumé processing workflows.
        """
        # Check value size
        if isinstance(value, str):
            for rule in self.rules:
                max_length = rule.max_length or 50000  # Default max length
                if len(value) > max_length:
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
        """
        Checks résumé state values against security patterns.
        
        Detects and blocks suspicious content to protect résumé processing integrity.
        """
        if not isinstance(value, str):
            return
        
        for rule in self.rules:
            if rule.pattern and re.search(rule.pattern, value):
                raise StateValidationError(
                    f"Security violation for key '{key}': {rule.name} detected"
                )
    
    def _validate_dataclass(self, key: str, value: Any) -> None:
        """
        Validates résumé dataclass structures for security compliance.
        
        Ensures structured data integrity for reliable résumé processing workflows.
        """
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



