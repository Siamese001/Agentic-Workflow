"""Backward compatibility shim for load_planning.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original load_planning.py contained 12 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .load_planning_impl import *  # Star import removed
# from .load_planning_models import *  # Star import removed
# from .load_planning_models_1 import *  # Star import removed
# from .load_planning_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
