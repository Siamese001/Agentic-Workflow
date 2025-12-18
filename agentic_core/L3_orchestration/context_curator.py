"""Backward compatibility shim for context_curator.


LOGGER = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original context_curator.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .context_curator_impl import *  # Star import removed
# from .context_curator_impl import *  # Star import removed

__all__ = ["*"]  # Re-export all imported names
