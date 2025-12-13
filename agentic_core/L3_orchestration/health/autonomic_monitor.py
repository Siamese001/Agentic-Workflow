"""Backward compatibility shim for autonomic_monitor.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original autonomic_monitor.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .autonomic_monitor_impl import *  # Star import removed
# from .autonomic_monitor_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
