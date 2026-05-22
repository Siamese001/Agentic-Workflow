"""W6: normalized SRFS reporting fields on section_metric_receipt.json for all generated lanes."""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

import pytest

from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.product_evidence_authority import build_evidence_authority
from apps_rg.runtime.sections.selected_role_fact_set import (
    SRFS_SLICE_SOURCE_FACT_GATE_BY_SECTION,
    graph_only_proof_pool_metadata,
    normalized_srfs_section_reporting_fields,
    srfs_proof_pool_metadata,
)
from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates

from tests._apps_contract.contract_harness_paths import harness_run
from apps_rg.runtime.validators.unify_bullets_x2 import run_unify_bullets_x2_gates
from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

REPO = Path(__file__).resolve().parents[2]

W6_FIELDS = (
    "proof_pool_type",
    "selected_role_fact_set_used",
    "srfs_section_id",
    "candidate_fact_pool_count",
    "allowed_fact_ids_count",
    "required_fact_ids_count",
    "claim_ledger_union_matches_required_fact_ids",
    "out_of_slice_fact_ids",
    "fallback_used",
    "fallback_reason",
    "x2_srfs_gate_status",
    "srfs_allowed_fact_ids_count",
    "full_resume_srfs_supported",
)


def _high_row(candidate_fact_id: str, *, claim_text: str = "Claim text for fixture.") -> dict:
    return {
        "candidate_fact_id": candidate_fact_id,
        "confidence": "HIGH",
        "claim_text": claim_text,
        "metric_values": [],
    }


def _srfs_doc(selection_id: str, sections: dict[str, list[dict]]) -> dict:
    out = {
        "selection_id": selection_id,
        "selected_facts_by_section": dict(sections),
        "blocked_facts": [],
        "facts_requiring_human_confirmation": [],
        "unsupported_jd_needs": [],
        "confidence_policy": "HIGH-only test fixture",
        "candidate_not_canonical_assertion": True,
        "no_jd_fact_minting_assertion": True,
    }
    for k in SECTION_KEYS:
        out["selected_facts_by_section"].setdefault(k, [])
    return out


def _write_srfs(path: Path, doc: dict) -> Path:
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return path


def _graph_proof_pool_metadata(section_id: str, *, allowed_count: int = 2) -> dict:
    meta = graph_only_proof_pool_metadata(
        section_id=section_id,
        candidate_fact_pool_count=1,
        allowed_fact_ids_count=allowed_count,
        graph_ref="artifacts/apps_rg/fact_inventory/augmented_skills_graph.json",
        legacy_ledger_ref="artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger.json",
    )
    meta["evidence_authority"] = build_evidence_authority(
        graph_ref=meta["graph_ref"],
        ledger_ref=meta["legacy_skills_ledger_ref"],
        skills_authority_status="PASS",
    )
    meta["selection_scope"] = {"is_proof_authority": False}
    return meta


def _stub_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")


@pytest.fixture
def srfs_all_sections(tmp_path: Path) -> Path:
    doc = _srfs_doc(
        "w6_multi",
        {
            "headline": [_high_row("bul_head_w6_001")],
            "executive_summary": [_high_row("bul_exec_w6_001")],
            "unify_bullets": [_high_row("bul_unify_w6_001")],
            "unify_narrative": [_high_row("bul_unify_w6_narr_001")],
            "ibm_bullets": [_high_row("bul_ibm_w6_001")],
            "ibm_narrative": [_high_row("bul_ibm_w6_narr_001")],
            "competencies": [_high_row("bul_comp_w6_001")],
        },
    )
    return _write_srfs(tmp_path / "srfs_w6.json", doc)


