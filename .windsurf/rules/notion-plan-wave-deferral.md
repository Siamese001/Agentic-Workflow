---
trigger: always_on
---

# Notion Plan-Wave Deferral

> ⛔ **While executing a multi-wave plan, Cascade MUST NOT call any Notion MCP tool. ALL Notion writes are deferred until after the final wave completes.**

## Protocol

1. **Wave 1 start**: `python tools/windsurf/wave_execution_state.py start --plan <slug-6hex>` — patches Plans DB Status → `In Progress` via direct HTTP (sanctioned non-MCP path, see below). This is the first tracked wave; W0 (baseline verification, if used) is pre-flight and does NOT affect Notion status.
2. **During execution**: NO Notion **MCP** calls. `pre_mcp_gate.check_notion_wave_deferral()` blocks MCP deterministically. Direct-HTTP wave-progress writes ARE sanctioned (see §"Sanctioned non-MCP path").
3. **After each wave** (optional but recommended): `python tools/windsurf/wave_execution_state.py wave-progress --plan <slug-6hex> --wave N` — appends `[Wave-Log <ts>] W{N} DONE` to Notion Summary via direct HTTP.
4. **After final wave**: `python tools/windsurf/wave_execution_state.py complete --plan <slug-6hex>` — patches Plans DB Status → `Completed` via direct HTTP.
5. **After step 4**: any remaining Cascade-side Notion **MCP** writes (post-mortem reads, ledger sync, etc.) batch one-per-block per §25.

> ⛔ **`PLAN_COMPLETE:` marker is mandatory when all plan tasks finish in a single session and `wave_execution_state.py complete` is not called.** Emit `PLAN_COMPLETE: plan=<slug-6hex>` as a bare line in the final response. Omission = Notion status enforcement failure (plan stays `In Progress` or `Not Started` forever). Enforced by `post_cascade_plan_complete_audit.py` (advisory warn on todo-all-done without marker) and CI gate NP13 (`check_plan_complete_marker_freshness.py`). RCA: `notion-np10-deferred-scope-c8f1a4` left at `Not Started` 2026-05-10 because this marker was never emitted.

Applies to plans with ≥2 waves. Single-wave/T0/T1 exempt. Notion **reads** at end-of-plan, not end-of-wave.

## Sanctioned non-MCP path (added 2026-05-10, plan notion-wave-lifecycle-autosync-f4a2b8)

> ⛔ The "no Notion MCP calls" rule above governs **MCP tool invocations** only — i.e. anything that emits an `<invoke name="mcp*_API-*">` tag in the Cascade response. **Direct HTTP calls to Notion's REST API from Python scripts are explicitly sanctioned**, even mid-wave, because they:
>
> 1. Do not invoke any MCP tool (no `<invoke>` tag → §25 audit does not fire).
> 2. Do not pass through Cascade's MCP transport layer (immune to the upstream Anthropic concurrent-dispatch race that motivates §25).
> 3. Are deterministically invoked by hooks / CLI subcommands, not by Cascade prose (drift-resistant).

The sanctioned chain is:

| Trigger | Mechanism | Notion side effect |
|---|---|---|
| `wave_execution_state.py start` | Direct HTTP via `tools/notion/wave_lifecycle_writer.py` | Status → `In Progress` (if currently `Not Started`/`Waiting`); Summary append |
| `wave_execution_state.py wave-progress --wave N` | Direct HTTP | Summary append `[Wave-Log <ts>] W{N} DONE` |
| `wave_execution_state.py complete` | Direct HTTP | Status → `Completed`; Summary append `[Wave-Log <ts>] PLAN COMPLETE` |
| `WAVE_START:` / `WAVE_COMPLETE:` / `PHASE_COMPLETE:` / `PLAN_COMPLETE:` markers in Cascade response | `post_cascade_wave_lifecycle_capture.py` hook → direct HTTP | Same as above, decided per marker |

### High-signal Summary appends (added 2026-05-10)

> ⛔ Every `WAVE_COMPLETE:` / `PHASE_COMPLETE:` / `PLAN_COMPLETE:` marker Cascade emits SHOULD carry an optional `note="<succinct one-liner>"` field. Without it the Notion Summary column degrades to a wall of `[Wave-Log <ts>] W{N} DONE` lines with zero scope information.

Marker grammar with note:

```
WAVE_COMPLETE: plan=<slug-6hex> wave=<N> note="<files>, <tests>, <scope>"
PHASE_COMPLETE: plan=<slug-6hex> phase=<id> note="<one-liner>"
PLAN_COMPLETE: plan=<slug-6hex> note="<final outcome>"
```

The note is whitespace-collapsed and capped at ~240 chars (`MAX_NOTE_CHARS` in `tools/notion/_wave_lifecycle_helpers.py`). Quotes (`"..."` or `'...'`) are required when the note contains spaces. Good shape:

- ✅ `note="4 files, +12 tests, summary-signal upgrade"`
- ✅ `note="9/9 phases green; ledger-binder hot path"`
- ❌ `note=stuff` (single bareword — works but signals nothing)
- ❌ `note="see plan §3 for details"` (forces operator to context-switch)

`WAVE_START:` MAY include `note=` but typically doesn't — start lines are noise unless something noteworthy gates the wave.

