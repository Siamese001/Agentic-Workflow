"""Runtime Utils - Utility functions for runtime operations."""
from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

from .main_util import main

try:
    from .runtime_bootstrapper import *
# guardian: allow-silent-swallow - optional dependency
        except ImportError:
    pass
__all__ = ['main']