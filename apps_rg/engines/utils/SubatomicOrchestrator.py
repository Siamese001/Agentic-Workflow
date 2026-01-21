"""Subatomic Orchestrator - Dynamic DAG builder using functional agents.

This orchestrator replaces the legacy K-node system with a dynamic mesh
of SubatomicHops assembled based on functional roles from the AgentRegistry.
"""

import asyncio
import logging
import networkx as nx
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from ..runtime.core.SubatomicHop import SubatomicHop, HopState, MicroStage
from ..runtime.core.dynamic_dag_manager import DAGManager, MutationAction
from ..runtime.registry.agent_capabilities import (
    AgentRegistry,
    AgentRole,
    get_agent_registry,
    create_functional_agent,
    LegacyCodeError,
    validate_no_legacy_code
)

Logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """Types of predefined workflows."""
    RESUME_GENERATION = "resume_generation"
    MESSAGE_OUTREACH = "message_outreach"
    CONTENT_CREATION = "content_creation"
    RESEARCH_SYNTHESIS = "research_synthesis"
    CUSTOM = "custom"


@dataclass
class WorkflowBlueprint:
    """Blueprint for a workflow graph."""
    name: str
    description: str
    roles: List[AgentRole]
    edges: List[Tuple[AgentRole, AgentRole]]
    mutation_hooks: Dict[AgentRole, List[Tuple[MutationAction, AgentRole]]] = field(default_factory=dict)
    parallel_groups: List[List[AgentRole]] = field(default_factory=list)


