"""Backward compatibility shim for constitutional_ai.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original constitutional_ai.py contained 16 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .constitutional_ai_impl_impl_impl_impl import *
from .constitutional_ai_models import *
from .constitutional_ai_models_1 import *
from .constitutional_ai_impl import *

__all__ = ['*']  # Re-export all imported names
