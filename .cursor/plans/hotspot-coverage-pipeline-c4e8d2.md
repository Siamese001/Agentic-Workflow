# Plan: Hotspot × Coverage Risk Pipeline

**Slug**: `hotspot-coverage-pipeline-c4e8d2`
**Tier**: T3 (cross-layer: tools/adg, tools/generate, system_learning, conftest, ops_scripts)
**Created**: 2026-04-28
**Status**: In progress
**Author**: Cursor Agent
**ADG Snapshot Baseline**: `artifacts/adg/adg_indexed_04252026_0843.sqlite` (Redis HOT)

## Problem

The static ADG ships **8 hotspot views** (`mv_hotspot_centrality`, `mv_path_criticality_rollup`, `mv_high_fan_in_out_with_defects`, `mv_debt_concentration_hotspots`, `mv_dependency_cone_risk`, `mv_graph_chokepoint_bridges`, `mv_graph_critical_path_blast_radius`, `mv_graph_reverse_dependency_hotspots`) — Step 1 of the analysis is fully populated.

The coverage scaffolding (`mv_eval_coverage_by_path`, `mv_l2_phase_coverage`, `mv_trace_replay_eval_gaps`) exists but is **fed by nothing**: runtime-edge ingest is structurally absent (see runtime ADG audit `docs/reports/runtime_adg_coverage_20260428_055900.md` — 95.4% orphaned snapshots, 2/5 Tier-1 spans).

The joined view `mv_hotspot_coverage_risk` and the priority output `v_hotspot_coverage_top_priority` **do not exist**. Raw test counts (22,474 tests across 2,286 files) cannot be ranked against risk because there is no `(risk × coverage_weakness)` join.

## Goal

Produce a working `(hotspot risk) × (coverage signal) → priority band` pipeline backed by REAL data, so any future "do we have enough tests for X" question is answerable from a single SQL view.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W1 | W1.1–W1.3 | `coverage.py` ingester (HIGHEST LEVERAGE — independent of runtime ADG) | ~9000 | `.coverage` SQLite produced by pytest exists or can be produced; coverage.py library available | Todo | New table `coverage_by_path` exists in ADG snapshot, populated with line + branch coverage per resolved file, joined to `nodes.id` via `resolved_path` |
| W2 | W2.1–W2.3 | `mv_hotspot_coverage_risk` joined materialized view | ~5000 | W1 produces `coverage_by_path`; existing hotspot views are stable | Todo | New MV joins `mv_path_criticality_rollup` + `coverage_by_path` + `mv_modified_area_regressions` + `test_stubs` density into a single per-node row with `risk_band`, `coverage_band`, `priority_band` |
| W3 | W3.1–W3.2 | `v_hotspot_coverage_top_priority` output report | ~4000 | W2 view is populated | Todo | Tool emits ranked markdown report at `artifacts/test_inventory/hotspot_coverage_priority.md` matching the user's bottom-diagram shape (Hotspot \| Risk \| Coverage \| Read) |
| W4 | W4.1–W4.4 | Runtime ADG trace binding fix (P2 deferred — decoupled from coverage path) | ~12000 | `system_learning/runtime_adg/store.py` is the SSOT; pre-existing 1,833 orphaned snapshots can be back-filled from payload `trace_id` | Todo | (a) `persist()` rejects empty `trace_id`; (b) back-fill recovers ≥80% of 1,833 orphans; (c) `_runtime_adg_coverage_audit.py` re-run shows bind rate ≥95% |
| W5 | W5.1–W5.5 | Edge-case hardening | ~6000 | W1–W4 land successfully | Todo | Pytest covers: empty `.coverage`, missing snapshot, schema drift, concurrent persist, malformed payload |
| W6 | W6.1–W6.2 | Commit + sync | ~2000 | All waves green | Todo | `git status` clean; `git push` ok; ADG regenerated with new MVs |

