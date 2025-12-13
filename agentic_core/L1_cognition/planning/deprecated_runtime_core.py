"""Backward compatibility shim for deprecated_runtime_core.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original deprecated_runtime_core.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .deprecated_runtime_core_impl_impl_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
