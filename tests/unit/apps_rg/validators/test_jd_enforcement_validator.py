"""Tests for apps_rg.validators.jd_enforcement_validator.JDEnforcementValidator.

Verifies the 15-rule enforcement surface restored from the 2025-12-08
atomization snapshot. See plan apps-rg-prior-art-gap-closure-3e3d5b.
"""

from __future__ import annotations

import pytest

try:
    from apps_rg.validators.jd_enforcement_validator import (
        JD_MIN_LENGTH_CHARS,
        JD_MIN_SKILL_COUNT,
        JDEnforcementResult,
        JDEnforcementRule,
        JDEnforcementValidator,
    )
except ModuleNotFoundError:
    pytest.skip(
        "apps-rg-unit-pytest-remediation-f7e2a9 W1: apps_rg.validators.jd_enforcement_validator "
        "not on disk.",
        allow_module_level=True,
    )


class TestJDInputValidation:
    """E1, E2 — JD input gate."""

    def test_e1_passes_for_jd_at_min_length(self) -> None:
        v = JDEnforcementValidator()
        results = v.validate_jd_input("A" * JD_MIN_LENGTH_CHARS, "GATE-0")
        assert len(results) == 2
        e1 = next(r for r in results if r.rule == JDEnforcementRule.E1_JD_MIN_LENGTH)
        assert e1.passed is True

    def test_e1_fails_below_min_length(self) -> None:
        v = JDEnforcementValidator()
        results = v.validate_jd_input("A" * (JD_MIN_LENGTH_CHARS - 1), "GATE-0")
        e1 = next(r for r in results if r.rule == JDEnforcementRule.E1_JD_MIN_LENGTH)
        assert e1.passed is False
        assert "min" in e1.details.lower()

    def test_e2_fails_for_none(self) -> None:
        v = JDEnforcementValidator()
        results = v.validate_jd_input(None, "GATE-0")
        e2 = next(r for r in results if r.rule == JDEnforcementRule.E2_JD_NON_NULL)
        assert e2.passed is False

    def test_e2_fails_for_whitespace_only(self) -> None:
        v = JDEnforcementValidator()
        results = v.validate_jd_input("    \n\t   ", "GATE-0")
        e2 = next(r for r in results if r.rule == JDEnforcementRule.E2_JD_NON_NULL)
        assert e2.passed is False

    def test_results_accumulated_across_calls(self) -> None:
        v = JDEnforcementValidator()
        v.validate_jd_input("A" * 200, "GATE-0")
        v.validate_jd_input("", "GATE-RETRY")
        all_results = v.get_all_results()
        assert len(all_results) == 4  # 2 rules × 2 calls

    def test_has_failures_reflects_aggregate(self) -> None:
        v = JDEnforcementValidator()
        v.validate_jd_input("A" * 200, "GATE-0")  # both pass
        assert v.has_failures() is False
        v.validate_jd_input("", "GATE-RETRY")  # both fail
        assert v.has_failures() is True
        assert len(v.get_failures()) == 2


class TestJDParsingAndExtraction:
    """E3, E4, E5 — parser + theme/skill extraction."""

    def test_e3_passes_for_non_empty_parsed_jd(self) -> None:
        v = JDEnforcementValidator()
        result = v.validate_jd_parsing({"title": "Senior SWE", "skills": ["python"]}, "GATE-1")
        assert result.passed is True
        assert result.rule == JDEnforcementRule.E3_JD_PARSING_SUCCESS

    def test_e3_fails_for_none_or_empty(self) -> None:
        v = JDEnforcementValidator()
        assert v.validate_jd_parsing(None, "GATE-1").passed is False
        assert v.validate_jd_parsing({}, "GATE-1").passed is False

    def test_e4_passes_when_themes_extracted(self) -> None:
        v = JDEnforcementValidator()
        assert v.validate_themes_extracted(["leadership", "scale"], "GATE-2").passed is True

    def test_e4_fails_when_no_themes(self) -> None:
        v = JDEnforcementValidator()
        assert v.validate_themes_extracted([], "GATE-2").passed is False
        assert v.validate_themes_extracted(None, "GATE-2").passed is False

    def test_e5_requires_min_skill_count(self) -> None:
        v = JDEnforcementValidator()
        skills_short = ["python", "kubernetes"]  # 2 < 5
        skills_full = ["python", "kubernetes", "aws", "terraform", "rust", "go"]  # 6 >= 5
        assert v.validate_skills_extracted(skills_short, "GATE-2").passed is False
        v2 = JDEnforcementValidator()
        result = v2.validate_skills_extracted(skills_full, "GATE-2")
        assert result.passed is True
        # E5 also caches keywords for downstream E9 checks.
        assert v2.jd_keywords == [str(s) for s in skills_full]
        assert len(v2.jd_keywords) >= JD_MIN_SKILL_COUNT


