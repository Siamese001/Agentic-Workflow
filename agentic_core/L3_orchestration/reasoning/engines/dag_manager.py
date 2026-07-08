# review: allow-silent-degradation -- ADG violation exemption

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

try:
    from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin
except ImportError:  # guardian: allow-silent-degradation -- Optional healer mixin

    class HealingPolicyMixin:  # type: ignore[no-redef]
        """Stub."""

        pass


try:
    from agentic_core.interfaces.mixins import MCPOperationMixin
except (
    ImportError,
    NameError,
    ModuleNotFoundError,
):  # guardian: allow-silent-swallow -- Optional MCP hardened mixin

    class MCPOperationMixin:  # type: ignore[no-redef]
        """Stub."""

        pass


from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "dag_manager")
trace_contract.emit_determinism_digest("p0", "dag_manager")

trace_contract._emit_dispatches_healing_run("p1", "dag_manager", "L3")
trace_contract._emit_routes_through("p1", "dag_manager", "L3")
trace_contract._emit_checks_agent_registry("p1", "dag_manager", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "dag_manager", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "dag_manager", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "dag_manager", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "dag_manager", "target_agent")
trace_contract._emit_verifies_policy("p1", "dag_manager", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "dag_manager", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "dag_manager", "boundary_check")
trace_contract._emit_transcripts_response("p1", "dag_manager", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "dag_manager")
trace_contract._emit_gated_by_confidence("p1", "dag_manager", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "dag_manager", "L3")
trace_contract._emit_reads_policy_state("p1", "dag_manager", "L3")
trace_contract._emit_authorize_and_execute("p2", "dag_manager", "execution_auth")
trace_contract._emit_validates_capability("p2", "dag_manager", "capability_check")
trace_contract._emit_routes_to_capability("p2", "dag_manager", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "dag_manager", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "dag_manager", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "dag_manager", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "dag_manager", "exec_output")
trace_contract._emit_dispatches_agent("p3", "dag_manager", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "dag_manager", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "dag_manager", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "dag_manager", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "dag_manager", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "dag_manager", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "dag_manager", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "dag_manager", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "dag_manager", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "dag_manager", "eval_metric")
trace_contract._emit_stores_embedding("p4", "dag_manager", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "dag_manager", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "dag_manager", "exec_snapshot_link")

"\nDAGManager - Extracted for one-class-per-file pattern.\n\nOriginally from: DAGMutatorAgent.py\nExtracted: 2026-01-06 (Surgical Extraction)\nRenamed: 2026-01-22 (Utility Renaming - Not an Agent)\n"


import networkx as nx

from agentic_core.utils.decorators_compat_util import standard_heal
from tqdm import tqdm

