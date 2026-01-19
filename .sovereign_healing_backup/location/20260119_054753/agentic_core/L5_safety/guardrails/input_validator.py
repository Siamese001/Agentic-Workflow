"""
Input Validator for L5 Safety Guardrails.

Provides input validation utilities for safety checks.
"""
from typing import Any, Dict, List, Optional, Union
import re
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """Validator for input sanitization and validation."""
    
    def __init__(self):
        self._rules: List[callable] = []
    
    def add_rule(self, rule: callable) -> None:
        """Add a validation rule."""
        self._rules.append(rule)
    
    def validate(self, input_data: Any) -> bool:
        """Validate input against all rules."""
        for rule in self._rules:
            if not rule(input_data):
                return False
        return True
    
    def sanitize_string(self, text: str) -> str:
        """Sanitize a string input."""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', text)
        return sanitized.strip()
    
    def validate_type(self, value: Any, expected_type: type) -> bool:
        """Validate that value is of expected type."""
        return isinstance(value, expected_type)
    
    def validate_range(self, value: Union[int, float], min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
        """Validate that value is within range."""
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        return True
    
    def validate_length(self, value: Union[str, list], min_len: Optional[int] = None, max_len: Optional[int] = None) -> bool:
        """Validate that value length is within bounds."""
        length = len(value)
        if min_len is not None and length < min_len:
            return False
        if max_len is not None and length > max_len:
            return False
        return True


def validate_input(data: Any, schema: Dict[str, Any]) -> bool:
    """Validate input data against a schema."""
    validator = InputValidator()
    return validator.validate(data)


__all__ = ['InputValidator', 'validate_input']
