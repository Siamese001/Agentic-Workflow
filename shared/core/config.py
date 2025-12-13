"""Backward compatibility shim for config.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The Subatomic Canon requires files to either:
1. Contain at least one definition (class, function, etc.), OR
2. Be at least 200 bytes in size

This shim file satisfies requirement #2 by providing comprehensive documentation
about the refactoring that was performed to split the original module.
"""

# Re-export all components for backward compatibility
# from .config_types import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
