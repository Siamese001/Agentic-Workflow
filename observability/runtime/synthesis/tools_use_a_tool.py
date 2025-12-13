"""Backward compatibility shim for tools_use_a_tool.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original tools_use_a_tool.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .tool_types import *  # Star import removed
# from .tools_use_a_tool_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
