from __future__ import annotations
"""
Self-Recovering Orchestrator - L3 Orchestration Enhancement

Dynamically adapts workflow graphs based on failure patterns.
Automatically mutates workflows to Route around failures and optimize execution.
"""
import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
import networkx as nx
Logger: Any = logging.getLogger(__name__)

class RecoveryStrategy(Enum):
    """Recovery strategies for failed nodes."""
    RETRY: Any = 'retry'
    SKIP: Any = 'skip'
    REPLACE: Any = 'replace'
    FORK: Any = 'fork'
    ROLLBACK: Any = 'rollback'

@dataclass
class NodeFailurePattern:
    """Tracks failure patterns for workflow nodes."""
    node_id: str
    failure_count: int = 0
    success_count: int = 0
    last_failure: Optional[datetime] = None
    failure_reasons: List[str] = field(default_factory=list)
    avg_execution_time: float = 0.0
    recovery_attempts: int = 0

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        total: Any = self.failure_count + self.success_count
        return self.failure_count / total if total > 0 else 0.0

    @property
    def is_problematic(self) -> bool:
        """Check if node is problematic."""
        return self.failure_rate > 0.5 and self.failure_count >= 3

@dataclass
class WorkflowMutation:
    """Represents a workflow graph mutation."""
    mutation_id: str
    mutation_type: RecoveryStrategy
    target_node: str
    replacement_node: Optional[str] = None
    reason: str = ''
    applied_at: Optional[datetime] = None
    success: bool = False

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

class SelfRecoveringOrchestratorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Orchestrator that automatically recovers from workflow failures.
    
    Features:
    - Automatic failure detection and classification
    - Dynamic workflow graph mutation
    - Intelligent retry with backoff
    - Alternative path routing
    - Failure pattern learning
    """

    def __init__(self) -> None:
        """Initialize the self-recovering orchestrator."""
        self.node_patterns: Dict[str, NodeFailurePattern] = {}
        self.mutation_history: List[WorkflowMutation] = []
        self.active_graphs: Dict[str, nx.DiGraph] = {}
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        self.alternative_routes: Dict[str, List[str]] = {}
        self.max_retries = 3
        self.retry_backoff_base = 2.0
        self.mutation_threshold = 0.45
        self.max_mutations_per_node = 3
        self.probation_list: Dict[str, Dict[str, int]] = {}
        self._mutation_task = None
        Logger.info('Self-Recovering Orchestrator initialized')

    def awaken_mutation_engine(self) -> Any:
        """Explicitly start the L3 evolution cycle"""
        if not self._mutation_task:
            self._mutation_task = asyncio.create_task(self.autonomous_mutation_cycle())
            Logger.info('L3 Autonomous mutation cycle awakened')

    async def autonomous_mutation_cycle(self) -> Any:
        """L3: Continuous workflow optimization cycle"""
        while True:
            try:
                await asyncio.sleep(600)
                for node_id, pattern in self.node_patterns.items():
                    if pattern.failure_rate > self.mutation_threshold and pattern.failure_count >= 3:
                        mutation_count: Any = sum((1 for m in self.mutation_history if m.target_node == node_id))
                        if mutation_count < self.max_mutations_per_node:
                            Logger.info(f'L3: Auto-mutating problematic node {node_id}')
                            await self.mutate_node(node_id, pattern.failure_rate)
                Logger.debug('L3: Autonomous mutation cycle completed')
            except Exception as e:
                Logger.error(f'L3 Mutation cycle error: {e}')
                await asyncio.sleep(60)

    async def execute_with_recovery(self, graph: nx.DiGraph, initial_inputs: Dict[str, Any], graph_id: str) -> Dict[str, Any]:
        """
        Execute a workflow graph with automatic recovery.
        
        Args:
            graph: Workflow graph to execute
            initial_inputs: Initial inputs
            graph_id: Unique graph identifier
            
        Returns:
            Execution results
        """
        self.active_graphs[graph_id] = graph.copy()
        execution_state: Any = {'graph_id': graph_id, 'start_time': datetime.now(), 'status': 'running', 'completed_nodes': set(), 'failed_nodes': set(), 'results': {}, 'mutations_applied': [], 'recovery_attempts': 0}
        try:
            await self._execute_graph_with_recovery(graph_id, initial_inputs, execution_state)
            if len(execution_state['completed_nodes']) == len(list(graph.nodes())):
                execution_state['status'] = 'completed'
            elif execution_state['failed_nodes']:
                execution_state['status'] = 'partial_failure'
            else:
                execution_state['status'] = 'completed_with_recovery'
        except Exception as e:
            Logger.error(f'Graph execution failed: {e}')
            execution_state['status'] = 'failed'
            execution_state['error'] = str(e)
        finally:
            execution_state['end_time'] = datetime.now()
            execution_state['duration'] = (execution_state['end_time'] - execution_state['start_time']).total_seconds()
        return execution_state

    async def _execute_graph_with_recovery(self, graph_id: str, initial_inputs: Dict[str, Any], execution_state: Dict[str, Any]):
        """Execute graph with recovery logic."""
        graph = self.active_graphs[graph_id]
        ready_nodes = self._get_ready_nodes(graph, execution_state['completed_nodes'])
        while ready_nodes:
            for node in ready_nodes:
                node_id = self._get_node_id(node)
                success = await self._execute_node_with_retry(node, node_id, initial_inputs, execution_state)
                if success:
                    execution_state['completed_nodes'].add(node)
                    self._record_node_success(node_id)
                else:
                    execution_state['failed_nodes'].add(node)
                    self._record_node_failure(node_id, 'Execution failed after retries')
                    recovery_applied = await self._apply_recovery_strategy(graph_id, node, node_id, execution_state)
                    if recovery_applied:
                        execution_state['recovery_attempts'] += 1
            ready_nodes = self._get_ready_nodes(graph, execution_state['completed_nodes'])

    async def _execute_node_with_retry(self, node: Any, node_id: str, initial_inputs: Dict[str, Any], execution_state: Dict[str, Any]) -> bool:
        """
        Execute a node with intelligent retry logic.
        
        Args:
            node: Node to execute
            node_id: Node identifier
            initial_inputs: Initial inputs
            execution_state: Execution state
            
        Returns:
            True if successful, False otherwise
        """
        pattern = self.node_patterns.get(node_id)
        max_retries = self.max_retries
        if pattern and pattern.is_problematic:
            max_retries = 1
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    backoff = self.retry_backoff_base ** attempt
                    Logger.info(f'Retry {attempt}/{max_retries} for {node_id} after {backoff}s')
                    await asyncio.sleep(backoff)
                start_time = datetime.now()
                result = await self._execute_single_node(node, initial_inputs, execution_state)
                execution_time = (datetime.now() - start_time).total_seconds()
                execution_state['results'][node] = result
                self._update_execution_time(node_id, execution_time)
                return True
            except Exception as e:
                Logger.warning(f'Node {node_id} attempt {attempt + 1} failed: {e}')
                if attempt == max_retries - 1:
                    return False
        return False

    async def _execute_single_node(self, node: Any, initial_inputs: Dict[str, Any], execution_state: Dict[str, Any]) -> Any:
        """Execute a single node."""
        if hasattr(node, 'run'):
            return await node.run(**initial_inputs)
        elif hasattr(node, 'execute'):
            return await node.execute(**initial_inputs)
        else:
            return {'status': 'mock_success', 'node': str(node)}

    async def _apply_recovery_strategy(self, graph_id: str, failed_node: Any, node_id: str, execution_state: Dict[str, Any]) -> bool:
        """
        Apply recovery strategy for a failed node.
        
        Args:
            graph_id: Graph identifier
            failed_node: The failed node
            node_id: Node identifier
            execution_state: Execution state
        Returns:
            True if recovery was applied
        """
        pattern = self.node_patterns.get(node_id)
        if not pattern:
            return False
        strategy = self._select_recovery_strategy(pattern)
        graph = self.active_graphs[graph_id]
        if strategy == RecoveryStrategy.SKIP:
            Logger.info(f'Applying SKIP strategy for {node_id}')
            execution_state['completed_nodes'].add(failed_node)
            execution_state['results'][failed_node] = {'status': 'skipped', 'reason': 'recovery_skip'}
            mutation = WorkflowMutation(mutation_id=f'mut_{len(self.mutation_history)}', mutation_type=RecoveryStrategy.SKIP, target_node=node_id, reason='Node consistently failing, skipping to continue workflow', applied_at=datetime.now(), success=True)
            self.mutation_history.append(mutation)
            execution_state['mutations_applied'].append(mutation)
            return True
        elif strategy == RecoveryStrategy.FORK:
            Logger.info(f'Applying FORK strategy for {node_id}')
            successors = list(graph.successors(failed_node))
            if successors:
                for successor in successors:
                    execution_state['completed_nodes'].add(failed_node)
                    execution_state['results'][failed_node] = {'status': 'forked', 'reason': 'recovery_fork'}
                mutation = WorkflowMutation(mutation_id=f'mut_{len(self.mutation_history)}', mutation_type=RecoveryStrategy.FORK, target_node=node_id, reason='Forking workflow to bypass failed node', applied_at=datetime.now(), success=True)
                self.mutation_history.append(mutation)
                execution_state['mutations_applied'].append(mutation)
                return True
        elif strategy == RecoveryStrategy.REPLACE:
            Logger.info(f'Applying REPLACE strategy for {node_id}')
            replacement = self._find_replacement_node(node_id, graph)
            if replacement:
                graph.add_node(replacement)
                predecessors = list(graph.predecessors(failed_node))
                successors = list(graph.successors(failed_node))
                for pred in predecessors:
                    graph.add_edge(pred, replacement)
                for succ in successors:
                    graph.add_edge(replacement, succ)
                graph.remove_node(failed_node)
                mutation = WorkflowMutation(mutation_id=f'mut_{len(self.mutation_history)}', mutation_type=RecoveryStrategy.REPLACE, target_node=node_id, replacement_node=str(replacement), reason='Replaced problematic node with alternative', applied_at=datetime.now(), success=True)
                self.mutation_history.append(mutation)
                execution_state['mutations_applied'].append(mutation)
                return True
        return False

    def _select_recovery_strategy(self, pattern: NodeFailurePattern) -> RecoveryStrategy:
        """
        Select appropriate recovery strategy based on failure pattern.
        
        Args:
            pattern: Node failure pattern
            
        Returns:
            Recovery strategy
        """
        if pattern.failure_rate > 0.8 and pattern.failure_count >= 5:
            return RecoveryStrategy.SKIP
        if pattern.failure_rate > 0.6 and pattern.recovery_attempts < 2:
            return RecoveryStrategy.REPLACE
        if pattern.failure_rate > 0.5:
            return RecoveryStrategy.FORK
        return RecoveryStrategy.RETRY

    async def mutate_node(self, failed_node: str, failure_rate: float) -> str:
        """L3: Sovereign mutation with Probationary Logic"""
        Logger.info(f'L3 SELF-HEALING: Mutating {failed_node} (failure_rate={failure_rate:.2f})')
        if failure_rate > 0.8:
            strategy: Any = 'SKIP'
        elif failure_rate > 0.6:
            strategy: Any = 'REPLACE'
        elif failure_rate > 0.5:
            strategy: Any = 'FORK'
        else:
            strategy: Any = 'RETRY'
        new_node: Any = f'{failed_node}_alt_{len(self.mutation_history)}'
        if strategy == 'REPLACE':
            self.alternative_routes[failed_node] = [new_node]
            self.probation_list[new_node] = {'test_runs': 0, 'failures': 0}
            Logger.info(f'L3: Replacement node {new_node} under probation')
        mutation: Any = WorkflowMutation(mutation_id=f'mut_{len(self.mutation_history)}', mutation_type=RecoveryStrategy[strategy], target_node=failed_node, replacement_node=new_node if strategy == 'REPLACE' else None, reason=f'Auto-mutation due to {failure_rate:.1%} failure rate', applied_at=datetime.now(), success=True)
        self.mutation_history.append(mutation)
        return new_node

    def _find_replacement_node(self, node_id: str, graph: nx.DiGraph) -> Optional[Any]:
        """Find a replacement node for a failed node."""
        if node_id in self.alternative_routes and self.alternative_routes[node_id]:
            return self.alternative_routes[node_id][0]
        return None

    def _get_ready_nodes(self, graph: nx.DiGraph, completed_nodes: Set) -> List[Any]:
        """Get nodes ready for execution."""
        ready = []
        for node in graph.nodes():
            if node in completed_nodes:
                continue
            predecessors = set(graph.predecessors(node))
            if predecessors.issubset(completed_nodes):
                ready.append(node)
        return ready

    def _get_node_id(self, node: Any) -> str:
        """Get identifier for a node."""
        if hasattr(node, 'config') and hasattr(node.config, 'hop_id'):
            return node.config.hop_id
        return str(node)

    def record_node_attempt(self, node_id: str, success: bool) -> Any:
        """Track node performance and handle probation checks"""
        if node_id not in self.node_patterns:
            self.node_patterns[node_id] = NodeFailurePattern(node_id=node_id)
        if success:
            self.node_patterns[node_id].success_count += 1
        else:
            self.node_patterns[node_id].failure_count += 1
            self.node_patterns[node_id].last_failure = datetime.now()
        if node_id in self.probation_list:
            prob: Any = self.probation_list[node_id]
            prob['test_runs'] += 1
            if not success:
                prob['failures'] += 1
            if prob['test_runs'] >= 5 and prob['failures'] / prob['test_runs'] > 0.6:
                Logger.warning(f"PROBATION FAILED: {node_id} is unreliable (failure rate: {prob['failures'] / prob['test_runs']:.1%}). Reverting mutation.")
                for mutation in self.mutation_history:
                    if mutation.replacement_node == node_id:
                        mutation.success = False
                        Logger.info(f'L3: Reverted mutation {mutation.mutation_id}')
                        break
                del self.probation_list[node_id]
                for original, alternatives in list(self.alternative_routes.items()):
                    if node_id in alternatives:
                        alternatives.remove(node_id)
                        if not alternatives:
                            del self.alternative_routes[original]
            elif prob['test_runs'] >= 5 and prob['failures'] / prob['test_runs'] <= 0.3:
                Logger.info(f"PROBATION PASSED: {node_id} is reliable (failure rate: {prob['failures'] / prob['test_runs']:.1%})")
                del self.probation_list[node_id]

    def _record_node_success(self, node_id: str):
        """Record successful node execution."""
        self.record_node_attempt(node_id, success=True)
        Logger.debug(f'Node {node_id} success recorded')

    def _record_node_failure(self, node_id: str, reason: str):
        """Record node failure."""
        self.record_node_attempt(node_id, success=False)
        if node_id not in self.node_patterns:
            self.node_patterns[node_id] = NodeFailurePattern(node_id=node_id)
        pattern = self.node_patterns[node_id]
        pattern.failure_count += 1
        pattern.last_failure = datetime.now()
        pattern.failure_reasons.append(reason)
        if len(pattern.failure_reasons) > 10:
            pattern.failure_reasons = pattern.failure_reasons[-10:]
        Logger.warning(f'Node {node_id} failure recorded: {reason}')

    def _update_execution_time(self, node_id: str, execution_time: float):
        """Update average execution time for a node."""
        if node_id not in self.node_patterns:
            self.node_patterns[node_id] = NodeFailurePattern(node_id=node_id)
        pattern = self.node_patterns[node_id]
        total_executions = pattern.success_count + pattern.failure_count
        if total_executions > 0:
            pattern.avg_execution_time = (pattern.avg_execution_time * (total_executions - 1) + execution_time) / total_executions

    def get_failure_analysis(self) -> Dict[str, Any]:
        """Get analysis of node failures."""
        problematic_nodes: Any = [{'node_id': node_id, 'failure_rate': pattern.failure_rate, 'failure_count': pattern.failure_count, 'recent_reasons': pattern.failure_reasons[-3:]} for node_id, pattern in self.node_patterns.items() if pattern.is_problematic]
        total_mutations: Any = len(self.mutation_history)
        successful_mutations: Any = sum((1 for m in self.mutation_history if m.success))
        return {'problematic_nodes': problematic_nodes, 'total_mutations': total_mutations, 'successful_mutations': successful_mutations, 'mutation_success_rate': successful_mutations / total_mutations if total_mutations > 0 else 0.0, 'total_nodes_tracked': len(self.node_patterns)}

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

def create_self_recovering_orchestrator() -> SelfRecoveringOrchestratorAgent:
    """Factory function to create self-recovering orchestrator."""
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    return SelfRecoveringOrchestratorAgent()
