"""
DAGManagerAgent - Extracted for one-class-per-file pattern.

Originally from: DAGMutatorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin

class DAGManagerAgent(HealerMixin, MCPHardenedMixin, L3SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin):
    """Manages the dynamic DAG with mutation capabilities.
    
    HARDENED: Redis caching + Pinecone vector support for DAG structure caching.
    """
    
    # [PHASE 5] Redis/Pinecone integration
    _cache_prefix: str = "dag_manager"
    _namespace: str = "l3_dags"
    
    def __init__(self, config: Optional[DAGConfig] = None) -> None:
        """Initialize the DAG Manager.
        
        Args:
            config: Optional configuration
        """
        self.config = config or DAGConfig()
        self.graph = nx.DiGraph()
        self.mutator = DAGMutator(self.config)
        self.execution_queue: List[str] = []
        self.node_registry: Dict[str, SubatomicHop] = {}
        self.function_registry: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            "total_mutations": 0,
            "successful_mutations": 0,
            "spawned_predecessors": 0,
            "spawned_successors": 0,
            "skipped_nodes": 0,
            "replaced_nodes": 0
        }
        
        Logger.info("Initialized DAGManagerAgent with dynamic mutation support")
    
    def register_function(self, name: str, function: Callable) -> None:
        """Register a hop function that can be spawned.
        
        Args:
            name: Function name
            function: The function to register
        """
        self.function_registry[name] = function
        Logger.debug(f"Registered function: {name}")
    
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
            hop=hop,
            depth=0,
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
            
            # Update specific stats
            if mutation.action == MutationAction.SPAWN_PREDECESSOR:
                self.stats["spawned_predecessors"] += 1
                # Queue new node for execution
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
            action=action,
            target_hop_id=target_hop_id,
            new_hop_spec=hop_spec,
            reason=reason,
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
                # Add back to queue
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
            **self.stats
        }
    
    def visualize_graph(self) -> Dict[str, Any]:
        """Get graph data for visualization.
        
        Returns:
            Dictionary with nodes and edges
        """
        nodes = []
        edges = []
        
        for node_id in self.graph.nodes:
            node_data = self.graph.nodes[node_id]
            hop = node_data.get('hop')
            
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

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
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
