from __future__ import annotations
"""
Validation Protocol - Dependency Inversion for L1 → L4
Defines the interface L1 needs without depending on L4 implementation.
"""
from typing import Any, Dict, List, Optional, Protocol


# NAMING FIXED: ValidationProtocol → ValidationProtocol
class ValidationProtocol(Protocol):
    """Protocol defining the validation context interface needed by L1.

    This inverts the L1 → L4 dependency by defining the interface in L1
    that L4's ValidationContext must implement.
    """

    def get_file_path(self) -> str:
        """Get the file path being validated."""
        ...

    def get_project_root(self) -> str:
        """Get the project root path."""
        ...

    def add_violation(self, key: int, message: str, Severity: str = "error") -> None:
        """Add a validation Violation."""
        ...

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get all recorded violations."""
        ...

    def has_violations(self) -> bool:
        """Check if any violations were recorded."""
        ...

    def get_cache(self, key: str) -> Optional[Any]:
        """Get cached value."""
        ...

    def set_cache(self, key: str, value: Any) -> None:
        """Set cached value."""
        ...

    def get_metadata(self, key: str) -> Optional[Any]:
        """Get metadata value."""
        ...

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        ...

# [NAMING ALIAS] PascalCase alias for backward compatibility
