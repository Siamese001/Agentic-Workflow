"""
Canon Validator - Stub module for backwards compatibility.

This module provides stub implementations for tests that import from canon_validator.
"""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ValidationContext:
    """Context for validation operations."""
    
    def __init__(self, **kwargs):
        self._data = kwargs
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self._data[key] = value


class Validator:
    """Base validator class."""
    
    def __init__(self, name: str = "Validator"):
        self.name = name
    
    def validate(self, data: Any, context: Optional[ValidationContext] = None) -> bool:
        return True


class CanonValidator(Validator):
    """Canon validator implementation."""
    pass


__all__ = ['ValidationContext', 'Validator', 'CanonValidator']
