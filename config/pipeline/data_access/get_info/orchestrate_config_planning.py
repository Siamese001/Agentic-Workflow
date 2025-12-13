"""Backward compatibility shim for orchestrate_config_planning.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original orchestrate_config_planning.py contained 11 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .orchestrate_config_planning_enums import *
from .orchestrate_config_planning_models import *
from .orchestrate_config_planning_models_1 import *
from .orchestrate_config_planning_impl import *

__all__ = ['*']  # Re-export all imported names
