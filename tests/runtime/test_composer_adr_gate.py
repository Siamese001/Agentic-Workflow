"""W1 phase 4 — composer ADR gate for R1B_PRODUCTION_THRESHOLD_PROOF."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.compose_semantic_cache_subclaims import (  # noqa: E402
    _map_threshold_proof_with_adr_gate,
)


BASE_THRESHOLD_EV_CALIBRATION_GAP = {
    "threshold_subclaim_status": "CALIBRATION_GAP",
    "rationale": "baseline calibration reports FP>0 at production threshold",
}
BASE_THRESHOLD_EV_PASS = {
    "threshold_subclaim_status": "PASS",
    "rationale": "baseline calibration reports FP=0 at production threshold",
}
BASE_THRESHOLD_EV_INFRA_GAP = {
    "threshold_subclaim_status": "INFRASTRUCTURE_GAP",
    "rationale": "BGE-M3 not operational",
}
BASE_THRESHOLD_EV_OVERRIDE = {
    "threshold_subclaim_status": "OVERRIDE_PRESENT",
    "rationale": "threshold override env var active without ADR",
}


def _make_adr(
    approval: str = "PENDING_APPROVAL",
    impl: str = "PROPOSED_NOT_APPLIED",
    applied: bool = False,
    recommended: float | None = 0.85,
):
    return {
        "adr_id": "SEMCACHE-THRESH-001",
        "recommended_threshold": recommended,
        "owner_approval": {"status": approval},
        "implementation_status": impl,
        "config_binding": {"applied": applied},
    }


def _make_sweep_fp0_at(t: float):
    return {
        "metrics_table": [
            {"threshold": t, "fp": 0, "unsafe_fp_count": 0},
            {"threshold": 0.95, "fp": 2, "unsafe_fp_count": 2},
        ],
    }


def _make_sweep_fp_nonzero_at(t: float):
    return {
        "metrics_table": [
            {"threshold": t, "fp": 3, "unsafe_fp_count": 3},
        ],
    }


class TestBranchOverridePresent:
    def test_override_blocks_regardless_of_adr(self):
        status, notes = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_OVERRIDE,
            adr_ev=_make_adr("APPROVED", "APPLIED", True, 0.85),
            sweep_ev=_make_sweep_fp0_at(0.85),
            configured_threshold=0.85,
        )
        assert status == "BLOCKED"
        assert "OVERRIDE" in notes


class TestBranchInfraGap:
    def test_infra_gap_short_circuits(self):
        status, _ = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_INFRA_GAP,
            adr_ev=_make_adr("APPROVED", "APPLIED", True, 0.85),
            sweep_ev=_make_sweep_fp0_at(0.85),
            configured_threshold=0.85,
        )
        assert status == "INFRASTRUCTURE_GAP"


class TestBranchNoADR:
    def test_no_adr_calibration_gap_stays_gap(self):
        status, _ = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_CALIBRATION_GAP,
            adr_ev=None,
            sweep_ev=None,
            configured_threshold=0.95,
        )
        assert status == "CALIBRATION_GAP"

    def test_no_adr_calibration_pass_becomes_pass(self):
        """Legacy W1p3 path — calibration-at-SSOT PASS is valid without ADR."""
        status, _ = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_PASS,
            adr_ev=None,
            sweep_ev=None,
            configured_threshold=0.95,
        )
        assert status == "PASS"


class TestBranchADRPending:
    def test_pending_approval_stays_calibration_gap(self):
        status, notes = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_CALIBRATION_GAP,
            adr_ev=_make_adr("PENDING_APPROVAL", "PROPOSED_NOT_APPLIED", False, 0.85),
            sweep_ev=_make_sweep_fp0_at(0.85),
            configured_threshold=0.95,
        )
        assert status == "CALIBRATION_GAP"
        assert "PENDING_APPROVAL" in notes or "not APPROVED" in notes

    def test_null_recommendation_stays_calibration_gap(self):
        """Honest NO_SAFE_THRESHOLD_FOUND case (W1p4 actual result)."""
        status, _ = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_CALIBRATION_GAP,
            adr_ev=_make_adr("PENDING_APPROVAL", "PROPOSED_NOT_APPLIED", False, None),
            sweep_ev=None,
            configured_threshold=0.95,
        )
        assert status == "CALIBRATION_GAP"


class TestBranchApprovedNotApplied:
    def test_approved_not_applied_is_partial(self):
        status, notes = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_CALIBRATION_GAP,
            adr_ev=_make_adr("APPROVED", "PROPOSED_NOT_APPLIED", False, 0.85),
            sweep_ev=_make_sweep_fp0_at(0.85),
            configured_threshold=0.95,
        )
        assert status == "PARTIAL"
        assert "applied=False" in notes or "not been deployed" in notes.lower()


class TestBranchDriftDetected:
    def test_drift_threshold_mismatch_is_partial(self):
        status, notes = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_CALIBRATION_GAP,
            adr_ev=_make_adr("APPROVED", "APPLIED", True, 0.85),
            sweep_ev=_make_sweep_fp0_at(0.85),
            configured_threshold=0.90,  # different from approved 0.85
        )
        assert status == "PARTIAL"
        assert "DRIFT_DETECTED" in notes

    def test_drift_sweep_fp_nonzero_is_partial(self):
        status, notes = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_CALIBRATION_GAP,
            adr_ev=_make_adr("APPROVED", "APPLIED", True, 0.85),
            sweep_ev=_make_sweep_fp_nonzero_at(0.85),
            configured_threshold=0.85,
        )
        assert status == "PARTIAL"
        assert "DRIFT_DETECTED" in notes

    def test_drift_sweep_missing_is_partial(self):
        status, notes = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_CALIBRATION_GAP,
            adr_ev=_make_adr("APPROVED", "APPLIED", True, 0.85),
            sweep_ev=None,
            configured_threshold=0.85,
        )
        assert status == "PARTIAL"
        assert "DRIFT_DETECTED" in notes

    def test_drift_sweep_row_missing_is_partial(self):
        status, notes = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_CALIBRATION_GAP,
            adr_ev=_make_adr("APPROVED", "APPLIED", True, 0.85),
            sweep_ev={"metrics_table": [{"threshold": 0.95, "fp": 0, "unsafe_fp_count": 0}]},
            configured_threshold=0.85,
        )
        assert status == "PARTIAL"
        assert "DRIFT_DETECTED" in notes


class TestBranchFullPass:
    def test_approved_applied_match_fp0_is_pass(self):
        """The ONLY path to PASS via the ADR gate."""
        status, notes = _map_threshold_proof_with_adr_gate(
            BASE_THRESHOLD_EV_CALIBRATION_GAP,  # base may still be gap
            adr_ev=_make_adr("APPROVED", "APPLIED", True, 0.85),
            sweep_ev=_make_sweep_fp0_at(0.85),
            configured_threshold=0.85,
        )
        assert status == "PASS"
        assert "Rule 7" in notes or "ADR gate" in notes


class TestLegacyWrapper:
    def test_legacy_wrapper_still_works(self):
        """The _map_threshold_proof wrapper (used by existing tests) must still dispatch."""
        from scripts.compose_semantic_cache_subclaims import _map_threshold_proof
        status, _ = _map_threshold_proof(BASE_THRESHOLD_EV_CALIBRATION_GAP)
        assert status == "CALIBRATION_GAP"

        status, _ = _map_threshold_proof(BASE_THRESHOLD_EV_PASS)
        assert status == "PASS"

        status, _ = _map_threshold_proof(BASE_THRESHOLD_EV_INFRA_GAP)
        assert status == "INFRASTRUCTURE_GAP"

        status, _ = _map_threshold_proof(BASE_THRESHOLD_EV_OVERRIDE)
        assert status == "BLOCKED"
