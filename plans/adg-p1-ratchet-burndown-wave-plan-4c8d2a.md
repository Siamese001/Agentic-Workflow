# ADG P1 Ratchet Burndown Wave Plan

Plan ID: adg-p1-ratchet-burndown-wave-plan-4c8d2a
Automation ID: adg-p1-ratchet-burndown
Refresh generated: 2026-07-08T18:22:13-04:00
Repo root: C:\Git\Agentic-Workflow-FRESH
Current local main: e8ad5e0af2e09c8bb4bfee4cd814778d7cf488c3
Origin main at refresh: 1ec308532ae9b0698853d0b5e9f6b11a442e27ef
Authority: AGENTS.md, docs/codex-primary-execution.md, .codex/automations/adg-p1-ratchet-burndown/automation.toml

## Scope

This is the refreshed P1 wave plan after ordinary P1 and the safe mechanical E1 trace-stub path were merged through PR #516.

The plan separates three states that were previously mixed:

- Digest-bound ADG baseline from `07072026_2307`.
- Merged but not yet ADG-regenerated P1 repair progress.
- Remaining structural ratchet families that require family-specific wave harnesses before source edits.

P1=0 remains the only clearance condition. P2/P3 must stay blocked until a fresh digest-bound full ADG handoff proves:

- `P1_FIX=0`
- `P1_RATCHET_REGRESSION=0`
- `P1_RATCHET_FLOOR_BACKLOG=0`
- no promoted P0 FIX or P0 WAVE rows

## Status Tables

### Wave Progress

| Wave | Family | Planned rows | Attempted rows | Proven cleared rows | Status | Evidence |
|---|---|---:|---:|---:|---|---|
| W0 | Dependency gate | 0 | 0 | 0 | Passed for current planning evidence | `consume_adg_repair_handoff.py` returned `dependency_status=ready`, `artifact_status=repair_ready`, `P0_FIX=0`, `P0_WAVE=0` |
| W1 | Ordinary P1 high anti-patterns | 3 | 3 | Not proven by fresh ADG | Merged | L2 package repair and HTTP judge repairs landed before the E1 waves |
| W2.E1.1-20 | `E1_trace_stub_module` | 982 | 979 | Not proven by fresh ADG | Merged, mechanical pool exhausted | PRs #511 through #516; wave 21 manifest has `candidate_count=0` |
| W2.E1.R | E1 residual proof/remediation | TBD after fresh ADG | 0 | 0 | Next gate | Must run fresh ADG before selecting B2 |
| W3.B2 | `B2_layer_skip_ratchet` | 862 | 0 | 0 | Planned | Requires layer-skip wave harness |
| W4.I1 | `I1_exit_disposition_ratchet` | 695 | 0 | 0 | Planned | Requires exit-disposition wave harness |
| W5.M | `M_taint_actionable_ratchet` | 688 | 0 | 0 | Planned | Requires schema/actionability wave harness |
| W6.O | `O_tool_call_parity_ratchet` | 206 | 0 | 0 | Planned | Requires tool-call receipt parity harness |
| W7.C3 | `C3_silent_writes_ratchet` | 125 | 0 | 0 | Planned | Requires write side-effect/receipt harness |
| W8.N | `N_guardrail_separation_ratchet` | 88 | 0 | 0 | Planned | Requires guardrail/orchestration separation harness |
| W9 | Final P1=0 proof | All remaining | 0 | 0 | Blocked until W2-W8 clear | Full ADG certification and handoff consumption |

### Phase Progress

| Phase | Objective | Status | Exit condition |
|---|---|---|---|
| P1-A | Prove upstream dependency and P0 clean | Passed for current evidence | Validator passes with `P0_FIX=0`, `P0_WAVE=0`, no artifact drift |
| P1-B | Clear ordinary P1 source rows | Merged, not freshly regenerated | Fresh ADG shows no ordinary P1 rows |
| P1-C | Exhaust safe E1 mechanical path | Merged, pending fresh ADG | Fresh ADG shows E1 zero or enumerates residual E1 rows |
| P1-D | Build next structural family harness | Not started | Harness can select, apply, replay, and validate a bounded family wave |
| P1-E | Burn down structural families | Not started | B2/I1/M/O/C3/N all zero in fresh/replayed evidence |
| P1-F | Final certification and publication | Blocked | Fresh full ADG handoff proves P1=0, then branch is merged and published |

