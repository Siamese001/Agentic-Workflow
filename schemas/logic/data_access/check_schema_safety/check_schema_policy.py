"""Backward compatibility shim for check_schema_policy.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original check_schema_policy.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .check_schema_policy_impl_impl_impl import *  # Star import removed
# from .check_schema_policy_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
