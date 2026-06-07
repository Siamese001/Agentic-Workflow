"""W2: PA Binding Role Tiering Tests

Validates that pa_binding.py correctly assigns treatment tiers per role and bullet ordinal.

Plan ref: docs/archive/windsurf/legacy-tree/plans/01_apps-rg-master-governed-runtime-hardening.md (W2/S3)
"""
from __future__ import annotations

import pytest
from pathlib import Path

from apps_rg.runtime.bindings.pa_binding import (
    build_section_prompt_artifact,
    build_section_prompt_artifact_for_bullet,
    SectionPromptArtifact,
)
from apps_rg.runtime.schemas.section_treatment_profile import (
    get_section_policy,
    get_bullet_treatment,
    is_verbatim_section,
)


class TestSectionTierAssignment:
    """Test correct tier assignment for each canonical section."""

    def test_headline_is_heavy(self):
        """headline must have HEAVY treatment."""
        policy = get_section_policy("headline")
        assert policy["treatment"] == "HEAVY"
        assert policy["rewrite_allowed"] is True
        assert policy["preserve_verbatim"] is False

    def test_executive_summary_is_heavy(self):
        """executive_summary must have HEAVY treatment."""
        policy = get_section_policy("executive_summary")
        assert policy["treatment"] == "HEAVY"
        assert policy["rewrite_allowed"] is True
        assert policy["preserve_verbatim"] is False

    def test_competencies_is_moderate(self):
        """competencies must have JD_RANKED_NOUN_PHRASES (moderate)."""
        policy = get_section_policy("competencies")
        assert policy["treatment"] == "JD_RANKED_NOUN_PHRASES"
        assert policy["rewrite_allowed"] is True
        assert policy.get("min_phrase_words") == 2
        assert policy.get("max_phrase_words") == 4

    def test_education_is_verbatim(self):
        """education must be VERBATIM."""
        policy = get_section_policy("education")
        assert policy["treatment"] == "VERBATIM"
        assert policy["rewrite_allowed"] is False
        assert policy["preserve_verbatim"] is True
        assert is_verbatim_section("education") is True

    def test_certifications_is_verbatim(self):
        """certifications must be VERBATIM."""
        policy = get_section_policy("certifications")
        assert policy["treatment"] == "VERBATIM"
        assert policy["rewrite_allowed"] is False
        assert policy["preserve_verbatim"] is True
        assert is_verbatim_section("certifications") is True

    def test_early_career_is_verbatim(self):
        """early_career must be VERBATIM."""
        policy = get_section_policy("early_career")
        assert policy["treatment"] == "VERBATIM"
        assert policy["rewrite_allowed"] is False
        assert policy["preserve_verbatim"] is True
        assert is_verbatim_section("early_career") is True


class TestUnifyBulletTiering:
    """Test Unify Consulting bullet ordinal tiering: 1-3 heavy, 4-5 moderate, 6+ light."""

    def test_unify_bullets_1_is_heavy(self):
        """Unify bullet 1 must be HEAVY."""
        treatment = get_bullet_treatment("unify_bullets", 1)
        assert treatment == "HEAVY"

    def test_unify_bullets_2_is_heavy(self):
        """Unify bullet 2 must be HEAVY."""
        treatment = get_bullet_treatment("unify_bullets", 2)
        assert treatment == "HEAVY"

    def test_unify_bullets_3_is_heavy(self):
        """Unify bullet 3 must be HEAVY."""
        treatment = get_bullet_treatment("unify_bullets", 3)
        assert treatment == "HEAVY"

    def test_unify_bullets_4_is_moderate(self):
        """Unify bullet 4 must be MODERATE."""
        treatment = get_bullet_treatment("unify_bullets", 4)
        assert treatment == "MODERATE"

    def test_unify_bullets_5_is_moderate(self):
        """Unify bullet 5 must be MODERATE."""
        treatment = get_bullet_treatment("unify_bullets", 5)
        assert treatment == "MODERATE"

    def test_unify_bullets_6_is_light(self):
        """Unify bullet 6 must be LIGHT."""
        treatment = get_bullet_treatment("unify_bullets", 6)
        assert treatment == "LIGHT"

    def test_unify_bullets_7_is_light(self):
        """Unify bullet 7+ must be LIGHT."""
        treatment = get_bullet_treatment("unify_bullets", 7)
        assert treatment == "LIGHT"
        treatment = get_bullet_treatment("unify_bullets", 10)
        assert treatment == "LIGHT"


