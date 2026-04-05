# System Learning Phase 3 — Evidence File

## 1. Commit Hash

```
649a712206c83d2be42fbde52c7127b0c1173dfa
```

## 2. File List (git diff --name-only HEAD~1..HEAD)

```
system_learning/constraints/__init__.py
system_learning/constraints/config_surfaces.py
system_learning/constraints/delta_enforcer.py
system_learning/validators/dampening.py
tests/unit_min_deps/system_learning/test_config_surface_constraints.py
tests/unit_min_deps/system_learning/test_dampening.py
```

6 files changed, 855 insertions(+)

## 3. pytest -q (Run 1)

```
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestForbiddenSurfaces::test_tool_allowlist_forbidden PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestForbiddenSurfaces::test_file_scope_whitelist_forbidden PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestForbiddenSurfaces::test_guardian_contracts_forbidden PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestForbiddenSurfaces::test_sandbox_escape_forbidden PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestUnknownSurfaces::test_unknown_surface_rejected PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestUnknownSurfaces::test_arbitrary_surface_rejected PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_escalation_threshold_valid_change PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_escalation_threshold_below_min_raises PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_escalation_threshold_above_max_raises PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_escalation_threshold_delta_too_large_raises PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_escalation_threshold_max_delta_allowed PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_anomaly_routing_threshold_valid_change PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingThresholds::test_anomaly_routing_threshold_bounds_enforced PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingIntConstraints::test_depth_breaker_valid_change PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingIntConstraints::test_depth_breaker_below_min_raises PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingIntConstraints::test_depth_breaker_above_max_raises PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingIntConstraints::test_depth_breaker_delta_too_large_raises PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL0RoutingIntConstraints::test_depth_breaker_max_delta_allowed PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestRAGParameters::test_retrieval_top_k_valid_change PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestRAGParameters::test_retrieval_top_k_bounds_enforced PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestRAGParameters::test_retrieval_top_k_delta_enforced PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestRAGParameters::test_rerank_top_n_valid_change PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestRAGParameters::test_rerank_top_n_bounds_enforced PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL1ModelPointers::test_cognition_model_valid_pointer PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL1ModelPointers::test_cognition_model_allowlist_enforced PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL1ModelPointers::test_cognition_model_unknown_model_rejected PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL1ModelPointers::test_embedding_model_valid_pointer PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL1ModelPointers::test_embedding_model_allowlist_enforced PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_token_budget_valid_change PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_token_budget_bounds_enforced PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_token_budget_delta_enforced PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_max_k_valid_change PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_max_k_bounds_enforced PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_max_retries_valid_change PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestL5PolicyTunables::test_max_retries_delta_enforced PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestTypeValidation::test_float_constraint_rejects_string PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestTypeValidation::test_int_constraint_rejects_float PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestTypeValidation::test_pointer_constraint_rejects_int PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestDeterminism::test_validation_deterministic PASSED
tests/unit_min_deps/system_learning/test_config_surface_constraints.py::TestDeterminism::test_validation_order_independent PASSED
tests/unit_min_deps/system_learning/test_dampening.py::TestCooldownPolicy::test_cooldown_elapsed_passes PASSED
tests/unit_min_deps/system_learning/test_dampening.py::TestCooldownPolicy::test_cooldown_not_elapsed_raises PASSED
tests/unit_min_deps/system_learning/test_dampening.py::TestCooldownPolicy::test_cooldown_exactly_elapsed_passes PASSED
tests/unit_min_deps/system_learning/test_dampening.py::TestSampleSizePolicy::test_sufficient_samples_passes PASSED
tests/unit_min_deps/system_learning/test_dampening.py::TestSampleSizePolicy::test_insufficient_samples_raises PASSED
tests/unit_min_deps/system_learning/test_dampening.py::TestSampleSizePolicy::test_exactly_min_samples_passes PASSED
tests/unit_min_deps/system_learning/test_dampening.py::TestDeterminism::test_cooldown_deterministic PASSED
tests/unit_min_deps/system_learning/test_dampening.py::TestDeterminism::test_sample_size_deterministic PASSED

48 passed in 0.06s
```

## 4. pytest -q (Run 2 — Determinism Proof)

```
48 passed in 0.05s
```

Identical result. All 48 tests pass on both runs.

## 5. Determinism Assertion (from test_config_surface_constraints.py, lines 192-204)

```python
class TestDeterminism:
    def test_validation_deterministic(self):
        """Same inputs produce same validation result (pass or fail)."""
        # Valid change - should pass both times
        validate_surface_change("escalation_threshold", 0.80, 0.82)
        validate_surface_change("escalation_threshold", 0.80, 0.82)

        # Invalid change - should fail both times with same exception type
        with pytest.raises(BoundsViolation):
            validate_surface_change("escalation_threshold", 0.80, 0.99)
        with pytest.raises(BoundsViolation):
            validate_surface_change("escalation_threshold", 0.80, 0.99)
```

## Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| No wall-clock/randomness/env access in new modules | PASS |
| No cross-layer runtime imports from agentic_core | PASS |
| All tunables allowlisted | PASS |
| Unknown/forbidden surfaces fail closed | PASS |
| All proposed changes constraint-validated | PASS |
| Bounds enforcement | PASS |
| Max-delta enforcement | PASS |
| Type validation | PASS |
| Model pointer allowlist enforced | PASS |
| Tool/file scope expansion forbidden | PASS |
| Safety rule relaxation forbidden | PASS |
| Cooldown policy enforced | PASS |
| Sample size policy enforced | PASS |
| All tests deterministic (run twice identical) | PASS |
| Proposal-only (no activation in Phase 3) | PASS |

