"""
Base Agents module.

Provides base agent classes for the agentic framework.
"""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, name: str = "BaseAgent", **kwargs):
        self.name = name
        self._config = kwargs
        self._state: Dict[str, Any] = {}
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's main function."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def get_state(self, key: str) -> Optional[Any]:
        """Get state value."""
        return self._state.get(key)
    
    def set_state(self, key: str, value: Any) -> None:
        """Set state value."""
        self._state[key] = value


class CognitionAgent(BaseAgent):
    """Base class for cognition agents (L1)."""
    pass


class ExecutionAgent(BaseAgent):
    """Base class for execution agents (L2)."""
    pass


class OrchestrationAgent(BaseAgent):
    """Base class for orchestration agents (L3)."""
    pass


class StateAgent(BaseAgent):
    """Base class for state agents (L4)."""
    pass


class SafetyAgent(BaseAgent):
    """Base class for safety agents (L5)."""
    pass


class ObservabilityAgent(BaseAgent):
    """Base class for observability agents (L6)."""
    pass


__all__ = [
    'BaseAgent',
    'CognitionAgent', 
    'ExecutionAgent',
    'OrchestrationAgent',
    'StateAgent',
    'SafetyAgent',
    'ObservabilityAgent',
]
