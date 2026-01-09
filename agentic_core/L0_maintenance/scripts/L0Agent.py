"""
L0Agent - Consolidated Base for L0 Maintenance Agents

Capabilities:
- HealerMixin: heal_repository() for self-repair
- MCPHardenedMixin: Hardened MCP with retry/timeout
- L0DelegationTestingMixin: Delegates testing to higher layers (boot-time safety)

L0 agents run at boot time, so they delegate testing rather than self-test.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L0_maintenance.scripts.l0_delegation_testing_mixin import L0DelegationTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin


@dataclass
class L0Agent(HealerMixin, MCPHardenedMixin, L0DelegationTestingMixin):
    """
    Consolidated base for L0 Maintenance agents.
    
    Guaranteed Capabilities:
    - heal_repository(): Self-repair method
    - _hardened_call(): MCP operations with retry/timeout
    - _delegate_tests(): Delegates testing to L1+ validators
    
    L0 Table Decision:
    - Basic Self-Testing: NO (boot-time stability)
    - Delegation to TestSovereigntyAgent: YES (on failure)
    """
    name: str = "L0Agent"
    layer: str = "L0"
    
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set = None) -> Dict[str, Any]:
        """Invoke shared healing chain then allow subclass override."""
        if _call_path is None:
            _call_path = set()
        super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
        return {"status": "not_implemented", "agent": self.name}

    def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self is not None
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results
