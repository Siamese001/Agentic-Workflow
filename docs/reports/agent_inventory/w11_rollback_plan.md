# W11 Rollback Plan (archive/delete execution)

## Principles

1. **Filesystem SSOT rollback** — restore from `archives/l2_rationalization_<YYYYMMDD>/` manifest, not git history alone.
2. **Import shim first** — if canonical binding breaks, re-export shim before reverting apps_rg.
3. **No production env rollback** — stub/legacy env vars remain until explicitly retired.

## Pre-execution snapshot

```text
git stash / branch: l2-rationalization-w11-exec-<date>
python -m compileall agentic_core apps_rg apps_shared -q
pytest (W10 boundary suite) — must pass before AND after each batch
ADG snapshot id recorded in migration receipt
```

## Rollback triggers

| Trigger | Action |
|---------|--------|
| `compileall` fails | Restore last batch from archive manifest |
| W10 boundary tests fail | Restore + open BLOCKED receipt |
| `test_ag6` / golden path fails | Restore shim OR fix forward (prefer fix forward) |
| CI `check_apps_rg_golden_path_runtime` fails | Restore shim path in CI allowlist |
| Live operator needs `legacy_full_resume` | **Do not delete** rollback env path |

## Per-batch rollback procedure

1. Read `archives/l2_rationalization_<date>/MANIFEST.json` for batch file list.
2. Copy files back to original paths (preserve mode).
3. If imports were rewritten, revert import commits first (single revert commit per batch).
4. Run:

```bash
python -m compileall agentic_core apps_rg apps_shared -q
python -m pytest tests/_apps_contract/test_apps_rg_exit_uwg_l4_no_bypass_boundary.py \
  tests/unit/agentic_core/test_l2_exit_uwg_l4_no_bypass_boundary.py \
  tests/unit/agentic_core/test_l6_current_run_learning_firewall_boundary.py -q -p no:xdist
```

5. Emit `ROLLBACK_COMPLETE: batch=<id> reason=<one-liner>` in migration receipt.

## Shim-specific rollback

If `apps_rg_l2_binding.py` removed before importers migrated:

- Restore `agentic_core/L2_execution/apps_rg_l2_binding.py` re-export shim unchanged.
- Or cherry-pick M1 migration revert only.

## Archive location (planned, not created in W11)

```text
archives/l2_rationalization_<YYYYMMDD>/
  MANIFEST.json
  agentic_core/L2_execution/...
  apps_rg/runtime/...
```

Receipt: `artifacts/governance/migration_receipts/<ts>_l2_rationalization_w11.json`
