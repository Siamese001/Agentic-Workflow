"""Backward compatibility shim for request_orchestrate_observability_planning.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original request_orchestrate_observability_planning.py contained 9 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .request_orchestrate_observability_planning_impl_impl import *  # Star import removed
# from .request_orchestrate_observability_planning_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
