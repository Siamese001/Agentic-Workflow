"""W2 — RTC-REQ-055 must remain PARTIAL after W2 ships.

W2 introduces R1B_INTEGRATED_RUNTIME_PROOF and flips RTC-REQ-056 to
ACCEPTED. None of this is allowed to retroactively certify the legacy
dense-only RTC-REQ-055 row, which still gates on
R1B_PRODUCTION_THRESHOLD_PROOF (CALIBRATION_GAP, pinned by W1p4).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.r1b_subclaim_schema import (
    GATED_ROWS,
    LEGACY_RTC_REQ_055_SUBCLAIMS,
)


class TestRTC055Stays:
    def test_rtc_req_055_still_gates_on_legacy_set(self):
        gating = GATED_ROWS["RTC-REQ-055"]["gating_subclaims"]
        assert gating == LEGACY_RTC_REQ_055_SUBCLAIMS
        assert "R1B_PRODUCTION_THRESHOLD_PROOF" in gating

    def test_rtc_req_055_does_not_gate_on_integrated_runtime_proof(self):
        gating = GATED_ROWS["RTC-REQ-055"]["gating_subclaims"]
        assert "R1B_INTEGRATED_RUNTIME_PROOF" not in gating
        assert "R1B_SAFE_REUSE_COMPOSITE_PROOF" not in gating

    def test_overrides_show_055_partial(self):
        ov_path = REPO_ROOT / "artifacts" / "certification" / "runtime_evidence_overrides.json"
        ov = json.loads(ov_path.read_text(encoding="utf-8"))
        assert ov["final_acceptance_status"]["RTC-REQ-055"] == "PARTIAL"
        # The acceptance caveat MUST still surface the threshold gap.
        caveat = ov["acceptance_caveat"]["RTC-REQ-055"]
        assert "PRODUCTION_THRESHOLD_PROOF" in caveat or "CALIBRATION_GAP" in caveat


class TestRTC056FlippedIndependently:
    def test_rtc_req_056_accepted_at_e6(self):
        ov = json.loads((REPO_ROOT / "artifacts" / "certification"
                         / "runtime_evidence_overrides.json").read_text(encoding="utf-8"))
        assert ov["final_acceptance_status"]["RTC-REQ-056"] == "ACCEPTED"
        assert ov["actual_proof_depth"]["RTC-REQ-056"] == "E6_INTEGRATED_RUNTIME_PROOF"

    def test_rtc_req_056_does_not_inherit_threshold_gap(self):
        gating = GATED_ROWS["RTC-REQ-056"]["gating_subclaims"]
        assert "R1B_INTEGRATED_RUNTIME_PROOF" in gating
        assert "R1B_SAFE_REUSE_COMPOSITE_PROOF" in gating
        # Threshold proof must NOT be in the gating set.
        assert "R1B_PRODUCTION_THRESHOLD_PROOF" not in gating
        assert "R1B_DENSE_SIMILARITY_COMPOSITION_PROOF" not in gating


class TestRTC059Unchanged:
    def test_rtc_req_059_accepted(self):
        ov = json.loads((REPO_ROOT / "artifacts" / "certification"
                         / "runtime_evidence_overrides.json").read_text(encoding="utf-8"))
        assert ov["final_acceptance_status"]["RTC-REQ-059"] == "ACCEPTED"
