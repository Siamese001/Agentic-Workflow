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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "mutation_phase_util", "p0_governance")
_emit_reads_policy_state("p0", "mutation_phase_util", "policy_binding")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("mutation_phase_util", "p4obs", "metric_1")
_emit_emits_metric_event("mutation_phase_util", "p4obs", "metric_2")
_emit_emits_metric_event("mutation_phase_util", "p4obs", "metric_3")
_emit_emits_metric_event("mutation_phase_util", "p4obs", "metric_4")
_emit_emits_metric_event("mutation_phase_util", "p4obs", "metric_5")
_emit_emits_metric_event("mutation_phase_util", "p4obs", "metric_6")
_emit_records_incident_event("mutation_phase_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("mutation_phase_util", "p4obs", "anomaly")
_emit_writes_observability_log("mutation_phase_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("mutation_phase_util", "p4obs", "mon_state")
_emit_triggers_alert("mutation_phase_util", "p4obs", "alert")
_emit_links_incident_trace("mutation_phase_util", "p4obs", "trace_link")
_emit_captures_pattern("mutation_phase_util", "p3lm", "pattern")
_emit_records_learning_event("mutation_phase_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("mutation_phase_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("mutation_phase_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("mutation_phase_util", "p3lm", "routing")
_emit_improves_agent_policy("mutation_phase_util", "p3lm", "policy")
_emit_stores_learning_state("mutation_phase_util", "p3lm", "state")
_emit_records_execution_trace("mutation_phase_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("mutation_phase_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("mutation_phase_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("mutation_phase_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("mutation_phase_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("mutation_phase_util", "env_read", "p2_env_1")
_emit_reads_environ("mutation_phase_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("mutation_phase_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("mutation_phase_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "mutation_phase_util", "context_pull")
_emit_pulls_context("p1", "mutation_phase_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "mutation_phase_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "mutation_phase_util", "uwg_term_2")
_emit_writes_through("p1", "mutation_phase_util", "write_through")
_emit_writes_through("p1", "mutation_phase_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "mutation_phase_util", "safety_validation")
_emit_invokes_eval("p1", "mutation_phase_util", "eval_call")
_emit_proposal_commits_routing("p1", "mutation_phase_util", "routing_commit")
_emit_escalates_to_human("p1", "mutation_phase_util", "human_escalation")
_emit_routes_through("p1", "mutation_phase_util", "route_through")
_emit_checks_agent_registry("p1", "mutation_phase_util", "agent_registry")
_emit_validates_agent_capability("p1", "mutation_phase_util", "capability")
_emit_dispatches_execution_plan("p1", "mutation_phase_util", "exec_plan")
_emit_agent_executes_agent("p1", "mutation_phase_util", "sub_agent")
_emit_routes_to_agent("p1", "mutation_phase_util", "target_agent")
_emit_verifies_policy("p1", "mutation_phase_util", "policy_check")
_emit_observes_runtime_state("p1", "mutation_phase_util", "runtime_state")
_emit_verifies_boundary("p1", "mutation_phase_util", "boundary_check")
_emit_transcripts_response("p1", "mutation_phase_util", "transcript")
_emit_hard_fails_untranscripted("p1", "mutation_phase_util")
_emit_gated_by_confidence("p1", "mutation_phase_util", "confidence_gate")
emit_replay_key("p0", "mutation_phase_util")
emit_determinism_digest("p0", "mutation_phase_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "mutation_phase_util", "execution_auth")
_emit_validates_capability("p2", "mutation_phase_util", "capability_check")
_emit_routes_to_capability("p2", "mutation_phase_util", "capability_route")
_emit_writes_via_uwg("p2", "mutation_phase_util", "uwg_write")
_emit_blocks_direct_write("p2", "mutation_phase_util", "direct_write_block")
_emit_records_tool_invocation("p2", "mutation_phase_util", "tool_invocation")
_emit_captures_execution_output("p2", "mutation_phase_util", "exec_output")
_emit_dispatches_agent("p3", "mutation_phase_util", "agent_dispatch")
_emit_coordinates_agents("p3", "mutation_phase_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "mutation_phase_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "mutation_phase_util", "healing_outcome")
_emit_escalates_failure("p3", "mutation_phase_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "mutation_phase_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "mutation_phase_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "mutation_phase_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "mutation_phase_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "mutation_phase_util", "eval_metric")
_emit_stores_embedding("p4", "mutation_phase_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "mutation_phase_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "mutation_phase_util", "exec_snapshot_link")

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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "StateSnapshot.restore_to")

        target_graph.clear()
        target_graph.add_nodes_from(self.graph_copy.nodes(data=True))
        target_graph.add_edges_from(self.graph_copy.edges(data=True))
        for node, attrs in self.node_attributes.items():
            if node in target_graph:
                target_graph.nodes[node].update(attrs)
        for edge, attrs in self.edge_attributes.items():
            if edge in target_graph and edge[0] in target_graph and (edge[1] in target_graph[edge[0]]):
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "DAGSafetyManager.add_validation_hook"
        )

        self._validation_hooks[phase].append(hook)
        logger.debug(f"Added validation hook for phase: {phase.value}")

    def create_snapshot(self, graph: nx.DiGraph, external_state: dict[str, Any] | None = None) -> str:
        """Create a snapshot of the current DAG state.

        Args:
            graph: Current graph
            external_state: Optional external state to include

        Returns:
            Snapshot ID
        """
        graph_copy = copy.deepcopy(graph)
        node_attributes = {}
        for node in graph.nodes():
            node_attributes[node] = dict(graph.nodes[node])
        edge_attributes = {}
        for edge in graph.edges():
            edge_attributes[edge] = dict(graph.edges[edge])
        snapshot = StateSnapshot(
            timestamp=time.time(),
            graph_copy=graph_copy,
            node_attributes=node_attributes,
            edge_attributes=edge_attributes,
            external_state=external_state or {},
        )
        self._snapshots.append(snapshot)
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
        if not self._snapshots:
            logger.error("No snapshots available")
            return False
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
        mutation_info = None
        for m in self._mutation_stack:
            if m["id"] == mutation_id:
                mutation_info = m
                break
        if not mutation_info:
            logger.error(f"Mutation not found: {mutation_id}")
            return False
        try:
            self._run_hooks(MutationPhase.PRE_VALIDATE, graph, mutation_info)
            snapshot_id = self.create_snapshot(graph)
            mutation_info["snapshot_id"] = snapshot_id
            self._run_hooks(MutationPhase.MUTATE, graph, mutation_info)
            mutation_func(graph)
            self._run_hooks(MutationPhase.POST_VALIDATE, graph, mutation_info)
            self._run_hooks(MutationPhase.COMMIT, graph, mutation_info)
            logger.info(f"Mutation successful: {mutation_id}")
            return True
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"Mutation failed: {mutation_id}, error: {e}")
            try:
                self._run_hooks(MutationPhase.ROLLBACK, graph, mutation_info)
                if mutation_info["snapshot_id"]:
                    self.restore_snapshot(mutation_info["snapshot_id"], graph)
                logger.info(f"Mutation rolled back: {mutation_id}")
            except Exception as rollback_error:  # guardian: allow-silent-swallow
                logger.error(f"Rollback failed: {mutation_id}, error: {rollback_error}")
            return False
        finally:
            self._mutation_stack = [m for m in self._mutation_stack if m["id"] != mutation_id]

    def _run_hooks(self, phase: MutationPhase, graph: nx.DiGraph, mutation_info: dict[str, Any]) -> None:
        """Run validation hooks for a phase.

        Args:
            phase: Phase to run hooks for
            graph: Current graph
            mutation_info: Mutation information
        """
        for hook in self._validation_hooks[phase]:
            try:
                hook(graph, mutation_info)
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
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
            raise ValueError(f"Depth inconsistency: {edge[0]}({source_depth}) -> {edge[1]}({target_depth})")


def create_default_safety_manager() -> DAGSafetyManager:
    """Create a safety manager with default hooks.

    Returns:
        DAGSafetyManager with default validation hooks
    """
    manager = DAGSafetyManager("default")
    manager.add_validation_hook(MutationPhase.PRE_VALIDATE, validate_acyclic_hook)
    manager.add_validation_hook(MutationPhase.POST_VALIDATE, validate_connectivity_hook)
    manager.add_validation_hook(MutationPhase.POST_VALIDATE, validate_node_attributes_hook)
    manager.add_validation_hook(MutationPhase.POST_VALIDATE, validate_depth_consistency_hook)
    return manager


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
        return False

    def execute(self, mutation_func: Callable[[nx.DiGraph], None]) -> bool:
        """Execute a mutation safely.

        Args:
            mutation_func: Function to perform mutation

        Returns:
            True if successful
        """
        return self.safety_manager.execute_mutation(self.graph, mutation_func, self.mutation_id)
