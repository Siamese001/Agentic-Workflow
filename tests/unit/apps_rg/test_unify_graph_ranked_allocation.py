"""unify_bullets must use graph track-ranked facts, not company_hint id[:6]."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    default_taxonomy_path,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.runtime.section_graph_skills_proof_pool import allocate_section_facts_from_graph_substrate
from apps_rg.runtime.sections.unify_bullets_graph_evidence import (
    TRACK_RANKED_SELECTION_METHOD,
    is_legacy_six_pack_ledger_order,
)

REPO = Path(__file__).resolve().parents[3]
JD = (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt").read_text(encoding="utf-8")
BRIEF = (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md").read_text(
    encoding="utf-8"
)


@pytest.mark.parametrize("section_id", ["unify_bullets"])
def test_unify_bullets_uses_track_ranked_not_company_hint(section_id: str) -> None:
    ledger = load_master_candidate_fact_ledger(repo_root=REPO)
    taxonomy = load_master_role_family_taxonomy(repo_root=REPO)
    plan, _ordered, _allowed = allocate_section_facts_from_graph_substrate(
        ledger=ledger,
        taxonomy=taxonomy,
        section_id=section_id,
        target_company="Brown & Brown",
        target_role="SVP IT Strategy & Innovation",
        jd_text=JD,
        briefing_text=BRIEF,
        ledger_path=default_ledger_path(repo_root=REPO),
        taxonomy_path=default_taxonomy_path(repo_root=REPO),
    )
    assert plan["selection_method"] == TRACK_RANKED_SELECTION_METHOD
    facts = plan.get("facts") or []
    assert len(facts) == 6
    ledger_ids = [str(f.get("ledger_candidate_fact_id") or f.get("candidate_fact_id") or "") for f in facts]
    assert not is_legacy_six_pack_ledger_order(ledger_ids)
    assert "company_hint" not in plan["selection_method"]
    by_slot = {
        str(f.get("fact_id") or ""): str(f.get("ledger_candidate_fact_id") or f.get("candidate_fact_id") or "")
        for f in facts
    }
    assert by_slot.get("bul_unify_004") == "fact_engineering_platform_004"
    assert by_slot.get("bul_unify_006") == "fact_engineering_platform_006"
