# RCA: Notion Plans DB Status Inconsistency (2026-05-10)

**Incident date**: 2026-05-10 ~10:50 UTC  
**Author**: RCA conducted by Cascade during recovery session  
**Severity**: HIGH (data correctness; no data loss but visible status corruption across ~170 rows + 11 duplicate-row pairs)  
**Status**: Resolved (recovery complete this session); upstream fixes pending in 3 deferred-scope plans

---

## 1. Executive summary

Three independent failure modes in the Notion Plans DB write surface conspired to produce the visible "all plans flipped to Not Started" symptom:

| # | Root cause | Mechanism | Surface |
|---|---|---|---|
| **A** | `_extract_status_from_plan()` defaults to `"Not Started"` when plan markdown lacks `status:` frontmatter | `tools/notion/backfill_historical_plan_statuses.py --patch` ran on 89 items and overwrote correct Notion Status values | The bulk overwrite |
| **B** | `register_ondisk_plans_batch.py` and Cascade-direct `mcp7_API-post-page` calls do not coordinate dedup, leaving 11 slugs with duplicate Notion rows | Phantom rows accumulated. When (A) hit, the Status flipped on multiple copies of the same slug | The "still seeing Not Started after I patched it" experience |
| **C** | `plan_registration_cache.json` only refreshes when explicitly invoked (no scheduled refresh) | 9-hour gap between cache snapshot (01:44 UTC) and incident (10:50 UTC) made the cache miss user's retire/consolidate edits | The cache-driven recovery missed 3 author-gate UI plans |

Each cause is independently fixable. (A) is a single-line bug. (B) requires architectural change. (C) is a cron/hook addition.

---

## 2. Failure A — bulk overwrite source

### 2.1 The bug

`@c:\Git\Agentic-Workflow-FRESH\tools\notion\backfill_historical_plan_statuses.py:127-158`

```python
def _extract_status_from_plan(md: str) -> str:
    # 1. Frontmatter: status: <value>
    m = re.search(r"^status:\s*(.+)$", md, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        ...
    # 2. Bold metadata line: **Status**: <value>
    m = re.search(r"\*\*Status\*\*:?\s*(.+)", md, flags=re.IGNORECASE)
    if m:
        ...
    # 3. Plain "Status: <value>" line
    m = re.search(r"^Status:\s*(.+)$", md, flags=re.MULTILINE)
    if m:
        ...
    # 4. Contains SUPERSEDED anywhere
    if "SUPERSEDED" in md:
        return "Retired"

    # 5. Default: Not Started
    return "Not Started"
```

The function returns `"Not Started"` for any plan markdown that doesn't match the four detection branches. **Most plans on disk do not include a frontmatter `status:` field** — they begin with `# Title` and never declare a top-level status. From the audit run during recovery:

```
fm_status: (none)         11 of 12 current Not Started rows
fm_status: Not Started     1 of 12 (notion-wave-lifecycle-autosync-f4a2b8)
```

### 2.2 The trigger

Commit `90883aafa105806b980b43c8cf4fb11108e6731c` (Sun May 10 06:56:00 2026 -0400 = 10:56 UTC) introduced the script. The commit message states "**W2 historical backfill (89 items)**" — confirming a `--patch` run hit 89 rows. Combined with subsequent re-runs (or partial completion across passes), the cumulative effect was the ~170 row Status overwrite the user observed at 10:50 UTC.

### 2.3 Why CI didn't catch it

`backfill_historical_plan_statuses.py --ci` exits 2 on drift detection (`@c:\Git\Agentic-Workflow-FRESH\tools\notion\backfill_historical_plan_statuses.py:243`). But the bug is in the drift CALCULATION itself — the script considers a plan with no frontmatter status as "drift from disk=Not Started", so its drift detection inherits the same flawed default. CI in `--ci` mode would have flagged the same 89 items as "drift to fix", presenting a false-positive backfill opportunity.

### 2.4 Fix

**Single-line fix**: change line 158 from `return "Not Started"` to:

```python
return None   # signal "no source-of-truth on disk; do not overwrite Notion"
```

Then in `main()`, when `disk_status is None`, skip the row entirely (do NOT include in drift_items, do NOT patch). This converts the script from "force Notion to match my best guess" to "patch only when on-disk has explicit ground truth".

Filed as **DEFERRED_SCOPE: backfill-historical-plan-statuses-default-bug**.

---

## 3. Failure B — duplicate Notion rows for same slug

### 3.1 Evidence

Recovery session found 11 slugs with duplicate Plans rows (some with 3 copies). Pattern from `@c:\Git\Agentic-Workflow-FRESH\artifacts\notion\plans_duplicates.json`:

```
adg-ci-gate-hardening-deferred-b4e3c9       Completed (2026-04-23) | Retired (2026-05-01)
adg-deferred-investigations-b5d9f2          Completed (2026-05-03) | Retired (2026-05-06)
adg-fail-aggregating-gate-chain-9d4e1f      Completed              | Archived (newer)
apps-research-spine-deferred-followup-9c3e1a Completed             | Not Started (phantom)
l6-doctrinal-alignment-noninvasive-b9d3f5   Completed              | Not Started (phantom, created 2026-05-10)
otel-collector-cert-receipt-b4d2e6          Not Started (phantom)  | Completed (newer)
... 5 more
```

