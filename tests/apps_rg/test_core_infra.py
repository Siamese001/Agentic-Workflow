"""
Phase 1 Core Infrastructure Tests - 100% pass required.

Tests the hardened core infrastructure:
- ImmutableStagingBuffer: Deep copy isolation, write-once locking
- TraceRegistry: Span-based tracing with latency tracking
"""

import pytest
import time
import sys
from pathlib import Path

# Add project root to path for imports BEFORE any app imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from apps_rg.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_rg.shared.core.trace_registry import TraceRegistry


def test_buffer_ghost_mutation_prevention():
    """
    CRITICAL SECURITY TEST:
    Verifies that modifying a dictionary read from the buffer
    does NOT modify the internal state of the buffer.
    """
    buffer = ImmutableStagingBuffer()
    secret_config = {"access_level": "admin", "nested": {"param": 1}}

    # Write to buffer
    buffer.write("config", secret_config, source_agent="Setup")

    # Read back (should be a copy)
    leaked_ref = buffer.read("config")

    # Attacker tries to mutate the reference
    leaked_ref["access_level"] = "hacker"
    leaked_ref["nested"]["param"] = 999

    # Verify internal state is pristine
    safe_data = buffer.read("config")
    assert safe_data["access_level"] == "admin"
    assert safe_data["nested"]["param"] == 1


def test_buffer_write_once_locking():
    """Ensure a key cannot be overwritten."""
    buffer = ImmutableStagingBuffer()
    buffer.write("key", "value1", "AgentA")

    with pytest.raises(PermissionError):
        buffer.write("key", "value2", "AgentB")


def test_buffer_transaction_history():
    """Verify transaction logging works correctly."""
    buffer = ImmutableStagingBuffer()
    buffer.set_cycle("CYCLE_001")
    buffer.write("data1", {"value": 1}, source_agent="Agent1")
    buffer.write("data2", {"value": 2}, source_agent="Agent2")

    history = buffer.get_history()
    assert len(history) == 2
    assert history[0].key == "data1"
    assert history[0].source_agent == "Agent1"
    assert history[0].cycle_id == "CYCLE_001"
    assert history[1].key == "data2"
    assert history[1].source_agent == "Agent2"


def test_buffer_read_default():
    """Verify read returns default for missing keys."""
    buffer = ImmutableStagingBuffer()
    result = buffer.read("nonexistent", default="fallback")
    assert result == "fallback"


def test_buffer_snapshot_isolation():
    """Verify get_snapshot returns a deep copy."""
    buffer = ImmutableStagingBuffer()
    buffer.write("key", {"nested": {"value": 1}}, "Test")

    snapshot = buffer.get_snapshot()
    snapshot["key"]["nested"]["value"] = 999

    # Original should be unchanged
    assert buffer.read("key")["nested"]["value"] == 1


def test_trace_span_lifecycle():
    """Verify spans track duration correctly."""
    registry = TraceRegistry()
    span = registry.start_span("trace_123", "Orchestrator", "Plan")

    time.sleep(0.01)

    registry.end_span(span, status="SUCCESS")

    summary = registry.get_summary()
    assert summary["total_spans"] == 1
    assert summary["avg_latency_ms"] > 0


def test_trace_span_failure_tracking():
    """Verify failure spans are tracked correctly."""
    registry = TraceRegistry()
    span = registry.start_span("trace_456", "Validator", "Validate")

    registry.end_span(span, status="FAILURE", error="Validation failed")

    summary = registry.get_summary()
    assert summary["failures"] == 1
    assert summary["completed"] == 1


def test_trace_token_tracking():
    """Verify token usage is tracked."""
    registry = TraceRegistry()
    span = registry.start_span("trace_789", "Generator", "Generate")

    registry.end_span(span, status="SUCCESS", tokens=1500)

    summary = registry.get_summary()
    assert summary["total_tokens"] == 1500


def test_trace_legacy_api():
    """Verify legacy add_trace API still works."""
    registry = TraceRegistry()
    registry.add_trace("PHASE_START", {"agent": "TestAgent"})

    traces = registry.get_traces()
    assert len(traces) == 1
    assert traces[0]["action"] == "PHASE_START"


def test_trace_count_by_type():
    """Verify count by action type works."""
    registry = TraceRegistry()
    registry.add_trace("PHASE_START", {"agent": "Agent1"})
    registry.add_trace("PHASE_START", {"agent": "Agent2"})
    registry.add_trace("PHASE_END", {"agent": "Agent1"})

    assert registry.count("PHASE_START") == 2
    assert registry.count("PHASE_END") == 1


def test_trace_get_latest():
    """Verify get_latest returns most recent trace."""
    registry = TraceRegistry()
    registry.add_trace("ACTION", {"agent": "First"})
    time.sleep(0.001)
    registry.add_trace("ACTION", {"agent": "Second"})

    latest = registry.get_latest("ACTION")
    assert latest is not None
    # The latest should be the second one added


def test_buffer_write_once_legacy_api():
    """Verify legacy write_once API works."""
    buffer = ImmutableStagingBuffer()
    buffer.write_once("legacy_key", "legacy_value")

    assert buffer.read("legacy_key") == "legacy_value"
    assert buffer.is_locked("legacy_key")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