class TestIBMBulletTiering:
    """Test IBM bullet ordinal tiering: 1-2 moderate, 3-5 light."""

    def test_ibm_bullets_1_is_moderate(self):
        """IBM bullet 1 must be MODERATE."""
        treatment = get_bullet_treatment("ibm_bullets", 1)
        assert treatment == "MODERATE"

    def test_ibm_bullets_2_is_moderate(self):
        """IBM bullet 2 must be MODERATE."""
        treatment = get_bullet_treatment("ibm_bullets", 2)
        assert treatment == "MODERATE"

    def test_ibm_bullets_3_is_light(self):
        """IBM bullet 3 must be LIGHT."""
        treatment = get_bullet_treatment("ibm_bullets", 3)
        assert treatment == "LIGHT"

    def test_ibm_bullets_4_is_light(self):
        """IBM bullet 4 must be LIGHT."""
        treatment = get_bullet_treatment("ibm_bullets", 4)
        assert treatment == "LIGHT"

    def test_ibm_bullets_5_is_light(self):
        """IBM bullet 5 must be LIGHT."""
        treatment = get_bullet_treatment("ibm_bullets", 5)
        assert treatment == "LIGHT"


class TestInsurTechBulletTiering:
    """Test InsurTech bullet tiering: all moderate."""

    def test_insurtech_bullets_is_moderate(self):
        """InsurTech bullets must be MODERATE."""
        policy = get_section_policy("insurtech_bullets")
        assert policy["treatment"] == "MODERATE"


class TestEYBulletTiering:
    """Test EY bullet tiering: all light."""

    def test_ey_bullets_is_light(self):
        """EY bullets must be LIGHT."""
        policy = get_section_policy("ey_bullets")
        assert policy["treatment"] == "LIGHT"


class TestPABuildSectionPromptArtifact:
    """Test PA builds correct SectionPromptArtifact for sections."""

    def test_build_headline_artifact(self):
        """headline artifact has correct tier and flags."""
        artifact = build_section_prompt_artifact("headline")
        assert artifact.section_id == "headline"
        assert artifact.treatment == "HEAVY"
        assert artifact.rewrite_allowed is True
        assert artifact.preserve_verbatim is False
        assert artifact.evidence_required is True

    def test_build_education_artifact_is_verbatim(self):
        """education artifact is verbatim with correct flags."""
        artifact = build_section_prompt_artifact("education")
        assert artifact.section_id == "education"
        assert artifact.treatment == "VERBATIM"
        assert artifact.rewrite_allowed is False
        assert artifact.preserve_verbatim is True
        assert artifact.copy_only is True

    def test_build_executive_summary_artifact(self):
        """executive_summary artifact has correct tier."""
        artifact = build_section_prompt_artifact("executive_summary")
        assert artifact.section_id == "executive_summary"
        assert artifact.treatment == "HEAVY"
        assert artifact.rewrite_allowed is True


