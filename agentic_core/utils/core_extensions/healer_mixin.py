"""
HealerMixin - Base healing functionality for all agents.

Provides shared healing infrastructure including:
- Healing budget management
- Cycle detection
- Standardized heal_repository method
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Set

Logger = logging.getLogger(__name__)


def healer_mixin():
    """Healer mixin function for compatibility"""
    pass


class HealerMixin:
    """
    Mixin that provides healing functionality to agents.
    
    All agents that need healing capabilities should inherit from this mixin.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._healing_count: int = 0
        self._healing_enabled: bool = True
        self._max_healing_operations: int = 100
    
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set[str]] = None
    ) -> Dict[str, int]:
        """
        Base heal_repository method for the MRO chain.
        
        This provides the shared healing logic that all agents inherit.
        Subclasses should call super().heal_repository() first, then add their specific logic.
        
        Args:
            dry_run: If True, only report what would be done
            execute: If True, apply fixes
            depth: Current recursion depth
            max_depth: Maximum recursion depth allowed
            _call_path: Set of visited agents for cycle detection
            
        Returns:
            Dict with healing statistics using canonical keys:
            - violations_found: Number of violations found
            - violations_fixed: Number of violations fixed
            - errors: Number of errors encountered
            - skipped: Number of items skipped
        """
        # Initialize call path for cycle detection
        if _call_path is None:
            _call_path = set()
        
        # Check for cycles
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            Logger.warning(f"Healing cycle detected: {agent_name}")
            return {
                'violations_found': 0,
                'violations_fixed': 0,
                'errors': 1,
                'skipped': 0
            }
        
        # Add current agent to call path
        _call_path.add(agent_name)
        
        # Check if healing is enabled
        if not self._healing_enabled:
            return {
                'violations_found': 0,
                'violations_fixed': 0,
                'errors': 0,
                'skipped': 0
            }
        
        # Check healing budget
        if self._healing_count >= self._max_healing_operations:
            Logger.warning(f"Healing budget exceeded for {agent_name}")
            return {
                'violations_found': 0,
                'violations_fixed': 0,
                'errors': 1,
                'skipped': 0
            }
        
        # Check depth limit
        if depth > max_depth:
            Logger.warning(f"Healing depth limit exceeded for {agent_name}")
            return {
                'violations_found': 0,
                'violations_fixed': 0,
                'errors': 1,
                'skipped': 0
            }
        
        # Base implementation does nothing
        # Subclasses should override and add their specific healing logic
        return {
            'violations_found': 0,
            'violations_fixed': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def enable_healing(self) -> None:
        """Enable healing for this agent."""
        self._healing_enabled = True
        Logger.debug(f"Healing enabled for {self.__class__.__name__}")
    
    def disable_healing(self) -> None:
        """Disable healing for this agent."""
        self._healing_enabled = False
        Logger.debug(f"Healing disabled for {self.__class__.__name__}")
    
    def reset_healing_count(self) -> None:
        """Reset the healing operation counter."""
        self._healing_count = 0
        Logger.debug(f"Healing count reset for {self.__class__.__name__}")
    
    def set_max_healing_operations(self, max_ops: int) -> None:
        """Set the maximum number of healing operations allowed."""
        self._max_healing_operations = max_ops
        Logger.debug(f"Max healing operations set to {max_ops} for {self.__class__.__name__}")
