"""
DAG Executor Framework Module
LEVEL 5 - Core framework for executing Directed Acyclic Graphs in agentic operations
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
from enum import Enum

class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class ExecutionMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"

@dataclass
class ExecutionNode:
    """Represents an execution node in the DAG framework"""
    node_id: str
    function: Callable
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class DAGExecutionConfig:
    """Configuration for DAG execution"""
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    max_parallel_nodes: int = 5
    timeout_seconds: float = 300.0
    enable_retry: bool = True
    enable_logging: bool = True

@dataclass
class DAGExecutionSummary:
    """Summary of DAG execution results"""
    execution_id: str
    total_nodes: int
    successful_nodes: int
    failed_nodes: int
    skipped_nodes: int
    total_execution_time: float
    success_rate: float

class DAGExecutor:
    """Core framework for executing DAGs with various strategies"""

    def __init__(self, config: DAGExecutionConfig = None):
        self.config = config or DAGExecutionConfig()
        self.logger = logging.getLogger(__name__)
        self.nodes: Dict[str, ExecutionNode] = {}
        self.execution_history: List[DAGExecutionSummary] = []

    def add_node(
        self,
        node_id: str,
        function: Callable,
        dependencies: List[str] = None,
        parameters: Dict[str, Any] = None,
        max_retries: int = 3
    ) -> None:
        """Add a node to the DAG"""
        if dependencies is None:
            dependencies = []
        if parameters is None:
            parameters = {}

        node = ExecutionNode(
            node_id=node_id,
            function=function,
            dependencies=dependencies,
            parameters=parameters,
            max_retries=max_retries
        )

        self.nodes[node_id] = node
        if self.config.enable_logging:
            self.logger.info(f"Added node {node_id} with {len(dependencies)} dependencies")

    async def execute_dag(
        self,
        input_data: Dict[str, Any],
        execution_mode: ExecutionMode = None
    ) -> DAGExecutionSummary:
        """Execute the DAG with specified mode"""
        mode = execution_mode or self.config.execution_mode
        start_time = datetime.utcnow()
        execution_id = f"dag_exec_{int(start_time.timestamp())}"

        try:
            # Validate DAG structure
            self._validate_dag_structure()

            # Reset node statuses
            self._reset_node_statuses()

            # Execute based on mode
            if mode == ExecutionMode.SEQUENTIAL:
                await self._execute_sequential(input_data)
            elif mode == ExecutionMode.PARALLEL:
                await self._execute_parallel(input_data)
            else:  # HYBRID
                await self._execute_hybrid(input_data)

            # Calculate execution summary
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            summary = self._calculate_summary(execution_id, execution_time)

            self.execution_history.append(summary)
            return summary

        except Exception as e:
            self.logger.error(f"DAG execution failed: {str(e)}")
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            summary = DAGExecutionSummary(
                execution_id=execution_id,
                total_nodes=len(self.nodes),
                successful_nodes=0,
                failed_nodes=len(self.nodes),
                skipped_nodes=0,
                total_execution_time=execution_time,
                success_rate=0.0
            )
            self.execution_history.append(summary)
            return summary

    async def _execute_sequential(self, input_data: Dict[str, Any]) -> None:
        """Execute nodes sequentially in dependency order"""
        execution_order = self._get_execution_order()
        results = {}

        for node_id in execution_order:
            node = self.nodes[node_id]
            await self._execute_single_node(node, results, input_data)
            results[node_id] = node.result

    async def _execute_parallel(self, input_data: Dict[str, Any]) -> None:
        """Execute nodes in parallel where possible"""
        execution_batches = self._get_parallel_batches()
        results = {}

        for batch in execution_batches:
            # Execute all nodes in batch in parallel
            tasks = []
            for node_id in batch:
                node = self.nodes[node_id]
                task = self._execute_single_node(node, results, input_data)
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)

            # Update results
            for node_id in batch:
                results[node_id] = self.nodes[node_id].result

    async def _execute_hybrid(self, input_data: Dict[str, Any]) -> None:
        """Execute nodes with hybrid strategy (parallel for independent, sequential for dependent)"""
        # For simplicity, use sequential execution for hybrid mode
        await self._execute_sequential(input_data)

    async def _execute_single_node(
        self,
        node: ExecutionNode,
        results: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> None:
        """Execute a single node with retry logic"""
        for attempt in range(node.max_retries + 1):
            try:
                node.status = NodeStatus.RUNNING
                node_start_time = datetime.utcnow()

                # Prepare node input
                node_input = self._prepare_node_input(node, results, input_data)

                # Execute node function
                if asyncio.iscoroutinefunction(node.function):
                    node.result = await node.function(**node_input)
                else:
                    node.result = node.function(**node_input)

                node.execution_time = (datetime.utcnow() - node_start_time).total_seconds()
                node.status = NodeStatus.COMPLETED

                if self.config.enable_logging:
                    self.logger.info(f"Node {node.node_id} completed successfully")
                break

            except Exception as e:
                node.error = str(e)
                node.retry_count = attempt + 1

                if attempt < node.max_retries:
                    if self.config.enable_logging:
                        self.logger.warning(f"Node {node.node_id} failed, retrying ({attempt + 1}/{node.max_retries})")
                    await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
                else:
                    node.status = NodeStatus.FAILED
                    if self.config.enable_logging:
                        self.logger.error(f"Node {node.node_id} failed after {node.max_retries} retries: {str(e)}")
                    raise e

    def _validate_dag_structure(self) -> None:
        """Validate DAG for circular dependencies"""
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            if node_id in self.nodes:
                for dep in self.nodes[node_id].dependencies:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if has_cycle(node_id):
                raise ValueError(f"Circular dependency detected involving node {node_id}")

    def _get_execution_order(self) -> List[str]:
        """Get topological order for sequential execution"""
        in_degree = {node_id: 0 for node_id in self.nodes}

        # Calculate in-degrees
        for node_id, node in self.nodes.items():
            for dep in node.dependencies:
                if dep in in_degree:
                    in_degree[node_id] += 1

        # Topological sort
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        execution_order = []

        while queue:
            current = queue.pop(0)
            execution_order.append(current)

            # Update in-degrees of dependent nodes
            for node_id, node in self.nodes.items():
                if current in node.dependencies:
                    in_degree[node_id] -= 1
                    if in_degree[node_id] == 0:
                        queue.append(node_id)

        return execution_order

    def _get_parallel_batches(self) -> List[List[str]]:
        """Get batches of nodes that can be executed in parallel"""
        execution_order = self._get_execution_order()
        batches = []
        current_batch = []

        for node_id in execution_order:
            node = self.nodes[node_id]

            # Check if all dependencies are in previous batches
            can_execute_now = all(
                dep not in current_batch for dep in node.dependencies
            )

            if can_execute_now and len(current_batch) < self.config.max_parallel_nodes:
                current_batch.append(node_id)
            else:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [node_id]

        if current_batch:
            batches.append(current_batch)

        return batches

    def _prepare_node_input(
        self,
        node: ExecutionNode,
        results: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare input data for node execution"""
        node_input = {**input_data, **node.parameters}

        # Add results from dependency nodes
        for dep in node.dependencies:
            if dep in results:
                node_input[f"dep_{dep}"] = results[dep]

        return node_input

    def _reset_node_statuses(self) -> None:
        """Reset all node statuses to pending"""
        for node in self.nodes.values():
            node.status = NodeStatus.PENDING
            node.result = None
            node.error = None
            node.retry_count = 0
            node.execution_time = 0.0

    def _calculate_summary(self, execution_id: str, execution_time: float) -> DAGExecutionSummary:
        """Calculate execution summary"""
        total_nodes = len(self.nodes)
        successful_nodes = sum(1 for node in self.nodes.values() if node.status == NodeStatus.COMPLETED)
        failed_nodes = sum(1 for node in self.nodes.values() if node.status == NodeStatus.FAILED)
        skipped_nodes = sum(1 for node in self.nodes.values() if node.status == NodeStatus.SKIPPED)

        success_rate = successful_nodes / total_nodes if total_nodes > 0 else 0.0

        return DAGExecutionSummary(
            execution_id=execution_id,
            total_nodes=total_nodes,
            successful_nodes=successful_nodes,
            failed_nodes=failed_nodes,
            skipped_nodes=skipped_nodes,
            total_execution_time=execution_time,
            success_rate=success_rate
        )

    def get_node_status(self, node_id: str) -> Optional[NodeStatus]:
        """Get status of a specific node"""
        if node_id in self.nodes:
            return self.nodes[node_id].status
        return None

    def get_execution_history(self) -> List[DAGExecutionSummary]:
        """Get history of all executions"""
        return self.execution_history.copy()

    def clear_dag(self) -> None:
        """Clear all nodes from the DAG"""
        self.nodes.clear()
        if self.config.enable_logging:
            self.logger.info("Cleared all nodes from DAG")

__all__ = [
    "DAGExecutor", "ExecutionNode", "DAGExecutionConfig",
    "DAGExecutionSummary", "NodeStatus", "ExecutionMode"
]
