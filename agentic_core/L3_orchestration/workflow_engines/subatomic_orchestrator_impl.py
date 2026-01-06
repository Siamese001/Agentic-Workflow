from __future__ import annotations
"""Implementation for SubatomicOrchestratorAgent."""

import asyncio
import logging
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

import networkx as nx

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L3_orchestration.workflow_engines.l3_subatomic_testing_mixin import L3SubatomicTestingMixin
from agentic_core.L3_orchestration.workflow_engines.OrchestrationBaseAgent import L3SubatomicTestingMixin


# NAMING FIXED: AgentRole → AgentRole
class AgentRole(Enum):
    '''Brief description of functionality and purpose.'''
    
    CONTEXT_GATHERER = "context_gatherer"
    STRATEGIC_PLANNER = "StrategicPlannerAgent"
    RESUME_BUILDER = "resume_builder"
    QUALITY_CRITIC = "quality_critic"
    MESSAGE_CRAFTER = "message_crafter"
    PROTOCOL_ENFORCER = "protocol_enforcer"
    FACT_CHECKER = "FactChecker"
    PERSONALIZER = "personalizer"
    INSIGHT_ANALYZER = "insight_analyzer"
    CONTENT_DRAFTER = "content_drafter"


# NAMING FIXED: WorkflowType → WorkflowType
class WorkflowType(Enum):
    '''Brief description of functionality and purpose.'''
    
    RESUME_GENERATION = "resume_generation"
    MESSAGE_OUTREACH = "message_outreach"
    CONTENT_CREATION = "content_creation"

# NAMING FIXED: MutationAction → MutationAction
class MutationAction(Enum):
    '''Brief description of functionality and purpose.'''
    
    SPAWN_PREDECESSOR = "spawn_predecessor"

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

# NAMING FIXED: WorkflowBlueprint → WorkflowBlueprint
class WorkflowBlueprint(HealerMixin):
    """Mock WorkflowBlueprint for type hinting."""
    def __init__(self, name, DESCRIPTION, ROLES, EDGES, mutation_hooks=None, parallel_groups=None):
        self.name = name
        self.DESCRIPTION = DESCRIPTION
        self.ROLES = ROLES
        self.EDGES = EDGES
        self.mutation_hooks = mutation_hooks or {}
        self.parallel_groups = parallel_groups or []

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

# NAMING FIXED: AgentRegistry → AgentRegistry
class AgentRegistry(HealerMixin):
    """Mock AgentRegistry for type hinting."""
    pass

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

def get_agent_registry() -> AgentRegistry:
    """Mock function."""
    return AgentRegistry()

# NAMING FIXED: DAGManagerAgent → DagManagerAgent
class DagManagerAgent(HealerMixin, MCPHardenedMixin, L3SubatomicTestingMixin):
    """Mock DAGManagerAgent for type hinting."""
    def __init__(self):
        self.node_registry = {}
        self.execution_queue = []

    def add_node(self, node):
                    
        pass

    def create_mutation_request(self, **kwargs):
                    
        return kwargs

    def request_mutation(self, mutation):
                    
        class MockMutationResult:
                                    
            def __init__(self, success):
                self.success = success
        if mutation['hop_function'] in self.node_registry:
            return MockMutationResult(True)
        else:
            return MockMutationResult(False)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# NAMING FIXED: SubatomicHop → SubatomicHop
class SubatomicHop(HealerMixin, MCPHardenedMixin, L3SubatomicTestingMixin):
    """Mock SubatomicHop for type hinting."""
    def __init__(self, role, hop_function, CONTEXT, enable_prompt_injection):
        self.config = type('obj', (object,), {'hop_id': role.value})()
        self.run = hop_function
        self.context = CONTEXT
        self.enable_prompt_injection = enable_prompt_injection
        self.DagManagerAgent = None

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

def create_functional_agent(role, hop_function, CONTEXT, enable_prompt_injection):
    '''Brief description of functionality and purpose.'''
    
    return SubatomicHop(role, hop_function, CONTEXT, enable_prompt_injection)

def validate_no_legacy_code(value, message):
    """Mock function."""
    pass

# Global orchestrator instance
_orchestrator: Optional[SubatomicOrchestratorAgent] = None

# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.workflow_engines.l3_subatomic_testing_mixin import L3SubatomicTestingMixin

# NAMING FIXED: SubatomicOrchestratorAgent → SubatomicOrchestratorAgent
class SubatomicOrchestratorAgent(HealerMixin, MCPHardenedMixin, L3SubatomicTestingMixin):
    """Implementation for SubatomicOrchestratorAgent."""

    def __init__(self, registry: Optional[AgentRegistry] = None):
        """Initialize the orchestrator.
        Args:
            registry: Optional agent registry (uses global if not provided)
        """
        self.REGISTRY = registry or get_agent_registry()
        self.DagManagerAgent = DAGManagerAgent()
        self.active_graphs: Dict[str, nx.DiGraph] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self._define_standard_workflows()
        LOGGER.info('Initialized SubatomicOrchestratorAgent')

    def _define_standard_workflows(self) -> None:
        """Define standard workflow blueprints."""
        self.resume_blueprint = WorkflowBlueprint(name='Resume Generation',
                                                 DESCRIPTION='Generate optimized resumes from profile data',
                                                 ROLES=[AgentRole.CONTEXT_GATHERER,
                                                        AgentRole.STRATEGIC_PLANNER,
                                                        AgentRole.RESUME_BUILDER,
                                                        AgentRole.QUALITY_CRITIC],
                                                 EDGES=[(AgentRole.CONTEXT_GATHERER,
                                                         AgentRole.STRATEGIC_PLANNER),
                                                        (AgentRole.STRATEGIC_PLANNER,
                                                         AgentRole.RESUME_BUILDER),
                                                        (AgentRole.RESUME_BUILDER,
                                                         AgentRole.QUALITY_CRITIC)],
                                                 mutation_hooks={AgentRole.QUALITY_CRITIC: [(MutationAction.SPAWN_PREDECESSOR,
                                                                                            AgentRole.CONTEXT_GATHERER),
                                                                                           (MutationAction.SPAWN_PREDECESSOR,
                                                                                            AgentRole.FACT_CHECKER)]})
        self.message_blueprint = WorkflowBlueprint(name='Message Outreach',
                                                  DESCRIPTION='Create personalized outreach messages',
                                                  ROLES=[AgentRole.CONTEXT_GATHERER,
                                                         AgentRole.STRATEGIC_PLANNER,
                                                         AgentRole.MESSAGE_CRAFTER,
                                                         AgentRole.QUALITY_CRITIC,
                                                         AgentRole.PROTOCOL_ENFORCER],
                                                  EDGES=[(AgentRole.CONTEXT_GATHERER,
                                                          AgentRole.STRATEGIC_PLANNER),
                                                         (AgentRole.STRATEGIC_PLANNER,
                                                          AgentRole.MESSAGE_CRAFTER),
                                                         (AgentRole.MESSAGE_CRAFTER,
                                                          AgentRole.QUALITY_CRITIC),
                                                         (AgentRole.QUALITY_CRITIC,
                                                          AgentRole.PROTOCOL_ENFORCER)],
                                                  mutation_hooks={AgentRole.QUALITY_CRITIC: [(MutationAction.SPAWN_PREDECESSOR,
                                                                                             AgentRole.PERSONALIZER)]})
        self.content_blueprint = WorkflowBlueprint(name='Content Creation',
                                                  DESCRIPTION='General content creation pipeline',
                                                  ROLES=[AgentRole.CONTEXT_GATHERER,
                                                         AgentRole.STRATEGIC_PLANNER,
                                                         AgentRole.CONTENT_DRAFTER,
                                                         AgentRole.QUALITY_CRITIC],
                                                  EDGES=[(AgentRole.CONTEXT_GATHERER,
                                                          AgentRole.STRATEGIC_PLANNER),
                                                         (AgentRole.STRATEGIC_PLANNER,
                                                          AgentRole.CONTENT_DRAFTER),
                                                         (AgentRole.CONTENT_DRAFTER,
                                                          AgentRole.QUALITY_CRITIC)],
                                                  parallel_groups=[[AgentRole.CONTEXT_GATHERER,
                                                                    AgentRole.INSIGHT_ANALYZER]])

    def build_standard_pipeline(self, WorkflowType: WorkflowType, **kwargs) -> nx.DiGraph:
        """Build a standard workflow pipeline.

        Args:
            WorkflowType: Type of workflow to build
            **kwargs: Additional parameters

        Returns:
            NetworkX DiGraph representing the workflow
        """
        for key, value in kwargs.items():
            if isinstance(value, str):
                validate_no_legacy_code(
                    value, f'build_standard_pipeline parameter {key}')
        if WorkflowType == WorkflowType.RESUME_GENERATION:
            BLUEPRINT = self.resume_blueprint
        elif WorkflowType == WorkflowType.MESSAGE_OUTREACH:
            BLUEPRINT = self.message_blueprint
        elif WorkflowType == WorkflowType.CONTENT_CREATION:
            BLUEPRINT = self.content_blueprint
        else:
            raise ValueError(f'Unknown workflow type: {WorkflowType}')
        return self._build_from_blueprint(BLUEPRINT, **kwargs)

    def build_custom_pipeline(self,
                              roles: List[AgentRole],
                              edges: List[tuple[AgentRole, AgentRole]],
                              **kwargs) -> nx.DiGraph:
        """Build a custom workflow pipeline.

        Args:
            roles: List of roles to include
            edges: Edges between roles
            **kwargs: Additional parameters

        Returns:
            NetworkX DiGraph representing the workflow
        """
        BLUEPRINT = WorkflowBlueprint(name='Custom Workflow',
                                      DESCRIPTION='User-defined custom workflow',
                                      ROLES=roles,
                                      EDGES=edges)
        return self._build_from_blueprint(BLUEPRINT, **kwargs)

    def _build_from_blueprint(self, blueprint: WorkflowBlueprint, **kwargs) -> nx.DiGraph:
        """Build a graph from a workflow blueprint.

        Args:
            blueprint: Workflow blueprint
            **kwargs: Additional parameters

        Returns:
            NetworkX DiGraph
        """
        LOGGER.info(f'Building workflow: {blueprint.name}')
        G = nx.DiGraph()
        role_to_hop: Dict[AgentRole, SubatomicHop] = {}
        for role in blueprint.ROLES:
            hop_function = self._get_hop_function(role, **kwargs)
            HOP = create_functional_agent(role=role,
                                          hop_function=hop_function,
                                          CONTEXT=kwargs.get('context',
                                                             {}),
                                          enable_prompt_injection=kwargs.get('enable_injections',
                                                                             True))
            HOP.DagManagerAgent = self.DagManagerAgent
            role_to_hop[role] = HOP
            G.add_node(HOP, role=role)
        for from_role, to_role in blueprint.EDGES:
            from_hop = role_to_hop[from_role]
            to_hop = role_to_hop[to_role]
            G.add_edge(from_hop, to_hop)
        for role, hooks in blueprint.mutation_hooks.items():
            if role in role_to_hop:
                HOP = role_to_hop[role]
                if 'mutation_hooks' not in HOP.context:
                    HOP.context['mutation_hooks'] = []
                HOP.context['mutation_hooks'].extend(hooks)
        graph_id = f'{blueprint.name}_{datetime.now().isoformat()}'
        self.active_graphs[graph_id] = G
        LOGGER.info(
            f'Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges')
        return G

    def _get_hop_function(self, role: AgentRole, **kwargs) -> callable:
        """Get the hop function for a role.

        Args:
            role: Agent role
            **kwargs: Additional parameters

        Returns:
            Hop function
        """

        async def mock_hop_function(**context):
            """Mock hop function that simulates work."""
            await asyncio.sleep(0.1)
            RESULT = {'role': role.value,
                      'status': 'completed',
                      'output': f'Mock output from {role.value}',
                      'timestamp': datetime.now().isoformat()}
            if role == AgentRole.CONTEXT_GATHERER:
                RESULT['research_data'] = {'sources': ['source1', 'source2']}
            elif role == AgentRole.STRATEGIC_PLANNER:
                RESULT['STRATEGY'] = {
                    'approach': 'analytical', 'framework': 'standard'}
            elif role in [AgentRole.CONTENT_DRAFTER, AgentRole.RESUME_BUILDER, AgentRole.MESSAGE_CRAFTER]:
                RESULT['CONTENT'] = {
                    'draft': 'Generated content draft', 'word_count': 500}
            elif role == AgentRole.QUALITY_CRITIC:
                RESULT['quality_score'] = 0.85
                RESULT['FEEDBACK'] = 'Good quality, minor improvements needed'
            return RESULT
        return mock_hop_function

    async def execute_graph(self,
                            graph: nx.DiGraph,
                            initial_inputs: Dict[str,
                                                 Any],
                            **kwargs) -> Dict[str,
                                              Any]:
        """Execute a workflow graph.
        Args:
            graph: The workflow graph to execute
            initial_inputs: Initial inputs for the graph
            **kwargs: Additional parameters

        Returns:
            Execution results
        """
        LOGGER.info(f'Executing graph with {graph.number_of_nodes()} nodes')
        for key, value in kwargs.items():
            if isinstance(value, str):
                validate_no_legacy_code(value, 'execute_graph inputs')
        execution_id = f'exec_{datetime.now().isoformat()}'
        execution_state = {'id': execution_id,
                           'start_time': datetime.now(),
                           'status': 'running',
                           'completed_nodes': set(),
                           'failed_nodes': set(),
                           'results': {}}
        try:
            for node in graph.nodes():
                self.DagManagerAgent.add_node(node)
            ready_nodes = self._get_ready_nodes(
                graph, execution_state['completed_nodes'])
            while ready_nodes:
                TASKS = []
                for node in ready_nodes:
                    node_inputs = self._get_node_inputs(graph,
                                                        node,
                                                        execution_state['results'],
                                                        initial_inputs)
                    TASK = self._execute_node(node, node_inputs)
                    TASKS.append(TASK)
                RESULTS = await asyncio.gather(*TASKS, return_exceptions=True)
                for node, result in zip(ready_nodes, RESULTS):
                    if isinstance(result, Exception):
                        LOGGER.error(
                            f'Node {node.config.hop_id} failed: {result}')
                        execution_state['failed_nodes'].add(node)
                        if hasattr(node, 'context') and 'mutation_hooks' in node.context:
                            await self._handle_node_failure(node, result, graph)
                    else:
                        LOGGER.info(f'Node {node.config.hop_id} completed')
                        execution_state['completed_nodes'].add(node)
                        execution_state['results'][node] = result
                        self.DagManagerAgent.execution_queue.append(node)
                ready_nodes = self._get_ready_nodes(
                    graph, execution_state['completed_nodes'])
            if len(execution_state['completed_nodes']) == graph.number_of_nodes():
                execution_state['status'] = 'completed'
            else:
                execution_state['status'] = 'partial_failure'
        except Exception as e:
            LOGGER.error(f'Graph execution failed: {e}')
            execution_state['status'] = 'failed'
            execution_state['error'] = str(e)
        finally:
            execution_state['end_time'] = datetime.now()
            execution_state['duration'] = (execution_state['end_time'] - execution_state['start_time']).total_seconds()
            self.execution_history.append(execution_state)
        return execution_state

    def _get_ready_nodes(self,
                         graph: nx.DiGraph,
                         completed_nodes: set[SubatomicHop]) -> list[SubatomicHop]:
        """Get nodes that are ready to execute.

        Args:
            graph: The workflow graph
            completed_nodes: Set of completed nodes

        Returns:
            List of ready nodes
        """
        READY = []
        for node in graph.nodes():
            if node in completed_nodes:
                continue
            PREDECESSORS = set(graph.predecessors(node))
            if PREDECESSORS.issubset(completed_nodes):
                READY.append(node)
        return READY

    def _get_node_inputs(self,
                         graph: nx.DiGraph,
                         node: SubatomicHop,
                         results: Dict[SubatomicHop,
                                       Any],
                         initial_inputs: Dict[str,
                             Any]) -> Dict[str,
                                           Any]:
        """Get inputs for a node.

        Args:
            graph: The workflow graph
            node: The node to get inputs for
            results: Results from completed nodes
            initial_inputs: Initial graph inputs
        Returns:
            Node inputs
        """
        INPUTS = initial_inputs.copy()
        for predecessor in graph.predecessors(node):
            if predecessor in results:
                pred_result = results[predecessor]
                INPUTS[f'from_{predecessor.config.hop_id}'] = pred_result
        return INPUTS

    async def _execute_node(self, node: SubatomicHop, inputs: Dict[str, Any]) -> Any:
        """Execute a single node.

        Args:
            node: The node to execute
            inputs: Node inputs

        Returns:
            Node result
        """
        try:
            RESULT = await node.run(**inputs)
            return RESULT
        except Exception as e:
            LOGGER.error(f'Node execution error: {e}')
            raise

    async def _handle_node_failure(self,
                                   node: SubatomicHop,
                                   error: Exception,
                                   graph: nx.DiGraph) -> None:
        """Handle node failure with potential mutations.

        Args:
            node: The failed node
            error: The error that occurred
            graph: The workflow graph
        """
        if 'mutation_hooks' not in node.context:
            return
        mutation_hooks = node.context['mutation_hooks']
        for action, role in mutation_hooks:
            try:
                MUTATION = self.DagManagerAgent.create_mutation_request(action=action,
                                                                    target_hop_id=node.config.hop_id,
                                                                    hop_function=role.value,
                                                                    REASON=f'Node failed: {str(error)}',
                                                                    requester_hop_id=node.config.hop_id)
                RESULT = self.DagManagerAgent.request_mutation(MUTATION)
                if RESULT.success:
                    LOGGER.info(
                        f'Successfully applied mutation for {role.value}')
                    new_hop = self.DagManagerAgent.node_registry.get(role.value)
                    if new_hop:
                        graph.add_node(new_hop, role=role)
                        graph.add_edge(new_hop, node)
            except Exception as e:
                LOGGER.error(f'Failed to apply mutation: {e}')

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics.

        Returns:
            Execution statistics
        """
        if not self.execution_history:
            return {'total_executions': 0}
        TOTAL = len(self.execution_history)
        COMPLETED = sum(
            (1 for e in self.execution_history if e['status'] == 'completed'))
        FAILED = sum(
            (1 for e in self.execution_history if e['status'] == 'failed'))
        avg_duration = sum((e.get('duration', 0)
                           for e in self.execution_history)) / TOTAL if TOTAL > 0 else 0
        return {'total_executions': TOTAL,
                'completed': COMPLETED,
                'failed': FAILED,
                'success_rate': COMPLETED / TOTAL if TOTAL > 0 else 0,
                'average_duration': avg_duration,
                'active_graphs': len(self.active_graphs)}

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


def get_orchestrator() -> SubatomicOrchestratorAgent:
    """Get the global orchestrator instance.

    Returns:
        SubatomicOrchestratorAgent instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SubatomicOrchestratorAgent()
    return _orchestrator


