# Wave 3 targeted pytest closure plan (Wave 1)

Replaces the aborted broad filter:

```text
python -m pytest tests/_apps_contract -k "unify_bullets or ibm_bullets or ibm_narrative or executive_summary"
```

## Receipt baseline (unchanged)

| Metric | Value |
|--------|-------|
| X2 PASS (latest REAL_LLM) | **7/7** |
| X3 ALLOW | **3/7** |
| proof_eligible | **1/7** |
| Skills authority PASS | **7/7** |

Open gaps are **judge / X3 / proof_eligible**, not deterministic X2.

## Targeted files (14)

| Tier | File | Risk |
|------|------|------|
| A | `test_apps_rg_augmented_skills_graph_source_authority.py` | low |
| A | `test_apps_rg_augmented_skills_graph_dual_source_all_sections.py` | low |
| A | `test_apps_rg_augmented_skills_graph_all_sections_runtime_receipts.py` | low-medium |
| A | `test_apps_rg_live_qwen_x2_repairs.py` | low |
| A | `test_apps_rg_proof_pool_resolver_contract.py` | low |
| A | `test_unify_bullets_text_claim_coverage.py` | low |
| A | `test_exec_summary_x2_product_gates.py` | low |
| A | `test_apps_rg_executive_summary_l2_proof_pool_alignment.py` | low |
| B | `test_unify_bullets_runtime_slice.py` | medium |
| B | `test_unify_bullets_section_pipeline.py` | medium-high |
| B | `test_ibm_bullets_runtime_slice.py` | medium |
| B | `test_ibm_bullets_section_pipeline.py` | medium |
| C | `test_ibm_narrative_runtime_slice.py` | high (qwen_vllm) |
| C | `test_exec_summary_runtime_slice.py` | medium-high |

Machine-readable: `wave3_targeted_pytest_closure_plan.json`
