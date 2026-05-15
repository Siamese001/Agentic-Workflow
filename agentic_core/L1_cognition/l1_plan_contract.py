"""L1 Plan Contract — LEGACY_SHIM

This module provides backward compatibility for the L1Planner symbol.
The functional implementation has been removed; instantiation now raises RuntimeError.

MIGRATION GUIDE:
- For apps_rg: Use apps_rg.runtime.bindings.l1_binding.l1_plan_apps_rg()
- For generic contract work: Use agentic_core.runtime.contracts.l1_plan_contract.L1PlanContract

LEGACY_SHIM: This module exists solely to provide import compatibility during migration.
No active app logic remains here. See plan p3.1_apps-rg-l1-contract-wiring-3e7f92.md for details.
"""

from __future__ import annotations

# Import kept for type annotation compatibility only
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract


class L1Planner:
    """LEGACY_SHIM: L1Planner is deprecated and must not be used.

    This class exists for backward compatibility imports only.
    Instantiation raises RuntimeError directing callers to the correct replacement.

    Migration paths:
    - apps_rg tasks: Use apps_rg.runtime.bindings.l1_binding.l1_plan_apps_rg()
    - Generic planning: Use agentic_core.runtime.contracts.l1_plan_contract.L1PlanContract directly
    """

    def __init__(self) -> None:
        """Raise RuntimeError with migration instructions."""
        raise RuntimeError(
            "L1Planner is deprecated and must not be used.\n"
            "For apps_rg, use: apps_rg.runtime.bindings.l1_binding.l1_plan_apps_rg\n"
            "For generic contract work, use: "
            "agentic_core.runtime.contracts.l1_plan_contract.L1PlanContract"
        )

    def plan(self, *args, **kwargs) -> L1PlanContract:
        """Stub method that always raises RuntimeError."""
        raise RuntimeError(
            "L1Planner.plan() is deprecated. Use l1_plan_apps_rg() or L1PlanContract directly."
        )
