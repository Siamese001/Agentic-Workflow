"""Headline xyz-grounding skill-text + plan↔ledger subset calibration (typed-edge, W2.3).

Two W2.3 headline fixes validated here:
1. Skill grounding: selected_fact_plan.facts carries claim_text only for reb_* bundles; skill_*
   graph nodes (in selected_skills) had no display text, so segments citing a skill could not
   ground (x2_headline_xyz_literal_grounding). Skill text is now derived from the graph-node id.
2. plan↔ledger coherence: a one-line headline cites a prioritized SUBSET of the deterministic
   graph selection (required_fact_ids), so exact set-equality falsely failed good headlines.
   The invariant is now ledger ⊆ required (no fabricated citation), not equality.
"""
from __future__ import annotations

from apps_rg.runtime.validators import headline_x2 as H


def test_skill_id_to_grounding_text_strips_qualifiers() -> None:
    assert H._skill_id_to_grounding_text("skill_sr_w12_databricks_lakehouse_fundamentals") == "databricks lakehouse fundamentals"
    assert H._skill_id_to_grounding_text("skill_sr_cloud_data_platform_engineering") == "cloud data platform engineering"
    assert H._skill_id_to_grounding_text("skill_dense_sparse_exact_retrieval_design") == "dense sparse exact retrieval design"


def test_fact_text_map_includes_skill_text() -> None:
    parsed = {
        "selected_fact_plan": {
            "facts": [{"fact_id": "reb_unify_x", "claim_text": "Distributed infra"}],
            "selected_skills": [{"skill_id": "skill_sr_w12_databricks_lakehouse_fundamentals"}],
            "selected_skill_ids": ["skill_dense_sparse_exact_retrieval_design"],
        }
    }
    m = H._extract_plan_fact_text_map(parsed)
    assert m["reb_unify_x"] == "Distributed infra"
    assert "lakehouse" in m["skill_sr_w12_databricks_lakehouse_fundamentals"]
    assert "retrieval" in m["skill_dense_sparse_exact_retrieval_design"]


def test_xyz_grounding_passes_when_segment_matches_skill_text() -> None:
    parsed = {
        "selected_fact_plan": {
            "facts": [],
            "selected_skill_ids": ["skill_sr_w12_databricks_lakehouse_fundamentals"],
        }
    }
    cl = [{"claim_text": "Lakehouse Infrastructure", "source_fact_ids": ["skill_sr_w12_databricks_lakehouse_fundamentals"]}]
    ok, _obs, _reason = H.check_headline_xyz_literal_grounding(
        headline_line="Lakehouse Infrastructure",
        claim_ledger=cl,
        fact_id_to_text=H._extract_plan_fact_text_map(parsed),
    )
    assert ok is True
