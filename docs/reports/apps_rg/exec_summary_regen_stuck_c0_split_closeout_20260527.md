# exec-summary-regen-stuck-c0-split-a4f8e2 — plan closeout (W0–W4) COMPLETE

**Plan:** [.cursor/plans/exec-summary-regen-stuck-c0-split-a4f8e2.md](../../.cursor/plans/exec-summary-regen-stuck-c0-split-a4f8e2.md)  
**Notion:** `36d27693-f55c-81d7-847a-c34cd7807849` — **Completed**  
**Parent closeout (defect capture):** [complete-open-scope-closeout-c9e4a1](../../.cursor/plans/complete-open-scope-closeout-c9e4a1.md)

```text
STATUS: PASS
FILES_CHANGED:
- [executive_summary_regen_observability.py](../../apps_rg/runtime/sections/executive_summary_regen_observability.py)
- [claim_proof_split_policy.py](../../apps_rg/fact_inventory/claim_proof_split_policy.py)
- [candidate_fact_ledger.py](../../apps_rg/fact_inventory/candidate_fact_ledger.py)
- [migrate_claim_proof_split_w2.py](../../tools/apps_rg/migrate_claim_proof_split_w2.py)
- [audit_fact_ledger_claim_proof_split.py](../../tools/apps_rg/audit_fact_ledger_claim_proof_split.py)
- [compare_exec_summary_w3_brown.py](../../tools/apps_rg/compare_exec_summary_w3_brown.py)
- [w4_exec_summary_regen_stuck_c0_split_closeout.py](../../tools/notion/w4_exec_summary_regen_stuck_c0_split_closeout.py)
COMMANDS_RUN:
- pytest regen + claim_proof contract (14) -> PASS
- audit_fact_ledger_claim_proof_split -> 0/42 failures
- Brown CLI exec_summary_20260527_025447_w3 -> exit 0, DRAFT_READY
- python tools/notion/w4_exec_summary_regen_stuck_c0_split_closeout.py -> plan Completed + backlog Done
TESTS_GATES:
- W1 stuck-loop tests (6) + W2 contract (5) + regen observability -> 14 passed
- W2 audit -> PASS
- W3 Brown compare hints -> all true
ARTIFACTS:
- [exec_summary_regen_stuck_c0_split_design_lock.json](../../artifacts/apps_rg/exec_summary_regen_stuck_c0_split_design_lock.json)
- [exec_summary_20260527_025447_w3](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_025447_w3)
REPORTS_GENERATED:
- [exec_summary_regen_stuck_c0_split_w0_receipt.md](exec_summary_regen_stuck_c0_split_w0_receipt.md)
- [exec_summary_regen_stuck_c0_split_w1_receipt.md](exec_summary_regen_stuck_c0_split_w1_receipt.md)
- [exec_summary_regen_stuck_c0_split_w2_receipt.md](exec_summary_regen_stuck_c0_split_w2_receipt.md)
- [exec_summary_regen_stuck_c0_split_w3_receipt.md](exec_summary_regen_stuck_c0_split_w3_receipt.md)
- [exec_summary_regen_stuck_c0_split_closeout_20260527.md](exec_summary_regen_stuck_c0_split_closeout_20260527.md)
NOTES:
- f8a3c2 judge-regen control-loop plan NOT reopened (per design lock).
- X3 remains REVIEW (Anthropic); out of scope — parity with baseline 230615.
```

## Problem → fix

| Defect | Fix | Proof |
|--------|-----|-------|
| G2: 10 regen cycles on same `x2_claim_field_maps` (rows 1+5) | `x2_stuck_same_failure` when signature repeats ≥2 cycles | [w1_receipt](exec_summary_regen_stuck_c0_split_w1_receipt.md); 6 unit tests |
| C0: I0-banned prose in `claim_text` vs X2 verbatim match | `claim_text` display / `proof_text` provenance split + 2-fact migration | [w2_receipt](exec_summary_regen_stuck_c0_split_w2_receipt.md); audit 0/42 |

## Wave summary

| Wave | Status | Receipt |
|------|--------|---------|
| W0 | PASS | [w0](exec_summary_regen_stuck_c0_split_w0_receipt.md) |
| W1 | PASS | [w1](exec_summary_regen_stuck_c0_split_w1_receipt.md) |
| W2 | PASS | [w2](exec_summary_regen_stuck_c0_split_w2_receipt.md) |
| W3 | PASS | [w3](exec_summary_regen_stuck_c0_split_w3_receipt.md) |
| W4 | PASS | this file |

## Brown W3 vs baseline `230615`

| Metric | Baseline | W3 `025447_w3` |
|--------|----------|----------------|
| `DRAFT_READY` | yes | yes |
| Published `x2_claim_field_maps_to_display_sentence` | PASS | PASS |
| Regen cycles with post-regen claim-map fail | 10/10 | **0/10** |
| `stopped_reason` | per-cycle X2 fail pattern | `trigger_judge_regression` |
| `stuck_loop_detected` | n/a | `false` |

## Definition of Done

| DoD | Status |
|-----|--------|
| DoD-1 Stuck-loop fixture test | DONE |
| DoD-2 Ledger audit | DONE |
| DoD-3 X2 contract | DONE |
| DoD-4 Regen pytest slice | DONE (14 tests) |
| DoD-5 Brown CLI artifact | DONE |
| DoD-6 Notion + backlog linked | DONE (W0 link, W4 Done) |
| DoD-7 Closeout + PLAN_COMPLETE | DONE |

## Backlog closure

| Item | Notion | Closure |
|------|--------|---------|
| G2 stuck-loop early-exit | [link](https://www.notion.so/Exec-summary-regen-G2-stuck-loop-early-exit-same-X2-row-fails-N-times-36c27693f55c81d4b75ef9ac99509a07) | **Done** — W1 shipped |
| C0 claim/proof split | [link](https://www.notion.so/Exec-summary-C0-fact-split-claim_text-display-allowed-vs-proof_text-full-body-36c27693f55c81b7916dc2a65edde07f) | **Done** — W2+W3 shipped |

## Out of scope (explicit)

- Anthropic judge certification (`X3_REVIEW_JUDGE_SOFT_FAIL`) — unchanged from Brown baseline; follow existing judge/regen quality plans.
- Reopening [f8a3c2](../../.cursor/plans/_archive/2026-05/exec-summary-judge-regen-control-loop-f8a3c2.md).
