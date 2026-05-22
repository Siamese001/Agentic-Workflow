# Executive Summary PA Core-Law Dedup — Closeout Receipt

**Plan:** [exec-summary-pa-core-law-dedup-f8e2a1.md](.cursor/plans/exec-summary-pa-core-law-dedup-f8e2a1.md)  
**Marker:** `EXEC_SUMMARY_PROMPT_CORE_LAW_V3` (template v1.2)  
**Completed:** 2026-05-22

## Summary

apps_rg executive-summary prompts now reference **pa_core_law_v1** contracts by name instead of restating full PA oath / X2 gate essays in static slots. **PRODUCT_SHAPE** is the sole in-prompt X2 gate catalog at compile time; SRFS oneshot is compact when the evidence capsule is active.

## Waves

| Wave | Outcome |
|------|---------|
| W1 | [pa_core_law_v1.yaml](apps_rg/prompt_assembly/pa_core_law_v1.yaml) + [pa_core_law.py](apps_rg/prompt_assembly/pa_core_law.py); S0 accepts `pa_truth_oath_v1` in [contracts.py](apps_rg/prompt_assembly/contracts.py) |
| W2 | Slim [executive_summary.generate_scratch_v1.yaml](apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml); removed `_EXEC_SUMMARY_X2_GATE_REFS`; PRODUCT_SHAPE always appended on non–INPUT_AUTHORITY path |
| W3 | Compact SRFS oneshot in [executive_summary_pa.py](apps_rg/runtime/sections/executive_summary_pa.py); [test_exec_summary_prompt_drift_ratchet.py](tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py) |
| W4 | Pytest green + Brown runtime proof (below) |

## Pytest (W4)

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/prompt_assembly/test_pa_core_law_v1.py \
  tests/unit/apps_rg/test_executive_summary_prompt_dedup_v2.py \
  tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py \
  tests/_apps_contract/test_exec_summary_pa_compiled_prompt.py \
  tests/unit/apps_rg/runtime/sections/test_executive_summary_evidence_capsule.py \
  tests/unit/apps_rg/runtime/sections/test_executive_summary_token_budget.py \
  -o addopts= -q
→ 50 passed, 0 failed
```

## Runtime proof — Brown & Brown (W4.1)

**Command:**

```bash
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md \
  --provider qwen_vllm --allow-non-allow-exit-zero
```

**Artifact dir:** [exec_summary_20260522_090529](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_090529)

| Check | Value |
|-------|--------|
| `runtime_generation_status` | `REAL_LLM` |
| [token_budget_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_090529/token_budget_receipt.json) `status` | `PASS` |
| `dispatch_allowed` | `true` |
| `capsule_applied` | `true` |
| `compiled_prompt_tokens_after_trim` | 7003 (avail 13824) |
| Compiled S0 cites | `pa_truth_oath_v1`, `pa_core_law_v1.yaml` |

**Note:** X2 product gates failed on this run (`jd_alignment_proof_flags`, `evidence_utilization`, `no_mechanism_inventory`) — expected for content-quality tuning, not in scope for token-governance / PA-dedup DoD.

**Prior baseline (dedup v2):** [exec_summary_20260522_084114](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260522_084114)

## Key files changed

- [pa_core_law_v1.yaml](apps_rg/prompt_assembly/pa_core_law_v1.yaml)
- [pa_core_law.py](apps_rg/prompt_assembly/pa_core_law.py)
- [contracts.py](apps_rg/prompt_assembly/contracts.py)
- [executive_summary.generate_scratch_v1.yaml](apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml)
- [executive_summary_pa.py](apps_rg/runtime/sections/executive_summary_pa.py)
- [section_product_shape_ssot.py](apps_rg/runtime/sections/section_product_shape_ssot.py)
- [strategic_tailor_v1.yaml](apps_rg/prompt_assembly/templates/strategic_tailor_v1.yaml) (header pointer)
- Tests: [test_pa_core_law_v1.py](tests/unit/apps_rg/prompt_assembly/test_pa_core_law_v1.py), [test_exec_summary_prompt_drift_ratchet.py](tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py), dedup/contract/token suites

## Definition of Done

| DoD | Status |
|-----|--------|
| DoD-1 pa_core_law_v1 + exec references | PASS |
| DoD-2 Single X2 catalog (PRODUCT_SHAPE) | PASS |
| DoD-3 Contract pytest suite | PASS (50) |
| DoD-4 Brown REAL_LLM + token budget PASS | PASS |
| DoD-5 Notion + this receipt | PASS (receipt); Notion slug `exec-summary-pa-core-law-dedup-f8e2a1` |
