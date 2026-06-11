---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\l2-execute-v3-gap-c4d7a8.md'
original_relative_path: 'l2-execute-v3-gap-c4d7a8.md'
source_sha256: 779624cd7f775a4ed3a97a1fb4a1424bdecac179d733abe2282c574f74d278c4
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L2 EXECUTE v3 — Gap Assessment & Receipt Closure Plan

- **Plan ID**: `l2-execute-v3-gap-c4d7a8`
- **Tier**: T3 (additive types + orchestrator across L2)
- **Status**: EXECUTING
- **Source doctrine**: `docs/reference/04_L2_Execute/04_L2_Execute_v3.md` (40 sub-items E1.1–E5.8)
- **Predecessors (closed)**: `l2-execute-best-practices-gap-b7c4e2` (16 gaps), `l2-execute-v2-agent-conformance-c8e4f1` (10 gaps)
- **ADG snapshot**: `artifacts/adg/adg_indexed_*.sqlite` (latest)
- **Last refreshed**: 2026-04-25

## 1. Scope

Close the v3-specific named-receipt + lineage gaps. **Additive only**: no edits to existing W1–W6 primitives. Out of scope: refactor of `SealedL2Artifact`, changes to UWG, L4 commit path, L5 HITL channel.

## 2. Detailed v3 Cross-Walk

