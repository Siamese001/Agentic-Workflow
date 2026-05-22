# apps_rg legacy SRFS JSON purge — plan closeout

**Plan:** [apps-rg-legacy-srfs-json-purge-a8f3c1.md](../../.cursor/plans/apps-rg-legacy-srfs-json-purge-a8f3c1.md)  
**Status:** PASS (waves D1–D5 complete; deferred items closed or documented)  
**Date:** 2026-05-22

## Wave receipts

| Wave | Receipt |
|------|---------|
| D1 | [apps_rg_legacy_srfs_json_purge_d1_receipt.md](apps_rg_legacy_srfs_json_purge_d1_receipt.md) |
| D2 | [apps_rg_legacy_srfs_json_purge_d2_receipt.md](apps_rg_legacy_srfs_json_purge_d2_receipt.md) |
| D3 | [apps_rg_legacy_srfs_json_purge_d3_receipt.md](apps_rg_legacy_srfs_json_purge_d3_receipt.md) |
| D4 | [apps_rg_legacy_srfs_json_purge_d4_receipt.md](apps_rg_legacy_srfs_json_purge_d4_receipt.md) |
| D5 | [apps_rg_legacy_srfs_json_purge_d5_receipt.md](apps_rg_legacy_srfs_json_purge_d5_receipt.md) |

## Deferred scope closure

All items deferred in D1/D2 receipts are **closed** by D3–D5:

- Runtime no longer requires `artifacts/.../selected_role_fact_set_active.json` on product paths.
- `srfs_integration` / `artifact_path_resolved` removed from PA assembly, evidence capsule compile, and token-budget pool detection.
- Aggregator, audit judge, and hot-path JSON writers removed (D3/D4).

## Operational follow-on (not plan-blocking)

Live provider proof remains **BLOCKED** when `APPS_RG_L2_PROVIDER_MODE=stub_only`:

```text
python -m apps_rg --section executive_summary --provider qwen_vllm --allow-non-allow-exit-zero
python ops_scripts/apps_rg/run_live_section_authority_proof.py
```

Run when live Qwen vLLM is available; pytest gates for D1–D5 already PASS per wave receipts.

## D5 final pytest (closeout session)

```text
29 passed, 1 skipped, 0 failed
```

(See [d5_receipt](apps_rg_legacy_srfs_json_purge_d5_receipt.md) for command list.)

## Disk + Notion

- Plan status on disk: **Completed**
- Notion Plans row: synced via `tools/notion/plan_notion_sync_apps_rg_legacy_srfs_json_purge.py` → **Completed**
