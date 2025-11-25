"""
L4 state management for persistent résumé processing data.

Ensures reliable storage and retrieval of workflow state for consistent résumé improvement.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
import json
from pathlib import Path

@dataclass
class WorkflowState:
    """
    Stores résumé workflow state data for persistence.
    
    Maintains job, resume, and strategy data for reliable résumé processing continuity.
    """
    job_data: Optional[Dict[str, Any]] = None
    resume_data: Optional[Dict[str, Any]] = None
    strategy_result: Optional[str] = None
    draft_result: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class StateManager:
    """
    Manages persistent state storage for résumé workflows.
    
    Ensures data integrity and continuity for comprehensive résumé improvement processes.
    """
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self._state: Optional[WorkflowState] = None
    
    def save_state(self, state: WorkflowState) -> None:
        """
        Persists résumé workflow state to storage.
        
        Ensures data preservation for reliable résumé processing continuity.
        """
        with open(self.storage_path, 'w') as f:
            json.dump({
                'job_data': state.job_data,
                'resume_data': state.resume_data,
                'strategy_result': state.strategy_result,
                'draft_result': state.draft_result,
                'metadata': state.metadata
            }, f)
        self._state = state
    
    def load_state(self) -> Optional[WorkflowState]:
        """
        Retrieves résumé workflow state from storage.
        
        Restores previous processing state for consistent résumé improvement workflows.
        """
        if not self.storage_path.exists():
            return None
        
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        
        self._state = WorkflowState(
            job_data=data.get('job_data'),
            resume_data=data.get('resume_data'),
            strategy_result=data.get('strategy_result'),
            draft_result=data.get('draft_result'),
            metadata=data.get('metadata', {})
        )
        return self._state
    
    def update_strategy_result(self, result: str) -> None:
        """Update strategy result - pure state mutation only."""
        if self._state is None:
            self._state = WorkflowState()
        self._state.strategy_result = result
        self.save_state(self._state)
