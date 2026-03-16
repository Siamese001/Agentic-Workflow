"""Unit tests for ResourcePredictor - deterministic, bounded resource predictions."""

import pytest

from agentic_core.L2_execution.engines.resource_predictor import (
    DefaultDeterministicResourcePredictor,
)
from agentic_core.L2_execution.types.resource_prediction_types import (
    FailureSignature,
    ResourceEnvelope,
    ResourcePrediction,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_resource_predictor")
_emit_applies_guardrail("p0", "test_resource_predictor", "p0_governance")
_emit_reads_policy_state("p0", "test_resource_predictor", "policy_binding")
_emit_snapshots_state("p0", "test_resource_predictor", "state_snapshot")
emit_replay_key("p0", "test_resource_predictor")
emit_determinism_digest("p0", "test_resource_predictor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestResourcePredictor:
    """Test suite for ResourcePredictor deterministic behavior."""

    def test_determinism_same_input_same_hash(self):
        """Same inputs must produce identical outputs and hashes."""
        predictor = DefaultDeterministicResourcePredictor()

        signature = FailureSignature(
            component="test_component",
            failure_type="timeout",
            fingerprint="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        )

        # Run prediction twice
        prediction1 = predictor.predict(signature=signature, history_bytes=None)
        prediction2 = predictor.predict(signature=signature, history_bytes=None)

        # Must be identical
        assert prediction1.content_hash() == prediction2.content_hash()
        assert prediction1.envelope == prediction2.envelope
        assert prediction1.confidence == prediction2.confidence
        assert prediction1.reasons == prediction2.reasons

    def test_bounded_clamping(self):
        """Resource envelopes must be clamped to configured bounds."""
        # Test with very tight bounds
        predictor = DefaultDeterministicResourcePredictor(
            min_cpu_cores=2,
            max_cpu_cores=4,
            min_memory_mb=1024,
            max_memory_mb=2048,
            min_timeout_s=60,
            max_timeout_s=300,
        )

        signature = FailureSignature(
            component="test",
            failure_type="unknown",  # Uses baseline envelope
            fingerprint="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        )

        prediction = predictor.predict(signature=signature, history_bytes=None)

        # Must be within bounds
        assert 2 <= prediction.envelope.cpu_cores <= 4
        assert 1024 <= prediction.envelope.memory_mb <= 2048
        assert 60 <= prediction.envelope.timeout_s <= 300

    def test_history_influence_deterministic(self):
        """History must influence predictions deterministically."""
        predictor = DefaultDeterministicResourcePredictor()

        signature = FailureSignature(
            component="test",
            failure_type="memory_error",
            fingerprint="fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
        )

        # Different history should produce different results than no history
        history1 = b"sample_history_data_1"

        prediction1 = predictor.predict(signature=signature, history_bytes=history1)
        prediction_no_history = predictor.predict(signature=signature, history_bytes=None)

        # Should be different when history is provided vs no history
        assert prediction1.content_hash() != prediction_no_history.content_hash()

        # History should increase confidence
        assert prediction1.confidence > prediction_no_history.confidence

        # Different history content should still be processed (even if result same due to deterministic hash)
        history2 = b"sample_history_data_2"
        prediction2 = predictor.predict(signature=signature, history_bytes=history2)

        # At minimum, history processing should work without errors
        assert prediction2 is not None
        assert prediction2.confidence > prediction_no_history.confidence

    def test_permutation_invariant_healing_inputs(self):
        """Permutation invariance test for healing inputs."""
        predictor = DefaultDeterministicResourcePredictor()

        # Same signature with different object construction should be identical
        signature1 = FailureSignature(
            component="component_a",
            failure_type="cpu_error",
            fingerprint="1111111111111111111111111111111111111111111111111111111111111111",
        )

        signature2 = FailureSignature(
            failure_type="cpu_error",  # Different order
            fingerprint="1111111111111111111111111111111111111111111111111111111111111111",
            component="component_a",
        )

        prediction1 = predictor.predict(signature=signature1, history_bytes=None)
        prediction2 = predictor.predict(signature=signature2, history_bytes=None)

        # Must be identical despite construction order
        assert prediction1.content_hash() == prediction2.content_hash()
        assert prediction1.envelope == prediction2.envelope

    def test_failure_type_baseline_envelopes(self):
        """Different failure types should use appropriate baseline envelopes."""
        predictor = DefaultDeterministicResourcePredictor()

        failure_types = ["timeout", "memory_error", "cpu_error", "io_error", "network_error", "unknown"]

        predictions = {}
        for failure_type in failure_types:
            signature = FailureSignature(
                component="test",
                failure_type=failure_type,
                fingerprint=f"{failure_type}_fingerprint_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            )
            prediction = predictor.predict(signature=signature, history_bytes=None)
            predictions[failure_type] = prediction

        # Should have different envelopes for different failure types
        timeout_env = predictions["timeout"].envelope
        memory_env = predictions["memory_error"].envelope
        cpu_env = predictions["cpu_error"].envelope

        # Memory errors should suggest more memory
        assert memory_env.memory_mb > timeout_env.memory_mb
        # CPU errors should suggest more CPU
        assert cpu_env.cpu_cores > timeout_env.cpu_cores

    def test_canonical_bytes_stability(self):
        """canonical_bytes() must be stable and ASCII-only."""
        signature = FailureSignature(
            component="test",
            failure_type="timeout",
            fingerprint="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        )

        envelope = ResourceEnvelope(cpu_cores=2, memory_mb=1024, timeout_s=300)

        prediction = ResourcePrediction(
            signature=signature,
            envelope=envelope,
            confidence=0.8,
            reasons=("test_reason", "another_reason"),
        )

        canonical = prediction.canonical_bytes()

        # Must be bytes
        assert isinstance(canonical, bytes)

        # Must be ASCII-only
        try:
            canonical.decode("ascii")
        except UnicodeDecodeError:
            pytest.fail("canonical_bytes() must be ASCII-only")

        # Must be stable across calls
        assert canonical == prediction.canonical_bytes()

    def test_confidence_bounds(self):
        """Confidence must always be within [0.0, 1.0]."""
        predictor = DefaultDeterministicResourcePredictor()

        signature = FailureSignature(
            component="test",
            failure_type="unknown",
            fingerprint="9999999999999999999999999999999999999999999999999999999999999999",
        )

        # Test with various scenarios
        scenarios = [
            None,  # No history
            b"short_history",
            b"very_long_history_data_" * 100,  # Long history
        ]

        for history in scenarios:
            prediction = predictor.predict(signature=signature, history_bytes=history)
            assert 0.0 <= prediction.confidence <= 1.0
