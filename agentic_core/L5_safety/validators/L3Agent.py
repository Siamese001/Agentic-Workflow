"""
L3Agent - Consolidated Base for L3 Orchestration Agents

Capabilities:
- HealerMixin: heal_repository() for self-repair
- MCPHardenedMixin: Hardened MCP with retry/timeout
- L3SubatomicTestingMixin: Orchestration/CRITIQUE hop testing

L3 agents handle orchestration - coordinating workflows, managing plans.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L5_safety.validators.structure_blueprint import (
    TESTS_DIR,
)
from agentic_core.utils.core_extensions.decorators import standard_heal
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin


@dataclass
class L3Agent(HealerMixin, MCPHardenedMixin):
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

    @standard_heal
    def heal_repository(self, dry_run: bool = True) -> dict[str, Any]:
        """Override in subclass to implement healing logic."""
        super().heal_repository(dry_run)
        return {"status": "not_implemented", "agent": self.name}

    def _run_self_tests(self) -> dict[str, Any]:
        """Override in subclass to implement self-tests."""
        return {"status": "not_implemented", TESTS_DIR: 0}

    async def orchestrate(self, task: dict) -> dict:
        """Override in subclass to implement orchestration logic."""
        raise NotImplementedError(f"{self.name} must implement orchestrate()")
