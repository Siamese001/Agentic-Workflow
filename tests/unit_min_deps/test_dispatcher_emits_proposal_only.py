"""Unit tests for L2 execution dispatcher proposal-only emission."""

from unittest.mock import patch

import pytest

from agentic_core.L2_execution.engines.resource_predictor import DefaultDeterministicResourcePredictor
from agentic_core.L2_execution.engines.rollback_refiner import DefaultDeterministicRollbackRefiner
from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing
from agentic_core.L2_execution.healers.healing_tier_types import HealingInput

pytestmark = pytest.mark.unit_min_deps


class TestDispatcherEmitsProposalOnly:
    """Test that dispatcher emits proposals without runtime mutation."""

    def test_resource_predictor_emission(self):
        """Dispatcher should emit resource prediction as proposal-only."""
        # Setup
        config = HealingTierConfig(
            heal_confidence_x=0.8,
            heal_confidence_y=0.5,
            max_heal_retries=3,
            model_qwen_vllm_id="test-model",
            model_gemini_2_5_pro_id="test-gemini",
        )

        healing_input = HealingInput(
            failure_type="timeout",
            error_signature="test_error_signature",
            retry_count=1,
            blast_radius_estimate=0.5,
            trace_id="test-trace-123",
            required_tools=(),
            violation_metadata_refs=(),
        )

        resource_predictor = DefaultDeterministicResourcePredictor()

        # Mock logger to capture emission
        with patch("agentic_core.L2_execution.healers.healing_tier_dispatcher.logger") as mock_logger:
            # Dispatch with resource predictor
            decision, record = dispatch_healing(
                healing_input=healing_input,
                config=config,
                agent_name="test_agent",
                timestamp_utc=1234567890,
                resource_predictor=resource_predictor,
                rollback_refiner=None,
            )

            # Should have logged resource prediction emission
            mock_logger.info.assert_called()

            # Check the call arguments for resource prediction
            calls = mock_logger.info.call_args_list
            resource_call = None
            for call in calls:
                if "Resource prediction emitted" in str(call):
                    resource_call = call
                    break

            assert resource_call is not None
            assert "test-trace-123" in str(resource_call)
            assert "test_agent" in str(resource_call)

    def test_rollback_refiner_emission(self):
        """Dispatcher should emit rollback refinement as proposal-only."""
        # Setup
        config = HealingTierConfig(
            heal_confidence_x=0.8,
            heal_confidence_y=0.5,
            max_heal_retries=3,
            model_qwen_vllm_id="test-model",
            model_gemini_2_5_pro_id="test-gemini",
        )

        healing_input = HealingInput(
            failure_type="memory_error",
            error_signature="test_memory_error",
            retry_count=2,
            blast_radius_estimate=0.7,
            trace_id="test-trace-456",
            required_tools=(),
            violation_metadata_refs=(),
        )

        rollback_refiner = DefaultDeterministicRollbackRefiner()

        # Mock logger to capture emission
        with patch("agentic_core.L2_execution.healers.healing_tier_dispatcher.logger") as mock_logger:
            # Dispatch with rollback refiner
            decision, record = dispatch_healing(
                healing_input=healing_input,
                config=config,
                agent_name="test_agent",
                timestamp_utc=1234567890,
                resource_predictor=None,
                rollback_refiner=rollback_refiner,
            )

            # Should have logged rollback refinement emission
            mock_logger.info.assert_called()

            # Check the call arguments for rollback refinement
            calls = mock_logger.info.call_args_list
            rollback_call = None
            for call in calls:
                if "Rollback refinement emitted" in str(call):
                    rollback_call = call
                    break

            assert rollback_call is not None
            assert "test-trace-456" in str(rollback_call)
            assert "test_agent" in str(rollback_call)

    def test_both_emissions(self):
        """Dispatcher should emit both resource prediction and rollback refinement."""
        # Setup
        config = HealingTierConfig(
            heal_confidence_x=0.8,
            heal_confidence_y=0.5,
            max_heal_retries=3,
            model_qwen_vllm_id="test-model",
            model_gemini_2_5_pro_id="test-gemini",
        )

        healing_input = HealingInput(
            failure_type="cpu_error",
            error_signature="test_cpu_error",
            retry_count=0,
            blast_radius_estimate=0.3,
            trace_id="test-trace-789",
            required_tools=(),
            violation_metadata_refs=(),
        )

        resource_predictor = DefaultDeterministicResourcePredictor()
        rollback_refiner = DefaultDeterministicRollbackRefiner()

        # Mock logger to capture emissions
        with patch("agentic_core.L2_execution.healers.healing_tier_dispatcher.logger") as mock_logger:
            # Dispatch with both predictors
            decision, record = dispatch_healing(
                healing_input=healing_input,
                config=config,
                agent_name="test_agent",
                timestamp_utc=1234567890,
                resource_predictor=resource_predictor,
                rollback_refiner=rollback_refiner,
            )

            # Should have logged both emissions
            assert mock_logger.info.call_count >= 2

            # Check for both types of emissions
            calls = [str(call) for call in mock_logger.info.call_args_list]

            resource_emitted = any("Resource prediction emitted" in call for call in calls)
            rollback_emitted = any("Rollback refinement emitted" in call for call in calls)

            assert resource_emitted
            assert rollback_emitted

    def test_no_runtime_config_mutation(self):
        """Dispatcher should not mutate runtime config directly."""
        # Setup
        config = HealingTierConfig(
            heal_confidence_x=0.8,
            heal_confidence_y=0.5,
            max_heal_retries=3,
            model_qwen_vllm_id="test-model",
            model_gemini_2_5_pro_id="test-gemini",
        )

        healing_input = HealingInput(
            failure_type="network_error",
            error_signature="test_network_error",
            retry_count=1,
            blast_radius_estimate=0.4,
            trace_id="test-trace-no-mutation",
            required_tools=(),
            violation_metadata_refs=(),
        )

        resource_predictor = DefaultDeterministicResourcePredictor()
        rollback_refiner = DefaultDeterministicRollbackRefiner()

        # Capture original config
        original_config_str = str(config)

        # Dispatch
        decision, record = dispatch_healing(
            healing_input=healing_input,
            config=config,
            agent_name="test_agent",
            timestamp_utc=1234567890,
            resource_predictor=resource_predictor,
            rollback_refiner=rollback_refiner,
        )

        # Config should be unchanged
        assert str(config) == original_config_str

    def test_emission_failure_swallowed(self):
        """Dispatcher should swallow emission failures and continue healing."""
        # Setup
        config = HealingTierConfig(
            heal_confidence_x=0.8,
            heal_confidence_y=0.5,
            max_heal_retries=3,
            model_qwen_vllm_id="test-model",
            model_gemini_2_5_pro_id="test-gemini",
        )

        healing_input = HealingInput(
            failure_type="io_error",
            error_signature="test_io_error",
            retry_count=1,
            blast_radius_estimate=0.6,
            trace_id="test-trace-failure",
            required_tools=(),
            violation_metadata_refs=(),
        )

        # Create a failing predictor
        class FailingPredictor:
            def predict(self, *, signature, history_bytes=None):
                raise RuntimeError("Prediction failed")

        resource_predictor = FailingPredictor()

        # Mock logger to verify debug logging
        with patch("agentic_core.L2_execution.healers.healing_tier_dispatcher.logger") as mock_logger:
            # Dispatch should not crash despite prediction failure
            decision, record = dispatch_healing(
                healing_input=healing_input,
                config=config,
                agent_name="test_agent",
                timestamp_utc=1234567890,
                resource_predictor=resource_predictor,
                rollback_refiner=None,
            )

            # Should still get a valid healing decision and record
            assert decision is not None
            assert record is not None

            # Should have logged the failure at debug level
            mock_logger.debug.assert_called()
            debug_calls = [str(call) for call in mock_logger.debug.call_args_list]
            failure_logged = any("resource prediction failed" in call for call in debug_calls)
            assert failure_logged

    def test_deterministic_failure_signature(self):
        """Failure signatures should be deterministic for same inputs."""
        # Setup
        config = HealingTierConfig(
            heal_confidence_x=0.8,
            heal_confidence_y=0.5,
            max_heal_retries=3,
            model_qwen_vllm_id="test-model",
            model_gemini_2_5_pro_id="test-gemini",
        )

        healing_input = HealingInput(
            failure_type="timeout",
            error_signature="deterministic_test",
            retry_count=1,
            blast_radius_estimate=0.5,
            trace_id="deterministic-trace-123",
            required_tools=(),
            violation_metadata_refs=(),
        )

        resource_predictor = DefaultDeterministicResourcePredictor()

        # Mock to capture prediction calls
        predictions = []

        def capture_predict(*, signature, history_bytes=None):
            predictions.append(signature)
            # Return a minimal prediction
            from agentic_core.L2_execution.types.resource_prediction_types import (
                ResourceEnvelope,
                ResourcePrediction,
            )

            envelope = ResourceEnvelope(cpu_cores=2, memory_mb=1024, timeout_s=300)
            return ResourcePrediction(
                signature=signature,
                envelope=envelope,
                confidence=0.8,
                reasons=("test",),
            )

        resource_predictor.predict = capture_predict

        # Dispatch twice with same inputs
        dispatch_healing(
            healing_input=healing_input,
            config=config,
            agent_name="test_agent",
            timestamp_utc=1234567890,
            resource_predictor=resource_predictor,
            rollback_refiner=None,
        )

        dispatch_healing(
            healing_input=healing_input,
            config=config,
            agent_name="test_agent",
            timestamp_utc=1234567890,
            resource_predictor=resource_predictor,
            rollback_refiner=None,
        )

        # Should have generated identical signatures
        assert len(predictions) == 2
        assert predictions[0].content_hash() == predictions[1].content_hash()
        assert predictions[0].fingerprint == predictions[1].fingerprint
