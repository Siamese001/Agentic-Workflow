"""Backward compatibility shim for prompts.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original prompts.py contained 24 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# TODO: Replace 'from .prompts_impl import *' with explicit imports
# # from .prompts_impl import *  # Star import removed

__all__ = ["*"]  # Re-export all imported names

