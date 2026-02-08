"""DAG Safety Manager - Ensures safe mutations with proper rollback.

This module provides enhanced DAG mutation safety with state snapshots,
validation hooks, and protection against partial state corruption.
"""

import copy
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import networkx as nx

logger = logging.getLogger(__name__)


class MutationPhase(Enum):
    """Phases of a mutation operation."""

    PRE_VALIDATE = "pre_validate"
    MUTATE = "mutate"
    POST_VALIDATE = "post_validate"
    COMMIT = "commit"
    ROLLBACK = "rollback"


@dataclass
class StateSnapshot:
    """Snapshot of DAG state at a point in time."""

    timestamp: float
    graph_copy: nx.DiGraph
    node_attributes: dict[str, dict[str, Any]]
    edge_attributes: dict[str, dict[str, Any]]
    external_state: dict[str, Any] = field(default_factory=dict)

    def restore_to(self, target_graph: nx.DiGraph) -> None:
        """Restore this snapshot to a target graph.

        Args:
            target_graph: Graph to restore state to
        """
        # Clear existing graph
        target_graph.clear()

        # Copy nodes and edges
        target_graph.add_nodes_from(self.graph_copy.nodes(data=True))
        target_graph.add_edges_from(self.graph_copy.edges(data=True))

        # Restore attributes
        for node, attrs in self.node_attributes.items():
            if node in target_graph:
                target_graph.nodes[node].update(attrs)

        for edge, attrs in self.edge_attributes.items():
            if edge in target_graph and edge[0] in target_graph and edge[1] in target_graph[edge[0]]:
                target_graph.edges[edge].update(attrs)


class DAGSafetyManager:
    """Manages DAG mutation safety with comprehensive rollback."""

    def __init__(self, name: str = "default"):
        """Initialize the safety manager.

        Args:
            name: Manager name for logging
        """
        self.name = name
        self._snapshots: list[StateSnapshot] = []
        self._validation_hooks: dict[MutationPhase, list[Callable]] = {phase: [] for phase in MutationPhase}
        self._mutation_stack: list[dict[str, Any]] = []

        logger.debug(f"Initialized DAGSafetyManager: {name}")

    def add_validation_hook(
        self,
        phase: MutationPhase,
        hook: Callable[[nx.DiGraph, dict[str, Any]], None],
    ) -> None:
        """Add a validation hook for a specific phase.

        Args:
            phase: Phase to attach hook to
            hook: Validation function
        """
        self._validation_hooks[phase].append(hook)
        logger.debug(f"Added validation hook for phase: {phase.value}")

    def create_snapshot(
        self,
        graph: nx.DiGraph,
        external_state: dict[str, Any] | None = None,
    ) -> str:
        """Create a snapshot of the current DAG state.

        Args:
            graph: Current graph
            external_state: Optional external state to include

        Returns:
            Snapshot ID
        """
        # Deep copy the graph
        graph_copy = copy.deepcopy(graph)

        # Extract attributes
        node_attributes = {}
        for node in graph.nodes():
            node_attributes[node] = dict(graph.nodes[node])

        edge_attributes = {}
        for edge in graph.edges():
            edge_attributes[edge] = dict(graph.edges[edge])

        # Create snapshot
        snapshot = StateSnapshot(
            timestamp=time.time(),
            graph_copy=graph_copy,
            node_attributes=node_attributes,
            edge_attributes=edge_attributes,
            external_state=external_state or {},
        )

        self._snapshots.append(snapshot)

        # Keep only last 10 snapshots
        if len(self._snapshots) > 10:
            self._snapshots.pop(0)

        snapshot_id = f"snapshot_{len(self._snapshots)}_{int(snapshot.timestamp)}"
        logger.debug(f"Created snapshot: {snapshot_id}")

        return snapshot_id

    def restore_snapshot(self, snapshot_id: str, target_graph: nx.DiGraph) -> bool:
        """Restore a snapshot to the target graph.

        Args:
            snapshot_id: ID of snapshot to restore
            target_graph: Graph to restore to

        Returns:
            True if restored successfully
        """
        # Find snapshot (simplified - in practice use proper ID mapping)
        if not self._snapshots:
            logger.error("No snapshots available")
            return False

        # Restore latest snapshot
        snapshot = self._snapshots[-1]
        snapshot.restore_to(target_graph)

        logger.info("Restored snapshot to graph")
        return True

    def begin_mutation(self, mutation_type: str, metadata: dict[str, Any]) -> str:
        """Begin a mutation operation.

        Args:
            mutation_type: Type of mutation
            metadata: Mutation metadata

        Returns:
            Mutation ID
        """
        mutation_id = f"mutation_{len(self._mutation_stack)}_{int(time.time())}"

        mutation_info = {
            "id": mutation_id,
            "type": mutation_type,
            "metadata": metadata,
            "start_time": time.time(),
            "snapshot_id": None,
        }

        self._mutation_stack.append(mutation_info)
        logger.debug(f"Began mutation: {mutation_id}")

        return mutation_id

    def execute_mutation(
        self,
        graph: nx.DiGraph,
        mutation_func: Callable[[nx.DiGraph], None],
        mutation_id: str,
    ) -> bool:
        """Execute a mutation with full safety checks.

        Args:
            graph: Graph to mutate
            mutation_func: Mutation function
            mutation_id: ID of the mutation

        Returns:
            True if successful
        """
        # Find mutation info
        mutation_info = None
        for m in self._mutation_stack:
            if m["id"] == mutation_id:
                mutation_info = m
                break

        if not mutation_info:
            logger.error(f"Mutation not found: {mutation_id}")
            return False

        try:
            # Phase 1: Pre-validation
            self._run_hooks(MutationPhase.PRE_VALIDATE, graph, mutation_info)

            # Create snapshot
            snapshot_id = self.create_snapshot(graph)
            mutation_info["snapshot_id"] = snapshot_id

            # Phase 2: Mutate
            self._run_hooks(MutationPhase.MUTATE, graph, mutation_info)
            mutation_func(graph)

            # Phase 3: Post-validation
            self._run_hooks(MutationPhase.POST_VALIDATE, graph, mutation_info)

            # Phase 4: Commit
            self._run_hooks(MutationPhase.COMMIT, graph, mutation_info)

            logger.info(f"Mutation successful: {mutation_id}")
            return True

        except Exception as e:
            logger.error(f"Mutation failed: {mutation_id}, error: {e}")

            # Rollback
            try:
                self._run_hooks(MutationPhase.ROLLBACK, graph, mutation_info)
                if mutation_info["snapshot_id"]:
                    self.restore_snapshot(mutation_info["snapshot_id"], graph)
                logger.info(f"Mutation rolled back: {mutation_id}")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {mutation_id}, error: {rollback_error}")

            return False
        finally:
            # Remove from stack
            self._mutation_stack = [m for m in self._mutation_stack if m["id"] != mutation_id]

    def _run_hooks(
        self,
        phase: MutationPhase,
        graph: nx.DiGraph,
        mutation_info: dict[str, Any],
    ) -> None:
        """Run validation hooks for a phase.

        Args:
            phase: Phase to run hooks for
            graph: Current graph
            mutation_info: Mutation information
        """
        for hook in self._validation_hooks[phase]:
            try:
                hook(graph, mutation_info)
            except Exception as e:
                logger.error(f"Validation hook failed in phase {phase.value}: {e}")
                raise

    def get_mutation_history(self) -> list[dict[str, Any]]:
        """Get history of mutations.

        Returns:
            List of mutation information
        """
        return copy.deepcopy(self._mutation_stack)

    def clear_history(self) -> None:
        """Clear mutation history and snapshots."""
        self._snapshots.clear()
        self._mutation_stack.clear()
        logger.debug("Cleared mutation history")


