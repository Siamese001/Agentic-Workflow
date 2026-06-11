---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\rca-h9-mv-routing-materialized-views.md'
original_relative_path: 'rca-h9-mv-routing-materialized-views.md'
source_sha256: 31fcb72cbe4e2fd025b2cceb573dd60904c6b3ef07541696f6a7a9fa680aed9f
recovered_status: LOST_RECOVERED
last_commit: 'e614a8e476f'
last_commit_date: '2026-04-21 15:34:22 -0400'
created_date: '2026-04-21'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA — H9: Missing `mv_routing_*` Materialized Views in ADG

**Plan reference:** `.windsurf/plans/routing-followups-7a2c91.md` (Phase F3.6 — verification cross-link to F2.3)
**Parent gap:** `.windsurf/plans/routing-unification-qwen-abe735.md` §6 H9
**Status:** RCA + verification checklist; implementation lives in F2.3
**Date:** 2026-04-21

---

## 1. Observed State

The ADG SQLite schema contains many `mv_*` materialized views for various concerns (hotspots, blast radius, chokepoints) per constitutional §22. However, **no** view exists whose name matches `mv_routing_*`.

This means queries like:

- "What is the current tier distribution across heal attempts?"
- "How much cost budget has each apps_* consumer burned?"
- "Which failure types triggered Pro vs Flash in the last 24h?"

...cannot be answered by a single-query SQL against the ADG. They require either:

- Cross-joining multiple non-routing MVs and raw edges
- Re-parsing telemetry JSONL manually
- Ad-hoc SQL per question

## 2. Why This Matters

Constitutional §22 mandates that T2/T3 refactoring plans cite materialized views as PRIMARY drivers. Routing-specific analysis today violates this because there is no routing-specific MV to cite. W6 plans (calibration, cost demotion) worked around the gap by reading raw `HealClassifierTelemetry` JSONL in `tools/routing/calibrate_thresholds.py`.

This works at small scale. It will not scale as:

- Telemetry volume grows (JSONL full-scan becomes expensive)
- Multi-tenant analysis is needed (`per-app-per-tier` rollups)
- ADG hotspot queries want to cross-reference routing decisions with structural violations

## 3. Recommended MVs (to be implemented in F2.3)

### `mv_routing_tier_distribution`

Aggregates the last 30 days of `RoutingDecision` emissions:

```sql
CREATE VIEW mv_routing_tier_distribution AS
SELECT
  tier,                                    -- HIGH | MEDIUM | LOW | HITL
  gate_applied,                            -- NO_OVERRIDE | GATE_1_* | ...
  gemini_subtier,                          -- '' | FLASH | PRO
  cost_demoted,                            -- bool
  target_model,                            -- resolved model id
  COUNT(*) AS decision_count,
  AVG(cost_usd) AS avg_cost_usd,
  SUM(cost_usd) AS total_cost_usd
FROM routing_decision_events
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY tier, gate_applied, gemini_subtier, cost_demoted, target_model;
```

### `mv_routing_cost_burndown`

Tracks cost budget consumption per app:

```sql
CREATE VIEW mv_routing_cost_burndown AS
SELECT
  app_name,
  DATE(timestamp) AS day,
  SUM(cost_usd) AS daily_cost_usd,
  SUM(CASE WHEN cost_demoted THEN 1 ELSE 0 END) AS demotion_count,
  MAX(cost_budget_remaining_usd) AS budget_high_watermark,
  MIN(cost_budget_remaining_usd) AS budget_low_watermark
FROM routing_decision_events
GROUP BY app_name, DATE(timestamp);
```

### `mv_routing_gate_effectiveness`

Measures whether gate-triggered escalations actually resolved failures:

```sql
CREATE VIEW mv_routing_gate_effectiveness AS
SELECT
  gate_applied,
  COUNT(*) AS total_firings,
  SUM(CASE WHEN outcome_success THEN 1 ELSE 0 END) AS successful_resolutions,
  ROUND(
    100.0 * SUM(CASE WHEN outcome_success THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS success_rate_pct
FROM routing_decision_events
WHERE gate_applied != 'NO_OVERRIDE'
GROUP BY gate_applied;
```

## 4. Upstream Dependency: F2.3

These MVs **cannot be created** until F2.3 (unified OTEL schema) ships, because:

1. The MVs need a canonical `routing_decision_events` table populated from unified OTEL spans
2. Four disparate telemetry schemas (listed in parent plan P5.3) must first converge
3. The ADG generator must ingest the unified spans

This RCA therefore serves as **verification scaffolding** for F2.3:

- Before F2.3 ships, confirm that its design includes a `routing_decision_events` table
- After F2.3 ships, implement these three MVs and commit the DDL in the ADG generator

## 5. Verification Checklist (post-F2.3)

- [ ] `routing_decision_events` table exists in ADG SQLite snapshot
- [ ] All three MVs above (or equivalents) are queryable via `adg_sqlite` MCP
- [ ] W6 `calibrate_thresholds.py` migrates to read from MV instead of JSONL
- [ ] Parent plan §22 graph-layer evidence sections in future T2/T3 plans cite these MVs

## 6. Risk of Proceeding Without F2.3

- Continue the JSONL-read workaround — fine at small scale, breaks at ≥10k events/day
- Implement MVs against disparate schemas — technical debt; must be rebuilt after F2.3

## 7. Next Action

When F2.3 is scheduled, this RCA becomes the **acceptance test** for F2.3's success. Reference this file from F2.3's plan §Success Criteria.

## 8. Provenance

ADG Provenance: backend=sqlite (MV enumeration planned for F2.3 execution), design based on parent plan P5.3 scope
Constitutional compliance: §22 — this RCA documents the gap that blocks §22 compliance for routing-specific plans; fix is scheduled.
