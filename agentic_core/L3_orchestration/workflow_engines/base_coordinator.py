"""
Base Coordinator Class

Provides the base interface and common functionality for all specialized coordinators.
Each coordinator owns a specific orchestration domain with clear responsibilities.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time
import asyncio

from .execution_strategy import WorkflowContext, WorkflowResult, ExecutionStatus


@dataclass
class CoordinatorCapability:
    """Describes a coordinator capability."""
    name: str
    description: str
    workflow_types: List[str]
    priority: int = 0


class WorkflowCoordinator(ABC):
    """
    Base coordinator for specialized orchestration domains.
    
    Each coordinator:
    - Owns a specific domain (RL, Territory, MCP, etc.)
    - Has clear responsibilities
    - Can be registered with UnifiedWorkflowEngine
    - Supports async coordination
    """
    
    def __init__(self, name: str):
        """Initialize coordinator."""
        self.name = name
        self.enabled = True
        self.coordinations = 0
        self.successes = 0
        self.failures = 0
        self.total_time = 0.0
    
    @abstractmethod
    async def coordinate(self, context: WorkflowContext) -> WorkflowResult:
        """
        Execute coordination logic.
        
        Args:
            context: Workflow context
            
        Returns:
            Workflow result
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[CoordinatorCapability]:
        """
        Return coordinator capabilities.
        
        Returns:
            List of capabilities
        """
        pass
    
    @abstractmethod
    def can_handle(self, workflow_type: str) -> bool:
        """
        Check if coordinator can handle workflow type.
        
        Args:
            workflow_type: Type of workflow
            
        Returns:
            True if coordinator can handle
        """
        pass
    
    async def safe_coordinate(self, context: WorkflowContext) -> WorkflowResult:
        """
        Safe coordination with metrics tracking.
        
        Args:
            context: Workflow context
            
        Returns:
            Workflow result
        """
        start_time = time.time()
        self.coordinations += 1
        
        try:
            result = await self.coordinate(context)
            
            if result.status == ExecutionStatus.COMPLETED:
                self.successes += 1
            else:
                self.failures += 1
            
            return result
        except Exception as e:
            self.failures += 1
            return WorkflowResult(
                workflow_id=context.workflow_id,
                status=ExecutionStatus.FAILED,
                error=f"Coordinator {self.name} failed: {str(e)}"
            )
        finally:
            self.total_time += time.time() - start_time
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get coordinator statistics."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "coordinations": self.coordinations,
            "successes": self.successes,
            "failures": self.failures,
            "success_rate": (self.successes / self.coordinations * 100) if self.coordinations > 0 else 0,
            "total_time": self.total_time,
            "avg_time": (self.total_time / self.coordinations) if self.coordinations > 0 else 0
        }
    
    def enable(self) -> None:
        """Enable coordinator."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable coordinator."""
        self.enabled = False


class CoordinatorRegistry:
    """Registry for workflow coordinators."""
    
    def __init__(self):
        """Initialize registry."""
        self.coordinators: Dict[str, WorkflowCoordinator] = {}
    
    def register(self, coordinator: WorkflowCoordinator) -> None:
        """Register coordinator."""
        self.coordinators[coordinator.name] = coordinator
    
    def unregister(self, name: str) -> None:
        """Unregister coordinator."""
        if name in self.coordinators:
            del self.coordinators[name]
    
    def get(self, name: str) -> Optional[WorkflowCoordinator]:
        """Get coordinator by name."""
        return self.coordinators.get(name)
    
    def get_for_workflow(self, workflow_type: str) -> Optional[WorkflowCoordinator]:
        """Get coordinator that can handle workflow type."""
        for coordinator in self.coordinators.values():
            if coordinator.enabled and coordinator.can_handle(workflow_type):
                return coordinator
        return None
    
    def get_all(self) -> List[WorkflowCoordinator]:
        """Get all coordinators."""
        return list(self.coordinators.values())
    
    def get_enabled(self) -> List[WorkflowCoordinator]:
        """Get enabled coordinators."""
        return [c for c in self.coordinators.values() if c.enabled]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_coordinators": len(self.coordinators),
            "enabled_coordinators": len([c for c in self.coordinators.values() if c.enabled]),
            "coordinators": {name: c.get_statistics() for name, c in self.coordinators.items()}
        }


# Global registry
coordinator_registry = CoordinatorRegistry()
