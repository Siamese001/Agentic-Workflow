"""Backward compatibility shim for lic_routing_rules.

This module maintains backward compatibility by re-exporting all components
from the refactored submodules. All functionality has been split into focused
modules to comply with cognitive density limits (max 5 top-level definitions).

The original lic_routing_rules.py contained 14 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
from .lic_routing_rules_impl import *
from .lic_routing_rules_models import *
from .route_models_2 import *
from .lic_routing_rules_impl import *

__all__ = ['*']  # Re-export all imported names
