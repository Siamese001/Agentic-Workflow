"""W3 (revised): generated lanes adopt augmented_skills_graph proof pool only."""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

from tests._apps_contract.contract_harness_paths import harness_run

REPO = Path(__file__).resolve().parents[2]
LEDGER = default_ledger_path(REPO)


def _stub_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")


def _lane_args(provider: str = "qwen_vllm") -> argparse.Namespace:
    return argparse.Namespace(
        provider=provider,
        temperature=0.45,
        x1d_judges="gemini_pro",
        mock_judges=True,
        allow_test_mock_judges=True,
        allow_non_allow_exit_zero=False,
        target_title="VP Engineering",
        target_company="Acme Corp",
        jd_text="Lead platform engineering.",
        briefing="Emphasize delivery and governance.",
        base_resume_ref="",
    )


@pytest.mark.skipif(not LEDGER.is_file(), reason="master candidate fact ledger missing")
@pytest.mark.parametrize("section", GENERATED_LANES)
def test_proof_pool_metadata_for_section_offline_stub(
    section: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_env(monkeypatch)
    run_dir = harness_run(f"_w3_graph_{uuid.uuid4().hex[:12]}", section)
    run_dir.mkdir(parents=True, exist_ok=True)
    args = _lane_args(provider="mock" if section in ("unify_narrative", "ibm_narrative") else "qwen_vllm")

    if section == "headline":
        from apps_rg.runtime.sections.headline_lane import build_headline_lane_args, run_headline_execution

        args = build_headline_lane_args(
            provider="qwen_vllm",
            temperature=0.55,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title=args.target_title,
            target_company=args.target_company,
            jd_text=args.jd_text,
            briefing=args.briefing,
        )
        run_headline_execution(args, artifact_dir_override=run_dir, print_output=False)
    elif section == "executive_summary":
        from apps_rg.runtime.sections.executive_summary_lane import run_executive_summary_execution
        from tests._apps_contract.test_exec_summary_section_pipeline import _harness_lane_namespace

        run_executive_summary_execution(
            _harness_lane_namespace(), artifact_dir_override=run_dir
        )
    elif section == "unify_bullets":
        from apps_rg.runtime.sections.unify_bullets_lane import run_unify_bullets_execution

        run_unify_bullets_execution(args, artifact_dir_override=run_dir)
    elif section == "unify_narrative":
        from apps_rg.runtime.sections.unify_narrative_lane import run_unify_narrative_execution

        run_unify_narrative_execution(args, artifact_dir_override=run_dir)
    elif section == "ibm_bullets":
        from apps_rg.runtime.sections.ibm_bullets_lane import run_ibm_bullets_execution

        run_ibm_bullets_execution(args, artifact_dir_override=run_dir)
    elif section == "ibm_narrative":
        from apps_rg.runtime.sections.ibm_narrative_lane import run_ibm_narrative_lane_execution

        run_ibm_narrative_lane_execution(args, artifact_dir_override=run_dir)
    elif section == "competencies":
        from apps_rg.runtime.sections.competencies_lane import (
            build_competencies_lane_args,
            run_competencies_lane_execution,
        )

        args = build_competencies_lane_args(
            provider="qwen_vllm",
            temperature=0.45,
            x1d_judges="gemini_pro",
            mock_judges=True,
            allow_test_mock_judges=True,
            target_title=args.target_title,
            target_company=args.target_company,
            jd_text=args.jd_text,
            briefing=args.briefing,
        )
        run_competencies_lane_execution(args, artifact_dir_override=run_dir)

    payload = json.loads((run_dir / "runtime_payload.json").read_text(encoding="utf-8"))
    meta = payload.get("proof_pool_metadata") or {}
    assert meta.get("proof_pool_type") == "augmented_skills_graph", section
    assert meta.get("skills_authority_status") == "PASS", section
    assert meta.get("base_resume_claim_authority") is False
    assert meta.get("fallback_used") is False
    assert payload.get("allowed_fact_ids")


def test_headline_fail_closed_when_graph_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Graph BLOCKED must not fall back to base-resume claim pool."""
    _stub_env(monkeypatch)
    monkeypatch.setattr(
        "apps_rg.runtime.proof_pool_resolver.resolve_augmented_skills_graph_authority",
        lambda **_: {"skills_authority_status": "BLOCKED", "skills_authority_block_reason": "test"},
    )
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
    )
    run_under = harness_run(f"_w3_blocked_{uuid.uuid4().hex[:12]}", "headline_fail")
    run_under.mkdir(parents=True, exist_ok=True)
    with pytest.raises(ValueError, match="graph-skills proof pool BLOCKED"):
        run_headline_execution(args, artifact_dir_override=run_under, print_output=False)
