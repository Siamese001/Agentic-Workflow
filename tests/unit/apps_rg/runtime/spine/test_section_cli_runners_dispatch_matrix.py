"""W4.2 — section CLI runners map to spine entrypoints."""

from __future__ import annotations

import pytest

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.spine import apps_rg_spine_run


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_section_runner_registered(lane: str) -> None:
    assert lane in apps_rg_spine_run._SECTION_RUNNERS
    runner = apps_rg_spine_run._SECTION_RUNNERS[lane]
    assert callable(runner)


def test_runner_count_matches_generated_lanes() -> None:
    assert set(apps_rg_spine_run._SECTION_RUNNERS) == set(GENERATED_LANES)
