#!/usr/bin/env python3
"""
DAG Engine
Section 4: DAG Orchestration - Core DAG execution engine
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import time
import logging

from .dag_types import NodeStatus, ExecutionState

logger = logging.getLogger(__name__)

@dataclass
class DAGExecutionResult:
    """Result of DAG execution"""
    dag_id: str
    status: ExecutionState
    completed_nodes: List[str]
    failed_nodes: List[str]
    execution_time: float
    results: Dict[str, Any] = field(default_factory=dict)

class DAGEngine:
    """Core DAG execution engine for workflow orchestration"""
    
    def __init__(self):
        self.dags: Dict[str, 'DAG'] = {}
        self.execution_history: List[DAGExecutionResult] = []
        self.current_executions: Dict[str, 'DAGExecution'] = {}
        
    def register_dag(self, dag: 'DAG') -> bool:
        """Register a DAG for execution"""
        try:
            if self.validate_dag(dag):
                self.dags[dag.dag_id] = dag
                logger.info(f"DAG {dag.dag_id} registered successfully")
                return True
            else:
                logger.error(f"DAG {dag.dag_id} validation failed")
                return False
        except Exception as e:
            logger.error(f"Failed to register DAG {dag.dag_id}: {e}")
            return False
    
    def validate_dag(self, dag: 'DAG') -> bool:
        """Validate DAG structure and dependencies"""
        # Check for circular dependencies
        if self._has_circular_dependencies(dag):
            return False
        
        # Check for orphaned nodes
        if self._has_orphaned_nodes(dag):
            return False
        
        # Validate node configurations
        for node in dag.nodes.values():
            if not node.validate():
                return False
        
        return True
    
    def execute_dag(self, dag_id: str, input_data: Optional[Dict[str, Any]] = None) -> DAGExecutionResult:
        """Execute a DAG with given input data"""
        if dag_id not in self.dags:
            raise ValueError(f"DAG {dag_id} not registered")
        
        dag = self.dags[dag_id]
        execution = DAGExecution(dag, input_data or {})
        self.current_executions[dag_id] = execution
        
        try:
            result = execution.run()
            self.execution_history.append(result)
            return result
        except Exception as e:
            logger.error(f"DAG execution failed: {e}")
            result = execution.get_current_result()
            result.status = ExecutionState.FAILED
            self.execution_history.append(result)
            return result
        finally:
            self.current_executions.pop(dag_id, None)
    
    def pause_execution(self, dag_id: str) -> bool:
        """Pause a running DAG execution"""
        if dag_id in self.current_executions:
            return self.current_executions[dag_id].pause()
        return False
    
    def resume_execution(self, dag_id: str) -> bool:
        """Resume a paused DAG execution"""
        if dag_id in self.current_executions:
            return self.current_executions[dag_id].resume()
        return False
    
    def cancel_execution(self, dag_id: str) -> bool:
        """Cancel a running DAG execution"""
        if dag_id in self.current_executions:
            return self.current_executions[dag_id].cancel()
        return False
    
    def get_execution_status(self, dag_id: str) -> Optional[Dict[str, Any]]:
        """Get current execution status"""
        if dag_id in self.current_executions:
            execution = self.current_executions[dag_id]
            return {
                'dag_id': dag_id,
                'status': execution.state,
                'completed_nodes': execution.get_completed_nodes(),
                'failed_nodes': execution.get_failed_nodes(),
                'running_nodes': execution.get_running_nodes(),
                'pending_nodes': execution.get_pending_nodes()
            }
        return None
    
    def _has_circular_dependencies(self, dag: 'DAG') -> bool:
        """Check if DAG has circular dependencies"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for dep in dag.get_dependencies(node_id):
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in dag.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    return True
        
        return False
    
    def _has_orphaned_nodes(self, dag: 'DAG') -> bool:
        """Check if DAG has orphaned nodes (no connections)"""
        if len(dag.nodes) <= 1:
            return False
        
        connected_nodes = set()
        for node_id in dag.nodes:
            connected_nodes.add(node_id)
            for dep in dag.get_dependencies(node_id):
                connected_nodes.add(dep)
        
        return len(connected_nodes) != len(dag.nodes)

