"""
Healer Registry — Declarative mapping of check_id to healer function.

Each healer receives the full check dict from the guardian aggregate
and returns a HealCheckResult. Healers may accept optional keyword
arguments (repo_root, apply) for mutating mode support.
"""

from __future__ import annotations

from typing import Callable

from agentic_core.L2_execution.healers.drift_detection_healer import (
    heal_guardian_drift_detection,
)
from agentic_core.L2_execution.types.heal_contract import HealCheckResult

HealerFn = Callable[..., HealCheckResult]

HEALER_REGISTRY: dict[str, HealerFn] = {
    "guardian_drift_detection": heal_guardian_drift_detection,
}

__all__ = ["HealerFn", "HEALER_REGISTRY"]
