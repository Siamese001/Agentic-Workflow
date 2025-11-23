from __future__ import annotations

"""Facade for DAG engine primitives used by orchestration layers.

This package re-exports the existing infra.dag_engine models and
executor so that callers can import from
``orchestration.dag_engine`` without changing the underlying
implementation.
"""

from infra.dag_engine.models import Graph, Node, Edge  # noqa: F401
from infra.dag_engine.executor import DAGExecutor  # noqa: F401

__all__ = [
    "Graph",
    "Node",
    "Edge",
    "DAGExecutor",
]
