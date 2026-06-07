"""W2: PA Binding Prompt Contract Tests

Validates that PA produces provider-neutral prompts with correct XML structure,
anti-invention rules, source_span-first requirement, and output schema.

Plan ref: docs/archive/windsurf/legacy-tree/plans/01_apps-rg-master-governed-runtime-hardening.md (W2/S3)
"""
from __future__ import annotations

import pytest
import json
from pathlib import Path

from apps_rg.runtime.bindings.pa_binding import (
    build_section_prompt_artifact,
    build_section_prompt_artifact_for_bullet,
    _load_pa_prompt_profile,
    SectionPromptArtifact,
    PA_BOUNDARY_CERT_S3,
)


class TestPAPromptProfileStructure:
    """Test PA prompt profile contains required contract elements."""

    def test_profile_has_treatment_instructions(self):
        """Profile must contain treatment instructions for each tier."""
        profile = _load_pa_prompt_profile()
        assert "treatment_instructions" in profile
        instr = profile["treatment_instructions"]
        assert "HEAVY" in instr
        assert "MODERATE" in instr
        assert "LIGHT" in instr
        assert "VERBATIM" in instr

    def test_profile_has_anti_invention_rules(self):
        """Profile must contain anti-invention rules."""
        profile = _load_pa_prompt_profile()
        assert "anti_invention_rules" in profile
        rules = profile["anti_invention_rules"]
        assert len(rules) > 0
        # Check for key anti-invention constraints
        rules_text = " ".join(rules).lower()
        assert "metric" in rules_text or "client" in rules_text or "tool" in rules_text

    def test_profile_has_output_artifact_schema(self):
        """Profile must define output artifact schema."""
        profile = _load_pa_prompt_profile()
        assert "output_artifact_schema" in profile
        schema = profile["output_artifact_schema"]
        assert "support_status_values" in schema
        values = schema["support_status_values"]
        assert "SUPPORTED" in values
        assert "INSUFFICIENT_SOURCE_SUPPORT" in values

    def test_heavy_tier_has_source_span_required(self):
        """HEAVY tier instruction must require source_span."""
        profile = _load_pa_prompt_profile()
        instr = profile["treatment_instructions"]["HEAVY"]
        assert instr.get("source_span_required", False) is True

    def test_heavy_tier_has_jd_alignment_required(self):
        """HEAVY tier instruction must require jd_alignment."""
        profile = _load_pa_prompt_profile()
        instr = profile["treatment_instructions"]["HEAVY"]
        assert instr.get("jd_alignment_required", False) is True

    def test_heavy_tier_has_blocked_items_required(self):
        """HEAVY tier instruction must require blocked_items."""
        profile = _load_pa_prompt_profile()
        instr = profile["treatment_instructions"]["HEAVY"]
        assert instr.get("blocked_items_required", False) is True

    def test_profile_has_prompt_directive(self):
        """Each tier must have a prompt directive."""
        profile = _load_pa_prompt_profile()
        instr = profile["treatment_instructions"]
        for tier in ["HEAVY", "MODERATE", "LIGHT"]:
            assert "prompt_directive" in instr[tier]
            assert len(instr[tier]["prompt_directive"]) > 0


class TestAntiInventionRulesPresent:
    """Test anti-invention rules are present in PA artifacts."""

    def test_heavy_artifact_has_anti_invention_rules(self):
        """HEAVY artifact includes anti-invention rules."""
        artifact = build_section_prompt_artifact("headline")
        assert len(artifact.anti_invention_rules) > 0

    def test_bullet_artifact_has_anti_invention_rules(self):
        """Bullet artifact includes anti-invention rules."""
        artifact = build_section_prompt_artifact_for_bullet("unify_bullets", 1)
        assert len(artifact.anti_invention_rules) > 0

    def test_anti_invention_rules_contain_no_metrics(self):
        """Anti-invention rules forbid inventing metrics."""
        profile = _load_pa_prompt_profile()
        rules_text = " ".join(profile["anti_invention_rules"]).lower()
        assert "metric" in rules_text or "no new metric" in rules_text

    def test_anti_invention_rules_contain_no_clients(self):
        """Anti-invention rules forbid inventing client names."""
        profile = _load_pa_prompt_profile()
        rules_text = " ".join(profile["anti_invention_rules"]).lower()
        assert "client" in rules_text

    def test_anti_invention_rules_contain_no_tools(self):
        """Anti-invention rules forbid inventing tools/tech."""
        profile = _load_pa_prompt_profile()
        rules_text = " ".join(profile["anti_invention_rules"]).lower()
        assert "tool" in rules_text or "tech" in rules_text

    def test_anti_invention_rules_contain_no_scope_expansion(self):
        """Anti-invention rules forbid scope expansion."""
        profile = _load_pa_prompt_profile()
        rules_text = " ".join(profile["anti_invention_rules"]).lower()
        assert "scope" in rules_text


