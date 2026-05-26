# W3 Receipt — Best-of Publish (Candidate Pool)

**Plan:** [exec-summary-judge-regen-control-loop-f8a3c2.md](../../.cursor/plans/exec-summary-judge-regen-control-loop-f8a3c2.md)  
**Wave:** W3 (H-1, H-3, H-6)  
**Date:** 2026-05-26

## Summary

Implemented immutable `CandidateSnapshot` pool, full-panel rescore before argmax publish, and artifact rebind from the selected snapshot only. Replaced `last_regen_candidate` publish path with `finalize_pool_publish`.

## Files

- [executive_summary_candidate_pool.py](../../apps_rg/runtime/sections/executive_summary_candidate_pool.py) — new
- [executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py) — pool freeze + publish integration
- [test_executive_summary_candidate_pool.py](../../tests/unit/apps_rg/test_executive_summary_candidate_pool.py) — new

## Artifacts emitted at runtime

- `candidate_pool_summary.json`
- `publish_integrity_receipt.json`

## Proof

```text
pytest tests/unit/apps_rg/test_executive_summary_candidate_pool.py -q -o addopts= → 7 passed
pytest tests/unit/apps_rg/test_executive_summary_g1_ledger_metric_sync.py -q -o addopts= → 3 passed (regression)
Brown 070105 rank fixture test → scratch wins over Claude 4.0→3.6 regen
```

## Caveats

- Plan PASS still requires W5 canonical CLI Brown proof (INV-6).
- `carried_forward` cert block at X3 is W4/W5 scope; publish rank uses `full_panel` only.
