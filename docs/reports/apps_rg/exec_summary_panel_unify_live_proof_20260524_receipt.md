# Executive Summary — Panel-Unify Live Proof

**Run ID:** `exec_summary_20260524_140149`  
**Date:** 2026-05-24  
**Purpose:** Verify all three X1D judges grade the same post-X2 packet after panel-unify lane fix.

## Command

```text
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**Log:** [_panel_unify_live.log](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/_panel_unify_live.log)

## Step 2 — Packet alignment (PASS)

| Provider | Final request artifact | `canonical_contract_hash` | `judge_packet_hash` (x1d output) |
|----------|------------------------|---------------------------|----------------------------------|
| Gemini | [x1d_gemini_pro_provider_request_20260524_140306_683.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/x1d_gemini_pro_provider_request_20260524_140306_683.json) | `472263cc72696781…` | `1835e270051ad620` |
| OpenAI | [x1d_openai_chatgpt_provider_request_20260524_140317_806.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/x1d_openai_chatgpt_provider_request_20260524_140317_806.json) | `472263cc72696781…` | `1835e270051ad620` |
| Claude | [x1d_anthropic_claude_provider_request_20260524_140325_587.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/x1d_anthropic_claude_provider_request_20260524_140325_587.json) | `472263cc72696781…` | `1835e270051ad620` |

Post-X2 packet SSOT: [executive_summary_judge_packet_post_x2.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/executive_summary_judge_packet_post_x2.json) — same `resume_display_text` as [resume_display_text.txt](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/resume_display_text.txt).

Refresh receipt: [post_x2_x1d_refresh_receipt.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/post_x2_x1d_refresh_receipt.json) (prior Claude 2.4 → refreshed 3.2 on aligned packet).

**Note:** Three judge-regen cycles ran but all reverted (`post_regen_x2_failed_after_x2_repair`); no `post_regen_x1d_full_refresh_receipt.json` — regen never committed. Final quorum is from post-X2 full refresh only.

## Step 3 — Outcome with aligned panel

| Provider | Score | Status |
|----------|-------|--------|
| Gemini | 4.5 | `MODEL_BACKED_PASS` |
| OpenAI | 4.2 | `MODEL_BACKED_PASS` |
| Claude | 3.2 | `MODEL_BACKED_FAIL` (`provider_blocked: false`) |

**Operator:** `DRAFT_READY` (exit 0), `CERTIFIED: false`, `PRODUCT_STATUS: X3_REVIEW_JUDGE_SOFT_FAIL`.

**Conclusion:** Input drift is ruled out for the final panel. Claude failure is residual synthesis/JD-emphasis scoring (bullet-stack, weak insurance-brokerage targeting, thin S6) — same themes as OpenAI/Gemini findings, stricter bar.

## Artifacts

- [x1d_llm_judge_outputs.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/x1d_llm_judge_outputs.json)
- [canonical_judge_contract.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/canonical_judge_contract.json)
- [judge_remediation_cycles.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/judge_remediation_cycles.json)
