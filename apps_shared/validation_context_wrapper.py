"""
Validation Context - Thin Wrapper
Delegates to Universal Context in agentic_core/infra/context.py

This is a backward compatibility shim. All new code should import directly from:
    from agentic_core.infra.context import context
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Set

from agentic_core.infra.context import get_context

logger = logging.getLogger(__name__)


class ValidationContext:
    """
    Thin wrapper around Universal Context for backward compatibility.
    
    Delegates all operations to the singleton Universal Context.
    """
    
    def __init__(self):
        """Initialize wrapper (delegates to singleton)."""
        self._ctx = get_context()
        logger.debug("ValidationContext wrapper initialized")
    
    @property
    def modified_files(self) -> Set[Path]:
        """Get modified files."""
        return self._ctx.modified_files
    
    @property
    def signals(self) -> Set[str]:
        """Get signals."""
        return self._ctx.signals
    
    @property
    def file_hashes(self) -> Dict[str, str]:
        """Get file hashes."""
        return self._ctx.file_hashes
    
    @property
    def cycle_id(self) -> int:
        """Get cycle ID."""
        return self._ctx.cycle_id
    
    @property
    def status(self) -> str:
        """Get status."""
        return self._ctx.status
    
    def add_modified_file(self, file_path: Path):
        """Add a file to the modified set."""
        self._ctx.add_modified_file(file_path)
    
    def add_signal(self, signal: str):
        """Add a signal to the context."""
        self._ctx.add_signal(signal)
    
    def update_file_hash(self, file_path: str, file_hash: str):
        """Update the hash for a file."""
        self._ctx.update_file_hash(file_path, file_hash)
    
    def get_file_hash(self, file_path: str) -> Optional[str]:
        """Get the hash for a file."""
        return self._ctx.get_file_hash(file_path)
    
    def save_memory(self):
        """Save memory to disk."""
        self._ctx.save_memory()
    
    def reset_for_new_cycle(self):
        """Reset for new cycle."""
        self._ctx.reset_for_new_cycle()
    
    def complete_cycle(self, status: str = "COMPLETED"):
        """Complete the cycle."""
        self._ctx.complete_cycle(status)


def create_validation_context() -> ValidationContext:
    """
    Factory function for backward compatibility.
    
    Returns:
        ValidationContext wrapper
    """
    return ValidationContext()
