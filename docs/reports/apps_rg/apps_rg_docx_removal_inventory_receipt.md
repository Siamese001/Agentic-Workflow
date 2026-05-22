# apps_rg DOCX removal — inventory receipt (W0)

**Plan:** [apps-rg-docx-output-removal-4650ff.md](../../.cursor/plans/apps-rg-docx-output-removal-4650ff.md)  
**Date:** 2026-05-22  
**Status:** W0 complete — implementation W1–W4 deferred

---

## Summary

apps_rg maintains **two DOCX pipelines** and **package-level hard requirements** for DOCX X2 gates and on-disk `.docx` files. Section lanes are already decoupled (`docx_render_ref: null`). Retiring DOCX means JSON-only product gates first, then stop emission, delete modules, migrate tests/CI.

---

## Dual pipelines

| Stack | Output | Modules |
|-------|--------|---------|
| Integrated R4 | `{artifact_dir}/outputs/resume.docx` | `DocxExportStep`, `json_resume_docx.py`, `resume_artifact_gate.py` |
| Offline package | `artifacts/apps_rg/runtime_proofs/docx/amit_ayer_resume_v1.docx` | `docx_manifest_builder.py`, `docx_renderer.py`, `docx_*_x2.py` |

---

## Consolidation chain (package “consolidator”)

`generated_lane_rollup` → `locked_copy` → `final_resume_assembler` → `docx_manifest` → `docx_renderer` → `resume_package_x3`

`resume_package_disposition` blocks on: `docx_manifest_x2`, `docx_render_x2`, `output_docx` on disk, and integrated `apps_rg_output_manifest` `docx_verified`.

---

## Contradiction

- `final_resume_x2`: gate `x2_no_docx_render` — no `.docx` in assembly dir
- Package X3: requires DOCX render proof and file

---

## Artifact paths to retire

- `artifacts/apps_rg/runtime_proofs/docx/*`
- `artifacts/apps_rg/runtime_proofs/docx_manifest/*`
- Per-run `outputs/resume.docx`, manifest fields `resume_docx_relpath`, `docx_verified`

---

## Stale references

- `outside_main_entry_policy.py`: `apps_rg.runtime.render.docx_renderer` (module is `internal/docx_renderer.py`)
- Prompt inventories: wrong path `runtime/render/docx_renderer.py`
- Deleted tools (enforced absent): `tools/apps_rg/render_resume_docx.py`, `resume_docx_renderer.py`

---

## Execution waves (deferred)

| Wave | Focus |
|------|--------|
| W1 | JSON-only product gates |
| W2 | Stop emission (recipe + offline orchestrator) |
| W3 | Delete modules + prompt/config cleanup |
| W4 | Tests, CI W7, receipt updates |

---

## Proof (W0)

```text
PLAN_COMPLETE: plan=apps-rg-docx-output-removal-4650ff note="W0 inventory receipt"
```
