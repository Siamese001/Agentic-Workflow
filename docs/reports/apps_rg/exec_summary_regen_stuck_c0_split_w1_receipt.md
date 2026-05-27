# W1 Receipt — exec-summary-regen-stuck-c0-split-a4f8e2

**Wave:** W1 — G2 stuck-same-failure early-exit  
**Date:** 2026-05-27  
**Status:** PASS

## W1.1 — Failure-signature helper

| Item | Result |
|------|--------|
| `regen_failure_signature()` | `(failing_gate_ids, row_indexes)` sorted/deduped |
| `x2_failed_row_indexes_from_gates()` | Parses `row_N` from Brown-shaped X2 gate text |
| Constants | `STUCK_LOOP_N_CYCLES=2`, `REGEN_STOPPED_REASON_X2_STUCK=x2_stuck_same_failure` |

## W1.2 — Cycles receipt + regen_lane_stats

| Item | Result |
|------|--------|
| `finalize_regen_cycle_observability` | Stuck checked **before** `regen_converged` hash equality |
| Cycle row fields | `post_regen_x2_failed_row_indexes`, `x2_stuck_same_failure` |
| Receipt fields | `stopped_reason`, `stuck_signature`, `regen_lane_stats` |
| `finalize_judge_regen_cycles_receipt` | Always emits `regen_lane_stats` rollup |

Lane loop unchanged structurally: existing `if _conv: break` handles `REGEN_STOPPED_REASON_X2_STUCK`.

## W1.3 — Tests

```text
pytest tests/unit/apps_rg/test_executive_summary_regen_cycle_observability.py -o addopts=
→ 9 passed (3 prior + 6 new stuck-loop cases)
```

Coverage:

- Brown-shaped gate parses rows 1+5
- Two cycles, distinct hashes, same signature → `x2_stuck_same_failure` at cycle 2
- Different row indexes on cycle 2 → no stuck
- Same signature + identical hash → stuck wins over converge (design precedence)

## Marker emitted

```
WAVE_COMPLETE: plan=exec-summary-regen-stuck-c0-split-a4f8e2 wave=1 note="+6 stuck-loop tests, executive_summary_regen_observability.py, regen_lane_stats"
```

## Next wave

**W2** — C0 `claim_text` / `proof_text` ledger split + two-fact migration.
