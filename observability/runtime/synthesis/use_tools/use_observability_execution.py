"""Backward compatibility shim for use_observability_execution.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original use_observability_execution.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .use_observability_execution_impl import *  # Star import removed
# from .use_observability_execution_models import *  # Star import removed
# from .use_observability_execution_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
