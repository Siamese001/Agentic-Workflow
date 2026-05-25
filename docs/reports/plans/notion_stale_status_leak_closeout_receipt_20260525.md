# Notion stale status leak closeout — receipt (2026-05-25)

Closes plan [notion-stale-status-leak-closeout-b8e4f2.md](../../.cursor/plans/notion-stale-status-leak-closeout-b8e4f2.md).

## Root cause

| Leak | Mechanism |
|------|-----------|
| `Active` | [AGENTS.md](../../AGENTS.md) / [notion_databases.yaml](../../config/notion_databases.yaml) instructed `Status=Active`; sync and debug scripts posted `"Active"` to Notion API |
| `Deprioritized` | [unified_notion_status_auditor.py](../../tools/notion/unified_notion_status_auditor.py) auto-patched to `"Deferred"` (also stale); drift vs canonical `Lower Priority` |

Notion Select fields **silently create** unknown option names — validation must block before write.

## Fix summary

- SSOT: [.cursor/scripts/_notion_plans_status_check.py](../../.cursor/scripts/_notion_plans_status_check.py) — `FORBIDDEN_PLANS_STATUSES`, expanded `STALE_EQUIVALENTS`
- Auditor imports SSOT (no duplicate canonical table)
- Writers/docs use `Not Started` / `In Progress` / `Lower Priority` only
- User deleted orphan `Active` / `Deprioritized` options in Notion UI (2026-05-25)

## Proof

| Command | Result |
|---------|--------|
| `pytest tests/unit/windsurf_scripts/test_notion_plans_status_check.py -o addopts=` | **70 passed** |
| `pytest tests/unit/tools_notion/test_backfill_historical_plan_statuses.py tests/unit/ops_scripts/ci/test_check_plan_freshness.py::TestIsActiveStatus -o addopts=` | **34 passed** |

## Notion

Row patched **Completed** via [plan_notion_sync_notion_stale_status_leak_closeout.py](../../tools/notion/plan_notion_sync_notion_stale_status_leak_closeout.py).
