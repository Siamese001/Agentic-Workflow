"""Graph-era Unify-narrative binding recognition (typed-edge role-facet guardrails).

Regression guard for the W2.3 fix: a graph-sourced Unify narrative binds its proof by citing
``reb_unify_*`` role-episode bundle ids + shared ``skill_*`` graph nodes under
``selected_fact_plan.primary_bundles`` and ``claim_ledger.source_fact_ids`` — NOT the legacy
``bul_unify_*`` slot ids. The X2 binding gates (``role_episode_bundle_id_required`` /
``graph_skill_node_ids_required`` / ``source_fact_or_graph_lineage_required``) and the
``unify_only_fact_scope`` gate must recognize those graph-era ids as first-class bindings.

Before the fix these four gates read ``observed='none'`` and blocked unify_narrative at X3 even
though the narrative legitimately carried the bundle/skill lineage.
"""
from __future__ import annotations

from typing import Any

from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates
from apps_rg.runtime.validators.unify_role_episode_x2 import (
    _collect_change_log_bindings,
    run_unify_narrative_role_episode_x2_gates,
)


def _scope_verdict(claim_ledger: list[dict]) -> bool:
    """Run the unify_narrative X2 gates and return the unify_only_fact_scope pass/fail."""
    gates = run_unify_narrative_x2_gates(
        narrative_sentence="Stewarded an end-to-end agentic AI mandate at Unify Consulting.",
        parsed_output={"claim_ledger": claim_ledger},
        claim_ledger=claim_ledger,
        jd_text="",
        runtime_generation_status="REAL_LLM",
        companion_bullet_texts="",
        companion_bullets_status="ACCEPTED_FINALIZED",
    )
    by_id = {g.gate_id: g.pass_ for g in gates}
    return bool(by_id.get("x2_unify_narrative_unify_only_fact_scope"))


def test_scope_accepts_graph_era_unify_ids() -> None:
    # Graph-era Unify lineage: bundle ids, metric_outcome ids, and shared skill nodes.
    cl = [
        {
            "claim_text": "Owned platform roadmap and agentic AI mandate.",
            "source_fact_ids": [
                "reb_unify_platform_commercialization_leadership",
                "metric_unify_22m_ip_led_revenue",
                "skill_ai_platform_commercialization",
            ],
        }
    ]
    assert _scope_verdict(cl) is True, "graph-era reb_/metric_/skill_ unify ids are valid scope"


def test_scope_rejects_foreign_lane_ids() -> None:
    # A foreign lane's bullet/metric ids must still fail Unify scope (leakage guard).
    cl = [{"claim_text": "x", "source_fact_ids": ["bul_ibm_005", "metric_ibm_20pct_joint_revenue_growth"]}]
    assert _scope_verdict(cl) is False, "foreign-lane ids must fail unify_only_fact_scope"

_BINDING_GATES = {
    "x2_unify_narrative_role_episode_bundle_id_required",
    "x2_unify_narrative_graph_skill_node_ids_required",
    "x2_unify_narrative_source_fact_or_graph_lineage_required",
}


def _meta() -> dict[str, Any]:
    return {
        "role_episode_bundles": [
            {
                "role_episode_bundle_id": "reb_unify_agentic_platform_architecture",
                "graph_skill_node_ids": [
                    "skill_governed_agentic_systems_architecture",
                    "skill_deterministic_route_selection",
                ],
                "linked_source_fact_ids": ["fact_engineering_platform_001"],
                "linked_metric_outcome_ids": [],
            },
            {
                "role_episode_bundle_id": "reb_unify_platform_commercialization_leadership",
                "graph_skill_node_ids": ["skill_ai_platform_commercialization"],
                "linked_source_fact_ids": ["fact_commercialization_001"],
                "linked_metric_outcome_ids": [],
            },
        ]
    }


def _graph_era_narrative_output() -> dict[str, Any]:
    # The narrative carries no per-bullet change_log binding; it cites bundle ids + skill nodes.
    return {
        "narrative_sentence": "Stewarded an end-to-end agentic AI mandate, owning platform "
        "roadmap and governed control-plane architecture.",
        "selected_fact_plan": {
            "primary_bundles": [
                "reb_unify_platform_commercialization_leadership",
                "reb_unify_agentic_platform_architecture",
            ]
        },
        "claim_ledger": [
            {
                "claim_text": "Owned platform roadmap and agentic AI mandate.",
                "source_fact_ids": [
                    "reb_unify_platform_commercialization_leadership",
                    "skill_ai_platform_commercialization",
                ],
            }
        ],
        "change_log": [{"action": "drafted_narrative", "detail": "synthesized capstone arc"}],
    }


def test_collect_bindings_recognizes_graph_era_ids() -> None:
    b = _collect_change_log_bindings(_graph_era_narrative_output(), _meta())
    assert "reb_unify_agentic_platform_architecture" in b["bundle_ids"]
    assert "reb_unify_platform_commercialization_leadership" in b["bundle_ids"]
    assert b["skill_ids"], "graph_skill_node_ids must resolve from the bound bundles"
    assert b["fact_or_lineage"], "a lineage fact must resolve from the bound bundles"


def test_graph_era_narrative_passes_binding_gates() -> None:
    out = _graph_era_narrative_output()
    gates = run_unify_narrative_role_episode_x2_gates(
        narrative_sentence=out["narrative_sentence"],
        parsed_output=out,
        proof_pool_metadata=_meta(),
    )
    by_id = {g.gate_id: g.passed for g in gates}
    for gid in _BINDING_GATES:
        assert by_id.get(gid) is True, f"{gid} should PASS for a graph-era narrative"


def test_truly_unbound_narrative_still_fails() -> None:
    # Adversarial: no primary_bundles, no cited bundle/skill ids, empty change_log -> nothing binds.
    out = {
        "narrative_sentence": "Generic delivery sentence.",
        "selected_fact_plan": {"primary_bundles": []},
        "claim_ledger": [],
        "change_log": [{"action": "drafted_narrative", "detail": "x"}],
    }
    gates = run_unify_narrative_role_episode_x2_gates(
        narrative_sentence=out["narrative_sentence"],
        parsed_output=out,
        proof_pool_metadata=_meta(),
    )
    by_id = {g.gate_id: g.passed for g in gates}
    for gid in _BINDING_GATES:
        assert by_id.get(gid) is False, f"{gid} must still FAIL when nothing is bound"
