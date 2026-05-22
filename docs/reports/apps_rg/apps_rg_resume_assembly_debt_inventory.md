# apps_rg resume assembly — technical debt inventory

**Parent plan:** [apps-rg-resume-assembly-debt-burndown-56c022.md](../../.cursor/plans/apps-rg-resume-assembly-debt-burndown-56c022.md)  
**DOCX child plan:** [apps-rg-docx-output-removal-4650ff.md](../../.cursor/plans/apps-rg-docx-output-removal-4650ff.md)  
**Date:** 2026-05-22

---

## Golden path vs offline

| Path | Entry | Assembly outputs |
|------|-------|------------------|
| **Product** | `python -m apps_rg` → `modular_resume_generation` | `{artifact_dir}/` modular root: lanes → rollup → locked_copy → assemble → **rg_output** |
| **Offline** | `tests/helpers/offline_lane_orchestration` | Global `artifacts/apps_rg/runtime_proofs/*` + package X3 + DOCX |

`canonical_dispatch` does **not** call `build_rollup()` or `emit_resume_package_artifacts`.

---

## Delete-risk matrix

### Safe to delete (A1–A9)

| ID | Item |
|----|------|
| A1 | Ghost `apps_rg.runtime.package.resume_package_x3` (no module file) |
| A2 | `apps_rg.runtime._offline.*` policy paths (modules deleted) |
| A3 | Retired `*_dispatch` modules |
| A4 | `lane_batch.run_orchestration()` (ImportError stub) |
| A5 | Deleted tools (`render_resume_docx`, `resume_docx_renderer`, …) |
| A6 | Empty `apps_rg/runtime/reports/` package |
| A7 | `NarrativePassStep` (not in recipe registry; `narrative_adapter` missing) |
| A8 | Ghost `ops_scripts/apps_rg/narrative_pass.py` |
| A9 | Stale `outside_main_entry_policy` docx renderer paths |

### Not safe without migration (B1–B10)

| ID | Item | Why |
|----|------|-----|
| B1 | Global `build_rollup()` | Offline/tests; latest-per-lane pointer semantics |
| B2 | `resume_package_x3` / disposition | Large contract test surface |
| B3 | `offline_lane_orchestration` | E2E CI driver |
| B4 | `lane_batch` constants | SSOT for lanes / base resume |
| B5 | `RgResumeOrchestrator` + reasoning agents | `apps_eval` + facade |
| B6 | `apps_rg/engines/*` | Unit tests + taxonomy |
| B7 | `srfs_receipt_aggregator`, `one_spine_inventory` | Audit tooling |
| B8 | `prepare_orchestrator_inputs` | RUNBOOK CLI |
| B9 | `full_resume_review_bundle` | R3/R4 whole-run |
| B10 | `integrated_product_proof_gate` | Product proof validator |

### Conditional (C1–C7)

| ID | Item | Notes |
|----|------|-------|
| C1 | `final_resume_assembled_v2` vs `rg_output` | Assembler still bridges integrated merge |
| C2 | Full assembly + `aggregation/*` on integrated path | Runs every modular whole-run |
| C3 | `full_resume_llm_coherence` | Env-gated aggregate judge |
| C4 | `aggregation/` package | Wired in assembler |
| C5 | Committed `runtime_proofs` artifacts | Stop writes before delete |
| C6 | `DocxExportStep` + artifact gate | See DOCX child plan |
| C7 | `render_run_summary` DOCX refs | Update with DOCX removal |

---

## Recommended wave order

1. **W1** — Safe ghosts (A*)  
2. **W2** — DOCX child plan  
3. **W3** — Direct lane → `rg_output` (drop C1 bridge)  
4. **W4** — Demote offline rollup + package X3  
5. **W5** — Engines/reasoning boundary documentation  

---

## Architecture (current)

```
python -m apps_rg
  → section lanes
  → build_modular_lane_rollup
  → build_locked_copy
  → assemble_final_resume (+ aggregation X2)
  → build_rg_output_from_modular_sections
  → [optional DocxExportStep]

offline tests only:
  → build_rollup (latest per lane)
  → … → docx → resume_package_x3
```
