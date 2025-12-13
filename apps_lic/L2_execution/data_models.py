"""Backward compatibility shim for data_models.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original data_models.py contained 20 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .data_models_impl import *
from .data_models_models import *
from .data_models_models_1 import *
from .data_models_models_2 import *
from .data_models_impl import *

__all__ = ['*']  # Re-export all imported names
