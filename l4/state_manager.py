"""L4 State Manager - Pure state management only."""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
import json
from pathlib import Path

@dataclass
class WorkflowState:
    """Pure state data structure - no business logic."""
    job_data: Optional[Dict[str, Any]] = None
    resume_data: Optional[Dict[str, Any]] = None
    strategy_result: Optional[str] = None
    draft_result: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class StateManager:
    """Pure state management - no orchestration, no execution logic."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self._state: Optional[WorkflowState] = None
    
    def save_state(self, state: WorkflowState) -> None:
        """Save state to storage - pure persistence only."""
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
        """Load state from storage - pure retrieval only."""
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
