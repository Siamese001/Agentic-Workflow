"""Backward compatibility shim for request_coordinate_observability_queries_impl_impl.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original request_coordinate_observability_queries_impl_impl.py contained 8 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .req_coord_v3 import *

__all__ = ['*']  # Re-export all imported names
