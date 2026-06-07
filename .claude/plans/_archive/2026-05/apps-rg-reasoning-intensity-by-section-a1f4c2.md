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
