"""
Node result primitives for control-flow orchestration.

This module holds a deterministic result container for DAG nodes,
encapsulating status metadata, payload outputs, and optional error
context. No runtime orchestration logic is included here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class NodeStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    SKIP = "skip"


@dataclass
class NodeResult:
    """Outcome of a DAG node execution."""

    status: NodeStatus
    output: Dict = field(default_factory=dict)
    error: Optional[str] = None
    next_edges: Optional[List[str]] = None
