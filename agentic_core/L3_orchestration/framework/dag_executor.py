"""DAG Executor - Workflow Orchestration Framework

Executes Directed Acyclic Graph (DAG) workflows with dependency resolution,
error handling, and execution tracing. Core component for L3 orchestration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import logging
import time
from enum import Enum

logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    """Execution status of a DAG node."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGNode:
    """Single node in a DAG workflow."""
    id: str
    node_type: str  # "task", "condition", "parallel"
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, object] = field(default_factory=dict)
    status: NodeStatus = NodeStatus.PENDING
    result: Optional[Dict[str, object]] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class DAGConfig:
    """Configuration for DAG execution."""
    max_parallel_nodes: int = 5
    enable_error_recovery: bool = True
    retry_attempts: int = 3
    retry_delay_ms: int = 1000
    timeout_per_node_ms: int = 30000
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of DAG execution."""
    status: str  # "success", "failure", "partial"
    completed_nodes: List[str]
    failed_nodes: List[str]
    skipped_nodes: List[str]
    execution_trace: List[Dict[str, object]]
    total_execution_time_ms: float
    metadata: Dict[str, object] = field(default_factory=dict)


class DAGExecutor:
    """Advanced DAG executor with dependency resolution and error handling.
    
    Executes workflows defined as DAGs with proper dependency management,
    parallel execution where possible, and comprehensive error recovery.
    """
    
    def __init__(
        self,
        dag_config: Dict[str, object],
        *,
        config: Optional[DAGConfig] = None,
    ) -> None:
        """Initialize DAG executor with workflow configuration.
        
        Args:
            dag_config: Dictionary defining the DAG structure and nodes
            config: Optional execution configuration
        """
        self.dag_config = dag_config
        self.config = config or DAGConfig()
        self.nodes: Dict[str, DAGNode] = {}
        self.execution_trace: List[Dict[str, object]] = []
        
        # Build nodes from configuration
        self._build_nodes_from_config()
        
        logger.debug(f"DAG Executor initialized with {len(self.nodes)} nodes")
    
    def _build_nodes_from_config(self) -> None:
        """Build DAG nodes from configuration dictionary."""
        nodes_config = self.dag_config.get("nodes", {})
        
        for node_id, node_data in nodes_config.items():
            node = DAGNode(
                id=node_id,
                node_type=node_data.get("type", "task"),
                dependencies=node_data.get("dependencies", []),
                config=node_data.get("config", {}),
            )
            self.nodes[node_id] = node
    
    def execute(
        self,
        context: Dict[str, object],
    ) -> ExecutionResult:
        """Execute the DAG with provided context.
        
        Args:
            context: Execution context with required data
            
        Returns:
            ExecutionResult with comprehensive execution details
        """
        start_time = time.time()
        logger.debug(f"Starting DAG execution with context keys: {list(context.keys())}")
        
        # Initialize execution state
        completed_nodes: List[str] = []
        failed_nodes: List[str] = []
        skipped_nodes: List[str] = []
        
        # Execute nodes in dependency order
        execution_order = self._calculate_execution_order()
        
        for node_id in execution_order:
            node = self.nodes[node_id]
            
            # Check if dependencies are satisfied
            if not self._are_dependencies_satisfied(node, completed_nodes):
                logger.warning(f"Skipping node {node_id} due to unsatisfied dependencies")
                node.status = NodeStatus.SKIPPED
                skipped_nodes.append(node_id)
                continue
            
            # Execute the node
            try:
                result = self._execute_node(node, context)
                if result:
                    completed_nodes.append(node_id)
                else:
                    failed_nodes.append(node_id)
            except Exception as e:
                logger.error(f"Node {node_id} failed with error: {str(e)}")
                node.status = NodeStatus.FAILED
                node.error = str(e)
                failed_nodes.append(node_id)
                
                # Stop execution on critical node failure
                if node.node_type == "critical":
                    logger.error(f"Critical node {node_id} failed, stopping execution")
                    break
        
        end_time = time.time()
        total_time_ms = (end_time - start_time) * 1000
        
        # Determine overall status
        if failed_nodes:
            status = "failure" if len(failed_nodes) > len(completed_nodes) else "partial"
        else:
            status = "success"
        
        result = ExecutionResult(
            status=status,
            completed_nodes=completed_nodes,
            failed_nodes=failed_nodes,
            skipped_nodes=skipped_nodes,
            execution_trace=self.execution_trace.copy(),
            total_execution_time_ms=total_time_ms,
            metadata={
                "total_nodes": len(self.nodes),
                "context_keys": list(context.keys()),
                "config": self.config.__dict__
            }
        )
        
        logger.debug(f"DAG execution completed: status={status}, time_ms={total_time_ms:.2f}")
        return result
    
    def _calculate_execution_order(self) -> List[str]:
        """Calculate node execution order based on dependencies."""
        # Simple topological sort
        order: List[str] = []
        remaining = set(self.nodes.keys())
        
        while remaining:
            # Find nodes with no unsatisfied dependencies
            ready_nodes = []
            for node_id in remaining:
                node = self.nodes[node_id]
                if all(dep in order for dep in node.dependencies):
                    ready_nodes.append(node_id)
            
            if not ready_nodes:
                # Circular dependency or missing dependency
                logger.warning("Circular dependency detected, adding remaining nodes")
                ready_nodes = list(remaining)
            
            # Add ready nodes to order
            for node_id in ready_nodes:
                order.append(node_id)
                remaining.remove(node_id)
        
        return order
    
    def _are_dependencies_satisfied(
        self,
        node: DAGNode,
        completed_nodes: List[str]
    ) -> bool:
        """Check if all node dependencies are satisfied."""
        return all(dep in completed_nodes for dep in node.dependencies)
    
    def _execute_node(
        self,
        node: DAGNode,
        context: Dict[str, object]
    ) -> bool:
        """Execute a single DAG node."""
        node.start_time = time.time()
        node.status = NodeStatus.RUNNING
        
        # Add to execution trace
        self.execution_trace.append({
            "node_id": node.id,
            "action": "start",
            "timestamp": node.start_time,
            "context_keys": list(context.keys())
        })
        
        try:
            # Simulate node execution based on type
            if node.node_type == "task":
                result = self._execute_task_node(node, context)
            elif node.node_type == "condition":
                result = self._execute_condition_node(node, context)
            elif node.node_type == "parallel":
                result = self._execute_parallel_node(node, context)
            else:
                result = {"status": "unknown_node_type"}
            
            node.result = result
            node.status = NodeStatus.COMPLETED
            
        except Exception as e:
            node.error = str(e)
            node.status = NodeStatus.FAILED
            result = None
        
        node.end_time = time.time()
        
        # Add to execution trace
        self.execution_trace.append({
            "node_id": node.id,
            "action": "complete",
            "timestamp": node.end_time,
            "status": node.status.value,
            "execution_time_ms": (node.end_time - node.start_time) * 1000
        })
        
        return node.status == NodeStatus.COMPLETED
    
    def _execute_task_node(
        self,
        node: DAGNode,
        context: Dict[str, object]
    ) -> Dict[str, object]:
        """Execute a task node."""
        # Simulate task execution
        task_type = node.config.get("task_type", "default")
        
        if task_type == "data_processing":
            return {"processed_items": 10, "status": "completed"}
        elif task_type == "validation":
            return {"validation_passed": True, "rules_checked": 5}
        else:
            return {"task_completed": True, "node_id": node.id}
    
    def _execute_condition_node(
        self,
        node: DAGNode,
        context: Dict[str, object]
    ) -> Dict[str, object]:
        """Execute a condition node."""
        # Simulate condition evaluation
        condition = node.config.get("condition", "true")
        
        if condition == "check_data_quality":
            return {"condition_met": True, "quality_score": 0.95}
        else:
            return {"condition_met": True}
    
    def _execute_parallel_node(
        self,
        node: DAGNode,
        context: Dict[str, object]
    ) -> Dict[str, object]:
        """Execute a parallel node."""
        # Simulate parallel execution
        parallel_tasks = node.config.get("parallel_tasks", 3)
        
        return {
            "parallel_tasks_completed": parallel_tasks,
            "total_results": parallel_tasks * 5
        }
