"""
L3 Orchestration Interface: IOrchestratorAgent

Abstract base class for all orchestration agents.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IOrchestratorAgent(ABC):
    """
    Interface for L3 Orchestration Agents.
    
    All orchestration agents must implement these methods
    to ensure consistent behavior across the system.
    """
    
    @abstractmethod

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
        
        Returns:
            Dict with healing summary
        """
        return {"violations": 0, "fixed": 0, "errors": 0}

    def execute(self, context: Any) -> Dict[str, Any]:
        """Execute the orchestration task."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the orchestrator."""
        pass
    
    def get_all_agents(self) -> List[Any]:
        """Get all agents managed by this orchestrator."""
        return []
