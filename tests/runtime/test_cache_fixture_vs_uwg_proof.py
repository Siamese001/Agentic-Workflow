"""Tests — W1 phase 2 L4 cache-state schema (g1) + fixture-vs-UWG (g2)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE_SCHEMA = REPO_ROOT / "tools" / "certification" / "evidence" / "probe_cache_state_schema.py"
PROBE_FIXTURE = REPO_ROOT / "tools" / "certification" / "evidence" / "probe_cache_fixture_vs_uwg.py"
ARTIFACT_SCHEMA = REPO_ROOT / "artifacts" / "certification" / "l4_cache_state_schema_proof.json"
ARTIFACT_FIXTURE = REPO_ROOT / "artifacts" / "certification" / "cache_fixture_vs_uwg_proof.json"


def _run_schema() -> int:
    return subprocess.run(
        [sys.executable, str(PROBE_SCHEMA)], cwd=str(REPO_ROOT),
        timeout=30, check=False, capture_output=True,
    ).returncode


def _run_fixture() -> int:
    return subprocess.run(
        [sys.executable, str(PROBE_FIXTURE)], cwd=str(REPO_ROOT),
        timeout=30, check=False, capture_output=True,
    ).returncode


def _read_schema() -> dict:
    _run_schema()
    return json.loads(ARTIFACT_SCHEMA.read_text(encoding="utf-8"))


def _read_fixture() -> dict:
    _run_fixture()
    return json.loads(ARTIFACT_FIXTURE.read_text(encoding="utf-8"))


class TestSchemaProbe10Concepts:
    """g1: prove 10 required cache-state concepts exist in the SSOT."""

    def test_schema_probe_exits_zero(self):
        assert _run_schema() == 0

    def test_all_ten_concepts_proven(self):
        a = _read_schema()
        assert a["concepts_total"] == 10
        assert a["concepts_proven_count"] == 10
        assert a["concepts_all_proven"] is True
        assert a["overall_status"] == "PASS"

    def test_each_required_concept_listed(self):
        a = _read_schema()
        concepts = {r["concept"] for r in a["concept_results"]}
        expected = {
            "tenant_scope", "normalized_request_hash", "semantic_embedding_ref",
            "answer_ref", "policy_hash", "blueprint_hash", "freshness_class",
            "reuse_safe_classes", "deterministic_digest", "audit_refs",
        }
        assert concepts == expected

    def test_every_concept_maps_to_concrete_ssot_fields(self):
        a = _read_schema()
        for result in a["concept_results"]:
            assert len(result["found_in_ssot"]) > 0, (
                f"{result['concept']} has no concrete SSOT field binding"
            )
            assert result["missing_from_ssot"] == [], (
                f"{result['concept']} declares fields not in SSOT: "
                f"{result['missing_from_ssot']}"
            )

    def test_anti_cheat_flags(self):
        a = _read_schema()
        f = a["anti_cheat_rules_honored"]
        assert f["every_concept_mapped_to_concrete_ssot_fields"] is True
        assert f["no_fake_or_placeholder_mapping"] is True
        assert f["probe_did_not_write_sidecar"] is True


class TestFixtureVsUwgProbe:
    """g2: prove UWG receipt API exists AND probe itself is fixture_only."""

    def test_fixture_probe_exits_zero(self):
        assert _run_fixture() == 0

    def test_uwg_surface_exists(self):
        a = _read_fixture()
        uwg = a["details"]["uwg_surface"]
        assert uwg["uwg_importable"] is True
        assert uwg["uwg_receipt_is_dataclass"] is True
        assert uwg["uwg_receipt_has_outcome_field"] is True

    def test_uwg_outcomes_match_spec(self):
        a = _read_fixture()
        uwg = a["details"]["uwg_surface"]
        assert set(uwg["uwg_outcome_enum_members"]) >= {
            "COMMIT_ACCEPTED", "COMMIT_REJECTED", "COMMIT_HELD",
        }

    def test_probe_is_fixture_only(self):
        """Rule 5: probe itself must not claim production durable mutation."""
        a = _read_fixture()
        fv = a["details"]["fixture_vs_production"]
        assert fv["fixture_only"] is True
        assert fv["production_durable_write_claim"] is False
        assert fv["uwg_receipt_id_for_production_write"] is None
        assert fv["probe_performs_cache_mutation"] is False

    def test_l4_write_enforcement_surface_present(self):
        a = _read_fixture()
        enf = a["details"]["l4_write_enforcement"]
        assert enf["some_enforcement_present"] is True

    def test_all_three_invariants_pass(self):
        a = _read_fixture()
        assert a["all_pass"] is True
        assert a["overall_status"] == "PASS"

    def test_anti_cheat_flags(self):
        a = _read_fixture()
        f = a["anti_cheat_rules_honored"]
        assert f["rule_4_uwg_receipt_used_when_available"] is True
        assert f["rule_5_fixture_only_label_emitted"] is True
        assert f["no_production_durable_write_claimed_without_receipt"] is True
        assert f["probe_did_not_write_sidecar"] is True


class TestCombinedSubclaimContract:
    """Both probes together drive R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF."""

    def test_schema_and_fixture_both_pass(self):
        schema = _read_schema()
        fixture = _read_fixture()
        assert schema["overall_status"] == "PASS"
        assert fixture["overall_status"] == "PASS"

    def test_composer_can_map_both_to_PFTR_subclaim(self):
        """Composer rule: PFTR = PASS iff schema and fixture both PASS."""
        schema = _read_schema()
        fixture = _read_fixture()
        both_pass = (schema["overall_status"] == "PASS"
                     and fixture["overall_status"] == "PASS")
        assert both_pass, (
            "R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF cannot PASS unless "
            "both schema (g1) and fixture-vs-UWG (g2) pass"
        )
