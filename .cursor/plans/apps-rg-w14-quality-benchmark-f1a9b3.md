---
plan_id: apps-rg-w14-quality-benchmark-f1a9b3
plan_type: doc
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: true
---

# apps_rg W14 — Section quality benchmark (offline evaluation scaffold)

Executable Cursor plan for **offline** resume-section quality evaluation: rubric dimensions, artifact layout, and future calibration phases — **without** promoting X1D to runtime release authority or mutating **L6** on the active run. See also: `docs/reports/apps_rg_prompt_authority/W14_quality_benchmark.md`.

> **plan_id discipline**: `plan_id` matches filename stem; wave markers use `plan=apps-rg-w14-quality-benchmark-f1a9b3`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: TODO  
CURRENT_WAVE: W0  
LAST_COMPLETED_WAVE: NONE  
LAST_UPDATED: 2026-05-15  

---

## Context (SCQA)

- **Situation** — W12 proves deterministic/X2 plumbing and prompt authority; subjective quality still needs **offline** measurement for judge calibration narratives.
- **Complication** — Ad-hoc scoring contaminates SSOT, risks treating X1D as release gate, and violates L6 future-run-only discipline.
- **Question** — How do we structure benchmarks, schemas, and phases so operators can label and calibrate **later** without blocking ship?
- **Answer** — Scaffold + governance boundaries + phased freeze/label/calibrate/report — no mandatory human scores in this plan’s initial execution.

---

## Hard boundaries

| Constraint | Reason |
|------------|--------|
| X2 remains runtime hard gate where coded | Determinism ownership |
| X1D stays **soft / advisory** until explicit offline promotion policy | Release safety |
| No L6 durable writes from L2/L3/tools/Exit during active run | Spine law |
| No fabricated benchmark scores in scaffold artifacts | Integrity |

---

## Wave summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.P1–W1.P2 | Scaffold directory + README + JSON Schema stub | ~4K | `apps_rg/evals/` writable | 🔲 TODO | Paths exist; README warns against fabricated scores |
| W2 | W2.P1 | **Freeze** phase spec (prompt_hash, contract ID, model version) | ~2K | W1 scaffold | 🔲 TODO | Written checklist for row metadata |
| W3 | W3.P1–W3.P2 | **Label / Calibrate / Report** procedure (doc-only) | ~3K | None | 🔲 TODO | Operator doc complete; no CI gate changes required |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Create `section_quality_benchmark/` tree | `apps_rg/evals/section_quality_benchmark/` | Folder taxonomy | ~2K | 🔲 TODO |
| W1.P2 | README + `*.schema.json` stub | same | Schema drift vs X2 | ~2K | 🔲 TODO |
| W2.P1 | Freeze metadata contract | plan + README | Version pinning | ~2K | 🔲 TODO |
| W3.P1 | Labeling procedure | docs in tree | PII / consent | ~1.5K | 🔲 TODO |
| W3.P2 | Calibration + reporting outline | docs in tree | Correlation scope | ~1.5K | 🔲 TODO |

---

## Dimensions (evaluation axes)

1. Factual support  
2. JD fit  
3. Executive presence  
4. Concision  
5. Specificity  
6. Seniority signal  
7. Unsupported claim risk  
8. Resume usefulness  

---

## Out of scope

- Running large human-label campaigns **in this plan’s first pass** (optional future execution).
- Changing X1D runtime thresholds or Exit policy.
- Core (`agentic_core`) judge relocation.

---

## Gap register

**GAP-1:** Benchmark rows must **never** back-propagate into locked deterministic sections without a separate ADR.

**GAP-2:** Public or third-party resume snippets require separate data-handling review before any labeling at scale.

---

## Definition of Done

*(dod_exempt: true — scaffold/design plan; verification is artifact presence + governance text, not production benchmark scores.)*

- DoD-1: `apps_rg/evals/section_quality_benchmark/README.md` exists with operator warnings.
- DoD-2: At least one `*.schema.json` for label rows (optional fields; no pre-filled scores).
- DoD-3: Freeze / label / calibrate / report phases documented in plan or README.
- DoD-4: Explicit statement that X1D is **not** a runtime release gate in this design.
- DoD-5: Cross-link from `docs/reports/apps_rg_prompt_authority/W14_quality_benchmark.md` updated if scaffold paths differ from that doc’s sketch.

---

## Marker quick reference

```
WAVE_START: plan=apps-rg-w14-quality-benchmark-f1a9b3 wave=1
WAVE_COMPLETE: plan=apps-rg-w14-quality-benchmark-f1a9b3 wave=1 note="scaffold files, scope=evals"
PLAN_COMPLETE: plan=apps-rg-w14-quality-benchmark-f1a9b3 note="W14 scaffold complete or deferred with reason"
```
