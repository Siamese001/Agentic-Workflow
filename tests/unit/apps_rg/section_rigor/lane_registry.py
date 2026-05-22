"""Re-export rigor SSOT from apps_rg; test-only weak-fail case registry."""

from __future__ import annotations

from typing import Callable

from apps_rg.runtime.rigor.lane_registry import (  # noqa: F401
    C0_CRITICAL_GATES,
    COMMON_PROOF_ARTIFACTS,
    LANE_CRITICAL_GATES,
    LaneRigorSpec,
    ProviderMode,
    STYLE_CRITICAL_GATES,
    UNIVERSAL_CRITICAL_GATES,
    lane_specs,
    spec_for_lane,
)
from dataclasses import dataclass


@dataclass(frozen=True)
class WeakFailCase:
    lane: str
    gate_id: str
    run_gates: Callable[[], list]


def weak_fail_cases() -> tuple[WeakFailCase, ...]:
    """Deliberately weak payloads must fail named gates (unit-level rigor, not CLI)."""
    from tests.unit.apps_rg.section_rigor import weak_payloads as wp

    return wp.all_weak_fail_cases()
