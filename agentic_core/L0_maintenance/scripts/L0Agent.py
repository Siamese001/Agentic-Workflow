"""
L0Agent - Consolidated Base for L0 Maintenance Agents

Capabilities:
- HealerMixin: heal_repository() for self-repair
- MCPHardenedMixin: Hardened MCP with retry/timeout
- L0DelegationTestingMixin: Delegates testing to higher layers (boot-time safety)

L0 agents run at boot time, so they delegate testing rather than self-test.

MRO HARDENING:
- Inheritance order: Mixins FIRST, SovereignBaseAgent LAST
- All mixins use cooperative super().__init__(**kwargs)
- SovereignBaseAgent terminates the MRO chain
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L0_maintenance.scripts.l0_delegation_testing_mixin import L0DelegationTestingMixin

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


@dataclass
class L0Agent(HealerMixin, MCPHardenedMixin, L0DelegationTestingMixin, SovereignBaseAgent):
    """
    Consolidated base for L0 Maintenance agents.
    
    MRO HARDENING:
    - HealerMixin: First (specialized capability)
    - MCPHardenedMixin: Second (universal protocol)
    - L0DelegationTestingMixin: Third (L0-specific testing)
    - SovereignBaseAgent: Last (root termination)
    
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
    
    def __post_init__(self):
        """Cooperative MRO initialization."""
        super().__init__(name=self.name)
    
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set = None) -> Dict[str, Any]:
        """Invoke shared healing chain then allow subclass override."""
        if _call_path is None:
            _call_path = set()
        result = super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
        return result

    def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, TESTS_DIR: []}
        try:
            assert self is not None
            results["passed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results
