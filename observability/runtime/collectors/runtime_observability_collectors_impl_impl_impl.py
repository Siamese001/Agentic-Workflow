"""Backward compatibility shim for runtime_observability_collectors_impl_impl_impl.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original runtime_observability_collectors_impl_impl_impl.py contained 6 top-level definitions wh
    ich
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .collectors_final import *  # Star import removed

__all__ = ["*"]  # Re-export all imported names
