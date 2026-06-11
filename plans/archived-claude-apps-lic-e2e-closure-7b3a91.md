---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\apps-lic-e2e-closure-7b3a91.md'
original_relative_path: 'apps-lic-e2e-closure-7b3a91.md'
source_sha256: c3a890960be71753a3f6c951ec4c3a970fca64d243716aeb5246847644c1b6ab
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic E2E Closure

PLAN_CREATED: slug=apps-lic-e2e-closure-7b3a91 path=.claude/plans/apps-lic-e2e-closure-7b3a91.md status=Completed

Status: Completed 2026-06-10  
Created: 2026-06-10  
Worktree: `C:\Git\apps_lic`  
Branch: `apps_lic`

## Objective

Make the apps_lic E2E posture coherent after W5: keep the main live 12-row W5 gate green, close stale local E2E failures, and make secondary live-soak tests bounded so provider latency produces explicit fail-closed evidence instead of hanging.

## Current Evidence

Green:

- Main W5 repair-loop and 12-row gate local suite passes with `34 passed, 4 warnings`.
- Latest full live 12-row gate evidence passes at `artifacts/apps_lic/live_e2e_codex_20260610/w5_main_full_e2e_12_archetype_matrix_retry20` with `acceptance_passed=true` and `quality_violation_count=0`.
- The 12-row gate contract tests pass.
- W8 AIG 30-profile fixture E2E tests pass.

Red / unstable:

- `tests/apps_lic/test_w6_e2e.py` still expects retired core API aliases: `get_gateway`, `get_fabric`, and `WriteClassSeverity`.
- `tests/apps_lic/test_w6_e2e.py` still expects older FEC producer names and grounded flags.
- `tests/apps_lic/test_aig_target_category_e2e.py` expects `l2_execution_status == "completed"` even when the current canonical spine correctly returns `completed_with_gate_halt`.
- `tests/apps_lic/test_post_w7_live_15_contact_company_validation.py` can block on live Qwen/vLLM provider I/O during ordinary pytest.

## Scope

In scope:

- Update apps_lic callers/tests to current core API names where the production contract changed.
- Add narrow core compatibility only if a core-internal module still imports a removed core symbol.
- Update E2E assertions to accept current canonical terminal states without weakening no-send, no-L4-write, proof-bundle, X2, or W5/X1D rules.
- Add bounded test-mode behavior to the 15-contact live soak tests so provider hangs do not masquerade as product failures.

Out of scope:

- Changing the main W5 4-per-company / 12-row live gate contract.
- Treating the 15-row company soak as the main gate.
- Weakening X1D, X2, no-send/no-L4-write, proof-bundle, or unsupported-claim contracts.
- Increasing W5 repair attempts beyond the hard cap of 2.
- Reworking provider architecture or live Qwen/vLLM deployment.

## Implementation Plan

1. Close W6 alias drift.
   - Replace apps_lic imports of `get_gateway` with `get_default_gateway`.
   - Replace apps_lic imports of `get_fabric` with `get_coordination_fabric`.
   - Repair core-internal `touch_state_writer` import of retired `WriteClassSeverity` while preserving its durable write-class semantics.

2. Close stale FEC producer assertions.
   - Align W6 E2E expectations with the current `apps_lic.cert.fec_producer` payload contract.
   - Keep coverage for retrieval-source presence, schema version, route/template IDs, and evidence sufficiency.

3. Close target-category terminal-state drift.
   - Treat `completed_with_gate_halt` as a valid no-send/no-L4-write terminal state when validation intentionally blocks exposure.
   - Preserve manifest and generated-draft assertions where an L2 artifact is present.

4. Bound secondary 15-contact soak tests.
   - Mark the expensive live runner tests as live-only or require an explicit environment opt-in.
   - Keep structural tests always-on so the 15-row source shape remains covered.
   - Add a fast summary-contract/unit test for the 15-row aggregate contract where possible.

5. Verify.
   - Run W5/main-gate suite.
   - Run W6 E2E, W8 AIG 30-profile E2E, target-category E2E, and post-W7 live gate contract tests.
   - Update this plan with final pass/fail evidence.

## Acceptance Criteria

- `tests/apps_lic/test_x1d_repair_loop_w0_fixtures.py`, `tests/apps_lic/test_x1d_judge_feedback_regeneration.py`, `tests/apps_lic/test_w5_validation_exit_canonical_wireup.py`, and `tests/apps_lic/test_post_w7_live_12_archetype_matrix.py` pass.
- `tests/apps_lic/test_w6_e2e.py`, `tests/apps_lic/test_w8_aig_30_profile_e2e.py`, `tests/apps_lic/test_aig_target_category_e2e.py`, and the non-live/default post-W7 gate tests pass.
- Live 15-row soak is either explicitly opt-in or bounded with clear fail-closed evidence; default pytest must not hang on provider I/O.

## Completion Evidence - 2026-06-10

Implemented:

- Closed W6 stale core API drift by replacing app-side `get_gateway` / `get_fabric` imports with `get_default_gateway` / `get_coordination_fabric`.
- Added a narrow core `WriteClassSeverity` compatibility enum for the core-internal touch-state writer, preserving the existing `durable` app-domain registration value.
- Aligned W6 FEC E2E assertions to the current `apps_lic.cert.fec_producer` v1.1 payload contract.
- Aligned target-category E2E assertions with the current canonical terminal state and retry-budget contract.
- Made the expensive 15-contact live provider soak explicit opt-in via `APPS_LIC_RUN_LIVE_15_SOAK=1`, while keeping source-shape and secondary summary-contract tests always-on.

Verification:

- Compile check passed for all touched Python files.
- Targeted E2E batch passed: `36 passed, 2 skipped, 4 warnings`.
  - Skips are only the explicit live 15-contact provider soak tests when `APPS_LIC_RUN_LIVE_15_SOAK` is not set.
- W5/main-gate suite still passed: `34 passed, 4 warnings`.

Remaining live-only action:

- To re-run the secondary live 15-contact soak, set `APPS_LIC_RUN_LIVE_15_SOAK=1` and run `tests/apps_lic/test_post_w7_live_15_contact_company_validation.py` or the script directly with the desired `--env-file`.
