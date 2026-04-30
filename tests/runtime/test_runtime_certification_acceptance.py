"""Tests — Acceptance legality + composition non-promotion (RTC-REQ-004, 005, 111, 127).

Plan: ``.windsurf/plans/runtime-cert-hardened-w0-7e3c9a.md``

Coverage
--------

  - ACCEPTED requires actual_proof_depth >= required_proof_depth (rule §1)
  - DOC_REFERENCE_ONLY rows cannot claim runtime (rule §3 / RTC-REQ-005)
  - E5_COMPOSITION_PROOF cannot satisfy E6/E7/E8/E9 (rule §2 / RTC-REQ-127)
  - PARTIAL requires acceptance_caveat
  - BLOCKED requires blocking_gap
  - Final status must be in ALLOWED_FINAL_STATUSES
  - Acceptance verifier script exits 0 in clean state
  - Acceptance verifier script exits 2 when override forces an illegal state
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.acceptance_validator import (
    ALLOWED_FINAL_STATUSES,
    apply_to_matrix,
    validate_acceptance,
)
from agentic_core.runtime.prove_requirements.matrix_loader import (
    CANONICAL_REQUIREMENT_COUNT,
    load_matrix,
)


class TestAcceptedRequiresStrongProof:
    """Rule §1 / RTC-REQ-004: ACCEPTED requires actual >= required."""

    def test_accepted_with_weak_proof_blocked(self):
        row = {
            "req_id": "TEST-001",
            "claim_type": "INTEGRATED_RUNTIME",
            "required_proof_depth": "E6_INTEGRATED_RUNTIME_PROOF",
        }
        v = validate_acceptance(
            row,
            actual_proof_depth="E2_STATIC_CHECK",
            final_acceptance_status="ACCEPTED",
        )
        assert v.legal is False
        assert "ACCEPTED_WITH_WEAK_PROOF" in v.rule_violations
        assert v.expected_fail_reason == "ACCEPTED_REQUIRES_ACTUAL_GE_REQUIRED"
        assert "E2_STATIC_CHECK" in v.actual_fail_reason
        assert "E6_INTEGRATED_RUNTIME_PROOF" in v.actual_fail_reason

    def test_accepted_with_equal_or_higher_proof_legal(self):
        row = {
            "req_id": "TEST-002",
            "claim_type": "INTEGRATED_RUNTIME",
            "required_proof_depth": "E6_INTEGRATED_RUNTIME_PROOF",
        }
        v = validate_acceptance(
            row,
            actual_proof_depth="E6_INTEGRATED_RUNTIME_PROOF",
            final_acceptance_status="ACCEPTED",
        )
        assert v.legal is True

        v_higher = validate_acceptance(
            row,
            actual_proof_depth="E7_REAL_OTEL_EXPORT",
            final_acceptance_status="ACCEPTED",
        )
        assert v_higher.legal is True

    def test_pending_status_never_violates(self):
        row = {
            "req_id": "TEST-003",
            "claim_type": "OBSERVABILITY_RUNTIME",
            "required_proof_depth": "E7_REAL_OTEL_EXPORT",
        }
        # Default behavior: actual=E0, status=PENDING is legal
        v = validate_acceptance(row)
        assert v.legal is True


class TestCompositionNonPromotion:
    """Rule §2 / RTC-REQ-127: E5_COMPOSITION_PROOF cannot satisfy E6+."""

    @pytest.mark.parametrize("required", [
        "E6_INTEGRATED_RUNTIME_PROOF",
        "E7_REAL_OTEL_EXPORT",
        "E8_REPLAY_DETERMINISM",
        "E9_PRODUCTION_DEPENDENCY_PROOF",
    ])
    def test_e5_cannot_satisfy_runtime_tiers(self, required):
        row = {"req_id": f"TEST-comp-{required}",
               "claim_type": "INTEGRATED_RUNTIME",
               "required_proof_depth": required}
        v = validate_acceptance(
            row,
            actual_proof_depth="E5_COMPOSITION_PROOF",
            final_acceptance_status="ACCEPTED",
        )
        assert v.legal is False
        assert "COMPOSITION_PROOF_CANNOT_PROMOTE" in v.rule_violations

    def test_e5_can_satisfy_e5_required(self):
        row = {"req_id": "TEST-comp-ok",
               "claim_type": "COMPOSITION_RUNTIME",
               "required_proof_depth": "E5_COMPOSITION_PROOF"}
        v = validate_acceptance(
            row,
            actual_proof_depth="E5_COMPOSITION_PROOF",
            final_acceptance_status="ACCEPTED",
        )
        assert v.legal is True


class TestDocReferenceOnly:
    """RTC-REQ-005: DOC_REFERENCE_ONLY rows cannot claim runtime."""

    def test_doc_reference_only_blocks_runtime_flag(self):
        row = {"req_id": "TEST-doc",
               "claim_type": "DOC_REFERENCE_ONLY",
               "required_proof_depth": "E1_SOURCE_MAPPING"}
        v = validate_acceptance(row, runtime_claim_allowed=True)
        assert v.legal is False
        assert "DOC_REFERENCE_ONLY_CANNOT_CLAIM_RUNTIME" in v.rule_violations
        assert v.expected_fail_reason == "DOC_REFERENCE_ONLY_RUNTIME_FORBIDDEN"


class TestPartialAndBlockedRequireText:
    """RTC-REQ-002: PARTIAL needs caveat, BLOCKED needs gap."""

    def test_partial_without_caveat_blocked(self):
        row = {"req_id": "T-partial", "claim_type": "STATIC_ENFORCEMENT",
               "required_proof_depth": "E2_STATIC_CHECK"}
        v = validate_acceptance(row, final_acceptance_status="PARTIAL")
        assert v.legal is False
        assert "PARTIAL_WITHOUT_CAVEAT" in v.rule_violations

    def test_blocked_without_gap_blocked(self):
        row = {"req_id": "T-blocked", "claim_type": "STATIC_ENFORCEMENT",
               "required_proof_depth": "E2_STATIC_CHECK"}
        v = validate_acceptance(row, final_acceptance_status="BLOCKED")
        assert v.legal is False
        assert "BLOCKED_WITHOUT_BLOCKING_GAP" in v.rule_violations

    def test_partial_with_caveat_legal(self):
        row = {"req_id": "T-partial-ok", "claim_type": "STATIC_ENFORCEMENT",
               "required_proof_depth": "E2_STATIC_CHECK"}
        v = validate_acceptance(row, final_acceptance_status="PARTIAL",
                                acceptance_caveat="evidence pending W1")
        assert v.legal is True


class TestFinalStatusEnum:
    def test_invalid_final_status_blocked(self):
        row = {"req_id": "T-bad-final", "claim_type": "STATIC_ENFORCEMENT",
               "required_proof_depth": "E2_STATIC_CHECK"}
        v = validate_acceptance(row, final_acceptance_status="MAYBE")
        assert v.legal is False
        assert "INVALID_FINAL_ACCEPTANCE_STATUS" in v.rule_violations

    def test_allowed_final_statuses_complete(self):
        # Sanity: the canonical 5 must be present
        for s in ("ACCEPTED", "ACCEPTED_WITH_CAVEAT", "PARTIAL", "BLOCKED", "PENDING"):
            assert s in ALLOWED_FINAL_STATUSES


class TestApplyToMatrix:
    def test_w0_baseline_all_pending_legal(self):
        """W0 baseline: no overrides => every row PENDING => all legal."""
        result = load_matrix()
        verdicts = apply_to_matrix(result.rows)
        assert len(verdicts) == CANONICAL_REQUIREMENT_COUNT
        illegal = [v for v in verdicts if not v.legal]
        assert illegal == [], f"unexpected violations on baseline: {[v.rule_violations for v in illegal[:3]]}"


class TestAcceptanceVerifierScript:
    def test_script_exits_zero_on_baseline(self):
        result = subprocess.run(
            [sys.executable, "scripts/verify_runtime_certification_acceptance.py"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
        )
        assert result.returncode == 0, f"unexpected exit {result.returncode}\n{result.stderr}"

    def test_script_exits_two_when_overrides_force_violation(self, tmp_path):
        """Synthesize an overrides sidecar that forces a real violation,
        run the verifier, expect exit 2 and a populated downgraded report."""
        sidecar_dir = REPO_ROOT / "artifacts" / "certification"
        sidecar_dir.mkdir(parents=True, exist_ok=True)
        sidecar = sidecar_dir / "runtime_evidence_overrides.json"
        backup = None
        if sidecar.exists():
            backup = sidecar.read_text(encoding="utf-8")
        try:
            # Pick a known runtime-tier row from the CSV: RTC-REQ-113 has
            # claim_type=OBSERVABILITY_RUNTIME, required=E7_REAL_OTEL_EXPORT.
            # Forcing E2 + ACCEPTED triggers ACCEPTED_WITH_WEAK_PROOF.
            sidecar.write_text(json.dumps({
                "actual_proof_depth": {"RTC-REQ-113": "E2_STATIC_CHECK"},
                "final_acceptance_status": {"RTC-REQ-113": "ACCEPTED"},
            }), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "scripts/verify_runtime_certification_acceptance.py"],
                capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
            )
            assert result.returncode == 2, (
                f"expected exit=2 (FAIL_CLOSED), got {result.returncode}\n{result.stdout}\n{result.stderr}"
            )
            # The downgraded-rows report must include the violation
            dr = json.loads((sidecar_dir / "downgraded_rows_report.json").read_text(encoding="utf-8"))
            assert dr["downgraded_count"] >= 1
            req_ids = [r["req_id"] for r in dr["downgraded_rows"]]
            assert "RTC-REQ-113" in req_ids
        finally:
            # Restore baseline (no sidecar => clean PENDING run)
            if backup is None:
                if sidecar.exists():
                    os.remove(sidecar)
            else:
                sidecar.write_text(backup, encoding="utf-8")
            # Re-run the verifier to restore clean reports
            subprocess.run(
                [sys.executable, "scripts/verify_runtime_certification_acceptance.py"],
                capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
            )
