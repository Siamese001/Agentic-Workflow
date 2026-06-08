# Terminal Cleanup Backlog

Captured on 2026-06-08 from:

```text
python ops_scripts/ci/check_terminal_cleanup.py
```

The full-repo scan currently reports 43 known violations across 32 files. PR CI now uses `--fail-on-new-only`, so unrelated changes are not blocked by this backlog while changed files remain unable to introduce terminal/subprocess cleanup debt.

## Triage Order

1. `agentic_core`: production-path process lifecycle and safety utilities.
2. `apps_rg`: app runtime and fact-inventory helpers.
3. `ops_scripts`: CI and operational scripts.
4. `tools/debug`: archival/debug move helpers.
5. `tools/demos`: demo-only process spawning.
6. `tools/notion` and `tools/_oneoff`: lower-priority migration helpers.

## Current Counts

| Group | Violations |
| --- | ---: |
| `agentic_core` | 5 |
| `apps_rg` | 5 |
| `ops_scripts` | 19 |
| `tools/adg`, `tools/analysis` | 2 |
| `tools/debug` | 8 |
| `tools/demos` | 1 |
| `tools/notion`, `tools/_oneoff` | 3 |

Machine-readable baseline: `docs/reports/ci/terminal_cleanup_backlog.json`.
