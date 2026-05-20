# Closeout — executive_summary judge-safe S2/S3 tightening (post-repair soft-fail)

## STATUS: PARTIAL

Scoped judge-safe repair fixes landed and **8/8 unit tests PASS**. Best live REAL_LLM proof run [`exec_summary_20260520_133741`](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_133741) achieved **X2 PASS** and **OpenAI 4.1 PASS**, but **X3 remains blocked** (Anthropic decisive failure; Gemini soft-fail). Later retries hit `L2_BLOCK:TOKEN_BUDGET_EXCEEDED_AFTER_TRIM` (environment, not repair logic).

## FILES_CHANGED

- [exec_summary_srfs_judge_safe.py](apps_rg/runtime/sections/exec_summary_srfs_judge_safe.py)
- [test_exec_summary_srfs_judge_safe.py](tests/unit/apps_rg/test_exec_summary_srfs_judge_safe.py)

## COMMANDS_RUN (exit codes)

| Command | Exit |
|---------|------|
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/unit/apps_rg/test_exec_summary_srfs_judge_safe.py -q -p pytest_timeout` | 0 |
| Canonical live (best): `python -m apps_rg --section executive_summary ...` → [`exec_summary_20260520_133741`](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_133741) | 1 (`X3_BLOCK`, expected nonzero) |
| Live retry [`exec_summary_20260520_134248`](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_134248), [`134343`](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_134343) | 1 (`L2_BLOCK:TOKEN_BUDGET_EXCEEDED_AFTER_TRIM`) |

## LATEST_RUN_DIR (best proof)

[exec_summary_20260520_133741](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_133741)

Baseline (prior repair): [exec_summary_20260520_131351](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_131351)

## ARTIFACTS_INSPECTED

- [l2_output.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_133741/l2_output.json)
- [srfs_judge_safe_repair.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_133741/srfs_judge_safe_repair.json)
- [x2_gate_outputs.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_133741/x2_gate_outputs.json)
- [x3_disposition.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_133741/x3_disposition.json)
- [x1d_llm_judge_outputs.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_133741/x1d_llm_judge_outputs.json)

## RUNTIME_FINDINGS (133741)

| Check | Result |
|-------|--------|
| S2 40% Basel/CCAR metric preserved | **yes** — verbatim `fact_governance_003` claim with `by 40%` |
| S3 tightened to SRFS wording | **yes** — `Designed and operationalized … regulated enterprise workflows; standardized AI lifecycle practices across intake, validation, execution, monitoring, and remediation.` (no density embellishment tails) |
| S4 six-month → three-week preserved | **yes** — full cycle-metric clause retained |
| X2 status | **PASS** (68/68 including density + responsibility_shape) |
| X3 disposition | `X3_BLOCK` — `decisive_judge_failures: anthropic_claude` |

### Judge scores (133741 vs 131351)

| Judge | 131351 (prior) | 133741 (this patch) |
|-------|----------------|---------------------|
| Gemini Pro | 3.0 fail | 2.0 fail |
| OpenAI ChatGPT | 4.1 **pass** | 4.1 **pass** |
| Anthropic Claude | 3.8 fail | 2.5 fail (decisive: S3/S4 lifecycle repetition) |

### Repair seam changes (summary)

1. **S2** — emit verbatim `fact_governance_003` claim (restores **40%**).
2. **S3** — stop overriding unsupported-commercialization with `_sentence_supports_004_lifecycle_arc`; strip density tails; when `platform_004` carries cycle metric, use `fact_engineering_platform_001` workflows clause + lifecycle head (semicolon join).
3. **S4** — when S3 uses split lifecycle head, emit **outcome tail only** (`Reducing lab-to-production…`) to avoid duplicate `Standardized AI lifecycle…` opener (code path present; 133741 run still used full metric sentence — next healthy Qwen run should pick tail path).
4. **Guards** — rewrite S3 on org-scale (`8 to 28`), unsupported embellishment, cycle metric in S3, S2 metric drop, S3/S4 duplicate opener.

## PROOF_CLASSIFICATION

**JUDGE_SAFE_REAL_LLM_PARTIAL** — Deterministic SRFS repair seam proven by unit tests + one full REAL_LLM run with X2 PASS; multi-judge unanimous ALLOW not achieved (Anthropic decisive on lifecycle repetition in 133741; Qwen token budget blocked follow-up runs).

## EXPLICIT_NON_CLAIMS

- X3_ALLOW / proof-eligible ALLOW not claimed.
- Anthropic ≥4.0 soft-fail clearance not claimed on 133741.
- Token-budget-blocked runs are not repair regressions.
- No mock/stub transport proof.

## FORBIDDEN_FILES_TOUCHED

| Boundary | Touched |
|----------|---------|
| `agentic_core` | **no** |
| Pre-dispatch gates | **no** |
| Judge thresholds | **no** |

## RCA_REFERENCE

[executive_summary_anthropic_soft_fail_rca_receipt.md](docs/reports/apps_rg/executive_summary_anthropic_soft_fail_rca_receipt.md) · [executive_summary_anthropic_soft_fail_repair_closeout_receipt.md](docs/reports/apps_rg/executive_summary_anthropic_soft_fail_repair_closeout_receipt.md)
