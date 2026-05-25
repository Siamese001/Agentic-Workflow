"""Every lane-critical X2 gate must have a weak-fail anchor or a dedicated test reference."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from tests.unit.apps_rg.section_rigor.gate_coverage_registry import (
    SECTION_DEDICATED_TEST_FRAGMENTS,
    RETIRED_GATE_REFS,
    uncovered_critical_gates,
    weak_fail_gate_ids_by_lane,
)
from tests.unit.apps_rg.section_rigor.lane_registry import LANE_CRITICAL_GATES, weak_fail_cases


def _weak_fail_gate_allowed(lane: str, gate_id: str) -> bool:
    critical = LANE_CRITICAL_GATES[lane]
    if gate_id in critical:
        return True
    ref = RETIRED_GATE_REFS.get(gate_id)
    replacement = str(ref.replacement_gate_id or "").strip() if ref else ""
    return bool(replacement and replacement in critical)


REPO_ROOT = Path(__file__).resolve().parents[4]


def test_every_generated_lane_has_critical_gates_and_dedicated_test_fragments() -> None:
    for lane in GENERATED_LANES:
        assert lane in LANE_CRITICAL_GATES, lane
        assert lane in SECTION_DEDICATED_TEST_FRAGMENTS, lane
        assert SECTION_DEDICATED_TEST_FRAGMENTS[lane], lane


def test_weak_fail_cases_reference_valid_lanes_and_critical_gates() -> None:
    for case in weak_fail_cases():
        assert case.lane in GENERATED_LANES
        assert _weak_fail_gate_allowed(case.lane, case.gate_id), (
            f"{case.gate_id} not in critical gates for {case.lane}"
        )


def test_each_lane_has_at_least_one_weak_fail_anchor() -> None:
    weak_by_lane = weak_fail_gate_ids_by_lane()
    for lane in GENERATED_LANES:
        assert weak_by_lane.get(lane), f"{lane} needs at least one weak_fail case"


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_dedicated_test_fragments_exist_on_disk(lane: str) -> None:
    for frag in SECTION_DEDICATED_TEST_FRAGMENTS[lane]:
        path = REPO_ROOT / frag
        assert path.is_file(), f"missing dedicated test file for {lane}: {frag}"


def test_all_lane_critical_gates_have_weak_or_dedicated_coverage() -> None:
    missing = uncovered_critical_gates(REPO_ROOT)
    assert not missing, (
        "Lane-critical gates without weak_fail or dedicated test reference:\n"
        + "\n".join(f"  {lane}: {gate}" for lane, gate in missing)
    )
