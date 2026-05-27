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
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-27

---

## Context (SCQA)

- **Situation** — P2-W1A already routes competencies proof through `augmented_skills_graph` (`resolve_section_proof_pool`, `build_verified_skill_inventory_projection`). Runtime uses **4** Qwen SC paths + Claude per-`category_label` merge, emits **6–8** taxonomy categories, and runs a **3-judge** X1D panel (`gemini_pro,openai_chatgpt,anthropic_claude`). Prompt SSOT (`competency_selector_v2.yaml`) still references `facts.skills` and BASE RESUME PARITY.
- **Complication** — Product intent is: **do not seed competencies from base résumé competency rows**; generate **top 10** JD/graph-matched competency clusters (`Category: kw, kw, kw`), score for graph reality, emit **top 6**; use **one judge** (Gemini Pro) like Unify/IBM bullet pool lanes—not exec-summary’s triple panel.
- **Question** — How do we implement graph-grounded 10→6 selection and single-judge X1D without regressing proof authority or locked deterministic sections?
- **Answer** — Extend employment-bullet pool patterns (SC path count, Claude/Gemini pool selector score floor, single `x1d_*_pool` row), tighten prompt/PA to graph projection only, and default `--x1d-judges gemini_pro` with X2 gate updates.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1 | Baseline validation receipt (current vs target) | ~3K | ADG/graph fixtures present | ✅ DONE | Gap matrix doc + failing contract tests sketched |
| W1 | W1.1–W1.2 | Prompt/PA SSOT: graph-only inventory, colon format, 10→6 instructions | ~8K | No `agentic_core` edits | ✅ DONE | Template + PA compile; graph_10x6 SSOT |
| W2 | W2.1–W2.3 | Runtime: 10-path pool, top-6 merge, graph reality gate | ~18K | Graph SQLite + hybrid JD fixture | ✅ DONE | `COMPETENCIES_SC_PATH_COUNT=10`, final count=6 |
| W3 | W3.1–W3.2 | X1D: single `gemini_pro` judge (pool selector row) | ~6K | `GOOGLE_API_KEY` or mock path | ✅ DONE | One judge row in `x1d_llm_judge_outputs.json` |
| W4 | W4.1 | Tests, gates, optional Brown CLI proof | ~10K | vLLM optional for full REAL_LLM | ✅ DONE | Targeted pytest green; contract receipt |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Document current vs target seam map | ✅ DONE |
| W1.1 | Update `competency_selector_v2.yaml` + `.pa_slots.yaml` | ✅ DONE |
| W1.2 | Update `competencies_contract.yaml` / rigor / taxonomy | ✅ DONE |
| W2.1 | `COMPETENCIES_SC_PATH_COUNT=10`, `FINAL_CATEGORY_COUNT=6` SSOT | 🔲 TODO |
| W2.2 | Competencies pool selector + `merge_competency_selections` top-6 floor | 🔲 TODO |
| W2.3 | Graph-reality scoring hook (`term_supports_resume_or_graph`, skill_ids) | 🔲 TODO |
| W3.1 | `competencies_pool_x1d_judge_rows` (mirror `employment_pool_x1d_judge_rows`) | 🔲 TODO |
| W3.2 | Default `--x1d-judges gemini_pro`; drop triple-panel for lane | 🔲 TODO |
| W4.1 | Contract tests + `test_competencies_graph_skills_proof_pool_*` extensions | 🔲 TODO |

---

## Out Of Scope

- Edits to `agentic_core/` spine (apps_rg overlay only).
- Changing locked deterministic sections (EY, InsurTech, education, certifications, dates, titles).
- Replacing Qwen generation provider or vLLM transport.
- Notion backlog row creation per wave (defer until plan complete per wave-deferral protocol).

---

## Wave 0 — Baseline & gap receipt

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W0.1** — Gap matrix: 4-path vs 10-path, 6–8 vs 6 fixed, 3-judge vs `gemini_pro` only | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- [competencies_10x6_gemini_gap_receipt.md](docs/reports/apps_rg/competencies_10x6_gemini_gap_receipt.md) lists file-level deltas.
- [test_competencies_10x6_target_contract.py](tests/_apps_contract/test_competencies_10x6_target_contract.py): 6 red-path failures (graph suite 6/6 pass).

