---
plan_id: graph-skills-deferred-followup-d7f2a8
plan_type: enhancement
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
parent_plan: graph-skills-quality-enhancement-c4e8a1
parent_plan_status: Completed
---

# Graph Skills — Deferred Follow-Up (W0–W10-AG)

Execute **remaining proof and lane quality** deferred from [graph-skills-quality-enhancement-c4e8a1](graph-skills-quality-enhancement-c4e8a1.md) (parent **Completed** 2026-05-26). Parent delivered W0–W10 code, hardening, and W10-AG **contract** unified C0.3 bind (`e27875b14e`). This plan owns **REAL_LLM spine proof (D16)**, **7/7 LIVE_X3**, utilization REAL_LLM, CI GHA receipts, and honest **release-claims** flip.

> **plan_id discipline:** `plan=graph-skills-deferred-followup-d7f2a8`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: In Progress
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-05-27
W1_REAL_LLM_RECEIPT: docs/reports/apps_rg/graph_skills_deferred_followup_w1_real_llm_receipt.json
W1_BROWN_ARTIFACT_DIR: artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_062524
PARENT_PLAN: graph-skills-quality-enhancement-c4e8a1
DEFERRED_REGISTER: docs/reports/apps_rg/graph_skills_deferred_scope_register_20260526.md

PLAN_CREATED: slug=graph-skills-deferred-followup-d7f2a8 path=.claude/plans/graph-skills-deferred-followup-d7f2a8.md status=Not Started notion_page=36c27693-f55c-8131-a2c2-f2ad66da13b4

NOTION_PAGE_ID: 36c27693-f55c-8131-a2c2-f2ad66da13b4
NOTION_PLAN_URL: https://www.notion.so/graph-skills-deferred-followup-d7f2a8-36c27693f55c8131a2c2f2ad66da13b4

---

## Context (SCQA)

- **Situation** — Parent maximized graph skills: JD subgraph, capsules, spine FEC, hybrid, CI ratchet workflow, utilization scorer, operator guide. W10-AG wired `apps_rg` → `maybe_run_graph_rag` with live `AppsRgGraphAdapter` over `augmented_skills_graph`.
- **Complication** — Closeout remains **PARTIAL**: LIVE_X3 **2/7**; D16 REAL_LLM not captured on Brown runs; W8 utilization `real_llm_executed: false`; D10/D13 lack GHA URLs; five lanes X2/X3 red or empty artifacts.
- **Question** — What proof remains before `claims_release_eligible` may flip true?
- **Answer** — Register-first (W0), exec_summary spine REAL_LLM pilot (W1), 7/7 lane reruns + checklists (W2), utilization + rubric REAL_LLM (W3), CI GHA (W4), closeout refresh (W5).

---

## Parent receipts (read-only)

| Artifact | Role |
|----------|------|
| [graph_skills_quality_enhancement_closeout.json](../docs/reports/apps_rg/graph_skills_quality_enhancement_closeout.json) | D1–D16 matrix at parent close |
| [graph_skills_c03_unified_pipeline_bind.json](../docs/reports/apps_rg/graph_skills_c03_unified_pipeline_bind.json) | W10-AG contract PASS |
| [graph_skills_quality_w10_ag_receipt.json](../docs/reports/apps_rg/graph_skills_quality_w10_ag_receipt.json) | W10-AG wave receipt |
| [graph_skills_deferred_scope_register_20260526.md](../docs/reports/apps_rg/graph_skills_deferred_scope_register_20260526.md) | DS-1 … DS-13 map |

---

## Deferred scope map

| ID | Title | Wave | Proof class |
|----|-------|------|-------------|
| DS-1 | D16 REAL_LLM spine C0.3 (`c0_graph_lane_receipt`, non-NA graph refs) | W1 | REAL_LLM |
| DS-2 | LIVE_X3 7/7 Brown reruns | W2 | LIVE_X3 |
| DS-3 | D6 artifact checklist all lanes | W2 | REAL_LLM |
| DS-4 | D1 rationale 7/7 run dirs | W2 | REAL_LLM |
| DS-5 | D8 utilization REAL_LLM | W3 | REAL_LLM |
| DS-6 | D3 per-lane X2 REAL_LLM vs rubric | W3 | REAL_LLM |
| DS-7 | D10/D13 CI GHA + nightly URLs | W4 | CI_RATCHET |
| DS-8 | unify_bullets / unify_narrative X2 remediation | W2 | REAL_LLM |
| DS-9 | ibm_bullets / ibm_narrative X2 remediation | W2 | REAL_LLM |
| DS-10 | competencies full Brown run | W2 | REAL_LLM |
| DS-11 | Proof pool spine FEC alignment (static shim gated) | W1 | CONTRACT |
| DS-12 | Closeout refresh + claims flip | W0, W5 | DETERMINISTIC |
| DS-13 | Spine FEC REAL_LLM all grounded lanes | W1–W2 | REAL_LLM |

---

## Status tables

### Wave progress

