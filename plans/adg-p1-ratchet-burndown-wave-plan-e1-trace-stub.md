# ADG P1 Ratchet Burndown Wave Plan - 07142026_0023

## Status Tables

| Wave | Scope | Target rows | Status | Stop condition |
|---:|---|---:|---|---|
| 0 | Dependency gate and P0/P1 evidence intake | 0 | Complete | Stop if handoff validator fails or P0_FIX/P0_WAVE is nonzero |
| 1 | Ordinary P1 FIX rows | 0 | Complete | Ordinary P1 is already clear in this generation |
| 2 | E1 trace-stub module wave | 1 | Executed | Source-level E1 proof and runtime proof passed; immutable snapshot replay remains old-state evidence |
| 3+ | Remaining P1 ratchet families | 2608 | Deferred | Continue only with safe mechanical subsets and focused proof |

## Evidence

ADG Provenance: backend=degraded_sqlite, snapshot=adg_indexed_07142026_0023.sqlite.

The producer-root handoff pointer is `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json`.
The validated immutable handoff is `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_07142026_0023.json`.
The validator command was:

```powershell
python tools/adg/consume_adg_repair_handoff.py --handoff-pointer C:\Git\Agentic-Workflow-FRESH\artifacts\adg\handoffs\adg_repair_handoff_latest.json --json
```

Validator result: exit code 0, `dependency_status=ready`, `artifact_status=repair_ready`, `adg_run_id=07142026_0023`.

Digest-bound artifacts:

| Artifact | Path | SHA-256 |
|---|---|---|
| snapshot | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_07142026_0023.sqlite` | `eb4ed076b76bdc7eb4f8b7d7f191bb492fd25bedc0900f479908e51ba0050dab` |
| gate results | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_gate_results_20260714_044004.json` | `e0d0125639a517bb58be00937201bdfb43c74405e11299ed6f1486a50813b4a3` |
| action queue | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_action_queue_07142026_0023.json` | `d650a743d3f0f456e0866e16f766490b537a05a9416b74c8ba6e9c5d8ca4a202` |
| burndown report | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_burndown_report_07142026_0023.md` | `6fc619c751a1bca43864f7ccb0b0668b2a6453ebdd723adddd15b2ce6337d962` |
| burndown table | `C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_burndown_table_07142026_0023.json` | `8ba19ac2e266e018a03acdb894afbd9eabf75369e6310e24497bbadc8813a851` |

P0 lane condition: `P0_FIX=0`, `P0_WAVE=0`, no promoted P0 FIX/WAVE row in gate results or action queue. `P0_TRACKED_BACKLOG=3` remains tracked backlog and is not a P1 target.

Ordinary P1 condition: `P1_FIX=0`, `P1_RATCHET_REGRESSION=0`. The ordinary P1 target is therefore `ordinary_p1_target=0`.

P1 ratchet backlog condition: `P1_RATCHET_FLOOR_BACKLOG=7` gates, 2609 rows. The all-or-nothing downstream clearance target is `target_rows=2609`, `final_p1_count=0`.

## P1 Ratchet Wave Math

| Priority | Gate | Rows | Ratchet target | Wave count | Initial disposition |
|---:|---|---:|---:|---:|---|
| 1 | `B2_layer_skip_ratchet` | 863 | 44 | 20 | Design-owned cross-layer import reshaping; skip until a safe file cluster is isolated |
| 2 | `M_taint_actionable_ratchet` | 699 | 35 | 20 | Design-owned structured-output contract work; skip until schema ownership is explicit |
| 3 | `I1_exit_disposition_ratchet` | 695 | 35 | 20 | Broad L2/L6 lifecycle contract work; skip until terminal-disposition model is selected |
| 4 | `O_tool_call_parity_ratchet` | 207 | 25 | 9 | Observability contract work; skip until receipt surface is selected per provider/tool family |
| 5 | `N_guardrail_separation_ratchet` | 88 | 25 | 4 | Cross-layer write-target separation; skip until shared target ownership is explicit |
| 6 | `C3_silent_writes_ratchet` | 56 | 25 | 3 | Mostly ops/tools/test inventory in this snapshot; skip production-irrelevant rows first |
| 7 | `E1_trace_stub_module` | 1 | 1 | 1 | Selected safe mechanical wave |

## Selected Wave

Selected gate: `E1_trace_stub_module`.

Exact row from the digest-bound snapshot:

| Gate | File | Total imports | Trace imports | Trace ratio |
|---|---|---:|---:|---:|
| `E1_trace_stub_module` | `agentic_core/adg/runtime/determinism_control.py` | 76 | 62 | 0.816 |

