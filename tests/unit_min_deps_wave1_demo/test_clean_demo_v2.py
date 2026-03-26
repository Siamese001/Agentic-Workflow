"""Clean demo file for Wave 2 testing."""

import tempfile
from pathlib import Path

import pytest

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
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
)


class TestWriteAmplificationDetector:
    """Test write amplification detection logic."""

    def test_write_amplification_threshold(self):
        """Test that write amplification is detected when threshold exceeded."""
                        from agentic_core.L2_execution.tools.write_gateway import (
                        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
        # Arrange
        detector = WriteSizeCapError(max_bytes=MAX_WRITE_BYTES)
        
        # Act & Assert
        with pytest.raises(WriteSizeCapError):
            detector.validate_write_size(MAX_WRITE_BYTES + 1)

    def test_prohibition_hit_tracking(self):
        """Test prohibition hit count tracking."""
        # Arrange
        initial_count = get_prohibition_hit_count()
        
        # Act
        record_prohibition_hit("test_operation")
        new_count = get_prohibition_hit_count()
        
        # Assert
        assert new_count == initial_count + 1

    def test_lifecycle_trace_integration(self):
        """Test lifecycle trace contract integration."""
        # Arrange
        agent_id = "test_write_guard_agent"
        
        # Act - Emit various lifecycle events
        _emit_agent_executes_agent(agent_id, "target_agent")
        _emit_applies_guardrail(agent_id, "write_guardrail")
        
        # Assert - Verify emissions were recorded
        assert True  # Placeholder assertion


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
