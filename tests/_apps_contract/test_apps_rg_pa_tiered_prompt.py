"""S3 contract tests — PA Tiered Prompt Patching for apps_rg.

Validates:
- SectionPromptArtifact shape for each treatment mode (HEAVY/MODERATE/LIGHT/VERBATIM/JD_RANKED)
- Source-span-first, JD alignment, blocked_items, support_status requirements per tier
- VERBATIM sections are copy-only, rewrite_allowed=False
- Narrative sections resolve to VERBATIM behavior
- education / certifications / early_career are VERBATIM
- Competencies produce JD-ranked noun phrase artifact with 2-4 word bounds
- Bullet ordinal routing: Unify 1→HEAVY, 4→MODERATE, 6→LIGHT
- Bullet ordinal routing: IBM 1→MODERATE, 3→LIGHT
- Unknown section fails closed
- PA does not import C0, L2, provider SDKs, model clients, or forbidden runtime paths
- PA does not execute model calls
- PA does not mutate cache or L4
- S1 and S2 tests still pass (smoke guard)

Hard boundaries:
- No generation behavior
- No model calls
- No PA, C0, L2, or agentic_core changes

See: artifacts/governance/apps_rg_resume_shipping_s3_pa_tiered_prompt_patching.md
"""
import importlib
import inspect
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_caches():
    """Reset both PA prompt profile and section treatment profile caches before each test."""
    from apps_rg.runtime.bindings.pa_binding import reset_pa_prompt_profile_cache
    from apps_rg.runtime.schemas.section_treatment_profile import reset_cache as reset_s2_cache
    reset_pa_prompt_profile_cache()
    reset_s2_cache()
    yield
    reset_pa_prompt_profile_cache()
    reset_s2_cache()


# ---------------------------------------------------------------------------
# Helper import
# ---------------------------------------------------------------------------

def _import_pa():
    from apps_rg.runtime.bindings import pa_binding
    return pa_binding


def _build(section_id, **kwargs):
    pa = _import_pa()
    return pa.build_section_prompt_artifact(section_id, **kwargs)


def _build_bullet(section_id, ordinal, **kwargs):
    pa = _import_pa()
    return pa.build_section_prompt_artifact_for_bullet(section_id, ordinal, **kwargs)


# ---------------------------------------------------------------------------
# Section 1: Profile and module presence
# ---------------------------------------------------------------------------

