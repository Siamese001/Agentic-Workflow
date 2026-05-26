# Graph Skills Quality — Deferred Scope Register (W0–W10-AG)

**Parent plan:** [graph-skills-quality-enhancement-c4e8a1](../../.cursor/plans/graph-skills-quality-enhancement-c4e8a1.md) — **Completed** 2026-05-26  
**Follow-on plan:** [graph-skills-deferred-followup-d7f2a8](../../.cursor/plans/graph-skills-deferred-followup-d7f2a8.md)  
**Closeout compiler:** [graph_skills_quality_enhancement_closeout.json](graph_skills_quality_enhancement_closeout.json) (generated pre–W10-AG commit; refresh in follow-on W0)  
**W10-AG contract bind:** [graph_skills_c03_unified_pipeline_bind.json](graph_skills_c03_unified_pipeline_bind.json) — `status: PASS` (contract/stress only)

---

## Executive summary

| Category | Count | Notes |
|----------|-------|-------|
| DoD items PARTIAL/BLOCKED at parent close | 11 of 16 | D1–D3, D5–D8, D10, D12–D13, D16 |
| LIVE_X3 ALLOW lanes | **2 / 7** | headline, executive_summary |
| W10-AG spine bind (contract) | **PASS** | `e27875b14e` — REAL_LLM spine proof still open |
| CI GHA ratchet URL | **Missing** | Local mirror PASS; `ci_unavailable: true` in closeout |
| Release claims | **All false** | `claims_release_eligible`, `claims_production_ready`, `claims_live_x3_7_of_7` |

---

## Deferred scope map (DS-*)

| ID | Source wave | Gap | Proof class | Primary blocker | Follow-on wave |
|----|-------------|-----|-------------|-----------------|----------------|
| DS-1 | W10-AG / D16 | REAL_LLM spine C0.3: `c0_graph_lane_receipt.json` per lane; FEC `graph_expansion_refs` ≠ `graphrag_deferred_phase1` on Brown run | `REAL_LLM_RUNTIME_PROOF` | No post-bind Brown exec_summary run with spine receipt | W1 |
| DS-2 | W10 / D6 | LIVE_X3 **7/7** — rerun Brown CLI all lanes | `LIVE_X3_ALLOW_PROOF` | unify/ibm X2 FAIL; competencies incomplete artifact dir | W2 |
| DS-3 | W10 / D6 | D6 artifact checklist: `native_c03_final_evidence.json` + `graph_selection_rationale.json` all lanes | `REAL_LLM_RUNTIME_PROOF` | 5/7 lanes missing native_c03; competencies missing entire checklist | W2 |
| DS-4 | W10 / D1 | `graph_selection_rationale.json` in run dirs **7/7** | `REAL_LLM_RUNTIME_PROOF` | competencies + backfill gap at parent close (6/7) | W2 |
| DS-5 | W8 / D8 | Utilization scorer **REAL_LLM** proof (`real_llm_executed: false` in W8 receipt) | `REAL_LLM_RUNTIME_PROOF` | Only contract/fixture probes | W3 |
| DS-6 | W4 / D3 | Per-lane REAL_LLM X2 gate outputs aligned to graph rubric | `REAL_LLM_RUNTIME_PROOF` | Contract-only at close | W3 |
| DS-7 | W7–W10 / D10,D13 | CI ratchet + nightly soak **green GHA run URLs** | `CI_RATCHET_PROOF` | No `gh` / GHA capture locally | W4 |
| DS-8 | W10 / lanes | **unify_bullets** / **unify_narrative** X2 fact-scope failures | `REAL_LLM_RUNTIME_PROOF` | `bul_unify_.003` not in proof pool | W2 |
| DS-9 | W10 / lanes | **ibm_bullets** / **ibm_narrative** metric + narrative X2 FAIL | `REAL_LLM_RUNTIME_PROOF` | IBM metric anchors / empty narrative | W2 |
| DS-10 | W10 / lanes | **competencies** — no real run artifacts (empty checklist) | `REAL_LLM_RUNTIME_PROOF` | Stale/incomplete `competencies_*` dir | W2 |
| DS-11 | W10-AG | Proof pool: demote static-only `c03_graphrag_bound` shim when spine FEC has live graph refs | `CONTRACT_TEST_PROOF` | Lane paths still build parallel bound docs | W1 |
| DS-12 | W10 | Closeout compiler refresh + `claims_*` flip only with proof | `DETERMINISTIC_RUNTIME_PROOF` | Closeout JSON predates W10-AG; claims stale | W0, W5 |
| DS-13 | W5 / D5,D7 | Spine FEC equality REAL_LLM across all grounded lanes | `REAL_LLM_RUNTIME_PROOF` | Partial at close | W1–W2 |

---

## W10-AG split (shipped vs still deferred)

| Item | Status on `main` (`e27875b14e`) | Follow-on |
|------|----------------------------------|-----------|
| `apps_rg/integrations/c0_graph_adapter.py` | **DONE** | — |
| `route_profiles.yaml` LIVE `graph_traverse` | **DONE** | — |
| `c0_binding` → `maybe_run_graph_rag` | **DONE** | — |
| Contract/stress tests + bind JSON | **PASS** | — |
| D16 REAL_LLM 7/7 + `c0_graph_lane_receipt` | **OPEN** | DS-1, DS-2 |
| `claims_c03_unified_pipeline_bound` in closeout | **Stale false** | DS-12 (re-run closeout) |
| Proof pool spine-only alignment | **OPEN** | DS-11 |

---

## Lane matrix snapshot (parent closeout)

| Lane | X3 | LIVE allow | Checklist | Top blocker |
|------|-----|------------|-----------|-------------|
| headline | ALLOW | yes | PARTIAL | missing `native_c03_final_evidence.json` |
| executive_summary | ALLOW | yes | PASS | — |
| unify_bullets | BLOCK | no | PARTIAL | X2 fact pool scope |
| unify_narrative | BLOCK | no | PARTIAL | upstream unify bullets |
| ibm_bullets | BLOCK | no | PARTIAL | IBM metric gates |
| ibm_narrative | BLOCK | no | PARTIAL | empty narrative / bullets N/A |
| competencies | UNKNOWN | no | PARTIAL | no runtime artifacts in dir |

---

## Parent markers (audit trail)

```
DEFERRED_SCOPE: plan=graph-skills-quality-enhancement-c4e8a1 wave=W10-AG gap="Unified C0.3 pipeline bind (c0_graph_adapter, route_profiles, D16 REAL_LLM)" impact="follow-on plan"
SPLIT_TO_NEW_PLAN: parent=graph-skills-quality-enhancement-c4e8a1 child=graph-skills-deferred-followup-d7f2a8 register=docs/reports/apps_rg/graph_skills_deferred_scope_register_20260526.md
```

---

## References

- [graph_skills_quality_w10_ag_receipt.json](graph_skills_quality_w10_ag_receipt.json)
- [graph_skills_quality_plan_completion_receipt.json](graph_skills_quality_plan_completion_receipt.json)
- [graph_skills_utilization_receipt.json](graph_skills_utilization_receipt.json)
- Workflow: [.github/workflows/graph-skills-authority-ratchet.yml](../../.github/workflows/graph-skills-authority-ratchet.yml)
