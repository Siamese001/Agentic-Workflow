"""
DAG engine compatibility shim for résumé processing workflows.

Preserves backward compatibility while supporting comprehensive résumé enhancement operations.
"""

from .dag_models import Node, Edge, Graph  # noqa: F401
from .dag_executor import DAGExecutor  # noqa: F401



