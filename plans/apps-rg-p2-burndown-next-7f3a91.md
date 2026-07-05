# apps_rg P2 Burndown Next Wave

## Status

- Branch: `codex-apps-rg-p2-burndown-next-plan`
- Plan status: draft, plan-only branch from local `main`
- Scope: continue ADG/BCG P2 MEDIUM hygiene burndown after PR #499, without duplicating work already published there

## Source Contract

- Validator command run before plan creation:
  - `python tools/adg/consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json`
- Validator result:
  - `ok=true`
  - `artifact_status=repair_ready`
  - `adg_run_id=07042026_2305`
  - `dependency_status=ready`
- Handoff pointer:
  - `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json`
- Immutable handoff:
  - `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_07042026_2305.json`
  - `handoff_sha256=6f33568575605193aa75dfecdc079079424367e00cf27dd730a9f2c3fa79fb37`
- Receipt:
  - `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_audit_pipeline_receipt_07042026_2305.json`
  - `receipt_sha256=32f823784e46f916527a63830483c8a2412afb6db8cae5e5cebc11fe0e56b376`
- Released timestamp window:
  - `started_at_utc=2026-07-05T03:05:06Z`
  - `completed_at_utc=2026-07-05T03:18:03Z`

## Artifact Inputs

Use the immutable handoff artifacts as source of truth, not checked-in `latest` mirrors when they drift.

- Snapshot:
  - `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-adg-audit-and-burndown\artifacts\adg\adg_indexed_07042026_2305.sqlite`
  - `sha256=88e2d437eec11417da46b2d212202f82004c56d5c223e9d97616a4df7f33e78c`
- Action queue:
  - `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-adg-audit-and-burndown\artifacts\adg\adg_action_queue_07042026_2305.json`
  - `sha256=c2af6a137edd5d85c4af499412c8cbc5bcb84a743af871f75802a61785897357`
- Burndown report:
  - `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-adg-audit-and-burndown\artifacts\adg\adg_burndown_report_07042026_2305.md`
  - `sha256=0489c066582c1730a35f34da8572cc435e7a5dd4bfdf9f432d32a56d09d98057`
- Burndown table:
  - `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-adg-audit-and-burndown\artifacts\adg\adg_burndown_table_07042026_2305.json`
  - `sha256=fcb6eea505f85f7d995d67bcce980db79fd45040d9ae20628c19e374b18eae1f`
- Gate results:
  - `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-adg-audit-and-burndown\artifacts\adg\adg_gate_results_20260705_031510.json`
  - `sha256=8298c586bab66bb15e3c0f01ad78c9b445f4b5e608523046dfc30726069767a5`

Checked-in mirror drift observed on this branch:

- `artifacts/adg/adg_cleanup_queue_and_p2_blocker_trace_latest.*` currently reflects `07042026_1748`.
- The validator-resolved immutable handoff reflects `07042026_2305`.
- Implementation must re-run the handoff validator and use the immutable `07042026_2305` handoff artifacts before source edits.

## Current P2 State

- Current MEDIUM hygiene count: `31`
- Ceiling in released 07042026_2305 trace: `0` in the P2 trace summary, while the burndown table reports `P2_anti_patterns_medium=31`.
- Practical automation target uses released current count:
  - `target_rows = max(5, ceil(31 * 0.25)) = 8`
- P2 evidence buckets:
  - `OSError`: 12
  - `Exception`: 12
  - `ValueError`: 3
  - `getattr`: 1
  - `NotADirectoryError`: 1
  - `ImportError`: 1
  - `TypeError`: 1
- P2 by-kind summary from burndown table:
  - `return_none_swallow`: 16 net
  - `log_and_swallow`: 5 net
  - `silent_exception_swallow`: 4 net
  - `default_fallback_masking`: 3 net
  - `broad_exception_catch`: 2 net
  - `hallucinated_tool_name`: 1 net

## Prior P2 Work To Avoid Duplicating

PR #499 (`codex-apps-rg-p2-behavior`) already targets the first three released hotspots:

- `apps_rg/runtime/c0/fact_vector_write_back.py`: 6 rows
- `apps_rg/runtime/bindings/u0_package_ingest.py`: 4 rows
- `apps_rg/runtime/observability/trace_reconciliation.py`: 2 rows

Next implementation should either:

- Start after PR #499 lands on `main`, then select the next rows below; or
- Rebase this branch on PR #499 if urgent parallel work is required; or
- If PR #499 is abandoned, explicitly switch this plan back to the first-three-hotspot plan and revalidate from the handoff.

Do not edit the PR #499 files again on this branch until one of those conditions is true.

## Next Target Rows

The next bounded wave should aim for at least 8 non-overlapping rows from the released file hotspot order, prioritizing live runtime/core surfaces over apps-only diagnostics.

Primary next wave:

