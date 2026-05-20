# Closeout — executive_summary Anthropic soft-fail repair (judge-safe)

## STATUS: PARTIAL

Repair-induced synthesis regression remediated per [executive_summary_anthropic_soft_fail_rca_receipt.md](docs/reports/apps_rg/executive_summary_anthropic_soft_fail_rca_receipt.md). Deterministic X2 PASS on live REAL_LLM run; X3 remains `X3_REVIEW_JUDGE_SOFT_FAIL` (Anthropic 3.8, Gemini 3.0; OpenAI 4.1 pass).

## ROOT_CAUSE_CONFIRMED

Post-`apply_srfs_judge_safe_repair` reshaping dropped `fact_engineering_platform_004` / `fact_engineering_platform_004_metric_06dd515f` cycle metric, duplicated S1/S2 on `fact_engineering_platform_001`, and Basel-stitched S3 — judged text scored Anthropic **3.5** while X2 stayed PASS. RCA receipt stands; this closeout proves seam fix + live re-run.

## FILES_CHANGED

- [exec_summary_srfs_judge_safe.py](apps_rg/runtime/sections/exec_summary_srfs_judge_safe.py) — S1 thesis-only when paired with 001; S2 governance-thread (`fact_governance_003`) or narrower mechanism; S3 lifecycle without Basel stitch when 004 in slice; S4 always replaced with cycle metric when 004/004_metric in SRFS slice (drops unsupported `$22M`/gross margin from preserved Qwen S4)
- [test_exec_summary_srfs_judge_safe.py](tests/unit/apps_rg/test_exec_summary_srfs_judge_safe.py) — unit proofs for metric preservation, S1/S2 dedup, in-slice `source_fact_ids`

## COMMANDS_RUN (exit codes)

| Command | Exit |
|---------|------|
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/unit/apps_rg/test_exec_summary_srfs_judge_safe.py -q -p pytest_timeout` | 0 |
| Canonical live: `python -m apps_rg --section executive_summary --target-company "CI Probe Company" --target-role "CI Probe Role" --jd tests/_fixtures/ci-probe-jd.txt --manual-brief tests/_fixtures/ci-probe-briefing.txt` (no stub, no `--allow-non-allow-exit-zero`) | 1 (expected: `X3_REVIEW_JUDGE_SOFT_FAIL`, `PROCESS_EXIT_CODE=1`) |

## TESTS_GATES

| Gate | Result |
|------|--------|
| `test_exec_summary_srfs_judge_safe.py` (4 cases) | PASS |
| Live X2 (68 gates) | PASS — including `x2_north_star_style_echo_unsupported_zero`, `x2_srfs_claim_business_metrics_substrate`, `x2_executive_summary_synthesis_quality` |
| Live X3 | `X3_REVIEW_JUDGE_SOFT_FAIL` — not ALLOW |

## LATEST_RUN_DIR

[exec_summary_20260520_131351](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_131351)

Baseline (pre-fix RCA): [exec_summary_20260520_125832](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_125832)

Intermediate regression (S4 preserve bug): [exec_summary_20260520_131140](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_131140) — `X3_BLOCK`, X2 substrate/style-echo FAIL.

## ARTIFACTS_INSPECTED

- [l2_output.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_131351/l2_output.json)
- [provider_response.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_131351/provider_response.json)
- [srfs_judge_safe_repair.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_131351/srfs_judge_safe_repair.json)
- [x2_gate_outputs.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_131351/x2_gate_outputs.json)
- [x3_disposition.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_131351/x3_disposition.json)
- [x1d_llm_judge_outputs.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_131351/x1d_llm_judge_outputs.json)

Note: `srfs_judge_safe_repair_final.json` not present on this run (density micro-repair did not apply).

## RUNTIME_FINDINGS

### Six-month → three-week metric

**Preserved.** Judged text S4: *"reducing lab-to-production cycle time from six months to three weeks"*. Claim ledger S4 cites `fact_engineering_platform_004` only. Repair removed pre-fix commercial rewrite (`$22M`, gross margin) from [srfs_judge_safe_repair.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260520_131351/srfs_judge_safe_repair.json) `before_resume_display_text`.

### S1/S2 redundancy

**Removed.** S1 thesis (`fact_engineering_platform_001` only). S2 governance (`fact_governance_003` only) — no duplicate capability stack vs RCA run.

### S3 Basel+lifecycle stitch

**Avoided.** S3 is lifecycle-only (`fact_engineering_platform_004` + `fact_engineering_platform_001`); Basel/CCAR isolated in S2.

### X2 status

**68/68 PASS** — product_quality_status `PASS`.

### X3 disposition

| Judge | Pre-fix (125832) | Post-fix (131351) |
|-------|------------------|-------------------|
| Gemini Pro | 5.0 pass | 3.0 fail |
| OpenAI ChatGPT | 4.3 pass | 4.1 pass |
| Anthropic Claude | 3.5 fail | 3.8 fail |

`x3_code`: `X3_REVIEW_JUDGE_SOFT_FAIL`. `authorization_scope`: `REVIEW_ONLY`. `runtime_generation_status`: `REAL_LLM`.

Anthropic findings shifted: no longer flags unused `fact_engineering_platform_004` or S1–S2 redundancy; flags S3 embellishment beyond proof-pool wording and S2 dropping explicit 40% metric.

## PROOF_CLASSIFICATION

**REPAIR_SEAM_REAL_LLM_PARTIAL** — Scoped judge-safe repair verified by unit tests + canonical REAL_LLM dispatch; deterministic substrate PASS; X1D multi-judge split remains (not proof-eligible ALLOW).

## EXPLICIT_NON_CLAIMS

- X3_ALLOW / proof-eligible ALLOW not claimed.
- REVIEW not treated as ALLOW.
- No judge threshold changes, no Anthropic bypass, no mock/stub transport proof.
- No JD-as-evidence; SRFS-only claim paths preserved (`x2_jd_as_proof_zero` PASS).
- Full multi-judge unanimous PASS not claimed (Gemini regressed on post-fix candidate).

## FORBIDDEN_FILES_TOUCHED

| Boundary | Touched |
|----------|---------|
| `agentic_core` | **no** |
| Pre-dispatch gates | **no** |
| Judge thresholds | **no** |

## RCA_REFERENCE

[executive_summary_anthropic_soft_fail_rca_receipt.md](docs/reports/apps_rg/executive_summary_anthropic_soft_fail_rca_receipt.md)
