"""
Fact Checker - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional


class FactChecker:
    """Checker for fact verification."""
    def __init__(self):
        self._facts = {}
    
    def register_fact(self, name: str, value: Any) -> None:
        self._facts[name] = value
    
    def check(self, name: str, value: Any) -> bool:
        if name not in self._facts:
            return False
        return self._facts[name] == value


__all__ = ['FactChecker']
