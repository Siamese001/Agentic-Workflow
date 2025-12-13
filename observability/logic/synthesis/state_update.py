"""Backward compatibility shim for state_update.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original state_update.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .state_update_types import *
from .state_update_impl import *

__all__ = ['*']  # Re-export all imported names
