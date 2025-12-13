"""Backward compatibility shim for deprecated_triplet_store_and_entities.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original deprecated_triplet_store_and_entities.py contained 8 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .deprecated_triplet_store_and_entities_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
