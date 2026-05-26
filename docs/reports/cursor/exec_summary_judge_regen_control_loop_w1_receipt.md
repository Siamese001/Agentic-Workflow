# W1 Receipt — exec-summary-judge-regen-control-loop-f8a3c2

**Wave:** W1 — G3 trigger-judge monotonicity  
**Date:** 2026-05-26  
**Status:** PASS (unit + fixture replay; live Brown CLI deferred to W5)

## Delivered

| Phase | Deliverable | Status |
|-------|-------------|--------|
| W1.0 | `evaluate_g3_trigger_judge_monotonicity()` deterministic table | DONE |
| W1.1 | Wired post soft-rescore in `executive_summary_lane.py`; `trigger_judge_unknown` / `trigger_judge_regression` | DONE |
| W1.2 | Negative tests + Brown `070105` fixture replay | DONE |

## G3 semantics (implemented)

- Evaluated per **soft-failed** trigger judge after soft-failed-only rescore.
- Uses holistic `score` (0–5) with `normalized_score×5` fallback.
- Tie-break: fewer major dimension fails → PASS; equal score + unchanged verdicts → REJECT (`trigger_judge_regression`).
- Missing after score or dimension verdicts on tie → `trigger_judge_unknown`.

## Lane behavior

After post-regen X2 pass + rescore:

1. Run G3; write `g3_trigger_judge_cycle_N.json`.
2. On G3 fail: `accepted=false`, `publish_eligible=false`, `reject_gate` set; revert lane state to pre-regen (`_pre_*`); do not commit regen X1D/L2.
3. On G3 pass: `publish_eligible=true`; commit rescore + artifacts as before.

## Brown fixture replay

`artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_070105/judge_remediation_cycles.json` cycle 1:

- Claude **4.0 → 3.6** → G3 **REJECT** (`trigger_judge_regression`).
- Matches plan acceptance: cycle 1 would be `publish_eligible: false`.

## Tests

```
pytest tests/unit/apps_rg/test_executive_summary_judge_remediation.py -q -o addopts=  → 20 passed
pytest tests/unit/apps_rg/test_executive_summary_judge_regen_loop.py -q -o addopts=  → (see command output)
```

## Marker

```
WAVE_COMPLETE: plan=exec-summary-judge-regen-control-loop-f8a3c2 wave=1 note="+4 g3 tests, 3 files, scope=G3-monotonicity"
```

## Next

**W2** — G1 ledger metric sync (deterministic, fail-closed).
