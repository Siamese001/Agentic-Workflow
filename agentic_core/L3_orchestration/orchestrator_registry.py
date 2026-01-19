"""
Orchestrator Registry - SSOT for Orchestrator Access
=====================================================

Provides a single entry point for obtaining orchestrator instances.
All orchestration requests should go through this registry.

Usage:
    from agentic_core.L3_orchestration.orchestrator_registry import get_orchestrator
    
    orchestrator = get_orchestrator("healing")
    result = orchestrator.dispatch("safety", "validate", payload)
"""

import warnings
from typing import Optional

from agentic_core.L3_orchestration.UnifiedOrchestratorAgent import UnifiedOrchestratorAgent


# Singleton instance
_unified_orchestrator: Optional[UnifiedOrchestratorAgent] = None


def get_orchestrator(mode: str = "unified") -> UnifiedOrchestratorAgent:
    """
    Get the appropriate orchestrator for the given mode.
    
    All modes now return the UnifiedOrchestratorAgent as the SSOT.
    Legacy mode names are supported for backward compatibility but
    will trigger deprecation warnings.
    
    Args:
        mode: Orchestration mode. Supported values:
            - "unified" (default): Returns UnifiedOrchestratorAgent
            - "healing": Returns UnifiedOrchestratorAgent (legacy alias)
            - "compliance": Returns UnifiedOrchestratorAgent (legacy alias)
            - "ssot": Returns UnifiedOrchestratorAgent (legacy alias)
            - "full": Returns UnifiedOrchestratorAgent (legacy alias)
    
    Returns:
        UnifiedOrchestratorAgent instance
    
    Raises:
        ValueError: If mode is not recognized
    """
    global _unified_orchestrator
    
    # Legacy mode aliases - all map to UnifiedOrchestratorAgent
    legacy_modes = {
        "healing": "HealingOrchestratorAgent",
        "compliance": "ComplianceOrchestratorAgent", 
        "ssot": "SSOTOrchestratorAgent",
        "full": "FullOrchestratorAgent",
    }
    
    if mode in legacy_modes:
        warnings.warn(
            f"Mode '{mode}' is deprecated. Use 'unified' mode instead. "
            f"The legacy {legacy_modes[mode]} has been consolidated into UnifiedOrchestratorAgent.",
            DeprecationWarning,
            stacklevel=2
        )
    elif mode != "unified":
        raise ValueError(
            f"Unknown orchestrator mode: '{mode}'. "
            f"Supported modes: 'unified', 'healing', 'compliance', 'ssot', 'full'"
        )
    
    # Lazy initialization of singleton
    if _unified_orchestrator is None:
        _unified_orchestrator = UnifiedOrchestratorAgent()
    
    return _unified_orchestrator


def reset_orchestrator() -> None:
    """Reset the singleton orchestrator (for testing purposes)."""
    global _unified_orchestrator
    _unified_orchestrator = None


# Deprecated class aliases for backward compatibility
class SSOTOrchestratorAgent:
    """
    DEPRECATED: Use UnifiedOrchestratorAgent instead.
    
    This class is a deprecated alias that will be removed in a future version.
    """
    def __new__(cls, *args, **kwargs):
        warnings.warn(
            "SSOTOrchestratorAgent is deprecated. Use UnifiedOrchestratorAgent instead. "
            "Import via: from agentic_core.L3_orchestration.UnifiedOrchestratorAgent import UnifiedOrchestratorAgent",
            DeprecationWarning,
            stacklevel=2
        )
        return get_orchestrator("unified")


class HealingOrchestratorAgent:
    """
    DEPRECATED: Use UnifiedOrchestratorAgent instead.
    
    This class is a deprecated alias that will be removed in a future version.
    """
    def __new__(cls, *args, **kwargs):
        warnings.warn(
            "HealingOrchestratorAgent is deprecated. Use UnifiedOrchestratorAgent instead. "
            "Import via: from agentic_core.L3_orchestration.UnifiedOrchestratorAgent import UnifiedOrchestratorAgent",
            DeprecationWarning,
            stacklevel=2
        )
        return get_orchestrator("unified")


class ConsolidatedOrchestratorAgent:
    """
    DEPRECATED: Use UnifiedOrchestratorAgent instead.
    
    This class is a deprecated alias that will be removed in a future version.
    """
    def __new__(cls, *args, **kwargs):
        warnings.warn(
            "ConsolidatedOrchestratorAgent is deprecated. Use UnifiedOrchestratorAgent instead. "
            "Import via: from agentic_core.L3_orchestration.UnifiedOrchestratorAgent import UnifiedOrchestratorAgent",
            DeprecationWarning,
            stacklevel=2
        )
        return get_orchestrator("unified")
