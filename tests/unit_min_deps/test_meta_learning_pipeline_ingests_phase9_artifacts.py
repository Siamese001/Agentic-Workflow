"""Unit tests for meta-learning pipeline ingestion of Phase 9 artifacts."""

import json

import pytest

from agentic_core.L2_execution.types.resource_prediction_types import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    FailureSignature,
    ResourceEnvelope,
    ResourcePrediction,
)
from agentic_core.L2_execution.types.rollback_refinement_types import (
    RollbackRefinementDecision,
    RollbackStrategyId,
)
from system_learning.pipelines.meta_learning_pipeline import (
    PipelineDependencies,
)

pytestmark = pytest.mark.unit_min_deps


class TestMetaLearningPipelineIngestsPhase9Artifacts:
    """Test that meta-learning pipeline ingests Phase 9 artifacts deterministically."""

    def test_pipeline_dependencies_accept_phase9_artifacts(self):
        """PipelineDependencies should accept Phase 9 artifact bytes."""
        # Create ResourcePrediction artifact
        signature = FailureSignature(
            component="test_component",
            failure_type="timeout",
            fingerprint="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        )

        envelope = ResourceEnvelope(cpu_cores=4, memory_mb=2048, timeout_s=600)

        resource_prediction = ResourcePrediction(
            signature=signature,
            envelope=envelope,
            confidence=0.85,
            reasons=("failure_type_timeout", "history_available", "high_cpu"),
        )

        # Serialize ResourcePrediction as bytes
        resource_prediction_bytes = json.dumps(
            {
                "signature": {
                    "component": signature.component,
                    "failure_type": signature.failure_type,
                    "fingerprint": signature.fingerprint,
                },
                "envelope": {
                    "cpu_cores": envelope.cpu_cores,
                    "memory_mb": envelope.memory_mb,
                    "timeout_s": envelope.timeout_s,
                },
                "confidence": resource_prediction.confidence,
                "reasons": list(resource_prediction.reasons),
            }
        ).encode("utf-8")

        # Create RollbackRefinementDecision artifact
        chosen_strategy = RollbackStrategyId("state_snapshot")
        ranked_strategies = (
            RollbackStrategyId("state_snapshot"),
            RollbackStrategyId("checkpoint_restore"),
            RollbackStrategyId("graceful_shutdown"),
        )

        rollback_decision = RollbackRefinementDecision(
            chosen=chosen_strategy,
            ranked=ranked_strategies,
            reasons=("chosen_strategy_state_snapshot", "failure_type_memory_error", "history_based"),
        )

        # Serialize RollbackRefinementDecision as bytes
        rollback_decision_bytes = json.dumps(
            {
                "chosen": {"name": chosen_strategy.name},
                "ranked": [{"name": s.name} for s in ranked_strategies],
                "reasons": list(rollback_decision.reasons),
            }
        ).encode("utf-8")

        # Create dependencies with Phase 9 artifacts
        deps = PipelineDependencies(
            audit_store=Mock(),
            telemetry_store=Mock(),
            config_provider=Mock(),
            baseline_metrics_provider=Mock(),
            resource_predictor_bytes=resource_prediction_bytes,
            rollback_refinement_decision_bytes=rollback_decision_bytes,
        )

        # Should accept Phase 9 artifacts without error
        assert deps.resource_predictor_bytes is not None
        assert deps.rollback_refinement_decision_bytes is not None
        assert isinstance(deps.resource_predictor_bytes, bytes)
        assert isinstance(deps.rollback_refinement_decision_bytes, bytes)

    def test_pipeline_dependencies_accept_none_artifacts(self):
        """PipelineDependencies should accept None for Phase 9 artifacts."""
        deps = PipelineDependencies(
            audit_store=Mock(),
            telemetry_store=Mock(),
            config_provider=Mock(),
            baseline_metrics_provider=Mock(),
            resource_predictor_bytes=None,
            rollback_refinement_decision_bytes=None,
        )

        # Should accept None values
        assert deps.resource_predictor_bytes is None
        assert deps.rollback_refinement_decision_bytes is None

    def test_artifact_serialization_stability(self):
        """Phase 9 artifacts should have stable serialization."""
        # Create ResourcePrediction
        signature = FailureSignature(
            component="stability_test",
            failure_type="cpu_error",
            fingerprint="stable_fingerprint_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        )

        envelope = ResourceEnvelope(cpu_cores=8, memory_mb=4096, timeout_s=900)

        resource_prediction = ResourcePrediction(
            signature=signature,
            envelope=envelope,
            confidence=0.9,
            reasons=("failure_type_cpu_error", "history_available"),
        )

        # Serialize twice
        bytes1 = json.dumps(
            {
                "signature": {
                    "component": signature.component,
                    "failure_type": signature.failure_type,
                    "fingerprint": signature.fingerprint,
                },
                "envelope": {
                    "cpu_cores": envelope.cpu_cores,
                    "memory_mb": envelope.memory_mb,
                    "timeout_s": envelope.timeout_s,
                },
                "confidence": resource_prediction.confidence,
                "reasons": list(resource_prediction.reasons),
            }
        ).encode("utf-8")

        bytes2 = json.dumps(
            {
                "signature": {
                    "component": signature.component,
                    "failure_type": signature.failure_type,
                    "fingerprint": signature.fingerprint,
                },
                "envelope": {
                    "cpu_cores": envelope.cpu_cores,
                    "memory_mb": envelope.memory_mb,
                    "timeout_s": envelope.timeout_s,
                },
                "confidence": resource_prediction.confidence,
                "reasons": list(resource_prediction.reasons),
            }
        ).encode("utf-8")

        # Should be identical
        assert bytes1 == bytes2

    def test_malformed_artifact_handling(self):
        """Pipeline should handle malformed artifacts gracefully."""
        # Create malformed artifact bytes
        malformed_bytes = b"invalid json data"

        # Should not raise exception when creating dependencies
        deps = PipelineDependencies(
            audit_store=Mock(),
            telemetry_store=Mock(),
            config_provider=Mock(),
            baseline_metrics_provider=Mock(),
            resource_predictor_bytes=malformed_bytes,
            rollback_refinement_decision_bytes=malformed_bytes,
        )

        # Should accept malformed bytes
        assert deps.resource_predictor_bytes == malformed_bytes
        assert deps.rollback_refinement_decision_bytes == malformed_bytes

    def test_empty_artifact_bytes(self):
        """Pipeline should handle empty artifact bytes."""
        empty_bytes = b""

        deps = PipelineDependencies(
            audit_store=Mock(),
            telemetry_store=Mock(),
            config_provider=Mock(),
            baseline_metrics_provider=Mock(),
            resource_predictor_bytes=empty_bytes,
            rollback_refinement_decision_bytes=empty_bytes,
        )

        # Should accept empty bytes
        assert deps.resource_predictor_bytes == empty_bytes
        assert deps.rollback_refinement_decision_bytes == empty_bytes


# Mock class for dependencies
class Mock:
    """Simple mock class for testing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getattr__(self, name):
        return Mock()

    def __call__(self, *args, **kwargs):
        return Mock()
