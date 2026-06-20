---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-exit-gate-harness-wiring-e4b7f2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-exit-gate-harness-wiring-e4b7f2.md'
source_sha256: 2156753b488aad68d9278dd545d856f45c177bd5c08225f5f0f2286927524f75
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-exit-gate-harness-wiring-e4b7f2
plan_type: infra
---

# apps_rg Exit Gate Harness Wiring

Wire `build_apps_rg_exit_harness()` into the live dispatch path so G21–G28 gates run on every resume generation and a blank/malformed executive summary hard-fails.

---

## Context (SCQA)

- **Situation** — The `ExitGateHarness`, G21–G28 evaluators, exit profile, and `build_apps_rg_exit_harness()` factory all exist and are correct. `apps_rg_dispatch.py` calls `exit_finalize_apps_rg(sealed, prompt)` at the Exit stage.
- **Complication** — `exit_finalize_apps_rg()` writes artifacts and returns `X3Disposition` directly, **never calling** `build_apps_rg_exit_harness()` or `evaluate_gate_mesh()`. The gate mesh is dead code on the hot path. Additionally, G21's `required_sections` list in the exit profile does not include `executive_summary_block`, so a blank exec summary would not be caught even after wiring.
- **Question** — How do we make the gate mesh run on every exit so a blank executive summary hard-fails?
- **Answer** — (1) Build a `SealedWorkflowPackage` from `SealedL2Artifact` inside `exit_finalize_apps_rg()`, (2) invoke the harness to evaluate G21–G28, (3) block `X3Disposition(exit_status="success")` if any hard_fail fires, (4) add `executive_summary_block` to G21 `required_sections`, and (5) populate G21 section presence from the parsed JSON artifact.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `agentic_core/runtime/exit/apps_rg_exit_binding.py:148-299` | `exit_finalize_apps_rg` — the target function | ✅ Read |
| `agentic_core/runtime/entry/apps_rg_dispatch.py:454-477` | Dispatch Exit block — shows call site | ✅ Read |
| `agentic_core/runtime/exit/apps_rg_exit_binding.py:310-329` | `build_apps_rg_exit_harness()` — factory to call | ✅ Read |
| `agentic_core/runtime/exit/exit_gate_harness.py:80-188` | `ExitGateHarness.evaluate()` signature | ✅ Read |
| `agentic_core/runtime/gates/gate_evaluators.py:104-165` | G21 `evaluate_g21` — checks `pkg.sealed_sections[].node_id` | ✅ Read |
| `apps_rg/config/domain_contract/exit_profile.resume_generation.v1.json:31-52` | G21 `required_sections` — missing `executive_summary_block` | ✅ Read |
| `agentic_core/runtime/contracts/sealed_workflow_types.py:107-165` | `SealedWorkflowPackage` fields | ✅ Read |

---

## Wave Structure

| Wave | Scope | Status |
|------|-------|--------|
| W1 | Wire harness: build `SealedWorkflowPackage` from `SealedL2Artifact`, invoke harness, gate on result in `exit_finalize_apps_rg` | 🔲 TODO |
| W2 | Config: add `executive_summary_block` to G21 `required_sections`; populate section presence from parsed JSON content | 🔲 TODO |
| W3 | Tests + live retest: unit tests for gate firing; run live invocation and verify gate blocks on blank exec summary | 🔲 TODO |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Status |
|---|---|---|---|---|
| W1.P1 | `SealedWorkflowPackage` builder from `SealedL2Artifact` | `apps_rg_exit_binding.py` | Must populate `sealed_sections` with `node_id` values from parsed JSON keys | 🔲 TODO |
| W1.P2 | Harness invocation + X3 gate logic | `apps_rg_exit_binding.py` | Must not break `eval_score` / `hitl_required` fields already in `X3Disposition` | 🔲 TODO |
| W2.P1 | Add `executive_summary_block` to G21 required_sections in exit profile | `exit_profile.resume_generation.v1.json` | Must also add `executive_summary` field mapping into G21 section-presence logic | 🔲 TODO |
| W2.P2 | Populate `pkg.sealed_sections` with JSON-key presence | `apps_rg_exit_binding.py` | JSON key `executive_summary` → node_id `executive_summary_block` | 🔲 TODO |
| W3.P1 | Unit tests: gate fires on missing exec summary, passes when present | `tests/_apps_contract/` | Need fixture `SealedL2Artifact` with blank exec summary | 🔲 TODO |
| W3.P2 | Live retest against Brown & Brown run | live invocation | Verify `exit_status` reflects gate verdict | 🔲 TODO |

---

## Definition of Done

| ID | Criterion | Verification |
|---|---|---|
| DoD-1 | `exit_finalize_apps_rg` calls `build_apps_rg_exit_harness().evaluate(...)` before writing artifact | Code review + grep |
| DoD-2 | `exit_profile.resume_generation.v1.json` G21 `required_sections` includes `executive_summary_block` | File diff |
| DoD-3 | A `SealedL2Artifact` whose `generated_content` JSON lacks `executive_summary` causes `exit_status="failure"` | Unit test |
| DoD-4 | A `SealedL2Artifact` with valid `executive_summary` produces `exit_status="success"` | Unit test + live run |
| DoD-5 | `python -m apps_rg --dry-run ...` exits 0 after changes | Smoke run |

### Verification-vs-Deferral

| Item | Verified in plan | Deferred |
|---|---|---|
| G22 rubric score integration (requires actual LLM judge scores) | ❌ | Deferred — G22 passes as UNKNOWN→WARN for now (no judge scores in evidence) |
| G26 no_fabrication score integration | ❌ | Deferred — no_fabrication evidence not plumbed yet |
| Multi-candidate ensemble flow | ❌ | Deferred — single-candidate path only |