| v3 | Requirement | Status | Evidence |
|---|---|:---:|---|
| E1.1 Packet receive | accept signed L0/L3 packet | ✅ | `prompt_envelope_validator.py`, `types/l2_instruction_packet.py` |
| E1.2 Authority bind | route_id, step_id, capability_token, compliance_hash, sandbox_envelope | ✅ | `capability/ticket_builder.py`, `types/capability_token_v4_types.py`, `types/sandbox_envelope_types.py` |
| E1.3 Environment freeze | tools/model/runtime/fs/network/secrets/budget locked | ✅ | `determinism/freeze_propagator.py`, `enforcement/budget_enforcer.py` |
| E1.4 Determinism bind | blueprint_hash, policy_hash, prompt_hash, input_hash, replay_key, **attempt_seed** | ⚠️ | `replay_envelope.py` ✅; **`attempt_seed`: 0 hits** |
| E1.5 Idempotency guard | run_id / idempotency_key | ✅ | `utils/replay_guard.py` (75 hits) |
| E1.6 Lineage root | **parent_route_id, parent_plan_id, parent_step_id, ancestry chain** | ❌ | 0 hits each |
| E1.7 Write lock | no L4/UWG direct path | ✅ | `enforcement/durable_write_wrapper.py`, UWG |
| **E1.8 PrepReceipt** | sealed receipt with frozen inputs/caps/budget/lineage | ❌ | **0 hits** — gap |
| E2.1 Signature chain | packet integrity / handoff boundary | ✅ | `prompt_envelope_validator.py`, `enforcement/manifest_hash_validator.py` |
| E2.2 Capability scope | tool/action ⊆ capability_token | ✅ | `enforcement/e2_validate_before_execute.py` (W1) |
| E2.3 Budget scope | timeouts, retry ceiling, IO quota, breaker | ✅ | `enforcement/budget_enforcer.py` |
| E2.4 Schema shape | input/output schema, allowed terminal classes | ✅ | `enforcement/seal_schema_validator.py` (W5) |
| E2.5 Side-effect class | READ/WRITE/ACTION/IRREVERSIBLE | ✅ | `types/l2_safety_contracts.py` (W1) |
| E2.6 Safety sanity | ACL, injection flags | ✅ | `enforcement/tool_guardrail_pipeline.py` (W1) |
| E2.7 Executability | runs without rerouting/replan | ⚠️ | implicit; no named check |
| **E2.8 ValidationReceipt** | **validation_packet_id** PASS / sealed REJECTED | ❌ | **0 hits** — gap |
| E3.1 Attempt open | attempt_count++, link validation_packet_id | ⚠️ | counters exist but no link to validation_packet_id |
| E3.2 Invocation build | exact tool/model call | ✅ | `reasoning/tool_intent_executor.py` |
| E3.3 Sandbox run | frozen perms / timeouts / breaker | ✅ | `enforcement/preventative_sandbox.py`, `enforcement/egress_proxy.py` (W2) |
| E3.4 Telemetry capture | trace_id, span_id, latency, stderr, return code | ✅ | `audit/telemetry_bus.py`, OTel hooks |
| E3.5 Output capture | payload, intermediate receipts, state diff, evidence | ✅ | `reasoning/compiled_artifact.py` |
| E3.6 Local checks | parseability, declared schema, return class | ✅ | `enforcement/seal_schema_validator.py` |
| E3.7 Result classify | SUCCESS/SOFT_REPAIRABLE/FAIL_TERMINAL/NEEDS_HELP/REJECTED | ✅ | `HealOutcome` (c8e4f1 W2) + `TerminalClassification` |
| **E3.8 AttemptReceipt** | sealed per-attempt receipt with counters/trace/result | ❌ | **0 hits** — gap |
| E4.1 Failure record | reason_code, parent_packet_id, failed_span_id | ⚠️ | `reason_code` ✅; `parent_packet_id` ✅; `failed_span_id` 0 |
| E4.2 Localize | classify schema/timeout/parse/tool/missing-input/transient | ✅ | `healers/heal_classifier_model.py` |
| E4.3 Repair plan | bounded fix only | ✅ | `healers/local_healer.py`, `healers/healing_router.py` |
| E4.4 Snapshot guard | same blueprint_hash/policy_hash/caps | ✅ | `assert_snapshot_binding` (c8e4f1 W1) |
| E4.5 Oscillation guard | repair_count + reason_code + retry ceiling | ✅ | `MAX_REPAIR_COUNT=3`, `enforcement/deterministic_loop_detector.py` |
| E4.6 Revalidation | back through E2/E3 checks | ✅ | `enforcement/e2_agent_gate.py` (c8e4f1 W4) |
| **E4.7 HealReceipt** | sealed `repair_attempt_id`, delta, counters, outcome | ❌ | **0 hits** — gap |
| E4.8 Outcome routing | PASS→E3 / FAIL→NEEDS_HELP / ESCALATE / FAIL_TERMINAL | ✅ | `HealOutcome` enum |
| E5.1 Payload package | final answer / artifact / failure record | ✅ | `SealedL2Artifact` |
| E5.2 Evidence package | evidence refs, state diff, stdout summary | ✅ | `SealedL2Artifact.evidence_bundle` |
| E5.3 Trace package | trace_id, span_ids, attempt receipts, lineage root, ancestry | ⚠️ | trace_id ✅; **attempt receipts + ancestry not yet packaged** |
| E5.4 Replay package | replay_key, input_hash, blueprint_hash, policy_hash, prompt_hash | ✅ | `ReplayMetadata` (some fields scarce: blueprint_hash 2, prompt_hash 1) |
| E5.5 Terminal stamp | SUCCESS/FAILURE/NEEDS_HELP/REJECTED | ✅ | `TerminalClassification` |
| E5.6 Contract check | satisfies post-L2 disposition contract | ✅ | `seal_schema_validator.py` (W5) |
| E5.7 Commit boundary | no durable write | ✅ | `durable_write_wrapper.py` invariant |
| **E5.8 DispatchReceipt** | `sealed_l2_artifact_id` for [5] / UWG / L6 | ❌ | **0 hits** — gap |

