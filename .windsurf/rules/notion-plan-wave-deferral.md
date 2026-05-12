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

> ⛔ **`PLAN_COMPLETE:` marker is mandatory when all plan tasks finish in a single session and `wave_execution_state.py complete` is not called.** Emit `PLAN_COMPLETE: plan=<slug-6hex>` as a bare line in the final response. Enforced by `post_cascade_plan_complete_audit.py` and CI gate NP13 (`check_plan_complete_marker_freshness.py`).

Applies to plans with ≥2 waves. Single-wave/T0/T1 exempt. Notion **reads** at end-of-plan, not end-of-wave.

## Sanctioned non-MCP path

> ⛔ Direct HTTP calls to Notion's REST API from Python scripts are **explicitly sanctioned** mid-wave. They do not invoke MCP tools and are immune to the §25 concurrent-dispatch constraint.

The sanctioned chain is:

| Trigger | Mechanism | Notion side effect |
|---|---|---|
| `wave_execution_state.py start` | Direct HTTP via `tools/notion/wave_lifecycle_writer.py` | Status → `In Progress` (if currently `Not Started`/`Waiting`); Summary append |
| `wave_execution_state.py wave-progress --wave N` | Direct HTTP | Summary append `[Wave-Log <ts>] W{N} DONE` |
| `wave_execution_state.py complete` | Direct HTTP | Status → `Completed`; Summary append `[Wave-Log <ts>] PLAN COMPLETE` |
| `WAVE_START:` / `WAVE_COMPLETE:` / `PHASE_COMPLETE:` / `PLAN_COMPLETE:` markers in Cascade response | `post_cascade_wave_lifecycle_capture.py` hook → direct HTTP | Same as above, decided per marker |

### High-signal Summary appends

> ⛔ Every completion marker SHOULD carry `note="<one-liner>"`. Without it the Notion Summary degrades to bare timestamps.

Marker grammar with note:

```
WAVE_COMPLETE: plan=<slug-6hex> wave=<N> note="<files>, <tests>, <scope>"
PHASE_COMPLETE: plan=<slug-6hex> phase=<id> note="<one-liner>"
PLAN_COMPLETE: plan=<slug-6hex> note="<final outcome>"
```

Note capped at ~240 chars. Quotes required when note contains spaces.

**Failure mode**: fail-soft. HTTP errors log to `artifacts/windsurf/wave_lifecycle_notion.jsonl`; wave-state on disk is source of truth.

**CI backstops**: NP4 (`check_plan_notion_wave_freshness.py`) detects on-disk-vs-Notion skew >7d. NP-DONE (`check_plan_done_notion_status.py`) detects all-waves-done plans where Notion status ≠ `Completed`; advisory, fail-closed via `NP_PLAN_DONE_STATUS_FAIL_CLOSED=1`.

## Retrospective-Plan Protocol

A **retrospective plan** documents already-completed work.

> ⛔ **NEVER call `wave_execution_state.py start` on a retrospective plan.** It will flip `Not Started` → `In Progress`, undoing a same-turn `Completed` status.

### Correct protocol

1. Write plan to `.windsurf/plans/<slug>.md`.
2. Register in Notion via `API-post-page` with `status=Completed` directly.
3. Emit `PLAN_COMPLETE: plan=<slug>` in the response (satisfies NP13).
4. Do **NOT** emit `PLAN_CREATED:` marker.
5. Do **NOT** call `wave_execution_state.py start`.

Two guards in `wave_execution_state.py` and `_wave_lifecycle_helpers.py` prevent accidental status flip if `start` is called anyway. CI gate `NP-GUARD` (`check_notion_plan_lifecycle_guard.py`) validates guards are present; fail-closed via `NP_LIFECYCLE_GUARD_FAIL_CLOSED=1`.

## Bypass

- `NOTION_WAVE_DEFERRAL_BYPASS=1` — bypass MCP-call deferral; logged. Use for user-requested mid-plan Notion **MCP reads** only.
- `WAVE_LIFECYCLE_NOTION_BYPASS=1` — skip the sanctioned direct-HTTP writer (logs only, no PATCH). Use when the Notion API is intentionally offline.
- `WAVE_LIFECYCLE_CAPTURE_BYPASS=1` — skip the post-cascade marker hook entirely.
- `PLAN_COMPLETE_AUDIT_BYPASS=1` — suppress the advisory `post_cascade_plan_complete_audit.py` warning.
- `NOTION_PLAN_COMPLETE_BYPASS=1` — skip CI gate NP12 entirely.
- `NOTION_PLAN_COMPLETE_FAIL_CLOSED=1` — flip NP12 to fail-closed (exit 1 on violations).

Constitutional §25, §35, §36.
