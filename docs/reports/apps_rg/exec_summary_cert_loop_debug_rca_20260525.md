# Debug RCA — Exec summary cert loop (16 attempts, no CERTIFIED)

**STATUS:** RCA complete (analysis only)  
**Best run:** [exec_summary_20260525_002352](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352)  
**Loop receipt:** [exec_summary_cert_loop_receipt.json](exec_summary_cert_loop_receipt.json)

---

## Symptom

- 16 full `python -m apps_rg --section executive_summary` (Brown targeting) attempts after recursion fix.
- Every run: **DRAFT_READY** (REAL_LLM, X2 PASS, exit 0).
- **Zero** runs: **CERTIFIED** (X3_ALLOW + 3/3 `MODEL_BACKED_PASS`).
- Typical panel: **2/3** (Gemini + OpenAI pass; Claude 3.0–3.5 fail).

---

## What is NOT the root cause

| Ruled out | Evidence |
|-----------|----------|
| Unfair judge briefing | `targeting_context_parity_receipt.json` → `parity_match: true` on post-fix runs |
| Wrong judge packet / contract drift | Shared `judge_packet_hash`; explicit `dimension_verdicts` from all providers on best run |
| X2 / proof failure | `x2_failed_gates: []`, `product_quality_status: PASS`, all judges `deterministic_alignment.pass: true` |
| Unsupported claims | Claude `unsupported_claims: []`, `decisive_failure: false` |
| Transport / blocked judges | All `MODEL_BACKED`, no `BLOCKED_*` |
| Recursion crash (later batch) | Fixed `_write_x1d_judge_artifacts`; runs completed |

---

## Primary root cause

**Residual prose quality fails Claude’s bar while passing Gemini/OpenAI on the same candidate text.**

Certification requires **every** configured X1D judge ≥ 4.0/5. The binding failure is almost always:

- **`anthropic_claude`** soft-fail (~3.4 normalized 0.68 vs threshold 0.8)

On best run, Claude failed **three rubric dimensions** (structured verdicts, not inferred):

| Dimension | Pass | Codes |
|-----------|------|-------|
| `executive_signal` | false | `achievement_inventory_not_strategy_narrative`, `missing_forward_vision` |
| `synthesis_quality` | false | `sequential_recap_not_integrated_synthesis`, `generic_closing_sentence` |
| `ats_alignment_without_keyword_stuffing` | false | `weak_alignment_to_ea_interoperability_innovation_themes` |
| `factual_support` | true | — |

Gemini (4.5) and OpenAI (4.4) passed **all eight** dimensions on the **same** paragraph.

**Conclusion:** Not a panel-contract bug; **generator output shape + judge calibration gap** on SVP narrative / Brown JD emphasis.

---

## Contributing cause A — Generator arc matches the failure mode

Final text on best run ([resume_display_text.txt](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/resume_display_text.txt)):

- S1 platform + revenue/margin  
- S2 “Building on that direction…” → Basel/CCAR  
- S3 “Monolithic risk…” → HPC  
- S4 “Advanced quantitative…” + certs  
- S5 “These efforts culminate…” generic outcomes  

Claude findings explicitly call this a **sequential inventory** with a **generic close** and weak **EA / interoperability / innovation** framing — aligned with dimension codes above.

---

## Contributing cause B — Judge regen did not improve the shipped draft

[judge_remediation_cycles.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_002352/judge_remediation_cycles.json):

| Cycle | Trigger | Outcome |
|-------|---------|---------|
| 1 | `solitary_severe_soft_fail` (Claude only) | Regen + X2 repair **accepted**, then **`reverted: post_regen_x2_failed_after_x2_repair`** |
| 2 | same | Same revert (X2: `x2_first_person_zero`, `x2_no_inferred_bridge_claims`, `x2_source_sensitive_phrases_supported`) |
| 3 | same | `accepted: true`, **`all_judges_pass: false`** |

Regen **ran** (trigger: 2 pass, 1 soft-fail, `solitary_severe_soft_fail`), but **could not commit** a rewrite that stays X2-green **and** lifts Claude. Shipped paragraph remains the pre-regen baseline that already scored 2/3.

---

## Contributing cause C — Full rerun loop is high-variance

Outer cert loop restarts **entire generation** each attempt. Observed `pass_count` across batch 2: 1, 2, 1, 1, 2, 1, 1, 1 — rerolls often **worse** than best (2/3), not monotonic improvement toward 3/3.

---

## Incident (batch 1 only): recursion

`_write_x1d_judge_artifacts` called itself → `maximum recursion depth exceeded` before judges. **Fixed** in [executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py). Attempts 1–2 of batch 1 had `pass_count: 0` for that reason.

---

## Smallest safe next fixes (ordered)

1. **Synthesis/regen targeting Claude dimensions** — regen user message already has `DIMENSION_VERDICTS`; tighten generator template or composition plan for S1/S6 (vision + EA/interop emphasis from JD, not proof).
2. **Judge regen revert policy** — investigate why regen cycles 1–2 pass X2 repair then still revert (`post_regen_x2_failed_after_x2_repair`); may be re-scoring pre-repair draft or second X2 pass stricter.
3. **Do not** lower Claude threshold or drop from roster without ADR (cert bar is 3/3).
4. Optional: cert loop should **reuse best draft + regen-only** instead of full regen-from-scratch when `pass_count == 2`.

---

## Proof pointers

| Artifact | Path |
|----------|------|
| X3 | `x3_disposition.json` → `X3_REVIEW_JUDGE_SOFT_FAIL`, `soft_failed_judges: ["anthropic_claude"]` |
| Dimension matrix | `x1d_dimension_matrix.json` |
| Judges | `x1d_llm_judge_outputs.json` |
| Regen | `judge_remediation_cycles.json` |
