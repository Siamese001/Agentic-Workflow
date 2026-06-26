# Graph SQLite Path Index Runtime

Plan ID: `graph-sqlite-path-index-runtime-b7e2c4`
Status: Implemented
Created: 2026-06-25
Owner: Codex

## Objective

Upgrade the apps_rg generated SQLite graph projection from lookup tables into a lightweight graph index with preserved edge rationale, reverse traversal, bounded paths, neighborhoods, sibling expansion, metric-usage memory, section budgets, rejection receipts, and diagnostics while keeping `apps_rg/fact_inventory/master_skills_arsenal_ledger.json` canonical.

## Constraints

- Do not make the generated `.sqlite` file canonical.
- Do not introduce a separate graph database engine.
- Do not fabricate fact-to-metric or role-to-metric paths not present in materialized graph edges.
- Keep graph rows as routing/context support, not claim proof.
- Preserve C0.3 public entrypoints and `new_atoms_created=0`.
- Do not touch unrelated dirty cache/headline/prompt files.

## Dependency Graph

ADG Provenance: `backend_used=sqlite`, snapshot `06242026_2303`.

Graph roots:

- `apps_rg/fact_inventory/augmented_skills_graph_sqlite.py`
- `apps_rg/runtime/c03_graph_sqlite_context.py`
- `apps_rg/runtime/c0/c03_graph_expansion.py`
- `apps_rg/runtime/c0/c03_sqlite_graph_selection.py`

Impacted consumers:

- `apps_rg/runtime/c0/evidence_room.py`
- `tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py`
- `tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py`
- `tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py`
- `tests/unit/apps_rg/fact_inventory/test_metric_outcome_materializer.py`
- `tests/unit/apps_rg/test_c03_graph_skills_mvp.py`

## Scope Declaration

Expected files to modify:

1. `apps_rg/fact_inventory/augmented_skills_graph_sqlite.py`
2. `apps_rg/fact_inventory/graph_sqlite_path_index.py`
3. `apps_rg/runtime/c0/c03_sqlite_graph_selection.py`
4. `tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py`
5. `tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py`
6. `docs/reports/apps_rg/graph_sqlite_path_index_runtime_b7e2c4_receipt.json`
7. `memory/MEMORY.md`
8. `memory/codex/apps_rg_graph_sqlite_path_index_runtime.md`

Unrelated dirty files observed before execution include cache, headline, prompt, and validator files outside this scope. They are not part of this plan.

## PRE_CODE_GATE

Changed surfaces:

- `materialize_augmented_skills_graph_sqlite`
- `validate_materialized_sqlite`
- new path-index builder helpers
- `select_c03_sqlite_graph_candidates`

Required tests:

- Edge notes/policies are preserved on `graph_edges`.
- `graph_edges_reverse` exposes reverse rationale.
- `graph_paths`, `graph_neighborhoods`, and `graph_sibling_links` are materialized deterministically.
- `section_evidence_budget`, `resume_metric_usage`, and `graph_selection_rejections` exist and are queryable.
- C0.3 selection returns path signatures, sibling alternatives, and richer rejection receipts.
- Metric usage changes ranking/penalty receipts without mutating canonical graph data.

## Waves

| Wave | Scope | Status |
|---|---|---|
| W1 | SQLite schema and path-index materialization | DONE |
| W2 | C0.3 selector integration | DONE |
| W3 | Tests, validation, and receipts | DONE |

## Verification Commands

```powershell
python -m pytest tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py -q
python -m pytest tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py tests/unit/apps_rg/fact_inventory/test_metric_outcome_materializer.py tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py tests/unit/apps_rg/test_c03_graph_skills_mvp.py -q
python apps_rg/fact_inventory/validate_c03_graph_hardening.py
python scripts/governance/codex_readiness.py --json
```

## Closeout Evidence

Receipt: `docs/reports/apps_rg/graph_sqlite_path_index_runtime_b7e2c4_receipt.json`

- `python -m pytest tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py -q` -> `23 passed`
- `python -m pytest tests/unit/apps_rg/fact_inventory/test_augmented_skills_graph_sqlite.py tests/unit/apps_rg/fact_inventory/test_metric_outcome_materializer.py tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py tests/unit/apps_rg/runtime/c0/test_c03_sqlite_graph_selection.py tests/unit/apps_rg/test_c03_graph_skills_mvp.py -q` -> `46 passed`
- `python apps_rg/fact_inventory/validate_c03_graph_hardening.py` -> PASS
- `python -m py_compile <changed graph-index python files>` -> PASS
- `git diff --check -- <graph-index changed files>` -> PASS; CRLF notices only
- `python scripts/governance/codex_readiness.py --json` -> WARN; critical checks passed, dirty worktree and duplicate MCP process advisories remain

Closeout note: the worktree contains unrelated dirty files outside this plan scope, including `agentic_core/**`, `apps_rg/cache/**`, headline/prompt files, and unrelated tests. They were not modified by this graph-index implementation.
