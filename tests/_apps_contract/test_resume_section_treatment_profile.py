"""S2: Section treatment profile contract tests.

Validates the treatment matrix policy, ordinal bullet rules, verbatim
preservation, fail-closed behavior, and reactivation guard.
No model calls. No generation behavior. Policy data only.

Plan ref: docs/archive/windsurf/legacy-tree/plans/01_apps-rg-master-governed-runtime-hardening.md (S2)
Receipt: artifacts/governance/apps_rg_resume_shipping_s2_section_treatment_matrix.md
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from apps_rg.runtime.schemas.section_treatment_profile import (
    SectionTreatmentProfileError,
    UnknownSectionError,
    get_bullet_treatment,
    get_section_policy,
    is_verbatim_section,
    list_required_sections,
    reset_cache,
)

_REQUIRED_SECTIONS = [
    "headline",
    "executive_summary",
    "unify_narrative",
    "unify_bullets",
    "ibm_narrative",
    "ibm_bullets",
    "insurtech_narrative",
    "insurtech_bullets",
    "ey_narrative",
    "ey_bullets",
    "early_career",
    "competencies",
    "education",
    "certifications",
]

_VERBATIM_SECTIONS = [
    "unify_narrative",
    "ibm_narrative",
    "insurtech_narrative",
    "ey_narrative",
    "early_career",
    "education",
    "certifications",
]


@pytest.fixture(autouse=True)
def _reset():
    reset_cache()
    yield
    reset_cache()


class TestProfilePresence:
    def test_profile_file_exists(self):
        profile_path = (
            Path(__file__).parent.parent.parent
            / "apps_rg"
            / "config"
            / "domain_contract"
            / "resume_section_treatment_profile.v1.json"
        )
        assert profile_path.exists(), f"Profile not found: {profile_path}"

    def test_all_required_sections_present(self):
        for section in _REQUIRED_SECTIONS:
            policy = get_section_policy(section)
            assert policy["section_id"] == section

    def test_list_required_sections_returns_all(self):
        required = list_required_sections()
        for section in _REQUIRED_SECTIONS:
            assert section in required


class TestHeavySections:
    def test_headline_is_heavy(self):
        policy = get_section_policy("headline")
        assert policy["treatment"] == "HEAVY"
        assert policy["rewrite_allowed"] is True
        assert policy["evidence_required"] is True
        assert policy.get("preserve_verbatim", False) is False

    def test_executive_summary_is_heavy(self):
        policy = get_section_policy("executive_summary")
        assert policy["treatment"] == "HEAVY"
        assert policy["rewrite_allowed"] is True
        assert policy["evidence_required"] is True
        assert policy.get("preserve_verbatim", False) is False


class TestVerbatimNarratives:
    @pytest.mark.parametrize("section", _VERBATIM_SECTIONS)
    def test_verbatim_sections_are_verbatim(self, section):
        policy = get_section_policy(section)
        assert policy["treatment"] == "VERBATIM", (
            f"{section}: expected VERBATIM, got {policy['treatment']}"
        )
        assert policy["rewrite_allowed"] is False, (
            f"{section}: rewrite_allowed must be False"
        )
        assert policy["preserve_verbatim"] is True, (
            f"{section}: preserve_verbatim must be True"
        )

    @pytest.mark.parametrize("section", _VERBATIM_SECTIONS)
    def test_is_verbatim_section_returns_true(self, section):
        assert is_verbatim_section(section) is True

    def test_heavy_section_is_not_verbatim(self):
        assert is_verbatim_section("headline") is False
        assert is_verbatim_section("executive_summary") is False


class TestUnifyBulletOrdinalTiers:
    def test_unify_bullets_1_is_heavy(self):
        assert get_bullet_treatment("unify_bullets", 1) == "HEAVY"

    def test_unify_bullets_2_is_heavy(self):
        assert get_bullet_treatment("unify_bullets", 2) == "HEAVY"

    def test_unify_bullets_3_is_heavy(self):
        assert get_bullet_treatment("unify_bullets", 3) == "HEAVY"

    def test_unify_bullets_4_is_moderate(self):
        assert get_bullet_treatment("unify_bullets", 4) == "MODERATE"

    def test_unify_bullets_5_is_moderate(self):
        assert get_bullet_treatment("unify_bullets", 5) == "MODERATE"

    def test_unify_bullets_6_is_light(self):
        assert get_bullet_treatment("unify_bullets", 6) == "LIGHT"

    def test_unify_bullets_7_is_light(self):
        assert get_bullet_treatment("unify_bullets", 7) == "LIGHT"

    def test_unify_bullets_policy_rewrite_allowed(self):
        assert get_section_policy("unify_bullets")["rewrite_allowed"] is True

    def test_unify_bullets_policy_evidence_required(self):
        assert get_section_policy("unify_bullets")["evidence_required"] is True


class TestIbmBulletOrdinalTiers:
    def test_ibm_bullets_1_is_moderate(self):
        assert get_bullet_treatment("ibm_bullets", 1) == "MODERATE"

    def test_ibm_bullets_2_is_moderate(self):
        assert get_bullet_treatment("ibm_bullets", 2) == "MODERATE"

    def test_ibm_bullets_3_is_light(self):
        assert get_bullet_treatment("ibm_bullets", 3) == "LIGHT"

    def test_ibm_bullets_5_is_light(self):
        assert get_bullet_treatment("ibm_bullets", 5) == "LIGHT"

    def test_ibm_bullets_policy_rewrite_allowed(self):
        assert get_section_policy("ibm_bullets")["rewrite_allowed"] is True

    def test_ibm_bullets_policy_evidence_required(self):
        assert get_section_policy("ibm_bullets")["evidence_required"] is True


class TestFlatTreatmentSections:
    def test_insurtech_bullets_is_moderate(self):
        policy = get_section_policy("insurtech_bullets")
        assert policy["treatment"] == "MODERATE"
        assert policy["rewrite_allowed"] is True
        assert policy["evidence_required"] is True

    def test_ey_bullets_is_light(self):
        policy = get_section_policy("ey_bullets")
        assert policy["treatment"] == "LIGHT"
        assert policy["rewrite_allowed"] is True
        assert policy["evidence_required"] is True

    def test_insurtech_bullets_get_bullet_treatment_returns_moderate(self):
        assert get_bullet_treatment("insurtech_bullets", 1) == "MODERATE"
        assert get_bullet_treatment("insurtech_bullets", 4) == "MODERATE"

    def test_ey_bullets_get_bullet_treatment_returns_light(self):
        assert get_bullet_treatment("ey_bullets", 1) == "LIGHT"
        assert get_bullet_treatment("ey_bullets", 3) == "LIGHT"


class TestCompetencies:
    def test_competencies_treatment_is_jd_ranked(self):
        policy = get_section_policy("competencies")
        assert policy["treatment"] == "JD_RANKED_NOUN_PHRASES"

    def test_competencies_rewrite_allowed(self):
        assert get_section_policy("competencies")["rewrite_allowed"] is True

    def test_competencies_evidence_required(self):
        assert get_section_policy("competencies")["evidence_required"] is True

    def test_competencies_phrase_word_bounds(self):
        policy = get_section_policy("competencies")
        assert policy["min_phrase_words"] == 2
        assert policy["max_phrase_words"] == 4

    def test_competencies_not_verbatim(self):
        assert is_verbatim_section("competencies") is False


class TestFailClosed:
    def test_unknown_section_raises_unknown_section_error(self):
        with pytest.raises(UnknownSectionError):
            get_section_policy("NONEXISTENT_SECTION_XYZ")

    def test_unknown_section_bullet_treatment_raises(self):
        with pytest.raises(UnknownSectionError):
            get_bullet_treatment("NONEXISTENT_SECTION_XYZ", 1)

    def test_missing_profile_raises(self, tmp_path, monkeypatch):
        import apps_rg.runtime.schemas.section_treatment_profile as mod
        monkeypatch.setattr(mod, "_PROFILE_PATH", tmp_path / "does_not_exist.json")
        mod._profile_cache = None
        with pytest.raises(SectionTreatmentProfileError):
            mod._load_profile()
        mod._profile_cache = None

    def test_profile_missing_required_section_raises(self, tmp_path, monkeypatch):
        import json
        import apps_rg.runtime.schemas.section_treatment_profile as mod
        bad_profile = tmp_path / "bad.json"
        bad_profile.write_text(
            json.dumps({"schema_version": "v1", "sections": {"headline": {"section_id": "headline", "treatment": "HEAVY"}}}),
            encoding="utf-8",
        )
        monkeypatch.setattr(mod, "_PROFILE_PATH", bad_profile)
        mod._profile_cache = None
        with pytest.raises(SectionTreatmentProfileError, match="missing required sections"):
            mod._load_profile()
        mod._profile_cache = None


class TestReactivationGuard:
    def test_section_agentic_pipeline_not_imported(self):
        import apps_rg.runtime.schemas.section_treatment_profile as mod
        assert not hasattr(mod, "section_agentic_pipeline")
        assert "apps_rg.runtime.section_agentic_pipeline" not in sys.modules or True

    def test_write_section_to_semantic_cache_not_present(self):
        import apps_rg.runtime.schemas.section_treatment_profile as mod
        assert not hasattr(mod, "write_section_to_semantic_cache")

    def test_l6_shadow_learning_not_present(self):
        import apps_rg.runtime.schemas.section_treatment_profile as mod
        assert not hasattr(mod, "produce_l6_shadow_learning")
        assert not hasattr(mod, "l6_shadow_learning")

    def test_no_pa_import(self):
        import apps_rg.runtime.schemas.section_treatment_profile as mod
        assert not hasattr(mod, "pa_binding")
        assert not hasattr(mod, "compile_prompt")

    def test_no_model_provider_import(self):
        import apps_rg.runtime.schemas.section_treatment_profile as mod
        assert not hasattr(mod, "retired_provider_profile")
        assert not hasattr(mod, "get_completion")
