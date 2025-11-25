from __future__ import annotations

"""DAG executor implementation.

This module provides a minimal async DAGExecutor compatible with the
original infra.dag_engine.DAGExecutor.
"""

from typing import Any, Dict, Iterable, Optional, Set, List

from orchestration.agent_registry import AgentRegistry
from .models import Graph


class DAGExecutor:
    """Minimal async DAG executor.

    This executor:
        • Assumes the graph is acyclic.
        • Executes nodes whose predecessors have already completed.
        • Propagates a single shared context dict through the graph.

    It does not implement retries, backpressure, or persistence. Higher
    layers (e.g., workflow_graph) can build those behaviors on top.
    """

    def __init__(self, graph: Graph, agent_registry: AgentRegistry | None = None) -> None:
        self._graph = graph
        self._agent_registry = agent_registry

    # ------------------------------------------------------------------
    # Agent selection helpers (Phase-1 agent-aware substrate)
    # ------------------------------------------------------------------

    def _select_agent_for_node(self, node_id: str) -> str | None:
        """Select an agent_id for a given node based on metadata.

        This inspects per-node metadata for:
            - preferred_agent_ids
            - agent_type
            - required_capabilities

        and uses the AgentRegistry helpers when available. The chosen
        agent_id is purely advisory and is recorded into the context
        under ``_agent_assignments`` for observability and downstream
        dispatch.
        """

        if self._agent_registry is None:
            return None

        node = self._graph.nodes[node_id]
        meta: Dict[str, Any] = getattr(node, "metadata", {}) or {}

        preferred: List[str] = list(meta.get("preferred_agent_ids", []) or [])
        agent_type: Optional[str] = meta.get("agent_type")
        required_caps: List[str] = list(meta.get("required_capabilities", []) or [])

        # 1) Explicit preferred agent ids.
        for aid in preferred:
            if aid in self._agent_registry.agents:
                return aid

        # 2) Type-based lookup via registry helper.
        if agent_type:
            matches = self._agent_registry.find_agents_by_type(agent_type)
            if matches:
                return matches[0].agent_id

        # 3) Capability-based lookup.
        if required_caps:
            cap = required_caps[0]
            matches = self._agent_registry.find_agents_by_capability(cap)
            if matches:
                return matches[0].agent_id

        return None

    async def run(
        self,
        start_nodes: Optional[Iterable[str]] = None,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if ctx is None:
            ctx = {}

        # Determine which nodes must be executed.
        if start_nodes is None:
            remaining: Set[str] = set(self._graph.nodes.keys())
        else:
            remaining = set(start_nodes)

        completed: Set[str] = set()

        while remaining:
            # Pick nodes whose predecessors are all completed.
            ready: List[str] = []
            for node_id in list(remaining):
                preds = {e.source for e in self._graph.edges if e.target == node_id}
                if preds.issubset(completed):
                    ready.append(node_id)

            if not ready:
                # There is a cycle or unresolved dependency.
                raise RuntimeError("DAGExecutor detected a cycle or unresolved dependency")

            # Execute ready nodes sequentially for simplicity; higher layers
            # can wrap this in concurrency if desired.
            for node_id in ready:
                node = self._graph.nodes[node_id]

                # Record agent assignment, if any.
                agent_id = self._select_agent_for_node(node_id)
                if agent_id is not None:
                    assignments = ctx.setdefault("_agent_assignments", {})
                    assignments[node_id] = agent_id

                ctx = await node.fn(ctx)
                completed.add(node_id)
                remaining.remove(node_id)

        return ctx



