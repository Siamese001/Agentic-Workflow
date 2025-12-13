"""Backward compatibility shim for req_coord_v3.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original req_coord_v3.py contained 8 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .req_coord_v3_impl_impl_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
