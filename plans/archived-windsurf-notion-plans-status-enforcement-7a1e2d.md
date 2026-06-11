---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\notion-plans-status-enforcement-7a1e2d.md'
original_relative_path: 'notion-plans-status-enforcement-7a1e2d.md'
source_sha256: 64e627264b6565fe5b341d3cb1526553cde5c29ccf048b1414291d5aa92e9bba
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Notion Plans Status Enforcement — Stop Duplicate-Option Drift

**Slug**: `notion-plans-status-enforcement-7a1e2d`
**Status**: Completed

## Execution Record (2026-05-03)

All 6 waves landed in one session.

- **W1 (rule)**: `@c:\Git\Agentic-Workflow-FRESH\.windsurf\rules\notion-plans-taxonomy.md` now leads with a plain-word canonical table + stale-option callout; emojis demoted to "display mnemonic" footnote.
- **W2 (helper)**: `@c:\Git\Agentic-Workflow-FRESH\.windsurf\scripts\_notion_plans_status_check.py` — pure logic with `decide()` + `check()` tuple alias. 28 unit tests green.
- **W3 PIVOTED**: pre_mcp_tool_use cannot see tool arguments (confirmed in `@c:\Git\Agentic-Workflow-FRESH\.windsurf\scripts\pre_mcp_gate.py:1042-1051`). Enforcement shifted to post-cascade text scan: `@c:\Git\Agentic-Workflow-FRESH\.windsurf\scripts\post_cascade_notion_plans_status_audit.py` — advisory audit registered in `@c:\Git\Agentic-Workflow-FRESH\.windsurf\hooks.json`. Smoke-tested: detects `🟡Draft` write with canonical suggestion; logs to `artifacts/windsurf/notion_plans_status_violations.jsonl`.
- **W4 (CI gate NP2)**: `@c:\Git\Agentic-Workflow-FRESH\ops_scripts\ci\check_notion_plans_status_drift.py` — advisory, fail-closed via `NOTION_PLANS_STATUS_FAIL_CLOSED=1`. Registered in `@c:\Git\Agentic-Workflow-FRESH\ops_scripts\ci\run_contract_gates.py` after NP1.
- **W5 (tests + registration)**: 28 pytest cases pass (`@c:\Git\Agentic-Workflow-FRESH\tests\unit\windsurf_scripts\test_notion_plans_status_check.py`). Hook + gate registered.
- **W6 (AG queue seed)**: marker emitted (see §13).

### Live-DB drift discovered on first NP2 run

5 of 126 Plans rows use stale options — queue these for workspace-admin cleanup:

| Slug | Offending | Canonical |
|---|---|---|
| legacy-yaml-deletion-audit-c8e3a4 | `🟡Draft` | `Draft` |
| holdout-corpus-authoring-b5d2f6 | `🟡Draft` | `Draft` |
| judge-spearman-calibration-a7e4c9 | `🟡Draft` | `Draft` |
| (4th `🟡Draft` row — see `artifacts/notion/plans_status_drift.json`) | `🟡Draft` | `Draft` |
| apps-eval-harness-terminal-3c9f81 | `🔵Completed` | `Completed` |

Patch via `API-patch-page` one-per-response per §25. Covered by the AG queue seed below.
**Tier**: T2 (cross-layer: rule + helper + Windsurf pre-hook + CI gate + tests)
**Parent**: none
**Related memories**: `2fe76ae0` (canonical Status options), `78c557a4` (AI Summary gate pattern)

## 1. Problem

Cascade has repeatedly written emoji-prefixed Status values (`🟡Draft`, `🔵Completed`) to the Plans DB, and Notion silently auto-created them as new Select options. This fractures the Plans taxonomy and breaks every query that filters by `Status == "Draft"`.

## 2. Goal

Make it **impossible** for Cascade to write a non-canonical Status value to the Plans DB, and surface any existing drift so stale options can be retired.

## 3. Non-Goals

