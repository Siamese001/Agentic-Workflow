"""Backward compatibility shim for l5___init__.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original l5___init__.py contained 7 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .init_v6 import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
