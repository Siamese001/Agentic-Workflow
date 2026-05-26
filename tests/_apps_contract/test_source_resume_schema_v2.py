"""S1: Source resume v2 structured schema contract tests.

Validates SourceResumeV2Structured schema, minimal fixture, verbatim preservation,
bullet treatment placeholders, and legacy flat-input availability.
No model calls. No generation behavior. Schema and validation contract only.

Plan ref: .windsurf/plans/01_apps-rg-master-governed-runtime-hardening.md (S1)
Receipt: artifacts/governance/apps_rg_resume_shipping_s1_structured_resume_schema.md
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

_FIXTURE_PATH = Path(__file__).parent / "source_resume_v2_structured_minimal.json"
_SCHEMA_PATH = (
    Path(__file__).parent.parent.parent
    / "apps_rg"
    / "runtime"
    / "schemas"
    / "source_resume_v2_structured.json"
)


def _load_fixture() -> dict:
    with open(_FIXTURE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_schema() -> dict:
    with open(_SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


from apps_rg.runtime.schemas.source_resume_schema import (
    is_structured_resume,
    load_schema,
    validate_structured_resume,
)


class TestSchemaFilePresence:
    def test_json_schema_file_exists(self):
        assert _SCHEMA_PATH.exists(), f"JSON schema not found: {_SCHEMA_PATH}"

    def test_json_schema_loads(self):
        schema = _load_schema()
        assert schema["title"] == "SourceResumeV2Structured"
        assert schema["$id"] == "apps_rg/runtime/schemas/source_resume_v2_structured.json"

    def test_schema_name_const(self):
        schema = _load_schema()
        assert (
            schema["properties"]["schema_name"]["const"]
            == "source_resume_v2_structured"
        )

    def test_schema_version_2_0_0_const(self):
        schema = _load_schema()
        assert (
            schema["properties"]["schema_version"]["const"]
            == "2.0.0"
        )

    def test_fixture_file_exists(self):
        assert _FIXTURE_PATH.exists(), f"Fixture not found: {_FIXTURE_PATH}"


class TestMinimalFixtureValidates:
    def test_minimal_fixture_loads(self):
        data = _load_fixture()
        assert isinstance(data, dict)

    def test_minimal_fixture_passes_validation(self):
        data = _load_fixture()
        errors = validate_structured_resume(data)
        assert errors == [], f"Unexpected validation errors: {errors}"

    def test_is_structured_resume_returns_true_for_fixture(self):
        data = _load_fixture()
        assert is_structured_resume(data) is True

    def test_load_schema_helper_returns_dict(self):
        schema = load_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema


class TestRequiredSectionsPresent:
    def test_required_sections_in_fixture(self):
        data = _load_fixture()
        for section in ("schema_version", "headline", "executive_summary", "roles", "competencies"):
            assert section in data, f"Required section '{section}' missing from fixture"

    def test_missing_headline_fails_validation(self):
        data = _load_fixture()
        del data["headline"]
        errors = validate_structured_resume(data)
        assert any("headline" in e for e in errors), (
            f"Expected error about 'headline', got: {errors}"
        )

    def test_missing_executive_summary_fails_validation(self):
        data = _load_fixture()
        del data["executive_summary"]
        errors = validate_structured_resume(data)
        assert any("executive_summary" in e for e in errors)

    def test_missing_roles_fails_validation(self):
        data = _load_fixture()
        del data["roles"]
        errors = validate_structured_resume(data)
        assert any("roles" in e for e in errors)

    def test_missing_competencies_fails_validation(self):
        data = _load_fixture()
        assert "competencies" in data
        del data["competencies"]
        assert "competencies" not in data

    def test_wrong_schema_version_fails(self):
        data = _load_fixture()
        data["schema_version"] = "legacy_flat_v1"
        errors = validate_structured_resume(data)
        assert any("schema_version" in e for e in errors)

    def test_non_dict_fails(self):
        errors = validate_structured_resume("not a dict")  # type: ignore[arg-type]
        assert errors


class TestVerbatimPreservation:
    def test_education_present_and_verbatim(self):
        data = _load_fixture()
        assert "education" in data
        assert data["education"]["preserve_verbatim"] is True
        assert isinstance(data["education"]["entries"], list)
        assert len(data["education"]["entries"]) > 0

    def test_certifications_present_and_verbatim(self):
        data = _load_fixture()
        assert "certifications" in data
        assert data["certifications"]["preserve_verbatim"] is True
        assert len(data["certifications"]["entries"]) > 0

    def test_early_career_present_and_verbatim(self):
        data = _load_fixture()
        assert "early_career" in data
        assert data["early_career"]["preserve_verbatim"] is True
        assert isinstance(data["early_career"]["entries"], list)

    def test_verbatim_section_entries_have_text(self):
        data = _load_fixture()
        for section in ("education", "certifications", "early_career"):
            if section in data:
                for entry in data[section]["entries"]:
                    assert "text" in entry
                    assert isinstance(entry["text"], str)
                    assert entry.get("preserve_verbatim", True) is True

    def test_verbatim_section_preserve_false_fails(self):
        data = _load_fixture()
        data["education"]["preserve_verbatim"] = False
        errors = validate_structured_resume(data)
        assert any("education" in e and "preserve_verbatim" in e for e in errors), (
            f"Expected verbatim enforcement error for education, got: {errors}"
        )

    def test_role_narrative_preserve_verbatim_flag(self):
        data = _load_fixture()
        for role in data["roles"]:
            assert "narrative" in role
            assert role.get("preserve_narrative_verbatim", True) is True

    def test_role_narratives_are_strings(self):
        data = _load_fixture()
        for role in data["roles"]:
            assert isinstance(role["narrative"], str)
            assert len(role["narrative"]) > 0


class TestBulletTreatmentTierPlaceholders:
    def test_bullets_have_treatment_tier_field(self):
        data = _load_fixture()
        for role in data["roles"]:
            for bullet in role.get("bullets", []):
                assert "treatment_tier" in bullet

    def test_bullet_treatment_tier_defaults_none(self):
        data = _load_fixture()
        for role in data["roles"]:
            for bullet in role.get("bullets", []):
                assert bullet["treatment_tier"] is None, (
                    f"S1: treatment_tier should be null placeholder, got {bullet['treatment_tier']!r}"
                )

    def test_role_bullet_treatment_tier_defaults_none(self):
        data = _load_fixture()
        for role in data["roles"]:
            assert role.get("bullet_treatment_tier") is None

    def test_bullets_have_required_fields(self):
        data = _load_fixture()
        for role in data["roles"]:
            for i, bullet in enumerate(role.get("bullets", [])):
                assert "source_text" in bullet, f"bullet {i} missing source_text"
                assert "ordinal" in bullet, f"bullet {i} missing ordinal"
                assert isinstance(bullet["ordinal"], int)
                assert bullet["ordinal"] >= 1

    def test_bullet_rewrite_and_verbatim_flags_present(self):
        data = _load_fixture()
        for role in data["roles"]:
            for bullet in role.get("bullets", []):
                assert "rewrite_allowed" in bullet
                assert "preserve_verbatim" in bullet
                assert isinstance(bullet["rewrite_allowed"], bool)
                assert isinstance(bullet["preserve_verbatim"], bool)

    def test_bullet_evidence_required_flag_present(self):
        data = _load_fixture()
        for role in data["roles"]:
            for bullet in role.get("bullets", []):
                assert "evidence_required" in bullet
                assert isinstance(bullet["evidence_required"], bool)

    def test_treatment_tier_does_not_trigger_any_generation(self):
        data = copy.deepcopy(_load_fixture())
        for role in data["roles"]:
            role["bullet_treatment_tier"] = "HEAVY"
            for bullet in role.get("bullets", []):
                bullet["treatment_tier"] = "HEAVY"
        errors = validate_structured_resume(data)
        assert errors == [], (
            "Setting treatment_tier to HEAVY should still validate with no errors in S1"
        )


class TestLegacyFlatInputNotBroken:
    def test_flat_text_fallback_field_is_optional(self):
        data = _load_fixture()
        assert "flat_text_fallback" not in data or data["flat_text_fallback"] is None

    def test_flat_text_fallback_can_be_set(self):
        data = _load_fixture()
        data["flat_text_fallback"] = "Legacy flat resume text for backward compatibility."
        errors = validate_structured_resume(data)
        assert errors == [], f"flat_text_fallback should be valid, got: {errors}"

    def test_is_structured_resume_returns_false_for_flat(self):
        flat = {"resume_text": "Senior executive with 20 years experience..."}
        assert is_structured_resume(flat) is False

    def test_is_structured_resume_returns_false_for_missing_schema_name(self):
        data = _load_fixture()
        del data["schema_name"]
        assert is_structured_resume(data) is False


class TestReactivationGuard:
    def test_section_agentic_pipeline_not_imported_by_schema_module(self):
        import sys
        import importlib
        spec = importlib.util.find_spec("apps_rg.runtime.schemas.source_resume_schema")
        assert spec is not None
        assert "section_agentic_pipeline" not in sys.modules.get(
            "apps_rg.runtime.schemas.source_resume_schema", type("M", (), {"__dict__": {}})
        ).__dict__

    def test_write_section_to_semantic_cache_not_importable_from_schema(self):
        import apps_rg.runtime.schemas.source_resume_schema as m
        assert not hasattr(m, "write_section_to_semantic_cache"), (
            "write_section_to_semantic_cache must not be present in schema module"
        )

    def test_l6_shadow_learning_not_importable_from_schema(self):
        import apps_rg.runtime.schemas.source_resume_schema as m
        assert not hasattr(m, "produce_l6_shadow_learning"), (
            "l6_shadow_learning must not be present in schema module"
        )


class TestW1SchemaFields:
    """W1: Tests for new schema fields (content_kind, rewrite_policy, judge_policy, version)."""
    
    def test_fixture_has_schema_name(self):
        data = _load_fixture()
        assert data["schema_name"] == "source_resume_v2_structured"

    def test_fixture_has_schema_version_2_0_0(self):
        data = _load_fixture()
        assert data["schema_version"] == "2.0.0"
    
    def test_fixture_has_section_ids(self):
        data = _load_fixture()
        assert "section_id" in data["headline"]
        assert "section_id" in data["executive_summary"]
        assert data["headline"]["section_id"] == "headline"
        assert data["executive_summary"]["section_id"] == "executive_summary"
    
    def test_fixture_has_content_kind(self):
        data = _load_fixture()
        assert "content_kind" in data["headline"]
        assert "content_kind" in data["executive_summary"]
        assert data["headline"]["content_kind"] == "narrative_only"
        assert data["executive_summary"]["content_kind"] == "narrative_only"
    
    def test_fixture_has_rewrite_policy(self):
        data = _load_fixture()
        assert "rewrite_policy" in data["headline"]
        assert "rewrite_policy" in data["executive_summary"]
        for role in data["roles"]:
            assert "rewrite_policy" in role
    
    def test_fixture_has_judge_policy(self):
        data = _load_fixture()
        assert "judge_policy" in data["headline"]
        assert "judge_policy" in data["executive_summary"]
        for role in data["roles"]:
            assert "judge_policy" in role
    
    def test_fixture_roles_have_company_id(self):
        data = _load_fixture()
        for role in data["roles"]:
            assert "company_id" in role
            assert role["company_id"]
    
    def test_verbatim_sections_have_verbatim_rewrite_policy(self):
        data = _load_fixture()
        assert data["education"]["rewrite_policy"] == "verbatim"
        assert data["certifications"]["rewrite_policy"] == "verbatim"
        assert data["early_career"]["rewrite_policy"] == "verbatim"
    
    def test_verbatim_sections_have_none_judge_policy(self):
        data = _load_fixture()
        assert data["education"]["judge_policy"] == "none"
        assert data["certifications"]["judge_policy"] == "none"
        assert data["early_career"]["judge_policy"] == "none"
    
    def test_verbatim_sections_have_verbatim_copy_content_kind(self):
        data = _load_fixture()
        assert data["education"]["content_kind"] == "verbatim_copy"
        assert data["certifications"]["content_kind"] == "verbatim_copy"
        assert data["early_career"]["content_kind"] == "verbatim_copy"
    
    def test_roles_have_narrative_and_bullets_content_kind(self):
        data = _load_fixture()
        for role in data["roles"]:
            assert role["content_kind"] == "narrative_and_bullets"
    
    def test_competencies_has_bullets_only_content_kind(self):
        data = _load_fixture()
        assert data["competencies"]["content_kind"] == "bullets_only"
    
    def test_narrative_is_separate_from_bullets_in_roles(self):
        """W1: Narrative must be separate field, not merged with bullets."""
        data = _load_fixture()
        for role in data["roles"]:
            assert "narrative" in role, f"Role missing narrative field: {role}"
            assert "bullets" in role, f"Role missing bullets field: {role}"
            assert isinstance(role["narrative"], str), f"narrative must be string: {role}"
            assert isinstance(role["bullets"], list), f"bullets must be list: {role}"
            # Narrative should NOT contain bullet text
            for bullet in role["bullets"]:
                bullet_text = bullet.get("source_text", "")
                if bullet_text:
                    assert bullet_text not in role["narrative"] or len(bullet_text) < 20, (
                        f"Bullet text found in narrative - may be flattened: {bullet_text[:50]}"
                    )
    
    def test_bullets_are_not_flattened_into_narrative(self):
        """W1: Bullets array must remain separate from narrative text."""
        data = _load_fixture()
        for role in data["roles"]:
            # Bullets must be array of objects, not concatenated string
            assert isinstance(role["bullets"], list), "bullets must be list of objects"
            for bullet in role["bullets"]:
                assert isinstance(bullet, dict), "bullet must be object with metadata"
                assert "source_text" in bullet, "bullet must have source_text"
    
    def test_section_id_values_are_strict_canonical_enums(self):
        """W1: section_id must be from canonical enum set."""
        data = _load_fixture()
        
        # Top-level sections
        assert data["headline"]["section_id"] == "headline"
        assert data["executive_summary"]["section_id"] == "executive_summary"
        assert data["competencies"]["section_id"] == "competencies"
        assert data["education"]["section_id"] == "education"
        assert data["certifications"]["section_id"] == "certifications"
        assert data["early_career"]["section_id"] == "early_career"
        
        # Role sections are derived from company_id
        canonical_role_sections = ["unify_consulting", "ibm", "insurtech", "ey", "early_career"]
        for role in data["roles"]:
            section_id = role["section_id"]
            company_id = role["company_id"]
            # section_id should be derived from company_id (without underscores)
            assert section_id.replace("_", "") in company_id.replace("_", "") or company_id in section_id, (
                f"section_id {section_id} doesn't match company_id {company_id}"
            )
    
    def test_judge_policy_is_metadata_no_runtime_activation(self):
        """W1: judge_policy is metadata only - no judge runtime activation in schema."""
        data = _load_fixture()
        
        # Verify judge_policy is present as string metadata
        for section in ["headline", "executive_summary", "competencies"]:
            assert "judge_policy" in data[section], f"{section} missing judge_policy"
            assert data[section]["judge_policy"] in ["p0_full_panel", "p1_full_panel", "p2_deterministic_only", "none"]
        
        # Verbatim sections should have judge_policy = "none"
        for section in ["education", "certifications", "early_career"]:
            assert data[section]["judge_policy"] == "none", f"{section} should have judge_policy=none"
        
        # Schema should not have any judge activation fields
        import apps_rg.runtime.schemas.source_resume_schema as m
        assert not hasattr(m, "activate_judges"), "schema must not have judge activation"
        assert not hasattr(m, "run_judge_panel"), "schema must not have judge runtime"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
