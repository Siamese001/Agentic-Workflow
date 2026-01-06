"""
L5Agent - Consolidated Base for L5 Safety Agents

Capabilities:
- HealerMixin: heal_repository() for self-repair
- MCPHardenedMixin: Hardened MCP with retry/timeout
- L5SubatomicTestingMixin: Safety validation testing

L5 agents handle safety - validation, compliance, security.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin


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
    
    def heal_repository(self, dry_run: bool = True) -> Dict[str, Any]:
        """Override in subclass to implement healing logic."""
        super().heal_repository(dry_run)
        return {"status": "not_implemented", "agent": self.name}
    
    def _run_self_tests(self) -> Dict[str, Any]:
        """Override in subclass to implement self-tests."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        return {"status": "not_implemented", "tests": 0}
    
    def validate(self, target: Any) -> Dict[str, Any]:
        """Override in subclass to implement validation logic."""
        raise NotImplementedError(f"{self.name} must implement validate()")