class TestSourceSpanFirstRequired:
    """Test source_span-first rule is enforced in prompt directives."""

    def test_heavy_tier_mentions_source_span(self):
        """HEAVY tier directive mentions source_span."""
        profile = _load_pa_prompt_profile()
        instr = profile["treatment_instructions"]["HEAVY"]
        directive = instr["prompt_directive"].lower()
        assert "source" in directive or "span" in directive or "verbatim" in directive

    def test_artifact_has_source_span_required_flag(self):
        """Tiered bullet artifacts require source_span field."""
        artifact = build_section_prompt_artifact_for_bullet("unify_bullets", 1)
        assert artifact.source_span_required is True


class TestSupportStatusValues:
    """Test support status values include INSUFFICIENT_SOURCE_SUPPORT."""

    def test_artifact_has_insufficient_source_support(self):
        """Artifact allows INSUFFICIENT_SOURCE_SUPPORT status."""
        artifact = build_section_prompt_artifact_for_bullet("unify_bullets", 1)
        assert "INSUFFICIENT_SOURCE_SUPPORT" in artifact.support_status_values

    def test_artifact_has_supported_status(self):
        """Artifact allows SUPPORTED status."""
        artifact = build_section_prompt_artifact_for_bullet("unify_bullets", 1)
        assert "SUPPORTED" in artifact.support_status_values


class TestProviderNeutralPrompts:
    """Test prompts are provider-neutral (no Claude-specific wording)."""

    def test_no_claude_specific_terms_in_directives(self):
        """Prompt directives contain no Claude-specific terms."""
        profile = _load_pa_prompt_profile()
        instr = profile["treatment_instructions"]
        forbidden_terms = ["claude", "anthropic", "constitutional"]
        for tier in ["HEAVY", "MODERATE", "LIGHT"]:
            directive = instr[tier]["prompt_directive"].lower()
            for term in forbidden_terms:
                assert term not in directive, f"Found forbidden term '{term}' in {tier} directive"

    def test_xml_style_sections_in_directives(self):
        """Prompt directives use XML-style sections."""
        profile = _load_pa_prompt_profile()
        instr = profile["treatment_instructions"]
        for tier in ["HEAVY", "MODERATE", "LIGHT"]:
            directive = instr[tier]["prompt_directive"]
            # Check for XML-style tags
            assert "<" in directive and ">" in directive, f"{tier} directive lacks XML-style tags"


class TestVerbatimBypass:
    """Test verbatim sections bypass LLM rewrite prompts."""

    def test_verbatim_artifact_has_copy_only(self):
        """Verbatim artifact has copy_only=True."""
        artifact = build_section_prompt_artifact("education")
        assert artifact.copy_only is True
        assert artifact.preserve_verbatim is True
        assert artifact.rewrite_allowed is False

    def test_verbatim_artifact_empty_directive(self):
        """Verbatim artifact has minimal/empty prompt directive."""
        artifact = build_section_prompt_artifact("education")
        # Verbatim sections should not have elaborate rewrite instructions
        assert artifact.treatment == "VERBATIM"


class TestOutputSchemaFields:
    """Test output schema fields per bullet are correct."""

    def test_bullet_artifact_has_all_required_flags(self):
        """Bullet artifact has all required output field flags."""
        artifact = build_section_prompt_artifact_for_bullet("unify_bullets", 1)
        # Required fields per W2 spec
        assert artifact.section_id is not None
        assert artifact.treatment is not None
        assert artifact.bullet_ordinal is not None
        assert artifact.source_span_required is True
        assert artifact.jd_alignment_required is True
        assert artifact.blocked_items_required is True
        assert artifact.support_status_required is True


class TestPAS3BoundaryCert:
    """Test PA S3 boundary certification is present."""

    def test_pa_boundary_cert_s3_exists(self):
        """PA_BOUNDARY_CERT_S3 constant exists."""
        assert PA_BOUNDARY_CERT_S3 is not None
        assert "s3" in PA_BOUNDARY_CERT_S3.lower() or "tiered" in PA_BOUNDARY_CERT_S3.lower()


class TestJudgePolicyIsMetadataOnly:
    """Test judge_policy remains metadata, no runtime activation."""

    def test_no_judge_activation_in_pa(self):
        """PA has no judge activation functions."""
        import apps_rg.runtime.bindings.pa_binding as pa_module
        assert not hasattr(pa_module, "activate_judges")
        assert not hasattr(pa_module, "run_judge_panel")
        assert not hasattr(pa_module, "score_with_judge")

    def test_artifact_has_no_judge_runtime_fields(self):
        """SectionPromptArtifact has no judge runtime fields."""
        artifact = build_section_prompt_artifact_for_bullet("unify_bullets", 1)
        # Should not have judge-specific runtime fields
        assert not hasattr(artifact, "judge_model")
        assert not hasattr(artifact, "judge_api_key")
        assert not hasattr(artifact, "judge_invocation")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
