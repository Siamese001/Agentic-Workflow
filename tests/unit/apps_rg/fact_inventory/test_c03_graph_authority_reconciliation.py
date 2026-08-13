from __future__ import annotations

import copy
import json
from pathlib import Path

from apps_rg.fact_inventory.c03_graph_authority_reconciliation import (
    classify_assertion_eligibility,
    reconcile_graph_authority,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    collect_canonical_graph_issues,
)

ROOT = Path(__file__).resolve().parents[4]
LEDGER_PATH = ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"


def _ledger() -> dict:
    return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))


def test_reconciliation_is_deterministic_idempotent_and_zero_loss() -> None:
    source = _ledger()
    first = reconcile_graph_authority(copy.deepcopy(source))
    second = reconcile_graph_authority(copy.deepcopy(first))

    assert first == second
    assert {row["skill_id"] for row in first["skill_rows"]} == {
        row["skill_id"] for row in source["skill_rows"]
    }
    assert {node["node_id"] for node in first["graph_nodes"]} >= {
        node["node_id"] for node in source["graph_nodes"]
    }
    assert {edge["edge_id"] for edge in first["graph_edges"]} >= {
        edge["edge_id"] for edge in source["graph_edges"]
    }


def test_every_skill_has_identity_taxonomy_and_explicit_retrieval_disposition() -> None:
    reconciled = reconcile_graph_authority(_ledger())
    nodes = {node["node_id"]: node for node in reconciled["graph_nodes"]}
    edge_triples = {
        (edge["edge_type"], edge["source_node_id"], edge["target_node_id"])
        for edge in reconciled["graph_edges"]
    }

    for row in reconciled["skill_rows"]:
        skill_id = row["skill_id"]
        assert skill_id in nodes
        assert row["domain_id"]
        assert row["career_epoch"]
        assert row["career_track_id"]
        assert row["pillar"]
        assert isinstance(row["retrieval_eligible"], bool)
        eligible, reason = classify_assertion_eligibility(row)
        assert row["retrieval_eligible"] is eligible
        assert row.get("retrieval_ineligibility_reason") == reason
        assert (
            "capability_domain_contains_skill",
            row["domain_id"],
            skill_id,
        ) in edge_triples
        assert (
            "epoch_contains_skill",
            row["career_epoch"],
            skill_id,
        ) in edge_triples


def test_eligible_skills_bind_exact_fact_edges_and_node_source_refs() -> None:
    reconciled = reconcile_graph_authority(_ledger())
    nodes = {node["node_id"]: node for node in reconciled["graph_nodes"]}
    edge_triples = {
        (edge["edge_type"], edge["source_node_id"], edge["target_node_id"])
        for edge in reconciled["graph_edges"]
    }

    for row in reconciled["skill_rows"]:
        if not row["retrieval_eligible"]:
            assert row["retrieval_ineligibility_reason"]
            continue
        fact_ids = set(row["fact_id_links"])
        assert fact_ids
        assert fact_ids <= set(nodes[row["skill_id"]]["source_refs"])
        assert all(
            ("skill_supported_by_fact", row["skill_id"], fact_id) in edge_triples
            for fact_id in fact_ids
        )


def test_reconciled_graph_has_no_canonical_shape_issue() -> None:
    reconciled = reconcile_graph_authority(_ledger())
    assert collect_canonical_graph_issues(reconciled) == []
    assert reconciled["graph_metadata"]["node_count"] == len(reconciled["graph_nodes"])
    assert reconciled["graph_metadata"]["edge_count"] == len(reconciled["graph_edges"])

