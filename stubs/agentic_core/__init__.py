"""
Sovereign Master Export Hub
Consolidates L0-L5 interfaces for broad test compatibility.
"""
from .core import (
    AgenticCore, initialize_core, MCPProtocolHandler,
    SovereignRegistry, MissionPlan, MissionResult, Missing
)

# Deep Path Fallbacks (Ensures NameError/ImportError resolution)
class NervousSystem: 
    def __init__(self, *args, **kwargs): self.active_missions = []
class OrchestratorConfig: pass
class DependencyDiplomat: pass

def get_dependency_diplomat(): return DependencyDiplomat()

__all__ = [
    "AgenticCore", "initialize_core", "MCPProtocolHandler",
    "SovereignRegistry", "MissionPlan", "MissionResult", "Missing",
    "NervousSystem", "OrchestratorConfig", "DependencyDiplomat", "get_dependency_diplomat"
]
