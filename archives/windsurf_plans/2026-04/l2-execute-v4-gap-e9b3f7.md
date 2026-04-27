# L2 EXECUTE v4 — Gap Assessment & Closure Plan

- **Plan ID**: `l2-execute-v4-gap-e9b3f7`
- **Tier**: T3 (additive: extend v3 receipts + pipeline + invariants)
- **Status**: EXECUTING
- **Source doctrine**: `docs/reference/04_L2_Execute/04_L2_Execute_v4.md` (735 lines, formal output contracts + 15 invariants + failure matrix)
- **Predecessor (closed)**: `l2-execute-v3-gap-c4d7a8` (8 v3 gaps closed; 33 tests + 151 prior tests)
- **Last refreshed**: 2026-04-25

## 1. v4 ↔ v3 Delta Inventory

| v4 addition | v3 state | Gap |
|---|:-:|:-:|
| `DEGRADED_SUCCESS` result class (E3.7, E5.5) | absent | ❌ |
| `RepairStatus` enum (REPAIRED/NOT_REPAIRED/QUARANTINED/NEEDS_HELP/FAIL_TERMINAL) | partial via HealOutcomeStamp | ❌ |
| `QUARANTINE` E4.8 outcome | absent | ❌ |
| `DispatchTarget` enum (EXIT_CONTROL/L3_MERGE/HITL_PACKETIZATION/UWG_REQUEST_CANDIDATE) | absent | ❌ |
| `ExecutionLane` enum (READ/MODEL/TOOL/ACTION/ARTIFACT) | absent | ❌ |
| E1.5 duplicate-sealed-receipt return | not implemented | ❌ |
| `SealedL2ArtifactContents` 7-section schema (identity/governance/execution/evidence/replay/observability/terminal) | partial via SealedL2Artifact | ❌ |
| `repair_tactic`, `before_hash`/`after_hash`, `oscillation_status`, `snapshot_guard_status`, `next_action` (E4 OUTPUT) | absent | ❌ |
| `decisive_reason_code`, `local_check_results`, `generated_artifacts`, `proposed_state_diff`, `quarantined_payload` (E3 OUTPUT) | absent | ❌ |
| `user_visible_safe`, `commit_requested`, `downstream_recommendation` (E5.5/E5 OUTPUT) | absent | ❌ |
| `decisive_rule_id`, `capability_scope_summary`, `side_effect_class`, `budget_snapshot` (E2 OUTPUT) | partial (only failed_rule + classified_side_effect) | ⚠️ |
| `frozen_execution_context`, `replay_bindings`, `write_lock_assertion`, `ready_for_validation` (E1 OUTPUT) | partial via PrepReceipt | ⚠️ |
| 15 numbered L2 invariants | undocumented in code | ❌ |
| Failure/Repair/Exit matrix | undocumented in code | ❌ |

**Gap count**: 14 deltas. All additive — extend existing v3 dataclasses with optional fields + defaults; existing 33 v3 tests must continue passing.

## 2. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| **W1** | P1.1 | New v4 enums (DEGRADED_SUCCESS, RepairStatus, DispatchTarget, ExecutionLane) extending v3 | 4k 🟢 | Todo | All v3 tests still green; new enums importable |
| **W2** | P2.1 | Extend AttemptReceipt + HealReceipt + DispatchReceipt with v4 fields (defaulted) | 5k 🟢 | Todo | Backward-compat preserved; new fields optional |
| **W3** | P3.1 | New `SealedL2ArtifactContents` 7-section schema; invariants module | 5k 🟢 | Todo | All 15 invariants represented; container builds from receipts |
| **W4** | P4.1 | Pipeline: handle DEGRADED_SUCCESS, duplicate-sealed-return (E1.5), QUARANTINE outcome, dispatch_target derivation | 6k 🟢 | Todo | New paths covered; v3 paths unchanged |
| **W5** | P5.1 | Tests for all v4 deltas (enums, fields, invariants, pipeline paths) | 6k 🟢 | Todo | New tests pass + v3 33 tests still green |
| **W6** | P6.1 | Harden + ruff + commit + push | 3k 🟢 | Todo | All tests green; pushed to origin/main |

**Total**: ~29k tokens. Additive — no edits to W1–W5 v3 primitive return shapes or test assertions.

## 3. Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Tokens | Status |
|---|---|---|---|---:|---|
| P1.1 | v4 enums | extend `agentic_core/L2_execution/types/l2_v3_receipts.py` | enum identity must match v4 spec literals exactly | 4k | Todo |
| P2.1 | v4 receipt fields | same file | every new field defaulted; tests must still pass | 5k | Todo |
| P3.1 | SealedL2ArtifactContents + invariants | new `agentic_core/L2_execution/types/l2_v4_invariants.py` | 15 invariants encoded with check fns | 5k | Todo |
| P4.1 | Pipeline v4 paths | extend `agentic_core/L2_execution/orchestration/l2_phase_pipeline.py` | duplicate-cache must be opt-in; default behavior unchanged | 6k | Todo |
| P5.1 | v4 tests | new `tests/unit/agentic_core/L2_execution/test_l2_v4_deltas.py` + `test_l2_v4_invariants.py` | cover DEGRADED, QUARANTINE, dispatch routing, invariant checks | 6k | Todo |
| P6.1 | Harden + commit | ruff, full pytest, git push | none | 3k | Todo |

## 4. ADG_HOTSPOT_REPORT (carried)

Reusing v3 plan's `ADG_HOTSPOT_REPORT` — v4 changes target the same files (`l2_v3_receipts.py`, `l2_phase_pipeline.py`) which were greenfield in v3 plan. New file `l2_v4_invariants.py` has fan_in=0.

## 5. ADG_GRAPH_LAYER_EVIDENCE (carried)

`mv_l2_phase_coverage`, `mv_replay_surface_gaps`, `v_p0_write_bypass_uwg` (must stay empty), `v_p2_duplicated_adapters` (no duplication of v3 receipts).

ADG Provenance: `backend=sqlite_direct, snapshot=adg_indexed_04232026_2225.sqlite` (additive change; no regen needed).

## 6. Exit Criteria

1. All 14 v4 deltas closed.
2. New tests pass + v3 33 tests + 151 prior L2 tests still pass.
3. `ruff check` clean on all 4 deliverables.
4. Plan committed; all waves committed individually; final push to `origin/main`.