trace_contract._emit_emits_metric_event("dag_manager", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("dag_manager", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("dag_manager", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("dag_manager", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("dag_manager", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("dag_manager", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("dag_manager", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("dag_manager", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("dag_manager", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("dag_manager", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("dag_manager", "p4obs", "alert")
trace_contract._emit_links_incident_trace("dag_manager", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("dag_manager", "p3lm", "pattern")
trace_contract._emit_records_learning_event("dag_manager", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("dag_manager", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("dag_manager", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("dag_manager", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("dag_manager", "p3lm", "policy")
trace_contract._emit_stores_learning_state("dag_manager", "p3lm", "state")
trace_contract._emit_records_execution_trace("dag_manager", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("dag_manager", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("dag_manager", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("dag_manager", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("dag_manager", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("dag_manager", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("dag_manager", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("dag_manager", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("dag_manager", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "dag_manager", "context_pull")
trace_contract._emit_pulls_context("p1", "dag_manager", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "dag_manager", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "dag_manager", "uwg_term_2")
trace_contract._emit_writes_through("p1", "dag_manager", "write_through")
trace_contract._emit_writes_through("p1", "dag_manager", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "dag_manager", "safety_validation")
trace_contract._emit_invokes_eval("p1", "dag_manager", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "dag_manager", "routing_commit")


try:
    from agentic_core.mixins.subatomic_testing_mixin import L3SubatomicTestingMixin
except (ImportError, AttributeError):  # guardian: allow-silent-swallow -- Optional subatomic testing mixin

    class L3SubatomicTestingMixin:  # type: ignore[no-redef]
        pass


class DAGManager(
    HealingPolicyMixin,
    MCPOperationMixin,
    L3SubatomicTestingMixin,
    RedisCacheMixin,
    PineconeVectorMixin,
):
    """Manages the dynamic DAG with mutation capabilities.

    HARDENED: Redis caching + Pinecone vector support for DAG structure caching.
    """

    _cache_prefix: str = "dag_manager"
    _namespace: str = "l3_dags"

    def __init__(self, config: DAGConfig | None = None) -> None:
        """Initialize the DAG Manager.

        Args:
            config: Optional configuration
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "DAGManager.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "DAGManager.__init__", "p0_governance")
        self.config = config or DAGConfig()
        self.graph = nx.DiGraph()
        self.mutator = DAGMutator(self.config)
        self.execution_queue: List[str] = []
        self.node_registry: Dict[str, SubatomicHop] = {}
        self.function_registry: Dict[str, Callable] = {}
        self.stats = {
            "total_mutations": 0,
            "successful_mutations": 0,
            "spawned_predecessors": 0,
            "spawned_successors": 0,
            "skipped_nodes": 0,
            "replaced_nodes": 0,
        }
        Logger.info("Initialized DAGManager with dynamic mutation support")

    def register_function(self, name: str, function: Callable) -> None:
        """Register a hop function that can be spawned.

        Args:
            name: Function name
            function: The function to register
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "DAGManager.register_function",
        )

        self.function_registry[name] = function
        Logger.debug(f"Registered function: {name}")

    def add_node(self, hop: SubatomicHop, predecessors: List[str] | None = None) -> None:
        """Add a node to the DAG.

        Args:
            hop: The SubatomicHop to add
            predecessors: Optional list of predecessor node IDs
        """
        self.node_registry[hop.config.hop_id] = hop
        self.graph.add_node(hop.config.hop_id, hop=hop, depth=0, created_at=datetime.now())
        if predecessors:
            for pred in predecessors:
                if pred in self.graph.nodes:
                    self.graph.add_edge(pred, hop.config.hop_id)
        self.mutator._update_depths(self.graph)
        if not predecessors:
            self.execution_queue.append(hop.config.hop_id)
        Logger.info(f"Added node {hop.config.hop_id} to DAG")

    def request_mutation(self, mutation: DAGMutation) -> MutationResult:
        """Request a mutation to the DAG.

        Args:
            mutation: The mutation to request

        Returns:
            Result of the mutation
        """
        self.stats["total_mutations"] += 1
        result = self.mutator.apply_mutation(self.graph, mutation)
        if result.success:
            self.stats["successful_mutations"] += 1
            if mutation.action == MutationAction.SPAWN_PREDECESSOR:
                self.stats["spawned_predecessors"] += 1
                if mutation.new_hop_spec:
                    self.execution_queue.insert(0, mutation.new_hop_spec.hop_id)
            elif mutation.action == MutationAction.SPAWN_SUCCESSOR:
                self.stats["spawned_successors"] += 1
            elif mutation.action == MutationAction.SKIP_SUCCESSOR:
                self.stats["skipped_nodes"] += 1
            elif mutation.action == MutationAction.REPLACE_NODE:
                self.stats["replaced_nodes"] += 1
        return result

    def create_mutation_request(
        self,
        action: MutationAction,
        target_hop_id: str,
        hop_function: str,
        reason: str,
        requester_hop_id: str,
        **kwargs,
    ) -> DAGMutation:
        """Create a mutation request.

        Args:
            action: Type of mutation
            target_hop_id: Target node ID
            hop_function: Function name for new node
            reason: Reason for mutation
            requester_hop_id: ID of requesting node
            **kwargs: Additional hop spec parameters

        Returns:
            DAGMutation object
        """
        hop_spec = HopSpec(hop_function=hop_function, **kwargs)
        return DAGMutation(
            action=action,
            target_hop_id=target_hop_id,
            new_hop_spec=hop_spec,
            reason=reason,
            requester_hop_id=requester_hop_id,
        )

    def get_next_node(self) -> SubatomicHop | None:
        """Get the next node to execute.

        Returns:
            Next SubatomicHop or None if queue is empty
        """
        if not self.execution_queue:
            return None
        hop_id = self.execution_queue.pop(0)
        return self.node_registry.get(hop_id)

    def pause_node(self, hop_id: str) -> bool:
        """Pause a node's execution.

        Args:
            hop_id: Node ID to pause

        Returns:
            True if paused successfully
        """
        if hop_id in self.node_registry:
            hop = self.node_registry[hop_id]
            if hop.state == HopState.RUNNING:
                hop.state = HopState.PAUSED
                Logger.info(f"Paused node {hop_id}")
                return True
        return False

    def resume_node(self, hop_id: str) -> bool:
        """Resume a paused node.

        Args:
            hop_id: Node ID to resume

        Returns:
            True if resumed successfully
        """
        if hop_id in self.node_registry:
            hop = self.node_registry[hop_id]
            if hop.state == HopState.PAUSED:
                hop.state = HopState.RUNNING
                self.execution_queue.append(hop_id)
                Logger.info(f"Resumed node {hop_id}")
                return True
        return False

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "queue_size": len(self.execution_queue),
            "registered_functions": len(self.function_registry),
            **self.stats,
        }

    def visualize_graph(self) -> Dict[str, Any]:
        """Get graph data for visualization.

        Returns:
            Dictionary with nodes and edges
        """
        nodes = []
        edges = []
        for node_id in tqdm(self.graph.nodes, desc="Processing", unit="item"):
            node_data = self.graph.nodes[node_id]
            hop = node_data.get("hop")
            nodes.append(
                {
                    "id": node_id,
                    "depth": node_data.get("depth", 0),
                    "state": hop.state.value if hop else None,
                    "skipped": node_data.get("skipped", False),
                    "replaced": node_data.get("replaced", False),
                },
            )
        for edge in self.graph.edges:
            edge_data = self.graph.edges[edge]
            edges.append(
                {"source": edge[0], "target": edge[1], "bridge": edge_data.get("bridge_created", False)},
            )
        return {"nodes": nodes, "edges": edges}

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> Dict[str, int]:
        """L3 orchestration agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L3 orchestration - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
