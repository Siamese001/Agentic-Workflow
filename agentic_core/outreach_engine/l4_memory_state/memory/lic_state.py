from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class OutreachState:
    """Represents an outreach workflow state."""
    state_id: str
    workflow_id: str
    current_stage: str
    data: Dict[str, Any]
    timestamp: datetime
    status: str = "active"

    def __post_init__(self):
        if not self.data:
            self.data = {}

class LICState:
    """Minimal functional LIC state implementation."""

    def __init__(self):
        self.states: Dict[str, OutreachState] = {}
        self.workflow_index: Dict[str, List[str]] = {}
        self.stage_index: Dict[str, List[str]] = {}

    def process(self, *args, **kwargs) -> Any:
        """Process LIC state operations."""
        operation = kwargs.get("operation", "status")
        
        if operation == "create":
            return self.create_state(**kwargs)
        elif operation == "update":
            return self.update_state(**kwargs)
        elif operation == "get":
            return self.get_state(**kwargs)
        elif operation == "delete":
            return self.delete_state(**kwargs)
        else:
            return {
                "status": "ready",
                "total_states": len(self.states),
                "active_workflows": len(self.workflow_index),
                "stages": len(self.stage_index),
                "processed": True
            }

    def create_state(self, state_id: str, workflow_id: str, current_stage: str,
                    data: Dict[str, Any], status: str = "active") -> Dict[str, Any]:
        """Create a new outreach state."""
        state = OutreachState(
            state_id=state_id,
            workflow_id=workflow_id,
            current_stage=current_stage,
            data=data,
            timestamp=datetime.now(),
            status=status
        )
        
        self.states[state_id] = state
        
        # Update indexes
        if workflow_id not in self.workflow_index:
            self.workflow_index[workflow_id] = []
        self.workflow_index[workflow_id].append(state_id)
        
        if current_stage not in self.stage_index:
            self.stage_index[current_stage] = []
        self.stage_index[current_stage].append(state_id)
        
        return {
            "status": "created",
            "state_id": state_id,
            "processed": True
        }

    def update_state(self, state_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing state."""
        if state_id not in self.states:
            return {"status": "not_found", "processed": True}
        
        state = self.states[state_id]
        
        # Update indexes if stage changed
        if "current_stage" in updates and updates["current_stage"] != state.current_stage:
            # Remove from old stage index
            if state.current_stage in self.stage_index:
                self.stage_index[state.current_stage].remove(state_id)
                if not self.stage_index[state.current_stage]:
                    del self.stage_index[state.current_stage]
            
            # Add to new stage index
            new_stage = updates["current_stage"]
            if new_stage not in self.stage_index:
                self.stage_index[new_stage] = []
            self.stage_index[new_stage].append(state_id)
            
            state.current_stage = new_stage
        
        # Update other fields
        if "data" in updates:
            state.data.update(updates["data"])
        
        if "status" in updates:
            state.status = updates["status"]
        
        state.timestamp = datetime.now()
        
        return {
            "status": "updated",
            "state_id": state_id,
            "processed": True
        }

    def get_state(self, state_id: Optional[str] = None, workflow_id: Optional[str] = None,
                 current_stage: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """Get state(s) with optional filtering."""
        if state_id:
            if state_id in self.states:
                state = self.states[state_id]
                return {
                    "status": "found",
                    "state": {
                        "state_id": state.state_id,
                        "workflow_id": state.workflow_id,
                        "current_stage": state.current_stage,
                        "data": state.data,
                        "timestamp": state.timestamp.isoformat(),
                        "status": state.status
                    },
                    "processed": True
                }
            else:
                return {"status": "not_found", "processed": True}
        
        # Filter states
        candidate_ids = None
        
        if workflow_id and workflow_id in self.workflow_index:
            candidate_ids = set(self.workflow_index[workflow_id])
        
        if current_stage and current_stage in self.stage_index:
            stage_ids = set(self.stage_index[current_stage])
            if candidate_ids is not None:
                candidate_ids &= stage_ids
            else:
                candidate_ids = stage_ids
        
        if candidate_ids is None:
            candidate_ids = set(self.states.keys())
        
        # Apply status filter
        results = []
        for state_id in candidate_ids:
            if state_id in self.states:
                state = self.states[state_id]
                
                if status and state.status != status:
                    continue
                
                results.append({
                    "state_id": state.state_id,
                    "workflow_id": state.workflow_id,
                    "current_stage": state.current_stage,
                    "data": state.data,
                    "timestamp": state.timestamp.isoformat(),
                    "status": state.status
                })
        
        return {
            "status": "retrieved",
            "states": results,
            "count": len(results),
            "processed": True
        }

    def delete_state(self, state_id: str) -> Dict[str, Any]:
        """Delete a specific state."""
        if state_id not in self.states:
            return {"status": "not_found", "processed": True}
        
        state = self.states[state_id]
        
        # Remove from workflow index
        if state.workflow_id in self.workflow_index:
            self.workflow_index[state.workflow_id].remove(state_id)
            if not self.workflow_index[state.workflow_id]:
                del self.workflow_index[state.workflow_id]
        
        # Remove from stage index
        if state.current_stage in self.stage_index:
            self.stage_index[state.current_stage].remove(state_id)
            if not self.stage_index[state.current_stage]:
                del self.stage_index[state.current_stage]
        
        # Remove from main storage
        del self.states[state_id]
        
        return {
            "status": "deleted",
            "state_id": state_id,
            "processed": True
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get state statistics."""
        status_counts = {}
        stage_counts = {}
        
        for state in self.states.values():
            status_counts[state.status] = status_counts.get(state.status, 0) + 1
            stage_counts[state.current_stage] = stage_counts.get(state.current_stage, 0) + 1
        
        return {
            "total_states": len(self.states),
            "active_workflows": len(self.workflow_index),
            "stages": len(self.stage_index),
            "status_distribution": status_counts,
            "stage_distribution": stage_counts
        }
