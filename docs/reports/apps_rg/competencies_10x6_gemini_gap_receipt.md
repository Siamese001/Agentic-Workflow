# Competencies 10→6 + Gemini Pro — Gap Receipt (CLOSED)

**Plan:** [competencies-graph-10x6-gemini-924516](../../.cursor/plans/competencies-graph-10x6-gemini-924516.md)  
**Updated:** 2026-05-27  
**Status:** All product gaps closed (W0–W4)

---

## Executive summary

| Dimension | Target | Current | Status |
|-----------|--------|---------|--------|
| Skills / competency **proof authority** | `augmented_skills_graph` only | P2-W1A graph proof pool + PA graph projection | **CLOSED** |
| **Pool size** (Qwen SC paths) | **10** candidates | `COMPETENCIES_SC_PATH_COUNT=10`, profile `10.0` | **CLOSED** |
| **Emitted categories** | **6** fixed (top-scoring, graph-real) | `MIN=MAX=6`; pool merge + taxonomy trim | **CLOSED** |
| **Selection model** | Generate 10 → score → keep top **6** | `qwen_competencies_graph_pool_*` + `merge_competencies_graph_pool_top_six` | **CLOSED** |
| **Display format** | `Category Label: kw, kw, kw` | Prompt + X2 | **CLOSED** |
| **X1D judges** | **1** judge: `gemini_pro` | Default `gemini_pro`; `competencies_pool_x1d_judge_rows` | **CLOSED** |
| **Pool judge row** | Single `*_pool_x1d_judge_rows` | `competencies_pool_x1d_judge_rows` | **CLOSED** |
| **Prompt SSOT** | Graph-only; no `facts.skills` authority | `competency_selector_v2.yaml` graph_10x6 | **CLOSED** |
| **Taxonomy emit** | Top **6** of **7** taxonomy buckets | `trim_taxonomy_to_graph_10x6_emit` in projection | **CLOSED** |

---

## Gap register (resolved)

| Gap | Resolution |
|-----|------------|
| GAP-1 10→6 selection | [competencies_graph_pool.py](../../apps_rg/runtime/reasoning/competencies_graph_pool.py), [bullet_lane_generation.py](../../apps_rg/runtime/reasoning/bullet_lane_generation.py) |
| GAP-2 Base résumé prompt drift | W1 prompt/PA/contract SSOT |
| GAP-3 Triple X1D panel | W3 `gemini_pro` default + pool judge row |
| GAP-4 Taxonomy 7→6 emit | [competencies_capability_projection.py](../../apps_rg/runtime/sections/competencies_capability_projection.py) `_trim_categories_to_emit_count` |

---

## Proof commands

```bash
python -m pytest tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py tests/_apps_contract/test_w2d_competency_selector.py tests/unit/apps_rg/test_competencies_10x6_pool.py tests/_apps_contract/test_competencies_10x6_target_contract.py -q -o addopts=
```

Smoke (test harness — product CLI blocks `--mock-judges` flags):

```powershell
$env:APPS_RG_TEST_HARNESS='1'; $env:APPS_RG_MOCK_JUDGES='1'; $env:APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO='1'
python -m apps_rg --section competencies --provider qwen_vllm --x1d-judges gemini_pro `
  --target-company "Synthetic Enterprise Corp." --target-role "SVP Engineering" `
  --resume apps_rg/resume/base/amit_ayer_base_resume_v1.json `
  --jd "<non-empty jd>" --manual-brief "<non-empty briefing>"
```

---

## Deferred (explicitly out of plan DoD)

| Item | Notes |
|------|-------|
| REAL_LLM Brown all-lanes run | DS-10 graph-skills deferred register |
| Notion backlog row per wave | Plan out-of-scope; optional manual sync via [plan_notion_sync_competencies_graph_10x6_gemini.py](../../tools/notion/plan_notion_sync_competencies_graph_10x6_gemini.py) |
| `agentic_core` judge harness | apps_rg overlay only |

---

## Related artifacts

- [competencies_10x6_w4_closeout_receipt.md](competencies_10x6_w4_closeout_receipt.md)
- [competencies_graph_proof_pool_p2_w1a_default_graph_authority_receipt.json](competencies_graph_proof_pool_p2_w1a_default_graph_authority_receipt.json)
