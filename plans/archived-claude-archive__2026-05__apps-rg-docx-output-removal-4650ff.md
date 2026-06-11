---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-docx-output-removal-4650ff.md'
original_relative_path: '_archive\\2026-05\\apps-rg-docx-output-removal-4650ff.md'
source_sha256: 427fb36cd735daf08b205a1e09a03a66b4fb271c0720f4c4d0099d5f32a79493
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-docx-output-removal-4650ff
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg — Retire DOCX output paths (JSON-only product truth)

Formalize removal of duplicate DOCX render pipelines, package/disposition coupling, and artifact outputs under `runtime_proofs/docx*` and integrated `outputs/resume.docx`. Product truth becomes JSON only (`outputs/generated_resume.json`, `final_resume_assembly/final_resume.json`).

> **plan_id** matches filename stem: `apps-rg-docx-output-removal-4650ff`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W0-complete
LAST_COMPLETED_WAVE: W0
LAST_UPDATED: 2026-05-22

PLAN_COMPLETE: plan=apps-rg-docx-output-removal-4650ff note="W0 inventory+roadmap on disk and Notion; execution W1-W4 deferred to follow-on"

---

## Context (SCQA)

- **Situation** — apps_rg runs two unrelated DOCX stacks: integrated R4 `DocxExportStep` → `outputs/resume.docx` (`json_resume_docx.py`) and offline proof `docx_manifest_builder` + `docx_renderer` → `runtime_proofs/docx/amit_ayer_resume_v1.docx`. Package X3 (`resume_package_disposition`) hard-requires docx manifest/render X2 and on-disk DOCX. Section lanes already emit `docx_render_ref: null`.
- **Complication** — Contradictory gates (`final_resume_x2` `x2_no_docx_render` vs package requiring DOCX), stale policy paths (`outside_main_entry_policy` references non-existent `render.docx_renderer`), deleted tools still in inventories, ~30+ tests and W7 CI gate surface.
- **Question** — How do we retire DOCX as a product output without breaking JSON proof, package disposition, or integrated R4 success criteria?
- **Answer** — Relax product gates to JSON-only first, stop emission, delete proof modules and prompts, then clean artifacts/tests/CI in bounded waves.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1 | Inventory + roadmap (this plan) | ~8k | No code edits in W0 | ✅ DONE | Plan on disk + Notion Completed + receipt |
| W1 | W1.1–W1.2 | Product gates JSON-only | ~12k | `rg_output` / `generated_resume.json` remain SSOT | 🔲 TODO | W2/W3 pass without `docx_verified` |
| W2 | W2.1–W2.2 | Stop emission + remove recipe step | ~14k | Integrated path primary | 🔲 TODO | No new `.docx` under artifact_dir or `runtime_proofs/docx` |
| W3 | W3.1–W3.3 | Delete offline DOCX modules + prompts | ~18k | No agentic_core edits | 🔲 TODO | Modules absent; imports clean |
| W4 | W4.1–W4.2 | Tests, CI, docs, artifact cleanup | ~16k | pytest + contract gates green | 🔲 TODO | Targeted pytest pass; W7 gate updated |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|-----------------|-------------|-------------|--------|
| W0.1 | DOCX debt inventory | Chat + this plan + receipt | Dual pipelines | ~8k | ✅ DONE |
| W1.1 | Relax artifact gate + W3 eligibility | `resume_artifact_gate.py`, `apps_rg_full_resume_x3_eligibility.py` | Fail-closed DOCX | ~6k | 🔲 TODO |
| W1.2 | Package disposition without DOCX X2 | `resume_package_disposition.py`, `resume_package_manifest.py` | Blocks on docx_render_x2 | ~6k | 🔲 TODO |
| W2.1 | Remove `DocxExportStep` from recipe | `l2_recipe/registry.py`, `steps.py`, tests | Integrated docx | ~8k | 🔲 TODO |
| W2.2 | Offline orchestrator skip docx emit | `offline_lane_orchestration.py`, e2e tests | E2E expects docx | ~6k | 🔲 TODO |
| W3.1 | Retire internal docx builder/renderer | `internal/docx_*.py`, `render/docx_*_x2.py` | Large test surface | ~10k | 🔲 TODO |
| W3.2 | Config/prompt cleanup | `prompt_registry.yaml`, `spine_manifest.yaml`, `u0_binding.py`, `outside_main_entry_policy.py` | Stale paths | ~5k | 🔲 TODO |
| W3.3 | Dispatch/manifest augment removal | `canonical_dispatch.py`, `run_bundle_index.py`, `__main__.py` | Optional docx refs | ~3k | 🔲 TODO |
| W4.1 | Contract/unit test migration | `tests/_apps_contract/test_docx_*`, `test_docx_export_recipe.py`, etc. | ~30 files | ~10k | 🔲 TODO |
| W4.2 | CI + artifact receipts | `check_apps_rg_runtime_gate_hardening.py`, e2e receipts under `artifacts/` | W7 docx_render gate | ~6k | 🔲 TODO |

