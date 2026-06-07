
# ADG Post-Run Burndown — FIX-First Dispatch

> Gate tables are **markdown**, not a 500-line JSON blob inside `.canvas.tsx`.  
> **Next action** comes from the action queue when present; otherwise burndown § Fix now + [playbook](docs/reports/cursor/adg_action_dispatch_playbook.md).

## When this rule fires

After ADG runs, burndown refresh, or user asks for gate status / burndown / next action.

## Protocol (order matters)

1. **Burndown tables (required):** Open [artifacts/adg/adg_burndown_report.md](artifacts/adg/adg_burndown_report.md) — Markdown preview (`Ctrl+Shift+V`) or stderr `READABLE_TABLES=...` from `python tools/reports/adg_burndown_canvas.py`.
2. **Action queue (when present):** If `artifacts/adg/adg_action_queue_<ts>.json` exists (or stderr `NEXT_ACTION=...`), load it before proposing work. Respect `emit_status` (`ok` | `degraded` | `failed`) and `provenance.degraded`. After W1: `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown`.
3. **Operator playbook:** Follow [docs/reports/cursor/adg_action_dispatch_playbook.md](docs/reports/cursor/adg_action_dispatch_playbook.md) — 15-minute ladder, P7 routing, ADG_REPAIR_LITMUS, TRACK deferral only.
4. **Refresh burndown:** `python tools/reports/adg_burndown_canvas.py` (regenerates markdown + optional compact canvas).
5. **Chat inline:** Paste stdout from `python tools/reports/adg_burndown_report.py` if needed — do not paraphrase gate counts.
6. **Canvas (optional):** Compact summary only. Full 48-gate grid is **not** in canvas source.

## FIX-first rules

- **FIX** (FAIL / REGR / SEED): one gate or one file this session; block before regr; smallest regression delta first among REGR.
- **TRACK** (DEBT / OPEN / ADVIS): never same-day mass fix; never auto-create backlog rows for all TRACK gates; defer to plan wave + `DEFERRED_SCOPE`.
- **Queue / actions:** TRACK verdicts are never emitted to `actions[]` (W1 contract). Do not outrank FIX with refactor candidates while FIX exists.
- **Stale clusters:** Do not use `artifacts/adg_failure_clusters.json` for ordering unless `snapshot_ts` matches active `adg_gate_results_*.json`.

## stderr contract (W1+ full gen)

| Line | Meaning |
|------|---------|
| `NEXT_ACTION=<path>` | Queue written; use `actions[0]` |
| `NEXT_ACTION_DEGRADED=1` | Optional inputs missing; FIX-only queue |
| `NEXT_ACTION_ERROR=...` | Queue emit failed; use burndown FIX table; **do not** treat as ADG pass |

## Forbidden

- Pointing users at raw `.canvas.tsx` as the gate table.
- Replacing markdown tables with prose summaries of counts.
- TRACK mass cleanup or auto-repair from queue rows without ADG_REPAIR_LITMUS.
- Inventing gate↔module links (W2: deterministic `linkage_source` only).

## Bypass

- `ADG_BURNDOWN_CANVAS_BYPASS=1` — skip canvas write
- `ADG_BURNDOWN_NO_OPEN=1` — do not `cursor -r` open files
- `ADG_BURNDOWN_INLINE_BYPASS=1` — skip stdout markdown

## References

- [adg_action_dispatch_playbook.md](docs/reports/cursor/adg_action_dispatch_playbook.md)
- [adg-action-dispatch-c9e4a2.md](.claude/plans/adg-action-dispatch-c9e4a2.md)
- [tools/reports/adg_burndown_report.py](tools/reports/adg_burndown_report.py)
- [tools/reports/adg_burndown_canvas.py](tools/reports/adg_burndown_canvas.py)
- [tools/reports/adg_action_queue.py](tools/reports/adg_action_queue.py) (W1)
