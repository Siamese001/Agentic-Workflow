# Executive Summary Regen Voice Repair — W6 E2E Closeout

**Plan:** [exec-summary-regen-voice-repair-unblock-e7c4a2.md](../../.cursor/plans/exec-summary-regen-voice-repair-unblock-e7c4a2.md) (Completed)  
**Plan closeout:** [exec_summary_regen_voice_repair_unblock_closeout_20260526.md](exec_summary_regen_voice_repair_unblock_closeout_20260526.md)  
**Wave:** W6  
**Date:** 2026-05-26  
**Status:** **PARTIAL** (criterion 3 — documented improvement vs baseline narrative; criteria 1–2 not met; plan closed with transport deferred F1–F3)

## Run

| Field | Value |
|-------|-------|
| Run ID | `exec_summary_20260526_224436` |
| Artifact dir | [exec_summary_20260526_224436](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_224436) |
| Command | `python -m apps_rg --section executive_summary` (Brown SVP, `qwen_vllm`, `--allow-non-allow-exit-zero`) |
| Env | `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1`, `APPS_RG_EXEC_SUMMARY_REGEN_CAPS=1` |
| CLI exit | 0 (~181s) |
| Baseline (plan anchor) | [exec_summary_20260526_213359](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_213359) (not present on disk in this workspace; scores taken from plan evidence table) |

## PASS criteria evaluation

| # | Criterion | Result |
|---|-----------|--------|
| 1 | `regen_outcome: accepted` + all judges pass | **FAIL** — `regen_outcome: no_acceptable_candidate`; Anthropic/Gemini below floor |
| 2 | Published regen candidate, X2 PASS, scores ≥ floor | **FAIL** — `final_publish_baseline: scratch`, `publish_selected_snapshot_id: scratch` |
| 3 | PARTIAL: scratch X2 + OpenAI pass; regen/judge improvement vs baseline | **PARTIAL** — see comparison below |

## Baseline vs W6 E2E (scratch / panel)

| Signal | Baseline `213359` (plan) | W6 `224436` |
|--------|--------------------------|-------------|
| Regen cycles | 10 | **2** (`stopped_reason: regen_converged`) |
| `regen_outcome` | `no_acceptable_candidate` | `no_acceptable_candidate` |
| `stopped_reason` | `regen_not_accepted` | **`regen_converged`** |
| OpenAI (cycle 1 `scores_before`) | 4.3 pass | **4.6 pass** |
| Anthropic | 3.5 fail | **3.8 fail** (improved, still below floor) |
| Gemini | 3.0 fail (`resume_voice`) | 3.0 fail (`resume_voice`) |
| `delta_class` (cycles) | `resume_voice_humanize` ×10 | `resume_voice_humanize` ×2 |
| Voice-repair S5 (published) | `capital-markets rigor informs which platform investments…` | **`FSA-certified capital modeling informs which platform investments…`** (W1 metric-grounded; no judge-fail substring) |
| Scratch X2 | PASS (plan) | **PASS** (`product_quality_status: PASS`, `x2_failed_gates: []`) |
| X3 | judge soft-fail pattern | `X3_REVIEW_JUDGE_SOFT_FAIL` (blocking: `anthropic_claude`) |

W1–W5 plumbing behaved as designed: convergence fired after identical `regen_output_hash` on cycle 2; per-cycle receipts exist ([judge_remediation_receipt_cycle_1.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_224436/judge_remediation_receipt_cycle_1.json), [judge_remediation_receipt_cycle_2.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_224436/judge_remediation_receipt_cycle_2.json)).

## Regen did not execute semantic repair (blockers)

Neither cycle produced `draft_parse_ok: true`. Both cycles show the same transport pattern in cycle receipts:

1. **Core runner refused:** `same_authority_regen refused: mocked_provider_allow` ([judge_remediation_receipt_cycle_1.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_224436/judge_remediation_receipt_cycle_1.json) attempt 1).
2. **Thread append blocked:** `block_reason: regen_input_exceeds_available_context_window` (attempt 2).

Therefore:

- No `provider_request_judge_regen_cycle*.json` with `REGEN_DELTA` user turns (surgical verify: `regen_delta_user_turn_seen: false`).
- No `x2_gate_outputs_post_regen_cycle_*.json` (regen never materialized a candidate for post-regen X2).
- Composite `executive_signal_and_voice_v1` was not exercised at runtime: panel snapshot shows Anthropic `major_failed_dimensions: []` while only Gemini lists `resume_voice` — routing stayed on `resume_voice_humanize`.

## Key artifacts

| Artifact | Link |
|----------|------|
| [judge_remediation_cycles.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_224436/judge_remediation_cycles.json) | Regen loop summary |
| [l2_output.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_224436/l2_output.json) | Published scratch display + claim ledger |
| [x3_disposition.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_224436/x3_disposition.json) | Product authorization |
| [publish_integrity_receipt.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_224436/publish_integrity_receipt.json) | Digest match OK |
| W5 verify receipt | [exec_summary_regen_voice_repair_w6_w5_verify_receipt.json](exec_summary_regen_voice_repair_w6_w5_verify_receipt.json) |
| Surgical verify receipt | [exec_summary_regen_voice_repair_w6_surgical_verify_receipt.json](exec_summary_regen_voice_repair_w6_surgical_verify_receipt.json) |

## Verification commands

```bash
# E2E (executed 2026-05-26)
$env:APPS_RG_EXEC_SUMMARY_JUDGE_REGEN='1'
$env:APPS_RG_EXEC_SUMMARY_REGEN_CAPS='1'
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md \
  --provider qwen_vllm \
  --allow-non-allow-exit-zero

python tools/cursor/verify_exec_summary_judge_regen_w5_artifacts.py \
  artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_224436

python tools/cursor/verify_exec_summary_anthropic_surgical_regen.py \
  artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_224436
```

## Recommended follow-up (out of W6 scope)

1. **Unblock regen transport:** resolve `mocked_provider_allow` on `SameAuthorityRegenRunner` for `qwen_vllm` judge-regen path; re-run with real provider allow.
2. **Context budget:** investigate `regen_input_exceeds_available_context_window` for prescriptive delta + incremental anchor payload (see [executive_summary_24k_context_budget_rationalization_20260526.md](executive_summary_24k_context_budget_rationalization_20260526.md)).
3. **Composite delta at runtime:** ensure Anthropic `major_failed_dimensions` populate `executive_signal` / `synthesis_quality` when below floor so W2 composite routes in live panel, not only in unit fixtures.

## Wave receipts (W0–W5)

- [exec_summary_regen_voice_repair_w1_receipt.md](exec_summary_regen_voice_repair_w1_receipt.md) … [w5_receipt.md](exec_summary_regen_voice_repair_w5_receipt.md)
