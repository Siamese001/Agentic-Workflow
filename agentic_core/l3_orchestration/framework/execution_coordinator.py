#!/usr/bin/env python3
"""
Execution Coordinator
Section 4: DAG Orchestration - Coordinates execution across multiple DAGs
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

from .dag_engine import DAGEngine

logger = logging.getLogger(__name__)

class CoordinationMode(str, Enum):
    """Coordination mode enumeration"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PRIORITY = "priority"

@dataclass
class ExecutionPlan:
    """Plan for coordinated DAG execution"""
    plan_id: str
    dag_executions: List[Dict[str, Any]]
    coordination_mode: CoordinationMode
    priority_order: Optional[List[str]] = None

class ExecutionCoordinator:
    """Coordinates execution across multiple DAGs"""
    
    def __init__(self):
        self.dag_engine: Optional[DAGEngine] = None
        self.execution_plans: Dict[str, ExecutionPlan] = {}
        self.active_coordinations: Dict[str, Dict[str, Any]] = {}
        
    def set_dag_engine(self, dag_engine: DAGEngine) -> None:
        """Set the DAG engine for coordination"""
        self.dag_engine = dag_engine
    
    def create_execution_plan(self, plan_id: str, dag_executions: List[Dict[str, Any]], 
                            coordination_mode: CoordinationMode = CoordinationMode.SEQUENTIAL) -> bool:
        """Create an execution plan for multiple DAGs"""
        try:
            plan = ExecutionPlan(
                plan_id=plan_id,
                dag_executions=dag_executions,
                coordination_mode=coordination_mode
            )
            self.execution_plans[plan_id] = plan
            logger.info(f"Execution plan {plan_id} created with {len(dag_executions)} DAG executions")
            return True
        except Exception as e:
            logger.error(f"Failed to create execution plan {plan_id}: {e}")
            return False
    
    def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """Execute a coordinated plan"""
        if plan_id not in self.execution_plans:
            raise ValueError(f"Execution plan {plan_id} not found")
        
        if not self.dag_engine:
            raise ValueError("DAG engine not set")
        
        plan = self.execution_plans[plan_id]
        self.active_coordinations[plan_id] = {
            'status': 'running',
            'results': []
        }
        
        try:
            if plan.coordination_mode == CoordinationMode.SEQUENTIAL:
                results = self._execute_sequential(plan)
            elif plan.coordination_mode == CoordinationMode.PARALLEL:
                results = self._execute_parallel(plan)
            elif plan.coordination_mode == CoordinationMode.PRIORITY:
                results = self._execute_priority(plan)
            else:
                raise ValueError(f"Unsupported coordination mode: {plan.coordination_mode}")
            
            self.active_coordinations[plan_id]['status'] = 'completed'
            self.active_coordinations[plan_id]['results'] = results
            
            return {
                'success': True,
                'plan_id': plan_id,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Execution plan {plan_id} failed: {e}")
            self.active_coordinations[plan_id]['status'] = 'failed'
            return {
                'success': False,
                'plan_id': plan_id,
                'error': str(e)
            }
        
        finally:
            self.active_coordinations.pop(plan_id, None)
    
    def _execute_sequential(self, plan: ExecutionPlan) -> List[Dict[str, Any]]:
        """Execute DAGs sequentially"""
        results = []
        for dag_exec in plan.dag_executions:
            result = self.dag_engine.execute_dag(dag_exec['dag_id'], dag_exec.get('input_data', {}))
            results.append({
                'dag_id': dag_exec['dag_id'],
                'result': result
            })
        return results
    
    def _execute_parallel(self, plan: ExecutionPlan) -> List[Dict[str, Any]]:
        """Execute DAGs in parallel (simplified implementation)"""
        # For now, execute sequentially but mark as parallel execution
        return self._execute_sequential(plan)
    
    def _execute_priority(self, plan: ExecutionPlan) -> List[Dict[str, Any]]:
        """Execute DAGs in priority order"""
        # For now, execute sequentially
        return self._execute_sequential(plan)
    
    def get_coordination_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get status of active coordination"""
        return self.active_coordinations.get(plan_id)

# Re-export components
__all__ = [
    'ExecutionCoordinator', 'ExecutionPlan', 'CoordinationMode'
]