## Evidence Snapshot

All baseline counts below are from the producer-root artifacts, not a worktree-local pointer.

| Artifact | Path |
|---|---|
| Handoff pointer | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json` |
| Immutable handoff | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_07072026_2307.json` |
| SQLite snapshot | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_07072026_2307.sqlite` |
| Gate results | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_gate_results_20260708_032528.json` |
| Action queue | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_action_queue_07072026_2307.json` |
| Burndown table | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_burndown_table_07072026_2307.json` |
| Burndown report | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_burndown_report_07072026_2307.md` |

Validator command:

```powershell
python tools\adg\consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json
```

Accepted result at refresh:

- `adg_run_id=07072026_2307`
- `dependency_status=ready`
- `artifact_status=repair_ready`
- `P0_FIX=0`
- `P0_WAVE=0`
- `P1_FIX=0`
- `P1_RATCHET_FLOOR_BACKLOG=7`
- `P1_RATCHET_REGRESSION=0`

ADG MCP health at refresh:

- `status=ok`
- `sqlite=healthy`
- `redis=healthy`
- `adg_snapshot_id=07072026_2307`

## Current Numeric Model

The digest-bound ADG baseline still reports the original ratchet floors. The merged wave work has not been incorporated into a fresh ADG generation yet, so projected remaining counts are not clearance proof.

| Family | Digest-bound baseline rows | Merged selected rows | Blocked or residual rows before fresh ADG | Projected remaining rows |
|---|---:|---:|---:|---:|
| `E1_trace_stub_module` | 982 | 979 | 3 | 3 |
| `B2_layer_skip_ratchet` | 862 | 0 | 862 | 862 |
| `I1_exit_disposition_ratchet` | 695 | 0 | 695 | 695 |
| `M_taint_actionable_ratchet` | 688 | 0 | 688 | 688 |
| `O_tool_call_parity_ratchet` | 206 | 0 | 206 | 206 |
| `C3_silent_writes_ratchet` | 125 | 0 | 125 | 125 |
| `N_guardrail_separation_ratchet` | 88 | 0 | 88 | 88 |
| Total P1 ratchet | 3646 | 979 | 2667 | 2667 |

Planning values:

- `ordinary_p1_target = 3`
- `ratchet_target = 3646`
- `target_rows = 3649`
- `attempted_rows_to_date = 982` (3 ordinary P1 + 979 E1)
- `projected_remaining_ratchet_rows = 2667`
- `cleared_rows = not proven until fresh ADG`
- `final_p1_count = not zero / not proven`
- `target_status = missed`

## Completed Work

### Ordinary P1

The ordinary P1 source rows were handled before ratchet waves started:

- `agentic_core/L2_execution/l2_package_driven_executor.py`
- `agentic_core/L3_orchestration/exit_eval/judges/_base_http_judge.py`
- `tests/unit/agentic_core/L2_execution/test_l2_package_driven_repair.py`

Validation used:

```powershell
python -m compileall -q agentic_core\L2_execution\l2_package_driven_executor.py agentic_core\L3_orchestration\exit_eval\judges\_base_http_judge.py tests\unit\agentic_core\L2_execution\test_l2_package_driven_repair.py tests\unit\agentic_core\L3_orchestration\exit_eval\test_http_judges.py
python -m pytest tests\unit\agentic_core\L2_execution\test_l2_package_driven_repair.py tests\unit\agentic_core\L3_orchestration\exit_eval\test_http_judges.py -q
```

### E1 Trace Stub Waves

The established mechanical E1 helper selected trace-heavy modules from the immutable SQLite snapshot, rewrote direct lifecycle trace symbol imports to one `trace_contract` alias, and preserved existing trace calls.

| Wave range | PR | Commit | Selected rows | Result |
|---|---|---|---:|---|
| W2.E1.1-2 | #511 | `6fd4c792ea15c6ef48421025c54bd89ef17fd5dc` | 100 | Merged |
| W2.E1.3 | #512 | `4a01aefbb9e6df47f2ba43faff9856ed29b1aca6` | 50 | Merged |
| W2.E1.4 | #513 | `a4c6da0c738a5d139bb0fc851059892180e3ae7b` | 50 | Merged |
| W2.E1.5 | #514 | `b565443c7495857d437d6f7fa7fcc09a01b065fa` | 50 | Merged |
| W2.E1.6-15 | #515 | `07381172fa1d57811fcfee53a098bcb1518afadc` | 500 | Merged |
| W2.E1.16-20 | #516 | `42f5d07c4a053a391065e8325908af9b206f6b27` | 229 | Merged |

E1 proof artifacts:

- `artifacts/codex/runtime_proofs/e1_trace_import_waves6_15_manifest.json`
- `artifacts/codex/runtime_proofs/e1_trace_import_waves6_15_source_replay.json`
- `artifacts/codex/runtime_proofs/e1_trace_import_waves6_15_runtime_proof.json`
- `artifacts/codex/runtime_proofs/e1_trace_import_waves16_20_manifest.json`
- `artifacts/codex/runtime_proofs/e1_trace_import_waves16_20_source_replay.json`
- `artifacts/codex/runtime_proofs/e1_trace_import_waves16_20_runtime_proof.json`
- `artifacts/codex/runtime_proofs/e1_trace_import_wave21_manifest.json`

E1 stop condition reached:

- `e1_trace_import_wave21_manifest.json` reports `candidate_count=0`.
- `e1_trace_import_wave12_blocked_candidates.json` records `agentic_core/adg/runtime/determinism_control.py` as parse-invalid under the mechanical rewrite.
- Fresh ADG must now decide whether E1 is fully cleared, has residual non-mechanical rows, or needs an explicit exclusion/backlog disposition.

## Next Execution Order

Do not start B2 until W2.E1.R completes. E1 is still the highest-priority family by severity ordering until fresh ADG proves it is zero.

1. Run a fresh full ADG certification from local `main` or a clean main-derived worktree:

   ```powershell
   python tools\adg\run_full_adg_audit.py --mode certification --format both --continue-on-p0
   ```

2. Consume the fresh handoff:

   ```powershell
   python tools\adg\consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json
   ```

3. If E1 is not zero, execute W2.E1.R before B2:

   - enumerate residual E1 rows from the fresh action queue/burndown artifacts
   - classify each residual row as mechanical, owner-decision, public contract, or exclusion/backlog candidate
   - repair mechanical residual rows only
   - stop if residual rows require design ownership or public contract changes

4. If E1 is zero and P0 remains clean, start W3.B2 with a family-specific harness.

5. Continue families in order: B2, I1, M, O, C3, N.

6. Regenerate and consume full ADG after every family or after a bounded wave batch if the family harness can prove exact row-level deltas.

## Wave Catalog

### Wave 0 - Dependency Gate

Objective: prove this lane is downstream-safe before each edit batch.

Required checks:

- producer-root handoff pointer resolves to immutable timestamped artifacts
- receipt SHA, run ID, and artifact digests validate
- `P0_FIX=0`
- `P0_WAVE=0`
- action queue, gate results, burndown table, and report do not promote P0 FIX/WAVE rows

Stop if any dependency artifact is stale, missing, digest-invalid, timestamp-inconsistent, or not direct.

### Wave 1 - Ordinary P1

Status: merged, pending fresh ADG proof.

No new source work is planned here unless fresh ADG reintroduces ordinary P1 rows.

### Wave 2 - E1 Residual Proof

Objective: prove `E1_trace_stub_module=0` or isolate residual non-mechanical rows.

Rows:

- Baseline: 982
- Merged selected: 979
- Projected residual: 3

Wave plan:

| Sub-wave | Scope | Target | Stop rule |
|---|---|---:|---|
| W2.E1.R0 | Fresh ADG proof | all E1 rows | Stop if P0 reappears or artifacts drift |
| W2.E1.R1 | Mechanical residual rows | all safe residuals | Stop on parse-invalid or public compatibility surface |
| W2.E1.R2 | Residual owner decision packet | any unsafe residual | Stop without editing and report owner/design blocker |

Validation:

- source replay for any repaired residual
- runtime import proof or base-blocker comparison
- compileall on touched files
- pinned or fresh E1 gate replay
- fresh handoff consumption

### Wave 3 - B2 Layer Skip Ratchet

Objective: reduce `B2_layer_skip_ratchet` from 862 to zero after E1 is proven clear.

Per-wave floor:

- `max(25, ceil(862 * 0.05)) = 44`

Estimated waves:

- 20 waves: 19 waves of 44 rows plus one final smaller wave.

Harness required before edits:

- query layer-skip rows from fresh ADG artifacts
- group rows by source layer, destination layer, target module, and import symbol
- select clusters where one lower-layer contract or dependency inversion removes at least 44 rows
- emit a source replay proving the selected skip edges are gone from touched files

Preferred mechanical patterns:

- move passive data contracts downward
- introduce lower-layer protocol/types modules
- replace direct high-layer imports with dependency-inverted call sites
- avoid compatibility shims that preserve the skip

Stop conditions:

- public API migration required
- app ownership decision required
- change crosses more than one dependency cluster
- no testable lower-layer contract can be introduced safely

### Wave 4 - I1 Exit Disposition Ratchet

Objective: reduce `I1_exit_disposition_ratchet` from 695 to zero.

Per-wave floor:

- `max(25, ceil(695 * 0.05)) = 35`

Estimated waves:

- 20 waves: 19 waves of 35 rows plus one final smaller wave.

Harness required before edits:

- query `mv_exit_disposition_coverage` from fresh ADG
- group by execution entrypoint, command surface, and terminal branch pattern
- generate row-level before/after evidence for each selected entrypoint

Preferred mechanical patterns:

- add explicit success/failure/blocked disposition objects
- replace implicit fallthrough/`None` with typed terminal state
- preserve public command output unless an approved contract update exists

Stop conditions:

- external output contract would change
- disposition semantics require product or governance decision
- entrypoint has no focused test surface and cannot be smoke-tested safely

### Wave 5 - M Taint Actionable Ratchet

Objective: reduce `M_taint_actionable_ratchet` from 688 to zero.

Per-wave floor:

- `max(25, ceil(688 * 0.05)) = 35`

Estimated waves:

- 20 waves: 19 waves of 35 rows plus one final smaller wave.

Harness required before edits:

- query actionable taint rows from fresh ADG artifacts
- group by output schema owner and command/report surface
- verify each selected surface has a bounded schema or receipt target

Preferred mechanical patterns:

- bind actionable outputs to existing schema classes
- emit non-actionable diagnostic classifications where the text is informational only
- add receipt shape tests for command/report outputs

Stop conditions:

- schema ownership unclear
- user-facing output contract changes
- redaction/privacy policy decision needed

### Wave 6 - O Tool Call Parity Ratchet

Objective: reduce `O_tool_call_parity_ratchet` from 206 to zero.

Per-wave floor:

- `max(25, ceil(206 * 0.05)) = 25`

Estimated waves:

- 9 waves: 8 waves of 25 rows plus one final smaller wave.

Harness required before edits:

- query tool-call parity rows from fresh ADG
- group by provider/tool wrapper and receipt boundary
- prove each selected call path records provider identity, request intent, result status, and failure class

Preferred mechanical patterns:

- add receipt emission adjacent to tool invocation
- reuse existing redaction helpers
- avoid logging secrets or full payloads

Stop conditions:

- provider contract unavailable locally
- receipt could expose credentials or user data
- call path has side effects that cannot be dry-run tested

### Wave 7 - C3 Silent Writes Ratchet

Objective: reduce `C3_silent_writes_ratchet` from 125 to zero.

Per-wave floor:

- `max(25, ceil(125 * 0.05)) = 25`

Estimated waves:

- 5 waves.

Harness required before edits:

- query fresh C3 rows with module-target side-effect semantics
- group by write target and writer module
- prove the selected writer either emits side effect evidence or has an approved silent-write classification

Preferred mechanical patterns:

- add write receipts
- add side-effect emission to the same writer surface
- reuse existing receipt/event helpers

Stop conditions:

- write semantics ambiguous
- migration receipt required
- write target has multiple owners and no clear local contract

### Wave 8 - N Guardrail Separation Ratchet

Objective: reduce `N_guardrail_separation_ratchet` from 88 to zero.

Per-wave floor:

- `max(25, ceil(88 * 0.05)) = 25`

Estimated waves:

- 4 waves: 3 waves of 25 rows plus one final smaller wave.

Harness required before edits:

- query shared write targets between L5 guardrails and L3 orchestration
- group by shared target and policy/action boundary
- prove selected changes keep L5 policy decisions separate from L3 state transitions

Preferred mechanical patterns:

- split policy verdict objects from orchestration state writes
- introduce lower-layer data contracts or facades
- preserve enforcement semantics with tests

Stop conditions:

- security/product policy choice required
- enforcement semantics would change
- shared state owner unclear

### Wave 9 - Final P1=0 Proof

Objective: certify P1 zero before downstream lanes edit.

Required command:

```powershell
python tools\adg\run_full_adg_audit.py --mode certification --format both --continue-on-p0
python tools\adg\consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json
```

Required evidence:

- `P1_FIX=0`
- `P1_RATCHET_REGRESSION=0`
- `P1_RATCHET_FLOOR_BACKLOG=0`
- no promoted P0 FIX/WAVE rows
- action queue, gate results, burndown table, and burndown report agree
- run receipt validates
- publication closeout passes after merge

## Validation Commands

Use these as the default validation ladder for each wave.

```powershell
python tools\adg\consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json
python -c "import subprocess, compileall, sys; files=[p for p in subprocess.check_output(['git','diff','--name-only','--','*.py'], text=True).splitlines() if p.endswith('.py')]; failed=[p for p in files if not compileall.compile_file(p, quiet=1)]; print(f'COMPILE_FILE_COUNT={len(files)}'); print(f'COMPILE_FAILED_COUNT={len(failed)}'); sys.exit(1 if failed else 0)"
python -m pytest tests\unit\agentic_core\L2_execution\test_l2_package_driven_repair.py tests\unit\agentic_core\L3_orchestration\exit_eval\test_http_judges.py -q
python ops_scripts\ci\check_terminal_cleanup.py --verbose --fail-on-new-only --base-ref <base-sha>
git diff --check
python scripts\governance\verify_codex_run_receipt.py <receipt.json>
```

Add family-specific replay checks before commit:

- E1: source replay plus runtime import or base-blocker comparison
- B2: layer-skip row replay for touched source/target pairs
- I1: exit-disposition coverage replay for touched entrypoints
- M: actionable/schema binding replay
- O: receipt parity replay
- C3: side-effect/write receipt replay
- N: guardrail/orchestration shared-target replay

## Rollback And Skip Criteria

Skip an item only when other independent rows in the same family remain safe. Stop the whole wave when no independent safe rows remain.

Skip criteria:

- generated/archive row with explicit exclusion evidence
- public compatibility surface
- parse-invalid mechanical rewrite
- unavailable provider/tool contract
- no focused smoke path for side-effecting code

Stop criteria:

- design choice required
- broad cross-layer refactor required
- public contract change required
- migration receipt required
- ownership decision unclear
- repeated test failure
- dirty unrelated changes in the edit worktree
- merge conflict or remote rejection
- handoff/gate/action-queue/burndown disagreement
- P0 FIX/WAVE reappears

## Definition Of Done

| Requirement | Done when | Evidence |
|---|---|---|
| Dependency gate | Producer-root handoff validates for the current run window | `consume_adg_repair_handoff.py --json` exit 0 |
| P0 remains clean | `P0_FIX=0` and `P0_WAVE=0` with no promoted P0 rows | Handoff plus action queue/burndown agreement |
| P1 reaches zero | `P1_FIX=0`, `P1_RATCHET_REGRESSION=0`, `P1_RATCHET_FLOOR_BACKLOG=0` | Fresh full ADG certification handoff |
| Per-family replay | Selected family rows have row-level before/after proof | Family replay artifact under `artifacts/codex/runtime_proofs/` |
| Runtime smoke | Touched modules compile and focused tests or import/smoke proof passes | compileall, pytest, runtime proof |
| Static cleanup | No new terminal-cleanup or whitespace failures | terminal-cleanup and `git diff --check` |
| Receipt | Substantial wave emits a valid run receipt | `verify_codex_run_receipt.py` passes |
| Publication | Branch is committed, PR opened, non-squash merged, and pushed | local `main` equals `origin/main`; branch tip contained |

## Reporting Fields

Use these values until fresh ADG supersedes them:

- `ordinary_p1_target = 3`
- `ratchet_target = 3646`
- `planned_rows = 3649`
- `attempted_rows = 982`
- `projected_remaining_rows = 2667`
- `cleared_rows = not proven until fresh ADG`
- `final_p1_count = not zero / not proven`
- `target_status = missed`
- `blocker_type = E1_MECHANICAL_POOL_EXHAUSTED_AWAITING_FRESH_ADG_AND_STRUCTURAL_HARNESSES`
- `next_unblock_action = run fresh full ADG, resolve any residual E1, then start B2 with a family-specific harness`
