# RCA — Anthropic X1D soft-fail (exec_summary_20260520_125832)

## STATUS: PASS (analysis complete; no patch applied)

## FILES_INSPECTED

- [x3_disposition.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/x3_disposition.json)
- [x1d_llm_judge_outputs.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/x1d_llm_judge_outputs.json)
- [x1d_anthropic_claude_provider_response_raw_20260520_130001_522.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/x1d_anthropic_claude_provider_response_raw_20260520_130001_522.json)
- [executive_summary_judge_packet.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/executive_summary_judge_packet.json)
- [l2_output.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/l2_output.json)
- [provider_response.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/provider_response.json)
- [compiled_prompt_artifact.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/compiled_prompt_artifact.json)
- [x2_gate_outputs.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/x2_gate_outputs.json)
- [section_metric_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/section_metric_receipt.json)
- [srfs_judge_safe_repair.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/srfs_judge_safe_repair.json)
- [srfs_judge_safe_repair_final.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/srfs_judge_safe_repair_final.json)
- [srfs_density_micro_repair.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/srfs_density_micro_repair.json)

## ROOT_CAUSE

**Primary:** Post-generation **SRFS judge-safe repair** reshaped live Qwen output into a weaker five-sentence arc that Anthropic graded under **rubric dimension `synthesis_quality`** (score **3.5** vs threshold **4.0**). This is **not** an unsupported-claim failure, **not** a pre-dispatch defect, and **not** a rubric mismatch across judges.

### Judge scores (same rubric: `SRFS_GRADE_ONLY_RUBRIC`)

| Judge | Score | Pass | Decisive failure |
|-------|------:|------|------------------|
| Gemini Pro | 5.0 | yes | no |
| OpenAI ChatGPT | 4.3 | yes | no |
| Anthropic Claude | 3.5 | no | no |

All three: `unsupported_claims: []`, `decisive_failure: false`.

### Exact Anthropic critique (failing dimension: **synthesis_quality**)

From [x1d_llm_judge_outputs.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/x1d_llm_judge_outputs.json):

1. **S1–S2 redundancy** — S2 re-enumerates `fact_engineering_platform_001` capabilities already stated in S1, weakening the mechanism layer of the five-sentence arc.
2. **S3 lifecycle stitch** — `"Leads platform lifecycle across architecture, operating model, and engineering scale-out"` is only loosely tied to facts; S3 awkwardly combines lifecycle language with the Basel III/CCAR 40% clause.
3. **Unused high-value SRFS fact** — `fact_engineering_platform_004` / six-month→three-week cycle metric was in the allowed packet but **not used** in the judged text (Anthropic: would have strengthened lifecycle/outcomes).
4. **fail_reasons:** `"S1-S2 redundancy reduces synthesis quality below threshold."`, `"S3 lifecycle clause lacks direct fact citation, weakening factual support."`
5. **quality_flags:** `s1_s2_redundancy`, `unused_high_value_metric_fact_engineering_platform_004`

**Not the driver:** Anthropic noted CI-probe JD vs senior-executive tone mismatch but explicitly stated anti-overfit rules prevent penalizing absence of JD-as-proof.

### Generation vs repair vs gates

| Stage | What happened |
|-------|----------------|
| **Raw Qwen** ([provider_response.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/provider_response.json)) | Distinct arc: S3 lifecycle (`fact_engineering_platform_004`), S4 **$22M / gross margin / 6mo→3wk** (`fact_engineering_platform_004_metric_06dd515f`). SRFS-supported. |
| **Judge-safe repair** ([srfs_judge_safe_repair.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/srfs_judge_safe_repair.json)) | Replaced full summary with fact-tight templates: S2 = platform capability list from `fact_engineering_platform_001`, S3 = lifecycle+Basel stitch (`build_fact_tight_s3_sentence`), S4 = team scale only (`fact_exec_002`) — **dropped** commercial/cycle metrics. |
| **Density micro-repair** | Trimmed S2 clause only ([srfs_judge_safe_repair_final.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/srfs_judge_safe_repair_final.json)). |
| **Judges graded** | Post-repair [l2_output.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832/l2_output.json) text — not raw Qwen. |
| **X2** | 68/68 PASS including `x2_executive_summary_synthesis_quality` — deterministic gates do not encode S1–S2 redundancy or SRFS fact-utilization. |
| **X3** | `X3_REVIEW_JUDGE_SOFT_FAIL` — one soft-failed judge (`anthropic_claude`). |

### Classification

| Hypothesis | Verdict |
|------------|---------|
| Unsupported claim concern | **Ruled out** — Anthropic `unsupported_claims: []`; X2 claim gates PASS. |
| Rubric mismatch | **Ruled out** — same `executive_summary_x1d_v1` / SRFS rubric for all judges. |
| Prompt shaping alone | **Partial** — prompt asks for five-sentence arc; repair templates dominate final shape. |
| **Generation quality (post-repair synthesis)** | **Primary** — judged copy is repair output, not raw Qwen. |
| **Judge variance** | **Secondary** — Anthropic applies stricter synthesis_quality scoring; Gemini 5.0 on same candidate. |

## RECOMMENDED_ZERO_LOSS_CORRECTION

**Do not patch yet** — smallest safe change when implementing:

1. **`exec_summary_srfs_judge_safe.py`** — When `fact_engineering_platform_004` / `fact_engineering_platform_004_metric_06dd515f` is in the SRFS slice, **preserve or re-insert** the six-month→three-week outcome in **S3 or S4** instead of replacing S4 with team-scale-only when rewriting commercial S4.
2. **Differentiate S1 vs S2** — If both cite `fact_engineering_platform_001`, use a **thesis-only S1** and a **narrower mechanism S2** (or governance-thread S2 via `fact_governance_003`) so repair does not duplicate the capability stack.
3. **Avoid Basel+lifecycle stitch in S3** when a dedicated S4 already carries `fact_engineering_platform_004` metrics from Qwen — skip `_sentence_s3_needs_lifecycle_rewrite` / commercial rewrite when ledger already maps lifecycle+metrics across S3/S4.

Preserves: SRFS-only proof, no JD-as-evidence, no unsupported claims, no mock fallback, no judge threshold changes, no Anthropic bypass, no pre-dispatch edits.

**Optional later (not smallest):** deterministic X2 check for S1–S2 duplicate `source_fact_ids` on adjacent sentences — only if judge-safe repair alone is insufficient.

## PROOF_CLASSIFICATION

**JUDGE_VARIANCE_WITH_REPAIR_INDUCED_SYNTHESIS_REGRESSION** — Live Qwen was SRFS-valid; post-repair arc triggered Anthropic `synthesis_quality` soft-fail while X2 remained PASS.

## EXPLICIT_NON_CLAIMS

- X3_ALLOW not claimed (`X3_REVIEW_JUDGE_SOFT_FAIL`).
- Pre-dispatch gates not at fault (`dispatch_started=true`, targeting PASS).
- Anthropic decisive failure not claimed (`decisive_failure=false`).
- No recommendation to weaken threshold 4.0 or bypass Anthropic.
- No recommendation to treat REVIEW as ALLOW.
