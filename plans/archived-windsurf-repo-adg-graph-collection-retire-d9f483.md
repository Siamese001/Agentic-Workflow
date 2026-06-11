---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\repo-adg-graph-collection-retire-d9f483.md'
original_relative_path: 'repo-adg-graph-collection-retire-d9f483.md'
source_sha256: 71923a6ed8eaab0334559f8a16195654f7aa0564e823b72f0274a4d57f2bf117
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan — Retire `repo_adg_graph` Edge-Bulk Collection

**Slug**: `repo-adg-graph-collection-retire-d9f483`
**Status**: Draft (awaiting /plan kick-off; benchmark-gated)
**Tier**: T2 (scoped retirement of a documented anti-pattern)
**Parent marker**: `DEFERRED_SCOPE: plan=wave-e-adg-card-projection-2df148 wave=E phase=E.F3 layer=L4 fan_in=0 surface=State coverage_gap_pct=50.0 est_tokens=4000`
**Priority band**: **P3** (auto-scored)
**ADG baseline**: latest `adg_indexed_<ts>.sqlite` at kick-off
**ADG provenance**: `backend=sqlite, snapshot=adg_indexed_<ts>.sqlite`

---

## Intent

The `repo_adg_graph` ChromaDB collection stores ~624k raw-edge documents — the documented anti-pattern described in the 2026-04-06 assessment. Wave E built the `adg_cards` semantic projection as its replacement. This plan retires `repo_adg_graph` after benchmarks prove cards dominate on retrieval quality and cost.

---

## ADG_GRAPH_LAYER_EVIDENCE

Primary drivers (constitutional §22):

- **Materialized views (≥3)**: `mv_digest_reconciliation` (confirms card + edge coverage parity before retirement), `mv_snapshot_regression_summary` (no-regression gate), `mv_snapshot_integrity_anomalies` (integrity check post-retirement)
- **Semantic edges**: `writes_to` (identify collection writers), `reads_from` (identify collection readers)
- **P-views**: `v_p2_duplicated_adapters` (flag remaining raw-edge readers for replacement)

## ADG_HOTSPOT_REPORT

Hotspots recomputed at kick-off on readers + writers of `repo_adg_graph`. Target archetype:

- **STATE_NODE** (the collection itself — retirement must preserve state integrity via cards)
- **CENTRAL_DEPENDENCY** (any module reading from `repo_adg_graph` that still exists post-Wave-E)

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|:---:|---|:---:|---|
| W1 | P1.1 | Benchmark: cards vs. raw edges on 3 retrieval tasks | 1500 | Curated benchmark exists | Todo | Report shows cards ≥ edges on all 3 tasks |
| W2 | P2.1 | Inventory remaining `repo_adg_graph` readers | 500 | ADG edges indexed | Todo | CSV of all reader call sites |
| W3 | P3.1 | Migrate readers to card queries | 1000 | Readers ≤5 | Todo | All readers use cards; tests pass |
| W4 | P4.1 | Delete collection + ingest script + dead tests | 500 | W3 complete | Todo | Collection absent; `ingest_adg.py` archived |
| W5 | P5.1 | Writeback + ADR retirement notice | 500 | — | Todo | ADR + Notion row present |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|:---:|:---:|
| P1.1 | Benchmark | `tools/eval/retrieval_benchmark.py` + report | Benchmark stability | 1500 | Todo |
| P2.1 | Reader inventory | `tools/diag/repo_adg_graph_readers.py` (new, ephemeral) | grep → ADG resolve | 500 | Todo |
| P3.1 | Reader migration | ≤5 call sites across L3/L4 | Card-query equivalence | 1000 | Todo |
| P4.1 | Delete + archive | `tools/ingestion/ingest_adg.py` (archive), ChromaDB drop | Irreversible — guarded by W1 | 500 | Todo |
| P5.1 | ADR + writeback | ADR-NNN + Notion | — | 500 | Todo |

**Total est**: 4000 tokens (matches marker)

## Gap Register

| Gap | Impact | Resolution Wave |
|---|---|---|
| G-1 | Old anti-pattern collection alive despite replacement | W4 |
| G-2 | No benchmark evidence for retirement | W1 |
| G-3 | Readers unknown | W2 |

## Success Criteria (rollup)

1. Benchmark: cards ≥ raw edges on precision@10 across 3 tasks
2. ChromaDB `repo_adg_graph` collection deleted
3. `tools/ingestion/ingest_adg.py` archived with deprecation-complete banner
4. No test regressions
5. ADR posted

## Dependencies

- Wave E card projection — DONE
- Benchmark suite — verify at kick-off; W-E1 (hybrid-search-adg-seed-rerank) may provide additional calibration data

## Execution-Order Note

Depends on `hybrid-search-adg-seed-rerank-c58e21` for stronger benchmark baseline; consider sequencing this AFTER that plan lands.

## Out of Scope

- Other ChromaDB collections
- ADG card-emitter changes
- Retrieval engine rewrite (separate plan)
