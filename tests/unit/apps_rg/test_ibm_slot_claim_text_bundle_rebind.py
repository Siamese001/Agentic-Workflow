"""IBM slot claim_text must be rebound to its role-episode BUNDLE, not the ranked candidate fact.

Regression for the W2.2 X1D grounding false-fail (plan typed-edge-role-facet-guardrails-a6f3d2,
2026-06-14): the slot->candidate-fact ranking (stamped to bul_ibm_* by order) and the
slot->bundle map used by generation are assigned independently, so a bundle-generated bullet
(e.g. the IBM-AWS alliance bullet on bul_ibm_005) was graded by the X1D judge against an
unrelated ranked candidate fact's claim_text (Salesforce "$10M ARR") -> factual_support /
fact_bullet_mismatch decisive fail. `_rebind_ibm_slot_claim_text_to_bundle` aligns the slot's
judge-facing claim_text with the bundle narrative + approved metric-outcome labels.
"""

from __future__ import annotations

from apps_rg.runtime.section_graph_skills_proof_pool import (
    _rebind_ibm_slot_claim_text_to_bundle,
)


def test_rebind_aligns_alliance_slot_claim_text_to_bundle() -> None:
    plan = {
        "facts": [
            {
                "fact_id": "bul_ibm_005",
                "candidate_fact_id": "fact_revenue_ops_001",
                "claim_text": (
                    "Designed analytics in Salesforce to prioritize high-potential deals, "
                    "generating $10M in new annual recurring revenue and refining GTM strategies."
                ),
                "has_metric": False,
                "metric_raw": "",
            }
        ]
    }
    _rebind_ibm_slot_claim_text_to_bundle(plan)
    fact = plan["facts"][0]
    ct = str(fact["claim_text"])
    # Rebound to the IBM-AWS alliance bundle narrative + its approved metric.
    assert "alliance" in ct.lower()
    assert "20%" in ct
    # Held/unapproved candidate-fact figures must NOT leak into the grounding evidence.
    assert "$10M" not in ct and "10M" not in ct
    # candidate_fact_id lineage preserved; bundle provenance recorded.
    assert fact["candidate_fact_id"] == "fact_revenue_ops_001"
    assert fact["role_episode_bundle_id"] == "reb_ibm_aws_alliance_partner_cosell_gtm"
    assert "fact_partnerships_gtm_002" in (fact.get("bundle_linked_source_fact_ids") or [])


def test_rebind_ignores_non_ibm_slot_facts() -> None:
    plan = {"facts": [{"fact_id": "fact_unrelated_001", "claim_text": "Original claim."}]}
    _rebind_ibm_slot_claim_text_to_bundle(plan)
    assert plan["facts"][0]["claim_text"] == "Original claim."
