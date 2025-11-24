"""
L3 - Pure Orchestration Layer

This layer contains only control flow and coordination logic.
No business logic, tool execution, or state management is allowed here.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Protocol, TypeVar, Generic, Callable
from enum import Enum
from dataclasses import dataclass, field
from l3.workflow_graph import run_workflow_graph  # Added import
import asyncio

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


def run_dag(ctx, plans, *, max_retries: int = 0):
    """Execute workflow DAG with the given context and plans.
    
    This is a synchronous wrapper around run_workflow_graph that matches
    the expected test interface.
    
    Args:
        ctx: ExecutionContext
        plans: WorkflowPlanBundle
        max_retries: Maximum number of retries (currently unused)
        
    Returns:
        DAGResult-like object with l2_results and other fields
    """
    # Run the async workflow graph
    result = asyncio.run(run_workflow_graph(plans, ctx))
    
    # Wrap the result in a DAGResult-like object for backward compatibility
    from dataclasses import dataclass
    
    @dataclass
    class DAGResultCompat:
        l2_results: Any
        final_state_patch: Dict[str, Any]
        correction_signals: List[Any]
        safety_passed: bool
        corrected: bool
        corrections: List[Any]
        
        def __getattr__(self, name):
            # Allow accessing l2_results fields directly
            if hasattr(self.l2_results, name):
                return getattr(self.l2_results, name)
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    # Extract correction signals and safety status
    correction_signals = []
    safety_passed = True
    if hasattr(result, 'safety') and result.safety:
        from l5 import safety_gate
        safety_passed = safety_gate(result.safety)
    
    # Build final state patch (only include keys expected by tests)
    final_state_patch = {}
    if hasattr(result, 'strategy') and result.strategy:
        final_state_patch['strategy_text'] = str(result.strategy)
    if hasattr(result, 'rag') and result.rag:
        final_state_patch['rag_evidence'] = getattr(result.rag, 'evidence', [])
    if hasattr(result, 'drafting') and result.drafting:
        final_state_patch['drafted_sections'] = getattr(result.drafting, 'sections', [])
    if hasattr(result, 'qa') and result.qa:
        final_state_patch['qa_findings'] = getattr(result.qa, 'findings', [])
    if hasattr(result, 'safety') and result.safety:
        final_state_patch['safety_findings'] = getattr(result.safety, 'findings', [])
    
    # Add correction signals and metadata to the patch
    final_state_patch['correction_signals'] = correction_signals
    final_state_patch['ais_error_events'] = []  # Placeholder for AIS error events
    final_state_patch['safety_passed'] = safety_passed
    
    return DAGResultCompat(
        l2_results=result,
        final_state_patch=final_state_patch,
        correction_signals=correction_signals,
        safety_passed=safety_passed,
        corrected=False,
        corrections=[],
    )


async def run_dag_async(
    nodes: List[WorkflowNode],
    edges: List[Edge],
    initial_context: Dict[str, Any],
    *,
    max_retries: int = 0
) -> DAGResult:
    """Execute a DAG workflow asynchronously.
    
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
    'run_workflow_graph',
]
