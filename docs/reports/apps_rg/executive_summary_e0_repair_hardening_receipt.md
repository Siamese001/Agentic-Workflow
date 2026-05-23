# Executive summary E0 repair hardening — closeout receipt

**Plan:** [exec-summary-e0-repair-hardening-c4e8f1.md](../../.cursor/plans/exec-summary-e0-repair-hardening-c4e8f1.md)  
**Prerequisite:** [apps-rg-pa-ssot-gap-b8e4f1.md](../../.cursor/plans/apps-rg-pa-ssot-gap-b8e4f1.md) (COMPLETED)  
**Pre-fix RCA run:** [exec_summary_20260523_153906](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260523_153906)  
**Date:** 2026-05-23

## Summary

Closed the post-PA-SSOT executive_summary failure chain: graph-only deterministic repair no longer injects mechanism-inventory S1 or thins `claim_ledger` below utilization when the fact pool is large. Lane orchestration respects `skipped_x2_regression`. C0 demotes `fact_certs_*` to background stratum. Prompt U0/I0 ratchet 4–5 sentences and ≥5 ledger rows when pool ≥6.

## Waves delivered

| Wave | Status | Evidence |
|------|--------|----------|
| W1 E0 SSOT | Inherited (PA plan) | [pa_e0_compile_proof_receipt.json](../../artifacts/apps_rg/plans/pa_e0_compile_proof_receipt.json) `pass: true` |
| W2 Prompt ratchet | Done | [executive_summary_pa.py](../../apps_rg/runtime/sections/executive_summary_pa.py), [executive_summary.generate_scratch_v1.yaml](../../apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml) |
| W3 Graph-only repair | Done | [exec_summary_graph_only_quality.py](../../apps_rg/runtime/sections/exec_summary_graph_only_quality.py) |
| W4 Lane orchestration | Done | [executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py) |
| W5 C0 certs demotion | Done | [c04_exec_summary_shaping.py](../../apps_rg/runtime/c0/c04_exec_summary_shaping.py) |
| W6 Tests + CI slice | Done | pytest W6 slice (67 tests) |
| W7 Live Brown & Brown | **DONE** | [exec_summary_20260523_164959](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260523_164959) — PRODUCT_QUALITY PASS; X3_REVIEW_JUDGE_SOFT_FAIL (Track C) |
| W8 Closeout | Done | This receipt |

## Commands run

```text
python ops_scripts/apps_rg/verify_pa_e0_compile_proof.py
  -> PA-E0-COMPILE-PROOF PASS

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/_apps_contract/test_pa_e0_examples_ssot.py \
  tests/unit/apps_rg/test_exec_summary_graph_only_quality.py \
  tests/unit/apps_rg/test_executive_summary_evidence_utilization.py \
  tests/unit/apps_rg/test_executive_summary_prompt_ssot.py \
  tests/unit/apps_rg/test_executive_summary_repair_orchestration.py \
  tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py \
  tests/_apps_contract/test_executive_summary_x2_x1d_alignment.py \
  tests/unit/apps_rg/test_executive_summary_synthesis_regen.py \
  tests/unit/apps_rg/runtime/c0/test_exec_summary_graph_shaping.py -q
  -> 67 passed
```

## Root causes closed

| ID | Fix |
|----|-----|
| RC-REP-1 | Thesis-led S1 via `_thesis_platform_opener()`; mechanism inventory gated in repair |
| RC-REP-2 | ≥5 `claim_ledger` rows when `len(plan_facts) >= 6` |
| RC-REP-3 | `detect_graph_only_synthesis_violations` includes mechanism + utilization |
| RC-REP-4 | `apply_graph_only_generation_quality_repair` skips apply when `_repair_would_regress_x2`; lane honors `skipped_x2_regression` |
| RC-C0-1 | `fact_certs_*` → `STRATUM_BACKGROUND` in C0 shaping |

## Live proof (W7)

Canonical command:

```powershell
python -m apps_rg --section executive_summary `
  --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**2026-05-23 final run:** [exec_summary_20260523_164959](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260523_164959)

| Check | Result |
|-------|--------|
| `x2_exec_summary_sentence_count_4_5` | PASS |
| `x2_exec_summary_no_mechanism_inventory` | PASS |
| `x2_exec_summary_evidence_utilization` | PASS (5 ledger rows) |
| `x2_executive_summary_synthesis_quality` | PASS |
| `x2_exec_summary_mechanical_opener_stack_zero` | PASS |
| `graph_only_generation_quality_repair.json` | applied; ledger does not block product pass |
| `PRODUCT_QUALITY_STATUS` | PASS |
| `PRODUCT_STATUS` | X3_REVIEW_JUDGE_SOFT_FAIL (gemini_pro, anthropic_claude — Track C) |

## Files changed (this plan)

- [exec_summary_graph_only_quality.py](../../apps_rg/runtime/sections/exec_summary_graph_only_quality.py)
- [executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py)
- [executive_summary_pa.py](../../apps_rg/runtime/sections/executive_summary_pa.py)
- [executive_summary.generate_scratch_v1.yaml](../../apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml)
- [c04_exec_summary_shaping.py](../../apps_rg/runtime/c0/c04_exec_summary_shaping.py)
- [lane_registry.py](../../apps_rg/runtime/rigor/lane_registry.py)
- [test_executive_summary_repair_orchestration.py](../../tests/unit/apps_rg/test_executive_summary_repair_orchestration.py)
- [test_exec_summary_graph_only_quality.py](../../tests/unit/apps_rg/test_exec_summary_graph_only_quality.py)
- [test_executive_summary_prompt_ssot.py](../../tests/unit/apps_rg/test_executive_summary_prompt_ssot.py)
