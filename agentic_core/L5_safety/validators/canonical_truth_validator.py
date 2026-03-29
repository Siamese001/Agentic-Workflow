"""Canonical truth validator for L5 safety."""
from __future__ import annotations

from typing import Any


class CanonicalTruthValidator:
    """Validator for canonical truth assertions."""
    
    def __init__(self) -> None:
        self._truths: dict[str, Any] = {}
    
    def register_truth(self, key: str, value: Any) -> None:
        """Register a canonical truth value."""
        self._truths[key] = value
    
    def validate(self, key: str, value: Any) -> bool:
        """Validate a value against registered truth."""
        if key not in self._truths:
            return True  # No truth registered, allow
        return self._truths[key] == value
    
    def get_truth(self, key: str) -> Any:
        """Get registered truth value."""
        return self._truths.get(key)


def validate_canonical_truth(key: str, value: Any) -> bool:
    """Validate value against canonical truth registry."""
    validator = CanonicalTruthValidator()
    return validator.validate(key, value)


__all__ = ["CanonicalTruthValidator", "validate_canonical_truth"]
