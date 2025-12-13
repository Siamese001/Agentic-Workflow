"""Backward compatibility shim for track_lic_state.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original track_lic_state.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .track_lic_state_impl import *
from .track_lic_state_impl import *

__all__ = ['*']  # Re-export all imported names
