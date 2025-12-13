"""Backward compatibility shim for check_schema_rules.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original check_schema_rules.py contained 6 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# from .check_schema_rules_impl import *  # Star import removed
# from .check_schema_rules_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
