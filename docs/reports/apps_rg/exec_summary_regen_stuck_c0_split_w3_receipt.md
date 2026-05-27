# W3 Receipt — exec-summary-regen-stuck-c0-split-a4f8e2

**Wave:** W3 — Brown canonical CLI re-proof vs `230615`  
**Date:** 2026-05-27  
**Status:** PASS

## W3.1 — Brown canonical CLI (parity with baseline)

| Item | Value |
|------|-------|
| Command | `python -m apps_rg --section executive_summary --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md --provider qwen_vllm --temperature 0.45 --allow-non-allow-exit-zero` |
| Artifact dir | [exec_summary_20260527_025447_w3](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_025447_w3) |
| Process exit | `0` (~17.7 min) |
| Preflight | `all_pre_dispatch_gates_passed` (qwen health + model ready) |

## Acceptance vs baseline `exec_summary_20260526_230615`

| Metric | Baseline `230615` | W3 `025447_w3` | Verdict |
|--------|-------------------|----------------|---------|
| `operator_status` | `DRAFT_READY` | `DRAFT_READY` | Parity |
| `x2_product_quality_status` | `PASS` | `PASS` | Parity |
| `x2_claim_field_maps_to_display_sentence` (published X2) | PASS | PASS | **Structural defect resolved** |
| Regen cycles with `x2_claim_field_maps` post-regen fail | **10 / 10** | **0 / 10** | **Improved** |
| `stopped_reason` | (implicit exhaust / `post_regen_x2_failed` per cycle) | `trigger_judge_regression` | Different terminal (not stuck-loop) |
| `regen_lane_stats.stuck_loop_detected` | n/a (pre-W1 schema) | `false` | Stuck-loop did not fire |
| `product_status` | `X3_REVIEW_JUDGE_SOFT_FAIL` | `X3_REVIEW_JUDGE_SOFT_FAIL` | Parity (Claude floor) |

Compare tool:

```text
python tools/apps_rg/compare_exec_summary_w3_brown.py artifacts/.../exec_summary_20260527_025447_w3
→ w3_acceptance_hints all true
```

## Interpretation

- **W2 (claim/proof split)** removed the structural contradiction: published scratch X2 now passes `x2_claim_field_maps_to_display_sentence` (rows 1+5 no longer blocked by I0-banned mechanism/credential prose in `claim_text`).
- **W1 (stuck-loop)** was not needed on this run — regen exhausted on judge regression, not repeated identical X2 row failures.
- Judge certification remains soft-fail (Anthropic); in scope for operator review, not a W3 blocker (same as baseline).

## Marker emitted

```
WAVE_COMPLETE: plan=exec-summary-regen-stuck-c0-split-a4f8e2 wave=3 note="Brown W3 exec_summary_20260527_025447_w3 claim_gate 0/10 regen fails vs baseline 10/10"
```

## Next wave

**W4** — Closeout receipt, Notion Completed, backlog link-up.
