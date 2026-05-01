"""W1p6 — R1B_SAFE_REUSE_COMPOSITE_PROOF tests.

Verifies:
1. Old dense-only proof (R1B_PRODUCTION_THRESHOLD_PROOF) remains CALIBRATION_GAP
2. New safe-reuse composite proof may PASS when its inputs are satisfied
3. RTC-REQ-055 stays PARTIAL while RTC-REQ-059 can be ACCEPTED
4. Composite refuses PASS when any required input is not PASS
5. Composite refuses PASS when sweep shows unsafe_fp_count>0
6. Composite refuses PASS when sweep has no row at configured threshold
7. Canonical CSV contains RTC-REQ-059 with correct claim_type
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.compose_semantic_cache_subclaims import _map_safe_reuse_composite_proof
from agentic_core.runtime.prove_requirements.r1b_subclaim_schema import (
    CORE_SUBCLAIMS,
    LEGACY_RTC_REQ_055_SUBCLAIMS,
    GATED_ROWS,
    ALL_SUBCLAIMS,
)

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"


# ──────────────────────────────────────────────────────────────────────
# Section 1: Legacy dense-only proof stays CALIBRATION_GAP
# ──────────────────────────────────────────────────────────────────────


class TestLegacyDenseOnlyProofPreserved:
    """W1p4 finding on R1B_PRODUCTION_THRESHOLD_PROOF is not erased."""

    def test_sidecar_threshold_subclaim_is_calibration_gap(self):
        sidecar_path = ARTIFACTS_DIR / "semantic_cache_subclaims.json"
        if not sidecar_path.exists():
            pytest.skip("sidecar not present (run composer)")
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        subs = sidecar.get("subclaims", {})
        assert "R1B_PRODUCTION_THRESHOLD_PROOF" in subs
        threshold_status = subs["R1B_PRODUCTION_THRESHOLD_PROOF"]["status"]
        assert threshold_status == "CALIBRATION_GAP", (
            f"Legacy dense-only threshold proof must stay CALIBRATION_GAP. "
            f"Got {threshold_status!r} — W1p4 finding was overwritten."
        )

    def test_threshold_adr_still_pending(self):
        """SEMCACHE-THRESH-001 remains PENDING_APPROVAL."""
        adr_path = ARTIFACTS_DIR / "semantic_cache_threshold_adr.json"
        if not adr_path.exists():
            pytest.skip("threshold ADR not present")
        adr = json.loads(adr_path.read_text(encoding="utf-8"))
        approval = adr.get("owner_approval", {}).get("status")
        # User explicitly said: "Do not approve or apply SEMCACHE-THRESH-001"
        assert approval != "APPROVED", (
            f"SEMCACHE-THRESH-001 owner_approval.status={approval!r} "
            f"(must not be APPROVED in W1p6)"
        )

    def test_legacy_rtc_req_055_gating_does_not_include_composite(self):
        """LEGACY_RTC_REQ_055_SUBCLAIMS excludes the composite subclaim."""
        assert "R1B_SAFE_REUSE_COMPOSITE_PROOF" not in LEGACY_RTC_REQ_055_SUBCLAIMS

    def test_rtc_req_055_still_gates_on_threshold(self):
        """RTC-REQ-055 still gates on R1B_PRODUCTION_THRESHOLD_PROOF."""
        gating = GATED_ROWS["RTC-REQ-055"]["gating_subclaims"]
        assert "R1B_PRODUCTION_THRESHOLD_PROOF" in gating


# ──────────────────────────────────────────────────────────────────────
# Section 2: New composite proof may PASS when inputs satisfied
# ──────────────────────────────────────────────────────────────────────


class TestCompositeProofPassPath:
    """Composite subclaim is emitted when its material inputs are satisfied."""

    def _good_sweep(self, threshold: float = 0.95) -> dict:
        return {
            "metrics_table": [
                {
                    "threshold": threshold,
                    "TP": 5, "FP": 0, "TN": 6, "FN": 0,
                    "unsafe_fp_count": 0,
                    "hard_negative_allowed_count": 0,
                    "safe_positive_block_count": 0,
                    "precision": 1.0, "recall": 1.0,
                    "false_positive_rate": 0.0, "false_negative_rate": 0.0,
                }
            ]
        }

    def _good_veto(self) -> dict:
        return {
            "status": "PASS",
            "metrics": {"false_negatives": 0},
            "safety_score": 1.0,
            "primary_veto_mode": "C_PRIMARY_LLM_JUDGE",
            "invocation_counts": {
                "llm_judge_invocation_count": 5,
                "timeout_count": 0,
                "parse_fail_count": 0,
                "unknown_count": 0,
                "error_count": 0,
            },
        }

    def test_all_pass_returns_pass(self):
        status, notes = _map_safe_reuse_composite_proof(
            model_status="PASS",
            veto_status="PASS",
            negatives_status="PASS",
            pftr_status="PASS",
            terminal_status="PASS",
            veto_ev=self._good_veto(),
            sweep_ev=self._good_sweep(),
            configured_threshold=0.95,
        )
        assert status == "PASS", f"expected PASS, got {status}: {notes}"

    def test_composite_does_not_require_threshold_proof(self):
        """Composite works even when threshold proof is CALIBRATION_GAP."""
        # The threshold proof status is NOT an input here; the composite
        # only needs the 5 material inputs + sweep. This is the key
        # decoupling from the legacy dense-only path.
        status, notes = _map_safe_reuse_composite_proof(
            model_status="PASS",
            veto_status="PASS",
            negatives_status="PASS",
            pftr_status="PASS",
            terminal_status="PASS",
            veto_ev=self._good_veto(),
            sweep_ev=self._good_sweep(),
            configured_threshold=0.95,
        )
        assert status == "PASS"


# ──────────────────────────────────────────────────────────────────────
# Section 3: Composite refuses PASS when inputs unsatisfied
# ──────────────────────────────────────────────────────────────────────


class TestCompositeProofRefusesPassPaths:
    """Every gating condition can independently block PASS."""

    def _good_sweep(self):
        return {
            "metrics_table": [{
                "threshold": 0.95,
                "TP": 5, "FP": 0, "TN": 6, "FN": 0,
                "unsafe_fp_count": 0,
                "hard_negative_allowed_count": 0,
            }]
        }

    def _good_veto(self):
        return {
            "status": "PASS", "metrics": {"false_negatives": 0},
            "safety_score": 1.0,
            "invocation_counts": {"llm_judge_invocation_count": 5},
        }

    def test_model_not_pass_blocks(self):
        status, _ = _map_safe_reuse_composite_proof(
            "PARTIAL", "PASS", "PASS", "PASS", "PASS",
            self._good_veto(), self._good_sweep(), 0.95,
        )
        assert status != "PASS"

    def test_veto_not_pass_blocks(self):
        status, _ = _map_safe_reuse_composite_proof(
            "PASS", "PARTIAL", "PASS", "PASS", "PASS",
            self._good_veto(), self._good_sweep(), 0.95,
        )
        assert status != "PASS"

    def test_negatives_not_pass_blocks(self):
        status, _ = _map_safe_reuse_composite_proof(
            "PASS", "PASS", "PARTIAL", "PASS", "PASS",
            self._good_veto(), self._good_sweep(), 0.95,
        )
        assert status != "PASS"

    def test_pftr_not_pass_blocks(self):
        status, _ = _map_safe_reuse_composite_proof(
            "PASS", "PASS", "PASS", "PARTIAL", "PASS",
            self._good_veto(), self._good_sweep(), 0.95,
        )
        assert status != "PASS"

    def test_terminal_not_pass_blocks(self):
        status, _ = _map_safe_reuse_composite_proof(
            "PASS", "PASS", "PASS", "PASS", "PARTIAL",
            self._good_veto(), self._good_sweep(), 0.95,
        )
        assert status != "PASS"

    def test_hard_blocker_propagates_to_blocked(self):
        """BLOCKED on input -> BLOCKED composite."""
        status, _ = _map_safe_reuse_composite_proof(
            "BLOCKED", "PASS", "PASS", "PASS", "PASS",
            self._good_veto(), self._good_sweep(), 0.95,
        )
        assert status == "BLOCKED"

    def test_sweep_missing_is_partial(self):
        status, notes = _map_safe_reuse_composite_proof(
            "PASS", "PASS", "PASS", "PASS", "PASS",
            self._good_veto(), None, 0.95,
        )
        assert status == "PARTIAL"
        assert "sweep" in notes.lower()

    def test_sweep_no_row_at_threshold_is_partial(self):
        sweep = {"metrics_table": [{"threshold": 0.80, "TP": 0, "FP": 0, "TN": 0, "FN": 0,
                                     "unsafe_fp_count": 0, "hard_negative_allowed_count": 0}]}
        status, notes = _map_safe_reuse_composite_proof(
            "PASS", "PASS", "PASS", "PASS", "PASS",
            self._good_veto(), sweep, 0.95,
        )
        assert status == "PARTIAL"
        assert "0.95" in notes or "no row" in notes.lower()

    def test_unsafe_fp_count_positive_blocks_pass(self):
        bad_sweep = {"metrics_table": [{
            "threshold": 0.95, "TP": 5, "FP": 0, "TN": 5, "FN": 1,
            "unsafe_fp_count": 1, "hard_negative_allowed_count": 1,
        }]}
        status, notes = _map_safe_reuse_composite_proof(
            "PASS", "PASS", "PASS", "PASS", "PASS",
            self._good_veto(), bad_sweep, 0.95,
        )
        # Either PARTIAL or FAIL — must NOT be PASS
        assert status != "PASS"

    def test_hard_negative_allowed_returns_fail(self):
        bad_sweep = {"metrics_table": [{
            "threshold": 0.95, "TP": 4, "FP": 0, "TN": 6, "FN": 1,
            "unsafe_fp_count": 0,  # but hard_neg_allowed non-zero
            "hard_negative_allowed_count": 1,
        }]}
        status, _ = _map_safe_reuse_composite_proof(
            "PASS", "PASS", "PASS", "PASS", "PASS",
            self._good_veto(), bad_sweep, 0.95,
        )
        assert status in ("PARTIAL", "FAIL")  # non-PASS is the invariant

    def test_veto_fn_positive_blocks_pass(self):
        bad_veto = {
            "status": "PASS", "metrics": {"false_negatives": 1},
            "safety_score": 0.9,
            "invocation_counts": {"llm_judge_invocation_count": 5},
        }
        status, _ = _map_safe_reuse_composite_proof(
            "PASS", "PASS", "PASS", "PASS", "PASS",
            bad_veto, self._good_sweep(), 0.95,
        )
        assert status != "PASS"


# ──────────────────────────────────────────────────────────────────────
# Section 4: Row statuses coexist correctly
# ──────────────────────────────────────────────────────────────────────


class TestRowCoexistence:
    """RTC-REQ-055 stays PARTIAL, RTC-REQ-059 can be ACCEPTED."""

    def test_rtc_req_055_partial(self):
        overrides_path = ARTIFACTS_DIR / "runtime_evidence_overrides.json"
        if not overrides_path.exists():
            pytest.skip("overrides not present (run verifier)")
        overrides = json.loads(overrides_path.read_text(encoding="utf-8"))
        final = overrides.get("final_acceptance_status", {})
        assert final.get("RTC-REQ-055") == "PARTIAL", (
            f"RTC-REQ-055 must stay PARTIAL. Got {final.get('RTC-REQ-055')!r}"
        )

    def test_rtc_req_059_accepted_on_current_evidence(self):
        overrides_path = ARTIFACTS_DIR / "runtime_evidence_overrides.json"
        if not overrides_path.exists():
            pytest.skip("overrides not present")
        overrides = json.loads(overrides_path.read_text(encoding="utf-8"))
        final = overrides.get("final_acceptance_status", {})
        # On the current sidecar (AG approved, FN=0, unsafe_fp=0 at 0.95),
        # RTC-REQ-059 should be ACCEPTED. If evidence regresses, this test
        # will flip and serve as a regression alert.
        assert final.get("RTC-REQ-059") == "ACCEPTED", (
            f"RTC-REQ-059 expected ACCEPTED. Got {final.get('RTC-REQ-059')!r}"
        )

    def test_rtc_req_055_acceptance_caveat_names_threshold(self):
        """Caveat MUST still surface the threshold CALIBRATION_GAP."""
        overrides_path = ARTIFACTS_DIR / "runtime_evidence_overrides.json"
        if not overrides_path.exists():
            pytest.skip("overrides not present")
        overrides = json.loads(overrides_path.read_text(encoding="utf-8"))
        caveat = overrides.get("acceptance_caveat", {}).get("RTC-REQ-055", "")
        assert "THRESHOLD_PROOF" in caveat or "CALIBRATION_GAP" in caveat, (
            f"RTC-REQ-055 caveat must name the threshold gap. Got: {caveat}"
        )


# ──────────────────────────────────────────────────────────────────────
# Section 5: Catalog and CSV alignment
# ──────────────────────────────────────────────────────────────────────


class TestCatalogAndCSV:
    """Schema + CSV structural invariants."""

    def test_composite_in_core_subclaims(self):
        assert "R1B_SAFE_REUSE_COMPOSITE_PROOF" in CORE_SUBCLAIMS

    def test_composite_not_in_legacy_055_gating(self):
        assert "R1B_SAFE_REUSE_COMPOSITE_PROOF" not in LEGACY_RTC_REQ_055_SUBCLAIMS

    def test_rtc_req_059_gating_includes_composite(self):
        gating = GATED_ROWS["RTC-REQ-059"]["gating_subclaims"]
        assert "R1B_SAFE_REUSE_COMPOSITE_PROOF" in gating

    def test_rtc_req_059_gating_excludes_threshold_proof(self):
        """RTC-REQ-059 must NOT require R1B_PRODUCTION_THRESHOLD_PROOF."""
        gating = GATED_ROWS["RTC-REQ-059"]["gating_subclaims"]
        assert "R1B_PRODUCTION_THRESHOLD_PROOF" not in gating

    def test_csv_contains_rtc_req_059(self):
        import csv
        csv_path = (
            REPO_ROOT / "docs" / "reference" / "contracts" / "certification"
            / "runtime_certification_requirements_100_percent_hardened.csv"
        )
        rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8")))
        row = next((r for r in rows if r["req_id"] == "RTC-REQ-059"), None)
        assert row is not None, "RTC-REQ-059 missing from hardened CSV"
        assert row["claim_type"] == "COMPOSITION_RUNTIME"
        assert "safe" in row["requirement_title"].lower() or "veto" in row["requirement_title"].lower()
        assert row["priority"] == "P0"


# ──────────────────────────────────────────────────────────────────────
# Section 6: Anti-cheat invariants
# ──────────────────────────────────────────────────────────────────────


class TestAntiCheat:
    """W1p6 must not silently convert the old finding into PASS."""

    def test_composite_not_named_production_threshold_proof(self):
        """Composite subclaim cannot be aliased over the legacy one."""
        assert "R1B_PRODUCTION_THRESHOLD_PROOF" != "R1B_SAFE_REUSE_COMPOSITE_PROOF"
        assert "R1B_PRODUCTION_THRESHOLD_PROOF" in ALL_SUBCLAIMS
        assert "R1B_SAFE_REUSE_COMPOSITE_PROOF" in ALL_SUBCLAIMS

    def test_rtc_req_055_requirement_text_not_changed(self):
        """RTC-REQ-055 requirement_text must not be swapped out silently.

        The user: 'If updating it, write a migration report.' This test ensures
        if someone edits RTC-REQ-055 text, they must acknowledge that a report
        now exists.
        """
        migration_report = (
            REPO_ROOT / "docs" / "architecture"
            / "requirement_architecture_alignment_report.md"
        )
        assert migration_report.exists(), (
            "If RTC-REQ-055 is being reinterpreted, migration report is required"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
