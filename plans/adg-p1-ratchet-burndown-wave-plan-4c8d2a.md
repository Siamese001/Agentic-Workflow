# ADG P1 Ratchet Burndown Wave Plan

Plan ID: adg-p1-ratchet-burndown-wave-plan-4c8d2a
Automation ID: adg-p1-ratchet-burndown
Generated: 2026-07-08T10:04:00-04:00
Worktree: C:\Git\Agentic-Workflow-FRESH-worktrees\codex-adg-p1-ratchet-burndown
Branch: codex/adg-p1-ratchet-burndown-20260708T094956
Status: corrective plan generated after the run identified the missing full-scope P1 wave plan

Follow-on branch: codex/adg-p1-ratchet-burndown-20260708T161101
Follow-on branch: codex/adg-p1-ratchet-burndown-20260708T162958
Follow-on branch: codex/adg-p1-ratchet-burndown-20260708T163522

## Scope

This plan is the concrete P1 execution and burndown plan required by the automation TOML. It is grounded in the validated producer-root ADG handoff for run `07072026_2307` and covers the whole current P1 scope:

- Ordinary P1 high anti-pattern rows first.
- P1 ratchet floor backlog only after ordinary P1 is clear.
- P1=0 is the only success condition.
- P2/P3 remain blocked until a fresh validated handoff proves P1=0.

The earlier run patch cleared only the ordinary P1 source rows. That was incomplete as an automation deliverable because the TOML also requires this wave-based ratchet plan for all P1 scope.

## Source Artifacts

All source artifacts are from the producer root, not from a same-named worktree pointer:

