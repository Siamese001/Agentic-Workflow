#!/usr/bin/env python3
"""
DAG Node
Section 4: DAG Orchestration - Individual DAG node implementation
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

from .dag_types import NodeStatus, DependencyType, NodeType

logger = logging.getLogger(__name__)

@dataclass
class NodeConfiguration:
    """Configuration for a DAG node"""
    node_id: str
    node_type: NodeType
    executor: str
    timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay_seconds: int = 1
    required_resources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NodeResult:
    """Result of node execution"""
    node_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

class DAGNode:
    """Individual node in a DAG workflow"""
    
    def __init__(self, config: NodeConfiguration):
        self.config = config
        self.dependencies: List[str] = []
        self.dependency_types: Dict[str, DependencyType] = {}
        self.conditions: List[Callable[[Dict[str, Any]], bool]] = []
        self.pre_exec_hooks: List[Callable] = []
        self.post_exec_hooks: List[Callable] = []
        self.status = NodeStatus.PENDING
        self.result: Optional[NodeResult] = None
        self.execution_count = 0
        
    def add_dependency(self, node_id: str, dependency_type: DependencyType = DependencyType.DATA) -> 'DAGNode':
        """Add a dependency to this node"""
        if node_id not in self.dependencies:
            self.dependencies.append(node_id)
            self.dependency_types[node_id] = dependency_type
        return self
    
    def remove_dependency(self, node_id: str) -> 'DAGNode':
        """Remove a dependency from this node"""
        if node_id in self.dependencies:
            self.dependencies.remove(node_id)
            self.dependency_types.pop(node_id, None)
        return self
    
    def add_condition(self, condition: Callable[[Dict[str, Any]], bool]) -> 'DAGNode':
        """Add execution condition to this node"""
        self.conditions.append(condition)
        return self
    
    def add_pre_exec_hook(self, hook: Callable) -> 'DAGNode':
        """Add pre-execution hook"""
        self.pre_exec_hooks.append(hook)
        return self
    
    def add_post_exec_hook(self, hook: Callable) -> 'DAGNode':
        """Add post-execution hook"""
        self.post_exec_hooks.append(hook)
        return self
    
    def validate(self) -> bool:
        """Validate node configuration"""
        if not self.config.node_id:
            logger.error("Node ID cannot be empty")
            return False
        
        if not self.config.executor:
            logger.error(f"Node {self.config.node_id} executor cannot be empty")
            return False
        
        if self.config.timeout_seconds <= 0:
            logger.error(f"Node {self.config.node_id} timeout must be positive")
            return False
        
        if self.config.retry_attempts < 0:
            logger.error(f"Node {self.config.node_id} retry attempts cannot be negative")
            return False
        
        return True
    
    def can_execute(self, context: Dict[str, Any]) -> bool:
        """Check if node can execute based on conditions"""
        for condition in self.conditions:
            if not condition(context):
                return False
        return True
    
    def execute(self, input_data: Dict[str, Any]) -> NodeResult:
        """Execute the node with given input data"""
        self.execution_count += 1
        start_time = datetime.now()
        
        try:
            # Execute pre-execution hooks
            for hook in self.pre_exec_hooks:
                hook(self, input_data)
            
            # Execute the node
            result_data = self._execute_internal(input_data)
            
            # Create successful result
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self.result = NodeResult(
                node_id=self.config.node_id,
                success=True,
                data=result_data,
                execution_time=execution_time,
                timestamp=end_time
            )
            
            # Execute post-execution hooks
            for hook in self.post_exec_hooks:
                hook(self, self.result)
            
            return self.result
            
        except Exception as e:
            # Create failed result
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self.result = NodeResult(
                node_id=self.config.node_id,
                success=False,
                error_message=str(e),
                execution_time=execution_time,
                timestamp=end_time
            )
            
            logger.error(f"Node {self.config.node_id} execution failed: {e}")
            return self.result
    
    def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal execution logic - to be overridden by specific node types"""
        # Default implementation - just return input data
        return {
            'node_id': self.config.node_id,
            'node_type': self.config.node_type,
            'input_data': input_data,
            'execution_count': self.execution_count
        }
    
    def reset(self) -> None:
        """Reset node state"""
        self.status = NodeStatus.PENDING
        self.result = None
        self.execution_count = 0
    
    def get_dependency_summary(self) -> Dict[str, Any]:
        """Get summary of node dependencies"""
        return {
            'node_id': self.config.node_id,
            'dependencies': self.dependencies.copy(),
            'dependency_types': self.dependency_types.copy(),
            'dependency_count': len(self.dependencies)
        }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of node execution"""
        if self.result:
            return {
                'node_id': self.config.node_id,
                'status': 'completed' if self.result.success else 'failed',
                'execution_count': self.execution_count,
                'last_execution_time': self.result.execution_time,
                'last_execution_timestamp': self.result.timestamp.isoformat()
            }
        else:
            return {
                'node_id': self.config.node_id,
                'status': 'not_executed',
                'execution_count': 0
            }

class TaskNode(DAGNode):
    """Task node for executing specific tasks"""
    
    def __init__(self, config: NodeConfiguration, task_func: Callable):
        super().__init__(config)
        self.task_func = task_func
    
    def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task function"""
        if not callable(self.task_func):
            raise ValueError(f"Task function for node {self.config.node_id} is not callable")
        
        return self.task_func(input_data)

