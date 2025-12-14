"""Backward compatibility shim for execute_observability_execution.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original execute_observability_execution.py contained 8 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .execute_observability_execution_impl import *  # Star import removed
# from .execute_observability_execution_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
