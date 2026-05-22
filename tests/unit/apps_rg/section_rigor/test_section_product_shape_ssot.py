"""Product-shape SSOT aligns with generated lanes, templates, and lane-critical gates."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.section_product_shape_ssot import (
    all_generated_lane_shapes,
    section_product_shape,
)
from tests.unit.apps_rg.section_rigor.lane_registry import LANE_CRITICAL_GATES

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_all_generated_lanes_have_product_shape() -> None:
    shapes = all_generated_lane_shapes()
    assert {s.section_id for s in shapes} == set(GENERATED_LANES)


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_product_shape_required_gates_subset_of_lane_critical(lane: str) -> None:
    shape = section_product_shape(lane)
    critical = LANE_CRITICAL_GATES[lane]
    missing = [g for g in shape.required_gate_ids if g not in critical]
    assert not missing, f"{lane} shape gates not in LANE_CRITICAL_GATES: {missing}"


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_product_shape_template_ref_exists(lane: str) -> None:
    shape = section_product_shape(lane)
    path = REPO_ROOT / shape.template_ref
    assert path.is_file(), f"{lane} template missing: {shape.template_ref}"


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_product_shape_prompt_block_mentions_section(lane: str) -> None:
    from apps_rg.runtime.sections.section_product_shape_ssot import format_product_shape_prompt_block

    block = format_product_shape_prompt_block(lane)
    assert f"section: {lane}" in block
    for gid in section_product_shape(lane).required_gate_ids:
        assert gid in block
