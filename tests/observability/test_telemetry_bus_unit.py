"""
Unit tests for TelemetryBus core functionality.

Tests event capture, error recording, and configuration management.
"""

import pytest
import time
from unittest.mock import patch

from runtime.telemetry_bus import (
    TelemetryBus, 
    TelemetryEvent, 
    TelemetryError, 
    TelemetryTrace,
    get_telemetry_bus
)


class TestTelemetryBus:
    """Test suite for TelemetryBus core functionality."""
    
    def setup_method(self):
        """Setup fresh telemetry bus for each test."""
        # Clear singleton to ensure clean state
        TelemetryBus._instance = None
        self.bus = TelemetryBus()
        self.bus.clear()
    
    def test_record_event_captures_payload(self):
        """Test that record_event captures payload correctly."""
        payload = {
            "workflow_type": "outreach",
            "archetype": "C_LEVEL",
            "mission_id": "test_mission",
            "stage": "research",
            "duration": 1.5
        }
        
        self.bus.record_event("phase_start", "L3", payload)
        
        events = self.bus.get_events()
        assert len(events) == 1
        
        event = events[0]
        assert event.name == "phase_start"
        assert event.layer == "L3"
        assert event.payload["workflow_type"] == "outreach"
        assert event.payload["archetype"] == "C_LEVEL"
        assert event.timestamp > 0
    
    def test_record_error_includes_exception_and_context(self):
        """Test that record_error captures exception details and context."""
        error = ValueError("Test error message")
        context = {
            "workflow_type": "outreach",
            "stage": "safety_validation",
            "archetype": "EXECUTIVE"
        }
        
        self.bus.record_error("safety_failure", "L5", error, context)
        
        errors = self.bus.get_errors()
        assert len(errors) == 1
        
        error_event = errors[0]
        assert error_event.name == "safety_failure"
        assert error_event.layer == "L5"
        assert error_event.error == error
        assert str(error_event.error) == "Test error message"
        assert error_event.context["workflow_type"] == "outreach"
        assert error_event.timestamp > 0
    
    def test_record_trace_captures_trace_data(self):
        """Test that record_trace captures trace information."""
        trace_data = {
            "trace_id": "trace_123",
            "span_id": "span_456",
            "operation_name": "outreach_workflow",
            "duration_ms": 1500
        }
        
        self.bus.record_trace(trace_data)
        
        traces = self.bus.get_traces()
        assert len(traces) == 1
        
        trace = traces[0]
        assert trace.trace["trace_id"] == "trace_123"
        assert trace.trace["operation_name"] == "outreach_workflow"
        assert trace.timestamp > 0
    
    def test_telemetry_respects_config_when_disabled(self):
        """Test that telemetry is not recorded when disabled."""
        self.bus.configure(enabled=False)
        
        payload = {"workflow_type": "outreach", "stage": "research"}
        error = ValueError("Test error")
        trace_data = {"trace_id": "trace_123"}
        
        # Record events
        self.bus.record_event("phase_start", "L3", payload)
        self.bus.record_error("test_error", "L3", error, {})
        self.bus.record_trace(trace_data)
        
        # Verify nothing was recorded
        assert len(self.bus.get_events()) == 0
        assert len(self.bus.get_errors()) == 0
        assert len(self.bus.get_traces()) == 0
    
    def test_detail_level_filters_payload_minimal(self):
        """Test that minimal detail level filters payload correctly."""
        self.bus.configure(enabled=True, detail_level="minimal")
        
        payload = {
            "workflow_type": "outreach",
            "archetype": "C_LEVEL",
            "mission_id": "test_mission",
            "stage": "research",
            "duration": 1.5,
            "detailed_metrics": {"cpu": 0.8, "memory": 512}
        }
        
        self.bus.record_event("phase_start", "L3", payload)
        
        events = self.bus.get_events()
        assert len(events) == 1
        
        filtered_payload = events[0].payload
        # Should only include allowed keys for minimal level
        assert "workflow_type" in filtered_payload
        assert "stage" in filtered_payload
        assert "archetype" not in filtered_payload
        assert "mission_id" not in filtered_payload
        assert "duration" not in filtered_payload
        assert "detailed_metrics" not in filtered_payload
    
    def test_detail_level_filters_payload_standard(self):
        """Test that standard detail level filters payload correctly."""
        self.bus.configure(enabled=True, detail_level="standard")
        
        payload = {
            "workflow_type": "outreach",
            "archetype": "C_LEVEL",
            "mission_id": "test_mission",
            "stage": "research",
            "duration": 1.5,
            "detailed_metrics": {"cpu": 0.8, "memory": 512}
        }
        
        self.bus.record_event("phase_start", "L3", payload)
        
        events = self.bus.get_events()
        assert len(events) == 1
        
        filtered_payload = events[0].payload
        # Should include standard keys
        assert "workflow_type" in filtered_payload
        assert "archetype" in filtered_payload
        assert "stage" in filtered_payload
        assert "duration" in filtered_payload
        assert "detailed_metrics" not in filtered_payload
    
    def test_detail_level_verbose_includes_all_payload(self):
        """Test that verbose detail level includes all payload data."""
        self.bus.configure(enabled=True, detail_level="verbose")
        
        payload = {
            "workflow_type": "outreach",
            "archetype": "C_LEVEL",
            "mission_id": "test_mission",
            "stage": "research",
            "duration": 1.5,
            "detailed_metrics": {"cpu": 0.8, "memory": 512}
        }
        
        self.bus.record_event("phase_start", "L3", payload)
        
        events = self.bus.get_events()
        assert len(events) == 1
        
        filtered_payload = events[0].payload
        # Should include all keys for verbose level
        assert filtered_payload == payload
    
    def test_get_events_with_filters(self):
        """Test that get_events respects layer and name filters."""
        # Record multiple events
        self.bus.record_event("phase_start", "L3", {"stage": "research"})
        self.bus.record_event("phase_end", "L3", {"stage": "research"})
        self.bus.record_event("phase_start", "L2", {"stage": "company_research"})
        
        # Test layer filter
        l3_events = self.bus.get_events(layer="L3")
        assert len(l3_events) == 2
        assert all(e.layer == "L3" for e in l3_events)
        
        # Test name filter
        start_events = self.bus.get_events(name="phase_start")
        assert len(start_events) == 2
        assert all(e.name == "phase_start" for e in start_events)
        
        # Test combined filters
        l3_start_events = self.bus.get_events(layer="L3", name="phase_start")
        assert len(l3_start_events) == 1
        assert l3_start_events[0].layer == "L3"
        assert l3_start_events[0].name == "phase_start"
    
    def test_get_errors_with_filters(self):
        """Test that get_errors respects layer and name filters."""
        error1 = ValueError("Error 1")
        error2 = RuntimeError("Error 2")
        
        # Record multiple errors
        self.bus.record_error("research_failure", "L2", error1, {"type": "company"})
        self.bus.record_error("safety_failure", "L5", error2, {"type": "content"})
        self.bus.record_error("research_failure", "L2", error1, {"type": "contact"})
        
        # Test layer filter
        l2_errors = self.bus.get_errors(layer="L2")
        assert len(l2_errors) == 2
        assert all(e.layer == "L2" for e in l2_errors)
        
        # Test name filter
        research_errors = self.bus.get_errors(name="research_failure")
        assert len(research_errors) == 2
        assert all(e.name == "research_failure" for e in research_errors)
    
    def test_clear_resets_all_data(self):
        """Test that clear method resets all telemetry data."""
        # Record some data
        self.bus.record_event("phase_start", "L3", {"stage": "research"})
        self.bus.record_error("test_error", "L3", ValueError("test"), {})
        self.bus.record_trace({"trace_id": "123"})
        
        # Verify data exists
        assert len(self.bus.get_events()) == 1
        assert len(self.bus.get_errors()) == 1
        assert len(self.bus.get_traces()) == 1
        
        # Clear and verify empty
        self.bus.clear()
        assert len(self.bus.get_events()) == 0
        assert len(self.bus.get_errors()) == 0
        assert len(self.bus.get_traces()) == 0
    
    def test_get_summary_provides_statistics(self):
        """Test that get_summary returns correct statistics."""
        # Record some data
        self.bus.record_event("phase_start", "L3", {"stage": "research"})
        self.bus.record_event("phase_end", "L2", {"stage": "company_research"})
        self.bus.record_error("test_error", "L5", ValueError("test"), {})
        self.bus.record_trace({"trace_id": "123"})
        
        summary = self.bus.get_summary()
        
        assert summary["total_events"] == 2
        assert summary["total_errors"] == 1
        assert summary["total_traces"] == 1
        assert summary["enabled"] == True
        assert summary["detail_level"] == "standard"
        assert set(summary["layers"]) == {"L3", "L2", "L5"}
        assert set(summary["event_names"]) == {"phase_start", "phase_end"}
    
    def test_singleton_pattern(self):
        """Test that TelemetryBus implements singleton pattern correctly."""
        bus1 = TelemetryBus()
        bus2 = TelemetryBus()
        
        # Should be the same instance
        assert bus1 is bus2
        
        # Changes to one should affect the other
        bus1.record_event("test", "L3", {"data": "test"})
        assert len(bus2.get_events()) == 1
    
    def test_get_telemetry_bus_returns_singleton(self):
        """Test that get_telemetry_bus returns the global singleton."""
        bus1 = get_telemetry_bus()
        bus2 = get_telemetry_bus()
        
        # Should return the same instance
        assert bus1 is bus2
        
        # Should be TelemetryBus instance
        assert isinstance(bus1, TelemetryBus)
    
    def test_thread_safety(self):
        """Test that TelemetryBus is thread-safe."""
        import threading
        
        def record_events():
            for i in range(10):
                self.bus.record_event(f"event_{i}", "L3", {"index": i})
        
        # Create multiple threads
        threads = [threading.Thread(target=record_events) for _ in range(5)]
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have recorded all events without corruption
        events = self.bus.get_events()
        assert len(events) == 50  # 5 threads * 10 events each
