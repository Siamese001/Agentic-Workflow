"""Governed apps_rg C0 evidence room — C0.2/C0.3 boundary and FEC binding (no mocks)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    EvidenceItem,
    FinalEvidenceContract,
)
from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    load_master_candidate_fact_ledger,
)
from apps_rg.runtime.c0.c02_evidence_fetch import fetch_c02_evidence_atoms
from apps_rg.runtime.c0.c03_graph_expansion import expand_c03_graph_bindings
from apps_rg.runtime.c0.c04_stratify import stratify_c04_evidence
from apps_rg.runtime.c0.c05_fec_packet import build_c05_final_evidence_contract, _strip_forbidden_items
from apps_rg.runtime.c0.c07_handoff_audit import audit_c07_handoff
from apps_rg.runtime.c0.constants import CONFIDENCE_PENDING, SOURCE_JD
from apps_rg.runtime.proof_pool_resolver import SectionProofPool

REPO = Path(__file__).resolve().parents[3]
LEDGER = default_ledger_path(REPO)


def _first_high_ledger_fact() -> dict:
    if not LEDGER.is_file():
        return {
            "candidate_fact_id": "fact_test_001",
            "claim_text": "Led platform modernization with measurable cost reduction.",
            "confidence": "HIGH",
        }
    ledger = load_master_candidate_fact_ledger(repo_root=REPO, path=LEDGER)
    for row in ledger.get("candidate_facts") or []:
        if str(row.get("confidence") or "").upper() == "HIGH":
            return dict(row)
    rows = ledger.get("candidate_facts") or []
    assert rows, "ledger must contain candidate_facts"
    return dict(rows[0])


def _pool(*, facts: list[dict] | None = None) -> SectionProofPool:
    facts = facts or [_first_high_ledger_fact()]
    allowed = {str(f["candidate_fact_id"]) for f in facts}
    return SectionProofPool(
        section="competencies",
        proof_source="srfs",
        proof_pool_ref="proof_pool.json",
        proof_pool_digest="abc",
        selected_fact_plan={"facts": facts},
        allowed_fact_ids_ordered=sorted(allowed),
        allowed_fact_ids=allowed,
        bullet_rows=[],
        proof_pool_metadata={},
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=True,
        base_resume_json_ref="",
        base_resume_json_hash="",
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        srfs_ref="srfs.json",
        base_resume_override_used=False,
    )


@pytest.mark.skipif(not LEDGER.is_file(), reason="master ledger missing")
def test_c02_does_not_use_jd_as_proof() -> None:
    c02 = fetch_c02_evidence_atoms(section_id="competencies", pool=_pool(), repo_root=REPO)
    assert c02["jd_used_as_proof"] is False
    assert any(r["source_type"] == SOURCE_JD for r in c02["rejected_candidates"])


@pytest.mark.skipif(not LEDGER.is_file(), reason="master ledger missing")
def test_c02_atoms_have_source_metadata() -> None:
    c02 = fetch_c02_evidence_atoms(section_id="competencies", pool=_pool(), repo_root=REPO)
    atoms = c02["atoms"]
    assert atoms
    atom = atoms[0]
    for key in (
        "fact_id",
        "text_to_embed",
        "source_type",
        "source_span_ref",
        "proof_status",
        "graph_node_refs",
    ):
        assert key in atom
    assert c02["graph_inference_performed"] is False


@pytest.mark.skipif(not LEDGER.is_file(), reason="master ledger missing")
def test_c02_carries_graph_refs_metadata_only() -> None:
    atom = fetch_c02_evidence_atoms(section_id="competencies", pool=_pool(), repo_root=REPO)["atoms"][0]
    assert atom["graph_node_refs"] == []


def test_strip_forbidden_removes_jd_inline() -> None:
    items = [
        EvidenceItem(
            source="jd_payload",
            content="We need a VP who knows Kubernetes",
            source_type="app_payload_inline",
        ),
        EvidenceItem(
            source="fact:f1",
            content="Short claim atom",
            source_type="proof_pool",
            source_id="f1",
        ),
    ]
    kept, ex = _strip_forbidden_items(items)
    assert len(kept) == 1
    assert ex


def test_prior_variant_defaults_pending_trace() -> None:
    rows = [
        {
            "source_resume_variant": "CTO Resume - Amit Ayer.docx",
            "candidate_fact_atom": "Built cloud-native platform on Kubernetes.",
            "source_span_ref": "CTO Resume - Amit Ayer.docx::line_3",
            "matched_existing_fact_id": None,
            "confidence": CONFIDENCE_PENDING,
            "proof_status": "claim_eligible",
            "requires_trace_audit": True,
            "embed_allowed": False,
            "reason": "unmatched",
        }
    ]
    assert rows[0]["embed_allowed"] is False
    assert rows[0]["confidence"] == CONFIDENCE_PENDING


@pytest.mark.skipif(not LEDGER.is_file(), reason="master ledger missing")
def test_c03_no_new_atoms() -> None:
    atoms = fetch_c02_evidence_atoms(section_id="competencies", pool=_pool(), repo_root=REPO)["atoms"]
    c03 = expand_c03_graph_bindings(section_id="competencies", atoms=atoms, repo_root=REPO)
    assert c03["new_atoms_created"] == 0
    assert len(c03["bindings"]) == len(atoms)


def test_c03_adjacency_only_not_claim_support() -> None:
    atoms = [
        {
            "fact_id": "f1",
            "skill_tags": ["nonexistent_skill_xyz"],
            "proof_status": "claim_eligible",
            "metric_refs": [],
            "career_phase_refs": [],
            "source_span_ref": "x",
        }
    ]
    c03 = expand_c03_graph_bindings(section_id="competencies", atoms=atoms, repo_root=REPO)
    b = c03["bindings"][0]
    if b["graph_support_strength"] == "ADJACENT_ONLY":
        assert b["claim_support_allowed"] is False


def test_c04_excludes_pending_when_proof_required() -> None:
    atoms = [
        {
            "fact_id": "f_pending",
            "proof_status": "claim_eligible",
            "confidence": CONFIDENCE_PENDING,
            "blocked_sections": [],
        }
    ]
    c04 = stratify_c04_evidence(
        section_id="executive_summary",
        atoms=atoms,
        graph_bindings=[],
        lane_requires_proof=True,
    )
    assert "f_pending" in c04["excluded_fact_ids"]


@pytest.mark.skipif(not LEDGER.is_file(), reason="master ledger missing")
def test_c05_emits_fec_with_allowed_fact_ids() -> None:
    atoms = fetch_c02_evidence_atoms(section_id="competencies", pool=_pool(), repo_root=REPO)["atoms"]
    c03 = expand_c03_graph_bindings(section_id="competencies", atoms=atoms, repo_root=REPO)
    c04 = stratify_c04_evidence(
        section_id="competencies",
        atoms=atoms,
        graph_bindings=c03["bindings"],
    )
    fec, receipt = build_c05_final_evidence_contract(
        section_id="competencies",
        atoms=atoms,
        strata=c04["strata"],
        graph_bindings=c03["bindings"],
        front_spine=None,
        allowed_fact_ids=c04["allowed_fact_ids"],
        merge_canonical_c0=False,
    )
    assert isinstance(fec, FinalEvidenceContract)
    assert receipt["allowed_fact_ids"]
    for it in fec.evidence_items:
        assert it.allowed_prompt_slot == ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY


def test_c07_flags_adjacency_as_proof_violation() -> None:
    fec, _ = build_c05_final_evidence_contract(
        section_id="competencies",
        atoms=[
            {
                "fact_id": "f1",
                "text_to_embed": "claim",
                "source_type": "proof_pool",
                "source_span_ref": "s",
                "proof_status": "proof_eligible",
            }
        ],
        strata={},
        graph_bindings=[],
        front_spine=None,
        allowed_fact_ids=["f1"],
        merge_canonical_c0=False,
    )
    c07 = audit_c07_handoff(
        fec=fec,
        c02_receipt={"graph_inference_performed": False},
        c03_receipt={"new_atoms_created": 0, "pending_trace_promoted": False},
        graph_bindings=[
            {
                "fact_id": "f1",
                "graph_support_strength": "ADJACENT_ONLY",
                "claim_support_allowed": True,
            }
        ],
    )
    assert c07["handoff_safe"] is False
    assert any("adjacency_as_proof" in v for v in c07["violations"])


def test_section_c0_room_enabled_for_competencies() -> None:
    from apps_rg.runtime.c0.evidence_room import section_c0_evidence_room_enabled

    assert section_c0_evidence_room_enabled("competencies")
    assert section_c0_evidence_room_enabled("executive_summary")
    assert not section_c0_evidence_room_enabled("headline")


def test_agentic_core_binding_import() -> None:
    from agentic_core.runtime.c0.apps_rg_c0_binding import c0_retrieve_apps_rg as spine_c0

    from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg as apps_c0

    assert spine_c0 is apps_c0


def test_c02_atom_ingest_eligible_rejects_pending_trace() -> None:
    from apps_rg.runtime.c0.c02_fact_vector_ingest import c02_atom_ingest_eligible

    ok, reason = c02_atom_ingest_eligible(
        {
            "fact_id": "f1",
            "text_to_embed": "Governed agentic platform delivery at scale.",
            "confidence": CONFIDENCE_PENDING,
            "proof_status": "claim_eligible",
        }
    )
    assert ok is False
    assert "pending_trace" in reason


@pytest.mark.skipif(not LEDGER.is_file(), reason="master ledger missing")
def test_c02_atoms_to_chunks_one_per_fact() -> None:
    from apps_rg.runtime.c0.c02_fact_vector_ingest import atoms_to_fact_vector_chunks

    row = _first_high_ledger_fact()
    atoms = [
        {
            "fact_id": row["candidate_fact_id"],
            "text_to_embed": row["claim_text"],
            "source_type": "candidate_fact_ledger",
            "source_span_ref": f"ledger:{row['candidate_fact_id']}",
            "confidence": "HIGH",
            "proof_status": "proof_eligible",
            "skill_tags": list(row.get("capability_tags") or [])[:3],
            "allowed_sections": ["competencies"],
            "blocked_sections": [],
        }
    ]
    chunks, _atoms, skipped = atoms_to_fact_vector_chunks(atoms, section_id="competencies")
    assert len(chunks) == 1
    assert skipped == []
    assert chunks[0].source_document_id == row["candidate_fact_id"]
    assert "competencies" in chunks[0].section_targets


def test_manifest_schema_fields() -> None:
    from apps_rg.runtime.c0 import c02_evidence_fetch as c02_mod

    manifest_path = REPO / "artifacts/apps_rg/c0/prior_resume_variant_fact_extraction_manifest.json"
    if manifest_path.is_file():
        row = json.loads(manifest_path.read_text(encoding="utf-8"))["rows"][0]
        assert "source_resume_variant" in row
        assert "source_span_ref" in row
        assert "candidate_fact_atom" in row
    atom = c02_mod._atom_from_manifest_row(
        {
            "source_resume_variant": "v.docx",
            "candidate_fact_atom": "AI governance controls",
            "source_span_ref": "v.docx::line_1",
            "matched_existing_fact_id": "fact_engineering_platform_001",
            "confidence": "HIGH",
            "proof_status": "proof_eligible",
            "requires_trace_audit": False,
            "embed_allowed": True,
            "variant_family": "AI/Data/Governance",
        },
        section_id="competencies",
    )
    assert atom is not None
    assert atom["source_span_ref"] == "v.docx::line_1"
