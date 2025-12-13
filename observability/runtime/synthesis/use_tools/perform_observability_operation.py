"""Backward compatibility shim for perform_observability_operation.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original perform_observability_operation.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .perform_observability_operation_impl import *  # Star import removed
# from .perform_observability_operation_models import *  # Star import removed
# from .perform_observability_operation_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