- Handoff pointer: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json`
- Immutable handoff: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_07072026_2307.json`
- SQLite snapshot: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_07072026_2307.sqlite`
- Gate results: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_gate_results_20260708_032528.json`
- Action queue: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_action_queue_07072026_2307.json`
- Burndown table: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_burndown_table_07072026_2307.json`
- Burndown report: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_burndown_report_07072026_2307.md`

Startup validator:

`python tools/adg/consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json`

Accepted result:

- `dependency_status=ready`
- `artifact_status=repair_ready`
- `adg_run_id=07072026_2307`
- `P0_FIX=0`
- `P0_WAVE=0`
- `P1_FIX=0`
- `P1_RATCHET_REGRESSION=0`
- `P1_RATCHET_FLOOR_BACKLOG=7`

## Current P1 Baseline

| Category | Count | Target |
|---|---:|---:|
| Ordinary P1 high anti-pattern rows | 3 | 3 |
| P1 ratchet floor backlog rows | 3646 | 3646 |
| Total P1 rows in scope | 3649 | 3649 |

`ordinary_p1_target = 3`

`current_p1_ratchet_backlog_count = 3646`

`target_rows = ordinary_p1_target + current_p1_ratchet_backlog_count = 3649`

`target_status = met` only when a regenerated or replayed digest-bound ADG proof reports zero ordinary P1 rows and zero P1 ratchet backlog rows.

## Ordinary P1 Wave

| Wave | Rows | Files | Repair class | Status | Validation |
|---|---:|---|---|---|---|
| O1 | 3 | `agentic_core/L2_execution/l2_package_driven_executor.py`; `agentic_core/L3_orchestration/exit_eval/judges/_base_http_judge.py`; `tests/unit/agentic_core/L2_execution/test_l2_package_driven_repair.py` | Replace silent or `None` swallows with explicit guarded fallback/error behavior. | Attempted in branch | `compileall` passed; focused pytest passed 6/6 |

Ordinary P1 row evidence:

- `anti_pattern_findings.id=754`: `silent_exception_swallow`, `agentic_core/L2_execution/l2_package_driven_executor.py`, line 246, symbol `ImportError`
- `anti_pattern_findings.id=755`: `silent_exception_swallow`, `agentic_core/L2_execution/l2_package_driven_executor.py`, line 273, symbol `TypeError`
- `anti_pattern_findings.id=938`: `return_none_swallow`, `agentic_core/L3_orchestration/exit_eval/judges/_base_http_judge.py`, line 95, symbol `ValueError`

Validation commands already run for O1:

- `python -m compileall -q agentic_core\L2_execution\l2_package_driven_executor.py agentic_core\L3_orchestration\exit_eval\judges\_base_http_judge.py tests\unit\agentic_core\L2_execution\test_l2_package_driven_repair.py tests\unit\agentic_core\L3_orchestration\exit_eval\test_http_judges.py`
- `python -m pytest tests\unit\agentic_core\L2_execution\test_l2_package_driven_repair.py tests\unit\agentic_core\L3_orchestration\exit_eval\test_http_judges.py -q`

## Ratchet Priority Order

Priority follows the digest-bound P1 ratchet floor backlog and selects broadest/highest-impact families first while preserving dependency safety.

For each selected gate/family:

`ratchet_target_per_wave = max(25 rows, ceil(selected_gate_rows * 0.05))`

The automation must continue selecting safe rows until the final count is zero. The per-wave floor is a minimum progress floor, not the final target.

| Priority | Gate/family | Current rows | Per-wave floor | Estimated waves to zero | Dependency grouping | Primary repair shape |
|---:|---|---:|---:|---:|---|---|
| 1 | `E1_trace_stub_module` | 982 | 50 | 20 | Group by trace stub module family and import fanout. | Retire trace-only stubs, bind traces to concrete runtime owners, or consolidate into explicit observability helpers with tests. |
| 2 | `B2_layer_skip_ratchet` | 862 | 44 | 20 | Group by source layer and shared target contract. | Remove direct lower-to-higher imports through dependency inversion, lower-layer contracts, or orchestration-owned adapters. |
| 3 | `I1_exit_disposition_ratchet` | 695 | 35 | 20 | Group by execution entrypoint, command surface, and return path. | Add explicit exit dispositions, typed failure/success outcomes, and tests for each public execution path. |
| 4 | `M_taint_actionable_ratchet` | 688 | 35 | 20 | Group by actionable surface and schema owner. | Bind actionable outputs to structured schemas, receipts, or non-actionable classification. |
| 5 | `O_tool_call_parity_ratchet` | 206 | 25 | 9 | Group by tool/provider call path and receipt boundary. | Add tool-call parity receipts, provider identity, and traceable call/result linkage. |
| 6 | `C3_silent_writes_ratchet` | 125 | 25 | 5 | Group by write target and side-effect owner. | Add explicit side-effect emission or receipt coverage around writes; classify intentional silent writes only with evidence. |
| 7 | `N_guardrail_separation_ratchet` | 88 | 25 | 4 | Group by shared write target between guardrail and orchestration layers. | Split guardrail policy decisions from orchestration state writes through explicit facades or lower-layer contracts. |

Total planned ratchet waves: 98

Total planned waves including ordinary P1 and final proof: 100

## Wave Execution Plan

### W0 - Gate Intake

Objective: Revalidate the exact producer-root handoff before any ratchet edit wave.

Commands:

- `python tools/adg/consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json`
- Confirm `P0_FIX=0`, `P0_WAVE=0`, no digest-bound P0 FIX/WAVE rows, and no handoff/action-queue/burndown drift.

Stop conditions:

- Non-zero validator exit.
- `dependency_status=dependency_not_ready`.
- `artifact_status` not `certified` or `repair_ready`.
- P0 FIX/WAVE reappears.
- Timestamp or digest inconsistency.

### W1 - Ordinary P1 High Anti-Patterns

Objective: Clear the 3 ordinary P1 source rows before ratchet work.

Rows: 3

Status: already attempted in this branch.

Validation:

- `compileall` on touched files.
- Focused pytest for L2 repair and HTTP judge behavior.
- Lightweight anti-pattern query against touched files when regenerated SQLite evidence is available.

Stop conditions:

- Targeted tests fail twice with the same cause.
- Repair requires public contract change or migration receipt.
- A source row cannot be changed without broad ownership choice.

### W2 - E1 Trace Stub Module Burndown

Objective: Reduce `E1_trace_stub_module` from 982 to zero.

Rows: 982

Per-wave floor: 50

Estimated waves: 20

Wave 1 status: implemented in branch.

Wave 1 scope:

- Selected the top 50 E1 candidates from `adg_indexed_07072026_2307.sqlite` by trace import count, total imports, and path.
- Replaced direct lifecycle trace symbol imports with one `trace_contract` module alias import in each selected module.
- Preserved existing trace emissions by rewriting each local trace function reference to `trace_contract.<symbol>`.
- Expected E1 reduction on next ADG generation: 50 modules, pending regenerated ADG proof.

Wave 1 proof:

- Source replay: `artifacts/codex/runtime_proofs/e1_trace_import_wave1_source_replay.json` reports `passed=50`, `failed=0`.
- Runtime import proof: `artifacts/codex/runtime_proofs/e1_trace_import_wave1_runtime_importable_subset_proof.json` reports `passed=47`, `failed=0` for importable modules.
- Full import blocker capture: `artifacts/codex/runtime_proofs/e1_trace_import_wave1_runtime_proof.json` reports 3 import-time blockers unrelated to the trace import rewrite: one circular import in `filesystem_mcp.py` and two missing module imports in L4 state memory surfaces.
- Clean-base import blocker probe: `artifacts/codex/runtime_proofs/e1_trace_import_wave1_base_import_blocker_probe.json` reproduces the same 3 import-time blockers from base commit `f6489212c2fa25d5a0818a0c56b051008dd7e5dc`.
- Pinned legacy E1 gate against the consumed snapshot remains pass: `current=982 baseline=982`.
- Compile proof passed for all changed Python files.
- Focused pytest passed for ordinary P1 repairs: 6 collected, 6 passed.

Wave 2 status: implemented in branch.

Wave 2 scope:

- Selected the next 50 E1 candidates from `adg_indexed_07072026_2307.sqlite`, excluding wave-1 manifest candidates.
- Replaced direct lifecycle trace symbol imports with one `trace_contract` module alias import in each selected module.
- Preserved existing trace emissions by rewriting each local trace function reference to `trace_contract.<symbol>`.
- Repaired the inherited PR terminal-cleanup failure in `agentic_core/L2_execution/utils/safe_subprocess.py` by adding an explicit default timeout and placing the `Popen` lifecycle guardian on the call line expected by the gate.
- Expected cumulative E1 reduction on next ADG generation: 100 modules, pending regenerated ADG proof.

Wave 2 proof:

- ADG MCP health: `status=ok`, `adg_snapshot_id=07072026_2307`; detailed candidate extraction used the immutable SQLite snapshot because the exposed MCP tools do not include ad hoc SQL.
- Source replay: `artifacts/codex/runtime_proofs/e1_trace_import_wave2_source_replay.json` reports `passed=50`, `failed=0`.
- Runtime import proof: `artifacts/codex/runtime_proofs/e1_trace_import_wave2_runtime_importable_subset_proof.json` reports `passed=46`, `failed=0` for importable modules.
- Full import blocker capture: `artifacts/codex/runtime_proofs/e1_trace_import_wave2_runtime_proof.json` reports 4 import-time blockers unrelated to the trace import rewrite.
- Clean-HEAD import blocker probe: `artifacts/codex/runtime_proofs/e1_trace_import_wave2_head_import_blocker_probe.json` reproduces the same 4 import-time blockers from branch HEAD `191efe1550a99a0465022c0ffce322071609c2a7`.
- Pinned legacy E1 gate against the consumed snapshot remains pass: `current=982 baseline=982`.
- Compile proof passed for all wave-2 changed Python files.
- Terminal cleanup proof passed for changed files: `check_terminal_cleanup.py --verbose --fail-on-new-only --base-ref 2acff50883eb631c66d7b4d88c6c58ac0b6d000a`.
- Focused pytest passed for ordinary P1 repairs: 6 collected, 6 passed.

Wave 3 status: implemented in follow-on branch `codex/adg-p1-ratchet-burndown-20260708T161101`.

Wave 3 scope:

- Selected the next 50 E1 candidates from `adg_indexed_07072026_2307.sqlite`, excluding wave-1 and wave-2 manifest candidates.
- Replaced direct lifecycle trace symbol imports with one `trace_contract` module alias import in each selected module.
- Preserved existing trace emissions by rewriting each local trace function reference to `trace_contract.<symbol>`.
- Expected cumulative E1 reduction on next ADG generation: 150 modules, pending regenerated ADG proof.

Wave 3 proof:

- ADG MCP health: `status=ok`, `adg_snapshot_id=07072026_2307`; detailed candidate extraction used the immutable SQLite snapshot because the exposed MCP tools do not include ad hoc SQL.
- Source replay: `artifacts/codex/runtime_proofs/e1_trace_import_wave3_source_replay.json` reports `passed=50`, `failed=0`.
- Runtime import proof: `artifacts/codex/runtime_proofs/e1_trace_import_wave3_runtime_importable_subset_proof.json` reports `passed=48`, `failed=0` for importable modules.
- Full import blocker capture: `artifacts/codex/runtime_proofs/e1_trace_import_wave3_runtime_proof.json` reports 2 import-time blockers unrelated to the trace import rewrite.
- Base import blocker probe: `artifacts/codex/runtime_proofs/e1_trace_import_wave3_base_import_blocker_probe.json` reproduces the same 2 import-time blockers from local `main` before wave 3.
- Pinned legacy E1 gate against the consumed snapshot remains pass: `current=982 baseline=982`.
- Validation status is partial until the wave-3 branch finishes compile, static, pytest, receipt, PR, and publication checks.

Wave 4 status: implemented in follow-on branch `codex/adg-p1-ratchet-burndown-20260708T162958`.

Wave 4 scope:

- Selected the next 50 E1 candidates from `adg_indexed_07072026_2307.sqlite`, excluding wave-1, wave-2, and wave-3 manifest candidates.
- Replaced direct lifecycle trace symbol imports with one `trace_contract` module alias import in each selected module.
- Preserved existing trace emissions by rewriting each local trace function reference to `trace_contract.<symbol>`.
- Expected cumulative E1 reduction on next ADG generation: 200 modules, pending regenerated ADG proof.

Wave 4 proof:

- ADG MCP health: `status=ok`, `adg_snapshot_id=07072026_2307`; detailed candidate extraction used the immutable SQLite snapshot because the exposed MCP tools do not include ad hoc SQL.
- Source replay: `artifacts/codex/runtime_proofs/e1_trace_import_wave4_source_replay.json` reports `passed=50`, `failed=0`.
- Runtime import proof: `artifacts/codex/runtime_proofs/e1_trace_import_wave4_runtime_proof.json` reports `passed=50`, `failed=0` for the full selected manifest.
- Base import blocker probe: `artifacts/codex/runtime_proofs/e1_trace_import_wave4_base_import_blocker_probe.json` also reports `passed=50`, `failed=0`.
- Runtime importable subset proof: `artifacts/codex/runtime_proofs/e1_trace_import_wave4_runtime_importable_subset_proof.json` reports `passed=50`, `failed=0`.
- Pinned legacy E1 gate against the consumed snapshot remains pass: `current=982 baseline=982`.
- Validation, PR, and publication completed in PR #513; local `main` and `origin/main` contain commit `a4c6da0c738a5d139bb0fc851059892180e3ae7b` through merge commit `2b8fc50e88b8ef25341e2b122d64c2b4a133526f`.

Wave 5 status: implemented in follow-on branch `codex/adg-p1-ratchet-burndown-20260708T163522`.

Wave 5 scope:

- Selected the next 50 E1 candidates from `adg_indexed_07072026_2307.sqlite`, excluding wave-1, wave-2, wave-3, and wave-4 manifest candidates.
- Replaced direct lifecycle trace symbol imports with one `trace_contract` module alias import in each selected module.
- Preserved existing trace emissions by rewriting each local trace function reference to `trace_contract.<symbol>`.
- Expected cumulative E1 reduction on next ADG generation: 250 modules, pending regenerated ADG proof.

Wave 5 proof:

- ADG MCP health: `status=ok`, `adg_snapshot_id=07072026_2307`; detailed candidate extraction used the immutable SQLite snapshot because the exposed MCP tools do not include ad hoc SQL.
- Source replay: `artifacts/codex/runtime_proofs/e1_trace_import_wave5_source_replay.json` reports `passed=50`, `failed=0`.
- Full runtime import proof: `artifacts/codex/runtime_proofs/e1_trace_import_wave5_runtime_proof.json` reports `passed=47`, `failed=3`.
- Base import blocker probe: `artifacts/codex/runtime_proofs/e1_trace_import_wave5_base_import_blocker_probe.json` reproduces the same 3 import-time blockers from local `main` before wave 5.
- Runtime importable subset proof: `artifacts/codex/runtime_proofs/e1_trace_import_wave5_importable_subset_runtime_proof.json` reports `passed=47`, `failed=0`.
- Pinned legacy E1 gate against the consumed snapshot remains pass: `current=982 baseline=982`.
- Compileall passed for 50 changed Python files; focused ordinary-P1 pytest passed `6/6`; terminal cleanup and `git diff --check` passed.
- Local `verify_codex_primary.py` failed only on user-profile automation mirror drift at `C:\Users\amita\.codex\automations\adg-p1-ratchet-burndown\automation.toml`, outside this branch payload.

Selection policy:

- Select the highest-fanout trace stub family first.
- Keep each wave to one cohesive module family or one import-fanout cluster.
- Prefer deletion or consolidation of pure stubs when no runtime contract depends on them.
- Preserve behavior through tests or explicit compatibility wrappers only when consumers still require the surface.

Validation per wave:

- `python -m compileall -q <touched files>`
- Focused pytest for touched package or nearest existing tests.
- ADG query or lightweight gate replay for `E1_trace_stub_module` on touched paths.

Rollback/skip criteria:

- If a module is a public compatibility surface, skip it and record an owner/contract decision.
- If deletion expands scope outside one family, split the wave.
- Revert only the current wave patch with `apply_patch`; do not reset unrelated work.

### W3 - B2 Layer Skip Burndown

Objective: Reduce `B2_layer_skip_ratchet` from 862 to zero.

Rows: 862

Per-wave floor: 44

Estimated waves: 20

Selection policy:

- Start with direct L0/L1 imports into L6 or higher-layer observability/runtime modules.
- Group rows by target contract so one lower-layer interface can retire many skip edges.
- Prefer moving passive data contracts downward over importing higher-layer services downward.
- Do not create new compatibility shims that preserve the layer skip.

Validation per wave:

- `python -m compileall -q <touched files>`
- Focused pytest for routing/enforcement package plus any moved contract tests.
- ADG layer query or gate replay for touched source/target pairs.

Rollback/skip criteria:

- Stop if the fix requires public API migration, app package ownership choice, or broad cross-layer redesign beyond the selected cluster.
- Skip a cluster only when independent B2 clusters remain safe.

### W4 - I1 Exit Disposition Burndown

Objective: Reduce `I1_exit_disposition_ratchet` from 695 to zero.

Rows: 695

Per-wave floor: 35

Estimated waves: 20

Selection policy:

- Group by execution entrypoint and command boundary.
- Add explicit success/failure/blocked disposition values rather than implicit `None`, fallthrough, or logging-only completion.
- Test representative success and failure paths for each group.

Validation per wave:

- `python -m compileall -q <touched files>`
- Focused pytest for execution/orchestration/audit surfaces touched.
- Lightweight query for `no_exit_disposition` rows on touched paths.

Rollback/skip criteria:

- Stop if introducing a disposition changes external command output without an approved contract update.
- Skip generated or archival files only when the digest-bound gate supports exclusion or backlog tracking.

### W5 - M Taint Actionable Burndown

Objective: Reduce `M_taint_actionable_ratchet` from 688 to zero.

Rows: 688

Per-wave floor: 35

Estimated waves: 20

Selection policy:

- Group by actionable output surface and owning schema.
- Convert free-form action outputs into schema-bound objects, receipts, or explicitly non-actionable diagnostics.
- Start with governance and hook scripts where command boundaries are tight and validation is cheap.

Validation per wave:

- `python -m compileall -q <touched files>`
- Focused unit tests for schema validation and command output.
- Gate replay for actionable rows on touched files.

Rollback/skip criteria:

- Stop if schema ownership is unclear or output format is a public contract.
- Skip rows requiring product/design decision; continue with independent script-level rows.

### W6 - O Tool Call Parity Burndown

Objective: Reduce `O_tool_call_parity_ratchet` from 206 to zero.

Rows: 206

Per-wave floor: 25

Estimated waves: 9

Selection policy:

- Group by tool/provider call path.
- Add receipt parity where a tool call has observable side effects or external dependency.
- Record provider identity, request intent, result status, and failure class without leaking secrets.

Validation per wave:

- `python -m compileall -q <touched files>`
- Focused pytest or dry-run command for touched tool wrappers.
- Receipt shape validation where available.

Rollback/skip criteria:

- Stop if receipt content could expose credentials or user data without a redaction contract.
- Skip wrappers whose provider contract is not locally available.

### W7 - C3 Silent Writes Burndown

Objective: Reduce `C3_silent_writes_ratchet` from 125 to zero.

Rows: 125

Per-wave floor: 25

Estimated waves: 5

Selection policy:

- Group by write target.
- Add explicit side-effect emission, write receipts, or approved silent-write classification.
- Start with single-owner file/database writes before multi-owner runtime state writes.

Validation per wave:

- `python -m compileall -q <touched files>`
- Focused tests for write success/failure and receipt emission.
- Gate replay for `C3_silent_writes_ratchet` on touched paths.

Rollback/skip criteria:

- Stop if write semantics are ambiguous or require migration receipt.
- Skip writes in archived/generated files only with explicit exclusion evidence.

### W8 - N Guardrail Separation Burndown

Objective: Reduce `N_guardrail_separation_ratchet` from 88 to zero.

Rows: 88

Per-wave floor: 25

Estimated waves: 4

Selection policy:

- Group by shared write target between L5 guardrails and L3 orchestration.
- Keep L5 responsible for policy decisions and L3 responsible for orchestration state transitions.
- Introduce lower-layer data contracts or explicit facades when shared state cannot be eliminated directly.

Validation per wave:

- `python -m compileall -q <touched files>`
- Focused tests for guardrail decision and orchestration side effects.
- Gate replay for touched shared write targets.

Rollback/skip criteria:

- Stop if separating writes changes enforcement semantics without approved design.
- Skip clusters that need product/security policy choice; continue with independent clusters.

### W9 - Final P1=0 Proof

Objective: Prove all ordinary P1 and ratchet P1 rows are zero before merge/publication.

Required proof:

- No ordinary P1 high anti-pattern rows in regenerated or replayed evidence.
- `P1_FIX=0`
- `P1_RATCHET_REGRESSION=0`
- `P1_RATCHET_FLOOR_BACKLOG=0`
- Action queue, gate results, burndown table, and burndown report agree.
- No P0 FIX/WAVE reintroduced.

Validation commands:

- Targeted compile/test commands for the final touched set.
- Lightweight ADG gate replay where available.
- Full ADG certification handoff proof before merge/publication:
  `python tools/adg/run_full_adg_audit.py --mode certification --format both --continue-on-p0`
- Re-consume the released handoff:
  `python tools/adg/consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json`

Stop conditions:

- Any P1 row remains.
- Any artifact disagreement appears.
- Any P0 FIX/WAVE row appears.
- Full ADG proof is stale, digest-invalid, timestamp-inconsistent, or not direct.
- Merge/publish is blocked by validation, conflict, credentials, or remote rejection.

## Estimated Validation Cost

| Wave group | Estimated per-wave validation | Final validation cost |
|---|---|---|
| O1 | 1 to 5 minutes | Included in current run |
| E1 | 5 to 15 minutes per module family | Gate replay plus focused tests |
| B2 | 10 to 30 minutes per dependency cluster | ADG layer replay plus package tests |
| I1 | 5 to 20 minutes per entrypoint group | Exit-path tests plus gate replay |
| M | 5 to 20 minutes per schema group | Schema tests plus command dry runs |
| O | 5 to 20 minutes per provider/tool group | Receipt tests plus redaction checks |
| C3 | 5 to 15 minutes per write-target group | Side-effect tests plus gate replay |
| N | 10 to 30 minutes per shared-target group | Guardrail/orchestration tests plus gate replay |
| Final proof | Full audit duration for current repo size | Fresh released handoff must prove P1=0 |

## Deadline Assumption

The current automation window can safely stage the ordinary P1 patch and generate this all-scope wave plan. It cannot safely execute 98 structural ratchet waves under the standing approval without repeatedly crossing design, ownership, public-contract, or migration-receipt boundaries.

Execution must continue in bounded follow-on waves that keep each patch reversible and independently validated. The all-or-nothing target remains unchanged: downstream lanes stay blocked until P1=0 is proven.

## Stop Conditions For All Waves

- Design choice required.
- Broad cross-layer refactor required outside the selected family.
- Public contract change required.
- Migration receipt required.
- Ownership decision unclear.
- Repeated test failure.
- Dirty unrelated user changes in the worktree.
- Merge conflict or remote publication block.
- Handoff/gate/action-queue/burndown disagreement.
- Any P0 FIX/WAVE row appears.

## Reporting Fields

Current run reporting values:

- `ordinary_p1_target = 3`
- `ratchet_target = 3646`
- `planned_rows = 3649`
- `attempted_rows = 253`
- `cleared_rows = not proven until regenerated/replayed ADG evidence`
- `remaining_rows = 3396 ratchet rows expected before regeneration, assuming 250 E1 rows clear after ADG refresh`
- `final_p1_count = not zero / not proven`
- `target_status = missed`
- `blocker_type = RATCHET_SCOPE_REQUIRES_WAVE_REFACTOR_EXECUTION`
- `next_unblock_action = execute W2 through W9 in bounded family waves, then consume a fresh full ADG handoff proving P1=0`
