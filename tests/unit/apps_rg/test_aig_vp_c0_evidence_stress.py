"""AIG VP Global Head Agentic AI — C0 evidence room stress."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import load_master_role_family_taxonomy
from apps_rg.fact_inventory.track_weighted_graph_expansion import infer_projection_role_family_key
from apps_rg.runtime.c0.c01_retrieval_plan import build_c01_retrieval_plan
from apps_rg.runtime.c0.c03_graph_expansion import expand_c03_graph_bindings

REPO = Path(__file__).resolve().parents[3]
JD = REPO / "apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt"


@pytest.mark.skipif(not JD.is_file(), reason="AIG JD fixture missing")
def test_aig_jd_maps_to_insurance_carrier_projection() -> None:
    jd = JD.read_text(encoding="utf-8")
    tax = load_master_role_family_taxonomy(repo_root=REPO)
    key = infer_projection_role_family_key(
        target_role="VP, Global Head of Agentic AI Solutions",
        jd_text=jd,
        briefing_text="",
        taxonomy=tax,
    )
    assert key == "INSURANCE_CARRIER_TRANSFORMATION"


@pytest.mark.skipif(not JD.is_file(), reason="AIG JD fixture missing")
def test_c01_includes_insurance_retrieval_targets() -> None:
    plan = build_c01_retrieval_plan(
        section_id="competencies",
        target_role="VP Global Head Agentic AI",
        role_family_key="INSURANCE_CARRIER_TRANSFORMATION",
        jd_text=JD.read_text(encoding="utf-8"),
    )
    primary = plan.get("retrieval_targets", {}).get("primary_targets") or []
    assert "underwriting_claims_ops_facts" in primary
    assert plan.get("role_family_key") == "INSURANCE_CARRIER_TRANSFORMATION"
