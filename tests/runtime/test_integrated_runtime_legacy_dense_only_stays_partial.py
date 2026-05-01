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


class TestRTC056HonestInfrastructureGap:
    """Committed state: RTC-REQ-056 is PENDING because the C-primary
    ALLOW-path proof is gated on a live approved SAFE-producing provider
    (anthropic_haiku or local_qwen). The W2 infrastructure is complete
    but mock_safe is NOT authorized for final certification acceptance.

    When a live approved provider becomes available AND the probe writes
    ``c_primary_allow.pass = True`` into path_proofs_ledger.json, RTC-REQ-056
    will flip to ACCEPTED automatically. These assertions encode the
    committed honest state — update them only when that transition is
    intentional and supported by live evidence.
    """

    def test_rtc_req_056_pending_due_to_infrastructure_gap(self):
        ov = json.loads((REPO_ROOT / "artifacts" / "certification"
                         / "runtime_evidence_overrides.json").read_text(encoding="utf-8"))
        # RTC-REQ-056 is either absent (reverting to PENDING default) OR
        # explicitly PENDING/PARTIAL/BLOCKED — but NEVER ACCEPTED without
        # a live approved provider.
        status = ov["final_acceptance_status"].get("RTC-REQ-056")
        assert status in (None, "PENDING", "PARTIAL", "BLOCKED"), (
            f"RTC-REQ-056 must not be ACCEPTED in committed state "
            f"(got {status!r}); mock_safe is MOCK_PROVIDER_ONLY."
        )

    def test_path_proofs_ledger_records_infrastructure_gap(self):
        ledger = json.loads((REPO_ROOT / "artifacts" / "certification"
                             / "integrated_runtime" / "path_proofs_ledger.json"
                             ).read_text(encoding="utf-8"))
        # Fail-closed leg always PASSes — that's the real proof we ship.
        assert ledger["c_primary_fail_closed"]["pass"] is True
        # Allow leg is gated on a live provider; committed default is not-pass.
        # If a live provider is configured, allow_pass may be True; we only
        # assert the ledger structure is present with the expected keys.
        assert "pass" in ledger["c_primary_allow"]
        assert "provider_attempted" in ledger["c_primary_allow"]
        # Structural run must always be labeled STRUCTURAL_ONLY.
        assert ledger["structural_allow_topology"]["match_status"] == "STRUCTURAL_ONLY"

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
