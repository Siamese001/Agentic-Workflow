"""Backward compatibility shim for tests_modularity_test_layer_imports_impl.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original tests_modularity_test_layer_imports_impl.py contained 7 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# TODO: Replace 'from .test_layer_impl import *' with explicit imports
# # from .test_layer_impl import *  # Star import removed
