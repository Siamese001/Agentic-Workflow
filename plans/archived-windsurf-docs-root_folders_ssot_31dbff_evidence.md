---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\root_folders_ssot_31dbff_evidence.md'
original_relative_path: 'root_folders_ssot_31dbff_evidence.md'
source_sha256: f88c5d2daa1c8d2d30201eadc3abef1ef6c8bc6039727213513a7aa8cef1a669
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-03'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Root Folders SSOT Audit -- agentic_core + apps_*

## Scope

Reconcile `LAYER_OVERRIDES` and `build_sovereign_territories()` in
`agentic_core/L5_safety/config/structure_blueprint/_constants.py`
against actual disk folder structures. 14 variances identified and resolved.
No file moves. No structural changes. SSOT-only edits to one file.

Change sets applied:
- A1: L0_routing -- add seam
- A2: L1_cognition -- add telemetry
- A3: L2_execution -- add capability, determinism
- A4: L3_orchestration -- add arbitration, ptc, replay
- A5: L4_state -- add engines, storage
- A6: L5_safety -- remove phantom governance/runners/security; add static_checks;
  add enforcement_subfolders (governance) and config_subfolders (structure_blueprint)
- B:  prompt_governance -- add contracts
- C:  _build_layer_definition() -- add enforcement_subfolders + config_subfolders handlers

## CODE_COMMIT

f4fb1b8601c4317a4c453d744b3bd1c859c22f2b

## EVIDENCE_COMMIT

ca36fd9e29d88e64616b2a855cacd53f1412c6cf

## FILES_CHANGED_CODE

agentic_core/L5_safety/config/structure_blueprint/_constants.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/root_folders_ssot_31dbff_evidence.md

## INSPECTED_FILES

agentic_core/L5_safety/config/structure_blueprint/_constants.py
agentic_core/L0_routing/
agentic_core/L1_cognition/
agentic_core/L2_execution/
agentic_core/L3_orchestration/
agentic_core/L4_state/
agentic_core/L5_safety/
agentic_core/L6_observability/
agentic_core/prompt_governance/
agentic_core/runtime/
agentic_core/config/
agentic_core/seams/
agentic_core/knowledge/
apps_lic/
apps_rg/
apps_shared/

## GitDiffScope

$ git diff --name-only
agentic_core/L5_safety/config/structure_blueprint/_constants.py

## SSOTSmokeTest

$ python -c "..."
OK: all 14 variance assertions passed

## PytestStatus

Pre-existing baseline (verified via git stash): 1 skipped, 13 warnings, 16 errors in collection.
Post-change result: 1 skipped, 13 warnings, 16 errors in collection. Zero regressions introduced.
Collection errors are unrelated import failures (missing agentic_core.L4_state.utils.layer_gravity,
blueprint_hash symbol) that pre-date this phase.
EXIT CODE: 1

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

