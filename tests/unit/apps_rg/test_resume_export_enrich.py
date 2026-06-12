"""resume_export_enrich - static-profile parity for DOCX export."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.render.resume_export_enrich import (
    certifications_from_static_profile,
    enrich_generated_resume_for_docx,
    repair_headline_name_leak,
    skills_categories_from_static_profile,
)


def test_repair_headline_replaces_segment1_when_name_token_present() -> None:
    profile = {
        "name": "Amit Tester",
        "employment_identity": [
            {
                "company": "Co",
                "title": "SVP Engineering, Agentic AI Platforms",
                "end_date": "present",
            },
        ],
    }
    bad = "Engineering Leader amit | AI Platforms | Enterprise Scale Operations"
    fixed = repair_headline_name_leak(bad, profile)
    assert "amit" not in fixed.lower()
    assert fixed.startswith("SVP Engineering, Agentic AI Platforms |")


def test_skills_categories_from_static_profile_is_not_authority() -> None:
    profile = {
        "skills": [
            {"category": "Agentic AI Platforms", "terms": ["GraphRAG", "Policy gating"]},
        ],
    }
    assert skills_categories_from_static_profile(profile) is None


def test_certifications_from_static_profile_maps_export_shape() -> None:
    profile = {
        "certifications": [
            {
                "name": "Cert One",
                "issuing_organization": "Board",
                "year": "2024",
            },
        ],
    }
    assert certifications_from_static_profile(profile) == [
        {"name": "Cert One", "issuer": "Board", "date": "2024"}
    ]


def test_enrich_fills_certifications_contact_from_static_profile_without_skills() -> None:
    profile = {
        "name": "Taylor Example",
        "phone": "+1-555-0000",
        "email": "t@example.com",
        "linkedin": "linkedin.com/in/t",
        "certifications": [
            {
                "name": "Cert One",
                "issuing_organization": "Board",
                "year": "2024",
            },
        ],
        "employment_identity": [],
    }
    blob = json.dumps(profile)
    payload = {
        "candidate_name": "Taylor Example",
        "sections": {
            "summary": {"text": "x", "word_count": 10},
            "experience": [],
            "skills": {},
            "education": [],
        },
    }
    out = enrich_generated_resume_for_docx(payload, blob)
    assert out["contact_info"]["email"] == "t@example.com"
    assert out["sections"]["skills"] == {}
    assert out["sections"]["certifications"][0]["issuer"] == "Board"


def test_enrich_static_profile_identity_overrides_llm_contact_and_name() -> None:
    profile = {
        "name": "Canonical Name",
        "phone": "+1-base-phone",
        "email": "base@example.com",
        "location": "Base City, ST",
        "employment_identity": [],
    }
    blob = json.dumps(profile)
    payload = {
        "candidate_name": "Wrong LLM Name",
        "contact_info": {
            "phone": "+1-wrong",
            "email": "wrong@example.com",
            "linkedin": "https://linkedin.com/wrong",
        },
        "sections": {"summary": {"text": "x" * 30, "word_count": 10}, "experience": []},
    }
    out = enrich_generated_resume_for_docx(payload, blob)
    assert out["candidate_name"] == "Canonical Name"
    assert out["contact_info"]["phone"] == "+1-base-phone"
    assert out["contact_info"]["email"] == "base@example.com"
    assert out["contact_info"]["location"] == "Base City, ST"
    assert out["contact_info"]["linkedin"] == "https://linkedin.com/wrong"


def _walk_keys(obj: Any) -> set[str]:
    if isinstance(obj, dict):
        keys = set(obj)
        for value in obj.values():
            keys.update(_walk_keys(value))
        return keys
    if isinstance(obj, list):
        keys: set[str] = set()
        for value in obj:
            keys.update(_walk_keys(value))
        return keys
    return set()


def test_candidate_static_profile_file_is_claim_free() -> None:
    repo = Path(__file__).resolve().parents[3]
    profile_path = repo / "apps_rg" / "resume" / "base" / "candidate_static_profile.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    assert set(profile) == {
        "name",
        "phone",
        "email",
        "linkedin",
        "github",
        "location",
        "certifications",
        "employment_identity",
    }
    forbidden = {
        "skills",
        "bullets",
        "summary",
        "summaries",
        "accomplishments",
        "metrics",
        "metrics_summary",
        "role_narrative",
        "claims",
        "claim_text",
        "facts",
    }
    assert _walk_keys(profile).isdisjoint(forbidden)
