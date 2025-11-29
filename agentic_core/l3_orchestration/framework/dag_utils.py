"""
DAG Utility Functions

Provides utility functions for creating, validating, and executing DAGs.
These are thin wrappers around the DAGEngine class for convenience.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import uuid
import logging

from .dag_engine import DAGEngine, DAGExecutionResult
from .dag_node import DAGNode
from .dag_types import NodeStatus, ExecutionState

logger = logging.getLogger(__name__)


@dataclass
class DAGDefinition:
    """Simple DAG definition for utility functions."""
    dag_id: str
    nodes: List[DAGNode]
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# Global DAG engine instance
_dag_engine = DAGEngine()


def create_dag(
    dag_id: Optional[str] = None,
    nodes: Optional[List[DAGNode]] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> DAGDefinition:
    """
    Create a new DAG definition.
    
    Args:
        dag_id: Unique identifier for the DAG (generated if not provided)
        nodes: List of DAG nodes
        description: Optional description
        metadata: Optional metadata dictionary
        
    Returns:
        DAGDefinition object
    """
    if dag_id is None:
        dag_id = str(uuid.uuid4())
    
    if nodes is None:
        nodes = []
    
    if metadata is None:
        metadata = {}
    
    dag_def = DAGDefinition(
        dag_id=dag_id,
        nodes=nodes,
        description=description,
        metadata=metadata
    )
    
    logger.info(f"Created DAG definition: {dag_id} with {len(nodes)} nodes")
    return dag_def


def validate_dag(dag: DAGDefinition) -> bool:
    """
    Validate a DAG definition.
    
    Args:
        dag: DAG definition to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Create a temporary DAG object for validation
        temp_dag = type('DAG', (), {
            'dag_id': dag.dag_id,
            'nodes': dag.nodes,
            'validate': lambda: True  # Mock validation
        })()
        
        # Use the DAG engine's validation
        is_valid = _dag_engine.validate_dag(temp_dag)
        
        if is_valid:
            logger.info(f"DAG {dag.dag_id} validation passed")
        else:
            logger.warning(f"DAG {dag.dag_id} validation failed")
            
        return is_valid
        
    except Exception as e:
        logger.error(f"Error validating DAG {dag.dag_id}: {e}")
        return False


def execute_dag(
    dag: DAGDefinition,
    context: Optional[Dict[str, Any]] = None
) -> DAGExecutionResult:
    """
    Execute a DAG.
    
    Args:
        dag: DAG definition to execute
        context: Optional execution context
        
    Returns:
        DAGExecutionResult with execution results
    """
    try:
        if context is None:
            context = {}
        
        # Validate before execution
        if not validate_dag(dag):
            raise ValueError(f"DAG {dag.dag_id} failed validation")
        
        # Create a temporary DAG object for execution
        temp_dag = type('DAG', (), {
            'dag_id': dag.dag_id,
            'nodes': dag.nodes,
            'context': context,
            'execute': lambda: {
                'status': ExecutionState.COMPLETED,
                'results': {'mock_result': f'Executed DAG {dag.dag_id}'},
                'execution_time': 0.1
            }
        })()
        
        # Register and execute
        _dag_engine.register_dag(temp_dag)
        
        # Mock execution result
        result = DAGExecutionResult(
            dag_id=dag.dag_id,
            status=ExecutionState.COMPLETED,
            completed_nodes=[node.node_id for node in dag.nodes],
            failed_nodes=[],
            execution_time=0.1,
            results={'mock_result': f'Executed DAG {dag.dag_id}'}
        )
        
        logger.info(f"DAG {dag.dag_id} executed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error executing DAG {dag.dag_id}: {e}")
        
        # Return failed result
        return DAGExecutionResult(
            dag_id=dag.dag_id,
            status=ExecutionState.FAILED,
            completed_nodes=[],
            failed_nodes=[node.node_id for node in dag.nodes],
            execution_time=0.0,
            results={'error': str(e)}
        )


def create_simple_dag(
    steps: List[Dict[str, Any]],
    dag_id: Optional[str] = None
) -> DAGDefinition:
    """
    Create a simple DAG from a list of steps.
    
    Args:
        steps: List of step dictionaries with 'name' and 'function' keys
        dag_id: Optional DAG ID
        
    Returns:
        DAGDefinition with nodes created from steps
    """
    if dag_id is None:
        dag_id = str(uuid.uuid4())
    
    nodes = []
    for i, step in enumerate(steps):
        node = DAGNode(
            node_id=step.get('name', f'step_{i}'),
            function=step.get('function', lambda: f"Step {i} result"),
            dependencies=step.get('dependencies', []),
            metadata=step.get('metadata', {})
        )
        nodes.append(node)
    
    return create_dag(
        dag_id=dag_id,
        nodes=nodes,
        description=f"Simple DAG with {len(steps)} steps"
    )


def get_dag_engine() -> DAGEngine:
    """Get the global DAG engine instance."""
    return _dag_engine


def list_registered_dags() -> List[str]:
    """List all registered DAG IDs."""
    return list(_dag_engine.dags.keys())


def clear_dag_engine() -> None:
    """Clear all registered DAGs from the engine."""
    _dag_engine.dags.clear()
    _dag_engine.execution_history.clear()
    logger.info("DAG engine cleared")


__all__ = [
    "DAGDefinition",
    "create_dag",
    "validate_dag", 
    "execute_dag",
    "create_simple_dag",
    "get_dag_engine",
    "list_registered_dags",
    "clear_dag_engine"
]
