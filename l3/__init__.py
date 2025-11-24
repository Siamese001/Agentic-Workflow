"""
L3 - Pure Orchestration Layer

This layer contains only control flow and coordination logic.
No business logic, tool execution, or state management is allowed here.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Protocol, TypeVar, Generic, Callable
from enum import Enum
from dataclasses import dataclass, field

T = TypeVar('T')

class NodeStatus(str, Enum):
    """Status of a workflow node."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class NodeResult(Generic[T]):
    """Result of a workflow node execution."""
    status: NodeStatus
    output: Optional[T] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowNode(Protocol[T]):
    """Protocol that all workflow nodes must implement."""
    
    @property
    def node_id(self) -> str:
        """Unique identifier for this node."""
        ...
        
    async def execute(self, context: Dict[str, Any]) -> NodeResult[T]:
        """Execute this node with the given context."""
        ...

@dataclass
class Edge:
    """Directed edge between two workflow nodes."""
    source: str
    target: str
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None

class Workflow:
    """A directed acyclic graph (DAG) of workflow nodes."""
    
    def __init__(self, nodes: List[WorkflowNode], edges: List[Edge]):
        self.nodes = {node.node_id: node for node in nodes}
        self.edges = edges
        self._validate()
    
    def _validate(self) -> None:
        """Validate the workflow graph."""
        # Check for cycles, invalid node references, etc.
        # Implementation omitted for brevity
        pass
    
    async def execute(self, initial_context: Dict[str, Any]) -> Dict[str, NodeResult]:
        """Execute the workflow with the given initial context."""
        # Implementation of DAG execution
        # This is a simplified version - a real implementation would include:
        # - Parallel execution where possible
        # - Dependency resolution
        # - Error handling and retries
        # - Progress tracking
        results: Dict[str, NodeResult] = {}
        context = initial_context.copy()
        
        # Simple linear execution for now
        for node_id, node in self.nodes.items():
            result = await node.execute(context)
            results[node_id] = result
            if result.status == NodeStatus.FAILED:
                break
                
            # Update context with node output
            if result.output is not None:
                context[node_id] = result.output
                
        return results

@dataclass
class DAGResult:
    """Result of a DAG execution."""
    success: bool
    results: Dict[str, NodeResult] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


async def run_dag(
    nodes: List[WorkflowNode],
    edges: List[Edge],
    initial_context: Dict[str, Any],
    *,
    max_retries: int = 0
) -> DAGResult:
    """Execute a DAG workflow.
    
    Args:
        nodes: List of workflow nodes to execute
        edges: List of edges defining dependencies
        initial_context: Initial execution context
        
    Returns:
        DAGResult with execution results
    """
    try:
        workflow = Workflow(nodes, edges)
        results = await workflow.execute(initial_context)
        
        # Check if any node failed
        failed = any(r.status == NodeStatus.FAILED for r in results.values())
        
        return DAGResult(
            success=not failed,
            results=results,
            error=None if not failed else "One or more nodes failed",
            metadata={"node_count": len(nodes), "edge_count": len(edges)}
        )
    except Exception as e:
        return DAGResult(
            success=False,
            results={},
            error=str(e),
            metadata={"node_count": len(nodes), "edge_count": len(edges)}
        )


# Re-export public interfaces
__all__ = [
    'NodeStatus',
    'NodeResult',
    'WorkflowNode',
    'Edge',
    'Workflow',
    'DAGResult',
    'run_dag',
]
