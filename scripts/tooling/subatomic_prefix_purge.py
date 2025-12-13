"""Backward compatibility shim for subatomic_prefix_purge.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original subatomic_prefix_purge.py contained 10 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .subatomic_prefix_purge_impl_impl_impl import *

__all__ = ['*']  # Re-export all imported names
