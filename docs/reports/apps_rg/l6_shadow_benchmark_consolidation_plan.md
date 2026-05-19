# L6 Shadow Benchmark Consolidation Plan

**Report date:** 2026-05-18  
**Status:** DESIGN_ONLY  
**proof_eligible:** false  

---

## Executive summary

This report records the consolidation of apps_rg human benchmark strategy from **per-section first-pass calibration** (including separate IBM bullet/narrative waves) to **pooled decision-surface calibration** for L6 shadow learning and future X1D judge calibration. Work is **documentation and schema only** — no runtime, gate, judge, or data-collection changes.

---

## Scope delivered (2 waves)

### Wave 1 — Plan docs

| Artifact | Path |
|----------|------|
| Human benchmark plan (pooled) | [human_benchmark_plan.md](artifacts/apps_rg/plans/human_benchmark_plan.md) |
| Public dataset sourcing notes | [public_dataset_sourcing_notes.md](artifacts/apps_rg/plans/public_dataset_sourcing_notes.md) |
| This consolidation report | [l6_shadow_benchmark_consolidation_plan.md](docs/reports/apps_rg/l6_shadow_benchmark_consolidation_plan.md) |

### Wave 2 — Schema + manifest

| Artifact | Path |
|----------|------|
| Benchmark sample schema (draft-07) | [human_benchmark_schema.json](artifacts/apps_rg/plans/human_benchmark_schema.json) |
| Design-only manifest | [l6_shadow_benchmark_consolidation_manifest.json](docs/reports/apps_rg/l6_shadow_benchmark_consolidation_manifest.json) |

**Receipt (hyperlinked):** [l6_shadow_benchmark_consolidation_receipt.md](docs/reports/apps_rg/l6_shadow_benchmark_consolidation_receipt.md)

---

## Inputs

- **Existing X1D human benchmark plan:** `.cursor/plans/p5.1_apps-rg-x1d-human-benchmark-plan-9e4c2f.md`
- **Current apps_rg generated section set:** headline, executive_summary, competencies, unify_narrative, unify_bullets, ibm_narrative, ibm_bullets, plus deterministic copy-verbatim fields
- **W14 scaffold:** `apps_rg/evals/section_quality_benchmark/` (per-section row schemas — complementary, not replaced)

---

## Consolidation decisions

| Topic | Decision |
|-------|----------|
| IBM bullets | Calibrate inside **`pooled_bullets`** first; no separate first-pass IBM-only track |
| IBM narrative | Calibrate inside **`pooled_narratives`** first; no separate first-pass IBM-only track |
| IBM-only split | Permitted only if slice metrics show material underperformance vs pool |
| P0 standalone | `headline`, `executive_summary`, `competencies` |
| P0 pooled | `pooled_bullets` (unify + ibm), `pooled_narratives` (unify + ibm) |
| Deterministic sections | **No** human L6 calibration (header, contact, companies, titles, dates, education, certs, early_career) |
| Final aggregation | 30–40 samples **if** evaluator implemented (conditional) |

---

## L6 shadow constraints (documented)

- Consumes completed-run **RuntimeExhaustBundle** after current-run boundary
- Emits **CompletedEvalRecord**, **RCA**, **ProposalPacket** only
- Future promotion via **UWG** — not current-run mutation
- Aligns with `apps_rg/runtime/shadow/l6_shadow_learning.py` observer-only posture (no code change in this effort)

---

## Sample targets (future)

| Surface | n |
|---------|---|
| headline | 30–40 |
| executive_summary | 40–60 |
| competencies | 30–40 |
| pooled_narratives | 60 (section-tagged) |
| pooled_bullets | 80 (section-tagged) |
| final_aggregation | 30–40 (if implemented) |

---

## Calibration thresholds (future)

- Cohen kappa ≥ 0.65 (inter-rater)
- Spearman rho ≥ 0.80 (human vs judge)
- Report false PASS / false FAIL rates
- Uncalibrated judges: advisory only

---

## Non-claims

- No human labels collected
- No datasets ingested
- No judge promoted
- No runtime behavior changed
- No calibration complete
- `agentic_core` not modified

---

## Open gaps

1. Reviewer workflow not implemented  
2. Benchmark collection not implemented  
3. Human scoring not collected  
4. Judge calibration report not computed  
5. Final aggregation evaluator may not exist — conditional targets only  
6. Drift holdout split undefined until collection wave  

---

## Verification pointers

See [l6_shadow_benchmark_consolidation_manifest.json](docs/reports/apps_rg/l6_shadow_benchmark_consolidation_manifest.json) and [l6_shadow_benchmark_consolidation_receipt.md](docs/reports/apps_rg/l6_shadow_benchmark_consolidation_receipt.md) for `files_changed`, `commands_run`, and validation results.
