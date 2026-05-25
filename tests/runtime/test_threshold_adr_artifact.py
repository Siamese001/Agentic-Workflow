"""W1 phase 4 — threshold ADR artifact schema + PROPOSED_NOT_APPLIED invariants."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ADR_JSON = REPO_ROOT / "artifacts" / "certification" / "semantic_cache_threshold_adr.json"
ADR_MD = REPO_ROOT / "docs" / "adr" / "semantic_cache_threshold_recalibration.md"

pytestmark = pytest.mark.skipif(
    not ADR_JSON.exists(),
    reason="semantic_cache_threshold_adr.json not present (run ops_scripts/ci/generate_threshold_adr.py)",
)


@pytest.fixture(scope="module")
def adr() -> dict:
    return json.loads(ADR_JSON.read_text(encoding="utf-8"))


class TestADRJSONPresent:
    def test_json_file_exists(self):
        assert ADR_JSON.exists()

    def test_md_file_exists(self):
        assert ADR_MD.exists()

    def test_md_non_empty(self):
        assert ADR_MD.stat().st_size > 1000, "ADR MD suspiciously small"


class TestADRSchemaFields:
    def test_adr_id_canonical(self, adr):
        assert adr["adr_id"] == "SEMCACHE-THRESH-001"

    def test_adr_version_present(self, adr):
        assert adr.get("adr_version") == "1.0"

    def test_old_threshold_is_0_95(self, adr):
        assert adr["old_threshold"] == 0.95

    def test_recommended_threshold_type(self, adr):
        rec = adr["recommended_threshold"]
        assert rec is None or isinstance(rec, (int, float))

    def test_model_block_bge_m3(self, adr):
        assert adr["model"]["identifier"] == "BAAI/bge-m3"
        assert adr["model"]["operation"] == "dense_cosine"
        assert adr["model"]["dim"] == 1024

    def test_dataset_block_declares_100_pairs(self, adr):
        assert adr["dataset"]["n_pairs"] >= 100
        assert adr["dataset"]["n_positives"] == 50
        assert adr["dataset"]["n_negatives"] == 50

    def test_dataset_sha256_present(self, adr):
        sha = adr["dataset"]["sha256"]
        assert isinstance(sha, str) and len(sha) == 64

    def test_metrics_table_has_6_rows(self, adr):
        # Even when sweep=NO_SAFE_THRESHOLD_FOUND, all 6 threshold rows
        # are still present
        assert len(adr["metrics_table"]) == 6

    def test_sweep_source_provenance(self, adr):
        assert "sweep_source" in adr
        assert "sha256" in adr["sweep_source"]

    def test_safety_rationale_non_empty(self, adr):
        assert len(adr.get("safety_rationale", "")) > 20

    def test_rollback_rule_non_empty(self, adr):
        assert len(adr.get("rollback_rule", "")) > 20


class TestProposedNotAppliedInvariants:
    """User-approved invariants — ADR never auto-applies."""

    def test_owner_approval_is_pending(self, adr):
        assert adr["owner_approval"]["status"] == "PENDING_APPROVAL"

    def test_owner_approval_has_no_approver(self, adr):
        assert adr["owner_approval"]["approver"] is None

    def test_owner_approval_has_no_timestamp(self, adr):
        assert adr["owner_approval"]["approved_utc"] is None

    def test_implementation_status_proposed_not_applied(self, adr):
        assert adr["implementation_status"] == "PROPOSED_NOT_APPLIED"

    def test_config_binding_applied_false(self, adr):
        assert adr["config_binding"]["applied"] is False

    def test_config_binding_target_key_declared(self, adr):
        target = adr["config_binding"]["target_key"]
        assert "semantic_cache_manager" in target
        assert "dynamic" in target.lower()

    def test_apply_procedure_documented(self, adr):
        proc = adr["config_binding"]["apply_procedure"]
        assert "not automatically applied" in proc.lower()
        assert "semantic_cache_manager" in proc


class TestAntiCheatInvariants:
    def test_anti_cheat_block_declared(self, adr):
        assert "anti_cheat_invariants" in adr

    def test_rule_1_honored(self, adr):
        assert adr["anti_cheat_invariants"]["rule_1_no_silent_threshold_lowering"] is True

    def test_rule_7_adr_gate_honored(self, adr):
        assert adr["anti_cheat_invariants"]["rule_7_adr_gate"] is True

    def test_generator_never_auto_approves(self, adr):
        assert adr["anti_cheat_invariants"]["generator_never_auto_approves"] is True

    def test_generator_never_sets_applied_true(self, adr):
        assert adr["anti_cheat_invariants"]["generator_never_sets_applied_true"] is True


class TestJsonMdSync:
    def test_md_mentions_adr_id(self):
        text = ADR_MD.read_text(encoding="utf-8")
        assert "SEMCACHE-THRESH-001" in text

    def test_md_declares_proposed_not_applied(self):
        text = ADR_MD.read_text(encoding="utf-8")
        assert "PROPOSED_NOT_APPLIED" in text

    def test_md_declares_pending_approval(self):
        text = ADR_MD.read_text(encoding="utf-8")
        assert "PENDING_APPROVAL" in text

    def test_md_has_metrics_table(self):
        text = ADR_MD.read_text(encoding="utf-8")
        assert "| Threshold" in text
        # at least one threshold value row
        assert "| 0.95 |" in text
        assert "| 0.85 |" in text


class TestRegeneration:
    def test_regeneration_preserves_invariants(self, adr, tmp_path):
        """Re-running the generator MUST still land at PENDING_APPROVAL."""
        import subprocess, sys
        result = subprocess.run(
            [sys.executable, "ops_scripts/ci/generate_threshold_adr.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        adr_after = json.loads(ADR_JSON.read_text(encoding="utf-8"))
        assert adr_after["owner_approval"]["status"] == "PENDING_APPROVAL"
        assert adr_after["implementation_status"] == "PROPOSED_NOT_APPLIED"
        assert adr_after["config_binding"]["applied"] is False
