"""L3 static-DAG registry.

Provides the SSOT for ``StaticDagProof`` construction and lookup. Used
by ``MANAGED_WORKFLOW`` runs to bind a typed runtime L3 receipt to a
verifiable static DAG specification.
"""

from agentic_core.L3_orchestration.registry.static_dag_proof import (
    STATIC_DAG_PROOF_SCHEMA_VERSION,
    StaticDagEdge,
    StaticDagNode,
    StaticDagProof,
    build_static_dag_proof,
    compute_static_dag_digest,
)
from agentic_core.L3_orchestration.registry.static_dag_registry import (
    DEMO_TWO_NODE_DAG_ID,
    StaticDagRegistry,
    get_default_registry,
)

__all__ = [
    "DEMO_TWO_NODE_DAG_ID",
    "STATIC_DAG_PROOF_SCHEMA_VERSION",
    "StaticDagEdge",
    "StaticDagNode",
    "StaticDagProof",
    "StaticDagRegistry",
    "build_static_dag_proof",
    "compute_static_dag_digest",
    "get_default_registry",
]
