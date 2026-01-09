"""
Action Registry - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional, Callable


class ActionRegistry:
    """Registry for actions."""
    def __init__(self):
        self._actions: Dict[str, Callable] = {}
    
    def register(self, name: str, action: Callable) -> None:
        self._actions[name] = action
    
    def execute(self, name: str, *args, **kwargs) -> Any:
        if name not in self._actions:
            raise ValueError(f"Action not found: {name}")
        return self._actions[name](*args, **kwargs)
    
    def list_actions(self) -> List[str]:
        return list(self._actions.keys())


__all__ = ['ActionRegistry']
