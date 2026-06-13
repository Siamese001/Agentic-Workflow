# Unified Routing -- Single Float-Confidence Gateway

Collapse 5 separate DET/QWEN/GEMINI routing systems into 1 canonical choke point (route_healing_tier / new route_by_confidence in healing_tier_router.py), retire all S-score routing logic, and eliminate every hardcoded confidence literal.

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


## ADG Source: Redis hot cache (timestamp 03132026_1424 -- 8121 nodes, 221,487 edges)

| System | File | Layer | ADG Prod Callers | Action |
|---|---|---|---|---|
| route_healing_tier() | healing_tier_router.py | L2 | 1 (healing_tier_dispatcher.py) | CANONICAL |
| decide_heal_escalation() | heal_policy_types.py | L5 | 2 (SovereignBaseAgent.py, decorators_util.py) | RETIRE routing logic |
| compute_routing_decision() | execute_ssot.py | L0 | 0 prod callers (called by _ssot_routing._route_decision) | DE-HARDCODE 13/26 |
| ConfidenceScore._high_threshold (env-var) | _ssot_types.py | L0 | 1 (_ssot_routing.py only) | REMOVE |
| heuristic_threshold=0.75 | tiered_batch_util.py | L5 | constructor default | ALIGN |

**Redis-confirmed delta from prior SQLite plan:**
- _ssot_routing.py ALREADY imports HEALING_CONFIDENCE_X + HEALING_CONFIDENCE_Y from healing_tier_config.py (9 import edges) -- Phase 5 needs no new import, only replace literals with those already-bound names
- compute_routing_decision is defined in execute_ssot.py (not _ssot_routing.py) -- adds execute_ssot.py to scope
- execute_ssot.py also already imports HEALING_CONFIDENCE_X/Y from healing_tier_config.py
- SCORE_THRESHOLD_DET / SCORE_THRESHOLD_QWEN are NOT ADG symbols -- bare integer literals 13 / 26 in _ssot_routing.py and execute_ssot.py; no existing constant to reference
- healing_tier_router.py has 1 global_state_mutation antipattern edge (unrelated to routing; noted separately)
- _ssot_routing.py has retry_without_backoff + silent_exception_swallow antipatterns (out of scope)
- RoutingTier production importers: 1 only (_ssot_routing.py) -- apps_rg / apps_shared no longer in scope
- No dead imports, no layer violations in any routing file

---

## New Addition: route_by_confidence() in healing_tier_router.py

Bridge for callers that hold a pre-computed confidence float (no HealingInput available):

    def route_by_confidence(
        confidence: float,
        *,
        retry_count: int = 0,
        config: HealingTierConfig | None = None,
    ) -> HealingDecision:

Zero new decision logic -- identical X/Y band logic as route_healing_tier(), exposed for external callers.

---

## Implementation Phases

### Phase 1 -- healing_tier_config.py (2 new constants)
- Add SSOT_SCORE_THRESHOLD_DET: int = 13
- Add SSOT_SCORE_THRESHOLD_QWEN: int = 26
  These become the canonical S-score band constants referenced by execute_ssot.py and _ssot_routing.py

### Phase 2 -- healing_tier_router.py (new function)
- Add route_by_confidence(confidence, *, retry_count, config) -> HealingDecision
- Add to __all__

### Phase 3 -- heal_policy_types.py (retire routing logic)
- Delete classify_score(), classify_confidence(), decide_reasoning_tier()
- Replace decide_heal_escalation() body: delegate to route_by_confidence(inputs.confidence_value, retry_count=inputs.prior_failures)  [lazy import from healing_tier_router to avoid L5->L2 at module level]
- HealEscalationInputs.confidence_value default: 0.75 -> HEALING_CONFIDENCE_X (import from healing_tier_config)
- Delete SCORE_THRESHOLD_DET / SCORE_THRESHOLD_QWEN constants from this file (moved to healing_tier_config.py Phase 1)

### Phase 4 -- _ssot_types.py (pure data container)
- Remove _high_threshold property (env-var SOVEREIGN_HIGH_CONFIDENCE via os.getenv -- 1 reads_env edge confirmed)
- Remove _med_threshold property
- Remove is_high_confidence, is_medium_confidence, is_low_confidence properties
- ConfidenceScore final shape: value: float, reasoning: str, factors: dict -- nothing else

