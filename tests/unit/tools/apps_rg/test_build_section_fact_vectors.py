"""Unit tests for C0.2 per-section fact vector section assignment (no Chroma required)."""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("company", "expected_employer_sections"),
    [
        ("IBM Corporation", ["ibm_bullets", "ibm_narrative"]),
        ("Unify Platform", ["unify_bullets", "unify_narrative"]),
        ("Current Role — Platform Engineering", ["unify_bullets", "unify_narrative"]),
        ("Acme Corp", []),
    ],
)
def test_assign_sections_employer_routing(company: str, expected_employer_sections: list[str]) -> None:
    from tools.apps_rg.build_section_fact_vectors import (
        ALL_SECTIONS,
        CROSS_SECTION_TARGETS,
        assign_sections_for_fact,
    )

    row = {"company": company, "role_families_supported": []}
    sections = assign_sections_for_fact(row)
    for s in CROSS_SECTION_TARGETS:
        assert s in sections
    for s in expected_employer_sections:
        assert s in sections
    assert all(s in ALL_SECTIONS for s in sections)


def test_assign_sections_role_family_enriches_unify_lanes() -> None:
    from tools.apps_rg.build_section_fact_vectors import assign_sections_for_fact

    row = {
        "company": "Unknown Vendor",
        "role_families_supported": ["ENGINEERING_PLATFORM"],
    }
    sections = assign_sections_for_fact(row)
    assert "unify_bullets" in sections
    assert "unify_narrative" in sections


def test_build_section_atoms_skips_non_high_confidence(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_rg.runtime.c0 import c02_fact_vector_ingest as ingest_mod
    from tools.apps_rg.build_section_fact_vectors import build_section_atoms

    def _fake_ledger(**_kwargs: object) -> dict:
        return {
            "candidate_facts": [
                {
                    "candidate_fact_id": "fact_low_001",
                    "company": "IBM",
                    "confidence": "LOW",
                    "claim_text": "low confidence claim",
                    "role_families_supported": [],
                },
                {
                    "candidate_fact_id": "fact_high_001",
                    "company": "IBM",
                    "confidence": "HIGH",
                    "claim_text": "high confidence claim",
                    "role_families_supported": ["ENGINEERING_PLATFORM"],
                },
            ]
        }

    monkeypatch.setattr(
        "tools.apps_rg.build_section_fact_vectors.load_master_candidate_fact_ledger",
        _fake_ledger,
    )
    monkeypatch.setattr(
        ingest_mod,
        "c02_atom_ingest_eligible",
        lambda atom: (atom.get("fact_id") == "fact_high_001", "skipped"),
    )

    atoms, summary = build_section_atoms(repo_root=Path("/tmp"))
    assert summary["eligible_atoms"] == 1
    assert atoms[0]["fact_id"] == "fact_high_001"
    assert "ibm_bullets" in atoms[0]["allowed_sections"]
    assert "competencies" in atoms[0]["allowed_sections"]
