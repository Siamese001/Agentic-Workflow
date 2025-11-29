#!/usr/bin/env python3
"""
Coordination Utilities
Section 4: DAG Orchestration - Utilities for coordinating multiple workflows
"""

from typing import Dict, Any, List, Optional, Set
import logging
import time
from enum import Enum

logger = logging.getLogger(__name__)

class CoordinationMode(str, Enum):
    """Coordination mode enumeration"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PRIORITY_BASED = "priority_based"
    RESOURCE_CONSTRAINED = "resource_constrained"

class CoordinationUtil:
    """Utility class for workflow coordination"""
    
    def __init__(self, mode: CoordinationMode = CoordinationMode.SEQUENTIAL):
        self.mode = mode
        self.active_workflows: Set[str] = set()
        self.completed_workflows: Set[str] = set()
        self.failed_workflows: Set[str] = set()
        self.resource_pool: Dict[str, int] = {}
    
    def add_workflow(self, workflow_id: str, priority: int = 0) -> bool:
        """Add workflow to coordination queue"""
        if workflow_id in self.active_workflows:
            logger.warning(f"Workflow {workflow_id} already active")
            return False
        
        self.active_workflows.add(workflow_id)
        logger.info(f"Added workflow {workflow_id} to coordination queue")
        return True
    
    def complete_workflow(self, workflow_id: str) -> bool:
        """Mark workflow as completed"""
        if workflow_id not in self.active_workflows:
            logger.warning(f"Workflow {workflow_id} not in active set")
            return False
        
        self.active_workflows.remove(workflow_id)
        self.completed_workflows.add(workflow_id)
        logger.info(f"Completed workflow {workflow_id}")
        return True
    
    def fail_workflow(self, workflow_id: str, error: str) -> bool:
        """Mark workflow as failed"""
        if workflow_id not in self.active_workflows:
            logger.warning(f"Workflow {workflow_id} not in active set")
            return False
        
        self.active_workflows.remove(workflow_id)
        self.failed_workflows.add(workflow_id)
        logger.error(f"Failed workflow {workflow_id}: {error}")
        return True
    
    def get_next_workflows(self, max_concurrent: int = 5) -> List[str]:
        """Get next workflows to execute based on coordination mode"""
        if self.mode == CoordinationMode.SEQUENTIAL:
            return list(self.active_workflows)[:1] if self.active_workflows else []
        elif self.mode == CoordinationMode.PARALLEL:
            return list(self.active_workflows)[:max_concurrent]
        elif self.mode == CoordinationMode.PRIORITY_BASED:
            # Simplified priority-based selection
            return list(self.active_workflows)[:max_concurrent]
        else:
            return list(self.active_workflows)[:max_concurrent]
    
    def allocate_resources(self, workflow_id: str, required_resources: Dict[str, int]) -> bool:
        """Allocate resources for workflow execution"""
        for resource, amount in required_resources.items():
            available = self.resource_pool.get(resource, 0)
            if available < amount:
                logger.warning(f"Insufficient {resource}: need {amount}, have {available}")
                return False
        
        # Allocate resources
        for resource, amount in required_resources.items():
            self.resource_pool[resource] = self.resource_pool.get(resource, 0) - amount
        
        logger.info(f"Allocated resources for workflow {workflow_id}")
        return True
    
    def release_resources(self, workflow_id: str, allocated_resources: Dict[str, int]) -> None:
        """Release resources from completed workflow"""
        for resource, amount in allocated_resources.items():
            self.resource_pool[resource] = self.resource_pool.get(resource, 0) + amount
        
        logger.info(f"Released resources from workflow {workflow_id}")
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination status"""
        return {
            "mode": self.mode,
            "active_workflows": list(self.active_workflows),
            "completed_workflows": list(self.completed_workflows),
            "failed_workflows": list(self.failed_workflows),
            "resource_pool": self.resource_pool.copy(),
            "total_processed": len(self.completed_workflows) + len(self.failed_workflows)
        }
    
    def set_resource_pool(self, resources: Dict[str, int]) -> None:
        """Initialize resource pool"""
        self.resource_pool = resources.copy()
        logger.info(f"Initialized resource pool: {resources}")

def manage_orchestration_state(workflows: List[Dict[str, Any]], mode: CoordinationMode = CoordinationMode.SEQUENTIAL) -> Dict[str, Any]:
    """Manage orchestration state for multiple workflows"""
    coordinator = CoordinationUtil(mode)
    
    # Initialize resources if specified
    total_resources = {}
    for workflow in workflows:
        resources = workflow.get("required_resources", {})
        for resource, amount in resources.items():
            total_resources[resource] = total_resources.get(resource, 0) + amount
    
    coordinator.set_resource_pool(total_resources)
    
    # Add all workflows to coordination queue
    for workflow in workflows:
        workflow_id = workflow["workflow_id"]
        coordinator.add_workflow(workflow_id, workflow.get("priority", 0))
    
    return {
        "status": "initialized",
        "coordinator_status": coordinator.get_coordination_status(),
        "workflows_queued": len(workflows)
    }

# Re-export components
__all__ = [
    'CoordinationUtil', 'CoordinationMode', 'manage_orchestration_state'
]
