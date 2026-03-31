"""ADG Repair Orchestrator Package.

Provides automated detection and repair of ADG deficiencies.

Usage:
    from tools.adg.repair import ADGRepairOrchestrator

    orchestrator = ADGRepairOrchestrator(
        adg_dir=Path("artifacts/adg"),
        timestamp="03122026_0512"
    )
    result = orchestrator.run(dry_run=True)
    orchestrator.print_summary()
"""

from .base_rule import BaseRepairRule
from .repair_orchestrator import ADGRepairOrchestrator
from .rule_engine import RuleEngine, repair_rule
from .types import (
    Deficiency,
    FixCategory,
    FixResult,
    RepairRunResult,
    RuleMatch,
)

__all__ = [
    "ADGRepairOrchestrator",
    "BaseRepairRule",
    "Deficiency",
    "FixCategory",
    "FixResult",
    "RepairRunResult",
    "repair_rule",
    "RuleEngine",
    "RuleMatch",
]
