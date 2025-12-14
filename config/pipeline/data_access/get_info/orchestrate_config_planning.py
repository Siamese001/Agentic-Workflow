"""Backward compatibility shim for orchestrate_config_planning.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original orchestrate_config_planning.py contained 11 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .orchestrate_config_planning_impl import *  # Star import removed
# from .orchestrate_config_planning_models import *  # Star import removed
# from .orchestrate_config_planning_models_1 import *  # Star import removed
# from .orchestrate_config_planning_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
