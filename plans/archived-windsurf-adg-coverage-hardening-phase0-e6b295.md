---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\adg-coverage-hardening-phase0-e6b295.md'
original_relative_path: 'adg-coverage-hardening-phase0-e6b295.md'
source_sha256: 8e25e0fba5550584e0245cedc6a4f684250df50e2815bb0acfb68bb18a55e7a2
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan — ADG Coverage Hardening Phase 0

**Slug**: `adg-coverage-hardening-phase0-e6b295`
**Status**: Draft (awaiting /plan kick-off)
**Tier**: T3 (cross-layer; parent-assessment-driven; coverage remediation breadth)
**Parent marker**: `DEFERRED_SCOPE: plan=wave-e-adg-card-projection-2df148 wave=E phase=E.F2 layer=L1 fan_in=0 surface=None coverage_gap_pct=99.7 est_tokens=8000`
**Priority band**: **P4** (auto-scored — high coverage gap but no surface intersection)
**Parent assessment**: `.windsurf/plans/adg-chromadb-retrieval-assessment-8a3f2b.md`
**ADG baseline**: latest `adg_indexed_<ts>.sqlite` at kick-off
**ADG provenance**: `backend=sqlite, snapshot=adg_indexed_<ts>.sqlite`

---

## Intent

The parent assessment identified a 99.7% coverage gap in the ADG coverage register for L1 cognition surfaces. Phase 0 establishes the **coverage baseline + hardening scaffolding** so subsequent phases (not in scope here) can close specific gaps with evidence. This plan is foundational, not remediative.

---

## ADG_GRAPH_LAYER_EVIDENCE

Primary drivers (constitutional §22):

- **Materialized views (≥3)**: `mv_eval_coverage_by_path` (current coverage index), `mv_exit_disposition_coverage` (disposition-side coverage), `mv_handoff_witness_tiers` (witness-tier coverage)
- **Semantic edges**: `flows_to`, `controls_flow`, `emits_side_effect` — surfaces lacking coverage
- **P-views**: `v_p1_not_on_spine` (lowest-priority coverage targets — schedule last), `v_p0_l1_direct_infra` (P0 gaps — top priority)

## ADG_HOTSPOT_REPORT

Hotspots recomputed at kick-off. Target archetypes:

- **CENTRAL_DEPENDENCY** (widely-depended L1 surfaces without coverage — top priority)
- **ORCHESTRATOR** (L1 dispatch points lacking test coverage)

Impact score applies L1 multiplier ×1.0 (standard) × coverage_gap_pct.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|:---:|---|:---:|---|
| W1 | P1.1 | Coverage baseline snapshot (extend `artifacts/adg/coverage/`) | 2000 | MVs populated | Todo | Baseline JSON with 99.7% gap delineated |
| W2 | P2.1 | Hotspot prioritization — L1 surfaces ranked by fan-in + criticality | 1500 | W1 done | Todo | Ranked CSV; top-20 identified |
| W3 | P3.1 | Coverage-gap analyzer + report generator | 2000 | Baseline stable | Todo | Report runnable; generates `docs/reports/adg-coverage/<ts>.md` |
| W4 | P4.1 | Scaffolding: test-stub generator for top-20 gaps (audit-only) | 1500 | Top-20 ranked | Todo | 20 stub tests appear in `tests/` with `@pytest.mark.todo` |
| W5 | P5.1 | ADR documenting hardening approach + next-phase plan slug | 1000 | — | Todo | ADR + follow-up plan drafts |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|:---:|:---:|
| P1.1 | Baseline | `tools/adg/coverage/baseline_snapshot.py` (new) | Coverage-index freshness | 2000 | Todo |
| P2.1 | Prioritization | `tools/adg/coverage/hotspot_rank.py` (new) | Ranking heuristic | 1500 | Todo |
| P3.1 | Analyzer | `tools/adg/coverage/gap_report.py` (new) | Report format | 2000 | Todo |
| P4.1 | Stub generator | `tools/adg/coverage/stub_gen.py` (new) | Test-name collision | 1500 | Todo |
| P5.1 | ADR + follow-ups | `docs/architecture/adr/ADR-NNN-*.md` + 3 phase-1 plan drafts | Scoping | 1000 | Todo |

**Total est**: 8000 tokens (matches marker)

## Gap Register

| Gap | Impact | Resolution Wave |
|---|---|---|
| G-1 | 99.7% L1 coverage unknown | W1 |
| G-2 | No hotspot-ranked prioritization | W2 |
| G-3 | No automated gap reporting | W3 |
| G-4 | No test scaffolding for identified gaps | W4 |
| G-5 | No documented hardening approach | W5 |

## Success Criteria (rollup)

1. Coverage baseline JSON in `artifacts/adg/coverage/baseline_<ts>.json`
2. Top-20 L1 gaps ranked and documented
3. `gap_report.py` runnable; produces deterministic markdown output
4. 20 `@pytest.mark.todo` stubs appear (no skips; todo marker only)
5. ADR posted; 3 phase-1 execution-plan slugs drafted (not executed)

## Dependencies

- Parent assessment `adg-chromadb-retrieval-assessment-8a3f2b.md`
- MV `mv_eval_coverage_by_path` populated — VERIFIED 2026-04-22 (51 MVs present)

## Out of Scope

- Actually closing the 99.7% coverage gap (that is phase 1+, scheduled via follow-up plans from W5)
- Writing the test bodies for the 20 stub tests (phase 1 work)
- Coverage hardening for L0/L2/L3/L4/L5/L6 (separate plans)

## Execution-Order Note

Lowest priority (P4) of the 5 follow-up plans. Schedule after the P1–P3 items (W7.1, W8.1, E.F1, E.F3) have landed so hotspot ranking benefits from fresher ADG snapshots.
