#!/usr/bin/env python3
"""
State Managers
Section 4: DAG Orchestration - State management utilities for orchestration
"""

from typing import Dict, Any, List, Optional, Union
import logging
import time
import json
from enum import Enum

logger = logging.getLogger(__name__)

class WorkflowState(str, Enum):
    """Workflow state enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StateManager:
    """Base class for managing orchestration state"""
    
    def __init__(self, manager_id: str, persistence_config: Optional[Dict[str, Any]] = None):
        self.manager_id = manager_id
        self.persistence_config = persistence_config or {}
        self.state_store: Dict[str, Dict[str, Any]] = {}
        self.state_history: List[Dict[str, Any]] = []
    
    def set_state(self, entity_id: str, state: WorkflowState, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Set state for an entity"""
        try:
            timestamp = time.time()
            state_entry = {
                "entity_id": entity_id,
                "state": state,
                "metadata": metadata or {},
                "timestamp": timestamp,
                "manager_id": self.manager_id
            }
            
            self.state_store[entity_id] = state_entry
            self.state_history.append(state_entry)
            
            logger.info(f"Set state for {entity_id} to {state}")
            return True
        except Exception as e:
            logger.error(f"Failed to set state: {e}")
            return False
    
    def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get current state for an entity"""
        return self.state_store.get(entity_id)
    
    def get_entities_by_state(self, state: WorkflowState) -> List[str]:
        """Get all entities in a specific state"""
        return [
            entity_id for entity_id, state_data in self.state_store.items()
            if state_data.get("state") == state
        ]
    
    def transition_state(self, entity_id: str, from_state: WorkflowState, to_state: WorkflowState) -> bool:
        """Transition entity from one state to another"""
        current_state_data = self.get_state(entity_id)
        
        if not current_state_data:
            logger.error(f"No current state found for {entity_id}")
            return False
        
        if current_state_data.get("state") != from_state:
            logger.warning(f"State mismatch for {entity_id}: expected {from_state}, got {current_state_data.get('state')}")
            return False
        
        return self.set_state(entity_id, to_state, {"previous_state": from_state})
    
    def get_state_history(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get state history for an entity"""
        return [
            entry for entry in self.state_history
            if entry.get("entity_id") == entity_id
        ]
    
    def cleanup_old_states(self, max_age_seconds: int = 3600) -> int:
        """Clean up old state entries"""
        cutoff_time = time.time() - max_age_seconds
        original_count = len(self.state_store)
        
        entities_to_remove = []
        for entity_id, state_data in self.state_store.items():
            if state_data.get("timestamp", 0) < cutoff_time:
                entities_to_remove.append(entity_id)
        
        for entity_id in entities_to_remove:
            del self.state_store[entity_id]
        
        removed_count = original_count - len(self.state_store)
        logger.info(f"Cleaned up {removed_count} old state entries")
        return removed_count

class WorkflowStateManager(StateManager):
    """Specialized state manager for workflows"""
    
    def __init__(self, manager_id: str = "workflow_state_manager"):
        super().__init__(manager_id)
        self.workflow_metrics: Dict[str, Dict[str, Any]] = {}
    
    def start_workflow(self, workflow_id: str, workflow_config: Dict[str, Any]) -> bool:
        """Start a workflow and initialize its state"""
        success = self.set_state(workflow_id, WorkflowState.RUNNING, {
            "config": workflow_config,
            "start_time": time.time()
        })
        
        if success:
            self.workflow_metrics[workflow_id] = {
                "start_time": time.time(),
                "steps_completed": 0,
                "steps_total": len(workflow_config.get("steps", [])),
                "errors": []
            }
        
        return success
    
    def complete_workflow(self, workflow_id: str, result: Dict[str, Any]) -> bool:
        """Mark workflow as completed"""
        success = self.set_state(workflow_id, WorkflowState.COMPLETED, {
            "result": result,
            "end_time": time.time()
        })
        
        if success and workflow_id in self.workflow_metrics:
            metrics = self.workflow_metrics[workflow_id]
            metrics["end_time"] = time.time()
            metrics["duration"] = metrics["end_time"] - metrics["start_time"]
        
        return success
    
    def fail_workflow(self, workflow_id: str, error: str) -> bool:
        """Mark workflow as failed"""
        success = self.set_state(workflow_id, WorkflowState.FAILED, {
            "error": error,
            "end_time": time.time()
        })
        
        if success and workflow_id in self.workflow_metrics:
            self.workflow_metrics[workflow_id]["errors"].append(error)
        
        return success
    
    def update_workflow_progress(self, workflow_id: str, step_completed: str) -> bool:
        """Update workflow progress"""
        if workflow_id in self.workflow_metrics:
            self.workflow_metrics[workflow_id]["steps_completed"] += 1
            return True
        return False
    
    def get_workflow_metrics(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific workflow"""
        return self.workflow_metrics.get(workflow_id)

class ResourceStateManager(StateManager):
    """Specialized state manager for resource allocation"""
    
    def __init__(self, manager_id: str = "resource_state_manager"):
        super().__init__(manager_id)
        self.resource_allocations: Dict[str, Dict[str, int]] = {}
    
    def allocate_resource(self, resource_id: str, workflow_id: str, amount: int) -> bool:
        """Allocate resource to workflow"""
        if resource_id not in self.resource_allocations:
            self.resource_allocations[resource_id] = {}
        
        self.resource_allocations[resource_id][workflow_id] = amount
        
        return self.set_state(f"resource_{resource_id}", WorkflowState.RUNNING, {
            "allocations": self.resource_allocations[resource_id].copy(),
            "total_allocated": sum(self.resource_allocations[resource_id].values())
        })
    
    def release_resource(self, resource_id: str, workflow_id: str) -> bool:
        """Release resource from workflow"""
        if resource_id in self.resource_allocations and workflow_id in self.resource_allocations[resource_id]:
            del self.resource_allocations[resource_id][workflow_id]
            
            if not self.resource_allocations[resource_id]:
                return self.set_state(f"resource_{resource_id}", WorkflowState.COMPLETED, {
                    "allocations": {},
                    "total_allocated": 0
                })
            else:
                return self.set_state(f"resource_{resource_id}", WorkflowState.RUNNING, {
                    "allocations": self.resource_allocations[resource_id].copy(),
                    "total_allocated": sum(self.resource_allocations[resource_id].values())
                })
        
        return False

# Re-export components
__all__ = [
    'StateManager', 'WorkflowStateManager', 'ResourceStateManager',
    'WorkflowState'
]
