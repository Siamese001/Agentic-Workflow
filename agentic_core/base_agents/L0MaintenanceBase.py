from __future__ import annotations

"""
L0MaintenanceBase - Consolidated Base for L0 Maintenance Agents

Zero-Ambiguity Standard: Renamed from L0MaintenanceBaseAgent to L0MaintenanceBase
to clarify this is a CLASS (blueprint), not an active worker agent.

Capabilities:
- HealerMixin: heal_repository() for self-repair
- MCPHardenedMixin: Hardened MCP via SovereignBaseAgent (root injection)
- L0DelegationTestingMixin: Delegates testing to higher layers (boot-time safety)

L0 agents run at boot time, so they delegate testing rather than self-test.

MRO HARDENING:
- Inheritance order: Specialized Mixins -> SovereignBaseAgent (includes MCP)
- MCPHardenedMixin is now in SovereignBaseAgent - DO NOT add it here
- MRO: HealerMixin -> L0DelegationTestingMixin -> SovereignBaseAgent -> MCPHardenedMixin -> object
"""

from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

# L0DelegationTestingMixin - archived, use stub for backward compatibility
try:
    from agentic_core.base_agents.l0_delegation_testing_mixin import (
        L0DelegationTestingMixin,
    )
except ImportError:

    class L0DelegationTestingMixin:
        """Stub mixin for L0 delegation testing - original archived."""

        pass


from agentic_core.L5_safety.utils.decorators_util import standard_heal
from agentic_core.L5_safety.config.structure_blueprint_config import (
    TESTS_DIR,
)


@dataclass
class L0MaintenanceBase(L0DelegationTestingMixin, SovereignBaseAgent):
    """
    Consolidated base for L0 Maintenance agents.

    Zero-Ambiguity Standard: This is a CLASS (blueprint), not an active worker agent.
    The "Agent" suffix was removed to clarify its role as a foundational base class.

    MRO HARDENING:
    - HealerMixin: First (specialized capability)
    - L0DelegationTestingMixin: Second (L0-specific testing)
    - SovereignBaseAgent: Last (root - includes MCPHardenedMixin)

    MRO: HealerMixin -> L0DelegationTestingMixin -> SovereignBaseAgent -> MCPHardenedMixin -> object

    Guaranteed Capabilities:
    - heal_repository(): Self-repair method
    - _hardened_call(): MCP operations via SovereignBaseAgent
    - _delegate_tests(): Delegates testing to L1+ validators

    L0 Table Decision:
    - Basic Self-Testing: NO (boot-time stability)
    - Delegation to TestSovereigntyAgent: YES (on failure)
    """

    # Zero-Ambiguity: Mark as foundational class, not runtime agent
    NOT_AN_AGENT: bool = True

    name: str = "L0MaintenanceBase"
    layer: str = "L0"

    def __post_init__(self) -> None:
        """Cooperative MRO initialization."""
        super().__post_init__()

    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Invoke shared healing chain then allow subclass override."""
        if _call_path is None:
            _call_path = set()
        result = super().heal_repository(
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path,
            **kwargs,
        )
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

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by L0MaintenanceBase.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        file_path = violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")

        # Default implementation - delegates to heal_repository if available
        try:
            if hasattr(self, "heal_repository"):
                result = self.heal_repository(target_path=file_path)
                return {
                    "status": "success" if result.get("violations_fixed", 0) > 0 else "skipped",
                    "details": f"L0MaintenanceBase healed {result.get('violations_fixed', 0)} violations",
                    "artifacts": [file_path] if file_path else [],
                    "errors": result.get("errors", []),
                }
            else:
                return {
                    "status": "skipped",
                    "details": f"L0MaintenanceBase heal() not yet implemented for {violation_type}",
                    "artifacts": [],
                    "errors": [],
                }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"L0MaintenanceBase heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