class DecisionNode(DAGNode):
    """Decision node for conditional workflow branching"""
    
    def __init__(self, config: NodeConfiguration, decision_func: Callable[[Dict[str, Any]], str]):
        super().__init__(config)
        self.decision_func = decision_func
    
    def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute decision function"""
        if not callable(self.decision_func):
            raise ValueError(f"Decision function for node {self.config.node_id} is not callable")
        
        decision = self.decision_func(input_data)
        return {
            'node_id': self.config.node_id,
            'decision': decision,
            'input_data': input_data
        }

class ParallelNode(DAGNode):
    """Parallel node for executing multiple tasks concurrently"""
    
    def __init__(self, config: NodeConfiguration, task_funcs: List[Callable]):
        super().__init__(config)
        self.task_funcs = task_funcs
    
    def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tasks in parallel"""
        if not self.task_funcs:
            raise ValueError(f"No task functions provided for parallel node {self.config.node_id}")
        
        async def execute_parallel():
            tasks = []
            for i, func in enumerate(self.task_funcs):
                if callable(func):
                    task = asyncio.create_task(asyncio.to_thread(func, input_data))
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        
        # Run async execution
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(execute_parallel())
        finally:
            loop.close()
        
        return {
            'node_id': self.config.node_id,
            'parallel_results': results,
            'task_count': len(self.task_funcs)
        }

class ConditionNode(DAGNode):
    """Condition node for evaluating complex conditions"""
    
    def __init__(self, config: NodeConfiguration, condition_func: Callable[[Dict[str, Any]], bool]):
        super().__init__(config)
        self.condition_func = condition_func
    
    def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate condition"""
        if not callable(self.condition_func):
            raise ValueError(f"Condition function for node {self.config.node_id} is not callable")
        
        condition_result = self.condition_func(input_data)
        return {
            'node_id': self.config.node_id,
            'condition_met': condition_result,
            'input_data': input_data
        }

# Node factory for creating different node types
class NodeFactory:
    """Factory for creating DAG nodes"""
    
    @staticmethod
    def create_task_node(node_id: str, executor: str, task_func: Callable, **kwargs) -> TaskNode:
        """Create a task node"""
        config = NodeConfiguration(
            node_id=node_id,
            node_type=NodeType.TASK,
            executor=executor,
            **kwargs
        )
        return TaskNode(config, task_func)
    
    @staticmethod
    def create_decision_node(node_id: str, executor: str, decision_func: Callable, **kwargs) -> DecisionNode:
        """Create a decision node"""
        config = NodeConfiguration(
            node_id=node_id,
            node_type=NodeType.DECISION,
            executor=executor,
            **kwargs
        )
        return DecisionNode(config, decision_func)
    
    @staticmethod
    def create_parallel_node(node_id: str, executor: str, task_funcs: List[Callable], **kwargs) -> ParallelNode:
        """Create a parallel node"""
        config = NodeConfiguration(
            node_id=node_id,
            node_type=NodeType.PARALLEL,
            executor=executor,
            **kwargs
        )
        return ParallelNode(config, task_funcs)
    
    @staticmethod
    def create_condition_node(node_id: str, executor: str, condition_func: Callable, **kwargs) -> ConditionNode:
        """Create a condition node"""
        config = NodeConfiguration(
            node_id=node_id,
            node_type=NodeType.CONDITION,
            executor=executor,
            **kwargs
        )
        return ConditionNode(config, condition_func)

# Re-export components
__all__ = [
    'DAGNode', 'TaskNode', 'DecisionNode', 'ParallelNode', 'ConditionNode',
    'NodeFactory', 'NodeConfiguration', 'NodeResult', 'DependencyType', 'NodeType'
]
