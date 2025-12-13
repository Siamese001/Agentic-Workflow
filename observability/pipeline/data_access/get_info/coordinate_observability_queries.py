"""Backward compatibility shim for coordinate_observability_queries.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original coordinate_observability_queries.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .coordinate_observability_queries_impl_impl_impl import *
from .coordinate_observability_queries_impl import *

__all__ = ['*']  # Re-export all imported names
