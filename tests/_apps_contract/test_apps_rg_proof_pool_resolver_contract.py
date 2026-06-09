"""Contract tests: shared proof-pool resolver — augmented_skills_graph only."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
    resolve_section_proof_pool,
)

REPO = Path(__file__).resolve().parents[2]
LEDGER_PATH = default_ledger_path(REPO)
SECTION_IDS = (
    "executive_summary",
    "headline",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
)


def _srfs_doc(sections: dict[str, list[dict]]) -> dict:
    from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS

    out = {
        "selection_id": "proof_pool_contract",
        "selected_facts_by_section": {k: [] for k in SECTION_KEYS},
        "blocked_facts": [],
        "facts_requiring_human_confirmation": [],
        "unsupported_jd_needs": [],
    }
    for k, rows in sections.items():
        out["selected_facts_by_section"][k] = rows
    return out


@pytest.mark.parametrize("section_id", SECTION_IDS)
def test_default_resolves_augmented_skills_graph(section_id: str) -> None:
    if not LEDGER_PATH.is_file():
        pytest.skip(f"ledger missing: {LEDGER_PATH}")
    pool = resolve_section_proof_pool(
        section=section_id,
        repo_root=REPO,
        target_company="Acme",
        target_title="VP Engineering",
        jd_text="Lead platform engineering.",
        briefing_text="Emphasize scale and delivery.",
        product_visible=False,
    )
    assert pool.proof_source == PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    assert pool.broad_skills_ledger_present is False
    assert pool.srfs_present is False
    assert pool.base_resume_fallback_used is False
    assert pool.proof_pool_digest
    meta = pool.proof_pool_metadata or {}
    assert meta.get("proof_pool_type") == "augmented_skills_graph"
    assert meta.get("broad_skills_ledger_used_as_authority") is False
    assert pool.targeting_inputs_used.get("jd_title_company") is True
    assert pool.targeting_inputs_used.get("briefing") is True


@pytest.mark.parametrize(
    ("section_id", "prefix"),
    (
        ("insurtech_bullets", "bul_insurtech_"),
        ("insurtech_narrative", "bul_insurtech_"),
        ("ey_bullets", "bul_ey_"),
        ("ey_narrative", "bul_ey_"),
    ),
)
def test_role_lanes_resolve_canonical_bullet_namespace(section_id: str, prefix: str) -> None:
    if not LEDGER_PATH.is_file():
        pytest.skip(f"ledger missing: {LEDGER_PATH}")
    pool = resolve_section_proof_pool(
        section=section_id,
        repo_root=REPO,
        target_company="Synthetic Role Lane Target",
        target_title="SVP Engineering",
        jd_text="Role-lane namespace proof.",
        briefing_text="",
        product_visible=False,
    )
    assert pool.proof_source == PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    assert pool.allowed_fact_ids_ordered
    assert all(fid.startswith(prefix) for fid in pool.allowed_fact_ids_ordered)
    assert all(
        str(f.get("fact_id") or "").startswith(prefix)
        for f in (pool.selected_fact_plan.get("facts") or [])
    )


def test_headline_fail_closed_when_graph_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "apps_rg.runtime.proof_pool_resolver.resolve_augmented_skills_graph_authority",
        lambda **_: {"skills_authority_status": "BLOCKED", "skills_authority_block_reason": "test"},
    )
    with pytest.raises(ValueError, match="graph-skills proof pool BLOCKED"):
        resolve_section_proof_pool(section="headline", repo_root=REPO, product_visible=False)


def test_non_proof_inputs_recorded_in_usage_extension() -> None:
    if not LEDGER_PATH.is_file():
        pytest.skip(f"ledger missing: {LEDGER_PATH}")
    from apps_rg.runtime.proof_pool_resolver import proof_pool_usage_ledger_extension

    pool = resolve_section_proof_pool(
        section="competencies",
        repo_root=REPO,
        jd_text="Role needs cloud leadership.",
        briefing_text="Position for enterprise SaaS.",
        target_company="TargetCo",
        target_title="CTO",
    )
    ext = proof_pool_usage_ledger_extension(pool)
    assert ext["non_proof_inputs"] == ["jd_title_company", "briefing"]
    assert ext["claim_support_inputs"] == ["augmented_skills_graph"]
    assert ext["input_authority"]["augmented_skills_graph"] in (
        "CLAIM_EVIDENCE_AND_SKILLS_AUTHORITY",
        "SKILLS_COMPETENCY_AUTHORITY",
    )
    assert ext["input_authority"]["base_resume"] == "DEPRECATED_NON_AUTHORITY"


def test_legacy_broad_skills_ledger_flag_rejected() -> None:
    with pytest.raises(ValueError, match="legacy_broad_skills_ledger is not permitted"):
        resolve_section_proof_pool(
            section="unify_bullets",
            repo_root=REPO,
            legacy_broad_skills_ledger=True,
        )
