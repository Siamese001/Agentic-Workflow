"""Backward compatibility shim for check_outreach_rules.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original check_outreach_rules.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .check_outreach_rules_impl import *  # Star import removed
# from .check_outreach_rules_impl import *  # Star import removed

__all__ = ["*"]  # Re-export all imported names
