"""E2E (no mocks): C0.1–C0.7 evidence room for all generated lanes via wire_section_fec_bridge."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
)
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import default_graph_sqlite_path
from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.c0.constants import FORBIDDEN_PROOF_SOURCE_TYPES
from apps_rg.runtime.c0.evidence_room import C0_ROOM_RECEIPT
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane
from apps_rg.runtime.spine.c0_fec_compose import (
    FEC_BRIDGE_ARTIFACT,
    FEC_BRIDGE_RECEIPT,
    wire_spine_c0_fec_for_section,
)
from apps_rg.runtime.spine.c0_graph_lane_receipt import C0_GRAPH_LANE_RECEIPT_ARTIFACT
from apps_rg.runtime.spine.spine_c03_authority import spine_graph_refs_live
from apps_rg.runtime.sections.competencies_lane_defaults import (
    BRIEFING_DEFAULT,
    JD_TEXT_DEFAULT,
    REPO_ROOT,
    TARGET_COMPANY_DEFAULT,
    TARGET_TITLE_DEFAULT,
)
from apps_rg.runtime.sections.resume_employment_bullets import collect_employment_bullets

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "artifacts/apps_rg/c0/prior_resume_variant_fact_extraction_manifest.json"
LEDGER = default_ledger_path(REPO)
GRAPH_SQLITE = default_graph_sqlite_path(REPO)
CHROMA_DB = REPO / "data/cache/chromadb"

_C0_PHASE_SCHEMA: dict[str, str] = {
    "c01": "c01_retrieval_plan_v1",
    "c02": "c02_evidence_fetch_v1",
    "c03": "c03_skills_graph_v1",
    "c04": "c04_stratify_v1",
    "c05": "c05_fec_packet_v1",
    "c06": "c06_weak_refine_v1",
    "c07": "c07_handoff_audit_v1",
}


def _lane_args() -> argparse.Namespace:
    return argparse.Namespace(
        target_company=TARGET_COMPANY_DEFAULT,
        target_title=TARGET_TITLE_DEFAULT,
        target_role=TARGET_TITLE_DEFAULT,
        jd_text=JD_TEXT_DEFAULT,
        briefing=BRIEFING_DEFAULT,
        base_resume_ref="",
        provider="retired_provider_profile",
    )


@pytest.mark.skipif(not LEDGER.is_file(), reason="master candidate fact ledger missing")
@pytest.mark.skipif(not MANIFEST.is_file(), reason="prior resume variant manifest missing")
@pytest.mark.skipif(not CHROMA_DB.is_dir(), reason="fact_vectors Chroma cache missing")
@pytest.mark.parametrize("section_id", GENERATED_LANES)
def test_generated_lane_c0_evidence_room_e2e(
    tmp_path: Path,
    section_id: str,
) -> None:
    """Real front spine + proof pool + C0.1–C0.7 + FEC bridge per generated lane."""
    os.environ["APPS_RG_C0_EVIDENCE_ROOM"] = "1"
    os.environ["CHROMA_PERSIST_DIR"] = str(CHROMA_DB)
    artifact_dir = tmp_path / f"{section_id}_c0_e2e"
    pool, _base, _path, _hash, front_spine = load_section_proof_for_lane(
        section_id=section_id,
        args=_lane_args(),
        repo_root=REPO,
        collect_employment_bullets_fn=collect_employment_bullets,
        artifact_dir=artifact_dir,
    )
    assert pool.allowed_fact_ids_ordered, f"{section_id}: proof pool must resolve allowed facts"
    runtime_payload: dict = {"run_id": f"c0_e2e_{section_id}", "section_id": section_id}
    bridge = wire_spine_c0_fec_for_section(
        artifact_dir=artifact_dir,
        section_id=section_id,
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
    )
    doc = bridge.bridge_doc
    assert doc.get("producer_stage") == "section_c0_evidence_room", section_id
    assert doc.get("canonical_c0_2_claimed") is True
    if doc.get("core_c03_graph_rag_used") is True:
        assert doc.get("canonical_c0_3_claimed") is True
    else:
        assert doc.get("canonical_c0_3_claimed") is False
    assert doc.get("apps_rg_c03_skills_graph_used") is True
    assert doc.get("canonical_c0_5_claimed") is True
    assert doc.get("fec_shape_only") is False
    assert doc.get("c07_handoff_safe") is True
    room = doc.get("c0_evidence_room") or {}
    assert room.get("c02_atom_count", 0) > 0
    c01 = room.get("c01") or {}
    assert c01.get("section_id") == section_id
    c07 = room.get("c07") or {}
    assert c07.get("handoff_safe") is True
    assert not c07.get("violations")

    for phase, schema in _C0_PHASE_SCHEMA.items():
        receipt = room.get(phase) or {}
        assert receipt, f"{section_id}: missing c0_evidence_room.{phase}"
        assert receipt.get("schema_version") == schema, f"{section_id}: {phase} schema"

    c03_room = room.get("c03") or {}
    graph_ref = str(c03_room.get("graph_context_ref") or "").strip()
    assert graph_ref, f"{section_id}: C0.3 must bind augmented skills graph SQLite"
    graph_path = Path(graph_ref)
    if not graph_path.is_file():
        graph_path = REPO / graph_ref
    assert graph_path.is_file(), f"{section_id}: graph DB missing at {graph_ref}"
    assert graph_path.name == GRAPH_SQLITE.name, section_id
    metrics = c03_room.get("binding_metrics") or {}
    assert metrics.get("atom_count", 0) == room.get("c02_atom_count", 0), section_id
    assert "fact_links_available" in metrics, section_id
    assert metrics.get("fact_links_available", -1) >= 0, section_id

    bundle = json.loads((artifact_dir / C0_ROOM_RECEIPT).read_text(encoding="utf-8"))
    c03_full = bundle.get("c03") or {}
    bindings = list(c03_full.get("bindings") or [])
    assert len(bindings) == room.get("c02_atom_count", 0), section_id
    assert c03_full.get("new_atoms_created") == 0, section_id
    c05 = room.get("c05") or {}
    assert c05.get("graph_binding_count", 0) == len(bindings), section_id
    assert c05.get("evidence_item_count", 0) > 0, section_id

    assert (artifact_dir / C0_ROOM_RECEIPT).is_file()
    assert (artifact_dir / FEC_BRIDGE_ARTIFACT).is_file()
    assert (artifact_dir / FEC_BRIDGE_RECEIPT).is_file()
    assert (artifact_dir / C0_GRAPH_LANE_RECEIPT_ARTIFACT).is_file()
    assert (artifact_dir / "c0_metrics.json").is_file()

    fec_on_disk = json.loads((artifact_dir / FEC_BRIDGE_ARTIFACT).read_text(encoding="utf-8"))
    assert fec_on_disk.get("allowed_fact_ids")
    for item in fec_on_disk.get("evidence_items") or []:
        slot = str(item.get("allowed_prompt_slot") or "")
        if slot:
            assert slot == ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY
        st = str(item.get("source_class") or item.get("source_type") or "")
        assert st not in FORBIDDEN_PROOF_SOURCE_TYPES
