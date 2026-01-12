"""
SovereignBaseAgent - Base class for sovereign agents.

Provides foundational capabilities for agents with sovereign authority.
"""
from typing import Any, Dict, Optional
import logging
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

logger = logging.getLogger(__name__)


class SovereignBaseAgent(MCPHardenedMixin):
    """Base class for sovereign agents with elevated authority."""
    
    def __init__(self, name: str = "SovereignAgent", **kwargs):
        self.name = name
        self._config = kwargs
        self._state: Dict[str, Any] = {}
        self._authority_level = kwargs.get('authority_level', 'standard')
    
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
        """Base heal_repository implementation - subclasses should override."""
        super().heal_repository()

        return {"skipped": 1}


__all__ = ['SovereignBaseAgent']
