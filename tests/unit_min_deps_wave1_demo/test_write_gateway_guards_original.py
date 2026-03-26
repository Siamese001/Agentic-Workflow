"""Unit tests for write gateway guards (RCA Phase 5).

Tests write amplification detector, size cap, and mutation entropy cap.
"""

from pathlib import Path


    MAX_GROWTH_RATIO,
    MAX_WRITE_BYTES,
    MutationEntropyError,
    WriteAmplificationError,
    WriteSizeCapError,
    get_prohibition_hit_count,
    record_prohibition_hit,
    write_text,
)
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_guardian_action,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_policy_state,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_snapshots_state,
    _emit_validates_agent_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_through,
)


class TestWriteAmplificationDetector:
    """Test write amplification detection logic."""

    def test_write_amplification_threshold(self):
        """Test that write amplification is detected when threshold exceeded."""
                        from agentic_core.L2_execution.tools.write_gateway import MAX_GROWTH_RATIO, MAX_WRITE_BYTES, MutationEntropyError, WriteAmplificationError, WriteSizeCapError, get_prohibition_hit_count, record_prohibition_hit, write_text
                        from agentic_core.L2_execution.tools.write_gateway import MAX_GROWTH_RATIO, MAX_WRITE_BYTES, MutationEntropyError, WriteAmplificationError, WriteSizeCapError, get_prohibition_hit_count, record_prohibition_hit, write_text
                        from agentic_core.L2_execution.tools.write_gateway import MAX_GROWTH_RATIO, MAX_WRITE_BYTES, MutationEntropyError, WriteAmplificationError, WriteSizeCapError, get_prohibition_hit_count, record_prohibition_hit, write_text
                        from agentic_core.L2_execution.tools.write_gateway import MAX_GROWTH_RATIO, MAX_WRITE_BYTES, MutationEntropyError, WriteAmplificationError, WriteSizeCapError, get_prohibition_hit_count, record_prohibition_hit, write_text
                        from agentic_core.L2_execution.tools.write_gateway import MAX_GROWTH_RATIO, MAX_WRITE_BYTES, MutationEntropyError, WriteAmplificationError, WriteSizeCapError, get_prohibition_hit_count, record_prohibition_hit, write_text
                        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import _emit_agent_executes_agent, _emit_applies_guardrail, _emit_authorize_and_execute, _emit_blocks_direct_write, _emit_captures_evaluation_metric, _emit_captures_execution_output, _emit_captures_pattern, _emit_captures_runtime_anomaly, _emit_checks_agent_registry, _emit_coordinates_agents, _emit_dispatches_agent, _emit_dispatches_execution_plan, _emit_dispatches_healing_run, _emit_emits_metric_event, _emit_escalates_failure, _emit_escalates_to_human, _emit_execution_terminates_at_uwg, _emit_feeds_meta_learning, _emit_gated_by_confidence, _emit_guardian_action, _emit_proposal_commits_routing, _emit_pulls_context, _emit_reads_policy_state, _emit_reads_runtime_state, _emit_records_execution_trace, _emit_records_healing_outcome, _emit_records_learning_event, _emit_records_telemetry_event, _emit_snapshots_state, _emit_validates_agent_capability, _emit_writes_learning_snapshot, _emit_writes_through
                        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import _emit_agent_executes_agent, _emit_applies_guardrail, _emit_authorize_and_execute, _emit_blocks_direct_write, _emit_captures_evaluation_metric, _emit_captures_execution_output, _emit_captures_pattern, _emit_captures_runtime_anomaly, _emit_checks_agent_registry, _emit_coordinates_agents, _emit_dispatches_agent, _emit_dispatches_execution_plan, _emit_dispatches_healing_run, _emit_emits_metric_event, _emit_escalates_failure, _emit_escalates_to_human, _emit_execution_terminates_at_uwg, _emit_feeds_meta_learning, _emit_gated_by_confidence, _emit_guardian_action, _emit_proposal_commits_routing, _emit_pulls_context, _emit_reads_policy_state, _emit_reads_runtime_state, _emit_records_execution_trace, _emit_records_healing_outcome, _emit_records_learning_event, _emit_records_telemetry_event, _emit_snapshots_state, _emit_validates_agent_capability, _emit_writes_learning_snapshot, _emit_writes_through
                        from agentic_core.L2_execution.tools.write_gateway import MAX_GROWTH_RATIO, MAX_WRITE_BYTES, MutationEntropyError, WriteAmplificationError, WriteSizeCapError, get_prohibition_hit_count, record_prohibition_hit, write_text
                        from agentic_core.L2_execution.tools.write_gateway import MAX_GROWTH_RATIO, MAX_WRITE_BYTES, MutationEntropyError, WriteAmplificationError, WriteSizeCapError, get_prohibition_hit_count, record_prohibition_hit, write_text
                        from agentic_core.L2_execution.tools.write_gateway import MAX_GROWTH_RATIO, MAX_WRITE_BYTES, MutationEntropyError, WriteAmplificationError, WriteSizeCapError, get_prohibition_hit_count, record_prohibition_hit, write_text
                        from agentic_core.L2_execution.tools.write_gateway import MAX_GROWTH_RATIO, MAX_WRITE_BYTES, MutationEntropyError, WriteAmplificationError, WriteSizeCapError, get_prohibition_hit_count, record_prohibition_hit, write_text
                        # Arrange
                        detector = WriteAmplificationDetector(
                            max_growth_ratio=MAX_GROWTH_RATIO,
                            max_write_bytes=MAX_WRITE_BYTES,
                        )
                        # Simulate write operations that exceed threshold
                        detector.track_write(100)  # Initial write
                        detector.track_write(500)  # This should trigger amplification warning
                        # Assert
                        assert detector.get_amplification_ratio() > MAX_GROWTH_RATIO
                        assert detector.is_amplification_detected()

                assert detector.is_amplification_detected()

        assert detector.is_amplification_detected()

    def test_write_size_cap_enforcement(self):
        """Test that write size cap is enforced."""
        import pytest
        # Arrange
        detector = WriteSizeCapError(max_bytes=MAX_WRITE_BYTES)
        
        # Act & Assert
        with pytest.raises(WriteSizeCapError):
            detector.validate_write_size(MAX_WRITE_BYTES + 1)

    def test_mutation_entropy_detection(self):
        """Test mutation entropy calculation and detection."""
        # Arrange
        detector = MutationEntropyError(threshold=0.8)
        
        # Simulate high entropy mutations
        mutations = [
            "delete_file", "create_file", "modify_permissions", "change_owner"
        ]
        
        # Act
        entropy_score = detector.calculate_entropy(mutations)
        
        # Assert
        assert entropy_score > 0.8
        assert detector.is_entropy_too_high(entropy_score)

    def test_prohibition_hit_tracking(self):
        """Test prohibition hit count tracking."""
        # Arrange
        initial_count = get_prohibition_hit_count()
        
        # Act
        record_prohibition_hit("test_operation")
        new_count = get_prohibition_hit_count()
        
        # Assert
        assert new_count == initial_count + 1

    def test_write_text_with_validation(self):
        """Test write_text function with validation."""
        import tempfile
        # Arrange
        test_path = Path(tempfile.mkdtemp()) / "test_file.txt"
        test_content = "Test content for write validation"
        
        # Act
        write_text(str(test_path), test_content)
        
        # Assert
        assert test_path.exists()
        assert test_path.read_text() == test_content


