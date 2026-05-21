"""Section-rigor SSOT: lane registry aligns with generated_lane_rollup and proof artifacts."""

from __future__ import annotations

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES, REQUIRED_RELATIVE
from tests.unit.apps_rg.section_rigor.lane_registry import (
    COMMON_PROOF_ARTIFACTS,
    lane_specs,
)


def test_lane_specs_cover_all_generated_lanes() -> None:
    spec_lanes = {s.lane for s in lane_specs()}
    assert spec_lanes == set(GENERATED_LANES)


def test_common_proof_artifacts_include_rollup_required_and_c0_metrics() -> None:
    assert set(REQUIRED_RELATIVE).issubset(set(COMMON_PROOF_ARTIFACTS))
    assert "c0_metrics.json" in COMMON_PROOF_ARTIFACTS


def test_each_lane_has_critical_gates_and_brown_targeting() -> None:
    for spec in lane_specs():
        assert spec.critical_gates, spec.lane
        assert "Brown & Brown" in spec.extra_cli_args
        assert spec.provider_mode == "qwen_live"
