"""W4 — section lanes invoke spine ``c0_retrieve_apps_rg``; STOP AS EVIDENCE GAP on weak FEC."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK,
)
from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF
from apps_rg.runtime.proof_pool_resolver import SectionProofPool
from apps_rg.runtime.spine.c0_fec_compose import build_spine_c0_fec_artifact
from apps_rg.runtime.spine.front_contracts import (
    build_section_front_spine_from_args,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.spine.section_c0_retrieve import (
    STOP_AS_EVIDENCE_GAP,
    StopAsEvidenceGapError,
    assert_no_stop_as_evidence_gap,
    invoke_section_spine_c0_retrieve,
    merge_spine_fec_into_bridge_doc,
)

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _clear_fixture_dev_bypass() -> None:
    deactivate_fixture_dev_bypass()


def _args(**overrides: object) -> SimpleNamespace:
    base = {
        "target_company": "Acme Corp",
        "target_title": "VP Engineering",
        "target_role": "VP Engineering",
        "jd_text": "Lead platform engineering.",
        "briefing": "Regulated delivery.",
        "base_resume_ref": "",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _minimal_pool() -> SectionProofPool:
    return SectionProofPool(
        section="executive_summary",
        proof_source="augmented_skills_graph",
        proof_pool_ref="apps_rg/fixtures/graph.json",
        proof_pool_digest="abc",
        selected_fact_plan={"facts": [{"fact_id": "bul_acme_001", "claim_text": "Built platform."}]},
        allowed_fact_ids_ordered=["bul_acme_001"],
        allowed_fact_ids={"bul_acme_001"},
        bullet_rows=[],
        proof_pool_metadata={"proof_pool_type": "augmented_skills_graph"},
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="base.json",
        base_resume_json_hash="hash",
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        srfs_ref="",
        base_resume_override_used=False,
    )


def _pass_fec() -> FinalEvidenceContract:
    return FinalEvidenceContract(
        request_id="req-w4",
        run_id="run-w4",
        app_id="apps_rg",
        trace_id="trace-w4",
        l5_certification_ref="test:valid:w6",
        support_status=SUPPORT_STATUS_PASS,
        support_target_met=True,
        final_evidence_digest="digest-w4",
        graph_expansion_refs=(C0_GRAPH_LANE_NA_REF,),
        dense_search_refs=("chromadb:fact_vectors:hit",),
    )


def test_stop_as_evidence_gap_on_weak_fec() -> None:
    fec = FinalEvidenceContract(
        request_id="r",
        run_id="run",
        app_id="apps_rg",
        trace_id="t",
        l5_certification_ref="test:valid:w6",
        support_status=SUPPORT_STATUS_WEAK,
        support_target_met=False,
    )
    with pytest.raises(StopAsEvidenceGapError, match=STOP_AS_EVIDENCE_GAP):
        assert_no_stop_as_evidence_gap(grounding_required=True, fec=fec, section_id="headline")


def test_stop_as_evidence_gap_allows_pass() -> None:
    assert_no_stop_as_evidence_gap(
        grounding_required=True,
        fec=_pass_fec(),
        section_id="headline",
    )


def test_invoke_section_spine_c0_retrieve_merges_into_bridge(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spine = build_section_front_spine_from_args(
        section_id="executive_summary",
        args=_args(),
        repo_root=REPO,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_c0_retrieve.c0_retrieve_apps_rg",
        lambda **_: _pass_fec(),
    )
    result = invoke_section_spine_c0_retrieve(
        front_spine=spine,
        section_id="executive_summary",
    )
    assert result.receipt["proof_pool_shim_skipped"] is True
    assert result.receipt["graph_lane_na_ref"] == C0_GRAPH_LANE_NA_REF
    assert result.receipt["canonical_c0_2_dense_claimed"] is True

    bridge = build_spine_c0_fec_artifact(
        section_id="executive_summary",
        front_spine=spine,
        pool=_minimal_pool(),
    )
    assert bridge.bridge_doc["fec_shape_only"] is False
    assert bridge.bridge_doc["binding_kind"] == "spine_c0_retrieve_apps_rg"


def test_build_spine_fec_uses_retrieve_not_proof_pool_shim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spine = build_section_front_spine_from_args(
        section_id="executive_summary",
        args=_args(),
        repo_root=REPO,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_c0_retrieve.c0_retrieve_apps_rg",
        lambda **_: _pass_fec(),
    )
    bridge = build_spine_c0_fec_artifact(
        section_id="executive_summary",
        front_spine=spine,
        pool=_minimal_pool(),
    )
    assert bridge.bridge_doc.get("proof_pool_shim_only") is False
    assert bridge.bridge_doc.get("spine_c0_retrieve_receipt")


def test_graph_lane_deferral_doc_exists() -> None:
    doc = Path("apps_rg/config/domain_contract/C0_graph_lane_deferral.md")
    assert doc.is_file()
    text = doc.read_text(encoding="utf-8")
    assert C0_GRAPH_LANE_NA_REF in text
    assert "STOP AS EVIDENCE GAP" in text


def test_merge_spine_fec_sets_canonical_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spine = build_section_front_spine_from_args(
        section_id="executive_summary",
        args=_args(),
        repo_root=REPO,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.spine.section_c0_retrieve.c0_retrieve_apps_rg",
        lambda **_: _pass_fec(),
    )
    result = invoke_section_spine_c0_retrieve(
        front_spine=spine,
        section_id="executive_summary",
    )
    merged = merge_spine_fec_into_bridge_doc(
        {"proof_source": "proof_pool", "fec_bridge_mode": "spine_c0_fec_compose"},
        spine=result,
        pool_allowed_fact_ids=["bul_acme_001"],
    )
    assert merged["canonical_c0_5_claimed"] is True
    assert merged["fec_shape_only"] is False
