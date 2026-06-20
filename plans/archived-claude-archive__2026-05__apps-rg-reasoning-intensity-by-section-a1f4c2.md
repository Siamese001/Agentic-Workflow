---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-reasoning-intensity-by-section-a1f4c2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-reasoning-intensity-by-section-a1f4c2.md'
source_sha256: 9ac2354f47b5312d48752197646db2cb706ca20f1a19dc5fa7d0eae8a01d2188
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
title: apps_rg reasoning intensity by section
created: "2026-05-16"
wave: follow-up-narrow scope
artifacts:
  audit: docs/reports/apps_rg_reasoning_intensity_audit.md
---

# Plan: Tiered reasoning intensity (`apps_rg`)

## Goal

Tune **temperature / self-consistency / ToT knobs / reflexion** per **lane** (`_reasoning_section_lane`), keep **generic `agentic_core`** free of app literals, attach **truthful `ReasoningExecutionReceipt`**, cap **X1D** for **executive_summary** when proof/cert is missing.

## Execution chunks (narrow)

1. **Declarative lane map:** `apps_rg/runtime/reasoning/section_reasoning_intensity.py` — `_EXEC_SUMMARY_PROFILE` matches or exceeds lesser tiers (`executive_summary_must_dominate_lesser_sections`).
2. **HTTP shim:** `section_qwen_slice.call_qwen_vllm` — strip orch/meta; forbid scratchpad on transport; build plan via `apps_rg_http_reasoning_plan`; resolver receipt on `ProviderResult`.
3. **Dispatch wiring:** section dispatches use `tag_reasoning_lane`; **critical lanes** attach `reasoning_section_lane` + `reasoning_execution_receipt` snapshot to `prompt_selection_trace.json` via `prompt_trace_reasoning.attach_reasoning_to_prompt_trace`.
4. **X1D:** `x1_gates._apply_reasoning_quality_certification_cap` — exec lane uses `REASONING_EXECUTIVE_SUMMARY_*` codes when receipt missing/denied.
5. **Verification:** pytest targets (`test_reasoning_execution_control_plane`, `test_x1_gates`, `test_reasoning_intensity_profiles`).
6. **Accounting:** OVERALL stays **PARTIAL** until full `tests/unit/apps_rg` green, IBM/education/cert trace parity optional, **T3 runner** or documented consumer handling of reflex `aggregate_blocked`, **T1** lane binds.

## Out of scope (explicit)

Multi-call branch/reflex runners, new registries inside `agentic_core`, weakening locked copy, synthetic certification.

## Acceptance

Audit matrix on disk (`docs/reports/apps_rg_reasoning_intensity_audit.md`), regression asserts exec > T0/T2 on knobs, singleton receipts never claim APPLIED for unexecuted orch.

**Overall plan status:** **PARTIAL** (see audit status table — not global unconditional PASS).
