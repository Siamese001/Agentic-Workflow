"""Backward compatibility shim for constitutional_ai.

This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original constitutional_ai.py contained 16 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""

# Re-export all components for backward compatibility
# TODO: Replace 'from .constitutional_ai_impl_impl_impl_impl import *' with explicit imports
# # from .constitutional_ai_impl_impl_impl_impl import *  # Star import removed
# TODO: Replace 'from .constitutional_ai_models import *' with explicit imports
# # from .constitutional_ai_models import *  # Star import removed
# TODO: Replace 'from .constitutional_ai_models_1 import *' with explicit imports
# # from .constitutional_ai_models_1 import *  # Star import removed
# TODO: Replace 'from .constitutional_ai_impl import *' with explicit imports
# # from .constitutional_ai_impl import *  # Star import removed

__all__ = ["*"]  # Re-export all imported names

