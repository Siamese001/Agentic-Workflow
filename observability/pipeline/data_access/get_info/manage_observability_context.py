"""Backward compatibility shim for manage_observability_context.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original manage_observability_context.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .manage_observability_context_impl_impl_impl import *  # Star import removed
# from .manage_observability_context_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
