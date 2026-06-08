"""Phase 0 seed — base-resume employment coverage + source-class diversity.

Deterministic, hermetic (reads the base resume; no Chroma/provider). Guards the cold-start fix
(plan apps-rg-fact-vector-writeback-discipline-67652c, Phase 0): build_section_fact_vectors now also
seeds base-resume EMPLOYMENT bullets (InsurTech/EY/IBM/Unify) as grounded project_evidence atoms, so a
pure seed spans >=2 normative source classes (candidate_profile + project_evidence) — the FEC marks
single-class dense support as WEAK and blocks insurtech/ey otherwise.
"""
from __future__ import annotations

from apps_rg.runtime.c0.c02_fact_vector_ingest import c02_atom_to_fact_vector_chunk
from apps_rg.runtime.c0.constants import SOURCE_BASE_RESUME
from apps_rg.runtime.c0.fact_vector_write_back import EXTRACT, STAGE_FOR_FACT_VECTORS, decide_write_back
from tools.apps_rg.build_section_fact_vectors import build_base_resume_employment_atoms


def _atoms():
    atoms, summary = build_base_resume_employment_atoms()
    return atoms, summary


def test_seeds_insurtech_and_ey_employment_bullets() -> None:
    atoms, _ = _atoms()
    by_id = {a["fact_id"]: a for a in atoms}
    for bid in ("bul_insurtech_001", "bul_insurtech_002", "bul_insurtech_003",
                "bul_ey_001", "bul_ey_002", "bul_ey_003"):
        assert bid in by_id, f"{bid} not seeded from base resume"


def test_insurtech_atoms_target_insurtech_lanes() -> None:
    atoms, _ = _atoms()
    it = next(a for a in atoms if a["fact_id"] == "bul_insurtech_001")
    assert "insurtech_bullets" in it["allowed_sections"]
    assert "insurtech_narrative" in it["allowed_sections"]


def test_employment_atoms_are_grounded_project_evidence() -> None:
    atoms, _ = _atoms()
    it = next(a for a in atoms if a["fact_id"] == "bul_insurtech_001")
    assert it["source_type"] == SOURCE_BASE_RESUME
    assert it["fact_vector_source_class"] == "project_evidence"
    assert it["source_span_ref"] == "base_resume:bul_insurtech_001"


def test_employment_atoms_route_as_extract_to_staging() -> None:
    atoms, _ = _atoms()
    it = next(a for a in atoms if a["fact_id"] == "bul_ey_001")
    d = decide_write_back(it)
    assert d.operation == EXTRACT
    assert d.route == STAGE_FOR_FACT_VECTORS


def test_chunk_builder_honors_project_evidence_source_class() -> None:
    atoms, _ = _atoms()
    it = next(a for a in atoms if a["fact_id"] == "bul_insurtech_001")
    chunk = c02_atom_to_fact_vector_chunk(it, section_id="insurtech_bullets", ledger_version_hash="h")
    assert chunk.source_class == "project_evidence"


def test_default_source_class_is_candidate_profile() -> None:
    # An atom with no fact_vector_source_class hint stays candidate_profile (skills-ledger default).
    plain = {"fact_id": "fact_x", "text_to_embed": "y" * 30, "allowed_sections": ["competencies"]}
    chunk = c02_atom_to_fact_vector_chunk(plain, section_id="competencies", ledger_version_hash="h")
    assert chunk.source_class == "candidate_profile"


def test_seed_spans_two_source_classes() -> None:
    # The employment seed contributes project_evidence; the ledger seed contributes candidate_profile.
    # Together they satisfy the FEC's >=2-class requirement.
    atoms, summary = _atoms()
    assert summary["base_resume_employment_atoms"] >= 6  # 3 insurtech + 3 ey at minimum
    assert all(a["fact_vector_source_class"] == "project_evidence" for a in atoms)
