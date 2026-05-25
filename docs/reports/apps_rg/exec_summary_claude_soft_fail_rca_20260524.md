# RCA: Claude X1D Soft-Fail (Not Blocked) — Executive Summary

**Evidence run:** [exec_summary_20260524_140149](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/)  
**Panel-unify proof:** [exec_summary_panel_unify_live_proof_20260524_receipt.md](exec_summary_panel_unify_live_proof_20260524_receipt.md)

## Executive summary

Claude is **`MODEL_BACKED_FAIL` (score 3.2)**, not blocked. On the aligned panel (`judge_packet_hash` **`1835e270051ad620`**, `canonical_contract_hash` **`472263cc…`** for all three providers), Gemini/OpenAI pass (4.5 / 4.2) while Claude fails. Root cause is a **three-layer gap**: (1) **X2 synthesis heuristics are weaker than X1D residual quality**, (2) **proof-pool / prose shape mismatches Brown & Brown IT-innovation targeting**, and (3) **judge-regen repair cannot land** because rewrites trip **`x2_source_sensitive_phrases_supported`**. Transport and packet parity are ruled out.

---

## Ruled out

| Hypothesis | Evidence |
|------------|----------|
| Claude provider blocked | `provider_available: true`, `provider_blocked: false`, live HTTP 200 in [x1d_anthropic_claude_provider_response_raw_20260524_140347_605.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/x1d_anthropic_claude_provider_response_raw_20260524_140347_605.json) |
| Split judge panel (stale OpenAI vs fresh Claude) | Final trio shares `1835e270051ad620` in [x1d_llm_judge_outputs.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/x1d_llm_judge_outputs.json) |
| Different rubric / contract per provider | Same `JUDGE_CONTRACT_HASH` and full user prompt in all three `x1d_*_provider_request_*` artifacts |
| Post-parse reconcile laundering Claude fail | `reconcile_grade_only_judge_result` only suppresses findings tied to **passed** gates; Claude’s fail reasons are **residual** (synthesis, JD emphasis) — score unchanged |
| Anthropic “minimal system” drift | `_call_anthropic` uses `build_x1d_judge_system_prompt(compact=True)` — same shared contract as OpenAI/Gemini ([executive_summary_x1d.py](apps_rg/runtime/judges/executive_summary_x1d.py) ~1108) |

---

## Root cause 1 — X2 / X1D criteria mismatch (primary)

**Symptom:** `x2_executive_summary_synthesis_quality: pass` but Claude cites `bullet_stack_prose`, thin S6, weak role-family targeting.

**Mechanism:** X2 `check_synthesis_quality()` mostly counts **action-verb openers** and mechanical patterns ([executive_summary_x2.py](apps_rg/runtime/validators/executive_summary_x2.py) ~370–431). Baseline prose has only **one** `ACTION_VERB_OPENERS` sentence (`Built…`); openers are `Technology`, `Platform`, `Basel`, `Monolithic`, `Built`, `Governed` — a **semantic accomplishment stack** that passes X2 but fails Claude’s rubric dim 2/6.

The judge rubric explicitly states (**GRAPH_ONLY_GRADE_ONLY_RUBRIC**):

> Residual quality (always in scope — not closed by X2 alone): executive clarity, narrative coherence, commercial fit…

So Claude is **contractually correct** to fail sub-4.0 while all X2 gates pass.

**OpenAI on the same text** lists “achievement stacking” and “insurance fit implied” but still scores **4.2** — **provider calibration**, not packet drift.

---

## Root cause 2 — Targeting vs proof pool (content)

JD + briefing target **`INSURANCE_BROKERAGE_IT_INNOVATION`** (in gate `x2_exec_summary_jd_alignment_proof_flags`). Selected C0 facts are **platform / governance / quant-HPC** ([selected_fact_plan.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/selected_fact_plan.json) — 7 facts, no brokerage-distribution fact). Claude penalizes missing federated architecture, interoperability, innovation-incubation **emphasis** without inventing claims — valid under dim 4/6 when JD is targeting context.

`fact_certs_001` is **unused** (allowed weave); regen cycles try to weave certs and break X2.

---

## Root cause 3 — Judge regen cannot fix Claude (repair loop)

Three regen cycles in [judge_remediation_cycles.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/judge_remediation_cycles.json); all **`reverted: post_regen_x2_failed_after_x2_repair`**.

**Example (cycle 1):** Qwen regen adds *“enhancing **audit-ready** delivery”* ([provider_response_judge_regen.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_140149/provider_response_judge_regen.json)). Reproduction:

```text
baseline  → check_source_sensitive_phrases: PASS
regen     → FAIL: Unsupported sensitive phrases: ['audit']
```

`SOURCE_SENSITIVE_PHRASES` includes **`audit`** ([executive_summary_x2.py](apps_rg/runtime/validators/executive_summary_x2.py) ~144–150); no selected fact’s `claim_text` contains “audit”, so any regen “executive polish” using audit language fails X2 and reverts — **baseline text never improves**.

---

## Score timeline (same run)

| Stage | Claude | Notes |
|-------|--------|-------|
| First panel (~14:02:44) | ~2.4 | Pre–full post-X2 contract `3841c710…` |
| Post-X2 full refresh (~14:03:25) | **3.2** | Aligned contract `472263cc…`, hash `1835e270…` |
| After 3 regen cycles | 3.2 | Regen reverted; final panel unchanged |

---

## Recommended fixes (ordered)

1. **Tighten X2 synthesis** to detect non-action accomplishment stacks (Platform/Basel/Monolithic…) or align `x2_executive_summary_synthesis_quality` failure with what X1D residual dims penalize — closes X2/X1D contradiction without lowering threshold.
2. **Judge regen guard:** extend `format_judge_regen_*` / voice repair to forbid `SOURCE_SENSITIVE_PHRASES` unless present in cited facts (e.g. block “audit-ready” unless `audit` in ledger sources).
3. **L2 / fact selection:** for `INSURANCE_BROKERAGE_IT_INNOVATION`, bias six-sentence plan toward interoperability / EA / innovation facts when graph-eligible — reduces legitimate Claude JD-emphasis fails.
4. **Calibration (optional):** panel quorum policy or Claude-specific rubric clause for “do not fail solely on implied JD fit when facts cannot support brokerage vocabulary” — only if product accepts weaker targeting bar.

---

## Proof commands

```text
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```
