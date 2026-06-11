---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\p2-apps-qna-product-spine-b3e8d2.md'
original_relative_path: 'p2-apps-qna-product-spine-b3e8d2.md'
source_sha256: d18ec777851d511617eab154c6e5779f1350dcae6a5a2bbaa6b6abfce3750c86
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-07'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# P2 — Wire apps_qna Product Mode (build) into Spine

> Parent: deferred-scope-spine-refinement-5e3d1b
> Scope: Wrap apps_qna build subcommand in governed_run spine envelope

## Context

`apps_qna` product mode (`build` subcommand) currently calls
`build_pack_via_spine()` which emits only a `ValidatedRequest` envelope.
No L0 route check, no L2 execution receipt, no Exit eval, no L6 exhaust,
no L7 HowTrace.

The cert mode (`--apps-e2e-live`) already uses `governed_run` with full
spine emission but is a no-op dry run. The live interview mode
(`--interview`) is partially wired.

## Change

Modify `apps_qna/__main__.py` to detect the `build` subcommand and wrap
it in `governed_run` with real CardPackBuilder execution. The existing
`EmissionConfig` from cert mode is reused with `expects_prompt_assembly=True`
and real L2 execution replacing the no-op.

Other subcommands (lint, route, init, feedback, self-eval) remain
unchanged — they are auxiliary tools, not the core product path.

## Files

- `apps_qna/__main__.py` — add `_run_product_build()` function, modify `main()`

## Acceptance

- `python -m apps_qna build --interview <slug> --company <name> ...` produces
  full spine receipts under `artifacts/apps_qna/runs/<ts>/`
- Receipts include: u0_intake_envelope, l1_plan_contract, route_contract,
  l2_execution_receipt, exit_review_packet, runtime_exhaust_bundle,
  agentic_core_how_trace
- Other subcommands unaffected