- Retiring the stale `🟡Draft` / `🔵Completed` options from Notion (manual workspace-admin action — outside Cascade's write surface).
- Extending the same guard to other Notion DBs (Backlog Items, SC/AP, MCP Registry) — follow-up plan if needed.
- Changing the display mnemonic in human-facing docs.

## 4. Root-Cause Summary

See RCA in chat. One-liner: rule prose used emoji mnemonic, Cascade wrote the mnemonic to the API, Notion auto-created the unknown option.

## 5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1 | Rule text — unambiguous canonical table | ~1k | Rule at `.windsurf/rules/notion-plans-taxonomy.md` | Draft | Rule opens with canonical plain-word table; emoji only in a "display mnemonic" footnote |
| W2 | P2 | Pure helper `_notion_plans_status_check.py` | ~2k | Helper pattern per `_ssot_folder_check.py` | Draft | `decide(db_id, property_name, value) -> Violation \| None`; unit tests pass |
| W3 | P3 | Windsurf pre-hook integration | ~2k | Hook at `.windsurf/scripts/pre_mcp_gate.py` | Draft | `API-post-page`/`API-patch-page` with Plans DB + non-canonical Status → exit 2 with canonical-list error |
| W4 | P4 | CI drift gate `check_notion_plans_status_drift.py` | ~2k | Gate pattern per `check_notion_plans_ai_summary.py` | Draft | Queries Plans DB, reports rows with non-canonical Status; advisory default, fail-closed via env var |
| W5 | P5 | Tests + registration | ~1.5k | Pytest at `tests/unit/windsurf_scripts/` | Draft | Helper tests ≥ 15 cases; gate registered in `run_contract_gates.py` |
| W6 | P6 | Author-Gate queue seed for follow-up cleanup | ~0.5k | §35 queue pattern | Draft | `AG_QUEUE_SEED` marker for "retire stale emoji options in Notion workspace" |

## 6. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1 | Rule unambiguity | `.windsurf/rules/notion-plans-taxonomy.md` | Emoji mnemonic currently leads; needs canonical-first reordering | 1k | Draft |
| P2 | Status-check helper | `.windsurf/scripts/_notion_plans_status_check.py` (new) | Must accept tool args shape from both `API-post-page` (properties.Status.select.name) and `API-patch-page` | 2k | Draft |
| P3 | Pre-hook wiring | `.windsurf/scripts/pre_mcp_gate.py` | Must only fire on Plans DB id (`6aba34d9-…`) + Status property; bypass env `NOTION_PLANS_STATUS_BYPASS=1` | 2k | Draft |
| P4 | Drift gate | `ops_scripts/ci/check_notion_plans_status_drift.py` (new) | Skips when `NOTION_API_KEY` unset; advisory; `NOTION_PLANS_STATUS_FAIL_CLOSED=1` for CI | 2k | Draft |
| P5 | Tests + gate registration | `tests/unit/windsurf_scripts/test_notion_plans_status_check.py` (new); `ops_scripts/ci/run_contract_gates.py` edit | Mirror `test_ssot_folder_check.py` table-driven style | 1.5k | Draft |
| P6 | AG queue seed | plan file only | `AG_QUEUE_SEED:` marker | 0.5k | Draft |

## 7. Files In Scope

- `.windsurf/rules/notion-plans-taxonomy.md` (edit)
- `.windsurf/scripts/_notion_plans_status_check.py` (new)
- `.windsurf/scripts/pre_mcp_gate.py` (edit — add Plans-status check branch)
- `ops_scripts/ci/check_notion_plans_status_drift.py` (new)
- `ops_scripts/ci/run_contract_gates.py` (edit — register NP2 gate)
- `tests/unit/windsurf_scripts/test_notion_plans_status_check.py` (new)

## 8. Canonical Status Values (SSOT)

```python
PLANS_DB_ID = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"
PLANS_DATA_SOURCE_ID = "ac53d31b-3068-4039-9ebe-856c12caab32"
CANONICAL_STATUSES = frozenset({"Live", "Draft", "Waiting", "Completed", "Retired", "Archived"})
STALE_EQUIVALENTS = {
    "🟡Draft": "Draft",
    "🔵Completed": "Completed",
    "🟢Live": "Live",
    "🟣Retired": "Retired",
    "⚪Archived": "Archived",
}
```

The helper offers a canonical suggestion when a stale equivalent is detected (mapping the emoji form to the plain word).

## 9. Hook Detection Logic

`pre_mcp_gate.py` already parses MCP tool calls. Add:

```
if tool in {"API-post-page", "API-patch-page"}:
    parent_db = args.get("parent", {}).get("database_id") or args.get("page_id_parent_db")
    if parent_db and _matches_plans_db(parent_db):
        status = args.get("properties", {}).get("Status", {}).get("select", {}).get("name")
        if status and status not in CANONICAL_STATUSES:
            block(exit=2, reason=f"Non-canonical Plans Status '{status}'. Use one of: {sorted(CANONICAL_STATUSES)}")
```

Parent-db matching must handle both the DB id and the data-source id (Notion API sometimes echoes either depending on request shape).

## 10. CI Gate Behavior (NP2)

- Paginate Plans DB via `API-query-data-source`.
- Extract each row's `Status.select.name`.
- Report rows with value ∉ `CANONICAL_STATUSES`.
- Emit JSON to `artifacts/notion/plans_status_drift.json`.
- Exit 0 by default; exit 1 if `NOTION_PLANS_STATUS_FAIL_CLOSED=1` and any drift found.
- Skip cleanly when `NOTION_API_KEY` / `NOTION_TOKEN` unset (offline CI safe).

## 11. Bypass

`NOTION_PLANS_STATUS_BYPASS=1` env var — logs a `WARNING:` row to `artifacts/windsurf/notion_plans_status_bypass.jsonl` and allows the write. Intended only for scripted workspace-admin migrations.

## 12. Success Criteria

- Rule file: canonical plain-word table precedes any emoji mention.
- Helper: ≥ 15 unit-test cases cover canonical-pass, stale-emoji-block-with-suggestion, unknown-string-block, non-Plans-DB-ignored, non-Status-property-ignored.
- Hook: smoke test — attempting `API-post-page` with `"Status": {"select": {"name": "🟡Draft"}}` to the Plans DB exits 2 with the canonical list.
- CI gate: registered as `NP2 Notion Plans Status drift (advisory)` after `NP1` in `run_contract_gates.py`; first run reports current drift count (zero expected once stale options are cleaned manually).
- AG queue seed emitted for the workspace-admin follow-up.

## 13. Deferred Scope

DEFERRED_SCOPE: workspace-admin manual retirement of stale `🟡Draft` (id `f5abd2a2-03bc-4951-9e38-ae9e1343909c`) and `🔵Completed` (id `6da99522-3194-4aa3-aac4-44296b4048b7`) Select options from the Plans DB schema. Requires Notion UI access — not automatable via MCP.

AG_QUEUE_SEED: plan=notion-plans-status-enforcement-7a1e2d id=cleanup-stale-options depends_on= title=Retire stale emoji Plans-DB Status options in Notion UI

## 14. References

- Constitutional §25 (MCP serialization), §27 (Windsurf config schema purity), §31 (SSOT folder routing)
- `.windsurf/rules/notion-plans-taxonomy.md`
- `ops_scripts/ci/check_notion_plans_ai_summary.py` (NP1 — pattern source)
- `.windsurf/scripts/_ssot_folder_check.py` (helper pattern source)
- Memory `2fe76ae0-2c34-4a2e-94e4-f8f26d2a04db` (canonical Status options)
