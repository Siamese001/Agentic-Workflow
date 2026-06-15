"""Headline graph-era binding recognition (typed-edge guardrails, W2.3).

The headline is the cross-employer top-line: it synthesizes graph evidence across ALL lanes,
so the model cites role-episode bundle ids (reb_*) + graph skill nodes (skill_*) directly in
claim_ledger.source_fact_ids — not the hpb_* positioning-family ids the explicit-field /
hpb-linked-fact paths resolve. Before the fix, _collect_bindings returned empty and the three
graph-lineage gates (positioning_bundle_id / graph_skill_node_ids / source_fact_or_graph_lineage)
read observed='none' and blocked headline at X3 even though it carried genuine graph lineage.
"""
from __future__ import annotations

from apps_rg.runtime.validators.headline_positioning_x2 import _collect_bindings


def _graph_era_headline() -> dict:
    return {
        "headline_line": "Lakehouse Retrieval Infrastructure | Governed Egress Architecture",
        "claim_ledger": [
            {
                "claim_text": "Lakehouse Retrieval Infrastructure",
                "source_fact_ids": [
                    "reb_unify_distributed_ecosystem_engineering",
                    "reb_ibm_aws_modernization_architecture",
                    "skill_dense_sparse_exact_retrieval_design",
                ],
            }
        ],
    }


def test_headline_recognizes_cross_employer_graph_lineage() -> None:
    b = _collect_bindings(_graph_era_headline(), {})
    assert "reb_unify_distributed_ecosystem_engineering" in b["bundle_ids"]
    assert "reb_ibm_aws_modernization_architecture" in b["bundle_ids"], "cross-employer reb_* allowed on the top-line"
    assert "skill_dense_sparse_exact_retrieval_design" in b["skill_ids"]
    assert b["fact_or_lineage"], "cited graph ids count as graph lineage"


def test_headline_with_no_graph_citations_binds_nothing() -> None:
    out = {"headline_line": "x", "claim_ledger": [{"claim_text": "x", "source_fact_ids": []}]}
    b = _collect_bindings(out, {})
    assert not b["bundle_ids"] and not b["skill_ids"] and not b["fact_or_lineage"]
