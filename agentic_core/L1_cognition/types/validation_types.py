from __future__ import annotations
'\nValidation Protocol - Dependency Inversion for L1 → L4\nDefines the interface L1 needs without depending on L4 implementation.\n'
from typing import Any, Protocol
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class IValidationProtocol(Protocol):
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

    def add_violation(self, key: int, message: str, Severity: str='error') -> None:
        """Add a validation Violation."""
        ...

    def get_violations(self) -> list[dict[str, Any]]:
        """Get all recorded violations."""
        ...

    def has_violations(self) -> bool:
        """Check if any violations were recorded."""
        ...

    def get_cache(self, key: str) -> Any | None:
        """Get cached value."""
        ...

    def set_cache(self, key: str, value: Any) -> None:
        """Set cached value."""
        ...

    def get_metadata(self, key: str) -> Any | None:
        """Get metadata value."""
        ...

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        ...
