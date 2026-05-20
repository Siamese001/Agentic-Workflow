"""Contract: C0.3 section binding may attach SQLite graph context without claiming proof."""
from __future__ import annotations

from pathlib import Path

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.runtime.c03_graphrag_bound import build_section_c03_graphrag_bound

REPO = Path(__file__).resolve().parents[2]


def test_section_c03_bound_attaches_sqlite_context_metadata() -> None:
    graph = load_augmented_skills_graph(repo_root=REPO)
    digest = "testdigest"
    doc = build_section_c03_graphrag_bound(
        section_id="executive_summary",
        graph=graph,
        graph_ref="apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        graph_digest=digest,
        selected_fact_ids=["fact_engineering_platform_001"],
        repo_root=REPO,
        attach_sqlite_context=True,
    )
    assert doc["c03_graphrag_bound_status"] in ("BOUND", "NOT_BOUND")
    assert "c03_sqlite_context_status" in doc
    assert doc.get("c03_sqlite_proof_classification") == "graph_context_routing_support_not_claim_proof"
    if doc.get("c03_sqlite_context_status") == "ATTACHED":
        assert doc.get("c03_sqlite_db_path")
        assert doc.get("c03_sqlite_graph_version")
