"""Backward-compatible re-exports — prefer test_section_x2_x1d_drift_ci.py."""

from tests._apps_contract.test_section_x2_x1d_drift_ci import (  # noqa: F401
    test_all_generated_lanes_x2_x1d_contract_zero_drift,
    test_executive_summary_extended_contract_zero_drift,
    test_executive_summary_judge_pre_x2_packet_covers_required_gates,
    test_global_audit_returns_no_violations,
    test_lane_audit_returns_no_violations,
    test_lane_specs_cover_generated_lanes,
    test_runtime_emits_ssot_product_shape_gates,
)
