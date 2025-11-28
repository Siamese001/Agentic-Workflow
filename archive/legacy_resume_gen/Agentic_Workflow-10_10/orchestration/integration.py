"""
Orchestration layer integration utilities.

This module provides integration functionality for orchestration operations,
connecting different components and managing cross-cutting concerns.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass

# Import WorkflowExecutionConfig from core/integration for backward compatibility
from core.integration import WorkflowExecutionConfig


@dataclass
class IntegrationConfig:
    """Configuration for orchestration integration."""
    enabled_components: List[str]
    connection_settings: Dict[str, Any]
    retry_policy: Dict[str, Any]


class OrchestrationIntegrator:
    """
    Integrates orchestration components and manages cross-cutting concerns.
    
    Provides integration between different orchestration modules and
    handles component lifecycle management.
    """
    
    def __init__(self, config: Optional[IntegrationConfig] = None):
        self.config = config or IntegrationConfig(
            enabled_components=[],
            connection_settings={},
            retry_policy={}
        )
        self._components: Dict[str, Any] = {}
    
    def register_component(self, name: str, component: Any) -> None:
        """Register a component for integration."""
        self._components[name] = component
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get a registered component."""
        return self._components.get(name)
    
    def integrate(self) -> bool:
        """Perform integration between registered components."""
        # Basic integration logic
        for component_name in self.config.enabled_components:
            if component_name not in self._components:
                return False
        return True


# Global integrator instance
default_integrator = OrchestrationIntegrator()


def get_integrator() -> OrchestrationIntegrator:
    """Get the default orchestration integrator."""
    return default_integrator


# Re-export functions from core.integration for backward compatibility
from core.integration import execute_workflow, create_workflow_context
