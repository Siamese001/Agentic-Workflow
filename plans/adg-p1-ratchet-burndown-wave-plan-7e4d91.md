# ADG P1 Ratchet Burndown Plan

## Baseline

- Handoff pointer: `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json`
- Validated handoff: `adg_run_id=07082026_2319`
- Handoff validator: `dependency_status=ready`, `artifact_status=repair_ready`
- Current counts: `P0_FIX=0`, `P0_WAVE=0`, `P0_TRACKED_BACKLOG=4`, `P1_FIX=0`, `P1_RATCHET_REGRESSION=0`, `P1_RATCHET_FLOOR_BACKLOG=7`
- Ordinary P1 target: `0`
- Ratchet target floor: `25`
- Planned rows: `7`
- This run's safe wave scope: `2` files, `2` E1 rows

## Ratchet Family Order

| Rank | Gate | Rows | Safety note |
|---|---|---:|---|
| 1 | `B2_layer_skip_ratchet` | 863 | Broad cross-layer edge refactor; too large for a bounded standing-approval patch in this run. |
| 2 | `C3_silent_writes_ratchet` | 56 | Broad 56-file surface; defer unless a later run has a dedicated write-side-effect harness. |
| 3 | `E1_trace_stub_module` | 3 | Safe mechanical subset exists: 2 bridge shims can be rewritten without design choice. |
| 4 | `I1_exit_disposition_ratchet` | 695 | Broad lifecycle coverage surface; defer in this run. |
| 5 | `M_taint_actionable_ratchet` | 690 | Broad taint surface; defer in this run. |
| 6 | `N_guardrail_separation_ratchet` | 88 | Broad guardrail surface; defer in this run. |
| 7 | `O_tool_call_parity_ratchet` | 206 | Broad tool-parity surface; defer in this run. |

## Most Critical Safe Wave

- Selected family: `E1_trace_stub_module`
- Why this wave: it is the highest-priority remaining family with a bounded mechanical subset that stays inside standing approval.
- Exact selected rows:
  - `apps_research/_telemetry.py`
  - `apps_research/services/telemetry.py`
- Deferred row:
  - `agentic_core/adg/runtime/determinism_control.py` is retained as the blocked E1 row for a later run because the rewrite is larger and more invasive than this lane should absorb in one safe batch.
- Per-wave floor: `ratchet_target=25`
- Safe mechanical subset: `2`
- Dependency grouping: both selected files are standalone telemetry bridge shims with the same import/re-export structure.
- Estimated validation cost: low; one focused import/fallback pytest file plus `compileall`.
- Timeout assumption: 30 seconds per targeted command, consistent with repo governance.

## Execution Plan

1. Patch both telemetry bridge shims to import the lifecycle trace contract as a module alias and re-export the contract members from that alias.
2. Add a focused regression test that checks both modules:
   - export the expected names
   - import cleanly when `agentic_core` is available
   - fall back to `_noop` behavior when `agentic_core` import fails
3. Run targeted validation:
   - `python -m compileall apps_research/_telemetry.py apps_research/services/telemetry.py tests/unit/apps_research/test_telemetry_bridge.py`
   - `python -m pytest tests/unit/apps_research/test_telemetry_bridge.py -q`
4. Capture a runtime proof artifact under:
   - `artifacts/codex/runtime_proofs/apps_research_telemetry_bridge_wave1_20260709T052502Z.json`
5. Commit, push, and publish if validation passes.

## Runtime Proof

- Proof command:
  - `python -m pytest tests/unit/apps_research/test_telemetry_bridge.py -q`
- Proof artifact path:
  - `artifacts/codex/runtime_proofs/apps_research_telemetry_bridge_wave1_20260709T052502Z.json`

## Branch And Publication

- Worktree: `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-adg-p1-ratchet-burndown`
- Branch: `codex/adg-p1-ratchet-burndown-20260709T012136`
- Commit sequence:
  1. `git add apps_research/_telemetry.py apps_research/services/telemetry.py tests/unit/apps_research/test_telemetry_bridge.py plans/adg-p1-ratchet-burndown-wave-plan-7e4d91.md artifacts/codex/runtime_proofs/apps_research_telemetry_bridge_wave1_20260709T052502Z.json`
  2. `git commit -m "Run ADG P1 E1 telemetry bridge wave"`
  3. `git push -u origin codex/adg-p1-ratchet-burndown-20260709T012136`
  4. Create or update PR to `main`
  5. Merge with non-squash PR merge if checks are green
  6. Run `python scripts/governance/codex_main_closeout.py --apply --fetch --json`
  7. Run `python scripts/governance/codex_main_closeout.py --check --fetch --json`

## Skip Criteria

- Skip any file that needs a design choice, broad cross-layer refactor, or uncertain ownership.
- Skip the blocked `E1` row if the alias rewrite expands beyond the two bridge shims.
- Skip `B2`, `C3`, `I1`, `M`, `N`, and `O` in this run because they are broader than the bounded mechanical patch scope.

## Stop Conditions

- Stop if compileall fails.
- Stop if the focused pytest fails.
- Stop if the runtime proof cannot import both bridge modules in both normal and fallback modes.
- Stop if the branch becomes dirty with unrelated files.
- Stop if merge or push is blocked by conflicts, credentials, or remote rejection.
- Stop as `target_status=missed/BLOCKED` if `P1=0` is not proven by fresh ADG evidence after publication.

## Downstream Status

- Current downstream-unblock status: not unblocked.
- This wave is partial progress only.
- Remaining P1 after the planned safe wave: at least the blocked `E1` row plus the broader ratchet families listed above.
