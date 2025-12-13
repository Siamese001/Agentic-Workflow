"""Backward compatibility shim for gen_v6.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original gen_v6.py contained 23 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .gen_v6_impl_impl_impl_impl import *

__all__ = ['*']  # Re-export all imported names
