from __future__ import annotations

"""Backward-compatible DAG engine shim.

This module preserves the original infra.dag_engine surface by
re-exporting the new flat dag_models and dag_executor modules.
"""

from .dag_models import Node, Edge, Graph  # noqa: F401
from .dag_executor import DAGExecutor  # noqa: F401



