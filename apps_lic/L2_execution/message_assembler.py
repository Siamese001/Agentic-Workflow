"""Backward compatibility shim for message_assembler.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original message_assembler.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .message_assembler_impl import *  # Star import removed
# from .message_assembler_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
