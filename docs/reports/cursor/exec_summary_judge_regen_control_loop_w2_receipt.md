# W2 Receipt — exec-summary-judge-regen-control-loop-f8a3c2

**Wave:** W2 — G1 ledger metric integrity  
**Date:** 2026-05-26  
**Status:** PASS (unit + Brown row-3 fixture; live CLI deferred to W5)

## Delivered

| Phase | Deliverable | Status |
|-------|-------------|--------|
| W2.0 | `sync_claim_ledger_metrics_from_facts()` fail-closed | DONE |
| W2.1 | Candidate-local G1 in judge regen prepare path + per-row receipt | DONE |

## G1 behavior

- Runs on the **candidate** `parsed` after `prepare_parsed_after_judge_regen` + ledger preserve (before post-regen X2).
- **Single source:** exactly one cited fact supplies the canonical `%` metric.
- **Repair:** `claim_text`, `claim`, and `resume_display_text` aligned to fact metric.
- **Ambiguity:** conflicting facts, missing metrics, or multi-source → `reject_gate=ledger_metric_sync_ambiguous`; cycle rejected (same revert path as G3).

## Artifacts per cycle

- `g1_ledger_metric_sync_receipt.json`
- Embedded in `judge_regen_prepare_receipt.json` under `g1_ledger_metric_sync`

## Brown fixture (row 3)

`exec_summary_20260526_070105` claim_ledger row 3:

- Before: `claim_text` … **10%** (fact supports **40%**)
- After G1: `claim_text` … **40%**
- Prevents `claim_ledger_row_3_metric_mismatch` from regen corrupting ledger vs facts.

## Tests

```
pytest tests/unit/apps_rg/test_executive_summary_g1_ledger_metric_sync.py -q -o addopts=  → 3 passed
pytest tests/unit/apps_rg/test_executive_summary_judge_remediation.py -q -o addopts=  → 20 passed
```

## Marker

```
WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=2 note="+3 g1 tests, 2 files, scope=G1-ledger-metric-sync; 070105 row3 10%→40%"
```

## Next

**W3** — `CandidateSnapshot`, full-panel publish rank, artifact rebind.