**Failure mode**: fail-soft. Any HTTP error logs to `artifacts/windsurf/wave_lifecycle_notion.jsonl` and exits 0. Wave-state on disk is the source of truth; Notion sync is best-effort.

**Backstop**: CI gate `NP4 Notion Plans wave freshness` (`ops_scripts/ci/check_plan_notion_wave_freshness.py`) detects on-disk-vs-Notion skew >7d on active plans.

**Belt-and-suspenders (added 2026-05-11, plan `plan-complete-notion-status-enforcement-a7e2d1`)**: CI gate `NP-DONE` (`ops_scripts/ci/check_plan_done_notion_status.py`) detects plans whose on-disk Wave Structure table shows all waves ✅ DONE but Notion status ≠ `Completed`. Advisory by default; fail-closed via `NP_PLAN_DONE_STATUS_FAIL_CLOSED=1`. Bypass: `NP_PLAN_DONE_STATUS_BYPASS=1`. Skips when `NOTION_TOKEN` / `NOTION_API_KEY` unset.

**Token-absent observability (added 2026-05-11)**: Both `post_cascade_wave_lifecycle_capture.py` and `tools/notion/wave_lifecycle_writer.py::emit_from_markers` now emit a visible `[...] WARN: NOTION_TOKEN not set` message to stderr when the token is absent, so the silent-skip failure mode is detectable in logs. Previously this was completely invisible (fail-open with no output).

**RCA — `apps-lic-quarantine-u0-coverage-review-d9f4a2`**: Plan completed all 11 waves but Notion remained `Archived`. Root cause chain: (A) plan pre-emptively set to `Archived` before W8-W10 resumed, (B) `wave_execution_state.py start/complete` never called (plan predated the wave-lifecycle autosync), (C) `PLAN_COMPLETE:` marker hook either had no `NOTION_TOKEN` or the HTTP PATCH failed silently (fail-open). Result: Notion stuck at `Archived` until manual `API-patch-page`. NP-DONE gate closes this detection gap. Full RCA: plan `plan-complete-notion-status-enforcement-a7e2d1`.

## Retrospective-Plan Protocol (added 2026-05-10, plan notion-plan-status-hardening-e5f3a1)

A **retrospective plan** is one authored to document already-completed work (all waves done in the same turn as plan creation, or plan created after work is complete).

> ⛔ **NEVER call `wave_execution_state.py start` on a retrospective plan.** The `start` command emits a `wave_start` Notion sync which will flip `Not Started` / `Waiting` → `In Progress`, undoing a same-turn `Completed` status set via `API-post-page`.

### Correct protocol for retrospective plans

1. Write the plan file to `.windsurf/plans/<slug>.md`.
2. Register in Notion via `API-post-page` with `status=Completed` directly.
3. Emit `PLAN_COMPLETE: plan=<slug>` in the response (satisfies NP13 audit).
4. Do **NOT** emit `PLAN_CREATED:` marker (which would queue a registration expecting `Not Started`).
5. Do **NOT** call `wave_execution_state.py start`.

### Belt-and-suspenders guards (plan notion-plan-status-hardening-e5f3a1)

Even if `start` is called inadvertently, two guards prevent the status flip:

1. **Primary guard** (`tools/windsurf/wave_execution_state.py` `_cmd_start`): looks up the current Notion status before calling `_notion_sync`. If `current_status == "Completed"`, skips the `wave_start` sync entirely and logs `NOTION_SYNC SKIPPED reason=status_already_completed`.
2. **Secondary guard** (`tools/notion/_wave_lifecycle_helpers.py` `patch_for_marker`): `wave_start` on a `Completed` plan returns an is_noop `NotionPatchSpec` with `reason=status_completed_guard:noop`. No status property is set, no Summary append is made.

CI gate `NP-GUARD` (`ops_scripts/ci/check_notion_plan_lifecycle_guard.py`) validates both guards are present. Advisory by default; `NP_LIFECYCLE_GUARD_FAIL_CLOSED=1` activates blocking.

### RCA reference

Race condition that motivated this section: 2026-05-10 session where `apps-rg-ag8-prompt-authority-coverage-d9f4c2` was created-and-completed in one turn. The `PLAN_CREATED:` marker was queued; when `wave_execution_state.py start` ran on the next turn, it saw `Not Started` (timing window before MCP `API-post-page` landed) and flipped to `In Progress`. Closed by this rule + guards.

## Bypass

- `NOTION_WAVE_DEFERRAL_BYPASS=1` — bypass MCP-call deferral; logged. Use for user-requested mid-plan Notion **MCP reads** only.
- `WAVE_LIFECYCLE_NOTION_BYPASS=1` — skip the sanctioned direct-HTTP writer (logs only, no PATCH). Use when the Notion API is intentionally offline.
- `WAVE_LIFECYCLE_CAPTURE_BYPASS=1` — skip the post-cascade marker hook entirely.
- `PLAN_COMPLETE_AUDIT_BYPASS=1` — suppress the advisory `post_cascade_plan_complete_audit.py` warning.
- `NOTION_PLAN_COMPLETE_BYPASS=1` — skip CI gate NP12 entirely.
- `NOTION_PLAN_COMPLETE_FAIL_CLOSED=1` — flip NP12 to fail-closed (exit 1 on violations).

Constitutional §25, §35, §36.