| Wave | Focus | Gate | Status |
|------|-------|------|--------|
| W0 | Register + refresh closeout baseline post W10-AG | G-W0 | **DONE** |
| W1 | D16 contract + DS-11 spine authority (REAL_LLM pilot open) | G-W1 | **DONE** (contract) |
| W2 | 7/7 LIVE_X3 + lane X2 remediations (DS-2–4,8–10) | G-W2 | In Progress |
| W3 | D8 utilization + D3 REAL_LLM rubric (DS-5–6) | G-W3 | Not Started |
| W4 | D10/D13 GHA ratchet + nightly (DS-7) | G-W4 | BLOCKED (no `gh` locally) |
| W5 | Release closeout — flip claims only with proof (DS-12) | G-W5 | Not Started |

---

## Canonical REAL_LLM CLI (Brown)

```bash
python -m apps_rg --section <lane> --provider qwen_vllm \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief <briefing.md per lane>
```

Lanes: `headline`, `executive_summary`, `unify_bullets`, `unify_narrative`, `ibm_bullets`, `ibm_narrative`, `competencies`.

**W1 pilot:** `executive_summary` only — require `c0_graph_lane_receipt.json` (or spine section receipt) with `canonical_c0_3_graph_claimed: true` and `graph_expansion_refs` without `graphrag_deferred_phase1`.

---

## Wave detail

### W0 — Register linkage + closeout refresh

- Link register on disk; parent Notion remains **Completed**.
- Re-run `python ops_scripts/apps_rg/emit_graph_skills_quality_w10.py` after W10-AG on HEAD; merge W10-AG bind claims into closeout notes (do not flip `claims_release_eligible` without W2–W5 proof).
- Emit `docs/reports/apps_rg/graph_skills_deferred_followup_w0_receipt.json`.

### W1 — D16 spine REAL_LLM (exec_summary pilot)

- Brown exec_summary run with Chroma + providers.
- Artifacts: `c0_graph_lane_receipt.json`, spine `section_spine_c0_retrieve_receipt` with `canonical_c0_3_graph_claimed: true`.
- DS-11: proof pool reads spine FEC `graph_expansion_refs`; contract test that static shim is not sole authority when spine LIVE.
- Emit `graph_skills_deferred_followup_w1_receipt.json`.

### W2 — 7/7 LIVE_X3 + lane remediations

- Rerun all seven lanes; fix unify proof-pool scope, IBM metrics, competencies empty dir.
- Each lane: `x3_disposition.json` → ALLOW; D6 checklist complete.
- Emit `graph_skills_deferred_followup_w2_receipt.json` with `live_x3_allow_count`.

### W3 — Utilization + rubric REAL_LLM

- W8 scorer on fresh REAL_LLM outputs (`real_llm_executed: true`).
- D3: store per-lane `x2_gate_outputs.json` under Brown dirs.
- Emit `graph_skills_deferred_followup_w3_receipt.json`.

### W4 — CI GHA

- Green run URL for `graph-skills-authority-ratchet.yml` + nightly soak workflow.
- Update W7 receipt; `claims_ci_ratchet_gha_executed: true` only with URL.
- Emit `graph_skills_deferred_followup_w4_receipt.json`.

### W5 — Release closeout

- Re-run closeout compiler; require `live_x3_allow_lane_count == 7` and D16 PASS for `claims_release_eligible`.
- Parent plan row stays **Completed**; this plan → **Completed** when G-W5 green.
- Emit `graph_skills_deferred_followup_closeout.json`.

---

## Phase gates

| Gate | Blocks | Requires |
|------|--------|----------|
| G-W0 | W1+ | Register on disk; closeout notes mention W10-AG PASS |
| G-W1 | W2 | exec_summary REAL_LLM spine receipt; DS-11 contract PASS |
| G-W2 | W3,W5 | 7/7 LIVE_X3 ALLOW + D6 checklist |
| G-W3 | W5 | D8 REAL_LLM utilization |
| G-W4 | W5 | D10/D13 GHA URLs |
| G-W5 | plan complete | `claims_release_eligible: true` only if all above |

---

## Honest non-claims (until G-W5)

| Claim | Allowed now | Flip when |
|-------|-------------|-----------|
| `claims_release_eligible` | **false** | W5 closeout all green |
| `claims_live_x3_7_of_7` | **false** | W2 seven ALLOW |
| `claims_dynamic_graphrag_traverse` | **true** (contract) | W1 REAL_LLM per lane |
| `claims_c03_unified_pipeline_bound` | **true** (contract) | W1 REAL_LLM spine receipt |
| `claims_ci_ratchet_gha_executed` | **false** | W4 URL |

---

## Out of scope

- Re-opening parent W0–W10 feature work (frozen unless blocker).
- Weakening X2 gates to force PASS.
- Mock-only REAL_LLM proof.
- New `agentic_core` app-id branches.

---

## Split marker

```
SPLIT_TO_NEW_PLAN: parent=graph-skills-quality-enhancement-c4e8a1 child=graph-skills-deferred-followup-d7f2a8 authorized_by=user decisive_reason="Parent Completed with PARTIAL closeout; deferred proof burndown"
DEFERRED_SCOPE_CAPTURED: register=docs/reports/apps_rg/graph_skills_deferred_scope_register_20260526.md items=13
```