class DAGExecution:
    """Manages execution of a single DAG"""
    
    def __init__(self, dag: 'DAG', input_data: Dict[str, Any]):
        self.dag = dag
        self.input_data = input_data
        self.state = ExecutionState.INITIALIZED
        self.node_results: Dict[str, Any] = {}
        self.node_status: Dict[str, NodeStatus] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.paused = False
        
        # Initialize all nodes as pending
        for node_id in dag.nodes:
            self.node_status[node_id] = NodeStatus.PENDING
    
    def run(self) -> DAGExecutionResult:
        """Execute the DAG"""
        self.state = ExecutionState.RUNNING
        self.start_time = datetime.now()
        
        try:
            while not self._is_execution_complete():
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                ready_nodes = self._get_ready_nodes()
                for node_id in ready_nodes:
                    self._execute_node(node_id)
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
            
            self.state = ExecutionState.COMPLETED if self._all_nodes_successful() else ExecutionState.FAILED
        except Exception as e:
            logger.error(f"DAG execution error: {e}")
            self.state = ExecutionState.FAILED
        finally:
            self.end_time = datetime.now()
        
        return self.get_current_result()
    
    def pause(self) -> bool:
        """Pause execution"""
        if self.state == ExecutionState.RUNNING:
            self.paused = True
            self.state = ExecutionState.PAUSED
            return True
        return False
    
    def resume(self) -> bool:
        """Resume execution"""
        if self.state == ExecutionState.PAUSED:
            self.paused = False
            self.state = ExecutionState.RUNNING
            return True
        return False
    
    def cancel(self) -> bool:
        """Cancel execution"""
        if self.state in [ExecutionState.RUNNING, ExecutionState.PAUSED]:
            self.state = ExecutionState.CANCELLED
            return True
        return False
    
    def get_current_result(self) -> DAGExecutionResult:
        """Get current execution result"""
        execution_time = 0.0
        if self.start_time and self.end_time:
            execution_time = (self.end_time - self.start_time).total_seconds()
        
        return DAGExecutionResult(
            dag_id=self.dag.dag_id,
            status=self.state,
            completed_nodes=self.get_completed_nodes(),
            failed_nodes=self.get_failed_nodes(),
            execution_time=execution_time,
            results=self.node_results.copy()
        )
    
    def get_completed_nodes(self) -> List[str]:
        """Get list of completed nodes"""
        return [node_id for node_id, status in self.node_status.items() if status == NodeStatus.COMPLETED]
    
    def get_failed_nodes(self) -> List[str]:
        """Get list of failed nodes"""
        return [node_id for node_id, status in self.node_status.items() if status == NodeStatus.FAILED]
    
    def get_running_nodes(self) -> List[str]:
        """Get list of running nodes"""
        return [node_id for node_id, status in self.node_status.items() if status == NodeStatus.RUNNING]
    
    def get_pending_nodes(self) -> List[str]:
        """Get list of pending nodes"""
        return [node_id for node_id, status in self.node_status.items() if status == NodeStatus.PENDING]
    
    def _is_execution_complete(self) -> bool:
        """Check if execution is complete"""
        return all(status in [NodeStatus.COMPLETED, NodeStatus.FAILED, NodeStatus.SKIPPED] 
                  for status in self.node_status.values())
    
    def _all_nodes_successful(self) -> bool:
        """Check if all nodes completed successfully"""
        return all(status == NodeStatus.COMPLETED for status in self.node_status.values())
    
    def _get_ready_nodes(self) -> List[str]:
        """Get nodes ready for execution"""
        ready_nodes = []
        for node_id, status in self.node_status.items():
            if status == NodeStatus.PENDING:
                deps = self.dag.get_dependencies(node_id)
                if all(self.node_status.get(dep) == NodeStatus.COMPLETED for dep in deps):
                    ready_nodes.append(node_id)
        return ready_nodes
    
    def _execute_node(self, node_id: str):
        """Execute a single node"""
        node = self.dag.nodes[node_id]
        self.node_status[node_id] = NodeStatus.RUNNING
        
        try:
            # Prepare input data for node
            node_input = self._prepare_node_input(node_id)
            
            # Execute node
            result = node.execute(node_input)
            
            # Store result
            self.node_results[node_id] = result
            self.node_status[node_id] = NodeStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Node {node_id} execution failed: {e}")
            self.node_results[node_id] = {'error': str(e)}
            self.node_status[node_id] = NodeStatus.FAILED
    
    def _prepare_node_input(self, node_id: str) -> Dict[str, Any]:
        """Prepare input data for node execution"""
        node_input = self.input_data.copy()
        
        # Add results from dependent nodes
        deps = self.dag.get_dependencies(node_id)
        for dep in deps:
            if dep in self.node_results:
                node_input[f'dep_{dep}'] = self.node_results[dep]
        
        return node_input

# Forward declaration for type hints
class DAG:
    """Forward declaration - will be implemented in dag_node.py"""
    pass
