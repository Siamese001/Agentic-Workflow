---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\meta-learning-realtime-healing-hardened-3d6acd.md'
original_relative_path: 'meta-learning-realtime-healing-hardened-3d6acd.md'
source_sha256: e1e5ac372aff87db7c6ef2c3a87759741ad526d35b4756b2295555bd205eab18
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Meta-Learning Real-Time Healing — Hardened Implementation Plan

This plan integrates architectural hardenings to ensure meta-learning is applied at heal-time while preserving sovereignty, determinism, and C0 informational-only constraints.

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


## Executive Summary

The original plan closed 6 gaps where meta-learning was post-fact, but introduced sovereignty violations. This hardened revision eliminates those violations while preserving all gap closures. Key changes: pattern advice is advisory-only (no tier promotion), bus is injected from L0, cross-layer imports removed, and success rate store is deterministic.

---

## Critical Hardenings Applied

### 1. C0 Compliance Restored
- Pattern advice can append reason_codes and adjust confidence for audit
- **FORBIDDEN:** tier promotion/demotion based on embeddings
- Routing remains pure function of core signals + historical priors

### 2. Control Plane Centralization
- MetaLearningBus no longer instantiated in L2
- Bus injected from L0, default is NullBus
- Preserves single control plane invariant

### 3. Layer Boundary Enforcement
- DefaultHealingPatternAdvisor uses protocol injection only
- No direct L2→L1 imports across layers
- All cross-layer dependencies via seams

### 4. Determinism Hardening
- HealingSuccessRateStore uses fixed precision (6 decimals)
- Updates logged via ExecutionTrace
- Export/import for replay reconstruction
- No silent failure paths

### 5. Invariant Preservation
- retry_count ≥ 3 forces GEMINI_2_5_PRO (unconditional)
- Oscillation guard requirements added
- Confidence always clamped to [0.0, 1.0]

---

## Revised Architecture

```
HealingInput
    │
    ├──► [Phase 1] MetaPriorProvider.get_prior(error_signature)
    │         └── reads from deterministic HealingSuccessRateStore
    │                   ▲
    │                   │ [Phase 2] write-back with ExecutionTrace
    │                   │
    ▼
route_healing_tier()          ← pure function: core + priors + retry
    │
    ├──► [Phase 3] HealingPatternAdvisor.advise(healing_input)
    │         └── returns metadata only (no tier changes)
    │         └── appends reason_codes, adjusts confidence for audit
    │
    ▼
dispatch_healing()
    │
    ├──► invoker.invoke_*()
    │
    ├──► [Phase 2] update_qwen_confidence_prior() (if QWEN)
    │
    ├──► _emit_outcome()  ────►  HealingOutcomeSink
    │                                   │
    │                                   ▼ [Phase 2]
    │                            OutcomeWriteBackHook
    │                                   │
    │                                   ▼
    │                            HealingSuccessRateStore.update()
    │                                   ▲
    │                                   │
    └── feeds back to MetaPriorProvider ─┘
    │
    └──► [Phase 4] MetaLearningBus (injected) enqueue
```

---

## Phase 1 — Deterministic Prior Cache

**Objective:** Replace dead stub with deterministic, replay-reconstructable store.

**Files (N=3):**
- `system_learning/ports/meta_prior_provider.py` (NEW)
- `system_learning/engines/healing_success_rate_store.py` (NEW, hardened)
- `agentic_core/L2_execution/healers/healing_tier_router.py` (MODIFY)

**Key Hardenings:**
- Fixed precision rounding to 6 decimals
- `export_state()` for replay reconstruction
- ExecutionTrace logging on updates
- No silent exceptions

---

## Phase 2 — Write-Back with Guardrails

**Objective:** Feed outcomes back with structured telemetry and invariant protection.

**Files (N=2):**
- `system_learning/ports/outcome_write_back_hook.py` (NEW)
- `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` (MODIFY)

**Key Hardenings:**
- Structured telemetry on failures
- Preserves retry_count ≥ 3 escalation
- No threshold mutations
- Oscillation guard documentation

---

## Phase 3 — Advisory-Only Pattern Influence

**Objective:** Provide pattern insights without altering routing decisions.

**Files (N=3):**
- `system_learning/ports/healing_pattern_advisor.py` (NEW)
- `system_learning/engines/default_healing_pattern_advisor.py` (NEW, protocol-only)
- `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` (MODIFY)

