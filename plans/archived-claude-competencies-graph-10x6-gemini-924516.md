---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\competencies-graph-10x6-gemini-924516.md'
original_relative_path: 'competencies-graph-10x6-gemini-924516.md'
source_sha256: ec97eaea05ff81a1474e22094fd593893a32ef99b2fba4526c3979f065b5d835
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: competencies-graph-10x6-gemini-924516
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Competencies — Graph 10→6 Selection + Gemini Pro Single Judge

Align the competencies lane with graph-skills authority (not base résumé `facts.skills`), a **generate 10 → keep top 6** selection pipeline grounded in `augmented_skills_graph`, colon+keyword display format, and a **single X1D judge** (`gemini_pro`) matching the employment-bullet pool model (one judge row, not a 3-provider panel).

> **plan_id discipline**: `competencies-graph-10x6-gemini-924516` ↔ `.cursor/plans/competencies-graph-10x6-gemini-924516.md`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-27
NOTION_PAGE_ID: 36d27693-f55c-81aa-b0de-ddc6e35f2b36
NOTION_PLAN_URL: https://www.notion.so/competencies-graph-10x6-gemini-924516-36d27693f55c81aab0deddc6e35f2b36
PLAN_COMPLETE: slug=competencies-graph-10x6-gemini-924516 waves=W0-W4 status=DONE notion_page=36d27693-f55c-81aa-b0de-ddc6e35f2b36

---

## Context (SCQA)

- **Situation** — P2-W1A routes competencies proof through `augmented_skills_graph`. Product now uses **10** Qwen SC paths, graph pool merge to **6** categories, and a **single** `gemini_pro` X1D pool judge row.
- **Complication** — Legacy path used 4 SC paths, 6–8 emit band, triple X1D panel, and taxonomy projection that could emit all **7** YAML buckets.
- **Question** — How to implement graph-grounded 10→6 selection and single-judge X1D without regressing proof authority?
- **Answer** — Employment-bullet pool patterns + graph_10x6 prompt SSOT + `competencies_pool_x1d_judge_rows` + taxonomy trim to `max_categories: 6`.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Status | Success Criteria |
|------|-----------|-------|--------|------------------|
| W0 | W0.1 | Baseline gap receipt | ✅ DONE | Gap matrix + red contract tests |
| W1 | W1.1–W1.2 | Prompt/PA SSOT graph_10x6 | ✅ DONE | Template + rigor MIN=MAX=6 |
| W2 | W2.1–W2.3 | 10-path pool, top-6 merge, graph gate | ✅ DONE | SC=10, merge=6, rationale artifact |
| W3 | W3.1–W3.2 | Single `gemini_pro` X1D | ✅ DONE | One judge row; default CLI |
| W4 | W4.1 | Tests + smoke proof | ✅ DONE | Pytest green; harness smoke |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Document current vs target seam map | ✅ DONE |
| W1.1 | Update `competency_selector_v2.yaml` + `.pa_slots.yaml` | ✅ DONE |
| W1.2 | Update contract / rigor / taxonomy SSOT | ✅ DONE |
| W2.1 | `COMPETENCIES_SC_PATH_COUNT=10`, emit=6 constants | ✅ DONE |
| W2.2 | Pool selector + top-6 merge | ✅ DONE |
| W2.3 | Lane execution targeting + `graph_selection_rationale.json` | ✅ DONE |
| W3.1 | `competencies_pool_x1d_judge_rows` | ✅ DONE |
| W3.2 | Default `--x1d-judges gemini_pro` | ✅ DONE |
| W4.1 | Contract + pool tests + smoke | ✅ DONE |
| W4.2 | Taxonomy projection trim 7→6 emit | ✅ DONE |

---

## Out Of Scope (unchanged)

- Edits to `agentic_core/` spine.
- Locked deterministic copy (EY, InsurTech, education, etc.).
- Replacing Qwen/vLLM transport.
- Notion backlog auto-write per wave (optional manual sync script only).
- Full Brown REAL_LLM all-lanes certification (DS-10 deferred register).

---

## Gap Register — CLOSED

| Gap | Status | Evidence |
|-----|--------|----------|
| GAP-1 10→6 selection | ✅ CLOSED | [competencies_graph_pool.py](../apps_rg/runtime/reasoning/competencies_graph_pool.py) |
| GAP-2 Prompt `facts.skills` drift | ✅ CLOSED | W1 SSOT + contract tests |
| GAP-3 Triple X1D | ✅ CLOSED | W3 pool judge + defaults |
| GAP-4 Taxonomy 7→6 emit | ✅ CLOSED | [competencies_capability_projection.py](../apps_rg/runtime/sections/competencies_capability_projection.py) trim |

---

## Definition of Done

| DoD | Status | Evidence |
|-----|--------|----------|
| DoD-1 Graph proof only | **PASS** | `test_competencies_graph_skills_proof_pool_p2_w1a.py` |
| DoD-2 Runtime 6 categories from 10 pool | **PASS** | `test_competencies_10x6_pool.py` + projection trim test |
| DoD-3 Single `gemini_pro` X1D | **PASS** | target contract + pool judge row |
| DoD-4 Prompt graph-only SSOT | **PASS** | `test_w2d_competency_selector.py` |
| DoD-5 Smoke run | **PASS** | Harness REAL_LLM exit 0; [w4 closeout](docs/reports/apps_rg/competencies_10x6_w4_closeout_receipt.md) |

---

## Key implementation files

| Area | Path |
|------|------|
| Pool constants / merge | [competencies_graph_pool.py](../apps_rg/runtime/reasoning/competencies_graph_pool.py) |
| Generation | [bullet_lane_generation.py](../apps_rg/runtime/reasoning/bullet_lane_generation.py) |
| Selector | [bullet_pool_claude_selector.py](../apps_rg/runtime/judges/bullet_pool_claude_selector.py) |
| X1D pool row | [employment_bullet_pool.py](../apps_rg/runtime/reasoning/employment_bullet_pool.py) `competencies_pool_x1d_judge_rows` |
| Lane execution | [competencies_lane_execution.py](../apps_rg/runtime/sections/competencies_lane_execution.py) |
| Taxonomy trim | [competencies_capability_projection.py](../apps_rg/runtime/sections/competencies_capability_projection.py) |
| Prompt | [competency_selector_v2.yaml](../apps_rg/prompt_assembly/templates/competency_selector_v2.yaml) |

---

## Receipts

- [competencies_10x6_gemini_gap_receipt.md](docs/reports/apps_rg/competencies_10x6_gemini_gap_receipt.md) — gap register closed
- [competencies_10x6_w4_closeout_receipt.md](docs/reports/apps_rg/competencies_10x6_w4_closeout_receipt.md) — W4 proof

WAVE_COMPLETE: plan=competencies-graph-10x6-gemini-924516 wave=closeout note="all waves DONE; GAP-4 taxonomy trim; DoD PASS"
