"""Infrastructure dependency error types for fail-closed enforcement.

No component may silently degrade when a required infrastructure dependency
(Redis, vector store, FAISS, RAG) is unavailable.  Raise
InfrastructureDependencyError instead of falling back to a local or
in-process substitute.
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

class InfrastructureDependencyError(RuntimeError):
    """Raised when a mandatory infrastructure dependency is unavailable.

    This error signals a hard failure — the system cannot continue safely
    without the required service.  Callers must not catch this error to
    implement a silent fallback; they should propagate it to the process
    boundary so the deployment is restarted or the operator is alerted.
    """