**Key Hardenings:**
- **REMOVED:** tier promotion logic
- Pattern advice appends reason_codes only
- Confidence adjustment for audit only
- No cross-layer imports

---

## Phase 4 — Bus Injection Only

**Objective:** Enqueue outcomes via injected bus, preserving control plane.

**Files (N=2):**
- `system_learning/ports/meta_outcome_bus_hook.py` (NEW)
- `agentic_core/L2_execution/healers/healing_tier_dispatcher.py` (MODIFY)

**Key Hardenings:**
- No internal bus instantiation
- Default is NullBus
- Bus injected from L0 only
- Proposal-only enforcement

---

## Implementation Diffs Summary

### Phase 1 Changes
```python
# healing_success_rate_store.py - hardened
def record_outcome(self, error_signature: str, success: bool) -> None:
    # ... EMA calculation with 6-decimal rounding
    self._rates[error_signature] = round(new_rate, 6)
    # ExecutionTrace logging
    self._log_update(error_signature, success, new_rate)

def export_state(self) -> dict[str, Any]:
    """For replay reconstruction."""
    return {"rates": dict(self._rates), "counts": dict(self._counts)}
```

### Phase 2 Changes
```python
# outcome_write_back_hook.py - with telemetry
def on_outcome(self, *, healing_input, decision, record, success: bool) -> None:
    try:
        self._store.record_outcome(healing_input.error_signature, success)
    except Exception as exc:
        self._emit_telemetry("write_back_failed", str(exc))

    # Preserve retry escalation invariant
    if healing_input.retry_count >= 3:
        # Never override forced escalation
        return
```

### Phase 3 Changes
```python
# REMOVED: tier promotion logic
# Pattern advice now only appends reason_codes and adjusts confidence for audit
if advice.pattern_found:
    decision = HealingDecision(
        heal_confidence=round(decision.heal_confidence + advice.confidence_boost, 6),
        tier=decision.tier,  # NEVER CHANGE TIER
        reason_codes=decision.reason_codes + (f"pattern_match={advice.similarity_score:.6f}",),
    )
```

### Phase 4 Changes
```python
# meta_outcome_bus_hook.py - injection only
class DefaultMetaOutcomeBusHook:
    def __init__(self, bus: MetaLearningBus | None = None) -> None:
        self._bus = bus  # Injected, never constructed internally

    def publish(self, ...) -> None:
        if self._bus is None:
            return  # NullBus default
        # Enqueue only if bus provided
```

---

## Test Coverage Requirements

Each phase requires tests for:
- Determinism and replay reconstruction
- C0 advisory-only behavior
- Bus injection contracts
- Invariant preservation (retry escalation)
- Oscillation guard behavior
- Precision rounding correctness

---

## Sovereignty Compliance Matrix

| Requirement | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|---|---|---|---|---|
| C0 informational-only | ✅ | ✅ | ✅ | ✅ |
| No threshold mutation | ✅ | ✅ | ✅ | ✅ |
| Control plane centralization | ✅ | ✅ | ✅ | ✅ |
| Layer boundaries | ✅ | ✅ | ✅ | ✅ |
| Deterministic replay | ✅ | ✅ | ✅ | ✅ |
| No silent failures | ✅ | ✅ | ✅ | ✅ |

---

## Forbidden Actions (Reiterated)

- Do NOT modify `HEALING_CONFIDENCE_X` or `HEALING_CONFIDENCE_Y`
- Do NOT allow pattern advice to change tier selection
- Do NOT instantiate MetaLearningBus in L2
- Do NOT import across layers without protocol injection
- Do NOT use floating point without fixed precision
- Do NOT swallow exceptions silently
- Do NOT override retry_count ≥ 3 escalation

---

## Phase Execution Order

| Phase | Files | Primary Gap | Sovereignty |
|---|---|---|---|
| Phase 1 | 3 | Gap 1, 3 | Deterministic store |
| Phase 2 | 2 | Gap 2, 5 | Write-back guardrails |
| Phase 3 | 3 | Gap 2, 4 | Advisory-only patterns |
| Phase 4 | 2 | Gap 6 | Bus injection |
| **Total** | **10** | **All 6 gaps** | **Fully compliant** |

This hardened plan closes all meta-learning gaps while preserving architectural sovereignty and determinism.

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

