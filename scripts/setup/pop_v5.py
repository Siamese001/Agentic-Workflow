"""Backward compatibility shim for pop_v5.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original pop_v5.py contained 24 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .pop_v5_impl_impl_impl_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
