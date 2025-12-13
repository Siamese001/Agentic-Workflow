"""Backward compatibility shim for gen_apps_impl_impl_impl_impl.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original gen_apps_impl_impl_impl_impl.py contained 23 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .gen_final import *

__all__ = ['*']  # Re-export all imported names
