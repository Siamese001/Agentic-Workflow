---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-orphaned\\adg-ci-gate-hardening-deferred-b4e3c9.md'
original_relative_path: '_archive\\2026-orphaned\\adg-ci-gate-hardening-deferred-b4e3c9.md'
source_sha256: 50a47d9b2575e7f410b5075b922056bfbedfeaf12191f871c82819bdc6731741
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
> SUPERSEDED 2026-05-02 - Notion status flipped to Superseded. Burndown/backlog/followup/deferred framing retired in favor of ratcheting CI gates (where applicable) or absorption into successor plans. Daily-drift counts are stale by design and not plan-tracked. Kept on disk for archive only.

---
plan_type: governance
---

# ADG CI Gate Hardening — Deferred Backlog

**Plan ID**: `adg-ci-gate-hardening-deferred-b4e3c9`
**Created**: 2026-04-22 (orphan-row recovery — Notion rows existed since 19:09 UTC, plan file materialized 19:42 UTC)
**SSOT**: Notion Wave/Phase Convergence DB rows (12 phases). This file is a disk anchor; detail lives in Notion.
**Status**: **Superseded by `adg-three-bucket-unified-c4f8e2`** (2026-04-30) — 12 phases redistributed across unified W3/W4/W5/W6.

## Parent Plan Summary

12-phase plan to **(A) harden post-ADG gates against false-positive green states** via negative tests + graph-layer primitives, and **(B) wire L2 runtime agents to ADG MVs / semantic edges / P-views**.

- Workstream A (gate semantic hardening): 1.3 → 2.3
- Workstream B (L2 agent graph-layer integration): 2.4 + 2.5 → 3.3
- Workstreams A and B are independent and can run in parallel

## Origin (why this exists)

Surfaced in 2026-04-22 session after the adg-ci-gate rollout (Waves A/B/C) revealed:
1. **Gate semantic hollowness** — Wave B shipped 4 exception contracts with gate reporting `PASS — 4 verified`; all 4 were actually SKIPPED due to broken caller resolution (wrong SQLite columns). Textbook false-positive green.
2. **Graph-layer underutilization** — Constitutional §22 says MVs/semantic edges MUST drive T2/T3 plans. Reality: 0 MVs, 0 semantic edges beyond `imports`, and 0 P-views used by the 5 new gates. Graph overlay built, value not collected.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|---|---|---|---:|---|
| **W1-P0** | 1.1, 1.2, 1.3 | Unblock commit workflow + small real gaps + gate precision audit | 15k | Todo |
| **W2-P1** | 2.1, 2.2, 2.3, 2.4, 2.5 | Handler fixes + warn→error promotion + weak-gate rewrite + MCP tool expose + ADR | 40k | Todo |
| **W3-P2** | 3.1, 3.2, 3.3 | Baseline burndowns (lifecycle, config-ref) + pilot L2 agent | 35k | Todo |
| **W4-P3** | 4.1 | Test-harness coverage burndown (1051 modules) | 50k | Todo |

**Total**: ~140k tokens across 12 phases.

## Phase-Level Summary

| Phase ID | Title | Scope | Est. Tokens | Status |
|---|---|---|---:|---|
| 1.1 | Fix pre-commit MM dual-state silent rollback | Pre-commit wrapper / hook change | 3k | Todo |
| 1.2 | Add ValueError handlers to 3 register_embedding_client callers | 3 files in agentic_core/L2, system_learning | 4k | Todo |
| 1.3 | **Gate precision audit — negative-test each post-ADG gate** | 5 gate scripts, new test fixtures | **8k** | Todo — **Workstream A foundation** |
| 2.1 | Add CriticalInfrastructureError handlers to 6 SemanticCacheManager._initialize callers | 6 files across L3/L4/apps_shared/system_learning | 6k | Todo |
| 2.2 | Promote remaining 2 warn-severity exception contracts to error | config/exception_contracts.yaml | 1k | Todo (depends 1.2 + 2.1) |
| 2.3 | **Rewrite weak gates using MVs + semantic edges** | check_test_harness_coverage, check_lifecycle_pairs, check_expected_wiring | **15k** | Todo — **Workstream A execution (depends 1.3)** |
| 2.4 | **Expose MVs + semantic edges via adg_sqlite MCP** | 4 new tools: adg_mv_hotspot_centrality, adg_blast_radius, adg_semantic_fanout, adg_p_view_query | **12k** | Todo — **Workstream B foundation** |
| 2.5 | **ADR — L2 agent graph-layer integration contract** | ADR-NNN (new) + AGENTS.md | **6k** | Todo — **Workstream B foundation (parallel with 2.4)** |
| 3.1 | Lifecycle-pair baseline burndown (142) | ~142 files with unclosed sqlite3.connect / open() | 15k | Todo |
| 3.2 | Config-reference baseline burndown (153) | ~153 undeclared env flags | 10k | Todo |
| 3.3 | **Pilot L2 agent — ExecutionOrchestrator._populate_d2_cache uses blast_radius MV** | agentic_core/L3_orchestration/execution_orchestrator.py | **10k** | Todo — **Workstream B pilot (depends 2.4 + 2.5)** |
| 4.1 | Test-harness coverage burndown (1051 uncovered prod modules) | tests/ (new), baseline pinning | 50k | Todo |

## Dependency Chain

```
1.3 (audit)  ──►  2.3 (rewrite weak gates)  ──►  stronger enforcement
1.2 + 2.1    ──►  2.2 (warn→error promotion)
2.4 (MCP tools)
2.5 (ADR)    ──►  3.3 (pilot agent)
2.3          ──►  3.1, 4.1 (so hotspot-centrality promotion rules apply)
```

## Detail — Per Phase (cross-reference only)

Full per-phase detail (Success Criteria, Files In Scope, Dependencies, Parent Plan Summary) lives in Notion Wave/Phase Convergence DB rows under `Plan File = adg-ci-gate-hardening-deferred-b4e3c9.md`.

Notion DB: https://www.notion.so/aa8d2507101e438481d960ea3fe33876
Query filter: `Plan File contains "adg-ci-gate-hardening-deferred"`

## Gap Register

None at plan creation. Deferred items that materialize during execution should be added here AND to the Notion row's Blocking Items field.

---

Generated 2026-04-22 as orphan-row recovery from the Notion audit report at `docs/reports/plans/notion_backlog_audit_20260422.md`. Original 12 Notion rows created 2026-04-22 19:09–19:24 UTC; enriched schema backfilled 19:32 UTC; plan file materialized 19:42 UTC.
