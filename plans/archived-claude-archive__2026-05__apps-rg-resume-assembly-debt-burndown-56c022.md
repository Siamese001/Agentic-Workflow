---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-resume-assembly-debt-burndown-56c022.md'
original_relative_path: '_archive\\2026-05\\apps-rg-resume-assembly-debt-burndown-56c022.md'
source_sha256: 078001d41bb22c253dfeaec9cd99f392ddcbd54f5a31d2a4659e3ea779cba195
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-resume-assembly-debt-burndown-56c022
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg — Resume assembly debt burndown (JSON SSOT + offline stack demotion)

Reduce resume assembly technical debt: retire unused/ghost paths, complete DOCX removal (child plan), converge integrated product truth to **`rg_output` / `outputs/generated_resume.json`**, and demote global `runtime_proofs` rollup→package X3 stack to contract-only or delete.

**Related plan (DOCX):** [apps-rg-docx-output-removal-4650ff.md](apps-rg-docx-output-removal-4650ff.md) — execute W1–W4 here as **W2** after W1 safe cleanup.

> **plan_id** matches filename stem: `apps-rg-resume-assembly-debt-burndown-56c022`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-05-25
NOTION_STATUS: Completed
NOTION_RECONCILED: 2026-05-25
PLAN_COMPLETED: 2026-05-25
CLOSEOUT_CLASS: W0_W3_PRODUCT_JSON_SSOT_DONE
PLAN_COMPLETE: plan=apps-rg-resume-assembly-debt-burndown-56c022 note="W0-W3 lane merge + fail-closed assembly"
DEFERRED_SCOPE: W4_offline_demotion,W5_engines_reasoning_boundary
CLOSEOUT_RECEIPT: docs/reports/plans/active_backlog_closeout_receipt_20260525.md
NOTION_PAGE_ID: 36827693-f55c-811f-9cae-c14d491432c4
NOTION_RECONCILED: 2026-05-24
ACTIVE_BACKLOG_MANIFEST: docs/reports/plans/active_in_progress_plans_manifest_20260524.md
ACTIVE_BACKLOG_ROLE: spine_child_w5
PARENT_PLAN: apps-rg-spine-only-unification-d8f4a2

PLAN_CREATED: slug=apps-rg-resume-assembly-debt-burndown-56c022 path=.cursor/plans/apps-rg-resume-assembly-debt-burndown-56c022.md status=Not Started

---

## Context (SCQA)

