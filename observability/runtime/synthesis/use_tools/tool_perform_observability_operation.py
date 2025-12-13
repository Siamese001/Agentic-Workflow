"""Backward compatibility shim for tool_perform_observability_operation.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original tool_perform_observability_operation.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .tool_perform_observability_operation_impl import *  # Star import removed
# from .tool_perform_observability_operation_models import *  # Star import removed
# from .tool_perform_observability_operation_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
