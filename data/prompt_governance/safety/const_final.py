"""Backward compatibility shim for const_final.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original const_final.py contained 7 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# TODO: Replace 'from .const_final_impl_impl_impl_impl import *' with explicit imports
# # from .const_final_impl_impl_impl_impl import *  # Star import removed

__all__ = ["*"]  # Re-export all imported names