**Gap count**: 7 named-receipt/lineage primitives + 1 orchestrator = 8 deliverables. All additive.

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| **W1** | P1.1 | LineageRoot + DeterminismBundle (incl. `attempt_seed`) | 4k 🟢 | Todo | Frozen dataclasses with all v3 fields; round-trip serialization tested |
| **W2** | P2.1 | PrepReceipt (E1.8) + ValidationReceipt (E2.8) | 5k 🟢 | Todo | Receipts carry lineage + determinism + accept/reject status; sealed once |
| **W3** | P3.1 | AttemptReceipt (E3.8) + HealReceipt (E4.7) | 5k 🟢 | Todo | Receipts carry attempt_count/repair_count, outcome class, link to validation_packet_id |
| **W4** | P4.1 | DispatchReceipt (E5.8) + tie into existing `SealedL2Artifact` | 4k 🟢 | Todo | DispatchReceipt references sealed_l2_artifact_id; targets [5]/UWG/L6 enumerated |
| **W5** | P5.1 | `L2PhasePipeline` orchestrator: E1→E2→E3→E4→E5 emitting all 5 receipts | 8k 🟢 | Todo | End-to-end test runs SUCCESS path + REJECTED path + HEAL→PASS path; produces ordered receipt sequence |
| **W6** | P6.1 | Harden + test + commit + push | 4k 🟢 | Todo | All tests green; commits per wave; pushed to origin/main |

**Total**: ~30k tokens. All waves additive — no edits to W1–W6 primitives from prior plans.

## 4. Phase-Level Summary

| Phase ID | Title | Scope | Pain Points | Tokens | Status |
|---|---|---|---|---:|---|
| P1.1 | Lineage + Determinism types | new `agentic_core/L2_execution/types/l2_v3_receipts.py` | snapshot binding must agree with c8e4f1 W1 | 4k | Todo |
| P2.1 | Prep + Validation receipts | extend `l2_v3_receipts.py` | reject path must be sealed before E3 runs | 5k | Todo |
| P3.1 | Attempt + Heal receipts | extend `l2_v3_receipts.py` | counters must increment monotonically; reason_code reused | 5k | Todo |
| P4.1 | Dispatch receipt | extend `l2_v3_receipts.py`; helper `from_sealed()` against existing `SealedL2Artifact` | no edit to `SealedL2Artifact` | 4k | Todo |
| P5.1 | Phase pipeline | new `agentic_core/L2_execution/orchestration/l2_phase_pipeline.py` | adapter pattern only; do not import heavy agents | 8k | Todo |
| P6.1 | Test + commit + push | `tests/unit/agentic_core/L2_execution/test_l2_v3_*.py` | full pytest run for new files | 4k | Todo |

## 5. ADG_HOTSPOT_REPORT (carried from b7c4e2 W0)

Reusing snapshot from `b7c4e2` §10 (no new edges into hot files). Targets are NEW files; fan_in=0 by definition.

| File (new) | Archetype | Fan-in | Layer | Impact |
|---|---|:-:|---|:-:|
| `types/l2_v3_receipts.py` | STATE_NODE | 0 | L2 | 0 (greenfield) |
| `orchestration/l2_phase_pipeline.py` | ORCHESTRATOR | 0 | L2 | 0 (greenfield) |

## 6. ADG_GRAPH_LAYER_EVIDENCE (carried)

Reusing `b7c4e2` §11 evidence:
- `mv_l2_phase_coverage` — new orchestrator must keep coverage ≥ baseline
- `mv_replay_surface_gaps` — new receipts close v3 replay gaps
- `mv_capability_and_egress_gaps` — receipts carry capability_token reference
- `v_p0_write_bypass_uwg` — MUST stay empty (invariant)
- `v_p2_duplicated_adapters` — new orchestrator must NOT duplicate `l2_agent_wrappers.run_l2_phases()` — adapter only

ADG Provenance: `backend=sqlite_direct, snapshot=adg_indexed_04232026_2225.sqlite` (carried — additive change, no regen needed pre-W6).

## 7. Exit Criteria

1. All 8 deliverables landed; all v3 named-receipt fields searchable in repo.
2. New unit tests pass; existing W1–W6 tests (191 across both prior plans) unaffected.
3. ADG regen post-W5 shows no new P0/P1 violations.
4. All waves committed individually; final push to `origin/main`.
5. Memory writeback: `ProceduralPattern:L2v3ReceiptClosure2026Q2`.
