"""W5 GAP-3 gate consumer tests — apps-rg-quarantine-gap-remediation-8f405c W6.P1.

Tests the quality_thresholds (L2) and provenance_requirements / output_requirements
(Exit) consumers added in W5.P1 and W5.P2.

Uses actual contract field names from:
  QualityThresholdsSection: min_quality, min_ats, word_min, word_max
  ProvenanceRequirementsSection: per_bullet_required, source_quote_required
  OutputRequirementsSection: formats, provenance_required, fact_checked_required
  ProfileManifestSection: hitl_policy_ref (metadata-only / DEFERRED)

No full runtime setup required — uses minimal FakeValidatedRequest objects.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agentic_core.L2_execution.apps_rg_l2_binding import (
    AppsRGQualityGatePolicy,
    evaluate_apps_rg_l2_quality_precheck,
    extract_apps_rg_quality_gate_policy,
)
from agentic_core.runtime.exit.apps_rg_exit_binding import (
    AppsRGExitGatePolicy,
    evaluate_apps_rg_exit_provenance_gate,
    extract_apps_rg_exit_gate_policy,
)

_REPO_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _DictPayload:
    """Dict-backed app_payload object (mirrors actual dict-access path in helpers)."""

    def __init__(self, data: dict):
        self._data = data

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        value = self._data.get(name)
        if isinstance(value, dict):
            return _DictPayload(value)
        if isinstance(value, list):
            return value
        return value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __contains__(self, key):
        return key in self._data


class FakeValidatedRequest:
    """Minimal stand-in for ValidatedRequest carrying only app_payload."""

    def __init__(self, app_payload_data: dict):
        self.app_payload = _DictPayload(app_payload_data)


# ---------------------------------------------------------------------------
# L2 quality gate consumer tests
# ---------------------------------------------------------------------------


class TestL2QualityGateExtraction:
    """Tests for extract_apps_rg_quality_gate_policy."""

    def test_extracts_actual_quality_fields(self):
        """Test 1: L2 extracts actual quality fields from payload."""
        req = FakeValidatedRequest({
            "quality_thresholds": {
                "min_quality": 0.82,
                "min_ats": 0.75,
                "word_min": 400,
                "word_max": 650,
            }
        })
        policy = extract_apps_rg_quality_gate_policy(req)
        assert policy.min_quality == 0.82
        assert policy.min_ats == 0.75
        assert policy.word_min == 400
        assert policy.word_max == 650
        assert policy.fail_closed is False

    def test_missing_quality_thresholds_returns_none_fields(self):
        """Test 2: Missing quality_thresholds returns policy with None fields."""
        req = FakeValidatedRequest({})
        policy = extract_apps_rg_quality_gate_policy(req)
        assert policy.min_quality is None
        assert policy.min_ats is None
        assert policy.word_min is None
        assert policy.word_max is None

    def test_missing_quality_thresholds_evaluation_is_not_applicable(self):
        """Test 2b: Missing quality_thresholds evaluation returns NOT_APPLICABLE with reason."""
        req = FakeValidatedRequest({})
        policy = extract_apps_rg_quality_gate_policy(req)
        result = evaluate_apps_rg_l2_quality_precheck(policy)
        assert result["verdict"] == "NOT_APPLICABLE"
        assert "reason" in result
        assert result["reason"]  # non-empty reason

    def test_missing_fields_not_treated_as_pass(self):
        """Test 2c: Missing quality fields must not be implied PASS."""
        req = FakeValidatedRequest({})
        policy = extract_apps_rg_quality_gate_policy(req)
        result = evaluate_apps_rg_l2_quality_precheck(policy)
        assert result["verdict"] != "PASS"


class TestL2WordCountEvaluation:
    """Tests for evaluate_apps_rg_l2_quality_precheck word count checks."""

    def test_word_count_below_word_min_warns_by_default(self):
        """Test 3: word_count below word_min produces WARN in fail-soft mode."""
        req = FakeValidatedRequest({
            "quality_thresholds": {"word_min": 400, "word_max": 650}
        })
        policy = extract_apps_rg_quality_gate_policy(req)
        result = evaluate_apps_rg_l2_quality_precheck(policy, run_context={"word_count": 250})
        assert result["verdict"] in ("WARN",), (
            f"Expected WARN for word_count=250 < word_min=400, got {result['verdict']}"
        )
        assert result["field_verdicts"].get("word_min") == "WARN"
        # Check reason is surfaced somewhere
        word_min_verdict = result["field_verdicts"]["word_min"]
        assert word_min_verdict != "PASS"

    def test_word_count_below_word_min_fails_in_fail_closed_mode(self, monkeypatch):
        """Test 4: word_count below word_min produces FAIL with APPS_RG_QUALITY_GATE_FAIL_CLOSED=1."""
        monkeypatch.setenv("APPS_RG_QUALITY_GATE_FAIL_CLOSED", "1")
        req = FakeValidatedRequest({
            "quality_thresholds": {"word_min": 400, "word_max": 650}
        })
        policy = extract_apps_rg_quality_gate_policy(req)
        result = evaluate_apps_rg_l2_quality_precheck(policy, run_context={"word_count": 250})
        assert result["verdict"] == "FAIL"
        assert result["field_verdicts"].get("word_min") == "FAIL"

    def test_word_count_in_range_passes(self):
        """Test 5: word_count inside [word_min, word_max] produces PASS."""
        req = FakeValidatedRequest({
            "quality_thresholds": {"word_min": 400, "word_max": 650}
        })
        policy = extract_apps_rg_quality_gate_policy(req)
        result = evaluate_apps_rg_l2_quality_precheck(policy, run_context={"word_count": 500})
        assert result["verdict"] == "PASS"
        assert result["field_verdicts"].get("word_min") == "PASS"
        assert result["field_verdicts"].get("word_max") == "PASS"

    def test_word_count_not_applicable_without_context(self):
        """word_count check is NOT_APPLICABLE when run_context has no word_count."""
        req = FakeValidatedRequest({
            "quality_thresholds": {"word_min": 400, "word_max": 650}
        })
        policy = extract_apps_rg_quality_gate_policy(req)
        result = evaluate_apps_rg_l2_quality_precheck(policy, run_context={})
        # min_quality/min_ats absent so only word checks; no word_count → NOT_APPLICABLE
        assert result["verdict"] == "NOT_APPLICABLE"

    def test_min_quality_carried_as_policy_metadata(self):
        """min_quality and min_ats are carried as metadata (not evaluable at L2)."""
        req = FakeValidatedRequest({
            "quality_thresholds": {"min_quality": 0.82, "min_ats": 0.75}
        })
        policy = extract_apps_rg_quality_gate_policy(req)
        result = evaluate_apps_rg_l2_quality_precheck(policy)
        assert result["policy_metadata"].get("min_quality_threshold") == 0.82
        assert result["policy_metadata"].get("min_ats_threshold") == 0.75
        assert result["field_verdicts"].get("min_quality") == "NOT_APPLICABLE"
        assert result["field_verdicts"].get("min_ats") == "NOT_APPLICABLE"


# ---------------------------------------------------------------------------
# Exit provenance gate consumer tests
# ---------------------------------------------------------------------------


class TestExitGateExtraction:
    """Tests for extract_apps_rg_exit_gate_policy."""

    def test_extracts_actual_provenance_and_output_fields(self):
        """Test 6: Exit extracts actual provenance/output fields + hitl_policy_ref metadata."""
        req = FakeValidatedRequest({
            "provenance_requirements": {
                "per_bullet_required": True,
                "source_quote_required": True,
            },
            "output_requirements": {
                "formats": ["markdown", "docx"],
                "provenance_required": True,
                "fact_checked_required": True,
            },
            "profile_manifest": {
                "hitl_policy_ref": "hitl/apps_rg/v1",
            },
        })
        policy = extract_apps_rg_exit_gate_policy(req)
        assert policy.per_bullet_required is True
        assert policy.source_quote_required is True
        assert policy.output_formats is not None
        assert "markdown" in policy.output_formats
        assert "docx" in policy.output_formats
        assert policy.output_provenance_required is True
        assert policy.fact_checked_required is True
        assert policy.hitl_policy_ref == "hitl/apps_rg/v1"

    def test_hitl_policy_ref_is_metadata_only_not_evaluated_as_failure(self):
        """Test 6b: hitl_policy_ref is metadata only — not a gate FAIL verdict."""
        req = FakeValidatedRequest({
            "profile_manifest": {"hitl_policy_ref": "hitl/apps_rg/v1"},
        })
        policy = extract_apps_rg_exit_gate_policy(req)
        result = evaluate_apps_rg_exit_provenance_gate(policy)
        # hitl_policy_ref must appear in deferred section, never in field_verdicts as FAIL
        assert "hitl_policy_ref" in result["deferred"]
        assert result["deferred"]["hitl_policy_ref"]["status"] == "DEFERRED"
        assert result["verdict"] != "FAIL"

    def test_missing_payload_returns_none_fields(self):
        """Missing exit gate fields return policy with None values."""
        req = FakeValidatedRequest({})
        policy = extract_apps_rg_exit_gate_policy(req)
        assert policy.per_bullet_required is None
        assert policy.source_quote_required is None
        assert policy.output_provenance_required is None
        assert policy.fact_checked_required is None
        assert policy.output_formats is None
        assert policy.hitl_policy_ref is None


class TestExitProvenanceGateEvaluation:
    """Tests for evaluate_apps_rg_exit_provenance_gate."""

    def test_provenance_required_without_per_bullet_warns_by_default(self):
        """Test 7: provenance_required=True with per_bullet_required=False warns (fail-soft)."""
        req = FakeValidatedRequest({
            "provenance_requirements": {
                "per_bullet_required": False,
                "source_quote_required": False,
            },
            "output_requirements": {
                "provenance_required": True,
            },
        })
        policy = extract_apps_rg_exit_gate_policy(req)
        result = evaluate_apps_rg_exit_provenance_gate(policy)
        assert result["verdict"] == "WARN", (
            f"Expected WARN for provenance inconsistency in fail-soft mode, got {result['verdict']}"
        )
        assert result["field_verdicts"].get("provenance_consistency") == "WARN"
        # Reason references provenance consistency
        assert "provenance" in str(result.get("policy_metadata", {})).lower() or \
               "provenance" in str(result.get("field_verdicts", {})).lower()

    def test_provenance_inconsistency_fails_in_fail_closed_mode(self, monkeypatch):
        """Test 8: provenance inconsistency produces FAIL with APPS_RG_PROVENANCE_GATE_FAIL_CLOSED=1."""
        monkeypatch.setenv("APPS_RG_PROVENANCE_GATE_FAIL_CLOSED", "1")
        req = FakeValidatedRequest({
            "provenance_requirements": {"per_bullet_required": False},
            "output_requirements": {"provenance_required": True},
        })
        policy = extract_apps_rg_exit_gate_policy(req)
        result = evaluate_apps_rg_exit_provenance_gate(policy)
        assert result["verdict"] == "FAIL"
        assert result["field_verdicts"].get("provenance_consistency") == "FAIL"

    def test_consistent_provenance_passes(self):
        """Consistent provenance_required=True + per_bullet_required=True → PASS."""
        req = FakeValidatedRequest({
            "provenance_requirements": {"per_bullet_required": True},
            "output_requirements": {"provenance_required": True},
        })
        policy = extract_apps_rg_exit_gate_policy(req)
        result = evaluate_apps_rg_exit_provenance_gate(policy)
        assert result["field_verdicts"].get("provenance_consistency") == "PASS"
        assert result["verdict"] not in ("FAIL", "WARN")

    def test_provenance_required_false_passes(self):
        """provenance_required=False → no consistency check needed → PASS."""
        req = FakeValidatedRequest({
            "provenance_requirements": {"per_bullet_required": False},
            "output_requirements": {"provenance_required": False},
        })
        policy = extract_apps_rg_exit_gate_policy(req)
        result = evaluate_apps_rg_exit_provenance_gate(policy)
        assert result["field_verdicts"].get("provenance_required") == "PASS"
        assert result["verdict"] == "PASS"

    def test_fact_checked_required_is_deferred_metadata_not_enforced(self):
        """Test 9: fact_checked_required=True is deferred metadata, not falsely enforced."""
        req = FakeValidatedRequest({
            "output_requirements": {"fact_checked_required": True},
        })
        policy = extract_apps_rg_exit_gate_policy(req)
        result = evaluate_apps_rg_exit_provenance_gate(policy)
        # Must appear in deferred section, not produce FAIL
        assert "fact_checked_required" in result["deferred"]
        assert result["deferred"]["fact_checked_required"]["status"] == "DEFERRED"
        assert result["verdict"] != "FAIL"
        # Must not claim fact-check ran
        deferred_reason = result["deferred"]["fact_checked_required"]["reason"]
        assert "fact_check" in deferred_reason.lower() or "deferred" in deferred_reason.lower()

    def test_empty_payload_returns_not_applicable(self):
        """Empty payload → no evaluable checks → NOT_APPLICABLE verdict."""
        req = FakeValidatedRequest({})
        policy = extract_apps_rg_exit_gate_policy(req)
        result = evaluate_apps_rg_exit_provenance_gate(policy)
        assert result["verdict"] == "NOT_APPLICABLE"
        assert "reason" in result


# ---------------------------------------------------------------------------
# Field map status tests
# ---------------------------------------------------------------------------


class TestFieldMapStatus:
    """Test 10: apps_rg_ingress_field_map.v1.yaml reflects W5 wiring."""

    _FIELD_MAP_PATH = (
        _REPO_ROOT / "apps_rg" / "contracts" / "apps_rg_ingress_field_map.v1.yaml"
    )

    def _load_raw(self) -> str:
        return self._FIELD_MAP_PATH.read_text(encoding="utf-8")

    def test_quality_thresholds_section_is_mapped(self):
        content = self._load_raw()
        assert "/quality_thresholds:" in content
        # Section aggregation must be MAPPED
        import re
        match = re.search(r"/quality_thresholds:\s*\{[^}]*status:\s*(\w+)", content)
        assert match, "Could not find /quality_thresholds section aggregation"
        assert match.group(1) == "MAPPED"

    def test_quality_leaf_fields_are_mapped(self):
        content = self._load_raw()
        import re
        for field in ("min_quality", "min_ats", "word_min", "word_max"):
            assert f"/quality_thresholds/{field}" in content, (
                f"/quality_thresholds/{field} not found in field map"
            )
            # Leaf entries use multi-line YAML: key line (indented) followed by
            # indented `status:` on the next line.
            pattern = rf"\s/quality_thresholds/{field}:\s*\n\s+status:\s*(\w+)"
            match = re.search(pattern, content)
            assert match, f"Could not find status for /quality_thresholds/{field}"
            assert match.group(1) == "MAPPED", (
                f"/quality_thresholds/{field} status={match.group(1)}, expected MAPPED"
            )

    def test_provenance_requirements_section_is_mapped(self):
        content = self._load_raw()
        import re
        match = re.search(r"/provenance_requirements:\s*\{[^}]*status:\s*(\w+)", content)
        assert match, "Could not find /provenance_requirements section aggregation"
        assert match.group(1) == "MAPPED"

    def test_provenance_leaf_fields_are_mapped(self):
        content = self._load_raw()
        import re
        for field in ("per_bullet_required", "source_quote_required"):
            assert f"/provenance_requirements/{field}" in content
            pattern = rf"\s/provenance_requirements/{field}:\s*\n\s+status:\s*(\w+)"
            match = re.search(pattern, content)
            assert match, f"status not found for /provenance_requirements/{field}"
            assert match.group(1) == "MAPPED"

    def test_output_requirements_section_is_mapped(self):
        content = self._load_raw()
        import re
        match = re.search(r"/output_requirements:\s*\{[^}]*status:\s*(\w+)", content)
        assert match, "Could not find /output_requirements section aggregation"
        assert match.group(1) == "MAPPED"

    def test_output_requirements_wired_leaf_fields_are_mapped(self):
        content = self._load_raw()
        import re
        for field in ("provenance_required", "fact_checked_required", "formats"):
            assert f"/output_requirements/{field}" in content
            pattern = rf"\s/output_requirements/{field}:\s*\n\s+status:\s*(\w+)"
            match = re.search(pattern, content)
            assert match, f"status not found for /output_requirements/{field}"
            assert match.group(1) == "MAPPED"

    def test_hitl_policy_ref_remains_deferred(self):
        """hitl_policy_ref must remain DEFERRED — no HITL registry consumer at Exit."""
        content = self._load_raw()
        import re
        assert "/profile_manifest/hitl_policy_ref" in content
        pattern = r"\s/profile_manifest/hitl_policy_ref:\s*\n\s+status:\s*(\w+)"
        match = re.search(pattern, content)
        assert match, "status not found for /profile_manifest/hitl_policy_ref"
        assert match.group(1) == "DEFERRED", (
            f"hitl_policy_ref should remain DEFERRED until HITL registry (AG-13.b) lands, "
            f"got {match.group(1)}"
        )

    def test_deferred_fields_have_reason(self):
        """Any DEFERRED leaf field must have a non-empty reason."""
        content = self._load_raw()
        import re
        # Find all deferred leaf entries and check they have a reason line
        for m in re.finditer(r"(  /\S+)\n\s+status:\s*DEFERRED\n(\s+target:[^\n]*\n)?\s+reason:\s*(.+)", content):
            assert m.group(3).strip(), f"Empty reason for DEFERRED field: {m.group(1)}"

    def test_stale_field_names_not_required_as_mapped(self):
        """Stale plan field names must NOT appear as MAPPED (they don't exist in the contract)."""
        content = self._load_raw()
        stale_names = [
            "min_quality_score",
            "min_confidence",
            "hallucination_threshold",
            "jd_alignment_threshold",
            "require_evidence_grounding",
            "min_source_count",
            "max_staleness_days",
            "require_url_verification",
        ]
        for name in stale_names:
            import re
            # If stale name appears as a MAPPED leaf, that's a bug
            pattern = rf"/{name}\s*\n\s+status:\s*MAPPED"
            assert not re.search(pattern, content), (
                f"Stale field name /{name} should not appear as MAPPED in the field map"
            )


# ---------------------------------------------------------------------------
# W5 receipt consistency test
# ---------------------------------------------------------------------------


class TestW5ReceiptConsistency:
    """Test 11: W5 receipt artifact is consistent with W5 wiring."""

    _RECEIPT_PATH = (
        _REPO_ROOT / "artifacts" / "apps_rg" / "w5_gap3_field_consumers_receipt.json"
    )

    def test_w5_receipt_exists(self):
        assert self._RECEIPT_PATH.exists(), (
            f"W5 receipt not found at {self._RECEIPT_PATH}"
        )

    def test_w5_receipt_ready_for_w6(self):
        receipt = json.loads(self._RECEIPT_PATH.read_text(encoding="utf-8"))
        assert receipt.get("ready_for_w6") is True

    def test_w5_receipt_phases_complete(self):
        receipt = json.loads(self._RECEIPT_PATH.read_text(encoding="utf-8"))
        phases = receipt.get("phases", {})
        for phase_id in ("W5.P1", "W5.P2", "W5.P3"):
            assert phase_id in phases, f"Phase {phase_id} missing from receipt"
            assert phases[phase_id].get("status") == "COMPLETE", (
                f"Phase {phase_id} not COMPLETE: {phases[phase_id].get('status')}"
            )

    def test_w5_receipt_mapped_fields_use_actual_names(self):
        """Receipt must reference actual contract field names, not stale plan names."""
        receipt = json.loads(self._RECEIPT_PATH.read_text(encoding="utf-8"))
        receipt_text = json.dumps(receipt)
        stale_names = [
            "min_quality_score",
            "min_confidence",
            "hallucination_threshold",
            "jd_alignment_threshold",
            "require_evidence_grounding",
            "min_source_count",
            "max_staleness_days",
            "require_url_verification",
        ]
        for name in stale_names:
            # Stale names may appear as explanatory notes but must NOT appear as
            # required-MAPPED fields in the wiring_summary/mapped_fields
            wiring = receipt.get("wiring_summary", {})
            wiring_text = json.dumps(wiring)
            # The wiring summary consumer sections should not list stale names as
            # wired fields
            assert name not in str(wiring.get("L2_quality_gate", {}).get("fields_wired", {})), (
                f"Stale field name '{name}' found in L2 wiring summary fields_wired"
            )

    def test_w5_receipt_hitl_policy_ref_deferred(self):
        """hitl_policy_ref must be in deferred_fields, not in fully-wired fields."""
        receipt = json.loads(self._RECEIPT_PATH.read_text(encoding="utf-8"))
        deferred = receipt.get("deferred_fields", {})
        assert "profile_manifest.hitl_policy_ref" in deferred, (
            "hitl_policy_ref must appear in deferred_fields"
        )
        assert deferred["profile_manifest.hitl_policy_ref"].get("status") == "DEFERRED"
