"""Backward compatibility shim for structure_policy_check_safety.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original structure_policy_check_safety.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .structure_policy_check_safety_types import *
from .structure_policy_check_safety_impl import *

__all__ = ['*']  # Re-export all imported names
