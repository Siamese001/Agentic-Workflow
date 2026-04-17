# Wave F2 - Source Authoring Log

Per-gap honest record of F2's closure work, with outcomes and evidence.

Outcomes:
- **CLOSED** - real ARCHITECTURAL source found in repo and atom upgraded to NORMATIVE.
- **PARTIAL** - supplementary source added; evidence_class unchanged.
- **DEFERRED** - no real source located; WEAK retained; blocker carried forward.
- **REJECTED** - attempted closure would have required fabrication.

---

## F08 Exit Spine (RED 0.20 -> GREEN 1.00 projected)

### F08.01 - single evaluation spine
- **Outcome:** CLOSED.
- **Source:** `docs/architecture/eval_pipeline_acceptance.md` (SRC-ADR-003).
- **Evidence:** Named `evidence_eval_bridge.evaluate_and_emit()` as "Sole canonical choke point"; Invariant #2 "Singular live disposition - ExitControlGate.evaluate_sealed() is the only live gate call per request."

### F08.02 - L5 exit policy binding
- Already NORMATIVE in v1.1. No F2 action required, but SRC-ADR-003 adds direct reinforcement (ExitControlGate lives at `L5_safety/enforcement/exit_control_gate.py`).

### F08.03 - record run outcome
- **Outcome:** CLOSED.
- **Source:** SRC-ADR-003.
- **Evidence:** `evaluate_and_emit()` fires both `AsyncEvalIngester` and `ShadowEvalIngester` with outcome tracking; `build_shadow_eval_packet()` emits the CURRENT_RUN -> FUTURE_RUN recorded outcome.

### F08.04 - signal UWG for durable writes
- **Outcome:** CLOSED.
- **Source:** SRC-ADR-003.
- **Evidence:** Invariant #4: "Durable writes behind governed handoff only - `GovernedHandoffAgent.handoff()` is the sole durable-write seam". Handoff calls `PromotionAuthority.update_pointer_via_gateway()` (UWG).

### F08.05 - no ad-hoc exit paths
- **Outcome:** CLOSED.
- **Source:** SRC-ADR-003.
- **Evidence:** Invariant #5 + explicit enumeration of three fenced modules (`eval_spine.py`, `execution_adapter.py`, `eval_spine_adapter.py`) with `NON_CANONICAL_EVAL_LAB` markers and the rule "Do not add canonical pipeline wiring to these modules."

### F08 summary
- **4 of 4 WEAK atoms closed.** F08 moves RED -> GREEN.

---

## F07 Heal/Retry/Recovery (RED 0.25 -> YELLOW 0.75 projected)

### F07.01 - bounded heal/retry/recovery path
- **Outcome:** CLOSED.
- **Source:** `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md` (SRC-ADR-002).
- **Evidence:** `HealerRetryManager.execute_with_retry()` with `max_attempts=3` and `strictness_escalation=[0.70, 0.85, 0.95]`. Explicit invariant: bounded path via scope_lock + retry limits.

### F07.02 - bounded attempt count or duration
- **Outcome:** CLOSED.
- **Source:** SRC-ADR-002.
- **Evidence:** `timeout_escalation=[30, 20, 10]` seconds per attempt; `_should_retry()` returns False when `attempt >= max_attempts - 1`. "Max retries exhausted" is an explicit invariant.

### F07.03 - surface to L3 for re-planning
- **Outcome:** DEFERRED.
- **Candidate evaluated:** SRC-ADR-001 (`healing_dispatch_routing_adr.md`) describes ESCALATED tier routing to HITL or deterministic abort. However, the ADR carries `invalid_for_normative_use=True` on its frontmatter and cannot provide NORMATIVE support. SRC-ADR-002 does not explicitly name L3 as the re-planning target.
- **Held as:** WEAK_EVIDENCE with SRC-ADR-001 as ADVISORY supplement.
- **Blocker:** need a normative ADR (or constitutional rule) that explicitly names L3 as the escalation target. The `healing_dispatch_routing_adr.md` ADR could be revised to drop `invalid_for_normative_use` once HITL-reviewed, which would close this.

### F07.04 - no silent durable mutations in healing paths
- Already NORMATIVE in v1.1. No F2 action.

### F07 summary
- **2 of 3 WEAK atoms closed.** F07 moves RED -> YELLOW.

---

## F04 Context Assembly (RED 0.25, unchanged)

