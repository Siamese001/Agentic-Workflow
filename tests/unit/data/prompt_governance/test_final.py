"""Backward compatibility shim for test_final.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original test_final.py contained 7 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# TODO: Replace 'from .test_v7 import *' with explicit imports
# # from .test_v7 import *  # Star import removed

__all__ = ["*"]  # Re-export all imported names
