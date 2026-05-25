# L6 Follow-Up W0–W4 Batch Receipt

**Plan:** [l6-reorg-deferred-followup-f3a9c2](../../.cursor/plans/l6-reorg-deferred-followup-f3a9c2.md)  
**Status:** PASS (W2 burndown count documented-over-threshold; ADG full regen deferred)

## Waves

| Wave | Status | Artifacts |
|------|--------|-----------|
| W0 | PASS | [l6_followup_w0_receipt_20260525.md](l6_followup_w0_receipt_20260525.md), [l6_followup_w0_reconcile_20260525.json](l6_followup_w0_reconcile_20260525.json) |
| W1 | PASS | [ADR-087](../../architecture/adr/ADR-087-l6-passive-layout-followup.md), [ADR-086](../../architecture/adr/ADR-086-l6-eval-surface-consolidation.md) |
| W2 | PASS (documented) | [check_l6_architectural_exceptions.py](../../ops_scripts/ci/check_l6_architectural_exceptions.py); 43 dedup pairs |
| W3 | PASS | [l6_category_a_shared_spike_20260525.md](l6_category_a_shared_spike_20260525.md) |
| W4 | PASS | [engines/README.md](../../agentic_core/L6_system_learning/engines/README.md) |

## Proof

- `python ops_scripts/ci/check_l6_architectural_exceptions.py` (fail-closed) → OK
- `python tools/_oneoff/l6_e2e_closeout_verify.py` → **21/21 PASS**
- `pytest tests/unit/agentic_core/L6_observability/test_otel_runtime_ingest.py` → 3 passed

## Notes

- L_OPS eval modules were already canonical at `ops_scripts/reports/`; L6 paths are compat shims only.
- Edge count remains **86 raw / 43 dedup** — amendment in [architectural_exceptions.yaml](../../config/architectural_exceptions.yaml) (`plan_id` → follow-up plan).
