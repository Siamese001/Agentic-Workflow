"""Sovereign Layer: L1_cognition
[SIMPLIFIED] Imports guarded to prevent cascading failures during agent discovery.
"""

from typing import Any, Dict, List, Optional, Protocol

# [GUARDED IMPORTS] Only import modules that exist and are stable
try:
    from AgenticCore.L1_cognition.thought_engine.agent_registry_enums import (
        AgentCapability,
        AgentStatus,
    )
except ImportError:
    AgentCapability = None
    AgentStatus = None

__all__ = ['AgentCapability', 'AgentStatus']