## Phase 3 Implementation Summary

**Wave 3.1 — Config Surface Allowlist + Constraint Enforcement:**
- Exhaustive allowlisted tunables with frozen dataclass constraints
- L0 routing thresholds (float): escalation_threshold, anomaly_routing_threshold
- L0 routing int: depth_breaker
- RAG parameters (int): retrieval_top_k, rerank_top_n
- L1 model pointers (allowlist): cognition_model, embedding_model
- L5 policy tunables (int): token_budget, max_k, max_retries
- Forbidden surfaces: tool_allowlist, file_scope_whitelist, guardian_contracts, etc.
- Delta enforcer with pure validation functions (fail-closed)

**Wave 3.3 — Dampening Guards:**
- CooldownPolicy: minimum seconds between updates
- SampleSizePolicy: minimum observations before retraining
- Pure validation functions with injected timestamps (no wall-clock)
- Deterministic behavior across all validators

**Key Invariants:**
- Zero execution authority preserved
- No activation pointer updates in Phase 3
- All constraints are immutable (frozen dataclasses)
- All validation is deterministic and side-effect free
- Fail-closed on any constraint violation
- No wall-clock, randomness, or environment access

---

## Phase 3 Remediation — Wave 3.2 Completion

### Remediation Commit Hash

```
fe5a56a4e7010eb03b3060774bb695f14cceb018
```

### Remediation File List (git diff --name-only HEAD~1..HEAD)

```
system_learning/engines/l0_threshold_tuner.py
system_learning/engines/rag_optimizer.py
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py
tests/unit_min_deps/system_learning/test_rag_optimizer.py
```

4 files changed, 756 insertions(+)

### Remediation pytest -q (Run 1)

```
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_valid_proposal_passes_constraints PASSED
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_out_of_range_rejected PASSED
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_over_delta_rejected PASSED
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_cooldown_violated_returns_none PASSED
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_sample_size_violated_returns_none PASSED
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdTuner::test_no_change_needed_returns_none PASSED
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdChangePackage::test_canonical_bytes_deterministic PASSED
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdChangePackage::test_content_hash_deterministic PASSED
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestL0ThresholdChangePackage::test_different_values_produce_different_hash PASSED
tests/unit_min_deps/system_learning/test_l0_threshold_tuner.py::TestDeterminism::test_proposal_deterministic PASSED
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_valid_proposal_passes_constraints PASSED
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_out_of_range_rejected PASSED
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_cooldown_violated_returns_none PASSED
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_sample_size_violated_returns_none PASSED
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGOptimizer::test_no_change_needed_returns_none PASSED
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGChangePackage::test_canonical_bytes_deterministic PASSED
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGChangePackage::test_content_hash_deterministic PASSED
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestRAGChangePackage::test_different_values_produce_different_hash PASSED
tests/unit_min_deps/system_learning/test_rag_optimizer.py::TestDeterminism::test_proposal_deterministic PASSED

19 passed in 0.05s
```

### Remediation pytest -q (Run 2 — Determinism Proof)

```
19 passed in 0.04s
```

Identical result. All 19 tests pass on both runs.

### Existence Proof (rg output)

```
c:\Git\Agentic-Workflow\system_learning\engines\l0_threshold_tuner.py:
  - propose_l0_threshold_changes (line 71)

c:\Git\Agentic-Workflow\system_learning\engines\rag_optimizer.py:
  - propose_rag_param_changes (line 71)
```

### Determinism Assertion Snippet (from test_l0_threshold_tuner.py, lines 163-184)

```python
class TestDeterminism:
    def test_proposal_deterministic(self):
        """Identical inputs produce identical proposals."""
        cooldown = CooldownPolicy(min_seconds_between_updates=3600)
        sample = SampleSizePolicy(min_observations=1000)

        proposal1 = propose_l0_threshold_changes(
            snapshot_id="snap123",
            metrics={"escalation_rate": 0.25},
            current_config={"escalation_threshold": 0.80},
            now_utc=1700003600,
            history={
                "escalation_threshold_last_update": 1700000000,
                "escalation_threshold_n_obs": 1500,
            },
            cooldown_policy=cooldown,
            sample_policy=sample,
        )

        proposal2 = propose_l0_threshold_changes(
            # ... identical inputs ...
        )

        assert proposal1 is not None
        assert proposal2 is not None
        assert proposal1.content_hash() == proposal2.content_hash()
```

### Wave 3.2 Implementation Summary

**L0 Threshold Tuner:**
- Proposal-only engine for L0 routing threshold optimization
- Enforces allowlist, bounds, max-delta via constraint validators
- Enforces cooldown + sample-size via dampening policies
- Deterministic inputs only (now_utc injected, no wall-clock)
- Returns immutable L0ThresholdChangePackage with canonical_bytes() and content_hash()

**RAG Optimizer:**
- Proposal-only engine for RAG parameter optimization
- Enforces allowlist, bounds, max-delta via constraint validators
- Enforces cooldown + sample-size via dampening policies
- Deterministic inputs only (now_utc injected, no wall-clock)
- Returns immutable RAGChangePackage with canonical_bytes() and content_hash()

**Coverage:**
- Valid proposals pass constraints ✓
- Out-of-range proposals capped at bounds ✓
- Cooldown violations return None (no proposal) ✓
- Sample-size violations return None (no proposal) ✓
- Deterministic: identical inputs → identical content_hash ✓
- No activation pointer updates (proposal-only) ✓
