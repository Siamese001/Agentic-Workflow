# Competencies graph_10x6 + Gemini Pro — W4 Closeout Receipt

**Plan:** [competencies-graph-10x6-gemini-924516](../../.cursor/plans/competencies-graph-10x6-gemini-924516.md)  
**Generated:** 2026-05-27  
**Wave:** W4 (tests + smoke proof)

---

## Verification summary

| DoD | Evidence | Status |
|-----|----------|--------|
| DoD-1 Graph proof only | `pytest tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py` | PASS |
| DoD-2 10→6 pool runtime | `test_competencies_10x6_pool.py` + `bullet_lane_generation.json` | PASS |
| DoD-3 Single `gemini_pro` X1D | `test_competencies_10x6_target_contract.py` + smoke `x1d_llm_judge_outputs.json` | PASS |
| DoD-4 Prompt graph-only SSOT | `test_w2d_competency_selector.py` + target contract | PASS |
| DoD-5 Mock/harness smoke | REAL_LLM run exit 0 (test harness env) | PASS (non-certifying) |

---

## Pytest bundle (W4)

```text
56 passed — graph proof (p2_w1a), w2d selector, 10x6 pool unit, target contract, rigor SSOT, bullet_lane path count
```

Key files:

- [test_competencies_10x6_pool.py](../../tests/unit/apps_rg/test_competencies_10x6_pool.py) (new)
- [test_competencies_10x6_target_contract.py](../../tests/_apps_contract/test_competencies_10x6_target_contract.py)
- [test_competencies_graph_pool_w2.py](../../tests/_apps_contract/test_competencies_graph_pool_w2.py)
- [test_bullet_lane_sc_claude_selection.py](../../tests/unit/apps_rg/test_bullet_lane_sc_claude_selection.py) (competencies SC count → 10)

---

## Smoke run (REAL_LLM + test-harness mock judges)

**Command** (product CLI rejects `--mock-judges`; use harness env):

```powershell
$env:APPS_RG_TEST_HARNESS='1'
$env:APPS_RG_MOCK_JUDGES='1'
$env:APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO='1'
python -m apps_rg --section competencies --provider qwen_vllm --x1d-judges gemini_pro `
  --target-company "Synthetic Enterprise Corp." --target-role "SVP Engineering" `
  --resume apps_rg/resume/base/amit_ayer_base_resume_v1.json `
  --jd "SVP Engineering leader for agentic AI platform..." `
  --manual-brief "Target graph-grounded competency clusters..."
```

**Result:** `PROCESS_EXIT_CODE: 0`, `RUNTIME_GENERATION_STATUS: REAL_LLM`

**Artifact:** [competencies_20260527_073044](artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260527_073044/)

| Artifact | Observed |
|----------|----------|
| [bullet_lane_generation.json](artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260527_073044/bullet_lane_generation.json) | `generation_mode=qwen_competencies_graph_pool_claude_top_6_regen`, `initial_path_count=10`, `final_category_count=6` |
| [x1d_llm_judge_outputs.json](artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260527_073044/x1d_llm_judge_outputs.json) | **1** judge row, `provider_key=gemini_pro`, `judge_role=competencies_graph_pool_selector` |
| [l2_output.json](artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260527_073044/l2_output.json) | **6** `competencies` categories emitted |

**Note:** Harness mock judges → `PRODUCT_X3_STATUS: X3_BLOCK`, `PROOF_ELIGIBLE: false` (expected). Pool selector used heuristic top-6 (`selection_mode=competencies_graph_top_6_heuristic`) with zero Claude selection rows under mock.

---

## Plan complete

Waves W0–W4 implemented. Deferred: full Brown all-lanes REAL_LLM certification (see plan Out Of Scope).