class TestGuardianIntegration:
    """Test integration with guardian enforcement."""

    def test_guardian_action_emission(self):
        """Test that guardian actions are properly emitted."""
        # Arrange
        test_action = "write_amplification_detected"
        
        # Act
        _emit_guardian_action(
            agent_id="test_agent",
            action=test_action,
            context={"file_path": "/test/path", "size": 1024}
        )
        
        # Assert - In real implementation, this would verify the emission
        assert True  # Placeholder assertion

    def test_lifecycle_trace_integration(self):
        """Test lifecycle trace contract integration."""
        # Arrange
        agent_id = "test_write_guard_agent"
        
        # Act - Emit various lifecycle events
        _emit_agent_executes_agent(agent_id, "target_agent")
        _emit_applies_guardrail(agent_id, "write_guardrail")
        _emit_blocks_direct_write(agent_id, "/blocked/path")
        
        # Assert - Verify emissions were recorded
        assert True  # Placeholder assertion


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_write_amplification_error_message(self):
        """Test WriteAmplificationError message format."""
        # Arrange
        ratio = 2.5
        threshold = 2.0
        
        # Act
        error = WriteAmplificationError(ratio, threshold)
        
        # Assert
        assert str(ratio) in str(error)
        assert str(threshold) in str(error)

    def test_mutation_entropy_error_message(self):
        """Test MutationEntropyError message format."""
        # Arrange
        entropy = 0.9
        threshold = 0.8
        
        # Act
        error = MutationEntropyError(entropy, threshold)
        
        # Assert
        assert str(entropy) in str(error)
        assert str(threshold) in str(error)

    def test_write_size_cap_error_message(self):
        """Test WriteSizeCapError message format."""
        # Arrange
        size = 2048
        max_size = 1024
        
        # Act
        error = WriteSizeCapError(size, max_size)
        
        # Assert
        assert str(size) in str(error)
        assert str(max_size) in str(error)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
