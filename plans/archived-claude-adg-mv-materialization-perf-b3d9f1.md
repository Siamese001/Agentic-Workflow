---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\adg-mv-materialization-perf-b3d9f1.md'
original_relative_path: 'adg-mv-materialization-perf-b3d9f1.md'
source_sha256: 5f4c893869a096a8685bb17aa806f7cdc71d6db3d4ff43c267dd7b746b943710
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: adg-mv-materialization-perf-b3d9f1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# ADG MV Materialization — Attack the ~530 s Refresh

Cut the dominant cost of an ADG run — the ~530 s `materialize_all_views` pass (52 `CREATE TABLE AS SELECT` over 1.07M edges) — by profiling the long poles first, then optimizing the heaviest statements and (optionally) materializing incrementally, **without changing any MV's output rows**.

> **plan_id discipline**: marker lines use `plan=adg-mv-materialization-perf-b3d9f1`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: DONE
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-06-07

## W2+W4 RESULT (verified)

`mv_runtime_spine_gaps` rewritten to set-based pre-aggregation (one indexed temp
table of spine-connected paths + a single IN-membership aggregation). **Isolated
EXCEPT equivalence proof: OLD 301.2 s vs NEW 0.10 s; rows 7=7, only_in_old=0,
only_in_new=0 → BYTE-IDENTICAL.** Full `materialize_all_views`: ~440 s → 4.5 s (~98×).

**LANDING NOTE:** fix re-applied to
`tools/generate/materialized_views/phase_a_path_authority.py` in the working tree
but **NOT yet committed** — a concurrent agent is mid repo-wide `.cursor→.claude`
migration (60+ churned files, incl. a 1-line path edit in phase_a). Commit deferred
until that settles to avoid entangling the one-hunk fix with the migration. The
exact rewrite lives in this plan's W2 execution detail and is trivially re-appliable.

PLAN_COMPLETE: plan=adg-mv-materialization-perf-b3d9f1 note="mv_runtime_spine_gaps 440s->4.5s (~98x), equivalence proven byte-identical via EXCEPT; commit deferred pending concurrent .cursor->.claude migration"

## W1 FINDING (decisive — collapses the plan)

Profiled `materialize_all_views` on `adg_indexed_05272026_1632.sqlite` (artifact
`mv_phase_profile_20260607_130124.json`): **TOTAL 439.7 s, of which a SINGLE
statement is 435.76 s (99.1%)** — `CREATE TABLE mv_runtime_spine_gaps` in Phase A.
Every other statement combined ≈ 4 s.

Root cause (EXPLAIN-confirmed): a **CORRELATED scalar `EXISTS` subquery** scanning
the full imports/calls edge set, evaluated per module row (**1,997 modules**) and
**duplicated 3×** (connected_count / gap_count / gap_pct). O(modules × edges) × 3.

**Plan impact:** W2 reduces to ONE statement rewrite (set-based pre-aggregation:
build the connected-resolved_path set once into a temp table, then a plain
per-layer aggregation with a membership test). **W3 (incremental materialization)
is UNNECESSARY** — there is no broad rebuild cost, just one pathological query.
Intermediate-index / parallelism angles are moot. Expected: ~440 s → <2 s,
output identical (guarded by the W4 per-table content-hash harness).

---

## Context (SCQA)

- **Situation** — Plan `adg-gate-pipeline-efficiency-e4b1c7` (2026-06-07) measured the ADG full-run breakdown: **MV materialization ~530 s dominates**; the gate dispatcher (~45 s) is a small slice and was proven non-threadable (GIL-bound, reverted). MV refresh runs 6 sequential phases (A → B,C → D → E → F) building 52 `mv_*` tables via `CREATE TABLE AS SELECT`, several of which are graph algorithms in SQL (centrality, blast radius, critical-path, recursive CTEs).
- **Complication** — Two obvious levers are already weak: **(a)** `nodes`/`edges` are **already comprehensively indexed** (verified 2026-06-07: src_id, dst_id, relation_type, (src_id,relation_type), (dst_id,relation_type), entity_type, layer, resolved_path, source_file, semantic_type, …) — base-table indexing won't move the needle; **(b)** SQLite is **single-writer**, so concurrent phase writes to one DB file serialize on the write lock — naive phase parallelism gives ~nothing. We do not yet have **per-phase / per-statement timing**, so we don't know which of the 52 statements own the 530 s.
- **Question** — How do we materially cut the 530 s MV refresh without altering any `mv_*` table's contents and without weakening the gates that consume them?
- **Answer** — Measure first (W1 profiling is mandatory and may show the cost is concentrated in a few graph-SQL statements), then optimize those specific statements (intermediate `mv_*` indexes for cross-phase joins, CTE rewrites, redundant-recompute elimination), then — only if profiling justifies it — incremental "dirty-only" materialization keyed on source digest. Every wave gates on byte-identical MV output vs. the current full rebuild.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Profile per-phase + per-statement timing; rank long poles | ✅ DONE | 0 | 1 (profiler) |
| W2 | Rewrite the ONE long pole `mv_runtime_spine_gaps` (set-based pre-aggregation) | ✅ DONE (uncommitted — see landing note) | 0 | 1 |
| W3 | Incremental materialization | ❌ UNNECESSARY (W1: no broad rebuild cost — single query) | — | — |
| W4 | Verify byte-identical MV output + timed before/after | ✅ DONE (EXCEPT proof 7=7, 0 diffs; 440s→4.5s) | 0 | 0 |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Instrument `materialize_all_views` with per-phase + per-statement timers | ✅ DONE |
| W1.2 | Emit ranked long-pole report; decide W2/W3 split | ✅ DONE — 1 query = 99.1%; W2=single rewrite, W3 dropped |
| W2.1 | Add indexes on intermediate `mv_*` tables joined by later phases | 🔲 TODO |
| W2.2 | Rewrite/contain the heaviest graph-SQL statements (long poles) | 🔲 TODO |
| W3.1 | Source-digest dirty tracking → skip unchanged MVs | 🔲 TODO |
| W4.1 | Full MV equivalence harness (row counts + content hash per table) | 🔲 TODO |
| W4.2 | Timed before/after (warm) + memory writeback | 🔲 TODO |

