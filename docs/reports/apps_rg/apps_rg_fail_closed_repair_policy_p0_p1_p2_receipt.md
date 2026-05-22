# apps_rg fail-closed + counted repair policy — completion receipt

**Plan SSOT:** [.cursor/plans/apps-rg-fail-closed-repair-f8c4e2.md](../../.cursor/plans/apps-rg-fail-closed-repair-f8c4e2.md)  
**Status:** Completed (2026-05-22)  
**Scope:** P0 pointer/status fail-closed · P1 repair ledger · P2 phase0 isolation

## Summary

Product runs no longer assemble from stale/mock/phase0 lane dirs. Bounded repairs are logged in `section_repair_ledger.json`; PASS requires authoritative attempt alignment with X2. Deterministic rewrites block product PASS unless a counted regen succeeds.

## Waves

| Wave | Result |
|------|--------|
| P0 | Successful-pointer-only; REAL_LLM+PASS bar; phase-1 fail-fast; companion narrative preflight |
| P1 | Ledger + policy + all 7 lanes; 6 ledger unit tests |
| P2 | Phase0 blocked on product; judge-safe off; package contract harness |

## Proof

```text
pytest tests/unit/apps_rg/runtime/test_section_repair_ledger_p1.py \
  tests/unit/apps_rg/runtime/test_product_fail_closed_p0.py \
  tests/unit/apps_rg/runtime/validators/test_companion_bullet_fail_closed.py \
  tests/_apps_contract/test_resume_package_x3.py \
  tests/_apps_contract/test_executive_summary_x2_x1d_alignment.py \
  -o addopts= -q
→ 44 passed
```

## Key modules

- [section_repair_ledger.py](../../apps_rg/runtime/section_repair_ledger.py)
- [section_repair_lane_integration.py](../../apps_rg/runtime/section_repair_lane_integration.py)
- [product_output_policy.py](../../apps_rg/runtime/product_output_policy.py)
