"""resume_export_enrich — base-resume parity for DOCX export (contact, skills, certs, headline repair)."""
from __future__ import annotations

import json

from apps_rg.runtime.render.resume_export_enrich import (
    enrich_generated_resume_for_docx,
    repair_headline_name_leak,
    skills_categories_from_base_resume,
)


def test_repair_headline_replaces_segment1_when_name_token_present() -> None:
    base = {
        "candidate_name": "Amit Tester",
        "header": {"name": "Amit Tester"},
        "facts": {
            "employment": [
                {
                    "fact_id": "exp_x",
                    "employer": "Co",
                    "title": "SVP Engineering, Agentic AI Platforms",
                    "is_current": True,
                    "bullets": [],
                },
            ],
        },
    }
    bad = "Engineering Leader amit | AI Platforms | Enterprise Scale Operations"
    fixed = repair_headline_name_leak(bad, base)
    assert "amit" not in fixed.lower()
    assert fixed.startswith("SVP Engineering, Agentic AI Platforms |")


def test_skills_categories_from_base_maps_fact_blocks() -> None:
    base = {
        "facts": {
            "skills": [
                {"category": "Agentic AI Platforms", "terms": ["GraphRAG", "Policy gating"]},
            ],
        },
    }
    sk = skills_categories_from_base_resume(base)
    assert sk is not None
    assert sk["categories"][0]["name"] == "Agentic AI Platforms"
    assert "GraphRAG" in sk["categories"][0]["items"]


def test_enrich_fills_skills_certifications_contact_from_master_blob() -> None:
    base = {
        "candidate_name": "Taylor Example",
        "header": {
            "phone": "+1-555-0000",
            "email": "t@example.com",
            "linkedin": "linkedin.com/in/t",
        },
        "facts": {
            "skills": [
                {"category": "Platforms", "terms": ["Kubernetes"]},
            ],
            "certifications": [
                {
                    "name": "Cert One",
                    "issuing_organization": "Board",
                    "year": "2024",
                },
            ],
            "employment": [],
        },
    }
    blob = json.dumps(base)
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
    cats = out["sections"]["skills"]["categories"]
    assert cats[0]["name"] == "Platforms"
    assert out["sections"]["certifications"][0]["issuer"] == "Board"


def test_enrich_base_resume_identity_overrides_llm_contact_and_name() -> None:
    base = {
        "candidate_name": "Canonical Name",
        "header": {
            "name": "Canonical Name",
            "phone": "+1-base-phone",
            "email": "base@example.com",
            "location": "Base City, ST",
        },
        "facts": {"employment": []},
    }
    blob = json.dumps(base)
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


def test_enrich_identity_falls_back_to_header_name_when_no_candidate_name() -> None:
    base = {
        "facts": {
            "header": {"name": "Header Only", "email": "h@example.com"},
            "employment": [],
        },
    }
    blob = json.dumps(base)
    payload = {"sections": {"summary": {"text": "x" * 30, "word_count": 10}, "experience": []}}
    out = enrich_generated_resume_for_docx(payload, blob)
    assert out["candidate_name"] == "Header Only"
    assert out["contact_info"]["email"] == "h@example.com"
