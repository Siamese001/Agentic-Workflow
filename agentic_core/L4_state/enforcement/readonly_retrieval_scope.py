"""
Phase 6 — Read-Only Retrieval Scope: mutation blocker for L4 retrieval paths.

Guarantees:
- read_only_retrieval_scope(): context manager that activates the read-only flag.
- is_read_only_retrieval_active(): returns True when inside the scope.
- assert_not_read_only(operation): raises RetrievalMutationViolation if scope active.

Any persistent mutation (Redis setex/set, Pinecone upsert, file write) that calls
assert_not_read_only() during an active retrieval scope is deterministically blocked
and surfaces as a typed pre-action violation.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Module-level flag — single-threaded agent model assumed (same as Phase 4 sandbox).
_READ_ONLY_RETRIEVAL_ACTIVE: bool = False


class RetrievalMutationViolation(Exception):
    """
    Raised when a persistent mutation is attempted inside a read-only retrieval scope.

    Attributes
    ----------
    code   : str  — always "RETRIEVAL_MUTATION_BLOCKED"
    detail : str  — human-readable description of the blocked operation
    """

    code: str = "RETRIEVAL_MUTATION_BLOCKED"

    def __init__(self, detail: str = "") -> None:
        self.detail = detail
        super().__init__(
            f"[{self.code}] Mutation blocked inside read-only retrieval scope"
            + (f": {detail}" if detail else "")
        )


def is_read_only_retrieval_active() -> bool:
    """Return True when a read_only_retrieval_scope() is currently active."""
    return _READ_ONLY_RETRIEVAL_ACTIVE


def assert_not_read_only(operation: str = "") -> None:
    """
    Raise RetrievalMutationViolation if a read-only retrieval scope is active.

    Call this at the top of any persistent-write seam (Redis set/setex,
    Pinecone upsert, file write) that must be blocked during retrieval.

    Parameters
    ----------
    operation : str
        Short description of the attempted mutation (e.g., "redis.setex",
        "pinecone.upsert"). Included in the violation detail for traceability.
    """
    if _READ_ONLY_RETRIEVAL_ACTIVE:
        raise RetrievalMutationViolation(detail=operation)


@contextmanager
def read_only_retrieval_scope() -> Generator[None, None, None]:
    """
    Context manager that activates the read-only retrieval flag.

    Usage
    -----
    with read_only_retrieval_scope():
        results = l4_semantic_query(query)   # safe — read-only
        # any assert_not_read_only() call here raises RetrievalMutationViolation

    Guarantees
    ----------
    - Flag is set to True on entry.
    - Flag is restored to False on exit (even on exception).
    - Re-entrant: nested scopes are allowed (flag stays True until outermost exits).
    """
    global _READ_ONLY_RETRIEVAL_ACTIVE
    already_active = _READ_ONLY_RETRIEVAL_ACTIVE
    _READ_ONLY_RETRIEVAL_ACTIVE = True
    try:
        yield
    finally:
        if not already_active:
            _READ_ONLY_RETRIEVAL_ACTIVE = False
