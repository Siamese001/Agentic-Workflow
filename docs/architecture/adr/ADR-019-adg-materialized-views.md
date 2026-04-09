# ADR-019: ADG SQLite Materialized View Layer Expansion

**Status**: Accepted  
**Date**: 2025  
**Deciders**: Engineering / ADG Working Group  

---

## Context

The ADG SQLite store (`adg_indexed_*.sqlite`) already materialised infrastructure-wiring
violation views (`v_p0_*` through `v_p3_*`, produced by `infra_wiring_views.py`).  However,
eleven families of architectural anti-patterns had no first-class SQL visibility:

1. Critical path and spine connectivity
2. Authority/sovereignty and write-path governance
3. L2 phase coverage and exit-disposition gaps
4. Capability, provider, and egress routing
5. Tool and agent shape / sprawl
6. Task-contract and action-safety
7. Trace / replay / eval linkage
8. Determinism and provenance drift
9. Exemption debt and concentration hotspots
10. Topology centrality and orphan detection
11. Snapshot baseline and regression diffs

Ad-hoc Python scripts in `tools/adg/structural_outputs.py` provided some overlap but
produced no persistent artefacts queryable by the ADG MCP.

---

## Decision

Implement a **physical materialized view layer** in four phases (A → D), producing 38
physical SQLite tables with prefix `mv_`. Each table:

- Is a real table (not a logical `CREATE VIEW`), populated via `CREATE TABLE … AS SELECT`
- Is idempotent: full `DROP + CREATE` on every ADG generation run
- Carries a `snapshot_id` column (`meta.commit_sha`) for historical regression tracing
- Has at least one covering index

### Phase structure

| Phase | Module | Families | Tables |
|-------|--------|----------|--------|
| A | `phase_a_path_authority.py` | 1, 2, 3, 8-partial, 10-partial | 14 |
| B | `phase_b_capability_tool_task.py` | 4, 5, 6, 10-remaining | 13 |
| C | `phase_c_trace_drift_debt.py` | 7, 8-remaining, 9 | 9 |
| D | `phase_d_snapshot_regression.py` | 11 | 6 |

### Execution order

`orchestrator.materialize_all_views(sqlite_path)` calls A → B → C → D in dependency order.
Phase B depends on Phase A's `mv_hotspot_centrality` and `mv_path_criticality_rollup`.
Phase C depends on A and B.
Phase D depends on A, B, and C (reads `mv_write_sovereignty_paths`,
`mv_path_criticality_rollup`, `mv_debt_concentration_hotspots`).

### Integration

`generate_full_adg.py` calls `_materialize_adg_views(paths.sqlite)` immediately after the
infra-wiring enrichment step, before the repair orchestrator runs.

---

## Consequences

### Positive

- 38 new queryable tables in the canonical SQLite — no new files or external stores required.
- `mv_snapshot_baseline` + `mv_snapshot_regression_summary` provide first-class regression
  signals: node delta, edge delta, violation delta, debt score delta.
- `mv_l2_phase_coverage` and `mv_exit_disposition_coverage` surface L2 phase gaps that
  were previously invisible to the ADG MCP.
- `mv_debt_concentration_hotspots` gives a weighted debt score per file, ranked.
- Idempotent design means every ADG regeneration refreshes all views deterministically.

### Negative / Trade-offs

- Full `DROP + CREATE` on every run adds ~0.5–2 s to ADG generation time on a large corpus.
- First-run `mv_snapshot_regression_summary` shows zero deltas (expected — no baseline to
  compare against).
- `mv_write_sovereignty_paths` assumes the `t_infra_importers` helper table exists (written
  by `infra_wiring_views.py`). Phase A must run after infra wiring enrichment.

### Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| SQLite schema drift invalidates queries | Queries use only canonical columns from `multi_writer.py` DDL |
| Phase D read-then-drop baseline race | Baseline is read before any `DROP TABLE` call |
| New relation types not yet in corpus | All views degrade gracefully to 0-row tables |
| Windows path separators in `LIKE` clauses | All path constants use forward-slash — SQLite LIKE is not path-aware |

---

## Alternatives Considered

1. **Logical `CREATE VIEW` only** — rejected because SQLite logical views are re-evaluated
   on every query, cannot be indexed, and are not queryable by the ADG MCP cache layer.
2. **Separate analytics database** — rejected (added operational complexity, two files to
   manage, violated SVP operational simplicity priority).
3. **Python-side aggregation in `structural_outputs.py`** — rejected (no persistence, no
   snapshot stamping, not queryable by MCP).

---

## Test Coverage

Each phase has a dedicated unit test file:
- `tests/unit/tools/generate/test_materialized_views_phase_a.py`
- `tests/unit/tools/generate/test_materialized_views_phase_b.py`
- `tests/unit/tools/generate/test_materialized_views_phase_c.py`
- `tests/unit/tools/generate/test_materialized_views_phase_d.py`

Tests cover: table creation, idempotency, snapshot ID propagation, gap detection,
correct row counts, and the `materialize_all_views` orchestrator integration.
