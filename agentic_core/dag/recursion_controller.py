#!/usr/bin/env python3
"""
Recursion Controller
Section 4: DAG Orchestration - Controls recursive DAG execution and prevents infinite loops
"""

from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

from .dag_engine import DAGEngine, ExecutionState
from .dag_types import NodeStatus

logger = logging.getLogger(__name__)

class RecursionPolicy(str, Enum):
    """Recursion policy enumeration"""
    DISABLED = "disabled"
    LIMITED = "limited"
    UNLIMITED = "unlimited"
    CONDITIONAL = "conditional"

class RecursionState(str, Enum):
    """Recursion execution state"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"

@dataclass
class RecursionConfig:
    """Configuration for recursion control"""
    max_depth: int = 10
    max_iterations: int = 100
    max_execution_time: int = 3600  # seconds
    policy: RecursionPolicy = RecursionPolicy.LIMITED
    memory_limit_mb: int = 1024
    allow_parallel_recursion: bool = False

@dataclass
class RecursionMetrics:
    """Metrics for recursion execution"""
    current_depth: int = 0
    total_iterations: int = 0
    execution_time: float = 0.0
    memory_usage_mb: float = 0.0
    nodes_executed: int = 0
    recursion_calls: int = 0

class RecursionController:
    """Controls recursive DAG execution and prevents infinite loops"""
    
    def __init__(self, config: RecursionConfig):
        self.config = config
        self.dag_engine: Optional[DAGEngine] = None
        self.execution_stack: List[str] = []
        self.visited_dags: Set[str] = set()
        self.recursion_history: List[Dict[str, Any]] = []
        self.metrics = RecursionMetrics()
        self.start_time: Optional[datetime] = None
        self.state = RecursionState.NOT_STARTED
        
    def set_dag_engine(self, dag_engine: DAGEngine) -> None:
        """Set the DAG engine for recursion control"""
        self.dag_engine = dag_engine
    
    def can_execute_recursive(self, dag_id: str, input_data: Dict[str, Any]) -> bool:
        """Check if recursive execution is allowed"""
        if self.config.policy == RecursionPolicy.DISABLED:
            return False
        
        # Check depth limit
        if self.metrics.current_depth >= self.config.max_depth:
            logger.warning(f"Recursion depth limit exceeded: {self.metrics.current_depth} >= {self.config.max_depth}")
            return False
        
        # Check iteration limit
        if self.metrics.total_iterations >= self.config.max_iterations:
            logger.warning(f"Recursion iteration limit exceeded: {self.metrics.total_iterations} >= {self.config.max_iterations}")
            return False
        
        # Check execution time limit
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            if elapsed >= self.config.max_execution_time:
                logger.warning(f"Recursion execution time limit exceeded: {elapsed} >= {self.config.max_execution_time}")
                return False
        
        # Check for circular DAG dependencies
        if dag_id in self.execution_stack:
            logger.warning(f"Circular DAG dependency detected: {dag_id} in {self.execution_stack}")
            return False
        
        # Check memory usage (simplified check)
        if self.metrics.memory_usage_mb >= self.config.memory_limit_mb:
            logger.warning(f"Recursion memory limit exceeded: {self.metrics.memory_usage_mb} >= {self.config.memory_limit_mb}")
            return False
        
        return True
    
    def execute_recursive(self, dag_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a DAG recursively with control"""
        if not self.dag_engine:
            raise ValueError("DAG engine not set")
        
        self.state = RecursionState.IN_PROGRESS
        if not self.start_time:
            self.start_time = datetime.now()
        
        # Add to execution stack
        self.execution_stack.append(dag_id)
        self.metrics.current_depth = len(self.execution_stack)
        self.metrics.recursion_calls += 1
        
        try:
            # Check if recursion is allowed
            if not self.can_execute_recursive(dag_id, input_data):
                self.state = RecursionState.TERMINATED
                return {
                    'success': False,
                    'error': 'Recursion execution terminated by policy',
                    'metrics': self.get_metrics_dict()
                }
            
            # Execute the DAG
            logger.info(f"Executing DAG {dag_id} recursively at depth {self.metrics.current_depth}")
            result = self.dag_engine.execute_dag(dag_id, input_data)
            
            # Update metrics
            self.metrics.total_iterations += 1
            self.metrics.nodes_executed += len(result.completed_nodes) + len(result.failed_nodes)
            
            # Record execution in history
            self.recursion_history.append({
                'dag_id': dag_id,
                'depth': self.metrics.current_depth,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
            # Check for recursive calls in result
            recursive_calls = self._extract_recursive_calls(result)
            if recursive_calls and self.config.policy != RecursionPolicy.DISABLED:
                recursive_results = []
                for call in recursive_calls:
                    call_result = self.execute_recursive(call['dag_id'], call.get('input_data', {}))
                    recursive_results.append(call_result)
                
                return {
                    'success': result.status == ExecutionState.COMPLETED,
                    'primary_result': result,
                    'recursive_results': recursive_results,
                    'metrics': self.get_metrics_dict()
                }
            
            return {
                'success': result.status == ExecutionState.COMPLETED,
                'result': result,
                'metrics': self.get_metrics_dict()
            }
            
        except Exception as e:
            logger.error(f"Recursive execution failed for DAG {dag_id}: {e}")
            self.state = RecursionState.FAILED
            return {
                'success': False,
                'error': str(e),
                'metrics': self.get_metrics_dict()
            }
        
        finally:
            # Remove from execution stack
            if self.execution_stack and self.execution_stack[-1] == dag_id:
                self.execution_stack.pop()
                self.metrics.current_depth = len(self.execution_stack)
            
            # Update state if stack is empty
            if not self.execution_stack:
                self.state = RecursionState.COMPLETED
    
    def terminate_execution(self) -> bool:
        """Terminate current recursive execution"""
        if self.state == RecursionState.IN_PROGRESS:
            self.state = RecursionState.TERMINATED
            if self.dag_engine:
                # Cancel all current executions
                for dag_id in list(self.dag_engine.current_executions.keys()):
                    self.dag_engine.cancel_execution(dag_id)
            return True
        return False
    
    def reset(self) -> None:
        """Reset recursion controller state"""
        self.execution_stack.clear()
        self.visited_dags.clear()
        self.recursion_history.clear()
        self.metrics = RecursionMetrics()
        self.start_time = None
        self.state = RecursionState.NOT_STARTED
    
    def get_metrics(self) -> RecursionMetrics:
        """Get current recursion metrics"""
        # Update execution time
        if self.start_time:
            self.metrics.execution_time = (datetime.now() - self.start_time).total_seconds()
        
        return self.metrics
    
    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get recursion metrics as dictionary"""
        metrics = self.get_metrics()
        return {
            'current_depth': metrics.current_depth,
            'total_iterations': metrics.total_iterations,
            'execution_time': metrics.execution_time,
            'memory_usage_mb': metrics.memory_usage_mb,
            'nodes_executed': metrics.nodes_executed,
            'recursion_calls': metrics.recursion_calls,
            'state': self.state,
            'execution_stack': self.execution_stack.copy()
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get recursion execution history"""
        return self.recursion_history.copy()
    
    def _extract_recursive_calls(self, result) -> List[Dict[str, Any]]:
        """Extract recursive DAG calls from execution result"""
        recursive_calls = []
        
        # Check result data for recursive call indicators
        if hasattr(result, 'results') and result.results:
            for key, value in result.results.items():
                if isinstance(value, dict) and 'recursive_dag_call' in value:
                    recursive_calls.append({
                        'dag_id': value.get('dag_id'),
                        'input_data': value.get('input_data', {})
                    })
        
        # Check for patterns indicating recursion
        if hasattr(result, 'results') and result.results:
            for key, value in result.results.items():
                if isinstance(value, str) and value.startswith('execute_dag:'):
                    parts = value.split(':', 2)
                    if len(parts) >= 2:
                        recursive_calls.append({
                            'dag_id': parts[1],
                            'input_data': {}
                        })
        
        return recursive_calls

class RecursionGuard:
    """Guard for preventing infinite recursion in specific contexts"""
    
    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
        self.call_stack: List[str] = []
        self.call_counts: Dict[str, int] = {}
    
    def enter_recursive_call(self, context: str) -> bool:
        """Enter a recursive call context"""
        # Check depth
        if len(self.call_stack) >= self.max_depth:
            return False
        
        # Check call frequency
        call_count = self.call_counts.get(context, 0)
        if call_count > self.max_depth * 2:  # Heuristic for potential infinite loops
            return False
        
        self.call_stack.append(context)
        self.call_counts[context] = call_count + 1
        return True
    
    def exit_recursive_call(self, context: str) -> None:
        """Exit a recursive call context"""
        if self.call_stack and self.call_stack[-1] == context:
            self.call_stack.pop()
    
    def reset(self) -> None:
        """Reset guard state"""
        self.call_stack.clear()
        self.call_counts.clear()

# Utility functions for recursion control
def create_recursion_controller(max_depth: int = 10, max_iterations: int = 100) -> RecursionController:
    """Create a recursion controller with default configuration"""
    config = RecursionConfig(
        max_depth=max_depth,
        max_iterations=max_iterations,
        policy=RecursionPolicy.LIMITED
    )
    return RecursionController(config)

def safe_recursive_execute(controller: RecursionController, dag_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Safely execute a DAG recursively with error handling"""
    try:
        return controller.execute_recursive(dag_id, input_data)
    except Exception as e:
        logger.error(f"Safe recursive execution failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'metrics': controller.get_metrics_dict()
        }

# Re-export components
__all__ = [
    'RecursionController', 'RecursionConfig', 'RecursionMetrics',
    'RecursionGuard', 'RecursionPolicy', 'RecursionState',
    'create_recursion_controller', 'safe_recursive_execute'
]
