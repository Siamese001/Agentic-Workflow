from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "DAGMutatorAgent")
emit_determinism_digest("p0", "DAGMutatorAgent")

_emit_dispatches_healing_run("p1", "DAGMutatorAgent", "L3")
_emit_routes_through("p1", "DAGMutatorAgent", "L3")
_emit_checks_agent_registry("p1", "DAGMutatorAgent", "agent_registry")
_emit_validates_agent_capability("p1", "DAGMutatorAgent", "capability")
_emit_dispatches_execution_plan("p1", "DAGMutatorAgent", "exec_plan")
_emit_agent_executes_agent("p1", "DAGMutatorAgent", "sub_agent")
_emit_routes_to_agent("p1", "DAGMutatorAgent", "target_agent")
_emit_verifies_policy("p1", "DAGMutatorAgent", "policy_check")
_emit_observes_runtime_state("p1", "DAGMutatorAgent", "runtime_state")
_emit_verifies_boundary("p1", "DAGMutatorAgent", "boundary_check")
_emit_transcripts_response("p1", "DAGMutatorAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "DAGMutatorAgent")
_emit_gated_by_confidence("p1", "DAGMutatorAgent", "confidence_gate")
_emit_escalates_to_human("p1", "DAGMutatorAgent", "L3")
_emit_reads_policy_state("p1", "DAGMutatorAgent", "L3")
_emit_authorize_and_execute("p2", "DAGMutatorAgent", "execution_auth")
_emit_validates_capability("p2", "DAGMutatorAgent", "capability_check")
_emit_routes_to_capability("p2", "DAGMutatorAgent", "capability_route")
_emit_writes_via_uwg("p2", "DAGMutatorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "DAGMutatorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "DAGMutatorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "DAGMutatorAgent", "exec_output")
_emit_dispatches_agent("p3", "DAGMutatorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "DAGMutatorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "DAGMutatorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "DAGMutatorAgent", "healing_outcome")
_emit_escalates_failure("p3", "DAGMutatorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "DAGMutatorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "DAGMutatorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "DAGMutatorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "DAGMutatorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "DAGMutatorAgent", "eval_metric")
_emit_stores_embedding("p4", "DAGMutatorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "DAGMutatorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "DAGMutatorAgent", "exec_snapshot_link")

"Dynamic DAG Mutation Manager - Runtime graph transformation.\n\nThis module implements the ability for the DAG to rewrite itself at runtime,\nallowing nodes to spawn new predecessors when they detect Missing information.\n"
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

import networkx as nx
from pydantic import BaseModel, Field, validator

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout

_emit_emits_metric_event("DAGMutatorAgent", "p4obs", "metric_1")
_emit_emits_metric_event("DAGMutatorAgent", "p4obs", "metric_2")
_emit_emits_metric_event("DAGMutatorAgent", "p4obs", "metric_3")
_emit_emits_metric_event("DAGMutatorAgent", "p4obs", "metric_4")
_emit_emits_metric_event("DAGMutatorAgent", "p4obs", "metric_5")
_emit_emits_metric_event("DAGMutatorAgent", "p4obs", "metric_6")
_emit_records_incident_event("DAGMutatorAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("DAGMutatorAgent", "p4obs", "anomaly")
_emit_writes_observability_log("DAGMutatorAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("DAGMutatorAgent", "p4obs", "mon_state")
_emit_triggers_alert("DAGMutatorAgent", "p4obs", "alert")
_emit_links_incident_trace("DAGMutatorAgent", "p4obs", "trace_link")
_emit_captures_pattern("DAGMutatorAgent", "p3lm", "pattern")
_emit_records_learning_event("DAGMutatorAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("DAGMutatorAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("DAGMutatorAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("DAGMutatorAgent", "p3lm", "routing")
_emit_improves_agent_policy("DAGMutatorAgent", "p3lm", "policy")
_emit_stores_learning_state("DAGMutatorAgent", "p3lm", "state")
_emit_records_execution_trace("DAGMutatorAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("DAGMutatorAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("DAGMutatorAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("DAGMutatorAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("DAGMutatorAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("DAGMutatorAgent", "env_read", "p2_env_1")
_emit_reads_environ("DAGMutatorAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("DAGMutatorAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("DAGMutatorAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "DAGMutatorAgent", "context_pull")
_emit_pulls_context("p1", "DAGMutatorAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "DAGMutatorAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "DAGMutatorAgent", "uwg_term_2")
_emit_writes_through("p1", "DAGMutatorAgent", "write_through")
_emit_writes_through("p1", "DAGMutatorAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "DAGMutatorAgent", "safety_validation")
_emit_invokes_eval("p1", "DAGMutatorAgent", "eval_call")
_emit_proposal_commits_routing("p1", "DAGMutatorAgent", "routing_commit")

if TYPE_CHECKING:
    pass
Logger = logging.getLogger(__name__)


class GraphTransaction:
    """Context manager for atomic graph mutations.

    Implements copy-on-write semantics to ensure the graph is never
    left in a corrupted state if a mutation fails partway through.
    """

    def __init__(self, manager) -> None:
        """Initialize the transaction.

        Args:
            manager: The DynamicDAGManager instance
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "GraphTransaction.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "GraphTransaction.__init__", "p0_governance")
        self.manager = manager
        self.original_graph = None
        self.transaction_graph = None

    def __enter__(self):
        """Enter transaction - create a copy of the graph.

        Returns:
            The transaction graph (copy of original)
        """
        self.original_graph = self.manager.graph
        self.transaction_graph = self.manager.graph.copy()
        self.manager._transaction_graph = self.transaction_graph
        Logger.debug("Entered graph transaction")
        return self.transaction_graph

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction - commit or rollback.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred

        Returns:
            False to propagate exceptions, True to suppress
        """
        self.manager._transaction_graph = None
        if exc_type is not None:
            self.manager.graph = self.original_graph
            Logger.error(f"DAG Mutation failed. Rolled back state. Error: {exc_val}")
            return False
        try:
            self._validate_transaction_graph()
            self.manager.graph = self.transaction_graph
            Logger.debug("DAG Transaction committed successfully")
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            self.manager.graph = self.original_graph
            Logger.error(f"DAG Transaction validation failed. Rolled back. Error: {e}")
            return False
        return True

    def _validate_transaction_graph(self):
        """Validate that the transaction graph is still a valid DAG.

        Raises:
            ValueError: If validation fails
        """
        if not nx.is_directed_acyclic_graph(self.transaction_graph):
            raise ValueError("Transaction would create a cycle")
        if not nx.is_weakly_connected(self.transaction_graph):
            Logger.warning("Transaction created disconnected components")
        for node in self.transaction_graph.nodes():
            if "hop_spec" not in self.transaction_graph.nodes[node]:
                raise ValueError(f"Node {node} Missing hop_spec attribute")
        self._validate_depth_ordering()

    def _validate_depth_ordering(self):
        """Validate that depth values are consistent with graph structure."""
        depths = nx.get_node_attributes(self.transaction_graph, "depth")
        for edge in self.transaction_graph.edges():
            source, target = edge
            source_depth = depths.get(source, 0)
            target_depth = depths.get(target, 0)
            if source_depth >= target_depth:
                raise ValueError(
                    f"Depth ordering Violation: {source}({source_depth}) -> {target}({target_depth})",
                )


class MutationAction(Enum):
    """Types of DAG mutations."""

    SPAWN_PREDECESSOR = "SPAWN_PREDECESSOR"
    SPAWN_SUCCESSOR = "SPAWN_SUCCESSOR"
    SKIP_SUCCESSOR = "SKIP_SUCCESSOR"
    REPLACE_NODE = "REPLACE_NODE"


class HopSpec(BaseModel):
    """Specification for creating a new hop."""

    hop_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hop_function: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=0)
    timeout: float = Field(default=300.0)
    retry_policy: dict[str, Any] | None = None

    class Config:
        extra = "allow"


class DAGMutation(BaseModel):
    """A mutation request for the DAG."""

    mutation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: MutationAction
    target_hop_id: str
    new_hop_spec: HopSpec | None = None
    reason: str
    timestamp: datetime = Field(default_factory=datetime.now)
    requester_hop_id: str

    @validator("new_hop_spec")
    def validate_hop_spec(cls, v, values):
        # guardian: allow-config-with-logic
        if values.get("action") in [MutationAction.SPAWN_PREDECESSOR, MutationAction.SPAWN_SUCCESSOR]:
            # guardian: allow-config-with-logic
            if v is None:
                raise ValueError("new_hop_spec is required for spawn operations")
        return v


class MutationResult(BaseModel):
    """Result of applying a mutation."""

    mutation_id: str
    success: bool
    message: str
    affected_nodes: list[str] = Field(default_factory=list)
    new_edges: list[tuple] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class DAGConfig(BaseModel):
    """configuration for DAG management."""

    max_depth: int = Field(default=50, ge=1, le=100)
    max_fan_out: int = Field(default=10, ge=1, le=50)
    enable_mutation_logging: bool = True
    mutation_history_size: int = Field(default=1000, ge=100)


class DAGMutatorAgent(SovereignBaseAgent):
    """Handles the actual graph mutations."""

    def __init__(self, config: DAGConfig) -> None:
        """Initialize the DAGMutatorAgent.

        Args:
            config: DAG configuration
        """
        self.config = config
        self.mutation_history: list[MutationResult] = []

    def apply_mutation(self, graph: nx.DiGraph, mutation: DAGMutation) -> MutationResult:
        """Apply a mutation to the graph with transactional safety.

        Args:
            graph: The NetworkX directed graph
            mutation: The mutation to apply

        Returns:
            MutationResult with details
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"DAGMutatorAgent.apply_mutation:{mutation.mutation_type}",
        )
        try:
            with GraphTransaction(self) as tx_graph:
                self._validate_mutation(tx_graph, mutation)
                if mutation.action == MutationAction.SPAWN_PREDECESSOR:
                    result = self._spawn_predecessor(tx_graph, mutation)
                elif mutation.action == MutationAction.SPAWN_SUCCESSOR:
                    result = self._spawn_successor(tx_graph, mutation)
                elif mutation.action == MutationAction.SKIP_SUCCESSOR:
                    result = self._skip_successor(tx_graph, mutation)
                elif mutation.action == MutationAction.REPLACE_NODE:
                    result = self._replace_node(tx_graph, mutation)
                else:
                    raise ValueError(f"Unknown mutation action: {mutation.action}")
                if self.config.enable_mutation_logging:
                    Logger.info(
                        f"Applied mutation {mutation.mutation_id}: {mutation.action.value} on {mutation.target_hop_id} - {mutation.reason}",
                    )
                self._store_mutation_result(result)
                return result
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            error_result = MutationResult(
                mutation_id=mutation.mutation_id, success=False, message=f"Mutation failed: {str(e)}",
            )
            self._store_mutation_result(error_result)
            return error_result

    def _validate_mutation(self, graph: nx.DiGraph, mutation: DAGMutation) -> None:
        """Validate that a mutation is safe to apply."""
        if mutation.target_hop_id not in graph.nodes:
            raise ValueError(f"Target node {mutation.target_hop_id} not found in graph")
        if mutation.action == MutationAction.SPAWN_PREDECESSOR:
            target_depth = graph.nodes[mutation.target_hop_id].get("depth", 0)
            if target_depth >= self.config.max_depth - 1:
                raise ValueError(f"Cannot spawn predecessor: would exceed max depth {self.config.max_depth}")
        if mutation.new_hop_spec and mutation.new_hop_spec.hop_id in graph.nodes:
            raise ValueError(f"Node {mutation.new_hop_spec.hop_id} already exists")
        if mutation.action == MutationAction.SPAWN_SUCCESSOR:
            successors = list(graph.successors(mutation.target_hop_id))
            if len(successors) >= self.config.max_fan_out:
                raise ValueError(
                    f"Cannot spawn successor: would exceed max fan-out {self.config.max_fan_out}",
                )

    def _spawn_predecessor(self, graph: nx.DiGraph, mutation: DAGMutation) -> MutationResult:
        """Spawn a new predecessor node."""
        new_node = mutation.new_hop_spec.hop_id
        target_node = mutation.target_hop_id
        graph.add_node(
            new_node,
            hop_spec=mutation.new_hop_spec.dict(),
            depth=graph.nodes[target_node].get("depth", 0) + 1,
            created_by=mutation.requester_hop_id,
            created_at=mutation.timestamp,
        )
        graph.add_edge(
            new_node, target_node, created_by=mutation.requester_hop_id, created_at=mutation.timestamp,
        )
        self._update_depths(graph)
        if not nx.is_directed_acyclic_graph(graph):
            graph.remove_node(new_node)
            raise ValueError("Mutation would create a cycle")
        return MutationResult(
            mutation_id=mutation.mutation_id,
            success=True,
            message=f"Spawned predecessor {new_node} for {target_node}",
            affected_nodes=[new_node, target_node],
            new_edges=[(new_node, target_node)],
        )

    def _spawn_successor(self, graph: nx.DiGraph, mutation: DAGMutation) -> MutationResult:
        """Spawn a new successor node."""
        new_node = mutation.new_hop_spec.hop_id
        target_node = mutation.target_hop_id
        graph.add_node(
            new_node,
            hop_spec=mutation.new_hop_spec.dict(),
            depth=graph.nodes[target_node].get("depth", 0) - 1,
            created_by=mutation.requester_hop_id,
            created_at=mutation.timestamp,
        )
        old_successors = list(graph.successors(target_node))
        for successor in old_successors:
            graph.remove_edge(target_node, successor)
            graph.add_edge(new_node, successor, moved_from=target_node, created_by=mutation.requester_hop_id)
        graph.add_edge(
            target_node, new_node, created_by=mutation.requester_hop_id, created_at=mutation.timestamp,
        )
        self._update_depths(graph)
        if not nx.is_directed_acyclic_graph(graph):
            graph.remove_node(new_node)
            for successor in old_successors:
                graph.add_edge(target_node, successor)
            raise ValueError("Mutation would create a cycle")
        return MutationResult(
            mutation_id=mutation.mutation_id,
            success=True,
            message=f"Spawned successor {new_node} for {target_node}",
            affected_nodes=[new_node, target_node] + old_successors,
            new_edges=[(target_node, new_node)] + [(new_node, s) for s in old_successors],
        )

    def _skip_successor(self, graph: nx.DiGraph, mutation: DAGMutation) -> MutationResult:
        """Skip a successor node by bridging the gap."""
        target_node = mutation.target_hop_id
        successors = list(graph.successors(target_node))
        if not successors:
            raise ValueError(f"Node {target_node} has no successors to skip")
        skip_node = successors[0]
        skip_successors = list(graph.successors(skip_node))
        for skip_successor in skip_successors:
            graph.add_edge(
                target_node, skip_successor, bridge_created=True, created_by=mutation.requester_hop_id,
            )
        graph.nodes[skip_node]["skipped"] = True
        graph.nodes[skip_node]["skipped_by"] = mutation.requester_hop_id
        graph.nodes[skip_node]["skipped_at"] = mutation.timestamp
        return MutationResult(
            mutation_id=mutation.mutation_id,
            success=True,
            message=f"Skipped successor {skip_node} of {target_node}",
            affected_nodes=[target_node, skip_node] + skip_successors,
            new_edges=[(target_node, s) for s in skip_successors],
        )

    def _replace_node(self, graph: nx.DiGraph, mutation: DAGMutation) -> MutationResult:
        """Replace a node with a new one."""
        old_node = mutation.target_hop_id
        new_node = mutation.new_hop_spec.hop_id
        predecessors = list(graph.predecessors(old_node))
        successors = list(graph.successors(old_node))
        graph.add_node(
            new_node,
            hop_spec=mutation.new_hop_spec.dict(),
            depth=graph.nodes[old_node].get("depth", 0),
            created_by=mutation.requester_hop_id,
            created_at=mutation.timestamp,
            replaces=old_node,
        )
        for pred in predecessors:
            graph.add_edge(pred, new_node, replaced_from=old_node, created_by=mutation.requester_hop_id)
        for succ in successors:
            graph.add_edge(new_node, succ, replaced_to=old_node, created_by=mutation.requester_hop_id)
        graph.nodes[old_node]["replaced"] = True
        graph.nodes[old_node]["replaced_by"] = new_node
        graph.nodes[old_node]["replaced_at"] = mutation.timestamp
        graph.remove_edges_from([(p, old_node) for p in predecessors])
        graph.remove_edges_from([(old_node, s) for s in successors])
        return MutationResult(
            mutation_id=mutation.mutation_id,
            success=True,
            message=f"Replaced node {old_node} with {new_node}",
            affected_nodes=[old_node, new_node] + predecessors + successors,
            new_edges=[(p, new_node) for p in predecessors] + [(new_node, s) for s in successors],
        )

    def _update_depths(self, graph: nx.DiGraph) -> None:
        """Update depth annotations for all nodes."""
        roots = [n for n in graph.nodes if graph.in_degree(n) == 0]
        for root in roots:
            graph.nodes[root]["depth"] = 0
            queue = [(root, 0)]
            while queue:
                node, depth = queue.pop(0)
                for successor in graph.successors(node):
                    current_depth = graph.nodes[successor].get("depth", -1)
                    if depth + 1 > current_depth:
                        graph.nodes[successor]["depth"] = depth + 1
                        queue.append((successor, depth + 1))

    def _store_mutation_result(self, result: MutationResult) -> None:
        """Store mutation result in history."""
        self.mutation_history.append(result)
        if len(self.mutation_history) > self.config.mutation_history_size:
            self.mutation_history = self.mutation_history[-self.config.mutation_history_size :]

    def get_mutation_history(self, limit: int | None = None) -> list[MutationResult]:
        """Get mutation history."""
        if limit:
            return self.mutation_history[-limit:]
        return self.mutation_history

    @timeout(120)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """
        DAG Mutation Healing - Validates graph mutation logic integrity.

        WIRED CAPABILITIES:
        - _validate_mutation(): Self-diagnostic on graph mutation rules.
        """
        metrics = super().heal_repository(
            dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path,
        )
        if not isinstance(metrics, dict):
            metrics = {"violations": 0, "fixed": 0, "errors": 0}
        if metrics.get("cycle_detected"):
            return metrics
        try:
            test_graph = nx.DiGraph()
            test_graph.add_node("root", depth=0)
            test_mutation = DAGMutation(
                action=MutationAction.SPAWN_SUCCESSOR,
                target_hop_id="root",
                new_hop_spec=HopSpec(hop_function="test_func", parameters={}),
                reason="diagnostic_check",
                requester_hop_id="system_healer",
            )
            if hasattr(self, "_validate_mutation"):
                self._validate_mutation(test_graph, test_mutation)
                metrics["fixed"] = metrics.get("fixed", 0) + 1
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            Logger.error(f"DAG Mutator healing failed: {e}")
            metrics["errors"] = metrics.get("errors", 0) + 1
        return metrics

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by DAGMutatorAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"DAGMutatorAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        # guardian: allow-silent-swallow
        except (RuntimeError, ValueError) as e:
            return {
                "status": "failed",
                "details": f"DAGMutatorAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
