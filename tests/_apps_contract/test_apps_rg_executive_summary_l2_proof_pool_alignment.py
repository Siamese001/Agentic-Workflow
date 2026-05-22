"""Executive summary L2 generation aligned with graph-only proof pool."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph import SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
    resolve_section_proof_pool,
)
from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
    validate_active_proof_pool_source_fact_ids,
)

REPO = Path(__file__).resolve().parents[2]
LEDGER_PATH = default_ledger_path(REPO)


@pytest.mark.skipif(not LEDGER_PATH.is_file(), reason="master ledger missing")
def test_executive_summary_l2_resolver_uses_augmented_skills_graph() -> None:
    pool = resolve_section_proof_pool(
        section="executive_summary",
        repo_root=REPO,
        target_company="Acme",
        target_title="SVP Engineering",
        jd_text="Lead platform programs.",
        briefing_text="Governed AI delivery.",
    )
    assert pool.proof_source == PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    assert pool.srfs_present is False
    assert pool.base_resume_fallback_used is False
    meta = pool.proof_pool_metadata or {}
    assert meta.get("proof_pool_type") == "augmented_skills_graph"
    assert meta.get("source_authority") == SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
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
    assert "AUGMENTED SKILLS GRAPH" in content
    assert fid in content
    assert "TARGETING_INPUT" in content


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

