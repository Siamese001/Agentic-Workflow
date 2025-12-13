"""Backward compatibility shim for invoke_observability_tool.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original invoke_observability_tool.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .invoke_observability_tool_impl import *  # Star import removed
# from .invoke_observability_tool_models import *  # Star import removed
# from .invoke_observability_tool_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