### 3.2 Multiple writer surfaces, no shared dedup

There are **at least 41 files** that write to Notion in this repo. The Plans DB has writers in:

| Writer | Dedupes? | How |
|---|---|---|
| `tools/notion/register_ondisk_plans_batch.py` | ✅ Yes | `_slug_already_registered()` — Slug.title.equals filter |
| `tools/notion/wave_lifecycle_writer.py` | ✅ Yes | `find_plan_page()` — same filter; falls back to most-recently-edited if duplicates exist (line 181-183) |
| Cascade-direct `mcp7_API-post-page` (e.g. when I registered the recovery plan today) | ❌ No | Cascade fires the MCP tool with no dedupe step |
| `tools/notion/plan_registration_backfill.py` | ❌ No | "API calls disabled in this version" but if enabled, no dedupe |
| `tools/windsurf/wave_execution_state.py` (start command) | Indirect | Calls `_check_plan_registration` first (cache-based check) |

**The gap**: when Cascade emits an `<invoke name="mcp7_API-post-page">` for plan registration via §36, there's no pre-write check that "a row with this slug already exists". The §36 pre-prompt hook surfaces unregistered plans but doesn't dedup if the cache says missing-but-actually-present.

### 3.3 Concrete dup-creation scenario observed today

`l6-doctrinal-alignment-noninvasive-b9d3f5`:
- Original row created 2026-05-09T11:05 (page_id `35b27693-f55c-8116-...`) — was Completed before the bulk overwrite
- **Phantom row created 2026-05-10T10:06** (page_id `35c27693-f55c-811c-...`) — at Not Started
- Trigger likely: §36 cache miss → Cascade or hook re-registered the slug at default Status

### 3.4 Fix architecture

Three-layer defense:

1. **Helper-level**: a single `register_plan_idempotent(slug, ...)` function in `tools/notion/_plan_registration.py` (or new module) that ALL Plans-DB POST callers use. Logic: query by slug; if non-archived row exists, return its page_id without creating; if multiple non-archived rows exist, raise `DuplicatePlansRowError` with the page_ids.

2. **Hook-level**: `pre_mcp_tool_use` hook for `API-post-page` targeting Plans DB performs the same dedupe query and **blocks** the MCP call if a row already exists. Cascade's slug-from-payload extraction is the same regex as the post-cascade audit hook.

3. **CI-level**: weekly `check_notion_plans_no_duplicates.py` queries the live DB, fails the build if any slug appears in >1 non-archived row.

Filed as **DEFERRED_SCOPE: notion-plan-registration-dedup-bug**.

---

## 4. Failure C — cache-staleness gap

### 4.1 Evidence

`@c:\Git\Agentic-Workflow-FRESH\.windsurf\state\plan_registration_cache.json` was timestamped `fetched_at: "2026-05-10T01:44:17Z"` — 9h before the incident. During those 9h the user retired 3 author-gate UI plans (`ui-choice-consistency-zero-loss-d9e4f2`, `ask-user-question-author-gate-harmonization-a7e3d2`, `ask-user-question-interactive-enrichment-b8c3e1`) that had been consolidated into `author-gate-ask-ui-consolidated-a1e3f7`. The cache missed those edits, so cache-driven recovery left them at the cache's stale "Not Started" value.

### 4.2 Why no scheduled refresh

`@c:\Git\Agentic-Workflow-FRESH\.windsurf\scripts\_plan_registration.py:72`:

```python
CACHE_TTL_SECONDS = 3600  # 1 hour
```

The TTL is 1h, but `cache_is_fresh()` is only CHECKED, never auto-refreshed. The cache only updates when `ops_scripts/ci/check_plan_registration_freshness.py --refresh` runs. That happens on pre-commit and weekly — neither captures intermediate user UI edits.

### 4.3 Fix

Add a `pre_user_prompt_plan_registration_refresh.py` hook that refreshes the cache asynchronously (background subprocess) when the cache is older than 1h. Existing `pre_user_prompt_plan_registration_surface.py` already runs at session start; bolt the refresh onto it.

Filed as **DEFERRED_SCOPE: plan-registration-cache-snapshot-discipline**.

---

## 5. Why post-cascade auto-patch hook is NOT the cause

`post_cascade_notion_plans_status_audit.py` has an `_auto_patch_violation()` function that flips non-canonical Status values to canonical equivalents (`Draft → Not Started`, `Live → In Progress`, etc.) via `STALE_EQUIVALENTS` in `_notion_plans_status_check.py`. I considered this as the bulk-overwrite source but ruled it out:

- **Per-response, not bulk**: hook fires once per Cascade response and only patches rows mentioned in that specific response's `<invoke>` blocks
- **Violations log shows only 1 entry** in `notion_plans_status_violations.jsonl` — the hook hasn't fired prolifically
- **Mapping is correct**: `Draft → Not Started` reflects a deliberate 2026-05-03 rename; not a bug

The hook is working as designed. It is NOT the bulk-overwrite source.

