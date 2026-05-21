"""E2E (no mocks): competencies C0 evidence room through real proof pool + front spine + FEC bridge."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
)
from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.c0.constants import FORBIDDEN_PROOF_SOURCE_TYPES
from apps_rg.runtime.c0.evidence_room import C0_ROOM_RECEIPT
from apps_rg.runtime.proof_pool_lane_integration import load_section_proof_for_lane
from apps_rg.runtime.section_fec_bridge import (
    FEC_BRIDGE_ARTIFACT,
    FEC_BRIDGE_RECEIPT,
    wire_section_fec_bridge_for_lane,
)
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


def _competencies_args() -> argparse.Namespace:
    return argparse.Namespace(
        target_company=TARGET_COMPANY_DEFAULT,
        target_title=TARGET_TITLE_DEFAULT,
        target_role=TARGET_TITLE_DEFAULT,
        jd_text=JD_TEXT_DEFAULT,
        briefing=BRIEFING_DEFAULT,
        selected_role_fact_set="",
        broad_skills_ledger_path="",
        base_resume_ref="",
        provider="qwen_vllm",
    )


@pytest.mark.skipif(not LEDGER.is_file(), reason="master candidate fact ledger missing")
@pytest.mark.skipif(not MANIFEST.is_file(), reason="prior resume variant manifest missing")
def test_competencies_c0_evidence_room_e2e_real_proof_pool_and_fec(tmp_path: Path) -> None:
    """Real U0/L1/L0 front spine, proof pool, C0.1–C0.7, and FEC bridge artifacts — no mocks."""
    os.environ["APPS_RG_C0_EVIDENCE_ROOM"] = "1"
    os.environ.pop("CHROMA_PERSIST_DIR", None)
    artifact_dir = tmp_path / "competencies_c0_e2e"
    args = _competencies_args()
    pool, _base, _path, _hash, front_spine = load_section_proof_for_lane(
        section_id="competencies",
        args=args,
        repo_root=REPO,
        collect_employment_bullets_fn=collect_employment_bullets,
        artifact_dir=artifact_dir,
    )
    assert pool.allowed_fact_ids_ordered, "proof pool must resolve real allowed facts"
    runtime_payload: dict = {"run_id": "c0_e2e_proof", "section_id": "competencies"}
    bridge = wire_section_fec_bridge_for_lane(
        artifact_dir=artifact_dir,
        section_id="competencies",
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
    )
    doc = bridge.bridge_doc
    assert doc.get("canonical_c0_2_claimed") is True
    assert doc.get("canonical_c0_3_claimed") is True
    assert doc.get("canonical_c0_5_claimed") is True
    assert doc.get("fec_shape_only") is False
    assert doc.get("c07_handoff_safe") is True
    room = doc.get("c0_evidence_room") or {}
    assert room.get("c02_atom_count", 0) > 0
    c07 = room.get("c07") or {}
    assert c07.get("handoff_safe") is True
    assert not c07.get("violations")

    fec_path = artifact_dir / FEC_BRIDGE_ARTIFACT
    room_path = artifact_dir / C0_ROOM_RECEIPT
    assert fec_path.is_file()
    assert room_path.is_file()
    assert (artifact_dir / FEC_BRIDGE_RECEIPT).is_file()

    fec_on_disk = json.loads(fec_path.read_text(encoding="utf-8"))
    assert fec_on_disk.get("allowed_fact_ids")
    for item in fec_on_disk.get("evidence_items") or []:
        slot = str(item.get("allowed_prompt_slot") or "")
        assert slot == ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY
        st = str(item.get("source_class") or item.get("source_type") or "")
        assert st not in FORBIDDEN_PROOF_SOURCE_TYPES
        content = str(item.get("content") or item.get("text") or "")
        assert "jd_payload" not in str(item.get("source") or "").lower()
        if content:
            assert len(content) <= 2000

    snap = runtime_payload.get("canonical_final_evidence_contract_snapshot")
    assert isinstance(snap, dict)
    assert int(snap.get("evidence_item_count") or 0) > 0
    assert snap.get("final_evidence_digest")

    pa_fields = __import__(
        "apps_rg.runtime.section_fec_bridge",
        fromlist=["pa_consumption_receipt_fields"],
    ).pa_consumption_receipt_fields(runtime_payload)
    assert pa_fields["canonical_c0_5_claimed"] is True
    assert pa_fields["evidence_contract_consumed"] is True
    assert pa_fields["raw_proof_pool_direct_to_pa"] is False


def test_prior_manifest_on_disk_has_required_row_fields() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = payload.get("rows") or []
    assert len(rows) >= 100
    row = rows[0]
    for key in (
        "source_resume_variant",
        "candidate_fact_atom",
        "source_span_ref",
        "matched_existing_fact_id",
        "confidence",
        "proof_status",
        "embed_allowed",
    ):
        assert key in row


@pytest.mark.skipif(
    os.environ.get("PYTEST_APPS_RG_LIVE_L2", "").strip().lower() not in ("1", "true", "yes"),
    reason="set PYTEST_APPS_RG_LIVE_L2=1 for live competencies CLI (no mocks, no stub)",
)
def test_competencies_cli_live_through_c0_room_artifacts(tmp_path: Path) -> None:
    """Full ``python -m apps_rg --section competencies`` with live qwen — zero mock/stub flags."""
    from apps_rg.runtime.providers.competencies_live_provider_gate import qwen_vllm_http_models_preflight

    ok, detail, _snap = qwen_vllm_http_models_preflight(
        provider_url=os.environ.get("APPS_RG_QWEN_OPENAI_BASE", "http://127.0.0.1:8000/v1"),
        timeout_s=5.0,
    )
    if not ok:
        pytest.skip(f"live qwen_vllm unavailable: {detail}")

    env = dict(os.environ)
    env["PYTEST_APPS_RG_LIVE_L2"] = "1"
    env["APPS_RG_C0_EVIDENCE_ROOM"] = "1"
    env.pop("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", None)
    env.pop("APPS_RG_TEST_HARNESS", None)
    env.pop("APPS_RG_MOCK_JUDGES", None)
    resume = REPO / "apps_rg/resume/base/amit_ayer_base_resume_v1.json"
    art = REPO / "artifacts" / "apps_rg" / "runtime_proofs" / f"c0_cli_e2e_{uuid.uuid4().hex[:12]}"
    art.mkdir(parents=True, exist_ok=True)
    live_jd = (
        "E2E C0 evidence room live proof: SVP Engineering, agentic AI platforms, "
        "governed delivery, and cross-functional leadership."
    )
    live_brief = (
        "E2E C0 evidence room live proof: emphasize platform scale, compliance-aware "
        "AI delivery, and executive stakeholder alignment."
    )
    cmd = [
        sys.executable,
        "-m",
        "apps_rg",
        "--section",
        "competencies",
        "--target-company",
        TARGET_COMPANY_DEFAULT,
        "--target-role",
        TARGET_TITLE_DEFAULT,
        "--jd",
        live_jd,
        "--manual-brief",
        live_brief,
        "--resume",
        str(resume),
        "--provider",
        "qwen_vllm",
        "--artifact-dir",
        str(art),
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )
    assert (art / C0_ROOM_RECEIPT).is_file(), (
        f"C0 evidence room receipt missing (rc={proc.returncode}): "
        f"{(proc.stderr or proc.stdout)[-2000:]}"
    )
    room = json.loads((art / C0_ROOM_RECEIPT).read_text(encoding="utf-8"))
    assert room.get("c07", {}).get("handoff_safe") is True
    fv = room.get("c02", {}).get("fact_vectors_ingest") or {}
    if fv.get("attempted"):
        assert int(fv.get("upserted_count") or 0) >= 1
    bridge = json.loads((art / FEC_BRIDGE_ARTIFACT).read_text(encoding="utf-8"))
    assert bridge.get("producer_stage") == "section_c0_evidence_room"
    assert bridge.get("canonical_c0_2_claimed") is True
    assert bridge.get("canonical_c0_3_claimed") is True
    assert bridge.get("canonical_c0_5_claimed") is True
    assert bridge.get("c07_handoff_safe") is True
    runtime_payload = json.loads((art / "runtime_payload.json").read_text(encoding="utf-8"))
    assert runtime_payload.get("canonical_final_evidence_contract_snapshot")
    compiled = json.loads((art / "compiled_prompt_artifact.json").read_text(encoding="utf-8"))
    assert compiled.get("canonical_c0_5_claimed") is True
    assert compiled.get("evidence_contract_consumed") is True
    x3 = json.loads((art / "x3_disposition.json").read_text(encoding="utf-8"))
    assert x3.get("runtime_generation_status") == "REAL_LLM"
    assert x3.get("mocked_judges") == []
    assert "MOCK" not in str(x3.get("runtime_generation_status") or "").upper()