WAVE_COMPLETE: plan=competencies-graph-10x6-gemini-924516 wave=0 note="+gap receipt, +6 red contract tests, graph 6/6 pass"

---

## Wave 1 — Prompt & contract SSOT

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W1.1** — Remove/replace BASE RESUME PARITY + `facts.skills` proof language; require `VERIFIED_SKILL_INVENTORY_PROJECTION` + 10 candidate / 6 emitted categories | ~5K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Align `competencies_contract.yaml`, `section_product_shape_ssot`, rigor constants (`MIN=MAX=6`) | ~3K | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `competency_selector_v2.yaml` forbids JD/briefing/base competencies as proof.
- Output contract: exactly **6** categories (`graph_10x6`, min=max=6).
- Display pattern: `Category Label: term, term, term` unchanged.

WAVE_COMPLETE: plan=competencies-graph-10x6-gemini-924516 wave=1 note="+prompt/contract SSOT, rigor MIN=MAX=6, w2d 26 pass"

**Key files**:
- `apps_rg/prompt_assembly/templates/competency_selector_v2.yaml`
- `apps_rg/prompt_assembly/templates/competency_selector_v2.pa_slots.yaml`
- `apps_rg/runtime/sections/competencies_pa.py`
- `apps_rg/prompt_assembly/section_contracts/competencies_contract.yaml`
- `apps_rg/runtime/sections/section_product_shape_ssot.py`
- `apps_rg/runtime/sections/competencies_rigor.py`

---

## Wave 2 — Runtime 10→6 graph selection

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W2.1** — Constants: `COMPETENCIES_SC_PATH_COUNT = 10`, `COMPETENCIES_FINAL_CATEGORY_COUNT = 6`, `COMPETENCIES_CANDIDATE_CATEGORY_COUNT = 10` in `employment_bullet_pool.py` / `section_reasoning_intensity.py` | ~4K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Extend `bullet_pool_claude_selector` competencies branch: score 10 category blocks, keep top 6 with `min_selection_score` + graph skill/fact support | ~10K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** — Wire `competencies_lane_execution` generation meta + `graph_selection_rationale.json`; ensure proof pool `selected_skill_rows` / `allowed_skill_ids` feed selector context | ~4K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Qwen generates **10** pool paths (or 10 explicit category candidates per path — document chosen shape in receipt).
- Claude selector (or deterministic ranker if Claude blocked) returns **6** categories, all passing `term_supports_resume_or_graph`.
- No read of base `facts.skills` for proof or inventory authority.

**Key files**:
- `apps_rg/runtime/reasoning/employment_bullet_pool.py`
- `apps_rg/runtime/reasoning/bullet_lane_generation.py`
- `apps_rg/runtime/judges/bullet_pool_claude_selector.py`
- `apps_rg/runtime/sections/competencies_lane_execution.py`
- `apps_rg/fact_inventory/competencies_graph_skills_proof_pool.py`
- `apps_rg/runtime/graph_selection_rationale.py`

---

## Wave 3 — Single Gemini Pro X1D judge

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W3.1** — Add `competencies_pool_x1d_judge_rows()` in `employment_bullet_pool.py` (or sibling module): one row, `provider_key=gemini_pro`, scores from pool selection / gate | ~4K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — `competencies_lane_execution`: when `generation_mode` is pool, use pool judge rows; else fallback single `run_competencies_judges(judge_keys=["gemini_pro"])`. Change defaults in `competencies_lane_runtime.py`, `canonical_dispatch.py`, `generated_lane_rollup.py` help text | ~2K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `x1d_llm_judge_outputs.json` contains **exactly one** judge entry for competencies product runs.
- Default CLI: `--x1d-judges gemini_pro` (not triple panel).
- X2 does not require `openai_chatgpt` / `anthropic_claude` for competencies (unlike executive_summary).

**Reference pattern** (employment bullets — single pool judge row):

