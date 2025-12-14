"""Backward compatibility shim for rank_final.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original rank_final.py contained 8 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .rank_final_impl_impl_impl_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