Why selected:

- It is the only E1 row and has no broad architecture or public-contract decision.
- The fix is mechanical: collapse many direct lifecycle-trace symbol imports into one lifecycle-trace module alias while preserving the same calls.
- It can be validated with a failing structural regression test, focused runtime behavior proof, and the E1 gate replay pinned to the digest-bound snapshot or regenerated snapshot.

PRE_CODE_GATE:

Changed surfaces:

- `agentic_core/adg/runtime/determinism_control.py` import surface only.
- No public class, function, or method signature changes are intended.

Existing test coverage:

- Existing repository tests import the ADG runtime package and determinism types indirectly.
- No focused test currently guards this file against trace-theater import fan-out.

Coverage gaps:

- No test fails when `determinism_control.py` directly imports many `_emit_*` lifecycle trace functions.
- No focused runtime smoke test proves `DeterminismController` still emits a digest after import-surface refactor.

Required new tests:

- `test_determinism_control_uses_trace_contract_module_alias`: assert direct imports from `lifecycle_trace_contract` do not include `_emit_*` fan-out and use the module alias instead.
- `test_determinism_controller_digest_survives_trace_import_refactor`: instantiate `DeterminismController`, seed/patch/emit digest, and assert deterministic report state is preserved.

Dimensions:

- Edge cases: module import shape has a strict structural assertion.
- State transitions: controller seed, patch, digest, and report transitions are exercised.
- Determinism: digest hash is recomputed from fixed events.
- Fail-closed: structural test fails on direct `_emit_*` import fan-out.
- Matrix: one trace-import shape plus one runtime behavior path.

## Validation Commands

Run after the test is written and before production change to prove the structural test fails:

```powershell
python -m pytest tests/unit/agentic_core/adg/runtime/test_determinism_control_trace_stub.py -q
```

Run after production change:

```powershell
python -m pytest tests/unit/agentic_core/adg/runtime/test_determinism_control_trace_stub.py -q
python -m py_compile agentic_core/adg/runtime/determinism_control.py tests/unit/agentic_core/adg/runtime/test_determinism_control_trace_stub.py
$env:ADG_SNAPSHOT='C:\Git\Agentic-Workflow-FRESH\artifacts\adg\adg_indexed_07142026_0023.sqlite'; python ops_scripts/ci/check_trace_stub_modules.py
```

Runtime proof artifact:

`artifacts/codex/runtime_proofs/adg_p1_e1_trace_stub_runtime_proof_20260714.json`

## Publication Plan

If the selected wave passes focused tests, compile, runtime proof, and E1 replay:

1. Commit with a partial-progress message, because P1 remains nonzero.
2. Push branch `codex/adg-p1-ratchet-burndown-20260714T0518Z`.
3. Open or update the PR to `main` with `codex` and `codex-automation` labels when available.
4. Merge non-squash when publication gates pass.
5. Push `origin/main`.
6. Run:

```powershell
python scripts/governance/codex_main_closeout.py --apply --fetch --json
python scripts/governance/codex_main_closeout.py --check --fetch --json
```

Downstream status remains blocked unless regenerated or replayed evidence proves final P1 count is zero. This selected wave can at most reduce the tracked P1 ratchet backlog from 2609 to 2608.

## Wave 2 Result

Executed on branch `codex/adg-p1-ratchet-burndown-20260714T0518Z`.

Changed files:

- `agentic_core/adg/runtime/determinism_control.py`
- `tests/unit/agentic_core/adg/runtime/test_determinism_control_trace_stub.py`

Validation result:

- Pre-change focused pytest failed for the intended E1 structural reason: 62 direct trace emit imports.
- Post-change focused pytest passed: `2 passed`.
- `py_compile` passed for the production module and test file.
- Runtime proof artifact passed at `artifacts/codex/runtime_proofs/adg_p1_e1_trace_stub_runtime_proof_20260714.json`.
- Pinned immutable-snapshot E1 replay passed as a ratchet gate but still reported the old released-snapshot row (`current=1 baseline=1`). It is not clearance evidence for this worktree edit.

Target status after this wave: `missed/BLOCKED`. The lane remains blocked for downstream P2/P3 until a fresh full ADG generation proves P1=0.

## Stop Criteria

Stop without further edits if:

- Any digest-bound artifact conflicts with validator counts.
- The selected E1 test or runtime proof fails after one repair attempt.
- The E1 replay cannot be pinned to the released handoff snapshot.
- Publication is blocked by dirty unrelated worktrees, merge conflicts, credentials, or remote rejection.
- A remaining P1 family requires a design decision, public contract change, migration receipt, or uncertain ownership decision.
