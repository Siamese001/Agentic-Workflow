"""Section-scoped runtime proof helpers (neutral of ``runtime.dispatch``)."""

from apps_rg.runtime.section_proof.mock_runtime_proof_policy import (
    MOCK_JUDGES_REJECT_EXIT_CODE,
    allow_non_allow_exit_zero_ok,
    attach_lane_proof_bundle_fields,
    compute_lane_proof_bundle,
    emit_mock_judges_blocked_stderr,
    infer_product_quality_blocked_or_mock,
    mock_judges_blocked_before_run,
)

__all__ = [
    "MOCK_JUDGES_REJECT_EXIT_CODE",
    "allow_non_allow_exit_zero_ok",
    "attach_lane_proof_bundle_fields",
    "compute_lane_proof_bundle",
    "emit_mock_judges_blocked_stderr",
    "infer_product_quality_blocked_or_mock",
    "mock_judges_blocked_before_run",
]