async def execute_resume_workflow(profile_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Execute the resume generation workflow.

    Args:
        profile_data: User profile data
        **kwargs: Additional parameters

    Returns:
        Execution results
    """
    ORCHESTRATOR = get_orchestrator()
    GRAPH = ORCHESTRATOR.build_standard_pipeline(WorkflowType.RESUME_GENERATION,
                                                 CONTEXT={
                                                     'profile': profile_data},
                                                 **kwargs)
    return await ORCHESTRATOR.execute_graph(GRAPH, initial_inputs={'profile': profile_data})

async def execute_message_workflow(recipient_data: Dict[str, Any],
                                   message_type: str,
                                   **kwargs) -> Dict[str, Any]:
    """Execute the message outreach workflow.

    Args:
        recipient_data: Recipient profile data
        message_type: Type of message to create
        **kwargs: Additional parameters

    Returns:
        Execution results
    """
    ORCHESTRATOR = get_orchestrator()
    GRAPH = ORCHESTRATOR.build_standard_pipeline(WorkflowType.MESSAGE_OUTREACH,
                                                 CONTEXT={'recipient': recipient_data,
                                                          'type': message_type},
                                                 **kwargs)
    return await ORCHESTRATOR.execute_graph(GRAPH,
                                            initial_inputs={'recipient': recipient_data,
                                                            'type': message_type})