"""
Canon Validator Engine - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional


class Engine:
    """Base engine class."""
    def __init__(self):
        pass
    def run(self, *args, **kwargs) -> Any:
        return None


class ValidationEngine(Engine):
    """Validation engine implementation."""
    pass


__all__ = ['Engine', 'ValidationEngine']
