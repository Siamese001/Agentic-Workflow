# ADG P1 H1 New-Orphan Burndown Plan

Plan ID: adg-p1-h1-new-orphan-burndown-9b2f6c
Automation ID: weekly-adg-audit-and-burndown
Generated: 2026-07-08T22:18:00-04:00
Branch: codex-generate-full-adg
Worktree: C:\Git\Agentic-Workflow-FRESH-worktrees\codex-generate-full-adg
Status: execution started

## Scope

This plan handles the single P1 FIX gate emitted by the released full ADG handoff `07082026_2156`.

The historical plan file `plans/adg-p1-ratchet-burndown-wave-plan-4c8d2a.md` has unrelated uncommitted edits in the primary `main` checkout. This plan intentionally uses a new file to avoid overwriting that dirty work during the local-main fast-forward.

## Status Tables

### Wave Progress

| Wave | Gate | Rows | Target | Status | Evidence |
|---|---|---:|---:|---|---|
| W0 | Producer handoff intake | 1 | 1 | Passed | `consume_adg_repair_handoff.py` returned `ok=true`, `P0_FIX=0`, `P0_WAVE=0`, `P1_FIX=1` |
| W1 | H1 new orphan | 1 | 0 | Fixed | Gate SQL now counts symbol-target imports as module fan-in |
| W2 | Focused validation | 0 | 0 | Passed | Focused pytest plus H1 unit coverage passed |
| W3 | Full ADG handoff refresh | 0 | 0 | Passed with post-gate debt | Full ADG emitted repair-ready handoff `07082026_2214`; post gates remain red |
| W4 | Local-main PR execution | 0 | 0 | Pending | Branch tip contained in local `main` |

### Phase Progress

| Phase | Objective | Status | Exit condition |
|---|---|---|---|
| P1-A | Confirm P0 stays clear | Passed | `P0_FIX=0`, `P0_WAVE=0` in released handoff |
| P1-B | Identify the H1 row | Passed | Snapshot diff `07082026_2146 -> 07082026_2156` found one new orphan |
| P1-C | Align H1 with ADG import model | Fixed | H1 counts incoming imports to module nodes and same-path symbol nodes |
| P1-D | Prove H1 clears | Passed | Gate result reports `H1_new_orphans_delta_ratchet` pass with `violation_count=0` |
| P1-E | Publish locally | Pending | Local `main` fast-forwards to branch tip |

## Source Evidence

| Artifact | Path |
|---|---|
| Handoff pointer | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json` |
| Immutable handoff | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_07082026_2156.json` |
| Current snapshot | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_07082026_2156.sqlite` |
| Prior snapshot | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_07082026_2146.sqlite` |
| Gate results | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_gate_results_20260709_020235.json` |
| Action queue | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_action_queue_07082026_2156.json` |

Released handoff counts:

| Count | Value |
|---|---:|
| P0_FIX | 0 |
| P0_WAVE | 0 |
| P0_TRACKED_BACKLOG | 4 |
| P1_FIX | 1 |
| P1_RATCHET_REGRESSION | 1 |
| P1_RATCHET_FLOOR_BACKLOG | 7 |

## RCA

`H1_new_orphans_delta_ratchet` compares the current ADG module-orphan set to the prior snapshot. It flags modules with `fan_in=0` on `imports` edges.

The only new orphan is:

| Layer | Path |
|---|---|
| L_APP | `apps_rg/runtime/sections/section_final_materialized_binding.py` |

The module is not dead. It is imported by runtime consumers, but those imports resolve to symbol nodes:

| Importer | Imported symbols |
|---|---|
| `apps_rg/runtime/spine/section_x3_finalize.py` | `final_claim_ledger_rows`, `resolve_final_materialized_text`, `validate_final_materialized_input_binding` |
| `apps_rg/runtime/sections/section_x2_gate_outputs.py` | `augment_x2_payload_with_final_materialized_binding` |
| `apps_rg/runtime/sections/role_episode_lane.py` | `augment_x2_payload_with_final_materialized_binding` |

Because H1 counted only direct module-node fan-in, symbol-target imports left the module node orphaned even though the module was live. That made H1 sensitive to ADG's bipartite module-to-symbol graph shape rather than actual runtime reachability.

The first full rerun also exposed a second nuance: H1 is a delta gate, so a stale new-orphan row can age out once the next run becomes the prior snapshot. The durable fix is therefore not just a consumer import-shape change; H1 itself must resolve symbol-target imports back to their owning module path.

## Repair Design

Keep the high-authority runtime consumer as a module-alias import:

`from apps_rg.runtime.sections import section_final_materialized_binding as final_materialized_binding`

Then call helper functions through `final_materialized_binding.<helper>`.

Patch `ops_scripts/ci/check_w6_new_orphans_delta.py` so `_orphan_set` treats an import to any node with the same `resolved_path` as module fan-in, while excluding same-file self edges. This matches the ADG graph projection note that imports are commonly module-to-symbol edges.

## Validation Commands

Run these before commit:

```powershell
python -m pytest tests\unit\apps_rg\test_section_x3_finalize.py tests\unit\apps_rg\test_section_authority_x2_write_integration.py tests\unit\apps_rg\test_role_episode_x2_gates.py -q
python -m pytest tests\unit\ops_scripts\ci\test_check_w6_new_orphans_delta.py -q
python tools\adg\consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json
python tools\adg\run_full_adg_audit.py --mode certification --format both --continue-on-p0
```

Focused H1 proof:

```powershell
python tools\generate\generate_full_adg.py --continue-on-p0
```

Then compare the fresh snapshot with `07082026_2156` and require no new H1 orphan rows for the touched module.

## Stop Conditions

| Condition | Action |
|---|---|
| P0 FIX or P0 WAVE reappears | Stop and do not start lower lanes |
| H1 still reports the touched module | Stop and inspect ADG import extraction |
| Focused tests fail twice with the same cause | Stop and report blocker |
| Full ADG handoff is incomplete or digest-invalid | Stop and block downstream lanes |
| Primary checkout dirty file would be overwritten | Stop and preserve user work |

## Definition Of Done

| Requirement | Done when | Evidence |
|---|---|---|
| H1 row identified | Exact new orphan path is known | SQLite diff output |
| Source fix scoped | Only module fan-in repair is changed | Git diff |
| Tests pass | Focused apps_rg and H1 gate tests pass | Pytest output |
| H1 clears | Fresh ADG comparison shows no new H1 orphan row | SQLite diff output |
| Handoff released | Producer-root handoff consumer returns `ok=true` | Consumer JSON |
| Branch committed | All branch changes are committed | Git log |
| Local PR executed | Local `main` contains branch tip | `merge-base --is-ancestor` |
