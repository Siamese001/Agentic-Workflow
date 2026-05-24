"""Contract: all GENERATED_LANES X2/X1D drift CI harness stays green."""

from __future__ import annotations

import pytest

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.sections.executive_summary_x2_x1d_contract import (
    JUDGE_PACKET_REQUIRED_GATE_KEYS,
    assert_executive_summary_x2_x1d_contract,
    judge_packet_pre_x2_gate_keys,
)
from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape
from apps_rg.runtime.sections.section_x2_x1d_contract import (
    all_lane_x2_x1d_specs,
    assert_all_generated_lanes_x2_x1d_contract,
    audit_all_generated_lanes_x2_x1d_drift,
    audit_lane_x2_x1d_drift,
    extract_runtime_x2_gate_ids,
    lane_x2_x1d_spec,
)


def test_all_generated_lanes_x2_x1d_contract_zero_drift() -> None:
    assert_all_generated_lanes_x2_x1d_contract()


def test_executive_summary_extended_contract_zero_drift() -> None:
    assert_executive_summary_x2_x1d_contract()


def test_lane_specs_cover_generated_lanes() -> None:
    specs = {s.section_id for s in all_lane_x2_x1d_specs()}
    assert specs == set(GENERATED_LANES)


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_runtime_emits_ssot_product_shape_gates(lane: str) -> None:
    spec = lane_x2_x1d_spec(lane)
    runtime = extract_runtime_x2_gate_ids(
        x2_module_ref=spec.x2_module_ref,
        x2_run_function=spec.x2_run_function,
    )
    shape = section_product_shape(lane)
    missing = [g for g in shape.required_gate_ids if g not in runtime]
    assert not missing, f"{lane}: SSOT gates missing from {spec.x2_run_function}: {missing}"


@pytest.mark.parametrize("lane", list(GENERATED_LANES))
def test_lane_audit_returns_no_violations(lane: str) -> None:
    assert audit_lane_x2_x1d_drift(lane) == []


def test_global_audit_returns_no_violations() -> None:
    assert audit_all_generated_lanes_x2_x1d_drift() == []


def test_executive_summary_judge_pre_x2_packet_covers_required_gates() -> None:
    keys = judge_packet_pre_x2_gate_keys()
    missing = sorted(JUDGE_PACKET_REQUIRED_GATE_KEYS - keys)
    assert not missing, missing