### Phase 5 -- _ssot_routing.py (already has constants, just use them)
- Redis confirmed: HEALING_CONFIDENCE_X and HEALING_CONFIDENCE_Y are already imported (9 import edges)
- _route_decision(): replace bare literals 0.75 -> HEALING_CONFIDENCE_X, 0.5 -> HEALING_CONFIDENCE_Y
- compute_routing_decision() lives in execute_ssot.py -- see Phase 6 for those changes
- Remove any ImportError fallback _CONF_X/_CONF_Y literals if present

### Phase 6 -- execute_ssot.py (de-hardcode S-score thresholds)
- Redis confirmed: execute_ssot.py already imports HEALING_CONFIDENCE_X/Y from healing_tier_config.py
- Replace bare S <= 13 -> S <= SSOT_SCORE_THRESHOLD_DET (import from healing_tier_config)
- Replace bare S <= 26 -> S <= SSOT_SCORE_THRESHOLD_QWEN

### Phase 7 -- _ssot_reporting.py (band thresholds)
- Import HEALING_CONFIDENCE_X, HEALING_CONFIDENCE_Y from healing_tier_config
- Replace hardcoded band thresholds (2 antipattern edges confirmed)

### Phase 8 -- tiered_batch_util.py
- Import HEALING_CONFIDENCE_X from healing_tier_config
- heuristic_threshold: float = 0.75 -> float = HEALING_CONFIDENCE_X

### Phase 9 -- qwen_meta_learning.py (fix re-export)
- Remove HEALING_CONFIDENCE_X, HEALING_CONFIDENCE_Y from __all__
- Imports kept (needed for immutability assertions), not re-exported

### Phase 10 -- Caller updates

SovereignBaseAgent.py (2 reads_env edges confirmed -- HEAL_POLICY_MODEL_ESCALATION):
- Replace import of HealEscalationInputs / decide_heal_escalation with route_by_confidence from healing_tier_router
- Replace decide_heal_escalation(HealEscalationInputs(confidence_value=x, ...)) call with route_by_confidence(x, retry_count=prior_failures)
- Map HealingDecision.tier to existing proceed/tier logic

decorators_util.py (2 reads_env edges confirmed -- HEAL_POLICY_MODEL_ESCALATION):
- SovereignDecisionEngine._route_decision() already returns RoutingDecision with .tier set
- Use RoutingDecision.tier directly instead of re-routing via decide_heal_escalation
- Map: DETERMINISTIC -> no LLM, QWEN -> ReasoningTier.LOW, GEMINI -> ReasoningTier.HIGH
- Remove decide_heal_escalation import entirely

---

## Test Plan

| File | Action |
|---|---|
| test_heal_policy_types.py | Remove tests for classify_score / classify_confidence / decide_reasoning_tier; update decide_heal_escalation tests to verify delegation to route_by_confidence |
| test_healing_tier_router.py | Add parametric tests for route_by_confidence: 3 tiers + retry escalation boundary |
| test_ssot_types_pure_data.py (NEW) | Assert ConfidenceScore has no _high_threshold, is_high_confidence etc. |
| test_routing_single_choke_point.py (NEW) | Assert no bare 0.75 / 0.5 literals in routing files; HEALING_CONFIDENCE_X/Y are the only threshold symbols |
| test_three_tier_convergence.py | Existing -- must still pass |
| test_execute_ssot_routing_matrix.py | Existing -- verify S-score gates correct after constant extraction |

---

## Out of Scope
- apps_rg / apps_shared: Redis confirms RoutingTier now has 0 external importers outside _ssot_routing.py
- system_learning/confidence/: HealingConfidenceScorer is L6 observability, different system
- healing_tier_router.py global_state_mutation antipattern: separate issue, track separately

---

## Verification
    pytest tests/unit/agentic_core/L2_execution/healers/test_healing_tier_router.py
    pytest tests/unit/agentic_core/L5_safety/types/test_heal_policy_types.py
    pytest tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_routing_matrix.py
    pytest tests/unit_min_deps/test_three_tier_convergence.py
    python tools/generate_full_adg.py
    python tools/adg/adg_redis_ingest.py --force

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

