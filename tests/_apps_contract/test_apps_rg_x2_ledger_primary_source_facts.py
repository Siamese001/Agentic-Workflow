"""Contract: ledger-primary proof pools pass X2 source_fact_id membership gates."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_BROAD_SKILLS_LEDGER,
    PROOF_SOURCE_SRFS,
    resolve_section_proof_pool,
)
from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
    evaluate_proof_pool_source_fact_gate,
    proof_pool_x2_gate_id,
    validate_active_proof_pool_source_fact_ids,
)

from tests._apps_contract.contract_harness_paths import harness_run

REPO = Path(__file__).resolve().parents[2]
LEDGER_PATH = default_ledger_path(REPO)


def _high_row(candidate_fact_id: str) -> dict:
    return {
        "candidate_fact_id": candidate_fact_id,
        "confidence": "HIGH",
        "claim_text": "Fixture claim for proof pool validation.",
        "metric_values": [],
        "capability_tags": ["leadership"],
    }


def _srfs_doc(section: str, rows: list[dict]) -> dict:
    from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS

    doc = {
        "selection_id": "x2_ledger_test",
        "selected_facts_by_section": {k: [] for k in SECTION_KEYS},
        "blocked_facts": [],
        "facts_requiring_human_confirmation": [],
        "unsupported_jd_needs": [],
    }
    doc["selected_facts_by_section"][section] = rows
    return doc


@pytest.mark.skipif(not LEDGER_PATH.is_file(), reason="master ledger missing")
def test_competencies_accepts_valid_ledger_primary_source_fact_ids() -> None:
    pool = resolve_section_proof_pool(section="competencies", repo_root=REPO)
    assert pool.proof_source == PROOF_SOURCE_BROAD_SKILLS_LEDGER
    fid = str(pool.allowed_fact_ids_ordered[0] if pool.allowed_fact_ids_ordered else "")
    assert fid
    ok, receipt, _ = validate_active_proof_pool_source_fact_ids(
        section="competencies",
        collected_ids=[fid],
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
        proof_pool_ref=pool.proof_pool_ref,
        proof_pool_digest=pool.proof_pool_digest,
    )
    assert ok is True
    assert receipt["x2_source_fact_pool_status"] == "PASS"


def test_competencies_rejects_jd_and_briefing_as_proof() -> None:
    pool = resolve_section_proof_pool(section="competencies", repo_root=REPO)
    ok, receipt, _ = validate_active_proof_pool_source_fact_ids(
        section="competencies",
        collected_ids=["JD_ONLY", "briefing_research_001", "target_company_acme"],
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
    )
    assert ok is False
    assert receipt["jd_or_briefing_ids_rejected"]
    assert receipt["x2_source_fact_pool_status"] == "FAIL"


def test_competencies_rejects_random_unsupported_ids() -> None:
    pool = resolve_section_proof_pool(section="competencies", repo_root=REPO)
    ok, receipt, _ = validate_active_proof_pool_source_fact_ids(
        section="competencies",
        collected_ids=["totally_unknown_fact_xyz_999"],
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
    )
    assert ok is False
    assert "totally_unknown_fact_xyz_999" in receipt["unsupported_source_fact_ids"]


@pytest.mark.skipif(not LEDGER_PATH.is_file(), reason="master ledger missing")
def test_ibm_bullets_accepts_ledger_ids_from_active_pool() -> None:
    pool = resolve_section_proof_pool(section="ibm_bullets", repo_root=REPO)
    assert pool.proof_source == PROOF_SOURCE_BROAD_SKILLS_LEDGER
    fid = next(iter(pool.allowed_fact_ids), "")
    assert fid
    ok, _, _ = evaluate_proof_pool_source_fact_gate(
        section_id="ibm_bullets",
        collected_ids=[fid],
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
    )
    assert ok is True


@pytest.mark.skipif(not LEDGER_PATH.is_file(), reason="master ledger missing")
def test_unify_bullets_accepts_ledger_ids_from_active_pool() -> None:
    pool = resolve_section_proof_pool(section="unify_bullets", repo_root=REPO)
    assert pool.proof_source == PROOF_SOURCE_BROAD_SKILLS_LEDGER
    fid = next(iter(pool.allowed_fact_ids), "")
    ok, _, _ = evaluate_proof_pool_source_fact_gate(
        section_id="unify_bullets",
        collected_ids=[fid],
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
    )
    assert ok is True


def test_srfs_override_legacy_ids_still_pass(tmp_path: Path) -> None:
    srfs_path = tmp_path / "srfs.json"
    srfs_path.write_text(
        json.dumps(_srfs_doc("competencies", [_high_row("bul_comp_srfs_001")])),
        encoding="utf-8",
    )
    pool = resolve_section_proof_pool(
        section="competencies",
        selected_role_fact_set_path=str(srfs_path),
        repo_root=REPO,
    )
    assert pool.proof_source == PROOF_SOURCE_SRFS
    ok, receipt, _ = evaluate_proof_pool_source_fact_gate(
        section_id="competencies",
        collected_ids=["bul_comp_srfs_001"],
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
    )
    assert ok is True
    assert receipt["proof_source"] == PROOF_SOURCE_SRFS


def test_base_resume_fallback_ids_pass_only_when_fallback_active(tmp_path: Path) -> None:
    monkeypatch_ledger = tmp_path / "missing.json"
    pool = resolve_section_proof_pool(
        section="headline",
        broad_skills_ledger_path=str(monkeypatch_ledger),
        repo_root=REPO,
    )
    assert pool.proof_source == "base_resume_fallback"
    fid = next(iter(pool.allowed_fact_ids), "")
    assert fid
    ok, receipt, _ = validate_active_proof_pool_source_fact_ids(
        section="headline",
        collected_ids=[fid],
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
    )
    assert ok is True
    assert receipt["proof_source"] == "base_resume_fallback"
    bad, _, _ = validate_active_proof_pool_source_fact_ids(
        section="headline",
        collected_ids=[fid],
        allowed_fact_ids={"bul_unify_001"},
        proof_pool_metadata=pool.proof_pool_metadata,
    )
    assert bad is False


_REMAINING_LEDGER_SECTIONS = (
    "headline",
    "executive_summary",
    "unify_narrative",
    "ibm_narrative",
)

_JD_BRIEFING_RANDOM = ["JD_ONLY", "briefing_research_001", "target_company_acme", "totally_unknown_fact_xyz_999"]


@pytest.mark.skipif(not LEDGER_PATH.is_file(), reason="master ledger missing")
@pytest.mark.parametrize("section", _REMAINING_LEDGER_SECTIONS)
def test_remaining_lane_accepts_ledger_primary_source_fact_ids(section: str) -> None:
    pool = resolve_section_proof_pool(section=section, repo_root=REPO)
    assert pool.proof_source == PROOF_SOURCE_BROAD_SKILLS_LEDGER
    fid = next(iter(pool.allowed_fact_ids), "")
    assert fid
    ok, receipt, _ = evaluate_proof_pool_source_fact_gate(
        section_id=section,
        collected_ids=[fid],
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
        proof_pool_ref=pool.proof_pool_ref,
        proof_pool_digest=pool.proof_pool_digest,
    )
    assert ok is True
    assert receipt["x2_source_fact_pool_status"] == "PASS"
    assert receipt["proof_source"] == PROOF_SOURCE_BROAD_SKILLS_LEDGER


@pytest.mark.skipif(not LEDGER_PATH.is_file(), reason="master ledger missing")
@pytest.mark.parametrize("section", _REMAINING_LEDGER_SECTIONS)
def test_remaining_lane_rejects_jd_briefing_and_random_ids(section: str) -> None:
    pool = resolve_section_proof_pool(section=section, repo_root=REPO)
    ok, receipt, _ = validate_active_proof_pool_source_fact_ids(
        section=section,
        collected_ids=_JD_BRIEFING_RANDOM,
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
    )
    assert ok is False
    assert receipt["jd_or_briefing_ids_rejected"]
    assert "totally_unknown_fact_xyz_999" in receipt["unsupported_source_fact_ids"]
    assert receipt["x2_source_fact_pool_status"] == "FAIL"


def test_headline_srfs_override_preserves_legacy_gate_id(tmp_path: Path) -> None:
    srfs_path = tmp_path / "srfs_headline.json"
    srfs_path.write_text(
        json.dumps(_srfs_doc("headline", [_high_row("bul_head_srfs_001")])),
        encoding="utf-8",
    )
    pool = resolve_section_proof_pool(
        section="headline",
        selected_role_fact_set_path=str(srfs_path),
        repo_root=REPO,
    )
    assert pool.proof_source == PROOF_SOURCE_SRFS
    ok, receipt, _ = evaluate_proof_pool_source_fact_gate(
        section_id="headline",
        collected_ids=["bul_head_srfs_001"],
        allowed_fact_ids=pool.allowed_fact_ids,
        proof_pool_metadata=pool.proof_pool_metadata,
    )
    assert ok is True
    assert receipt["proof_source"] == PROOF_SOURCE_SRFS
    assert (
        proof_pool_x2_gate_id(
            "headline",
            proof_pool_metadata=pool.proof_pool_metadata,
            srfs_slice_gate_active=True,
        )
        == "x2_headline_source_fact_ids_within_srfs_slice"
    )


def test_mock_headline_lane_x2_receipt_matches_usage_ledger(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    from apps_rg.runtime.sections import headline_lane as lane

    args = lane.build_headline_lane_args(
        provider="qwen_vllm",
        temperature=lane.HEADLINE_TEMP_DEFAULT,
        x1d_judges="gemini_pro",
        mock_judges=True,
        allow_test_mock_judges=True,
        target_title="SVP Engineering",
        target_company="Synthetic Enterprise Corp.",
        jd_text="",
        briefing="",
    )
    ctx = lane.run_headline_lane_execution(args)
    rd = Path(ctx["artifact_dir"])
    usage = json.loads((rd / "section_input_usage_ledger.json").read_text(encoding="utf-8"))
    receipt_path = rd / "x2_source_fact_pool_receipt.json"
    assert receipt_path.is_file()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt.get("section") == "headline"
    assert usage.get("proof_source") == receipt.get("proof_source")
    assert usage.get("proof_pool_digest") == receipt.get("proof_pool_digest")
    x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"]: g["pass"] for g in x2.get("gates", [])}
    membership_gate = gate_ids.get("x2_headline_active_proof_pool_source_fact_ids")
    srfs_gate = gate_ids.get("x2_headline_source_fact_ids_within_srfs_slice")
    assert membership_gate is True or srfs_gate is True


def test_mock_executive_summary_lane_x2_receipt_matches_usage_ledger(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    from apps_rg.runtime.dispatch.executive_summary_dispatch import build_parser
    from apps_rg.runtime.sections.executive_summary_lane import run_executive_summary_execution
    from tests._apps_contract.test_exec_summary_section_pipeline import _tag_exec_summary_provider_resolution

    import uuid

    run_dir = harness_run(f"_exec_x2_pool_{uuid.uuid4().hex[:10]}")
    run_dir.mkdir(parents=True, exist_ok=True)
    args = build_parser().parse_args(
        ["--provider", "mock", "--mock-judges", "--allow-non-allow-exit-zero"]
    )
    _tag_exec_summary_provider_resolution(args)
    args.allow_test_mock_judges = True
    run_executive_summary_execution(args, artifact_dir_override=run_dir)

    usage = json.loads((run_dir / "section_input_usage_ledger.json").read_text(encoding="utf-8"))
    receipt_path = run_dir / "x2_source_fact_pool_receipt.json"
    assert receipt_path.is_file()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt.get("section") == "executive_summary"
    assert usage.get("proof_source") == receipt.get("proof_source")
    assert usage.get("proof_pool_digest") == receipt.get("proof_pool_digest")
    x2 = json.loads((run_dir / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"]: g["pass"] for g in x2.get("gates", [])}
    membership_gate = gate_ids.get("x2_executive_summary_active_proof_pool_source_fact_ids")
    srfs_gate = gate_ids.get("x2_executive_summary_source_fact_ids_within_srfs_slice")
    assert membership_gate is True or srfs_gate is True


def test_mock_competencies_lane_x2_and_usage_ledger_agree(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    from apps_rg.runtime.sections import competencies_lane as lane

    args = lane.build_competencies_lane_args(
        provider="qwen_vllm",
        temperature=lane.COMPETENCIES_TEMP_DEFAULT,
        x1d_judges="gemini_pro",
        mock_judges=True,
        allow_test_mock_judges=True,
        target_title="SVP Engineering",
        target_company="Synthetic Enterprise Corp.",
        jd_text="",
        briefing="",
    )
    ctx = lane.run_competencies_lane_execution(args)
    rd = Path(ctx["artifact_dir"])
    usage = json.loads((rd / "section_input_usage_ledger.json").read_text(encoding="utf-8"))
    receipt_path = rd / "x2_source_fact_pool_receipt.json"
    assert receipt_path.is_file()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert usage.get("proof_source") == receipt.get("proof_source")
    assert usage.get("proof_pool_digest") == receipt.get("proof_pool_digest")
    x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"]: g["pass"] for g in x2.get("gates", [])}
    assert gate_ids.get("x2_all_terms_source_fact_ids") is True
    membership_gate = gate_ids.get("x2_competencies_active_proof_pool_source_fact_ids")
    srfs_gate = gate_ids.get("x2_competencies_source_fact_ids_within_srfs_slice")
    assert membership_gate is True or srfs_gate is True
