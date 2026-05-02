"""StaticDagRegistry — single SSOT for static DAG specifications.

For this pass the registry contains exactly one DAG: the
``mw_demo_two_node`` 2-node DAG used by the structural-only
``integrated_managed_workflow_run`` entry point. Future DAGs simply
register themselves with the same ``StaticDagProof`` shape.

Doctrine alignment:
    Layer-gravity: this module lives in ``agentic_core.L3_orchestration``
    so any layer above L3 (apps_*, system_learning, infrastructure) can
    consume it; nothing below L3 may.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.L3_orchestration.registry.static_dag_proof import (
    StaticDagEdge,
    StaticDagNode,
    StaticDagProof,
    build_static_dag_proof,
)

DEMO_TWO_NODE_DAG_ID = "mw_demo_two_node"
DEMO_TWO_NODE_DAG_VERSION = "1.0"


def _build_demo_two_node_dag() -> StaticDagProof:
    """Construct the 2-node demo DAG used by the structural MW run.

    node_a (entry)  --sequence-->  node_b (terminal)

    Both nodes declare ``L2_NOOP`` so the structural-only run can hand
    them to L2 without invoking real tools or models.
    """
    nodes = (
        StaticDagNode(
            node_id="node_a",
            owner="agentic_core.L3_orchestration.registry.static_dag_registry",
            step_contract_schema="L3StepContract.v1",
            allowed_execution_surface="L2_NOOP",
        ),
        StaticDagNode(
            node_id="node_b",
            owner="agentic_core.L3_orchestration.registry.static_dag_registry",
            step_contract_schema="L3StepContract.v1",
            allowed_execution_surface="L2_NOOP",
        ),
    )
    edges = (
        StaticDagEdge(from_node="node_a", to_node="node_b", edge_kind="sequence"),
    )
    return build_static_dag_proof(
        dag_id=DEMO_TWO_NODE_DAG_ID,
        dag_name="MW Demo Two-Node DAG",
        dag_version=DEMO_TWO_NODE_DAG_VERSION,
        nodes=nodes,
        edges=edges,
        entry_nodes=("node_a",),
        terminal_nodes=("node_b",),
        route_ids=("MW_DEMO_TWO_NODE",),
        dag_registry_ref=(
            "agentic_core.L3_orchestration.registry.static_dag_registry."
            "DEMO_TWO_NODE_DAG_ID"
        ),
        max_depth=2,
        has_cycle=False,
    )


@dataclass(frozen=True)
class StaticDagRegistry:
    """Read-only registry over the in-process catalog."""

    catalog: dict[str, StaticDagProof]

    def get(self, dag_id: str) -> StaticDagProof:
        if dag_id not in self.catalog:
            raise KeyError(
                f"StaticDagRegistry: dag_id={dag_id!r} not registered; "
                f"known: {sorted(self.catalog.keys())}"
            )
        return self.catalog[dag_id]

    def known_dag_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self.catalog.keys()))


_DEFAULT_REGISTRY: StaticDagRegistry | None = None


def get_default_registry() -> StaticDagRegistry:
    """Return the process-wide default registry (lazy-built once)."""
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = StaticDagRegistry(
            catalog={
                DEMO_TWO_NODE_DAG_ID: _build_demo_two_node_dag(),
            }
        )
    return _DEFAULT_REGISTRY


__all__ = [
    "DEMO_TWO_NODE_DAG_ID",
    "DEMO_TWO_NODE_DAG_VERSION",
    "StaticDagRegistry",
    "get_default_registry",
]
