"""Infrastructure dependency error types for fail-closed enforcement.

No component may silently degrade when a required infrastructure dependency
(Redis, vector store, FAISS, RAG) is unavailable.  Raise
InfrastructureDependencyError instead of falling back to a local or
in-process substitute.
"""
from __future__ import annotations
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class InfrastructureDependencyError(RuntimeError):
    """Raised when a mandatory infrastructure dependency is unavailable.

    This error signals a hard failure — the system cannot continue safely
    without the required service.  Callers must not catch this error to
    implement a silent fallback; they should propagate it to the process
    boundary so the deployment is restarted or the operator is alerted.
    """
