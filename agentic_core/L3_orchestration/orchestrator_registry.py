"""
Orchestrator Registry - SSOT for Orchestrator Access
=====================================================

Provides a single entry point for obtaining orchestrator instances.
All orchestration requests should go through this registry.

Phase 2 Enhancement (Jan 19, 2026):
- Factory pattern for mode-based orchestrator instantiation
- All modes route to UnifiedOrchestratorAgent
- Deprecation warnings for legacy class usage
- Type-safe IOrchestratorAgent return type

Usage:
    from agentic_core.L3_orchestration.orchestrator_registry import get_orchestrator
    
    orchestrator = get_orchestrator("healing")
    result = orchestrator.run_mission(["BiasAuditorAgent"], dry_run=True)
"""

import warnings
from typing import Dict, Optional, Type

from agentic_core.L3_orchestration.UnifiedOrchestratorAgent import UnifiedOrchestratorAgent
from agentic_core.L3_orchestration.interfaces import IOrchestratorAgent


# Singleton instance
_unified_orchestrator: Optional[UnifiedOrchestratorAgent] = None


def get_orchestrator(mode: str = "unified", **kwargs) -> IOrchestratorAgent:
    """
    Factory function: Single entry point for orchestration.
    Replaces direct instantiation of legacy orchestrator classes.
    
    All modes now return the UnifiedOrchestratorAgent as the SSOT.
    The mode parameter configures the orchestrator's behavior.
    
    Args:
        mode: Orchestration mode. Supported values:
            - "unified" (default): Full orchestration capabilities
            - "healing": Focus on heal_repository operations
            - "compliance": Focus on compliance validation
            - "ssot": Focus on SSOT enforcement
            - "full": Run all operations (alias for unified)
        **kwargs: Additional arguments passed to orchestrator constructor
    
    Returns:
        IOrchestratorAgent instance (UnifiedOrchestratorAgent)
    
    Raises:
        ValueError: If mode is not recognized
    """
    # Valid modes
    valid_modes = {"unified", "healing", "compliance", "ssot", "full"}
    
    if mode not in valid_modes:
        raise ValueError(
            f"Unknown orchestrator mode: '{mode}'. "
            f"Available modes: {sorted(valid_modes)}"
        )
    
    # Create new instance with specified mode
    # Note: We don't use singleton here to allow mode-specific instances
    return UnifiedOrchestratorAgent(mode=mode, **kwargs)


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