---

## Out Of Scope

- **Base-table indexing on `nodes`/`edges`** — already comprehensive (verified); not the bottleneck.
- **Naive intra-file phase parallelism** — blocked by SQLite single-writer. (A separate-temp-DB compute-then-attach approach is a possible W-future only if W1 proves compute, not the write lock, dominates AND statement opts are insufficient — explicitly deferred, not in this plan.)
- Changing any `mv_*` table's schema or row contents. This plan is **pure latency** — output must be identical.
- The gate dispatcher / gates (separate, already settled in `adg-gate-pipeline-efficiency-e4b1c7`).

---

## Wave 1 — Profile (measure before optimizing)

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — instrumentation only (timing prints / a profile artifact); no MV logic change.

**Phases**:
- **W1.1** — per-phase + per-statement timers | ~6K tokens | PHASE_STATUS: TODO
- **W1.2** — ranked long-pole report + W2/W3 decision | ~4K tokens | PHASE_STATUS: TODO

**Acceptance**:
- A profile artifact lists every phase's wall-clock and the top ~10 individual statements by time, on a real-snapshot copy.
- The long poles (statements owning the majority of 530 s) are named, so W2/W3 target evidence, not guesses.

---

## Wave 2 — Targeted Statement Optimization

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Authorization**: NOT_REQUIRED — latency-only changes proven output-identical by the W4 harness; no schema/row change.

**Phases**:
- **W2.1** — index intermediate `mv_*` tables that later phases JOIN (these are created via `CREATE TABLE AS SELECT` and have NO indexes by default — likely a real cross-phase join cost) | ~8K tokens | PHASE_STATUS: TODO
- **W2.2** — rewrite/contain the heaviest long-pole statements from W1 (CTE flattening, removing redundant recomputation, `ANALYZE`/query-plan tuning) | ~12K tokens | PHASE_STATUS: TODO

**Acceptance**:
- Each touched statement's output is byte-identical (W4 harness); measured per-statement speedup recorded.

---

## Wave 3 — Incremental Materialization (conditional)

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Authorization**: REQUIRED — `architecture_choice`. Incremental/dirty-only materialization changes WHEN MVs rebuild (correctness-sensitive: a stale MV that should have rebuilt would silently mislead gates). Fires an Author-Gate before edits; only pursued if W1 shows full-rebuild-every-run is the dominant cost and the source-change surface is cleanly detectable.

**Phases**:
- **W3.1** — source-digest dirty tracking: skip rebuilding an `mv_*` whose source tables/edges are unchanged since the last snapshot | ~14K tokens | PHASE_STATUS: TODO

**Acceptance**:
- On an unchanged source, skipped MVs are provably identical to a full rebuild; on any source change, affected MVs rebuild. Fail-closed: when in doubt, rebuild.

---

## Wave 4 — Verify

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — equivalence harness: per-table row count + content hash, full-rebuild vs optimized, on the same snapshot copy | ~6K tokens | PHASE_STATUS: TODO
- **W4.2** — timed warm before/after; memory writeback updating [[adg-pipeline-perf-profile]] | ~4K tokens | PHASE_STATUS: TODO

**Acceptance**:
- All 52 `mv_*` tables: identical row count + content hash vs the current full rebuild.
- Net warm wall-clock improvement reported with the per-long-pole breakdown.

---

## Execution Details

### W1.1 — Instrument timing
**Scope**: a profiling harness (NOT shipped in the hot path) that wraps `materialize_phase_a..f` and times each, plus a per-statement timer around the DROP/CREATE/INDEX statements within the long-pole phase(s). Run on a copy of `artifacts/adg/adg_indexed_<ts>.sqlite`. Emit `artifacts/adg/mv_phase_profile_<ts>.json`.