---

## 6. Test pollution observation

`@c:\Git\Agentic-Workflow-FRESH\artifacts\windsurf\wave_lifecycle_notion.jsonl` shows real Notion patches with test slugs (`x-aaaaaa`, `demo-plan-abc123`, `page-123`). Pattern:

```
{"event": "apply_spec_patch", "slug": "x-aaaaaa", "page_id": "page-123", "ok": true, ...}
```

This means **unit tests for `wave_lifecycle_writer.py` are hitting prod Notion** when `NOTION_TOKEN` is set in the test environment. The test slugs don't correspond to real plans, so the patches go to a stub `page-123` that — based on consistent `ok=true` returns — appears to exist somewhere in Notion. Not the bulk-overwrite source, but a separate problem worth filing.

Filed as **DEFERRED_SCOPE: wave-lifecycle-tests-prod-notion-pollution**.

---

## 7. Mitigation summary (this session)

| Layer | Action | Outcome |
|---|---|---|
| Recovery | Built `tools/notion/restore_plan_statuses_from_cache.py` | Reusable for any future Plans DB corruption event |
| Recovery | Conservative restore from cache | 78 patches direct + ~86 background = 164 rows restored |
| Recovery | Stale-Completed pattern detection (waves all DONE on disk, Status=Not Started) | 2 rows patched |
| Recovery | User-named consolidated plans | 3 rows retired (ui-choice, harmonization, enrichment) |
| Recovery | Phantom-duplicate archive | 3 rows in_trash=true (apps-research-spine-deferred-followup, l6-doctrinal-alignment-noninvasive, otel-collector-cert-receipt) |
| Recovery | High-confidence final patches (4) | final-deferred-scope→Retired, l6-folder-rename→Retired, author-gate-ask-ui-deferred-scope→Completed, notion-wave-lifecycle-autosync→Completed |
| Recovery | Final-five legitimate-state patches | apps-architect-deferred-scope-2→Deferred, apps-rg-spine-hardening→Retired, runtime-cert-e-ci-gate→Deferred, apps-rg-pipeline-deferred→Deferred, author-gate-ask-ui-consolidated→In Progress |
| **Net** | **180 → 1 Not Started** (1 = legitimate freshly-registered P0 plan) | |

---

## 8. Action items (deferred scope)

| Priority | Action | Effort |
|---|---|---|
| **P1** | Fix `backfill_historical_plan_statuses.py` default-to-Not-Started (return None when no on-disk ground truth, skip row) | 1-line code change + test |
| **P1** | Build dedupe layer for Plans DB writers — single `register_plan_idempotent()` helper used by ALL POST paths + pre_mcp_tool_use block + weekly CI gate | 3-wave plan |
| **P2** | Cleanup remaining 8 non-Not-Started duplicate slugs (Completed/Retired/Archived divergences) | Manual triage per slug |
| **P2** | Add `pre_user_prompt_plan_registration_refresh.py` for hourly auto-refresh of plan_registration_cache.json | New hook, ~50 lines |
| **P3** | Fix unit-test pollution of prod Notion (mock or NOTION_TOKEN guard in test-only paths) | Audit affected tests |
| **P3** | Add freshness telemetry: every Plans DB writer logs to `artifacts/windsurf/plans_db_writes.jsonl` so future RCA has a paper trail | Cross-cutting |

---

## 9. Lessons

1. **"Default-to-X" patterns in inference code are dangerous.** The drift detector in `backfill_historical_plan_statuses.py` was trying to be helpful (assume Not Started when no metadata) but in a field like Status where any value carries semantic weight, the only safe default is "skip — no ground truth".
2. **Multiple writer surfaces without coordination = duplicate data.** 41 files writing to Notion is too many to evolve safely without a central helper. The dedupe responsibility leaked.
3. **Caches need refresh discipline matching their intended freshness.** TTL=1h means nothing if no one refreshes the cache hourly. Either auto-refresh or downgrade the TTL claim.
4. **The cache-driven recovery covered 95% of the damage.** Even with stale-by-9h cache, snapshot-based restore is the highest-leverage recovery mechanism. Investing in regular snapshots pays back at incident time.

---

## 10. References

- Plan: `@c:\Git\Agentic-Workflow-FRESH\.windsurf\plans\notion-plans-status-bulk-recovery-c4e2f9.md`
- Recovery tool: `@c:\Git\Agentic-Workflow-FRESH\tools\notion\restore_plan_statuses_from_cache.py`
- Bug source: `@c:\Git\Agentic-Workflow-FRESH\tools\notion\backfill_historical_plan_statuses.py:127-158`
- Trigger commit: `90883aafa105806b980b43c8cf4fb11108e6731c` (Sun May 10 06:56 EDT)
- Constitutional: §25 (MCP serialization), §35 (queue drain), §36 (plan registration)
- Rules: `.windsurf/rules/notion-plans-taxonomy.md`, `.windsurf/rules/plan-registration-enforcement.md`, `.windsurf/rules/notion-plan-wave-deferral.md`
- Memory: entity "Notion Plans DB Bulk-Overwrite Incident 2026-05-10"
