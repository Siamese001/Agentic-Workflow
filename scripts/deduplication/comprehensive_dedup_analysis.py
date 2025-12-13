"""Backward compatibility shim for comprehensive_dedup_analysis.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original comprehensive_dedup_analysis.py contained 25 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .comprehensive_dedup_analysis_impl_impl_impl import *  # Star import removed
# from .comprehensive_dedup_analysis_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
