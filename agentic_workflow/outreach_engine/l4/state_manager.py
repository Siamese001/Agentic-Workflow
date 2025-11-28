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
class OutreachWorkflowState:
    """Isolated outreach state, never cross-contaminates resume state."""
    mission_id: str
    mission: Dict[str, Any]
    research_context: Dict[str, Any]
    message_result: Dict[str, Any]
    validation_history: List[Dict[str, Any]]
    signals_used: List[Dict[str, Any]] = field(default_factory=list)
    signal_density_score: float = 0.0
    archetype: str = ""
    route: str = ""
    temperature_schedule: Dict[str, float] = field(default_factory=dict)
    meta_loop_iterations: int = 0

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
    workflow_type: str = "resume"
    outreach_state: Optional[OutreachWorkflowState] = None

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
            'workflow_type': state.workflow_type,
            'outreach_state': state.outreach_state.__dict__ if state.outreach_state else None,
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
        
        # Reconstruct outreach state if present
        outreach_data = data.get('outreach_state')
        outreach_state = None
        if outreach_data:
            outreach_state = OutreachWorkflowState(
                mission_id=outreach_data.get('mission_id', ''),
                mission=outreach_data.get('mission', {}),
                research_context=outreach_data.get('research_context', {}),
                message_result=outreach_data.get('message_result', {}),
                validation_history=outreach_data.get('validation_history', []),
                signals_used=outreach_data.get('signals_used', []),
                signal_density_score=outreach_data.get('signal_density_score', 0.0),
                archetype=outreach_data.get('archetype', ''),
                route=outreach_data.get('route', ''),
                temperature_schedule=outreach_data.get('temperature_schedule', {}),
                meta_loop_iterations=outreach_data.get('meta_loop_iterations', 0)
            )
        
        self._state = WorkflowState(
            job_data=data.get('job_data'),
            resume_data=data.get('resume_data'),
            strategy_result=data.get('strategy_result'),
            draft_result=data.get('draft_result'),
            workflow_type=data.get('workflow_type', 'resume'),
            outreach_state=outreach_state,
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

    def save_outreach_state(
        self,
        mission_id: str,
        outreach_state: OutreachWorkflowState,
        link_to_resume_workflow: Optional[str] = None
    ) -> None:
        """Store outreach state without modifying resume workflow fields."""
        state = self.load_state() or WorkflowState()
        if link_to_resume_workflow and state.job_data:
            state.workflow_type = "resume_outreach"
            state.metadata["linked_resume_workflow"] = link_to_resume_workflow
        else:
            state.workflow_type = "outreach"
        state.outreach_state = outreach_state
        state.metadata["outreach_mission_id"] = mission_id
        self.save_state(state)

    def load_outreach_state(self, mission_id: str) -> Optional[OutreachWorkflowState]:
        state = self.load_state()
        if state and state.metadata.get("outreach_mission_id") == mission_id:
            return state.outreach_state
        return None
