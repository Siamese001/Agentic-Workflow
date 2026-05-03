---
trigger: model_decision
description: Apply when authoring a new plan file under .windsurf/plans/, starting wave execution, or making any claim about a plan's Notion registration status. Enforces §36 plan-Notion registration.
---

# Plan-Notion Registration Enforcement (§36)

> ⛔ Every `.windsurf/plans/<slug>-<6hex>.md` MUST have a Notion Plans DB row
> before wave execution begins. Cascade MUST query the Plans DB — never guess —
> before asserting any plan's registration status.

Sibling to §24 (deferred-scope capture), §31 (SSOT folder routing), §35 (AG queue drain).
Same structural shape: pure helper + marker + post-hook + pre-hook + chokepoint block
+ pre-commit gate + weekly drift + bypass env var.

## The Invariant

For every plan file at `.windsurf/plans/<slug>-<6hex>.md` with Status in
`{Live, Draft, Waiting, Completed}`:

1. A matching Notion Plans DB row (data source `ac53d31b-3068-4039-9ebe-856c12caab32`)
   MUST exist before `wave_execution_state.py start --plan <slug>` succeeds.
2. The row MUST carry: `Slug` (title), `Status` (select), `Exists On Disk` (checkbox=true),
   `Plan File Path` (rich_text), `Summary` (rich_text), `AI Summary ` (rich_text, trailing
   space in property name — enforced separately by NP1 gate).
3. Retired and Archived plans are exempt from wave-start enforcement (the plan is no
   longer actively tracked); they still appear in the drift report.

## Required Author-Time Marker

When Cascade writes a new plan file, the authoring response MUST also contain:

```
PLAN_CREATED: slug=<slug-6hex> path=.windsurf/plans/<slug>-<6hex>.md status=Draft|Live
```

Grammar mirrors `AG_QUEUE_SEED:` and `DEFERRED_SCOPE:`. Fields are space-separated
`key=value` pairs; `status` defaults to `Draft`. The marker is captured by
`post_cascade_plan_registration_capture.py` into
`.windsurf/state/plan_registration_queue.jsonl`.

A marker without a subsequent Notion `API-post-page` against the Plans DB is a
pending registration — surfaced by `pre_user_prompt_plan_registration_surface.py`
at the next user turn.

## Enforcement Chokepoint

`tools/windsurf/wave_execution_state.py start` refuses to mark a plan as in-progress
when the plan is not registered. Block message:

```
BLOCKED: plan <slug> not registered in Notion Plans DB.
Required: API-post-page into Plans DB
  (Slug, Status=Live|Draft, Exists On Disk=true, Plan File Path, Summary, AI Summary)
  before wave execution.
Cache source: <cache|cache_stale|cache_missing> · Reason: <detail>
Bypass: PLAN_REGISTRATION_BYPASS=1
```

Because this CLI is the canonical entry for wave execution (already used by the
§25 Notion-wave-deferral rule), one chokepoint covers all wave work.

## Query Before Claim (Behavioral)

> Cascade MUST NOT assert that a plan is or is not registered without having called
> `API-query-data-source` against data source `ac53d31b-3068-4039-9ebe-856c12caab32`
> in the current response. Session memory and cached responses are not authoritative.

This rule exists because on 2026-05-03 Cascade told the user a plan
(`apps-runtime-domain-enforcement-a7e9d4`) was "not registered" without querying
the Plans DB; the plan **was** registered (page `35527693-f55c-8188-8cc2-db4d69806b3c`,
Status=Live). The false-negative was caught only because the user asked Cascade to
generate an enforcement plan — a lucky second-order correction.

Acceptable alternatives when a live Notion call is impossible (API down, token unset,
§25 serialization conflict):

- "I cannot verify registration status right now because <reason>."
- "The local cache at `.windsurf/state/plan_registration_cache.json` says X (fetched <ts>,
  age <age>)." — explicit staleness disclosure, not a bare claim.

No hook enforces this (remote-MCP serialization would stall every turn). The rule
text + weekly drift report + explicit incident log are the mitigation.

## Cache Discipline

- `.windsurf/state/plan_registration_cache.json` holds a snapshot of the Plans DB
  keyed by slug, with `fetched_at_epoch` timestamp. TTL 1 hour.
- Populated by `ops_scripts/ci/check_plan_registration_freshness.py` and
  `ops_scripts/calibration/plan_registration_weekly_report.py`.
- The wave-start block reads the cache and fails OPEN only when cache is
  missing AND `NOTION_API_KEY` / `NOTION_TOKEN` is unset (offline-safe local dev).
- When a registration has been marked in the queue (`registered=true`) but the
  cache hasn't refreshed yet, the wave-start block treats the slug as registered
  (queue is authoritative for in-flight state).

## Bypass

`PLAN_REGISTRATION_BYPASS=1` env var — bypasses the wave-start block and pre-commit
gate. Use only for:

- Scripted batch runs against historical plans predating §36.
- Emergency rollback / hotfix sessions where wave execution must proceed before
  Notion is reachable.
- Explicitly acknowledged exploratory sessions.

Every bypass is logged to `artifacts/windsurf/plan_registration_bypasses.jsonl`.

## Forbidden Patterns

- ❌ Writing a new plan file without emitting `PLAN_CREATED:` in the same response.
- ❌ Running `wave_execution_state.py start --plan <slug>` before posting the Plans DB row.
- ❌ Stating "plan X is not registered" without a live `API-query-data-source` call in
  the same response.
- ❌ Manually clearing `.windsurf/state/plan_registration_queue.jsonl` to suppress
  pending-registration surfacing (use `PLAN_REGISTRATION_BYPASS=1` instead — it logs).
- ❌ Editing `.windsurf/state/plan_registration_cache.json` by hand to fake
  registration status. The cache is deterministic output of Notion queries.

## Enforcement Layers

1. **This rule** (advisory — conditional).
2. **Helper** `.windsurf/scripts/_plan_registration.py` — pure SSOT logic.
3. **Post-hook** `.windsurf/scripts/post_cascade_plan_registration_capture.py` —
   captures `PLAN_CREATED:` markers into the queue.
4. **Pre-hook** `.windsurf/scripts/pre_user_prompt_plan_registration_surface.py` —
   emits `PLAN_REGISTRATION_PENDING:` lines at turn start.
5. **Chokepoint block** `tools/windsurf/wave_execution_state.py` (CLI) —
   fail-closed at wave-start on unregistered plans.
6. **Pre-commit gate** `ops_scripts/ci/check_plan_registration_freshness.py` (T7u)
   — blocks commits adding plan files whose matching Notion row is missing.
7. **Weekly drift** `ops_scripts/calibration/plan_registration_weekly_report.py` —
   reports orphans both directions (on-disk-not-in-Notion, Notion-Live-not-on-disk).
8. **Sibling gate NP1** `ops_scripts/ci/check_notion_plans_ai_summary.py` — already
   enforces non-empty AI Summary; §36 extends with presence enforcement.

## References

- Constitutional: §24 (DEFERRED_SCOPE), §25 (MCP serialization), §31 (SSOT folder),
  §33 (always-on budget), §35 (AG queue drain), §36 (this rule — new).
- Siblings: `ssot-folder-enforcement.md`, `author-gate-queue-drain.md`,
  `deferred-scope-capture.md`, `notion-plans-taxonomy.md`.
- AGENTS.md: Notion Workspace Map · Plans DB row.
- Plan: `.windsurf/plans/plan-notion-registration-enforcement-c8f3a1.md`.
- Incident: 2026-05-03 false-negative on `apps-runtime-domain-enforcement-a7e9d4`.
