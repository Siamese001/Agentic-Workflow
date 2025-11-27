"""
L4 state manager for resume job alignment workflows.

Ensures reliable storage and retrieval for resume enhancement.
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path

@dataclass
class TemporalContext:
    """
    Manages temporal context for resume job alignment workflows.

    Provides time-bounded reasoning for resume enhancement.
    """
    current_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processing_window: str = "30d"  # Default 30-day window
    temporal_relationships: Dict[str, Any] = field(default_factory=dict)
    
    def is_within_window(self, timestamp: datetime) -> bool:
        """Checks if timestamp is within resume processing window."""
        from datetime import timedelta
        window_delta = timedelta(days=int(self.processing_window.replace('d', '')))
        return (self.current_time - timestamp) <= window_delta

@dataclass 
class EpisodicMemory:
    """
    Stores episodic memory for resume job alignment workflows.

    Maintains interaction history for resume enhancement learning.
    """
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    max_interactions: int = 100
    
    def add_interaction(self, interaction: Dict[str, Any]) -> None:
        """Adds new resume workflow interaction to episodic memory."""
        interaction['timestamp'] = datetime.now(timezone.utc).isoformat()
        self.interactions.append(interaction)
        
        # Maintain size limit
        if len(self.interactions) > self.max_interactions:
            self.interactions = self.interactions[-self.max_interactions:]
    
    def get_recent_interactions(self, count: int = 10) -> List[Dict[str, Any]]:
        """Gets most recent resume workflow interactions for job alignment."""
        return self.interactions[-count:]

@dataclass
class ProceduralMemory:
    """
    Stores procedural memory for resume job alignment workflows.

    Maintains how-to knowledge for resume enhancement execution.
    """
    procedures: Dict[str, Any] = field(default_factory=dict)
    success_patterns: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_procedure(self, name: str, procedure: Dict[str, Any]) -> None:
        """Adds new resume workflow procedure for job alignment."""
        self.procedures[name] = {
            **procedure,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
    
    def get_procedure(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieves resume workflow procedure for job alignment."""
        return self.procedures.get(name)

@dataclass
class WorkflowState:
    """
    Stores resume workflow state data for job alignment persistence.

    Maintains temporal context for resume enhancement continuity.
    """
    job_data: Optional[Dict[str, Any]] = None
    resume_data: Optional[Dict[str, Any]] = None
    strategy_result: Optional[str] = None
    draft_result: Optional[str] = None
    temporal_context: TemporalContext = field(default_factory=TemporalContext)
    episodic_memory: EpisodicMemory = field(default_factory=EpisodicMemory)
    procedural_memory: ProceduralMemory = field(default_factory=ProceduralMemory)
    metadata: Dict[str, Any] = field(default_factory=dict)

class StateManager:
    """
    Manages persistent state storage for resume job alignment workflows.

    Ensures data integrity for resume enhancement processes.
    """
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self._state: Optional[WorkflowState] = None
    
    def save_state(self, state: WorkflowState) -> None:
        """
        Persists resume workflow state for job alignment processing.

        Ensures data preservation for resume enhancement continuity.
        """
        # Serialize datetime objects for JSON storage
        serializable_state = {
            'job_data': state.job_data,
            'resume_data': state.resume_data,
            'strategy_result': state.strategy_result,
            'draft_result': state.draft_result,
            'temporal_context': {
                'current_time': state.temporal_context.current_time.isoformat(),
                'processing_window': state.temporal_context.processing_window,
                'temporal_relationships': state.temporal_context.temporal_relationships
            },
            'episodic_memory': {
                'interactions': state.episodic_memory.interactions,
                'max_interactions': state.episodic_memory.max_interactions
            },
            'procedural_memory': {
                'procedures': state.procedural_memory.procedures,
                'success_patterns': state.procedural_memory.success_patterns
            },
            'metadata': state.metadata
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(serializable_state, f, indent=2)
        self._state = state
    
    def load_state(self) -> Optional[WorkflowState]:
        """
        Retrieves resume workflow state for job alignment processing.

        Restores previous state for resume enhancement workflows.
        """
        if not self.storage_path.exists():
            return None
        
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        
        # Reconstruct temporal context
        temporal_data = data.get('temporal_context', {})
        temporal_context = TemporalContext(
            current_time=datetime.fromisoformat(temporal_data.get('current_time', datetime.now(timezone.utc).isoformat())),
            processing_window=temporal_data.get('processing_window', '30d'),
            temporal_relationships=temporal_data.get('temporal_relationships', {})
        )
        
        # Reconstruct episodic memory
        episodic_data = data.get('episodic_memory', {})
        episodic_memory = EpisodicMemory(
            interactions=episodic_data.get('interactions', []),
            max_interactions=episodic_data.get('max_interactions', 100)
        )
        
        # Reconstruct procedural memory
        procedural_data = data.get('procedural_memory', {})
        procedural_memory = ProceduralMemory(
            procedures=procedural_data.get('procedures', {}),
            success_patterns=procedural_data.get('success_patterns', [])
        )
        
        self._state = WorkflowState(
            job_data=data.get('job_data'),
            resume_data=data.get('resume_data'),
            strategy_result=data.get('strategy_result'),
            draft_result=data.get('draft_result'),
            temporal_context=temporal_context,
            episodic_memory=episodic_memory,
            procedural_memory=procedural_memory,
            metadata=data.get('metadata', {})
        )
        
        return self._state
    
    def add_interaction(self, interaction_type: str, content: Dict[str, Any]) -> None:
        """
        Adds resume workflow interaction for job alignment context.

        Maintains history for resume enhancement processing.
        """
        if self._state is None:
            self._state = WorkflowState()
        
        interaction = {
            'type': interaction_type,
            'content': content
        }
        self._state.episodic_memory.add_interaction(interaction)
    
    def get_temporal_context(self) -> TemporalContext:
        """
        Gets current temporal context for resume job alignment.

        Provides temporal boundaries for resume enhancement analysis.
        """
        if self._state is None:
            self._state = WorkflowState()
        return self._state.temporal_context
