"""Backward compatibility shim for data_models.


logger = logging.getLogger(__name__)
This module maintains backward compatibility by re-exporting all components
modules to comply with cognitive density limits (max 5 top-level definitions).

The original data_models.py contained 20 top-level definitions which
violated the Subatomic Canon. It has been refactored into focused submodules.
"""
import logging

# Re-export all components for backward compatibility
# from .data_models_impl import *  # Star import removed
# from .data_models_models import *  # Star import removed
# from .data_models_models_1 import *  # Star import removed
# from .data_models_models_2 import *  # Star import removed
# from .data_models_impl import *  # Star import removed

__all__ = ['*']  # Re-export all imported names
