"""
Backward compatibility module for decorators.

This module provides backward compatibility for imports expecting
agentic_core.utils.decorators by re-exporting from decorators_util.
"""

from .decorators_util import *

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Ensure all decorators_util exports are available as decorators
__all__ = [name for name in dir() if not name.startswith("_")]
