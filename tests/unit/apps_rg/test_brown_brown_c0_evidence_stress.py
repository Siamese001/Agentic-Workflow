"""Brown & Brown SVP IT Strategy — C0 evidence room stress."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import load_master_role_family_taxonomy
from apps_rg.fact_inventory.track_weighted_graph_expansion import infer_projection_role_family_key
from apps_rg.runtime.c0.c01_retrieval_plan import build_c01_retrieval_plan

REPO = Path(__file__).resolve().parents[3]
JD = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
BRIEF = REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.txt"


@pytest.mark.skipif(not JD.is_file(), reason="Brown JD fixture missing")
def test_brown_jd_maps_to_brokerage_or_insurer_it() -> None:
    jd = JD.read_text(encoding="utf-8")
    briefing = BRIEF.read_text(encoding="utf-8") if BRIEF.is_file() else ""
    tax = load_master_role_family_taxonomy(repo_root=REPO)
    key = infer_projection_role_family_key(
        target_role="Senior Vice President, IT Strategy & Innovation",
        jd_text=jd,
        briefing_text=briefing,
        taxonomy=tax,
    )
    assert key in ("INSURANCE_BROKERAGE_IT_INNOVATION", "INSURER_IT_AI_ENABLEMENT")
    assert key != "SVP_ENGINEERING_AI_PLATFORM"


@pytest.mark.skipif(not JD.is_file(), reason="Brown JD fixture missing")
def test_c01_brokerage_it_strategy_targets() -> None:
    plan = build_c01_retrieval_plan(
        section_id="executive_summary",
        target_role="SVP IT Strategy & Innovation",
        role_family_key="INSURANCE_BROKERAGE_IT_INNOVATION",
        jd_text=JD.read_text(encoding="utf-8"),
    )
    primary = plan.get("retrieval_targets", {}).get("primary_targets") or []
    assert "it_strategy_innovation_facts" in primary
