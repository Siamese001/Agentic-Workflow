"""Unit tests for L2 execution dispatcher proposal-only emission."""

from unittest.mock import patch

import pytest

from agentic_core.L2_execution.engines.resource_predictor import DefaultDeterministicResourcePredictor
from agentic_core.L2_execution.engines.rollback_refiner import DefaultDeterministicRollbackRefiner
from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_dispatcher import dispatch_healing
from agentic_core.L2_execution.healers.healing_tier_types import HealingInput
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_dispatcher_emits_proposal_only")
# REMOVED: _emit_applies_guardrail("p0", "test_dispatcher_emits_proposal_only", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_dispatcher_emits_proposal_only", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_dispatcher_emits_proposal_only", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_dispatcher_emits_proposal_only", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_dispatcher_emits_proposal_only", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_dispatcher_emits_proposal_only", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_dispatcher_emits_proposal_only", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_dispatcher_emits_proposal_only", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_dispatcher_emits_proposal_only", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_dispatcher_emits_proposal_only", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_dispatcher_emits_proposal_only", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_dispatcher_emits_proposal_only", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_dispatcher_emits_proposal_only", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_dispatcher_emits_proposal_only", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_dispatcher_emits_proposal_only", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_dispatcher_emits_proposal_only", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_dispatcher_emits_proposal_only", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_dispatcher_emits_proposal_only", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_dispatcher_emits_proposal_only", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_dispatcher_emits_proposal_only", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_dispatcher_emits_proposal_only", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_dispatcher_emits_proposal_only", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_dispatcher_emits_proposal_only", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_dispatcher_emits_proposal_only", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_dispatcher_emits_proposal_only", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_dispatcher_emits_proposal_only", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_dispatcher_emits_proposal_only", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_dispatcher_emits_proposal_only", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_dispatcher_emits_proposal_only", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_dispatcher_emits_proposal_only", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_dispatcher_emits_proposal_only", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_dispatcher_emits_proposal_only", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_dispatcher_emits_proposal_only", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_dispatcher_emits_proposal_only", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_dispatcher_emits_proposal_only", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_dispatcher_emits_proposal_only", "write_through")
# REMOVED: _emit_writes_through("p1", "test_dispatcher_emits_proposal_only", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_dispatcher_emits_proposal_only", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_dispatcher_emits_proposal_only", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_dispatcher_emits_proposal_only", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_dispatcher_emits_proposal_only", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_dispatcher_emits_proposal_only", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_dispatcher_emits_proposal_only", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_dispatcher_emits_proposal_only", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_dispatcher_emits_proposal_only", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_dispatcher_emits_proposal_only", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_dispatcher_emits_proposal_only", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_dispatcher_emits_proposal_only", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_dispatcher_emits_proposal_only", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_dispatcher_emits_proposal_only", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_dispatcher_emits_proposal_only", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_dispatcher_emits_proposal_only")
# REMOVED: _emit_gated_by_confidence("p1", "test_dispatcher_emits_proposal_only", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_dispatcher_emits_proposal_only")
# REMOVED: emit_determinism_digest("p0", "test_dispatcher_emits_proposal_only")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_dispatcher_emits_proposal_only", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_dispatcher_emits_proposal_only", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_dispatcher_emits_proposal_only", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_dispatcher_emits_proposal_only", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_dispatcher_emits_proposal_only", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_dispatcher_emits_proposal_only", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_dispatcher_emits_proposal_only", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_dispatcher_emits_proposal_only", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_dispatcher_emits_proposal_only", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_dispatcher_emits_proposal_only", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_dispatcher_emits_proposal_only", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_dispatcher_emits_proposal_only", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_dispatcher_emits_proposal_only", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_dispatcher_emits_proposal_only", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_dispatcher_emits_proposal_only", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_dispatcher_emits_proposal_only", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_dispatcher_emits_proposal_only", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_dispatcher_emits_proposal_only", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_dispatcher_emits_proposal_only", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_dispatcher_emits_proposal_only", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
    """Test no_runtime_config_mutation runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute no_runtime_config_mutation
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
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