class SubatomicOrchestrator:
    """Orchestrator that builds and executes dynamic DAGs of functional agents."""

    def __init__(self, registry: Optional[AgentRegistry] = None):
        """Initialize the orchestrator.

        Args:
            registry: Optional agent registry (uses global if not provided)
        """
        self.registry = registry or get_agent_registry()
        self.DagManager = DAGManager()
        self.active_graphs: Dict[str, nx.DiGraph] = {}
        self.execution_history: List[Dict[str, Any]] = []

        # Define standard workflows
        self._define_standard_workflows()

        Logger.info("Initialized SubatomicOrchestrator")

    def _define_standard_workflows(self) -> None:
        """Define standard workflow blueprints."""

        # Resume Generation Workflow
        self.resume_blueprint = WorkflowBlueprint(
            name="Resume Generation",
            description="Generate optimized resumes from profile data",
            roles=[
                AgentRole.CONTEXT_GATHERER,
                AgentRole.STRATEGIC_PLANNER,
                AgentRole.RESUME_BUILDER,
                AgentRole.QUALITY_CRITIC
            ],
            edges=[
                (AgentRole.CONTEXT_GATHERER, AgentRole.STRATEGIC_PLANNER),
                (AgentRole.STRATEGIC_PLANNER, AgentRole.RESUME_BUILDER),
                (AgentRole.RESUME_BUILDER, AgentRole.QUALITY_CRITIC)
            ],
            mutation_hooks={
                AgentRole.QUALITY_CRITIC: [
                    (MutationAction.SPAWN_PREDECESSOR, AgentRole.CONTEXT_GATHERER),
                    (MutationAction.SPAWN_PREDECESSOR, AgentRole.FACT_CHECKER)
                ]
            }
        )

        # Message Outreach Workflow
        self.message_blueprint = WorkflowBlueprint(
            name="Message Outreach",
            description="Create personalized outreach messages",
            roles=[
                AgentRole.CONTEXT_GATHERER,
                AgentRole.STRATEGIC_PLANNER,
                AgentRole.MESSAGE_CRAFTER,
                AgentRole.QUALITY_CRITIC,
                AgentRole.PROTOCOL_ENFORCER
            ],
            edges=[
                (AgentRole.CONTEXT_GATHERER, AgentRole.STRATEGIC_PLANNER),
                (AgentRole.STRATEGIC_PLANNER, AgentRole.MESSAGE_CRAFTER),
                (AgentRole.MESSAGE_CRAFTER, AgentRole.QUALITY_CRITIC),
                (AgentRole.QUALITY_CRITIC, AgentRole.PROTOCOL_ENFORCER)
            ],
            mutation_hooks={
                AgentRole.QUALITY_CRITIC: [
                    (MutationAction.SPAWN_PREDECESSOR, AgentRole.PERSONALIZER)
                ]
            }
        )

        # Content Creation Workflow
        self.content_blueprint = WorkflowBlueprint(
            name="Content Creation",
            description="General content creation pipeline",
            roles=[
                AgentRole.CONTEXT_GATHERER,
                AgentRole.STRATEGIC_PLANNER,
                AgentRole.CONTENT_DRAFTER,
                AgentRole.QUALITY_CRITIC
            ],
            edges=[
                (AgentRole.CONTEXT_GATHERER, AgentRole.STRATEGIC_PLANNER),
                (AgentRole.STRATEGIC_PLANNER, AgentRole.CONTENT_DRAFTER),
                (AgentRole.CONTENT_DRAFTER, AgentRole.QUALITY_CRITIC)
            ],
            parallel_groups=[
                [AgentRole.CONTEXT_GATHERER, AgentRole.INSIGHT_ANALYZER]
            ]
        )

    def build_standard_pipeline(
        self,
        WorkflowType: WorkflowType,
        **kwargs
    ) -> nx.DiGraph:
        """Build a standard workflow pipeline.

        Args:
            WorkflowType: Type of workflow to build
            **kwargs: Additional parameters

        Returns:
            NetworkX DiGraph representing the workflow
        """
        # Validate no legacy references
        for key, value in kwargs.items():
            if isinstance(value, str):
                validate_no_legacy_code(value, f"build_standard_pipeline parameter {key}")

        # Select blueprint
        if WorkflowType == WorkflowType.RESUME_GENERATION:
            blueprint = self.resume_blueprint
        elif WorkflowType == WorkflowType.MESSAGE_OUTREACH:
            blueprint = self.message_blueprint
        elif WorkflowType == WorkflowType.CONTENT_CREATION:
            blueprint = self.content_blueprint
        else:
            raise ValueError(f"Unknown workflow type: {WorkflowType}")

        return self._build_from_blueprint(blueprint, **kwargs)

    def build_custom_pipeline(
        self,
        roles: List[AgentRole],
        edges: List[Tuple[AgentRole, AgentRole]],
        **kwargs
    ) -> nx.DiGraph:
        """Build a custom workflow pipeline.

        Args:
            roles: List of roles to include
            edges: Edges between roles
            **kwargs: Additional parameters

        Returns:
            NetworkX DiGraph representing the workflow
        """
        # Create custom blueprint
        blueprint = WorkflowBlueprint(
            name="Custom Workflow",
            description="User-defined custom workflow",
            roles=roles,
            edges=edges
        )

        return self._build_from_blueprint(blueprint, **kwargs)

    def _build_from_blueprint(self, blueprint: WorkflowBlueprint, **kwargs) -> nx.DiGraph:
        """Build a graph from a workflow blueprint.

        Args:
            blueprint: Workflow blueprint
            **kwargs: Additional parameters

        Returns:
            NetworkX DiGraph
        """
        Logger.info(f"Building workflow: {blueprint.name}")

        # Create graph
        G = nx.DiGraph()

        # Create agent instances
        role_to_hop: Dict[AgentRole, SubatomicHop] = {}

        for role in blueprint.roles:
            # Get the hop function for this role
            hop_function = self._get_hop_function(role, **kwargs)

            # Create the hop
            hop = create_functional_agent(
                role=role,
                hop_function=hop_function,
                context=kwargs.get("context", {}),
                enable_prompt_injection=kwargs.get("enable_injections", True)
            )

            # Set DAG manager for mutation support
            hop.DagManager = self.DagManager

            role_to_hop[role] = hop
            G.add_node(hop, role=role)

        # Add edges
        for from_role, to_role in blueprint.edges:
            from_hop = role_to_hop[from_role]
            to_hop = role_to_hop[to_role]
            G.add_edge(from_hop, to_hop)

        # Configure mutation hooks
        for role, hooks in blueprint.mutation_hooks.items():
            if role in role_to_hop:
                hop = role_to_hop[role]
                # Store mutation capabilities in hop context
                if "mutation_hooks" not in hop.context:
                    hop.context["mutation_hooks"] = []
                hop.context["mutation_hooks"].extend(hooks)

        # Store graph
        graph_id = f"{blueprint.name}_{datetime.now().isoformat()}"
        self.active_graphs[graph_id] = G

        Logger.info(f"Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

        return G

    def _get_hop_function(self, role: AgentRole, **kwargs) -> callable:
        """Get the hop function for a role.

        Args:
            role: Agent role
            **kwargs: Additional parameters

        Returns:
            Hop function
        """
        # In a real implementation, these would be actual functions
        # For now, we create mock functions based on role

        async def mock_hop_function(**context):
            """Mock hop function that simulates work."""
            await asyncio.sleep(0.1)  # Simulate work

            result = {
                "role": role.value,
                "status": "completed",
                "output": f"Mock output from {role.value}",
                "timestamp": datetime.now().isoformat()
            }

            # Add role-specific mock data
            if role == AgentRole.CONTEXT_GATHERER:
                result["research_data"] = {"sources": ["source1", "source2"]}
            elif role == AgentRole.STRATEGIC_PLANNER:
                result["strategy"] = {"approach": "analytical", "framework": "standard"}
            elif role in [AgentRole.CONTENT_DRAFTER, AgentRole.RESUME_BUILDER, AgentRole.MESSAGE_CRAFTER]:
                result["content"] = {"draft": "Generated content draft", "word_count": 500}
            elif role == AgentRole.QUALITY_CRITIC:
                result["quality_score"] = 0.85
                result["feedback"] = "Good quality, minor improvements needed"

            return result

        return mock_hop_function

    async def execute_graph(
        self,
        graph: nx.DiGraph,
        initial_inputs: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a workflow graph.

        Args:
            graph: The workflow graph to execute
            initial_inputs: Initial inputs for the graph
            **kwargs: Additional parameters

        Returns:
            Execution results
        """
        Logger.info(f"Executing graph with {graph.number_of_nodes()} nodes")

        # Validate no legacy references
        for key, value in initial_inputs.items():
            if isinstance(value, str):
                validate_no_legacy_code(value, "execute_graph inputs")

        # Track execution
        execution_id = f"exec_{datetime.now().isoformat()}"
        execution_state = {
            "id": execution_id,
            "start_time": datetime.now(),
            "status": "running",
            "completed_nodes": set(),
            "failed_nodes": set(),
            "results": {}
        }

        try:
            # Initialize graph with DAG manager
            for node in graph.nodes():
                self.DagManager.add_node(node)

            # Execute nodes in topological order
            ready_nodes = self._get_ready_nodes(graph, execution_state["completed_nodes"])

            while ready_nodes:
                # Execute ready nodes in parallel
                tasks = []
                for node in ready_nodes:
                    # Get inputs for this node
                    node_inputs = self._get_node_inputs(
                        graph, node, execution_state["results"], initial_inputs
                    )

                    Task = self._execute_node(node, node_inputs)
                    tasks.append(Task)

                # Wait for all tasks to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for node, result in zip(ready_nodes, results):
                    if isinstance(result, Exception):
                        Logger.error(f"Node {node.config.hop_id} failed: {result}")
                        execution_state["failed_nodes"].add(node)

                        # Handle failure - check for mutations
                        if hasattr(node, 'context') and "mutation_hooks" in node.context:
                            await self._handle_node_failure(node, result, graph)
                    else:
                        Logger.info(f"Node {node.config.hop_id} completed")
                        execution_state["completed_nodes"].add(node)
                        execution_state["results"][node] = result

                        # Add to execution queue
                        self.DagManager.execution_queue.append(node)

                # Get next ready nodes
                ready_nodes = self._get_ready_nodes(graph, execution_state["completed_nodes"])

            # Check if all nodes completed
            if len(execution_state["completed_nodes"]) == graph.number_of_nodes():
                execution_state["status"] = "completed"
            else:
                execution_state["status"] = "partial_failure"

        except Exception as e:
            Logger.error(f"Graph execution failed: {e}")
            execution_state["status"] = "failed"
            execution_state["error"] = str(e)

        finally:
            execution_state["end_time"] = datetime.now()
            execution_state["duration"] = (
                execution_state["end_time"] - execution_state["start_time"]
            ).total_seconds()

            # Store in history
            self.execution_history.append(execution_state)

        return execution_state

    def _get_ready_nodes(
        self,
        graph: nx.DiGraph,
        completed_nodes: Set[SubatomicHop]
    ) -> List[SubatomicHop]:
        """Get nodes that are ready to execute.

        Args:
            graph: The workflow graph
            completed_nodes: Set of completed nodes

        Returns:
            List of ready nodes
        """
        ready = []

        for node in graph.nodes():
            if node in completed_nodes:
                continue

            # Check if all predecessors are completed
            predecessors = set(graph.predecessors(node))
            if predecessors.issubset(completed_nodes):
                ready.append(node)

        return ready

    def _get_node_inputs(
        self,
        graph: nx.DiGraph,
        node: SubatomicHop,
        results: Dict[SubatomicHop, Any],
        initial_inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get inputs for a node.

        Args:
            graph: The workflow graph
            node: The node to get inputs for
            results: Results from completed nodes
            initial_inputs: Initial graph inputs

        Returns:
            Node inputs
        """
        inputs = initial_inputs.copy()

        # Add outputs from predecessor nodes
        for predecessor in graph.predecessors(node):
            if predecessor in results:
                pred_result = results[predecessor]
                inputs[f"from_{predecessor.config.hop_id}"] = pred_result

        return inputs

    async def _execute_node(
        self,
        node: SubatomicHop,
        inputs: Dict[str, Any]
    ) -> Any:
        """Execute a single node.

        Args:
            node: The node to execute
            inputs: Node inputs

        Returns:
            Node result
        """
        try:
            # Run the hop through all micro-stages
            result = await node.run(**inputs)
            return result
        except Exception as e:
            Logger.error(f"Node execution error: {e}")
            raise

    async def _handle_node_failure(
        self,
        node: SubatomicHop,
        error: Exception,
        graph: nx.DiGraph
    ) -> None:
        """Handle node failure with potential mutations.

        Args:
            node: The failed node
            error: The error that occurred
            graph: The workflow graph
        """
        # Check if node wants to mutate
        if "mutation_hooks" not in node.context:
            return

        mutation_hooks = node.context["mutation_hooks"]

        for action, role in mutation_hooks:
            try:
                # Create mutation request
                mutation = self.DagManager.create_mutation_request(
                    action=action,
                    target_hop_id=node.config.hop_id,
                    hop_function=role.value,
                    reason=f"Node failed: {str(error)}",
                    requester_hop_id=node.config.hop_id
                )

                # Apply mutation
                result = self.DagManager.request_mutation(mutation)

                if result.success:
                    Logger.info(f"Successfully applied mutation for {role.value}")

                    # Add new node to graph
                    new_hop = self.DagManager.node_registry.get(role.value)
                    if new_hop:
                        graph.add_node(new_hop, role=role)
                        graph.add_edge(new_hop, node)

            except Exception as e:
                Logger.error(f"Failed to apply mutation: {e}")

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics.

        Returns:
            Execution statistics
        """
        if not self.execution_history:
            return {"total_executions": 0}

        total = len(self.execution_history)
        completed = sum(1 for e in self.execution_history if e["status"] == "completed")
        failed = sum(1 for e in self.execution_history if e["status"] == "failed")

        avg_duration = sum(e.get("duration", 0) for e in self.execution_history) / total

        return {
            "total_executions": total,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total if total > 0 else 0,
            "average_duration": avg_duration,
            "active_graphs": len(self.active_graphs)
        }


# Global orchestrator instance
_orchestrator: Optional[SubatomicOrchestrator] = None


def get_orchestrator() -> SubatomicOrchestrator:
    """Get the global orchestrator instance.

    Returns:
        SubatomicOrchestrator instance
    """
    global _orchestrator

    if _orchestrator is None:
        _orchestrator = SubatomicOrchestrator()

    return _orchestrator


# Convenience functions
async def execute_resume_workflow(profile_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Execute the resume generation workflow.

    Args:
        profile_data: User profile data
        **kwargs: Additional parameters

    Returns:
        Execution results
    """
    orchestrator = get_orchestrator()

    # Build the workflow
    graph = orchestrator.build_standard_pipeline(
        WorkflowType.RESUME_GENERATION,
        context={"profile": profile_data},
        **kwargs
    )

    # Execute the workflow
    return await orchestrator.execute_graph(
        graph,
        initial_inputs={"profile": profile_data}
    )


async def execute_message_workflow(
    recipient_data: Dict[str, Any],
    message_type: str,
    **kwargs
) -> Dict[str, Any]:
    """Execute the message outreach workflow.

    Args:
        recipient_data: Recipient profile data
        message_type: Type of message to create
        **kwargs: Additional parameters

    Returns:
        Execution results
    """
    orchestrator = get_orchestrator()

    # Build the workflow
    graph = orchestrator.build_standard_pipeline(
        WorkflowType.MESSAGE_OUTREACH,
        context={"recipient": recipient_data, "type": message_type},
        **kwargs
    )

    # Execute the workflow
    return await orchestrator.execute_graph(
        graph,
        initial_inputs={"recipient": recipient_data, "type": message_type}
    )
