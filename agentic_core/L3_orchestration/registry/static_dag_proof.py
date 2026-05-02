"""StaticDagProof — typed proof of a static L3 DAG specification.

Spec:
    The static DAG describes a managed workflow. A ``StaticDagProof``
    captures everything the L3 runtime receipt MUST be consistent with:
    nodes, edges, entry/terminal points, traversal bounds, and the
    no-execute / no-retrieve / no-prompt-assembly / no-L4-write
    policies that L3 must obey.

The proof is hash-bound (``dag_sha256`` over canonical JSON of stable
fields). The runtime L3 receipt's ``dag_sha256`` MUST equal this value
or verifier fail-closes.

Static doctrine (NEVER negotiable):
    - All nodes MUST have an owner.
    - All nodes MUST have a step_contract_schema.
    - All nodes MUST declare an allowed_execution_surface.
    - L3 MUST NOT execute, retrieve, assemble prompts, or write L4 —
      these policies are stamped into the proof.
    - DAG MUST be acyclic (``has_cycle == False``) unless a bounded
      retry loop is declared with explicit ``bounded_loop_max``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

STATIC_DAG_PROOF_SCHEMA_VERSION = "1.0"

_DIGEST_STABLE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "dag_id",
    "dag_name",
    "dag_version",
    "node_ids",
    "edge_list",
    "entry_nodes",
    "terminal_nodes",
    "node_count",
    "edge_count",
    "max_depth",
    "has_cycle",
    "all_nodes_have_owner",
    "all_nodes_have_step_contract_schema",
    "all_nodes_have_allowed_execution_surface",
    "l3_no_execute_policy",
    "l3_no_retrieve_policy",
    "l3_no_prompt_assembly_policy",
    "l3_no_l4_write_policy",
    "route_ids",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class StaticDagNode:
    """One node in the static DAG."""

    node_id: str
    owner: str
    step_contract_schema: str
    allowed_execution_surface: str  # e.g. "L2_TOOL", "L2_MODEL", "L2_NOOP"

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "owner": self.owner,
            "step_contract_schema": self.step_contract_schema,
            "allowed_execution_surface": self.allowed_execution_surface,
        }


@dataclass(frozen=True)
class StaticDagEdge:
    """Directed edge."""

    from_node: str
    to_node: str
    edge_kind: str = "sequence"  # sequence | branch | bounded_retry

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_node": self.from_node,
            "to_node": self.to_node,
            "edge_kind": self.edge_kind,
        }


@dataclass(frozen=True)
class StaticDagProof:
    """Hash-bound proof of one static DAG specification."""

    dag_id: str
    dag_name: str
    dag_version: str
    nodes: tuple[StaticDagNode, ...]
    edges: tuple[StaticDagEdge, ...]
    entry_nodes: tuple[str, ...]
    terminal_nodes: tuple[str, ...]
    route_ids: tuple[str, ...] = ()
    dag_file_path: str = ""
    dag_registry_ref: str = ""
    dag_registry_sha256: str = ""
    max_depth: int = 0
    has_cycle: bool = False
    bounded_loop_max: int = 0
    schema_version: str = STATIC_DAG_PROOF_SCHEMA_VERSION
    dag_sha256: str = ""

    def __post_init__(self) -> None:
        if not self.dag_id or not isinstance(self.dag_id, str):
            raise ValueError("StaticDagProof.dag_id must be non-empty string")
        if not self.nodes:
            raise ValueError("StaticDagProof.nodes must be non-empty")
        node_ids = {n.node_id for n in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("StaticDagProof.nodes contain duplicate node_id")
        for e in self.edges:
            if e.from_node not in node_ids:
                raise ValueError(f"edge.from_node={e.from_node!r} not in nodes")
            if e.to_node not in node_ids:
                raise ValueError(f"edge.to_node={e.to_node!r} not in nodes")
        for entry in self.entry_nodes:
            if entry not in node_ids:
                raise ValueError(f"entry_node={entry!r} not in nodes")
        for term in self.terminal_nodes:
            if term not in node_ids:
                raise ValueError(f"terminal_node={term!r} not in nodes")
        for n in self.nodes:
            if not n.owner:
                raise ValueError(f"node {n.node_id!r} missing owner")
            if not n.step_contract_schema:
                raise ValueError(
                    f"node {n.node_id!r} missing step_contract_schema"
                )
            if not n.allowed_execution_surface:
                raise ValueError(
                    f"node {n.node_id!r} missing allowed_execution_surface"
                )
        if self.has_cycle and self.bounded_loop_max <= 0:
            raise ValueError(
                "StaticDagProof.has_cycle=True requires bounded_loop_max > 0"
            )
        if self.schema_version != STATIC_DAG_PROOF_SCHEMA_VERSION:
            raise ValueError("StaticDagProof.schema_version mismatch")

    @property
    def all_nodes_have_owner(self) -> bool:
        return all(bool(n.owner) for n in self.nodes)

    @property
    def all_nodes_have_step_contract_schema(self) -> bool:
        return all(bool(n.step_contract_schema) for n in self.nodes)

    @property
    def all_nodes_have_allowed_execution_surface(self) -> bool:
        return all(bool(n.allowed_execution_surface) for n in self.nodes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "dag_id": self.dag_id,
            "dag_name": self.dag_name,
            "dag_version": self.dag_version,
            "dag_file_path": self.dag_file_path,
            "dag_registry_ref": self.dag_registry_ref,
            "dag_registry_sha256": self.dag_registry_sha256,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "node_ids": [n.node_id for n in self.nodes],
            "edge_list": [e.to_dict() for e in self.edges],
            "nodes": [n.to_dict() for n in self.nodes],
            "entry_nodes": list(self.entry_nodes),
            "terminal_nodes": list(self.terminal_nodes),
            "max_depth": self.max_depth,
            "has_cycle": self.has_cycle,
            "bounded_loop_max": self.bounded_loop_max,
            "all_nodes_have_owner": self.all_nodes_have_owner,
            "all_nodes_have_step_contract_schema": self.all_nodes_have_step_contract_schema,
            "all_nodes_have_allowed_execution_surface": self.all_nodes_have_allowed_execution_surface,
            "l3_no_execute_policy": True,
            "l3_no_retrieve_policy": True,
            "l3_no_prompt_assembly_policy": True,
            "l3_no_l4_write_policy": True,
            "route_ids": list(self.route_ids),
            "dag_sha256": self.dag_sha256,
        }


def compute_static_dag_digest(payload: Mapping[str, Any]) -> str:
    """Compute deterministic digest from canonical fields.

    The digest excludes ``dag_file_path`` / ``dag_registry_ref`` /
    ``dag_registry_sha256`` since they are environment-bound. Only the
    intrinsic graph identity participates.
    """
    stable: dict[str, Any] = {}
    for k in _DIGEST_STABLE_FIELDS:
        v = payload.get(k)
        if isinstance(v, (list, tuple)):
            stable[k] = [
                _canonical_json(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            stable[k] = v
    blob = _canonical_json(stable).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def build_static_dag_proof(
    *,
    dag_id: str,
    dag_name: str,
    dag_version: str,
    nodes: tuple[StaticDagNode, ...],
    edges: tuple[StaticDagEdge, ...],
    entry_nodes: tuple[str, ...],
    terminal_nodes: tuple[str, ...],
    route_ids: tuple[str, ...] = (),
    dag_file_path: str = "",
    dag_registry_ref: str = "",
    dag_registry_sha256: str = "",
    max_depth: int = 0,
    has_cycle: bool = False,
    bounded_loop_max: int = 0,
) -> StaticDagProof:
    """Construct and seal a StaticDagProof in one call."""
    pre_payload: dict[str, Any] = {
        "schema_version": STATIC_DAG_PROOF_SCHEMA_VERSION,
        "dag_id": dag_id,
        "dag_name": dag_name,
        "dag_version": dag_version,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "node_ids": [n.node_id for n in nodes],
        "edge_list": [e.to_dict() for e in edges],
        "entry_nodes": list(entry_nodes),
        "terminal_nodes": list(terminal_nodes),
        "max_depth": max_depth,
        "has_cycle": has_cycle,
        "all_nodes_have_owner": all(bool(n.owner) for n in nodes),
        "all_nodes_have_step_contract_schema": all(bool(n.step_contract_schema) for n in nodes),
        "all_nodes_have_allowed_execution_surface": all(bool(n.allowed_execution_surface) for n in nodes),
        "l3_no_execute_policy": True,
        "l3_no_retrieve_policy": True,
        "l3_no_prompt_assembly_policy": True,
        "l3_no_l4_write_policy": True,
        "route_ids": list(route_ids),
    }
    digest = compute_static_dag_digest(pre_payload)
    return StaticDagProof(
        dag_id=dag_id,
        dag_name=dag_name,
        dag_version=dag_version,
        nodes=tuple(nodes),
        edges=tuple(edges),
        entry_nodes=tuple(entry_nodes),
        terminal_nodes=tuple(terminal_nodes),
        route_ids=tuple(route_ids),
        dag_file_path=dag_file_path,
        dag_registry_ref=dag_registry_ref,
        dag_registry_sha256=dag_registry_sha256,
        max_depth=max_depth,
        has_cycle=has_cycle,
        bounded_loop_max=bounded_loop_max,
        dag_sha256=digest,
    )


__all__ = [
    "STATIC_DAG_PROOF_SCHEMA_VERSION",
    "StaticDagEdge",
    "StaticDagNode",
    "StaticDagProof",
    "build_static_dag_proof",
    "compute_static_dag_digest",
]
