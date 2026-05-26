# Executive summary — Anthropic surgical regen W5 Brown proof (2026-05-26)

> **Plan:** [exec-summary-anthropic-surgical-regen-f3c8d2](../../.cursor/plans/exec-summary-anthropic-surgical-regen-f3c8d2.md)  
> **Prior Brown run (pre-W3):** [exec_summary_20260526_193949](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_193949)

## Command

```powershell
$env:VLLM_MAX_MODEL_LEN = '24576'
python -m apps_rg --section executive_summary `
  --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd_exec.txt `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md `
  --provider qwen_vllm
```

| Result | Value |
|--------|--------|
| Exit code | **0** |
| Wall time | ~313s |
| `OPERATOR_STATUS` | **DRAFT_READY** |
| `PRODUCT_STATUS` | `X3_REVIEW_JUDGE_SOFT_FAIL` |
| Run root | [exec_summary_20260526_202438](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_202438) |

## W5 infrastructure checks (verifier)

```bash
python tools/cursor/verify_exec_summary_anthropic_surgical_regen.py \
  artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_202438
```

Receipt: [anthropic_surgical_regen_verify.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_202438/anthropic_surgical_regen_verify.json)

| Check | Result |
|-------|--------|
| `judge_feedback_lines_dropped` | **0** all 3 cycles |
| G5 schema | `executive_summary_g5_delta_scope_v2` all cycles |
| `REGEN_DELTA` + allowlist `EDIT_BUDGET` in provider request | **yes** (e.g. `freeze all other sentences verbatim`) |
| Verifier `w5_infrastructure_ok` | **PASS** |

## Regen cycle comparison vs `exec_summary_20260526_193949`

| Cycle | Pre-W3 (193949) | W5 (202438) |
|-------|-----------------|-------------|
| 1 | G5 **legacy fail** (4 edits > budget 3) | G5v2 **pass**; rejected **G3** `trigger_judge_regression` (Claude 3.8→3.6) |
| 2 | G5 legacy fail | G5v2 **allowlist fail** (edited S2–S3 outside allowlist [4,5,6]) |
| 3 | G5 legacy fail | G5v2 allowlist fail (edited S3 outside allowlist) |
| Outcome | `no_acceptable_candidate` / scratch | Same — scratch published |

**Takeaway:** W1–W4 goals are proven on the live path — full judge feedback, G5v2 allowlist replaces bogus legacy budget blocks on cycle 1, prescriptive `EDIT_BUDGET` in transport. No acceptable regen candidate yet: cycle 1 regressed the trigger judge; cycles 2–3 over-edited outside cited sentences.

## Artifacts (quick links)

- [judge_remediation_cycles.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_202438/judge_remediation_cycles.json)
- [g5_delta_scope_cycle_1.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_202438/g5_delta_scope_cycle_1.json)
- [provider_request_judge_regen_cycle01_attempt00_judge_regen-01-00-b7c6e49e.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_202438/provider_request_judge_regen_cycle01_attempt00_judge_regen-01-00-b7c6e49e.json)
- [cli_section_execution_report.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_202438/cli_section_execution_report.json)

## Follow-up (out of W5 scope)

- Tighten allowlist inference (avoid over-broad S1–S6 union when judge cites S4–S6 only).
- G3 regression guard vs multi-judge rescore after cycle 1 Gemini collapse.
- Re-run when Qwen regen stability improves for multi-cycle acceptance.
