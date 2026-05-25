# ADG Action Dispatch — Plan Closeout Receipt

**Plan:** [adg-action-dispatch-c9e4a2.md](../../.cursor/plans/adg-action-dispatch-c9e4a2.md)  
**Date:** 2026-05-25

## STATUS: PASS

## FILES_CHANGED

- [adg-action-dispatch-c9e4a2.md](../../.cursor/plans/adg-action-dispatch-c9e4a2.md)
- [adg_action_dispatch_playbook.md](adg_action_dispatch_playbook.md)
- [adg_action_dispatch_plan_index.md](adg_action_dispatch_plan_index.md)
- [adg-post-run-burndown.mdc](../../.cursor/rules/adg-post-run-burndown.mdc)
- [adg_action_queue.schema.json](../../.cursor/schemas/adg_action_queue.schema.json)
- [adg_action_queue.py](../../tools/reports/adg_action_queue.py)
- [generate_full_adg.py](../../tools/generate/generate_full_adg.py)
- [hotspot_gate_linkage.py](../../tools/adg/hotspot_gate_linkage.py)
- [scan_apps_hotspots.py](../../tools/adg/scan_apps_hotspots.py)
- [adg_burndown_report.py](../../tools/reports/adg_burndown_report.py)
- [adg_fix_backlog_sync.py](../../tools/notion/adg_fix_backlog_sync.py)
- [test_adg_action_queue.py](../../tests/unit/tools/reports/test_adg_action_queue.py)
- [test_hotspot_gate_linkage.py](../../tests/unit/tools/adg/test_hotspot_gate_linkage.py)
- [test_adg_burndown_next_action.py](../../tests/unit/tools/reports/test_adg_burndown_next_action.py)
- [test_adg_fix_backlog_sync.py](../../tests/unit/tools/notion/test_adg_fix_backlog_sync.py)

## COMMANDS_RUN

| Command | Result |
|---------|--------|
| `python -m pytest tests/unit/tools/reports/test_adg_action_queue.py -q -o "addopts=-v --tb=short"` | exit 0, **7 passed** |
| `python -m pytest tests/unit/tools/adg/test_hotspot_gate_linkage.py tests/unit/tools/reports/test_adg_burndown_next_action.py -q -o "addopts=-v --tb=short"` | exit 0, **6 passed** |
| `python -m pytest tests/unit/tools/notion/test_adg_fix_backlog_sync.py tests/unit/tools/reports/test_adg_action_queue.py -q -o "addopts=-v --tb=short"` | exit 0, **13 passed** |
| `python tools/reports/adg_action_queue.py --latest --top 10 --format markdown` | exit 0 |
| `python tools/reports/adg_burndown_report.py --out artifacts/adg/adg_burndown_report.md` (canvas bypass env) | exit 0 |
| `python tools/adg/scan_apps_hotspots.py` | exit 0, 6 hotspot reports |
| `python tools/notion/adg_fix_backlog_sync.py --latest --dry-run` | exit 0, 3 FIX payloads |
| `python tools/notion/plan_notion_sync_adg_action_dispatch_closeout.py` | exit 0, Plans Status=Completed |
| `python tools/notion/adg_fix_backlog_sync.py --latest --apply` | exit 0, **3** Backlog rows created |

## TESTS_GATES

- W1 queue builder + schema validation + TRACK exclusion — PASS (7 tests)
- W2 hotspot linkage + burndown `## Next action` — PASS (6 tests)
- W3 Notion FIX sync (skip token, dry-run, API failure path) — PASS (6 tests)

## QUEUE_ARTIFACT

[adg_action_queue_20260525_130122.json](../../artifacts/adg/adg_action_queue_20260525_130122.json)

## QUEUE_TOP_3

| Rank | Target | ordering_reason | signal (truncated) |
|-----:|--------|-----------------|---------------------|
| 1 | `B2_layer_skip_ratchet` | fix_regr_p1_delta_asc | Counts: Import edges that skip more than one layer ordinal (layer-hop). Sub: +21 vs baseline 954. |
| 2 | `F1_untyped_seam_ratchet` | fix_regr_p2_delta_asc | Counts: Cross-layer imports where target has empty type_surface. Sub: +27 vs baseline 1078. |
| 3 | `Q2_cyclomatic_complexity_ratchet` | fix_regr_p3_delta_asc | Counts: Functions with McCabe cyclomatic complexity above ceiling. Sub: +1 vs baseline 910. |

## DEGRADED_INPUTS

NONE (`provenance.degradation_reasons` empty on live queue)

## ARTIFACTS

- [adg_action_queue_20260525_130122.json](../../artifacts/adg/adg_action_queue_20260525_130122.json)
- [adg_burndown_report.md](../../artifacts/adg/adg_burndown_report.md)
- [apps_lic_hotspots_20260525T132938Z.md](../adg/apps_lic_hotspots_20260525T132938Z.md) (+ 5 sibling `apps_*_hotspots_*` under `docs/reports/adg/`)

## NON_CLAIMS

```
NON_CLAIMS:
- no auto-repair from queue rows
- no TRACK mass cleanup in this plan
- no gate weakening or ratchet baseline changes
- no agentic_core changes
- W3 Notion sync is optional and not ADG certification
```

## NOTES

- `--apply` Notion sync not run in this closeout (dry-run only); operator runs `python tools/notion/adg_fix_backlog_sync.py --latest --apply` when `NOTION_TOKEN` is set.
- Burndown regen may require `ADG_BURNDOWN_CANVAS_BYPASS=1` if canvas sort fails; markdown SSOT still writes.
