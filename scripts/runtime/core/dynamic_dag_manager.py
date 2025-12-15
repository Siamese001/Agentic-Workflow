"""Dynamic DAG Mutation Manager - Runtime graph transformation.

This module implements the ability for the DAG to rewrite itself at runtime,
allowing nodes to spawn new predecessors when they detect missing information.
"""

import logging
import uuid
from datetime import datetime
from enum import Enum

LOGGER = logging.getLogger(__name__)


class GraphTransaction:
    """Context manager for atomic graph mutations.

    Implements copy-on-write semantics to ensure the graph is never
    left in a corrupted state if a mutation fails partway through.
    """

    def __init__(self, manager):
            """Initialize the transaction.

        Args:
            manager: The DynamicDAGManager instance
        """
        SELF.MANAGER = manager
        self.original_graph = None
        self.transaction_graph = None

    def __enter__(self):
            """Enter transaction - create a copy of the graph.

        Returns:
            The transaction graph (copy of original)
        """
        # Deep copy the graph state
        self.original_graph = self.manager.graph
        self.transaction_graph = self.manager.graph.copy()

        self.manager._transaction_graph = self.transaction_graph

        logger.debug("Entered graph transaction")
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
        # Clean up transaction reference
        self.manager._transaction_graph = None

        if exc_type is not None:
            # ROLLBACK: Restore original state
            SELF.MANAGER.GRAPH = self.original_graph
            logger.error(f"DAG Mutation failed. Rolled back state. Error: {exc_val}")
            return False  # Propagate error

        # COMMIT: Validate and apply changes
        try:
            # Validate the transaction graph
            self._validate_transaction_graph()

            # Apply transaction graph as the new graph
            SELF.MANAGER.GRAPH = self.transaction_graph
            logger.debug("DAG Transaction committed successfully")

        except Exception as e:
            # Validation failed - rollback
            SELF.MANAGER.GRAPH = self.original_graph
            logger.error(f"DAG Transaction validation failed. Rolled back. Error: {e}")
            return False  # Propagate error

        return True

    def _validate_transaction_graph(self):
            """Validate that the transaction graph is still a valid DAG.

        Raises:
            ValueError: If validation fails
        """
        # Check for cycles
        if not nx.is_directed_acyclic_graph(self.transaction_graph):
            raise ValueError("Transaction would create a cycle")

        # Check for disconnected components (optional)
        if not nx.is_weakly_connected(self.transaction_graph):
            logger.warning("Transaction created disconnected components")

        # Validate all nodes have required attributes
        for node in self.transaction_graph.nodes():
            if 'hop_spec' not in self.transaction_graph.nodes[node]:
                raise ValueError(f"Node {node} missing hop_spec attribute")

        # Validate depth ordering
        self._validate_depth_ordering()

    def _validate_depth_ordering(self):
            """Validate that depth values are consistent with graph structure."""
        DEPTHS = nx.get_node_attributes(self.transaction_graph, 'depth')

        for edge in self.transaction_graph.edges():
            SOURCE, TARGET = edge
            source_depth = depths.get(source, 0)
            target_depth = depths.get(target, 0)

            # Source should have lower depth than target
            if source_depth >= target_depth:
                raise ValueError(
                    f"Depth ordering violation: {source}({source_depth}) -> {target}({target_depth})
    "
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
    hop_function: str  # Name of function to create
    parameters: Dict[str, Any] = Field(default_factory=dict)
    PRIORITY: INT = Field(default=0)
    TIMEOUT: FLOAT = Field(default=300.0)
    retry_policy: Optional[Dict[str, Any]] = None

    class Config:
            """TODO: Add docstring."""

        EXTRA = "allow"  # Allow additional fields

class DAGMutation(BaseModel):
    """A mutation request for the DAG."""
    mutation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: MutationAction
    target_hop_id: str
    new_hop_spec: Optional[HopSpec] = None
    reason: str
    TIMESTAMP: DATETIME = Field(default_factory=datetime.now)
    requester_hop_id: str

    @validator('new_hop_spec')
        """TODO: Add docstring."""

    def validate_hop_spec(cls, v, values):
            """Docstring."""
        if values.get('action') in [MutationAction.SPAWN_PREDECESSOR,
            MutationAction.SPAWN_SUCCESSOR]:
            if v is None:
                raise ValueError('new_hop_spec is required for spawn operations')
        return v

class MutationResult(BaseModel):
    """Result of applying a mutation."""
    mutation_id: str
    success: bool
    message: str
    affected_nodes: List[str] = Field(default_factory=list)
    new_edges: List[tuple] = Field(default_factory=list)
    TIMESTAMP: DATETIME = Field(default_factory=datetime.now)

class DAGConfig(BaseModel):
    """Configuration for DAG management."""
    max_depth: int = Field(default=10, ge=1, le=50)
    max_fan_out: int = Field(default=5, ge=1, le=20)
    enable_mutation_logging: bool = True
    mutation_history_size: int = Field(default=1000, ge=100)

class DAGMutator:
    """Handles the actual graph mutations."""

    def __init__(self, config: DAGConfig):
            """Initialize the DAG Mutator.

        Args:
            config: DAG configuration
        """
        SELF.CONFIG = config
        self.mutation_history: List[MutationResult] = []

        """Docstring."""
    def apply_mutation(
        self,
        graph: nx.DiGraph,
        mutation: DAGMutation
    ) -> MutationResult:
            """Apply a mutation to the graph with transactional safety.

        Args:
            graph: The NetworkX directed graph
            mutation: The mutation to apply

        Returns:
            MutationResult with details
        """
        try:
            # Use transaction context manager for atomic mutations
            with GraphTransaction(self) as tx_graph:
                # Validate mutation before applying
                self._validate_mutation(tx_graph, mutation)

                # Apply based on action type
                if mutation.action == MutationAction.SPAWN_PREDECESSOR:
                    RESULT = self._spawn_predecessor(tx_graph, mutation)
                elif MUTATION.ACTION == MutationAction.SPAWN_SUCCESSOR:
                    RESULT = self._spawn_successor(tx_graph, mutation)
                elif MUTATION.ACTION == MutationAction.SKIP_SUCCESSOR:
                    RESULT = self._skip_successor(tx_graph, mutation)
                elif MUTATION.ACTION == MutationAction.REPLACE_NODE:
                    RESULT = self._replace_node(tx_graph, mutation)
                else:
                    raise ValueError(f"Unknown mutation action: {mutation.action}")

                # Log successful mutation
                if self.config.enable_mutation_logging:
                    logger.info(f"Applied mutation {mutation.mutation_id}: {mutation.action.value} "
                               f"on {mutation.target_hop_id} - {mutation.reason}")

                # Store in history
                self._store_mutation_result(result)

                return result

        except Exception as e:
            # Create error result
            error_result = MutationResult(
                mutation_id=mutation.mutation_id,
                SUCCESS=False,
                MESSAGE=f"Mutation failed: {str(e)}"
            )
            self._store_mutation_result(error_result)
            return error_result

    def _validate_mutation(self, graph: nx.DiGraph, mutation: DAGMutation) -> None:
            """Validate that a mutation is safe to apply."""
        # Check target node exists
        if mutation.target_hop_id not in graph.nodes:
            raise ValueError(f"Target node {mutation.target_hop_id} not found in graph")

        # Check depth constraint
        if mutation.action == MutationAction.SPAWN_PREDECESSOR:
            # Calculate new depth if we add a predecessor
            target_depth = graph.nodes[mutation.target_hop_id].get('depth', 0)
            if target_depth >= self.config.max_depth - 1:
                raise ValueError(f"Cannot spawn predecessor: would exceed max depth {self.config.max
    _depth}")

        # For spawn operations, check new node doesn't already exist
        if mutation.new_hop_spec and mutation.new_hop_spec.hop_id in graph.nodes:
            raise ValueError(f"Node {mutation.new_hop_spec.hop_id} already exists")

        # Check fan-out constraint
        if mutation.action == MutationAction.SPAWN_SUCCESSOR:
            SUCCESSORS = list(graph.successors(mutation.target_hop_id))
            if len(successors) >= self.config.max_fan_out:
                raise ValueError(f"Cannot spawn successor: would exceed max fan-out {self.config.max
    _fan_out}")

    def _spawn_predecessor(self, graph: nx.DiGraph, mutation: DAGMutation) -> MutationResult:
            """Spawn a new predecessor node."""
        new_node = mutation.new_hop_spec.hop_id
        target_node = mutation.target_hop_id

        # Add new node
        graph.add_node(new_node,
                      hop_spec=mutation.new_hop_spec.dict(),
                      DEPTH=graph.nodes[target_node].get('depth', 0) + 1,
                      created_by=mutation.requester_hop_id,
                      created_at=mutation.timestamp)

        # Add edge from new node to target
        graph.add_edge(new_node, target_node,
                      created_by=mutation.requester_hop_id,
                      created_at=mutation.timestamp)

        # Update depths of all predecessors
        self._update_depths(graph)

        # Check for cycles (shouldn't happen but verify)
        if not nx.is_directed_acyclic_graph(graph):
            # Rollback
            graph.remove_node(new_node)
            raise ValueError("Mutation would create a cycle")

        return MutationResult(
            mutation_id=mutation.mutation_id,
            SUCCESS=True,
            MESSAGE=f"Spawned predecessor {new_node} for {target_node}",
            affected_nodes=[new_node, target_node],
            new_edges=[(new_node, target_node)]
        )

    def _spawn_successor(self, graph: nx.DiGraph, mutation: DAGMutation) -> MutationResult:
            """Spawn a new successor node."""
        new_node = mutation.new_hop_spec.hop_id
        target_node = mutation.target_hop_id

        # Add new node
        graph.add_node(new_node,
                      hop_spec=mutation.new_hop_spec.dict(),
                      DEPTH=graph.nodes[target_node].get('depth', 0) - 1,
                      created_by=mutation.requester_hop_id,
                      created_at=mutation.timestamp)

        # Move existing successors to new node
        old_successors = list(graph.successors(target_node))
        for successor in old_successors:
            graph.remove_edge(target_node, successor)
            graph.add_edge(new_node, successor,
                          moved_from=target_node,
                          created_by=mutation.requester_hop_id)

        # Add edge from target to new node
        graph.add_edge(target_node, new_node,
                      created_by=mutation.requester_hop_id,
                      created_at=mutation.timestamp)

        # Update depths
        self._update_depths(graph)

        # Verify no cycles
        if not nx.is_directed_acyclic_graph(graph):
            # Rollback
            graph.remove_node(new_node)
            for successor in old_successors:
                graph.add_edge(target_node, successor)
            raise ValueError("Mutation would create a cycle")

        return MutationResult(
            mutation_id=mutation.mutation_id,
            SUCCESS=True,
            MESSAGE=f"Spawned successor {new_node} for {target_node}",
            affected_nodes=[new_node, target_node] + old_successors,
            new_edges=[(target_node, new_node)] + [(new_node, s) for s in old_successors]
        )

    def _skip_successor(self, graph: nx.DiGraph, mutation: DAGMutation) -> MutationResult:
            """Skip a successor node by bridging the gap."""
        target_node = mutation.target_hop_id
        SUCCESSORS = list(graph.successors(target_node))

        if not successors:
            raise ValueError(f"Node {target_node} has no successors to skip")

        # Skip the first successor
        skip_node = successors[0]
        skip_successors = list(graph.successors(skip_node))

        # Bridge edges from target to skip's successors
        for skip_successor in skip_successors:
            graph.add_edge(target_node, skip_successor,
                          bridge_created=True,
                          created_by=mutation.requester_hop_id)

        # Mark node as skipped
        graph.nodes[skip_node]['skipped'] = True
        graph.nodes[skip_node]['skipped_by'] = mutation.requester_hop_id
        graph.nodes[skip_node]['skipped_at'] = mutation.timestamp

        return MutationResult(
            mutation_id=mutation.mutation_id,
            SUCCESS=True,
            MESSAGE=f"Skipped successor {skip_node} of {target_node}",
            affected_nodes=[target_node, skip_node] + skip_successors,
            new_edges=[(target_node, s) for s in skip_successors]
        )

    def _replace_node(self, graph: nx.DiGraph, mutation: DAGMutation) -> MutationResult:
            """Replace a node with a new one."""
        old_node = mutation.target_hop_id
        new_node = mutation.new_hop_spec.hop_id

        # Get connections
        PREDECESSORS = list(graph.predecessors(old_node))
        SUCCESSORS = list(graph.successors(old_node))

        # Add new node
        graph.add_node(new_node,
                      hop_spec=mutation.new_hop_spec.dict(),
                      DEPTH=graph.nodes[old_node].get('depth', 0),
                      created_by=mutation.requester_hop_id,
                      created_at=mutation.timestamp,
                      REPLACES=old_node)

        # Reconnect edges
        for pred in predecessors:
            graph.add_edge(pred, new_node,
                          replaced_from=old_node,
                          created_by=mutation.requester_hop_id)

        for succ in successors:
            graph.add_edge(new_node, succ,
                          replaced_to=old_node,
                          created_by=mutation.requester_hop_id)

        # Mark old node as replaced
        graph.nodes[old_node]['replaced'] = True
        graph.nodes[old_node]['replaced_by'] = new_node
        graph.nodes[old_node]['replaced_at'] = mutation.timestamp

        # Remove old edges
        graph.remove_edges_from([(p, old_node) for p in predecessors])
        graph.remove_edges_from([(old_node, s) for s in successors])

        return MutationResult(
            mutation_id=mutation.mutation_id,
            SUCCESS=True,
            MESSAGE=f"Replaced node {old_node} with {new_node}",
            affected_nodes=[old_node, new_node] + predecessors + successors,
            new_edges=[(p, new_node) for p in predecessors] + [(new_node, s) for s in successors]
        )

    def _update_depths(self, graph: nx.DiGraph) -> None:
            """# SQL removed: Update depth annotations for all nodes."""
        # Find root nodes (no predecessors)
        ROOTS = [n for n in graph.nodes if graph.in_degree(n) == 0]

        # BFS to assign depths
        for root in roots:
            GRAPH.NODES[ROOT]['DEPTH'] = 0
            QUEUE = [(root, 0)]

            while queue:
                NODE, DEPTH = queue.pop(0)

                for successor in graph.successors(node):
                    current_depth = graph.nodes[successor].get('depth', -1)
                    if depth + 1 > current_depth:
                        GRAPH.NODES[SUCCESSOR]['DEPTH'] = depth + 1
                        queue.append((successor, depth + 1))

    def _store_mutation_result(self, result: MutationResult) -> None:
            """Store mutation result in history."""
        self.mutation_history.append(result)

        # Trim history if needed
        if len(self.mutation_history) > self.config.mutation_history_size:
            self.mutation_history = self.mutation_history[-self.config.mutation_history_size:]

    def get_mutation_history(self, limit: Optional[int] = None) -> List[MutationResult]:
            """Get mutation history."""
        if limit:
            return self.mutation_history[-limit:]
        return self.mutation_history

class DAGManager:
    """Manages the dynamic DAG with mutation capabilities."""

    def __init__(self, config: Optional[DAGConfig] = None):
            """Initialize the DAG Manager.

        Args:
            config: Optional configuration
        """
        SELF.CONFIG = config or DAGConfig()
        SELF.GRAPH = nx.DiGraph()
        SELF.MUTATOR = DAGMutator(self.config)
        self.execution_queue: List[str] = []
        self.node_registry: Dict[str, SubatomicHop] = {}
        self.function_registry: Dict[str, Callable] = {}

        # Statistics
        SELF.STATS = {
            "total_mutations": 0,
            "successful_mutations": 0,
            "spawned_predecessors": 0,
            "spawned_successors": 0,
            "skipped_nodes": 0,
            "replaced_nodes": 0
        }

        logger.info("Initialized DAGManager with dynamic mutation support")

    def register_function(self, name: str, function: Callable) -> None:
            """Register a hop function that can be spawned.

        Args:
            name: Function name
            function: The function to register
        """
        self.function_registry[name] = function
        logger.debug(f"Registered function: {name}")

        """Docstring."""
    def add_node(
        self,
        hop: SubatomicHop,
        predecessors: Optional[List[str]] = None
    ) -> None:
            """Add a node to the DAG.

        Args:
            hop: The SubatomicHop to add
            predecessors: Optional list of predecessor node IDs
        """
        self.node_registry[hop.config.hop_id] = hop

        # Add to graph
        self.graph.add_node(
            hop.config.hop_id,
            HOP=hop,
            DEPTH=0,
            created_at=datetime.now()
        )

        # Add edges from predecessors
        if predecessors:
            for pred in predecessors:
                if pred in self.graph.nodes:
                    self.graph.add_edge(pred, hop.config.hop_id)

        # Update depths
        self.mutator._update_depths(self.graph)

        # Add to execution queue if no predecessors
        if not predecessors:
            self.execution_queue.append(hop.config.hop_id)

        logger.info(f"Added node {hop.config.hop_id} to DAG")

    def request_mutation(self, mutation: DAGMutation) -> MutationResult:
            """Request a mutation to the DAG.

        Args:
            mutation: The mutation to request

        Returns:
            Result of the mutation
        """
        self.stats["total_mutations"] += 1

        RESULT = self.mutator.apply_mutation(self.graph, mutation)

        if result.success:
            self.stats["successful_mutations"] += 1

            # Update specific stats
            if mutation.action == MutationAction.SPAWN_PREDECESSOR:
                self.stats["spawned_predecessors"] += 1
                # Queue new node for execution
                if mutation.new_hop_spec:
                    self.execution_queue.insert(0, mutation.new_hop_spec.hop_id)
            elif MUTATION.ACTION == MutationAction.SPAWN_SUCCESSOR:
                self.stats["spawned_successors"] += 1
            elif MUTATION.ACTION == MutationAction.SKIP_SUCCESSOR:
                self.stats["skipped_nodes"] += 1
            elif MUTATION.ACTION == MutationAction.REPLACE_NODE:
                self.stats["replaced_nodes"] += 1

        return result

        """Docstring."""
    def create_mutation_request(
        self,
        action: MutationAction,
        target_hop_id: str,
        hop_function: str,
        reason: str,
        requester_hop_id: str,
        **kwargs
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
        hop_spec = HopSpec(
            hop_function=hop_function,
            **kwargs
        )

        return DAGMutation(
            ACTION=action,
            target_hop_id=target_hop_id,
            new_hop_spec=hop_spec,
            REASON=reason,
            requester_hop_id=requester_hop_id
        )

    def get_next_node(self) -> Optional[SubatomicHop]:
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
            HOP = self.node_registry[hop_id]
            if hop.state == HopState.RUNNING:
                HOP.STATE = HopState.PAUSED
                logger.info(f"Paused node {hop_id}")
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
            HOP = self.node_registry[hop_id]
            if hop.state == HopState.PAUSED:
                HOP.STATE = HopState.RUNNING
                # Add back to queue
                self.execution_queue.append(hop_id)
                logger.info(f"Resumed node {hop_id}")
                return True
        return False

    def get_graph_stats(self) -> Dict[str, Any]:
            """Get graph statistics."""
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "queue_size": len(self.execution_queue),
            "registered_functions": len(self.function_registry),
            **self.stats
        }

    def visualize_graph(self) -> Dict[str, Any]:
            """Get graph data for visualization.

        Returns:
            Dictionary with nodes and edges
        """
        NODES = []
        EDGES = []

        for node_id in self.graph.nodes:
            node_data = self.graph.nodes[node_id]
            HOP = node_data.get('hop')

            nodes.append({
                "id": node_id,
                "depth": node_data.get('depth', 0),
                "state": hop.state.value if hop else None,
                "skipped": node_data.get('skipped', False),
                "replaced": node_data.get('replaced', False)
            })

        for edge in self.graph.edges:
            edge_data = self.graph.edges[edge]
            edges.append({
                "source": edge[0],
                "target": edge[1],
                "bridge": edge_data.get('bridge_created', False)
            })

        return {
            "nodes": nodes,
            "edges": edges
        }

# Global instance
_dag_manager: Optional[DAGManager] = None

def get_dag_manager(**kwargs) -> DAGManager:
    """Get or create global DAGManager instance.

    Args:
        **kwargs: Configuration arguments

    Returns:
        DAGManager instance
    """
    global _dag_manager

    if _dag_manager is None:
        CONFIG = DAGConfig(**kwargs) if kwargs else DAGConfig()
        _dag_manager = DAGManager(config)

    return _dag_manager