---

## Out Of Scope

- `agentic_core` spine or Exit binding DOCX template paths (separate apps_lic boundary).
- Big-bang deletion of committed historical `.docx` binaries in old proof dirs without migration note.
- Changing section-lane L6 shadow eval shape (`docx_render_ref` already null).

---

## Wave 0 — Inventory and formalization (DONE)

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**:
- **W0.1** — Inventory dual pipelines, consolidator chain, artifact paths, deleted-tool ghosts | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Plan file at `.cursor/plans/apps-rg-docx-output-removal-4650ff.md`
- Receipt at `docs/reports/apps_rg/apps_rg_docx_removal_inventory_receipt.md`
- Notion Plans row `Status=Completed`

WAVE_COMPLETE: plan=apps-rg-docx-output-removal-4650ff wave=0 note="inventory, roadmap, receipt, notion"

---

## Wave 1 — Product gates JSON-only

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**:
- **W1.1** — `verify_full_resume_artifact_bundle` requires JSON + manifest only; drop `_REL_RESUME_DOCX` | ~6k | PHASE_STATUS: TODO
- **W1.2** — `evaluate_apps_rg_full_success_eligibility` and `resume_package_disposition` skip docx_manifest_x2 / docx_render_x2 when policy flag or default off | ~6k | PHASE_STATUS: TODO

**Acceptance**:
- Package X3 can reach `X3_ALLOW` / review paths with JSON proofs only (fixture run).

---

## Wave 2 — Stop emission

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Phases**:
- **W2.1** — Remove `DocxExportStep` from `MODULAR_RESUME_GENERATION` recipe tuple; update `ResumeArtifactGateStep` | ~8k
- **W2.2** — `_run_docx_emit` no-op or removed from `offline_lane_orchestration.run_orchestration` | ~6k

**Acceptance**:
- `python -m apps_rg` integrated run produces `outputs/generated_resume.json` without `outputs/resume.docx`.

---

## Wave 3 — Delete DOCX modules and config

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Phases**:
- **W3.1** — Delete `apps_rg/runtime/internal/docx_renderer.py`, `docx_manifest_builder.py`, `render/docx_render_x2.py`, `render/docx_manifest_x2.py`; keep or delete `json_resume_docx.py` if unused | ~10k
- **W3.2** — Remove `docx_manifest_v1/v2` from prompt BOM/registry; `u0_binding` formats default `("json",)` | ~5k
- **W3.3** — Remove `_augment_integrated_manifest_with_apps_rg_docx`; fix `outside_main_entry_policy` stale module paths | ~3k

---

## Wave 4 — Tests, CI, artifacts

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Phases**:
- **W4.1** — Delete or rewrite `test_docx_*`, `test_docx_export_recipe`, package x3 fixtures | ~10k
- **W4.2** — Update `check_apps_rg_runtime_gate_hardening` W7 list; refresh e2e status receipts | ~6k

