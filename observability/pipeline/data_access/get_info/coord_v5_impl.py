"""Backward compatibility shim for coord_v5_impl.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original coord_v5_impl.py contained 8 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .coord_v5_impl_impl import *

__all__ = ['*']  # Re-export all imported names
