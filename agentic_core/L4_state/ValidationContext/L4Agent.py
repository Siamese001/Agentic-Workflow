"""
L4Agent - Consolidated Base for L4 State Agents

Capabilities:
- HealerMixin: heal_repository() for self-repair
- MCPHardenedMixin: Hardened MCP with retry/timeout
- L4SubatomicTestingMixin: State consistency testing

L4 agents handle state - caching, persistence, memory.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin


@dataclass
class L4Agent(HealerMixin, MCPHardenedMixin):
    """
    Consolidated base for L4 State agents.
    
    Guaranteed Capabilities:
    - heal_repository(): Self-repair method
    - _hardened_call(): MCP operations with retry/timeout
    - _run_self_tests(): Subatomic testing for state consistency
    
    L4 Table Decision:
    - Basic Self-Testing: YES (state consistency, idempotency)
    - Delegation to TestSovereigntyAgent: YES (on failure)
    """
    name: str = "L4Agent"
    layer: str = "L4"
    
    def heal_repository(self, dry_run: bool = True) -> Dict[str, Any]:
        """Override in subclass to implement healing logic."""
        super().heal_repository(dry_run)
        return {"status": "not_implemented", "agent": self.name}
    
    def _run_self_tests(self) -> Dict[str, Any]:
        """Override in subclass to implement self-tests."""
        return {"status": "not_implemented", "tests": 0}
    
    async def update_state(self, task: Dict) -> Dict:
        """Override in subclass to implement state update logic."""
        raise NotImplementedError(f"{self.name} must implement update_state()")