- **Situation** — Golden path `python -m apps_rg` uses `modular_resume_generation`: section lanes → `build_modular_lane_rollup` → `locked_copy` → `assemble_final_resume` → `build_rg_output_from_modular_sections`. A parallel **offline** stack (`build_rollup` latest-per-lane → assembly → DOCX → `resume_package_x3`) runs only in tests/helpers. Section lanes already omit DOCX (`docx_render_ref: null`).
- **Complication** — Dual JSON shapes (`final_resume_assembled_v2` vs `rg_output_schema`), redundant assembler bridge, package X3 not on integrated CLI but large contract surface, ghost modules (`resume_package_x3`, `_offline.*`, `NarrativePassStep`), and superseded reasoning/engines kept for eval.
- **Question** — How do we simplify assembly to one JSON product truth and shrink safe-to-remove debt without breaking integrated R4 or contract gates?
- **Answer** — Safe ghost cleanup first; DOCX removal (child plan); then direct lane→`rg_output` merge on integrated path; finally demote or delete offline global rollup/package proofs with test migration.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1 | Inventory + risk matrix (chat + receipt) | ~10k | Analysis only | ✅ DONE | Receipt + this plan on disk |
| W1 | W1.1–W1.3 | Safe ghost / dead-step cleanup | ~8k | No behavior change on golden path | ✅ DONE | outside_main + l2 registry tests pass |
| W2 | W2.1–W2.4 | DOCX removal (child plan W1–W4) | ~50k | See docx plan | ✅ DONE | No product DOCX; JSON gates pass |
| W3 | W3.1–W3.3 + fail-closed | JSON SSOT + live assembly/judges/BGE | ~35k | `outputs/generated_resume.json` authoritative | ✅ DONE (unit) | Lane merge; gap placeholders; product policy; live smoke still manual |
| W4 | W4.1–W4.2 | Offline stack demotion | ~25k | Contract tests migrated | 🔲 TODO | No `build_rollup()` on product path; package optional |
| W5 | W5.1–W5.2 | Engines/reasoning eval boundary | ~20k | `apps_eval` facade kept until migrated | 🔲 TODO | Documented ownership; no false product claims |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|-----------------|-------------|-------------|--------|
| W0.1 | Assembly debt inventory | Chat + [receipt](docs/reports/apps_rg/apps_rg_resume_assembly_debt_inventory.md) | Dual pipelines | ~10k | ✅ DONE |
| W1.1 | Remove ghost policy targets | `outside_main_entry_policy.py`, `docx_renderer.py` metadata | Stale CLI path | ~2k | ✅ DONE |
| W1.2 | Delete dead recipe step | `steps.py` `NarrativePassStep`; empty `runtime/reports/` | Unregistered step | ~2k | ✅ DONE |
| W1.3 | Doc sync for deleted CLIs | `outside_main` DISALLOWED uses `internal.docx_renderer` | Ghost `narrative_pass` kept in DISALLOWED | ~2k | ✅ DONE |
| W2.1–W2.4 | DOCX burndown | Per [apps-rg-docx-output-removal-4650ff](.cursor/plans/apps-rg-docx-output-removal-4650ff.md) | Two DOCX stacks | ~50k | ✅ DONE |
| W3.1 | Direct lane → rg_output merge | `modular_rg_output_builder.py`, `modular_resume_generation.py` | Assembler bridge | ~15k | ✅ DONE (code) |
| W3.2 | Fail-closed assembly + judges + BGE | `product_output_policy.py`, `final_resume_assembler.py`, `r1b_bge_embedding.py`, `full_resume_*` | Structural-only shortcut rejected | ~10k | ✅ DONE |
| W3.3 | Contract tests + live smoke | `test_modular_*`, `test_*_gap`, `test_product_output_policy.py` | Dual truth tests | ~10k | ✅ DONE (unit); live `python -m apps_rg` manual |
| W4.1 | Isolate `build_rollup()` to tests | `generated_lane_rollup.py`, offline helper | Mixed-run rollup | ~12k | 🔲 TODO |
| W4.2 | Package X3 contract boundary | `resume_package_disposition.py`, package tests | Not on integrated CLI | ~13k | 🔲 TODO |
| W5.1 | Engines folder disposition | `apps_rg/engines/*`, taxonomy refs | No runtime import | ~10k | 🔲 TODO |
| W5.2 | Reasoning superseded markers | `RgResumeOrchestrator`, facade, eval | Eval parity | ~10k | 🔲 TODO |

---

## Delete-risk register (from inventory)

| ID | Item | Risk | Wave |
|----|------|------|------|
| A1–A9 | Ghost modules, empty packages, `NarrativePassStep`, deleted tools | **Safe** | W1 |
| B1–B10 | Offline orchestrator, package X3, `build_rollup`, reasoning facade, engines tests | **Not safe** without migration | W4–W5 |
| C1–C7 | Dual JSON, assembler+aggregation, DOCX recipe, proof artifacts | **Conditional** | W2–W3 |

Full matrix: [apps_rg_resume_assembly_debt_inventory.md](docs/reports/apps_rg/apps_rg_resume_assembly_debt_inventory.md).

---

## Out Of Scope

- `agentic_core` Exit/UWG/L4 binding changes.
- Rewriting section-lane prompts or X2 lane gates.
- Big-bang delete of committed historical proof trees under `artifacts/apps_rg/runtime_proofs/` (stop writes first).
- Removing `RgResumeOrchestrator` before `apps_eval` facade migration (W5 documents only unless user authorizes eval break).

---

## Wave 0 — Inventory (DONE)

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

WAVE_COMPLETE: plan=apps-rg-resume-assembly-debt-burndown-56c022 wave=0 note="inventory receipt, risk matrix, parent plan"

---

## Wave 1 — Safe cleanup (ghost / dead code)

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases:** W1.1 policy/inventory path fixes · W1.2 remove `NarrativePassStep` + empty `runtime/reports` · W1.3 docs

**Acceptance:**
- `NarrativePassStep` removed from `apps_rg/l2_recipe/steps.py`; tests updated
- `pytest tests/_apps_contract/test_no_outside_main_runtime_entrypoints.py tests/unit/apps_rg/test_l2_recipe_registry.py -q` — 65 passed

WAVE_COMPLETE: plan=apps-rg-resume-assembly-debt-burndown-56c022 wave=1 note="NarrativePassStep removed, reports pkg deleted, policy/docx metadata paths fixed"

---

