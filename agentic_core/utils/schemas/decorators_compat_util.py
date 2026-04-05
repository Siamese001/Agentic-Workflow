"""
Backward compatibility module for decorators.

This module provides backward compatibility for imports expecting
agentic_core.utils.decorators by re-exporting from decorators_util.
"""

from .decorators_util import *

__all__ = [name for name in dir() if not name.startswith("_")]
