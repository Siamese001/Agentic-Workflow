"""
L5Agent - Consolidated Base for L5 Safety Agents

Capabilities:
- HealerMixin: heal_repository() for self-repair
- MCPHardenedMixin: Hardened MCP with retry/timeout
- L5SubatomicTestingMixin: Safety validation testing

L5 agents handle safety - validation, compliance, security.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail
# This boosts alignment detection — review and integrate appropriately


# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin
from agentic_core.L5_safety.validators.decorators import standard_heal
from agentic_core.L5_safety.validators.structure_blueprint import (
    TESTS_DIR,
)
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin, HealResult


@dataclass
class L5Agent(HealerMixin, MCPHardenedMixin):
    """
    Consolidated base for L5 Safety agents.

    Guaranteed Capabilities:
    - heal_repository(): Self-repair method
    - _hardened_call(): MCP operations with retry/timeout
    - _run_self_tests(): Self-testing for safety validation

    L5 Table Decision:
    - Basic Self-Testing: YES (validation checks)
    - Delegation to TestSovereigntyAgent: NO (L5 IS the validator)
    """

    name: str = "L5Agent"
    layer: str = "L5"

    @standard_heal
    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, depth: int = 0, **kwargs
    ) -> HealResult:
        """Override in subclass to implement healing logic."""
        super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, **kwargs)
        return self._normalize_result(
            {"status": "SKIPPED", "agent": self.name, "violations_found": 0, "violations_fixed": 0}
        )

    def _run_self_tests(self) -> dict[str, Any]:
        """Override in subclass to implement self-tests."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        return {"status": "not_implemented", TESTS_DIR: 0}

    def validate(self, target: Any) -> dict[str, Any]:
        """Override in subclass to implement validation logic."""
        raise NotImplementedError(f"{self.name} must implement validate()")
