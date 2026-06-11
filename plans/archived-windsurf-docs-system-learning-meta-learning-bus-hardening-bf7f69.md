---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\system-learning-meta-learning-bus-hardening-bf7f69.md'
original_relative_path: 'system-learning-meta-learning-bus-hardening-bf7f69.md'
source_sha256: 1437f6511912f21023e21790d9b4bbf5f376a2498ee565c16ab1c130ddd833d0
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# System Learning & Meta-Learning Bus Hardening

Closes the end-to-end feedback loop so healing outcomes flow from the dispatch path through the meta-learning bus, update L4-backed success-rate priors, and feed back into confidence routing at heal-time.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State (AST Scan Findings)

### Files in scope
| File | Role |
|------|------|
| `agentic_core/L0_routing/meta_control/meta_learning_bus.py` | FIFO queue, `MetaLearningChangePackage` |
| `system_learning/ports/meta_prior_provider.py` | Read-only seam for priors |
| `system_learning/ports/meta_outcome_bus_hook.py` | Publishes healing outcomes |
| `system_learning/engines/healing_success_rate_store.py` | In-memory success-rate store |
| `system_learning/pipelines/meta_learning_pipeline.py` | Full W4-A–W4-E pipeline |
| `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` | Dispatch path (wires hook) |
| `agentic_core/L2_execution/healers/healing_tier_router.py` | Consumes `MetaPriorProvider` |
| `agentic_core/L2_execution/healers/qwen_meta_learning.py` | Qwen-side prior update |
| `system_learning/engines/rlhf_optimizer.py` | DPO-driven bounded adjustments |

### Critical Gaps Found

**Gap 1 — Schema mismatch: `DefaultMetaOutcomeBusHook` uses wrong constructor (BREAKING)**
`meta_outcome_bus_hook.py` creates `MetaLearningChangePackage(change_type=..., payload=..., proposal_only=True)`.
Actual class in `meta_learning_bus.py` takes `(trace_id, kind, payload, package_hash)` with no `change_type` or `proposal_only` fields.
This fails at runtime whenever the hook fires.

**Gap 2 — No bus consumer drains the queue**
`MetaLearningBus` is a pure FIFO deque. Nothing calls `dequeue()` and applies outcomes to the success-rate store. Published packages silently accumulate and are garbage-collected between runs.

**Gap 3 — Live `MetaPriorProvider` not injected in production**
`healing_tier_router.route_healing_tier()` accepts `meta_prior_provider` but defaults to `None`, silently falling back to neutral prior. No code wires the real L4-backed provider.

**Gap 4 — Bus is in-memory only; no persistence**
All accumulated priors are lost between process restarts. Cold-start always returns 0.50 neutral prior regardless of historical performance.

**Gap 5 — `HealingSuccessRateStore` not backed by L4**
`qwen_meta_learning._historical_success_rates` is a module-level dict. Same dict sits in `system_learning/engines/healing_success_rate_store.py`. No shared persistent store; updates from one path are invisible to the other.

**Gap 6 — No end-to-end test for dispatch → bus → prior → routing**

---

## Phase 1 — Fix `MetaLearningChangePackage` Schema Mismatch (Wave 1)

**Scope:** `meta_outcome_bus_hook.py` only

**Wave 1-A: Align `DefaultMetaOutcomeBusHook` to actual constructor**
Replace:
```python
MetaLearningChangePackage(change_type=..., proposal_only=True)
```
With:
```python
MetaLearningChangePackage.create(
    trace_id=healing_input.trace_id,
    kind="healing_outcome",
    payload={...}
)
```
This is a breaking bug fix — single-file change.

**Acceptance criteria:**
- `tests/unit/test_meta_learning_bus.py` passes with no `TypeError`.
- New test: `DefaultMetaOutcomeBusHook.publish_outcome()` called with valid inputs → bus size increases by 1.

---

## Phase 2 — Bus Consumer: Drain → Update Success-Rate Store (Wave 2)

**Scope:** New `system_learning/engines/bus_consumer.py` + `healing_success_rate_store.py`

**Wave 2-A: `HealingSuccessRateStore` as L4-backed singleton**
- Define `HealingSuccessRateStore` with `get_rate(error_signature) → float` and `update_rate(error_signature, success) → None`.
- Back it by a JSON file in `L4_state/stores/healing_success_rates.json` (atomic write via temp file + `os.replace`).
- Expose `get_bm25_store()`-style singleton accessor `get_success_rate_store()`.

**Wave 2-B: `MetaLearningBusConsumer`**
- Implement `drain_and_apply(bus, store)` function:
  - Dequeues all packages from `MetaLearningBus`.
  - For `kind == "healing_outcome"`: calls `store.update_rate(error_signature, success)`.
  - Returns count of processed packages.
- Called by background thread or explicit tick in `meta_learning_pipeline.run()`.

**Acceptance criteria:**
- `drain_and_apply(bus, store)` with 3 pre-enqueued packages → store has updated 3 rates.
- Persistence test: write store → reload from JSON → rates match.
- Idempotency test: calling `drain_and_apply` twice on empty bus → 0 packages, no error.

---

## Phase 3 — Wire Live `MetaPriorProvider` into Routing (Wave 3)

**Scope:** `healing_tier_dispatcher.py`, new `L4MetaPriorProvider`

**Wave 3-A: `L4MetaPriorProvider` adapter**
- Implement `L4MetaPriorProvider` satisfying `MetaPriorProvider` protocol.
- Delegates `get_prior(error_signature)` to `HealingSuccessRateStore.get_rate(error_signature)`.
- Falls back to `NeutralMetaPriorProvider` on `FileNotFoundError` (cold start).

**Wave 3-B: Wire into dispatcher**
- In `healing_tier_dispatcher.py`, construct `L4MetaPriorProvider` once (lazy singleton).
- Pass it to `route_healing_tier(..., meta_prior_provider=provider)`.
- After dispatch completes, call `DefaultMetaOutcomeBusHook.publish_outcome(...)`.
- Call `drain_and_apply(bus, store)` at end of dispatch cycle (synchronous, in-process).

**Acceptance criteria:**
- Integration test: inject store with `error_signature="syntax_error"` at rate=0.95 → assert routing selects `LOCAL_AGENT` for borderline confidence input.
- Cold-start test: no JSON file present → `NeutralMetaPriorProvider` used, no exception.

---

## Phase 4 — RLHF Optimizer + Dampening Integration (Wave 4)

**Scope:** `rlhf_optimizer.py`, `meta_learning_pipeline.py`

**Wave 4-A: Connect RLHF optimizer to pipeline**
- `DefaultDeterministicRLHFOptimizer.propose_from_dpo()` already produces bounded `ChangePackage`.
- Wire it into `meta_learning_pipeline.run()` after healing outcome aggregation.
- Proposals written to L4 as advisory; never auto-activated.

**Wave 4-B: Oscillation + cooldown guard**
- Verify `OscillationPolicy` and `CooldownPolicy` are applied before any proposal in the pipeline.
- Write matrix test: fast repeated outcomes → no proposal due to cooldown.

**Evidence file:** `docs/reports/sub/phase_system_learning_bus_evidence.md`

---

## Risk Register

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| JSON store file contention under concurrent healing | Medium | `threading.Lock` wrapping all store reads/writes |
| Bus fills unboundedly under high heal rate | Medium | Add `maxlen` to `deque` (e.g., 10 000) with drop-oldest |
| RLHF adjustment creating runaway threshold drift | Low | Bounds enforced in `DefaultDeterministicRLHFOptimizer` |
| Cold start with corrupt JSON | Low | Atomic write + checksum validation on load |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

