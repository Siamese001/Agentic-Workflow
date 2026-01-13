"""
IOrchestratorAgent: Abstract Base Class defining the orchestration contract.
Restored: 2026-01-13 | Version: 1.1.0 (Hardened)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.common.healing.healer_mixin import HealerMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin

class ExecutionPhase(Enum):
    PLANNING = "planning"
    EXECUTION = "execution"
    OBSERVATION = "observation"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ExecutionContext:
    task_id: str
    input_data: Dict[str, Any]
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class IOrchestratorAgent(ABC, MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    Abstract interface for all L3 Orchestrators.
    Enforces the Think-Act-Observe cycle.
    
    Inherits heal_repository from HealerMixin (Canon Key 51 compliance).
    """

    @abstractmethod
    def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """Primary entry point for orchestration."""
        pass

    @abstractmethod
    def think(self, context: ExecutionContext) -> Dict[str, Any]:
        """Cognitive planning phase."""
        pass

    @abstractmethod
    def act(self, actions: List[Dict[str, Any]], context: ExecutionContext) -> List[Dict[str, Any]]:
        """Action execution phase."""
        pass

    @abstractmethod
    def observe(self, action_results: List[Dict[str, Any]], context: ExecutionContext) -> Dict[str, Any]:
        """Result interpretation and state update."""
        pass

    @abstractmethod
    def should_continue(self, context: ExecutionContext) -> bool:
        """Evaluates if task objectives have been met."""
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Returns serializable state of the orchestrator."""
        pass
