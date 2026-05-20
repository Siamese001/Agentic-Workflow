"""W3: SelectedRoleFactSet proof pools adopted per section lane (structural + offline stub)."""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

import pytest

from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

from tests._apps_contract.contract_harness_paths import harness_run

REPO = Path(__file__).resolve().parents[2]


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


def _stub_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")


@pytest.fixture
def srfs_all_sections(tmp_path: Path) -> Path:
    doc = _srfs_doc(
        "w3_multi_slice",
        {
            "headline": [_high_row("bul_head_w3_001")],
            "executive_summary": [_high_row("bul_exec_w3_001")],
            "unify_bullets": [_high_row("bul_unify_w3_001")],
            "unify_narrative": [_high_row("bul_unify_w3_narr_001")],
            "ibm_bullets": [_high_row("bul_ibm_w3_001")],
            "ibm_narrative": [_high_row("bul_ibm_w3_narr_001")],
            "competencies": [_high_row("bul_comp_w3_001")],
        },
    )
    return _write_srfs(tmp_path / "srfs_all.json", doc)


@pytest.mark.parametrize("section", GENERATED_LANES)
def test_proof_pool_metadata_for_section_offline_stub(
    section: str,
    srfs_all_sections: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _stub_env(monkeypatch)
    u = uuid.uuid4().hex[:12]
    run_dir = harness_run(f"_w3_contract_{u}", section)
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
        from apps_rg.runtime.sections.executive_summary_lane_api import build_parser
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

    payload = json.loads((run_dir / "runtime_payload.json").read_text(encoding="utf-8"))
    meta = payload.get("proof_pool_metadata") or {}
    assert meta.get("proof_pool_type") == "selected_role_fact_set"
    assert meta.get("selected_role_fact_set_used") is True
    assert meta.get("fallback_used") is False
    assert meta.get("srfs_section_id") == section
    assert meta.get("candidate_fact_pool_count") == 1
    ids = {str(x).split("_metric_", 1)[0] for x in (payload.get("allowed_fact_ids") or [])}
    if section == "headline":
        assert "bul_head_w3_001" in ids
        assert "bul_exec_w3_001" not in ids


def test_headline_fails_closed_when_slice_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """SRFS supplied without headline slice — must not fall back to base pool."""
    _stub_env(monkeypatch)
    doc = {
        "selection_id": "w3_headline_missing",
        "selected_facts_by_section": {"executive_summary": [_high_row("bul_exec_only")]},
        "blocked_facts": [],
        "facts_requiring_human_confirmation": [],
        "unsupported_jd_needs": [],
        "confidence_policy": "HIGH-only test fixture",
        "candidate_not_canonical_assertion": True,
        "no_jd_fact_minting_assertion": True,
    }
    p = _write_srfs(tmp_path / "srfs_no_headline.json", doc)
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
        selected_role_fact_set=str(p),
    )
    run_under = harness_run(f"_w3_contract_{uuid.uuid4().hex[:12]}", "headline_fail")
    run_under.mkdir(parents=True, exist_ok=True)
    with pytest.raises(ValueError, match="headline"):
        run_headline_execution(args, artifact_dir_override=run_under, print_output=False)


def test_cross_slice_headline_excludes_executive_only_fact(tmp_path: Path) -> None:
    from apps_rg.runtime.sections.selected_role_fact_set import resolve_srfs_section_proof_bundle

    doc = _srfs_doc(
        "cross",
        {
            "headline": [_high_row("only_in_headline")],
            "executive_summary": [_high_row("only_in_exec")],
        },
    )
    p = _write_srfs(tmp_path / "cross.json", doc)
    _, _, allowed_h, _ = resolve_srfs_section_proof_bundle(p, "headline")
    assert "only_in_headline" in allowed_h
    assert "only_in_exec" not in allowed_h


def test_legacy_base_pool_metadata_when_no_srfs_headline(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _stub_env(monkeypatch)
    from apps_rg.runtime.sections.headline_lane import build_headline_lane_args, run_headline_execution

    u = uuid.uuid4().hex[:12]
    run_dir = harness_run(f"_w3_contract_{u}", "headline_legacy")
    run_dir.mkdir(parents=True, exist_ok=True)
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
    payload = json.loads((run_dir / "runtime_payload.json").read_text(encoding="utf-8"))
    meta = payload.get("proof_pool_metadata") or {}
    assert meta.get("selected_role_fact_set_used") is False
    assert meta.get("proof_pool_type") in ("broad_skills_ledger", "base_resume_fallback")
    if meta.get("proof_pool_type") == "broad_skills_ledger":
        assert meta.get("broad_skills_ledger_used") is True
        assert meta.get("fallback_used") is False
    else:
        assert meta.get("fallback_used") is True
