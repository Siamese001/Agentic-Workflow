"""Backward compatibility shim for rg_creative_brief_impl_impl_impl.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original rg_creative_brief_impl_impl_impl.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .brief_v4 import *

__all__ = ['*']  # Re-export all imported names
