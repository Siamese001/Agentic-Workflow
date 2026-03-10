"""
Healer Registry — Declarative mapping of check_id to healer function.

Each healer receives the full check dict from the guardian aggregate
and returns a HealCheckResult. Healers may accept optional keyword
arguments (repo_root, apply) for mutating mode support.
"""

from __future__ import annotations

from typing import Callable

from agentic_core.L2_execution.healers.architecture_governance_healer import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    heal_import_compliance,
    heal_layer_gravity,
)
from agentic_core.L2_execution.healers.architecture_governor_healer import (
    heal_architecture_governance,
)
from agentic_core.L2_execution.healers.classification_compliance_healer import (
    heal_naming_compliance,
    heal_territory_compliance,
)
from agentic_core.L2_execution.healers.drift_detection_healer import (
    heal_guardian_drift_detection,
)
from agentic_core.L2_execution.healers.file_classification_healer import (
    heal_file_classification,
)
from agentic_core.L2_execution.healers.filesystem_ssot_healer import (
    heal_filesystem_ssot_drift,
)
from agentic_core.L2_execution.healers.gravity_leak_healer import (
    heal_gravity_violations,
)
from agentic_core.L2_execution.healers.hierarchy_agent_healer import (
    heal_hierarchy_violations,
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
    "filesystem_ssot_drift": heal_filesystem_ssot_drift,
    "hierarchy_violations": heal_hierarchy_violations,
    "architecture_governance": heal_architecture_governance,
    "gravity_violations": heal_gravity_violations,
    "file_classification": heal_file_classification,
}

__all__ = ["HealerFn", "HEALER_REGISTRY"]