## Wave 2 — DOCX removal (child plan)

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

Execute [apps-rg-docx-output-removal-4650ff](.cursor/plans/apps-rg-docx-output-removal-4650ff.md) waves W1–W4 in order. Do not start W3 of this plan until W2 DoD-2 (integrated smoke without DOCX) passes.

---

## Wave 3 — JSON SSOT on integrated path

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED — architecture_choice (assembler vs direct merge)

**SSOT decision (required before W3.1):** **Option A — `artifact_dir/outputs/generated_resume.json` (`rg_output_schema`)** ← recommended.

**Phases:**
- **W3.1** — Build `rg_output` directly from lane `l2_output.json` map; stop reading `final_resume_assembly/final_resume.json` for product merge
- **W3.2** — Default `APPS_RG_ASSEMBLY_STRUCTURAL_ONLY=1` for integrated runs; assembly artifacts optional proof-only
- **W3.3** — Update generation entrypoint + modular builder tests

**Acceptance:**
- `python -m apps_rg` (smoke profile) produces valid `outputs/generated_resume.json` without requiring assembler X2 all-pass for product success

---

## Wave 4 — Offline stack demotion

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

**Phases:**
- **W4.1** — Document `build_rollup()` as test-only; ensure `canonical_dispatch` / `modular_resume_generation` never call it
- **W4.2** — Refactor `test_resume_package_x3` + offline orchestrator to explicit `@pytest.mark.offline_assembly` (or move under `tests/helpers/` only)

**Acceptance:**
- Integrated product proof gate does not require `resume_package_x3_disposition.json` in `artifacts/apps_rg/runs/<id>/`

---

## Wave 5 — Engines / reasoning boundary

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

**Phases:**
- **W5.1** — ADG/taxonomy note: `apps_rg/engines/*` = test-support, not product runtime
- **W5.2** — Extend quarantine registry; optional eval migration ticket for facade-only `RgResumeOrchestrator`

---

## Definition of Done

DoD-1: Plan + inventory receipt on disk; Notion Plans row `Status=Not Started` (or `In Progress` when execution starts).
- Evidence: `.cursor/plans/apps-rg-resume-assembly-debt-burndown-56c022.md`; Notion query by Slug
- Status: TODO (pending your review approval)

DoD-2: W1 — Safe cleanup merged; no new test failures.
- Evidence: `pytest tests/_apps_contract/test_no_outside_main_runtime_entrypoints.py tests/unit/apps_rg/test_l2_recipe_registry.py -q` — 65 passed
- Status: DONE

DoD-3: W2 — DOCX child plan DoD-3 satisfied (integrated smoke, no `outputs/resume.docx`).
- Evidence: per docx plan
- Status: TODO

DoD-4: W3 — Integrated run validates `rg_output_schema` without assembler gate blocking product.
- Evidence: `python -m apps_rg` smoke + `pytest tests/unit/apps_rg/test_modular_rg_output_builder.py -q`
- Status: TODO

DoD-5: W4 — Package X3 not required on integrated run dirs.
- Evidence: `pytest tests/unit/apps_rg/test_integrated_product_proof_gate.py -q`
- Status: TODO

### Verification vs Deferral

| Item | In plan | Deferred |
|------|---------|----------|
| Inventory | W0 ✅ | — |
| Ghost cleanup | W1 | — |
| DOCX | W2 (child plan) | — |
| JSON SSOT | W3 | Until SSOT sign-off |
| Offline package | W4 | — |
| Eval/reasoning | W5 | Full facade removal |

---

## Key paths

| Layer | Path |
|-------|------|
| Integrated merge | `apps_rg/l2_recipe/modular_rg_output_builder.py` |
| Assembly (conditional) | `apps_rg/runtime/internal/final_resume_assembler.py` |
| Offline test stack | `tests/helpers/offline_lane_orchestration.py` |
| Global rollup | `apps_rg/runtime/internal/generated_lane_rollup.py` (`build_rollup`) |
| Package X3 | `apps_rg/runtime/internal/resume_package_disposition.py` |
| Child DOCX plan | `.cursor/plans/apps-rg-docx-output-removal-4650ff.md` |

---

DEFERRED_SCOPE: plan=apps-rg-resume-assembly-debt-burndown-56c022 id=w5-eval-facade-removal depends_on=apps_eval-migration title="Remove RgResumeOrchestrator facade after apps_eval migration" items="scenario_runner, taxonomy strings" rationale="Eval parity blocks hard delete" priority=P3
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
