"""Backward compatibility shim for request_manage_observability_context.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original request_manage_observability_context.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .request_manage_observability_context_types import *
from .request_manage_observability_context_impl import *

__all__ = ['*']  # Re-export all imported names
