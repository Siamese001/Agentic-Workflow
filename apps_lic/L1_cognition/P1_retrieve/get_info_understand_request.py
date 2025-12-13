"""Backward compatibility shim for get_info_understand_request.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original get_info_understand_request.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .get_info_understand_request_types import *
from .get_info_understand_request_impl import *

__all__ = ['*']  # Re-export all imported names
