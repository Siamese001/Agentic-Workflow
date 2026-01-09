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