# Default validation hooks
def validate_acyclic_hook(graph: nx.DiGraph, mutation_info: dict[str, Any]) -> None:
    """Validate that graph remains acyclic."""
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Mutation would create a cycle")


def validate_connectivity_hook(graph: nx.DiGraph, mutation_info: dict[str, Any]) -> None:
    """Validate graph connectivity."""
    if not nx.is_weakly_connected(graph):
        logger.warning("Mutation created disconnected components")


def validate_node_attributes_hook(graph: nx.DiGraph, mutation_info: dict[str, Any]) -> None:
    """Validate all nodes have required attributes."""
    for node in graph.nodes():
        if "hop_spec" not in graph.nodes[node]:
            raise ValueError(f"Node {node} missing hop_spec attribute")


def validate_depth_consistency_hook(graph: nx.DiGraph, mutation_info: dict[str, Any]) -> None:
    """Validate depth values are consistent."""
    depths = nx.get_node_attributes(graph, "depth")

    for edge in graph.edges():
        source_depth = depths.get(edge[0], 0)
        target_depth = depths.get(edge[1], 0)

        if target_depth <= source_depth:
            raise ValueError(
                f"Depth inconsistency: {edge[0]}({source_depth}) -> {edge[1]}({target_depth})",
            )


def create_default_safety_manager() -> DAGSafetyManager:
    """Create a safety manager with default hooks.

    Returns:
        DAGSafetyManager with default validation hooks
    """
    manager = DAGSafetyManager("default")

    # Add default hooks
    manager.add_validation_hook(MutationPhase.PRE_VALIDATE, validate_acyclic_hook)
    manager.add_validation_hook(MutationPhase.POST_VALIDATE, validate_connectivity_hook)
    manager.add_validation_hook(MutationPhase.POST_VALIDATE, validate_node_attributes_hook)
    manager.add_validation_hook(MutationPhase.POST_VALIDATE, validate_depth_consistency_hook)

    return manager


# Context manager for safe mutations
class SafeMutationContext:
    """Context manager for safe DAG mutations."""

    def __init__(
        self,
        safety_manager: DAGSafetyManager,
        graph: nx.DiGraph,
        mutation_type: str,
        metadata: dict[str, Any] | None = None,
    ):
        """Initialize the context.

        Args:
            safety_manager: Safety manager instance
            graph: Graph to mutate
            mutation_type: Type of mutation
            metadata: Optional metadata
        """
        self.safety_manager = safety_manager
        self.graph = graph
        self.mutation_type = mutation_type
        self.metadata = metadata or {}
        self.mutation_id = None

    def __enter__(self):
        """Enter mutation context.

        Returns:
            Mutation function wrapper
        """
        self.mutation_id = self.safety_manager.begin_mutation(self.mutation_type, self.metadata)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit mutation context.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        if exc_type is not None:
            logger.error(f"Mutation context failed: {exc_val}")
        return False  # Propagate exceptions

    def execute(self, mutation_func: Callable[[nx.DiGraph], None]) -> bool:
        """Execute a mutation safely.

        Args:
            mutation_func: Function to perform mutation

        Returns:
            True if successful
        """
        return self.safety_manager.execute_mutation(self.graph, mutation_func, self.mutation_id)
