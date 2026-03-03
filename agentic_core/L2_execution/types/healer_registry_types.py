"""
Healer Registry — Declarative mapping of check_id to healer function.

Each healer receives the full check dict from the guardian aggregate
and returns a HealCheckResult. Healers may accept optional keyword
arguments (repo_root, apply) for mutating mode support.
"""

from __future__ import annotations

from typing import Callable

from agentic_core.L2_execution.healers.architecture_governance_healer import (
    heal_import_compliance,
    heal_layer_gravity,
)
from agentic_core.L2_execution.healers.classification_compliance_healer import (
    heal_naming_compliance,
    heal_territory_compliance,
)
from agentic_core.L2_execution.healers.drift_detection_healer import (
    heal_guardian_drift_detection,
)
from agentic_core.L2_execution.healers.hierarchy_compliance_healer import (
    heal_missing_structure,
    heal_subfolder_compliance,
)
from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult

HealerFn = Callable[..., HealCheckResult]

HEALER_REGISTRY: dict[str, HealerFn] = {
    "guardian_drift_detection": heal_guardian_drift_detection,
    "naming_compliance": heal_naming_compliance,
    "territory_compliance": heal_territory_compliance,
    "missing_structure": heal_missing_structure,
    "subfolder_compliance": heal_subfolder_compliance,
    "import_compliance": heal_import_compliance,
    "layer_gravity": heal_layer_gravity,
}

__all__ = ["HealerFn", "HEALER_REGISTRY"]
