"""Runtime Utils - Utility functions for runtime operations."""

from .main_util import main

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

try:
    from .runtime_bootstrapper import *  # noqa: F401,F403
except ImportError:
    pass

__all__ = [
    "main",
]
