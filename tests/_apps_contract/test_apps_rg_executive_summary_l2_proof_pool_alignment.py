"""Executive summary L2 generation aligned with shared proof-pool resolver (X2 + usage ledger)."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_BASE_RESUME_FALLBACK,
    PROOF_SOURCE_BROAD_SKILLS_LEDGER,
    PROOF_SOURCE_SRFS,
    resolve_section_proof_pool,
)
from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
    evaluate_proof_pool_source_fact_gate,
    validate_active_proof_pool_source_fact_ids,
)

REPO = Path(__file__).resolve().parents[2]
LEDGER_PATH = default_ledger_path(REPO)


def _high_row(candidate_fact_id: str) -> dict:
    return {
        "candidate_fact_id": candidate_fact_id,
        "confidence": "HIGH",
        "claim_text": "Fixture executive-summary claim for proof pool alignment.",
        "metric_values": [],
        "capability_tags": ["leadership"],
    }


def _srfs_doc(rows: list[dict]) -> dict:
    from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS

    doc = {
        "selection_id": "exec_l2_pool_test",
        "selected_facts_by_section": {k: [] for k in SECTION_KEYS},
        "blocked_facts": [],
        "facts_requiring_human_confirmation": [],
        "unsupported_jd_needs": [],
    }
    doc["selected_facts_by_section"]["executive_summary"] = rows
    return doc


@pytest.mark.skipif(not LEDGER_PATH.is_file(), reason="master ledger missing")
def test_executive_summary_l2_resolver_uses_broad_skills_ledger_without_srfs() -> None:
    pool = resolve_section_proof_pool(
        section="executive_summary",
        repo_root=REPO,
        target_company="Acme",
        target_title="SVP Engineering",
        jd_text="Lead platform programs.",
        briefing_text="Governed AI delivery.",
    )
    assert pool.proof_source == PROOF_SOURCE_BROAD_SKILLS_LEDGER
    assert pool.broad_skills_ledger_present is True
    assert pool.srfs_present is False
    assert pool.base_resume_fallback_used is False
    fid = next(iter(pool.allowed_fact_ids), "")
    assert fid
    payload = {
        "run_id": "exec_pool_unit",
        "allowed_fact_ids": list(pool.allowed_fact_ids_ordered),
        "proof_pool_metadata": pool.proof_pool_metadata,
        "selected_fact_plan": pool.selected_fact_plan,
        "target_title": "SVP",
        "target_company": "Acme",
        "jd_text": "jd",
        "briefing": "brief",
    }
    compiled = compile_executive_summary_prompt(payload, run_id="exec_pool_unit")
    content = compiled.artifact.messages[-1]["content"]
    assert "CLAIM SUPPORT POOL (BROAD SKILLS LEDGER)" in content
    assert fid in content
    assert "TARGETING_INPUT" in content


def test_executive_summary_l2_resolver_uses_srfs_when_supplied(tmp_path: Path) -> None:
    srfs_path = tmp_path / "srfs_exec.json"
    srfs_path.write_text(
        json.dumps(_srfs_doc([_high_row("bul_exec_srfs_l2_001")])),
        encoding="utf-8",
    )
    pool = resolve_section_proof_pool(
        section="executive_summary",
        selected_role_fact_set_path=str(srfs_path),
        repo_root=REPO,
    )
    assert pool.proof_source == PROOF_SOURCE_SRFS
    assert pool.srfs_present is True
    payload = {
        "run_id": "exec_srfs_unit",
        "allowed_fact_ids": list(pool.allowed_fact_ids_ordered),
        "proof_pool_metadata": pool.proof_pool_metadata,
        "selected_fact_plan": pool.selected_fact_plan,
        "srfs_integration": {"artifact_path_resolved": str(srfs_path)},
        "target_title": "SVP",
        "target_company": "Acme",
        "jd_text": "jd",
        "briefing": "brief",
    }
    compiled = compile_executive_summary_prompt(payload, run_id="exec_srfs_unit")
    content = compiled.artifact.messages[-1]["content"]
    assert "CLAIM SUPPORT POOL (SRFS)" in content
    assert "bul_exec_srfs_l2_001" in content


def test_executive_summary_l2_explicit_base_fallback_when_ledger_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing_ledger.json"
    pool = resolve_section_proof_pool(
        section="executive_summary",
        broad_skills_ledger_path=str(missing),
        repo_root=REPO,
    )
    assert pool.proof_source == PROOF_SOURCE_BASE_RESUME_FALLBACK
    assert pool.base_resume_fallback_used is True
    fid = next(iter(pool.allowed_fact_ids), "")
    assert fid
    ok, receipt, _ = validate_active_proof_pool_source_fact_ids(
        section="executive_summary",
        collected_ids=[fid],
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
        proof_pool_ref=pool.proof_pool_ref,
        proof_pool_digest=pool.proof_pool_digest,
    )
    assert ok is True
    assert receipt["proof_source"] == PROOF_SOURCE_BASE_RESUME_FALLBACK
    compiled = compile_executive_summary_prompt(
        {
            "run_id": "exec_fallback_unit",
            "allowed_fact_ids": list(pool.allowed_fact_ids_ordered),
            "proof_pool_metadata": pool.proof_pool_metadata,
            "selected_fact_plan": pool.selected_fact_plan,
            "target_title": "SVP",
            "target_company": "Acme",
            "jd_text": "jd",
            "briefing": "brief",
        },
        run_id="exec_fallback_unit",
    )
    assert "CLAIM SUPPORT POOL (BASE RESUME FALLBACK)" in compiled.artifact.messages[-1]["content"]


@pytest.mark.skipif(not LEDGER_PATH.is_file(), reason="master ledger missing")
def test_executive_summary_rejects_jd_briefing_and_random_ids() -> None:
    pool = resolve_section_proof_pool(section="executive_summary", repo_root=REPO)
    ok, receipt, _ = validate_active_proof_pool_source_fact_ids(
        section="executive_summary",
        collected_ids=["JD_ONLY", "briefing_research_001", "totally_unknown_exec_xyz"],
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
    )
    assert ok is False
    assert receipt["jd_or_briefing_ids_rejected"]
    assert "totally_unknown_exec_xyz" in receipt["unsupported_source_fact_ids"]


def test_mock_executive_summary_lane_digest_and_receipt_match_usage_ledger(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    from apps_rg.runtime.dispatch.executive_summary_dispatch import build_parser
    from apps_rg.runtime.sections.executive_summary_lane import run_executive_summary_execution
    from tests._apps_contract.test_exec_summary_section_pipeline import _tag_exec_summary_provider_resolution

    run_dir = REPO / "artifacts" / "apps_rg" / "runtime_proofs" / f"_exec_l2_pool_{uuid.uuid4().hex[:10]}"
    run_dir.mkdir(parents=True, exist_ok=True)
    args = build_parser().parse_args(
        ["--provider", "mock", "--mock-judges", "--allow-non-allow-exit-zero"]
    )
    _tag_exec_summary_provider_resolution(args)
    args.allow_test_mock_judges = True
    run_executive_summary_execution(args, artifact_dir_override=run_dir)

    usage = json.loads((run_dir / "section_input_usage_ledger.json").read_text(encoding="utf-8"))
    receipt = json.loads((run_dir / "x2_source_fact_pool_receipt.json").read_text(encoding="utf-8"))
    runtime = json.loads((run_dir / "runtime_payload.json").read_text(encoding="utf-8"))
    compiled = (run_dir / "compiled_prompt.txt").read_text(encoding="utf-8")
    prompt_artifact = json.loads((run_dir / "compiled_prompt_artifact.json").read_text(encoding="utf-8"))

    assert usage.get("proof_source") == receipt.get("proof_source")
    assert usage.get("proof_pool_digest") == receipt.get("proof_pool_digest")
    assert usage.get("non_proof_inputs") == ["jd_title_company", "briefing"]
    assert prompt_artifact.get("proof_pool_digest") == usage.get("proof_pool_digest")
    assert "CLAIM SUPPORT POOL" in compiled
    pp_type = str((runtime.get("proof_pool_metadata") or {}).get("proof_pool_type") or "")
    if pp_type == "broad_skills_ledger":
        assert "BROAD SKILLS LEDGER" in compiled
    elif pp_type == "selected_role_fact_set":
        assert "(SRFS)" in compiled
    else:
        assert "BASE RESUME FALLBACK" in compiled
    l2 = json.loads((run_dir / "l2_output.json").read_text(encoding="utf-8"))
    for claim in l2.get("claim_ledger") or []:
        for tok in claim.get("source_fact_ids") or []:
            assert str(tok) not in ("JD_ONLY", "briefing_research_001", "target_company_acme")
    pool = resolve_section_proof_pool(section="executive_summary", repo_root=REPO)
    if pool.proof_source == PROOF_SOURCE_BROAD_SKILLS_LEDGER:
        fid = next(iter(pool.allowed_fact_ids), "")
        ok, _, _ = evaluate_proof_pool_source_fact_gate(
            section_id="executive_summary",
            collected_ids=[fid],
            allowed_fact_ids=pool.allowed_fact_ids,
            proof_pool_metadata=pool.proof_pool_metadata,
            proof_pool_ref=pool.proof_pool_ref,
            proof_pool_digest=pool.proof_pool_digest,
        )
        assert ok is True
