"""Backward compatibility shim for promoter_with_output.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original promoter_with_output.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .promoter_with_output_impl_impl_impl import *

__all__ = ['*']  # Re-export all imported names
