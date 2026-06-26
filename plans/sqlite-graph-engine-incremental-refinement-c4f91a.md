# SQLite Graph Engine Incremental Refinement

Plan ID: `sqlite-graph-engine-incremental-refinement-c4f91a`
Status: Approved
Created: 2026-06-25
Owner: Codex

## Objective

Complete the incremental SQLite graph-engine requirements for apps_rg C0.3 graph-skills traversal while preserving `main`/canonical JSON authority and keeping SQLite as a generated runtime/query projection.

## Constraints

- Use `main` as source-of-truth baseline.
- Do not migrate to a new graph database.
- Do not replace `apps_rg/fact_inventory/master_skills_arsenal_ledger.json` as canonical graph authority.
- Do not introduce Neo4j, Kuzu, RDF, NetworkX runtime dependency, or server-based graph infrastructure.
- Do not treat graph rows as claim proof; facts remain proof substrate.
- Do not touch unrelated dirty files.

## Dependency Graph

ADG Provenance: `backend_used=sqlite`, snapshot `06242026_2303`.

Roots:

- `apps_rg/fact_inventory/augmented_skills_graph_sqlite.py`
- `apps_rg/fact_inventory/graph_sqlite_path_index.py`
- `apps_rg/runtime/c03_graph_sqlite_context.py`
- `apps_rg/runtime/c0/c03_graph_expansion.py`

Impacted consumers:

- `apps_rg/runtime/c0/evidence_room.py`
- `apps_rg/fact_inventory/run_materialize_augmented_skills_graph_sqlite.py`
- `tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py`
- new `tests/unit/apps_rg/fact_inventory/test_graph_sqlite_path_index.py`

## Scope Declaration

Expected files to modify/create:

1. `apps_rg/fact_inventory/graph_sqlite_path_index.py`
2. `apps_rg/fact_inventory/augmented_skills_graph_sqlite.py`
3. `apps_rg/runtime/c03_graph_sqlite_context.py`
4. `apps_rg/fact_inventory/validate_graph_sqlite_path_index.py`
5. `tests/unit/apps_rg/fact_inventory/test_graph_sqlite_path_index.py`
6. `docs/reports/apps_rg/sqlite_graph_engine_incremental_refinement.md`
7. `plans/sqlite-graph-engine-incremental-refinement-c4f91a.md`

The worktree contains unrelated dirty files under `agentic_core/**`, `apps_rg/cache/**`, headline/prompt files, and unrelated tests. They are excluded from this scope.

## PRE_CODE_GATE

Changed/new surfaces:

- `materialize_graph_path_index`
- `build_reverse_edge_view`
- `build_graph_sibling_links`
- `build_graph_neighborhoods`
- `record_resume_metric_usage`
- `record_graph_selection_rejection`
- `query_repeated_metrics`
- `query_reverse_metric_paths`
- `query_sibling_alternatives`
- `query_section_evidence_budget`
- `query_best_metric_candidates`
- `validate_graph_sqlite_path_index`
- optional path-index fields in `assemble_c03_graph_sqlite_context`

Required tests:

- materialization preserves graph node/edge/link counts
- reverse traversal finds upstream nodes
- sibling links produce alternatives
- metric usage penalizes/query-orders repeated metrics
- section evidence budget loads defaults
- rejection receipts can be inserted and queried
- graph_paths contains valid paths
- validator fails if required tables are missing

## Verification Commands

```powershell
python apps_rg/fact_inventory/validate_graph_sqlite_path_index.py
python -m pytest tests/unit/apps_rg/fact_inventory/test_graph_sqlite_path_index.py -q
python -m pytest tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py -q
```

