"""Backward compatibility shim for collectors_v7.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original collectors_v7.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .collectors_v7_impl import *

__all__ = ['*']  # Re-export all imported names