### F04.02 - context attribution
- **Outcome:** DEFERRED.
- **Candidates evaluated:** Constitutional §5 ADG-first (code dependencies, not context); AGENTS.md Memory Lifecycle (memory write, not context assembly); `normative_requirements_spec.md` (retrieval/shaping, not context grounding).
- **Held as:** WEAK_EVIDENCE (unchanged from v1.1).
- **Blocker B3 unchanged.**

### F04.03 - no private unattributed context substitute
- **Outcome:** DEFERRED. Same reason as F04.02.

### F04.04 - context assembly idempotence
- **Outcome:** PARTIAL.
- **Supplementary source added:** SRC-ADR-005 (`REPLAY_DETERMINISM_RULES.md`) for replay-determinism doctrine. Explicitly defines `mutation_hash` over `(actor_id, run_id, operation, path, data_hash)` and `ReplayModeGuard` requiring identical mutation chains on replay.
- **Why not upgraded to NORMATIVE:** the spec covers mutation replay determinism, not context-assembly-layer idempotence. Adjacent principle, not direct statement.
- **Held as:** WEAK_EVIDENCE with SRC-ADR-005 binding.

### F04 summary
- **0 of 3 WEAK atoms upgraded.** F04 remains RED.
- F2 refused to author a speculative context-assembly ADR without implementation backing and HITL review.

---

## F09 Write Gate (YELLOW 0.80 -> GREEN 1.00 projected)

### F09.05 - reject writes without exit signal
- **Outcome:** CLOSED.
- **Source:** SRC-ADR-003.
- **Evidence:** `GovernedHandoffAgent.handoff(approved=True)` returns `HandoffRecord(committed=False, error=...)` when `packet.approval_state != "APPROVED"`. This is the exit-signal rejection semantic: no approval signal from the evaluation spine -> no durable write.

---

## Yellow-family cleanup

### F01.06 - structured rejection reason code
- **Outcome:** CLOSED.
- **Source:** SRC-ADR-004 (`L0_DECOMPOSITION_SPEC.md`).
- **Evidence:** L0a's `IngressValidationResult` has an explicit `rejection_reason` field; failure-modes table enumerates structured reasons (schema_invalid, auth_failed, budget_exhausted).

### F03.04 - one route per plan step
- **Outcome:** CLOSED.
- **Source:** SRC-ADR-004.
- **Evidence:** L0b invariant: "Final path selection is deterministic in L0b" and "ML routing NEVER directly selects final path. Only L0b deterministic logic selects path." Single `RoutingDecision.path` value returned per invocation.

### F05.04 - L3 dispatch to L2
- **Outcome:** DEFERRED.
- **Candidates evaluated:** SRC-ADR-006 (`AUTHORITY_HIERARCHY_INVARIANTS.md`) covers L1/L0/L2/L5/UWG/L4/L6 authority but does not name L3 as a distinct authority layer. The required execution flow `L1_PROPOSE -> L0_AUTHORIZE -> L5_VALIDATE -> L2_EXECUTE -> UWG_MUTATE` has no L3 step.
- **Held as:** WEAK_EVIDENCE (unchanged).
- **Blocker B6:** need an L3-orchestration charter ADR that explicitly defines L3's dispatch role.

---

## Summary Counts

| Outcome | Count |
|---|---:|
| **CLOSED** | **9** (F07.01, F07.02, F08.01, F08.03, F08.04, F08.05, F09.05, F01.06, F03.04) |
| PARTIAL | 1 (F04.04) |
| DEFERRED | 4 (F04.02, F04.03, F05.04, F07.03) |
| REJECTED | 0 |

## Projected Coverage

| Family | v1.1 | Post-F2 (projected) | Bucket change |
|---|---:|---:|---|
| F01 | 0.83 YELLOW | 1.00 GREEN | YELLOW -> GREEN |
| F03 | 0.75 YELLOW | 1.00 GREEN | YELLOW -> GREEN |
| F04 | 0.25 RED | 0.25 RED | unchanged |
| F05 | 0.75 YELLOW | 0.75 YELLOW | unchanged |
| F07 | 0.25 RED | 0.75 YELLOW | RED -> YELLOW |
| F08 | 0.20 RED | 1.00 GREEN | RED -> GREEN |
| F09 | 0.80 YELLOW | 1.00 GREEN | YELLOW -> GREEN |

**Global projection:** 45 NORM + 13 WEAK -> **54 NORM + 4 WEAK** -> coverage = `54 / (54 + 4) = 0.931` **GREEN**.

From v1.1 0.776 YELLOW to projected **0.931 GREEN** (bucket flip).

Red families remaining: **1** (F04 only).
Green families: **8** (F01, F02, F03, F06, F08, F09, F10, F11, F12).
Yellow families: **2** (F05, F07).
