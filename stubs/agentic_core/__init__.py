"""
Agentic Core Stub Package - L0-L5 Test Compatibility Layer

PURPOSE:
    Consolidates L0-L5 layer interfaces for broad test compatibility.
    Provides stub implementations of core agentic components when real
    implementations are unavailable or under development.

STATUS: Active - Required for test infrastructure
LAYERS:
    - L0: Maintenance (MissionPlan, SovereignRegistry)
    - L1: Cognition (NervousSystem, OrchestratorConfig)
    - L2: Execution (Tool registry, MCP stubs)
    - L3: Orchestration (Healing, Mission coordination)
    - L4: State (Cache, Vector stores)
    - L5: Safety (Red team, Hallucination detection)

USAGE:
    >>> from stubs.agentic_core import AgenticCore, MissionPlan
    >>> core = AgenticCore()
    >>> result = await core.run("test task")
"""
try:
    from .core import (
        AgenticCore, initialize_core, MCPProtocolHandler,
        SovereignRegistry, MissionPlan, MissionResult, Missing
    )
except ImportError:
    # Fallback stubs if core module has issues
    class AgenticCore: pass
    class MCPProtocolHandler: pass
    class SovereignRegistry: pass
    class MissionPlan: pass
    class MissionResult: pass
    class Missing: pass
    def initialize_core(): pass

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
