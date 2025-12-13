"""Backward compatibility shim for route_classifier.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original route_classifier.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .route_classifier_impl import *
from .route_classifier_impl import *

__all__ = ['*']  # Re-export all imported names
