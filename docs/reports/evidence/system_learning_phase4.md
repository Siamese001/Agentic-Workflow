# System Learning Phase 4 — Evidence File

## 1. Commit Hash

```
d014b600d40950da8473d65db3e9eb21047af49e
```

## 2. File List (git diff --name-only HEAD~1..HEAD)

```
system_learning/validators/oscillation_detector.py
system_learning/validators/replay_validator.py
system_learning/validators/shadow_evaluator.py
tests/unit_min_deps/system_learning/test_oscillation_detector.py
tests/unit_min_deps/system_learning/test_replay_validator.py
tests/unit_min_deps/system_learning/test_shadow_evaluator.py
```

6 files changed, 908 insertions(+)

## 3. pytest -q (Run 1)

```
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_deterministic_engine_passes PASSED
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_nondeterministic_engine_fails PASSED
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_error_includes_both_hashes PASSED
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_same_output_twice_produces_same_hash PASSED
tests/unit_min_deps/system_learning/test_replay_validator.py::TestReplayValidator::test_different_snapshots_produce_different_hashes PASSED
tests/unit_min_deps/system_learning/test_replay_validator.py::TestDeterminism::test_replay_validate_deterministic PASSED
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_pass_within_thresholds PASSED
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_latency_regression PASSED
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_error_rate_regression PASSED
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_safety_violation_increase PASSED
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_cpu_regression PASSED
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_fail_mem_regression PASSED
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestShadowEvaluator::test_multiple_violations_reported PASSED
tests/unit_min_deps/system_learning/test_shadow_evaluator.py::TestDeterminism::test_evaluate_shadow_deterministic PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_oscillation_true_pattern PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_oscillation_true_pattern_reverse PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_non_oscillation_pattern PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_non_oscillation_all_same PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_insufficient_data PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_oscillation_with_epsilon_tolerance PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDetectOscillation::test_non_oscillation_three_values PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_freeze_decision_on_oscillation PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_no_freeze_on_non_oscillation PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_freeze_until_utc_computation PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestComputeFreezeDecision::test_freeze_decision_deterministic PASSED
tests/unit_min_deps/system_learning/test_oscillation_detector.py::TestDeterminism::test_detect_oscillation_deterministic PASSED

26 passed in 0.06s
```

## 4. pytest -q (Run 2 — Determinism Proof)

```
26 passed in 0.04s
```

Identical result. All 26 tests pass on both runs.

## 5. Replay Validator Determinism Assertion (from test_replay_validator.py, lines 82-97)

```python
class TestDeterminism:
    def test_replay_validate_deterministic(self):
        """replay_validate itself is deterministic."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2, "extra": "data"}

        def canonicalize(output):
            # Canonical: sorted items
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 42}

        # Run replay_validate multiple times
        hash1 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)
        hash2 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)
        hash3 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)

        assert hash1 == hash2 == hash3
```

## Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| All validators deterministic, injected-input only | PASS |
| No activation pointer updates or store commits | PASS |
| All tests pass twice identically | PASS |
| Replay validator enforces determinism | PASS |
| Shadow evaluator fail-closed on regression | PASS |
| Oscillation detector with freeze decision | PASS |
| No wall-clock/randomness/env access | PASS |
| No cross-layer imports | PASS |

## Phase 4 Implementation Summary

**Wave 4.1 — Deterministic Replay Validator:**
- `replay_validate(snapshot, engine_fn, *, canonicalize_fn) -> str`
- Runs engine twice with same input, compares SHA-256 hashes
- Raises `DeterminismViolation` if hashes differ (includes both hashes in error)
- Returns hash if identical
- No randomness/time/env access
- Engine function and canonicalizer are injected

**Wave 4.2 — Shadow Mode Evaluator (Pure Comparator):**
- `ShadowMetrics`: p95_latency_ms, error_rate, safety_violation_count, cpu_pct, mem_mb
- `ShadowThresholds`: max regression percentages and absolute limits
- `evaluate_shadow(production, shadow, thresholds) -> None`
- Fail-closed with `ShadowRegression` on any threshold violation
- Deterministic comparisons only (no floating drift)
- No environment access; metrics are inputs

**Wave 4.3 — Oscillation Detector + Dampening Hook:**
- `OscillationPolicy`: window (5), epsilon, freeze_seconds
- `detect_oscillation(values, policy) -> bool`
  - Detects alternating pattern in last N values
  - Deterministic pattern check
- `FreezeDecision`: should_freeze, freeze_until_utc
- `compute_freeze_decision(values, last_update_utc, now_utc, policy) -> FreezeDecision`
  - If oscillation: freeze_until_utc = now_utc + freeze_seconds
  - No wall clock; now_utc injected

**Coverage:**
- Determinism pass case (same output twice) ✓
- Fail case (different outputs across calls) ✓
- Error includes both hashes ✓
- Pass within thresholds ✓
- Fail latency regression ✓
- Fail error rate regression ✓
- Fail safety violation increase ✓
- Fail CPU regression ✓
- Fail memory regression ✓
- Oscillation true pattern ✓
- Non-oscillation pattern ✓
- Freeze decision computes expected freeze_until_utc ✓

**Key Invariants:**
- Zero execution authority preserved
- No activation pointer updates in Phase 4
- All validators are deterministic and side-effect free
- Fail-closed on any violation
- No wall-clock, randomness, or environment access
- Proposal/validation-only (no store commits)