@pytest.mark.skip(reason="SRFS JSON CLI lane entry removed (legacy purge D2/D3)")
@pytest.mark.parametrize("section", GENERATED_LANES)
def test_section_metric_receipt_w6_srfs_mode_all_fields(
    section: str,
    srfs_all_sections: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _stub_env(monkeypatch)
    u = uuid.uuid4().hex[:12]
    run_dir = harness_run(f"_w6_srfs_{u}", section)
    run_dir.mkdir(parents=True, exist_ok=True)
    srfs = str(srfs_all_sections)

    if section == "headline":
        from apps_rg.runtime.sections.headline_lane import build_headline_lane_args, run_headline_execution

        args = build_headline_lane_args(
            provider="qwen_vllm",
            temperature=0.55,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs,
        )
        run_headline_execution(args, artifact_dir_override=run_dir, print_output=False)
    elif section == "executive_summary":
        from apps_rg.runtime.sections.executive_summary_lane import run_executive_summary_execution
        from apps_rg.runtime.sections.executive_summary_lane import build_parser
        from tests._apps_contract.test_exec_summary_section_pipeline import _tag_exec_summary_provider_resolution

        args = build_parser().parse_args(
            [
                "--provider",
                "mock",
                "--mock-judges",
                "--allow-non-allow-exit-zero",
            ]
        )
        _tag_exec_summary_provider_resolution(args)
        args.allow_test_mock_judges = True
        args.selected_role_fact_set = srfs
        run_executive_summary_execution(args, artifact_dir_override=run_dir)
    elif section == "unify_bullets":
        from apps_rg.runtime.sections.unify_bullets_lane import run_unify_bullets_execution

        args = argparse.Namespace(
            provider="qwen_vllm",
            temperature=0.45,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs,
        )
        run_unify_bullets_execution(args, artifact_dir_override=run_dir)
    elif section == "unify_narrative":
        from apps_rg.runtime.sections.unify_narrative_lane import run_unify_narrative_execution

        args = argparse.Namespace(
            provider="mock",
            temperature=0.32,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs,
        )
        run_unify_narrative_execution(args, artifact_dir_override=run_dir)
    elif section == "ibm_bullets":
        from apps_rg.runtime.sections.ibm_bullets_lane import run_ibm_bullets_execution

        args = argparse.Namespace(
            provider="qwen_vllm",
            temperature=0.45,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs,
        )
        run_ibm_bullets_execution(args, artifact_dir_override=run_dir)
    elif section == "ibm_narrative":
        from apps_rg.runtime.sections.ibm_narrative_lane import run_ibm_narrative_lane_execution

        args = argparse.Namespace(
            provider="mock",
            temperature=0.35,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs,
        )
        run_ibm_narrative_lane_execution(args, artifact_dir_override=run_dir)
    elif section == "competencies":
        from apps_rg.runtime.sections.competencies_lane import build_competencies_lane_args, run_competencies_lane_execution

        args = build_competencies_lane_args(
            provider="qwen_vllm",
            temperature=0.45,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set=srfs,
        )
        run_competencies_lane_execution(args, artifact_dir_override=run_dir)
    else:
        raise AssertionError(section)

    receipt_path = run_dir / "section_metric_receipt.json"
    assert receipt_path.is_file(), f"missing section_metric_receipt for {section}"
    rec = json.loads(receipt_path.read_text(encoding="utf-8"))
    for k in W6_FIELDS:
        assert k in rec, f"{section} missing {k}"
    assert rec["selected_role_fact_set_used"] is True
    assert rec["proof_pool_type"] == "selected_role_fact_set"
    assert rec["fallback_used"] is False
    assert rec["fallback_reason"] == ""
    assert rec["srfs_section_id"] == section
    assert rec["x2_srfs_gate_status"] in ("PASS", "FAIL", "UNKNOWN")
    assert isinstance(rec["out_of_slice_fact_ids"], list)
    assert rec["full_resume_srfs_supported"] is False


@pytest.mark.skip(reason="SRFS JSON CLI lane entry removed (legacy purge D2/D3)")
@pytest.mark.parametrize("section", ("headline", "unify_bullets", "competencies"))
def test_section_metric_receipt_w6_no_srfs_base_pool(
    section: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _stub_env(monkeypatch)
    u = uuid.uuid4().hex[:12]
    run_dir = harness_run(f"_w6_nosrfs_{u}", section)
    run_dir.mkdir(parents=True, exist_ok=True)

    if section == "headline":
        from apps_rg.runtime.sections.headline_lane import build_headline_lane_args, run_headline_execution

        args = build_headline_lane_args(
            provider="qwen_vllm",
            temperature=0.55,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set="",
        )
        run_headline_execution(args, artifact_dir_override=run_dir, print_output=False)
    elif section == "unify_bullets":
        from apps_rg.runtime.sections.unify_bullets_lane import run_unify_bullets_execution

        args = argparse.Namespace(
            provider="qwen_vllm",
            temperature=0.45,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set="",
        )
        run_unify_bullets_execution(args, artifact_dir_override=run_dir)
    elif section == "competencies":
        from apps_rg.runtime.sections.competencies_lane import build_competencies_lane_args, run_competencies_lane_execution

        args = build_competencies_lane_args(
            provider="qwen_vllm",
            temperature=0.45,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title="T",
            target_company="C",
            jd_text="J",
            briefing="B",
            selected_role_fact_set="",
        )
        run_competencies_lane_execution(args, artifact_dir_override=run_dir)
    else:
        raise AssertionError(section)

    rec = json.loads((run_dir / "section_metric_receipt.json").read_text(encoding="utf-8"))
    assert rec["selected_role_fact_set_used"] is False
    assert rec["proof_pool_type"] in ("broad_skills_ledger", "base_resume_fallback")
    if rec["proof_pool_type"] == "broad_skills_ledger":
        assert rec.get("fallback_used") is False
    else:
        assert rec["fallback_used"] is True
        assert rec["fallback_reason"]
        assert "no" in rec["fallback_reason"].lower() or "selected" in rec["fallback_reason"].lower()
    assert rec["x2_srfs_gate_status"] == "NOT_APPLICABLE"
    assert rec["out_of_slice_fact_ids"] == []
    assert rec["full_resume_srfs_supported"] is False


def test_w6_normalizer_unify_bullets_fail_out_of_slice() -> None:
    pp = _graph_proof_pool_metadata("unify_bullets")
    allowed = {"bul_unify_001"}
    from tests._apps_contract.test_apps_rg_srfs_w4_x2_slice_gates import _minimal_bullets_stub

    bad_id = "bul_exec_cross_w6"
    bullets, ledger, po = _minimal_bullets_stub("bul_unify_")
    ledger[0] = {"claim_text": ledger[0]["claim_text"], "source_fact_ids": [bad_id]}
    bullets[0]["source_fact_ids"] = [bad_id]
    x2 = [g.to_dict() for g in run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=po,
        claim_ledger=ledger,
        allowed_fact_ids=allowed,
        jd_text="",
        runtime_generation_status="MOCKED",
        x1d_judges=[],
        srfs_source_fact_slice_gate_active=True,
    )]
    gid = "x2_unify_bullets_active_proof_pool_source_fact_ids"
    assert {g["gate_id"]: g for g in x2}[gid]["pass"] is False
    rep = normalized_srfs_section_reporting_fields(
        section_id="unify_bullets",
        runtime_payload={"proof_pool_metadata": pp},
        x2_gates=x2,
        selected_fact_plan={"required_fact_ids": [bad_id]},
        claim_ledger=ledger,
    )
    assert rep["x2_srfs_gate_status"] == "NOT_APPLICABLE"
    assert rep.get("x2_active_proof_pool_gate_status") == "FAIL"
    assert bad_id in rep["out_of_slice_fact_ids"]


def test_w6_normalizer_unify_narrative_fail_out_of_slice() -> None:
    pp = _graph_proof_pool_metadata("unify_narrative")
    allowed = {"bul_unify_001"}
    bad_id = "unify_narrative_base_001"
    x2 = [
        g.to_dict()
        for g in run_unify_narrative_x2_gates(
            narrative_sentence="Single sentence about Unify Consulting platforms for enterprise.",
            parsed_output={
                "narrative_sentence": "x",
                "claim_ledger": [],
                "jd_alignment": {
                    "selected_jd_themes": ["t"],
                    "targeting_rationale": "r",
                    "jd_used_as_proof": False,
                    "briefing_used_as_proof": False,
                    "selected_briefing_themes": [],
                },
                "gap_notes": [],
                "change_log": [],
                "self_check": {},
            },
            claim_ledger=[{"claim_text": "Led platform work.", "source_fact_ids": [bad_id]}],
            jd_text="enterprise",
            briefing_text="",
            runtime_generation_status="MOCKED",
            companion_bullet_texts=None,
            x1d_judges=[],
            allowed_fact_ids=allowed,
            srfs_source_fact_slice_gate_active=True,
        )
    ]
    gid = "x2_unify_narrative_active_proof_pool_source_fact_ids"
    assert {g["gate_id"]: g for g in x2}[gid]["pass"] is False
    rep = normalized_srfs_section_reporting_fields(
        section_id="unify_narrative",
        runtime_payload={"proof_pool_metadata": pp},
        x2_gates=x2,
        selected_fact_plan={"required_fact_ids": [bad_id]},
        claim_ledger=[{"claim_text": "Led platform work.", "source_fact_ids": [bad_id]}],
    )
    assert rep["x2_srfs_gate_status"] == "NOT_APPLICABLE"
    assert rep.get("x2_active_proof_pool_gate_status") == "FAIL"
    assert bad_id in rep["out_of_slice_fact_ids"]


def test_w6_normalizer_competencies_fail_out_of_slice() -> None:
    pp = _graph_proof_pool_metadata("competencies")
    allowed = {"bul_comp_001"}
    bad_id = "bul_bad_outside_w6"
    competencies = []
    for i in range(8):
        competencies.append(
            {
                "category_label": f"Category {i}",
                "terms": [
                    {
                        "text": f"skill {i}a",
                        "source_fact_id": "bul_comp_001",
                        "source_fact_ids": ["bul_comp_001"],
                    },
                    {
                        "text": f"skill {i}b",
                        "source_fact_id": "bul_comp_001",
                        "source_fact_ids": ["bul_comp_001"],
                    },
                ],
                "source_fact_ids": ["bul_comp_001"],
            }
        )
    competencies[0]["terms"][0]["source_fact_ids"] = [bad_id]
    competencies[0]["terms"][0]["source_fact_id"] = bad_id
    po = {
        "competencies": competencies,
        "claim_ledger": [{"claim_text": "c", "source_fact_ids": ["bul_comp_001"]} for _ in range(3)],
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False, "briefing_used_as_proof": False},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    cl = [{"claim_text": "c", "source_fact_ids": ["bul_comp_001"]} for _ in range(3)]
    x2 = [
        g.to_dict()
        for g in run_competencies_x2_gates(
            competencies=competencies,
            parsed_output=po,
            claim_ledger=cl,
            jd_text="",
            briefing_text="",
            bullet_texts_lower=[],
            resume_support_blob="bul_comp_001 skill",
            allowed_fact_ids=allowed,
            runtime_generation_status="MOCKED",
            x1d_judges=[],
            srfs_source_fact_slice_gate_active=True,
        )
    ]
    gid = "x2_competencies_active_proof_pool_source_fact_ids"
    assert {g["gate_id"]: g for g in x2}[gid]["pass"] is False
    rep = normalized_srfs_section_reporting_fields(
        section_id="competencies",
        runtime_payload={"proof_pool_metadata": pp},
        x2_gates=x2,
        selected_fact_plan={"required_fact_ids": ["bul_comp_001"]},
        claim_ledger=cl,
    )
    assert rep["x2_srfs_gate_status"] == "NOT_APPLICABLE"
    assert rep.get("x2_active_proof_pool_gate_status") == "FAIL"
    assert bad_id in rep["out_of_slice_fact_ids"]


def test_w6_normalizer_pass_path_matches_gate_envelope() -> None:
    pp = srfs_proof_pool_metadata(section_id="headline", candidate_fact_pool_count=1, allowed_fact_ids_count=2)
    x2 = [
        {
            "gate_id": "x2_headline_active_proof_pool_source_fact_ids",
            "pass": True,
            "observed_value": {"out_of_slice_fact_ids": [], "srfs_allowed_fact_ids_count": 2},
        }
    ]
    r = normalized_srfs_section_reporting_fields(
        section_id="headline",
        runtime_payload={"proof_pool_metadata": pp},
        x2_gates=x2,
        selected_fact_plan={"required_fact_ids": ["a"]},
        claim_ledger=[{"claim_text": "x", "source_fact_ids": ["a"]}],
    )
    assert r["x2_srfs_gate_status"] == "NOT_APPLICABLE"
    assert r.get("x2_active_proof_pool_gate_status") == "PASS"
    assert r["selected_role_fact_set_used"] is False
    assert r["proof_pool_type"] == "augmented_skills_graph"
    assert r["out_of_slice_fact_ids"] == []
