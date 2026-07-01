"""W4.2 — section CLI runners map to spine entrypoints."""

from __future__ import annotations

import pytest

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.spine import section_cli_runners


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_section_runner_registered(lane: str) -> None:
    assert lane in section_cli_runners.SECTION_LANE_RUNNERS
    runner = section_cli_runners.SECTION_LANE_RUNNERS[lane]
    assert callable(runner)


def test_runner_count_matches_generated_lanes() -> None:
    assert set(section_cli_runners.SECTION_LANE_RUNNERS) == set(GENERATED_LANES)
