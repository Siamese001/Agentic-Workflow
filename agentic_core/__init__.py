"""
agentic_core package initialization.
"""
import importlib
from typing import Any, Optional, Protocol, Dict, List

# Map of names to their module paths for lazy loading
_MODULE_MAP = {
    # L1 Cognition - Core Infrastructure
    "InferenceEngine": "agentic_core.L1_cognition.inference.inference_engine",
    "SPIFFEManager": "agentic_core.L1_cognition.identity.spiffe_manager_impl",
    "SignalContext": "agentic_core.L1_cognition.context.signal_context",
    "CanonBaseAgent": "agentic_core.L1_cognition.canon_base_agent",
    "ReflectionAgent": "agentic_core.L1_cognition.reflection_agent",
    "SovereignCognitivePlane": "agentic_core.L1_cognition.sovereign_cognitive_plane",
    
    # L2 Execution - Structured Engines
    "StructuredEngine": "agentic_core.L2_execution.structured_engine",
    "GitAgent": "agentic_core.L2_execution.git_agent",
    "ToolsmithAgent": "agentic_core.L2_execution.toolsmith_agent",
    
    # L3 Orchestration - Types and Core
    "ExecutionPhase": "agentic_core.L3_orchestration.orchestration_types",
    "ExecutionPhaseSignal": "agentic_core.L3_orchestration.orchestration_types",
    "WorkflowSnapshot": "agentic_core.L3_orchestration.orchestration_types",
    
    # Agent Registry
    "AgentRegistry": "agentic_core.L1_cognition.discovery.agent_registry",
    "AgentCategory": "agentic_core.L1_cognition.discovery.agent_registry_enums",
    "AgentCapability": "agentic_core.L1_cognition.discovery.agent_registry_enums",
    
    # Tools
    "tools": "agentic_core.tools.core",
}

def __getattr__(name: str) -> Any:
    """
    Lazy-load core components to prevent circular gravity leaks 
    during initial package discovery.
    """
    if name in _MODULE_MAP:
        module_path = _MODULE_MAP[name]
        module = importlib.import_module(module_path)
        
        # Handle both module-level imports and class-level exports
        if hasattr(module, name):
            return getattr(module, name)
        return module

    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = list(_MODULE_MAP.keys())