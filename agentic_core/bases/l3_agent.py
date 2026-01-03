"""
L3Agent - Consolidated Base for L3 Orchestration Agents

Capabilities:
- HealerMixin: heal_repository() for self-repair
- MCPHardenedMixin: Hardened MCP with retry/timeout
- L3SubatomicTestingMixin: Orchestration/CRITIQUE hop testing

L3 agents handle orchestration - coordinating workflows, managing plans.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.workflow_engines.l3_subatomic_testing_mixin import L3SubatomicTestingMixin


@dataclass
class L3Agent(HealerMixin, MCPHardenedMixin, L3SubatomicTestingMixin):
    """
    Consolidated base for L3 Orchestration agents.
    
    Guaranteed Capabilities:
    - heal_repository(): Self-repair method
    - _hardened_call(): MCP operations with retry/timeout
    - _run_self_tests(): Subatomic testing with CRITIQUE hop
    
    L3 Table Decision:
    - Basic Self-Testing: YES (plan validation)
    - Delegation to TestSovereigntyAgent: YES (on failure)
    """
    name: str = "L3Agent"
    layer: str = "L3"
    
    def heal_repository(self, dry_run: bool = True) -> Dict[str, Any]:
        """Override in subclass to implement healing logic."""
        return {"status": "not_implemented", "agent": self.name}
    
    async def orchestrate(self, task: Dict) -> Dict:
        """Override in subclass to implement orchestration logic."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        raise NotImplementedError(f"{self.name} must implement orchestrate()")
\nimport logging\n\nLogger = logging.getLogger(__name__)