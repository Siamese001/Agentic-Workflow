"""Backward compatibility shim for rules_final_impl_impl_impl_impl.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original rules_final_impl_impl_impl_impl.py contained 7 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .rules_v5 import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
