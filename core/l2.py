from __future__ import annotations

"""Core L2 execution shim.

This module re-exports the historical top-level l2 functions so callers
can import from core.l2 without breaking existing code.

It also explicitly exposes the internal ``_execute_*`` helpers required by
``workflow_graph.py`` when importing from ``core.l2``.
"""

from l2 import (  # type: ignore[import]
    _execute_strategy,
    _execute_retrieval,
    _execute_drafting,
    _execute_qa,
    _execute_safety,
)
from l2 import *  # noqa: F401,F403

__all__ = [
    # Internal execution helpers used by workflow_graph
    "_execute_strategy",
    "_execute_retrieval",
    "_execute_drafting",
    "_execute_qa",
    "_execute_safety",
]
