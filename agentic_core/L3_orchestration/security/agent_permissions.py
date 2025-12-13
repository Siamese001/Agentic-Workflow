"""Backward compatibility shim for agent_permissions.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original agent_permissions.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .agent_permissions_types import *
from .agent_permissions_impl import *

__all__ = ['*']  # Re-export all imported names
