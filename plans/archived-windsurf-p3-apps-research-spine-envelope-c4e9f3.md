---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\p3-apps-research-spine-envelope-c4e9f3.md'
original_relative_path: 'p3-apps-research-spine-envelope-c4e9f3.md'
source_sha256: b0634062bb8201eb32a35be0d73d54bb692c7fe2fbd8df8c6ed73a039937fc0a
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-07'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# P3 — Add Spine Envelope Inside apps_research

> Parent: deferred-scope-spine-refinement-5e3d1b
> Scope: Wrap apps_research product mode in governed_run spine envelope

## Context

`apps_research` product mode (default) calls `_run_canonical()` which resolves
the capability and delegates to the handler. This path has NO spine envelope —
no U0 intake, no L0 routing, no L2 receipt, no Exit eval, no L7 HowTrace.

The cert mode (`--apps-e2e-live`) already uses `governed_run` with full spine
emission but is a no-op dry run. The `research_l3_adapter.py` (W5) wraps
apps_research from the outside for apps_rg's L3 orchestration.

## Change

Same pattern as P2 (apps_qna): extract shared `_build_emission_config()`,
add `_run_product_research()` wrapping real execution in `governed_run`,
refactor cert mode to use shared config, update `main()`.

## Files

- `apps_research/__main__.py`

## Acceptance

- `python -m apps_research --topic "Brown & Brown"` produces full spine
  receipts under `artifacts/apps_research/runs/<ts>/`
- Receipts include: u0_intake_envelope, l1_plan_contract, route_contract,
  l2_execution_receipt, exit_review_packet, runtime_exhaust_bundle,
  agentic_core_how_trace
- Cert mode unaffected
