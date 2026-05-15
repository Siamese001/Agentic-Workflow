# RCA — `post_cursor_agent_response` hook dispatcher silently dark; NEXT_STEP markers not auto-captured

**Date:** 2026-04-24 19:40 UTC-04:00
**Status:** **RESOLVED** — bypass executed, both NEXT_STEP markers captured + posted to Notion
**Scope:** Cursor Agent response hook chain, NEXT_STEP / DEFERRED_SCOPE / Author-Gate auto-capture
**Severity:** Medium (silent capture loss; no data corruption; well-known bypass exists)

---

## Symptom

User asked: "RCA why next step → why plan is not created and saved to Notion per hooks?"

The 2 `NEXT_STEP:` markers Cursor Agent emitted in the prior response did **not** result in:

- Plan files under `.windsurf/plans/`
- Notion rows in the Wave/Phase Convergence DB
- Entries in `artifacts/windsurf/next_step_capture.jsonl`

…even though the markers were syntactically correct and the corresponding hook (`post_cursor_agent_next_step_capture.py`) is registered in `.windsurf/hooks.json`.

## Root Cause

**Windsurf 2.0.67 hook dispatcher bug** (documented in [`MEMORY:876ef21d`](../../README.md#known-issues)).

The `post_cursor_agent_response` hook chain stops firing silently after some period within a session. `pre_user_prompt` hooks continue to work, but the post-response chain goes dark. No error is surfaced to the user; the IDE simply skips the dispatch.

### Evidence

```
artifacts/windsurf/post_cursor_agent_heartbeat.jsonl last entry:
  2026-04-23T20:40:46Z  pid=18360

Time of this RCA:
  2026-04-24T19:40 EDT  →  2026-04-24T23:40 UTC

Heartbeat staleness: 23h 1m
```

The session has been continuously active during that window (multiple ADG runs, plan edits, test runs all visible in conversation history). Despite that, **the heartbeat hook — which writes one line per response — recorded zero firings**. This proves the dispatcher itself is dark, not the individual hooks.

### What Eliminates Other Causes

| Suspected cause | Eliminated by |
|---|---|
| Hook script missing | All 12 `post_cursor_agent_response` scripts exist in `.windsurf/scripts/` |
| Hook script broken | Manual replay (`manual_post_cursor_agent_replay.py`) ran all 12 hooks rc=0 in this RCA — they all work when invoked directly |
| Wrong field in `hooks.json` (constitutional rule §26) | grep confirmed only `command`, `working_directory`, `show_output` per documented schema |
| Marker shape malformed | `next_step_capture.py` reported `markers=2 auto_posted=2` once invoked manually |
| Notion auth missing | `NOTION_TOKEN` is set; both pages posted successfully (page IDs `34c27693-f55c-8151-9613-c955010b968a` and `34c27693-f55c-81fe-bc65-f62cfe886e8b`) |

The only remaining cause is the dispatcher itself. This matches the memory entry verbatim.

## Corrective Actions Taken

1. **Manual replay** of the full 12-hook chain on the prior response text:
   ```
   python .windsurf/scripts/manual_post_cursor_agent_replay.py --file artifacts/windsurf/replay_response.txt
   ```
   Result: `hooks=12 failed=0`. `post_cursor_agent_next_step_capture.py` reported `markers=2 auto_posted=2`.

2. **Plan files scaffolded** by the capture script's `_deferred_scope_plan_scaffold` helper:
   - `@c:/Git/Agentic-Workflow/.windsurf/plans/adg-cascading-ratchet-defer-exit-a41828.md`
   - `@c:/Git/Agentic-Workflow/.windsurf/plans/adg-architectural-p0-violations-cleanup-bced9c.md`

3. **Notion rows posted** to Wave/Phase Convergence DB:
   - Page `34c27693-f55c-8151-9613-c955010b968a` — *Extend defer-exit pattern to SC-1 / agentic-antipattern / dead-prod-imports gates* (P4)
   - Page `34c27693-f55c-81fe-bc65-f62cfe886e8b` — *Remediate the 3 SC-1 + 2 P0 architectural violations surfaced during W8 validation* (P3)

4. **Capture log updated**: `artifacts/windsurf/next_step_capture.jsonl` now contains both rows with `kind=auto_posted`.

## Bypass Protocol (in effect until upstream fix)

Per `MEMORY:876ef21d`, while Windsurf 2.0.67 has the dispatcher bug:

| Trigger | Bypass |
|---|---|
| Cursor Agent emits `DEFERRED_SCOPE:` marker | Cursor Agent **must** also `python .windsurf/scripts/defer.py "<full marker>"` in the same response |
| Cursor Agent emits `NEXT_STEP:` marker | User runs `python .windsurf/scripts/manual_post_cursor_agent_replay.py --file <response.txt>` (or `--clipboard`) |
| Heartbeat staleness >6h surfaces in pre-prompt hook | `pre_user_prompt_hook_health_check.py` already prints the bypass instructions |

Cursor Agent SHOULD invoke `defer.py` inline for DEFERRED_SCOPE markers (since it has shell access). For NEXT_STEP markers, the inline equivalent is the same `manual_post_cursor_agent_replay.py` invocation, which Cursor Agent can now also call directly when the heartbeat is stale.

## Sunset

When upstream Windsurf 2.0.68+ ships the dispatcher fix:
1. Watch `https://windsurf.com/changelog` for the post_cascade / hook-fix entry.
2. Verify by running `python .windsurf/scripts/post_cursor_agent_heartbeat.py` then sending a single Cursor Agent message and confirming a new heartbeat row appears.
3. Retire the `defer.py` and `manual_post_cursor_agent_replay.py` inline invocations.
4. Update `MEMORY:876ef21d` to mark the workaround as obsolete.

## Related Files

- Memory entry: `MEMORY:876ef21d` (Windsurf 2.0.67 hook dispatcher bug)
- Heartbeat log: `@c:/Git/Agentic-Workflow/artifacts/windsurf/post_cursor_agent_heartbeat.jsonl`
- Capture log: `@c:/Git/Agentic-Workflow/artifacts/windsurf/next_step_capture.jsonl`
- Hook config: `@c:/Git/Agentic-Workflow/.windsurf/hooks.json`
- Bypass scripts: `@c:/Git/Agentic-Workflow/.windsurf/scripts/defer.py`, `@c:/Git/Agentic-Workflow/.windsurf/scripts/manual_post_cursor_agent_replay.py`
- Constitutional rule §26: schema purity for `hooks.json` (verified clean — not the cause here)
- Constitutional rule §17: memory-lifecycle recall protocol (the memory entry that surfaced this RCA's root cause)
