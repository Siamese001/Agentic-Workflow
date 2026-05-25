# W3 Live Brown — Same-Authority Incremental Regen

**Plan:** [core-same-authority-incremental-regen-e7a4b1.md](../../../.cursor/plans/core-same-authority-incremental-regen-e7a4b1.md)  
**Run:** `exec_summary_20260525_122058`  
**Date:** 2026-05-25

## STATUS: PASS (W3 scoped — canonical regen path)

W3 proves **core `SameAuthorityRegenRunner` delegation** on a real Brown executive_summary lane. Product X3 is **`X3_REVIEW_JUDGE_SOFT_FAIL`** (Claude soft-fail); post-regen draft was **reverted** after X2 repair (`post_regen_x2_failed_after_x2_repair`). That is an app remediation outcome, not a failure of the same-authority chassis proof.

## Command

```bash
set APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1
set APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN=1
python -m apps_rg --section executive_summary --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --provider qwen_vllm --allow-non-allow-exit-zero --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

| Field | Value |
|-------|-------|
| Exit code | **0** (CLI; `--allow-non-allow-exit-zero`) |
| `run_dir` | [exec_summary_20260525_122058](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058) |

**Note:** Plan closeout cited `--proof-mode real`; that flag is not on `apps_rg` CLI. Real proof is under `artifacts/apps_rg/runtime_proofs/executive_summary/real/` (standard real lane).

## Provider request proof (strict)

| Check | Evidence | Result |
|-------|----------|--------|
| Same authority | Parent [provider_request.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/provider_request.json) and regen [provider_request_regen.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/provider_request_regen.json): `Qwen/Qwen2.5-32B-Instruct-AWQ`, lane `vllm` | **PASS** |
| Thread shape | Regen `messages[]`: system → user (gen turn) → assistant (anchor) → user (`REGEN_DELTA_v1` + `PROMPT_LOCK`, no embedded anchor draft) | **PASS** |
| Prefix / compile hash | [compiled_prompt_artifact.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/compiled_prompt_artifact.json) `prompt_hash` = `5c0ac9618b78db2f`; regen `frozen_compile_ref` = `5c0ac9618b78db2f` | **PASS** |
| No recompile | [same_authority_regen_receipt.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/same_authority_regen_receipt.json): `no_prompt_recompile_assertion=true`, `frozen_compile_preserved=true` | **PASS** |
| No flat re-render | Regen body is `messages[]` append only (`provider_request_regen.json`), not a new flat compiled prompt replacing thread | **PASS** |
| Semantic ≠ transport | Receipt: `semantic_regen_attempt_index=1`, `transport_retry_count=0` | **PASS** |

## Artifact checklist

| Artifact | Path | Present |
|----------|------|---------|
| `compiled_prompt_artifact.json` | [compiled_prompt_artifact.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/compiled_prompt_artifact.json) | yes |
| `provider_request_regen.json` | [provider_request_regen.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/provider_request_regen.json) | yes |
| `same_authority_regen_receipt.json` | [same_authority_regen_receipt.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/same_authority_regen_receipt.json) | yes |
| `judge_remediation_receipt.json` | [judge_remediation_receipt.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/judge_remediation_receipt.json) | yes (`regen_engine`: `core.SameAuthorityRegenRunner`) |
| `judge_remediation_cycles.json` | [judge_remediation_cycles.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/judge_remediation_cycles.json) | yes |
| `x1d_llm_judge_outputs.json` | [x1d_llm_judge_outputs.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/x1d_llm_judge_outputs.json) | yes |
| `x3_disposition.json` | [x3_disposition.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/x3_disposition.json) | yes (`X3_REVIEW_JUDGE_SOFT_FAIL`) |
| `x2_gate_outputs.json` (before + after) | Single [x2_gate_outputs.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/x2_gate_outputs.json) | **PARTIAL** — no separate before/after snapshot files; cycle receipt captures post-regen X2 failures |

## Trigger proof

- [judge_remediation_trigger.json](../../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260525_122058/judge_remediation_trigger.json): `solitary_dimension_major_soft_fail` on `executive_signal` + `synthesis_quality` (Claude), `x2_passed=true` before regen.
- Core heal: `repair_tactic=incremental_delta_turn_v1`, `trigger_source=X3_JUDGE`, `heal_outcome=PASS`, `next_action=RETURN_TO_E3`.

## Closeout commands

| Command | Result |
|---------|--------|
| `python -m compileall agentic_core apps_rg -q` | exit 0 |
| `pytest tests/unit/agentic_core/L2_execution/regen/ -q` | exit 0, 17 passed |
| `pytest tests/unit/apps_rg/test_executive_summary_judge_remediation.py tests/unit/apps_rg/test_same_authority_regen_delegation.py -q` | exit 0, 15 passed |
| `python ops_scripts/ci/check_same_authority_regen_boundary.py` | exit 0, PASS |

## Infra prerequisite (Brown unblock)

First Brown attempt failed: `No module named 'agentic_core.L6_system_learning.span_contracts'`. Added compatibility shim [span_contracts.py](../../../agentic_core/L6_system_learning/span_contracts.py) → `runtime_adg.span_contracts`.

## FILES_CHANGED (W3 session)

- [executive_summary_same_authority_regen_bridge.py](../../../apps_rg/runtime/sections/executive_summary_same_authority_regen_bridge.py)
- [executive_summary_judge_remediation.py](../../../apps_rg/runtime/sections/executive_summary_judge_remediation.py)
- [executive_summary_repair_policy.py](../../../apps_rg/runtime/sections/executive_summary_repair_policy.py)
- [test_same_authority_regen_delegation.py](../../../tests/unit/apps_rg/test_same_authority_regen_delegation.py)
- [span_contracts.py](../../../agentic_core/L6_system_learning/span_contracts.py) (import shim)

## NOTES

- Regen engine accepted parse; lane reverted draft when post-regen X2 failed (`x2_exec_summary_meta_filler_zero`, `x2_source_sensitive_phrases_supported`) — expected app policy, not chassis bypass.
- W4 orchestrator remains blocked per plan until merge gate; this receipt satisfies W3.2 live proof.
