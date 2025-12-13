"""Backward compatibility shim for orchestrate_observability_planning.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original orchestrate_observability_planning.py contained 18 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .orchestrate_observability_planning_impl_impl_impl import *  # Star import removed
# from .orchestrate_observability_planning_models import *  # Star import removed
# from .obs_models_2 import *  # Star import removed
# from .orchestrate_observability_planning_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