| Planned Rows | File | Surface | Reason |
|---:|---|---|---|
| 2 | `apps_rg/runtime/section_graph_skills_proof_pool.py` | live runtime | Highest remaining non-PR #499 live runtime hotspot |
| 1 | `apps_rg/runtime/assembly/full_resume_text.py` | live runtime | One-row live runtime hygiene candidate |
| 1 | `apps_rg/runtime/c0/c02_semantic_cache_payload.py` | live runtime | One-row live runtime hygiene candidate |
| 1 | `apps_rg/runtime/fact_vectors_bootstrap.py` | live runtime | One-row live runtime hygiene candidate |
| 1 | `apps_rg/runtime/judges/executive_summary_x1d.py` | live runtime | One-row live runtime hygiene candidate |
| 1 | `apps_rg/runtime/mandatory_run_outputs.py` | live runtime | One-row live runtime hygiene candidate |
| 1 | `apps_rg/runtime/orchestration/patch_run.py` | live runtime | One-row live runtime hygiene candidate |

Planned rows: `8`

Reserve candidates if any primary row is unsafe:

- `apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py`
- `apps_rg/runtime/orchestration/section_lane_executor.py`
- `apps_rg/runtime/providers/provider_attempt_spans.py`
- `apps_rg/runtime/reasoning/bullet_fact_entailment.py`
- `apps_rg/runtime/section_model_limits.py`
- `apps_rg/runtime/sections/upstream_evidence_block.py`
- `apps_rg/runtime/shadow/l6_microstep_observability.py`
- `apps_rg/cache/whole_run_entrypoint_preflight.py`
- `apps_eval/coverage/apps_rg.py`
- `apps_eval/diagnostics/apps_rg.py`

## Execution Waves

Wave 0: pre-edit gates

- Confirm branch is rebased on a main that includes PR #499, or explicitly merge/rebase PR #499 into the working branch.
- Re-run the exact handoff validator.
- Confirm current target files are clean in the worktree.
- Query the target files for broad/silent/return-None patterns and map each row to a mechanical edit.
- Stop if rows require architecture/product behavior choices.

Wave 1: 2-row live runtime hotspot

- Inspect `apps_rg/runtime/section_graph_skills_proof_pool.py`.
- Expected safe edit class: narrow exception handling, convert silent returns into explicit typed status, or remove provably unused fallback.
- Add or update focused tests if behavior becomes observable.
- Run targeted tests for the file.

Wave 2: first four one-row runtime candidates

- Inspect and edit:
  - `apps_rg/runtime/assembly/full_resume_text.py`
  - `apps_rg/runtime/c0/c02_semantic_cache_payload.py`
  - `apps_rg/runtime/fact_vectors_bootstrap.py`
  - `apps_rg/runtime/judges/executive_summary_x1d.py`
- Keep each edit independent and mechanical.
- Run targeted tests/import checks after each file or pair.

Wave 3: final two one-row runtime candidates

- Inspect and edit:
  - `apps_rg/runtime/mandatory_run_outputs.py`
  - `apps_rg/runtime/orchestration/patch_run.py`
- Substitute reserve candidates if these rows are already cleared by another branch or unsafe.

Wave 4: validation and publication

- Run targeted tests for every touched file.
- Run a lightweight static check:
  - `python -m compileall <touched source files>`
- Re-run:
  - `python tools/adg/consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json`
- If practical after PR #499 lands, run a lightweight P2 evidence regeneration or targeted ADG report command. If full ADG is too expensive, record why it was deferred.
- Commit, push, open PR, and do not merge unless local closeout is clean and GitHub checks are complete.

## Validation Commands

Baseline commands:

- `python tools/adg/consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json`
- `python -m compileall apps_rg/runtime/section_graph_skills_proof_pool.py apps_rg/runtime/assembly/full_resume_text.py apps_rg/runtime/c0/c02_semantic_cache_payload.py apps_rg/runtime/fact_vectors_bootstrap.py apps_rg/runtime/judges/executive_summary_x1d.py apps_rg/runtime/mandatory_run_outputs.py apps_rg/runtime/orchestration/patch_run.py`

Targeted tests to discover/confirm during implementation:

- Use `rg` to find existing tests for each target file.
- If no focused tests exist, add small characterization tests for the changed behavior rather than relying on broad integration only.
- Run the closest apps_rg unit or contract test slice after each wave.

## Skip Criteria

Skip a candidate if:

- It needs product behavior judgment.
- It changes public contracts without existing tests.
- It touches generated artifacts or archived bundles.
- It overlaps PR #499 before PR #499 has landed or been merged into the branch.
- It creates broad cross-layer coupling.
- It requires rebaselining instead of reducing real debt.
- Targeted tests fail twice for reasons unrelated to the mechanical edit.

## Stop Conditions

Stop and report RCA if:

- Handoff validator fails, is stale, or resolves to a different run without updated artifacts.
- P0/P1 precedence gates regress.
- Working tree has unrelated dirty changes.
- Source evidence cannot map a P2 row to a safe mechanical change.
- `cleared_rows < target_rows` and all remaining candidates are unsafe.

## Publication Notes

- This branch currently contains only the plan.
- Source implementation should start from a branch that includes PR #499 or from main after PR #499 lands.
- If implementation proceeds on this branch, update this plan with actual selected rows and validation results before opening the implementation PR.
