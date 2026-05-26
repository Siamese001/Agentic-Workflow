# Governance dedup E2E verification — 2026-05-26

**Plan:** `governance-dedup-closeout-e8a4c2`  
**Runner:** [governance_dedup_e2e_verify.py](../../tools/cursor/governance_dedup_e2e_verify.py)  
**Status:** PASS

## What was exercised

| Layer | Checks |
|-------|--------|
| Artifacts | Closeout + W0–W4 receipts, sprawl CSV, demotion map, archive dirs |
| Manifest | `governance_dedup_closeout_receipt.json` schema (gaps, waves, metrics) |
| Structural | `hooks.json` → dispatch only; 0 windsurf `always_on`; plans ≤ 20 |
| CI gates | AG wiring, agents sync, optimized config, rules index, token budget, native config strict, hook matrix |
| Tests | `tests/unit/ops_scripts/hooks/cursor/` + `test_check_ag_hook_wiring.py` (**57 passed**) |

## Re-run

```bash
python tools/cursor/governance_dedup_e2e_verify.py
```

Machine-readable output: [governance_dedup_e2e_verify_20260526.json](governance_dedup_e2e_verify_20260526.json)
