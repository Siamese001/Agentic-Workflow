"""W1 phase 4 — threshold sweep probe."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = REPO_ROOT / "artifacts" / "certification" / "threshold_sweep_results.json"

pytestmark = pytest.mark.skipif(
    not ARTIFACT.exists(),
    reason="threshold_sweep_results.json not present (requires live BGE-M3 run)",
)


@pytest.fixture(scope="module")
def sweep() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


class TestSweepSchema:
    def test_probe_name(self, sweep):
        assert sweep["probe"] == "threshold_sweep"

    def test_phase_label(self, sweep):
        assert sweep["phase"] == "W1p4"

    def test_subclaim_target(self, sweep):
        assert sweep["subclaim_target"] == "R1B_PRODUCTION_THRESHOLD_PROOF"

    def test_candidate_thresholds_exact(self, sweep):
        assert sweep["candidate_thresholds"] == [0.95, 0.92, 0.90, 0.88, 0.85, 0.80]


class TestMetricsTable:
    def test_six_rows(self, sweep):
        if sweep["overall_status"] in ("INFRASTRUCTURE_GAP", "DATASET_MISSING", "OVERRIDE_PRESENT"):
            pytest.skip(f"sweep did not run (status={sweep['overall_status']})")
        assert len(sweep["metrics_table"]) == 6

    def test_each_row_has_all_14_metric_fields(self, sweep):
        if not sweep.get("metrics_table"):
            pytest.skip("no metrics (precondition failed)")
        required_fields = {
            "threshold", "tp", "fn", "tn", "fp",
            "precision", "recall", "fpr", "fnr", "f1", "accuracy",
            "unsafe_fp_count", "policy_freshness_preserved", "lexical_overlap_preserved",
        }
        for m in sweep["metrics_table"]:
            missing = required_fields - set(m.keys())
            assert not missing, f"row t={m.get('threshold')} missing {missing}"

    def test_totals_consistent(self, sweep):
        if not sweep.get("metrics_table"):
            pytest.skip("no metrics")
        for m in sweep["metrics_table"]:
            total = m["tp"] + m["fn"] + m["tn"] + m["fp"]
            # total must equal number of measurable pairs
            assert total > 0
            # precision/recall consistency
            if m["tp"] + m["fp"]:
                assert abs(m["precision"] - m["tp"] / (m["tp"] + m["fp"])) < 0.001
            if m["tp"] + m["fn"]:
                assert abs(m["recall"] - m["tp"] / (m["tp"] + m["fn"])) < 0.001


class TestSafetyRuleEnforcement:
    def test_status_is_sweep_complete_or_no_safe(self, sweep):
        if sweep["overall_status"] in ("INFRASTRUCTURE_GAP", "DATASET_MISSING"):
            pytest.skip(f"sweep did not run")
        assert sweep["overall_status"] in ("SWEEP_COMPLETE", "NO_SAFE_THRESHOLD_FOUND")

    def test_recommended_is_null_or_in_sweep(self, sweep):
        rec = sweep["recommended_threshold"]
        if rec is None:
            return  # valid
        assert rec in sweep["candidate_thresholds"]

    def test_no_safe_threshold_when_any_fp_nonzero(self, sweep):
        """If every threshold has fp>0, recommended must be null."""
        if not sweep.get("metrics_table"):
            pytest.skip("no metrics")
        all_fp_nonzero = all(m["fp"] > 0 for m in sweep["metrics_table"])
        if all_fp_nonzero:
            assert sweep["recommended_threshold"] is None
            assert sweep["overall_status"] == "NO_SAFE_THRESHOLD_FOUND"

    def test_recommendation_rule_documented(self, sweep):
        rule = sweep.get("recommendation_rule", "")
        assert "fp=0" in rule.lower() or "fp == 0" in rule.lower()
        assert "unsafe_fp" in rule.lower()


class TestAntiCheat:
    def test_probe_did_not_modify_env(self, sweep):
        assert sweep["anti_cheat_rules_honored"]["probe_did_not_modify_threshold_env"] is True

    def test_probe_did_not_create_adr(self, sweep):
        assert sweep["anti_cheat_rules_honored"]["probe_did_not_create_adr"] is True

    def test_probe_did_not_write_sidecar(self, sweep):
        assert sweep["anti_cheat_rules_honored"]["probe_did_not_write_sidecar"] is True

    def test_rule_1_honored(self, sweep):
        assert sweep["anti_cheat_rules_honored"]["rule_1_no_silent_threshold_lowering"] is True


class TestADRPathNote:
    def test_adr_path_note_references_generator(self, sweep):
        note = sweep.get("adr_path_note", "")
        assert "generate_threshold_adr.py" in note
        assert "does NOT create the ADR" in note


class TestOverrideRespected:
    def test_override_active_marks_blocked(self, sweep):
        # If overrides were present at probe time, status must reflect that
        if sweep.get("override_active"):
            assert sweep["overall_status"] == "OVERRIDE_PRESENT"
            assert sweep["recommended_threshold"] is None