class TestPABuildBulletArtifact:
    """Test PA builds correct SectionPromptArtifact for bullets with ordinal tiering."""

    def test_build_unify_bullet_1_heavy(self):
        """Unify bullet 1 artifact is HEAVY."""
        artifact = build_section_prompt_artifact_for_bullet("unify_bullets", 1)
        assert artifact.section_id == "unify_bullets"
        assert artifact.treatment == "HEAVY"
        assert artifact.bullet_ordinal == 1
        assert artifact.rewrite_allowed is True

    def test_build_unify_bullet_4_moderate(self):
        """Unify bullet 4 artifact is MODERATE."""
        artifact = build_section_prompt_artifact_for_bullet("unify_bullets", 4)
        assert artifact.treatment == "MODERATE"
        assert artifact.bullet_ordinal == 4

    def test_build_unify_bullet_6_light(self):
        """Unify bullet 6 artifact is LIGHT."""
        artifact = build_section_prompt_artifact_for_bullet("unify_bullets", 6)
        assert artifact.treatment == "LIGHT"
        assert artifact.bullet_ordinal == 6

    def test_build_ibm_bullet_1_moderate(self):
        """IBM bullet 1 artifact is MODERATE."""
        artifact = build_section_prompt_artifact_for_bullet("ibm_bullets", 1)
        assert artifact.treatment == "MODERATE"
        assert artifact.bullet_ordinal == 1

    def test_build_ibm_bullet_3_light(self):
        """IBM bullet 3 artifact is LIGHT."""
        artifact = build_section_prompt_artifact_for_bullet("ibm_bullets", 3)
        assert artifact.treatment == "LIGHT"
        assert artifact.bullet_ordinal == 3

    def test_build_insurtech_bullet_moderate(self):
        """InsurTech bullet artifact is MODERATE (flat, not tiered)."""
        artifact = build_section_prompt_artifact_for_bullet("insurtech_bullets", 1)
        assert artifact.treatment == "MODERATE"
        artifact = build_section_prompt_artifact_for_bullet("insurtech_bullets", 5)
        assert artifact.treatment == "MODERATE"

    def test_build_ey_bullet_light(self):
        """EY bullet artifact is LIGHT (flat, not tiered)."""
        artifact = build_section_prompt_artifact_for_bullet("ey_bullets", 1)
        assert artifact.treatment == "LIGHT"
        artifact = build_section_prompt_artifact_for_bullet("ey_bullets", 3)
        assert artifact.treatment == "LIGHT"


class TestRoleIdAndEmployerPropagation:
    """Test role_id and employer propagate through PA artifacts."""

    def test_role_id_in_unify_artifact(self):
        """Unify artifact carries role_id."""
        artifact = build_section_prompt_artifact_for_bullet(
            "unify_bullets", 1, role_id="unify", employer="Unify Consulting"
        )
        assert artifact.role_id == "unify"
        assert artifact.employer == "Unify Consulting"

    def test_role_id_in_ibm_artifact(self):
        """IBM artifact carries role_id."""
        artifact = build_section_prompt_artifact_for_bullet(
            "ibm_bullets", 1, role_id="ibm", employer="IBM"
        )
        assert artifact.role_id == "ibm"
        assert artifact.employer == "IBM"


class TestNarrativeSectionsAreVerbatim:
    """Test that narrative sections are verbatim, not rewritten."""

    def test_unify_narrative_is_verbatim(self):
        """unify_narrative must be VERBATIM."""
        policy = get_section_policy("unify_narrative")
        assert policy["treatment"] == "VERBATIM"
        assert policy["preserve_verbatim"] is True

    def test_ibm_narrative_is_verbatim(self):
        """ibm_narrative must be VERBATIM."""
        policy = get_section_policy("ibm_narrative")
        assert policy["treatment"] == "VERBATIM"
        assert policy["preserve_verbatim"] is True

    def test_insurtech_narrative_is_verbatim(self):
        """insurtech_narrative must be VERBATIM."""
        policy = get_section_policy("insurtech_narrative")
        assert policy["treatment"] == "VERBATIM"
        assert policy["preserve_verbatim"] is True

    def test_ey_narrative_is_verbatim(self):
        """ey_narrative must be VERBATIM."""
        policy = get_section_policy("ey_narrative")
        assert policy["treatment"] == "VERBATIM"
        assert policy["preserve_verbatim"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