```228:288:apps_rg/runtime/reasoning/employment_bullet_pool.py
def employment_pool_x1d_judge_rows(...) -> list[dict[str, Any]]:
    """Single X1D row from Claude pool selection (15× Qwen paths → top-N pass)."""
    ...
    return [row]
```

**Target**: same shape with `gemini_pro` + competencies pool selector artifacts.

---

## Wave 4 — Tests & proof

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W4.1** — Tests: `test_w2d_competency_selector` (6 categories, 10 pool), new `test_competencies_10x6_pool.py`, extend graph proof pool tests; update `test_competencies_rigor_constants_derived_from_ssot` if min=max=6 | ~10K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Commands**:
```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py tests/_apps_contract/test_w2d_competency_selector.py tests/unit/apps_rg/test_competencies_10x6_pool.py -q
python -m apps_rg --section competencies --provider qwen_vllm --x1d-judges gemini_pro --mock-judges
```

**Acceptance**:
- Contract tests fail before W2/W3 implementation (TDD) then pass after.
- Mock-judges run produces 6 categories + 1 X1D row without triple-panel requirement.

---

## Gap Register

**GAP-1: 10→6 selection not implemented**
- Current: 4 SC paths, 6–8 categories, Claude per-label merge.
- Target: 10 paths/candidates → score → 6 emitted.

**GAP-2: Base résumé prompt drift**
- `competency_selector_v2.yaml` still cites `facts.skills` / BASE RESUME PARITY; runtime PA uses graph projection.

**GAP-3: Triple X1D panel**
- Default `gemini_pro,openai_chatgpt,anthropic_claude` in `competencies_lane_runtime.py` / dispatch.
- Target: `gemini_pro` only + pool judge row when SC+selector active.

**GAP-4: Taxonomy projection vs free-form categories**
- `finalize_competencies_v3_output` maps to fixed taxonomy (7 labels). W2 must decide: top-6 from taxonomy buckets vs 6 free-form graph clusters (recommend: **6 taxonomy buckets** with graph-ranked terms inside).

---

## Definition of Done

DoD-1: Competencies proof remains `augmented_skills_graph` only (no `facts.skills` authority, no broad_skills_ledger fallback).
- Evidence: `python -m pytest tests/unit/apps_rg/fact_inventory/test_competencies_graph_skills_proof_pool_p2_w1a.py -q`
- Status: TODO

DoD-2: Runtime emits exactly 6 graph-grounded competency categories from a 10-candidate pool.
- Evidence: contract test `test_competencies_10x6_pool.py` + artifact `bullet_pool_selection.json` shows ≤10 scored, 6 merged
- Status: TODO

DoD-3: Single X1D judge `gemini_pro` for competencies lane.
- Evidence: `x1d_llm_judge_outputs.json` length 1; default `--x1d-judges gemini_pro` in lane CLI
- Status: TODO

DoD-4: Prompt/PA SSOT matches graph-only + colon keyword format.
- Evidence: grep gate or contract test on `competency_selector_v2.yaml` (no `facts.skills` as authority)
- Status: TODO

DoD-5: Smoke run (mock judges acceptable for CI).
- Evidence: `python -m apps_rg --section competencies --x1d-judges gemini_pro --mock-judges` exit 0
- Status: TODO

### Verification vs Deferral

| Item | In DoD | Deferred |
|------|---------|----------|
| REAL_LLM Brown run all lanes | No | DS-10 graph-skills deferred register |
| Executive summary judge panel | No | Unchanged |
| `agentic_core` judge harness | No | apps_rg only |

---

## Immutable Constraints

- L2 proposes; no durable writes outside Exit/UWG.
- Locked deterministic copy unchanged.
- Do not weaken X2 gates to pass bad output.
- `augmented_skills_graph` remains sole skills/competency proof authority (P2-W1A).

---

## Related artifacts

- Validation thread: competencies graph authority vs 10→6 / single-judge gap (2026-05-27).
- Receipts: `docs/reports/apps_rg/competencies_graph_proof_pool_p2_w1a_default_graph_authority_receipt.json`
- Employment pool reference: `apps_rg/runtime/reasoning/employment_bullet_pool.py`
