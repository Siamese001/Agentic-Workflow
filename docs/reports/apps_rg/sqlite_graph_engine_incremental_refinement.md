# SQLite Graph Engine Incremental Refinement Receipt

Date: 2026-06-26

## Scope

This increment completes the C0.3 graph-skills traversal refinements as an SQLite runtime/query projection over the canonical JSON graph. It does not migrate apps_rg to a graph database and does not replace `apps_rg/fact_inventory/master_skills_arsenal_ledger.json` as the source of truth.

## Implemented

- Added public path-index helper APIs for reverse traversal, graph neighborhoods, sibling alternatives, section evidence budgets, repeated metric usage, graph selection rejection receipts, and novelty-aware metric candidate queries.
- Added `materialize_graph_path_index(conn)` so callers/tests can rebuild generated path, neighborhood, sibling, and budget tables from materialized `graph_nodes` and `graph_edges`.
- Extended C0.3 SQLite graph context receipts with optional path-index diagnostics:
  - `path_index_status`
  - `reverse_path_receipts`
  - `sibling_alternatives`
  - `metric_novelty_candidates`
  - `rejected_candidate_receipts`
  - `section_evidence_budget`
- Added `apps_rg/fact_inventory/validate_graph_sqlite_path_index.py` as a standalone validator. By default it materializes a temporary SQLite projection from canonical JSON and reports whether required graph-index objects and core counts are present.
- Added focused APP CONTRACT tests for path-index materialization, reverse traversal, sibling alternatives, repeated metric penalty behavior, section budgets, rejection receipts, valid paths, and validator fail-closed behavior.

## Authority And Invariants

- Canonical graph authority remains JSON.
- SQLite remains a generated runtime/query layer.
- `graph_edges_reverse` is a view, not duplicated edge authority.
- `graph_paths`, `graph_neighborhoods`, `graph_sibling_links`, `section_evidence_budget`, `resume_metric_usage`, and `graph_selection_rejections` are runtime/query aids.
- Graph rows are routing and diagnostic support, not claim proof.

## Validation Evidence

`python apps_rg/fact_inventory/validate_graph_sqlite_path_index.py`

- Status: PASS
- `sqlite_projection_canonical`: false
- `graph_node_count`: 710
- `graph_edge_count`: 2203
- `graph_path_count`: 18515
- `graph_neighborhood_count`: 12755
- `graph_sibling_link_count`: 11166
- `section_evidence_budget_count`: 378
- `skill_fact_link_count`: 241
- `metric_outcome_count`: 92

`python -m pytest tests/unit/apps_rg/fact_inventory/test_graph_sqlite_path_index.py -q`

- Result: 8 passed

`python -m pytest tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py -q`

- Result: 19 passed

`python -m pytest tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py -q`

- Result: 4 passed