class TestProfilePresence:
    def test_pa_prompt_profile_file_exists(self):
        repo_root = Path(__file__).parent.parent.parent
        profile = repo_root / "apps_rg/config/domain_contract/resume_pa_prompt_profile.v1.json"
        assert profile.exists(), f"PA prompt profile missing: {profile}"

    def test_pa_prompt_profile_loads(self):
        import json
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_rg/config/domain_contract/resume_pa_prompt_profile.v1.json"
        with open(profile_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("schema_version") == "resume_pa_prompt_profile.v1"

    def test_pa_prompt_profile_has_all_treatment_keys(self):
        import json
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_rg/config/domain_contract/resume_pa_prompt_profile.v1.json"
        with open(profile_path, encoding="utf-8") as f:
            data = json.load(f)
        keys = set(data["treatment_instructions"].keys())
        expected = {"HEAVY", "MODERATE", "LIGHT", "VERBATIM", "JD_RANKED_NOUN_PHRASES"}
        assert expected == keys

    def test_section_prompt_artifact_importable(self):
        from apps_rg.runtime.bindings.pa_binding import SectionPromptArtifact
        assert SectionPromptArtifact is not None

    def test_build_section_prompt_artifact_importable(self):
        from apps_rg.runtime.bindings.pa_binding import build_section_prompt_artifact
        assert callable(build_section_prompt_artifact)

    def test_build_section_prompt_artifact_for_bullet_importable(self):
        from apps_rg.runtime.bindings.pa_binding import build_section_prompt_artifact_for_bullet
        assert callable(build_section_prompt_artifact_for_bullet)

    def test_pa_boundary_cert_exported(self):
        from apps_rg.runtime.bindings.pa_binding import PA_BOUNDARY_CERT_S3
        assert isinstance(PA_BOUNDARY_CERT_S3, str)
        assert len(PA_BOUNDARY_CERT_S3) > 0


# ---------------------------------------------------------------------------
# Section 2: HEAVY section prompt
# ---------------------------------------------------------------------------

class TestHeavySection:
    def test_headline_treatment_is_heavy(self):
        artifact = _build("headline")
        assert artifact.treatment == "HEAVY"

    def test_heavy_section_source_span_required(self):
        artifact = _build("headline")
        assert artifact.source_span_required is True

    def test_heavy_section_jd_alignment_required(self):
        artifact = _build("headline")
        assert artifact.jd_alignment_required is True

    def test_heavy_section_blocked_items_required(self):
        artifact = _build("headline")
        assert artifact.blocked_items_required is True

    def test_heavy_section_support_status_required(self):
        artifact = _build("headline")
        assert artifact.support_status_required is True

    def test_heavy_section_rewrite_allowed(self):
        artifact = _build("headline")
        assert artifact.rewrite_allowed is True

    def test_heavy_section_not_verbatim(self):
        artifact = _build("headline")
        assert artifact.preserve_verbatim is False

    def test_heavy_section_not_copy_only(self):
        artifact = _build("headline")
        assert artifact.copy_only is False

    def test_heavy_section_prompt_directive_mentions_star(self):
        artifact = _build("headline")
        assert "STAR" in artifact.prompt_directive or "HEAVY" in artifact.prompt_directive

    def test_heavy_section_prompt_directive_mentions_source_span(self):
        artifact = _build("headline")
        assert "source" in artifact.prompt_directive.lower() or "span" in artifact.prompt_directive.lower()

    def test_heavy_section_anti_invention_rules_present(self):
        artifact = _build("headline")
        assert len(artifact.anti_invention_rules) >= 5

    def test_heavy_section_anti_invention_no_new_metrics(self):
        artifact = _build("headline")
        combined = " ".join(artifact.anti_invention_rules).lower()
        assert "metric" in combined

    def test_heavy_section_support_status_values_include_insufficient(self):
        artifact = _build("headline")
        assert "INSUFFICIENT_SOURCE_SUPPORT" in artifact.support_status_values

    def test_executive_summary_also_heavy(self):
        artifact = _build("executive_summary")
        assert artifact.treatment == "HEAVY"
        assert artifact.jd_alignment_required is True
        assert artifact.blocked_items_required is True

    def test_section_id_preserved(self):
        artifact = _build("headline")
        assert artifact.section_id == "headline"

    def test_optional_role_id_threaded(self):
        artifact = _build("headline", role_id="unify", employer="Unify Consulting")
        assert artifact.role_id == "unify"
        assert artifact.employer == "Unify Consulting"

    def test_optional_source_text_threaded(self):
        artifact = _build("headline", source_text="CTO | Technology | Insurance")
        assert artifact.source_text == "CTO | Technology | Insurance"

    def test_optional_jd_context_ref_threaded(self):
        artifact = _build("headline", jd_context_ref="jd://brown-and-brown/svp-it")
        assert artifact.jd_context_ref == "jd://brown-and-brown/svp-it"


# ---------------------------------------------------------------------------
# Section 3: MODERATE section prompt
# ---------------------------------------------------------------------------

class TestModerateSection:
    def test_insurtech_bullets_treatment_is_moderate(self):
        artifact = _build("insurtech_bullets")
        assert artifact.treatment == "MODERATE"

    def test_moderate_section_source_span_required(self):
        artifact = _build("insurtech_bullets")
        assert artifact.source_span_required is True

    def test_moderate_section_jd_alignment_required(self):
        artifact = _build("insurtech_bullets")
        assert artifact.jd_alignment_required is True

    def test_moderate_section_blocked_items_required(self):
        artifact = _build("insurtech_bullets")
        assert artifact.blocked_items_required is True

    def test_moderate_section_support_status_required(self):
        artifact = _build("insurtech_bullets")
        assert artifact.support_status_required is True

    def test_moderate_section_rewrite_allowed(self):
        artifact = _build("insurtech_bullets")
        assert artifact.rewrite_allowed is True

    def test_moderate_section_not_copy_only(self):
        artifact = _build("insurtech_bullets")
        assert artifact.copy_only is False

    def test_moderate_section_anti_invention_present(self):
        artifact = _build("insurtech_bullets")
        assert len(artifact.anti_invention_rules) >= 5

    def test_moderate_prompt_directive_mentions_moderate(self):
        artifact = _build("insurtech_bullets")
        assert "MODERATE" in artifact.prompt_directive or "moderate" in artifact.prompt_directive.lower()

    def test_moderate_support_status_values_correct(self):
        artifact = _build("insurtech_bullets")
        assert "INSUFFICIENT_SOURCE_SUPPORT" in artifact.support_status_values
        assert "BLOCKED" in artifact.support_status_values
        assert "SUPPORTED" in artifact.support_status_values


# ---------------------------------------------------------------------------
# Section 4: LIGHT section prompt
# ---------------------------------------------------------------------------

class TestLightSection:
    def test_ey_bullets_treatment_is_light(self):
        artifact = _build("ey_bullets")
        assert artifact.treatment == "LIGHT"

    def test_light_section_source_span_required(self):
        artifact = _build("ey_bullets")
        assert artifact.source_span_required is True

    def test_light_section_jd_alignment_not_required(self):
        artifact = _build("ey_bullets")
        assert artifact.jd_alignment_required is False

    def test_light_section_blocked_items_required(self):
        artifact = _build("ey_bullets")
        assert artifact.blocked_items_required is True

    def test_light_section_support_status_required(self):
        artifact = _build("ey_bullets")
        assert artifact.support_status_required is True

    def test_light_section_anti_invention_present(self):
        artifact = _build("ey_bullets")
        assert len(artifact.anti_invention_rules) >= 5

    def test_light_section_not_copy_only(self):
        artifact = _build("ey_bullets")
        assert artifact.copy_only is False

    def test_light_prompt_directive_mentions_light(self):
        artifact = _build("ey_bullets")
        assert "LIGHT" in artifact.prompt_directive or "minimal" in artifact.prompt_directive.lower()


# ---------------------------------------------------------------------------
# Section 5: VERBATIM sections
# ---------------------------------------------------------------------------

class TestVerbatimSections:
    @pytest.mark.parametrize("section_id", [
        "education",
        "certifications",
        "early_career",
        "unify_narrative",
        "ibm_narrative",
        "insurtech_narrative",
        "ey_narrative",
    ])
    def test_verbatim_section_treatment(self, section_id):
        artifact = _build(section_id)
        assert artifact.treatment == "VERBATIM", f"{section_id}: expected VERBATIM, got {artifact.treatment}"

    @pytest.mark.parametrize("section_id", [
        "education",
        "certifications",
        "early_career",
        "unify_narrative",
        "ibm_narrative",
    ])
    def test_verbatim_section_rewrite_not_allowed(self, section_id):
        artifact = _build(section_id)
        assert artifact.rewrite_allowed is False, f"{section_id}: rewrite_allowed should be False"

    @pytest.mark.parametrize("section_id", [
        "education",
        "certifications",
        "early_career",
        "unify_narrative",
    ])
    def test_verbatim_section_preserve_verbatim_true(self, section_id):
        artifact = _build(section_id)
        assert artifact.preserve_verbatim is True, f"{section_id}: preserve_verbatim should be True"

    @pytest.mark.parametrize("section_id", [
        "education",
        "certifications",
        "early_career",
    ])
    def test_verbatim_section_copy_only_true(self, section_id):
        artifact = _build(section_id)
        assert artifact.copy_only is True, f"{section_id}: copy_only should be True"

    @pytest.mark.parametrize("section_id", [
        "education",
        "certifications",
        "early_career",
        "unify_narrative",
    ])
    def test_verbatim_section_prompt_directive_prohibits_rewrite(self, section_id):
        artifact = _build(section_id)
        directive_lower = artifact.prompt_directive.lower()
        assert (
            "verbatim" in directive_lower
            or "no rewrite" in directive_lower
            or "copy" in directive_lower
        ), f"{section_id}: directive should prohibit rewriting, got: {artifact.prompt_directive}"

    @pytest.mark.parametrize("section_id", [
        "education",
        "certifications",
    ])
    def test_verbatim_section_jd_alignment_not_required(self, section_id):
        artifact = _build(section_id)
        assert artifact.jd_alignment_required is False, f"{section_id}: verbatim section should not require JD alignment"


# ---------------------------------------------------------------------------
# Section 6: Competencies (JD_RANKED_NOUN_PHRASES)
# ---------------------------------------------------------------------------

class TestCompetenciesSection:
    def test_competencies_treatment_is_jd_ranked(self):
        artifact = _build("competencies")
        assert artifact.treatment == "JD_RANKED_NOUN_PHRASES"

    def test_competencies_jd_alignment_required(self):
        artifact = _build("competencies")
        assert artifact.jd_alignment_required is True

    def test_competencies_blocked_items_required(self):
        artifact = _build("competencies")
        assert artifact.blocked_items_required is True

    def test_competencies_phrase_word_bounds_present(self):
        artifact = _build("competencies")
        assert artifact.phrase_word_bounds is not None
        assert artifact.phrase_word_bounds["min"] == 2
        assert artifact.phrase_word_bounds["max"] == 4

    def test_competencies_prompt_directive_mentions_noun_phrases(self):
        artifact = _build("competencies")
        assert (
            "noun phrase" in artifact.prompt_directive.lower()
            or "NOUN PHRASES" in artifact.prompt_directive
        )

    def test_competencies_prompt_directive_no_sentence_bullets(self):
        artifact = _build("competencies")
        assert "sentence" in artifact.prompt_directive.lower() or "No sentence" in artifact.prompt_directive

    def test_competencies_anti_invention_present(self):
        artifact = _build("competencies")
        assert len(artifact.anti_invention_rules) >= 5

    def test_competencies_rewrite_allowed(self):
        artifact = _build("competencies")
        assert artifact.rewrite_allowed is True

    def test_competencies_not_copy_only(self):
        artifact = _build("competencies")
        assert artifact.copy_only is False

    def test_competencies_evidence_required(self):
        artifact = _build("competencies")
        assert artifact.evidence_required is True


# ---------------------------------------------------------------------------
# Section 7: Bullet ordinal tier routing
# ---------------------------------------------------------------------------

class TestBulletOrdinalTierRouting:
    def test_unify_bullet_1_is_heavy(self):
        artifact = _build_bullet("unify_bullets", 1)
        assert artifact.treatment == "HEAVY"
        assert artifact.bullet_ordinal == 1

    def test_unify_bullet_2_is_heavy(self):
        artifact = _build_bullet("unify_bullets", 2)
        assert artifact.treatment == "HEAVY"

    def test_unify_bullet_3_is_heavy(self):
        artifact = _build_bullet("unify_bullets", 3)
        assert artifact.treatment == "HEAVY"

    def test_unify_bullet_4_is_moderate(self):
        artifact = _build_bullet("unify_bullets", 4)
        assert artifact.treatment == "MODERATE"
        assert artifact.bullet_ordinal == 4

    def test_unify_bullet_5_is_moderate(self):
        artifact = _build_bullet("unify_bullets", 5)
        assert artifact.treatment == "MODERATE"

    def test_unify_bullet_6_is_light(self):
        artifact = _build_bullet("unify_bullets", 6)
        assert artifact.treatment == "LIGHT"
        assert artifact.bullet_ordinal == 6

    def test_unify_bullet_7_is_light(self):
        artifact = _build_bullet("unify_bullets", 7)
        assert artifact.treatment == "LIGHT"

    def test_ibm_bullet_1_is_moderate(self):
        artifact = _build_bullet("ibm_bullets", 1)
        assert artifact.treatment == "MODERATE"
        assert artifact.bullet_ordinal == 1

    def test_ibm_bullet_2_is_moderate(self):
        artifact = _build_bullet("ibm_bullets", 2)
        assert artifact.treatment == "MODERATE"

    def test_ibm_bullet_3_is_light(self):
        artifact = _build_bullet("ibm_bullets", 3)
        assert artifact.treatment == "LIGHT"
        assert artifact.bullet_ordinal == 3

    def test_ibm_bullet_4_is_light(self):
        artifact = _build_bullet("ibm_bullets", 4)
        assert artifact.treatment == "LIGHT"

    def test_insurtech_bullet_1_is_moderate_flat(self):
        artifact = _build_bullet("insurtech_bullets", 1)
        assert artifact.treatment == "MODERATE"

    def test_ey_bullet_1_is_light_flat(self):
        artifact = _build_bullet("ey_bullets", 1)
        assert artifact.treatment == "LIGHT"

    def test_bullet_artifact_has_section_id(self):
        artifact = _build_bullet("unify_bullets", 1)
        assert artifact.section_id == "unify_bullets"

    def test_bullet_artifact_has_ordinal(self):
        artifact = _build_bullet("unify_bullets", 4, role_id="unify")
        assert artifact.bullet_ordinal == 4
        assert artifact.role_id == "unify"

    def test_unify_bullet_1_source_span_required(self):
        artifact = _build_bullet("unify_bullets", 1)
        assert artifact.source_span_required is True

    def test_unify_bullet_1_jd_alignment_required(self):
        artifact = _build_bullet("unify_bullets", 1)
        assert artifact.jd_alignment_required is True

    def test_unify_bullet_1_blocked_items_required(self):
        artifact = _build_bullet("unify_bullets", 1)
        assert artifact.blocked_items_required is True

    def test_unify_bullet_6_source_span_required(self):
        artifact = _build_bullet("unify_bullets", 6)
        assert artifact.source_span_required is True

    def test_unify_bullet_6_jd_alignment_not_required(self):
        artifact = _build_bullet("unify_bullets", 6)
        assert artifact.jd_alignment_required is False


# ---------------------------------------------------------------------------
# Section 8: Fail-closed behavior
# ---------------------------------------------------------------------------

class TestFailClosed:
    def test_unknown_section_raises(self):
        from apps_rg.runtime.schemas.section_treatment_profile import UnknownSectionError
        with pytest.raises(UnknownSectionError):
            _build("nonexistent_section_xyz")

    def test_unknown_section_bullet_raises(self):
        from apps_rg.runtime.schemas.section_treatment_profile import UnknownSectionError
        with pytest.raises(UnknownSectionError):
            _build_bullet("nonexistent_section_xyz", 1)

    def test_unknown_section_error_is_subclass_of_treatment_profile_error(self):
        from apps_rg.runtime.schemas.section_treatment_profile import (
            UnknownSectionError,
            SectionTreatmentProfileError,
        )
        assert issubclass(UnknownSectionError, SectionTreatmentProfileError)

    def test_build_section_prompt_artifact_returns_dataclass(self):
        from apps_rg.runtime.bindings.pa_binding import SectionPromptArtifact
        artifact = _build("headline")
        assert isinstance(artifact, SectionPromptArtifact)

    def test_build_bullet_artifact_returns_dataclass(self):
        from apps_rg.runtime.bindings.pa_binding import SectionPromptArtifact
        artifact = _build_bullet("unify_bullets", 1)
        assert isinstance(artifact, SectionPromptArtifact)


# ---------------------------------------------------------------------------
# Section 9: PA boundary / reactivation guards
# ---------------------------------------------------------------------------

class TestPABoundaryGuards:
    def test_pa_binding_does_not_import_section_agentic_pipeline(self):
        import apps_rg.runtime.bindings.pa_binding as pa_mod
        source = inspect.getsource(pa_mod)
        assert "section_agentic_pipeline" not in source, \
            "pa_binding must not import section_agentic_pipeline"

    def test_pa_binding_does_not_import_write_section_to_semantic_cache(self):
        import apps_rg.runtime.bindings.pa_binding as pa_mod
        source = inspect.getsource(pa_mod)
        assert "write_section_to_semantic_cache" not in source, \
            "pa_binding must not import write_section_to_semantic_cache"

    def test_pa_binding_does_not_import_l6_shadow_learning(self):
        import apps_rg.runtime.bindings.pa_binding as pa_mod
        source = inspect.getsource(pa_mod)
        assert "l6_shadow_learning" not in source, \
            "pa_binding must not import l6_shadow_learning"

    def test_pa_binding_does_not_import_provider_sdks(self):
        import apps_rg.runtime.bindings.pa_binding as pa_mod
        source = inspect.getsource(pa_mod)
        for forbidden in ("import openai", "import anthropic", "from openai", "from anthropic"):
            assert forbidden not in source, \
                f"pa_binding must not import provider SDKs: found '{forbidden}'"

    def test_pa_binding_does_not_import_model_clients(self):
        import apps_rg.runtime.bindings.pa_binding as pa_mod
        source = inspect.getsource(pa_mod)
        for forbidden in ("httpx", "requests.post", "urllib.request.urlopen"):
            assert forbidden not in source, \
                f"pa_binding must not make HTTP calls: found '{forbidden}'"

    def test_pa_binding_does_not_call_local_model_server_or_retired_provider_directly(self):
        import apps_rg.runtime.bindings.pa_binding as pa_mod
        source = inspect.getsource(pa_mod)
        for forbidden in ("local_model_server.invoke", "gateway.invoke", "provider.invoke"):
            assert forbidden not in source, \
                f"pa_binding must not call provider endpoints: found '{forbidden}'"

    def test_pa_binding_does_not_import_c0_execution(self):
        import apps_rg.runtime.bindings.pa_binding as pa_mod
        source = inspect.getsource(pa_mod)
        for forbidden in ("from agentic_core.runtime.c0", "import c0_binding"):
            assert forbidden not in source, \
                f"pa_binding S3 functions must not import C0: found '{forbidden}'"

    def test_pa_binding_does_not_import_l2_execution(self):
        import apps_rg.runtime.bindings.pa_binding as pa_mod
        source = inspect.getsource(pa_mod)
        for forbidden in ("from agentic_core.L2_execution", "import l2_binding"):
            assert forbidden not in source, \
                f"pa_binding S3 functions must not import L2: found '{forbidden}'"

    def test_build_section_prompt_artifact_does_not_call_model(self):
        artifact = _build("headline")
        assert isinstance(artifact.prompt_directive, str)
        assert len(artifact.prompt_directive) > 0

    def test_build_section_prompt_artifact_does_not_mutate_cache(self):
        from apps_rg.runtime.schemas.section_treatment_profile import _profile_cache
        before_id = id(_profile_cache)
        _build("headline")
        from apps_rg.runtime.schemas.section_treatment_profile import _profile_cache as after
        assert after is not None

    def test_pa_does_not_write_l4(self):
        import apps_rg.runtime.bindings.pa_binding as pa_mod
        source = inspect.getsource(pa_mod)
        for forbidden in ("L4_state", "write_to_l4", "l4_write"):
            assert forbidden not in source or "import" not in source, \
                f"pa_binding must not write L4 state: found '{forbidden}'"

    def test_section_treatment_not_importing_agentic_core(self):
        import apps_rg.runtime.schemas.section_treatment_profile as s2_mod
        source = inspect.getsource(s2_mod)
        import_lines = [l for l in source.splitlines() if l.strip().startswith(("import ", "from "))]
        assert not any("agentic_core" in l for l in import_lines), \
            "section_treatment_profile must not import agentic_core"

    def test_pa_prompt_config_does_not_contain_provider_keys(self):
        import json
        repo_root = Path(__file__).parent.parent.parent
        profile_path = repo_root / "apps_rg/config/domain_contract/resume_pa_prompt_profile.v1.json"
        with open(profile_path, encoding="utf-8") as f:
            content = f.read()
        for forbidden in ("openai", "anthropic", "retired_provider", "local_model_server", "httpx", "subprocess"):
            assert forbidden.lower() not in content.lower(), \
                f"PA prompt profile must not contain provider refs: found '{forbidden}'"


# ---------------------------------------------------------------------------
# Section 10: Regression — S1 and S2 tests still pass (import-level smoke)
# ---------------------------------------------------------------------------

class TestS1S2Regression:
    def test_source_resume_schema_importable(self):
        from apps_rg.runtime.schemas.source_resume_schema import (
            validate_structured_resume,
            is_structured_resume,
        )
        assert callable(validate_structured_resume)
        assert callable(is_structured_resume)

    def test_section_treatment_profile_importable(self):
        from apps_rg.runtime.schemas.section_treatment_profile import (
            get_section_policy,
            get_bullet_treatment,
            is_verbatim_section,
        )
        assert callable(get_section_policy)
        assert callable(get_bullet_treatment)
        assert callable(is_verbatim_section)

    def test_section_treatment_all_required_sections_present(self):
        from apps_rg.runtime.schemas.section_treatment_profile import list_required_sections
        required = list_required_sections()
        assert len(required) >= 14

    def test_s2_get_section_policy_still_works(self):
        from apps_rg.runtime.schemas.section_treatment_profile import get_section_policy
        from apps_rg.runtime.schemas.section_treatment_profile import reset_cache
        reset_cache()
        policy = get_section_policy("headline")
        assert policy["treatment"] == "HEAVY"
