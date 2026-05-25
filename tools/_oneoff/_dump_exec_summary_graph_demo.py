#!/usr/bin/env python3
"""One-off: show skills graph + executive_summary incorporation (demo)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
os.environ.setdefault("PYTEST_CURRENT_TEST", "demo")

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.fact_inventory.track_weighted_graph_expansion import ROOT
from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)

JD = (
    "SVP Engineering Agentic AI. Lead platform engineering, LLM orchestration, "
    "RAG, and enterprise AI governance."
)
ROLE = "SVP Engineering Agentic AI"
COMPANY = "Brown and Brown"
OUT = REPO / "artifacts" / "apps_rg" / "demos" / "exec_summary_graph_incorporation_demo.json"


def main() -> int:
    activate_fixture_dev_bypass(non_product_certified=True)
    pool = resolve_section_proof_pool(
        section="executive_summary",
        repo_root=ROOT,
        target_company=COMPANY,
        target_role=ROLE,
        jd_text=JD,
        product_visible=False,
    )
    deactivate_fixture_dev_bypass()

    meta = dict(pool.proof_pool_metadata or {})
    plan = dict(pool.selected_fact_plan or {})
    facts = list(plan.get("facts") or [])
    c03 = meta.get("c03_graphrag_bound") if isinstance(meta.get("c03_graphrag_bound"), dict) else {}

    graph = load_augmented_skills_graph(repo_root=ROOT)
    gm = graph.get("graph_metadata") if isinstance(graph.get("graph_metadata"), dict) else {}

    demo = {
        "skills_graph_file": meta.get("augmented_skills_graph_ref"),
        "skills_graph_digest": meta.get("augmented_skills_graph_digest"),
        "graph_inventory": {
            "skill_rows_total": len(graph.get("skill_rows") or []),
            "graph_nodes": gm.get("node_count"),
            "graph_edges": gm.get("edge_count"),
            "schema_version": gm.get("schema_version"),
        },
        "executive_summary_selection": {
            "selection_method": plan.get("selection_method"),
            "fact_count": len(facts),
            "facts": [
                {
                    "fact_id": f.get("fact_id"),
                    "claim_text": f.get("claim_text"),
                    "career_track": f.get("career_track"),
                    "skill_id": f.get("skill_id"),
                }
                for f in facts
            ],
        },
        "c03_graph_expansion": {
            "bound_status": meta.get("c03_graph_bound_status"),
            "hop_paths_count": meta.get("c03_graph_hop_paths_count"),
            "expansion_refs_sample": (c03.get("graph_expansion_refs") or [])[:12],
        },
        "selected_skill_rows": meta.get("selected_skill_rows") or [],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(demo, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(demo, indent=2, ensure_ascii=False))
    print(f"\nWrote {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
