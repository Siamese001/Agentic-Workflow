# SQLite graph-engine incremental refinement

## Summary

This package keeps `master_skills_arsenal_ledger.json` as the canonical graph
authority and hardens the generated SQLite projection so it behaves more like
a lightweight graph engine.

It does **not** migrate apps_rg to Neo4j, Kùzu, RDF, NetworkX runtime, or any
server-based graph database.

## Added capabilities

- richer edge metadata preservation
- reverse traversal through `graph_edges_reverse`
- materialized path receipts through `graph_paths`
- sibling expansion through `graph_sibling_links`
- N-hop context through `graph_neighborhoods`
- metric novelty memory through `resume_metric_usage`
- section evidence budgets through `section_evidence_budget`
- rejected candidate receipts through `graph_selection_rejections`

## Why this matters

The repeated-metric problem is primarily a traversal and ranking problem. The
system needs to find alternative proof-bound paths rather than repeatedly
selecting the same high-salience fact or metric. These SQLite refinements let
C0.3 ask graph-like questions while keeping the current lightweight runtime.

## Commands

```bash
python apps_rg/fact_inventory/apply_graphdb_capability_sqlite_hardening.py
python apps_rg/fact_inventory/validate_graph_sqlite_path_index.py
python -m pytest tests/unit/apps_rg/fact_inventory/test_graph_sqlite_path_index.py -q
```

## Zero-loss contract

Source tables are never truncated by the new path-index module:

- `graph_nodes`
- `graph_edges`
- `skill_fact_links`

Generated graph-engine tables are rebuilt additively from the source graph
projection.
