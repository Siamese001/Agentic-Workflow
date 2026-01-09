"""
Canon Validator Agentic V2 - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional


class ValidationContext:
    """Context for validation operations."""
    def __init__(self, **kwargs):
        self._data = kwargs
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


class Validator:
    """Base validator class."""
    def __init__(self, name: str = "Validator"):
        self.name = name
    def validate(self, data: Any) -> bool:
        return True


__all__ = ['ValidationContext', 'Validator']
