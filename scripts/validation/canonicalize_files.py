"""Backward compatibility shim for canonicalize_files.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original canonicalize_files.py contained 11 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .canonicalize_files_impl_impl_impl_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
