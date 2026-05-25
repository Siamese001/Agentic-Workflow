# Executive Summary Operator Ship — W5 Live Proof Receipt

**Run ID:** `exec_summary_20260524_001344`  
**Plan:** [exec-summary-operator-ship-a3f7c2.md](../../.cursor/plans/exec-summary-operator-ship-a3f7c2.md)  
**Tier achieved:** **Minimum ship (DRAFT_READY)** — not CERTIFIED  
**Status:** PASS (minimum ship criteria met) — **plan COMPLETED** at this tier (2026-05-24)

**Certified follow-up (not plan-blocking):** Best post-regen live run `exec_summary_20260524_125852` — Gemini 4.5 PASS, OpenAI 4.2 PASS, Claude 3.4 FAIL (residual synthesis/JD emphasis). Latest run `exec_summary_20260524_130459` hit OpenAI `429 insufficient_quota` (provider blocked).

## Command

```text
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**Shell exit:** `0`  
**Log:** [\_w5_operator_ship_live_v2.log](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/_w5_operator_ship_live_v2.log)

## Operator disposition (stdout / CLI report)

| Field | Value |
|-------|-------|
| `OPERATOR_STATUS` | `DRAFT_READY` |
| `DRAFT_READY` | `true` |
| `CERTIFIED` | `false` |
| `PROCESS_EXIT_CODE` | `0` |
| `EXPECTED_NONZERO_EXIT` | `false` |
| `PRODUCT_QUALITY_STATUS` | `PASS` (X2 only) |
| `PRODUCT_STATUS` | `X3_REVIEW_JUDGE_SOFT_FAIL` |
| `PROOF_ELIGIBLE` | `false` |
| `RUNTIME_GENERATION_STATUS` | `REAL_LLM` |

## X3 / judges

- **X2:** all gates pass (`x2_failed_gates: []`)
- **Judges:** Gemini PASS, OpenAI PASS, **Claude soft-fail** (2/3)
- **Judge regen:** triggered (`solitary_severe_soft_fail`), **accepted** (1 attempt) — see [judge_remediation_receipt.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_001344/judge_remediation_receipt.json)
- Post-regen: still `X3_REVIEW_JUDGE_SOFT_FAIL` (certification bar unchanged; no threshold weakening)

## Artifacts

| Artifact | Path |
|----------|------|
| Run directory | [exec_summary_20260524_001344](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_001344/) |
| CLI report | [cli_section_execution_report.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_001344/cli_section_execution_report.json) |
| X3 disposition | [x3_disposition.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_001344/x3_disposition.json) |
| Resume text | [resume_display_text.txt](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_001344/resume_display_text.txt) |
| Judge outputs | [x1d_llm_judge_outputs.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_001344/x1d_llm_judge_outputs.json) |
| Latest pointer | [latest_real_run.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/latest_real_run.json) |

## Code shipped (W1–W3 + hotfix)

- [executive_summary_operator_disposition.py](../../apps_rg/runtime/sections/executive_summary_operator_disposition.py) — draft vs certified tiers
- [cli_section_execution_report.py](../../apps_rg/runtime/cli_section_execution_report.py) — exit 0 on `DRAFT_READY`
- [executive_summary_repair_policy.py](../../apps_rg/runtime/sections/executive_summary_repair_policy.py) — judge regen default ON on product path
- [executive_summary_judge_remediation.py](../../apps_rg/runtime/sections/executive_summary_judge_remediation.py) — `JudgeOutput` coercion fix for soft-judge rerun
- [executive_summary_operator_guide.md](../../docs/apps_rg/executive_summary_operator_guide.md)

## Deferred (unchanged)

- 2/3 judge quorum for CERTIFIED (ADR)
- `repair_summary.json` consolidation (W4 P1)
- Package rollup draft ALLOW while package REVIEW

## Proof commands run

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/_apps_contract/test_executive_summary_operator_outcomes.py \
  tests/unit/apps_rg/test_executive_summary_operator_disposition.py \
  tests/unit/apps_rg/test_executive_summary_judge_remediation.py \
  tests/unit/apps_rg/test_executive_summary_synthesis_contract.py \
  -q
```
