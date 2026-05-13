"""S4 contract tests: apps_rg U0 Structured Resume Support.

Validates that the U0 ingress path correctly classifies, validates, and attaches
metadata for structured source resume payloads -- without rewriting content,
calling PA, C0, L2, providers, or mutating cache/L4.

No model calls. No generation. No agentic_core changes tested here.
No resume rewriting. No full resume-generation smoke.

Receipt: artifacts/governance/apps_rg_resume_shipping_s4_u0_structured_resume_support.md
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Fixtures -- canonical minimal structured resume
# ---------------------------------------------------------------------------

_FIXTURE_PATH = Path(__file__).parent / "source_resume_v2_structured_minimal.json"

VALID_STRUCTURED_RESUME: dict[str, Any] = {
    "schema_name": "source_resume_v2_structured",
    "schema_version": "2.0.0",
    "headline": {
        "section_id": "headline",
        "content_kind": "narrative_only",
        "rewrite_policy": "heavy",
        "judge_policy": "none",
        "text": "SVP Engineering"
    },
    "executive_summary": {
        "section_id": "executive_summary",
        "content_kind": "narrative_only",
        "rewrite_policy": "heavy",
        "judge_policy": "none",
        "text": "Experienced technology executive."
    },
    "roles": [
        {
            "section_id": "unify",
            "content_kind": "narrative_and_bullets",
            "rewrite_policy": "heavy",
            "judge_policy": "none",
            "employer": "Acme Corp",
            "company_id": "acme_corp",
            "title": "VP Engineering",
            "narrative": "Led platform modernization.",
            "bullets": [
                {"source_text": "Led 200-engineer org.", "ordinal": 1},
                {"source_text": "Delivered $40M program.", "ordinal": 2},
            ],
        },
        {
            "section_id": "ibm",
            "content_kind": "narrative_and_bullets",
            "rewrite_policy": "moderate",
            "judge_policy": "none",
            "employer": "Beta Inc",
            "company_id": "beta_inc",
            "title": "Director Engineering",
            "narrative": "Built cloud platform.",
            "bullets": [
                {"source_text": "Migrated 80 services to Kubernetes.", "ordinal": 1},
            ],
        },
    ],
    "competencies": {
        "section_id": "competencies",
        "content_kind": "bullets_only",
        "rewrite_policy": "moderate",
        "judge_policy": "none",
        "items": ["Cloud Architecture", "Agile Delivery", "Platform Engineering"]
    },
    "education": {
        "section_id": "education",
        "content_kind": "verbatim_copy",
        "rewrite_policy": "verbatim",
        "judge_policy": "none",
        "preserve_verbatim": True,
        "entries": [{"text": "BS Computer Science, MIT, 2001"}],
    },
    "certifications": {
        "section_id": "certifications",
        "content_kind": "verbatim_copy",
        "rewrite_policy": "verbatim",
        "judge_policy": "none",
        "preserve_verbatim": True,
        "entries": [{"text": "AWS Solutions Architect, 2022"}],
    },
    "early_career": {
        "section_id": "early_career",
        "content_kind": "verbatim_copy",
        "rewrite_policy": "verbatim",
        "judge_policy": "none",
        "preserve_verbatim": True,
        "entries": [{"text": "Software Engineer, Startup Inc, 1999-2001"}],
    },
}

INVALID_STRUCTURED_RESUME: dict[str, Any] = {
    "schema_name": "source_resume_v2_structured",
    "schema_version": "2.0.0",
    # Missing required: headline, executive_summary, roles, competencies
}

WRONG_VERSION_RESUME: dict[str, Any] = {
    "schema_name": "old_version_v1",
    "schema_version": "1.0.0",
    "headline": "SVP Engineering",
}

FLAT_RESUME_TEXT = "Experienced SVP Engineering with 20 years leading platform teams."


def _make_resume_payload(
    *,
    structured=None,
    flat_text: str = "",
    flat_fallback: str = "",
    resume_ref: str = "",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "resume_hash": hashlib.sha256((flat_text or "").encode()).hexdigest(),
        "source_resume_text": flat_text,
        "source_resume_ref": resume_ref,
    }
    if structured is not None:
        payload["structured_resume"] = structured
    if flat_fallback:
        payload["flat_text_fallback"] = flat_fallback
    return payload


# ---------------------------------------------------------------------------
# Import smoke
# ---------------------------------------------------------------------------

class TestImportSmoke:
    def test_classifier_importable(self):
        from apps_rg.runtime.u0 import structured_resume_classifier
        assert hasattr(structured_resume_classifier, "classify_resume_payload")
        assert hasattr(structured_resume_classifier, "attach_structured_resume_metadata")
        assert hasattr(structured_resume_classifier, "ResumeInputMode")
        assert hasattr(structured_resume_classifier, "StructuredResumeClassification")
        assert hasattr(structured_resume_classifier, "U0_STRUCTURED_RESUME_CERT_S4")

    def test_cert_ref_present(self):
        from apps_rg.runtime.u0.structured_resume_classifier import U0_STRUCTURED_RESUME_CERT_S4
        assert U0_STRUCTURED_RESUME_CERT_S4 == "u0-apps-rg-structured-resume-support-s4"

    def test_resume_input_mode_values(self):
        from apps_rg.runtime.u0.structured_resume_classifier import ResumeInputMode
        assert ResumeInputMode.STRUCTURED_SOURCE_RESUME_V2.value == "STRUCTURED_SOURCE_RESUME_V2"
        assert ResumeInputMode.LEGACY_FLAT_RESUME.value == "LEGACY_FLAT_RESUME"
        assert ResumeInputMode.MISSING_OR_INVALID_RESUME.value == "MISSING_OR_INVALID_RESUME"


# ---------------------------------------------------------------------------
# STRUCTURED_SOURCE_RESUME_V2 detection
# ---------------------------------------------------------------------------

class TestStructuredDetection:
    def test_valid_structured_is_detected(self):
        from apps_rg.runtime.u0.structured_resume_classifier import (
            classify_resume_payload, ResumeInputMode,
        )
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == ResumeInputMode.STRUCTURED_SOURCE_RESUME_V2.value

    def test_valid_structured_produces_schema_version(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert result.source_resume_schema_version == "source_resume_v2_structured"

    def test_valid_structured_produces_digest(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert len(result.source_resume_digest) == 64
        assert all(c in "0123456789abcdef" for c in result.source_resume_digest)

    def test_digest_is_deterministic(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload_a = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        payload_b = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        r_a = classify_resume_payload(payload_a)
        r_b = classify_resume_payload(payload_b)
        assert r_a.source_resume_digest == r_b.source_resume_digest

    def test_valid_structured_produces_mode_field(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == "STRUCTURED_SOURCE_RESUME_V2"

    def test_valid_structured_produces_available_sections(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert "roles" in result.available_sections
        assert "headline" in result.available_sections
        assert "executive_summary" in result.available_sections
        assert "competencies" in result.available_sections

    def test_valid_structured_produces_role_count(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert result.role_count == 2

    def test_validation_status_is_valid(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert result.structured_resume_validation_status == "VALID"

    def test_valid_structured_has_no_validation_errors(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert result.structured_resume_validation_errors == []


# ---------------------------------------------------------------------------
# Presence flags
# ---------------------------------------------------------------------------

class TestPresenceFlags:
    def test_has_education_true(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert result.has_education is True

    def test_has_certifications_true(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert result.has_certifications is True

    def test_has_early_career_true(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert result.has_early_career is True

    def test_no_optional_sections_returns_false_flags(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        minimal = {k: v for k, v in VALID_STRUCTURED_RESUME.items()
                   if k not in ("education", "certifications", "early_career")}
        payload = _make_resume_payload(structured=minimal)
        result = classify_resume_payload(payload)
        assert result.has_education is False
        assert result.has_certifications is False
        assert result.has_early_career is False


# ---------------------------------------------------------------------------
# Invalid structured resume -- fail closed
# ---------------------------------------------------------------------------

class TestInvalidStructuredResume:
    def test_invalid_structured_produces_missing_or_invalid_mode(self):
        from apps_rg.runtime.u0.structured_resume_classifier import (
            classify_resume_payload, ResumeInputMode,
        )
        payload = _make_resume_payload(structured=INVALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == ResumeInputMode.MISSING_OR_INVALID_RESUME.value

    def test_invalid_structured_produces_validation_status_invalid(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=INVALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert result.structured_resume_validation_status == "INVALID"

    def test_invalid_structured_produces_validation_errors(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=INVALID_STRUCTURED_RESUME)
        result = classify_resume_payload(payload)
        assert len(result.structured_resume_validation_errors) > 0

    def test_invalid_structured_does_not_silently_fall_back_to_flat(self):
        from apps_rg.runtime.u0.structured_resume_classifier import (
            classify_resume_payload, ResumeInputMode,
        )
        payload = _make_resume_payload(
            structured=INVALID_STRUCTURED_RESUME,
            flat_text=FLAT_RESUME_TEXT,
        )
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == ResumeInputMode.MISSING_OR_INVALID_RESUME.value

    def test_wrong_schema_version_produces_missing_or_invalid(self):
        from apps_rg.runtime.u0.structured_resume_classifier import (
            classify_resume_payload, ResumeInputMode,
        )
        payload = _make_resume_payload(structured=WRONG_VERSION_RESUME)
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == ResumeInputMode.MISSING_OR_INVALID_RESUME.value

    def test_non_dict_structured_resume_produces_missing_or_invalid(self):
        from apps_rg.runtime.u0.structured_resume_classifier import (
            classify_resume_payload, ResumeInputMode,
        )
        payload: dict[str, Any] = {
            "resume_hash": "abc",
            "source_resume_text": "",
            "structured_resume": "this is not a dict",
        }
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == ResumeInputMode.MISSING_OR_INVALID_RESUME.value
        assert result.structured_resume_validation_status == "INVALID"


# ---------------------------------------------------------------------------
# Flat text fallback co-existence
# ---------------------------------------------------------------------------

class TestFlatTextFallback:
    def test_invalid_structured_with_explicit_flat_fallback_preserves_both(self):
        from apps_rg.runtime.u0.structured_resume_classifier import (
            classify_resume_payload, ResumeInputMode,
        )
        payload = _make_resume_payload(
            structured=INVALID_STRUCTURED_RESUME,
            flat_fallback=FLAT_RESUME_TEXT,
        )
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == ResumeInputMode.MISSING_OR_INVALID_RESUME.value
        assert result.flat_text_fallback_present is True

    def test_valid_structured_with_flat_fallback_does_not_override_mode(self):
        from apps_rg.runtime.u0.structured_resume_classifier import (
            classify_resume_payload, ResumeInputMode,
        )
        payload = _make_resume_payload(
            structured=VALID_STRUCTURED_RESUME,
            flat_fallback=FLAT_RESUME_TEXT,
        )
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == ResumeInputMode.STRUCTURED_SOURCE_RESUME_V2.value
        assert result.flat_text_fallback_present is True


# ---------------------------------------------------------------------------
# Legacy flat resume
# ---------------------------------------------------------------------------

class TestLegacyFlatResume:
    def test_flat_text_only_produces_legacy_flat_mode(self):
        from apps_rg.runtime.u0.structured_resume_classifier import (
            classify_resume_payload, ResumeInputMode,
        )
        payload = _make_resume_payload(flat_text=FLAT_RESUME_TEXT)
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == ResumeInputMode.LEGACY_FLAT_RESUME.value

    def test_legacy_flat_produces_digest(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(flat_text=FLAT_RESUME_TEXT)
        result = classify_resume_payload(payload)
        assert len(result.source_resume_digest) == 64

    def test_legacy_flat_digest_matches_sha256(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(flat_text=FLAT_RESUME_TEXT)
        result = classify_resume_payload(payload)
        expected = hashlib.sha256(FLAT_RESUME_TEXT.encode("utf-8")).hexdigest()
        assert result.source_resume_digest == expected

    def test_legacy_flat_has_no_structured_metadata(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(flat_text=FLAT_RESUME_TEXT)
        result = classify_resume_payload(payload)
        assert result.available_sections == []
        assert result.role_count == 0
        assert result.has_education is False
        assert result.has_certifications is False
        assert result.has_early_career is False

    def test_legacy_flat_validation_status_is_not_applicable(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(flat_text=FLAT_RESUME_TEXT)
        result = classify_resume_payload(payload)
        assert result.structured_resume_validation_status == "NOT_APPLICABLE"

    def test_legacy_flat_has_no_schema_version(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(flat_text=FLAT_RESUME_TEXT)
        result = classify_resume_payload(payload)
        assert result.source_resume_schema_version == ""


# ---------------------------------------------------------------------------
# Missing resume
# ---------------------------------------------------------------------------

class TestMissingResume:
    def test_empty_payload_produces_missing_or_invalid(self):
        from apps_rg.runtime.u0.structured_resume_classifier import (
            classify_resume_payload, ResumeInputMode,
        )
        payload: dict[str, Any] = {
            "resume_hash": "",
            "source_resume_text": "",
            "source_resume_ref": "",
        }
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == ResumeInputMode.MISSING_OR_INVALID_RESUME.value

    def test_whitespace_only_flat_text_produces_missing_or_invalid(self):
        from apps_rg.runtime.u0.structured_resume_classifier import (
            classify_resume_payload, ResumeInputMode,
        )
        payload = _make_resume_payload(flat_text="   ")
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == ResumeInputMode.MISSING_OR_INVALID_RESUME.value


# ---------------------------------------------------------------------------
# attach_structured_resume_metadata
# ---------------------------------------------------------------------------

class TestAttachMetadata:
    def _make_contract(self, *, structured=None, flat_text: str = "") -> dict[str, Any]:
        resume_payload = _make_resume_payload(structured=structured, flat_text=flat_text)
        return {
            "resume_payload": resume_payload,
            "jd_payload": {"jd_hash": "abc", "jd_text": "some job description"},
            "target": {"company": "Acme", "role": "CTO", "level": "EXECUTIVE"},
        }

    def test_attach_returns_same_dict(self):
        from apps_rg.runtime.u0.structured_resume_classifier import attach_structured_resume_metadata
        contract = self._make_contract(structured=VALID_STRUCTURED_RESUME)
        result = attach_structured_resume_metadata(contract)
        assert result is contract

    def test_attach_populates_s4_metadata_key(self):
        from apps_rg.runtime.u0.structured_resume_classifier import attach_structured_resume_metadata
        contract = self._make_contract(structured=VALID_STRUCTURED_RESUME)
        attach_structured_resume_metadata(contract)
        assert "s4_metadata" in contract["resume_payload"]

    def test_attach_s4_metadata_contains_all_required_fields(self):
        from apps_rg.runtime.u0.structured_resume_classifier import attach_structured_resume_metadata
        contract = self._make_contract(structured=VALID_STRUCTURED_RESUME)
        attach_structured_resume_metadata(contract)
        meta = contract["resume_payload"]["s4_metadata"]
        for key in (
            "source_resume_schema_version",
            "source_resume_digest",
            "source_resume_mode",
            "available_sections",
            "role_count",
            "has_education",
            "has_certifications",
            "has_early_career",
            "structured_resume_validation_status",
            "flat_text_fallback_present",
        ):
            assert key in meta, f"Missing key: {key}"

    def test_attach_s4_metadata_mode_is_structured_for_valid_input(self):
        from apps_rg.runtime.u0.structured_resume_classifier import attach_structured_resume_metadata
        contract = self._make_contract(structured=VALID_STRUCTURED_RESUME)
        attach_structured_resume_metadata(contract)
        meta = contract["resume_payload"]["s4_metadata"]
        assert meta["source_resume_mode"] == "STRUCTURED_SOURCE_RESUME_V2"

    def test_attach_s4_metadata_mode_is_legacy_for_flat_text(self):
        from apps_rg.runtime.u0.structured_resume_classifier import attach_structured_resume_metadata
        contract = self._make_contract(flat_text=FLAT_RESUME_TEXT)
        attach_structured_resume_metadata(contract)
        meta = contract["resume_payload"]["s4_metadata"]
        assert meta["source_resume_mode"] == "LEGACY_FLAT_RESUME"

    def test_attach_s4_metadata_invalid_structured_has_errors_key(self):
        from apps_rg.runtime.u0.structured_resume_classifier import attach_structured_resume_metadata
        contract = self._make_contract(structured=INVALID_STRUCTURED_RESUME)
        attach_structured_resume_metadata(contract)
        meta = contract["resume_payload"]["s4_metadata"]
        assert meta["source_resume_mode"] == "MISSING_OR_INVALID_RESUME"
        assert "structured_resume_validation_errors" in meta
        assert len(meta["structured_resume_validation_errors"]) > 0

    def test_attach_does_not_alter_flat_text(self):
        from apps_rg.runtime.u0.structured_resume_classifier import attach_structured_resume_metadata
        contract = self._make_contract(flat_text=FLAT_RESUME_TEXT)
        before = contract["resume_payload"]["source_resume_text"]
        attach_structured_resume_metadata(contract)
        after = contract["resume_payload"]["source_resume_text"]
        assert before == after

    def test_attach_does_not_alter_structured_resume_content(self):
        from apps_rg.runtime.u0.structured_resume_classifier import attach_structured_resume_metadata
        contract = self._make_contract(structured=VALID_STRUCTURED_RESUME)
        before_headline = contract["resume_payload"]["structured_resume"]["headline"]
        attach_structured_resume_metadata(contract)
        after_headline = contract["resume_payload"]["structured_resume"]["headline"]
        assert before_headline == after_headline

    def test_attach_does_not_rewrite_structured_resume(self):
        from apps_rg.runtime.u0.structured_resume_classifier import attach_structured_resume_metadata
        contract = self._make_contract(structured=VALID_STRUCTURED_RESUME)
        original_bullets = [
            b["source_text"]
            for role in contract["resume_payload"]["structured_resume"]["roles"]
            for b in role["bullets"]
        ]
        attach_structured_resume_metadata(contract)
        after_bullets = [
            b["source_text"]
            for role in contract["resume_payload"]["structured_resume"]["roles"]
            for b in role["bullets"]
        ]
        assert original_bullets == after_bullets


# ---------------------------------------------------------------------------
# Fixture-based tests (uses the shared test fixture from S1)
# ---------------------------------------------------------------------------

class TestFixtureBased:
    def test_s1_fixture_classified_as_structured(self):
        from apps_rg.runtime.u0.structured_resume_classifier import (
            classify_resume_payload, ResumeInputMode,
        )
        if not _FIXTURE_PATH.exists():
            pytest.skip("S1 fixture not found")
        data = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        payload = _make_resume_payload(structured=data)
        result = classify_resume_payload(payload)
        assert result.source_resume_mode == ResumeInputMode.STRUCTURED_SOURCE_RESUME_V2.value

    def test_s1_fixture_has_required_metadata(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        if not _FIXTURE_PATH.exists():
            pytest.skip("S1 fixture not found")
        data = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        payload = _make_resume_payload(structured=data)
        result = classify_resume_payload(payload)
        assert result.source_resume_schema_version == "source_resume_v2_structured"
        assert len(result.source_resume_digest) == 64
        assert result.structured_resume_validation_status == "VALID"
        assert result.structured_resume_validation_errors == []

    def test_s1_fixture_role_count_positive(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        if not _FIXTURE_PATH.exists():
            pytest.skip("S1 fixture not found")
        data = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        payload = _make_resume_payload(structured=data)
        result = classify_resume_payload(payload)
        assert result.role_count >= 1


# ---------------------------------------------------------------------------
# U0 Boundary Guards -- no forbidden imports in classifier module
# ---------------------------------------------------------------------------

class TestU0BoundaryGuards:
    def _read_classifier_source(self) -> str:
        path = (
            Path(__file__).parents[2]
            / "apps_rg"
            / "runtime"
            / "u0"
            / "structured_resume_classifier.py"
        )
        return path.read_text(encoding="utf-8")

    def _import_lines(self, source: str) -> list[str]:
        return [
            ln.strip()
            for ln in source.splitlines()
            if ln.strip().startswith(("import ", "from "))
        ]

    def test_no_section_agentic_pipeline_import(self):
        lines = self._import_lines(self._read_classifier_source())
        for ln in lines:
            assert "section_agentic_pipeline" not in ln, f"Forbidden import: {ln}"

    def test_no_write_section_to_semantic_cache_import(self):
        lines = self._import_lines(self._read_classifier_source())
        for ln in lines:
            assert "write_section_to_semantic_cache" not in ln, f"Forbidden import: {ln}"

    def test_no_l6_shadow_learning_import(self):
        lines = self._import_lines(self._read_classifier_source())
        for ln in lines:
            assert "l6_shadow_learning" not in ln, f"Forbidden import: {ln}"

    def test_no_openai_import(self):
        lines = self._import_lines(self._read_classifier_source())
        for ln in lines:
            assert "openai" not in ln, f"Forbidden import: {ln}"

    def test_no_anthropic_import(self):
        lines = self._import_lines(self._read_classifier_source())
        for ln in lines:
            assert "anthropic" not in ln, f"Forbidden import: {ln}"

    def test_no_agentic_core_import(self):
        lines = self._import_lines(self._read_classifier_source())
        for ln in lines:
            assert "agentic_core" not in ln, f"Forbidden import: {ln}"

    def test_no_pa_binding_import(self):
        lines = self._import_lines(self._read_classifier_source())
        for ln in lines:
            assert "pa_binding" not in ln, f"Forbidden import: {ln}"

    def test_no_c0_binding_import(self):
        lines = self._import_lines(self._read_classifier_source())
        for ln in lines:
            assert "c0_binding" not in ln, f"Forbidden import: {ln}"

    def test_no_requests_post_call(self):
        source = self._read_classifier_source()
        assert "requests.post" not in source
        assert "httpx.post" not in source

    def test_no_qwen_vllm_reference(self):
        source = self._read_classifier_source()
        assert "qwen_vllm" not in source
        assert "vllm" not in source.lower().replace("valid", "").replace("invalid", "")

    def test_result_is_dataclass_frozen(self):
        from apps_rg.runtime.u0.structured_resume_classifier import StructuredResumeClassification
        import dataclasses
        assert dataclasses.is_dataclass(StructuredResumeClassification)
        assert StructuredResumeClassification.__dataclass_params__.frozen is True

    def test_classify_does_not_mutate_input(self):
        from apps_rg.runtime.u0.structured_resume_classifier import classify_resume_payload
        payload = _make_resume_payload(structured=VALID_STRUCTURED_RESUME)
        import copy
        payload_before = copy.deepcopy(payload)
        classify_resume_payload(payload)
        assert payload == payload_before


# ---------------------------------------------------------------------------
# S1/S2/S3 Regression smoke
# ---------------------------------------------------------------------------

class TestS1S2S3Regression:
    def test_s1_schema_module_importable(self):
        from apps_rg.runtime.schemas import source_resume_schema
        assert hasattr(source_resume_schema, "validate_structured_resume")
        assert hasattr(source_resume_schema, "is_structured_resume")

    def test_s2_treatment_profile_module_importable(self):
        from apps_rg.runtime.schemas import section_treatment_profile
        assert hasattr(section_treatment_profile, "get_section_policy")

    def test_s3_pa_binding_module_importable(self):
        from apps_rg.runtime.bindings import pa_binding
        assert hasattr(pa_binding, "build_section_prompt_artifact")
        assert hasattr(pa_binding, "SectionPromptArtifact")

    def test_s4_classifier_independent_of_s3_pa_binding(self):
        import sys
        classifier_mod = sys.modules.get("apps_rg.runtime.u0.structured_resume_classifier")
        if classifier_mod is None:
            from apps_rg.runtime.u0 import structured_resume_classifier as classifier_mod
        pa_mod_name = "apps_rg.runtime.bindings.pa_binding"
        assert pa_mod_name not in (
            getattr(classifier_mod, "__dict__", {}).get("__name__", ""),
        )
