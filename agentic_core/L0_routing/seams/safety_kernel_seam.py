"""
Seam for L5 safety core kernel - approved L0→L5 interface.
"""

from __future__ import annotations


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def load_classification_kernel():
    """Load classification_kernel from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.core_kernel.classification_kernel")


def get_classification_cache_context():
    """Get classification_cache_context from L5."""
    return load_classification_kernel().classification_cache_context
