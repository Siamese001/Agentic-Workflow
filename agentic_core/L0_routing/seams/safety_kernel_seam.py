"""
Seam for L5 safety core kernel - approved L0→L5 interface.
"""
from __future__ import annotations
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def load_classification_kernel():
    """Load classification_kernel from L5."""
    import importlib
    return importlib.import_module('agentic_core.L5_safety.core_kernel.classification_kernel')

def get_classification_cache_context():
    """Get classification_cache_context from L5."""
    return load_classification_kernel().classification_cache_context
