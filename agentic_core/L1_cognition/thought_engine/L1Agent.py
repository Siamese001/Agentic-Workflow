"""
L1Agent - Consolidated Base for L1 Cognition Agents

Capabilities:
- HealerMixin: heal_repository() for self-repair
- MCPHardenedMixin: Hardened MCP with retry/timeout
- L1SubatomicTestingMixin: Thought validation testing

L1 agents handle cognition - thinking, reasoning, understanding.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin


@dataclass
class L1Agent(HealerMixin, MCPHardenedMixin):
    """
    Consolidated base for L1 Cognition agents.
    
    Guaranteed Capabilities:
    - heal_repository(): Self-repair method
    - _hardened_call(): MCP operations with retry/timeout
    
    L1 Table Decision:
    - Basic Self-Testing: YES (thought validation)
    - Delegation to TestSovereigntyAgent: YES (on failure)
    """
    name: str = "L1Agent"
    layer: str = "L1"
    
    def heal_repository(self, dry_run: bool = True) -> Dict[str, Any]:
        """Override in subclass to implement healing logic."""
        super().heal_repository(dry_run)
        return {"status": "not_implemented", "agent": self.name}
    
    def _run_self_tests(self) -> Dict[str, Any]:
        """Override in subclass to implement self-tests."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        return {"status": "not_implemented", "tests": 0}
