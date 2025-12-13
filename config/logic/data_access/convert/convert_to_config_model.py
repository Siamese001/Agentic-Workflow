"""Backward compatibility shim for convert_to_config_model.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original convert_to_config_model.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .convert_to_config_model_enums import *
from .convert_to_config_model_models import *
from .convert_to_config_model_impl import *

__all__ = ['*']  # Re-export all imported names
