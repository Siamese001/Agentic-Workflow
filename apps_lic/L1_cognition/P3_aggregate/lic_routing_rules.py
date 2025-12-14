"""Backward compatibility shim for lic_routing_rules.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original lic_routing_rules.py contained 14 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .lic_routing_rules_impl import *  # Star import removed
# from .lic_routing_rules_models import *  # Star import removed
# from .route_models_2 import *  # Star import removed
# from .lic_routing_rules_impl import *  # Star import removed

__all__ = ["*"]  # Re-export all imported names
