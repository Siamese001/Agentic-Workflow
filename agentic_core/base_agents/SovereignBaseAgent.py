"""
SovereignBaseAgent - Base class for sovereign agents.

Provides foundational capabilities for agents with sovereign authority.

MRO HARDENING:
- This is the ROOT of the agent hierarchy
- All mixins should call super().__init__(**kwargs) to propagate up
- SovereignBaseAgent is LAST in MRO before object
- Uses cooperative multiple inheritance pattern
"""
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SovereignBaseAgent:
    """
    Base class for sovereign agents with elevated authority.
    
    MRO HARDENING: This class is the ROOT of the hierarchy.
    - Does NOT inherit from mixins (mixins are added by layer bases)
    - Terminates the super().__init__() chain cleanly
    - All kwargs are consumed here to prevent TypeError
    """
    
    def __init__(self, name: str = "SovereignAgent", **kwargs):
        # Consume remaining kwargs to terminate MRO chain cleanly
        # Any unrecognized kwargs are stored in _config
        super().__init__()  # Terminates at object
        self.name = name
        self._config = kwargs
        self._state: Dict[str, Any] = {}
        self._authority_level = kwargs.pop('authority_level', 'standard')
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's main function."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def get_state(self, key: str) -> Optional[Any]:
        """Get state value."""
        return self._state.get(key)
    
    def set_state(self, key: str, value: Any) -> None:
        """Set state value."""
        self._state[key] = value
    
    def get_authority_level(self) -> str:
        """Get the agent's authority level."""
        return self._authority_level
    
    def elevate_authority(self, level: str) -> None:
        """Elevate the agent's authority level."""
        self._authority_level = level
        logger.info(f"Authority elevated to: {level}")
    
    def log_info(self, message: str) -> None:
        """Log an info message."""
        logger.info(f"[{self.name}] {message}")
    
    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        logger.warning(f"[{self.name}] {message}")
    
    def log_error(self, message: str) -> None:
        """Log an error message."""
        logger.error(f"[{self.name}] {message}")
    
    def log_feedback(self, workflow_id: str, action: str, status: str, details: Dict[str, Any] = None) -> None:
        """Log feedback for a workflow action."""
        logger.info(f"[{self.name}] Workflow {workflow_id}: {action} - {status} - {details or {}}")
    
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """
        Base heal_repository implementation - ROOT termination point.
        
        MRO HARDENING: This is the END of the heal_repository chain.
        Subclasses should call super().heal_repository() which eventually
        reaches here and terminates cleanly.
        """
        # ROOT: No super() call - we ARE the termination point
        return {"violations": 0, "fixed": 0, "errors": 0, "skipped": 1}


__all__ = ['SovereignBaseAgent']
