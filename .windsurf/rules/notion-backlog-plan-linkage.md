---
trigger: conditional
condition: >
  Use when interacting with the Notion Backlog Items database — adding rows,
  patching relations, running backfill/orphan scripts, or querying linkage
  status. Also applies when authoring any script that writes to Backlog Items.
---

# Notion Backlog Items — Plan Linkage Invariant

> **Invariant:** Every Backlog Items row MUST have either (a) a `Plan` relation
> pointing to a Plans DB page, OR (b) a non-empty `Plan File` slug. Rows with
> neither are "true orphans" and are a CI violation (gate NP3).

## Invariant Details

| Field | Requirement | Status |
|---|---|---|
| `Plan` (relation) | Preferred — direct DB relation to Plans row | Required |
| `Plan File` (rich_text) | Fallback slug — used when Plan relation is absent | Acceptable |
| Neither | True orphan — CI gate NP3 flags, backfill scripts fix | Violation |

## Fill-Rate Targets (established W1–W3, plan `backlog-plan-linkage-enforcement-a4b2f1`)

| Property | Target | Achieved |
|---|---|---|
| Plan relation | ≥ 99.4% | ✅ 100% (0 true orphans, 2026-05-03 followup) |
| Plan File | 100% | ✅ 100% |
| Phase ID | ≥ 99.8% | ✅ |
| Status | ≥ 99.8% | ✅ |
| Wave ID | ≥ 99.8% | ✅ |
| Layer / Surface | ≥ 99% | ✅ |

## Authoritative-Source Policy (W4.2 Author-Gate decision, option A)

- **Status**: Plan-derived value wins ONLY when Backlog Status is the scorer-default (`Draft`). Hand-authored values are never overwritten.
- **Layer**: Plans DB carries no Layer property — Backlog value is authoritative.
- **Plan File**: Format mismatch (Backlog = slug, Plans = full path) — no override; Backlog slug is canonical.

## CI Gate

`ops_scripts/ci/check_notion_backlog_plan_linkage.py`

- **NP3** in `run_contract_gates.py` assurance gate plane.
- Advisory by default; fail-closed via `BACKLOG_PLAN_LINKAGE_FAIL_CLOSED=1`.
- Skips when `NOTION_API_KEY` / `NOTION_TOKEN` unset (offline CI safe).
- Artifact: `artifacts/notion/backlog_plan_linkage.json`.

## Fix Procedure (when NP3 fires)

1. Run `python tools/notion/backfill_backlog_plan_relation.py` to re-link unlinked rows.
2. If rows remain unlinked after backfill, run `python tools/notion/apply_orphan_disposition.py` to route true orphans to the catch-all plan.
3. Re-run gate to confirm zero violations.

## Related Scripts

| Script | Purpose |
|---|---|
| `tools/notion/backfill_backlog_plan_relation.py` | W1 — bulk Plan relation backfill |
| `tools/notion/apply_orphan_disposition.py` | W2 — route true orphans to catch-all |
| `tools/notion/backfill_backlog_outliers.py` | W3 — Phase ID / Status / Wave ID / Layer defaults |
| `tools/notion/audit_backlog_plan_derived.py` | W4 — delta audit: Backlog vs Plan-derived values |
| `tools/notion/apply_plan_derived_status.py` | W4 — upgrade scorer-default Status from Plan |
| `tools/notion/audit_backlog_fill_rates.py` | Ongoing fill-rate measurement |

## References

- Plan: `.windsurf/plans/backlog-plan-linkage-enforcement-a4b2f1.md`
- Sibling rule: `.windsurf/rules/notion-plans-taxonomy.md` (Plans DB Status canonicalization)
- CI gates NP1, NP2: `ops_scripts/ci/check_notion_plans_ai_summary.py`, `check_notion_plans_status_drift.py`
