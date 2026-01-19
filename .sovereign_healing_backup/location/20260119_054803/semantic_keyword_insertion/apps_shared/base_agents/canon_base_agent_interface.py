from __future__ import annotations
"""
Sovereign Interface: Canon Base Agent
Neutral contract for all canon agents - shared across bounded contexts.
Phase 9: DDD Remediation (Dec 26, 2025)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

# NAMING FIXED: CanonBaseAgentInterface → CanonBaseAgentInterface
class CanonBaseAgentInterface(MCPHardenedMixin, HealerMixin, ABC):
    pass

# Alias for backward compatibility

class CanonBaseAgentInterfaceImpl(MCPHardenedMixin, HealerMixin, ABC):
    """Sovereign interface for all canon agents — shared across contexts."""
    
    @abstractmethod
    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute primary mission."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of supported capabilities."""
        pass
    
    @abstractmethod
    def validate_state(self) -> bool:
        """Validate internal agent state."""
        pass