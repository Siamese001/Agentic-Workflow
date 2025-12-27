"""
Sovereign Stub for agentic_core (Dec 27, 2025)
Standardizes the interface for L1-L4 layers.
"""
from .core import (
    AgenticCore, 
    initialize_core, 
    MCPProtocolHandler,
    SovereignRegistry,
    MissionPlan,
    MissionResult,
    Missing
)

__all__ = [
    "AgenticCore",
    "initialize_core",
    "MCPProtocolHandler",
    "SovereignRegistry",
    "MissionPlan",
    "MissionResult",
    "Missing",
]