class TestDataflowAuditRules:
    """E6 .. E15 — dataflow audit via stage-evidence probes."""

    def test_unwired_stage_emits_failure(self) -> None:
        """When orchestrator passes None, the rule must fail (no silent pass)."""
        v = JDEnforcementValidator()
        result = v.validate_dataflow_stage(
            JDEnforcementRule.E6_JD_TO_THEMATIC,
            stage_evidence=None,
            gate_id="GATE-3",
        )
        assert result.passed is False
        assert "not provided" in result.details.lower()

    def test_e9_content_has_jd_keywords_fires_when_keywords_known(self) -> None:
        v = JDEnforcementValidator()
        v.validate_skills_extracted(
            ["Python", "Kubernetes", "AWS", "Terraform", "Rust"], "GATE-2"
        )
        # generated content includes one cached keyword → pass
        good = "Architected Python services on AWS managed by Terraform."
        assert (
            v.validate_dataflow_stage(
                JDEnforcementRule.E9_CONTENT_HAS_JD_KW, good, "GATE-9"
            ).passed
            is True
        )
        # generated content has zero keyword overlap → fail
        bad = "Wrote some C code for an embedded device."
        assert (
            v.validate_dataflow_stage(
                JDEnforcementRule.E9_CONTENT_HAS_JD_KW, bad, "GATE-9"
            ).passed
            is False
        )

    def test_e14_no_mock_data_interpreted_as_boolean(self) -> None:
        v = JDEnforcementValidator()
        # True → no mock used → pass
        assert (
            v.validate_dataflow_stage(
                JDEnforcementRule.E14_NO_MOCK_DATA, True, "AUDIT"
            ).passed
            is True
        )
        # False → mock used → fail
        assert (
            v.validate_dataflow_stage(
                JDEnforcementRule.E14_NO_MOCK_DATA, False, "AUDIT"
            ).passed
            is False
        )

    def test_generic_truthy_evidence_passes_for_generic_rule(self) -> None:
        v = JDEnforcementValidator()
        # E15 audit-trail dict with content → pass
        audit = {"jd_hash": "abc", "stage_log": ["GATE-0", "GATE-9"]}
        assert (
            v.validate_dataflow_stage(
                JDEnforcementRule.E15_COMPLETE_AUDIT, audit, "AUDIT"
            ).passed
            is True
        )

    def test_full_15_rule_surface_can_run_end_to_end(self) -> None:
        """Smoke test exercising every rule once."""
        v = JDEnforcementValidator()
        v.validate_jd_input("Looking for senior SWE. " * 20, "GATE-0")  # E1, E2
        v.validate_jd_parsing({"title": "Senior SWE"}, "GATE-1")  # E3
        v.validate_themes_extracted(["leadership"], "GATE-2")  # E4
        v.validate_skills_extracted(
            ["python", "k8s", "aws", "terraform", "rust", "go"], "GATE-2"
        )  # E5
        for rule in (
            JDEnforcementRule.E6_JD_TO_THEMATIC,
            JDEnforcementRule.E7_THEMATIC_USES_JD,
            JDEnforcementRule.E8_ARTIST_RECEIVES_JD,
            JDEnforcementRule.E10_ENRICHMENT_USES_JD,
            JDEnforcementRule.E11_VALIDATION_CHECKS_JD,
            JDEnforcementRule.E12_FILES_CONTAIN_JD,
            JDEnforcementRule.E13_QA_VERIFIES_JD,
        ):
            v.validate_dataflow_stage(rule, {"present": True}, "STAGE")
        v.validate_dataflow_stage(
            JDEnforcementRule.E9_CONTENT_HAS_JD_KW,
            "deployed python services on aws",
            "GATE-9",
        )
        v.validate_dataflow_stage(JDEnforcementRule.E14_NO_MOCK_DATA, True, "AUDIT")
        v.validate_dataflow_stage(
            JDEnforcementRule.E15_COMPLETE_AUDIT, {"trail": "present"}, "AUDIT"
        )

        rules_seen = {r.rule for r in v.get_all_results()}
        assert rules_seen == set(JDEnforcementRule)
        assert v.has_failures() is False


class TestOrchestratorImportContract:
    """Wiring contract: ResumeOrchestrator imports the real validator."""

    def test_orchestrator_re_exports_real_validator(self) -> None:
        from apps_rg.reasoning.ResumeOrchestrator import (
            JDEnforcementValidator as Reexported,
        )

        # Same class object (not a stub copy).
        assert Reexported is JDEnforcementValidator
        # Real method surface, not stub.
        v = Reexported()
        results = v.validate_jd_input("Hiring Senior SWE. " * 20, "GATE-0")
        assert isinstance(results, list)
        assert all(isinstance(r, JDEnforcementResult) for r in results)
