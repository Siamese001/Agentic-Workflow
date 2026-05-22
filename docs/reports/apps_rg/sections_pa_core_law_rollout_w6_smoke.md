# Sections PA Core-Law Rollout — W6 Runtime Smoke

**Generated:** 2026-05-22T10:22:55Z
**STATUS:** PARTIAL

**Plan:** [sections-pa-core-law-rollout-c3a8f1.md](.cursor/plans/sections-pa-core-law-rollout-c3a8f1.md)

## Targeting

- Company: Brown & Brown
- Role: SVP IT Strategy & Innovation
- JD: [brown_brown_svp_it_strategy_innovation_jd.txt](apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt)
- Brief: [brown_brown_svp_it_strategy_innovation_briefing_exec.md](apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md)

## Lane summary

| section | lane_status | REAL_LLM | x3 | X2 product | token_budget | PRODUCT_SHAPE×1 | pa_core_law | run_dir |
|---------|-------------|----------|-----|------------|--------------|-----------------|-------------|---------|
| headline | PASS | REAL_LLM | X3_REVIEW_JUDGE_SOFT_FAIL | PASS | EXEMPT | 1 | True | `artifacts/apps_rg/runtime_proofs/headline/real/headline_20260522_101600` |
| competencies | PASS | REAL_LLM | X3_BLOCK | PASS | None | 1 | True | `artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260522_101716` |
| unify_bullets | PASS | REAL_LLM | X3_REVIEW_JUDGE_SOFT_FAIL | PASS | None | 1 | True | `artifacts/apps_rg/runtime_proofs/unify_bullets/real/unify_bullets_20260522_101853` |
| unify_narrative | BLOCKED | BLOCKED_UPSTREAM_NOT_FINALIZED | X3_BLOCK | FAIL | None | 1 | True | `artifacts/apps_rg/runtime_proofs/unify_narrative/real/unify_narrative_20260522_102018` |
| ibm_bullets | PASS | REAL_LLM | X3_BLOCK | FAIL | None | 1 | True | `artifacts/apps_rg/runtime_proofs/ibm_bullets/real/ibm_bullets_20260522_102059` |
| ibm_narrative | BLOCKED | BLOCKED_UPSTREAM_NOT_FINALIZED | X3_BLOCK | FAIL | None | 1 | True | `artifacts/apps_rg/runtime_proofs/ibm_narrative/real/ibm_narrative_20260522_102228` |

## GAP semantics (W6)

- **GAP-1:** headline `token_budget_status=EXEMPT` (no exec-grade token_budget module).
- **GAP-3:** `x3_code` may be `X3_BLOCK` while `runtime_generation_status=REAL_LLM`; acceptable for PA-dedup DoD.

## Commands

- `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m apps_rg --section headline --target-company Brown & Brown --target-role SVP IT Strategy & Innovation --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md --provider qwen_vllm --allow-non-allow-exit-zero`
- `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m apps_rg --section competencies --target-company Brown & Brown --target-role SVP IT Strategy & Innovation --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md --provider qwen_vllm --allow-non-allow-exit-zero`
- `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m apps_rg --section unify_bullets --target-company Brown & Brown --target-role SVP IT Strategy & Innovation --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md --provider qwen_vllm --allow-non-allow-exit-zero`
- `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m apps_rg --section unify_narrative --target-company Brown & Brown --target-role SVP IT Strategy & Innovation --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md --provider qwen_vllm --allow-non-allow-exit-zero`
- `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m apps_rg --section ibm_bullets --target-company Brown & Brown --target-role SVP IT Strategy & Innovation --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md --provider qwen_vllm --allow-non-allow-exit-zero`
- `C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m apps_rg --section ibm_narrative --target-company Brown & Brown --target-role SVP IT Strategy & Innovation --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing_exec.md --provider qwen_vllm --allow-non-allow-exit-zero`