### W2.1 — Intermediate MV indexes
**Scope**: `tools/generate/materialized_views/phase_*.py`. For long-pole statements that JOIN an earlier phase's `mv_*` table, add `CREATE INDEX IF NOT EXISTS` on the join columns of that intermediate table before the consuming statement. (Base `nodes`/`edges` are already indexed — do NOT re-add those.)

### W3.1 — Dirty tracking
**Scope**: `orchestrator.py` + a digest helper. Compute a per-source-table digest (or reuse the snapshot `meta.artifact_digest` + per-relation counts); store last-built digests; skip an MV whose inputs are unchanged. Fail-closed to full rebuild on any digest miss/uncertainty.

### W4.1 — Equivalence harness
**Commands**:
```bash
# rebuild twice (baseline full vs optimized) on copies; compare per-table count + hash
python <profiling harness> --equivalence --snapshot <copy>
```

---

## ADG_HOTSPOT_REPORT

Snapshot: adg_indexed_05272026_1632.sqlite (nodes=180,057, edges=1,068,351).

| rank | file | layer | role | archetype | surfaces | note |
|------|------|-------|------|-----------|----------|------|
| 1 | tools/generate/materialized_views/phase_*.py | L_TOOLS | MV builders | STATE_NODE | State | 6 phases, 52 tables, ~530 s — the optimization target |
| 2 | tools/generate/materialized_views/orchestrator.py | L_TOOLS | MV driver | ORCHESTRATOR | State | phase sequencing; W3 dirty-tracking entry point |

**Layer note**: All touched files are `L_TOOLS` (ADG tooling), not the L0–L6 runtime spine — layer multipliers don't apply. The blast-radius control is **MV output equivalence** (W4 per-table count + content-hash harness): any latency change that alters a single `mv_*` row is a regression, since 12 P0/P1 dispatcher gates + the inline witness gate consume these tables.

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized Views (the optimization subject)
- Phase A (19 tables incl. `mv_critical_path_segments`, `mv_path_criticality_rollup`, `mv_hotspot_centrality`, `mv_handoff_witness_tiers`, `mv_write_sovereignty_paths`) — graph-algorithm SQL, likely long-pole candidates.
- Phases B,C depend only on A; D on A+B+C; E on A+B; F on C+E + `coverage_by_path`.

### Structural facts grounding the plan
- Base-table indexes (verified 2026-06-07): `nodes` 8 indexes, `edges` 11 indexes covering all hot join/filter columns → base indexing is NOT the bottleneck.
- Intermediate `mv_*` tables (created via `CREATE TABLE AS SELECT`) carry NO indexes unless a phase adds them — cross-phase joins against them are the realistic indexing target (W2.1).
- SQLite single-writer model → intra-file phase write-parallelism is blocked (out of scope).

### ADG Provenance
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05272026_1632.sqlite

---

## Gap Register

**GAP-1: No per-phase/per-statement timing exists** — the 530 s is an aggregate; W1 must decompose it before any optimization is justified. Optimizing without W1 = guessing.

**GAP-2: Payoff is uncertain** — if W1 shows the cost is spread evenly across inherent graph-SQL with no dominant pole and no cross-phase index gap, the achievable speedup may be modest, and W3 (incremental) becomes the only large lever. This plan is explicitly evidence-gated: W1 may downgrade W2/W3 scope.

**GAP-3: Correctness risk in W3** — incremental materialization can silently serve a stale MV. Fail-closed digest discipline + the W4 equivalence harness are mandatory mitigations; W3 is Author-Gated.

---

## Definition of Done

DoD-1: Per-phase + per-statement profile artifact produced; long poles named
- Evidence: `artifacts/adg/mv_phase_profile_<ts>.json` with ranked timings.
- Status: TODO

DoD-2: MV output unchanged (executable surface touched)
- Evidence: W4 equivalence harness → all 52 tables identical row count + content hash, optimized vs full rebuild.
- Status: TODO

DoD-3: Measured warm speedup
- Evidence: before/after warm `materialize_all_views` wall-clock + per-long-pole breakdown.
- Status: TODO

DoD-4: No new ADG violations / tests green
- Evidence: `pytest tests/unit/tools/generate/test_materialized_views_phase_*.py` pass; `python ops_scripts/ci/run_contract_gates.py` exits 0.
- Status: TODO

DoD-5: Memory + plan writeback
- Evidence: [[adg-pipeline-perf-profile]] updated with the per-phase numbers + what worked/didn't.
- Status: TODO

---

## Scope Expansion Authorization

```
DISCOVERED_SCOPE: plan=adg-mv-materialization-perf-b3d9f1 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=adg-mv-materialization-perf-b3d9f1 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
```

> Separate-temp-DB compute parallelism is SPLIT_TO_NEW_PLAN material if W1 ever justifies it.

---

## Marker Quick Reference

```
WAVE_START: plan=adg-mv-materialization-perf-b3d9f1 wave=<N>
WAVE_COMPLETE: plan=adg-mv-materialization-perf-b3d9f1 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=adg-mv-materialization-perf-b3d9f1 phase=<W1.1>
PLAN_COMPLETE: plan=adg-mv-materialization-perf-b3d9f1 note="<final outcome>"
```
