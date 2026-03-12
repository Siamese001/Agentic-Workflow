"""
Backward compatibility module for decorators.

This module provides backward compatibility for imports expecting
agentic_core.utils.decorators by re-exporting from decorators_util.
"""
from .decorators_util import *
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
__all__ = [name for name in dir() if not name.startswith('_')]