**Total estimated tokens**: ~38,000 (well under 1M cap)

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---:|---|
| W1.1 | Build `tools/adg/ingest_coverage_py.py` | new file ~150 lines | Coverage.py SQLite schema varies by version; need to handle missing `.coverage` gracefully | 4000 | Todo |
| W1.2 | Wire ingester into `tools/generate/generate_full_adg.py` | modify generator entry | Must run AFTER `nodes` table is built (FK on `resolved_path`) | 2000 | Todo |
| W1.3 | Add `coverage_by_path` table generation + tests | tests/unit/tools/adg/test_ingest_coverage_py.py | Schema lock, idempotency, file-not-found | 3000 | Todo |
| W2.1 | Define `mv_hotspot_coverage_risk` SQL | tools/generate/materialized_views/phase_d_*.py (new file) | Risk-band thresholds; coverage thresholds; SQL joins on multiple keys | 3000 | Todo |
| W2.2 | Tests for the new MV | tests/unit/tools/generate/test_phase_d_hotspot_coverage.py | Ensure deterministic ordering, NULL coverage handling | 2000 | Todo |
| W3.1 | Build `tools/analysis/hotspot_coverage_report.py` | new file ~120 lines | Markdown formatting; band-color thresholds | 3000 | Todo |
| W3.2 | Tests + sample report | tests/unit/tools/analysis/test_hotspot_coverage_report.py | Empty-MV handling | 1000 | Todo |
| W4.1 | Audit `persist()` callers in `system_learning/runtime_adg/store.py` | 1 file | Identify all entry points + assert trace_id required | 3000 | Todo |
| W4.2 | Add `trace_id` guardrail | same file | Pure addition; back-compat for old behavior gated by env var | 2000 | Todo |
| W4.3 | Back-fill `_trace_index.json` from payload | new tool: `tools/runtime_adg/backfill_trace_index_v2.py` | Existing tool exists; verify it's wired or write a v2 | 5000 | Todo |
| W4.4 | Re-run audit + verify ≥95% bind rate | run `_runtime_adg_coverage_audit.py` | Should show before/after delta | 2000 | Todo |
| W5.1 | Edge: empty `.coverage` | test | Path: ingester returns 0 rows + log warning | 1000 | Todo |
| W5.2 | Edge: missing snapshot file | test | Path: graceful skip with reason code | 1000 | Todo |
| W5.3 | Edge: malformed payload during back-fill | test | Path: skip + log + continue | 1000 | Todo |
| W5.4 | Edge: concurrent `persist()` | test | Path: file lock or retry | 1500 | Todo |
| W5.5 | Edge: schema migration (older snapshot) | test | Path: skip MV generation if upstream MVs missing | 1500 | Todo |
| W6.1 | Run full pytest suite (filtered) | `pytest -m "adg_runtime or adg_otel"` | Catch any breakage | 1000 | Todo |
| W6.2 | Commit + push to GitHub | git ops | None | 1000 | Todo |

## Gap Register

- **G1**: Don't yet know whether `.coverage` SQLite exists in repo with usable data. Mitigation: W1.1 first inspects, generates a fresh one if missing.
- **G2**: `mv_hotspot_coverage_risk` thresholds (risk_band, coverage_band) need calibration. Mitigation: Use percentile-based bands not absolute thresholds (P75/P90 within the snapshot for risk; <50%, 50-80%, >80% for coverage).
- **G3**: Runtime ADG fix (W4) is independent of W1-W3 — sequencing chosen to deliver coverage value first. If W4 blocks, W1-W3 still ship.
- **G4**: 30-day stale plan policy not relevant — plan is being executed in this session.

## Out of Scope

- Re-architecting the runtime ADG content-addressable store (separate plan)
- Adding new hotspot dimensions beyond what the 8 existing views compute
- Test-suite culling decisions (downstream of having priority data)
- Branch coverage from external tools beyond coverage.py

## ADG_HOTSPOT_REPORT

The hotspots driving this pipeline are the test-coverage measurement seams
and the hotspot-rank consumer modules. Computed from `mv_hotspot_centrality`
+ `mv_hotspot_coverage_risk`:

| Hotspot | Layer | Fan-in | Archetype | Surface | Rationale |
|---|---|---|---|---|---|
| `tools/analysis/test_concentration_risk.py` | L_TOOLS | low (tool) | ORCHESTRATOR | Observability Surface | Coordinates fan_in + test-attribution joins |
| `agentic_core/L6_observability/coverage_collector.py` (target) | L6 | TBD | CENTRAL_DEPENDENCY | Observability Surface | Will be the canonical coverage telemetry seam |
| `ops_scripts/ci/check_test_concentration_ratio.py` | L_TOOLS | 0 (CI) | SAFETY_GATEKEEPER | Observability Surface | CI ratchet gate over the pipeline output |

## ADG_GRAPH_LAYER_EVIDENCE

Required per constitutional §22.

**Materialized views consulted**:
- `mv_path_criticality_rollup` (PRIMARY risk axis — fan_in × fan_out × violation × cross_layer)
- `mv_high_fan_in_out_with_defects` (SECONDARY risk axis — combined_risk_score)
- `mv_debt_concentration_hotspots` (DEFECT axis — total_debt_score)
- `mv_modified_area_regressions` (RECENCY axis — recently-changed defects)

**Semantic edges used**:
- `imports` (test → production fan-in)
- `writes_to`, `writes_through` (state mutation flag for risk weighting)
- `invokes_provider` (external boundary flag)
- `flows_to`, `controls_flow` (behavior axis for whether tests truly exercise)

**P-views cross-referenced**:
- `v_p0_write_bypass_uwg` — every node here MUST be in priority output if not covered
- `v_p1_zero_caller_infra` — confirms which "hotspots" are actually unreachable
- `v_p2_dormant_ambiguous` — flags for low-priority output

**Surface intersections (per ADG canonical invariants §3)**:
- Write surface (`mv_replay_surface_gaps`) — joined via `node_id`
- Execution surface (`mv_l2_phase_coverage`) — joined via `layer`
- Observability surface — runtime ADG fix in W4 closes this

## Constitutional Compliance

- §0 No PowerShell → all commands via `subprocess.run(argv, shell=False)`
- §14 Subprocess timeout → 30s on every subprocess call
- §15 Precise exception handling → no bare `except`; specific types only
- §16 Progress bars → `ProgressReporter` for any loop >10 items or >5s
- §22 ADG Graph-Layer evidence → see above
- §28 SQLite-direct fallback → all reads use direct `sqlite3` (read-only); writes go through generator pipeline
