"""
L2Agent - Consolidated Base for L2 Execution Agents

Capabilities:
- HealerMixin: heal_repository() for self-repair
- MCPHardenedMixin: Hardened MCP with retry/timeout
- SubatomicTestingMixin: Tool execution testing

L2 agents handle execution - running tools, calling APIs.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class L2Agent(HealerMixin, MCPHardenedMixin, SubatomicTestingMixin):
    """
    Consolidated base for L2 Execution agents.
    
    Guaranteed Capabilities:
    - heal_repository(): Self-repair method
    - _hardened_call(): MCP operations with retry/timeout
    - _run_self_tests(): Subatomic testing for tool execution
    
    L2 Table Decision:
    - Basic Self-Testing: YES (tool validation)
    - Delegation to TestSovereigntyAgent: YES (on failure)
    """
    name: str = "L2Agent"
    layer: str = "L2"
    
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set = None) -> Dict[str, Any]:
        """Invoke shared healing chain then allow subclass override."""
        if _call_path is None:
            _call_path = set()
        super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
        return {"status": "not_implemented", "agent": self.name}