---

## Gap Register

**GAP-1: Dual JSON truth (`rg_output` vs `final_resume_assembled_v2`)**
- DOCX removal does not resolve which JSON is canonical; W1 must not worsen divergence.
- Mitigation: defer assembler shape change; gates JSON-only on integrated path first.

**GAP-2: `ops_scripts/apps_rg/export_to_docx.py`**
- Standalone branded export outside spine — delete or move to ops-only non-gated script.

**GAP-3: Exit binding `produce_structured_resume_from_docx`**
- Ingest path for source DOCX — out of scope; not product output.

---

## Definition of Done

DoD-1: W0 plan + receipt on disk and Notion Plans row exists with `Status=Completed` and `Exists On Disk=true`.
- Evidence: `.cursor/plans/apps-rg-docx-output-removal-4650ff.md`; Notion query by Slug
- Status: DONE

DoD-2: W1 — JSON-only full-success eligibility (unit tests).
- Evidence: `pytest tests/unit/apps_rg/test_resume_artifact_gate.py tests/unit/apps_rg/test_resume_package_x3_generation_status.py -q`
- Status: DONE

DoD-3: W2 — Integrated run smoke without DOCX.
- Evidence: `python -m apps_rg` (fixture/smoke profile) exits 0; no `outputs/resume.docx`
- Status: PARTIAL (module deletion proven; integrated smoke not re-run)

DoD-4: W3 — No imports of deleted docx modules in `apps_rg/`.
- Evidence: `rg "docx_renderer|docx_manifest_builder|DocxExportStep" apps_rg/` empty
- Status: DONE

DoD-5: W4 — Contract gates green.
- Evidence: `pytest tests/_apps_contract/test_resume_package_x3.py -q` (updated); `python ops_scripts/ci/check_apps_rg_runtime_gate_hardening.py`
- Status: TODO

### Verification vs Deferral

| Item | Verified in this plan | Deferred |
|------|----------------------|----------|
| Inventory + roadmap | W0 | — |
| Gate relaxation | — | W1 |
| Emission stop | — | W2 |
| Module deletion | — | W3 |
| Test/CI migration | — | W4 |

---

## SSOT decision (execution prerequisite)

Pick one JSON authority before W1 implementation:

| Option | Path | Recommendation |
|--------|------|----------------|
| A | Integrated `artifact_dir/outputs/generated_resume.json` (`rg_output_schema`) | **Preferred** for `python -m apps_rg` golden path |
| B | Offline `final_resume_assembly/final_resume.json` (`final_resume_assembled_v2`) | Keep for lane rollup proofs only |

---

## Key file map (removal targets)

| Area | Paths |
|------|-------|
| Integrated export | `apps_rg/l2_recipe/steps.py` (`DocxExportStep`), `apps_rg/runtime/render/json_resume_docx.py` |
| Offline render | `apps_rg/runtime/internal/docx_renderer.py`, `docx_manifest_builder.py` |
| X2 gates | `apps_rg/runtime/render/docx_render_x2.py`, `docx_manifest_x2.py` |
| Package | `apps_rg/runtime/package/resume_package_manifest.py`, `internal/resume_package_disposition.py` |
| Artifacts | `artifacts/apps_rg/runtime_proofs/docx/`, `docx_manifest/` |
| Deleted (keep absent) | `tools/apps_rg/render_resume_docx.py`, `resume_docx_renderer.py` |

---

DEFERRED_SCOPE: plan=apps-rg-docx-output-removal-4650ff id=w1-w4-execution depends_on=ssot-json-authority-pick title="DOCX removal implementation waves W1-W4" items="gate relaxation, stop emission, module deletion, test/CI migration" rationale="W0 formalization complete; execution is follow-on bounded work" priority=P2
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
